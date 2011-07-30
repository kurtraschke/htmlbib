import argparse
import os
import os.path
import shutil
import re
from contextlib import closing
from collections import defaultdict

from appscript import *
from mactypes import *
from jinja2 import Environment, FileSystemLoader
from jinja2 import Markup, FileSystemBytecodeCache

from tools import fix_title, publication_keywords, nl2br, id_hash
from preview.pcache import PreviewCache


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

        previewcachefile = os.path.join(self.cachedir, "previews")

        self.pcache = PreviewCache(previewcachefile,
                                   self.bibfile,
                                   self.bibstyle)

        templatecachedir = os.path.join(self.cachedir, "templates")
        if not os.path.exists(templatecachedir):
            os.mkdir(templatecachedir)

        bd = app('BibDesk', hide=True)
        self.doc = bd.open(Alias(self.bibfile))
        self.pubs = self.doc.publications.get()
        self.sortedpubs = bd.sort(self.pubs, by=u'cite key')

        loader = FileSystemLoader(self.templatedir)
        bytecode_cache = FileSystemBytecodeCache(directory=templatecachedir)

        self.env = Environment(loader=loader,
                               bytecode_cache=bytecode_cache,
                               autoescape=True)

        self.env.globals.update({'sorted': sorted,
                                 'fix_title': fix_title,
                                 'split_keywords': publication_keywords,
                                 'id_hash': id_hash})

        self.env.filters['nl2br'] = nl2br

        self.journals = defaultdict(list)
        self.keywords = defaultdict(list)
        self.years = defaultdict(list)
        self.authors = defaultdict(list)

        for pub in self.pubs:
            journal = pub.fields[u'Journal'].value.get() or \
                      pub.fields[u'Booktitle'].value.get()
            if journal != '':
                self.journals[journal].append(pub)

            for kw in publication_keywords(pub):
                self.keywords[kw].append(pub)

            year = pub.publication_year.get()
            if year != '':
                self.years[year].append(pub)

            for author in pub.authors.get():
                name = author.abbreviated_normalized_name.get()
                self.authors[name].append(pub)

        self.env.globals.update({'doc': self.doc,
                                 'pubs': self.pubs,
                                 'sortedpubs': self.sortedpubs,
                                 'journals': self.journals,
                                 'keywords': self.keywords,
                                 'years': self.years,
                                 'authors': self.authors,
                                 'preview': lambda x: self._preview(x),
                                 'filename': os.path.split(self.bibfile)[1]})

        templates = ['detail.html', 'keywords.html', 'years.html',
                     'authors.html', 'journals.html', 'index.html']

        for template in templates:
            self._render_template(template)

        shutil.rmtree(os.path.join(self.outdir, 'static'), True)
        shutil.copytree(os.path.join(self.templatedir, 'static'),
                        os.path.join(self.outdir, 'static'))
        shutil.copy(self.bibfile, self.outdir)

    def _preview(self, publication):
        return Markup(self.pcache.get_preview(publication.cite_key.get(),
                                              publication.modified_date.get()))

    def _render_template(self, template_name, **kwargs):
        template = self.env.get_template(template_name)
        stream = template.stream(**kwargs)
        stream.dump(os.path.join(self.outdir, template_name), "utf-8")


def main():
    parser = argparse.ArgumentParser(
        description='Generate an HTML preview for a BibTeX entry.')
    parser.add_argument('-s', '--style', help="BibTeX style",
                        default='IEEEtran')
    parser.add_argument('file', help='BibTeX file')
    parser.add_argument('outdir', help='Output directory')
    parser.add_argument('templatedir', help='Template directory',
                        default='templates')

    args = parser.parse_args()
    bibfile = os.path.abspath(args.file)
    outdir = os.path.abspath(args.outdir)
    templatedir = os.path.abspath(args.templatedir)
    bibstyle = args.style

    BibMaker(bibfile, outdir, templatedir, bibstyle).makebib()

if __name__ == "__main__":
    main()
