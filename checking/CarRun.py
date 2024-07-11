import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

IN1 = 20
IN2 = 21
IN3 = 19
IN4 = 26
ENA = 16
ENB = 13

GPIO.setup(ENA, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(IN1, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN2, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(ENB, GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(IN3, GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(IN4, GPIO.OUT, initial=GPIO.LOW)


pwm_ENA = GPIO.PWM(ENA, 2000)
pwm_ENB = GPIO.PWM(ENB, 2000)

pwm_ENA.start(0)
pwm_ENB.start(0)

CarSpeedControl = 80

def run():
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.HIGH)
    GPIO.output(IN4, GPIO.LOW)
    pwm_ENA.ChangeDutyCycle(CarSpeedControl)
    pwm_ENB.ChangeDutyCycle(CarSpeedControl)


def brake():
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.LOW)
    GPIO.output(IN3, GPIO.LOW)
    GPIO.output(IN4, GPIO.LOW)


if __name__ == "__main__":
    run()
    time.sleep(5)
    brake()
