# bgr8转jpeg格式

import enum

import cv2


# 导入库并显示摄像头显示组件


# import the necessary packages

# import simple_barcode_detection

import cv2

import numpy as np

import pyzbar.pyzbar as pyzbar

from PIL import Image


def bgr8_to_jpeg(value, quality=75):

    return bytes(cv2.imencode(".jpg", value)[1])


# 定义解析二维码接口


def decodeDisplay(image):

    barcodes = pyzbar.decode(image)

    for barcode in barcodes:

        # 提取二维码的边界框的位置

        # 画出图像中条形码的边界框

        (x, y, w, h) = barcode.rect

        cv2.rectangle(image, (x, y), (x + w, y + h), (225, 225, 225), 2)

        # 提取二维码数据为字节对象，所以如果我们想在输出图像上

        # 画出来，就需要先将它转换成字符串

        barcodeData = barcode.data.decode("utf-8")

        barcodeType = barcode.type

        # 绘出图像上条形码的数据和条形码类型

        text = "{} ({})".format(barcodeData, barcodeType)

        cv2.putText(image, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (225, 225, 225), 2)

        # 向终端打印条形码数据和条形码类型

        print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))

    return image


def detect():

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    # camera.set(3, 320)

    # camera.set(4, 240)

    # camera.set(5, 120)  # 设置帧率

    # fourcc = cv2.VideoWriter_fourcc(*"MPEG")

    # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc("M", "J", "P", "G"))

    # camera.set(cv2.CAP_PROP_BRIGHTNESS, 40)  # 设置亮度 -64 - 64  0.0

    # camera.set(cv2.CAP_PROP_CONTRAST, 50)  # 设置对比度 -64 - 64  2.0

    # camera.set(cv2.CAP_PROP_EXPOSURE, 156)  # 设置曝光值 1.0 - 5000  156.0

    cap.set(cv2.CAP_PROP_BRIGHTNESS, 0) 
    cap.set(cv2.CAP_PROP_CONTRAST, 1) 
    cap.set(cv2.CAP_PROP_SATURATION, 1) 
    cap.set(cv2.CAP_PROP_HUE, 0) 
    cap.set(cv2.CAP_PROP_GAIN, 0)
    cap.set(cv2.CAP_PROP_EXPOSURE, -1) 
    cap.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U, -1) 
    cap.set(cv2.CAP_PROP_WHITE_BALANCE_RED_V, -1) 
    cap.set(cv2.CAP_PROP_BACKLIGHT, 0)
    cap.set(cv2.CAP_PROP_SHARPNESS, 0)
    cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 1)
    cap.set(cv2.CAP_PROP_AUTOFOCUS, 1) 
    cap.set(cv2.CAP_PROP_AUTO_WB, 1)

    ret, frame = cap.read()

    while True:

        # 读取当前帧

        ret, frame = cap.read()
        # 转为灰度图像

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        im = decodeDisplay(gray)
        cv2.imshow("emmm", frame)

        cv2.waitKey(5)

        # 如果按键q则跳出本次循环

        if cv2.waitKey(10) & 0xFF == ord("q"):

            break

    cap.release()

    cv2.destroyAllWindows()


while 1:

    detect()
