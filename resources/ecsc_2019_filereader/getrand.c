#include <stdio.h>
#include <stdlib.h>
  
int main ( int argc, char** argv )
{
	int i = 0;
	sscanf(argv[1], "%d", &i);
	srand(i);
	unsigned long rand_num = rand();
	printf("RANDOM : %x\n", rand_num);
}
