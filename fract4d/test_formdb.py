#!/usr/bin/env python

# this is deliberately not included in test.py since it hits a live website
# and I don't want to screw up their bandwidth allocation

import sys
sys.path.append("..")

import unittest
import StringIO
import SocketServer
import SimpleHTTPServer
import posixpath
import urllib
import httplib
import os
import threading
import zipfile
import fractutils.slave

import formdb


formdb.target_base = "http://localhost:8090/"

class MyRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # same as a simplehttprequesthandler, but with a different base dir
    def translate_path(self, path):
        """Translate a /-separated PATH to the local filename syntax.

        Components that mean special things to the local file system
        (e.g. drive or directory names) are ignored.  (XXX They should
        probably be diagnosed.)

        """
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = posixpath.normpath("../testdata")
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir): continue
            path = os.path.join(path, word)
        return path

    #def log_message(self, format, *args):
    #    # hide log messages
    #    pass
    
def threadStart():
    handler = MyRequestHandler
    httpd = SocketServer.TCPServer(("",8090), handler)
    httpd.serve_forever()

thread = threading.Thread(target=threadStart)
thread.setDaemon(True)
thread.start()

class Test(unittest.TestCase):
    def testFetch(self):
        conn = httplib.HTTPConnection('localhost',8090)
        conn.request("GET", "/trigcentric.fct")
        response = conn.getresponse()
        self.assertEqual(200, response.status)

    def testFetchWithFormDB(self):
        data = formdb.fetchzip("test.zip")
        self.assertNotEqual(None, data)
        
    def testFetchAndUnpack(self):        
        conn = httplib.HTTPConnection('localhost',8090)
        conn.request("GET", "/test.zip")
        response = conn.getresponse()
        self.assertEqual(200, response.status)
        zf = zipfile.ZipFile(StringIO.StringIO(response.read()),"r")
        info = zf.infolist()
        self.assertEqual("trigcentric.fct", info[0].filename)
        
    def testCreate(self):
        f = open("../testdata/example_formula_db.txt")
        
        formlinks = formdb.parse(f)

        self.assertEqual(5, len(formlinks))

        self.assertEqual("/cgi-bin/formuladb?view;file=gwfa.ucl;type=.txt", formlinks[0])
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
