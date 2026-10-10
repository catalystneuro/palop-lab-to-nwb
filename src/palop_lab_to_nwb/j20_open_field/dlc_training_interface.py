from pathlib import Path

import numpy as np
import pandas as pd
from ndx_pose import PoseTraining, SkeletonInstance, SkeletonInstances, TrainingFrame, TrainingFrames
from neuroconv.basedatainterface import BaseDataInterface
from neuroconv.tools.nwb_helpers import get_module
from pydantic import FilePath
from pynwb import NWBFile


class DeepLabCutTrainingFramesInterface(BaseDataInterface):
    """Labeled frames of one video from a DeepLabCut training dataset (CollectedData_<scorer>.h5)."""

    keywords = ("DeepLabCut", "pose estimation", "training data")

    def __init__(self, file_path: FilePath, video_name: str):
        """
        Parameters
        ----------
        file_path : FilePath
            Path to the CollectedData_<scorer>.h5 file of a DeepLabCut training dataset.
        video_name : str
            Name of the video whose labeled frames are written, as it appears in the labeled-data folder.
        """
        super().__init__(file_path=file_path, video_name=video_name)

    def get_labels(self) -> pd.DataFrame:
        labels = pd.read_hdf(self.source_data["file_path"])
        return labels[labels.index.get_level_values(1) == self.source_data["video_name"]]

    def add_to_nwbfile(
        self,
        nwbfile: NWBFile,
        metadata: dict,
        skeleton_metadata_key: str = "deep_lab_cut_metadata_key",
        video_metadata_key: str = "behavior_video",
    ):
        labels = self.get_labels()
        if labels.empty:
            raise ValueError(f"No labeled frames for '{self.source_data['video_name']}' in {self.source_data['file_path']}.")

        behavior_module = get_module(nwbfile=nwbfile, name="behavior", description="processed behavioral data")
        skeleton_name = metadata["Pose"]["Skeletons"][skeleton_metadata_key]["name"]
        skeleton = behavior_module["Skeletons"].skeletons[skeleton_name]
        source_video = nwbfile.acquisition[metadata["Behavior"]["ExternalVideos"][video_metadata_key]["name"]]
        annotator = metadata["Pose"]["PoseTraining"]["annotator"]

        bodyparts = labels.columns.get_level_values("bodyparts")[::2].tolist()
        if bodyparts != list(skeleton.nodes):
            raise ValueError(f"Labeled bodyparts {bodyparts} do not match the skeleton nodes {list(skeleton.nodes)}.")
        node_locations_per_frame = labels.to_numpy().reshape(len(labels), len(bodyparts), 2)

        training_frames = []
        for (_, _, image_name), node_locations in zip(labels.index, node_locations_per_frame):
            frame_index = int(Path(image_name).stem.removeprefix("img"))
            skeleton_instance = SkeletonInstance(
                id=np.uint8(0),
                node_locations=node_locations,
                node_visibility=~np.isnan(node_locations).any(axis=1),
                skeleton=skeleton,
            )
            training_frames.append(
                TrainingFrame(
                    name=f"frame_{frame_index}",
                    annotator=annotator,
                    skeleton_instances=SkeletonInstances(skeleton_instances=[skeleton_instance]),
                    source_video=source_video,
                    source_video_frame_index=np.uint64(frame_index),
                )
            )

        behavior_module.add(PoseTraining(training_frames=TrainingFrames(training_frames=training_frames)))
