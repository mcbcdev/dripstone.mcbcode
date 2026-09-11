"""
generate.py

Loads your trained model from a checkpoint and generates text from a prompt
you type in.

How to run it:
    python src/generate.py --prompt "Once upon a time"

Optional flags (all have sensible defaults from config.json if you skip them):
    --max_new_tokens   how many new characters to generate
    --temperature      higher = more random/creative, lower = more predictable.
                        Try values between 0.5 and 1.2.
    --top_k            only consider the top_k most likely next characters at
                        each step (helps avoid picking weird, unlikely characters)

Connects to:
- tokenizer.py (encodes your prompt, decodes the model's output)
- model.py     (the trained neural network that predicts each next token)
"""

import argparse
import json
import os

import torch

from tokenizer import CharTokenizer
from model import SmallLanguageModel


def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find '{path}'. Run this command from inside the ai-template "
            f"folder (the one that contains config.json)."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_model_and_tokenizer(config):
    """
    Shared by generate.py and api.py: loads the tokenizer vocabulary and the
    trained model weights from the checkpoint saved by train.py.
    """
    p_cfg = config["paths"]
    checkpoint_path = os.path.join(p_cfg["checkpoint_dir"], "latest.pt")

    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(
            f"No trained model found at '{checkpoint_path}'. Train a model first "
            f"with: python src/train.py"
        )

    device = (
        "cuda" if torch.cuda.is_available()
        else "mps" if torch.backends.mps.is_available()
        else "cpu"
    )

    checkpoint = torch.load(checkpoint_path, map_location=device)
    mc = checkpoint["model_config"]

    tokenizer = CharTokenizer.load(p_cfg["tokenizer_file"])

    model = SmallLanguageModel(
        vocab_size=mc["vocab_size"],
        n_embd=mc["n_embd"],
        n_head=mc["n_head"],
        n_layer=mc["n_layer"],
        block_size=mc["block_size"],
        dropout=mc.get("dropout", 0.1),
    ).to(device)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    return model, tokenizer, device


def generate_text(model, tokenizer, device, prompt, max_new_tokens, temperature, top_k):
    if prompt == "":
        # An empty prompt still needs *something* to feed the model as a
        # starting point, so we hand it a single blank/placeholder token.
        idx = torch.zeros((1, 1), dtype=torch.long, device=device)
    else:
        idx = torch.tensor([tokenizer.encode(prompt)], dtype=torch.long, device=device)

    out = model.generate(idx, max_new_tokens=max_new_tokens, temperature=temperature, top_k=top_k)
    return tokenizer.decode(out[0].tolist())


def main():
    parser = argparse.ArgumentParser(description="Generate text from your trained model.")
    parser.add_argument("--config", default="config.json")
    parser.add_argument("--prompt", default="", help="Text to start generating from")
    parser.add_argument("--max_new_tokens", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=None)
    parser.add_argument("--top_k", type=int, default=None)
    args = parser.parse_args()

    config = load_config(args.config)
    g_cfg = config.get("generation", {})

    max_new_tokens = args.max_new_tokens if args.max_new_tokens is not None else g_cfg.get("max_new_tokens", 200)
    temperature = args.temperature if args.temperature is not None else g_cfg.get("temperature", 0.8)
    top_k = args.top_k if args.top_k is not None else g_cfg.get("top_k", 40)

    model, tokenizer, device = load_model_and_tokenizer(config)

    text = generate_text(model, tokenizer, device, args.prompt, max_new_tokens, temperature, top_k)
    print(text)


if __name__ == "__main__":
    main()
