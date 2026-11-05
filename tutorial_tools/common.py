"""Paths, plotting defaults and the one-sided Fourier inner product.

No dependency on the instructor's lecture directory or external TDC files.
"""
from pathlib import Path
import os
import sys

for key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
            "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[key] = "1"

BASE = Path(__file__).resolve().parents[1]
DATA = BASE / "data"
OUTPUT = BASE / "outputs"
OUTPUT.mkdir(exist_ok=True)
ORBIT = DATA / "MicroSateOrbitEclipticTCB"

# Prefer source checkouts when available; otherwise use the packages installed
# in tri_env. Both the plain clone names (Triangle-Simulator) and the GitHub
# archive names (Triangle-Simulator-master) are recognised. TRIANGLE_ROOT is
# optional, not machine-specific.
ROOT = None
SIMULATOR_NAMES = ("Triangle-Simulator", "Triangle-Simulator-master")
GB_NAMES = ("Triangle-GB", "Triangle-GB-main")
BBH_NAMES = ("Triangle-BBH", "Triangle-BBH-main")


def _first_directory(parent, names):
    for name in names:
        if (parent / name).is_dir():
            return name
    return None


candidates = ([Path(os.environ["TRIANGLE_ROOT"])] if os.environ.get("TRIANGLE_ROOT") else [])
candidates += [BASE, *BASE.parents]
for candidate in candidates:
    simulator = _first_directory(candidate, SIMULATOR_NAMES)
    if simulator is None:
        continue
    ROOT = candidate
    gb = _first_directory(candidate, GB_NAMES)
    bbh = _first_directory(candidate, BBH_NAMES)
    folders = [name for name in (simulator, gb, bbh) if name]
    if bbh and (candidate / bbh / "WF4Py").is_dir():
        folders.append(f"{bbh}/WF4Py")
    for folder in folders:
        sys.path.insert(0, str(candidate / folder))
    break

import numpy as np
import matplotlib.pyplot as plt

DAY = 86400.
BLUE, ORANGE, RED, GREY = "#185e92", "#d78b25", "#b54b48", "#7c8790"
plt.rcParams.update({"figure.figsize": (9, 3.5), "font.size": 11,
                     "axes.spines.top": False, "axes.spines.right": False})


def inner(a, b, weight):
    """(a|b) = 4 df Re sum(a* b / S), with weight = 4 df / S."""
    return float(np.real(np.sum(np.conj(a) * b * weight)))


def load_arrays(name):
    with np.load(DATA / name, allow_pickle=False) as z:
        return {key: z[key] for key in z.files}


