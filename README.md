_this readme is 100% ai generated_

# selfhost-ai

A small, open-source template for training and running your own language
model — entirely on your own hardware. No OpenAI, Gemini, Claude API,
Hugging Face Inference, or any paid AI service required.

Clone it, train it on your own data, and self-host the result. Fork it and
turn it into something completely your own.

## Table of contents

- [What this is](#what-this-is)
- [Features](#features)
- [Project structure](#project-structure)
- [Self-hosting: quick start](#self-hosting-quick-start)
- [Configuration](#configuration)
- [Forking this repo](#forking-this-repo)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Disclaimer](#disclaimer)

## What this is

`selfhost-ai` is a minimal, from-scratch implementation of a GPT-style
transformer language model, meant to be read, understood, and modified —
not just run as a black box. It gives you every piece needed to go from
raw text to a working, locally-hosted model:

- A character-level tokenizer
- A small transformer model definition
- A training loop with checkpointing and resume support
- A text generation script
- An optional local HTTP API, so you can call your model from a website
  or app the same way you'd call a hosted API

Everything runs locally with plain PyTorch. Training happens on your own
computer, and the resulting model stays yours — nothing is sent to an
external service at any point.

This is an educational, small-scale framework, not a competitor to large
commercial models. See [Disclaimer](#disclaimer) below.

## Features

- Zero external AI API dependencies
- Zero paid services required
- Single `config.json` controls model size and training settings
- Checkpointing: stop and resume training anytime
- CLI text generation with adjustable temperature and length
- Optional Flask-based local API with CORS support, ready to call from a
  browser-based frontend
- Small enough to train on a normal laptop CPU; scales up if you have a
  GPU

## Project structure

```
selfhost-ai/
├── README.md              - this file
├── LICENSE                - MIT license
├── requirements.txt       - Python dependencies
├── config.json             - model and training settings
│
├── data/
│   ├── README.md           - how to prepare your own training data
│   └── training.txt        - example dataset
│
├── src/
│   ├── tokenizer.py         - text <-> token conversion
│   ├── model.py              - the transformer model
│   ├── dataset.py            - batching logic for training
│   ├── train.py               - training entry point
│   ├── generate.py            - text generation entry point
│   └── api.py                  - optional local HTTP API
│
├── checkpoints/             - trained model weights (empty until you train)
│
└── examples/
    └── README.md            - example commands
```

## Self-hosting: quick start

You'll need **Python 3.9+** installed. No account, subscription, or API
key of any kind is required for any of this.

```bash
# 1. Get the code (see "Forking this repo" below for the no-terminal way)
git clone https://github.com/YOUR_USERNAME/selfhost-ai.git
cd selfhost-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your training data
#    Replace the contents of data/training.txt with your own text.
#    See data/README.md for formatting guidance.

# 4. Train
python src/train.py

# 5. Generate text
python src/generate.py --prompt "Once upon a time"

# 6. (Optional) Serve it over HTTP for a website/app to call
pip install flask
python src/api.py
```

Training can be stopped anytime and resumed later:

```bash
python src/train.py --resume
```

Full usage details — including how to connect this to a website, expose
it publicly with a tunnel, and what to realistically expect from a small
model — are in [`examples/README.md`](examples/README.md) and
[`data/README.md`](data/README.md).

## Configuration

All model size and training behavior is controlled through `config.json`
— no code changes required to experiment with different setups:

```json
{
  "model": {
    "n_embd": 128,
    "n_head": 4,
    "n_layer": 4,
    "block_size": 128,
    "dropout": 0.1
  },
  "training": {
    "batch_size": 32,
    "learning_rate": 0.0003,
    "max_iters": 3000,
    "device": "auto"
  }
}
```

Smaller values train faster on modest hardware; larger values produce a
more capable (but slower to train) model. See the comments in
`config.json` itself for what each field controls.

## Forking this repo

Forking gives you your own independent copy of `selfhost-ai` to customize
freely — new training data, different model settings, your own features
— without affecting the original.

1. Click the **Fork** button at the top right of this repo's GitHub page.
2. GitHub creates a copy under your own account, e.g.
   `github.com/your-username/selfhost-ai`.
3. From there, either:
   - **Clone it locally** with `git clone` if you're comfortable with a
     terminal, or
   - **Download it as a ZIP** via the green **Code** button >
     **Download ZIP** if you're not — unzip it and follow the
     [quick start](#self-hosting-quick-start) above.
4. Make your changes (swap the training data, adjust `config.json`,
   modify the code), commit, and push back to your fork whenever you're
   ready.
5. If you build something you think improves the original project, open a
   pull request back to this repo (see [Contributing](#contributing)).

Your fork is entirely independent — you can rename it, make it private,
and take it in any direction without needing permission from anyone.

## Contributing

Contributions are welcome, whether that's a bug fix, a documentation
improvement, or a new feature.

1. **Fork** the repo and create a branch for your change:
   ```bash
   git checkout -b my-change
   ```
2. **Make your change.** Keep the project's goals in mind — simplicity
   and readability over raw model performance. Comment non-obvious code
   the way the rest of the project does, since a lot of people using this
   repo are learning as they go.
3. **Test it.** At minimum, run through the quick start above end to end
   (train on the example dataset, generate text, run the API if you
   touched `api.py`) and confirm nothing broke.
4. **Commit and push** to your fork:
   ```bash
   git commit -m "Describe your change"
   git push origin my-change
   ```
5. **Open a pull request** against this repo, with a short description of
   what changed and why.

### Reporting issues

If you find a bug or have a feature request, open an issue describing:
- What you expected to happen
- What actually happened
- Steps to reproduce (your `config.json` settings and roughly how much
  training data you used, if relevant)

### What kinds of contributions fit well here

- Bug fixes and clearer error messages
- Documentation improvements
- Small, well-explained features that stay in the spirit of "simple and
  educational" rather than adding heavy dependencies or complexity
- Additional example datasets or configuration presets

Large architectural changes are welcome too, but consider opening an issue
to discuss the approach first, since they're more likely to need
back-and-forth before merging.

## Roadmap

Ideas being considered for future versions (not promises, just direction):

- Optional retrieval-augmented generation (RAG) support, for grounding
  responses in a document set instead of relying purely on trained
  weights
- Additional tokenizer options beyond character-level
- Example integrations for common self-hosting setups

Open an issue if there's something specific you'd like to see.

## License

MIT — see [LICENSE](LICENSE). Use it, modify it, fork it, ship it as your
own project, all without restriction.

## Disclaimer

This project produces small, educational language models trained on
whatever data you provide. It is not, and is not intended to be, a
replacement for large commercial models like ChatGPT or Claude. Output
quality depends entirely on your training data, model size, and training
time — expect a model that reflects patterns in your data, not one with
broad general knowledge or reliable factual accuracy.