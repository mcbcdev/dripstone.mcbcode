# Preparing training data

This folder holds the text your model learns from.

## Quick start

`training.txt` already has a small example dataset in it, so you can run
training immediately without writing anything yourself. Once you've
confirmed everything works, replace it with your own text.

## What kind of file works

- Plain text or markdown, saved as a single `.txt` file (or `.md` - the
  tokenizer doesn't care about the extension, it just reads characters).
- One file. If your data is spread across multiple files, combine them into
  one `training.txt` before training (e.g. by pasting them together).
- UTF-8 encoding (the default for basically every text editor).

## How much text do you need

This project uses a character-level tokenizer, so "how much text" is
measured in characters, not words.

- **Bare minimum to run without errors:** a few thousand characters (roughly
  what's already in the example file).
- **Enough to see recognizable patterns:** tens of thousands of characters
  (a few dozen pages).
- **Enough for genuinely coherent output:** hundreds of thousands of
  characters or more, plus a longer training run.

There's no hard cap - more data generally means a better model, as long as
your `max_iters` in `config.json` is high enough to actually train on it.

## What kind of content works well

- Text that's internally consistent in style and topic trains faster and
  produces more coherent output. A dataset that's all one genre (e.g. all
  recipes, or all dialogue in one character's voice) will "sound like" that
  genre much sooner than a dataset that jumps between wildly different
  styles.
- Repetition is actually helpful for a small model - seeing similar
  sentence structures multiple times makes patterns easier to learn.
- Avoid mixing in a lot of unusual symbols, foreign scripts, or garbled
  text unless you want the model to learn those too - every unique
  character adds a small amount of extra difficulty for a tiny model.

## Important: only use text you have the right to use

Only include text you wrote yourself, text you have permission to use, or
text that's in the public domain / openly licensed for this purpose.
Training on copyrighted text you don't have rights to is your
responsibility to check, not something this template can verify for you.

## After you change this file

Any time you replace or significantly change `training.txt`, you should
start a fresh training run (don't use `--resume`) - the tokenizer's
vocabulary is built from this file, so a different file means a different
vocabulary, and old checkpoints won't match anymore. `train.py` will warn
you if it detects a mismatch.
