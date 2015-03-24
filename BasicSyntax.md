# Introduction #

This describes the basic syntax of the configuration files, the .bdgcfg files.

# Details #

For each project you need to create a .bdgcfg file to tell BadgerConfig what to generate for this file. The basic layout of a .bdgcfg file is a standard windows ini file. It can look like this:

```
[General]
Type = StaticLibrary
SourceFiles = SourceFiles;../SourceFiles

[Project]
```

This is actually from one of my projects at home, and often you can get away with this minimal file for most of your projects. Note that there are some sections here, hardcoded and then each section have some keys with values.

A lot of values can be inferred from the location and name of the file, for example the project name is taken by default from the name of the .bdgcfg file itself, the platform is taken from the parent directory. You can of course override these by giving keys inside the file itself:

```
[General]
Type = StaticLibrary
SourceFiles = SourceFiles;../SourceFiles
Name = Math
Platform = iPhone

[Project]

```


There are three major sections, General, Project and Solution. They pretty much follow the convention of Visual Studio (so if you come from XCode, then you have to bend your mind a little).

If you give a Solution section, then a .sln file will also be generated for you. For the iPhone support, if you give a Solution section, a .xcode project file will be created for you.

Some of the keys can contain paths. Always give relative paths from the directory that the .bdgcfg file is in.


# General keys #

### Name ###

This is the name of the project. It will be taken from the filename of the bdgcfg file, but you can override it here.

### Platform ###

This is taken from the parent directory name if not given, but you can give it here to override. It must match one of the directory names in BadgerConfig/Templates from the distribution.

```
[General]
Platform=iPhone
```

### Type ###

Type must be one of the following:

  * ConsoleApplication
  * StaticLibrary
  * WindowsApplication
  * DynamicLibrary
  * MfcApplication


### SourceFiles ###

This lists, in a semi colon delimited list, relative paths to the SourceFiles flat listings of the actual files to include in the .vcproj file. It's very typical to have two items here, one for the platform independent files and one for the platform dependent files.

```
[General]
Type = StaticLibrary
SourceFiles = SourceFiles;../SourceFiles
```


# Project keys #


### Defines ###

A semicolon delimited list of defines you want to have in the project.

```
[Project]
Defines=FOOBAR;PLATFORM_WINDOWS
```

### OutputFile ###

You can optionally redirect the output here:

```
[Project]
OutputFile=../../../../lib/tool_glew_$(configurationname).lib
```

### uuid ###

This is the GUID that Visual Studio assigns each project. If you don't give this, BadgerConfig will automatically generate a stable hash for this given the path and name of the project.

```
[Project]
Uuid=baa7cb88-8db5-4568-92c0-b645e3333d08
```

### IncludePaths ###

A semicolon delimited list of relative paths to find headers in.

```
[Project]
IncludePaths=../../../../Shared;../../../../External/Packages/freetype-2.1.10/include
```

### LibraryPaths ###

A semicolon delimited list of relative paths to find libraries in.

```
[Project]
LibraryPaths=../../../../External/Packages/freetype-2.1.10/lib
```

### Libraries ###

A semicolon delimited list of libraries to link with.

```
[Project]
Libraries=Ws2_32.lib;Kernel.lib
```

### DisabledVCWarnings ###

A semicolon delimited list of warnings to disable in Visual Studio.

```
[Project]
DisabledVCWarnings=4131;4244;4267;4100;4245
```

### PostBuildCommand ###

This is very useful for inserting commands once the project builds successfully, e.g. run unit tests automatically:

```
[Project]
PostBuildCommand=$(TargetPath) -unittest
```



# Solution keys #



### Dependencies ###

Lists the other projects that you want to link into this solution. It needs to be a semicolon separated list, e.g.

```
[Solution]
Dependencies=Core;AuroraTest
```

### DependenciesPaths ###

Lists, semi colon delimited, relative paths that will be searched recursivly for the project names (through the .bdgcfg files) given in the Dependencies key.

```
[Solution]
Dependencies=Core;AuroraTest
DependenciesPaths=../../../External;../../../Stage
```