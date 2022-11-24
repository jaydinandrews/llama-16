#include "asm.h"

int assemble(char *filename){
  FILE *as;
  char line[MAX];

  as = fopen(filename, "r");
  if(as == NULL){
    printf("\n File \"%s\" does not exist or", filename);
    printf("\n you do not have permission to read it.\n");
    return 0;
  }
  while(1){
  
  if(fgets(line, MAX, as)==NULL)
    break; //Finished reading the file, exit loop

  if(!skip(line)){
   if(strlen(line) > MAX - 2){
    //line too long
   }
  }
  } //main while loop
}


int skip(char *line){
  if (line == NULL)
    return 1;
  if(*line==';')
    return 1;
  while(line != NULL && *line <= 32 && *line != '\0' && *line == '\t'){
    line++;
    if(*line == ';')
      return 1;
  }
  if(*line == '\0')
    return 1;
  line++;
  if(*line == '\0')
    return 1;
  else
    return 0;
}
