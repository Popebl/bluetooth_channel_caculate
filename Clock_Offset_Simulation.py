#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021-2023 Bo Lei 
#
# This is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation; either
# version 2.0 of the License, or (at your option) any later version.
#

from bokeh.layouts import gridplot
from bokeh.plotting import figure,show


from bluetooth_channel_simulation import Mode, get_bluetooth_channel
page_channel_list = []
page_scan_channel_list = []



def page_gengerate(bt_address, start_clock, end_clock):
    global page_channel_list
    page_channel_list = get_bluetooth_channel(bt_address, Mode.PAGE, start_clock, end_clock)



def page_scan_generate(bt_address, start_clock, end_clock):
    global page_scan_channel_list
    for clock in range(start_clock, end_clock):
        return_page_scan_channel_list = get_bluetooth_channel(bt_address, Mode.PAGE_SCAN, clock * 0x1000, clock * 0x1000 +1)
        page_scan_channel_list.append(return_page_scan_channel_list[0])


def clock_offset_simulate():
    #"11:22:2a:96:ef:25"
    test_bt_address = "00:00:2a:96:ef:25"
    temp_clock = 1000
    end_clock = 0x1000 * temp_clock  #0x1000 tick is 1.28 sec.
    global page_channel_list
    global page_scan_channel_list
    #page_gengerate(test_bt_address, 0, end_clock)
    page_scan_generate(test_bt_address, 0, temp_clock)
    page_scan_channel_index = 0
    paging_list = []

    return 0
    print(end_clock)
    for _ in range(0, temp_clock):
        for i in range(0, end_clock):
            #print(i)
            for searching_position in range(0, end_clock - i):
                #print(searching_position)
                if (page_channel_list[i + searching_position] == page_scan_channel_list[_]) and ((page_channel_list[i + searching_position] % 4) < 2):
                #if (page_channel_list[i + searching_position] == 33) and ((page_channel_list[i + searching_position] % 4) < 2): 测试B Train 漏洞
                    paging_list.append(searching_position)
                    break

    #x = [0, len(paging_list)]
    x = range(0, len(paging_list))
    y = paging_list
    p = figure(plot_width=1600, plot_height=400)
    p.scatter(x, y, size=20, radius=1, marker="circle", color="navy", alpha=0.5)
    show(p)
    return 0



if __name__ == '__main__':
    clock_offset_simulate()

