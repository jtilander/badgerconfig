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
import GenerateXcode
import getopt

def collectFiles( startDir, suffix ):
	result = []
	for root, dirs, files in os.walk(startDir):
		for name in files:
			base, ext = os.path.splitext(name)
			if ext.lower() == suffix:
				result += [os.path.join(root, name)]
	return result

def main( argv ):
	"""
		Goes recursivly down and generates all the solutions and vcproj for you.
	"""
	try:
		opts, args = getopt.getopt( argv, 'vsb:')
	except getopt.GetoptError:
		print main.__doc__
		return 1
	
	basepath = os.path.abspath('.')
	generateSLN = 0
	generateXcode = 1
	generateVcProj = 1
	verbose = 0
	for o,a in opts:
		if '-v' == o:
			verbose = 1
		if '-s' == o:
			generateSLN = 1
		if '-b' == o:
			basepath = os.path.abspath(a)
			
	if sys.platform == 'darwin':
		generateSLN = 0
		generateVcProj = 0

	if verbose:
		logging.basicConfig( level = logging.DEBUG, format = '%(levelname)s %(message)s' )
	else:
		logging.basicConfig( level = logging.INFO, format = '%(message)s' )
	
	logging.info( 'Searching %s' % basepath )
	configFiles = collectFiles(basepath, Engine.CONFIGURATION_SUFFIX)
	logging.info( 'Found %d configurations' % len(configFiles) )
	logging.info( 'Generating project files...' )
	
	#
	# This section is enterily for the visual studio projects...
	#
	solutionConfigs = []
	for config in configFiles:
		logging.info( '%s' % config )
		
		if generateVcProj:
			try:
				GenerateProject.main([config])
				solutionConfigs.append(config)
			except IOError,e:
				#logging.info( 'Ignoring unsupported config %s (%s)' % (config, str(e)) )
				logging.exception(e)
				pass
	
		if generateXcode:
			try:
				GenerateXcode.processSingleSolution(config)
			except IOError,e:
				logging.exception(e)
				pass
	
	if sys.platform != 'darwin':
		if generateSLN:
			logging.info( 'Generating solutions...' )
			okSolutions = 0
			for config in solutionConfigs:
				if 0 == GenerateSolution.main([config]):
					okSolutions += 1
					logging.info( '%s' % config )
			logging.info( 'Generated %d solutions' % okSolutions )
		else:
			logging.info( 'Skipping sln generation, specify "-s" on the command line to generate solutions' )
	
	return 0

if __name__ == '__main__':
	sys.exit( main( sys.argv[1:] ) )
