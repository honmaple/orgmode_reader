#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: __init__.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-07-19 10:23:59 (CST)
# Last Update:星期一 2017-8-14 14:18:35 (CST)
#          By:
# Description:
# **************************************************************************
from pelican import signals
from pelican.readers import BaseReader
from pelican.utils import pelican_open
from orgpython import Regex
from orgpython import Org as _Org
from orgpython import Heading as _Heading
from orgpython import Src as _Src
from orgpython import Example as _Example
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from hashlib import sha1
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
    'save_as': compile(r'^#\+PROPERTY:\s+SAVE_AS (.*?)$'),
    'status': compile(r'^#\+PROPERTY:\s+STATUS (.*?)$')
    # 'summary': compile(r'^#\+SUMMARY:(.*?)$'),
    # 'slug': compile(r'^#\+SLUG:(.*?)$'),
    # 'language': compile(r'^#\+LANGUAGE:(.*?)$'),
    # 'modified': compile(r'^#\+MODIFIED:(.*?)$'),
    # 'tags': compile(r'^#\+TAGS:(.*?)$'),
    # 'save_as': compile(r'^#\+SAVE_AS:(.*?)$'),
}


class Heading(_Heading):
    def heading_id(self, text):
        i = int(sha1(text.encode()).hexdigest(), 16) % (10**8)
        return 'org-{}'.format(i)


class Src(_Src):
    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        try:
            lexer = get_lexer_by_name(self.lang, stripall=True)
        except ClassNotFound:
            lexer = guess_lexer(text)
        formatter = HtmlFormatter()
        return highlight(text, lexer, formatter)


class Example(_Example):
    def to_html(self):
        text = '\n'.join([child.to_html() for child in self.children])
        lexer = guess_lexer(text)
        formatter = HtmlFormatter()
        return highlight(text, lexer, formatter)


class Org(_Org):
    def parse_heading(self, text):
        element = Heading(text, self.offset, self.toc.flag)
        self.toc.append(element)
        self.children.append(element)

    def parse_src(self, text):
        lang = Regex.begin_src.match(text).group('lang')
        element = Src(self.current, lang)
        self.begin_init(element)

    def parse_example(self, text):
        element = Example(self.current)
        self.begin_init(element)


def org_to_html(text, offset=0, toc=True):
    return Org(text, offset, toc).to_html()


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
                    metadata[_meta] = _regex.match(line).group(1).strip()
                    break

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
