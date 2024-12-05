#include <cstdio>
#include <cstring>
#include <vector>
#include <stack>
#include <deque>
#include <unordered_map>
#include <algorithm>

using namespace std;

#define VERBOSE     0
#define DEBUG       0
    // do sanity checks
#define WORD_FILE   "words"

// Crossword puzzle (generalized) grid filler.

// A 'grid' is a set of 'slots',
// each of which holds a word of a fixed length.
// A 'cell' (letter space) in a slot can be linked to a cell in another slot.
// Use add_slot() and add_link() to describe this.
// This can also represent
// - higher-dimensional grids
// - grids on tori or Klein bottles
// - other weird things
// as well as conventional 2D grids
// Note: currently a cell can't be shared by >2 slots,
// but this shouldn't be hard to add.
//
// This program enumerates all solutions for a given grid.

// Other terms
// 'pattern': a word in which some or all positions are undetermined
// (represented by _)

// copyright (C) 2024 David P. Anderson

///////////// WORD LISTS AND PATTERNS //////////////

#define MAX_LEN 29
    // longest word plus 1 for NULL

typedef vector<char*> WLIST;
typedef vector<int> ILIST;
typedef bool MASK[MAX_LEN];

struct WORDS {
    WLIST words[MAX_LEN+1];
    int nwords[MAX_LEN+1];
    int max_len;

    // read words from file into per-length vectors
    //
    void read() {
        FILE* f = fopen(WORD_FILE, "r");
        char buf[256];
        max_len = 0;
        while (fgets(buf, 256, f)) {
            int len = strlen(buf)-1;
            buf[len] = 0;
            if (len>max_len) {
                max_len = len;
            }
            nwords[len]++;
            words[len].push_back(strdup(buf));
        }
    }
    void print_counts() {
        printf("%d\n", max_len);
        for (int i=1; i<=MAX_LEN; i++) {
            printf("%d: %d\n", i, nwords[i]);
        }
    }
} words;

// a 'pattern' has '_' for wildcard.

char* NULL_PATTERN = (char*)"____________________________";

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
};

// for each word len, cache of pattern -> ILIST pairs
//
PATTERN_CACHE pattern_cache[MAX_LEN];

void init_pattern_cache() {
    for (int i=1; i<=MAX_LEN; i++) {
        pattern_cache[i].init(i, &(words.words[i]));
    }
}

////////////////// SLOTS AND GRIDS ////////////////

struct SLOT;

// link from a position in a slot to a position in another slot.
//
struct LINK {
    SLOT *other_slot;       // NULL if no link
    int other_pos;
    inline bool empty() {
        return other_slot == NULL;
    }
};

typedef enum {LETTER_UNKNOWN, LETTER_OK, LETTER_NOT_OK} LETTER_STATUS;

struct SLOT {
    int num;        // number in grid (arbitrary)
    int len;
    LINK links[MAX_LEN];

    bool filled;
        // is this slot filled?
    char filled_pattern[MAX_LEN];
        // pattern of letters from crossing filled slots lower on stack
    ILIST *compatible_words;
        // words compatible with this pattern
    int next_word_index;
        // next one to try
    char current_word[MAX_LEN];
        // if filled, current word

    // for each position and each letter (a-z)
    // keep track of whether putting the letter in that position
    // was OK (nonzero compatible words in the linked slot).
    // These must be cleared each time we fill this slot.
    //
    bool usable_letter_checked[MAX_LEN][26];
    bool usable_letter_ok[MAX_LEN][26];

    SLOT(int _len, int _num) {
        len = _len;
        num = _num;
    }
    void clear_usable_letter_checked() {
        memset(usable_letter_checked, 0, sizeof(usable_letter_checked));
    }

    // debugging
    void print_usable() {
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

    void add_link(int this_pos, SLOT* other_slot, int other_pos) {
        LINK &link = links[this_pos];
        if (link.other_slot) {
            printf("slot %d, pos %d: already linked\n", num, this_pos);
            exit(1);
        }
        link.other_slot = other_slot;
        link.other_pos = other_pos;
    }

    void words_init() {
        // initialize pattern and compatible word list
        strcpy(filled_pattern, NULL_PATTERN);
        filled_pattern[len] = 0;
        compatible_words = pattern_cache[len].get_list(filled_pattern);
    }

    void print_state() {
        printf("slot %d:\n", num);
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
    }

    bool find_next_usable_word();
    bool letter_compatible(int pos, char c);
    bool check_pattern(char* mp);
};

struct GRID {
    int slot_num;
    vector<SLOT*> slots;
    stack<SLOT*> filled_slots;

