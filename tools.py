import re

from jinja2 import evalcontextfilter, Markup, escape


def publication_keywords(publication):
    keywords = publication.keywords.get()
    if keywords == '':
        return []
    else:
        return [kw.strip() for kw in re.split(',|;', keywords)]


def fix_title(title):
    replacements = [
        ('``', u'\u201C'),
        ('\'\'', u'\u201D'),
        ('`', u'\u2018'),
        ('\'', u'\u2019'),
        ('---', u'\u2014'),
        ('--', u'\u2013')
        ]

    title = re.sub(r"{(.*?)}", r"\1", title)

    for replacement in replacements:
        title = title.replace(replacement[0], replacement[1])

    return title


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join([u'<p>%s</p>' % p.replace('\n', Markup('<br>\n'))
                           for p in _paragraph_re.split(escape(value))])
    if eval_ctx.autoescape:
        result = Markup(result)
    return result
