
.PHONY: all

# this should also produce the shared object
# library on other platforms. please change
# the name accordingly.

all: libbf_x86_64-linux-gnu.so
	@echo finished making all targets

libbf_x86_64-linux-gnu.so: libbf.o
	g++ -shared -Wl,-flto -Wl,-soname,libtn.so -o libbf_x86_64-linux-gnu.so libbf.o

libbf.o:: bf.cc
	g++ -c -fPIC bf.cc -o libbf.o -O3 -std=c++17 -Wall -Wextra -Wpedantic -Werror -fno-exceptions -march=native
 

