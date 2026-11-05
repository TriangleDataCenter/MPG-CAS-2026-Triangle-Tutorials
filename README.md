# Mock LISA/Taiji Data Challenge — hands-on tutorial

Five short, CPU-only Jupyter notebooks for the hands-on session of the MPG-CAS
Summer School 2026. Start with notebook 01 and continue in order; each notebook
also runs on its own.

The repository is self-contained: the notebooks, a small `tutorial_tools/`
helper package and the numerical inputs they need are all included. You install
only the scientific codes that your chosen notebooks use:

* **Triangle-Simulator** — required by every notebook;
* **Triangle-GB** — only for the galactic-binary (GB) exercises, notebooks 02–03;
* **Triangle-BBH** — only for the massive black-hole binary (MBHB) exercises,
  notebooks 04–05.

## Notebooks

| Notebook | What you will do | Data / source SNR | Extra packages |
| --- | --- | --- | --- |
| [01 — Simulated TDI data and custom sources](01_Simulated_TDI_Data_and_Custom_Sources.ipynb) | Simulate measurements; form xi, eta and A/E/T; plot time series and ASD; compute five source responses | Ten-day **one-GB + one-MBHB** simulation with instrumental noise, using Tutorial 4 source parameters; separate one-day signal-only gallery. No target SNR normalisation. | Triangle-Simulator |
| [02 — GB search and parameter estimation](02_GB_Search_and_Parameter_Estimation.ipynb) | F-statistic + differential evolution; reconstruct/subtract; one-source and joint two-source nessai posteriors | One year, seeded Gaussian noise; optimal A/E SNRs **55 and 40** | + Triangle-GB, bilby, nessai |
| [03 — GB sky localisation](03_GB_LISA_and_Detector_Network.ipynb) | Compare LISA and LISA+Taiji+TianQin using a nonlinear sky likelihood | **Zero noise**; LISA A/E SNR **30**, network ≈54.3 | + Triangle-GB, bilby, nessai |
| [04 — MBHB search, inference and likelihoods](04_MBHB_Search_Parameter_Estimation_and_Likelihoods.ipynb) | Reconstruct the TDC signal; compare full and heterodyned likelihoods; nessai setup | Original noisy TDC II-0.2 five-day cut; optimal A/E SNR **≈1090.7** | + Triangle-BBH (WF4Py CPU), bilby |
| [05 — MBHB sky localisation](05_MBHB_LISA_and_Detector_Network.ipynb) | Compare LISA and the three-detector network using the same zero-noise source | **Zero noise**; LISA A/E SNR **80** | + Triangle-BBH (WF4Py CPU), bilby, nessai |

## Requirements

* **Linux or macOS.** The notebooks use the `fork` multiprocessing start method,
  which Windows does not provide.
* **Git** and **conda** (Miniconda or Anaconda).
* **Python 3.9**, as required by the Triangle packages.
* CPU only: no GPU and no internet access during the exercises.
* About 3 GB of disk space for the conda environment. The repository itself is
  about 5 MB.

All commands below are run in a shell with the `tri_env` conda environment
activated (from step 3 onwards).

## Installation

The instructions start from a clean machine. Clone this repository first, then
clone and install the scientific packages it needs.

### 1. Clone this repository

```sh
mkdir -p ~/triangle-tutorials
cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/MPG-CAS-2026-Triangle-Tutorials.git tutorials
cd tutorials
```

The rest of the instructions assume this layout, with the Triangle checkouts
**next to** `tutorials/`:

```
~/triangle-tutorials/
├── tutorials/            <- this repository
├── Triangle-Simulator/   <- required
├── Triangle-GB/          <- optional (notebooks 02-03)
└── Triangle-BBH/         <- optional (notebooks 04-05)
```

`tutorial_tools/common.py` finds these checkouts automatically, whether they sit
next to this repository or inside it (the latter is git-ignored). If you keep
them somewhere else, set `TRIANGLE_ROOT` to the directory that contains them
before you start Jupyter.

### 2. Create the Python environment

```sh
conda create -n tri_env -c conda-forge python=3.9.19 uv -y
conda activate tri_env
```

`uv` is used only as a fast installer. If you prefer pip, replace every
`uv pip install` below with `python -m pip install`.

### 3. Install Triangle-Simulator (required by every notebook)

```sh
cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/Triangle-Simulator.git
uv pip install -e Triangle-Simulator
```

### 4. Install only the optional parts you need

| You want to run | Triangle-Simulator | Triangle-GB | Triangle-BBH | Sampling tools |
| --- | :---: | :---: | :---: | :---: |
| Notebook 01 only | yes | — | — | — |
| Notebooks 01–03 (GB) | yes | yes | — | yes |
| Notebooks 01–05 (GB + MBHB) | yes | yes | yes | yes |
| Notebooks 01, 04, 05 (MBHB, no GB) | yes | — | yes | yes |

