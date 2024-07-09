import cv2

if __name__ == "__main__":
    video = cv2.VideoCapture(0)
    fps = video.get(cv2.CAP_PROP_FPS)
    print(fps)
    size = (int(video.get(cv2.CAP_PROP_FRAME_WIDTH)), int(video.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    print(size)
    while True:
        ret, frame = video.read()
        cv2.imshow("A video", frame)
        c = cv2.waitKey(1)
        if c == 27:
            break
    video.release()
    cv2.destroyAllWindows()
