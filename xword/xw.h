#include <cstring>
#include <vector>
#include <stack>
#include <cstdlib>

using namespace std;

#define NO_DUPS     1
    // don't allow duplicate words
#define EXIT_AFTER_SOLVE    1
    // exit after find a solution

// turn off if you use curses

#define VERBOSE_INIT            0
    // initialization of grid
#define VERBOSE_STEP_GRID       0
    // show grid after each step (fill or backtrack)
#define VERBOSE_STEP_STATE      0
    // show detailed state after each step
#define VERBOSE_NEXT_USABLE     0
    // SLOT::find_next_usable_work()
#define VERBOSE_FILL_NEXT_SLOT  0
    // GRID::fill_next_slot()
#define VERBOSE_FILL_SLOT       0
    // GRID::fill_slot()
#define VERBOSE_BACKTRACK       0
    // GRID::backtrack()

#define CHECK_ASSERTS           0
    // do sanity checks: conditions that should always hold


///////////// WORD LISTS AND PATTERNS //////////////

// a 'pattern' has '_' for wildcard.

#define NULL_PATTERN (char*)"____________________________"

#define MAX_LEN 29
    // longest word plus 1 for NULL

typedef vector<char*> WLIST;
typedef vector<int> ILIST;
typedef bool MASK[MAX_LEN];

struct WORDS {
    WLIST words[MAX_LEN+1];
    int nwords[MAX_LEN+1];
    int max_len;
    void read();
    void print_counts();
};

extern WORDS words;
extern void init_pattern_cache();

////////////////// SLOTS AND GRIDS ////////////////

struct SLOT;
struct GRID;

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
        // next compatible word to try
    char current_word[MAX_LEN];
        // if filled, current word
    int row, col;
        // for planar grids

    // for each position and each letter (a-z)
    // keep track of whether putting the letter in that position
    // was OK (nonzero compatible words in the linked slot).
    // These must be cleared each time we fill this slot.
    //
    bool usable_letter_checked[MAX_LEN][26];
    bool usable_letter_ok[MAX_LEN][26];

    SLOT(int _len) {
        len = _len;
        strcpy(filled_pattern, NULL_PATTERN);
        filled_pattern[len] = 0;
    }
    inline void clear_usable_letter_checked() {
        memset(usable_letter_checked, 0, sizeof(usable_letter_checked));
    }
    void preset_char(int pos, char c) {
        filled_pattern[pos] = c;
    }
    void preset(char *p) {
        strcpy(filled_pattern, p);
    }

    void print_usable();
    void add_link(int this_pos, SLOT* other_slot, int other_pos);
    void print_state();
    void words_init();
    bool find_next_usable_word(GRID*);
    bool letter_compatible(int pos, char c);
    bool check_pattern(char* mp);
};

struct GRID {
    int slot_num=0;
    vector<SLOT*> slots;
    vector<SLOT*> filled_slots;
    int npreset_slots;

    SLOT* add_slot(SLOT* slot) {
        slot->num = slot_num++;
        slots.push_back(slot);
        return slot;
    }
    void add_link(SLOT *slot1, int pos1, SLOT *slot2, int pos2) {
        char c1 = slot1->filled_pattern[pos1];
        char c2 = slot2->filled_pattern[pos2];
        if (c1 != '_') {
            slot2->filled_pattern[pos2] = c1;
        } else if (c2 != '_') {
            slot1->filled_pattern[pos1] = c2;
        } else {
            slot1->add_link(pos1, slot2, pos2);
            slot2->add_link(pos2, slot1, pos1);
        }
    }
    void print_solution() {
        printf("------ solution --------\n");
        for (SLOT *slot: slots) {
            printf("%d: %s\n", slot->num, slot->current_word);
        }
    }
    void print_state() {
        printf("------- state ----------\n");
        for (SLOT *slot: filled_slots) {
            slot->print_state();
        }
        for (SLOT *slot: slots) {
            if (slot->filled) continue;
            slot->print_state();
        }
        printf("\n------- end ----------\n");
    }

    void preset_init();
        // propagate preset chars

    // call this after adding slots and links
    void prepare() {
        npreset_slots = 0;
        preset_init();
        for (SLOT *s: slots) {
            s->words_init();
            if (s->filled) {
                npreset_slots++;
            }
        }
    }

    bool fill_next_slot();
    bool backtrack();
    bool fill();
    void fill_slot(SLOT*);
};