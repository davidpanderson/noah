#include <cstdio>
#include <cstring>
#include <vector>

using std::vector;

#define MAX_LEN 28

typedef vector<char*> WLIST;
typedef vector<int> ILIST;
WLIST words[MAX_LEN+1];

int nwords[MAX_LEN+1];

struct PATTERN {
    char chars[MAX_LEN];
    inline void init() {
        memset(chars, 0, MAX_LEN);
    }
    inline void set(int i, char c) {
        chars[i] = c;
    }
};

inline bool match(int len, PATTERN &pattern, char* word) {
    for (int i=0; i<len; i++) {
        if (pattern.chars[i] && pattern.chars[i]!=word[i]) return false;
    }
    return true;
}

void get_matches(int len, PATTERN &pattern, ILIST &ilist) {
    WLIST &wlist = words[len];
    for (unsigned int i=0; i<wlist.size(); i++) {
        if (match(len, pattern, wlist[i])) {
            ilist.push_back(i);
        }
    }
}

void show_matches(int len, ILIST &ilist) {
    for (int i: ilist) {
        printf("%s\n", words[len][i]);
    }
}

//////////////////

struct SLOT {
    int len;
};

// parse black-square grid
//
// *aaaaa*
// a*a*aaa
// aaaaa*a
// aaa***a

void read_grid() {
}

//////////////////
void read_words() {
    FILE* f = fopen("words", "r");
    char buf[256];
    int max = 0, i;
    while (fgets(buf, 256, f)) {
        int len = strlen(buf)-1;
        if (len>max) {
            printf("%s", buf);
            max = len;
        }
        nwords[len]++;
        words[len].push_back(strdup(buf));
    }
    printf("%d\n", max);
    for (i=1; i<=MAX_LEN; i++) {
        printf("%d: %d\n", i, nwords[i]);
    }
}

int main(int, char**) {
    read_words();
    PATTERN p;
    p.set(0, 'c');
    p.set(2, 'a');
    ILIST ilist;
    get_matches(5, p, ilist);
    show_matches(5, ilist);
}
