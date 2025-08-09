#!/usr/bin/env python3
"""
mini_chat_all_in_one.py

Run as:
  # CLI mode
  python mini_chat_all_in_one.py --cli

  # Web mode (opens a FastAPI server at http://localhost:8000)
  python mini_chat_all_in_one.py --web

This script:
- Provides a small CLI chat using Hugging Face transformers (default: EleutherAI/gpt-neo-125M)
- Provides a FastAPI WebSocket chat server + minimal HTML client (written to ./client.html)
- Has a simple content filter (expand for production)
- Stores conversation history in memory per process (not persistent)
"""

import argparse
import os
import asyncio
from typing import Optional

# Model-related imports
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Web server imports
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

# ---------------------------
# Configuration
# ---------------------------
DEFAULT_MODEL = "EleutherAI/gpt-neo-125M" # change to another model if desired
DEFAULT_MAX_NEW_TOKENS = 150
CLIENT_HTML_PATH = "client.html"

# ---------------------------
# Utilities
# ---------------------------
def get_device():
    """Detect the best available device for PyTorch."""
    if torch.cuda.is_available():
        return "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        return "mps"
    else:
        return "cpu"

DEFAULT_DEVICE = get_device()

# ---------------------------
# Utilities
# ---------------------------
def safe_check(text: str) -> bool:
    """
    Very simple content filter: block obvious harmful keywords.
    Replace/extend with a better filter for production.
    """
    banned = [
        "bomb", "kill", "suicide", "self-harm", "illegal", "terrorist", "explode",
        "child porn", "cp", "ddos", "hitman", "assassinate"
    ]
    low = text.lower()
    return not any(w in low for w in banned)

