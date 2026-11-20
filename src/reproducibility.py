from __future__ import annotations

import random
import numpy as np
import torch


def set_reproducibility(seed: int) -> None:
    """Seed the relevant random number generators.

    TODO: complete this function so that Python, NumPy and PyTorch are
    controlled. Improve CUDA/cuDNN repeatability when CUDA is available.
    """
    random.seed(seed)
    np.random.seed(seed)
    
    torch.random.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False

    torch.use_deterministic_algorithms(True)


def seed_worker(worker_id: int) -> None:
    """Seed a DataLoader worker from PyTorch's worker seed."""
    worker_seed = torch.initial_seed() % (2**32)

    np.random.seed(worker_seed)
    random.seed(worker_seed)


def make_generator(seed: int) -> torch.Generator:
    """Return a seeded torch.Generator used for deterministic shuffling."""
    g = torch.Generator()
    g.manual_seed(seed)
    return g
