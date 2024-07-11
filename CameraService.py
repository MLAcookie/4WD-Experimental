import thread
import cv2


class CameraService:
    enable = False
    video = 0
    fps = 0
    size = (0, 0)
    frame = []

    def ScanLoop():
        while CameraService.enable:
            pass

    def Start():
        CameraService.enable = True
        CameraService.video = cv2.VideoCapture(0)
        CameraService.fps = CameraService.video.get(cv2.CAP_PROP_FPS)
        CameraService.size = (
            int(CameraService.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(CameraService.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        pass

    def Stop():
        CameraService.enable = False

    def __init__(self) -> None:
        pass
