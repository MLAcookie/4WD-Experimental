import RPi.GPIO as GPIO
import time
from collections import deque
import CameraService
import Sokoban
import ImOutput

# 设置GPIO口为BCM编码方式
GPIO.setmode(GPIO.BCM)

# 忽略警告信息
GPIO.setwarnings(False)

# 管脚参数
# 小车按键定义
key = 8
# 小车电机引脚定义
IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13
# 超声波引脚定义
EchoPin = 0
TrigPin = 1
# RGB三色灯引脚定义
LED_R = 22
LED_G = 27
LED_B = 24
# 舵机引脚定义
FrontServoPin = 23
ServoUpDownPin = 9
ServoLeftRightPin = 11
# 红外避障引脚定义
AvoidSensorLeft = 12
AvoidSensorRight = 17
# 蜂鸣器引脚定义
buzzer = 8
# 灭火电机引脚设置
# OutfirePin = 2  # 灭火电机
# 循迹红外引脚定义
TrackSensorLeftPin1 = 3  # 定义左边第一个循迹红外传感器引脚为3
TrackSensorLeftPin2 = 5  # 定义左边第二个循迹红外传感器引脚为5
TrackSensorRightPin1 = 4  # 定义右边第一个循迹红外传感器引脚为4
TrackSensorRightPin2 = 18  # 定义右边第二个循迹红外传感器引脚为18
# 光敏电阻引脚定义
LdrSensorLeft = 7
LdrSensorRight = 6


# 电机引脚初始化为输出模式
# 按键引脚初始化为输入模式
# 寻迹引脚初始化为输入模式
def init():
    global pwm_ENA
    global pwm_ENB
    global pwm_FrontServo
    global pwm_UpDownServo
    global pwm_LeftRightServo
    global pwm_Rled
    global pwm_Gled
    global pwm_Bled
    GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(buzzer, GPIO.OUT, initial=GPIO.HIGH)
    GPIO.setup(EchoPin, GPIO.IN)
    GPIO.setup(TrigPin, GPIO.OUT)
    GPIO.setup(LED_R, GPIO.OUT)
    GPIO.setup(LED_G, GPIO.OUT)
    GPIO.setup(LED_B, GPIO.OUT)
    GPIO.setup(FrontServoPin, GPIO.OUT)
    GPIO.setup(ServoUpDownPin, GPIO.OUT)
    GPIO.setup(ServoLeftRightPin, GPIO.OUT)
    GPIO.setup(AvoidSensorLeft, GPIO.IN)
    GPIO.setup(AvoidSensorRight, GPIO.IN)
    GPIO.setup(LdrSensorLeft, GPIO.IN)
    GPIO.setup(LdrSensorRight, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin1, GPIO.IN)
    GPIO.setup(TrackSensorLeftPin2, GPIO.IN)
    GPIO.setup(TrackSensorRightPin1, GPIO.IN)
    GPIO.setup(TrackSensorRightPin2, GPIO.IN)
    # 设置pwm引脚和频率为2000hz
    pwm_ENA = GPIO.PWM(ENA, 2000)
    pwm_ENB = GPIO.PWM(ENB, 2000)
    pwm_ENA.start(0)
    pwm_ENB.start(0)
    # 设置舵机的频率和起始占空比
    pwm_FrontServo = GPIO.PWM(FrontServoPin, 50)
    pwm_UpDownServo = GPIO.PWM(ServoUpDownPin, 50)
    pwm_LeftRightServo = GPIO.PWM(ServoLeftRightPin, 50)
    pwm_FrontServo.start(0)
    pwm_UpDownServo.start(0)
    pwm_LeftRightServo.start(0)
    pwm_Rled = GPIO.PWM(LED_R, 1000)
    pwm_Gled = GPIO.PWM(LED_G, 1000)
    pwm_Bled = GPIO.PWM(LED_B, 1000)
    pwm_Rled.start(0)
    pwm_Gled.start(0)
    pwm_Bled.start(0)


