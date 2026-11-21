#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 xieyin contributors
"""麻豆区 (madouqu2.shop) 详情页解析器（输出与 jav_scrape.build_nfo 兼容的字典）。"""
from __future__ import annotations

import html
import re
import race_common as rc


def parse_madouqu(body: bytes, code: str) -> dict:
    """解析麻豆区详情页 HTML，提取元数据字段。

    输出字段遵循 rc.WHITELIST 白名单，绝不写入任何磁力/播放/下载链接。
    """
    t = body.decode("utf-8", "ignore")
    d = {"code": code, "source": "madouqu"}

    # 1. 封面大图 (OG Image / 正文图片)
    m_cover = re.search(r'property=["\']og:image["\']\s+content=["\']([^"\']+)["\']', t)
    if not m_cover:
        m_cover = re.search(r'name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']', t)
    if not m_cover:
        m_cover = re.search(r'class=["\']mdqn-cover[^"\']*["\'][^>]+src=["\']([^"\']+)["\']', t)
    if m_cover:
        c_url = m_cover.group(1).strip()
        # 清除 WordPress Photon / i0.wp.com 缩略图参数，还原原始高清图 URL
        if "wp-content/uploads" in c_url:
            clean_url = re.sub(r"^https?://i[0-3]\.wp\.com/", "https://", c_url)
            clean_url = clean_url.split("?")[0]
            d["cover"] = clean_url
        else:
            d["cover"] = c_url

    # 2. 标题 / 片名（优先提取正文标注的“麻豆片名”，兜底用页面 title）
    m_name = re.search(r'麻豆片名[：:]\s*([^<\r\n]+)', t)
    if m_name and m_name.group(1).strip():
        title_raw = m_name.group(1).strip()
        # 清除同行残留的“麻豆女郎”、“下载地址”或 HTML 残留
        title_raw = re.split(r'\s*(?:麻豆女郎|下载地址|下載地址|麻豆番号|Magnet|<)[：:]?', title_raw)[0].strip()
        d["title"] = title_raw
    else:
        m_t = re.search(r'<title>([^<]+)</title>', t, re.I)
        if m_t:
            raw = html.unescape(m_t.group(1))
            # 去除尾部网站名及站点描述
            raw = re.sub(r'[\s–\-]+麻豆区.*$', '', raw).strip()
            # 去掉开头番号
            d["title"] = re.sub(r'^[A-Za-z0-9\-_]+\s+', '', raw).strip() or raw

    # 3. 演员（麻豆女郎）：优先取 post-tag-label 标签，次选正文“麻豆女郎：”
    actors = []
    tags = re.findall(r'class=["\']post-tag-label["\'][^>]*>([^<]+)</a>', t)
    for tag in tags:
        clean_tag = tag.strip()
        if clean_tag and clean_tag not in actors:
            actors.append(clean_tag)
    if not actors:
        m_act = re.search(r'麻豆女郎[：:]\s*([^<\r\n]+)', t)
        if m_act:
            for a in re.split(r'[,，、\s]+', m_act.group(1).strip()):
                if a and a not in actors:
                    actors.append(a)
    if actors:
        d["actors"] = actors

    # 4. 片商 / 厂牌（麻豆传媒、精东影业、蜜桃传媒等）
    m_cat = re.search(r'class=["\']category-label["\'][^>]*>([^<]+)</a>', t)
    if m_cat:
        d["studio"] = m_cat.group(1).strip()
    else:
        d["studio"] = "麻豆传媒"

    # 5. 发行日期
    m_date = re.search(r'<time[^>]*datetime=["\']([^"\']+)["\']', t)
    if m_date:
        d["releasedate"] = m_date.group(1).split("T")[0]

    return rc.sanitize(d)
