#include <cstdio>
#include <cstring>
#include <vector>
#include <stack>
#include <unordered_map>
#include <algorithm>

using namespace std;

// Crossword puzzle (generalized) grid filler.
//
// A 'grid' is a set of 'slots',
// each of which holds a word of a fixed length.
// A 'cell' (letter space) in a slot can be linked to a cell in another slot.
// Use add_slot() and add_link() to describe this.
// This can representalso
// - higher-dimensional grids
// - grids on tori or Klein bottles
// - other weird things
// as well as conventional 2D grids
// Note: currently a cell can't be shared by >2 slots,
// but this shouldn't be hard to add.
//
// For a given slot S, mask(S) is the bitmask of the linked positions.
// If W is a word and M is a mask,
// mword(W, M) is the letters in W in masked positions,
// i.e. the crossed letters in W.
//
// For purposes of grid-filling, only mwords matter.
// So we convert the original grid to a form using mwords instead of words;
// in this form, every cell is linked, i.e. crossed
//
// A solution is an assignment of mwords to slots.
// For each slot there is a set of (actual) words that match the mword.
// For an (actual) solution you can pick any word from each set.
//
// This program enumerates all solutions for a given grid.

// Other terms
// 'pattern': a word (or mword) in which some or all positions are undetermined
// (represented by _)

// copyright (C) 2024 David P. Anderson

#define VERBOSE     1

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
        FILE* f = fopen("words", "r");
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

char* NULL_PATTERN = (char*)"_____________________________________________";

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

char* mword_example(int len, char* w, MASK mask) {
    char pattern[MAX_LEN];
    int j=0;
    for (int i=0; i<len; i++) {
        pattern[i] = mask[i]?w[j++]:'_';
    }
    pattern[len] = 0;
    for (char *w: words.words[len]) {
        if (match(len, pattern, w)) {
            return w;
        }
    }
    return (char*)"not found";
}

// for a given word list,
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

// get list of mwords for given (len, mask)
//
void get_mwords_aux(int len, MASK mask, WLIST &wlist) {
    vector<string> mw;
    for (char* word: words.words[len]) {
        char mword[MAX_LEN];
        int j = 0;
        for (int i=0; i<len; i++) {
            if (mask[i]) {
                mword[j++] = word[i];
            }
        }
        mword[j] = 0;
        mw.push_back(mword);
    }
    sort(mw.begin(), mw.end());
    auto last = std::unique(mw.begin(), mw.end());
    mw.erase(last, mw.end());

    for (string s: mw) {
        wlist.push_back(strdup(s.c_str()));
    }
}

////////////////// SLOTS AND GRIDS ////////////////

struct SLOT;

// link from a position in a slot to a position in another slot.
//
struct LINK {
    SLOT *other_slot;       // NULL if no link
    int other_pos;
};

typedef enum {LETTER_UNKNOWN, LETTER_OK, LETTER_NOT_OK} LETTER_STATUS;

struct SLOT {
    int num;        // number in grid (arbitrary)
    int len;
    LINK links[MAX_LEN];

    // masked items; fill in after links done
    MASK mask;
    int mlen;
    int mpos[MAX_LEN];  // mask position of cell i
    LINK mlinks[MAX_LEN];
    WLIST mwords;
    PATTERN_CACHE pattern_cache;
        // cache of pattern -> ILIST pairs

    bool filled;
    char mpattern[MAX_LEN];
        // mword pattern from filled slots
    ILIST *compatible_mwords;
        // mwords compatible with this pattern
    int next_mword_index;
        // next one to try

    bool usable_letter_checked[MAX_LEN][26];
    bool usable_letter_ok[MAX_LEN][26];

