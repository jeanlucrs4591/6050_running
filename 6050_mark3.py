# -*- coding: utf-8 -*-
#!/usr/bin/python

# import module
import csv
import smbus
import math
from time import sleep
from datetime import datetime

# slave_add
DEV_ADDR = 0x68
# register_add
ACCEL_XOUT = 0x3b
ACCEL_YOUT = 0x3d
ACCEL_ZOUT = 0x3f
TEMP_OUT = 0x41
GYRO_XOUT = 0x43
GYRO_YOUT = 0x45
GYRO_ZOUT = 0x47
PWR_MGMT_1 = 0x6b
PWR_MGMT_2 = 0x6c
AFS_SEL_ADD = 0x1c
AFS_SEL_SET = 0x10 # 0x18:16g, 0x10:8g, 0x08 4g, 0x00 2g
ACCEL_DIV = 4096.0 # 16g:2048.0, 8g:4096.0, 4g:8192.0, 2g:16384.0

bus = smbus.SMBus(1)
# Unlock Sleep
bus.write_byte_data(DEV_ADDR, PWR_MGMT_1, 0)

def read_byte(adr):
    return bus.read_byte_data(DEV_ADDR, adr)

def write_byte(adr, param):
    bus.write_byte_data(DEV_ADDR, adr, param)

def read_word(adr):
    high = bus.read_byte_data(DEV_ADDR, adr)
    low = bus.read_byte_data(DEV_ADDR, adr+1)
    val = (high << 8) + low
    return val

def read_word_sensor(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def get_temp():
    temp = read_word_sensor(TEMP_OUT)
    x = temp / 340 + 36.53
    return x

def get_gyro_data_lsb():
    x = read_word_sensor(GYRO_XOUT)
    y = read_word_sensor(GYRO_YOUT)
    z = read_word_sensor(GYRO_ZOUT)
    return [x, y, z]

def get_gyro_data_deg():
    x,y,z = get_gyro_data_lsb()
    x = x / 131.0
    y = y / 131.0
    z = z / 131.0
    return [x, y, z]

def get_accel_data_lsb():
    x = read_word_sensor(ACCEL_XOUT)
    y = read_word_sensor(ACCEL_YOUT)
    z = read_word_sensor(ACCEL_ZOUT)
    return [x, y, z]

def get_accel_data_g():
    x,y,z = get_accel_data_lsb()
    x = x / ACCEL_DIV
    y = y / ACCEL_DIV
    z = z / ACCEL_DIV
    return [x, y, z]

# Main function
write_byte(AFS_SEL_ADD, AFS_SEL_SET)
sleep(1)
state = False
count = 0
print 'ready'
while 1:

    d = datetime.now()
    accel_x,accel_y,accel_z = get_accel_data_g()

    #print 'acl[g]',
    #print 'x: %06.3f' % accel_x,
    #print 'y: %06.3f' % accel_y,
    #print 'z: %06.3f' % accel_z,
    #print

    if abs(accel_x) > 2 or abs(accel_y) > 2 or abs(accel_z) > 2:
        count = 0
        if state == False:
            filename = '/home/pi/Desktop/{0:04}{1:02}{2:02}{3:02}{4:02}{5:02}.csv'.format(d.year, d.month, d.day, d.hour, d.minute, d.second)
            state = True
            print 'start'

    if state:
        datetext = '{0}:{1:02}:{2:02}.{3:06}'.format(d.hour, d.minute, d.second, d.microsecond)
        with open(filename, 'a') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([datetext, '%06.3f' % accel_x, '%06.3f' % accel_y, '%06.3f' % accel_z])
        f.close()

    if count > 2000:
        state = False
        print 'stop'

    count+=1

    sleep(0.022)
