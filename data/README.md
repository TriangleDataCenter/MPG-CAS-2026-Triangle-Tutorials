# Data inputs

Small, read-only inputs used by the notebooks. Nothing here is generated at run
time, and the notebooks never download data. New results go to `../outputs/`.

| File | Contents | Used by |
| --- | --- | --- |
| `MicroSateOrbitEclipticTCB/SCP{1,2,3}.dat`, `SCV{1,2,3}.dat` | TDC II orbit samples: spacecraft positions and velocities of the three LISA spacecraft, daily cadence | all notebooks (`Orbit(OrbitDir=...)`) |
| `emri_polarisations.npz` | Cropped source-frame EMRI `h+`/`hx` segment used for the response gallery | 01 |
| `emri_polarisations.json` | Source file, SHA-256 and sign convention of the array above | 01 (documentation) |
| `gb_sequential_search.npz` | One-year, seeded GB search data (A/E channels) and injected signals | 02 |
| `gb_sequential_search.json` | Search setup, injections and recovered parameters of the sequential search | 02 |
| `gb_matched_single_posterior.npz` | nessai draws for the matched one-source GB posterior | 02 |
| `gb_matched_single.json` | Sampler settings and physical columns of those draws | 02 |
| `gb_matched_double_midphase_posterior.npz` | nessai draws for the joint two-source GB posterior | 02 |
| `gb_matched_double_midphase.json` | Sampler settings and physical columns of those draws | 02 |
| `gb_joint_mcmc_audit.json` | Independent local MCMC cross-check of the joint GB posterior | documentation |
| `mbhb_tdc_cut.npz` | Five-day TDC II-0.2 cut: frequency grid, A/E data and inverse-noise weights | 04 |
| `mbhb_tdc_cut.json` | Source files, input hashes, preprocessing and original search parameters | 04 |

The orbit files are copies of `OrbitData/MicroSateOrbitEclipticTCB` from
[Triangle-Simulator](https://github.com/TriangleDataCenter/Triangle-Simulator);
that directory also ships `MicroSateOrbit.hdf5`, which these notebooks do not
read.

The GB posterior files contain both the cached sampler coordinates
(`sampled_coordinates`, 8-D for one source and 16-D for two) and the matching
physical parameters (`physical_samples`: `f0`, `fdot0`, longitude, latitude,
`A`, inclination, `phase0`, `psi`), which notebook 02 plots. The MBHB cut was
produced from the public
[TDC II-0.2 data](https://zenodo.org/records/15469724) and
[injection parameters](https://zenodo.org/records/15532090); the exact
preprocessing is recorded in `mbhb_tdc_cut.json`.
