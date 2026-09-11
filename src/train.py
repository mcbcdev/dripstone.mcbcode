"""
train.py

This is the script you actually run to train your language model.

What it does, step by step:
  1. Loads settings from config.json
  2. Reads your training text from data/training.txt
  3. Builds a tokenizer vocabulary from that text (or loads an existing one,
     if you're resuming a previous run)
  4. Builds the model (see model.py)
  5. Repeats, many times: grab a batch of text -> ask the model to predict
     the next token at every position -> measure how wrong it was (the
     "loss") -> nudge the model's internal numbers to be a little less
     wrong next time (this nudging is called "backpropagation")
  6. Every so often, prints progress and saves a checkpoint file, so you can
     stop training at any time (even by force-closing the terminal) and
     pick back up later without losing your progress

How to run it (from inside the ai-template folder):
    python src/train.py

To resume training instead of starting over:
    python src/train.py --resume

Connects to:
- tokenizer.py (turns text into token ids)
- dataset.py   (serves up batches of training data)
- model.py     (the neural network being trained)
"""

import argparse
import json
import os
import time

import torch

from tokenizer import CharTokenizer
from dataset import TextDataset
from model import SmallLanguageModel


def load_config(path):
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Could not find '{path}'. Make sure you're running this command from "
            f"inside the ai-template folder (the one that contains config.json)."
        )
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def pick_device(preference="auto"):
    """
    Figures out the best available device to train on.
    - "cuda" = an NVIDIA GPU (fastest, if you have one)
    - "mps"  = Apple Silicon GPU (M1/M2/M3 Macs)
    - "cpu"  = your regular processor (slower, but works everywhere for free)
    """
    if preference != "auto":
        return preference
    if torch.cuda.is_available():
        return "cuda"
    if torch.backends.mps.is_available():
        return "mps"
    return "cpu"


@torch.no_grad()
def estimate_loss(model, dataset, eval_iters, batch_size, device):
    """
    Runs a handful of batches through the model WITHOUT updating its weights,
    just to measure how well it's currently doing on both the training data
    and the validation data. Averaging several batches makes the number less
    noisy than looking at a single training step's loss.
    """
    model.eval()
    result = {}
    for split in ("train", "val"):
        losses = torch.zeros(eval_iters)
        for k in range(eval_iters):
            x, y = dataset.get_batch(split, batch_size, device)
            _, loss = model(x, y)
            losses[k] = loss.item()
        result[split] = losses.mean().item()
    model.train()
    return result


def save_checkpoint(model, optimizer, iteration, model_config, checkpoint_path):
    """
    Saves everything needed to either resume training or generate text later:
    - the model's learned weights
    - the optimizer's internal state (so resuming training is smooth, not jumpy)
    - which training iteration this is
    - the model's architecture settings, so generate.py can rebuild the exact
      same model shape even if config.json gets edited afterwards
    """
    torch.save({
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
        "iteration": iteration,
        "model_config": model_config,
    }, checkpoint_path)
    print(f"Saved checkpoint at iteration {iteration} -> {checkpoint_path}")


