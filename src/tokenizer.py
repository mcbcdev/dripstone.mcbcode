"""
tokenizer.py

This file turns raw text into numbers (called "tokens") that the model can
learn from, and turns the model's number output back into readable text.

We use a "character-level" tokenizer here. That means every single character
(letters, spaces, punctuation, emoji, etc.) gets its own number. This is the
simplest possible way to do it, needs zero extra libraries, and is easy to
understand end to end. It is not as efficient as the "subword" tokenizers
that big models like GPT use, but for a small educational model it works
fine and keeps this project simple.

Used by:
- train.py    (builds the vocabulary from your training data, saves it)
- dataset.py  (indirectly, via the token ids train.py hands it)
- generate.py (loads the saved vocabulary, encodes your prompt, decodes output)
- api.py      (same job as generate.py, just behind a web server)
"""

import json
import os


class CharTokenizer:
    def __init__(self, vocab=None):
        # `vocab` is a list of every unique character seen in the training text.
        # Its position in the list IS the token id for that character.
        self.vocab = vocab or []
        self.char_to_id = {ch: i for i, ch in enumerate(self.vocab)}
        self.id_to_char = {i: ch for i, ch in enumerate(self.vocab)}

    @classmethod
    def build_from_text(cls, text):
        """
        Scans a piece of text and builds a vocabulary containing every unique
        character in it. Call this once, on your training data, before training.
        """
        if len(text) == 0:
            raise ValueError("Cannot build a tokenizer from empty text.")
        unique_chars = sorted(set(text))
        return cls(vocab=unique_chars)

    @property
    def vocab_size(self):
        return len(self.vocab)

    def encode(self, text):
        """
        Turns a string into a list of integers.
        Example: "hi" -> [7, 12]
        """
        try:
            return [self.char_to_id[ch] for ch in text]
        except KeyError as err:
            bad_char = err.args[0]
            raise ValueError(
                f"The character {bad_char!r} does not appear anywhere in the data "
                f"this model was trained on, so it can't be encoded. This usually "
                f"happens when your prompt uses a symbol, letter, or emoji that "
                f"wasn't in data/training.txt. Either remove it from your prompt, "
                f"or add examples containing it to your training data and retrain."
            )

    def decode(self, ids):
        """
        Turns a list of integers back into a string.
        Example: [7, 12] -> "hi"
        """
        return "".join(self.id_to_char[i] for i in ids)

    def save(self, path):
        """Saves the vocabulary to a JSON file so it can be reloaded later,
        without needing the original training text again."""
        directory = os.path.dirname(path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.vocab, f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, path):
        """Loads a vocabulary that was previously saved with .save()."""
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No tokenizer vocabulary found at '{path}'. You need to train a "
                f"model first (run: python src/train.py) before you can generate "
                f"text or start the API - training is what creates this file."
            )
        with open(path, "r", encoding="utf-8") as f:
            vocab = json.load(f)
        return cls(vocab=vocab)
