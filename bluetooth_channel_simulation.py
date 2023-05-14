#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2023 Bo Lei 
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.0 of the License, or (at your option) any later version.
#



from enum import Enum
from enum import unique

@unique
class Mode(Enum):
    PAGE_SCAN = 0
    PAGE_INTERLACED_SCAN = 1
    INQUIRY_SCAN = 2
    INQUIRY_INTERLACED_SCAN = 3
    PAGE = 4
    INQUIRY = 6
    SLAVE_RESPONSE = 7
    MASTER_RESPONSE = 8
    INQUIRY_RESPONSE = 9
    CONNECTION = 10

@unique
class TRAIN(Enum): #BLUETOOTH CORE SPECIFICATION Version 5.2 | Vol 2, Part B 2.6.4.2
    B = 8
    A = 24



class channel_table():
    table = []

    def __init__(self):
        for element in range(0, 80, 2):
            self.table.append(element)
        for element in range(1, 79, 2):
            self.table.append(element)


g_channel_table_1 = channel_table()

def add_5 (x,a):
    return (x+a) % 32

def xor_5 (z,b):
    #clear data 
    z_l = z & 0xF
    b = b & 0xF
    z_n = z_l ^ b;
    z_n = z_n + (z & 0x10)
    return z_n

'''
    
    if b & 0x8 == 0x8:
       z_n = z_n | 0x8
    else:
       z_n = z_n & (~0x8)
'''


def xor_5_3(c, y1):
    c0 = c & 0x1
    c1 = (c & 0x2) >> 1
    c2 = (c & 0x4) >> 2
    c3 = (c & 0x8) >> 3
    c4 = (c & 0x10) >> 4

    c0 = c0 ^ y1
    c1 = c1 ^ y1
    c2 = c2 ^ y1
    c3 = c3 ^ y1
    c4 = c4 ^ y1

    cn = (c4 << 4) + \
         (c3 << 3) + \
         (c2 << 2) + \
         (c1 << 1) + \
         c0

    return cn

def butterfly(a,b,p):
    a_n = b if p else a
    b_n = a if p else b
    return a_n, b_n

def permutation(z,c,d):
    p0 = d & 0x1
    p1 = (d & 0x2) >> 1
    p2 = (d & 0x4) >> 2
    p3 = (d & 0x8) >> 3
    p4 = (d & 0x10) >> 4
    p5 = (d & 0x20) >> 5
    p6 = (d & 0x40) >> 6
    p7 = (d & 0x80) >> 7
    p8 = (d & 0x100) >> 8
    p9 = c & 0x1
    p10 = (c & 0x2) >> 1
    p11 = (c & 0x4) >> 2
    p12 = (c & 0x8) >> 3
    p13 = (c & 0x10) >> 4

    z0_0 = z & 0x1
    z0_1 = (z & 0x2) >> 1
    z0_2 = (z & 0x4) >> 2
    z0_3 = (z & 0x8) >> 3
    z0_4 = (z & 0x10) >> 4

    #stage 1
    z1_0, z1_3 = butterfly(z0_0, z0_3, p12)
    z1_1, z1_2 = butterfly(z0_1, z0_2, p13)
    z1_4 = z0_4

    #stage 2
    z2_1, z2_3 = butterfly(z1_1, z1_3, p11) 
    z2_2, z2_4 = butterfly(z1_2, z1_4, p10)
    z2_0 = z1_0
    
    #stage 3
    z3_0, z3_3 = butterfly(z2_0, z2_3, p9) 
    z3_1, z3_4 = butterfly(z2_1, z2_4, p8) 
    z3_2 = z2_2

    #stage 4
    z4_0, z4_2 = butterfly(z3_0, z3_2, p6)
    z4_3, z4_4 = butterfly(z3_3, z3_4, p7)
    z4_1 = z3_1

    #stage 5
    z5_0, z5_4 = butterfly(z4_0, z4_4, p4)
    z5_1, z5_3 = butterfly(z4_1, z4_3, p5)
    z5_2 = z4_2

    #stage 6
    z6_1, z6_2 = butterfly(z5_1, z5_2, p2)
    z6_3, z6_4 = butterfly(z5_3, z5_4, p3)
    z6_0 = z5_0

    #stage 7
    z7_0, z7_1 = butterfly(z6_0, z6_1, p0)
    z7_2, z7_3 = butterfly(z6_2, z6_3, p1)
    z7_4 = z6_4
    
    z7 = (z7_4 << 4) +\
         (z7_3 << 3) +\
         (z7_2 << 2) +\
         (z7_1 << 1) +\
         z7_0
    return z7

def add_7(z,e,f,y2):
    zn = (z + e + f + y2)
    return zn

