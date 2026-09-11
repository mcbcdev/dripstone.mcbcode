"""
model.py

This file defines the actual neural network: a small GPT-style ("decoder-only
transformer") language model.

In plain terms: the model reads a sequence of tokens (numbers representing
text) and learns to predict what token comes next. Do that prediction over
and over, each time feeding the new token back in, and you get generated text.

The main pieces, from simplest to most complex:
- Embeddings: turn a token id (and its position in the sequence) into a list
  of numbers ("vector") the model can do math with.
- Self-attention: lets each token look back at earlier tokens and decide
  which ones are relevant to it. This is the core trick that makes
  transformers good at language.
- Feed-forward layers: a small neural net applied to each token to further
  process what attention found.
- Blocks: one "block" is one round of attention + feed-forward. Stacking
  more blocks (n_layer) makes the model deeper and generally more capable,
  at the cost of more compute.

Used by:
- train.py    (creates a fresh model and trains its weights)
- generate.py (loads trained weights and generates text)
- api.py      (same as generate.py, behind a web server)
"""

import torch
import torch.nn as nn
from torch.nn import functional as F


class SelfAttentionHead(nn.Module):
    """
    One "head" of self-attention. A head learns one particular way of
    relating tokens to each other. Multiple heads run in parallel so the
    model can pay attention to several different kinds of relationships
    at once (e.g. one head might track grammar, another might track topic).
    """

    def __init__(self, n_embd, head_size, block_size, dropout):
        super().__init__()
        self.key = nn.Linear(n_embd, head_size, bias=False)
        self.query = nn.Linear(n_embd, head_size, bias=False)
        self.value = nn.Linear(n_embd, head_size, bias=False)

        # This "causal mask" stops a token from looking at tokens that come
        # after it - otherwise the model could cheat during training by
        # peeking at the answer.
        self.register_buffer("tril", torch.tril(torch.ones(block_size, block_size)))
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        # x shape: (batch, time/sequence length, channels/embedding size)
        B, T, C = x.shape
        k = self.key(x)     # what each token "offers"
        q = self.query(x)   # what each token is "looking for"
        v = self.value(x)   # the actual information each token carries

        # compare every query against every key to get attention scores
        wei = q @ k.transpose(-2, -1) * (k.shape[-1] ** -0.5)
        wei = wei.masked_fill(self.tril[:T, :T] == 0, float("-inf"))
        wei = F.softmax(wei, dim=-1)
        wei = self.dropout(wei)

        # blend the values together according to the attention scores
        return wei @ v


class MultiHeadAttention(nn.Module):
    """Runs several attention heads in parallel and combines their outputs."""

    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        if n_embd % n_head != 0:
            raise ValueError(
                f"n_embd ({n_embd}) must be evenly divisible by n_head ({n_head}). "
                f"Fix these values in config.json."
            )
        head_size = n_embd // n_head
        self.heads = nn.ModuleList(
            [SelfAttentionHead(n_embd, head_size, block_size, dropout) for _ in range(n_head)]
        )
        self.proj = nn.Linear(n_embd, n_embd)
        self.dropout = nn.Dropout(dropout)

    def forward(self, x):
        out = torch.cat([head(x) for head in self.heads], dim=-1)
        return self.dropout(self.proj(out))


class FeedForward(nn.Module):
    """A small 2-layer network applied independently to each token's vector."""

    def __init__(self, n_embd, dropout):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, 4 * n_embd),
            nn.GELU(),
            nn.Linear(4 * n_embd, n_embd),
            nn.Dropout(dropout),
        )

    def forward(self, x):
        return self.net(x)


class Block(nn.Module):
    """
    One transformer block: self-attention, then feed-forward, each wrapped
    with a "residual connection" (adding the input back to the output) and
    layer normalization, which are standard tricks that make deep networks
    like this one actually trainable.
    """

    def __init__(self, n_embd, n_head, block_size, dropout):
        super().__init__()
        self.sa = MultiHeadAttention(n_embd, n_head, block_size, dropout)
        self.ffwd = FeedForward(n_embd, dropout)
        self.ln1 = nn.LayerNorm(n_embd)
        self.ln2 = nn.LayerNorm(n_embd)

    def forward(self, x):
        x = x + self.sa(self.ln1(x))
        x = x + self.ffwd(self.ln2(x))
        return x


