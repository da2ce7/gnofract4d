/* function objects which perform individual iterations of a fractal function */

#include "iterFunc.h"
#include "io.h"

#include <cstddef>
#include <iostream>
#include <iomanip> // setprecision
#include <string>  // strstream
#include <cmath>
#include <complex>
#include <sstream>

#define IO_DECLS(className) \
    friend std::ostream& operator<< <>(std::ostream& s, const className& m); \
    friend std::istream& operator>> <>(std::istream& s, className& m); \
    std::ostream& put(std::ostream& s) const { return s << *this; } \
    std::istream& get(std::istream& s) { return s >> *this;  } 

#define FIELD_FUNCTION "function"

// forward static calls of << to appropriate virtual function
std::ostream& 
operator<<(std::ostream& s, const iterFunc& iter)
{
    return iter.put(s);
}

std::istream&
operator>>(std::istream& s, iterFunc& iter)
{
    return iter.get(s);
}

/* This class eases the implementation of fractal types 
   T is the type of the actual fractal subclass, used for boring things 
       like cloning
   NOPTIONS is the number of parameters the fractal has */

template<class T, int NOPTIONS>
class iterImpl : public iterFunc
{
protected:
    const char *m_type;
    std::complex<double> a[NOPTIONS+1];
public:
    iterImpl(const char *type) : m_type(type) {}

    int nOptions() const
        { 
            return NOPTIONS; 
        }
    virtual void setOption(int n, std::complex<double> val) 
        {
            if(n < 0 || n >= NOPTIONS) return;
            //cout << "option " << n << " set to " << val << "\n";
            a[n] = val;
        }
    virtual std::complex<double> *opts()
        {
            return a;
        }
    virtual std::complex<double> getOption(int n) const
        {
            if(n < 0 || n >= NOPTIONS) return 0.0; 
            return a[n];
        }
    virtual const char *optionName(int n) const
        {
            return NULL;            
        }
    const char *type() const
        {
            return m_type;
        }
    int flags() const
        {
            return T::FLAGS;
        }
    virtual void reset(double *params)
        {
            /* suitable defaults for most types */
            // FIXME : duplicated in fractal.cpp
            params[XCENTER] = 0.0;
            params[YCENTER] = 0.0;
            params[ZCENTER] = 0.0;
            params[WCENTER] = 0.0;
            
            params[MAGNITUDE] = 4.0;
            params[BAILOUT] = 4.0;
            for(int i = XYANGLE; i < ZWANGLE+1; i++) {
                params[i] = 0.0;
            }
        }
    virtual e_bailFunc preferred_bailfunc(void)
        {
            return BAILOUT_MAG;
        }
    /* utility functions */

    /* copy constructor */
    iterFunc *clone() const
        {
            return new T((const T&)*this);
        }
    /* because you can't get a function pointer to a constructor (for no
       good reason that I can determine), we have a static member function
       called create which performs the construction for us. */
    static iterFunc *create()
        {
            return new T();
        }
    /* equality */
    bool operator==(const iterFunc &c) const
        {
            const T *p = dynamic_cast<const T *>(&c);
            if(!p) return false;
            for(int i = 0; i < NOPTIONS; ++i)
            {
                if(p->a[i] != a[i]) return false;
            }
            return true;
        }
    virtual std::string ret_code()  const { return ""; };
    virtual std::string save_iter_code() const {
        return "T lastx = pIter[X]; T lasty = pIter[Y]";
    }
    virtual std::string restore_iter_code() const {
        return "pIter[X] = lastx; pIter[Y] = lasty";
    }
    
    virtual void get_code(std::map<std::string,std::string>& code_map) const 
        {
            code_map["ITER"]=iter_code();
            code_map["DECL"]=decl_code();
            code_map["RET"]= ret_code();
            ostringstream os; 
            os << nOptions();
            code_map["N_OPTIONS"]= os.str();
            code_map["SAVE_ITER"]=save_iter_code();
            code_map["RESTORE_ITER"]=restore_iter_code();
            code_map["XPOS"]= flags() & USE_COMPLEX ? "z.real()" : "pIter[X]";
            code_map["YPOS"]= flags() & USE_COMPLEX ? "z.imag()" : "pIter[Y]";
        }
    IO_DECLS(iterImpl)
};

