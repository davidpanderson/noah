#include <cstdio>
#include <stdlib.h>

#include "xw.h"

#define MAX_SIZE 21
    // NYT sunday is 21x21

// black square grid:
// read a file of the form
//
//  **aaaaaaaaaaa**
//  *aaaaaaaaaaaaa*
//  aaaaaaaaaaaaaaa
//  aaaaa***aaaXaaa
// etc.
// * = a black square.
// a = any letter (can hard-code entries)
//      or . or space (blank cell)
//
// ... and make it into a GRID
//
// By convention there are no unchecked squares,
// so to print it you can just print the acrosses.

SLOT *slots[MAX_SIZE][MAX_SIZE];
    // for each cell, the across word if any
int starts[MAX_SIZE][MAX_SIZE];
    // and the column where that word starts
int nrows, ncols;

void read_black_square_grid(FILE *f, GRID &grid) {
    int i, j, k, start, len;
    char chars[MAX_SIZE][MAX_SIZE];
    char buf[256];

    while (fgets(buf, sizeof(buf), f)) {
        int nc = strlen(buf)-1;
        if (ncols) {
            if (nc != ncols) {
                fprintf(stderr, "size mismatch\n");
                exit(1);
            }
        } else {
            ncols = nc;
        }
        strncpy(chars[nrows], buf, nc);
        chars[nrows][nc] = 'X';
        nrows++;
    }
    // add a row of X at bottom
    for (j=0; j<ncols; j++) {
        chars[nrows][j] = 'X';
    }

    for (i=0; i<nrows; i++) {
        start = -1;
        for (j=0; j<ncols; j++) {
            slots[i][j] = NULL;
            if (chars[i][j] == 'X') {
                if (start >= 0) {
                    len = j-start;
                }
                if (len > 1) {
                    SLOT *slot = grid.add_slot(new SLOT(len));
                    for (k=start; k<j; k++) {
                        slots[i][k] = slot;
                        starts[i][k] = start;
                    }
                }
                start = j;
            }
        }
    }

    for (j=0; j<ncols; j++) {
        start = -1;
        for (i=0; i<nrows; i++) {
            if (chars[i][j] == 'X') {
                if (start >= 0) {
                    len = i-start;
                }
                if (len > 1) {
                    SLOT *slot = grid.add_slot(new SLOT(len));
                    for (k=start; k<i; k++) {
                        if (slots[k][j]) {
                            SLOT *slot2 = slots[k][j];
                            grid.add_link(slot, k-start, slot2, starts[k][j]);
                        }
                    }
                }
                start = i;
            }
        }
    }
}

void print_grid(GRID &grid, bool) {
    int i, j;
    for (i=0; i<nrows; i++) {
        for (j=0; j<ncols; j++) {
            SLOT *slot = slots[i][j];
            if (slot) {
                printf("%s", slot->filled_pattern);
                j += slot->len;
            } else {
                printf("*");
            }
        }
    }
}

int main(int argc, char** argv) {
    GRID grid;
    words.read();
    init_pattern_cache();
    FILE *f = fopen(argv[1], "r");
    read_black_square_grid(f, grid);
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
