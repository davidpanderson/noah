#include <cstdio>
#include <cstring>
#include <unordered_map>
#include <algorithm>

#include "xw.h"

// copyright (C) 2025 David P. Anderson

// xw: fill generalized crossword puzzle grids
// This program enumerates all solutions for a given grid.

// This function must be linked with code that exports the following.

extern void make_grid(const char* filename, GRID&);
    // read the given file and populate the GRID structure.
    // We supply two variants:
    // black-square format (NYT type puzzles)
    // line-grid format (Atlantic cryptic type puzzles)
extern void print_grid(GRID&, bool curses);
    // print the (partially-filled) grid

///////////// WORD LISTS AND PATTERNS //////////////

// 'pattern': a word in which some or all positions are undetermined
// (represented by _)

WORDS words;

// read words from file into per-length vectors
//
void WORDS::read(const char* fname) {
    FILE* f = fopen(fname, "r");
    if (!f) {
        printf("no word list %s\n", fname);
        exit(1);
    }
    char buf[256];
    while (fgets(buf, 256, f)) {
        int len = strlen(buf)-1;
        if (len >= MAX_LEN) continue;
        buf[len] = 0;
        nwords[len]++;
        words[len].push_back(strdup(buf));
    }
}
void WORDS::shuffle() {
    for (int i=1; i<=MAX_LEN; i++) {
        if (words[i].empty()) continue;
        random_shuffle(words[i].begin(), words[i].end());
    }
}
void WORDS::print_counts() {
    printf("%d\n", max_len);
    for (int i=1; i<=MAX_LEN; i++) {
        printf("%d: %d\n", i, nwords[i]);
    }
}

// does word match pattern?
//
inline bool match(int len, char *pattern, char* word) {
    for (int i=0; i<len; i++) {
        if (pattern[i]!='_' && pattern[i]!=word[i]) return false;
    }
    return true;
}

// get list of indices of words matching pattern
//
void get_matches(int len, char *pattern, WLIST &wlist, ILIST &ilist) {
    for (unsigned int i=0; i<wlist.size(); i++) {
        if (match(len, pattern, wlist[i])) {
            ilist.push_back(i);
        }
    }
}

void show_matches(int len, WLIST &wlist, ILIST &ilist) {
    for (int i: ilist) {
        printf("%s\n", wlist[i]);
    }
}

// for a list of words of given len,
// cache a mapping of pattern -> word index list
//
struct PATTERN_CACHE {
    int len;
    WLIST *wlist;
    unordered_map<string, ILIST*> map;

    void init(int _len, WLIST *_wlist) {
        len = _len;
        wlist = _wlist;
    }
    ILIST* get_list(char* pattern) {
        auto it = map.find(pattern);
        if (it == map.end()) {
            ILIST *ilist = new ILIST;
            get_matches(len, pattern, *wlist, *ilist);
            map[pattern] = ilist;
            return ilist;
        } else {
            return it->second;
        }
    }
    void clear() {
        map.clear();
    }
};

// for each word len, cache of pattern -> ILIST pairs
//
PATTERN_CACHE pattern_cache[MAX_LEN];

void init_pattern_cache() {
    for (int i=1; i<=MAX_LEN; i++) {
        pattern_cache[i].init(i, &(words.words[i]));
    }
}

void clear_pattern_cache() {
    for (int i=1; i<=MAX_LEN; i++) {
        pattern_cache[i].clear();
    }
}

// finalize a slot.
// get initial list of compatible words.
// If slot is preset, mark as filled
//
void SLOT::prepare_slot() {
    preset_pattern[len] = 0;
    strcpy(filled_pattern, preset_pattern);

    if (strchr(filled_pattern, '_')) {
        compatible_words = pattern_cache[len].get_list(filled_pattern);
        filled = false;
    } else {
        compatible_words = NULL;
        strcpy(current_word, filled_pattern);
        filled = true;
    }
}

// debugging
void SLOT::print_usable() {
    printf("usable checked:\n");
    for (int i=0; i<len; i++) {
        for (int j=0; j<26; j++) {
            printf("%d", usable_letter_checked[i][j]);
        }
        printf("\n");
    }
    printf("usable ok:\n");
    for (int i=0; i<len; i++) {
        for (int j=0; j<26; j++) {
            printf("%d", usable_letter_ok[i][j]);
        }
        printf("\n");
    }
}

void SLOT::add_link(int this_pos, SLOT* other_slot, int other_pos) {
    LINK &link = links[this_pos];
    if (link.other_slot) {
        printf("slot %d, pos %d: already linked\n", num, this_pos);
        exit(1);
    }
    link.other_slot = other_slot;
    link.other_pos = other_pos;
}