template<class T, int NOPTIONS>
std::ostream& 
operator<<(std::ostream& s, const iterImpl<T,NOPTIONS>& m) 
{ 
    write_field(s,FIELD_FUNCTION);
    s << m.type() << "\n";
    s << std::setprecision(20);
    for(int i = 0; i < NOPTIONS; ++i)
    {
        s << m.optionName(i) << "=" << m.getOption(i) << "\n";
    }
    s << SECTION_STOP << "\n"; 
    return s; 
} 

template<class T, int NOPTIONS>
std::istream& 
operator>>(std::istream& s, iterImpl<T, NOPTIONS>& m) 
{ 
    while(s)
    {
        std::string name,val;
        
        if(!read_field(s,name,val))
        {
            break;
        }

        for(int i = 0; i < NOPTIONS; ++i)
        {
            if(0 == strcmp(name.c_str(),m.optionName(i)))
            {
                std::istrstream vs(val.c_str());
                std::complex<double> opt;
                vs >> opt;
                m.setOption(i,opt);
                break;
            }
        }
        if(SECTION_STOP == name) break;
    }
    return s; 
}

#ifdef HAVE_GMP
#define GMP_FUNC_OP \
    void operator()(gmp::f *p) const \
        { \
            calc<gmp::f>(p);\
        }
#else
#define GMP_FUNC_OP
#endif

// z <- z^2 +c
class mandFunc : public iterImpl<mandFunc,0>
{
public:
    enum { FLAGS = HAS_X2 | HAS_Y2 };
    mandFunc() : iterImpl<mandFunc,0>(name()) {} 

    static const char *name()
        {
            return "Mandelbrot";
        }
    std::string decl_code() const 
        { 
            return "double atmp"; 
        }
    std::string iter_code() const 
        { 
            return 
                "pTemp[X2] = pIter[X] * pIter[X];"
                "pTemp[Y2] = pIter[Y] * pIter[Y];"
                "atmp = pTemp[X2] - pTemp[Y2] + pInput[CX];"
                "pIter[Y] = 2.0 * pIter[X] * pIter[Y] + pInput[CY];"
                "pIter[X] = atmp";
        }
};


// Newton's method for a quadratic complex polynomial
// z <- (z^2 + c)/2z
class newtFunc : public iterImpl<newtFunc,0>
{
 public:
    enum { FLAGS = USE_COMPLEX };
    newtFunc() : iterImpl<newtFunc,0>(name()){};
    static const char *name() 
        {
            return "Newton";
        }
    virtual e_bailFunc preferred_bailfunc(void)
        {
            return BAILOUT_DIFF;
        }
    std::string decl_code() const 
        { 
            return "std::complex<double> z(pIter[X],pIter[Y]) , c(pInput[CX],pInput[CY])";
        }
    std::string iter_code() const 
        { 
            return "z = (2.0 *z*z*z + c)/ (3.0 * z * z)";
        }
    std::string ret_code()  const 
        { 
            return "pIter[X] = z.real(); pIter[Y] = z.imag()"; 
        }
    virtual void reset(double *params)
        {
            iterImpl<newtFunc,0>::reset(params);
            // start at Julia
            params[XZANGLE] = params[YWANGLE] = M_PI/2.0;
            //offset from zero to give it something to work on
            params[XCENTER] = 0.1;
        }
};


// z <- (Az^3-B)/C z^2 + c
class novaFunc : public iterImpl<novaFunc,3>
{
public:
    enum {  FLAGS = USE_COMPLEX };
    novaFunc() : iterImpl<novaFunc,3>(name()) 
        { 
            reset_opts(); 
        };

    static char *name()
        {
            return "Nova";
        }
    std::string decl_code() const 
        { 
            return "std::complex<double> z(pIter[X],pIter[Y]), c(pInput[CX],pInput[CY])";
        }
    std::string iter_code() const 
        { 
            return "z = z - (a[0] * z*z*z - a[1])/(a[2] * z * z) + c";
        }
    std::string ret_code() const
        {
            return "pIter[X] = z.real(); pIter[Y] = z.imag()";
        }
    std::string save_iter_code() const
        {
            return "std::complex<double> last_z = z";
        }
    std::string restore_iter_code() const
        {
            return "z = last_z";
        }

