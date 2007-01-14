# If your project uses a database, you can set up database tests
# similar to what you see below. Be sure to set the db_uri to
# an appropriate uri for your testing database. sqlite is a good
# choice for testing, because you can use an in-memory database
# which is very fast.

from turbogears import testutil, database
from elephant_valley.model import *

import sqlite
database.set_db_uri("sqlite:///:memory:")

class TestFormulaFile(testutil.DBTest):
    def get_model(self):
        return FormulaFile
    
    def test_creation(self):
        "Object creation should set the name"
        obj = FormulaFile(file_name = "gf4d.frm")
        
        assert obj.file_name == "gf4d.frm"

    def testFormulas(self):
        ff = FormulaFile(file_name = "x")

        assert ff.formulas == []
        
        f1 = Formula(formulaFile=ff,formula_name = "a")
        f2 = Formula(formulaFile=ff,formula_name = "b")

        assert ff.formulas.count(f1) != 0
        assert ff.formulas.count(f2) != 0
        
    def test_dup(self):
        try:
            obj1 = FormulaFile(file_name = "1")
            obj2 = FormulaFile(file_name = "1")
        except sqlite.IntegrityError:
            return
        assert False and "Should have failed integrity check"
        
class TestFormula(testutil.DBTest):
    def get_model(self):
        return Formula

    def test_creation(self):
        ff = FormulaFile(file_name = "x")        
        obj = Formula(formulaFile=ff,formula_name = "Mandelbrot")
        assert obj.formulaFile.file_name == "x"

class TestFractal(testutil.DBTest):
    def get_model(self):
        return Fractal

    def test_creation(self):
        ff = FormulaFile(file_name = "x")        
        f = Formula(formulaFile=ff,formula_name = "Mandelbrot")
        fractal = Fractal(formula=f,title="My Fractal",description="Boring")
        assert fractal.formula.formulaFile.file_name == "x"
    
