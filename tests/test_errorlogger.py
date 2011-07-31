# coding: utf-8

import os
import sys
import unittest
import sqlite3
import threading

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(base_dir)
from errorlogger import ErrorLogger


def worker(path, mode):
    try:
        with ErrorLogger(path, mode):
            a = 1 / 0
    except:
        pass


class TestErrorLoggerFile(unittest.TestCase):

    def setUp(self):
        pass
        self.path = 'error.txt'
        self._clear(self.path)

    def tearDown(self):
        pass

    def test_no_error(self):
        try:
            with ErrorLogger(self.path):
                a = 1 + 1
        except:
            self.fail('must not happen')

    def test_zero_division_error(self):
        try:
            with ErrorLogger(self.path):
                a = 1 / 0
        except:
            s = self._read(self.path)
            self.assertTrue('ZeroDivisionError' in s)

    def test_custom_error(self):
        class MyError: pass
        try:
            with ErrorLogger(self.path):
                raise MyError()
        except:
            s = self._read(self.path)
            self.assertTrue('MyError', s)

    def test_multi_thread(self):
        job_num = 10
        jobs = []
        for i in range(job_num):
            job = threading.Thread(target=worker, args=(self.path, 'file'))
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()

        s = self._read(self.path)
        self.assertEqual(s.count('ZeroDivisionError'), job_num)

    def _read(self, path):
        with open(path, 'r') as f:
            return f.read()

    def _clear(self, path):
        with open(path, 'w'):
            pass


class TestErrorLoggerSqlite(unittest.TestCase):

    def setUp(self):
       self.path = 'error.db'
       if os.path.isfile(self.path):
          os.unlink(self.path)

    def tearDown(self):
        pass

    def test_no_error(self):
        try:
            with ErrorLogger(self.path, 'sqlite'):
                a = 1 + 1
        except:
            self.fail('must not happen')

    def test_zero_division_error(self):
        try:
            with ErrorLogger(self.path, 'sqlite'):
                a = 1 / 0
        except:
            s = self._select(self.path)
            self.assertTrue('ZeroDivisionError' in s)

    def test_custom_error(self):
        class MyError(Exception): pass
        try:
            with ErrorLogger(self.path, 'sqlite'):
                raise MyError()
        except:
            s = self._select(self.path)
            self.assertTrue('MyError' in s)

    def test_multi_thread(self):
        job_num = 10
        jobs = []
        for i in range(job_num):
            job = threading.Thread(target=worker, args=(self.path, 'sqlite'))
            jobs.append(job)
            job.start()

        for job in jobs:
            job.join()

        rows = self._select_all(self.path)
        for row in rows:
            self.assertTrue('ZeroDivisionError' in row)

    def _select(self, db):
        con = sqlite3.connect(db)
        for row in con.execute('SELECT message FROM logs'):
            return row[0]

    def _select_all(self, db):
        con = sqlite3.connect(db)
        rows = []
        for row in con.execute('SELECT message FROM logs'):
            rows.append(row[0])
        con.close()
        return rows


if __name__ == '__main__':
    unittest.main()
