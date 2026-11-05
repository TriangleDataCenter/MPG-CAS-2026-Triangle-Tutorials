# Mock LISA/Taiji Data Challenge — hands-on tutorial

Five  Jupyter notebooks for the hands-on session of the MPG-CAS
Summer School 2026. You should install the simulation / analysis codes that your chosen notebooks use:

* **Triangle-Simulator** — required by every notebook;
* **Triangle-GB** — only for the galactic-binary (GB) exercises, notebooks 02–03;
* **Triangle-BBH** — only for the massive black-hole binary (MBHB) exercises,
  notebooks 04–05.


## Requirements

* **Linux or macOS.**.
* **Git** and **conda** (Miniconda or Anaconda).
* **Python 3.9**, as required by the Triangle packages.


All commands below are run in the `tri_env` conda environment
activated.

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

The rest of the instructions assume this layout: 
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

This installs Jupyter, `bilby`, `nessai`, `nessai-bilby`, and `tqdm`.

#### Triangle-GB — notebooks 02 and 03 only

```sh
cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/Triangle-GB.git
uv pip install -e Triangle-GB
```

#### Triangle-BBH — notebooks 04 and 05 only


```sh
cd ~/triangle-tutorials
git clone https://github.com/TriangleDataCenter/Triangle-BBH.git
uv pip install ./Triangle-BBH/WF4Py
uv pip install -e Triangle-BBH
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