#### Sampling tools — notebooks 02–05

```sh
cd ~/triangle-tutorials
uv pip install -r tutorials/requirements.txt
```

This installs Jupyter, `bilby`, `nessai`, `nessai-bilby`, PyTorch and `tqdm`.
Notebook 01 needs Jupyter but none of the samplers.

#### Triangle-GB — notebooks 02 and 03 only

```sh
cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/Triangle-GB.git
uv pip install -e Triangle-GB
```

#### Triangle-BBH — notebooks 04 and 05 only

The tutorials use the **WF4Py CPU** waveform backend, so neither a GPU nor
BBHx is needed.

```sh
cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/Triangle-BBH.git
uv pip install ./Triangle-BBH/WF4Py
uv pip install -e Triangle-BBH
```

Install `Triangle-BBH` after `Triangle-Simulator`, because it imports `Triangle`
at run time.

### 5. Register the kernel and start Jupyter

```sh
cd ~/triangle-tutorials/tutorials
python -m ipykernel install --user --name tri_env --display-name "Python (tri_env)"
python -m jupyter lab
```

In JupyterLab, open notebook 01, select the **Python (tri_env)** kernel and use
**Run All**. Repeat for the other notebooks in order.

## Complete recipes for the three common cases

Every recipe starts from an empty parent directory and a fresh shell.

**A. Simulation only (notebook 01)**

```sh
mkdir -p ~/triangle-tutorials && cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/MPG-CAS-2026-Triangle-Tutorials.git tutorials
conda create -n tri_env -c conda-forge python=3.9.19 uv -y
conda activate tri_env
git clone https://github.com/TriangleDataCenter/Triangle-Simulator.git
uv pip install -e Triangle-Simulator
uv pip install jupyterlab ipykernel
cd tutorials
python -m ipykernel install --user --name tri_env --display-name "Python (tri_env)"
python -m jupyter lab
```

**B. Simulation + GB (notebooks 01–03)**

```sh
mkdir -p ~/triangle-tutorials && cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/MPG-CAS-2026-Triangle-Tutorials.git tutorials
conda create -n tri_env -c conda-forge python=3.9.19 uv -y
conda activate tri_env
git clone https://github.com/TriangleDataCenter/Triangle-Simulator.git
uv pip install -e Triangle-Simulator
git clone https://github.com/TriangleDataCenter/Triangle-GB.git
uv pip install -e Triangle-GB
uv pip install -r tutorials/requirements.txt
cd tutorials
python -m ipykernel install --user --name tri_env --display-name "Python (tri_env)"
python -m jupyter lab
```

**C. Everything (notebooks 01–05)**

```sh
mkdir -p ~/triangle-tutorials && cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/MPG-CAS-2026-Triangle-Tutorials.git tutorials
conda create -n tri_env -c conda-forge python=3.9.19 uv -y
conda activate tri_env
git clone https://github.com/TriangleDataCenter/Triangle-Simulator.git
uv pip install -e Triangle-Simulator
git clone https://github.com/TriangleDataCenter/Triangle-GB.git
uv pip install -e Triangle-GB
git clone https://github.com/TriangleDataCenter/Triangle-BBH.git
uv pip install ./Triangle-BBH/WF4Py
uv pip install -e Triangle-BBH
uv pip install -r tutorials/requirements.txt
cd tutorials
python -m ipykernel install --user --name tri_env --display-name "Python (tri_env)"
python -m jupyter lab
```

## Check the installation

With `tri_env` active and the working directory inside `tutorials/`:

```python
import Triangle
from Triangle.Orbit import Orbit
from tutorial_tools.common import ORBIT

# Only if you installed the optional packages:
# import Triangle_GB, Triangle_BBH

orbit = Orbit(OrbitDir=str(ORBIT))
print("Triangle imports OK, orbit samples:", orbit.N)
```

The imports print a few harmless CPU-only messages, such as
`pkg-config call failed`, `No pyseobnr` and `no cupy`.

## Running the notebooks

The notebooks ship with their completed outputs, but **Run All** still performs
the native calculations for the simulation, search and likelihood steps. The
expensive nested-sampling runs are opt-in, so a default pass takes 10–15
minutes on a 12-core laptop:

| Notebook | Default work | Approx. time |
| --- | --- | --- |
| 01 | fresh ten-day simulation and source gallery | 1–2 min |
| 02 | differential-evolution searches; stored posterior draws | 2 min |
| 03 | fresh two-parameter nessai runs, LISA and network | 4–5 min |
| 04 | differential-evolution search; full/heterodyned likelihood test | 1–2 min |
| 05 | fresh two-parameter nessai runs, LISA and network | 3–4 min |

