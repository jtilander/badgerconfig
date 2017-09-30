#include "PreCompiled.h"
#include "Main.h"
#include <Shared/Assert.h>
#include <Shared/Malloc.h>
#include <stdio.h>

int myMain(int argc, char* argv[])
{
	(void)argc;
	(void)argv;
	
	printf("Hello world!\n");
	
	const int size = 1024 * 16;
	void* ptr = mem::malloc(size);
	
	MY_ASSERT( 0 != ptr, "Failed to allocate %d bytes from the system", size);
	
	mem::free(ptr);
	return 0;
}
