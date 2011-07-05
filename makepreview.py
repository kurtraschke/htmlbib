import tempfile
import shutil
import os.path
import argparse
import subprocess
import shlex

import lxml.etree as etree

def htmlpreview(bibfile, citekey, bibstyle='IEEEtran'):
    basename = os.path.split(bibfile)[1].split('.')[0]
    workingdir = tempfile.mkdtemp()

    previewtemplate = r"""
\documentclass[letterpaper]{article}
\usepackage{hyperref}
\pagestyle{empty}
\renewcommand{\refname}{}
\begin{document}
\nocite{%(citekey)s}
\bibliography{%(bibfile)s}   
\bibliographystyle{%(bibstyle)s}
\end{document}
"""

    with open(os.path.join(workingdir, 'preview.tex'), 'w') as previewfile:
        previewfile.write(previewtemplate % {'citekey': citekey,
                                             'bibfile': basename,
                                             'bibstyle': bibstyle})

    shutil.copy(bibfile, workingdir)
    
    with open(os.devnull, 'w') as devnull:
        subprocess.check_call(shlex.split('htlatex preview'), stdout=devnull, cwd=workingdir)
        subprocess.check_call(shlex.split('bibtex preview'), stdout=devnull, cwd=workingdir)
        subprocess.check_call(shlex.split('htlatex preview'), stdout=devnull, cwd=workingdir)

    with open(os.path.join(workingdir, 'preview.html'), 'r') as outfile:
        parser = etree.HTMLParser()
        tree = etree.parse(outfile, parser)
        
        node =  tree.xpath("//p[@class='bibitem']")[0]
        node.remove(node.xpath("//span[@class='biblabel']")[0])

        html = etree.tostring(node, encoding=unicode, method='html')

    shutil.rmtree(workingdir)
    return html

def main():
    parser = argparse.ArgumentParser(description='Generate an HTML preview for a BibTeX entry.')
    parser.add_argument('file', help='BibTeX file')
    parser.add_argument('citekey', help='cite key')
    args = parser.parse_args()
    
    inputfile = os.path.abspath(args.file)
    
    print htmlpreview(inputfile, args.citekey)

if __name__ == '__main__':
    main()
