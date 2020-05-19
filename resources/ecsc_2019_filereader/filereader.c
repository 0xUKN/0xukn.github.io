int readfile(char *filename,char *file_content)
{
  uint stack_canary;
  FILE *__stream;
  ulong uVar2;
  
  stack_canary = rand();
  stackPush(&canaries,(ulong)stack_canary);
  __stream = fopen(filename,"r");
  if (__stream == NULL) 
  {
    printf("Error opening file \'%s\'",filename);
  }
  else 
  {
    fread(file_content,1,0x7ff,__stream);
    fclose(__stream);
  }
  uVar2 = stackPop(&canaries);
  if ((uint)uVar2 != stack_canary) {
    puts("Stack smashing detected!");
    exit(0xff);
  }
  return uVar2;
}

int main(int argc,char *argv[])
{
  uint __seed;
  int iVar1;
  long lVar2;
  undefined8 *puVar3;
  byte bVar4;
  char file_content [256];
  FILE *local_118;
  char filename [260];
  uint stack_canary;
  
  bVar4 = 0;
  __seed = getpid();
  srand(__seed);
  stack_canary = rand();
  stackPush(&canaries,(ulong)stack_canary);
  lVar2 = 0x100;
  puVar3 = file_content;
 
  if (argc < 2) 
  {
    printf("usage: %s <input_file>\n",**argv[]);              
    exit(1);
  }

  local_118 = fopen((char *)*argv[][1],"r");

  if (local_118 == NULL) 
  {
    printf("Unable to open file \'%s\'\n",*argv[][1]);            
    exit(2);
  }

  bzero(filename,0x100);
  while( true ) 
  {
    iVar1 = fscanf(local_118,"%s",filename);
    if (iVar1 == -1) break;
    printf("Attempting to read file \'%s\'\n",filename);
    bzero(file_content,0x800);
    readfile(filename,file_content);
    puts(file_content);
    bzero(filename,0x100);
  }
  __seed = stackPop(&canaries);
  if (__seed != stack_canary) 
  {
    puts("Stack smashing detected!");
    exit(0xff);
  }
  return 0;
}

