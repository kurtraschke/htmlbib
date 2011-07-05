import argparse
import os
import os.path
import codecs
import shelve
import shutil
import re
from contextlib import closing
from collections import defaultdict


from appscript import *
from mactypes import *
from jinja2 import Environment, FileSystemLoader, Markup

from makepreview import htmlpreview
from textitle import fix_title

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

#elif os.path.exists(outdir) and not os.path.isdir(outdir)

bd = app('BibDesk')
doc = bd.open(Alias(bibfile))
pubs = doc.publications.get()
sortedpubs = bd.sort(pubs, by=u'cite key')

env = Environment(loader=FileSystemLoader(templatedir))
env.globals['sorted'] = sorted
env.globals['fix_title'] = fix_title

def cachedpreview(publication, bibfile, bibstyle):
    citekey = str(publication.cite_key.get())
    lastmod = publication.modified_date.get()
    with closing(shelve.open(os.path.join(outdir, "previewcache"))) as cache:
        if citekey not in cache or lastmod > cache[citekey]['lastmod']:
            data = {'lastmod': lastmod,
                    'preview': htmlpreview(bibfile, citekey, bibstyle)}
            cache[citekey] = data
            
        preview = cache[citekey]['preview']
    return preview

def publication_keywords(publication):
    keywords = publication.keywords.get()
    if keywords == '':
        return []
    else:
        return [kw.strip() for kw in re.split(',|;', keywords)]


def make_detail():
    template = env.get_template('bibliography.html')
    out = template.render(publications=sortedpubs,
                          preview=lambda publication: Markup(cachedpreview(publication,
                                                                           bibfile,
                                                                           bibstyle)),
                          keywords=publication_keywords)
    
    with codecs.open(os.path.join(outdir,"detail.html"), "w", "utf-8") as f:
        f.write(out)

def make_keywords():
    keywords = defaultdict(list)
    for pub in pubs:
        for kw in publication_keywords(pub):
            keywords[kw].append(pub)

    template = env.get_template('keywords.html')
    out = template.render(keywords=keywords)
    
    with codecs.open(os.path.join(outdir,"keywords.html"), "w", "utf-8") as f:
        f.write(out)

def make_years():
    years = defaultdict(list)
    for pub in pubs:
        year = pub.fields[u'Year'].value.get()
        if year != '':
            years[year].append(pub)

    template = env.get_template('years.html')
    out = template.render(years=years)
    
    with codecs.open(os.path.join(outdir,"years.html"), "w", "utf-8") as f:
        f.write(out)

def make_authors():
    authors = doc.authors.get()
    names = sorted(authors, key=lambda x: x.last_name.get())

    template = env.get_template('authors.html')
    out = template.render(authors=authors, names=names)
    
    with codecs.open(os.path.join(outdir,"authors.html"), "w", "utf-8") as f:
        f.write(out)

def make_journals():
    journals = defaultdict(list)

    for pub in pubs:
        journal = pub.fields[u'Journal'].value.get() or pub.fields[u'Booktitle'].value.get()
        if journal != '':
            journals[journal].append(pub)

    template = env.get_template('journals.html')
    out = template.render(journals=journals)
    
    with codecs.open(os.path.join(outdir,"journals.html"), "w", "utf-8") as f:
        f.write(out)

    

make_detail()
make_keywords()
make_years()
make_authors()
make_journals()

shutil.rmtree(os.path.join(outdir, 'static'), True)
shutil.copytree(os.path.join(templatedir,'static'), os.path.join(outdir, 'static')) 


