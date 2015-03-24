# Introduction #

This describes the simple fileformat for how to list source files.

# Basics #

A "SourceFiles" file is basically any text document that lists other source files for badgerconfig. If you look at the examples folder you find several files literally named SourceFiles and they will contain text like this:

```

#
# List all the source files here (and we can have comments)
#

../main.cpp

#
# Platform specifc (whitespace doesn't matter)
#
    ../Win32/Timer.cpp
    ../Timer.h


```

If you've been doing any unix work, this looks like any other standard flat file format out there, each line describes something (relative path from the directory the SourceFiles is in to the actual file we're trying to pull in), whitespace doesn't matter and we can have optional comments for any line that starts with a hash mark.

We can give options for each source file with a key=value pair after the sourcefile itself on the same line, each pair separated by a horizontal bar (|).


# Folders #

BadgerConfig will assume that you will have a pretty flat hierarchy of folders inside the project files, in fact, it will only take into account one level. This level is usually used to express platform affinity of the source file. Any relative path will do, and the first folder name encountered after a .. component will be the folder name in visual studio. You can do tricks like referring to the current directory up and down to force a folder name (say you are already in a folder called x64, you could refer to the source file by ../x64/foo.cpp to force the x64 folder name).


# Precompiled headers #

Precompiled headers are great, they make compile times go down significantly. There is a limited support for pch in BadgerConfig, mostly for Visual Studio. If you list a file like this:

```
#
# Marks the file PreCompiled.cpp as the PCH in Visual Studio
#
	../Win32/PreCompiled.cpp|PreCompiled=1
	../Win32/PreCompiled.h
	../../Win32/Malloc.cpp
```

then BadgerConfig will automatically generate the correct .vcproj for compiling the PCH and then using it.


# Custom rules #

It it often very useful to generate custom rules for "sourcefiles" other than .cpp files and have them transformed with some batch script into something else. It's fairly easy to

```
#
# Transform the image 16x16_arrow.tga by calling the executable/batch script GenerateBinaryInline
# with two arguments: sourcepath and sourcepath + the new extension after the comma
#
../Data/16x16_arrow.tga|CustomRule=GenerateBinaryInline,.tga.inl
```