class SmallLanguageModel(nn.Module):
    """
    The full model: embeddings, a stack of Blocks, then a final layer that
    turns each token's vector into a prediction over the whole vocabulary
    (i.e. "how likely is each possible next character?").

    Arguments (all come from config.json):
      vocab_size  - how many unique tokens exist (from the tokenizer)
      n_embd      - size of each token's internal vector ("embedding dimension")
      n_head      - number of attention heads per block
      n_layer     - how many blocks are stacked (the model's "depth")
      block_size  - max number of tokens the model can look at at once
                    (a.k.a. "context length")
      dropout     - fraction of connections randomly disabled during training,
                    which helps prevent the model from just memorizing the data
    """

    def __init__(self, vocab_size, n_embd, n_head, n_layer, block_size, dropout):
        super().__init__()
        self.block_size = block_size

        self.token_embedding = nn.Embedding(vocab_size, n_embd)
        self.position_embedding = nn.Embedding(block_size, n_embd)
        self.blocks = nn.Sequential(
            *[Block(n_embd, n_head, block_size, dropout) for _ in range(n_layer)]
        )
        self.ln_f = nn.LayerNorm(n_embd)
        self.lm_head = nn.Linear(n_embd, vocab_size)

        self.apply(self._init_weights)

    def _init_weights(self, module):
        # Starting weights small and centered on zero tends to make training
        # more stable. This is a standard initialization scheme.
        if isinstance(module, nn.Linear):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)
            if module.bias is not None:
                torch.nn.init.zeros_(module.bias)
        elif isinstance(module, nn.Embedding):
            torch.nn.init.normal_(module.weight, mean=0.0, std=0.02)

    def forward(self, idx, targets=None):
        """
        idx: (batch, time) tensor of token ids.
        targets: optional (batch, time) tensor of the "correct next token" for
                 each position - only needed during training, to compute loss.
        """
        B, T = idx.shape
        if T > self.block_size:
            raise ValueError(
                f"Got a sequence of {T} tokens, but this model's block_size "
                f"(context length) is only {self.block_size}. Shorten the input, "
                f"or increase block_size in config.json and retrain from scratch."
            )

        tok_emb = self.token_embedding(idx)                          # (B, T, n_embd)
        pos_emb = self.position_embedding(torch.arange(T, device=idx.device))  # (T, n_embd)
        x = tok_emb + pos_emb
        x = self.blocks(x)
        x = self.ln_f(x)
        logits = self.lm_head(x)   # (B, T, vocab_size) - raw scores per possible next token

        loss = None
        if targets is not None:
            B, T, C = logits.shape
            loss = F.cross_entropy(logits.view(B * T, C), targets.view(B * T))

        return logits, loss

    @torch.no_grad()
    def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None):
        """
        Generates new tokens one at a time. Each newly generated token is
        appended and fed back in as input for predicting the next one -
        this is how the model "writes" text step by step.

        temperature: higher values (e.g. 1.2) make output more random/creative,
                     lower values (e.g. 0.3) make it more predictable/repetitive.
        top_k: if set, only the top_k most likely next tokens are considered
               at each step, which helps avoid picking very unlikely tokens.
        """
        for _ in range(max_new_tokens):
            # only feed in the last `block_size` tokens - that's all the
            # model is able to look at
            idx_cond = idx[:, -self.block_size:]
            logits, _ = self(idx_cond)
            logits = logits[:, -1, :] / max(temperature, 1e-5)

            if top_k is not None:
                v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
                logits[logits < v[:, [-1]]] = float("-inf")

            probs = F.softmax(logits, dim=-1)
            idx_next = torch.multinomial(probs, num_samples=1)
            idx = torch.cat((idx, idx_next), dim=1)

        return idx
