#!/usr/bin/env python

# test types which are used by formula authors

import fracttypes
import unittest

class Test(unittest.TestCase):
    def testTypeCtor(self):
        c = fracttypes.Type(
            id=72,
            suffix="i", printf="%d", typename="int",
            default=0, slots=1, cname="int")

        self.assertEqual("i",c.suffix)

    def testTypes(self):
        self.assertEqual(
            "bool",
            fracttypes.typeObjectList[fracttypes.Bool].typename)

        self.assertEqual(
            "int",
            fracttypes.typeObjectList[fracttypes.Int].typename)

        self.assertEqual(
            "float",
            fracttypes.typeObjectList[fracttypes.Float].typename)

        self.assertEqual(
            "complex",
            fracttypes.typeObjectList[fracttypes.Complex].typename)

        self.assertEqual(
            "color",
            fracttypes.typeObjectList[fracttypes.Color].typename)

        self.assertEqual(
            "string",
            fracttypes.typeObjectList[fracttypes.String].typename)

        self.assertEqual(
            "hyper",
            fracttypes.typeObjectList[fracttypes.Hyper].typename)

        self.assertEqual(
            "gradient",
            fracttypes.typeObjectList[fracttypes.Gradient].typename)

    def testTypeIDs(self):
        for i in xrange(len(fracttypes.typeObjectList)):
            self.assertEqual(i,fracttypes.typeObjectList[i].typeid)
            
    def testPrintfOfType(self):
        self.assertEqual(
            "%d", fracttypes.typeObjectList[fracttypes.Bool].printf)
        self.assertEqual(
            "%d", fracttypes.typeObjectList[fracttypes.Int].printf)
        self.assertEqual(
            "%g", fracttypes.typeObjectList[fracttypes.Float].printf)
        self.assertEqual(
            None, fracttypes.typeObjectList[fracttypes.String].printf)

    def testCType(self):
        expected =  {
            fracttypes.Int : "int",
            fracttypes.Float : "double",
            fracttypes.Complex : "double",
            fracttypes.Hyper : "double",
            fracttypes.Bool : "int",
            fracttypes.Color : "double",
            fracttypes.String : "<Error>",
            fracttypes.Gradient : "void *"
            }

        for (k,v) in expected.items():            
            self.assertEqual(v,fracttypes.typeObjectList[k].cname)

    def testFloatInitVal(self):
        float_type = fracttypes.typeObjectList[fracttypes.Float]
        v = fracttypes.Var(fracttypes.Float,1.234)
        
        self.assertEqual(["1.23399999999999999"],float_type.init_val(v))
        self.assertEqual(["1.23399999999999999"],v.init_val())
        
        v.param_slot = 3
        self.assertEqual(["t__pfo->p[3].doubleval"],float_type.init_val(v))
        self.assertEqual(["t__pfo->p[3].doubleval"],v.init_val())

    def testPartNames(self):
        v = fracttypes.Var(fracttypes.Float)
        self.assertEqual([""], v.part_names)

        v = fracttypes.Var(fracttypes.Complex)
        self.assertEqual(["_re","_im"], v.part_names)

        v = fracttypes.Var(fracttypes.Color)
        self.assertEqual(["_re","_i","_j","_k"], v.part_names)

    def testComplexInitVal(self):
        v = fracttypes.Var(fracttypes.Complex, [1.234,-7.89])
        
        self.assertEqual(
            ["1.23399999999999999","-7.88999999999999968"],
            v.init_val())
        
        v.param_slot = 3
        self.assertEqual(
            ["t__pfo->p[3].doubleval","t__pfo->p[4].doubleval"],
            v.init_val())

    def testGradientInitVal(self):
        v = fracttypes.Var(fracttypes.Gradient, 0)
        self.assertRaises(fracttypes.TranslationError,v.init_val)

        v.param_slot = 3
        self.assertEqual(["t__pfo->p[3].gradient"], v.init_val())
        
    def testIntInitVal(self):
        v = fracttypes.Var(fracttypes.Int, 1)
        self.checkIntInitVal(v)

    def testBoolInitVal(self):
        v = fracttypes.Var(fracttypes.Bool, 1)
        self.checkIntInitVal(v)

    def checkIntInitVal(self,v):
        self.assertEqual(["1"], v.init_val())

        v.param_slot = 3
        self.assertEqual(["t__pfo->p[3].intval"],v.init_val())
        
    def testColorInitVal(self):
        v = fracttypes.Var(fracttypes.Color, [1.234,-7.89, 11.1, 1.0e10])
        self.checkQuadInitVal(v)

    def testHyperInitVal(self):
        v = fracttypes.Var(fracttypes.Hyper, [1.234,-7.89, 11.1, 1.0e10])
        self.checkQuadInitVal(v)
        
    def checkQuadInitVal(self,v):
        self.assertEqual(
            ["1.23399999999999999",
             "-7.88999999999999968",
             "11.09999999999999964",
             "10000000000.00000000000000000"],
            v.init_val())
        
        v.param_slot = 3
        self.assertEqual(
            ["t__pfo->p[3].doubleval",
             "t__pfo->p[4].doubleval",
             "t__pfo->p[5].doubleval",
             "t__pfo->p[6].doubleval"
             ],
            v.init_val())
        
def suite():
    return unittest.makeSuite(Test,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')
