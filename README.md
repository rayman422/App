# MiniChat - All-in-One AI Chat Application

A single-file Python application that provides both CLI and web-based chat interfaces using Hugging Face transformers. Perfect for local AI chat without external dependencies.

## Features

- **CLI Mode**: Interactive command-line chat interface
- **Web Mode**: FastAPI server with WebSocket chat and auto-generated HTML client
- **Model Support**: Works with any Hugging Face causal language model
- **Device Detection**: Automatic CUDA/GPU detection with CPU fallback
- **Content Filtering**: Basic safety filters (expandable for production)
- **Conversation Memory**: Maintains chat history per session
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install requirements
pip install --upgrade pip
pip install -r requirements.txt
```

**CPU-only users**: If you don't have a GPU, install the CPU version of PyTorch:
```bash
pip install --index-url https://download.pytorch.org/whl/cpu torch
```

### 2. Test Installation

```bash
python test_mini_chat.py
```

### 3. Run the Application

**CLI Mode:**
```bash
python mini_chat_all_in_one.py --cli
```

**Web Mode:**
```bash
python mini_chat_all_in_one.py --web
```
Then open http://localhost:8000 in your browser.

## Usage

### CLI Commands

- `help` - Show available commands
- `clear` - Clear chat history
- `exit` or `quit` - Exit the program

### Command Line Options

```bash
python mini_chat_all_in_one.py [OPTIONS]

Options:
  --model TEXT     Hugging Face model name (default: EleutherAI/gpt-neo-125M)
  --device TEXT    Device override (cpu, cuda, mps)
  --cli            Run CLI chat mode
  --web            Run web server mode
  --host TEXT      Host for web server (default: 0.0.0.0)
  --port INTEGER   Port for web server (default: 8000)
  --version        Show version and exit
  --help           Show help message
```

### Model Examples

```bash
# Use default small model
python mini_chat_all_in_one.py --cli

# Use GPT-2 (larger, better quality)
python mini_chat_all_in_one.py --cli --model gpt2

# Force CPU usage
python mini_chat_all_in_one.py --cli --device cpu

# Custom model
python mini_chat_all_in_one.py --cli --model microsoft/DialoGPT-medium
```

## Model Recommendations

### Lightweight Models (Good for testing)
- `EleutherAI/gpt-neo-125M` - Default, very small
- `distilgpt2` - Small GPT-2 variant
- `microsoft/DialoGPT-small` - Small conversational model

### Balanced Models (Good quality/speed)
- `gpt2` - Standard GPT-2
- `microsoft/DialoGPT-medium` - Medium conversational model

### High-Quality Models (Slower, better responses)
- `gpt2-medium` - Larger GPT-2 variant
- `microsoft/DialoGPT-large` - Large conversational model

## Troubleshooting

### Common Issues

**"CUDA out of memory"**
- Use a smaller model: `--model EleutherAI/gpt-neo-125M`
- Force CPU: `--device cpu`
- Reduce `max_new_tokens` in the code

**"Model loading failed"**
- Check internet connection (models download from Hugging Face)
- Try a different model name
- Use `--device cpu` if GPU issues persist

**"Import errors"**
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt`
- Check Python version (3.8+ required)

**"Port already in use"**
- Use different port: `--port 8001`
- Check if another service is using port 8000

### Performance Tips

- **GPU**: Models run 5-10x faster on CUDA
- **Model Size**: Smaller models = faster responses
- **Memory**: Larger models need more RAM/VRAM
- **CPU**: Use quantized models for better CPU performance

## Development

### Project Structure

```
mini_chat_all_in_one.py  # Main application
requirements.txt          # Dependencies
test_mini_chat.py        # Test suite
README.md                # This file
```

### Key Components

- **ModelWrapper**: Handles model loading and inference
- **safe_check**: Content filtering system
- **write_client_html**: Generates web interface
- **run_cli**: CLI chat interface
- **create_app**: FastAPI web server

### Extending the Application

**Add New Models:**
```python
# In ModelWrapper._load()
if "llama" in model_name.lower():
    # Special handling for LLaMA models
    pass
```

**Improve Content Filtering:**
```python
def safe_check(text: str) -> bool:
    # Add your custom filtering logic
    # Consider using external libraries like detoxify
    pass
```

**Add Persistence:**
```python
# Save chat history to file/database
import json
with open("chat_history.json", "w") as f:
    json.dump(chat_history, f)
```

## Docker Support

### Basic Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY mini_chat_all_in_one.py .

EXPOSE 8000
CMD ["python", "mini_chat_all_in_one.py", "--web", "--host", "0.0.0.0"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  minichat:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/root/.cache/huggingface  # Cache models
    environment:
      - TRANSFORMERS_CACHE=/root/.cache/huggingface
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source. Feel free to modify and distribute.

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Run `python test_mini_chat.py` to verify setup
3. Check that all dependencies are installed correctly
4. Try with a different model or device setting

## Roadmap

- [ ] Quantized model support (4-bit, 8-bit)
- [ ] LoRA fine-tuning capabilities
- [ ] Better content moderation
- [ ] Multi-user web interface
- [ ] API rate limiting
- [ ] Docker optimization
- [ ] Model caching improvements