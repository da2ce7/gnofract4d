/* Gnofract4D -- a little fractal generator-browser program
 * Copyright (C) 1999 Aurelien Alleaume, Edwin Young
 *
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

#ifndef _TEST_FONCTION_H_
#define _TEST_FONCTION_H_



#define	NFUNCS 2

#define X 0
#define Y 1
#define CX 2
#define CY 3
#define X2 4
#define Y2 5
#define EJECT 6
#define EJECT_VAL 7

static const int N_SCRATCH_REGISTERS=8;

typedef double scratch_space[N_SCRATCH_REGISTERS] ;

typedef int (*fractFunc)(
	const dvec4& params, 
	const d& eject, 
	scratch_space scratch,
	int nIters);

extern fractFunc fractFuncTable[NFUNCS];

int test_mandelbrot_double(
	const dvec4& params, 
	const d& eject, 
	scratch_space scratch,
	int nIters);

int test_mandelbrot_cln(const dvec4& params, const d& eject, int nIters);

#endif
