# Abliterated LLM Server

Serve **abliterated Qwen models** through [llama.cpp](https://github.com/ggml-org/llama.cpp) in multi-model router mode and expose them to the internet with an **ngrok** tunnel. Built to run on **Google Colab**, but it works on any Linux machine with minor path changes.

---

## Table of Contents

- [Overview](#overview)
- [What is Abliteration?](#what-is-abliteration)
- [Features](#features)
- [Models](#models)
- [Requirements](#requirements)
- [Quick Start](#quick-start)
- [How It Works](#how-it-works)
- [Configuration](#configuration)
- [Using the API](#using-the-api)
- [Security Notes](#security-notes)
- [Troubleshooting](#troubleshooting)
- [Responsible Use](#responsible-use)
- [License](#license)

---

## Overview

`llama_serve_final.py` automates the full setup of a remotely accessible LLM server in one script:

1. Installs llama.cpp
2. Installs and authenticates ngrok
3. Downloads two abliterated GGUF models from Hugging Face
4. Starts llama.cpp as a multi-model router on port `9931`
5. Opens an ngrok tunnel and prints the public URL

Once running, you can send requests to the public URL from any app that supports an OpenAI-compatible API.

## What is Abliteration?

Abliteration is a technique that removes a model's "refusal direction" from its weights. Researchers identify the direction in the model's activations associated with refusing requests, then project it out. The result is a model that follows instructions without the built-in refusal behavior, and without needing a full fine-tune.

Abliterated models can behave unpredictably and may produce content that the original model would have refused. See [Responsible Use](#responsible-use).

## Features

- One-script setup for the server, tunnel, and models
- Multi-model router: serve several GGUF models from one directory
- OpenAI-compatible `/v1` endpoints
- Public HTTPS URL via ngrok, no port forwarding needed
- Quantized models (`Q4_K_M`) for modest GPU or RAM requirements
- Automatic restart handling: stops any previous llama server before starting a new one
- ngrok log output on failure for easier debugging

## Models

| Model | Repository | File |
|---|---|---|
| Qwen3 14B Abliterated | `RootMonsteR/Qwen3-14B-Abliterated-GGUF` | `qwen3-14b-abliterated-Q4_K_M.gguf` |
| Qwen3.5 9B Abliterated | `lukey03/Qwen3.5-9B-abliterated-GGUF` | `Qwen3.5-9B-abliterated-Q4_K_M.gguf` |

Both are `Q4_K_M` quantizations, a good balance of quality and size. Expect roughly 9 GB for the 14B model and 5-6 GB for the 9B model.

## Requirements

- **Python 3.9+**
- **Linux** (x86_64), such as Google Colab
- **A GPU is strongly recommended.** A Colab T4 (16 GB VRAM) can run one model at a time comfortably.
- **Free disk space** of at least 20 GB for both models
- **An ngrok account** and authtoken: [dashboard.ngrok.com](https://dashboard.ngrok.com/get-started/your-authtoken)
- **Internet access** to download llama.cpp, ngrok, and the models

Python dependencies (installed automatically by the script):

- `huggingface_hub`
- `requests`

## Quick Start

### Option A: Google Colab (recommended)

1. Open a new Colab notebook and set the runtime to **GPU** (Runtime > Change runtime type).
2. Add your ngrok token as a Colab secret named `NGROK_TOKEN` (key icon in the left sidebar).
3. Upload `llama_serve_final.py` or paste its contents into cells.
4. Run the script. When it finishes, it prints:

```
   LLM URL: https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

### Option B: Local Linux machine

1. Clone the repo:

```bash
   git clone https://github.com/<your-username>/abliterated_llm_server.git
   cd abliterated_llm_server
```

2. Change `MODELS_DIR` from `/content/models` to a local path, for example `./models`.

3. Export your token and run:

```bash
   export NGROK_TOKEN="your-real-token"
   python llama_serve_final.py
```

## How It Works

| Stage | What happens |
|---|---|
| **1. Install llama.cpp** | Runs the llama installer script, which places the binary in `~/.llama-app/` |
| **2. Install ngrok** | Downloads and extracts the ngrok v3 binary into the working directory |
| **3. Authenticate ngrok** | Registers your authtoken with `ngrok config add-authtoken` |
| **4. Download models** | Uses `hf_hub_download` to fetch each GGUF file into `MODELS_DIR` |
| **5. Start the server** | Launches `llama serve --models-dir ...` on `127.0.0.1:9931` and logs to `/tmp/llama.log` |
| **6. Verify models** | Calls `/v1/models` to confirm both models are registered |
| **7. Open the tunnel** | Starts `ngrok http 9931` and reads the public URL from ngrok's local API at `127.0.0.1:4040` |

The llama server binds to `127.0.0.1` only. The ngrok tunnel is the sole public entry point.

## Configuration

| Variable | Default | Description |
|---|---|---|
| `NGROK_TOKEN` | `"hello"` (placeholder) | Your ngrok authtoken. **Replace it, and never commit the real value.** |
| `PORT` | `"9931"` | Local port for the llama server and ngrok tunnel |
| `MODELS_DIR` | `/content/models` | Directory where GGUF models are stored and loaded from |

### Using environment variables for secrets

Replace the hardcoded token with:

```python
import os
NGROK_TOKEN = os.environ["NGROK_TOKEN"]
```

On Colab, use secrets instead:

```python
from google.colab import userdata
NGROK_TOKEN = userdata.get("NGROK_TOKEN")
```

### Adding more models

Drop any additional `.gguf` file into `MODELS_DIR`, or add an entry to the `models` dictionary in the script:

```python
models = {
    "owner/repo-name": "filename.gguf",
}
```

Restart the server to register the new model.

## Using the API

Replace `<NGROK_URL>` with the URL printed by the script.

### List available models

```bash
curl <NGROK_URL>/v1/models
```

Use the model IDs returned here in the `model` field of your requests.

### Chat completion (curl)

```bash
curl <NGROK_URL>/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "<model-id-from-/v1/models>",
    "messages": [
      {"role": "user", "content": "Hello! Who are you?"}
    ]
  }'
```

### Python (OpenAI client)

```python
from openai import OpenAI

client = OpenAI(
    base_url="<NGROK_URL>/v1",
    api_key="not-needed",
)

response = client.chat.completions.create(
    model="<model-id-from-/v1/models>",
    messages=[{"role": "user", "content": "Write a haiku about tunnels."}],
)

print(response.choices[0].message.content)
```

### Compatible clients

Any tool that accepts a custom OpenAI-compatible base URL should work, including Open WebUI, SillyTavern, Continue, LibreChat, and LangChain.

## Security Notes

- **Your ngrok URL is public.** Anyone who has it can use your server, and by default there is no authentication.
- **Add protection** by starting ngrok with basic auth:

```python
  ["./ngrok", "http", PORT, "--basic-auth", "user:a-strong-password"]
```

  Or check whether your llama.cpp build supports an `--api-key` flag.
- **Never commit your ngrok token.** If it leaks, revoke it in the ngrok dashboard immediately. Deleting it in a later commit does not remove it from git history.
- **Free Colab sessions are temporary.** The URL changes each time you restart the tunnel.
- Treat everything sent through the tunnel as potentially visible to ngrok.

## Troubleshooting

| Problem | Likely cause | Fix |
|---|---|---|
| `Failed to connect to ngrok` | ngrok did not start or the token is invalid | Check the printed ngrok logs; confirm the authtoken |
| `/v1/models` returns an empty list | Models are not in `MODELS_DIR` | Verify the downloads finished and the path is correct |
| Connection error on `/v1/models` | The server needs more time to start | Increase `time.sleep(5)` or check `/tmp/llama.log` |
| Out-of-memory errors | The model is too large for your GPU or RAM | Use the 9B model, a smaller quantization, or a larger runtime |
| `ERR_NGROK_` errors in the browser | Tunnel limits or an expired session | Restart ngrok; check your account's limits |
| `Permission denied: ./ngrok` | Binary is not executable | Run `chmod +x ./ngrok` |
| Slow generation | Running on CPU | Switch to a GPU runtime |

### Checking logs

```bash
cat /tmp/llama.log
cat /tmp/ngrok.log
```

### Stopping everything

```python
llama.terminate()
ngrok.terminate()
```

## Responsible Use

Abliterated models have had their safety training deliberately weakened. By using this project you agree to:

- Use it lawfully and ethically
- Not use it to generate content that harms others
- Take responsibility for what you generate and share
- Respect the licenses of the underlying models (Qwen) and the abliterated derivatives

The authors provide this project for research and educational purposes and are not responsible for misuse.

## License

Add your chosen license here (for example MIT). Note that the model weights have their own licenses, set by their respective authors on Hugging Face.

## Acknowledgements

- [llama.cpp](https://github.com/ggml-org/llama.cpp)
- [ngrok](https://ngrok.com)
- [Hugging Face](https://huggingface.co)
- The Qwen team at Alibaba Cloud
- The authors of the abliterated GGUF models used here
