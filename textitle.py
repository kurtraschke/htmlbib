import re

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
