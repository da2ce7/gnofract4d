import os

import fc, event

FRACTAL = 0
INNER = 1
OUTER = 2
TRANSFORM = 3
GRADIENT = 4

def stricmp(a,b):
    return cmp(a.lower(),b.lower())

class TypeInfo:
    def __init__(self, parent, compiler, t, exclude=None):
        self.parent = parent
        self.formula_type = t
        self.exclude= exclude
        self.fname = None
        self.formula = None
        self.formulas = []
        self.files = compiler.find_files_of_type(t)
        self.files.sort(stricmp)
        
    def set_file(self,compiler,fname):
        if self.fname == fname:
            return
        if None == fname:
            self.formulas = []
        else:
            ff = compiler.get_file(fname)
            self.formulas = ff.get_formula_names(self.exclude)
            self.formulas.sort(stricmp)
        self.fname = fname
        self.set_formula(compiler,None)
        self.file_changed()
        
    def set_formula(self,compiler,formula):
        if self.formula == formula:
            return
        self.formula = formula
        self.formula_changed()
        
    def file_changed(self):
        self.parent.file_changed()

    def formula_changed(self):
        self.parent.formula_changed()

    def apply(self,f,t):
        f.freeze()

        if None == self.fname or None == self.formula:
            return

        if t == FRACTAL:
            f.set_formula(self.fname,self.formula)
            f.reset()
        elif t == INNER:
            f.set_inner(self.fname,self.formula)
        elif t == OUTER:
            f.set_outer(self.fname,self.formula)
        elif t == TRANSFORM:
            f.append_transform(self.fname,self.formula)
        elif t == GRADIENT:
            f.set_gradient_from_file(self.fname, self.formula)

        if f.thaw():
            f.changed()
        

class T:
    def __init__(self,compiler):
        self.compiler = compiler
        self.typeinfo = [
            TypeInfo(self, compiler, fc.FormulaTypes.FRACTAL),
            TypeInfo(self, compiler, fc.FormulaTypes.COLORFUNC, "OUTSIDE"),
            TypeInfo(self, compiler, fc.FormulaTypes.COLORFUNC, "INSIDE"),
            TypeInfo(self, compiler, fc.FormulaTypes.TRANSFORM),
            TypeInfo(self, compiler, fc.FormulaTypes.GRADIENT)
            ]
        self.current_type = -1
        self.type_changed = event.T()
        self.file_changed = event.T()
        self.formula_changed = event.T()
        self.set_type(FRACTAL)
        
        
    def set_type(self,t):
        if self.current_type == t:
            return
        self.current_type = t
        self.current = self.typeinfo[t]
        self.type_changed()

    def set_file(self,fname):
        if fname:
            fname = os.path.basename(fname)
        self.current.set_file(self.compiler,fname)

    def set_formula(self,formula):
        self.current.set_formula(self.compiler,formula)
        
    def get_type_info(self,t):
        return self.typeinfo[t]

    def update(self,fname,formula):
        self.set_file(fname)
        self.set_formula(formula)

    def apply(self,f):
        self.current.apply(f,self.current_type)
