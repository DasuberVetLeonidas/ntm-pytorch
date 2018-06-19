import torch
from torch.utils.data import Dataset
from torch.distributions.binomial import Binomial


class CopyDataset(Dataset):
    """A Dataset class to generate random examples for the copy task. Each
    sequence has a random length between `min_seq_len` and `max_seq_len`.
    Each vector in the sequence has a fixed length of `seq_width`. The last
    vector is a delimeter flag denoting end of sequence.

    To account for the delimiter flag, the input sequence length as well
    width is one more than the target sequence.
    """

    def __init__(self, task_params):
        """Initialize a dataset instance for copy task.

        Arguments
        ---------
        task_params : dict
            A dict containing parameters relevant to copy task.
        """
        self.seq_width = task_params['seq_width']
        self.min_seq_len = task_params['min_seq_len']
        self.max_seq_len = task_params['max_seq_len']

    def __len__(self):
        # sequences are generated randomly so this does not matter
        # set a sufficiently large size for data loader to sample mini-batches
        return 65536

    def __getitem__(self, idx):
        # idx only acts as a counter while generating batches.
        seq_len = torch.randint(
            self.min_seq_len, self.max_seq_len, (1,), dtype=torch.long).item()
        prob = 0.5 * torch.ones([seq_len, self.seq_width], dtype=torch.float64)
        seq = Binomial(1, prob).sample()

        # fill in input sequence, one bit longer and wider than target
        # it is zero-padded upto maximum length after delimiter
        input_seq = torch.zeros([self.max_seq_len + 1, self.seq_width + 1])
        input_seq[:seq_len, :self.seq_width] = seq
        input_seq[seq_len, self.seq_width] = 1.0  # delimiter

        # fill in and zero pad target sequence similarly
        target_seq = torch.zeros([self.max_seq_len, self.seq_width])
        target_seq[:seq_len, :self.seq_width] = seq
        return {'input': input_seq, 'target': target_seq}
