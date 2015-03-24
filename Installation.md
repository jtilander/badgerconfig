# Introduction #

This describes how to install badgerconfig to your system.

# Download and hookup #

Make sure that you download the source and unzip it somewhere on your local drive. Remember the location and create a batchfile somehwere in your path and call it genall.cmd and then place the following text in it:

```
@echo off
setlocal
	set BASE=%~dp0
	%BASE%..\BadgerConfig\GenerateAll.py %*
endlocal
```

Here you see that I've given the relative path to the python script, but you of course need to modify the path to be whatever you have on your system (depending upon where you unzipped badgerconfig and where you placed the .cmd file). You might also want to call out the python.exe somewhere if you have not registered .py files as script files.


# Master config #

After you've hooked up the shortcut batch script, you need to locate the masterconfig files for the platforms you are interested in. Locate the directory BadgerConfig/Templates. In it you will find a directory for each platform. In each directory there is a CppBuildTemplate.vcproj file which is the xml template for the visual studio project file that gets generated and then there is a MasterConfig file, which is a shadow .bdcfg file that gets merged with the project file you will write later for each project. In here you can give system wide paths for example that will affect all the projects, as well as defines etc. Basically each key in the .bdgcfg file can be affected here, the path keys are all merged with the actual keys in the end.

You should go in here and modify the keys to suit your purposes (in the MasterConfig file). Unless you find a special need, you should not need to go into the CppBuildTemplate.vcproj file at all.