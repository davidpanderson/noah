#include <cstdio>

#include "xw.h"

#define CURSES      1
#define SQUARE_GRID_SIZE    6

#if CURSES
#include <ncurses.h>
#endif

void make_square_grid(GRID &grid, int len) {
    vector<SLOT*> across;
    vector<SLOT*> down;
    for (int i=0; i<len; i++) {
        across.push_back(grid.add_slot(len));
    }
    for (int i=0; i<len; i++) {
        down.push_back(grid.add_slot(len));
    }
    for (int i=0; i<len; i++) {
        for (int j=0; j<len; j++) {
            grid.add_link(across[i], j, down[j], i);
        }
    }
}

void print_grid(GRID &grid, bool is_solution) {
#if CURSES
    int offset = is_solution? SQUARE_GRID_SIZE+2 : 0;
    for (int i=0; i<SQUARE_GRID_SIZE; i++) {
        SLOT *slot = grid.slots[i];
        move(i+offset, 0);
        printw("%s", slot->filled?slot->current_word:slot->filled_pattern);
    }
    refresh();
#else
    for (int i=0; i<SQUARE_GRID_SIZE; i++) {
        SLOT *slot = grid.slots[i];
        printf("%s\n", slot->filled?slot->current_word:slot->filled_pattern);
    }
#endif
}

int main(int, char**) {
    GRID grid;
    words.read();
    init_pattern_cache();
    make_square_grid(grid, SQUARE_GRID_SIZE);
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
