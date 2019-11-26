# -*- coding: utf-8 -*-
"""
    emmett_assets.ext
    -----------------

    Provides assets management for Emmett

    :copyright: (c) 2014-2019 by Giovanni Barillari
    :license: BSD, see LICENSE for more details.
"""

import os

from emmett.extensions import Extension
from renoir.extensions import Extension as RenoirExtension
from renoir.lexers import Lexer

from .webassets import Environment, Bundle


class Assets(Extension):
    default_config = dict(
        out_folder='dist'
    )

    def on_load(self):
        src_path = os.path.join(self.app.root_path, 'assets')
        if not os.path.exists(src_path):
            os.mkdir(src_path)
        dst_path = os.path.join(self.app.static_path, self.config.out_folder)
        dst_url = '/static' + (
            (self.config.out_folder and '/' + self.config.out_folder) or '')
        self.templates_ext = self.app.use_template_extension(
            AssetsTemplate,
            dst_path=dst_path,
            dst_url=dst_url,
            src_path=src_path
        )

    @property
    def register(self):
        return self.templates_ext.assets.register

    @property
    def css(self):
        return CSSAsset

    @property
    def js(self):
        return JSAsset


class Asset(Bundle):
    def __init__(self, *contents, **options):
        if len(contents) == 1 and isinstance(contents[0], (list, tuple)):
            contents = contents[0]
        options['filters'] = options.get('filters') or []
        contents, options = self._initialize_(*contents, **options)
        super(Asset, self).__init__(*contents, **options)

    def _initialize_(self, *contents, **options):
        return contents, options

    def _auto_filter_(self, contents, options, exts, fname=None):
        fname = fname or exts[0]
        if fname not in options['filters']:
            counts = 0
            for el in contents:
                if isinstance(el, str):
                    if el.split(".")[-1] in exts:
                        counts += 1
            if counts:
                if counts != len(contents):
                    last_ext = False
                    need_filter = []
                    grouped_contents = []
                    for c in contents:
                        if isinstance(c, str):
                            c_ext = c.split(".")[-1]
                        else:
                            c_ext = None
                        if c_ext != last_ext:
                            grouped_contents.append([])
                            if c_ext == fname:
                                need_filter.append(True)
                            else:
                                need_filter.append(False)
                            last_ext = c_ext
                        grouped_contents[-1].append(c)
                    copt = {'filters': [fname]}
                    new_contents = []
                    for i in range(0, len(grouped_contents)):
                        if not isinstance(grouped_contents[i][0], str):
                            for el in grouped_contents[i]:
                                new_contents.append(el)
                        else:
                            if need_filter[i] == True:
                                new_contents.append(
                                    self.__class__(
                                        *grouped_contents[i], **copt))
                            else:
                                new_contents.append(
                                    self.__class__(*grouped_contents[i]))
                    contents = new_contents
                else:
                    options['filters'].append(fname)
        return contents, options


class JSAsset(Asset):
    def _initialize_(self, *contents, **options):
        contents, options = self._auto_filter_(contents, options, ['coffee'])
        return contents, options

    def minify(self):
        self.filters.append('jsmin')
        self._set_filters(self.filters)
        return self


class CSSAsset(Asset):
    def _initialize_(self, *contents, **options):
        contents, options = self._auto_filter_(
            contents, options, ['sass', 'scss'], 'libsass')
        return contents, options

    def minify(self):
        self.filters.append('cssmin')
        self._set_filters(self.filters)
        return self


class AssetsLexer(Lexer):
    evaluate = True

    def process(self, ctx, value):
        ctx.python_node(f'for _asset_url_ in __emt_assets_gen__("{value}"):')
        ctx.variable('_asset_url_', escape=False)
        ctx.python_node('pass')


class AssetsTemplate(RenoirExtension):
    namespace = 'EmmettAssets'
    lexers = {'assets': AssetsLexer}

    def on_load(self):
        self.assets = Environment(
            self.config['dst_path'],
            self.config['dst_url'],
            load_path=[self.config['src_path']]
        )

    @staticmethod
    def _js(url):
        return f'<script type="text/javascript" src="{url}"></script>'

    @staticmethod
    def _css(url):
        return f'<link rel="stylesheet" href="{url}" type="text/css">'

    def _get_static(self, asset):
        rv = []
        for url in self.assets[asset].urls():
            file_name = url.split('?')[0]
            file_ext = file_name.rsplit('.', 1)[-1]
            if file_ext == 'js':
                el = self._js(url)
            elif file_ext == "css":
                el = self._css(url)
            else:
                continue
            rv.append(el)
        return rv

    def context(self, ctx):
        ctx['__emt_assets_gen__'] = self._get_static
