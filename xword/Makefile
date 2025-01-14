all: lines black_square

SRC = xw.cpp
HDR = xw.h

xword: xword.cpp
	g++ -g xword.cpp -o xword

word_square: word_square.cpp $(SRC) $(HDR)
	g++ -g word_square.cpp $(SRC) -lncurses -o word_square
lines: lines.cpp $(SRC) $(HDR)
	g++ -g lines.cpp $(SRC) -lncurses -o lines
black_square: black_square.cpp $(SRC) $(HDR)
	g++ -g black_square.cpp $(SRC) -lncurses -o black_square
xwtest: xwtest.cpp $(SRC) $(HDR)
	g++ -g xwtest.cpp $(SRC) -lncurses -o xwtest
