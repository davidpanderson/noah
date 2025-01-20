# XW: a filler for generalized crossword grids

XW is a program that, given a word list and a crossword puzzle grid,
finds all the ways the grid can be filled with words from the list.

## Generalized grids

In XW terminology, 'grid' is a set of 'slots',
each of which holds a word of a fixed length.
A 'cell' (letter space) in one slot can be 'linked' to a cell in another slot,
in which case the 2 cells must contain the same letter.

This structure can represent
* conventional 2D grids (black-square, barrier style, etc.)
* grids on tori or Klein bottles
* a variety of other planar and non-planar forms.

Note: in the current version of XW a cell can be shared by at most 2 slots,
so XW can't represent e.g. 3D grids.
Removing this limitation
wouldn't be hard to add; let me know if you want this.

XW provides several ways to describe grids, which are detailed below.

## Example

XW is written in C++ and runs on Unix-like systems with g++ and make.
Download the source code and type `make`.
You may have to install the `ncurses` library first.

Let's do the example grid from
[here](https://www.nytimes.com/2018/05/11/crosswords/how-to-make-crossword-puzzle-grid.html).

Create a file `bs_15_1` containing:
```
mirror
.....*....*....
.....*....*....
..........*....
......**...*...
***.....*.....*
...*...........
.....*....*....
....*.....*....
```
This describes the upper half of the grid;
asterisks are black squares.
`mirror` says to duplicate this, rotated, for the lower half.

Now run
```
black_square --grid_file bs_15_1
```

After a few seconds it will find a solution, such as
```
Solution found:
p l a t e * c y s t * e r r s
r e b o p * p o o h * a h e m
o v e r i n s u r e * t i p i
p o t a t o * * t o m * n o t
* * * s o l a r * l a v e r *
r u m * m o n o l o g i s t s
a n o d e * s t a g * s t a t
d a d o * s w a t s * t o g a
i r e s * m e t e * j a n e t
i r r e v e r e n c e * e s s
* e a s e l * s t u n g * * *
c s t * e l d * * e n l a c e
o t i c * i r r a d i a t e d
r e n o * e a t s * e r o d e
e d g y * r y e s * s e m e n
```
You can then
* save this to a file
* ask for the solution in sequence (this will usually be a small change).
* restart with a different random seed to get a completely different solution.
* if you don't like one of the words, add it to the 'veto' list and start over.

Now let's try a generalized grid, using this grid file:
```
mirror
wrap_row
*....*....*....
.....*....*....
.....*....*....
......**...*...
***.....*.....*
...*....*....*.
.....*....*....
....*.....*....
```
The `wrap_row` means that the grid wraps around horizontally:
when an across word goes off the right edge,
it comes back on the left.

This yields, for example:
```
* l i r a * e c r u * s u e s
i a t e s * b o o n * e m a c
r d e s t * b l o c * a b s u
e e m e r s * * t o n * r e d
* * * w o o e r * a t t a r *
c h o * i d l e * t h u g * e
u e r e d * l a c e * l e a g
t i n e * c e d e d * s o n a
e r e r * a n a l * m a u n d
s * r i f t * p l e a * s a s
* v i e r s * t i t h e * * *
r a n * o p e * * c a t a m a
o d e s * a x i l * t h r e n
v i s e * w i r e * m i s a d
e s s e * s t a y * a c e s *
```

You can hard-wire words (or single letters) in the grid.
For example, this grid file
```
.....*....*....
.....*....*....
macbookair*....
......**...*...
***.....*.....*
...*tenuretrack
.....*....*....
....*.....*....
....*....*.....
puzzlepiece*...
*.....*.....***
...*...**......
....*callnumber
....*....*.....
....*....*.....
```
might produce this solution:
```
s o a k s * q u a n * p e a t
e l c a p * i p s o * l a u e
m a c b o o k a i r * o r t s
i n t o l u * * m e t * l o h
* * * b e s o t * p k w y s *
c c s * t e n u r e t r a c k
r a n t o * e n i a * a p r i
o r e e * t t e s t * p r o t
u b e r * i a s k * d t i l e
p u z z l e p i e c e * l l d
* r e a c t * n d o l a * * *
l e w * d a t * * n o r b i t
a t e m * c a l l n u m b e r
g o e r * k l a s * s e r r a
o r d s * s c s i * e n t s y
```
(Note: you need a large word list to solve this,
and there are some funky words).

## Black-square grids

The above examples are 'black square' grids.
These are 2D arrays in which some cells are black,
indicating word boundaries.
These are used for traditional crosswords
(e.g. NYT puzzles) and some cryptics (e.g. Out of Left Field).

The above examples show the basic file format
used by XW to represent black-square grids.

By convention, black-square grids have no unchecked cells
and no words shorter than 3 letters.
XW doesn't enforce these conventions.
Unchecked cells are not treated as 1-letter slots.

The grid options (one per line at the start of the file) are:

`mirror`

The file specifies only the top half of the grid.
The bottom half is a copy of the same pattern, rotated 180 degrees.
If an odd number N of rows is given,
the first N-1 are copied.

`wrap_row`

Slots that reach the right edge of the grid
wrap around to the left edge and continue.

`wrap_col`

same, for columns.

`twist_row`

If `wrap_row` is specified, and a slot in row *i* wraps around,
it continues in row *N-i-1*, where *N* is the number of rows.
In other words, the grid's left and right edges are identified,
but with a twist.

`twist_col`

same, for columns.

Different combinations of options correspond
to grids on different 2-manifolds:

`wrap_row` or `wrap_col`: cylinder

`wrap_row + twist_row`: Mobius strip

`wrap_row + wrap_col`: torus

`wrap_row + twist_row + wrap_col`: Klein bottle

`wrap_row + twist_row + wrap_col + twist_col`: Projective plane

## Barrier grids

A 'barrier grid' is a 2D array in which

* Every cell has a letter (no black squares)
* Barriers between adjacent cells (represented by thick lines)
indicate word boundaries.

This format is used in some cryptic puzzles,
e.g.  puzzles from The Atlantic by Emily Cox and Henry Rathvon.

A barrier grids is represented by a file of the form:
```
-------------------------
|. . . .|. . . . . . . .|
   -   -   -       -
|.|.|. . . . . . . . . .|
       -   -       -
|. . . . . .|. . . . . .|
... etc.
-------------------------

```
where

* `-` represents a horizontal barrier
* `|` represents a vertical barrier
* `.` represents a cell
* A lower-case alpha character represents a preset cell

Unlike black-square grids, you must specify barriers
on the outer edges of the grid.

Barrier grids can have the same options
(`mirror` etc.) as black-square grids.
If you specify `row_wrap`, a slot wraps around
if the rightmost cell has no right barrier and the
corresponding leftmost cell has no left barrier.

## Arbitrary grids

XW provides an API for creating arbitrary grids.
This API involves two structs, `SLOT` and `GRID`.

`SLOT` represents a slot in a grid:
```
struct SLOT {
    int len;    // number of characters in word
    // the following are optional; for convenience with planar grids
    int row, col;
    bool across;

    SLOT(int len);

    // you can change the length after creating the slot.
    // Call the following when the final length is known
    //
    void set_len();

    // assign a preset cell
    void preset_char(int pos, char c);
};
```

`GRID` represents a generalized grid:
```
struct GRID {
    SLOT* add_slot(SLOT*);
    void add_link(SLOT *slot1, int pos1, SLOT *slot2, int pos2);
};
```
`add_slot()` adds a slot to the grid.
`add_link()` links a cell in one slot to a cell in another one.
A given cell can be shared by at most two slots.

You must supply the following functions and link them
with the XW main program (in xw.cpp).
```
void make_grid(const char* fname, GRID &grid);
void print_grid(GRID&, bool curses);
```

`make_grid()` populates a `GRID`.
If the main program was called with the `--grid_file` argument,
the filename will be passed as `fname`.

`print_grid()` 
prints a grid (as ASCII characters on a screen).
The way you do this is up to you.
If `curses` is set, you should use `ncurses` library calls
(e.g. `move()`,`printw()`, and `refresh()`)
to print at the upper-left corner of the screen.