# 超声波测距，如果为1000则未检测到
# 由于实践中存在测距异常的情况（没有障碍，但是会偶然测到障碍），实现中每次测距会测3次，取平均值，其中只要有1次为1000就表示没检测到
def Distance():
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000012)
    GPIO.output(TrigPin, GPIO.LOW)
    t3 = time.time()
    while not GPIO.input(EchoPin):  # 等回音超过3ms，视为无关障碍
        t4 = time.time()
        if (t4 - t3) > 0.003:
            return 1000
    t1 = time.time()
    while GPIO.input(EchoPin):  # 看回音持续了多久，超过3ms视为噪音
        t5 = time.time()
        if (t5 - t1) > 0.003:
            return 1000

    t2 = time.time()
    k1 = ((t2 - t1) * 340 / 2) * 100
    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000012)
    GPIO.output(TrigPin, GPIO.LOW)
    t3 = time.time()
    while not GPIO.input(EchoPin):  # 等回音超过3ms，视为无关障碍
        t4 = time.time()
        if (t4 - t3) > 0.003:
            return 1000
    t1 = time.time()
    while GPIO.input(EchoPin):  # 看回音持续了多久，超过3ms视为噪音
        t5 = time.time()
        if (t5 - t1) > 0.003:
            return 1000

    t2 = time.time()
    k2 = ((t2 - t1) * 340 / 2) * 100

    GPIO.output(TrigPin, GPIO.LOW)
    time.sleep(0.000002)
    GPIO.output(TrigPin, GPIO.HIGH)
    time.sleep(0.000012)
    GPIO.output(TrigPin, GPIO.LOW)
    t3 = time.time()
    while not GPIO.input(EchoPin):  # 等回音超过3ms，视为无关障碍
        t4 = time.time()
        if (t4 - t3) > 0.003:
            return 1000
    t1 = time.time()
    while GPIO.input(EchoPin):  # 看回音持续了多久，超过3ms视为噪音
        t5 = time.time()
        if (t5 - t1) > 0.003:
            return 1000

    t2 = time.time()
    k3 = ((t2 - t1) * 340 / 2) * 100
    return (k1 + k2 + k3) / 3.0


# 舵机旋转到指定角度,占空比为2.5-12.5为0~180度
def set_servo_angle(k):
    pwm_FrontServo.ChangeDutyCycle(2.5 + 10 * k / 180)


def set_camera_updown(k):
    pwm_UpDownServo.ChangeDutyCycle(2.5 + 10 * k / 180)


def set_camera_leftright(k):
    pwm_LeftRightServo.ChangeDutyCycle(2.5 + 10 * k / 180)


# 舵机电压清零，持续保持在某个电平会使得电机持续运转，所以在设置后需要再清零，此时电机不会重置位置而是直接停机，
def stop_servo_angle():
    pwm_FrontServo.ChangeDutyCycle(0)


def stop_camera_updown():
    pwm_UpDownServo.ChangeDutyCycle(0)


def stop_camera_leftright():
    pwm_LeftRightServo.ChangeDutyCycle(0)


# 小车鸣笛
def whistle():
    GPIO.output(buzzer, GPIO.LOW)
    time.sleep(1.5)
    GPIO.output(buzzer, GPIO.HIGH)
    time.sleep(0.001)


# 锁死
def lock():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(2)
    pwm_ENB.ChangeDutyCycle(2)


def lockInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        lock()
        t2 = time.time()
        if (t2 - t1) > timeSet:
            brake()
            return 0


# 小车前进，两驱动轮前进
def run(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)


# 小车前进，两驱动轮前进
def runInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        t2 = time.time()
        run(leftSpeed, rightSpeed)
        if (t2 - t1) > timeSet:
            brake()  # 有问题替换成锁死
            return 0


# 小车左转，右驱动轮前进
def left(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)


# 小车左转
def leftInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        t2 = time.time()
        left(leftSpeed, rightSpeed)
        if (t2 - t1) > timeSet:
            brake()  # 有问题替换成锁死
            return 0


# 小车右转，左驱动轮前进
def right(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)


# 小车右转
def rightInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        t2 = time.time()
        right(leftSpeed, rightSpeed)
        if (t2 - t1) > timeSet:
            brake()  # 有问题替换成锁死
            return 0


# 小车原地左转，左驱动轮后退，右驱动轮前进
def spin_left(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)


# 小车原地左转
def spin_leftInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        t2 = time.time()
        spin_left(leftSpeed, rightSpeed)
        if (t2 - t1) > timeSet:
            brake()  # 有问题替换成锁死
            return 0


