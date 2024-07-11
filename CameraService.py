from enum import Enum
import threading
import cv2
import cv2.aruco as aruco
import time

arucoCodeList = [0, 1]


class ObjectType(Enum):
    box = 0
    barrier = 1
    null = 2


def IsInCodeList(ids: list) -> ObjectType:
    if ids is None:
        return ObjectType.null
    id_to_type = {
        arucoCodeList[0]: ObjectType.barrier,
        arucoCodeList[1]: ObjectType.box,
    }
    for id in ids:
        if id[0] in id_to_type:
            print(id_to_type[id[0]])
            return id_to_type[id[0]]
    return ObjectType.null


def ScanHasArucoCode(mat, scale: float = 1):
    frame = mat
    frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    # parameters = aruco.DetectorParameters()
    parameters = aruco.DetectorParameters_create()
    # detector = aruco.ArucoDetector(aruco_dict, parameters)
    # corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
    aruco.drawDetectedMarkers(frame, corners, ids)
    cv2.imshow("Aruco", frame)
    return IsInCodeList(ids)


class Service:
    thread = None
    frame = None
    video = None
    enable = False
    fps = 0
    size = (0, 0)

    frontObject = ObjectType.null

    qrCodeCallback = None
    qrCodeFlag = False
    qrCodeInfo = ""

    def ScanLoop():
        if not Service.enable:
            return
        while Service.enable:
            ret, Service.frame = Service.video.read()
            Service.frontObject = ScanHasArucoCode(Service.frame, 0.5)
            cv2.waitKey(10)
        Service.video.release()

    def Start(api=cv2.CAP_ANY):
        Service.enable = True
        Service.video = cv2.VideoCapture(0, api)
        Service.fps = Service.video.get(cv2.CAP_PROP_FPS)
        Service.size = (
            int(Service.video.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(Service.video.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        ret, Service.frame = Service.video.read()
        Service.thread = threading.Thread(target=Service.ScanLoop)
        Service.thread.start()

    def Stop():
        Service.enable = False

    def __init__(self) -> None:
        pass


if __name__ == "__main__":
    Service.Start()
    time.sleep(10)
    Service.Stop()
