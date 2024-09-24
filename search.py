from functools import reduce
from markupsafe import Markup
import json
import logging
import os
import shutil

from sigal import signals
from sigal.utils import url_from_path
from sigal.writer import AbstractWriter

logger = logging.getLogger(__name__)

ASSETS_PATH = os.path.normpath(
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static', 'js'))

class PageWriter(AbstractWriter):
    '''A writer for writing media pages, based on writer'''

    template_file = "search.html"

    def write(self, album):
        ''' Generate the media page and save it '''

        from sigal import __url__ as sigal_link

        page = self.template.render({
            'album': album,
            'index_title': self.index_title,
            'settings': self.settings,
            'sigal_link': sigal_link,
            'theme': {'name': os.path.basename(self.theme),
                      'url': url_from_path(os.path.relpath(self.theme_path,
                                                           album.dst_path))},
        })

        output_file = os.path.join(album.dst_path, 'search.html')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(page)

def generate_search(gallery):
    id = 1
    output_file = os.path.join(gallery.albums['.'].dst_path, 'static/js/search-content.js')
    store = {}
    for album in gallery.albums.values():
        album_titles = " , ".join([*map(lambda x: x[1], album.breadcrumb)])
        for item in album.medias:
            data = {}
            data['title'] = item.title
            if 'author' in item.meta:
                data['author'] = item.meta['author'][0]
            data['url'] = "/" + item.path + "/" + item.url
            data['thumbnail'] = item.thumbnail
            data['mime'] = item.mime
            if 'slides' in item.meta:
                data['slides'] = item.meta['slides'][0]
            data['album'] = album_titles;
            store[str(id)] = data
            id = id + 1

    with open(output_file, 'w', encoding='utf8') as f:
        f.write("window.store = ")
        f.write(json.dumps(store))

    writer = PageWriter(gallery.settings, index_title="Search Results")
    writer.write(gallery.albums['.'])

    shutil.copyfile(os.path.join(ASSETS_PATH, 'lunr.js'),
                    os.path.join(gallery.albums['.'].dst_path, 'static', 'js', 'lunr.js'))

def register(settings):
    signals.gallery_build.connect(generate_search)
