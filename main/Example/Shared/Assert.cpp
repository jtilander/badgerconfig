#include "Precompiled.h"
#include "Assert.h"
#include <stdio.h>
#include <stdarg.h>
#include <varargs.h>

void onAssert(const char* file, int line, const char* expression, const char* format, ...)
{
	char buffer[1024];
	va_list args;
	va_start(args, format);
	vsnprintf(buffer, sizeof(buffer), format, args);
	
	printf("%s(%d): ASSERT(%s)! %s\n", file, line, expression, buffer);
}
