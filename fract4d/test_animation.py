#!/usr/bin/env python

# test director bean class implementation

import unittest
import sys

import animation, fractal, fc

# centralized to speed up tests
g_comp = fc.Compiler()
g_comp.file_path.append("../formulas")
g_comp.load_formula_file("gf4d.frm")
g_comp.load_formula_file("test.frm")
g_comp.load_formula_file("gf4d.cfrm")

class Test(unittest.TestCase):
    def setUp(self):
        self.anim = animation.T(g_comp)

    def tearDown(self):
        pass

    def testDefault(self):
        self.assertEqual(self.anim.get_avi_file(),"")
        self.assertEqual(self.anim.get_width(),640)
        self.assertEqual(self.anim.get_height(),480)
        self.assertEqual(self.anim.get_framerate(),25)
        self.assertEqual(self.anim.get_redblue(),True)
        self.assertEqual(self.anim.keyframes_count(),0)

    def testChangeOptions(self):
        filename="/testing/test.fct"
        dirname="/testing"
        number=300
        #avi file
        self.anim.set_avi_file(filename)
        self.assertEqual(self.anim.get_avi_file(),filename)
        #width
        self.anim.set_width(number)
        self.assertEqual(self.anim.get_width(),number)
        #height
        self.anim.set_height(number)
        self.assertEqual(self.anim.get_height(),number)
        #framerate
        number=28
        self.anim.set_framerate(number)
        self.assertEqual(self.anim.get_framerate(),number)
        #reedblue
        self.anim.set_redblue(False)
        self.assertEqual(self.anim.get_redblue(),False)
        #test for count still 0
        self.assertEqual(self.anim.keyframes_count(),0)

    def testKeyframes(self):
        filename="/testing/test.fct"
        duration=10
        stop=5
        int_type=animation.INT_LOG
        #test adding
        self.anim.add_keyframe(filename,duration,stop,int_type)
        self.assertEqual(self.anim.keyframes_count(),1)
        self.assertEqual(self.anim.get_keyframe_filename(0),filename)
        self.assertEqual(self.anim.get_keyframe_duration(0),duration)
        self.assertEqual(self.anim.get_keyframe_stop(0),stop)
        self.assertEqual(self.anim.get_keyframe_int(0),int_type)
        self.assertEqual(len(self.anim.get_directions(0)),6)
        #test changing one by one
        filename2="/testing/test2.fct"
        duration2=20
        stop2=10
        int_type2=animation.INT_INVLOG

        self.anim.set_keyframe_duration(0,duration2)
        self.assertEqual(self.anim.get_keyframe_duration(0),duration2)
        self.anim.set_keyframe_stop(0,stop2)
        self.assertEqual(self.anim.get_keyframe_stop(0),stop2)
        self.anim.set_keyframe_int(0,int_type2)
        self.assertEqual(self.anim.get_keyframe_int(0),int_type2)
        #test changing whole
        self.anim.change_keyframe(0,duration,stop,int_type)
        self.assertEqual(self.anim.get_keyframe_duration(0),duration)
        self.assertEqual(self.anim.get_keyframe_stop(0),stop)
        self.assertEqual(self.anim.get_keyframe_int(0),int_type)
        #test adding new
        self.anim.add_keyframe(filename2,duration2,stop2,int_type2)
        self.assertEqual(self.anim.keyframes_count(),2)
        #test deleting
        self.anim.remove_keyframe(1)
        self.assertEqual(self.anim.keyframes_count(),1)
        self.anim.remove_keyframe(0)
        self.assertEqual(self.anim.keyframes_count(),0)

    def testLoading(self):
        result=self.anim.load_animation("../testdata/animation.fcta")
        #keyframes
        self.assertEqual(self.anim.keyframes_count(),2)
        self.assertEqual(self.anim.get_keyframe_filename(0),"kf1")
        self.assertEqual(self.anim.get_keyframe_duration(0),10)
        self.assertEqual(self.anim.get_keyframe_stop(0),10)
        self.assertEqual(self.anim.get_keyframe_int(0),0)
        self.assertEqual(self.anim.get_keyframe_filename(1),"kf2")
        self.assertEqual(self.anim.get_keyframe_duration(1),20)
        self.assertEqual(self.anim.get_keyframe_stop(1),20)
        self.assertEqual(self.anim.get_keyframe_int(1),1)
        #output stuff
        self.assertEqual(self.anim.get_avi_file(),u"output.avi")
        self.assertEqual(self.anim.get_framerate(),28)
        self.assertEqual(self.anim.get_width(),320)
        self.assertEqual(self.anim.get_height(),240)
        self.assertEqual(self.anim.get_redblue(),False)

    def testCreateList(self):
        self.anim.add_keyframe("f1.fct", 10, 4, animation.INT_LOG)
	self.anim.add_keyframe("f2.fct", 6, 3, animation.INT_LOG)
	list = self.anim.create_list()

	self.assertEqual(17, len(list))
	# starts with 4 identical frames
	self.assertEqual(["/tmp/image_0000000.png"] * 4, list[0:4])
	# then a sequence of 10 changing frames
	self.assertEqual(["/tmp/image_%07d.png" % n for n in range(1,11)], list[4:14])
	# then 3 more unchanging frames
	self.assertEqual(["/tmp/image_0000010.png"] * 3, list[14:17])

    def testFilenames(self):
        self.assertEqual(
		"/tmp/image_0000037.png",
		self.anim.get_image_filename(37))

	self.assertEqual(
		"/tmp/file_0000064.fct",
		self.anim.get_fractal_filename(64))

    def testMu(self):
        for x in xrange(animation.INT_LINEAR, animation.INT_COS+1):
		# for all interpolation types, 0 -> 0 and 1.0 -> 1.0
		self.assertEqual(0.0, self.anim.get_mu(x, 0.0))
		self.assertEqual(1.0, self.anim.get_mu(x, 1.0))

	# different results for internal points
	self.assertEqual(0.5, self.anim.get_mu(animation.INT_LINEAR, 0.5))
	self.assertEqual(0.58496250072115619, self.anim.get_mu(animation.INT_LOG, 0.5))
	self.assertEqual(0.37754066879814552, self.anim.get_mu(animation.INT_INVLOG, 0.5))
	self.assertEqual(0.49999999999999994, self.anim.get_mu(animation.INT_COS, 0.5))

	self.assertRaises(ValueError, self.anim.get_mu,83, 0.6)
	
    def testFindValues(self):
        f = fractal.T(g_comp)
	f.loadFctFile(open("../testdata/chainsoflight.fct"))
        vals = self.anim.find_values(f)
	self.assertEqual(
		[-692.29926383912390975,
		 84.20938258550194178,
		 0.00000000000000000,
		 0.00000000000000000,
		 708.66008038696850235,
		 -0.34249284178074824,
		 0.00000000000000000,
		 0.00000000000000000,
		 0.00000000000000000,
		 0.00000000000000000,
		 0.00000000000000000,
		 {"@p1" : (0.66253178213589414,-0.22238807443609804)}],
		vals)

    def testGetKeyframeValues(self):
        self.anim.add_keyframe("../testdata/director1.fct", 10, 0, animation.INT_LINEAR)
	self.anim.add_keyframe("../testdata/director2.fct", 5, 0, animation.INT_LINEAR)

	(values, durations ) = self.anim.get_keyframe_values()

	self.assertEqual(2,len(values))
	self.assertEqual(
		[0.0] * 4 + [4.0] + [0.0] * 6  + [ { "@bailout" : (4.0,) }],
		values[0])

	self.assertEqual(
		[-0.121875, 0.94999999999999996, 0.0, 0.0, 0.46875,
		 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, {'@bailout': (4.0,)}],
		values[1])

	self.assertEqual([10,5], durations)
			
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
