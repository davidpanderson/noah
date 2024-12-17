// DEPRECATED: doesn't support unique words, and too complex

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
    random_shuffle(mw.begin(), mw.end());

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
        // mword pattern from filled slots lower on stack
    ILIST *compatible_mwords;
        // mwords compatible with this pattern
    int next_mword_index;
        // next one to try
    char current_mword[MAX_LEN];
        // if filled, current word

    // for each position and each letter (a-z)
    // we keep track of whether putting the letter in that position
    // as OK (nonzero compatible mwords in the linked slot).
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
        mpattern[len] = 0;
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

    void print_state() {
        printf("slot %d:\n", num);
        if (filled) {
            printf("   filled; mword: %s; index %d\n",
                current_mword, next_mword_index
            );
        } else {
            printf("   unfilled\n");
        }
        printf("   mpattern: %s\n", mpattern);
        if (compatible_mwords) {
            printf("   %ld compat mwords\n",
                compatible_mwords->size()
            );
        } else {
            printf("   compat words is null\n");
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
        printf("------ solution --------\n");
        for (SLOT *slot: slots) {
            printf("%d: %s\n", slot->num, slot->current_mword);
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
        printf("%s\n", slot->filled?slot->current_mword:slot->mpattern);
    }
}

////////////////// GRID-FILL ALGORITHMS ////////////////

// Scan compatible mwords for the given slot, starting from current index.
// If find one that's usable (crossing words still have compat mwords)
// install it and return true
//
// Each position in the mword links to an xword
// For each position and each possible letter (a-z) either
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
    if (next_mword_index == 0) {
        clear_usable_letter_checked();
    }
    int n = compatible_mwords->size();
#if VERBOSE
    printf("slot %d: find next usable mword; %d of %d\n",
        num, next_mword_index, n
    );
    printf("   mpattern %s\n", mpattern);
#endif
    while (next_mword_index < n) {
        char* mw = mwords[(*compatible_mwords)[next_mword_index++]];
        bool usable = true;
        for (int i=0; i<mlen; i++) {
            if (mpattern[i] != '_') continue;
            char c = mw[i];
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
            printf("%s is usable for slot %d\n", mw, num);
            print_usable();
#endif
            strcpy(current_mword, mw);
            return true;
        }
    }
#if VERBOSE
    printf("no compat words are usable for slot %d\n", num);
    print_usable();
#endif
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
    return slot2->check_mpattern(pattern2);
}

// mp differs from current mpattern by 1 additional letter.
// see if this slot has an mword matching this
// (only need to check mwords compatible with current mpattern)
//
bool SLOT::check_mpattern(char* mp) {
    for (int i: *compatible_mwords) {
        if (match(len, mp, mwords[i])) {
            return true;
        }
    }
    return false;
}

// Find the unfilled slot with fewest compatible mwords
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
        size_t n = slot->compatible_mwords->size();
#if VERBOSE
        printf("   slot %d, %ld compatible mwords\n",
            slot->num, n
        );
#endif
        if (n < nbest) {
            nbest = n;
            best = slot;
        }
    }

    best->next_mword_index = 0;
    if (best->find_next_usable_mword()) {
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

// we've found a usable mword for the given slot.
// for each position where its pattern was _:
// in the linked slot, update the pattern and the compatible_mwords list.
// If the pattern is full, mark slot as filled and push
//
void GRID::fill_slot(SLOT* slot) {
#if VERBOSE
    printf("filling %s in slot %d\n", slot->current_mword, slot->num);
#endif
    for (int i=0; i<slot->mlen; i++) {
        char c = slot->mpattern[i];
        if (c != '_') continue;
        LINK &link = slot->mlinks[i];
        SLOT *slot2 = link.other_slot;
        slot2->mpattern[link.other_pos] = slot->current_mword[i];
        if (strchr(slot2->mpattern, '_')) {
            slot2->compatible_mwords = slot2->pattern_cache.get_list(
                slot2->mpattern
            );
            if (slot2->compatible_mwords->empty()) {
                printf("empty compat list for slot %d pattern %s\n",
                    slot2->num, slot2->mpattern
                );
                exit(1);
            }
        } else {
            // other slot is now filled
            slot2->compatible_mwords = NULL;
            slot2->filled = true;
            strcpy(slot2->current_mword, slot2->mpattern);
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
        // update mpatterns of unfilled crossing slots
        //
        for (int i=0; i<slot->mlen; i++) {
            LINK &link = slot->mlinks[i];
            SLOT* slot2 = link.other_slot;
            if (slot2->filled) continue;
            slot2->mpattern[link.other_pos] = '_';
            slot2->compatible_mwords = slot2->pattern_cache.get_list(
                slot2->mpattern
            );
            if (slot2->compatible_mwords->empty()) {
                printf("empty compat list for slot %d pattern %s\n",
                    slot2->num, slot2->mpattern
                );
                exit(1);
            }
        }
        if (slot->find_next_usable_mword()) {
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
//      'mpattern' reflecting crossing letters:
//          filled slots: slots lower on the stack
//          unfilled slots: all filled slots
//      compatible_mwords: list of mwords compatible with mpattern
// filled slots have
//      current mword
//      a 'next index' into compatible_mwords
//
// fill_next_slot() picks an unfilled slot S
//      (currently, the one with fewest compatible mwords).
//      it scans its compatible_mwords list for an mword that's 'usable'
//          (i.e. other unfilled slots would have compatible words)
//      if it finds one it adds that S to the filled stack,
//          sets S.current_word
//          and updates mpattern and compatible_mwords
//          of affected unfilled slots
//      otherwise we backtrack:
//          loop
//              for slot S at top of stack:
//              update mpatterns of unfilled slots to remove
//                  letters in S.current_word unspecified in S.mpattern
//              look for next usable mword
//              if none
//                  pop S
//              else
//                  set S.current_word
//                  update mpatterns of unfilled slots to include new mword
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
    //make_test_grid(grid);
    make_square_grid(grid, 6);
    grid.prepare();
    //grid.print_mlinks();
    //grid.print_mwords();
    if (grid.fill()) {
        grid.print_solution();
    } else {
        printf("no solution\n");
    }
}
