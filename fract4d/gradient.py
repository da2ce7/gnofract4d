#!/usr/bin/env python

#Class definition for Gradients

#These two are SHTOLEN from libgimpcolor/gimpcolorspace.c
def RGBtoHSV(rgb):
	trgb = rgb
	trgb.sort
	max = trgb[0]
	min = trgb[2]
	delta = max - min

	hsv[2]=max
	if delta > 0:
		hsv[1]=max/delta
		if rgb[0] == max:
			hsv[0] = (rgb[1] - rgb[2]) / delta
			if hsv[0] < 0.0:
				hsv[0] += 6.0
			elif rgb[1] == max:
				hsv[0] = 2.0 + (rgb[2] - rgb[0]) / delta
			elif rgb[2] == max:
				hsv[0] = 4.0 + (rgb[0] - rgb[1]) / delta

		hsv[0] /= 6.0
	else:
		hsv[0] = 0.0
		hsv[1] = 0.0
		
	return hsv

def HSVtoRGB(hsv):
	rgb=[0,0,0]
	hsv=[hsv[0]/255,hsv[1]/255,hsv[2]/255]
	if hsv[1] == 0.0:
		rgb=[hsv[2],hsv[2],hsv[2]]
	else:
		hue = hsv[0]

		if hue == 1.0:
			hue = 0.0

		hue *= 6.0

		i = int(hue)
		f = hue - i
		w = hsv[2] * (1.0 - hsv[1])
		q = hsv[2] * (1.0 - (hsv[1] * f))
		t = hsv[2] * (1.0 - (hsv[1] * (1.0 - f)))
		
		#I'll be buggered if I know why this works
		if i == 0:
			rgb[0] = hsv[2]
			rgb[1] = t
			rgb[2] = w
		elif i == 1:
			rgb[0] = q
			rgb[1] = hsv[2]
			rgb[2] = w
		elif i == 2:
			rgb[0] = w
			rgb[1] = hsv[2]
			rgb[2] = t
		elif i == 3:
			rgb[0] = w
			rgb[1] = q
			rgb[2] = hsv[2]
		elif i == 4:
			rgb[0] = t
			rgb[1] = w
			rgb[2] = hsv[2]
		elif i == 5:
			rgb[0] = hsv[2]
			rgb[1] = w
			rgb[2] = q
			
	rgb=[rgb[0]*255,rgb[1]*255,rgb[2]*255]
			
	return rgb

class Gradient:
	def __init__(self):
		self.first=[255,0,255]
		self.handles=[	['HSV','Linear', [.5,[0, 255, 255]]],
						['HSV','Linear', [1, [255, 0, 255]]]]
		
		#Key:	Colouring mode, Blending mode, [position [R|H, G|S, B|V]]
		#Possibly add option for midpoint
		
		self.num=255
		self.detail=1.0/self.num
		self.alternating=.333
		
	def compute(self):
		clist=[]; i=0; alt=0
		while i < 1:
			ialt=i+alt
			if ialt > 1:
				ialt-=1.0
			col=self.getColourAt(ialt)
			clist.append((i,
						 int(col[0]),
						 int(col[1]),
						 int(col[2]),
						 255))
			i += self.detail
			alt+=self.alternating
			if alt > 1:
				alt-=1.0
							
		self.clist = clist
			
	def getColourAt(self, pos):
		#Clever stuff is shtolen from gimp/app/core/gimpgradient.c
		seg = self.getSegAt(pos)
		
		if seg == 0:
			s_lpos = 0
			s_lcol = self.first
		else:
			s_lpos = self.handles[seg-1][2][0]
			s_lcol = self.handles[seg-1][2][1]
		
		s_rpos = self.handles[seg][2][0]
		s_rcol = self.handles[seg][2][1]
		
		cmode = self.handles[seg][0]
		bmode = self.handles[seg][1]
		s_len = s_rpos-s_lpos
		
		#Uncomment the following when we've implemented movable middle handles
		#s_mpos = (.5 - s_lpos) / s_len
		s_mpos = 0.5
		pos    = (pos- s_lpos) / s_len
		
		if bmode == 'Linear':
			factor = self.getLinearFactor(pos, s_mpos)
		else:
			factor = self.getCurvedFactor(pos, s_mpos)
		
		#Assume RGB mode, for the moment
		RH = s_lcol[0] + (s_rcol[0] - s_lcol[0]) * factor
		GS = s_lcol[1] + (s_rcol[1] - s_lcol[1]) * factor
		BV = s_lcol[2] + (s_rcol[2] - s_lcol[2]) * factor

		if cmode == 'RGB':
			return [RH, GS, BV]
		else:
			return HSVtoRGB([RH,GS,BV])
		
	#Obtains the first handle to the right of pos
	#Essentially, we obtain the segment of gradient in which pos resides.
	def getSegAt(self, pos):
		for seg in self.handles:
			if pos <= seg[2][0]:
				return self.handles.index(seg)
	
	def getLinearFactor(self, pos, middle):
		if pos <= middle:
			return 0.5 * pos / middle
		else:
			pos -= middle;
			middle = 1.0 - middle
			return 0.5 + 0.5 * pos / middle
		
	def getCurvedFactor(self, pos, middle):
		return pos**( log(0.5) / log(middle) )
		
	def getCList(self):
		return self.clist