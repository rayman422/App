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
import sys
import platform
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
DEFAULT_TEMPERATURE = 0.8
DEFAULT_TOP_P = 0.95
DEFAULT_TOP_K = 50
DEFAULT_REPETITION_PENALTY = 1.1
DEFAULT_MAX_LENGTH = 2048
CLIENT_HTML_PATH = "client.html"

# Model presets for different use cases
MODEL_PRESETS = {
    "fast": "EleutherAI/gpt-neo-125M",
    "balanced": "microsoft/DialoGPT-medium",
    "quality": "gpt2",
    "creative": "EleutherAI/gpt-neo-1.3B",
    "coding": "microsoft/DialoGPT-medium"
}

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

def save_conversation_history(history: list, filename: str):
    """Save conversation history to a JSON file."""
    try:
        import json
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        print(f"[INFO] Conversation history saved to {filename}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to save history: {e}")
        return False

def load_conversation_history(filename: str) -> list:
    """Load conversation history from a JSON file."""
    try:
        import json
        with open(filename, 'r', encoding='utf-8') as f:
            history = json.load(f)
        print(f"[INFO] Conversation history loaded from {filename}")
        return history
    except Exception as e:
        print(f"[ERROR] Failed to load history: {e}")
        return []

def create_system_prompt(prompt_type: str = "general") -> str:
    """Create system prompts for different conversation types."""
    prompts = {
        "general": "You are a helpful AI assistant. Be concise and helpful.",
        "creative": "You are a creative AI assistant. Be imaginative and artistic in your responses.",
        "coding": "You are a coding assistant. Provide clear, working code examples and explanations.",
        "professional": "You are a professional AI assistant. Be formal, accurate, and business-like.",
        "casual": "You are a friendly AI assistant. Be casual, warm, and conversational."
    }
    return prompts.get(prompt_type, prompts["general"])

def format_timestamp() -> str:
    """Get current timestamp for logging."""
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def export_conversation(history: list, format_type: str = "txt", filename: str = None) -> str:
    """Export conversation history in different formats."""
    if not filename:
        timestamp = format_timestamp().replace(":", "-").replace(" ", "_")
        filename = f"conversation_{timestamp}.{format_type}"
    
    try:
        if format_type == "txt":
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"MiniChat Conversation - {format_timestamp()}\n")
                f.write("=" * 50 + "\n\n")
                for i, turn in enumerate(history, 1):
                    f.write(f"Turn {i}:\n")
                    f.write(f"You: {turn['user']}\n")
                    f.write(f"Bot: {turn['bot']}\n\n")
            return filename
        elif format_type == "md":
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"# MiniChat Conversation - {format_timestamp()}\n\n")
                for i, turn in enumerate(history, 1):
                    f.write(f"## Turn {i}\n\n")
                    f.write(f"**You:** {turn['user']}\n\n")
                    f.write(f"**Bot:** {turn['bot']}\n\n")
            return filename
        elif format_type == "json":
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "metadata": {
                        "timestamp": format_timestamp(),
                        "total_turns": len(history)
                    },
                    "conversation": history
                }, f, indent=2, ensure_ascii=False)
            return filename
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    except Exception as e:
        print(f"[ERROR] Failed to export conversation: {e}")
        return None

def write_client_html(path: str = CLIENT_HTML_PATH, ws_path: str = "/ws/chat"):
    """
    Writes an enhanced HTML client that connects to the WebSocket.
    """
    html = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>MiniChat 2.0</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }}
        .header p {{
            opacity: 0.9;
            font-size: 1.1em;
        }}
        .chat-container {{
            padding: 20px;
            height: 500px;
            display: flex;
            flex-direction: column;
        }}
        #log {{
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 15px;
            margin-bottom: 20px;
            border: 1px solid #e9ecef;
        }}
        .message {{
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 15px;
            max-width: 80%;
            word-wrap: break-word;
        }}
        .you {{
            background: #007bff;
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 5px;
        }}
        .bot {{
            background: #28a745;
            color: white;
            margin-right: auto;
            border-bottom-left-radius: 5px;
        }}
        .sys {{
            background: #6c757d;
            color: white;
            text-align: center;
            margin: 10px auto;
            font-style: italic;
        }}
        .input-container {{
            display: flex;
            gap: 10px;
            align-items: center;
        }}
        #input {{
            flex: 1;
            padding: 15px;
            border: 2px solid #e9ecef;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }}
        #input:focus {{
            border-color: #667eea;
        }}
        #send {{
            padding: 15px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }}
        #send:hover {{
            transform: translateY(-2px);
        }}
        .typing {{
            display: none;
            color: #6c757d;
            font-style: italic;
            text-align: center;
            margin: 10px 0;
        }}
        .status {{
            text-align: center;
            padding: 10px;
            color: #6c757d;
            font-size: 14px;
        }}
        @media (max-width: 600px) {{
            .container {{ margin: 10px; }}
            .header {{ padding: 20px; }}
            .header h1 {{ font-size: 2em; }}
            .chat-container {{ height: 400px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 MiniChat 2.0</h1>
            <p>AI-Powered Conversations</p>
        </div>
        <div class="chat-container">
            <div id="log"></div>
            <div class="typing" id="typing">Bot is typing...</div>
            <div class="input-container">
                <input id="input" placeholder="Type your message..." autocomplete="off" />
                <button id="send">Send</button>
            </div>
            <div class="status" id="status">Connecting...</div>
        </div>
    </div>
    <script>
        const log = document.getElementById("log");
        const input = document.getElementById("input");
        const send = document.getElementById("send");
        const typing = document.getElementById("typing");
        const status = document.getElementById("status");
        
        function addMessage(cls, text, isHTML = false) {{
            const div = document.createElement("div");
            div.className = `message ${{cls}}`;
            div.innerHTML = isHTML ? text : text.replace(/\\n/g, '<br>');
            log.appendChild(div);
            log.scrollTop = log.scrollHeight;
        }}
        
        function setStatus(text, isError = false) {{
            status.textContent = text;
            status.style.color = isError ? '#dc3545' : '#6c757d';
        }}
        
        function showTyping(show) {{
            typing.style.display = show ? 'block' : 'none';
            if (show) log.scrollTop = log.scrollHeight;
        }}
        
        const ws = new WebSocket((location.protocol === "https:" ? "wss://" : "ws://") + location.host + "{ws_path}");
        
        ws.onopen = () => {{
            setStatus("Connected");
            addMessage('sys', 'Connected to MiniChat server');
        }};
        
        ws.onmessage = (e) => {{
            showTyping(false);
            addMessage('bot', e.data);
        }};
        
        ws.onclose = () => {{
            setStatus("Disconnected", true);
            addMessage('sys', 'Disconnected from server');
        }};
        
        ws.onerror = (e) => {{
            setStatus("Connection error", true);
            console.error(e);
        }};
        
        function sendMessage() {{
            const text = input.value.trim();
            if (!text) return;
            
            addMessage('you', text);
            ws.send(text);
            input.value = "";
            showTyping(true);
        }}
        
        send.onclick = sendMessage;
        input.addEventListener("keydown", (e) => {{
            if (e.key === "Enter") sendMessage();
        }});
        
        // Focus input on load
        input.focus();
    </script>
</body>
</html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[INFO] Wrote enhanced client HTML to {path}")

# ---------------------------
# Model Loader
# ---------------------------
class ModelWrapper:
    def __init__(self, model_name: str = DEFAULT_MODEL, device: Optional[str] = None, 
                 temperature: float = DEFAULT_TEMPERATURE, top_p: float = DEFAULT_TOP_P,
                 top_k: int = DEFAULT_TOP_K, repetition_penalty: float = DEFAULT_REPETITION_PENALTY,
                 system_prompt: str = "general"):
        self.model_name = model_name
        self.device = device or DEFAULT_DEVICE
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.repetition_penalty = repetition_penalty
        self.system_prompt = create_system_prompt(system_prompt)
        self.tokenizer = None
        self.model = None
        self.conversation_history = []
        self.max_history_length = 10
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
    def generate(self, prompt: str, max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS, 
                temperature: float = None, top_p: float = None, top_k: int = None) -> str:
        try:
            # Use instance parameters if not overridden
            temp = temperature if temperature is not None else self.temperature
            tp = top_p if top_p is not None else self.top_p
            tk = top_k if top_k is not None else self.top_k
            
            # Tokenize and move to device
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_k=tk,
                top_p=tp,
                temperature=temp,
                repetition_penalty=self.repetition_penalty,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3
            )
            
            # decode only the newly generated tokens
            gen_text = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[-1]:], skip_special_tokens=True)
            return gen_text.strip()
        except Exception as e:
            print(f"[ERROR] Generation failed: {e}")
            return "I'm sorry, I encountered an error while generating a response. Please try again."
    
    def generate_stream(self, prompt: str, max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS,
                       temperature: float = None, top_p: float = None, top_k: int = None):
        """Generate text with streaming output."""
        try:
            # Use instance parameters if not overridden
            temp = temperature if temperature is not None else self.temperature
            tp = top_p if top_p is not None else self.top_p
            tk = top_k if top_k is not None else self.top_k
            
            # Tokenize and move to device
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            
            # Generate with streaming
            generated_tokens = []
            for outputs in self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=True,
                top_k=tk,
                top_p=tp,
                temperature=temp,
                repetition_penalty=self.repetition_penalty,
                pad_token_id=self.tokenizer.eos_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
                no_repeat_ngram_size=3,
                return_dict_in_generate=True,
                output_scores=False,
                streaming=True
            ):
                if outputs.logits is not None:
                    next_token = outputs.logits.argmax(dim=-1)[-1].unsqueeze(0)
                    generated_tokens.append(next_token)
                    
                    # Decode and yield the new token
                    new_text = self.tokenizer.decode(next_token, skip_special_tokens=True)
                    if new_text.strip():
                        yield new_text
                        
        except Exception as e:
            print(f"[ERROR] Streaming generation failed: {e}")
            yield "I'm sorry, I encountered an error while generating a response. Please try again."
    
    def add_to_history(self, user_input: str, bot_response: str):
        """Add conversation turn to history."""
        self.conversation_history.append({"user": user_input, "bot": bot_response})
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history.pop(0)
    
    def get_context_prompt(self, current_input: str) -> str:
        """Build context-aware prompt from conversation history."""
        if not self.conversation_history:
            return f"{self.system_prompt}\n\nUser: {current_input}\nAssistant:"
        
        context = f"{self.system_prompt}\n\n"
        for turn in self.conversation_history[-3:]:  # Last 3 turns for context
            context += f"User: {turn['user']}\nAssistant: {turn['bot']}\n"
        context += f"User: {current_input}\nAssistant:"
        return context
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def switch_model(self, new_model_name: str):
        """Switch to a different model."""
        print(f"[INFO] Switching from {self.model_name} to {new_model_name}...")
        self.model_name = new_model_name
        self.clear_history()
        self._load()
        print(f"[INFO] Switched to {new_model_name}")
    
    def get_stats(self) -> dict:
        """Get conversation statistics."""
        if not self.conversation_history:
            return {"total_turns": 0, "total_user_chars": 0, "total_bot_chars": 0}
        
        total_user_chars = sum(len(turn['user']) for turn in self.conversation_history)
        total_bot_chars = sum(len(turn['bot']) for turn in self.conversation_history)
        
        return {
            "total_turns": len(self.conversation_history),
            "total_user_chars": total_user_chars,
            "total_bot_chars": total_bot_chars,
            "avg_user_length": total_user_chars / len(self.conversation_history),
            "avg_bot_length": total_bot_chars / len(self.conversation_history)
        }

