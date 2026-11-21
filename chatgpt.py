"""Local, documented Codex App Server client for ChatGPT sign-in and usage."""
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time
from urllib.parse import urlsplit

DEFAULT_PROFILE = Path.home() / ".atelier-3d" / "codex"


class ChatGPT:
    def __init__(self, profile=None):
        self.profile = Path(profile) if profile else DEFAULT_PROFILE
        self.process = None
        self.lock = threading.RLock()
        self.messages = queue.Queue()
        self.sequence = 0
        self.login_state = None

    def _read(self, process, messages):
        try:
            for line in process.stdout:
                try:
                    event = json.loads(line)
                except (ValueError, TypeError):
                    continue
                if event.get("method") == "account/login/completed":
                    self.login_state = event.get("params", {})
                messages.put(event)
        finally:
            messages.put(None)

    def _start(self):
        if self.process and self.process.poll() is None:
            return
        executable = os.getenv("ATELIER_CODEX_BIN") or shutil.which("codex")
        if not executable:
            raise ValueError("Cài Codex CLI chính thức rồi khởi động lại gateway để kết nối ChatGPT.")
        self.profile.mkdir(mode=0o700, parents=True, exist_ok=True)
        workdir = self.profile / "planning"
        workdir.mkdir(exist_ok=True)
        environment = dict(os.environ, CODEX_HOME=str(self.profile))
        for key in ("OPENAI_API_KEY", "CODEX_API_KEY", "OPENAI_BASE_URL"):
            environment.pop(key, None)
        args = [executable, "app-server", "--listen", "stdio://", "--disable", "shell_tool",
                "--disable", "plugins", "--disable", "remote_plugin", "-c", 'web_search="disabled"']
        self.process = subprocess.Popen(args, cwd=workdir, env=environment, stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding="utf-8",
                                        errors="replace", bufsize=1)
        self.messages = queue.Queue()
        threading.Thread(target=self._read, args=(self.process,self.messages), daemon=True).start()
        try:
            self._rpc("initialize", {"clientInfo":{"name":"atelier-3d","title":"Atelier 3D","version":"0.2.0"}})
            self._send({"method":"initialized"})
        except (OSError, ValueError):
            self.close()
            raise

    def _send(self, message):
        try:
            self.process.stdin.write(json.dumps(message, ensure_ascii=False) + "\n")
            self.process.stdin.flush()
        except OSError as exc:
            raise ValueError("Codex App Server đã ngắt kết nối.") from exc

    def _next(self, deadline):
        try:
            result = self.messages.get(timeout=max(0, deadline - time.monotonic()))
        except queue.Empty as exc:
            raise ValueError("Codex App Server phản hồi quá thời gian.") from exc
        if result is None:
            raise ValueError("Codex App Server đã ngắt kết nối. Kiểm tra phiên bản Codex CLI.")
        if "method" in result and "id" in result:
            self._send({"id":result["id"],"error":{"code":-32601,"message":"Interactive tools are disabled"}})
        return result

    def _rpc(self, method, params=None, forward=None):
        self.sequence += 1
        ident = self.sequence
        message = {"id":ident, "method":method}
        if params is not None:
            message["params"] = params
        self._send(message)
        deadline = time.monotonic() + 18
        while True:
            event = self._next(deadline)
            if event.get("id") == ident and "method" not in event:
                if "error" in event:
                    raise ValueError(f"Codex báo lỗi với thao tác {method}.")
                return event["result"]
            if forward is not None:
                forward.append(event)

    def login(self):
        with self.lock:
            self._start()
            self.login_state = None
            result = self._rpc("account/login/start", {"type":"chatgpt","useHostedLoginSuccessPage":True,
                                                         "appBrand":"chatgpt"})
            url = urlsplit(result.get("authUrl",""))
            if url.scheme != "https" or url.hostname not in {"auth.openai.com","chatgpt.com"} or url.username or url.password:
                raise ValueError("Codex không trả địa chỉ xác thực ChatGPT hợp lệ.")
            return {"url":url.geturl()}

    def status(self):
        with self.lock:
            self._start()
            account = self._rpc("account/read", {"refreshToken":False}).get("account") or {}
            if account.get("type") != "chatgpt":
                return {"connected":False, "loginFailed":bool(self.login_state and not self.login_state.get("success"))}
            payload = {"connected":True,"plan":account.get("planType"),"limits":[]}
            try:
                result = self._rpc("account/rateLimits/read")
            except ValueError:
                payload["quotaUnavailable"] = True
                return payload
            bucket = (result.get("rateLimitsByLimitId") or {}).get("codex") or result.get("rateLimits") or {}
            for name in ("primary","secondary"):
                window = bucket.get(name) or {}
                used = window.get("usedPercent")
                if type(used) in (int,float) and 0 <= used <= 100:
                    payload["limits"].append({"remaining":round(100-used, 1),
                                              "minutes":window.get("windowDurationMins"),"resetsAt":window.get("resetsAt")})
            return payload

    def plan(self, instructions, prompt):
        with self.lock:
            self._start()
            account = self._rpc("account/read", {"refreshToken":False}).get("account") or {}
            if account.get("type") != "chatgpt":
                raise ValueError("Kết nối ChatGPT trước khi dùng để xử lý yêu cầu.")
            result = self._rpc("thread/start", {
                "ephemeral":True, "sandbox":"read-only", "approvalPolicy":"never",
                "cwd":str(self.profile / "planning"), "developerInstructions":instructions,
            })
            thread = result["thread"]["id"]
            pending = []
            turn = self._rpc("turn/start", {
                "threadId":thread, "input":[{"type":"text","text":prompt,"text_elements":[]}],
            }, forward=pending)["turn"]["id"]
            deadline = time.monotonic() + 135
            answer = ""
            try:
                while True:
                    event = pending.pop(0) if pending else self._next(deadline)
                    params = event.get("params") or {}
                    if params.get("threadId") != thread:
                        continue
                    if event.get("method") == "item/completed" and params.get("turnId") == turn:
                        item = params.get("item") or {}
                        if item.get("type") == "agentMessage":
                            answer = item.get("text","")
                    if event.get("method") == "turn/completed" and params.get("turn",{}).get("id") == turn:
                        if params["turn"].get("status") != "completed" or not answer:
                            raise ValueError("ChatGPT chưa trả được dữ liệu dựng hình. Kiểm tra hạn mức và thử lại.")
                        return answer
            except ValueError:
                try:
                    self._rpc("turn/interrupt", {"threadId":thread,"turnId":turn})
                except ValueError:
                    pass
                raise

    def close(self):
        process, self.process = self.process, None
        if process and process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=2)
            except (subprocess.TimeoutExpired, ValueError):
                process.kill()
