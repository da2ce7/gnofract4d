#!/usr/bin/env python

# unit tests for canon module

import unittest
import canon
import absyn
import ir
import symbol
from fracttypes import *

class CanonTest(unittest.TestCase):
    def setUp(self):
        self.fakeNode = absyn.Empty(0)
        self.canon = canon.T(symbol.T())
    def tearDown(self):
        pass

    # convenience methods to make quick trees for testing
    def eseq(self,stms, exp):
        return ir.ESeq(stms, exp, self.fakeNode, Int)
    def var(self,name="a"):
        return ir.Var(name,self.fakeNode, Int)
    def const(self,value=0):
        return ir.Const(value, self.fakeNode, Int)
    def binop(self,stms,op="+"):
        return ir.Binop(op,stms,self.fakeNode, Int)
    def move(self,dest,exp):
        return ir.Move(dest, exp, self.fakeNode, Int)
    
    def testEmptyTree(self):
        self.assertEqual(self.canon.linearize(None),None)

    def testBinop(self):
        # binop with no eseqs
        tree = self.binop([self.var(), self.const()])
        ltree = self.canon.linearize(tree)
        self.assertTreesEqual(tree, ltree)
        self.assertESeqsNotNested(ltree,1)

        # left-hand eseq
        tree = self.binop([self.eseq([self.move(self.var(),self.const())],
                                      self.var("b")),
                           self.const()])

        ltree = self.canon.linearize(tree)
        self.failUnless(isinstance(ltree,ir.ESeq) and \
                        isinstance(ltree.children[0],ir.Move) and \
                        isinstance(ltree.children[1],ir.Binop) and \
                        isinstance(ltree.children[1].children[0],ir.Var))
        self.assertESeqsNotNested(ltree,1)

        # nested left-hand eseq
        tree = self.binop([self.eseq([self.move(self.var(),self.const())],
                                      self.var("b")),
                           self.const()])

        tree = self.binop([tree,self.const()])

        ltree = self.canon.linearize(tree)
        self.assertESeqsNotNested(ltree,1)

        # right-hand eseq
        tree = self.binop([self.var("a"),
                           self.eseq([self.move(self.var("b"),self.const())],
                                                self.var("b"))])
        ltree = self.canon.linearize(tree)
        self.assertESeqsNotNested(ltree,1)
        self.failUnless(isinstance(ltree.children[0].children[0], ir.Var) and \
                        ltree.children[0].children[0].name == \
                        ltree.children[1].children[1].children[0].name)

        # commuting right-hand eseq
        tree = self.binop([self.const(4),
                           self.eseq([self.move(self.var("b"),self.const())],
                                                self.var("b"))])
        ltree = self.canon.linearize(tree)
        self.assertESeqsNotNested(ltree,1)
        self.failUnless(isinstance(ltree.children[1].children[0],ir.Const))

        # nested right-hand eseq
        tree = self.binop([self.var("a"),
                           self.eseq([self.move(self.var("b"),self.const())],
                                                self.var("b"))])
        tree = self.binop([self.const(),tree])

        print tree.pretty()
        ltree = self.canon.linearize(tree)
        print ltree.pretty()
        self.assertESeqsNotNested(ltree,1)
        
    def assertESeqsNotNested(self,t,parentAllowsESeq):
        'check that no ESeqs are left below nodes if other types'
        if isinstance(t,ir.ESeq):
            if parentAllowsESeq:
                for child in t.children:
                    self.assertESeqsNotNested(child,1)
            else:
                self.fail("tree not well-formed after linearize")
        else:
            for child in t.children:
                self.assertESeqsNotNested(child,0)
                
    def assertTreesEqual(self, t1, t2):
        self.failUnless(
            t1.pretty() == t2.pretty(),
            ("%s, %s should be equivalent" % (t1.pretty(), t2.pretty())))

def suite():
    return unittest.makeSuite(CanonTest,'test')

if __name__ == '__main__':
    unittest.main(defaultTest='suite')

