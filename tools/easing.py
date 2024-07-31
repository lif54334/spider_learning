#!/usr/bin/env python
# -*- coding: utf-8 -*-
# copy from https://github.com/aneasystone/selenium-test/blob/master/12-slider-captcha.py
# thanks to aneasystone for his great work
import math
from typing import List, Tuple

import numpy as np

# 定义了一系列缓动函数（easing functions）和一个生成轨迹点的函数，主要用于模拟平滑动画效果，常应用于UI滑块验证等场景。
# https://github.com/gdsmith/jquery.easing/blob/master/jquery.easing.js
def ease_in_quad(x):
    return x * x


def ease_out_quad(x):
    return 1 - (1 - x) * (1 - x)


def ease_out_quart(x):
    return 1 - pow(1 - x, 4)


def ease_out_expo(x):
    if x == 1:
        return 1
    else:
        return 1 - pow(2, -10 * x)


def ease_out_bounce(x):
    n1 = 7.5625
    d1 = 2.75
    if x < 1 / d1:
        return n1 * x * x
    elif x < 2 / d1:
        x -= 1.5 / d1
        return n1 * x * x + 0.75
    elif x < 2.5 / d1:
        x -= 2.25 / d1
        return n1 * x * x + 0.9375
    else:
        x -= 2.625 / d1
        return n1 * x * x + 0.984375


def ease_out_elastic(x):
    if x == 0:
        return 0
    elif x == 1:
        return 1
    else:
        c4 = (2 * math.pi) / 3
        return pow(2, -10 * x) * math.sin((x * 10 - 0.75) * c4) + 1


def get_tracks(distance, seconds, ease_func) -> Tuple[List[int], List[int]]:
    # 此函数根据给定的距离、持续时间和指定的缓动函数来生成一系列的偏移量和轨迹点。
    # 首先，它定义了一个基础轨迹列表和偏移量列表，然后在指定的时间间隔（本例中为0.1秒）内遍历时间，并计算出每个时间点基于缓动函数应达到的偏移量。
    # 每个偏移量相对于前一个偏移量的增量即为轨迹点，累积偏移量则记录实际移动的总距离。
    tracks = [0]
    offsets = [0]
    for t in np.arange(0.0, seconds, 0.1):
        ease = globals()[ease_func]
        offset = round(ease(t / seconds) * distance)
        tracks.append(offset - offsets[-1])
        offsets.append(offset)
    return offsets, tracks


if __name__ == '__main__':
    o, tl = get_tracks(129, 3, "ease_out_expo")
    print(tl)