void SLOT::print_state(bool show_links) {
    printf("slot %d:\n", num);
    printf("   row %d column %d; %s; len %d\n",
        row, col, is_across?"across":"down", len
    );
    if (filled) {
        printf("   filled; word: %s; index %d\n",
            current_word, next_word_index
        );
    } else {
        printf("   unfilled\n");
    }
    printf("   stack pattern: %s\n", filled_pattern);
    if (compatible_words) {
        printf("   %ld compat words\n",
            compatible_words->size()
        );
    } else {
        printf("   compat words is null\n");
    }
    if (show_links) {
        printf("   links\n");
        for (int i=0; i<len; i++) {
            LINK &link = links[i];
            if (link.other_slot) {
                printf("      pos %d -> slot %d pos %d\n",
                    i, link.other_slot->num, link.other_pos
                );
            }
        }
    }
}

////////////////// GRID-FILL ALGORITHMS ////////////////

// Sketch of fill algorithm:
//
// at any point we have a stack of filled slots
// each slot has
//      'filled_pattern' reflecting crossing letters:
//          filled slots: slots lower on the stack
//          unfilled slots: all filled slots
//      compatible_words: list of words compatible with filled_pattern
// filled slots have
//      current word
//      a 'next index' into compatible_words
//
// fill_next_slot() picks an unfilled slot S
//      (currently, the one with fewest compatible words).
//      it scans its compatible_words list for an word that's 'usable'
//          (i.e. other unfilled slots would have compatible words)
//      if it finds one it adds that S to the filled stack,
//          sets S.current_word
//          and updates filled_pattern and compatible_words
//          of affected unfilled slots
//      otherwise we backtrack:
//          loop
//              for slot S at top of stack:
//              update filled_patterns of unfilled slots to remove
//                  letters in S.current_word unspecified in S.filled_pattern
//              look for next usable word
//              if none
//                  pop S
//              else
//                  set S.current_word
//                  update filled_patterns of unfilled slots to include new word
//                  return

// Scan compatible words for the given slot, starting from current index.
// If find one that's usable (crossing words still have compat words)
// install it and return true
//
// For each linked position and each possible letter (a-z) either
// - we haven't checked it yet
// - we checked and it's OK (the linked slot had compatible words)
// - we checked and it's not OK
//
// so when scanning words:
//  if any letter not checked, check it for all linked slots
//  if any letter not OK, skip word
//
bool SLOT::find_next_usable_word(GRID *grid) {
    if (!compatible_words) return false;
    if (next_word_index == 0) {
        clear_usable_letter_checked();
    }
    int n = compatible_words->size();
#if VERBOSE_NEXT_USABLE
    printf("find_next_usable_word() slot %d: %d of %d\n",
        num, next_word_index, n
    );
    printf("   stack pattern %s\n", filled_pattern);
#endif
    while (next_word_index < n) {
        int ind = (*compatible_words)[next_word_index++];
        char* w = words.words[len][ind];
#if VERBOSE_NEXT_USABLE
        printf("   checking %s\n", w);
#endif
        bool usable = true;
        for (int i=0; i<len; i++) {
            if (links[i].empty()) continue;
            if (filled_pattern[i] != '_') continue;
            char c = w[i];
            int nc = c-'a';
            if (!usable_letter_checked[i][nc]) {
                usable_letter_checked[i][nc] = true;
                bool x = letter_compatible(i, c);
                usable_letter_ok[i][nc] = x;
#if CHECK_ASSERTS
            } else {
                bool x = letter_compatible(i, c);
                if (x != usable_letter_ok[i][nc]) {
                    printf("USABLE inconsistent flag i %d char %c x %d mw %s\n", i, c, x, w);
                    exit(1);
                }
#endif
            }
            if (!usable_letter_ok[i][nc]) {
                usable = false;
                break;
            }
        }
#if NO_DUPS
        for (SLOT *s2: grid->filled_slots) {
            if (!strcmp(w, s2->current_word)) {
                usable = false;
                dup_stack_level = s2->stack_level;
                break;
            }
        }
#endif
        if (usable) {
#if VERBOSE_NEXT_USABLE
            printf("   %s is usable for slot %d\n", w, num);
            //print_usable();
#endif
            strcpy(current_word, w);
            return true;
        }
    }
#if VERBOSE_NEXT_USABLE
    printf("   no compat words are usable for slot %d\n", num);
    print_usable();
#endif
    return false;
}

// see if given letter in given crossed position is compatible with xword
//
bool SLOT::letter_compatible(int pos, char c) {
    LINK &link = links[pos];
    SLOT* slot2 = link.other_slot;
    if (slot2->filled) return true;
    char pattern2[MAX_LEN];
    strcpy(pattern2, slot2->filled_pattern);
    pattern2[link.other_pos] = c;
    return slot2->check_pattern(pattern2);
}

