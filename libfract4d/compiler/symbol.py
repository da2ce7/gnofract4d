#!/usr/bin/env python

# Trivial symbol table implementation
from fracttypes import *
import copy
from UserDict import UserDict
import string
import types
import re

def efl(template, tlist):
    'short-hand for expandFuncList - just reduces the amount of finger-typing'
    list = []
    for t in tlist:
        f = "Func(%s)" % re.sub("_", str(t), template)
        list.append(eval(f))
    return list
    
def createDefaultDict():
    d = {
        # standard library functions
        
        "sqr": efl("[_] , _",  [Int, Float, Complex]),
        
        # standard operators

        # comparison
        "!=": efl("[_,_] , Bool", [Int, Float, Complex, Bool]),
        "==": efl("[_,_] , Bool", [Int, Float, Complex, Bool]),
        
        # fixme - issue a warning for complex compares
        ">":  efl("[_,_] , Bool", [Int, Float, Complex]),
        ">=": efl("[_,_] , Bool", [Int, Float, Complex]),
        "<":  efl("[_,_] , Bool", [Int, Float, Complex]),
        "<=": efl("[_,_] , Bool", [Int, Float, Complex]),

        # arithmetic
        "%":  efl("[_,_] , _", [Int, Float]),
        "/":  efl("[_,_] , _", [Float, Complex]) + \
              [ Func([Color, Float], Float)],
        "*":  efl("[_,_] , _", [Int, Float, Complex]) + \
              [ Func([Color, Float], Float)],
        "+":  efl("[_,_] , _", [Int, Float, Complex, Color]),
        "-":  efl("[_,_] , _", [Int, Float, Complex, Color]),
        "^":  efl("[_,_] , _", [Float, Complex]),
        "mag":[ Func([Complex], Float)],
        
        # unary negation already factored out

        # logical ops
        "&&": Func([Bool, Bool], Bool),
        "||": Func([Bool, Bool], Bool),
        "!" : Func([Bool],Bool),
        
        "#pixel": Var(Complex,0.0), # fixme, value 
        "#z" : Var(Complex,0.0),
        "z"  : Var(Complex,0.0) # same as #z
        }
    return d


def mangle(k):
    return string.lower(k)
               
class T(UserDict):
    default_dict = createDefaultDict()
    def __init__(self):
        UserDict.__init__(self)
        self.reset()
        self.nextlabel = 0
        
    def has_key(self,key):
        return self.data.has_key(mangle(key))

    def is_user(self,key):
        return not self.data[mangle(key)].pos == -1
    
    def __getitem__(self,key):
        return self.data[mangle(key)]
    def __setitem__(self,key,value):
        k = mangle(key)
        if self.data.has_key(k):
            if T.default_dict.has_key(k):
                msg = "is predefined"
            else:
                l = self.data[k].pos
                msg = ("was already defined on line %d" % l)
            
            raise KeyError, ("symbol '%s' %s" % (key,msg))

        self.data[mangle(key)] = value
    def __delitem__(self,key):
        del self.data[mangle(key)]
        
    def reset(self):
        self.data = copy.deepcopy(T.default_dict)

    def newLabel(self):
        label = "label%d" % self.nextlabel
        self.nextlabel += 1
        return label

    
