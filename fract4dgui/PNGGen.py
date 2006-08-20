#UI and logic for generation PNG images
#It gets all information from director bean class, gets all values, and,
#in special thread, while it finds in-between values it call gtkfractal.HighResolution
#to create images

from __future__ import generators

import gtk
import gobject
import re
import math
import sys
import os
from threading import *

import gtkfractal, hig
from fract4d import fractal,fracttypes, animation

running=False
thread_error=False

class PNGGeneration(gtk.Dialog,hig.MessagePopper):
    def __init__(self,animation,compiler):
        gtk.Dialog.__init__(self,
            "Generating images...",None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            (gtk.STOCK_CANCEL,gtk.RESPONSE_CANCEL))

        hig.MessagePopper.__init__(self)
        self.lbl_image=gtk.Label("Current image progress")
        self.vbox.pack_start(self.lbl_image,True,True,0)
        self.pbar_image = gtk.ProgressBar()
        self.vbox.pack_start(self.pbar_image,True,True,0)
        self.lbl_overall=gtk.Label("Overall progress")
        self.vbox.pack_start(self.lbl_overall,True,True,0)
        self.pbar_overall = gtk.ProgressBar()
        self.vbox.pack_start(self.pbar_overall,True,True,0)
        self.set_geometry_hints(None,min_aspect=3.5,max_aspect=3.5)
        self.anim=animation

        #-------------loads compiler----------------------------
        self.compiler=compiler

    def generate_png(self):
        global running
        durations=[]

        #--------find values and duration from all keyframes------------
        try:
	   durations = self.anim.get_keyframe_durations()
        except Exception, err:
            self.show_error(_("Error processing keyframes"), str(err))
            yield False
            return

        #---------------------------------------------------------------
        create_all_images=self.to_create_images_again()
        gt=GenerationThread(
            durations,self.anim,
            self.compiler,
            create_all_images,self.pbar_image,self.pbar_overall)
        gt.start()
        working=True
        while(working):
            gt.join(1)
            working=gt.isAlive()
            yield True

        if thread_error==True:
            self.show_error("Error during image generation", "Unknown")
            yield False
            return


        if running==False:
            yield False
            return
        running=False
        self.destroy()
        yield False
    
    def to_create_images_again(self):
        create = True
        filelist = self.anim.create_list()
	for f in filelist:		
            if os.path.exists(f):
                gtk.threads_enter()
                try:
		    folder_png = self.anim.get_png_dir()
                    response = self.ask_question(
                        _("The temporary directory: %s already contains at least one image" % folder_png),
                        _("Use them to speed up generation?"))

                except Exception, err:
                    print err
		    gtk.threads_leave()
                    raise

		gtk.threads_leave()
		    
                if response==gtk.RESPONSE_ACCEPT:
                    create=False
                else:
                    create=True
                return create

        return create

    def show_error(self,message,secondary):
        running=False
        self.error=True
        gtk.threads_enter()
        error_dlg = hig.ErrorAlert(
            parent=self,
            primary=message,
            secondary=secondary)
        error_dlg.run()
        error_dlg.destroy()
        gtk.threads_leave()
        event = gtk.gdk.Event(gtk.gdk.DELETE)
        self.emit('delete_event', event)

    def show(self):
        global running
        self.show_all()
        running=True
        self.error=False
        task=self.generate_png()
        gobject.idle_add(task.next)
        response = self.run()
        if response != gtk.RESPONSE_CANCEL:
            if running==True: #destroy by user
                running=False
                self.destroy()
                return 1
            else:
                if self.error==True: #error
                    self.destroy()
                    return -1
                else: #everything ok
                    self.destroy()
                    return 0
        else: #cancel pressed
            running=False
            self.destroy()
            return 1

