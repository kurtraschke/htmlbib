import argparse
import os
import os.path
import shelve
import shutil
import re
from contextlib import closing
from collections import defaultdict


from appscript import *
from mactypes import *
from jinja2 import Environment, FileSystemLoader, Markup, FileSystemBytecodeCache

from makepreview import htmlpreview
from tools import fix_title, publication_keywords

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

if not os.path.exists(outdir):
    os.mkdir(outdir)

cachedir = os.path.join(outdir, "cache")
if not os.path.exists(cachedir):
    os.mkdir(cachedir)


templatecachedir = os.path.join(cachedir, "templates")
if not os.path.exists(templatecachedir):
    os.mkdir(templatecachedir)

bd = app('BibDesk')
doc = bd.open(Alias(bibfile))
pubs = doc.publications.get()
sortedpubs = bd.sort(pubs, by=u'cite key')

env = Environment(loader=FileSystemLoader(templatedir),
                  bytecode_cache=FileSystemBytecodeCache(directory=templatecachedir))
env.globals['sorted'] = sorted
env.globals['fix_title'] = fix_title
env.globals['keywords'] = publication_keywords

def cachedpreview(publication, bibfile, bibstyle):
    citekey = str(publication.cite_key.get())
    lastmod = publication.modified_date.get()
    with closing(shelve.open(os.path.join(cachedir, "previews"))) as cache:
        if citekey not in cache or lastmod > cache[citekey]['lastmod']:
            data = {'lastmod': lastmod,
                    'preview': htmlpreview(bibfile, citekey, bibstyle)}
            cache[citekey] = data

        preview = cache[citekey]['preview']
    return preview


def render_template(template_name, **kwargs):
    template = env.get_template(template_name)
    stream = template.stream(**kwargs)
    stream.dump(os.path.join(outdir, template_name), "utf-8")


def make_detail():
    render_template('detail.html', publications=sortedpubs,
                    preview=lambda publication: Markup(cachedpreview(publication,
                                                                     bibfile,
                                                                     bibstyle)),
                    keywords=publication_keywords)


def make_keywords():
    keywords = defaultdict(list)
    for pub in pubs:
        for kw in publication_keywords(pub):
            keywords[kw].append(pub)

    render_template('keywords.html', keywords=keywords)


def make_years():
    years = defaultdict(list)
    for pub in pubs:
        year = pub.fields[u'Year'].value.get()
        if year != '':
            years[year].append(pub)

    render_template('years.html', years=years)


def make_authors():
    authors = doc.authors.get()
    names = sorted(authors, key=lambda x: x.last_name.get())

    render_template('authors.html', authors=authors, names=names)


def make_journals():
    journals = defaultdict(list)

    for pub in pubs:
        journal = pub.fields[u'Journal'].value.get() or pub.fields[u'Booktitle'].value.get()
        if journal != '':
            journals[journal].append(pub)

    render_template('journals.html', journals=journals)


make_detail()
make_keywords()
make_years()
make_authors()
make_journals()

shutil.rmtree(os.path.join(outdir, 'static'), True)
shutil.copytree(os.path.join(templatedir,'static'), os.path.join(outdir, 'static'))
