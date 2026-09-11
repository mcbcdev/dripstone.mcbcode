# Examples

These are copy-pasteable commands showing the full workflow, using the
example dataset that already ships in `data/training.txt`. Run all commands
from inside the `ai-template` folder.

## 1. Install dependencies

```
pip install -r requirements.txt
```

## 2. Train a model

```
python src/train.py
```

With the default `config.json` settings and the small example dataset, this
trains a tiny model in a few minutes on a normal laptop CPU. You'll see
output like this as it trains:

```
Using device: cpu
Built a new tokenizer with 58 unique characters, saved to 'checkpoints/vocab.json'.
Training data: 4213 tokens total (3791 train / 422 val)
Model created with 813,626 parameters.
Starting training: iteration 0 -> 3000
iter      0 | train loss 4.2117 | val loss 4.2094 | elapsed 0.0 min
iter    250 | train loss 2.1043 | val loss 2.2381 | elapsed 0.4 min
iter    500 | train loss 1.7822 | val loss 1.9560 | elapsed 0.8 min
...
Training finished.
Final checkpoint: checkpoints/latest.pt
```

(Your exact numbers will differ - this is just an example of the shape of
the output.)

## 3. Generate text

```
python src/generate.py --prompt "The sun rose"
```

Right after training on the small example dataset for the default number of
iterations, don't expect polished writing - expect something that has
picked up on spelling, spacing, and some local sentence patterns from the
training text, but doesn't yet form fully coherent, original sentences of
its own. That's normal for a model this small trained this briefly. See the
main README's "What to realistically expect" section for more on this.

Try different settings to see how they change the output:

```
python src/generate.py --prompt "The garden" --temperature 0.5
python src/generate.py --prompt "The garden" --temperature 1.2
python src/generate.py --prompt "The garden" --max_new_tokens 500
```

## 4. Stop and resume training

You can stop training at any time (Ctrl+C, or just closing the window) - a
checkpoint is saved periodically, so you won't lose much progress. To pick
back up where you left off:

```
python src/train.py --resume
```

## 5. (Optional) Run the local API

```
pip install flask
python src/api.py
```

Then, in a separate terminal:

```
curl -X POST http://localhost:8000/generate -H "Content-Type: application/json" -d "{\"prompt\": \"The sun rose\"}"
```

## 6. Try your own data

Replace the contents of `data/training.txt` with your own text (see
`data/README.md`), delete the `checkpoints/` folder's contents (or just
`latest.pt` and `vocab.json`) so you start a fresh vocabulary, and run
`python src/train.py` again.
