# coding: utf-8
"""
errorlogger
===========

Dump error message in `with` statement to file or sqlite.


Usage
-----

    from errorlogger import ErrorLogger
    
    # dump to file
    with ErrorLogger('log.txt'):
        do_something()

    # dump to sqlite    
    with ErrorLogger('log.db', 'sqlite'):
        do_something()


License
-------

MIT License


Author
------

echi5ya  <echi5ya@gmail.com>
"""

import sqlite3
import datetime
import traceback
import threading


__all__ = ['ErrorLogger']


CREATE_TABLE_SQL = """\
create table if not exists logs(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message TEXT,
    created_at VARCHER(128)
);
"""


_lock = threading.RLock()


class ErrorLogger(object):

    def __init__(self, path, mode='file'):
        self.path = path
        if mode in ('file', 'sqlite'):
            self.mode = mode
        else:
            self.mode = 'file'

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type:
            msg = ''.join(traceback.format_exception(exc_type, exc_value, tb))
            if self.mode == 'sqlite':
                self._log_to_sqlite(msg)
            else:
                self._log_to_file(msg)
            return False
        return True

    def _log_to_sqlite(self, msg):
        con = sqlite3.connect(self.path)
        con.execute(CREATE_TABLE_SQL)
        sql = (
            "INSERT INTO logs "
            "VALUES (NULL,?,DATETIME('NOW', 'LOCALTIME'))"
        )
        con.execute(sql, (msg,))
        con.commit()
        con.close()

    def _log_to_file(self, msg):
        with _lock:
            with open(self.path, 'a') as f:
                t = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write('%s\n' % ('-' * 80))
                f.write('%s\n%s' % (t, msg))
