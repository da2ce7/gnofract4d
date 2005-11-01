# slave.py - run a subordinate process asynchronously

import sys
import os

import fcntl
import signal
import select
import errno
import time

try:
    import subprocess
except ImportError:
    # this python too old - use our backported copy of stdlib file
    import gf4d_subprocess as subprocess

def makeNonBlocking(fd):
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    try:
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NDELAY)
    except AttributeError:
        import FCNTL
        fcntl.fcntl(fd, FCNTL.F_SETFL, fl | FCNTL.FNDELAY)
        
class Slave(object):
    def __init__(self, cmd, *args):
        self.cmd = cmd
        self.args = list(args)
        self.process = None
        self.input = ""
        self.in_pos = 0
        self.stdin = None
        self.stdout = None
        self.output = ""
        self.dead = False
        
    def run(self, input):
        self.input = input
        self.process = subprocess.Popen(
            [self.cmd, str(len(input))] + self.args,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,close_fds=True)

        makeNonBlocking(self.process.stdin.fileno())
        makeNonBlocking(self.process.stdout.fileno())
        self.stdin = self.process.stdin
        self.stdout = self.process.stdout

    def write(self):
        if self.dead:
            self.on_finish_writing()
            return False
        
        bytes_to_write = min(len(self.input) - self.in_pos,1000)
        if bytes_to_write < 1:
            self.stdin.close()
            self.on_finish_writing()
            return False

        try:            
            self.stdin.write(
                self.input[self.in_pos:self.in_pos+bytes_to_write])
            #print "wrote %d" % bytes_to_write
        except IOError, err:
            if err.errno == errno.EAGAIN:
                #print "again!"
                return True
            raise
        
        self.in_pos += bytes_to_write
        return True

    def read(self):
        if self.dead:
            self.on_complete()
            return False
        try:
            data = self.stdout.read(-1)
            #print "read", len(data)
            if data == "":
                # checking all these ways to see if child has died
                # since they don't seem to be reliable
                if self.process.poll() == None or self.process.returncode != None:
                    self.on_complete()
                    return False
        except IOError, err:
            if err.errno == errno.EAGAIN:
                #print "again!"
                return True
            raise
        self.output += data
        return True

    def on_complete(self):
        pass

    def on_finish_writing(self):
        pass

    def terminate(self):
        try:
            self.dead = True
            os.kill(self.process.pid,signal.SIGKILL)
        except OSError, err:
            if err.errno == errno.ESRCH:
                # already dead
                return
            raise

import gtk
import gobject

class GTKSlave(gobject.GObject,Slave):
    __gsignals__ = {
        'operation-complete' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'progress-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_STRING, gobject.TYPE_FLOAT))
        }

    def __init__(self, cmd, *args):
        gobject.GObject.__init__(self)
        Slave.__init__(self,cmd,*args)
        self.write_id = None
        self.read_id = None

    def on_finish_writing(self):
        if self.write_id:
            #print "unreg write"
            gtk.input_remove(self.write_id)
            self.write_id = None
            
    def on_readable(self, source, condition):        
        #print "readable:", source, condition
        self.emit('progress-changed', "Reading", -1.0)
        self.read()
        return True

    def on_writable(self, source, condition):
        #print "writable:",source,condition
        self.write()
        self.emit('progress-changed', "Writing",
                  (self.in_pos+1.0)/(len(self.input)+1))
        return True

    def on_complete(self):
        if self.read_id:
            #print "unreg read"
            gtk.input_remove(self.read_id)
            self.read_id = None
        self.emit('progress-changed', "Done",0.0)
        self.emit('operation-complete')
            
    def run(self,input):
        Slave.run(self,input)

        self.write_id = gtk.input_add(
            self.stdin, gtk.gdk.INPUT_WRITE, self.on_writable)
        self.read_id = gtk.input_add(
            self.stdout, gtk.gdk.INPUT_READ, self.on_readable)

gobject.type_register(GTKSlave)
