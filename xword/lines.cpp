#include <cstdio>
#include <stdlib.h>
#include "xw.h"

#define MAX_SIZE 21
    // NYT sunday is 21x21

// read a file of the form
//
//  a a a a|a a a a a a a a
//      -   -   -       -
//  a|a|a a a a a a a a a a
//          -   -       -
//  a a a a a a|a a a a a a
// etc.
//
// | is a vertical bar and - is a horizontal bar
// a = any letter (can hard-code words or parts of words)
//      or . or space (blank cell)
//
// ... and make it into a GRID
//
// There can be unchecked squares.

void read_line_grid(FILE* f, GRID& grid) {
    char file[MAX_SIZE][MAX_SIZE];
    char buf[256];
    int nrows=0, ncols=0;
    int j;

    while (fgets(buf, sizeof(buf), f)) {
        int n = strlen(buf)-1;
        if (!n%2) {
            printf("bad line len\n");
            exit(1);
        }
        int nc = n/2;
        if (ncols && nc!=ncols) {
            printf("wrong line len\n");
            exit(1);
        }
        for (j=0; j<n; j++) {
        }
        nrows++;
    }
}

void print_grid(GRID &grid, bool is_solution) {
}

int main(int argc, char** argv) {
    GRID grid;
    words.read();
    init_pattern_cache();
    FILE *f = fopen(argv[1], "r");
    read_line_grid(f, grid); 
    grid.prepare();
#if CURSES
    initscr();
#endif
    if (grid.fill()) {
        grid.print_solution();
    } else {
        printf("no solution\n");
    }
}