    const char *optionName(int i) const
        {
            static const char *optNames[] =
            {
                "a", "b", "c"
            };
            if(i < 0 || i >= 3) return NULL;
            return optNames[i];
        }
    virtual void reset(double *params)
        {
            reset_opts();
            iterImpl<novaFunc,3>::reset(params);
            // start at Julia
            params[XZANGLE] = params[YWANGLE] = M_PI/2.0;
        }
    virtual e_bailFunc preferred_bailfunc(void)
        {
            return BAILOUT_DIFF;
        }
 private:
    void reset_opts()
        {
            // default is z - (z^3 - 1) / 3z^2 + c
            a[0] = std::complex<double>(1.0,0.0);
            a[1] = std::complex<double>(1.0,0.0);
            a[2] = std::complex<double>(3.0,0.0);
        }
};


// z <- ( re(z) > 0 ? (z - 1) * c : (z + 1) * c)
class barnsleyFunc: public iterImpl<barnsleyFunc,0>
{
public:
    enum {  FLAGS = 0 };
    barnsleyFunc() : iterImpl<barnsleyFunc,0>(name()) {};

    static char *name()
        {
            return "Barnsley Type 1";
        }
    std::string decl_code() const 
        { 
            return "double x_cy, x_cx, y_cy, y_cx";
        }
    std::string iter_code() const 
        { 
            return 
                "x_cy = pIter[X] * pInput[CY]; x_cx = pIter[X] * pInput[CX];"
                "y_cy = pIter[Y] * pInput[CY]; y_cx = pIter[Y] * pInput[CX];"
                
                "if(pIter[X] >= 0)"
                "{"
                    "pIter[X] = (x_cx - pInput[CX] - y_cy );"
                    "pIter[Y] = (y_cx - pInput[CY] + x_cy );"
                "}"
                "else"
                "{"
                    "pIter[X] = (x_cx + pInput[CX] - y_cy);"
                    "pIter[Y] = (y_cx + pInput[CY] + x_cy);"
                "}";
        }
};


class barnsley2Func: public iterImpl<barnsley2Func,0>
{
public:
    enum {  FLAGS = 0 };
    barnsley2Func() : iterImpl<barnsley2Func,0>(name()) {};

    static const char *name()
        {
            return "Barnsley Type 2";
        }
    std::string decl_code() const 
        { 
            return "double x_cy, x_cx, y_cy, y_cx";
        }
    std::string iter_code() const 
        { 
            return 
                "x_cy = pIter[X] * pInput[CY]; x_cx = pIter[X] * pInput[CX];"
                "y_cy = pIter[Y] * pInput[CY]; y_cx = pIter[Y] * pInput[CX]; "
    
                "if(pIter[X]*pInput[CY] + pIter[Y]*pInput[CX] >= 0) "
                "{" 
                    "pIter[X] = (x_cx - pInput[CX] - y_cy );"
                    "pIter[Y] = (y_cx - pInput[CY] + x_cy );"
                "}" 
                "else"
                "{" 
                    "pIter[X] = (x_cx + pInput[CX] - y_cy);"
                    "pIter[Y] = (y_cx + pInput[CY] + x_cy);" 
                "}";
        }
};


// z <- lambda * z * ( 1 - z)
class lambdaFunc: public iterImpl<lambdaFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    lambdaFunc() : iterImpl<lambdaFunc,0>(name()) {};

    static const char *name()
        {
            return "Lambda";
        }
    virtual void reset(double *params)
        {
            iterImpl<lambdaFunc,0>::reset(params);
            // override some defaults for a prettier picture
            params[XCENTER] = 1.0;
            params[ZCENTER] = 0.5;
            params[MAGNITUDE] = 8.0;
        }
    std::string decl_code() const 
        { 
            return "double tx, ty";
        }
    std::string iter_code() const 
        { 
            return
                "pTemp[X2] = pIter[X] * pIter[X]; pTemp[Y2] = pIter[Y] * pIter[Y];"
    
                /* t <- z * (1 - z) */
                "tx = pIter[X] - pTemp[X2] + pTemp[Y2];"
                "ty = pIter[Y] - 2.0 * pIter[X] * pIter[Y];"
    
                "pIter[X] = pInput[CX] * tx - pInput[CY] * ty;"
                "pIter[Y] = pInput[CX] * ty + pInput[CY] * tx";
        }
};

