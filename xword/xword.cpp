#include <cstdio>
#include <cstring>
#include <vector>
#include <stack>
#include <unordered_map>
#include <algorithm>

using namespace std;

// Crossword puzzle (generalized) grid filler.
//
// A 'grid' is a set of slots, each of which holds a word of a fixed length.
// A cell (letter space) in a slot can be linked to one or more
// cells in other slots.
// This can represent conventional 2D grids and also
// - higher-dimensional grids
// - grids on tori or Klein bottles
// - other weird things
//
// For a given slot S, mask(S) is the bitmask of the positions with links.
// If W is a word an M is a mask,
// mword(W, M) is the letters in W in masked positions,
// i.e. the crossed letters in W.
//
// For purposes of grid-filling, only mwords matter.
// So we convert the original grid to a form using mwords instead of words;
// in this form, every cell is linked i.e. crossed
//
// A solution is an assignment of mwords to slots.
// For each slot there is a set of (actual) words that match the mword.
// For an (actual) solution you can pick any word from each set.
//
// This program enumerates all solutions for a given grid.

// Other terms
// 'pattern': an mword in which some or all positions are undetermined
// (represented by _)

// copyright (C) 2024 David P. Anderson

///////////// STUFF RELATED TO WORD LISTS AND PATTERNS //////////////

#define MAX_LEN 28

typedef vector<char*> WLIST;
typedef vector<int> ILIST;

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
};

WORDS words;

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

// for a given work list,
// cache a mapping of pattern -> word index list
//
struct LIST_CACHE {
    int len;
    WLIST *wlist;
    unordered_map<string, ILIST*> map;

    LIST_CACHE(int _len, WLIST *_wlist) {
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

typedef bool MASK[MAX_LEN];

// get list of mwords for given (len, mask)
//
void get_mwords(int len, MASK mask, WLIST &wlist) {
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
// there can be multiple links for a given position
struct LINK {
    SLOT *other_slot;
    int other_pos;

    LINK(SLOT* _other_slot, int _other_pos) {
        other_slot = _other_slot;
        other_pos = _other_pos;
    }
};

struct SLOT {
    int num;        // number in grid (arbitrary)
    int len;
    vector<LINK> links[MAX_LEN];

    // masked items; fill in after links done
    int mlen;
    int mpos[MAX_LEN];  // mask position of cell i
    vector<LINK> mlinks[MAX_LEN];
    WLIST *mwords;

    bool filled;
    char mpattern[MAX_LEN];
    ILIST *compatible_mwords;

    SLOT(int _len, int _num) {
        len = _len;
        num = _num;
        filled = false;
        memset(mpattern, '_', sizeof(mpattern));
        mpattern[len] = 0;
    }
    void add_link(int this_pos, SLOT* other_slot, int other_pos) {
        LINK link(other_slot, other_pos);
        links[this_pos].push_back(link);
    }

    // get ordinals of crossing positions
    void get_mpos() {
        int j = 0;
        for (int i=0; i<len; i++) {
            if (!links[i].empty()) {
                mpos[i] = j++;
            }
        }
        mlen = j;
    }

    // compute mask links
    void get_mlinks() {
        int j=0;
        for (int i=0; i<len; i++) {
            if (links[i].empty()) continue;
            for (LINK &link: links[i]) {
                SLOT *slot2 = link.other_slot;
                LINK newlink(slot2, slot2->mpos[link.other_pos]);
                mlinks[j].push_back(newlink);
            }
            j++;
        }
    }

    void print_mlinks() {
        printf("Slot %d:\n", num);
        for (int i=0; i<mlen; i++) {
            printf("   pos %d:\n", i);
            for (LINK &link: mlinks[i]) {
                printf("      slot %d, pos %d\n",
                    link.other_slot->num, link.other_pos
                );
            }
        }
    }

    void get_mwords() {
    }

    void print_mwords() {
    }

};

struct GRID {
    int slot_num;
    vector<SLOT*> slots;

    SLOT* add_slot(int len) {
        SLOT *slot = new SLOT(len, slot_num++);
        slots.push_back(slot);
        return slot;
    }
    void add_link(SLOT *slot1, int pos1, SLOT *slot2, int pos2) {
        slot1->add_link(pos1, slot2, pos2);
        slot2->add_link(pos2, slot1, pos1);
    }
    void get_mlinks() {
        for (SLOT *s: slots) {
            s->get_mpos();
        }
        for (SLOT *s: slots) {
            s->get_mlinks();
        }
    }
    void print_mlinks() {
        for (SLOT *s: slots) {
            s->print_mlinks();
        }
    }
    void get_mwords() {
        for (SLOT *s: slots) {
            s->get_mwords();
        }
    }
    void print_mwords() {
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
        get_mlinks();
        get_mwords();
    }
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

//////////////////

GRID grid;

#if 0
stack<SLOT*> filled_slots;

// Scan compatible words starting from current index.
// Consider only words that differ from current word
// in at least one crossing position.
// If find one that's usable (crossing words still have compat words)
// install it and return true
//
bool find_next_usable(SLOT *slot) {
    while (slot->compat_index < slot->ncompat) {
        // scan positions.
        for (int i=0; i<slot->len; i++) {
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
bool fill_next_slot() {
    // find unfilled slot with smallest compat set
    //
    int nbest = 9999999;
    SLOT* best;
    for (SLOT* slot: grid.slots) {
        if (slot->filled) continue;
        if (slot->ncompat < nbest) {
            nbest = slot->ncompat;
            best = slot;
        }
    }

    if (find_next_usable(best)) {
        filled_slots.push(best);
        return true;
    } else {
        return false;
    }
}

bool fill() {
    for (SLOT* slot: grid.slots) {
        slot->compatible = words.all(slot->len);
        if (slot->compatible.empty()) {
            printf("no words of length %d\n", slot->len);
        }
    }
    while (1) {
        if (filled_slots.size() == grid.nslots) {
            return true;
        }
        if (fill_next_slot()) {
        } else {
        }
    }
}

#endif
//////////////////

void test_match() {
    char *p = (char*)"c_a__";
    ILIST ilist;
    get_matches(5, p, words.words[5], ilist);
    show_matches(5, words.words[5], ilist);
}

int main(int, char**) {
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
