from neuroconv import NWBConverter
from neuroconv.datainterfaces import DeepLabCutInterface, ExternalVideoInterface

from .dlc_training_interface import DeepLabCutTrainingFramesInterface


class J20OpenFieldNWBConverter(NWBConverter):
    """Open-field video, DeepLabCut pose estimates and DeepLabCut training frames for one session."""

    data_interface_classes = dict(
        Video=ExternalVideoInterface,
        PoseEstimation=DeepLabCutInterface,
        PoseTraining=DeepLabCutTrainingFramesInterface,
    )
