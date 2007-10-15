#!/usr/bin/python
# Quickly generates the necessary files for a new library or a game project.
#
# Jim Tilander (2007)
import logging
import sys
import os
import getopt
import string

HELP = """
Usage: GenerateSkeleton.py [options] <projectname>

Valid options:

	-q Quiet
	-v Verbose
	-p Platform

"""

DEFAULT_PLATFORMS = ['Win32', 'Tool']
VERBOSE = False

MAINPROGRAM = """#include "PreCompiled.h"
#include <Core/TestMainStub.h>

int __cdecl main( int, char** )
{
	return aurora::testStub();
}

"""

LIBRARYCONFIG = """[General]
Type = StaticLibrary
SourceFiles = SourceFiles;../SourceFiles

[Project]
Uuid=%(uuid)s
"""

TESTCONFIG = """[General]
Type = ConsoleApplication
SourceFiles = SourceFiles;../SourceFiles

[Project]
Uuid=%(uuid)s
PostBuildCommand=$(TargetPath) -unittest

[Solution]
Dependencies=%(projectname)s;Streams;Log;Core;AuroraTest
"""

def uuidgen():
	return os.popen( 'uuidgen' ).readlines()[0].strip().lower()

def generateProject( projectname, platforms ):
	logging.debug( 'Got projectname %s' % projectname )
	logging.debug( 'Processing platforms: %s' % string.join( platforms, ', ' ) )
	#if os.path.isdir( projectname ):
	#	logging.error( "Directory for %s already exists, won't clobber files." % projectname )
	#	return False
	
	for platform in platforms:
		logging.info( 'Processing %s/%s' % (projectname, platform) )
		try:
			os.makedirs( os.path.join( projectname, 'Build', platform ) )
		except WindowsError:
			pass
		try:
			os.makedirs( os.path.join( projectname, 'Test', 'Build', platform ) )
		except WindowsError:
			pass
		
		d = {}
		d['projectname'] = projectname
		d['uuid'] = uuidgen()
		open( os.path.join( projectname, 'Build', platform, projectname + '.bdgcfg' ), 'wt' ).write( LIBRARYCONFIG % d )
		open( os.path.join( projectname, 'Build', platform, 'SourceFiles' ), 'wt' ).write( '' )
		
		d['uuid'] = uuidgen()
		open( os.path.join( projectname, 'Test', 'Build', platform, 'Test' + projectname + '.bdgcfg' ), 'wt' ).write( TESTCONFIG % d )
		open( os.path.join( projectname, 'Test', 'Build', platform, 'SourceFiles' ), 'wt' ).write( '' )
	
	logging.info( 'Writing common files' )
	open( os.path.join( projectname, 'Build', 'SourceFiles' ), 'wt' ).write( '# Add files here\n' )
	open( os.path.join( projectname, 'Test', 'Main.cpp' ), 'wt' ).write( MAINPROGRAM )
	open( os.path.join( projectname, 'Test', 'Build', 'SourceFiles' ), 'wt' ).write( '\t../Main.cpp\n' )
	
	return True

def main( argv ):
	try:
		opts, values = getopt.getopt( argv, 'vqp:')
	except getopt.GetOptError:
		print HELP
		return 1
	
	if len(values) != 1:
		print HELP
		return 1
	
	platforms = []
	for o,a in opts:
		if '-p' == o:
			platforms.append(a)
		if '-v' == o:
			global VERBOSE
			VERBOSE = True

	projectname = values[0]
	if len(platforms) == 0:
		platforms = DEFAULT_PLATFORMS

	if VERBOSE:
		logging.basicConfig( level = logging.DEBUG, format = '%(levelname)-8s %(message)s' )
	else:
		logging.basicConfig( level = logging.INFO, format = '%(levelname)-8s %(message)s' )
	
	if not generateProject( projectname, platforms ):
		logging.debug( 'Failure' )
		return 1
	logging.debug( 'Success.' )
	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv[1:] ) )
