#!/usr/bin/env python

# test symbol table implementation

import symbol
import unittest
from fracttypes import *

class SymbolTest(unittest.TestCase):
    def setUp(self):
        self.t = symbol.T()

    def tearDown(self):
        pass

    def testPrefix(self):
        t = symbol.T("boo")
        v = Var(Int,1)
        t["x"] = v
        self.assertEqual(t["x"].cname,"boox")
        
    def testSqr(self):
        sqr_c = self.t[("sqr")][2];
        sqr_i = self.t[("sqR")][0];
        self.failUnless(isinstance(sqr_c, Func) and sqr_c.ret == Complex)
        self.failUnless(isinstance(sqr_i, Func) and sqr_i.args == [Int])

    def testNoOverride(self):
        self.assertRaises(KeyError,self.t.__setitem__,("sqr"),1)
        
    def testAddCheckVar(self):
        self.t["fish"] = Var(Int,1)
        self.failUnless(self.t.has_key("fish"))
        self.failUnless(self.t.has_key("FisH"))
        x = self.t["fish"]
        self.failUnless(isinstance(x,Var) and x.value == 1 and x.type == Int)

    def test_user(self):
        self.t["fish"] = Var(Int,1,1)
        self.failUnless(self.t.is_user("fish"))
        self.failUnless(not self.t.is_user("z"))

    def test_expand(self):
        l = symbol.efl("foo", "[_,_] , _", [Int, Float, Complex])
        self.assertEqual(len(l),3)
        self.assertEqual(l[0].ret, Int)
        self.assertEqual(l[1].args, [Float,Float])

    def test_matches(self):
        times = self.t["*"]
        times_i = times[0]
        self.failUnless(times_i.matchesArgs([Int,Int]))
        self.failUnless(times_i.matchesArgs([Int,Bool]))
        self.failUnless(not times_i.matchesArgs([Int,Color]))

    def test_clash_with_secret_vars(self):
        self.assertRaises(KeyError, self.t.__setitem__, ("t__temp0"), 1)

    def testStartsWithHash(self):
        self.assertRaises(KeyError,self.t.__setitem__,"#wombat",1)

    def testAt(self):
        self.t["@foo"] = Var(Int, 1, 0)
        self.assertEqual(self.t.realName("@foo"), "t__a_foo")

    def testCName(self):
        self.t["bar"] = Var(Int,1,0)
        self.assertEqual(self.t["bAr"].cname,"bar")
        v = Var(Int,1,0)
        v.cname = "fish"
        self.t["var_with_name"] = v
        self.assertEqual(self.t["var_with_name"].cname,"fish")
        self.assertEqual(self.t["cos"][0].cname,"cos")
        
    def testZ(self):
        self.assertEqual(self.t["z"].type, Complex)

    def testAlias(self):
        self.assertEqual(self.t["#z"], self.t["z"])

    def testParams(self):
        self.assertEqual(self.t["@p6"].type, Complex)
        self.assertEqual(self.t["@p1"], self.t["p1"])
        self.assertEqual(self.t["@fn1"][0].ret, Complex)
                         
    def testReset(self):
        self.t["fish"] = Var(Int, 1, 1)
        self.t.reset()
        self.assertRaises(KeyError, self.t.__getitem__, ("fish"))
        
def suite():
    return unittest.makeSuite(SymbolTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