#thread to interpolate values and calls generation of .png files
class GenerationThread(Thread):
    def __init__(
        self,durations,animation,compiler,
        create_all_images,pbar_image,pbar_overall):
        Thread.__init__(self)
        self.durations=durations
        self.anim=animation
        self.create_all_images=create_all_images
        self.pbar_image=pbar_image
        self.pbar_overall=pbar_overall
        #initializing progress bars
        self.pbar_image.set_fraction(0)
        self.pbar_overall.set_fraction(0)
        self.pbar_overall.set_text("0/"+str(sum(self.durations)+1))
        self.compiler=compiler

	self.current = gtkfractal.HighResolution(
		compiler,
		int(self.anim.get_width()),int(self.anim.get_height()))

	self.current.connect('status-changed', self.onStatusChanged)
	self.current.connect('progress-changed', self.onProgressChanged)

        #semaphore to signalize that image generation is finished
        self.next_image=Semaphore(1)

    def onProgressChanged(self,f,progress):
        global running
        if running:
            self.pbar_image.set_fraction(progress/100.0)

    #one image generation complete - tell (with "semaphore" self.next_image) we can continue
    def onStatusChanged(self,f,status_val):
        if status_val == 0:
            #release semaphore
            self.next_image.release()

    def run(self):
        global thread_error,running
        import traceback
        try:
            #first generates image from base keyframe
            self.generate_base_keyframe()
            #pass through all keyframes and generates inter images
            for i in range(self.anim.keyframes_count()-1):
                self.generate_images(i)
                if running==False:
                    return
            #wait for last image to finish rendering
            self.next_image.acquire()
            #generate list file
            list = self.anim.create_list()
	    lfilename = os.path.join(self.anim.get_png_dir(), "list")
	    lfile = open(lfilename,"w")
	    print >>lfile, "\n".join(list)
	    lfile.close()
	    
        except:
            traceback.print_exc()
            thread_error=True
            running=False
            return


    def generate_base_keyframe(self):
        f=fractal.T(self.compiler)
        f.loadFctFile(open(self.anim.get_keyframe_filename(0)))

        self.next_image.acquire()
        #writes .fct file if user wanted that
        if self.anim.get_fct_enabled():
            f.save(open(self.anim.get_fractal_filename(0),"w"))
        #check if image already exist and user wants to leave it or not
        if not(os.path.exists(self.anim.get_image_filename(0)) and self.create_all_images==False): #check if image already exist
            self.current.set_fractal(f)
	    self.current.reset_render()
            self.current.draw_image(self.anim.get_image_filename(0))
        else:
            #just release semaphore
            self.next_image.release()
        return

    #main method for generating images
    #it generates images between iteration-th-1 and iteration-th keyframe
    #first, it gets border values (keyframe values)
    #(values - x,y,z,w,size,angles,formula parameters)
    #then, in a loop, it generates inter values, fill fractal class with it and
    #calls gtkfractal.HighResolution to generate images
    def generate_images(self,iteration):
        global running
        #sum of all frames, needed for padding output files
        sumN=sum(self.durations)
        lenN=len(str(sumN))
        #number of images already generated
        sumBefore=sum(self.durations[0:iteration])
        #current duration
        N=self.durations[iteration]

        f_prev=fractal.T(self.compiler)
        f_prev.loadFctFile(open(self.anim.get_keyframe_filename(iteration)))

	f_next=fractal.T(self.compiler)
	f_next.loadFctFile(open(self.anim.get_keyframe_filename(iteration+1)))
	
        #------------------------------------------------------------
        #loop to generate images between current (iteration-th) and previous keyframe
        for i in range(1,N+1):
            #but, first, wait for previous image to finish rendering
            self.next_image.acquire()
            #check if user canceled us
            if running==False:
                return
            #update progress bar
            percent=float((sumBefore+i))/(sumN+1)
            self.pbar_overall.set_fraction(percent)
            self.pbar_overall.set_text(str(sumBefore+i)+"/"+str(sumN+1))

            # create a blended fractal partway between prev and next keyframe
	    int_type=self.anim.get_keyframe_int(iteration)
            mu=self.anim.get_mu(int_type, float(i)/float(N))
            f_frame = f_prev.blend(f_next,mu)

            #writes .fct file if user wanted that
            if self.anim.get_fct_enabled():
                f_frame.save(open(self.anim.get_fractal_filename(sumBefore+i),"w"))

            #check if image already exist and user wants to leave it or not
            if not(os.path.exists(self.anim.get_image_filename(sumBefore+i)) and self.create_all_images==False): #check if image already exist
                self.current.set_fractal(f_frame)
		self.current.reset_render()
                self.current.draw_image(self.anim.get_image_filename(sumBefore+i))
            else:
                #just release semaphore
                self.next_image.release()
        return
