# -*- coding: utf-8 -*-
from time import sleep
import RPi.GPIO as IO          #calling header file which helps us use GPIO’s of PI
import time                            #calling time to provide delays in program
import smbus
import string
import array
import time
import numpy as np

#converts 16 bit two's compliment reading to signed int
def getSignedNumber(number): #for gyro
    if number & (1 << 15):
        return number | ~65535
    else:
        return number & 65535

def chkAndCtrl():
    global start_time
    global recOmegaI
    #Variable Initialization
    global countS
    #recOmegaI = [None] *10
    global omegaI
    global thetaI
    global sumPower
    global sumsumP
    global kAngle
    global kOmega
    global kSpeed
    global kDistance
    global vE5
    global xE5
    global power
    factor = .061 #convert deg per sec 2000 deg / sec
    N = 10
    R=0
    noiseBand = 2
    loopTime = .02
    zeroErrorOmega = 0.19 #0.216 for N =3 # 0.184 for N = 10  # signed number to be calibrated -.55
    resetN = 9
    for x in range(0,N):
        i2c_bus.write_byte(i2c_address,0x43)
        X_L = i2c_bus.read_byte(i2c_address)
        i2c_bus.write_byte(i2c_address,0x44)
        X_H = i2c_bus.read_byte(i2c_address)
        X = X_H << 8 | X_L

        i2c_bus.write_byte(i2c_address,0x45)
        Y_L = i2c_bus.read_byte(i2c_address)
        i2c_bus.write_byte(i2c_address,0x46)
        Y_H = i2c_bus.read_byte(i2c_address)
        Y = Y_H << 8 | Y_L

        i2c_bus.write_byte(i2c_address,0x47)
        Z_L = i2c_bus.read_byte(i2c_address)
        i2c_bus.write_byte(i2c_address,0x48)
        Z_H = i2c_bus.read_byte(i2c_address)
        Z = Z_H << 8 | Z_L

        X = getSignedNumber(X)/131
        Y = getSignedNumber(Y)/131
        #print('change in y is',X)
        #time.sleep(0.1)
        Z = getSignedNumber(Z)/131
        print("gyro_data",int(X),int(Y),int(Z))
        #ry = Y
        #R = R+ry
        rx = X
        R= R+rx

    omegaI = R * factor/ N + zeroErrorOmega
    #print(omegaI)
    if abs(omegaI) < noiseBand:
        #print("im still")
        omegaI = 0
    #print(omegaI)
    recOmegaI[0] = omegaI
    #print(time.time())
    thetaI = thetaI + omegaI*loopTime
    #print(time.time())
    #print(thetaI)
    countS = 0

    # to prevent control action from single event or disturbance
    for i in range(0,resetN+1):
        if abs(recOmegaI[i])<2:
            countS = countS + 1

    # When the inverted pendulum stops falling at the end
    # or just start falling the condition below will execute
    if countS>resetN:
        thetaI = 0
        #print("im in reset")
        vE5 = 0
        xE5 = 0
        sumPower = 0
        sumsumP = 0

    for ii in range(resetN,0,-1):
        recOmegaI[ii] = recOmegaI[ii-1]

    # control algorithm here
    #print('angle:'+str(kAngle * thetaI / 100))
    #print('omega:'+str(kOmega * omegaI / 100))

    powerScale = (kAngle * thetaI ) + (kOmega * omegaI ) + (kSpeed * vE5) + (kDistance * xE5)
    power = max (min (95 * powerScale /100 , 100), -100)
    #print(powerScale,"    ",power)
    #print('power',power)
    sumPower = sumPower + power
    sumsumP = sumsumP + sumPower
    #vE5 = sumPower
    #xE5 = sumsumP/1000

recOmegaI = array.array('f',(0.0 for i in range(0,30)))
#Variable Initialization
countS = 0
#recOmegaI = [None] *10
omegaI = 0
thetaI = 0
sumPower = 0
sumsumP = 0
kAngle = 25 #250
kOmega = 5
kSpeed = 0 #60
kDistance = 0 #20
vE5 = 0
xE5 = 0
power = 0

#open /dev/i2c-1
i2c_bus=smbus.SMBus(1)
#i2c slave address of the L3G4200D
i2c_address=0x68

#initialise the L3G4200D

#normal mode and all axes on to control reg1
#i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
#full 2000dps to control reg4
i2c_bus.write_byte_data(i2c_address, 0x6B, 0)

IO.setwarnings(False)           #do not show any warnings
IO.setmode (IO.BCM)         #we are programming the GPIO by BCM pin numbers. (PIN35 as ‘GPIO19’)
IO.setup(19,IO.OUT)           # initialize GPIO19 as an output.

IO.setup(13,IO.OUT)

p = IO.PWM(19,50)          #GPIO19 as PWM output, with 100Hz frequency
p1 = IO.PWM(13,50)
p.start(0)                              #generate PWM signal with 0% duty cycle
p1.start(0)

IO.setup(16,IO.OUT)
IO.setup(26,IO.OUT)
IO.setup(20,IO.OUT)
IO.setup(21,IO.OUT)

#sleep for 100m second
start_time  = time.time()
while True:
    chkAndCtrl()
##  time.sleep(3)
   # p.stop()
   # p1.stop()

    '''if power < 30 and power > 0:
    	power=30
    elif power > -30 and power < 0:
    	power=-30'''



    #print(str(power)+' power  '+str(thetaI))
    p.ChangeDutyCycle(abs(power))
    p1.ChangeDutyCycle(abs(power))
    if power>0:
        # clockwise rotation - viewed from breadboard side gyro sensor
        #   front taken as breadboard side
        # right motor
        IO.output(16,0) #motor 1 left
        IO.output(26,1)

        #   left motor
        IO.output(21,0)
        IO.output(20,1) #motor 2 left

    else:
    	# anti clockwise rotation - viewed from breadboard side gyro sensor
        #   right motor
        IO.output(16,1) #motor 1 right
        IO.output(26,0)

        #   left motor
        IO.output(21,1)
        IO.output(20,0) #motor 2 left







robo_2.py
Displaying robo_2.py.
