#include <cstdio>
#include <stdlib.h>

#include "xw.h"

// fill a black-square grid.
// options:
// --mirror: 2n+1 rows are given; append the 180 deg rotation of the first 2n
// --wrap_row, --wrap_col: words can wrap around in the x or y directions
// --twist_row, --twist_col: if wrap, apply a twist (Klein bottle)

#define MAX_SIZE 22
    // NYT sunday is 21x21

// file format for black-square grids:
//
//  **...........**
//  *.............*
//  ...............
//  table***...*...
// etc.
// * = a black square.
// a = any letter (can hard-code entries)
//      or . or space (blank cell)
//
// By convention there are no unchecked squares,
// so to print a grid you can just print the acrosses.
//
// Lots of sample grids: https://crosswordgrids.com/

bool mirror;
bool wrap[2];   // [wrap columns?, wrap rows?]
bool twist[2];  // whether to twist when wrap
int size[2];    // [#cols, #rows]

char chars[MAX_SIZE][MAX_SIZE];
    // file contents
    // X/Y coords: first coord is col, 2nd is row
SLOT *across_slots[MAX_SIZE][MAX_SIZE];
SLOT *down_slots[MAX_SIZE][MAX_SIZE];
    // for each cell, the across and down slots if any
int across_pos[MAX_SIZE][MAX_SIZE];
int down_pos[MAX_SIZE][MAX_SIZE];
    // and the position in that slot
vector<SLOT*> across_slots_list;
vector<SLOT*> down_slots_list;

// return coords of previous cell in that row (coord=0) or column (1)
// (taking into account wrapping and/or twisting in that direction)
//
void prev(int (&c)[2], int coord, int (&d)[2]) {
    d[0] = c[0];
    d[1] = c[1];
    int coord2 = 1 - coord;
    d[coord2] -= 1;
    if (d[coord2] < 0) {
        d[coord2] = size[coord2] - 1;
        if (twist[coord]) {
            d[coord] = size[coord] - c[coord] - 1;
        }
    }
}

void next(int (&c)[2], int coord, int (&d)[2]) {
    d[0] = c[0];
    d[1] = c[1];
    int coord2 = 1 - coord;
    d[coord2] += 1;
    if (d[coord2] == size[coord2]) {
        d[coord2] = 0;
        if (twist[coord]) {
            d[coord] = size[coord] - c[coord] - 1;
        }
    }
}

#if 0
int main(int argc, char** argv) {
    int c[2], d[2];
    size[0] = 3;
    size[1] = 5;
    twist[0] = true;
    while(1) {
        scanf("%d %d", &c[0], &c[1]);
        prev(c, 0, d);
        printf("prev 0: %d %d\n", d[0], d[1]);
        next(c, 0, d);
        printf("next 0: %d %d\n", d[0], d[1]);
        prev(c, 1, d);
        printf("prev 1: %d %d\n", d[0], d[1]);
        next(c, 1, d);
        printf("next 1: %d %d\n", d[0], d[1]);

    }
}

void print_grid(GRID &grid, bool) {
}
#endif

bool is_prev_black(int (&c)[2], int coord) {
    int d[2];
    int coord2 = 1 - coord;
    if (c[coord2] == 0) {
        if (wrap[coord]) {
            prev(c, coord, d);
            return chars[d[0]][d[1]] == '*';
        } else {
            return true;
        }
    } else {
        d[0] = c[0];
        d[1] = c[1];
        d[coord2] -= 1;
        return chars[d[0]][d[1]] == '*';
    }
}
bool is_next_black(int (&c)[2], int coord) {
    int d[2];
    int coord2 = 1 - coord;
    if (c[coord2] == size[coord2]) {
        if (wrap[coord]) {
            next(c, coord, d);
            return chars[d[0]][d[1]] == '*';
        } else {
            return true;
        }
    } else {
        d[0] = c[0];
        d[1] = c[1];
        d[coord2] += 1;
        return chars[d[0]][d[1]] == '*';
    }
}

void read_file(FILE *f) {
    int i, j, k, start, len;
    char buf[256];
    int nrows=0, ncols=0;

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
        //chars[nrows][ncols] = '*';
        nrows++;
    }

    if (mirror) {
        for (i=0; i<nrows-1; i++) {
            for (j=0; j<ncols; j++) {
                chars[nrows+i][j] = chars[nrows-i-2][ncols-j-1];
            }
            //chars[nrows+i][ncols] = '*';
        }
        nrows += (nrows-1);
    }

    // add a row of * at bottom
    for (j=0; j<ncols; j++) {
        //chars[nrows][j] = '*';
    }
    size[0] = nrows;
    size[1] = ncols;
}

