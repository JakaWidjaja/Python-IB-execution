#declare variable
cc = g++ -std=c++14

vol_path=/media/lun/Data2/Trading_Algo/class_c++/Volatility

all: trading

trading: main.o volatility.o
		$(cc) main.o volatility.o -0 main

main.o: main.cpp
		$(cc) main.cpp

volatility.o: volatility.cpp
		$(cc) -I $(vol_path) volatility.cpp

clean:
	rm -rf *o trading

