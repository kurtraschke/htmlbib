import sqlite3
from .engine import htmlpreview


class PreviewCache(object):
    def __init__(self, cachefile, bibfile, bibstyle):
        self.bibfile = bibfile
        self.bibstyle = bibstyle
        self.db = sqlite3.connect(cachefile,
                  detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.db.row_factory = sqlite3.Row

        self.db.execute("""CREATE TABLE IF NOT EXISTS preview_cache(
                           cite_key TEXT PRIMARY KEY,
                           last_modified TIMESTAMP,
                           html_preview TEXT)""")
        self.db.commit()

    def _set_preview(self, cite_key, last_modified):
        html_preview = htmlpreview(self.bibfile, cite_key, self.bibstyle)

        self.db.execute("""INSERT OR REPLACE INTO preview_cache
                           (cite_key, last_modified, html_preview)
                           VALUES (?, ?, ?)""",
                        (cite_key, last_modified, html_preview))
        self.db.commit()

    def get_preview(self, cite_key, last_modified):
        cur = self.db.execute("""SELECT last_modified FROM preview_cache
                                 WHERE cite_key = ?""",
                              (cite_key,))

        row = cur.fetchone()
        if row is None or row['last_modified'] < last_modified:
            self._set_preview(cite_key, last_modified)

        cur = self.db.execute("""SELECT html_preview FROM preview_cache
                                 WHERE cite_key = ?""",
                              (cite_key,))
        row = cur.fetchone()

        return row['html_preview']
