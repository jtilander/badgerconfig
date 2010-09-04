#include "PreCompiled.h"
#include "../Malloc.h"
#include <malloc.h>

void* mem::malloc(int size)
{
	return ::malloc(size);
}

void mem::free(void* ptr)
{
	if( !ptr )
		return;
	::free(ptr);
}
