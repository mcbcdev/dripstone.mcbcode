<img src="/logo.png" alt="shai" width="100">

# selfhost-ai

a small, open-source template for training and running your own language
model — entirely on your own hardware. no openai, gemini, claude api,
hugging face inference, or any paid ai service required.

clone it, train it on your own data, and self-host the result. fork it and
turn it into something completely your own.

## table of contents

- [what this is](#what-this-is)
- [features](#features)
- [project structure](#project-structure)
- [self-hosting: quick start](#self-hosting-quick-start)
- [configuration](#configuration)
- [forking this repo](#forking-this-repo)
- [contributing](#contributing)
- [roadmap](#roadmap)
- [license](#license)
- [disclaimer](#disclaimer)

## what this is

`selfhost-ai` is a minimal, from-scratch implementation of a GPT-style
transformer language model, meant to be read, understood, and modified —
not just run as a black box. It gives you every piece needed to go from
raw text to a working, locally-hosted model:

- a character-level tokenizer
- a small transformer model definition
- a training loop with checkpointing and resume support
- a text generation script
- an optional local http api, so you can call your model from a website
  or app the same way you'd call a hosted api

everything runs locally with plain pytorch. training happens on your own
computer, and the resulting model stays yours — nothing is sent to an
external service at any point.

this is an educational, small-scale framework, not a competitor to large
commercial models. See [disclaimer](#disclaimer) below.

## features

- zero external ai api dependencies
- zero paid services required
- single `config.json` controls model size and training settings
- checkpointing: stop and resume training anytime
- cli text generation with adjustable temperature and length
- optional flask-based local api with cors support, ready to call from a
  browser-based frontend
- small enough to train on a normal laptop cpu; scales up if you have a
  gpu

## project structure

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

## self-hosting: quick start

you'll need **python 3.9+** installed. no account, subscription, or api
key of any kind is required for any of this.

```bash
# 1. get the code (see "Forking this repo" below for the no-terminal way)
git clone https://github.com/YOUR_USERNAME/selfhost-ai.git
cd selfhost-ai

# 2. install dependencies
pip install -r requirements.txt

# 3. add your training data
#    replace the contents of data/training.txt with your own text.
#    see data/README.md for formatting guidance.

# 4. train
python src/train.py

# 5. generate text
python src/generate.py --prompt "Once upon a time"

# 6. (optional) Serve it over http for a website/app to call
pip install flask
python src/api.py
```

training can be stopped anytime and resumed later:

```bash
python src/train.py --resume
```

full usage details — including how to connect this to a website, expose
it publicly with a tunnel, and what to realistically expect from a small
model — are in [`examples/README.md`](examples/README.md) and
[`data/README.md`](data/README.md).

## configuration

all model size and training behavior is controlled through `config.json`
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

smaller values train faster on modest hardware; larger values produce a
more capable (but slower to train) model. See the comments in
`config.json` itself for what each field controls.

## forking this repo

forking gives you your own independent copy of `selfhost-ai` to customize
freely — new training data, different model settings, your own features
— without affecting the original.

1. click the **Fork** button at the top right of this repo's GitHub page.
2. gitHub creates a copy under your own account, e.g.
   `github.com/your-username/selfhost-ai`.
3. from there, either:
   - **Clone it locally** with `git clone` if you're comfortable with a
     terminal, or
   - **Download it as a ZIP** via the green **Code** button >
     **Download ZIP** if you're not — unzip it and follow the
     [quick start](#self-hosting-quick-start) above.
4. make your changes (swap the training data, adjust `config.json`,
   modify the code), commit, and push back to your fork whenever you're
   ready.
5. if you build something you think improves the original project, open a
   pull request back to this repo (see [Contributing](#contributing)).

your fork is entirely independent — you can rename it, make it private,
and take it in any direction without needing permission from anyone.

## contributing

contributions are welcome, whether that's a bug fix, a documentation
improvement, or a new feature.

1. **fork** the repo and create a branch for your change:
   ```bash
   git checkout -b my-change
   ```
2. **make your change.** keep the project's goals in mind — simplicity
   and readability over raw model performance. comment non-obvious code
   the way the rest of the project does.
3. **test it.** At minimum, run through the quick start above end to end
   (train on the example dataset, generate text, run the api if you
   touched `api.py`) and confirm nothing broke.
4. **commit and push** to your fork:
   ```bash
   git commit -m "Describe your change"
   git push origin my-change
   ```
5. **open a pull request** against this repo, with a short description of
   what changed and why.

### reporting issues

if you find a bug or have a feature request, open an issue describing:
- What you expected to happen
- What actually happened
- Steps to reproduce (your `config.json` settings and roughly how much
  training data you used, if relevant)

### what kinds of contributions fit well here

- bug fixes and clearer error messages
- documentation improvements
- small, well-explained features that stay in the spirit of "simple and
  educational" rather than adding heavy dependencies or complexity
- additional example datasets or configuration presets

large architectural changes are welcome too, but consider opening an issue
to discuss the approach first, since they're more likely to need
back-and-forth before merging.

## roadmap

ideas being considered for future versions (not promises, just direction):

- optional retrieval-augmented generation (rag) support, for grounding
  responses in a document set instead of relying purely on trained
  weights
- additional tokenizer options beyond character-level
- axample integrations for common self-hosting setups

open an issue if there's something specific you'd like to see.

## License

mit — see [licence](LICENSE). use it, modify it, fork it, ship it as your
own project, all without restriction.

## Disclaimer

this project produces small, educational language models trained on
whatever data you provide. it is not, and is not intended to be, a
replacement for large commercial models like chatgpt or claude. output
quality depends entirely on your training data, model size, and training
time — expect a model that reflects patterns in your data, not one with
broad general knowledge or reliable factual accuracy.
