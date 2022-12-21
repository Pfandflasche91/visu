#!/usr/bin/python
# -*- coding:utf-8 -*-
import smbus
import time
import serial
import RPi.GPIO as GPIO

#address AD/DA converter
i2cAdda     =   0x48           # I2C-Adresse des Wandlers
adda_ain3   =   0x03        # Sensoren
adda_ain0   =   0x00
addaOut     =   0x40

#set GPIO numbering mode


def initmotor(pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(pin,GPIO.OUT)
    servo = GPIO.PWM(pin,50)
    servo.start(0)
    print("init motor")
    return servo

def deinitmotor(servo):
    servo.stop()
    GPIO.cleanup()  
    print("deinit motor")

def setmotorangle(servo,angle):
    servo.ChangeDutyCycle(angle)
    time.sleep(0.3)
    servo.ChangeDutyCycle(0)
    time.sleep(0.7)
    print("motorangle set to:" + str(angle) + " = " +str((angle-2)*18))

def send(signalname,unit,count,value):
    ser.write((signalname + "_" + unit +"_"+ str(count) +"_"+ value +"\n").encode())
    print("SEND: Signalname: " + signalname + " | SignalUnit: " + unit + " | SignalCount: "+ str(count) +"| SignalValue: "+ value)

def read():
    if ser.inWaiting() > 0:
        message = ser.read_until()
        signalName=str(message)[2:7]
        signalUnit=str(message)[8:14]
        signalCount=str(message)[15:16]
        signalValue=str(message)[17:20]
        print("READ: Signalname: " +signalName+" | SignalUnit: "+signalUnit+ " | SignalCount: "+signalCount+ " | SignalValue: "+signalValue)
        
        if int(signalValue)>180:
            signalValue = "180" 
        elif int(signalValue) < 0:
            signalValue = "0"
            
        for i in range(11):
            if int(signalValue) >= i*18 and int(signalValue) < (i+1)*18 :
                angle = i+2
                break
        setmotorangle(servo,angle)
        
    
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', baudrate=56000,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                    )
    print("serial communication established")
    i2c = smbus.SMBus(1)
    print("i2c communication established")

    servo = initmotor(11)

    count = 20
    bufferone = ""
    buffertwo = ""
    while True:
        bufferone = ""
        buffertwo = ""
        for i in range(count):
            ain_3 = i2c.read_byte_data(i2cAdda,adda_ain3)
            ain_0 = i2c.read_byte_data(i2cAdda,adda_ain0)
            ain_3_V = ain_3/255 * 3.3
            ain_0_V = ain_0/255 * 3.3
            bufferone = bufferone+"{:.3f}".format(ain_0_V)
            buffertwo = buffertwo+"{:.3f}".format(ain_3_V)
            time.sleep(0.05)
        
        send("ain_3","V",count,buffertwo)
        send("ain_0","V",count,bufferone)
        read()