void find_slots(GRID &grid) {
    int i, j;
    // make across slots
    // scan each row.
    //
    for (i=0; i<size[1]; i++) {
        int row = i;
        int col = 0;
        SLOT *slot = NULL;
        bool wrapped = false;
        while (1) {
            if (chars[row][col] == '*') {
                if (slot) {
                    slot = NULL;
                }
                if (wrapped) break;
            } else {
                // non-black
                if (slot) {
                    across_slots[row][col] = slot;
                    across_pos[row][col] = slot->len;
                    slot->len += 1;
                    int c[2]={row, col};
                    if (is_next_black(c, 0)) {
                        slot = NULL;
                    }
                } else {
                    int c[2]={row, col};
                    if (is_prev_black(c, 0)) {
                        slot = new SLOT(1);
                        slot->row = row;
                        slot->col = col;
                        slot->is_across = true;
                        across_slots[row][col] = slot;
                        across_pos[row][col] = 0;
                        across_slots_list.push_back(slot);
                    }
                }
            }
            if (col == size[0]-1) {
                if (slot && wrap[0]) {
                    int c[2]={row, col}, d[2];
                    next(c, 0, d);
                    row = d[0];
                    col = d[1];
                    wrapped = true;
                } else {
                    break;
                }
            } else {
                col++;
            }
        }
    }

    // make down slots
    //
    for (j=0; j<size[1]; j++) {
        int row = 0;
        int col = j;
        SLOT *slot = NULL;
        bool wrapped = false;
        while (1) {
            if (chars[row][col] == '*') {
                if (slot) {
                    slot = NULL;
                }
                if (wrapped) break;
            } else {
                // non-black
                if (slot) {
                    down_slots[row][col] = slot;
                    down_pos[row][col] = slot->len;
                    slot->len += 1;
                    int c[2]={row, col};
                    if (is_next_black(c, 1)) {
                        slot = NULL;
                    }
                } else {
                    int c[2]={row, col};
                    if (is_prev_black(c, 1)) {
                        slot = new SLOT(1);
                        slot->row = row;
                        slot->col = col;
                        slot->is_across = false;
                        down_slots[row][col] = slot;
                        down_pos[row][col] = 0;
                        down_slots_list.push_back(slot);
                    }
                }
            }
            if (row == size[1]-1) {
                if (slot && wrap[1]) {
                    int c[2]={row, col}, d[2];
                    next(c, 1, d);
                    row = d[0];
                    col = d[1];
                    wrapped = true;
                } else {
                    break;
                }
            } else {
                row++;
            }
        }
    }

    // link slots and add preset chars
    //
    for (i=0; i<size[0]; i++) {
        for (j=0; j<size[1]; j++) {
            char c = chars[i][j];
            if (c == '*') {
                continue;
            }
            SLOT *aslot = across_slots[i][j];
            SLOT *dslot = down_slots[i][j];
            int apos = across_pos[i][j];
            int dpos = down_pos[i][j];
            if (c == '.') {
                aslot->add_link(apos, dslot, dpos);
                dslot->add_link(dpos, aslot, apos);
            } else {
                aslot->preset_char(apos, c);
                dslot->preset_char(dpos, c);
            }
        }
    }

    // add slots to grid
    //
    for (SLOT *slot: across_slots_list) {
        slot->init();
        grid.add_slot(slot);
    }
    for (SLOT *slot: down_slots_list) {
        slot->init();
        grid.add_slot(slot);
    }
}

void print_grid(GRID &grid, bool) {
    char chars[MAX_SIZE][MAX_SIZE];
    int i, j;
    for (i=0; i<size[1]; i++) {
        for (j=0; j<size[0]; j++) {
            SLOT *slot = across_slots[i][j];
            if (slot) {
                int pos = across_pos[i][j];
                if (slot->filled) {
                    chars[i][j] = slot->current_word[pos];
                } else {
                    chars[i][j] = slot->filled_pattern[pos];
                }
            } else {
                chars[i][j] = '*';
            }
        }
        chars[i][size[0]] = 0;
    }
    for (i=0; i<size[1]; i++) {
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
    words.read();
    init_pattern_cache();
    const char *fname = "bs_11_1";
    for (int i=1; i<argc; i++) {
        if (!strcmp(argv[i], "--mirror")) {
            mirror = true;
        } else if (!strcmp(argv[i], "--wrap_row")) {
            wrap[0] = true;
        } else if (!strcmp(argv[i], "--wrap_col")) {
            wrap[1] = true;
        } else if (!strcmp(argv[i], "--twist_row")) {
            twist[0] = true;
        } else if (!strcmp(argv[i], "--twist_col")) {
            twist[1] = true;
        } else {
            fname = argv[i];
        }
    }
    FILE *f = fopen(fname, "r");
    if (!f) {
        printf("no file %s\n", fname);
        exit(1);
    }
    read_file(f);
    find_slots(grid);
    grid.prepare();
    grid.print_state();
#if 1
    if (grid.fill()) {
        // grid.print_solution();
        print_grid(grid, true);
    } else {
        printf("no solution\n");
    }
#endif
}