// mp differs from current mpattern by 1 additional letter.
// see if this slot has an compatible word matching this
// (only need to check words compatible with current filled_pattern)
//
bool SLOT::check_pattern(char* mp) {
    for (int i: *compatible_words) {
        if (match(len, mp, words.words[len][i])) {
            return true;
        }
    }
    return false;
}

// Find the unfilled slot with fewest compatible words
// if any of these are usable,
// mark slot as filled, push on stack, return true
// Else return false (need to backtrack)
// precondition:
//      there are unfilled slots
//      compat lists of unfilled slots are updated and nonempty
//
bool GRID::fill_next_slot() {
    // find unfilled slot with smallest compat set
    //
    size_t nbest = 9999999;
    SLOT* best=0;
#if VERBOSE_FILL_NEXT_SLOT
    printf("fill_next_slot():\n");
#endif
    for (SLOT* slot: slots) {
        if (slot->filled) continue;
        size_t n = slot->compatible_words->size();
#if VERBOSE_FILL_NEXT_SLOT
        printf("   slot %d, %ld compatible words\n",
            slot->num, n
        );
#endif
        if (n < nbest) {
            nbest = n;
            best = slot;
        }
    }
#if CHECK_ASSERTS
    if (!best) {
        printf("no unfilled slot\n");
        exit(1);
    }
#endif

    best->next_word_index = 0;
    if (best->find_next_usable_word(this)) {
#if VERBOSE_FILL_NEXT_SLOT
        printf("   slot %d has usable words; pushing on filled stack\n", best->num);
#endif
        best->filled = true;
#if CHECK_ASSERTS
        if (find(filled_slots.begin(), filled_slots.end(), best) != filled_slots.end()) {
            printf("slot %d is already in filled stack\n", best->num);
            exit(1);
        }
#endif
        best->stack_level = filled_slots.size();
        filled_slots.push_back(best);
        fill_slot(best);
        return true;
    } else {
#if VERBOSE_FILL_NEXT_SLOT
        printf("   slot %d has no usable words\n", best->num);
#endif
        return false;
    }
}

// we've found a usable word for the given slot.
// for each position where its pattern was _:
// in the linked slot, update the pattern and the compatible_words list.
// If the pattern is full, mark slot as filled and push
//
void GRID::fill_slot(SLOT* slot) {
#if VERBOSE_FILL_SLOT
    printf("fill_slot(): filling %s in slot %d\n", slot->current_word, slot->num);
#endif
    for (int i=0; i<slot->len; i++) {
        LINK &link = slot->links[i];
        if (link.empty()) continue;
        char c = slot->filled_pattern[i];
        if (c != '_') continue;
        SLOT *slot2 = link.other_slot;
        slot2->filled_pattern[link.other_pos] = slot->current_word[i];
        if (strchr(slot2->filled_pattern, '_')) {
            slot2->compatible_words = pattern_cache[slot2->len].get_list(
                slot2->filled_pattern
            );
#if VERBOSE_FILL_SLOT
            printf("   slot %d now has %ld compat words for pattern %s\n",
                slot2->num, slot2->compatible_words->size(),
                slot2->filled_pattern
            );
#endif
            if (slot2->compatible_words->empty()) {
                printf("empty compat list for slot %d pattern %s\n",
                    slot2->num, slot2->filled_pattern
                );
                exit(1);
            }
        } else {
#if CHECK_ASSERTS
            if (find(filled_slots.begin(), filled_slots.end(), slot2) != filled_slots.end()) {
                printf("slot %d is already in filled stack\n", slot2->num);
                exit(1);
            }
#endif
            // other slot is now filled
#if VERBOSE_FILL_SLOT
            printf("   slot %d is now filled: %s\n",
                slot2->num, slot2->filled_pattern
            );
#endif
            slot2->compatible_words = NULL;
            slot2->filled = true;
            strcpy(slot2->current_word, slot2->filled_pattern);
            slot2->stack_level = filled_slots.size();
            filled_slots.push_back(slot2);
        }
    }
}

