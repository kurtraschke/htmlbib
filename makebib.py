import argparse
import os
import os.path
import shelve
import shutil
import re
from contextlib import closing
from collections import defaultdict
from zlib import crc32

from appscript import *
from mactypes import *
from jinja2 import Environment, FileSystemLoader
from jinja2 import Markup, FileSystemBytecodeCache

from makepreview import htmlpreview
from tools import fix_title, publication_keywords, nl2br


class BibMaker(object):
    def __init__(self, bibfile, outdir, templatedir, bibstyle):
        self.bibfile = bibfile
        self.outdir = outdir
        self.templatedir = templatedir
        self.bibstyle = bibstyle

    def makebib(self):
        if not os.path.exists(self.outdir):
            os.mkdir(self.outdir)

        self.cachedir = os.path.join(self.outdir, "cache")
        if not os.path.exists(self.cachedir):
            os.mkdir(self.cachedir)

        self.previewcachefile = os.path.join(self.cachedir, "previews")

        templatecachedir = os.path.join(self.cachedir, "templates")
        if not os.path.exists(templatecachedir):
            os.mkdir(templatecachedir)

        bd = app('BibDesk', hide=True)
        self.doc = bd.open(Alias(self.bibfile))
        self.pubs = self.doc.publications.get()
        self.sortedpubs = bd.sort(self.pubs, by=u'cite key')

        self.env = Environment(loader=FileSystemLoader(self.templatedir),
                               bytecode_cache=FileSystemBytecodeCache(directory=templatecachedir),
                               autoescape=True)

        self.env.globals.update({'sorted': sorted, 'fix_title': fix_title,
                                 'split_keywords': publication_keywords,
                                 'id_hash': lambda x: "%08x" % (crc32(x.encode('utf-8')) & 0xffffffff)})
        self.env.filters['nl2br'] = nl2br

        self.journals = defaultdict(list)
        self.keywords = defaultdict(list)
        self.years = defaultdict(list)

        for pub in self.pubs:
            journal = pub.fields[u'Journal'].value.get() or pub.fields[u'Booktitle'].value.get()
            if journal != '':
                self.journals[journal].append(pub)
            for kw in publication_keywords(pub):
                self.keywords[kw].append(pub)
            year = pub.publication_year.get()
            if year != '':
                self.years[year].append(pub)

        self.env.globals.update({'doc': self.doc, 'pubs': self.pubs,
                                 'sortedpubs': self.sortedpubs,
                                 'journals': self.journals,
                                 'keywords': self.keywords,
                                 'years': self.years,
                                 'authors': self.doc.authors.get(),
                                 'names': sorted(self.doc.authors.get(),
                                                 key=lambda x: x.last_name.get())})

        templates = {'detail.html': {'publications': self.sortedpubs,
                                     'preview': lambda publication: Markup(
                                         cachedpreview(publication,
                                                       self.bibfile,
                                                       self.bibstyle,
                                                       self.previewcachefile))},
                     'keywords.html': {},
                     'years.html': {},
                     'authors.html': {},
                     'journals.html': {},
                     'index.html': {'filename': os.path.split(self.bibfile)[1]}}

        for template, args in templates.iteritems():
            self.render_template(template, **args)

        shutil.rmtree(os.path.join(self.outdir, 'static'), True)
        shutil.copytree(os.path.join(self.templatedir, 'static'), os.path.join(self.outdir, 'static'))
        shutil.copy(self.bibfile, self.outdir)

    def render_template(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        stream = template.stream(**kwargs)
        stream.dump(os.path.join(self.outdir, template_name), "utf-8")


def cachedpreview(publication, bibfile, bibstyle, cachefile):
    citekey = str(publication.cite_key.get())
    lastmod = publication.modified_date.get()
    with closing(shelve.open(cachefile)) as cache:
        if citekey not in cache or lastmod > cache[citekey]['lastmod']:
            data = {'lastmod': lastmod,
                    'preview': htmlpreview(bibfile, citekey, bibstyle)}
            cache[citekey] = data

        preview = cache[citekey]['preview']
    return preview


def main():
    parser = argparse.ArgumentParser(description='Generate an HTML preview for a BibTeX entry.')
    parser.add_argument('-s', '--style', help="BibTeX style", default='IEEEtran')
    parser.add_argument('file', help='BibTeX file')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('templatedir', help='Template directory', default='templates')

    args = parser.parse_args()
    bibfile = os.path.abspath(args.file)
    outdir = os.path.abspath(args.outdir)
    templatedir = os.path.abspath(args.templatedir)
    bibstyle = args.style

    BibMaker(bibfile, outdir, templatedir, bibstyle).makebib()

if __name__ == "__main__":
    main()