// z <- (|x| + i |y|)^2 + c
class shipFunc: public iterImpl<shipFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    shipFunc() : iterImpl<shipFunc,0>(name()) {};

    static const char *name()
        {
            return "Burning Ship";
        }
    std::string iter_code() const 
        { 
            return
                "pIter[X] = fabs(pIter[X]);"
                "pIter[Y] = fabs(pIter[Y]);"

                /* same as mbrot from here */
                "pTemp[X2] = pIter[X] * pIter[X];"
                "pTemp[Y2] = pIter[Y] * pIter[Y];"
                "atmp = pTemp[X2] - pTemp[Y2] + pInput[CX];"
                "pIter[Y] = 2.0 * pIter[X] * pIter[Y] + pInput[CY];"
                "pIter[X] = atmp";
        }
    std::string decl_code() const 
        { 
            return "double atmp";
        }
    virtual void reset(double *params)
        {
            iterImpl<shipFunc,0>::reset(params);
            // override some defaults for a prettier picture
            params[XCENTER] = -0.5;
            params[YCENTER] = -0.5;
        }
};

// z <- a[0] * (|x| + i |y|)^2 + a[1] * (|x| + i|y|) + a[2] * c
class buffaloFunc: public iterImpl<buffaloFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    buffaloFunc() : iterImpl<buffaloFunc,0>(name()) {}

    static const char *name()
        {
            return "Buffalo";
        }
    std::string decl_code() const 
        { 
            return "double atmp";
        }
    std::string iter_code() const
        {
            return 
                "pIter[X] = fabs(pIter[X]);"
                "pIter[Y] = fabs(pIter[Y]);"
   
                "pTemp[X2] = pIter[X] * pIter[X];"
                "pTemp[Y2] = pIter[Y] * pIter[Y];"
                "atmp = pTemp[X2] - pTemp[Y2] - pIter[X] + pInput[CX];"
                "pIter[Y] = 2.0 * pIter[X] * pIter[Y] - pIter[Y] + pInput[CY];"
                "pIter[X] = atmp";
        }
    virtual void reset(double *params)
        {
            iterImpl<buffaloFunc,0>::reset(params);
            // override some defaults for a prettier picture
            params[MAGNITUDE] = 6.0;
        }
};

// z <- z^3 + c
class cubeFunc : public iterImpl<cubeFunc,0>
{
public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    cubeFunc() : iterImpl<cubeFunc,0>(name()) {}

    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
    std::string decl_code() const 
        { 
            return "double atmp";
        }
    std::string iter_code() const
        {
            return 
                "pTemp[X2] = pIter[X] * pIter[X];"
                "pTemp[Y2] = pIter[Y] * pIter[Y];"
                "atmp = pTemp[X2] * pIter[X] - 3.0 * pIter[X] * pTemp[Y2] + pInput[CX];"
                "pIter[Y] = 3.0 * pTemp[X2] * pIter[Y] - pTemp[Y2] * pIter[Y] + pInput[CY];"
                "pIter[X] = atmp";
        }
};


// computes z^a + c
class ztoaFunc : public iterImpl<ztoaFunc,1>
{
public:
    enum { FLAGS = USE_COMPLEX };
    ztoaFunc() : iterImpl<ztoaFunc,1>(name()) {
    }
    static const char *name()
        {
            return "ManZPower";
        }
    std::string decl_code() const 
        { 
            return 
                "std::complex<double> z(pIter[X],pIter[Y]);" 
                "std::complex<double> c(pInput[CX],pInput[CY]);";
        }
    std::string iter_code() const
        {
            return
                "z = pow(z,a[0]) + c;";
        }
    std::string ret_code() const
        {
            return "pIter[X] = z.real(); pIter[Y] = z.imag()";
        }
    std::string save_iter_code() const
        {
            return "std::complex<double> last_z = z";
        }
    std::string restore_iter_code() const
        {
            return "z = last_z";
        }
    const char *optionName(int i) const
        {
            if(i != 0)  return NULL;
            return "a";
        }
    virtual void reset(double *params)
        {
            reset_opts();
            iterImpl<ztoaFunc,1>::reset(params);
            params[ZCENTER] = 1.0E-10; // avoid weird behavior with pow(0,...)
        }
private:
    void reset_opts()
        {
            // default is z^4 + c
            a[0] = std::complex<double>(4.0,0.0);
        }

};


