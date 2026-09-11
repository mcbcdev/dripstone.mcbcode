"""
dataset.py

Takes the full list of token ids (produced by the tokenizer from your
training text), splits it into a training set and a small validation set,
and hands out random chunks ("batches") for the model to train on.

Why a validation set? During training we only ever adjust the model based on
the training set. The validation set is data the model never directly trains
on, so checking the loss on it tells us whether the model is actually
learning general patterns, or just memorizing the training text.

Used by:
- train.py (calls get_batch(...) every training step)
"""

import torch


class TextDataset:
    def __init__(self, token_ids, block_size, val_split=0.1):
        if len(token_ids) < block_size * 2:
            raise ValueError(
                f"Your training data only produced {len(token_ids)} tokens, which "
                f"is too small for a block_size of {block_size}. Either add more "
                f"text to your training file, or lower 'block_size' in config.json."
            )

        data = torch.tensor(token_ids, dtype=torch.long)
        split_idx = int(len(data) * (1 - val_split))
        self.train_data = data[:split_idx]
        self.val_data = data[split_idx:]
        self.block_size = block_size

    def get_batch(self, split, batch_size, device):
        """
        Returns a batch of (input, target) pairs.

        For each random chunk of `block_size` tokens, the "input" (x) is the
        chunk itself, and the "target" (y) is that same chunk shifted one
        token to the right. In other words: at every position, the model's
        job is "given everything so far, predict the very next token".
        """
        data = self.train_data if split == "train" else self.val_data

        if len(data) <= self.block_size:
            raise ValueError(
                f"The '{split}' split only has {len(data)} tokens, which isn't "
                f"enough for a block_size of {self.block_size}. Add more training "
                f"data, or lower block_size / val_split in config.json."
            )

        ix = torch.randint(len(data) - self.block_size, (batch_size,))
        x = torch.stack([data[i:i + self.block_size] for i in ix])
        y = torch.stack([data[i + 1:i + 1 + self.block_size] for i in ix])
        return x.to(device), y.to(device)
