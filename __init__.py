#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-07-19 10:23:59 (CST)
# Last Update:星期四 2017-7-27 11:14:3 (CST)
#          By:
# Description:
# **************************************************************************
from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open
from orgpython import org_to_html
from re import compile

regex = {
    'title': compile(r'^#\+TITLE:(.*?)$'),
    'date': compile(r'^#\+DATE:(.*?)$'),
    'category': compile(r'^#\+CATEGORY:(.*?)$'),
    'author': compile(r'^#\+AUTHOR:(.*?)$'),
    'summary': compile(r'^#\+PROPERTY:\s+SUMMARY (.*?)$'),
    'slug': compile(r'^#\+PROPERTY:\s+SLUG (.*?)$'),
    'language': compile(r'^#\+PROPERTY:\s+LANGUAGE (.*?)$'),
    'modified': compile(r'^#\+PROPERTY:\s+MODIFIED (.*?)$'),
    'tags': compile(r'^#\+PROPERTY:\s+TAGS (.*?)$'),
    'save_as': compile(r'^#\+PROPERTY:\s+SAVE_AS (.*?)$')
    # 'summary': compile(r'^#\+SUMMARY:(.*?)$'),
    # 'slug': compile(r'^#\+SLUG:(.*?)$'),
    # 'language': compile(r'^#\+LANGUAGE:(.*?)$'),
    # 'modified': compile(r'^#\+MODIFIED:(.*?)$'),
    # 'tags': compile(r'^#\+TAGS:(.*?)$'),
    # 'save_as': compile(r'^#\+SAVE_AS:(.*?)$'),
}


class OrgReader(BaseReader):
    enabled = True

    file_extensions = ['org']

    def read(self, filename):
        max_line = self.settings.get('ORG_MAX_LINE', 15)
        to_toc = self.settings.get('ORG_TO_TOC', True)
        with pelican_open(filename) as text:
            content = org_to_html(text, toc=to_toc)
            meta = text.splitlines()[:max_line]
        metadata = {}
        for line in meta:
            for _meta, _regex in regex.items():
                if _regex.match(line):
                    metadata[_meta] = _regex.match(line).group(1)

        for key in ['save_as', 'modified', 'lang', 'summary']:
            if key in metadata and not metadata[key]:
                metadata.pop(key)

        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return content, parsed


def add_reader(readers):
    readers.reader_classes['org'] = OrgReader


def register():
    signals.readers_init.connect(add_reader)
