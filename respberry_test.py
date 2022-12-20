#!/usr/bin/python
# -*- coding:utf-8 -*-
import smbus
import time
import serial

#address AD/DA converter
i2cAdda     =   0x48           # I2C-Adresse des Wandlers
adda_ain3   =   0x03        # Sensoren
adda_ain0   =   0x00
addaOut     =   0x40

def send(signalname,unit,count,value):
    ser.write((signalname + "_" + unit +"_"+ str(count) +"_"+ value +"\n").encode())
    print(signalname + "_" + unit +"_"+ str(count) +"_"+ value)
    
if __name__ == '__main__':
    ser = serial.Serial('/dev/ttyS0', baudrate=56000,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS
                    )
    print("serial communication established")
    i2c = smbus.SMBus(1)
    print("i2c communication established")
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