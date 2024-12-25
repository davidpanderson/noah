#include <cstdio>
#include <stdlib.h>

#include "xw.h"

#define MAX_SIZE 22
    // NYT sunday is 21x21

// file format for black-square grids:
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
// This code reads such a file and produces a GRID
//
// By convention there are no unchecked squares,
// so to print it you can just print the acrosses.
//
// Lots of examples: https://crosswordgrids.com/

SLOT *slots[MAX_SIZE][MAX_SIZE];
    // for each cell, the across word if any
int starts[MAX_SIZE][MAX_SIZE];
    // and the column where that word starts
vector<SLOT*> across_slots;
int nrows, ncols;

void read_black_square_grid(FILE *f, GRID &grid, bool mirror) {
    int i, j, k, start, len;
    char chars[MAX_SIZE][MAX_SIZE];
    char buf[256];

    // read file into chars array
    //
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
        strncpy(chars[nrows], buf, ncols);
        chars[nrows][ncols] = '*';
        nrows++;
    }

    if (mirror) {
        for (i=0; i<nrows-1; i++) {
            for (j=0; j<ncols; j++) {
                chars[nrows+i][j] = chars[nrows-i-2][ncols-j-1];
            }
            chars[nrows+i][ncols] = '*';
        }
        nrows += (nrows-1);
    }

    // add a row of * at bottom
    for (j=0; j<ncols; j++) {
        chars[nrows][j] = '*';
    }

    // make across slots
    //
    for (i=0; i<nrows; i++) {
        start = -1;     // index of initial non-black cell
        for (j=0; j<ncols+1; j++) {
            if (chars[i][j] == '*') {
                if (start < 0) continue;
                len = j-start;
                if (len > 1) {
#if VERBOSE_INIT
                    printf("adding across slot at %d, %d; len %d\n",
                        i, start, len
                    );
#endif
                    SLOT *slot = grid.add_slot(new SLOT(len));
                    slot->row = i;
                    slot->col = start;
                    for (k=start; k<j; k++) {
                        slots[i][k] = slot;
                        starts[i][k] = start;
                    }
                    across_slots.push_back(slot);
                }
                start = -1;
            } else {
                if (start < 0) {
                    start = j;
                }
            }
        }
    }

    // make down slots
    //
    for (j=0; j<ncols; j++) {
        start = -1;
        for (i=0; i<nrows+1; i++) {
            if (chars[i][j] == '*') {
                if (start < 0) continue;
                len = i-start;
                if (len > 1) {
#if VERBOSE_INIT
                    printf("adding down slot at %d, %d; len %d\n",
                        start, j, len
                    );
#endif
                    SLOT *slot = grid.add_slot(new SLOT(len));
                    for (k=start; k<i; k++) {
                        if (slots[k][j]) {
                            SLOT *slot2 = slots[k][j];
                            grid.add_link(slot, k-start, slot2, j-starts[k][j]);
                        }
                    }
                }
                start = -1;
            } else {
                if (start < 0) {
                    start = i;
                }
            }
        }
    }

    // handle presets
    //
    for (i=0; i<nrows; i++) {
        for (j=0; j<ncols+1; j++) {
            char c = chars[i][j];
            if (c == '*' || c == '.') {
                continue;
            }
            SLOT *slot = slots[i][j];
            int pos = j - starts[i][j];
            slot->preset_char(pos, c);
        }
    }
}

void print_grid(GRID &grid, bool) {
    char chars[MAX_SIZE][MAX_SIZE];
    int i, j;
    for (i=0; i<nrows; i++) {
        for (j=0; j<ncols; j++) {
            chars[i][j] = '*';
        }
        chars[i][ncols] = 0;
    }
    for (SLOT* slot: across_slots) {
        i = slot->row;
        j = slot->col;
        if (slot->filled) {
            strncpy(&(chars[i][j]), slot->current_word, slot->len);
        } else {
            strncpy(&(chars[i][j]), slot->filled_pattern, slot->len);
        }
    }
    for (i=0; i<nrows; i++) {
#if CURSES
        move(i, 0);
        printw("%s", &(chars[i][0]));
#else
        printf("%s\n", &(chars[i][0]));
#endif
    }
#if CURSES
    refresh();
#endif
}

int main(int argc, char** argv) {
    GRID grid;
    bool mirror=false;
    words.read();
    init_pattern_cache();
    const char *fname = "bs_11_1";
    for (int i=1; i<argc; i++) {
        if (!strcmp(argv[i], "--mirror")) {
            mirror = true;
        } else {
            fname = argv[i];
        }
    }
    FILE *f = fopen(fname, "r");
    if (!f) {
        printf("no file %s\n", fname);
        exit(1);
    }
    read_black_square_grid(f, grid, mirror);
    grid.prepare();
    // grid.print_state();
    if (grid.fill()) {
        // grid.print_solution();
        print_grid(grid, true);
    } else {
        printf("no solution\n");
    }
}
