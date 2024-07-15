# 本文件定义了一个摄像头服务功能
# 会维护一个线程来做一些图像识别功能
# 当小车需要识别一些东西的时候，直接访问线程中的全局静态变量即可，方便开发

from enum import Enum
import threading
import cv2
import cv2.aruco as aruco
import pyzbar.pyzbar as pyzbar
import time
import ImOutput


# 定义识别的物体类型
class ObjectType(Enum):
    box = 0
    barrier = 1
    null = 2


# 定义二维码识别功能模块
class QRCodeModule:
    qrCodeInfo = None

    # 使用pyzbar库识别二维码
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


# 定义Aruco码识别模块
class ArucoModule:
    # 定义需要识别的Aruco码的Id
    arucoCodeList = [0, 1]
    frontObject = ObjectType.null

    # 判断识别的Aruco码是否在列表中
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

    # 检测是否有Aruco码
    # 小车的python版本为3.7，且上面最新的opencv版本为4.4.56
    # 然而，关于Aruco的api在后面的版本中有修改，这里注释的部分是之后版本的写法
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


# 定义摄像头服务
class Service:
    # 摄像头参数部分
    enable = False
    enableQRCodeModule = False
    showCamera = True
    wait = 10
    # 摄像头服务变量部分
    thread = None
    frame = None
    video = None
    scale = 0.5
    fps = 0
    size = (0, 0)

    # 线程循环
    def ScanLoop():
        if not Service.enable:
            return
        while Service.enable:
            ret, temp = Service.video.read()
            temp = cv2.resize(temp, None, fx=Service.scale, fy=Service.scale, interpolation=cv2.INTER_CUBIC)
            temp = ArucoModule.ScanArucoCode(temp)
            if Service.enableQRCodeModule:
                temp = QRCodeModule.ScanQRCode(temp)
            else:
                QRCodeModule.qrCodeInfo = ""
            if Service.showCamera:
                cv2.imshow("Camera", temp)
            else:
                cv2.destroyWindow("Camera")
            Service.frame = temp
            cv2.waitKey(Service.wait)
        Service.video.release()

    # 启动服务
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
        # 新建并启动线程
        Service.thread = threading.Thread(target=Service.ScanLoop)
        Service.thread.start()

    # 关闭服务
    def Stop():
        Service.enable = False


if __name__ == "__main__":
    Service.Start()
    time.sleep(10)
    Service.Stop()
