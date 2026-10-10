from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
from neuroconv.utils import dict_deep_update, load_dict_from_file

from palop_lab_to_nwb.j20_open_field import J20OpenFieldNWBConverter

TIMEZONE = ZoneInfo("America/Los_Angeles")
DLC_SCORER = "DLC_resnet50_J20_FVBApr30shuffle1_700000"
DLC_TRAINING_FILE = Path("training-datasets/iteration-0/UnaugmentedDataSet_J20_FVBApr30/CollectedData_SB.h5")
GENOTYPES = dict(WT="hAPP-J20 WT/WT", TG="hAPP-J20 WT/TG")


def get_sessions(data_dir_path: str | Path) -> pd.DataFrame:
    """Session table from metadata.csv, indexed by session name."""
    return pd.read_csv(Path(data_dir_path) / "metadata.csv", dtype=str).set_index("session")


def session_to_nwb(
    data_dir_path: str | Path,
    output_dir_path: str | Path,
    session_id: str,
    stub_test: bool = False,
    overwrite: bool = False,
):
    data_dir_path = Path(data_dir_path)
    output_dir_path = Path(output_dir_path)
    if stub_test:
        output_dir_path = output_dir_path / "nwb_stub"
    output_dir_path.mkdir(parents=True, exist_ok=True)

    session = get_sessions(data_dir_path).loc[session_id]
    subject_id = session["mouse_id"]
    video_name = session["video"]
    videos_dir_path = data_dir_path / "videos"
    dlc_meta = pd.read_pickle(videos_dir_path / f"{video_name}{DLC_SCORER}_meta.pickle")["data"]

    source_data = dict(
        Video=dict(
            file_paths=[videos_dir_path / f"{video_name}.avi"],
            metadata_key="behavior_video",
            video_name="BehaviorVideo",
        ),
        PoseEstimation=dict(
            file_path=videos_dir_path / f"{video_name}{DLC_SCORER}.h5",
            sampling_frequency=dlc_meta["fps"],
        ),
    )
    conversion_options = dict()

    training_file_path = data_dir_path / DLC_TRAINING_FILE
    if video_name in pd.read_hdf(training_file_path).index.get_level_values(1):
        source_data["PoseTraining"] = dict(file_path=training_file_path, video_name=video_name)
        conversion_options["PoseTraining"] = dict(
            skeleton_metadata_key="deep_lab_cut_metadata_key", video_metadata_key="behavior_video"
        )

    converter = J20OpenFieldNWBConverter(source_data=source_data)

    metadata = converter.get_metadata()
    editable_metadata = load_dict_from_file(Path(__file__).parent / "j20_open_field_metadata.yaml")
    metadata = dict_deep_update(metadata, editable_metadata, append_list=False)

    session_start_time = datetime.fromisoformat(f"{session['date']}T{session['time']}").replace(tzinfo=TIMEZONE)
    date_of_birth = datetime.fromisoformat(session["dob"]).replace(tzinfo=TIMEZONE)
    session_notes = load_dict_from_file(Path(__file__).parent / "j20_open_field_session_notes.yaml")

    metadata["NWBFile"].update(
        session_start_time=session_start_time,
        session_id=session_id,
        session_description=(
            f"60-minute open-field session, exposure {session['exposure']} of 2, "
            f"recorded with overhead camera {session['camera']}."
        ),
    )
    if session_id in session_notes:
        metadata["NWBFile"]["notes"] = session_notes[session_id]

    metadata["Subject"].update(
        subject_id=subject_id,
        sex=session["sex"],
        genotype=GENOTYPES[session["genotype"]],
        date_of_birth=date_of_birth,
        age=f"P{(session_start_time.date() - date_of_birth.date()).days}D",
        weight=f"{session['weight_g']} g",
    )

    camera_metadata_key = "behavior_video_camera"
    metadata["Devices"][camera_metadata_key] = dict(
        name=f"Camera{session['camera']}",
        description=f"Overhead camera {session['camera']} of the four-arena open-field rig.",
    )

    pose_estimation = metadata["Pose"]["PoseEstimations"]["deep_lab_cut_metadata_key"]
    pose_estimation.pop("dimensions", None)
    pose_estimation.pop("original_videos", None)
    pose_estimation.update(device_metadata_key=camera_metadata_key, source_video_metadata_key="behavior_video")
    for bodypart, series in pose_estimation["PoseEstimationSeries"].items():
        series.update(name=bodypart, confidence_definition="Softmax output of the deep neural network.")
    # config.yaml repeats some video_sets keys, which neuroconv's strict YAML reader rejects
    dlc_config = load_dict_from_file(data_dir_path / "config.yaml")
    bodyparts = dlc_config["bodyparts"]
    skeleton = metadata["Pose"]["Skeletons"]["deep_lab_cut_metadata_key"]
    skeleton.update(
        subject=subject_id,
        edges=[[bodyparts.index(node_a), bodyparts.index(node_b)] for node_a, node_b in dlc_config["skeleton"]],
    )

    nwbfile_path = output_dir_path / f"sub-{subject_id}_ses-{session_id}.nwb"
    converter.run_conversion(
        nwbfile_path=nwbfile_path,
        metadata=metadata,
        conversion_options=conversion_options,
        overwrite=overwrite,
    )
    return nwbfile_path


if __name__ == "__main__":
    data_dir_path = Path("/Volumes/seagate_0/vame/J20")
    output_dir_path = Path("~/conversion_nwb/palop-lab-to-nwb").expanduser()

    session_to_nwb(
        data_dir_path=data_dir_path,
        output_dir_path=output_dir_path,
        session_id="MetaSession3",
        stub_test=True,
        overwrite=True,
    )