def hop_kernel(a,b,c,d,e,f,x,y1,y2):

    z0 = add_5(x,a)  
    z1 = xor_5(z0,b)
    c1 = xor_5_3(c, y1)
    # c1 = 0x0
    z2 =  permutation(z1,c1,d)
    z3 =  add_7(z2,e,f,y2)
    #print(z3)#

    global g_channel_table_1
    #print('%02d' % g_channel_table_1.table[z3 % 79], end=' ')
    return g_channel_table_1.table[z3 % 79]





#LSB                                                      MSB|
#|-------------LAP-------------|---UAP---|--------NAP--------| 
#|0000|0000|0000|0000|0000|0000|0000|0000|0000|0000|0000|0000|
#
#A23-0 LAP of device
#A27-24 UAP of device
def control_word(bt_addr, clock, mode, koffset, knudge, N):
    
    if mode == 'i':
       bt_addr = 0x9e8b33



    a = (bt_addr & 0xf800000) >> 23
    b = (bt_addr & 0x780000) >> 19
    c = ((bt_addr & 0x100) >> 4) +\
      ((bt_addr & 0x40) >> 3) +\
      ((bt_addr & 0x10) >> 2) +\
      ((bt_addr & 0x4) >> 1) +\
      (bt_addr & 0x1) 

    d = (bt_addr & 0x7fe00) >> 10
    e = ((bt_addr & 0x2000) >> 7) +\
     ((bt_addr & 0x800) >> 6) +\
     ((bt_addr & 0x200) >> 5) +\
     ((bt_addr & 0x80) >> 4) +\
     ((bt_addr & 0x20) >> 3) +\
     ((bt_addr & 0x8) >> 2) +\
     ((bt_addr & 0x2) >> 1)
    f = 0
  
    clock_4_2_0 = ((clock & 0x1c) >> 1) +\
                (clock & 0x1)

    clock_16_12 = (clock & 0x1f000) >> 12

    # page
    temp = ((clock_4_2_0 - clock_16_12 + 32) % 16)

    x_page_scan = clock_16_12
    x_page_interlaced_scan = (clock_16_12 + 16) % 32
    xir = (clock_16_12 + N) % 32
    xir_interlaced = (xir + 16) % 32

    xp =  (clock_16_12 + koffset + knudge + ((clock_4_2_0 - clock_16_12 + 32) % 16)) % 32
    # Inquiry
    xi =  (clock_16_12 + koffset + knudge + ((clock_4_2_0 - clock_16_12) % 16)) % 32
    #Master page response
    xprm = (clock_16_12 + koffset + knudge + (((clock_4_2_0 - clock_16_12) % 16) + N)) % 32
    #Slave page response
    xprs = (clock_16_12 + N) % 32 
    #Inquiry response


    y1 = (clock & 0x2) >> 1
    y2 = ((clock & 0x2) >> 1) * 32

    #print("0x%x, 0x%x, 0x%x, 0x%x, 0x%x, 0x%x" % a, b, c, d, e, f)

    return a,b,c,d,e,f,x_page_scan,x_page_interlaced_scan,xir_interlaced,xp,xi,xprm,xprs,xir,y1,y2


#
def get_bluetooth_channel(bt_addr, mode, start_clock, end_clock):
    # input bt_addr string link: AA:BB:CC:DD:EE:FF
    bt_addr_list = bt_addr.split(':')
    bt_addr_num = []
    bt_channel_list = []
    for element in bt_addr_list:
        element = int(element,16)
        bt_addr_num.append(element)
    ulap =  ((bt_addr_num[2] & 0xf) << 24) +\
            (bt_addr_num[3] << 16) +\
            (bt_addr_num[4] << 8) +\
            bt_addr_num[5]
    #print(bt_addr_num, bt_addr_num)

    #print('\n\nulap is 0x%08x mode is' % ulap, end=' ')
    #print(mode, end=' ')

    #print('\n0x%08x: ' % clock, end='')
    for test_clock in range(start_clock, end_clock):
        #if (test_clock - start_clock) % 16 == 0:
            # print('\n0x%08x: ' % test_clock, end='')
        a, b, c, d, e, f, x_page_scan, x_page_interlaced_scan, xir_interlaced, xp, xi, xprm, xprs, xir, y1 ,y2 =\
            control_word(ulap, test_clock, mode, TRAIN.B.value, 0, 0)

        if mode == Mode.PAGE_SCAN:
            x = x_page_scan
            y1 = 0
            y2 = 0
            f = 0
        if mode == Mode.PAGE_INTERLACED_SCAN:
            x = x_page_interlaced_scan
            y1 = 0
            y2 = 0
            f = 0
        if mode == Mode.INQUIRY_SCAN:
            x = xir
            y1 = 0
            y2 = 0
            f = 0
        if mode == Mode.INQUIRY_INTERLACED_SCAN:
            x = x_page_interlaced_scan
            y1 = 0
            y2 = 0
            f = 0
        if mode == Mode.PAGE:
            x = xp
        if mode == Mode.INQUIRY:
            x = xi
        if mode == Mode.MASTER_RESPONSE:
            x = xprm
        if mode == Mode.SLAVE_RESPONSE:
            x = xprs
        if mode == Mode.INQUIRY_RESPONSE:
            x = xir
            y1 = 1
            y2 = 32

        bt_channel = hop_kernel(a, b, c, d, e, f, x, y1, y2)
        bt_channel_list.append(bt_channel)
        print('%02d' % bt_channel, end=' ')
        '''
        #kernel_sub_module_test(xp, a, b, c, d, e, f, y1, y2)
        if mode == Mode.PAGE:
            bt_channel = hop_kernel(a,b,c,d,e,f,xp,y1,y2)
            print('%02d' % bt_channel, end=' ')
        if mode == Mode.INQUIRY:
            bt_channel = hop_kernel(a,b,c,d,e,f,xi,y1,y2)
            print('%02d' % bt_channel, end=' ')
        if mode == Mode.PAGE_SCAN:
            bt_channel = hop_kernel(a,b,c,d,e,0,x_page_scan,0,0)
            print('%02d' % bt_channel, end=' ')
        if mode == Mode.INQUIRY_SCAN:
            bt_channel = hop_kernel(a,b,c,d,e,0,xir,0,0)
            print('%02d' % bt_channel, end=' ')
        #break
        '''
    return bt_channel_list








