# J20 open field: conversion notes

## Experiment overview
Open-field behavior of hAPP-J20 transgenic (WT/TG) and wild-type (WT/WT) mice from the J20-FVB line, Palop Lab,
Gladstone Institutes. Experimenter: Shreya Bangera. Each mouse was filmed from above for 60 minutes in a circular
arena on two exposures (exposure 1: 2024-01-16 to 01-18, MetaSession1-55; exposure 2: 2024-01-22 to 01-23,
MetaSession56-110). Four arenas were recorded in parallel by cameras 1-4.

## Source data
Root: `/Volumes/seagate_0/vame/J20` (a DeepLabCut project folder).

| Stream | Files | Interface | Status |
|---|---|---|---|
| Behavior video | `videos/MetaSession{N}.avi` (H.264 in AVI, 1024x1024, 30 fps, ~108,271 frames) | `ExternalVideoInterface` | Implemented |
| Pose estimates | `videos/MetaSession{N}DLC_resnet50_J20_FVBApr30shuffle1_700000.h5` + `config.yaml` | `DeepLabCutInterface` (ndx-pose) | Implemented |
| DLC training frames | `training-datasets/iteration-0/UnaugmentedDataSet_J20_FVBApr30/CollectedData_SB.h5` | `DeepLabCutTrainingFramesInterface` (custom, ndx-pose `PoseTraining`) | Implemented |
| Session/subject metadata | `metadata.csv` | read in `session_to_nwb` | Implemented |
| Run-day notes | `20240110 J20-FVB Behavior Expt.xlsx` | transcribed to `j20_open_field_session_notes.yaml` | Implemented |

Not converted: `dlc-models/` (TensorFlow checkpoints), `evaluation-results/`, `labeled-data/` PNGs (frames are
recoverable from the video by index), the iteration-1 training set, arena lux readings, and birth cohort.

## Sessions and subjects
- 109 sessions in `metadata.csv`, 55 mice (54 with two sessions). MetaSession104 (mouse 101, exposure 2) has no video.
- `subject_id` = `mouse_id`, `session_id` = `MetaSession{N}`. Output: `sub-{mouse_id}_ses-MetaSession{N}.nwb`.
- `session_start_time` = `date` + `time` from `metadata.csv`, which match the acquisition timestamps in the original
  SpinView filenames. Timezone America/Los_Angeles.
- Subject: sex, genotype (`hAPP-J20 WT/WT` or `hAPP-J20 WT/TG`), date of birth, age in days, and that day's weight.

## Timing
Single camera per session, no external clock. DLC rows are video frames (frame counts match the AVI headers,
108,270-108,273), so pose and video share one timebase: rate 30 Hz from the DLC `_meta.pickle`, starting time 0.
SpinView logged ~108,298 saved frames, about 27 more than the AVIs hold; DLC ran on the AVIs so nothing is misaligned.

## DeepLabCut
- All 109 pose files come from iteration 0 (ResNet-50, shuffle 1, snapshot 700000), run 2024-05-19 to 05-22.
- Training frames: the 449 iteration-0 labels (30 sessions, ~15 frames each) are the training set of that model and
  are written as `PoseTraining` in the matching session files, linked to the session's `BehaviorVideo` by frame index.
  The 1,679 iteration-1 labels postdate the inference and are not included.
- `config.yaml` defines only two skeleton edges (Nose-FLPaw, FLPaw-FRPaw); written as given.
- `config.yaml` repeats some `video_sets` keys, which neuroconv's ruamel reader rejects. The config is not passed to
  `DeepLabCutInterface`; edges are read from it with PyYAML in `session_to_nwb`.
- Series are named by bodypart (`FLPaw`), not neuroconv's `PoseEstimationSeriesFlpaw`; skeleton is named `Skeleton`.
- Labeled positions agree with the DLC predictions at the same frame index (within ~2 px), confirming alignment.
- `hdmf-zarr<0.14` is pinned: neuroconv 0.10.2 imports the zarr 2 API and hdmf-zarr 0.14 pulls zarr 3.
- Pose `dimensions` and `original_videos` are dropped (deprecated in ndx-pose 0.4.0); the container links to the
  `BehaviorVideo` ImageSeries through `source_video` instead.
- neuroconv 0.10.2 passes the camera as `devices=[...]`, which ndx-pose 0.4.0 deprecates in favor of `device`.
  Expect a DeprecationWarning until neuroconv updates.

## Open questions
- [ ] `strain` is set to `FVB`, the background named in the lab's line name `J20-FVB`; ask the lab for the FVB
  substrain (e.g. FVB/NJ). `genotype` carries the transgene status using the spreadsheet's Genotype column
  (`hAPP-J20 WT/WT`, `hAPP-J20 WT/TG`).
- [ ] Related publication or protocol (IACUC) to cite.

Decided not to include: arena dimensions (not available), train/test split of the training frames.

## Status
- [x] Data inspection, interface mapping, metadata
- [x] Conversion code
- [x] Stub test on one session, NWB Inspector
- [x] Full conversion (2026-10-10): 109 files, 55 subjects, 30 with PoseTraining, no errors. Inspector reports only
  absolute `external_file` paths (fixed by `dandi organize`) and a missing Subject description (suggestion).
- [x] Example notebooks (`notebooks/`): demo plus one review notebook per stream, all executed against the converted files
- [ ] DANDI sandbox upload (`dandi organize` moves the AVIs next to the NWB files)