def main():
    parser = argparse.ArgumentParser(description="Train a small language model from scratch.")
    parser.add_argument("--config", default="config.json", help="Path to config.json")
    parser.add_argument("--resume", action="store_true", help="Resume from the last saved checkpoint")
    args = parser.parse_args()

    config = load_config(args.config)
    m_cfg = config["model"]
    t_cfg = config["training"]
    d_cfg = config["data"]
    p_cfg = config["paths"]

    device = pick_device(t_cfg.get("device", "auto"))
    print(f"Using device: {device}")
    if device == "cpu":
        print("Training on CPU - this works fine for a small model, it will just be "
              "slower than a GPU. Keep the model and dataset small and be patient.")

    os.makedirs(p_cfg["checkpoint_dir"], exist_ok=True)

    # ---------------------------------------------------------------
    # Load training text
    # ---------------------------------------------------------------
    train_file = d_cfg["train_file"]
    if not os.path.exists(train_file):
        raise FileNotFoundError(
            f"Training file not found at '{train_file}'. Put your training text "
            f"there, or change 'train_file' in config.json to point somewhere else. "
            f"See data/README.md for guidance on preparing training data."
        )
    with open(train_file, "r", encoding="utf-8") as f:
        text = f.read()

    if len(text.strip()) == 0:
        raise ValueError(
            f"'{train_file}' is empty. Add some text to it before training - see "
            f"data/README.md for tips on how much text you need and how to format it."
        )

    # ---------------------------------------------------------------
    # Tokenizer: build fresh, or load the existing one when resuming
    # ---------------------------------------------------------------
    tokenizer_path = p_cfg["tokenizer_file"]
    if args.resume and os.path.exists(tokenizer_path):
        tokenizer = CharTokenizer.load(tokenizer_path)
        print(f"Loaded existing tokenizer ({tokenizer.vocab_size} unique characters).")
    else:
        tokenizer = CharTokenizer.build_from_text(text)
        tokenizer.save(tokenizer_path)
        print(f"Built a new tokenizer with {tokenizer.vocab_size} unique characters, "
              f"saved to '{tokenizer_path}'.")

    token_ids = tokenizer.encode(text)
    dataset = TextDataset(
        token_ids,
        block_size=m_cfg["block_size"],
        val_split=d_cfg.get("val_split", 0.1),
    )
    print(f"Training data: {len(token_ids)} tokens total "
          f"({len(dataset.train_data)} train / {len(dataset.val_data)} val)")

    # ---------------------------------------------------------------
    # Build the model
    # ---------------------------------------------------------------
    model_config = {
        "vocab_size": tokenizer.vocab_size,
        "n_embd": m_cfg["n_embd"],
        "n_head": m_cfg["n_head"],
        "n_layer": m_cfg["n_layer"],
        "block_size": m_cfg["block_size"],
        "dropout": m_cfg.get("dropout", 0.1),
    }
    model = SmallLanguageModel(**model_config).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model created with {n_params:,} parameters.")

    optimizer = torch.optim.AdamW(model.parameters(), lr=t_cfg["learning_rate"])

    checkpoint_path = os.path.join(p_cfg["checkpoint_dir"], "latest.pt")
    start_iter = 0

    if args.resume:
        if not os.path.exists(checkpoint_path):
            raise FileNotFoundError(
                f"--resume was passed but no checkpoint exists yet at "
                f"'{checkpoint_path}'. Run training once WITHOUT --resume first."
            )
        checkpoint = torch.load(checkpoint_path, map_location=device)

        if checkpoint["model_config"]["vocab_size"] != tokenizer.vocab_size:
            raise ValueError(
                "This checkpoint was trained with a different tokenizer vocabulary "
                "than the one just built from your current training data - likely "
                "because the training data changed. You can't resume training with "
                "a mismatched vocabulary. Either restore the original training data, "
                "or delete the checkpoints/ folder and start a fresh training run."
            )

        model.load_state_dict(checkpoint["model_state_dict"])
        optimizer.load_state_dict(checkpoint["optimizer_state_dict"])
        start_iter = checkpoint["iteration"] + 1
        print(f"Resuming training from iteration {start_iter}.")

    # ---------------------------------------------------------------
    # Training loop
    # ---------------------------------------------------------------
    max_iters = t_cfg["max_iters"]
    eval_interval = t_cfg["eval_interval"]
    eval_iters = t_cfg["eval_iters"]
    checkpoint_interval = t_cfg["checkpoint_interval"]
    batch_size = t_cfg["batch_size"]
    grad_clip = t_cfg.get("grad_clip", 1.0)

    if start_iter >= max_iters:
        print(f"This model has already trained for {start_iter} iterations, which is "
              f">= max_iters ({max_iters}) in config.json. Raise max_iters if you want "
              f"to keep training it, then run again with --resume.")
        return

    print(f"Starting training: iteration {start_iter} -> {max_iters}")
    start_time = time.time()

    for it in range(start_iter, max_iters):
        xb, yb = dataset.get_batch("train", batch_size, device)
        logits, loss = model(xb, yb)

        optimizer.zero_grad(set_to_none=True)
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip)
        optimizer.step()

        is_last_iter = (it == max_iters - 1)

        if it % eval_interval == 0 or is_last_iter:
            losses = estimate_loss(model, dataset, eval_iters, batch_size, device)
            elapsed_min = (time.time() - start_time) / 60
            print(f"iter {it:>6} | train loss {losses['train']:.4f} | "
                  f"val loss {losses['val']:.4f} | elapsed {elapsed_min:.1f} min")

        if (it % checkpoint_interval == 0 and it != start_iter) or is_last_iter:
            save_checkpoint(model, optimizer, it, model_config, checkpoint_path)

    print("Training finished.")
    print(f"Final checkpoint: {checkpoint_path}")
    print("Generate text with: python src/generate.py --prompt \"your prompt here\"")


if __name__ == "__main__":
    main()
