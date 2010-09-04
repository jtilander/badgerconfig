#ifndef assert_h
#define assert_h

#if defined TARGET_WIN32
	#define MY_BREAK() do { __debugbreak(); } while(0)
#elif defined TARGET_IPHONE
	#if defined(__arm__)
		#define MY_BREAK() do { __asm__ volatile("bkpt 0"); } while(0)
	#else
		#define MY_BREAK() do { __asm__ volatile("int $3\nnop\n"); } while(0)
	#endif
#else
	#error "Unknown platform"
#endif

#define MY_ASSERT(expr, message, ...)										\
	do																		\
	{																		\
		if( !(expr) )														\
		{																	\
			onAssert(__FILE__, __LINE__, #expr, message, ## __VA_ARGS__);	\
			MY_BREAK();														\
		}																	\
	} while(0)

void onAssert(const char* file, int line, const char* expression, const char* format, ...);


#endif
