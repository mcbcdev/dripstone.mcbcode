"""
api.py

An OPTIONAL local web server that lets you (or another program, like a
website or a bot) send a prompt over HTTP and get generated text back,
instead of using the command line.

This is NOT required for training or generating text - train.py and
generate.py work completely fine without this file ever being touched.
This is just a convenience layer for people who want to build something on
top of their model later (a website, a Discord bot, etc).

Requires Flask. Install it with:
    pip install flask

How to run it:
    python src/api.py

Then, from another terminal (or any HTTP client, or a webpage's JavaScript),
send a request like:
    curl -X POST http://localhost:8000/generate ^
         -H "Content-Type: application/json" ^
         -d "{\"prompt\": \"Once upon a time\"}"

(On Mac/Linux, replace the ^ line-continuations with a backslash, or just
put it all on one line.)

Everything runs on your own computer - nothing is sent to any external
service.

Connects to:
- tokenizer.py
- model.py
- generate.py (reuses load_model_and_tokenizer and generate_text so the
  logic for turning a prompt into text lives in exactly one place)
"""

import os

try:
    from flask import Flask, request, jsonify
except ImportError:
    raise ImportError(
        "Flask is not installed, but it's required to run the API. Install it "
        "with: pip install flask"
    )

from generate import load_config, load_model_and_tokenizer, generate_text

config = load_config("config.json")
g_cfg = config.get("generation", {})

print("Loading model, this can take a few seconds...")
model, tokenizer, device = load_model_and_tokenizer(config)
print("Model loaded.")

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    """
    Browsers block a webpage's JavaScript from calling a different address
    (like your API) unless the server explicitly says it's allowed. These
    headers say "yes, any webpage can call this API." That's fine for a
    small personal project running on your own machine - if you ever put
    this online for other people to use, you'd want to lock this down to
    your specific website's address instead of "*".
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/generate", methods=["POST", "OPTIONS"])
def generate_endpoint():
    """
    Expects a JSON body like:
        { "prompt": "Once upon a time", "max_new_tokens": 200, "temperature": 0.8, "top_k": 40 }
    Only "prompt" is required - everything else falls back to config.json's
    defaults if you leave it out.
    """
    if request.method == "OPTIONS":
        # This is the browser's "preflight" check, asking permission before
        # it sends the real POST request. No body to process here - the
        # add_cors_headers() function above already attached the headers
        # that answer that permission check.
        return "", 204

    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt", "")
    max_new_tokens = data.get("max_new_tokens", g_cfg.get("max_new_tokens", 200))
    temperature = data.get("temperature", g_cfg.get("temperature", 0.8))
    top_k = data.get("top_k", g_cfg.get("top_k", 40))

    try:
        text = generate_text(model, tokenizer, device, prompt, max_new_tokens, temperature, top_k)
    except ValueError as e:
        # e.g. a prompt containing a character the tokenizer has never seen
        return jsonify({"error": str(e)}), 400

    return jsonify({"prompt": prompt, "generated_text": text})


@app.route("/health", methods=["GET"])
def health():
    """Simple check to confirm the server is up and a model is loaded."""
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting local API on http://localhost:{port}")
    print("This only runs on your own machine - press Ctrl+C to stop it.")
    app.run(host="0.0.0.0", port=port)