# 小车原地右转，左驱动轮前进，右驱动轮后退
def spin_right(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)


# 小车原地右转
def spin_rightInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        t2 = time.time()
        spin_right(leftSpeed, rightSpeed)
        if (t2 - t1) > timeSet:
            brake()  # 有问题替换成锁死
            return 0


# 小车停止
def brake():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)


# 小车后退，两驱动轮前进
def back(leftSpeed, rightSpeed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(leftSpeed)
    pwm_ENB.ChangeDutyCycle(rightSpeed)


# 小车后退
def backInTime(leftSpeed, rightSpeed, timeSet):
    t1 = time.time()
    while True:
        t2 = time.time()
        back(leftSpeed, rightSpeed)
        if (t2 - t1) > timeSet:
            brake()  # 有问题替换成锁死
            return 0


# 小车反方向左转，右驱动轮后退
def back_left(Speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.HIGH)
    pwm_ENA.ChangeDutyCycle(Speed)
    pwm_ENB.ChangeDutyCycle(Speed)


# 小车反方向右转，左驱动轮后退
def back_right(Speed):
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(Speed)
    pwm_ENB.ChangeDutyCycle(Speed)


####################################################################

dir_code = 0  # 小车朝向 0 1 2 3 分别代表↑ → ↓ ←
row_max = 4  # 最大行数
column_max = 4  # 最大列数w
row = 1  # 小车当前所在行
column = 1  # 小车当前所在列
delayTime = 0  # 小车原地转偏移量（时间）
delayTime2 = 0  # 小车倒车转偏移量（时间）


# 向前移动一格 todo
def move_one():
    ImOutput.Out.Println("开始: move_one函数")
    runInTime(10, 10, 0.2)

    lineCount = 0
    lineCountF = False

    run(15, 15)

    while True:
        L1 = 1 if GPIO.input(TrackSensorLeftPin1) else 0
        L2 = 1 if GPIO.input(TrackSensorLeftPin2) else 0
        R2 = 1 if GPIO.input(TrackSensorRightPin1) else 0
        R1 = 1 if GPIO.input(TrackSensorRightPin2) else 0

        # 0000
        # 全黑
        if L1 == 0 and L2 == 0 and R2 == 0 and R1 == 0:
            if lineCountF == False:
                # print("到达第",lineCount,"条线")
                lineCountF = True
                lineCount = lineCount + 1
            if lineCount == 3:
                lockInTime(4, 4, 0.5)
                ImOutput.Out.Println("结束: move_one函数")
                return 2

        # 0111,0011
        # 0 X X X
        # 最左边检测到
        if L1 == 0 and R1 == 1:
            spin_left(15, 15)
            # time.sleep(0.02)

        # 1110,1100
        # X X X 0
        # 最右边检测到
        elif R1 == 0 and L1 == 1:
            spin_right(15, 15)
            # time.sleep(0.02)

        # 1011
        # X 0 1 X
        # 处理左小弯
        elif L2 == 0 and R2 == 1:
            left(0, 15)

        # 1101
        # X 1 0 X
        # 处理右小弯
        elif L2 == 1 and R2 == 0:
            right(15, 0)

        # 1001
        # X 0 0 X-
        # 处理直线
        elif L2 == 0 and R2 == 0:
            run(15, 15)
        # 全1

        if L1 == 1 and R1 == 1:
            lineCountF = False


# 交点处原地左转
def turn_left():
    global delayTime
    global delayTime2

    ImOutput.Out.Println("开始: 原地左转")
    lineCount = 0
    lineCountF = False
    backInTime(20, 20, 0.1 + delayTime2)

    spin_leftInTime(20, 20, 0.7 + delayTime)

    ImOutput.Out.Println("spin左转")

    spin_left(15, 15)

    while True:
        L1 = 1 if GPIO.input(TrackSensorLeftPin1) else 0
        L2 = 1 if GPIO.input(TrackSensorLeftPin2) else 0
        R2 = 1 if GPIO.input(TrackSensorRightPin1) else 0
        R1 = 1 if GPIO.input(TrackSensorRightPin2) else 0

        if L1 == 0 and L2 == 0 and R2 == 0 and R1 == 0:
            ImOutput.Out.Println("全黑,退出巡线模式")
            brake()
            return 2

        # 0010,1010,1000,0110,0100
        # 0 0 1 0
        # 1 0 X 0
        # 0 1 X 0
        # 处理右锐角和右直角的转动
        if (L1 == 0 or L2 == 0) and R1 == 0:
            spin_right(15, 15)
            time.sleep(0.04)

        # 0101,0001
        # 0 1 0 0
        # 0 X 0 1
        # 0 X 1 0
        # 处理左锐角和左直角的转动
        elif L1 == 0 and (R2 == 0 or R1 == 0):
            spin_left(15, 15)
            time.sleep(0.04)

        # 0111,0011
        # 0 X X X
        # 最左边检测到
        elif L1 == 0:
            spin_left(15, 15)
            # time.sleep(0.02)

        # 1110,1100
        # X X X 0
        # 最右边检测到
        elif R1 == 0:
            spin_right(15, 15)
            # time.sleep(0.02)

        # 1011
        # X 0 1 X
        # 处理左小弯
        elif L2 == 0 and R2 == 1:
            left(0, 15)

        # 1101
        # X 1 0 X
        # 处理右小弯
        elif L2 == 1 and R2 == 0:
            right(15, 0)

        # 1001
        # X 0 0 X-
        # 处理直线
        elif L2 == 0 and R2 == 0:
            run(15, 15)


# 交点处原地右转 todo
def turn_right():
    global delayTime
    global delayTime2

    ImOutput.Out.Println("开始: 原地右转")
    lineCount = 0
    lineCountF = False
    backInTime(20, 20, 0.1 + delayTime2)

    spin_rightInTime(20, 20, 0.7 + delayTime)

    ImOutput.Out.Println("spin右转")

    spin_right(15, 15)

    while True:
        L1 = 1 if GPIO.input(TrackSensorLeftPin1) else 0
        L2 = 1 if GPIO.input(TrackSensorLeftPin2) else 0
        R2 = 1 if GPIO.input(TrackSensorRightPin1) else 0
        R1 = 1 if GPIO.input(TrackSensorRightPin2) else 0

        if L1 == 0 and L2 == 0 and R2 == 0 and R1 == 0:
            ImOutput.Out.Println("全黑,退出巡线模式")
            brake()
            return 2

        # 0010,1010,1000,0110,0100
        # 0 0 1 0
        # 1 0 X 0
        # 0 1 X 0
        # 处理右锐角和右直角的转动
        if (L1 == 0 or L2 == 0) and R1 == 0:
            spin_right(15, 15)
            time.sleep(0.04)

        # 0101,0001
        # 0 1 0 0
        # 0 X 0 1
        # 0 X 1 0
        # 处理左锐角和左直角的转动
        elif L1 == 0 and (R2 == 0 or R1 == 0):
            spin_left(15, 15)
            time.sleep(0.04)

        # 0111,0011
        # 0 X X X
        # 最左边检测到
        elif L1 == 0:
            spin_left(15, 15)
            # time.sleep(0.02)

        # 1110,1100
        # X X X 0
        # 最右边检测到
        elif R1 == 0:
            spin_right(15, 15)
            # time.sleep(0.02)

        # 1011
        # X 0 1 X
        # 处理左小弯
        elif L2 == 0 and R2 == 1:
            left(0, 15)

        # 1101
        # X 1 0 X
        # 处理右小弯
        elif L2 == 1 and R2 == 0:
            right(15, 0)

        # 1001
        # X 0 0 X-
        # 处理直线
        elif L2 == 0 and R2 == 0:
            run(15, 15)


# 交点处原地掉头
def turn_back():
    turn_left()
    turn_left()


# 推箱子函数
def push_box():

    lineCount = 0
    lineCountF = False

    run(15, 15)

    while True:
        L1 = 1 if GPIO.input(TrackSensorLeftPin1) else 0
        L2 = 1 if GPIO.input(TrackSensorLeftPin2) else 0
        R2 = 1 if GPIO.input(TrackSensorRightPin1) else 0
        R1 = 1 if GPIO.input(TrackSensorRightPin2) else 0

        # 全黑
        if L1 == 0 and L2 == 0 and R2 == 0 and R1 == 0:
            if lineCountF == False:
                # print("到达第",lineCount,"条线")
                lineCountF = True
                lineCount = lineCount + 1
            if lineCount == 5:
                lockInTime(2, 2, 0.5)
                ImOutput.Out.Println("结束: push部分函数")
                break

        # 0111,0011
        # 0 X X X
        # 最左边检测到
        if L1 == 0 and R1 == 1:
            spin_left(15, 15)
            # time.sleep(0.02)

        # 1110,1100
        # X X X 0
        # 最右边检测到
        elif R1 == 0 and L1 == 1:
            spin_right(15, 15)
            # time.sleep(0.02)

        # 1011
        # X 0 1 X
        # 处理左小弯
        elif L2 == 0 and R2 == 1:
            left(0, 15)

        # 1101
        # X 1 0 X
        # 处理右小弯
        elif L2 == 1 and R2 == 0:
            right(15, 0)

        # 1001
        # X 0 0 X-
        # 处理直线
        elif L2 == 0 and R2 == 0:
            run(15, 15)
        # 全1

        if L1 == 1 and R1 == 1:
            lineCountF = False

    lineCount2 = 0
    lineCountF2 = False

    back(15, 15)

    while True:
        L1 = 1 if GPIO.input(TrackSensorLeftPin1) else 0
        L2 = 1 if GPIO.input(TrackSensorLeftPin2) else 0
        R2 = 1 if GPIO.input(TrackSensorRightPin1) else 0
        R1 = 1 if GPIO.input(TrackSensorRightPin2) else 0

        # 全黑
        if L1 == 0 and L2 == 0 and R2 == 0 and R1 == 0:
            if lineCountF2 == False:
                # print("到达第",lineCount,"条线")
                lineCountF2 = True
                lineCount2 = lineCount2 + 1
            if lineCount2 == 2:
                lockInTime(2, 2, 0.5)
                ImOutput.Out.Println("结束: push函数")
                break

        if L1 == 0 and R1 == 1:
            spin_left(15, 15)
            # time.sleep(0.02)

        # 1110,1100
        # X X X 0
        # 最右边检测到
        elif R1 == 0 and L1 == 1:
            spin_right(15, 15)
            # time.sleep(0.02)

        # 1011
        # X 0 1 X
        # 处理左小弯
        elif L2 == 0 and R2 == 1:
            back_right(15)

        # 1101
        # X 1 0 X
        # 处理右小弯
        elif L2 == 1 and R2 == 0:
            back_left(15)

        # 1001
        # X 0 0 X-
        # 处理直线
        elif L2 == 0 and R2 == 0:
            back(15, 15)

        if L1 == 1 and R1 == 1:
            lineCountF2 = False


# 向某方向移动一格(用于初期扫描地图)
# 返回值为0则代表该操作会使小车越界,于是直接退出函数
# 返回值为-1则小车朝向目标方向后,前方出现了障碍物,未移动成功
# 返回值为1代表移动成功
def moveto(dir: int):
    print("开始：moveto函数 dir:", dir)
    global dir_code
    global row
    global column

    # 检测是否会越界,会则直接退出函数
    if dir == 0 and row == 0:
        ImOutput.Out.Println("目标位置越界")
        print("结束：moveto函数 dir:", dir)
        return 0
    if dir == 1 and column == column_max:
        ImOutput.Out.Println("目标位置越界")
        print("结束：moveto函数 dir:", dir)
        return 0
    if dir == 2 and row == row_max:
        ImOutput.Out.Println("目标位置越界")
        print("结束：moveto函数 dir:", dir)
        return 0
    if dir == 3 and column == 0:
        ImOutput.Out.Println("目标位置越界")
        print("结束：moveto函数 dir:", dir)
        return 0

    # 若小车当前朝向与目标方向不同
    if dir_code != dir:
        # 应该原地右转
        if (dir - dir_code == 1) or (dir - dir_code == -3):
            turn_right()
        # 应该原地左转
        elif (dir - dir_code == -1) or (dir - dir_code == 3):
            turn_left()
        # 应该原地掉头
        else:
            turn_back()
        # 小车朝向已面向目标方向
        dir_code = dir

    # 开始超声波检测前方是否有障碍物
    dist = Distance()
    # 有障碍物(35cm内),返回-1
    if dist <= 40:
        # if False:
        ImOutput.Out.Println("发现障碍物，不能前进")
        print("Row:", row, " Col:", column, " Dir:", dir_code)
        print("结束：moveto函数 dir:", dir)
        return -1

    # 没有障碍物,开始移动一格
    else:
        # 向前移动一格
        move_one()
        # 小车当前位置已改变
        if dir == 0:
            row -= 1
        if dir == 1:
            column += 1
        if dir == 2:
            row += 1
        if dir == 3:
            column -= 1
        ImOutput.Out.Println("向目标方向移动完成")
        print("Row:", row, " Col:", column, " Dir:", dir_code)
        print("结束：moveto函数 dir:", dir)
        return 1


# 检测是障碍物还是箱子 todo
def isBox():
    pass


# 初始化一个二维数组存储探索结果，初始值为'X'表示未知。
def initialize_map(row_max, column_max):
    return [["X" for _ in range(column_max)] for _ in range(row_max)]


# 判断给定的坐标是否在地图范围内
def is_valid_position(r, c):
    global row_max, column_max
    return 0 <= r < row_max and 0 <= c < column_max


# 地图遍历函数，使用BFS算法来遍历整个地图。
def bfs_explore_map():
    global row, column, dir_code, row_max, column_max

    # 初始化地图
    map_grid = initialize_map(row_max, column_max)
    directions = [(-1, 0), (0, 1), (1, 0), (0, -1)]  # 上右下左 对应的行列变化

    map_grid[row][column] = "L"  # 当前位置标记为空地

    def bfs(current_row, current_column, current_dir):
        for i in range(4):
            # 计算新的方向和位置
            new_dir = (current_dir + i) % 4
            dr, dc = directions[new_dir]
            new_row, new_column = current_row + dr, current_column + dc
            if not is_valid_position(new_row, new_column):
                continue
            if map_grid[new_row][new_column] == "X":  # 未探索
                result = moveto(new_dir)
                if result == 1:
                    # 移动成功，标记为空地
                    map_grid[new_row][new_column] = "L"
                    bfs(new_row, new_column, new_dir)

                    # 移回原位置
                    back_dir = (new_dir + 2) % 4
                    moveto(back_dir)
                elif result == -1:
                    dic = {CameraService.ObjectType.barrier: "O", CameraService.ObjectType.box: "B"}
                    ImOutput.Out.Println("前有阻挡")
                    # ImOutput.Out.Println("otto: 卧槽！冰！")
                    while CameraService.ArucoModule.frontObject is CameraService.ObjectType.null:
                        ImOutput.Out.Println("等待识别")
                        # ImOutput.Out.Println(CameraService.ArucoModule.frontObject)
                        time.sleep(0.2)
                    # 碰到障碍物，标记为障碍物
                    ######## 注意这里应该调用opencv函数判断是箱子还是障碍物
                    # 这里先全都当作障碍物
                    map_grid[new_row][new_column] = dic[CameraService.ArucoModule.frontObject]

    bfs(row, column, dir_code)
    return map_grid


def MoveAsPath(callback=None):
    for item in path:
        ImOutput.Out.Println("otto: 冲刺！冲刺！")
        if item > 3:
            ImOutput.Out.Println("otto: 冲！")
            moveto(item % 4)
            push_box()
        else:
            moveto(item % 4)
        if callback is not None:
            callback()
    ImOutput.Out.Println("otto: 哇哦！")


##################################################################################
# 入口函数
if __name__ == "__main__":
    init()
    # turn_left()
    inputt = input("请输入小车原地转偏移量（时间）:")
    delayTime = float(inputt)

    inputtt = input("请输入小车倒车转偏移量（时间）:")
    delayTime2 = float(inputtt)

    input1 = input("输入小车起始朝向: ")
    dir_code = int(input1)

    input2 = input("输入小车所在行: ")
    row = int(input2)

    input3 = input("输入小车所在列: ")
    column = int(input3)

    endY = int(input("输入终点行: "))
    endX = int(input("输入终点列: "))
    CameraService.Service.Start()
    # 调用探索函数，获取地图
    explored_map = bfs_explore_map()
    Sokoban.LoadFromMatrix(explored_map)

    Sokoban.SetStart(column, row)
    Sokoban.SetEnd(endX, endY)

    ans = Sokoban.SokobanSolve()

    path = Sokoban.Prase(ans)

    MoveAsPath()
