import re

ifdef_re = re.compile(r'\s*\$ifdef(\s+(?P<var>[a-z][a-z0-9_]*))?',
                      re.IGNORECASE)
endif_re = re.compile(r'\s*\$endif', re.IGNORECASE)

else_re = re.compile(r'\s*\$else', re.IGNORECASE)

define_re = re.compile(r'\s*\$define(\s+(?P<var>[a-z][a-z0-9_]*))?',
                       re.IGNORECASE)

class Error(Exception):
    def __init__(self,msg):
        Exception.__init__(self,msg)
        pass

class StackEntry:
    def __init__(self, line_num, isTrue):
        self.line_num = line_num
        self.isTrue = isTrue
    def __repr__(self):
        return "(%s,%s)" % (self.line_num, self.isTrue)
    
class T:
    def get_var(self, m, i, type):
        var = m.group("var")
        if not var:
            raise Error("%d: %s without variable" % (i, type))
        return var
    
    def popstack(self, i):
        if self.ifdef_stack == []:
            raise Error("%d: $ENDIF without $IFDEF" % i)
        
        self.ifdef_stack.pop()

        if self.ifdef_stack == []:
            return True
        else:
            return self.ifdef_stack[-1].isTrue
        
    def __init__(self, s):
        self.vars = {}
        lines = s.splitlines(True)
        self.ifdef_stack = []
        out_lines = []
        i = 1

        self.currently_true = True
        for line in lines:
            pass_through = False
            #print self.ifdef_stack, self.currently_true, line,
            m = ifdef_re.match(line)
            if m:
                var = self.get_var(m,i, "$IFDEF")
                if self.currently_true:
                    self.currently_true = self.vars.has_key(var)
                self.ifdef_stack.append(StackEntry(i, self.currently_true))
            elif else_re.match(line):
                self.currently_true = not self.currently_true

                if len(self.ifdef_stack) > 1:
                    self.currently_true = self.currently_true and \
                                          self.ifdef_stack[-2].isTrue

                self.ifdef_stack[-1].isTrue = self.currently_true
            elif endif_re.match(line):
                self.currently_true = self.popstack(i)
            else:
                if self.currently_true:
                    m = define_re.match(line)
                    if m:
                        # a $define
                        var = self.get_var(m,i, "$DEFINE")
                        self.vars[var] = 1
                    else:
                        # just a line
                        pass_through = True
                        
            if pass_through:
                out_lines.append(line)
            else:
                # cheesy way to get the line numbers to work out
                out_lines.append("\n")
                    
            i += 1
            
        if self.ifdef_stack != []:
            raise Error("%d: $IFDEF without $ENDIF" % \
                        self.ifdef_stack[-1].line_num)

        self._out = "".join(out_lines)
        
    def out(self):
        return self._out
    