    SLOT(int _len, int _num) {
        len = _len;
        num = _num;
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

    // get ordinals of linked cells
    void mpos_init() {
        int j = 0;
        for (int i=0; i<len; i++) {
            if (links[i].other_slot) {
                mpos[i] = j++;
            }
        }
        mlen = j;
    }

    // compute mask links
    void mlinks_init() {
        int j=0;
        for (int i=0; i<len; i++) {
            LINK &link = links[i];
            if (!link.other_slot) continue;
            SLOT *slot2 = link.other_slot;
            LINK &link2 = mlinks[j];
            link2.other_slot = slot2;
            link2.other_pos = slot2->mpos[link.other_pos];
            j++;
        }
    }

    void print_mlinks() {
        printf("Slot %d:\n", num);
        for (int i=0; i<mlen; i++) {
            printf("   pos %d:\n", i);
            LINK &link = mlinks[i];
            printf("      slot %d, pos %d\n",
                link.other_slot->num, link.other_pos
            );
        }
    }

    void mwords_init() {
        // get the slot's list of mwords
        for (int i=0; i<len; i++) {
            mask[i] = (links[i].other_slot != NULL);
        }
        get_mwords_aux(len, mask, mwords);

        // initialize pattern and compatible word list
        strcpy(mpattern, NULL_PATTERN);
        pattern_cache.init(mlen, &mwords);
        compatible_mwords = pattern_cache.get_list(mpattern);
    }

    void print_mwords() {
        printf("Slot %d:\n", num);
        int i=0;
        for (char* w: mwords) {
            printf("   %s (%s)\n", w, mword_example(len, w, mask));
            i++;
            if (i > 4) break;
        }
    }

    bool find_next_usable_mword();
    bool letter_compatible(int mpos, char c);
    bool check_mpattern(char* mp);
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
    void print_mlinks() {
        printf("Mlinks:\n");
        for (SLOT *s: slots) {
            s->print_mlinks();
        }
    }
    void print_mwords() {
        printf("Mwords:\n");
        for (SLOT *s: slots) {
            s->print_mwords();
        }
    }
    void print_solution() {
        for (unsigned int i=0; i<slots.size(); i++) {
            printf("%d: %s\n", i, slots[i]->mpattern);
        }
    }

    // call this after adding slots and links
    void prepare() {
        for (SLOT *s: slots) {
            s->mpos_init();
        }
        for (SLOT *s: slots) {
            s->mlinks_init();
            s->mwords_init();
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

////////////////// GRID-FILL ALGORITHMS ////////////////

// Scan compatible mwords for the given slot, starting from current index.
// If find one that's usable (crossing words still have compat mwords)
// install it and return true
//
// each position in the mword links to an xword
// for each position and each possible letter (a-z) either
// - we haven't checked it yet
// - we checked and it's OK
// - we checked and it's not OK
//
// so when scanning mwords:
//  if any letter not checked, check it for all linked slots
//  if any letter not OK, skip word
//
bool SLOT::find_next_usable_mword() {
    if (!compatible_mwords) return false;
    int n = compatible_mwords->size();
#if VERBOSE
    printf("slot %d: find next usable mword; %d of %d\n",
        num, next_mword_index, n
    );
#endif
    while (next_mword_index < n) {
        char* mw = mwords[(*compatible_mwords)[next_mword_index]];
        bool usable = true;
        for (int i=0; i<mlen; i++) {
            char c = mw[i];
            if (!usable_letter_checked[i][c]) {
                usable_letter_checked[i][c] = true;
                usable_letter_ok[i][c] = letter_compatible(i, c);
            }
            if (usable_letter_ok[i][c]) {
                continue;
            } else {
                usable = false;
                break;
            }
        }
#if VERBOSE
        printf("  %s is%s usable\n", mw, usable?"":" not");
#endif
        if (usable) {
            return true;
        }
        next_mword_index++;
    }
    return false;
}

// see if given letter in given position is compatible with xword
//
bool SLOT::letter_compatible(int mpos, char c) {
    LINK &link = mlinks[mpos];
    SLOT* slot2 = link.other_slot;
    char pattern2[MAX_LEN];
    strcpy(pattern2, slot2->mpattern);
    pattern2[link.other_pos] = c;
    if (!slot2->check_mpattern(pattern2)) {
        return false;
    }
    return true;
}

// mp differs from current mpattern by 1 additional letter.
// see if this slot has an mword matching this
// (only check mwords compatible with current mpattern)
//
bool SLOT::check_mpattern(char* mp) {
    for (int i: *compatible_mwords) {
        if (match(len, mp, mwords[i])) {
            return true;
        }
    }
    return false;
}

// precondition:
//      there are unfilled slots
//      compat lists of unfilled slots are updated and nonempty
// return:
//      false if we chose a slot but it had no usable words.
//          This means we need to backtrack
//      true: we chose a slot and pushed it on filled stack
//
bool GRID::fill_next_slot() {
    // find unfilled slot with smallest compat set
    //
    size_t nbest = 9999999;
    SLOT* best;
    for (SLOT* slot: slots) {
        if (slot->filled) continue;
        size_t n = slot->compatible_mwords->size();
        if (n < nbest) {
            nbest = n;
            best = slot;
        }
    }

    if (best->find_next_usable_mword()) {
        filled_slots.push(best);
        fill_slot(best);
        return true;
    } else {
        return false;
    }
}

// we've found a usable mword for the given slot.
// for each position where its pattern was _:
// in the linked slot, update the pattern and the compatible_mwords list.
// If the pattern is full, mark slot as filled and push
//
void GRID::fill_slot(SLOT* slot) {
    for (int i=0; i<slot->mlen; i++) {
        char c = slot->mpattern[i];
        if (c != '_') continue;
        LINK &link = slot->mlinks[i];
        SLOT *slot2 = link.other_slot;
        slot2->mpattern[link.other_pos] = c;
        if (strchr(slot2->mpattern, '_')) {
            slot2->compatible_mwords = slot2->pattern_cache.get_list(
                slot2->mpattern
            );
        } else {
            // other slot is now filled
            slot2->compatible_mwords = NULL;
            slot2->filled = true;
            filled_slots.push(slot2);
        }
    }
}

// the slot on top of the filled stack has no usable words.
// pop it, and look for a slot with another usable mword
//
bool GRID::backtrack() {
    while (1) {
        SLOT *slot = filled_slots.top();
        filled_slots.pop();
        slot->filled = false;
        if (filled_slots.empty()) {
            return false;
        }
        slot = filled_slots.top();
        if (slot->find_next_usable_mword()) {
            fill_slot(slot);
            return true;
        }
    }
}

bool GRID::fill() {
    while (1) {
        if (filled_slots.size() == slots.size()) {
            return true;
        }
        if (!fill_next_slot()) {
            if (!backtrack()) {
                return false;
            }
        }
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
    make_test_grid(grid);
    grid.prepare();
    grid.print_mlinks();
    grid.print_mwords();
#if 0
    if (fill()) {
        grid.print_solution();
    } else {
        printf("no solution\n");
    }
#endif
}
