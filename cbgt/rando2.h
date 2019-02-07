#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>
#include <stdarg.h>

/* -------------------------------- rando.h ------------------------------ */

/* Routine per la generazione dei pattern casuali (presuppone include math.h)
(dovrebbero essere portabili) */


/* float drand49(): ritorna un numero float tra 0.0 e 1.0
   float srand49(long): inizializza il seme e ritorna un numero random
                        compreso tra 0.0 e 1.0
(tratto da numerical recipes) */

static long rand49_idum=-77531;
static long rand49_idum2=-77531;
static long rand50_idum=-77531;

#define M 714025
#define IA 1366
#define IC 150889

float drand49()
{
        static long iy,ir[98];
        static int iff=0;
        int j;

	if (rand49_idum < 0 || iff == 0) {
            iff=1;
            if((rand49_idum=(IC-rand49_idum) % M)<0)
                             rand49_idum=(-rand49_idum);
            for (j=1;j<=97;j++) {
                    rand49_idum=(IA*(rand49_idum)+IC) % M;
                    ir[j]=(rand49_idum);
            }
            rand49_idum=(IA*(rand49_idum)+IC) % M;
            iy=(rand49_idum);
        }
        j=1 + 97.0*iy/M;
	if (j > 97 || j < 1) printf("RAN2: This cannot happen.");
        iy=ir[j];
        rand49_idum=(IA*(rand49_idum)+IC) % M;
        ir[j]=(rand49_idum);
        return (float) iy/M;
}

float drand49b()
{
        static long iy,ir[98];
        static int iff=0;
        int j;

	if (rand49_idum2 < 0 || iff == 0) {
            iff=1;
            if((rand49_idum2=(IC-rand49_idum2) % M)<0)
                             rand49_idum2=(-rand49_idum2);
            for (j=1;j<=97;j++) {
                    rand49_idum2=(IA*(rand49_idum2)+IC) % M;
                    ir[j]=(rand49_idum2);
            }
            rand49_idum2=(IA*(rand49_idum2)+IC) % M;
            iy=(rand49_idum2);
        }
        j=1 + 97.0*iy/M;
	if (j > 97 || j < 1) printf("RAN2: This cannot happen.");
        iy=ir[j];
        rand49_idum2=(IA*(rand49_idum2)+IC) % M;
        ir[j]=(rand49_idum2);
        return (float) iy/M;
}


float srand49(seme)
long seme;
{
   rand49_idum=(-seme);
   return drand49();
}

float srand49b(seme2)
long seme2;
{
   rand49_idum2=(-seme2);
   return drand49b();
}


float drand50()
{
        static long iy,ir[98];
        static int iff=0;
        int j;

	if (rand50_idum < 0 || iff == 0) {
            iff=1;
            if((rand50_idum=(IC-rand50_idum) % M)<0)
                             rand50_idum=(-rand50_idum);
            for (j=1;j<=97;j++) {
                    rand50_idum=(IA*(rand50_idum)+IC) % M;
                    ir[j]=(rand50_idum);
            }
            rand50_idum=(IA*(rand50_idum)+IC) % M;
            iy=(rand50_idum);
        }
        j=1 + 97.0*iy/M;
	if (j > 97 || j < 1) printf("RAN2: This cannot happen.");
        iy=ir[j];
        rand50_idum=(IA*(rand50_idum)+IC) % M;
        ir[j]=(rand50_idum);
        return (float) iy/M;
}

float srand50(seme)
long seme;
{
   rand50_idum=(-seme);
   return drand50();
}

#undef M
#undef IA
#undef IC

/* Generatore random di bit 0,1 con probabilita` 1/2 , 1/2 */
#define IB1 1
#define IB2 2
#define IB5 16
#define IB18 131072
#define MASK IB1+IB2+IB5

static unsigned long iseed=31277;

int srand10(seme)
long seme;
{
   iseed=seme;
}

int drand10()
{
        if (iseed & IB18) {
                iseed=((iseed ^ MASK) << 1) | IB1;
                return 1;
        } else {
                iseed <<= 1;
                return 0;
        }
}

#undef MASK
#undef IB18
#undef IB5
#undef IB2
#undef IB1

/* Ritorna un numero casuale con distribuzione normale (media nulla
varianza unitaria */

float gauss()
{
	static int iset=0;
	static float gset;
	float fac,r,v1,v2;

	if  (iset == 0) {
		do {
			v1=2.0*drand49()-1.0;
			v2=2.0*drand49()-1.0;
			r=v1*v1+v2*v2;
		} while (r >= 1.0);
		fac=sqrt(-2.0*log(r)/r);
		gset=v1*fac;
		iset=1;
		return v2*fac;
	} else {
		iset=0;
		return gset;
	}
}

float gauss2()
{
	static int iset=0;
	static float gset;
	float fac,r,v1,v2;

	if  (iset == 0) {
		do {
			v1=2.0*drand49b()-1.0;
			v2=2.0*drand49b()-1.0;
			r=v1*v1+v2*v2;
		} while (r >= 1.0);
		fac=sqrt(-2.0*log(r)/r);
		gset=v1*fac;
		iset=1;
		return v2*fac;
	} else {
		iset=0;
		return gset;
	}
}


float gammln(float xx)
{
  double x,y,tmp,ser;

  static double cof[6]={76.18009172947146,-86.50532032941677,
			24.01409824083091,-1.231739572450155,
			0.1208650973866179e-2,-0.5395239384953e-5};
  int j;

  y=x=xx;
  tmp=x+5.5;
  tmp-=(x+0.5)*log(tmp);
  ser=1.000000000190015;
  for(j=0;j<=5;j++) ser+=cof[j]/++y;
  return -tmp+log(2.5066282746310005*ser/x);
}

#define PI 3.141592654

float binom(float pp,int n)
{
  int j;

  static int nold=(-1);
  float am,em,g,angle,p,bnl,sq,t,y;
  static float pold=(-1.0),pc,plog,pclog,en,oldg;

  p=(pp<=0.5 ? pp:1.0-pp);
  am=n*p;
  if(n<25) {
    bnl=0.0;
    for(j=1;j<=n;j++)
      if(drand49()<p) ++bnl;
  } else if (am<1.0) {
    g=exp(-am);
    t=1.0;
    for(j=0;j<=n;j++) {
      t*=drand49();
      if(t<g) break;
    }
    bnl=(j<=n ? j:n);
  } else {
    if(n !=nold) {
      en=n;
      oldg=gammln(en+1.0);
      nold=n;
    } if(p!=pold) {
      pc=1.0-p;
      plog=log(p);
      pclog=log(pc);
      pold=p;
    }
    sq=sqrt(2.0*am*pc);
    do {
      do {
	angle=PI*drand49();
	y=tan(angle);
	em=sq*y+am;
      } while(em<0.0 || em>=(en+1.0));
      em=floor(em);
      t=1.2*sqrt(1.0+y*y)*exp(oldg-gammln(em+1.0)
			      -gammln(en-em+1.0)+em*plog+(en-em)*pclog);
    } while(drand49()>t);
    bnl=em;
  }
  if(p!=pp) bnl=n-bnl;
  return bnl;
}

#undef PI
