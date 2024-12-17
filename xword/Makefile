all: xword word_square

SRC = xw.cpp
HDR = xw.h

xword: xword.cpp
	g++ -g xword.cpp -o xword

word_square: word_square.cpp $(SRC) $(HDR)
	g++ -g word_square.cpp $(SRC) -lncurses -o word_square
