#include <cstring>
#include <vector>
#include <stack>
#include <cstdlib>

using namespace std;

#define VERBOSE     1

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

    // for each position and each letter (a-z)
    // keep track of whether putting the letter in that position
    // was OK (nonzero compatible words in the linked slot).
    // These must be cleared each time we fill this slot.
    //
    bool usable_letter_checked[MAX_LEN][26];
    bool usable_letter_ok[MAX_LEN][26];

    SLOT(int _len, char* preset_pattern=NULL) {
        len = _len;
        if (preset_pattern) {
            if (strlen(preset_pattern) != len) {
                fprintf(stderr, "bad preset pattern %s\n", preset_pattern);
                exit(1);
            }
            strcpy(filled_pattern, preset_pattern);
        } else {
            strcpy(filled_pattern, NULL_PATTERN);
            filled_pattern[len] = 0;
        }
    }
    inline void clear_usable_letter_checked() {
        memset(usable_letter_checked, 0, sizeof(usable_letter_checked));
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

    // call this after adding slots and links
    void prepare() {
        for (SLOT *s: slots) {
            s->words_init();
        }
    }

    bool fill_next_slot();
    bool backtrack();
    bool fill();
    void fill_slot(SLOT*);
};
