/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999-2002 Edwin Young
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
 *
 */

#ifdef HAVE_CONFIG_H
#  include <config.h>
#endif

#include "pointFunc.h"
#include "iterFunc.h"
#include "bailFunc.h"
#include "compiler.h"

#include <math.h>
#include <iostream>
#include <float.h>
#include <stdio.h>
#include <algorithm>

#include <unistd.h>
#include <dlfcn.h>

pointFunc *pointFunc_new(
    iterFunc *iterType, 
    e_bailFunc bailType, 
    double bailout,
    colorizer *pcf,
    e_colorFunc outerCfType,
    e_colorFunc innerCfType)
{

    compiler *c = new compiler();
    
    c->run();
    char buf[PATH_MAX];
    getcwd(buf,sizeof(buf));
    std::string out = buf + ("/" + c->out);

    void *dlHandle = dlopen(out.c_str(), RTLD_NOW);
    if(NULL == dlHandle)
    {
        return NULL;
    }
    pointFunc *(*pFunc)(
        iterFunc *,e_bailFunc, double, colorizer *, e_colorFunc, e_colorFunc) = 
        (pointFunc *(*)(iterFunc *,e_bailFunc, double, colorizer *, e_colorFunc, e_colorFunc)) 
        dlsym(dlHandle, "create_pointfunc");

    if(NULL == pFunc)
    {
        return NULL;
    }

    return pFunc(iterType, bailType, bailout, pcf, outerCfType, innerCfType);
}