    SLOT* add_slot(int len) {
        SLOT *slot = new SLOT(len, slot_num++);
        slots.push_back(slot);
        return slot;
    }
    void add_link(SLOT *slot1, int pos1, SLOT *slot2, int pos2) {
        slot1->add_link(pos1, slot2, pos2);
        slot2->add_link(pos2, slot1, pos1);
    }
    void print_solution() {
        printf("------ solution --------\n");
        for (SLOT *slot: slots) {
            printf("%d: %s\n", slot->num, slot->current_word);
        }
    }
    void print_state() {
        printf("------- state ----------\n");
        for (SLOT *slot: slots) {
            slot->print_state();
        }
        printf("USABLE filled slots: ");
        deque<SLOT*>* d = (deque<SLOT*>*)&filled_slots;
        for (int i=0; i<d->size(); i++) {
            SLOT *slot = (*d)[i];
            printf(" %d", slot->num);
        }
        printf("\n------- end ----------\n");
    }

    // call this after adding slots and links
    void prepare() {
        for (SLOT *s: slots) {
            s->words_init();
            s->filled = false;
        }
    }

    bool fill_next_slot();
    bool backtrack();
    bool fill();
    void fill_slot(SLOT*);
};

// parse black-square grid
//
// *aaaaa*
// a*a*aaa
// aaaaa*a
// aaa***a

void read_grid() {
}

void make_test_grid(GRID &grid) {
    SLOT *slot0 = grid.add_slot(10);
    SLOT *slot1 = grid.add_slot(6);
    SLOT *slot2 = grid.add_slot(4);
    SLOT *slot3 = grid.add_slot(5);
    grid.add_link(slot0, 3, slot2, 1);
    grid.add_link(slot1, 2, slot2, 3);
    grid.add_link(slot0, 6, slot3, 1);
    grid.add_link(slot1, 5, slot3, 3);
}

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

void print_square_grid(GRID &grid, int len) {
    for (int i=0; i<len; i++) {
        SLOT *slot = grid.slots[i];
        printf("%s\n", slot->filled?slot->current_word:slot->filled_pattern);
    }
}

////////////////// GRID-FILL ALGORITHMS ////////////////

// Scan compatible words for the given slot, starting from current index.
// If find one that's usable (crossing words still have compat words)
// install it and return true
//
// For each linked position and each possible letter (a-z) either
// - we haven't checked it yet
// - we checked and it's OK
// - we checked and it's not OK
//
// so when scanning words:
//  if any letter not checked, check it for all linked slots
//  if any letter not OK, skip word
//
bool SLOT::find_next_usable_word() {
    if (!compatible_words) return false;
    if (next_word_index == 0) {
        clear_usable_letter_checked();
    }
    int n = compatible_words->size();
#if VERBOSE
    printf("slot %d: find next usable word; %d of %d\n",
        num, next_word_index, n
    );
    printf("   stack pattern %s\n", filled_pattern);
#endif
    while (next_word_index < n) {
        int ind = (*compatible_words)[next_word_index++];
        char* w = words.words[len][ind];
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
#if DEBUG
                if (num==4 && i==0 && c=='a') {
                    printf("USABLE setting 4/0/a to %d\n", x);
                }
            } else {
                bool x = letter_compatible(i, c);
                if (x != usable_letter_ok[i][nc]) {
                    printf("USABLE inconsistent flag i %d char %c x %d mw %s\n", i, c, x, mw);
                    exit(1);
                }
#endif
            }
            if (!usable_letter_ok[i][nc]) {
                usable = false;
                break;
            }
        }
        if (usable) {
#if VERBOSE
            printf("%s is usable for slot %d\n", w, num);
            print_usable();
#endif
            strcpy(current_word, w);
            return true;
        }
    }
#if VERBOSE
    printf("no compat words are usable for slot %d\n", num);
    print_usable();
