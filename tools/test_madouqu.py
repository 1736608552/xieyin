#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""麻豆区数据源与国产番号解析单元测试。"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS = os.path.join(ROOT, "src", "xieyin", "app", "xieyin", "scripts")
sys.path.insert(0, SCRIPTS)

import jav_scrape as j
import race_scrape as rs
from madouqu_parse import parse_madouqu


class MadouquScrapeTest(unittest.TestCase):
    def test_code_of_madou(self):
        # 带有年份的国产番号（防止年份前两位被吞入番号）
        self.assertEqual(j.code_of("MDCM-0001 2022.11.05 國風按摩院 初訪春覺樓上 苏语棠 8.7"), "MDCM-0001")
        self.assertEqual(j.code_of("MDSR-0001-1 2022.05.13 妖女榨汁 篇章一 秦老師的秘密 夏晴子 8.6 巨乳"), "MDSR-0001-1")
        # 多段国产番号
        self.assertEqual(j.code_of("MDSR-0013-2 郝叔叔和他的女人"), "MDSR-0013-2")
        self.assertEqual(j.code_of("MD-0123-1"), "MD-0123-1")
        self.assertEqual(j.code_of("MDWP-0012"), "MDWP-0012")
        self.assertEqual(j.code_of("MC-001"), "MC-001")
        # 传统日系番号保持不变
        self.assertEqual(j.code_of("ADN-451-UC"), "ADN-451")
        self.assertEqual(j.code_of("071518-714"), "071518-714")

    def test_madou_code_re(self):
        self.assertTrue(bool(rs.MADOU_CODE_RE.match("MDSR-0013-2")))
        self.assertTrue(bool(rs.MADOU_CODE_RE.match("MD-0123")))
        self.assertTrue(bool(rs.MADOU_CODE_RE.match("PM-005")))
        self.assertTrue(bool(rs.MADOU_CODE_RE.match("TM-001")))
        self.assertFalse(bool(rs.MADOU_CODE_RE.match("ADN-451")))
        self.assertFalse(bool(rs.MADOU_CODE_RE.match("SSIS-001")))

    def test_check_code_multi_segment(self):
        body = b"Welcome to MDSR-0013-2 page"
        self.assertTrue(rs.check_code(body, "MDSR-0013-2"))
        self.assertFalse(rs.check_code(body, "MDSR-0014"))

    def test_parse_madouqu_html(self):
        sample_html = b"""<!doctype html>
        <html><head>
        <title>MDSR-0013-2 \xe9\x83\x9d\xe5\x8f\x94\xe5\x8f\x94\xe5\x92\x8c\xe4\xbb\x96\xe7\x9a\x84\xe5\xa5\xb3\xe4\xba\xba \xe8\x8b\x8f\xe7\x95\x85 \xe6\xa2\x81\xe5\xb9\x82 &#8211; \xe9\xba\xbb\xe8\xb1\x86\xe5\x8c\xba</title>
        <meta property="og:image" content="https://i0.wp.com/madouqu2.shop/wp-content/uploads/2026/03/1774614914-1396725d98d7177.png?ssl=1&amp;resize=240%2C160">
        <time datetime="2026-03-27T20:36:29+08:00">2026-03-27</time>
        </head><body>
        <a class="category-label" href="/modelmedia/">\xe9\xba\xbb\xe8\xb1\x86\xe4\xbc\xa0\xe5\xaa\x92</a>
        <a class="post-tag-label" href="/tag/1/">\xe6\xa2\x81\xe5\xb9\x82</a>
        <a class="post-tag-label" href="/tag/2/">\xe8\x8b\x8f\xe7\x95\x85</a>
        <p>\xe9\xba\xbb\xe8\xb1\x86\xe7\x95\xaa\xe5\x8f\xb7\xef\xbc\x9aMDSR-0013-2</p>
        <p>\xe9\xba\xbb\xe8\xb1\x86\xe7\x89\x87\xe5\x90\x8d\xef\xbc\x9a\xe9\x83\x9d\xe5\x8f\x94\xe5\x8f\x94\xe5\x92\x8c\xe4\xbb\x96\xe7\x9a\x84\xe5\xa5\xb3\xe4\xba\xba</p>
        <p>\xe9\xba\xbb\xe8\xb1\x86\xe5\xa5\xb3\xe9\x83\x8e\xef\xbc\x9a\xe8\x8b\x8f\xe7\x95\x85\xe3\x80\x81\xe6\xa2\x81\xe5\xb9\x82</p>
        <p>\xe4\xb8\x8b\xe8\xbc\x89\xe5\x9c\xb0\xe5\x9d\x80\xef\xbc\x9amagnet:?xt=urn:btih:dummy</p>
        </body></html>"""
        res = parse_madouqu(sample_html, "MDSR-0013-2")
        self.assertEqual(res["code"], "MDSR-0013-2")
        self.assertEqual(res["title"], "郝叔叔和他的女人")
        self.assertEqual(res["studio"], "麻豆传媒")
        self.assertEqual(res["releasedate"], "2026-03-27")
        self.assertIn("苏畅", res["actors"])
        self.assertIn("梁幂", res["actors"])
        # 验证 i0.wp.com 参数被清洗为原始高清图
        self.assertEqual(res["cover"], "https://madouqu2.shop/wp-content/uploads/2026/03/1774614914-1396725d98d7177.png")
        # 验证 magnet 绝不被写入
        for v in res.values():
            if isinstance(v, str):
                self.assertNotIn("magnet", v)


if __name__ == "__main__":
    unittest.main()
