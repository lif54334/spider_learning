# -*- coding: utf-8 -*-
# @Author  : relakkes@gmail.com
# @Time    : 2023/12/2 12:55
# @Desc    : 滑块相关的工具包
import os
from typing import List
from urllib.parse import urlparse

import cv2
import httpx
import numpy as np

# 定义了一个名为Slide的类，以及两个辅助函数get_track_simple和get_tracks，
# 用于处理滑块验证码的相关操作，
# 如缺口图片与背景图片的匹配、边缘检测、移动轨迹生成等。
class Slide:
    """
    copy from https://blog.csdn.net/weixin_43582101 thanks for author
    update: relakkes
    """
    # 这个类的主要目的是帮助找到滑块验证码中缺口的位置，进而生成相应的移动轨迹。
    def __init__(self, gap, bg, gap_size=None, bg_size=None, out=None):
        """
        :param gap: 缺口图片链接或者url
        :param bg: 带缺口的图片链接或者url
        """
        # 接受缺口图片(gap)和背景图片(bg)的链接或路径，可选地接受它们的尺寸以及输出图片的路径。它会检查图片是否是URL，并下载到临时文件夹，然后读取并调整图片尺寸。
        self.img_dir = os.path.join(os.getcwd(), 'temp_image')
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        bg_resize = bg_size if bg_size else (340, 212)
        gap_size = gap_size if gap_size else (68, 68)
        self.bg = self.check_is_img_path(bg, 'bg', resize=bg_resize)
        self.gap = self.check_is_img_path(gap, 'gap', resize=gap_size)
        self.out = out if out else os.path.join(self.img_dir, 'out.jpg')

    @staticmethod
    def check_is_img_path(img, img_type, resize):
        # 用于检查并处理图片路径。如果是URL，就通过HTTP请求获取图片内容，解码为OpenCV格式，按指定尺寸调整大小，并保存到本地。如果图片已经是本地路径，则直接返回。
        if img.startswith('http'):
            headers = {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;"
                          "q=0.8,application/signed-exchange;v=b3;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Accept-Language": "zh-CN,zh;q=0.9,en-GB;q=0.8,en;q=0.7,ja;q=0.6",
                "AbstractCache-Control": "max-age=0",
                "Connection": "keep-alive",
                "Host": urlparse(img).hostname,
                "Upgrade-Insecure-Requests": "1",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/91.0.4472.164 Safari/537.36",
            }
            img_res = httpx.get(img, headers=headers)
            if img_res.status_code == 200:
                img_path = f'./temp_image/{img_type}.jpg'
                image = np.asarray(bytearray(img_res.content), dtype="uint8")
                image = cv2.imdecode(image, cv2.IMREAD_COLOR)
                if resize:
                    image = cv2.resize(image, dsize=resize)
                cv2.imwrite(img_path, image)
                return img_path
            else:
                raise Exception(f"保存{img_type}图片失败")
        else:
            return img

    @staticmethod
    def clear_white(img):
        """清除图片的空白区域，这里主要清除滑块的空白"""
        img = cv2.imread(img)
        rows, cols, channel = img.shape
        min_x = 255
        min_y = 255
        max_x = 0
        max_y = 0
        for x in range(1, rows):
            for y in range(1, cols):
                t = set(img[x, y])
                if len(t) >= 2:
                    if x <= min_x:
                        min_x = x
                    elif x >= max_x:
                        max_x = x

                    if y <= min_y:
                        min_y = y
                    elif y >= max_y:
                        max_y = y
        img1 = img[min_x:max_x, min_y: max_y]
        return img1

    def template_match(self, tpl, target):
        # 使用OpenCV的模板匹配功能来寻找缺口在背景图片中的位置。它比较缺口图片与背景图片的相似度，找到最佳匹配区域并返回其左上角的x坐标。
        th, tw = tpl.shape[:2]
        result = cv2.matchTemplate(target, tpl, cv2.TM_CCOEFF_NORMED)
        # 寻找矩阵(一维数组当作向量,用Mat定义) 中最小值和最大值的位置
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        tl = max_loc
        br = (tl[0] + tw, tl[1] + th)
        # 绘制矩形边框，将匹配区域标注出来
        # target：目标图像
        # tl：矩形定点
        # br：矩形的宽高
        # (0,0,255)：矩形边框颜色
        # 1：矩形边框大小
        cv2.rectangle(target, tl, br, (0, 0, 255), 2)
        cv2.imwrite(self.out, target)
        return tl[0]

    @staticmethod
    def image_edge_detection(img):
        # 应用Canny边缘检测算法，从灰度图中提取边缘信息。
        edges = cv2.Canny(img, 100, 200)
        return edges

    def discern(self):
        # 先清理并处理缺口图片与背景图片，然后进行边缘检测，最后调用template_match找到缺口位置。
        img1 = self.clear_white(self.gap)
        img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2GRAY)
        slide = self.image_edge_detection(img1)

        back = cv2.imread(self.bg, cv2.COLOR_RGB2GRAY)
        back = self.image_edge_detection(back)

        slide_pic = cv2.cvtColor(slide, cv2.COLOR_GRAY2RGB)
        back_pic = cv2.cvtColor(back, cv2.COLOR_GRAY2RGB)
        x = self.template_match(slide_pic, back_pic)
        # 输出横坐标, 即 滑块在图片上的位置
        return x


def get_track_simple(distance) -> List[int]:
    # 生成一个简单的渐进式移动轨迹。通过控制加速度，使滑块在运动过程中速度先增后减，模拟真实的人类操作。

    # 有的检测移动速度的 如果匀速移动会被识别出来，来个简单点的 渐进
    # distance为传入的总距离
    # 移动轨迹
    track: List[int] = []
    # 当前位移
    current = 0
    # 减速阈值
    mid = distance * 4 / 5
    # 计算间隔
    t = 0.2
    # 初速度
    v = 1

    while current < distance:
        if current < mid:
            # 加速度为2
            a = 4
        else:
            # 加速度为-2
            a = -3
        v0 = v
        # 当前速度
        v = v0 + a * t  # type: ignore
        # 移动距离
        move = v0 * t + 1 / 2 * a * t * t
        # 当前位移
        current += move  # type: ignore
        # 加入轨迹
        track.append(round(move))
    return track


def get_tracks(distance: int, level: str = "easy") -> List[int]:
    # 根据难度级别（默认为"easy"）选择不同的轨迹生成策略。
    # 当难度为"easy"时，直接调用get_track_simple；
    # 否则，使用来自easing模块的get_tracks函数生成更复杂的缓动效果轨迹，例如指数缓出。

    if level == "easy":
        return get_track_simple(distance)
    else:
        from . import easing
        _, tricks = easing.get_tracks(distance, seconds=2, ease_func="ease_out_expo")
        return tricks