// We just popped this slot S from the stack.
// Find the level of the topmost filled slot that affects it, i.e.
// - had a dup word conflict
// - intersects S
// - intersects an unfilled slot that intersects S
//
// This is used for "jumptracking": if we couldn't find a word for this slot,
// we want to backtrack all the way to a slot that will make a difference
//
int SLOT::top_affecting_level() {
    int max_level=-1;
    if (dup_stack_level >= 0) {
        max_level = dup_stack_level;
        if (max_level == stack_level-1) return max_level;
    }
    for (int i=0; i<len; i++) {
        LINK &link = links[i];
        if (link.empty()) continue;
        SLOT* slot2 = link.other_slot;
        if (slot2->filled) {
            if (slot2->stack_level > max_level) {
                max_level = slot2->stack_level;
                if (max_level == stack_level-1) return max_level;
            }
        } else {
            for (int j=0; j<slot2->len; j++) {
                LINK &link2 = slot2->links[j];
                if (link2.empty()) continue;
                SLOT* slot3 = link2.other_slot;
                if (slot3->filled) {
                    if (slot3->stack_level > max_level) {
                        max_level = slot3->stack_level;
                        if (max_level == stack_level-1) return max_level;
                    }
                }
            }
        }
    }
    return max_level;
}

// We're undoing a filled word.
// Update filled_patterns of unfilled crossing slots
//
void SLOT::remove_filled_word() {
    for (int i=0; i<len; i++) {
        LINK &link = links[i];
        if (link.empty()) continue;
        SLOT* slot2 = link.other_slot;
        if (slot2->filled) continue;
        slot2->filled_pattern[link.other_pos] = '_';
        slot2->compatible_words = pattern_cache[slot2->len].get_list(
            slot2->filled_pattern
        );
        if (slot2->compatible_words->empty()) {
            // should never get here
            printf("   empty compat list for slot %d pattern %s\n",
                slot2->num, slot2->filled_pattern
            );
            exit(1);
        }
    }
}

// Remove current word for the slot S on top of the filled stack,
// and update compat word lists for crossing slots
// Look for next usable word for S.
// if find one: add it, update crossing slots, and return true
// else pop S and repeat for next slot down on stack
//
bool GRID::backtrack() {
    while (1) {
        SLOT *slot = filled_slots.back();
#if VERBOSE_BACKTRACK
        printf("backtrack() to slot %d\n", slot->num);
#endif
        slot->remove_filled_word();
        if (slot->find_next_usable_word(this)) {
            fill_slot(slot);
            return true;
        }

#if VERBOSE_BACKTRACK
        printf("slot %d has no more usable words; popping\n", slot->num);
#endif
        filled_slots.pop_back();
        slot->filled = false;
        if (filled_slots.empty()) {
            return false;
        }
        int level = slot->top_affecting_level();
        while (filled_slots.size() > level+1) {
            slot = filled_slots.back();
            slot->remove_filled_word();
            slot->filled = false;
            filled_slots.pop_back();
        }
    }
}

j
bool GRID::find_solutions(bool curses, double period) {
    static int count = 0;
    while (1) {
        if (filled_slots.size() + npreset_slots == slots.size()) {
            // we have a solution
            if (curses) {
                clear();
                refresh();
                endwin();
            }
            printf("\nSolution found:\n");
            print_grid(*this, false);
            printf("enter command\n"
                "s filename: append solution to file (default 'solutions')\n"
                "<CR>: next solution\n"
                "v word: add word to veto list\n> "
                "r: restart with new random word order\n> "
                "q: quit\n> "
            );
            char buf[256];
            fgets(buf, sizeof(buf), stdin);
            if (buf[0] != '\n') break;
            backtrack();
            if (curses) {
                initscr();
            }
            continue;
        }
        if (!fill_next_slot()) {
            if (!backtrack()) {
                break;
            }
        }
        count++;
        if (count == 10000) {
            count = 0;
            print_grid(*this, curses);
        }
#if VERBOSE_STEP_STATE
        print_state();
#endif
    }
    printf("no more solutions\n");
}

int main(int argc, char** argv) {
    GRID grid;
    bool curses = true;
    bool show_grid = false;
    double period;
    const char* word_list = DEFAULT_WORD_LIST;
    const char* grid_file = NULL;

    for (int i=1; i<argc; i++) {
        if (!strcmp(argv[i], "--word_list")) {
            word_list = argv[++i];
        } else if (!strcmp(argv[i], "--grid_file")) {
            grid_file = argv[++i];
        } else if (!strcmp(argv[i], "--curses")) {
            if (atoi(argv[++i]) == 0) curses = false;
        } else if (!strcmp(argv[i], "--show_grid")) {
            show_grid = true;
        } else if (!strcmp(argv[i], "--period")) {
            period = atof(argv[++i]);
        }
    }
    words.read(word_list);
    words.shuffle();
    init_pattern_cache();
    make_grid(grid_file, grid);
    grid.prepare_grid();
    if (show_grid) {
        grid.print_state(true);
        exit(0);
    }
    if (curses) {
        initscr();
    }
    grid.find_solutions(curses, period);
    if (curses) {
        endwin();
    }
}
