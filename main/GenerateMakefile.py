#!/usr/bin/python
#
# Generates a flat makefile for a given solution.
#
# (C) 2007 Jim Tilander
import logging
import os
import sys
import string
import ConfigParser
import Engine
import FileItem
import PathHelp

VERBOSE = True
HELP = 'Usage: %s <configfile>' % sys.argv[0]
OBJECT_EXTENSIONS = ['.cpp', '.c']

class ProjectDesc:
	def __init__(self):
		self.name = ''
		self.type = ''
		self.base = ''
		self.sourceFiles = []
	
	def __repr__(self):
		return self.name

# TODO: Collect ProjectDesc from dependencies.
# TODO: Remove duplicates
# TODO: Basically do what the generate solution program is doing, but also in the end generate full information about the actual projects as well.


def getProjectFiles( configFileName ):
	basePath = os.path.dirname(configFileName)
	generalDict, projectDict, solutionDict = Engine.readConfiguration(configFileName)
	sourceFiles = FileItem.readSourceFiles( basePath, generalDict['sourcefiles'] )

	desc = ProjectDesc()
	desc.type = generalDict['type']
	desc.name = generalDict['name']
	desc.base = basePath
	desc.sourceFiles = sourceFiles
	return desc

def generateMakefile( descs ):
	objectfiles = []
	libraryfiles = []
	executablefiles = []
	
	for desc in descs:
		if 'StaticLibrary' == desc.type:
			libraryFile = os.path.join(desc.base, '$(CONFIG)', 'lib' + desc.name + '.a')
			libraryfiles.append(libraryFile)
			logging.debug( 'Found static library at: %s' % libraryFile )
			for source in desc.sourceFiles:
				basename = os.path.basename(source.fullpath)
				name, ext = os.path.splitext(basename )
				if ext not in OBJECT_EXTENSIONS:
					continue
				objectFile = os.path.join(desc.base, '$(CONFIG)', name + '.o')
				logging.debug( '\t%s' % objectFile )
				objectfiles.append(objectFile)
			continue
		
		if 'ConsoleApplication' == desc.type:
			executable = os.path.join(desc.base, '$(CONFIG)', desc.name + '.elf')
			executablefiles.append(executable)
			logging.debug( 'Found console app at: %s' % executable )
			for source in desc.sourceFiles:
				basename = os.path.basename(source.fullpath)
				name, ext = os.path.splitext(basename )
				if ext not in OBJECT_EXTENSIONS:
					continue
				objectFile = os.path.join(desc.base, '$(CONFIG)', name + '.o')
				logging.debug( '\t%s' % objectFile )
				objectfiles.append(objectFile)
			continue

def main( argv ):
	if len(argv) != 1:
		print HELP
		return 1

	configFileName = os.path.abspath(argv[0])
	basePath = os.path.dirname(configFileName)

	try:
		desc = getProjectFiles( configFileName )
		print desc
		generateMakefile( [desc] )
		
		
		# Determine the output product path.
		targetName = os.path.join( basePath, 'Makefile' )
		
		makefile = ''
		
		# Write the final makefile down to disk.
		Engine.writeConfigFile( targetName, makefile )
	except SyntaxError, e:
		logging.error( str(e) )
		return 1
	return 0

if __name__ == '__main__':
	if VERBOSE:
		logging.basicConfig( level = logging.DEBUG, format = '%(levelname)s %(message)s' )
	else:
		logging.basicConfig( level = logging.INFO, format = '%(levelname)s %(message)s' )
	sys.exit( main( sys.argv[1:] ) )
