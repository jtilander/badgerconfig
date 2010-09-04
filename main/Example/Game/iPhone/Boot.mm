#include <UIKit/UIKit.h>
#include "../Main.h"

int main(int argc, char* argv[])
{
	NSAutoreleasePool* pool = [NSAutoreleasePool new];

	const int res = myMain(argc, argv);

	[pool release];
	return res;
} 