Switches in the first cells control the expensive stages:

| Notebook | Switch | Default | Effect when set to `False` |
| --- | --- | --- | --- |
| 02 | `RUN_SEARCH` | `True` | reuse the stored search coordinates in `data/` |
| 02 | `RUN_INFERENCE` | `False` | no 8-D/16-D sampling; stored draws are plotted |
| 04 | `RUN_SEARCH` | `True` | reuse the stored MBHB search result |
| 04 | `RUN_NESSAI` | `False` | no 11-D sampling |

Set `RUN_INFERENCE = True` in notebook 02 or `RUN_NESSAI = True` in notebook 04
to sample from scratch; the 16-D GB run alone takes about an hour on 12 cores.
Notebooks 03 and 05 always sample a two-parameter sky posterior with nessai;
lower `nlive` there for a quick, unconverged look.

All new files are written to `outputs/`, which is git-ignored and recreated on
demand. Files in `data/` are read-only reference inputs, and no notebook
downloads anything.

## Repository layout

```
.
├── .gitignore
├── 01_Simulated_TDI_Data_and_Custom_Sources.ipynb
├── 02_GB_Search_and_Parameter_Estimation.ipynb
├── 03_GB_LISA_and_Detector_Network.ipynb
├── 04_MBHB_Search_Parameter_Estimation_and_Likelihoods.ipynb
├── 05_MBHB_LISA_and_Detector_Network.ipynb
├── tutorial_tools/            shared path setup, inner product, corner plotting
├── data/                      small numerical inputs, see data/README.md
├── figures/                   one reference posterior image used by notebook 04
├── licenses/                  licences of the upstream repositories
├── requirements.txt           extra packages for notebooks 02-05
├── environment_versions.json  versions used for the reference run
├── manifest.json              SHA-256 record of the distributed files
└── README.md

outputs/ is created at the first run and is git-ignored.
```

## Data, provenance and licences

The notebooks condense the supplied working tutorials and examples of the
Triangle project:

* Triangle-Simulator Tutorials **1, 3, 4**. The mixed data use exactly the
  GB/MBHB parameters of Tutorial 4, with its EMRI/SGWB components omitted.
  `data/emri_polarisations.npz` contains only cropped source-frame input
  polarisations; its source hash and sign convention are recorded in the
  adjacent JSON. The EMRI dynamics are not regenerated; their TDI response is.
* Triangle-GB Examples **0, 1, 2** and
  `GB_network_PE_example_for_2609.16477.ipynb`.
* Triangle-BBH Example **4 (CPU)** and
  `MBHB_network_PE_example_for_2609.16477.ipynb`.
* [TDC II-0.2 data](https://zenodo.org/records/15469724) and
  [injection parameters](https://zenodo.org/records/15532090).
  `data/mbhb_tdc_cut.json` records the exact preprocessing and input hashes.

The upstream licences are retained in `licenses/`. `manifest.json` records the
SHA-256 of every distributed file.

## Troubleshooting

**`ModuleNotFoundError: No module named 'Triangle_GB'` (or `Triangle_BBH`)**
The notebook you are running needs an optional package. Install it as in step 4,
or start with a notebook that only needs Triangle-Simulator.

**`ModuleNotFoundError: No module named 'Triangle'`**
Triangle-Simulator is missing, or Jupyter was started outside `tri_env`:

```sh
conda activate tri_env
python -m ipykernel install --user --name tri_env --display-name "Python (tri_env)"
```

**The kernel list has no "Python (tri_env)"**
Register the kernel from the active environment (step 5) and restart JupyterLab.

**`pkg-config call failed`, `No pyseobnr`, `no cupy`, `No CuPy or GPU PhenomHM module`**
Expected messages from PyCBC and Triangle on a CPU-only machine. They do not
affect the notebooks.

**Sampling is slow**
Nested sampling dominates the runtime. Use the switches above, or reduce `nlive`
in the sampling cell. The stored outputs are a reference, not a convergence
guarantee.

**Windows**
Not supported: the notebooks rely on the `fork` start method. Use Linux, macOS
or WSL.

## Tested environment

`environment_versions.json` records the versions used for the reference run:
Python 3.9.19, numpy 1.26.4, scipy 1.13.1, matplotlib 3.9.4, pandas 2.3.0,
bilby 2.3.0, nessai 0.14.0, nessai-bilby 0.1.0, torch 2.7.1, h5py 3.13.0,
healpy 1.17.3 and pycbc 2.7.2.