def test():
    global g_channel_table_1



    #get_bluetooth_channel("05:76:86:74:af:00", 0x4, 0x1)

    #g_channel_table_1 = channel_table()
    #spec test data first set
    #get_bluetooth_channel("11:22:00:00:00:00", 0xff0, Mode.INQUIRY_SCAN)
    #get_bluetooth_channel("11:22:00:00:00:00", 0x0, Mode.PAGE)
    #get_bluetooth_channel("11:22:00:00:00:00", 0x0, Mode.INQUIRY)
    #get_bluetooth_channel("11:22:00:00:00:00", 0x1fc0, Mode.PAGE_SCAN)
    #get_bluetooth_channel("11:22:00:00:00:00", 0x1fc0, Mode.INQUIRY_SCAN)
    get_bluetooth_channel("11:22:00:00:00:00", 0x12, Mode.MASTER_RESPONSE)
    get_bluetooth_channel("11:22:00:00:00:00", 0x14, Mode.SLAVE_RESPONSE)
    get_bluetooth_channel("11:22:00:00:00:00", 0x14, Mode.INQUIRY_RESPONSE)


    #get_bluetooth_channel("11:22:00:00:00:00", 0x0, Mode.PAGE)
    #spec test data second set
    #get_bluetooth_channel("11:22:2a:96:ef:25",0x0,Mode.PAGE)
    #spec test data third set
    #get_bluetooth_channel("11:22:65:87:cb:a9",0x0,Mode.PAGE)



def kernel_sub_module_test(x,a,b,c,d,e,f,y1,y2):
    ''' test searial 1
        x = 0x1a
        a = 0xc
        b = 0xe
        c = 0x10
        y1 = 0
        d = 0x12b
        e = 0x70
        f = 0
        y2 = 0
        '''
    '''
    # test searial 2
    x = 0x1b
    a = 0xc
    b = 0xe
    c = 0x10
    y1 = 0
    d = 0x12b
    e = 0x70
    f = 0
    y2 = 0
    '''
    '''
    x = 0x1a
    a = 0xc
    b = 0xe
    c = 0x10
    y1 = 1
    d = 0x12b
    e = 0x70
    f = 0
    y2 = 0x20
    '''
    '''
    x = 0x1b
    a = 0xc
    b = 0xe
    c = 0x10
    y1 = 1
    d = 0x12b
    e = 0x70
    f = 0
    y2 = 0x20
    '''

    ret1 = add_5(x, a)
    ret2 = xor_5(ret1, b)
    ret3 = xor_5_3(c, y1)
    ret4 = permutation(ret2, ret3, d)
    ret5 = add_7(ret4, e, f, y2) % 79

    print('\n--x-- -a- -b- -c- -y1- -d- -e- -f- -y2-')
    print(' %x    %x   %x   %x  %x  %x  %x   %x   %x' % (x, a, b, c, y1, d, e, f, y2))
    print(' |--%x--|      |--%x--|' % (ret1, ret3))
    print(' |----%x----|' % ret2)
    print(' |-----------%x----------|' % ret4)
    print(' |------------------%x----------------|' % ret5)
    #print('hop kernel internal out:')



