from enum import Enum
import threading
import cv2
import cv2.aruco as aruco
import pyzbar.pyzbar as pyzbar
import time
import ImOutput


class ObjectType(Enum):
    box = 0
    barrier = 1
    null = 2


# class GestureModule:
#     enable = False

#     APP_ID = "你的 App ID"
#     API_KEY = "你的 Api Key"
#     SECRET_KEY = "你的 Secret Key"

#     types = {
#         "one": False,
#         "two": False,
#         "there": False,
#         "four": False,
#         "five": False,
#         "six": False,
#         "seven": False,
#         "eight": False,
#         "nine": False,
#         "Fist": False,
#         "OK": False,
#         "Prayer": False,
#         "Congratulation": False,
#         "Honour": False,
#         "Heart_single": False,
#         "Thumb_up": False,
#         "Thumb_down": False,
#         "ILY": False,
#         "Palm_up": False,
#         "Heart_1": False,
#         "Heart_2": False,
#         "Heart_3": False,
#         "Rock": False,
#         "Insult": False,
#     }
#     gesture = ""


class QRCodeModule:
    qrCodeInfo = None

    def ScanQRCode(mat):
        QRCodeModule.qrCodeInfo = None
        frame = mat
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        barcodes = pyzbar.decode(gray)
        for barcode in barcodes:
            (x, y, w, h) = barcode.rect
            cv2.rectangle(frame, (x, y), (x + w, y + h), (225, 225, 225), 2)
            barcodeData = barcode.data.decode("utf-8")
            if QRCodeModule is None:
                QRCodeModule.qrCodeInfo = barcodeData
                ImOutput.Out.Println(barcodeData)
        # ImOutput.Out.Println("QRCodeScanModule: 检测到二维码")
        return frame


class ArucoModule:
    arucoCodeList = [0, 1]
    frontObject = ObjectType.null

    def IsInCodeList(ids: list):
        if ids is None:
            ArucoModule.frontObject = ObjectType.null
            return
        switch = {
            ArucoModule.arucoCodeList[0]: ObjectType.barrier,
            ArucoModule.arucoCodeList[1]: ObjectType.box,
        }
        for id in ids:
            if id[0] in switch:
                # ImOutput.Out.Println("ArucoModule: 识别物体为 " + str(switch[id[0]]))
                ArucoModule.frontObject = switch[id[0]]
                return
        ArucoModule.frontObject = ObjectType.null

    def ScanArucoCode(mat):
        frame = mat
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        aruco_dict = aruco.getPredefinedDictionary(aruco.DICT_6X6_250)
        # parameters = aruco.DetectorParameters()
        parameters = aruco.DetectorParameters_create()
        # detector = aruco.ArucoDetector(aruco_dict, parameters)
        # corners, ids, rejectedImgPoints = detector.detectMarkers(gray)
        corners, ids, rejectedImgPoints = aruco.detectMarkers(gray, aruco_dict, parameters=parameters)
        aruco.drawDetectedMarkers(frame, corners, ids)
        ArucoModule.IsInCodeList(ids)
        return frame


class Service:
    enable = False
    enableQRCodeModule = False
    showCamera = True
    wait = 10
    thread = None
    frame = None
    video = None
    scale = 0.5
    fps = 0
    size = (0, 0)

    def ScanLoop():
        if not Service.enable:
            return
        while Service.enable:
            ret, temp = Service.video.read()
            temp = cv2.resize(temp, None, fx=Service.scale, fy=Service.scale, interpolation=cv2.INTER_CUBIC)
            temp = ArucoModule.ScanArucoCode(temp)
            if Service.enableQRCodeModule:
                temp = QRCodeModule.ScanQRCode(temp)
            if Service.showCamera:
                cv2.imshow("Camera", temp)
            else:
                cv2.destroyWindow("Camera")
            Service.frame = temp
            cv2.waitKey(Service.wait)
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
        Service.frame = cv2.resize(
            Service.frame, None, fx=Service.scale, fy=Service.scale, interpolation=cv2.INTER_CUBIC
        )
        Service.thread = threading.Thread(target=Service.ScanLoop)
        Service.thread.start()

    def Stop():
        Service.enable = False


if __name__ == "__main__":
    Service.Start()
    time.sleep(10)
    Service.Stop()
