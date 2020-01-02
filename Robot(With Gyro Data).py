#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import math
import smbus

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)
GPIO.setup(5, GPIO.OUT)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

a = GPIO.PWM(26, 1000)
b = GPIO.PWM(12, 1000)

power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def dist(a,b):
    return math.sqrt((a*a)+(b*b))

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

bus = smbus.SMBus(1) # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68       # This is the address value read via the i2cdetect command

# Now wake the 6050 up as it starts in sleep mode
bus.write_byte_data(address, power_mgmt_1, 0)

while True:
    try:
        #GPIO.output(5, True)
        #GPIO.output(6, False)
        #GPIO.output(13, True)
        #GPIO.output(19, False)

        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)

        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

    #    print("accel_xout: ", accel_xout, " scaled: ", accel_xout_scaled)
    #    print("accel_yout: ", accel_yout, " scaled: ", accel_yout_scaled)
    #    print("accel_zout: ", accel_zout, " scaled: ", accel_zout_scaled)

        #print("x rotation: " , get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled))
        y = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        print("y rotation: " , y)

        a.start(0)
        b.start(0)

        if y < 0:
            GPIO.output(5, True)
            GPIO.output(6, False)
            GPIO.output(13, True)
            GPIO.output(19, False)
            y = 0 - y

            if ((y/90)*300) > 100:
                a.ChangeDutyCycle(100)
                b.ChangeDutyCycle(100)

            else:
                a.ChangeDutyCycle((y/90)*300)
                b.ChangeDutyCycle((y/90)*300)

        else:
            GPIO.output(5, False)
            GPIO.output(6, True)
            GPIO.output(13, False)
            GPIO.output(19, True)
            #y = 0 - y
            if ((y/90)*300) > 100:
                a.ChangeDutyCycle(100)
                b.ChangeDutyCycle(100)

            else:
                a.ChangeDutyCycle((y/90)*300)
                b.ChangeDutyCycle((y/90)*300)


        #time.sleep(1)

        #    print("gyro data")
        #    print("---------")

        #    gyro_xout = read_word_2c(0x43)
        #    gyro_yout = read_word_2c(0x45)
        #    gyro_zout = read_word_2c(0x47)

        #    print("gyro_xout: ", gyro_xout, " scaled: ", (gyro_xout / 131))
        #    print("gyro_yout: ", gyro_yout, " scaled: ", (gyro_yout / 131))
        #    print("gyro_zout: ", gyro_zout, " scaled: ", (gyro_zout / 131))

        #    print('')
        #    print("accelerometer data")
        #    print("------------------")
        #


    except Exception as e:
        if str(e)[1] == 'K':
            break
        else: pass

a.stop()
b.stop()
