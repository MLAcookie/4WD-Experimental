from enum import Enum
import cv2
import cv2.aruco as aruco
import numpy as np

arucoCodeList = [0, 1]


class ObjectType(Enum):
    box = 0
    barrier = 1
    null = 2


def IsInCodeList(ids: list) -> ObjectType:
    if ids is None:
        return ObjectType.null
    id_to_type = {
        arucoCodeList[0]: ObjectType.box,
        arucoCodeList[1]: ObjectType.barrier,
    }
    for id in ids:
        if id[0] in id_to_type:
            return id_to_type[id[0]]
    return ObjectType.null


def ScanHasArucoCode(mat: np.matrix, scale: float = 1):
    frame = mat
    frame = cv2.resize(frame, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
    parameters = aruco.DetectorParameters()
    detector = aruco.ArucoDetector(aruco_dict, parameters)
    corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
    aruco.drawDetectedMarkers(frame, corners, ids)
    return frame


if __name__ == "__main__":
    video = cv2.VideoCapture(0)
    fps = video.get(cv2.CAP_PROP_FPS)
    print(fps)
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print(size)
    while True:
        ret, frame = video.read()
        cv2.imshow("A video", ScanHasArucoCode(frame))
        c = cv2.waitKey(1)
        if c == 27:
            break
    video.release()
    cv2.destroyAllWindows()