#endif
    return false;
}

// see if given letter in given crossed position is compatible with xword
//
bool SLOT::letter_compatible(int pos, char c) {
    LINK &link = links[pos];
    SLOT* slot2 = link.other_slot;
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
    SLOT* best;
#if VERBOSE
    printf("fill_next_slot():\n");
#endif
    for (SLOT* slot: slots) {
        if (slot->filled) continue;
        size_t n = slot->compatible_words->size();
#if VERBOSE
        printf("   slot %d, %ld compatible words\n",
            slot->num, n
        );
#endif
        if (n < nbest) {
            nbest = n;
            best = slot;
        }
    }

    best->next_word_index = 0;
    if (best->find_next_usable_word()) {
#if VERBOSE
        printf("   slot %d has usable words; pushing\n", best->num);
#endif
        best->filled = true;
        filled_slots.push(best);
        fill_slot(best);
        return true;
    } else {
#if VERBOSE
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
#if VERBOSE
    printf("filling %s in slot %d\n", slot->current_word, slot->num);
#endif
    for (int i=0; i<slot->len; i++) {
        LINK &link = slot->links[i];
        if (link.empty()) continue;
        char c = slot->filled_pattern[i];
        if (c != '_') continue;
        SLOT *slot2 = link.other_slot;
        slot2->filled_pattern[link.other_pos] = slot->current_word[i];
        if (strchr(slot2->filled_pattern, '_')) {
            slot2->compatible_words = pattern_cache[slot->len].get_list(
                slot2->filled_pattern
            );
            if (slot2->compatible_words->empty()) {
                printf("empty compat list for slot %d pattern %s\n",
                    slot2->num, slot2->filled_pattern
                );
                exit(1);
            }
        } else {
            // other slot is now filled
            slot2->compatible_words = NULL;
            slot2->filled = true;
            strcpy(slot2->current_word, slot2->filled_pattern);
            filled_slots.push(slot2);
        }
    }
}

// for the slot S on top of the filled stack:
// unlink current word.
// look for next usable word.
// if find one, link it and return true
// else pop S and repeat for next slot down on stack
//
bool GRID::backtrack() {
    while (1) {
        SLOT *slot = filled_slots.top();
#if VERBOSE
        printf("backtracking to slot %d\n", slot->num);
#endif
        // update filled_patterns of unfilled crossing slots
        //
        for (int i=0; i<slot->len; i++) {
            LINK &link = slot->links[i];
            if (link.empty()) continue;
            SLOT* slot2 = link.other_slot;
            if (slot2->filled) continue;
            slot2->filled_pattern[link.other_pos] = '_';
            slot2->compatible_words = pattern_cache[slot->len].get_list(
                slot2->filled_pattern
            );
            if (slot2->compatible_words->empty()) {
                printf("empty compat list for slot %d pattern %s\n",
                    slot2->num, slot2->filled_pattern
                );
                exit(1);
            }
        }
        if (slot->find_next_usable_word()) {
            fill_slot(slot);
            return true;
        }

#if VERBOSE
        printf("slot %d has no more usable words; popping\n", slot->num);
#endif
        filled_slots.pop();
        slot->filled = false;
        if (filled_slots.empty()) {
            return false;
        }
        slot = filled_slots.top();
    }
}

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

bool GRID::fill() {
    while (1) {
        if (filled_slots.size() == slots.size()) {
#if VERBOSE
            printf("All slots filled; we're done here\n");
#endif
            //return true;
            print_solution();
            backtrack();
            continue;
        }
        if (!fill_next_slot()) {
            if (!backtrack()) {
                return false;
            }
        }
#if VERBOSE
        print_square_grid(*this, 5);
        print_state();
#endif
    }
}

//////////////////

void test_match() {
    char *p = (char*)"c_a__";
    ILIST ilist;
    get_matches(5, p, words.words[5], ilist);
    show_matches(5, words.words[5], ilist);
}

int main(int, char**) {
    GRID grid;
    words.read();
    init_pattern_cache();
    //make_test_grid(grid);
    make_square_grid(grid, 6);
    grid.prepare();
    if (grid.fill()) {
        grid.print_solution();
    } else {
        printf("no solution\n");
    }
}
