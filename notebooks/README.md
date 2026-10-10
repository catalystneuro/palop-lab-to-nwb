# J20 open field notebooks

These notebooks load and plot the NWB files produced by the `j20_open_field` conversion: overhead video
of hAPP-J20 transgenic and wild-type mice in a circular open field, with DeepLabCut pose estimates
(ndx-pose) and, for 30 sessions, the DeepLabCut training frames.

- `palop_j20_open_field_demo.ipynb`: loads one session, plots the body-center trajectory, occupancy and
  distance traveled, and compares distance traveled across all sessions by genotype and exposure.
- `behavior_video.ipynb`, `pose_estimation.ipynb`, `pose_training.ipynb`: one review notebook per data
  stream, each with the NWB objects used, plots of the stream, and a comparison against the source files.

## Installing the dependencies

```bash
conda env create --file environment.yml
conda activate palop_j20_open_field_demo
```

## Running the notebooks

```bash
jupyter notebook palop_j20_open_field_demo.ipynb
```

Update `nwb_dir_path` or `nwb_file_path` in the first code cells to point to your converted NWB files.
The review notebooks also read the source DeepLabCut files to check the conversion; update those paths too.