def write_client_html(path: str = CLIENT_HTML_PATH, ws_path: str = "/ws/chat"):
    """
    Writes a minimal HTML client that connects to the WebSocket.
    """
    html = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>MiniChat</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 20px; }}
    #log {{ height: 360px; overflow:auto; border:1px solid #ddd; padding:10px; }}
    #input {{ width: 78%; padding:6px; }}
    button {{ padding:6px 10px; }}
    .you {{ color: #1a73e8; }}
    .bot {{ color: #2e7d32; }}
    .sys {{ color: #d32f2f; }}
  </style>
</head>
<body>
  <h2>MiniChat</h2>
  <div id="log"></div>
  <div style="margin-top:12px;">
    <input id="input" placeholder="Type your message..." />
    <button id="send">Send</button>
  </div>
  <script>
    const log = document.getElementById("log");
    function addLine(cls, html) {{
      const d = document.createElement("div");
      d.className = cls;
      d.innerHTML = html;
      log.appendChild(d);
      log.scrollTop = log.scrollHeight;
    }}

    const ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "{ws_path}");
    ws.onopen = () => addLine('sys', '<i>Connected to server.</i>');
    ws.onmessage = (e) => {{
      addLine('bot', '<b>Bot:</b> ' + e.data);
    }};
    ws.onclose = () => addLine('sys', '<i>Disconnected.</i>');
    ws.onerror = (e) => console.error(e);

    document.getElementById("send").onclick = () => {{
      const v = document.getElementById("input").value;
      if(!v) return;
      addLine('you', '<b>You:</b> ' + v);
      ws.send(v);
      document.getElementById("input").value = "";
    }};
    document.getElementById("input").addEventListener("keydown", (e) => {{
      if(e.key === "Enter") document.getElementById("send").click();
    }});
  </script>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Wrote client HTML to {path}")

# ---------------------------
# Model Loader
# ---------------------------
class ModelWrapper:
    def __init__(self, model_name: str = DEFAULT_MODEL, device: Optional[str] = None):
        self.model_name = model_name
        self.device = device or DEFAULT_DEVICE
        self.tokenizer = None
        self.model = None
        self._load()

    def _load(self):
        try:
            print(f"[INFO] Loading tokenizer & model: {self.model_name} on device {self.device} ...")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            # For some models the tokenizer doesn't set pad/eos; ensure eos_token_id exists
            if self.tokenizer.pad_token is None:
                try:
                    self.tokenizer.pad_token = self.tokenizer.eos_token
                except Exception:
                    pass
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            print("[INFO] Model loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            print("[INFO] Falling back to CPU...")
            self.device = "cpu"
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.model.to(self.device)
            print("[INFO] Model loaded on CPU.")

    @torch.no_grad()
    def generate(self, prompt: str, max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS) -> str:
        try:
            # Tokenize and move to device
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.8,
                pad_token_id=self.tokenizer.eos_token_id
            )
            # decode only the newly generated tokens
            gen_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True)
            return gen_text.strip()
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            return "I'm sorry, I encountered an error while generating a response. Please try again."

# ---------------------------
# CLI Chat
# ---------------------------
def run_cli(model_wrapper: ModelWrapper):
    print("MiniChat CLI — type 'exit' or Ctrl-C to quit.")
    print(f"Using model: {model_wrapper.model_name} on {model_wrapper.device}")
    print("Commands: 'help', 'clear', 'exit'")
    chat_history = ""
    try:
        while True:
            user = input("\nYou: ").strip()
            if user.lower() in ("exit", "quit"):
                print("Goodbye.")
                break
            if not user:
                continue
            if user.lower() == "help":
                print("Commands:")
                print("  help   - Show this help")
                print("  clear  - Clear chat history")
                print("  exit   - Exit the program")
                continue
            if user.lower() == "clear":
                chat_history = ""
                print("Chat history cleared.")
                continue
            if not safe_check(user):
                print("Bot: Sorry, I can't help with that.")
                continue
            
            print("Bot: Thinking...", end="", flush=True)
            prompt = chat_history + "\nUser: " + user + "\nAssistant:"
            reply = model_wrapper.generate(prompt)
            print("\rBot:", reply)
            
            # Update history
            chat_history += "\nUser: " + user + "\nAssistant: " + reply
    except KeyboardInterrupt:
        print("\nInterrupted — exiting.")

# ---------------------------
# Web (FastAPI) Chat
# ---------------------------
def create_app(model_wrapper: ModelWrapper):
    app = FastAPI()
    # For a single-process simple server we keep a global chat_history per process
    # In production you'd want per-user session storage, DB, authentication, etc.
    app.state.chat_history = ""

    @app.get("/")
    def index():
        if not os.path.exists(CLIENT_HTML_PATH):
            write_client_html(CLIENT_HTML_PATH)
        with open(CLIENT_HTML_PATH, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())

    @app.websocket("/ws/chat")
    async def websocket_chat(ws: WebSocket):
        await ws.accept()
        print("[INFO] WebSocket client connected.")
        try:
            while True:
                data = await ws.receive_text()
                if not safe_check(data):
                    await ws.send_text("SYSTEM: Blocked content.")
                    continue
                # Build prompt using stored chat history (process-level)
                prompt = app.state.chat_history + "\nUser: " + data + "\nAssistant:"
                # Run blocking model generate in thread pool to avoid blocking event loop
                reply = await asyncio.to_thread(model_wrapper.generate, prompt)
                app.state.chat_history += "\nUser: " + data + "\nAssistant: " + reply
                await ws.send_text(reply)
        except WebSocketDisconnect:
            print("[INFO] WebSocket client disconnected.")
        except Exception as e:
            print("[ERROR] WebSocket error:", e)
            try:
                await ws.close()
            except Exception:
                pass

    return app

# ---------------------------
# Main / CLI args
# ---------------------------
def main():
    ap = argparse.ArgumentParser(description="MiniChat — single-file chat server + CLI")
    ap.add_argument("--model", default=DEFAULT_MODEL, help="Hugging Face model name (default: %(default)s)")
    ap.add_argument("--device", default=None, help="Device override, e.g., cpu or cuda")
    ap.add_argument("--cli", action="store_true", help="Run CLI chat")
    ap.add_argument("--web", action="store_true", help="Run web server (FastAPI + WebSocket)")
    ap.add_argument("--host", default="0.0.0.0", help="Host for web server")
    ap.add_argument("--port", default=8000, type=int, help="Port for web server")
    ap.add_argument("--version", action="version", version="MiniChat 1.0.0")
    args = ap.parse_args()

    try:
        mw = ModelWrapper(model_name=args.model, device=args.device)
    except Exception as e:
        print(f"[ERROR] Failed to initialize model: {e}")
        print("[INFO] Try using --device cpu if you're having GPU issues")
        return 1

    if args.cli:
        run_cli(mw)
        return 0

    if args.web:
        # Ensure client HTML exists
        write_client_html(CLIENT_HTML_PATH)
        app = create_app(mw)
        # Run uvicorn programmatically
        print(f"[INFO] Starting server at http://{args.host}:{args.port} ...")
        print(f"[INFO] Open http://localhost:{args.port} in your browser")
        uvicorn.run(app, host=args.host, port=args.port, log_level="info")
        return 0

    # If neither specified, print usage + small interactive prompt
    print("No mode chosen. Use --cli or --web. Example:\n  python mini_chat_all_in_one.py --web")
    # Offer to run CLI by default if interactive
    try:
        run_cli(mw)
        return 0
    except Exception as e:
        print(f"[ERROR] CLI failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())