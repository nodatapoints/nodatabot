
.PHONY: all

# this should also produce the shared object
# library on other platforms.

all: libbf.so
	@echo finished making all targets

libbf.so: libbf.o
	g++ -shared -Wl,-flto -Wl,-soname,libbf.so -o libbf.so libbf.o

libbf.o:: bf.cc
	g++ -c -fPIC bf.cc -o libbf.o -O3 -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -march=native
 

