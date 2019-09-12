#include <stack>
#include <cstdio>

// instr -> c-style string with bf instructions
// out -> stdout fake, c-style mutable char buf
// max_it -> int, max commands to process
extern "C" int execute(const char* instr, char* out, const unsigned int out_size, int max_it) {
  const int BUF_SIZE = 512;
  unsigned char buf[BUF_SIZE] = {0};
  int ptr = BUF_SIZE/2;
  unsigned int iptr = 0;
  unsigned int out_ptr = 0;

  std::stack<unsigned int> loop;

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
        loop.push(iptr);
        break;
      case ']':
        if(loop.empty())
          return 3;
        if(buf[ptr])
          iptr = loop.top();
        else
          loop.pop();
        break;
      case '.':
        if(out_ptr < out_size)
          out[out_ptr++] = buf[ptr]; 
        break;
      case ',':
        // buf[ptr] = std::getchar(); # no way to easily provide input
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
