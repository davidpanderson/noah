#include <cstdio>
#include "xw.h"

#define MAX_SIZE 21
    // NYT sunday is 21x21

// line grid:
// read a file of the form
//
//  a a a a|a a a a a a a a
//      -   -   -       -
//  a|a|a a a a a a a a a a
//          -   -       -
//  a a a a a a|a a a a a a
// etc.
// and make it into a GRID
// There can be unmarked squares

void read_line_grid(FILE* f, GRID& grid) {
    char file[MAX_SIZE][MAX_SIZE];
    char buf[256];
    while (fgets(buf, sizeof(buf), f)) {
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
