#include "asm.h"

int main(int argc, char *argv[]){
  for(int i=1; i < argc; i++){
    assemble(argv[i]);
  }
  printf("\n");
  return 0;
}
