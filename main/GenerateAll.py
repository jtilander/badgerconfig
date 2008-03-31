#!/usr/bin/python
#
# Applies all the configurations....
#
# (C) 2007 Jim Tilander
import logging
import os
import sys
import string
import Engine
import GenerateProject
import GenerateSolution

VERBOSE = False
HELP = 'Usage: %s ' % sys.argv[0]

def collectFiles( startDir, suffix ):
	result = []
	for root, dirs, files in os.walk(startDir):
		for name in files:
			base, ext = os.path.splitext(name)
			if ext.lower() == suffix:
				result += [os.path.join(root, name)]
	return result

def main( argv ):
	configFiles = collectFiles(os.path.abspath('.'), Engine.CONFIGURATION_SUFFIX)
	logging.info( 'Found %d configurations' % len(configFiles) )
	logging.info( 'Generating project files...' )
	for config in configFiles:
		logging.info( '%s' % config )
		GenerateProject.main([config])
	
	if 'sln' in argv:
		logging.info( 'Generating solutions...' )
		okSolutions = 0
		for config in configFiles:
			if 0 == GenerateSolution.main([config]):
				okSolutions += 1
				logging.info( '%s' % config )
		logging.info( 'Generated %d solutions' % okSolutions )
	else:
		logging.info( 'Skipping sln generation, specify "sln" on the command line to generate solutions' )
	return 0

if __name__ == '__main__':
	if VERBOSE:
		logging.basicConfig( level = logging.DEBUG, format = '%(levelname)s %(message)s' )
	else:
		logging.basicConfig( level = logging.INFO, format = '%(message)s' )
	sys.exit( main( sys.argv[1:] ) )
