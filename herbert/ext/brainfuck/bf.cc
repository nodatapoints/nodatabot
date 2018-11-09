#include <vector>
#include <cstdio>

template<typename T>
struct stack : protected std::vector<T> {
    using std::vector<T>::push_back;
    using std::vector<T>::vector;
    using std::vector<T>::pop_back;
    using std::vector<T>::back;
    using std::vector<T>::empty;
};

// instr -> c-style string with bf instructions
// out -> stdout fake, c-style mutable char buf
// max_it -> int, max commands to process
extern "C" int execute(const char* instr, char* out, int max_it) {
  const int BUF_SIZE = 512;
  unsigned char buf[BUF_SIZE] = {0};
  int ptr = BUF_SIZE/2;
  unsigned int iptr = 0;
  unsigned int out_ptr = 0;

  stack<unsigned int> loop;

  while(--max_it) {

    switch(instr[iptr]) {
      case '+':
        ++buf[ptr];
        break;
      case '-':
        --buf[ptr];
        break;
      case '<':
        --ptr;
        if(ptr < 0) 
          ptr += BUF_SIZE;       
        break;
      case '>':
        ++ptr;
        if(ptr >= BUF_SIZE)
          ptr -= BUF_SIZE;
        break;
      case '[':
        loop.push_back(iptr);
        break;
      case ']':
        if(loop.empty())
          return 3;
        if(buf[ptr])
          iptr = loop.back();
        else
          loop.pop_back();
        break;
      case '.':
        out[out_ptr++] = buf[ptr]; 
        break;
      case ',':
        buf[ptr] = std::getchar();
        break;
      case '\0':
        return 3 * !loop.empty();
      default:
        break;
    }
    ++iptr;
    
  }
  out[out_ptr] = '\n';

  return !max_it;
}
