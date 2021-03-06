import torch
import torch.nn as nn
from torch import Tensor
from typing import Optional, Tuple


class ListenAttendSpell(nn.Module):
    """
    Listen, Attend and Spell (LAS) Model

    Args:
        listener (torch.nn.Module): encoder of seq2seq
        speller (torch.nn.Module): decoder of seq2seq

    Inputs: inputs, input_lengths, targets, teacher_forcing_ratio
        - **inputs** (torch.Tensor): tensor of sequences, whose length is the batch size and within which
          each sequence is a list of token IDs. This information is forwarded to the encoder.
        - **input_lengths** (torch.Tensor): tensor of sequences, whose contains length of inputs.
        - **targets** (torch.Tensor): tensor of sequences, whose length is the batch size and within which
          each sequence is a list of token IDs. This information is forwarded to the decoder.
        - **teacher_forcing_ratio** (float): The probability that teacher forcing will be used. A random number
          is drawn uniformly from 0-1 for every decoding token, and if the sample is smaller than the given value,
          teacher forcing would be used (default is 0.90)

    Returns: output
        - **output** (seq_len, batch_size, num_classes): list of tensors containing
          the outputs of the decoding function.

    Reference:
        - **Listen Attend and Spell**: https://arxiv.org/abs/1508.01211
    """
    def __init__(self, listener: nn.Module, speller: nn.Module) -> None:
        super(ListenAttendSpell, self).__init__()
        self.listener = listener
        self.speller = speller

    def forward(self, inputs: Tensor, input_lengths: Tensor, targets: Optional[Tensor] = None,
                teacher_forcing_ratio: float = 1.0, language_model: Optional[nn.Module] = None) -> Tuple[Tensor, dict]:
        encoder_outputs = self.listener(inputs, input_lengths)
        result = self.speller(targets, encoder_outputs, teacher_forcing_ratio, language_model)
        return result

    def flatten_parameters(self):
        self.listener.rnn.flatten_parameters()
        self.speller.rnn.flatten_parameters()

    def set_speller(self, decoder: nn.Module):
        self.speller = decoder
