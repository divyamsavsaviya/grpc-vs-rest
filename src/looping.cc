/**
 * this is the same basic function that is in the grpc server implementation
 */

#include <iostream>

#include "omp.h"

static int N = 100000;

// print test results
#define VERBOSE

int doLoop(int notused) { 

    auto baseValue = 1; 
    int a[N+1], b[N+1];

    // initialize comparison
    for (int i = 0; i < N; i++) {
        a[i] = baseValue;
        b[i] = i;
    }

#ifdef VERBOSE
#if defined(_OPENMP)
    printf("\n\nExecutable is using OpenMP\n\n");
#endif
    printf("---------------------------------\n");
    printf(" T,  i)   A   B   tmp\n");
#endif

    auto tcnt = 0;
    #pragma omp parallel
    {
#if defined(_OPENMP)
        auto id = omp_get_thread_num();
#else
        auto id = -1; 
#endif

        // how would you use reduction?
        auto cnt = 0;

        #pragma omp for schedule(static)
        //#pragma omp for schedule(dynamic)
        for (int i = 0; i < N; i++) {
            a[i] = baseValue;
            a[i+1] = b[i+1];
            baseValue = a[i];

            // on a single socket we see more collisions
            if ( baseValue != 1 ) {
                cnt++;
#ifdef VERBOSE 
                #pragma omp critical
                printf("%2d, %3d) %3d %3d %3d\n", id,i,a[i],b[i],baseValue);
#endif
             }
        }

       #pragma omp critical
       { tcnt += cnt; }
    }

#ifdef VERBOSE2
    printf("Collisions: %3d\n", tcnt);
#endif


    return tcnt;
}

int main(int argc, char** argv) {
  auto tc = doLoop(1);
  printf("Total collisions: %3d\n",tc);

  return 0;
}
