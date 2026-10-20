import os
import subprocess
import time
import requests

# Configuration
NGROK_TOKEN = "hello"
PORT = "9931"

# Install llama.cpp
subprocess.run(
    "curl -LsSf https://llama.app/install.sh | sh",
    shell=True, check=True
)

# Install ngrok
subprocess.run(
    "curl -fsSL https://bin.ngrok.com/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar -xz",
    shell=True, check=True
)
# Authenticate ngrok
subprocess.run(
    ["./ngrok", "config", "add-authtoken", NGROK_TOKEN],
    check=True
)

import sys
import subprocess
from pathlib import Path

subprocess.run([
    sys.executable, "-m", "pip",
    "install", "-q", "-U", "huggingface_hub"
], check=True)

from huggingface_hub import hf_hub_download

models = {
    "RootMonsteR/Qwen3-14B-Abliterated-GGUF":
        "qwen3-14b-abliterated-Q4_K_M.gguf",

    "lukey03/Qwen3.5-9B-abliterated-GGUF":
        "Qwen3.5-9B-abliterated-Q4_K_M.gguf"
}

Path("/content/models").mkdir(exist_ok=True)

for repo, filename in models.items():
    print(f"Downloading: {filename}", flush=True)

    path = hf_hub_download(
        repo_id=repo,
        filename=filename,
        local_dir="/content/models"
    )

    print(f"Downloaded: {path}")

print("All models downloaded successfully!")

import os
import subprocess
import time
import requests

PORT = "9931"
MODELS_DIR = "/content/models"

# Stop previous llama server
if "llama" in globals() and llama.poll() is None:
    llama.terminate()
    llama.wait()

# Start multi-model router
llama = subprocess.Popen(
    [
        os.path.expanduser("~/.llama-app/llama"),
        "serve",
        "--models-dir", MODELS_DIR,
        "--host", "127.0.0.1",
        "--port", PORT
    ],
    stdout=open("/tmp/llama.log", "w"),
    stderr=subprocess.STDOUT
)

time.sleep(5)

# Verify both models are registered
response = requests.get(
    f"http://127.0.0.1:{PORT}/v1/models"
)
print(response.json())

import subprocess
import time
import requests
import os

# Ensure ngrok binary is executable
subprocess.run(["chmod", "+x", "./ngrok"], check=True)

# Start ngrok
ngrok = subprocess.Popen(
    ["./ngrok", "http", PORT],
    stdout=open("/tmp/ngrok.log", "w"),
    stderr=subprocess.STDOUT
)

# Wait for tunnel to initialize
time.sleep(5)

try:
    # Display public URL
    response = requests.get(
        "http://127.0.0.1:4040/api/tunnels",
        timeout=10
    )
    response.raise_for_status()

    for tunnel in response.json()["tunnels"]:
        print("LLM URL:", tunnel["public_url"])

    if 'llama' in globals():
        print("Llama PID:", llama.pid)
    print("Ngrok PID:", ngrok.pid)

except Exception as e:
    print(f"Failed to connect to ngrok: {e}")
    if os.path.exists("/tmp/ngrok.log"):
        print("--- Ngrok Logs ---")
        with open("/tmp/ngrok.log", "r") as f:
            print(f.read())
