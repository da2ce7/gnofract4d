#!/usr/bin/env python

# Subclass of fract4d.fractal.T which works with a GUI

import sys
import os
import struct
import math

import gtk
import gobject

# so we can run without installing.
# FIXME is there a better way?
sys.path.append("..")

from fract4d import fractal,fract4dc

class Threaded(fractal.T):
    def __init__(self,comp):
        (r,w) = os.pipe()
        self.readfd = r
        s = fract4dc.fdsite_create(w)
        fractal.T.__init__(self,comp,s)
        self.msgformat = "5i"
        self.msgsize = struct.calcsize(self.msgformat)

        self.name_of_msg = [
            "PARAMS",
            "IMAGE",
            "PROGRESS",
            "STATUS",
            "PIXEL"
            ]

        self.skip_updates = False
        self.running = False

    def interrupt(self):
        if self.skip_updates:
            #print "skip recursive interrupt"
            return
        
        self.skip_updates = True
        
        fract4dc.interrupt(self.site)

        n = 0
        # wait for stream from worker to flush
        while self.running:
            n += 1
            gtk.main_iteration(True)

        self.skip_updates = False
        
    def draw(self,image):
        self.cmap = fract4dc.cmap_create(self.colorlist)

        #print "draw: init with %s" % self.initparams
        fract4dc.pf_init(self.pfunc,0.001,self.initparams)

        self.running = True
        fract4dc.async_calc(self.params,self.antialias,self.maxiter,1,
                           self.pfunc,self.cmap,1,image,self.site)

    def onData(self,fd,condition):
        bytes = os.read(fd,self.msgsize)
        if len(bytes) < self.msgsize:
            print "bad message: %s" % list(bytes)
            return

        (t,p1,p2,p3,p4) = struct.unpack("5i",bytes)
        m = self.name_of_msg[t] 
        #print "msg: %s %d %d %d %d" % (m,p1,p2,p3,p4)
        if t == 0:
            if not self.skip_updates: self.iters_changed(p1)
        elif t == 1:
            if not self.skip_updates: self.image_changed(p1,p2,p3,p4)
        elif t == 2:
            if not self.skip_updates: self.progress_changed(float(p1))
        elif t == 3:
            if p1 == 0: # DONE
                self.running = False
            if not self.skip_updates: self.status_changed(p1)
        elif t == 4:
            # FIXME pixel_changed
            pass
        else:
            raise Exception("Unknown message from fractal thread")

class T(Threaded,gobject.GObject):
    __gsignals__ = {
        'parameters-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, ()),
        'status-changed' : (
        (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_NO_RECURSE),
        gobject.TYPE_NONE, (gobject.TYPE_INT,))
        }

    def __init__(self,comp):
        gobject.GObject.__init__(self) # MUST be called before threaded.init

        Threaded.__init__(self,comp)
        gtk.input_add(self.readfd, gtk.gdk.INPUT_READ, self.onData)
        
        self.width = 640
        self.height = 480
        self.image = fract4dc.image_create(self.width,self.height)

        drawing_area = gtk.DrawingArea()
        drawing_area.add_events(gtk.gdk.BUTTON_RELEASE_MASK |
                                gtk.gdk.BUTTON1_MOTION_MASK |
                                gtk.gdk.POINTER_MOTION_HINT_MASK |
                                gtk.gdk.BUTTON_PRESS_MASK)
        
        drawing_area.connect('motion_notify_event', self.onMotionNotify)
        drawing_area.connect('button_release_event', self.onButtonRelease)
        drawing_area.connect('button_press_event', self.onButtonPress)
        drawing_area.connect('expose_event',self.onExpose)
        
        c = gtk.gdk.rgb_get_cmap()
        drawing_area.set_colormap(c)        
        drawing_area.set_size_request(self.width,self.height)

        self.widget = drawing_area
        self.compile()

    def reset(self):
        fractal.T.reset(self)
        self.emit('parameters-changed')
        
    def draw_image(self):
        self.interrupt()
        self.draw(self.image)
        return gtk.FALSE

    def set_param(self,n,val):
        #print "set param: %s %s" % (n, val)
        val = float(val)
        if self.params[n] != val:
            self.params[n] = val
            self.emit('parameters-changed')

    def status_changed(self,status):
        fractal.T.status_changed(self,status)
        self.emit('status-changed',status)
        
    def iters_changed(self,n):
        fractal.T.iters_changed(self,n)
        
    def image_changed(self,x1,y1,x2,y2):
        self.redraw_rect(x1,y1,x2-x1,y2-y1)

    def onExpose(self,widget,exposeEvent):
        r = exposeEvent.area
        self.redraw_rect(r.x,r.y,r.width,r.height)

    def onMotionNotify(self,widget,event):
        (self.newx,self.newy) = (event.x, event.y)

        #print "omn(%d,%d,%d,%d)" % (self.x, self.y, self.newx,self.newy)
        
        dummy = widget.window.get_pointer()
        self.redraw_rect(0,0,self.width,self.height)

        dy = int(abs(self.newx - self.x) * float(self.height)/self.width)
        if(self.newy < self.y or (self.newy == self.y and self.newx < self.x)):
            dy = -dy
        self.newy = self.y + dy;

        widget.window.draw_rectangle(
            self.widget.get_style().white_gc,
            gtk.FALSE,
            min(self.x,self.newx),
            min(self.y,self.newy),
            abs(self.newx-self.x), abs(self.newy-self.y));

    def onButtonPress(self,widget,event):
        self.x = event.x
        self.y = event.y
        self.newx = self.x
        self.newy = self.y
        
    def onButtonRelease(self,widget,event):
        self.redraw_rect(0,0,self.width,self.height)
        if event.button == 1:
            if self.x == self.newx or self.y == self.newy:
                zoom=0.5
                x = self.x
                y = self.y
            else:
                zoom= (1+abs(self.x - self.newx))/float(self.width)
                #print "pixz: %d" % (1+abs(self.x - self.newx))
                x = 0.5 + (self.x + self.newx)/2.0;
                y = 0.5 + (self.y + self.newy)/2.0;
                
            #print "xyz: (%f,%f,%f)" % (x, y, zoom)
            
        elif event.button == 2:
            (x,y) = (event.x, event.y)
            zoom = 1.0
            self.flip_to_julia()
        else:
            (x,y) = (event.x, event.y)
            zoom = 2.0
            
        #print "click (%d,%d)" % (event.x, event.y)
        self.recenter(x,y,zoom)

    def recenter(self,x,y,zoom):
        dx = (x - self.width/2.0)/self.width
        dy = (y - self.height/2.0)/self.width
        self.relocate(dx,dy,zoom)
        self.emit('parameters-changed')
        
    def redraw_rect(self,x,y,w,h):
        gc = self.widget.get_style().white_gc

        buf = fract4dc.image_buffer(self.image,x,y)
        if self.widget.window:
            self.widget.window.draw_rgb_image(
                gc,
                x, y,
                min(self.width-x,w),
                min(self.height-y,h),
                gtk.gdk.RGB_DITHER_NONE,
                buf,
                self.width*3)

gobject.type_register(T)
