# The fractal standard library, including operators

from codegen import ComplexArg
from fracttypes import *

def reals(l):
    # [[a + ib], [c+id]] => [ a, c]
    return [x.re for x in l]

def imags(l):
    return [x.im for x in l]

# basic binary operation
def add_ff_f(gen,t,srcs):
    return gen.emit_binop(t.op,srcs,t.datatype)

# many equivalent funcs
sub_ff_f = mul_ff_f = div_ff_f = add_ff_f
add_ii_i = sub_ii_i = mul_ii_i = div_ii_i = add_ff_f
gt_ii_b = gte_ii_b = lt_ii_b = lte_ii_b = eq_ii_b = noteq_ii_b = add_ff_f
gt_ff_b = gte_ff_b = lt_ff_b = lte_ff_b = eq_ff_b = noteq_ff_b = add_ff_f

def mul_cc_c(gen,t,srcs):
    # (a+ib) * (c+id) = ac - bd + i(bc + ad)
    ac = gen.emit_binop(t.op, [srcs[0].re, srcs[1].re], Float)
    bd = gen.emit_binop(t.op, [srcs[0].im, srcs[1].im], Float)
    bc = gen.emit_binop(t.op, [srcs[0].im, srcs[1].re], Float)
    ad = gen.emit_binop(t.op, [srcs[0].re, srcs[1].im], Float)
    dst = ComplexArg(
        gen.emit_binop('-', [ac, bd], Float),
        gen.emit_binop('+', [bc, ad], Float))
    return dst

def complex_ff_c(gen,t,srcs):
    # construct a complex number from two real parts
    return ComplexArg(srcs[0],srcs[1])

def add_cc_c(gen,t,srcs):
    # add 2 complex numbers
    dst = ComplexArg(
        gen.emit_binop(t.op,reals(srcs), Float),
        gen.emit_binop(t.op,imags(srcs), Float))
    return dst

# sub implemented same way as add
sub_cc_c = add_cc_c

def mag_c_f(gen,t,src):
    # |x| = x_re * x_re + x_im * x_im
    re_2 = gen.emit_binop('*',[src.re,src.re],Float)
    im_2 = gen.emit_binop('*',[src.im,src.im],Float)
    return gen.emit_binop('+',[re_2,im_2],Float)


def lt_cc_b(gen,t,srcs):    
    # compare real parts only
    return gen.emit_binop(t.op,reals(srcs), Bool)

# these comparisons implemented the same way
lte_cc_b = gt_cc_b = gte_cc_b = lt_cc_b

def eq_cc_b(gen,t,srcs):
    # compare 2 complex numbers for equality
    d1 = gen.emit_binop(t.op,reals(srcs), Bool)
    d2 = gen.emit_binop(t.op,imags(srcs), Bool)
    dst = gen.emit_binop("&&", [d1, d2], Bool)
    return dst

def noteq_cc_b(gen,t,srcs):
    # compare 2 complex numbers for inequality
    d1 = gen.emit_binop(t.op,reals(srcs), Bool)
    d2 = gen.emit_binop(t.op,imags(srcs), Bool)
    dst = gen.emit_binop("||", [d1, d2], Bool)
    return dst

# sqr = square(x) = x*x

def sqr_c_c(gen,t,srcs):
    # sqr(a+ib) = a2 - b2 + i(2ab)
    src = srcs[0]
    a2 = gen.emit_binop('*', [src.re, src.re], Float)
    b2 = gen.emit_binop('*', [src.im, src.im], Float)
    ab = gen.emit_binop('*', [src.re, src.im], Float)
    dst = ComplexArg(
        gen.emit_binop('-', [a2, b2], Float),
        gen.emit_binop('+', [ab, ab], Float))
    return dst
    
def sqr_f_f(gen,t,srcs):
    return gen.emit_binop('*',[srcs[0], srcs[0]], Float)

sqr_i_i = sqr_f_f