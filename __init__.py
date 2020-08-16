#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-07-19 10:23:59 (CST)
# Last Update: Sunday 2020-08-16 20:00:27 (CST)
#          By:
# Description:
# **************************************************************************
from re import compile

from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open

import orgpython
from orgpython import Document
from orgpython.inline import Link


class _Link(Link):
    def to_html(self):
        src = self.content
        if self.is_img():
            label = '<a href="{0}" data-fancybox="image"><img data-src="{1}" class="lazyload" /></a>'
            qiniu_url = compile(r'https?://7xs8ln.com1.z0.glb.clouddn.com')
            upyun_url = compile(r'https?://honmaple.b0.upaiyun.com')
            if qiniu_url.match(src) or upyun_url.match(src):
                return label.format(src + '-show', src + '-thumb')
            url = compile(r'https?://static.honmaple.com')
            if url.match(src):
                return label.format(src + '?type=show', src + '?type=thumb')
            return label.format(src, src)
        return super(_Link, self).to_html()


def parse_link(self, index, lines):
    return _Link.match(lines, index)


orgpython.inline.InlineText.parse_link = parse_link


class OrgReader(BaseReader):
    enabled = True

    file_extensions = ['org']

    def read(self, filename):
        to_toc = self.settings.get('ORG_TO_TOC', True)
        with pelican_open(filename) as text:
            org = Document(text, offset=1, toc=to_toc, highlight=True)
            content = org.to_html()

        metadata = {
            key.lower(): value
            for key, value in org.properties.items()
        }

        parsed = {}
        for key, value in metadata.items():
            if value:
                parsed[key] = self.process_metadata(key, value)

        return content, parsed


def add_reader(readers):
    readers.reader_classes['org'] = OrgReader


def register():
    signals.readers_init.connect(add_reader)


if __name__ == '__main__':
    print("aaa")
