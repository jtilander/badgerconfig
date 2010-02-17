#!/usr/bin/python
#
#
#
# (C) 2007 Jim Tilander
import string
import os
import PathHelp
import logging

UNIQUE_COUNTER = 1000
OBJECT_GENERATING_EXTENSIONS = ['.cpp', '.c', '.cxx', '.cs']

class FileItem:
	def __init__(self):
		self.fullpath = ''		# Absolute path to the item.
		self.folderPath = []	# Stores the directory items leading up the file as given in the SourceFiles
		self.outputBase = ''	# The filename that the object file get's generated into, e.g. if we have multiple Foobar.cpp we get this set to Foobar_001
		self.options = {}
		self.uuid = ''
		self.refuuid = ''
	
	def __repr__(self):
		return '%s -> %s | %s' % (self.fullpath, self.outputBase, self.options)

	def __name(self):
		return os.path.basename(self.fullpath)
	def __contextname(self):
		return os.path.basename( os.path.dirname( os.path.dirname(self.fullpath ) ) ) + '/' + os.path.basename(os.path.dirname(self.fullpath))
	def __basename(self):
		return os.path.splitext(os.path.basename(self.fullpath))[0].lower()
	def __ext(self):
		return os.path.splitext(self.fullpath)[1]
	basename = property(__basename)
	name = property(__name)
	contextname = property(__contextname)
	ext = property(__ext)

def parseFromLine(basePath, line):
	result = FileItem()
	values = string.split( line, '|', 1 )
	pathFromConfig = values[0].replace('/', os.sep) 
	folderItems = [ x for x in string.split(pathFromConfig, os.sep) if x != '..' ]
	del folderItems[-1]
	result.folderPath = folderItems #string.join( folderItems, os.sep )
	result.fullpath = PathHelp.normalize( os.path.join( basePath, pathFromConfig ) )
	#logging.debug( 'Folder path = %s' % (result.folderPath) )
	if len(values)>1:
		for pair in values[1].split('|'):
			values = pair.split('=')
			key = values[0]
			if len(values) == 2:
				value = values[1]
			else:
				value = ''
			result.options[key.lower()]=value
			logging.debug( 'Found file specific option %s: %s="%s"' % (result.fullpath, key, value) )
	return result

def parseSourceFiles( filename ):
	base = os.path.dirname(filename)
	result = []
	
	logging.debug('About to open %s' % filename )
	lines = open(filename).readlines()
	
	lines = [string.strip(x) for x in lines]
	lines = [x for x in lines if len(x)>0]
	lines = [x for x in lines if x[0] != '#']
	
	logging.debug( '%s contained %d lines' % (filename, len(lines)) )
	for line in lines:
		result.append( parseFromLine( base, line ) )
	logging.debug( 'Finished parsing items')
	return result

def sortOnFileName(a,b):
	return cmp(a.basename, b.basename)

def fixupUnique( fileItems ):
	global UNIQUE_COUNTER
	result = []
	objectGeneratingFiles = []
	
	# First just separate the non object generating files into the result. Save the ones that do generate object files into a special list for later 
	# check for uniqueness.
	for item in fileItems:
		name = item.basename
		ext = os.path.splitext(name)[1]
		if ext in OBJECT_GENERATING_EXTENSIONS:
			objectGeneratingFiles.append(item)
		else:
			result.append(item)
	
	# Check all the object generating files for a unique basename, since in visual studio the outpus goes into a flat heirarchy.
	# If the name is not unique then just add a counter to it to make it unique...
	objectGeneratingFiles.sort( sortOnFileName )
	for i, item in enumerate(objectGeneratingFiles):
		myname = item.basename
		if i > 0:
			othername = objectGeneratingFiles[i-1].basename
		else:
			othername = ''
		if myname == othername:
			item.outputBase = myname + '_%d' % UNIQUE_COUNTER
			UNIQUE_COUNTER += 1
		result.append(item)
	return result

def readSourceFiles( baseDir, commaSeparatedSourceFilesList ):
	assert( isinstance( commaSeparatedSourceFilesList, type('') ) )
	sourcefiles = commaSeparatedSourceFilesList.split(';')
	result = []
	for sourcefile in sourcefiles:
		fullpath = os.path.join( baseDir, sourcefile.replace('/', os.sep ) )
		fullpath = os.path.abspath(fullpath)
		logging.debug('Now parsing %s' % fullpath )
		result += parseSourceFiles( fullpath )
	
	logging.debug( 'Fixing unique references to items')
	return fixupUnique(result)
