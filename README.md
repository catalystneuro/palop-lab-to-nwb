# palop-lab-to-nwb
Open-field experiment on J20 mice cohort

NWB conversion scripts for Palop Lab data, using [NeuroConv](https://github.com/catalystneuro/neuroconv).

## Installation

```bash
uv venv
source .venv/bin/activate
uv pip install -e ".[j20_open_field]"
```

## J20 open field

Open-field video, DeepLabCut pose estimates (ndx-pose) and DeepLabCut training frames for J20-FVB mice.
See [conversion_notes.md](src/palop_lab_to_nwb/j20_open_field/conversion_notes.md).

### Single session

```python
from palop_lab_to_nwb.j20_open_field.j20_open_field_convert_session import session_to_nwb

session_to_nwb(
    data_dir_path="/Volumes/seagate_0/vame/J20",
    output_dir_path="/path/to/nwb_output",
    session_id="MetaSession3",
)
```

### All sessions

```python
from palop_lab_to_nwb.j20_open_field.j20_open_field_convert_all_sessions import dataset_to_nwb

if __name__ == "__main__":
    dataset_to_nwb(
        data_dir_path="/Volumes/seagate_0/vame/J20",
        output_dir_path="/path/to/nwb_output",
        max_workers=4,
    )
```

Errors for individual sessions are written to `<output_dir_path>/exceptions/<session_id>.txt`.