// generalised quadratic mandelbrot
// computes a[0] * z^2 + a[1] * z + a[2] * c
class quadFunc : public iterImpl<quadFunc,3>
{
public:
    enum { FLAGS = USE_COMPLEX };
    quadFunc() : iterImpl<quadFunc,3>(name()) {
        reset_opts();
    }
    static const char *name()
        {
            return "Quadratic";
        }
    std::string decl_code() const 
        { 
            return 
                "std::complex<double> z(pIter[X],pIter[Y]);" 
                "std::complex<double> c(pInput[CX],pInput[CY]);";
        }
    std::string iter_code() const
        {
            return 
                "z = (a[0] * z + a[1]) * z + a[2] * c;";
        }
    std::string ret_code() const
        {
            return "pIter[X] = z.real(); pIter[Y] = z.imag()";
        }
    std::string save_iter_code() const
        {
            return "std::complex<double> last_z = z";
        }
    std::string restore_iter_code() const
        {
            return "z = last_z";
        }
    const char *optionName(int i) const
        {
            static const char *optNames[] =
            {
                "a", "b", "c"
            };
            if(i < 0 || i >= 3) return NULL;
            return optNames[i];
        }

    virtual void reset(double *params)
        {
            reset_opts();
            iterImpl<quadFunc,3>::reset(params);
            params[XCENTER]=-0.75;
        }
private:
    void reset_opts()
        {
            // default is z^2 - z + c
            a[0] = std::complex<double>(1.0,0.0);
            a[1] = std::complex<double>(1.0,0.0);
            a[2] = std::complex<double>(1.0,0.0);
        }
};

/*
// Taylor series approximation to exp
class taylorFunc : public iterImpl<taylorFunc,0>
{
#define CUBE_DECL double atmp
#define CUBE_ITER "
    pTemp[X2] = pIter[X] * pIter[X];"
    pTemp[Y2] = pIter[Y] * pIter[Y];"
    atmp = pTemp[X2] * pIter[X] - 3.0 * pIter[X] * pTemp[Y2] + pInput[CX];"
    pIter[Y] = 3.0 * pTemp[X2] * pIter[Y] - pTemp[Y2] * pIter[Y] + pInput[CY];"
    pIter[X] = atmp

public:
    enum {  FLAGS = HAS_X2 | HAS_Y2 };
    cubeFunc() : iterImpl<cubeFunc,0>(name()) {}

    ITER_DECLS(CUBE_DECL, CUBE_ITER)
    static const char *name()
        {
            return "Cubic Mandelbrot";
        }
};
*/

#define CTOR_TABLE_ENTRY(className) \
    { className::name(), className::create }

ctorInfo ctorTable[] = {
    CTOR_TABLE_ENTRY(mandFunc),
    CTOR_TABLE_ENTRY(shipFunc),
    CTOR_TABLE_ENTRY(buffaloFunc),
    CTOR_TABLE_ENTRY(cubeFunc),
    CTOR_TABLE_ENTRY(quadFunc),
    CTOR_TABLE_ENTRY(barnsleyFunc),
    CTOR_TABLE_ENTRY(barnsley2Func),
    CTOR_TABLE_ENTRY(lambdaFunc),
    CTOR_TABLE_ENTRY(ztoaFunc),
    CTOR_TABLE_ENTRY(novaFunc),
    CTOR_TABLE_ENTRY(newtFunc),
    { NULL, NULL}
};


const ctorInfo *iterFunc_names()
{ 
    return ctorTable;
}

// factory method to make new iterFuncs
iterFunc *iterFunc_new(const char *name)
{
    if(!name) return NULL;

    ctorInfo *p = ctorTable;
    while(p->name)
    {
        if(0 == strcmp(name,p->name))
        {
            return p->ctor();
        }
        p++;
    }
    // unknown type
    return NULL;
}

// deserialize an iterFunc from a stream
// without knowing its type

iterFunc *iterFunc_read(std::istream& s)
{
    std::string name, value;

    while(s)
    {
        read_field(s,name,value);
    
        if(FIELD_FUNCTION == name)
        {
            iterFunc *f = iterFunc_new(value.c_str());
            if(f)
            {
                s >> *f;
            }
            return f;
        }
    }
    return NULL;
}