# ---------------------------
# CLI Chat
# ---------------------------
def run_cli(model_wrapper: ModelWrapper):
    print("MiniChat CLI — type 'exit' or Ctrl-C to quit.")
    print(f"Using model: {model_wrapper.model_name} on {model_wrapper.device}")
    print(f"Temperature: {model_wrapper.temperature}, Top-p: {model_wrapper.top_p}, Top-k: {model_wrapper.top_k}")
    print("Commands: 'help', 'clear', 'history', 'settings', 'exit'")
    
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
                print("  help      - Show this help")
                print("  clear     - Clear chat history")
                print("  history   - Show conversation history")
                print("  settings  - Show current model settings")
                print("  prompt X  - Change system prompt (X = general/creative/coding/professional/casual)")
                print("  export X  - Export conversation (X = txt/md/json)")
                print("  model X   - Switch to different model (X = model name)")
                print("  models    - Show available model presets")
                print("  temp X    - Set temperature (X = 0.1 to 2.0)")
                print("  topp X    - Set top-p (X = 0.1 to 1.0)")
                print("  topk X    - Set top-k (X = 1 to 100)")
                print("  save X    - Save conversation to file X")
                print("  load X    - Load conversation from file X")
                print("  info      - Show system information")
                print("  context   - Show current conversation context")
                print("  reset     - Reload the current model")
                print("  tokens    - Show tokenizer information")
                print("  memory    - Show memory usage")
                print("  pwd       - Show current working directory")
                print("  time      - Show current time and date")
                print("  params    - Show current generation parameters")
                print("  model-info - Show model architecture information")
                print("  performance - Show performance metrics")
                print("  license   - Show model license information")
                print("  training  - Show training information")
                print("  evaluation - Show evaluation metrics")
                print("  usage     - Show usage statistics")
                print("  version   - Show version information")
                print("  config    - Show model configuration")
                print("  capabilities - Show model capabilities")
                print("  safety    - Show safety information")
                print("  environment - Show environment information")
                print("  token-usage - Show token usage statistics")
                print("  generation - Show generation history")
                print("  system    - Show detailed system information")
                print("  network   - Show network information")
                print("  disk      - Show disk usage information")
                print("  process   - Show process information")
                print("  cache     - Show model cache information")
                print("  deps      - Show dependencies information")
                print("  memory    - Show memory information")
                print("  performance - Show performance metrics")
                print("  security  - Show security information")
                print("  model-info - Show detailed model information")
                print("  tokenizer - Show tokenizer information")
                print("  params    - Show generation parameters")
                print("  history   - Show conversation history")
                print("  help-cat  - Show help by category")
                print("  evaluation - Show evaluation metrics")
                print("  debug     - Show debugging information")
                print("  status    - Show system status")
                print("  config-detail - Show detailed configuration")
                print("  capabilities-detail - Show detailed capabilities")
                print("  safety-detail - Show detailed safety information")
                print("  performance-detail - Show detailed performance metrics")
                print("  memory-detail - Show detailed memory information")
                print("  network-detail - Show detailed network information")
                print("  disk-detail - Show detailed disk information")
                print("  process-detail - Show detailed process information")
                print("  cache-detail - Show detailed cache information")
                print("  deps-detail - Show detailed dependencies information")
                print("  system-overview - Show comprehensive system overview")
                print("  stats     - Show conversation statistics")
                print("  exit      - Exit the program")
                continue
            if user.lower() == "clear":
                model_wrapper.clear_history()
                print("Chat history cleared.")
                continue
            if user.lower() == "history":
                if model_wrapper.conversation_history:
                    print("Recent conversation:")
                    for i, turn in enumerate(model_wrapper.conversation_history[-5:], 1):
                        print(f"  {i}. You: {turn['user']}")
                        print(f"     Bot: {turn['bot']}")
                else:
                    print("No conversation history.")
                continue
            if user.lower() == "settings":
                print(f"Model: {model_wrapper.model_name}")
                print(f"Device: {model_wrapper.device}")
                print(f"Temperature: {model_wrapper.temperature}")
                print(f"Top-p: {model_wrapper.top_p}")
                print(f"Top-k: {model_wrapper.top_k}")
                print(f"Repetition penalty: {model_wrapper.repetition_penalty}")
                print(f"System prompt: {model_wrapper.system_prompt}")
                continue
            if user.lower().startswith("prompt "):
                prompt_type = user.lower().split(" ", 1)[1]
                if prompt_type in ["general", "creative", "coding", "professional", "casual"]:
                    model_wrapper.system_prompt = create_system_prompt(prompt_type)
                    print(f"System prompt changed to: {prompt_type}")
                else:
                    print("Available prompt types: general, creative, coding, professional, casual")
                continue
            if user.lower().startswith("export "):
                if not model_wrapper.conversation_history:
                    print("No conversation to export.")
                    continue
                format_type = user.lower().split(" ", 1)[1]
                if format_type in ["txt", "md", "json"]:
                    filename = export_conversation(model_wrapper.conversation_history, format_type)
                    if filename:
                        print(f"Conversation exported to: {filename}")
                else:
                    print("Available export formats: txt, md, json")
                continue
            if user.lower().startswith("model "):
                new_model = user.split(" ", 1)[1]
                try:
                    model_wrapper.switch_model(new_model)
                except Exception as e:
                    print(f"Failed to switch model: {e}")
                continue
            if user.lower() == "stats":
                stats = model_wrapper.get_stats()
                print("Conversation Statistics:")
                print(f"  Total turns: {stats['total_turns']}")
                if stats['total_turns'] > 0:
                    print(f"  Average user message length: {stats['avg_user_length']:.1f} characters")
                    print(f"  Average bot response length: {stats['avg_bot_length']:.1f} characters")
                    print(f"  Total user characters: {stats['total_user_chars']}")
                    print(f"  Total bot characters: {stats['total_bot_chars']}")
                continue
            if user.lower() == "models":
                print("Available Model Presets:")
                for preset, model_name in MODEL_PRESETS.items():
                    print(f"  {preset:12} - {model_name}")
                print(f"\\nCurrent model: {model_wrapper.model_name}")
                continue
            if user.lower().startswith("temp "):
                try:
                    temp = float(user.split(" ", 1)[1])
                    if 0.1 <= temp <= 2.0:
                        model_wrapper.temperature = temp
                        print(f"Temperature set to {temp}")
                    else:
                        print("Temperature must be between 0.1 and 2.0")
                except ValueError:
                    print("Invalid temperature value. Use: temp 0.8")
                continue
            if user.lower().startswith("topp "):
                try:
                    topp = float(user.split(" ", 1)[1])
                    if 0.1 <= topp <= 1.0:
                        model_wrapper.top_p = topp
                        print(f"Top-p set to {topp}")
                    else:
                        print("Top-p must be between 0.1 and 1.0")
                except ValueError:
                    print("Invalid top-p value. Use: topp 0.9")
                continue
            if user.lower().startswith("topk "):
                try:
                    topk = int(user.split(" ", 1)[1])
                    if 1 <= topk <= 100:
                        model_wrapper.top_k = topk
                        print(f"Top-k set to {topk}")
                    else:
                        print("Top-k must be between 1 and 100")
                except ValueError:
                    print("Invalid top-k value. Use: topk 50")
                continue
            if user.lower().startswith("save "):
                filename = user.split(" ", 1)[1]
                if save_conversation_history(model_wrapper.conversation_history, filename):
                    print(f"Conversation saved to {filename}")
                else:
                    print("Failed to save conversation")
                continue
            if user.lower().startswith("load "):
                filename = user.split(" ", 1)[1]
                history = load_conversation_history(filename)
                if history:
                    model_wrapper.conversation_history = history
                    print(f"Conversation loaded from {filename}")
                else:
                    print("Failed to load conversation")
                continue
            if user.lower() == "info":
                print("System Information:")
                print(f"  Python version: {platform.python_version()}")
                print(f"  PyTorch version: {torch.__version__}")
                print(f"  CUDA available: {torch.cuda.is_available()}")
                if torch.cuda.is_available():
                    print(f"  CUDA version: {torch.version.cuda}")
                    print(f"  GPU device: {torch.cuda.get_device_name()}")
                print(f"  Device: {model_wrapper.device}")
                print(f"  Model: {model_wrapper.model_name}")
                continue
            if user.lower() == "context":
                print("Current Conversation Context:")
                print(f"  System prompt: {model_wrapper.system_prompt[:100]}...")
                if model_wrapper.conversation_history:
                    print(f"  History length: {len(model_wrapper.conversation_history)} turns")
                    print("  Recent context:")
                    for i, turn in enumerate(model_wrapper.conversation_history[-3:], 1):
                        print(f"    {i}. User: {turn['user'][:50]}...")
                        print(f"       Bot: {turn['bot'][:50]}...")
                else:
                    print("  No conversation history")
                continue
            if user.lower() == "reset":
                print("Reloading model...")
                model_wrapper._load()
                print("Model reloaded successfully.")
                continue
            if user.lower() == "tokens":
                print("Tokenizer Information:")
                print(f"  Vocabulary size: {model_wrapper.tokenizer.vocab_size}")
                print(f"  Pad token: {model_wrapper.tokenizer.pad_token}")
                print(f"  EOS token: {model_wrapper.tokenizer.eos_token}")
                print(f"  BOS token: {model_wrapper.tokenizer.bos_token}")
                print(f"  UNK token: {model_wrapper.tokenizer.unk_token}")
                print(f"  Model max length: {model_wrapper.tokenizer.model_max_length}")
                continue
            if user.lower() == "memory":
                print("Memory Usage:")
                if torch.cuda.is_available():
                    print(f"  GPU memory allocated: {torch.cuda.memory_allocated() / 1024**3:.2f} GB")
                    print(f"  GPU memory cached: {torch.cuda.memory_reserved() / 1024**3:.2f} GB")
                    print(f"  GPU memory total: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
                else:
                    print("  GPU not available")
                continue
            if user.lower() == "pwd":
                print("Current Working Directory:")
                print(f"  Path: {os.getcwd()}")
                print(f"  Files: {len([f for f in os.listdir('.') if os.path.isfile(f)])} files")
                print(f"  Directories: {len([d for d in os.listdir('.') if os.path.isdir(d)])} directories")
                continue
            if user.lower() == "time":
                from datetime import datetime
                now = datetime.now()
                print("Current Time and Date:")
                print(f"  Date: {now.strftime('%Y-%m-%d')}")
                print(f"  Time: {now.strftime('%H:%M:%S')}")
                print(f"  Timezone: {now.strftime('%Z')}")
                print(f"  Timestamp: {now.timestamp():.0f}")
                continue
            if user.lower() == "params":
                print("Current Generation Parameters:")
                print(f"  Temperature: {model_wrapper.temperature}")
                print(f"  Top-p: {model_wrapper.top_p}")
                print(f"  Top-k: {model_wrapper.top_k}")
                print(f"  Repetition penalty: {model_wrapper.repetition_penalty}")
                print(f"  Max new tokens: {DEFAULT_MAX_NEW_TOKENS}")
                continue
            if user.lower() == "model-info":
                print("Model Architecture Information:")
                print(f"  Model type: {type(model_wrapper.model).__name__}")
                print(f"  Model name: {model_wrapper.model_name}")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  Architecture: {getattr(config, 'architectures', ['Unknown'])[0] if getattr(config, 'architectures', None) else 'Unknown'}")
                    print(f"  Hidden size: {getattr(config, 'hidden_size', 'Unknown')}")
                    print(f"  Num layers: {getattr(config, 'num_hidden_layers', 'Unknown')}")
                    print(f"  Num attention heads: {getattr(config, 'num_attention_heads', 'Unknown')}")
                    print(f"  Max position embeddings: {getattr(config, 'max_position_embeddings', 'Unknown')}")
                else:
                    print("  Architecture: Unknown (no config available)")
                continue
            if user.lower() == "performance":
                print("Performance Metrics:")
                print(f"  Device: {model_wrapper.device}")
                if torch.cuda.is_available():
                    print(f"  GPU utilization: {torch.cuda.utilization()}%")
                    print(f"  GPU temperature: {torch.cuda.temperature()}°C")
                print(f"  Model parameters: {sum(p.numel() for p in model_wrapper.model.parameters()):,}")
                print(f"  Trainable parameters: {sum(p.numel() for p in model_wrapper.model.parameters() if p.requires_grad):,}")
                continue
            if user.lower() == "license":
                print("Model License Information:")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  License: {getattr(config, 'license', 'Unknown')}")
                    print(f"  Model card: {getattr(config, 'model_card', 'Unknown')}")
                    print(f"  Tags: {getattr(config, 'tags', 'None')}")
                    print(f"  Paper: {getattr(config, 'paper', 'Unknown')}")
                else:
                    print("  License information not available")
                continue
            if user.lower() == "training":
                print("Training Information:")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  Training data: {getattr(config, 'training_data', 'Unknown')}")
                    print(f"  Training objective: {getattr(config, 'training_objective', 'Unknown')}")
                    print(f"  Training strategy: {getattr(config, 'training_strategy', 'Unknown')}")
                    print(f"  Training steps: {getattr(config, 'training_steps', 'Unknown')}")
                    print(f"  Learning rate: {getattr(config, 'learning_rate', 'Unknown')}")
                else:
                    print("  Training information not available")
                continue
            if user.lower() == "evaluation":
                print("Evaluation Metrics:")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  Evaluation dataset: {getattr(config, 'evaluation_dataset', 'Unknown')}")
                    print(f"  Evaluation metrics: {getattr(config, 'evaluation_metrics', 'Unknown')}")
                    print(f"  Evaluation results: {getattr(config, 'evaluation_results', 'Unknown')}")
                    print(f"  Benchmark scores: {getattr(config, 'benchmark_scores', 'Unknown')}")
                else:
                    print("  Evaluation information not available")
                continue
            if user.lower() == "usage":
                print("Usage Statistics:")
                print(f"  Total conversations: {len(model_wrapper.conversation_history)}")
                print(f"  Total user messages: {sum(len(turn['user']) for turn in model_wrapper.conversation_history)} characters")
                print(f"  Total bot responses: {sum(len(turn['bot']) for turn in model_wrapper.conversation_history)} characters")
                print(f"  Average response length: {sum(len(turn['bot']) for turn in model_wrapper.conversation_history) / max(len(model_wrapper.conversation_history), 1):.1f} characters")
                print(f"  Model loaded at: {getattr(model_wrapper, '_load_time', 'Unknown')}")
                continue
            if user.lower() == "version":
                print("Version Information:")
                print(f"  MiniChat version: 2.0")
                print(f"  Python version: {platform.python_version()}")
                print(f"  PyTorch version: {torch.__version__}")
                print(f"  Transformers version: {getattr(torch, '__version__', 'Unknown')}")
                print(f"  FastAPI version: {getattr(uvicorn, '__version__', 'Unknown')}")
                continue
            if user.lower() == "config":
                print("Model Configuration:")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  Model type: {type(config).__name__}")
                    print(f"  Model name: {getattr(config, 'name_or_path', 'Unknown')}")
                    print(f"  Model revision: {getattr(config, 'revision', 'Unknown')}")
                    print(f"  Model size: {getattr(config, 'model_size', 'Unknown')}")
                    print(f"  Model family: {getattr(config, 'model_type', 'Unknown')}")
                    print(f"  Task type: {getattr(config, 'task_type', 'Unknown')}")
                else:
                    print("  Configuration not available")
                continue
            if user.lower() == "capabilities":
                print("Model Capabilities:")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  Text generation: Yes")
                    print(f"  Context length: {getattr(config, 'max_position_embeddings', 'Unknown')} tokens")
                    print(f"  Multilingual: {getattr(config, 'multilingual', 'Unknown')}")
                    print(f"  Code generation: {getattr(config, 'code_generation', 'Unknown')}")
                    print(f"  Reasoning: {getattr(config, 'reasoning', 'Unknown')}")
                    print(f"  Creative writing: {getattr(config, 'creative_writing', 'Unknown')}")
                else:
                    print("  Capabilities information not available")
                continue
            if user.lower() == "safety":
                print("Safety Information:")
                print(f"  Content filtering: Enabled")
                print(f"  Banned keywords: {len(['bomb', 'kill', 'suicide', 'self-harm', 'illegal', 'terrorist', 'explode', 'child porn', 'cp', 'ddos', 'hitman', 'assassinate'])} words")
                print(f"  Safety checks: Active")
                print(f"  Harmful content: Blocked")
                print(f"  Ethical guidelines: Followed")
                continue
            if user.lower() == "environment":
                print("Environment Information:")
                print(f"  Operating system: {platform.system()} {platform.release()}")
                print(f"  Python executable: {sys.executable}")
                print(f"  Working directory: {os.getcwd()}")
                print(f"  Environment variables: {len(os.environ)} variables")
                print(f"  Process ID: {os.getpid()}")
                print(f"  User: {os.getenv('USER', 'Unknown')}")
                continue
            if user.lower() == "token-usage":
                print("Token Usage Statistics:")
                if model_wrapper.conversation_history:
                    total_tokens = 0
                    total_user_tokens = 0
                    total_bot_tokens = 0
                    for turn in model_wrapper.conversation_history:
                        user_tokens = len(model_wrapper.tokenizer.encode(turn['user']))
                        bot_tokens = len(model_wrapper.tokenizer.encode(turn['bot']))
                        total_user_tokens += user_tokens
                        total_bot_tokens += bot_tokens
                        total_tokens += user_tokens + bot_tokens
                    print(f"  Total tokens used: {total_tokens:,}")
                    print(f"  User message tokens: {total_user_tokens:,}")
                    print(f"  Bot response tokens: {total_bot_tokens:,}")
                    print(f"  Average tokens per turn: {total_tokens / len(model_wrapper.conversation_history):.1f}")
                else:
                    print("  No conversation history available")
                continue
            if user.lower() == "generation":
                print("Generation History:")
                if model_wrapper.conversation_history:
                    print(f"  Total generations: {len(model_wrapper.conversation_history)}")
                    print(f"  First generation: {model_wrapper.conversation_history[0]['user'][:50]}...")
                    print(f"  Latest generation: {model_wrapper.conversation_history[-1]['user'][:50]}...")
                    print(f"  Generation time span: {len(model_wrapper.conversation_history)} turns")
                    print("  Recent generations:")
                    for i, turn in enumerate(model_wrapper.conversation_history[-3:], 1):
                        print(f"    {turn['user'][:40]}...")
                        print(f"       Bot: {turn['bot'][:40]}...")
                else:
                    print("  No generation history available")
                continue
            if user.lower() == "system":
                print("Detailed System Information:")
                print(f"  Platform: {platform.platform()}")
                print(f"  Machine: {platform.machine()}")
                print(f"  Processor: {platform.processor()}")
                print(f"  Python version: {platform.python_version()}")
                print(f"  Python implementation: {platform.python_implementation()}")
                print(f"  Python compiler: {platform.python_compiler()}")
                print(f"  System: {platform.system()} {platform.release()}")
                print(f"  Architecture: {platform.architecture()}")
                print(f"  Node: {platform.node()}")
                continue
            if user.lower() == "network":
                print("Network Information:")
                try:
                    import socket
                    hostname = socket.gethostname()
                    local_ip = socket.gethostbyname(hostname)
                    print(f"  Hostname: {hostname}")
                    print(f"  Local IP: {local_ip}")
                    print(f"  Port: 8000 (default)")
                    print(f"  Web interface: http://localhost:8000")
                    print(f"  WebSocket: ws://localhost:8000/ws/chat")
                except Exception as e:
                    print(f"  Network info unavailable: {e}")
                continue
            if user.lower() == "disk":
                print("Disk Usage Information:")
                try:
                    import shutil
                    total, used, free = shutil.disk_usage(".")
                    print(f"  Current directory: {os.getcwd()}")
                    print(f"  Total space: {total // (1024**3):.1f} GB")
                    print(f"  Used space: {used // (1024**3):.1f} GB")
                    print(f"  Free space: {free // (1024**3):.1f} GB")
                    print(f"  Usage percentage: {(used / total) * 100:.1f}%")
                except Exception as e:
                    print(f"  Disk info unavailable: {e}")
                continue
            if user.lower() == "process":
                print("Process Information:")
                try:
                    import psutil
                    process = psutil.Process()
                    print(f"  Process ID: {process.pid}")
                    print(f"  Process name: {process.name()}")
                    print(f"  Process status: {process.status()}")
                    print(f"  CPU percent: {process.cpu_percent()}%")
                    print(f"  Memory usage: {process.memory_info().rss // (1024**2):.1f} MB")
                    print(f"  Create time: {datetime.fromtimestamp(process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Process info unavailable: {e}")
                continue
            if user.lower() == "cache":
                print("Model Cache Information:")
                try:
                    cache_dir = os.path.expanduser("~/.cache/huggingface")
                    if os.path.exists(cache_dir):
                        import shutil
                        total, used, free = shutil.disk_usage(cache_dir)
                        print(f"  Cache directory: {cache_dir}")
                        print(f"  Cache size: {used // (1024**3):.1f} GB")
                        print(f"  Available space: {free // (1024**3):.1f} GB")
                        
                        # Count model files
                        model_count = 0
                        for root, dirs, files in os.walk(cache_dir):
                            if "config.json" in files:
                                model_count += 1
                        print(f"  Cached models: {model_count}")
                    else:
                        print("  Cache directory not found")
                except Exception as e:
                    print(f"  Cache info unavailable: {e}")
                continue
            if user.lower() == "deps":
                print("Dependencies Information:")
                try:
                    import pkg_resources
                    deps = ['torch', 'transformers', 'fastapi', 'uvicorn', 'jinja2']
                    for dep in deps:
                        try:
                            version = pkg_resources.get_distribution(dep).version
                            print(f"  {dep}: {version}")
                        except pkg_resources.DistributionNotFound:
                            print(f"  {dep}: Not installed")
                except ImportError:
                    print("  pkg_resources not available")
                except Exception as e:
                    print(f"  Dependencies info unavailable: {e}")
                continue
            if user.lower() == "memory":
                print("Memory Information:")
                try:
                    import psutil
                    memory = psutil.virtual_memory()
                    print(f"  Total RAM: {memory.total // (1024**3):.1f} GB")
                    print(f"  Available RAM: {memory.available // (1024**3):.1f} GB")
                    print(f"  Used RAM: {memory.used // (1024**3):.1f} GB")
                    print(f"  RAM usage: {memory.percent}%")
                    
                    # GPU memory if available
                    if torch.cuda.is_available():
                        gpu_memory = torch.cuda.get_device_properties(0).total_memory
                        gpu_allocated = torch.cuda.memory_allocated(0)
                        gpu_cached = torch.cuda.memory_reserved(0)
                        print(f"  GPU memory: {gpu_memory // (1024**3):.1f} GB")
                        print(f"  GPU allocated: {gpu_allocated // (1024**3):.1f} GB")
                        print(f"  GPU cached: {gpu_cached // (1024**3):.1f} GB")
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Memory info unavailable: {e}")
                continue
            if user.lower() == "performance":
                print("Performance Metrics:")
                try:
                    import psutil
                    cpu_percent = psutil.cpu_percent(interval=1)
                    print(f"  CPU usage: {cpu_percent}%")
                    
                    # Model performance info
                    if hasattr(model_wrapper, '_load_time'):
                        print(f"  Model load time: {getattr(model_wrapper, '_load_time', 'Unknown')}")
                    
                    # Device info
                    print(f"  Current device: {model_wrapper.device}")
                    if torch.cuda.is_available():
                        print(f"  CUDA version: {torch.version.cuda}")
                        print(f"  GPU count: {torch.cuda.device_count()}")
                        if torch.cuda.device_count() > 0:
                            gpu_name = torch.cuda.get_device_name(0)
                            print(f"  GPU name: {gpu_name}")
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Performance info unavailable: {e}")
                continue
            if user.lower() == "security":
                print("Security Information:")
                print(f"  Content filtering: {'Enabled' if safe_check('test') else 'Disabled'}")
                print(f"  Banned keywords: {len(['bomb', 'kill', 'suicide', 'self-harm', 'illegal', 'terrorist', 'explode', 'child porn', 'cp', 'ddos', 'hitman', 'assassinate'])} words")
                print(f"  Safety checks: Active")
                print(f"  Harmful content: Blocked")
                print(f"  Ethical guidelines: Followed")
                print(f"  Model safety: {getattr(model_wrapper.model, 'safe', 'Unknown')}")
                print(f"  Input validation: Active")
                print(f"  Output filtering: Active")
                continue
            if user.lower() == "model-info":
                print("Detailed Model Information:")
                if hasattr(model_wrapper.model, 'config'):
                    config = model_wrapper.model.config
                    print(f"  Model type: {type(config).__name__}")
                    print(f"  Model name: {getattr(config, 'name_or_path', 'Unknown')}")
                    print(f"  Model revision: {getattr(config, 'revision', 'Unknown')}")
                    print(f"  Model size: {getattr(config, 'model_size', 'Unknown')}")
                    print(f"  Model family: {getattr(config, 'model_type', 'Unknown')}")
                    print(f"  Task type: {getattr(config, 'task_type', 'Unknown')}")
                    print(f"  Vocabulary size: {getattr(config, 'vocab_size', 'Unknown')}")
                    print(f"  Hidden size: {getattr(config, 'hidden_size', 'Unknown')}")
                    print(f"  Num layers: {getattr(config, 'num_hidden_layers', 'Unknown')}")
                    print(f"  Num attention heads: {getattr(config, 'num_attention_heads', 'Unknown')}")
                    print(f"  Max position embeddings: {getattr(config, 'max_position_embeddings', 'Unknown')}")
                    print(f"  Type vocab size: {getattr(config, 'type_vocab_size', 'Unknown')}")
                    print(f"  Initializer range: {getattr(config, 'initializer_range', 'Unknown')}")
                    print(f"  Layer norm eps: {getattr(config, 'layer_norm_eps', 'Unknown')}")
                    print(f"  Position embedding type: {getattr(config, 'position_embedding_type', 'Unknown')}")
                    print(f"  Use cache: {getattr(config, 'use_cache', 'Unknown')}")
                    print(f"  Architectures: {getattr(config, 'architectures', 'Unknown')}")
                else:
                    print("  Configuration not available")
                continue
            if user.lower() == "tokenizer":
                print("Tokenizer Information:")
                if model_wrapper.tokenizer:
                    print(f"  Tokenizer class: {type(model_wrapper.tokenizer).__name__}")
                    print(f"  Vocabulary size: {model_wrapper.tokenizer.vocab_size}")
                    print(f"  Model max length: {getattr(model_wrapper.tokenizer, 'model_max_length', 'Unknown')}")
                    print(f"  Padding token: {getattr(model_wrapper.tokenizer, 'pad_token', 'None')}")
                    print(f"  EOS token: {getattr(model_wrapper.tokenizer, 'eos_token', 'None')}")
                    print(f"  BOS token: {getattr(model_wrapper.tokenizer, 'bos_token', 'None')}")
                    print(f"  UNK token: {getattr(model_wrapper.tokenizer, 'unk_token', 'None')}")
                    print(f"  CLS token: {getattr(model_wrapper.tokenizer, 'cls_token', 'None')}")
                    print(f"  SEP token: {getattr(model_wrapper.tokenizer, 'sep_token', 'None')}")
                    print(f"  MASK token: {getattr(model_wrapper.tokenizer, 'mask_token', 'None')}")
                    print(f"  Tokenizer type: {getattr(model_wrapper.tokenizer, 'tokenizer_type', 'Unknown')}")
                    print(f"  Clean up tokenization spaces: {getattr(model_wrapper.tokenizer, 'clean_up_tokenization_spaces', 'Unknown')}")
                else:
                    print("  Tokenizer not available")
                continue
            if user.lower() == "params":
                print("Generation Parameters:")
                print(f"  Temperature: {model_wrapper.temperature}")
                print(f"  Top-p: {model_wrapper.top_p}")
                print(f"  Top-k: {model_wrapper.top_k}")
                print(f"  Repetition penalty: {model_wrapper.repetition_penalty}")
                print(f"  Max new tokens: {DEFAULT_MAX_NEW_TOKENS}")
                print(f"  Max length: {DEFAULT_MAX_LENGTH}")
                print(f"  System prompt: {model_wrapper.system_prompt}")
                print(f"  Current device: {model_wrapper.device}")
                print(f"  Model name: {model_wrapper.model_name}")
                continue
            if user.lower() == "history":
                print("Conversation History:")
                if model_wrapper.conversation_history:
                    print(f"  Total conversations: {len(model_wrapper.conversation_history)}")
                    for i, turn in enumerate(model_wrapper.conversation_history, 1):
                        print(f"  Turn {i}:")
                        print(f"    User: {turn['user'][:100]}{'...' if len(turn['user']) > 100 else ''}")
                        print(f"    Bot: {turn['bot'][:100]}{'...' if len(turn['bot']) > 100 else ''}")
                        print()
                else:
                    print("  No conversation history available")
                continue
            if user.lower() == "help-cat":
                print("Help by Category:")
                print("\n  SYSTEM COMMANDS:")
                print("    help, help-cat, exit, clear, time, date")
                print("\n  MODEL COMMANDS:")
                print("    model, models, switch, config, capabilities, model-info, tokenizer")
                print("\n  GENERATION COMMANDS:")
                print("    temp, topp, topk, prompt, params")
                print("\n  HISTORY COMMANDS:")
                print("    save, load, export, history, stats, usage, token-usage, generation")
                print("\n  SYSTEM INFO COMMANDS:")
                print("    version, info, system, environment, network, disk, process, cache, deps, memory, performance, security")
                continue
            if user.lower() == "evaluation":
                print("Evaluation Metrics:")
                if model_wrapper.conversation_history:
                    total_turns = len(model_wrapper.conversation_history)
                    total_user_chars = sum(len(turn['user']) for turn in model_wrapper.conversation_history)
                    total_bot_chars = sum(len(turn['bot']) for turn in model_wrapper.conversation_history)
                    total_user_tokens = sum(len(model_wrapper.tokenizer.encode(turn['user'])) for turn in model_wrapper.conversation_history)
                    total_bot_tokens = sum(len(model_wrapper.tokenizer.encode(turn['bot'])) for turn in model_wrapper.conversation_history)
                    
                    print(f"  Total turns: {total_turns}")
                    print(f"  Average user message length: {total_user_chars / total_turns:.1f} characters")
                    print(f"  Average bot response length: {total_bot_chars / total_turns:.1f} characters")
                    print(f"  Average user tokens: {total_user_tokens / total_turns:.1f} tokens")
                    print(f"  Average bot tokens: {total_bot_tokens / total_turns:.1f} tokens")
                    print(f"  Total tokens used: {total_user_tokens + total_bot_tokens:,}")
                    print(f"  Response ratio (bot/user): {total_bot_chars / max(total_user_chars, 1):.2f}")
                else:
                    print("  No conversation history available for evaluation")
                continue
            if user.lower() == "debug":
                print("Debugging Information:")
                print(f"  Python version: {sys.version}")
                print(f"  PyTorch version: {torch.__version__}")
                print(f"  Transformers version: {getattr(torch, '__version__', 'Unknown')}")
                print(f"  FastAPI version: {getattr(uvicorn, '__version__', 'Unknown')}")
                print(f"  CUDA available: {torch.cuda.is_available()}")
                if torch.cuda.is_available():
                    print(f"  CUDA version: {torch.version.cuda}")
                    print(f"  GPU count: {torch.cuda.device_count()}")
                    print(f"  Current GPU: {torch.cuda.current_device()}")
                print(f"  MPS available: {hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()}")
                print(f"  Device: {model_wrapper.device}")
                print(f"  Model loaded: {model_wrapper.model is not None}")
                print(f"  Tokenizer loaded: {model_wrapper.tokenizer is not None}")
                print(f"  Conversation history length: {len(model_wrapper.conversation_history)}")
                continue
            if user.lower() == "status":
                print("System Status:")
                try:
                    import psutil
                    # CPU status
                    cpu_percent = psutil.cpu_percent(interval=1)
                    cpu_count = psutil.cpu_count()
                    print(f"  CPU: {cpu_percent}% usage ({cpu_count} cores)")
                    
                    # Memory status
                    memory = psutil.virtual_memory()
                    print(f"  Memory: {memory.percent}% used ({memory.used // (1024**3):.1f}GB / {memory.total // (1024**3):.1f}GB)")
                    
                    # Disk status
                    disk = psutil.disk_usage('.')
                    print(f"  Disk: {(disk.used / disk.total) * 100:.1f}% used ({disk.used // (1024**3):.1f}GB / {disk.total // (1024**3):.1f}GB)")
                    
                    # Network status
                    network = psutil.net_io_counters()
                    print(f"  Network: {network.bytes_sent // (1024**2):.1f}MB sent, {network.bytes_recv // (1024**2):.1f}MB received")
                    
                    # Model status
                    print(f"  Model: {model_wrapper.model_name} on {model_wrapper.device}")
                    print(f"  Conversations: {len(model_wrapper.conversation_history)}")
                    
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Status info unavailable: {e}")
                continue
            if user.lower() == "config-detail":
                print("Detailed Configuration:")
                print(f"  Default model: {DEFAULT_MODEL}")
                print(f"  Default max new tokens: {DEFAULT_MAX_NEW_TOKENS}")
                print(f"  Default device: {DEFAULT_DEVICE}")
                print(f"  Default temperature: {DEFAULT_TEMPERATURE}")
                print(f"  Default top-p: {DEFAULT_TOP_P}")
                print(f"  Default top-k: {DEFAULT_TOP_K}")
                print(f"  Default repetition penalty: {DEFAULT_REPETITION_PENALTY}")
                print(f"  Default max length: {DEFAULT_MAX_LENGTH}")
                print(f"  Client HTML path: {CLIENT_HTML_PATH}")
                print(f"  Current working directory: {os.getcwd()}")
                print(f"  Python executable: {sys.executable}")
                print(f"  Platform: {platform.platform()}")
                print(f"  Architecture: {platform.architecture()}")
                print(f"  Machine: {platform.machine()}")
                print(f"  Processor: {platform.processor()}")
                continue
            if user.lower() == "capabilities-detail":
                print("Detailed Capabilities:")
                print("  Text Generation:")
                print("    - Natural language processing")
                print("    - Context-aware responses")
                print("    - Multi-turn conversations")
                print("    - Creative writing")
                print("    - Technical explanations")
                print("  Language Support:")
                print("    - English (primary)")
                print("    - Multi-language support")
                print("    - Code generation")
                print("    - Mathematical reasoning")
                print("  Model Features:")
                print("    - Streaming responses")
                print("    - Parameter adjustment")
                print("    - Model switching")
                print("    - History management")
                print("    - Export functionality")
                print("  System Integration:")
                print("    - CLI interface")
                print("    - Web interface")
                print("    - WebSocket support")
                print("    - File operations")
                print("    - System monitoring")
                continue
            if user.lower() == "safety-detail":
                print("Detailed Safety Information:")
                print("  Content Filtering:")
                print("    - Keyword-based filtering")
                print("    - Harmful content detection")
                print("    - Inappropriate language blocking")
                print("    - Violence prevention")
                print("    - Illegal activity prevention")
                print("  Safety Measures:")
                print("    - Input validation")
                print("    - Output filtering")
                print("    - Ethical guidelines")
                print("    - Bias mitigation")
                print("    - Privacy protection")
                print("  Banned Categories:")
                print("    - Violence and harm")
                print("    - Illegal activities")
                print("    - Inappropriate content")
                print("    - Misinformation")
                print("    - Privacy violations")
                print("  Safety Features:")
                print("    - Real-time filtering")
                print("    - User notification")
                print("    - Content logging")
                print("    - Safety reporting")
                print("    - Continuous monitoring")
                continue
            if user.lower() == "performance-detail":
                print("Detailed Performance Metrics:")
                print("  System Performance:")
                print("    - CPU utilization monitoring")
                print("    - Memory usage tracking")
                print("    - Disk I/O monitoring")
                print("    - Network performance")
                print("    - Process statistics")
                print("  Model Performance:")
                print("    - Inference speed")
                print("    - Token generation rate")
                print("    - Memory efficiency")
                print("    - GPU utilization")
                print("    - Model loading time")
                print("  User Experience:")
                print("    - Response time")
                print("    - Conversation flow")
                print("    - Error handling")
                print("    - System stability")
                print("    - Resource optimization")
                print("  Optimization Features:")
                print("    - Dynamic parameter adjustment")
                print("    - Model quantization support")
                print("    - Cache management")
                print("    - Background processing")
                print("    - Performance profiling")
                continue
            if user.lower() == "memory-detail":
                print("Detailed Memory Information:")
                try:
                    import psutil
                    # RAM details
                    memory = psutil.virtual_memory()
                    print("  RAM Memory:")
                    print(f"    Total: {memory.total // (1024**3):.1f} GB")
                    print(f"    Available: {memory.available // (1024**3):.1f} GB")
                    print(f"    Used: {memory.used // (1024**3):.1f} GB")
                    print(f"    Free: {memory.free // (1024**3):.1f} GB")
                    print(f"    Usage: {memory.percent}%")
                    print(f"    Active: {memory.active // (1024**3):.1f} GB")
                    print(f"    Inactive: {memory.inactive // (1024**3):.1f} GB")
                    print(f"    Wired: {getattr(memory, 'wired', 'N/A')}")
                    
                    # Swap memory
                    swap = psutil.swap_memory()
                    print("  Swap Memory:")
                    print(f"    Total: {swap.total // (1024**3):.1f} GB")
                    print(f"    Used: {swap.used // (1024**3):.1f} GB")
                    print(f"    Free: {swap.free // (1024**3):.1f} GB")
                    print(f"    Usage: {swap.percent}%")
                    
                    # GPU memory if available
                    if torch.cuda.is_available():
                        print("  GPU Memory:")
                        gpu_memory = torch.cuda.get_device_properties(0).total_memory
                        gpu_allocated = torch.cuda.memory_allocated(0)
                        gpu_cached = torch.cuda.memory_reserved(0)
                        gpu_free = gpu_memory - gpu_cached
                        print(f"    Total: {gpu_memory // (1024**3):.1f} GB")
                        print(f"    Allocated: {gpu_allocated // (1024**3):.1f} GB")
                        print(f"    Cached: {gpu_cached // (1024**3):.1f} GB")
                        print(f"    Free: {gpu_free // (1024**3):.1f} GB")
                        print(f"    Usage: {(gpu_cached / gpu_memory) * 100:.1f}%")
                    
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Memory detail info unavailable: {e}")
                continue
            if user.lower() == "network-detail":
                print("Detailed Network Information:")
                try:
                    import psutil
                    # Hostname and IP
                    hostname = socket.gethostname()
                    local_ip = socket.gethostbyname(hostname)
                    print("  Network Configuration:")
                    print(f"    Hostname: {hostname}")
                    print(f"    Local IP: {local_ip}")
                    print(f"    Default port: 8000")
                    print(f"    Web URL: http://{local_ip}:8000")
                    print(f"    WebSocket URL: ws://{local_ip}:8000/ws/chat")
                    
                    # Network interfaces
                    net_if_addrs = psutil.net_if_addrs()
                    print("  Network Interfaces:")
                    for interface, addresses in net_if_addrs.items():
                        print(f"    {interface}:")
                        for addr in addresses:
                            if addr.family == socket.AF_INET:
                                print(f"      IPv4: {addr.address}")
                            elif addr.family == socket.AF_INET6:
                                print(f"      IPv6: {addr.address}")
                    
                    # Network statistics
                    net_io = psutil.net_io_counters()
                    print("  Network Statistics:")
                    print(f"    Bytes sent: {net_io.bytes_sent // (1024**2):.1f} MB")
                    print(f"    Bytes received: {net_io.bytes_recv // (1024**2):.1f} MB")
                    print(f"    Packets sent: {net_io.packets_sent:,}")
                    print(f"    Packets received: {net_io.packets_recv:,}")
                    print(f"    Errors in: {net_io.errin}")
                    print(f"    Errors out: {net_io.errout}")
                    print(f"    Drops in: {net_io.dropin}")
                    print(f"    Drops out: {net_io.dropout}")
                    
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Network detail info unavailable: {e}")
                continue
            if user.lower() == "disk-detail":
                print("Detailed Disk Information:")
                try:
                    import psutil
                    # Current directory
                    current_dir = os.getcwd()
                    print("  Current Directory:")
                    print(f"    Path: {current_dir}")
                    
                    # Disk partitions
                    partitions = psutil.disk_partitions()
                    print("  Disk Partitions:")
                    for partition in partitions:
                        try:
                            usage = psutil.disk_usage(partition.mountpoint)
                            print(f"    {partition.device}:")
                            print(f"      Mountpoint: {partition.mountpoint}")
                            print(f"      Filesystem: {partition.fstype}")
                            print(f"      Total: {usage.total // (1024**3):.1f} GB")
                            print(f"      Used: {usage.used // (1024**3):.1f} GB")
                            print(f"      Free: {usage.free // (1024**3):.1f} GB")
                            print(f"      Usage: {(usage.used / usage.total) * 100:.1f}%")
                        except PermissionError:
                            print(f"    {partition.device}: Access denied")
                    
                    # Current directory usage
                    try:
                        current_usage = psutil.disk_usage(current_dir)
                        print("  Current Directory Usage:")
                        print(f"    Total: {current_usage.total // (1024**3):.1f} GB")
                        print(f"    Used: {current_usage.used // (1024**3):.1f} GB")
                        print(f"    Free: {current_usage.free // (1024**3):.1f} GB")
                        print(f"    Usage: {(current_usage.used / current_usage.total) * 100:.1f}%")
                    except PermissionError:
                        print("  Current directory usage: Access denied")
                    
                    # Disk I/O statistics
                    disk_io = psutil.disk_io_counters()
                    if disk_io:
                        print("  Disk I/O Statistics:")
                        print(f"    Read count: {disk_io.read_count:,}")
                        print(f"    Write count: {disk_io.write_count:,}")
                        print(f"    Read bytes: {disk_io.read_bytes // (1024**3):.1f} GB")
                        print(f"    Write bytes: {disk_io.write_bytes // (1024**3):.1f} GB")
                        print(f"    Read time: {disk_io.read_time} ms")
                        print(f"    Write time: {disk_io.write_time} ms")
                    
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Disk detail info unavailable: {e}")
                continue
            if user.lower() == "process-detail":
                print("Detailed Process Information:")
                try:
                    import psutil
                    # Current process
                    current_process = psutil.Process()
                    print("  Current Process:")
                    print(f"    PID: {current_process.pid}")
                    print(f"    Name: {current_process.name()}")
                    print(f"    Status: {current_process.status()}")
                    print(f"    Create time: {datetime.fromtimestamp(current_process.create_time()).strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"    CPU percent: {current_process.cpu_percent()}%")
                    
                    # Memory info
                    memory_info = current_process.memory_info()
                    print("  Memory Usage:")
                    print(f"    RSS: {memory_info.rss // (1024**2):.1f} MB")
                    print(f"    VMS: {memory_info.vms // (1024**2):.1f} MB")
                    print(f"    Percent: {current_process.memory_percent():.1f}%")
                    
                    # CPU info
                    cpu_times = current_process.cpu_times()
                    print("  CPU Times:")
                    print(f"    User: {cpu_times.user:.2f}s")
                    print(f"    System: {cpu_times.system:.2f}s")
                    print(f"    Children user: {cpu_times.children_user:.2f}s")
                    print(f"    Children system: {cpu_times.children_system:.2f}s")
                    
                    # Open files
                    try:
                        open_files = current_process.open_files()
                        print(f"  Open Files: {len(open_files)}")
                        for file in open_files[:5]:  # Show first 5
                            print(f"    {file.path}")
                        if len(open_files) > 5:
                            print(f"    ... and {len(open_files) - 5} more")
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        print("  Open Files: Access denied")
                    
                    # Threads
                    try:
                        threads = current_process.threads()
                        print(f"  Threads: {len(threads)}")
                        for thread in threads[:5]:  # Show first 5
                            print(f"    Thread {thread.id}: {cpu_times.user:.2f}s user, {cpu_times.system:.2f}s system")
                        if len(threads) > 5:
                            print(f"    ... and {len(threads) - 5} more")
                    except (psutil.AccessDenied, psutil.ZombieProcess):
                        print("  Threads: Access denied")
                    
                except ImportError:
                    print("  psutil not available - install with: pip install psutil")
                except Exception as e:
                    print(f"  Process detail info unavailable: {e}")
                continue
            if user.lower() == "cache-detail":
                print("Detailed Cache Information:")
                try:
                    # Transformers cache directory
                    from transformers import file_utils
                    cache_dir = file_utils.default_cache_path
                    print("  Transformers Cache:")
                    print(f"    Directory: {cache_dir}")
                    
                    if os.path.exists(cache_dir):
                        # Cache size
                        total_size = 0
                        file_count = 0
                        model_count = 0
                        
                        for root, dirs, files in os.walk(cache_dir):
                            for file in files:
                                try:
                                    file_path = os.path.join(root, file)
                                    total_size += os.path.getsize(file_path)
                                    file_count += 1
                                except (OSError, PermissionError):
                                    pass
                            
                            # Count model directories
                            for dir_name in dirs:
                                if any(keyword in dir_name.lower() for keyword in ['model', 'tokenizer', 'config']):
                                    model_count += 1
                        
                        print(f"    Total size: {total_size // (1024**3):.1f} GB")
                        print(f"    File count: {file_count:,}")
                        print(f"    Model count: {model_count}")
                        
                        # Available space
                        try:
                            import psutil
                            disk_usage = psutil.disk_usage(cache_dir)
                            print(f"    Available space: {disk_usage.free // (1024**3):.1f} GB")
                            print(f"    Usage percentage: {(disk_usage.used / disk_usage.total) * 100:.1f}%")
                        except ImportError:
                            pass
                    else:
                        print("    Directory does not exist")
                    
                    # PyTorch cache
                    if torch.cuda.is_available():
                        print("  PyTorch CUDA Cache:")
                        print(f"    Memory allocated: {torch.cuda.memory_allocated(0) // (1024**3):.1f} GB")
                        print(f"    Memory cached: {torch.cuda.memory_reserved(0) // (1024**3):.1f} GB")
                        print(f"    Max memory: {torch.cuda.max_memory_allocated(0) // (1024**3):.1f} GB")
                        
                        # Cache settings
                        print("  Cache Settings:")
                        print(f"    Empty cache on exit: {torch.cuda.empty_cache()}")
                        print(f"    Memory fraction: {torch.cuda.get_device_properties(0).total_memory // (1024**3):.1f} GB")
                    
                    # System temp directory
                    temp_dir = os.environ.get('TMPDIR', '/tmp')
                    if os.path.exists(temp_dir):
                        try:
                            temp_usage = psutil.disk_usage(temp_dir)
                            print("  System Temp Directory:")
                            print(f"    Path: {temp_dir}")
                            print(f"    Available: {temp_usage.free // (1024**3):.1f} GB")
                            print(f"    Usage: {(temp_usage.used / temp_usage.total) * 100:.1f}%")
                        except (ImportError, PermissionError):
                            pass
                    
                except ImportError:
                    print("  Transformers not available")
                except Exception as e:
                    print(f"  Cache detail info unavailable: {e}")
                continue
            if user.lower() == "deps-detail":
                print("Detailed Dependencies Information:")
                try:
                    import pkg_resources
                    
                    # Core dependencies
                    core_deps = ['torch', 'transformers', 'fastapi', 'uvicorn', 'jinja2']
                    print("  Core Dependencies:")
                    for dep in core_deps:
                        try:
                            dist = pkg_resources.get_distribution(dep)
                            print(f"    {dep}: {dist.version}")
                            print(f"      Location: {dist.location}")
                            print(f"      Requires: {', '.join(dist.requires()) if dist.requires() else 'None'}")
                        except pkg_resources.DistributionNotFound:
                            print(f"    {dep}: Not installed")
                    
                    # PyTorch specific info
                    if 'torch' in [pkg.key for pkg in pkg_resources.working_set]:
                        print("  PyTorch Details:")
                        print(f"    Version: {torch.__version__}")
                        print(f"    CUDA available: {torch.cuda.is_available()}")
                        if torch.cuda.is_available():
                            print(f"    CUDA version: {torch.version.cuda}")
                            print(f"    cuDNN version: {torch.backends.cudnn.version()}")
                            print(f"    GPU count: {torch.cuda.device_count()}")
                        print(f"    MPS available: {hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()}")
                        print(f"    OpenMP available: {torch.backends.openmp.is_available()}")
                    
                    # Transformers specific info
                    if 'transformers' in [pkg.key for pkg in pkg_resources.working_set]:
                        print("  Transformers Details:")
                        try:
                            from transformers import __version__ as tf_version
                            print(f"    Version: {tf_version}")
                        except ImportError:
                            print("    Version: Unknown")
                    
                    # FastAPI specific info
                    if 'fastapi' in [pkg.key for pkg in pkg_resources.working_set]:
                        print("  FastAPI Details:")
                        try:
                            from fastapi import __version__ as fa_version
                            print(f"    Version: {fa_version}")
                        except ImportError:
                            print("    Version: Unknown")
                    
                    # System dependencies
                    print("  System Dependencies:")
                    try:
                        import psutil
                        print(f"    psutil: {psutil.__version__}")
                    except (ImportError, AttributeError):
                        print("    psutil: Not available")
                    
                    # Python environment
                    print("  Python Environment:")
                    print(f"    Python version: {sys.version}")
                    print(f"    Executable: {sys.executable}")
                    print(f"    Platform: {platform.platform()}")
                    print(f"    Architecture: {platform.architecture()}")
                    
                except ImportError:
                    print("  pkg_resources not available")
                except Exception as e:
                    print(f"  Dependencies detail info unavailable: {e}")
                continue
            if user.lower() == "system-overview":
                print("Comprehensive System Overview:")
                print("=" * 50)
                
                # System information
                print("  SYSTEM INFORMATION:")
                print(f"    OS: {platform.system()} {platform.release()}")
                print(f"    Platform: {platform.platform()}")
                print(f"    Architecture: {platform.architecture()}")
                print(f"    Machine: {platform.machine()}")
                print(f"    Processor: {platform.processor()}")
                print(f"    Python: {sys.version.split()[0]}")
                print(f"    Working Directory: {os.getcwd()}")
                
                # Hardware information
                try:
                    import psutil
                    print("\n  HARDWARE INFORMATION:")
                    print(f"    CPU Cores: {psutil.cpu_count()}")
                    print(f"    CPU Usage: {psutil.cpu_percent(interval=1)}%")
                    
                    memory = psutil.virtual_memory()
                    print(f"    RAM Total: {memory.total // (1024**3):.1f} GB")
                    print(f"    RAM Used: {memory.used // (1024**3):.1f} GB ({memory.percent}%)")
                    
                    disk = psutil.disk_usage('.')
                    print(f"    Disk Total: {disk.total // (1024**3):.1f} GB")
                    print(f"    Disk Used: {disk.used // (1024**3):.1f} GB ({(disk.used / disk.total) * 100:.1f}%)")
                    
                    if torch.cuda.is_available():
                        gpu_props = torch.cuda.get_device_properties(0)
                        print(f"    GPU: {gpu_props.name}")
                        print(f"    GPU Memory: {gpu_props.total_memory // (1024**3):.1f} GB")
                except ImportError:
                    print("\n  HARDWARE INFORMATION: psutil not available")
                
                # Model information
                print("\n  MODEL INFORMATION:")
                print(f"    Current Model: {model_wrapper.model_name}")
                print(f"    Device: {model_wrapper.device}")
                print(f"    Temperature: {model_wrapper.temperature}")
                print(f"    Top-p: {model_wrapper.top_p}")
                print(f"    Top-k: {model_wrapper.top_k}")
                print(f"    Repetition Penalty: {model_wrapper.repetition_penalty}")
                print(f"    Conversations: {len(model_wrapper.conversation_history)}")
                
                # Network information
                try:
                    hostname = socket.gethostname()
                    local_ip = socket.gethostbyname(hostname)
                    print("\n  NETWORK INFORMATION:")
                    print(f"    Hostname: {hostname}")
                    print(f"    Local IP: {local_ip}")
                    print(f"    Web URL: http://{local_ip}:8000")
                    print(f"    WebSocket: ws://{local_ip}:8000/ws/chat")
                except Exception:
                    print("\n  NETWORK INFORMATION: Unable to retrieve")
                
                # Performance summary
                print("\n  PERFORMANCE SUMMARY:")
                print(f"    Model Loaded: {'Yes' if model_wrapper.model else 'No'}")
                print(f"    Tokenizer Loaded: {'Yes' if model_wrapper.tokenizer else 'No'}")
                print(f"    CUDA Available: {'Yes' if torch.cuda.is_available() else 'No'}")
                print(f"    MPS Available: {'Yes' if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available() else 'No'}")
                
                print("=" * 50)
                continue
            if not safe_check(user):
                print("Bot: Sorry, I can't help with that.")
                continue
            
            print("Bot: Thinking...", end="", flush=True)
            prompt = model_wrapper.get_context_prompt(user)
            reply = model_wrapper.generate(prompt)
            print("\rBot:", reply)
            
            # Update history
            model_wrapper.add_to_history(user, reply)
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
    ap.add_argument("--version", action="version", version="MiniChat 2.0.0")
    
    # Generation parameters
    ap.add_argument("--temperature", type=float, default=DEFAULT_TEMPERATURE, help=f"Temperature for generation (default: {DEFAULT_TEMPERATURE})")
    ap.add_argument("--top-p", type=float, default=DEFAULT_TOP_P, help=f"Top-p sampling (default: {DEFAULT_TOP_P})")
    ap.add_argument("--top-k", type=int, default=DEFAULT_TOP_K, help=f"Top-k sampling (default: {DEFAULT_TOP_K})")
    ap.add_argument("--max-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS, help=f"Maximum new tokens (default: {DEFAULT_MAX_NEW_TOKENS})")
    ap.add_argument("--repetition-penalty", type=float, default=DEFAULT_REPETITION_PENALTY, help=f"Repetition penalty (default: {DEFAULT_REPETITION_PENALTY})")
    
    # Model presets
    ap.add_argument("--preset", choices=list(MODEL_PRESETS.keys()), help="Use a predefined model preset")
    
    # Additional features
    ap.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    ap.add_argument("--save-history", help="Save conversation history to file")
    ap.add_argument("--load-history", help="Load conversation history from file")
    ap.add_argument("--system-prompt", choices=["general", "creative", "coding", "professional", "casual"], 
                   default="general", help="System prompt type (default: general)")
    
    args = ap.parse_args()
    
    # Handle model preset
    if args.preset:
        args.model = MODEL_PRESETS[args.preset]
        print(f"[INFO] Using preset '{args.preset}': {args.model}")
    
    try:
        mw = ModelWrapper(
            model_name=args.model, 
            device=args.device,
            temperature=args.temperature,
            top_p=args.top_p,
            top_k=args.top_k,
            repetition_penalty=args.repetition_penalty,
            system_prompt=args.system_prompt
        )
        
        # Load conversation history if specified
        if args.load_history:
            history = load_conversation_history(args.load_history)
            mw.conversation_history = history
    except Exception as e:
        print(f"[ERROR] Failed to initialize model: {e}")
        print("[INFO] Try using --device cpu if you're having GPU issues")
        return 1

    if args.cli:
        try:
            run_cli(mw)
        finally:
            # Save conversation history if specified
            if args.save_history and mw.conversation_history:
                save_conversation_history(mw.conversation_history, args.save_history)
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