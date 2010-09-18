#!/usr/bin/python
#
#
#
# (C) 2007 Jim Tilander
import logging
import os
import sys
import re
import ConfigParser
import PathHelp
import copy
import string

GENERAL_SECTION_NAME = 'General'
PROJECT_SECTION_NAME = 'Project'
SOLUTION_SECTION_NAME = 'Solution'
TEMPLATES_DIR = os.path.join( os.path.dirname(__file__), 'Templates')
VALID_CONFIG_TYPES = ['ConsoleApplication', 'StaticLibrary', 'WindowsApplication',  'DynamicLibrary', 'MfcApplication']
GENERAL_SECTION_ONLY_VARIABLES = ['type', 'sourcefiles']
CONFIGURATION_NAMES__NAKED = ['Debug', 'Release', 'Profile', 'Final']
CONFIGURATION_SUFFIX = '.bdgcfg'
PATHVARIABLES = ['includespaths', 'librarypaths', 'dependenciespaths']
DEFAULT_PLATFORMNAME = 'Win32'

def getConfigurations(projectDict):
    platform = projectDict['platform']
    if 'platformconfigalias' in projectDict.keys():
        platform = projectDict['platformconfigalias']
    return [ '%s|%s' % (x, platform) for x in CONFIGURATION_NAMES__NAKED ]

def mergeSeparatedStrings(a, b, separator):
    assert( isinstance( a, type('') ) )
    assert( isinstance( b, type('') ) )
    assert( len(separator) == 1 )
    result = a
    if not result.endswith(separator):
        result += separator
    if b.startswith(separator):
        b = b[len(separator):]
    result += b
    return result

def convertToRelativeList( baseDir, separatedList, separator ):
    result = []
    for item in separatedList.split( separator ):
        if len(item) == 0:
            continue
        result.append( PathHelp.relative( baseDir, item ).replace(os.sep,'/') )
    return string.join(result,separator)

def convertToAbsolutePathList( baseDir, separatedList, separator ):
    result = []
    for item in separatedList.split( separator ):
        if len(item) == 0:
            continue
        path = PathHelp.normalize( os.path.join( baseDir, item.replace('/', os.sep) )  )
        result.append( path )
    return string.join(result,separator)

def ensureLeadingSeparator(data, separator):
    if len(data) == 0:
        return data
    if data[0] != separator:
        return separator + data
    return data

def copyDictWithExclusions( general, excludedKeys ):
    """
        Takes one dictionary and copies it into another but excluding the values given in the exclude list.
        Returns a new dictionary
    """
    assert( isinstance(general, type({})) )
    assert( isinstance(excludedKeys, type([])) )
    
    result = {}
    for name, value in general.iteritems():
        if name in excludedKeys:
            continue
        result[ name ] = value
    return result

def parseSection(baseDir, sectionName, defaultDict, parser, errorDict):
    result = copy.deepcopy(defaultDict)
    try:
        for name, value in parser.items(sectionName):
            key = name.lower()
            # Special parsing of variables that are comma separated paths, they should always refer relative to the configuration file.
            if key.endswith('path'):
                value = convertToAbsolutePathList(baseDir, value, ';')
            if key.endswith('paths'):
                value = convertToAbsolutePathList(baseDir, value, ';')
                value = ensureLeadingSeparator(value,';')
            if key.endswith('defines'):
                value = ensureLeadingSeparator(value,';')
            if key in result.keys():
                if key.endswith('defines') or key.endswith('paths') or key.endswith('options') or key.endswith('libraries'):
                    old = result[ key ]
                    result[ key ] = value + old
                else:
                    result[ key ] = value
            else:
                result[ key ] = value
    except ConfigParser.NoSectionError:
        return errorDict
    return result

def loadDefaultDict( platform, section, default ):
    filename = os.path.join( TEMPLATES_DIR, platform, 'MasterConfig' )
    myParser = ConfigParser.ConfigParser()
    myParser.read(filename)
    return parseSection( os.path.dirname(filename), section, default, myParser, {} )

def generateUUID( name, platform ):
    text = name + '/' + platform
    import md5
    hexdigest = md5.new( text ).hexdigest()
    # HexDigest is 32 hex characters long, the UUID is 8-4-4-4-12 characters long == 32.
    result = '%s-%s-%s-%s-%s' % (hexdigest[0:8], hexdigest[8:12], hexdigest[12:16], hexdigest[16:20], hexdigest[20:32])
    return result

def readConfiguration(configFileName):
    """
        configFileName needs to be an absolute path
        Returns three separate dictionaries if the corresponding section is present in the configfile
    """
    assert( isinstance( configFileName, type('') ) )
    configFile = open(configFileName)
    
    # Figure out the defaults
    baseDir = os.path.dirname(configFileName)
    parentDir = os.path.basename( os.path.dirname(configFileName) )
    fileName = os.path.splitext( os.path.basename(configFileName) )[0]
    parser = ConfigParser.ConfigParser()
    parser.read(configFileName)
    
    # Now populate the dictionaries
    generalDict = {}
    generalDict['platform'] = parentDir
    generalDict['debugname']    = CONFIGURATION_NAMES__NAKED[0]
    generalDict['releasename']  = CONFIGURATION_NAMES__NAKED[1]
    generalDict['profilename']  = CONFIGURATION_NAMES__NAKED[2]
    generalDict['finalname']    = CONFIGURATION_NAMES__NAKED[3]
    generalDict['platformname'] = DEFAULT_PLATFORMNAME
    
    generalDict['name'] = fileName
    generalDict = parseSection(baseDir, GENERAL_SECTION_NAME, generalDict, parser, generalDict)
    
    if 'type' not in generalDict:
        raise SyntaxError('Must have a type key in the general section, choose from %s (offending file was %s)' % (str(VALID_CONFIG_TYPES), configFileName) )
    
    projectDict = loadDefaultDict(generalDict['platform'], PROJECT_SECTION_NAME, copyDictWithExclusions(generalDict, GENERAL_SECTION_ONLY_VARIABLES))
    projectDict = parseSection(baseDir, PROJECT_SECTION_NAME, projectDict, parser, projectDict)
    
    if 'uuid' not in projectDict:
        projectDict['uuid'] = generateUUID(fileName, parentDir)

    solutionDict = loadDefaultDict(generalDict['platform'], SOLUTION_SECTION_NAME, copyDictWithExclusions(generalDict, GENERAL_SECTION_ONLY_VARIABLES))
    solutionDict = parseSection(baseDir, SOLUTION_SECTION_NAME, solutionDict, parser, {})
    return generalDict, projectDict, solutionDict

def getTemplatesDir( generalDict ):
    assert( isinstance( generalDict, type({}) ) )
    platform = generalDict['platform']
    configtype = generalDict['type']
    filename = os.path.join( TEMPLATES_DIR, platform )
    return filename

def replaceKeywords( basePath, template, projectDict, fixupRules ):
    """
        Steps through the template and finds all the instances with %%%KEYWORD%%% and for each instance runs 
        a replace with a new value calculated from the project dictionary and run through any rules given in the 
        fixupRules dictionary (which should contain a list of functions that can transform the entry from first to last entry in a chain).
        
        Returns the new replaced string.
    """
    assert( isinstance( template, type('') ) )
    assert( isinstance( projectDict, type({}) ) )
    assert( isinstance( fixupRules, type({}) ) )
    
    pattern = re.compile( r'\%\%\%([^\%]+)\%\%\%' )
    keywords = [ x.group(1).lower() for x in re.finditer( pattern, template ) ]

    for keyword in keywords:
        try:
            value = projectDict[keyword]
            if keyword.endswith('path'):
                value = PathHelp.relative( basePath, value ).replace(os.sep,'/') 
            if keyword.endswith('paths'):
                value = convertToRelativeList( basePath, value, ';' )
            try:
                fixupChain = fixupRules[keyword]
                for patcher in fixupChain:
                    value = patcher(value)
            except KeyError:
                pass
        except KeyError:
            value = ''
        logging.debug( 'Transforming %30s -> %s' % ('%%%%%%%s%%%%%%' % keyword.upper(), value) )
        template = template.replace( '%%%%%%%s%%%%%%' % keyword.upper(), value )
    return template

def writeConfigFile( filename, data ):
    assert( isinstance( filename, type('') ) )
    assert( isinstance( data, type('') ) )
    logging.debug( 'About to write the final text configuration file to "%s"' % filename )
    # TODO: Here we can insert hooks for automatically checkout files from sourcecontrol
    stream = file( filename, 'wt' )
    stream.write(data)
    stream.close()

def findFile( basePath, searchName, platform ):
    """
        Typically this function is called from findDependencies, it resolves a .vcproj file typically given a platform and a base directory.
        A recursive search is performed to try to find the filename. If there are multiple candidates, the platform must match. If only 
        one candidate is found, it's assumed that the platform matches.
        
        Returns a full path to the requested filename
    """
    logging.debug( 'Trying to find file %s with platform %s under %s' % (searchName, platform, basePath))
    candidates = []
    for root, dirs, files in os.walk( basePath ):
        for name in files:
            fullName = os.path.join(root, name)
            if searchName.lower() != name.lower():
                continue
            candidates.append(fullName)
            candidateParentDir = os.path.basename( os.path.dirname( fullName ) )
            if platform.lower() != candidateParentDir.lower():
                continue
            return fullName
    # Ok, if we find just *one* instance of the .vcproj or similar file, we can be resonable sure that the user wanted this 
    # dependency in the solution, this to allow "foreign" projects not generated by BadgerConfig, but that we still want to depend upon.
    if len(candidates) == 1:
        return candidates[0]
    return ""

def findDependencies( basePath, dependencies, searchPaths, platform, fileNameFunctor ):
    """
        Resolve dependencies given a list of dependencies from the ini file (comma separated list) and a list of search paths (comma separated list)
        as well as the platform and a callback function that can transform the dependency name into a filename, e.g. given a dependency
        "Foo" the function could return "Foo.vcproj".
        
        Returns a list of paths to the resolved depndency files
    """
    assert( isinstance( basePath, type('') ) )
    assert( isinstance( dependencies, type('') ) )
    assert( isinstance( searchPaths, type('') ) )
    assert( isinstance( platform, type('') ) )
    assert( callable( fileNameFunctor ) )

    result = []
    if len(dependencies) and 0 == len(searchPaths):
        raise SyntaxError( 'We have dependencies, but no search paths' )
    
    searchPaths = [ PathHelp.normalize( os.path.join(basePath, x ) ) for x in searchPaths.split(';') ]
    for dependency in dependencies.split(';'):
        dependency = string.strip(dependency)
        if 0 == len(dependency):
            continue
        searchName = fileNameFunctor(dependency)
        logging.debug( 'Now searching for %s' % searchName )
        for searchPath in searchPaths:
            logging.debug( 'Current search path "%s"' % searchPath )
            candidate = findFile( searchPath, searchName, platform )
            if len(candidate):
                result += [candidate]
                break
        else:
            raise KeyError( 'Failed to find dependency %s in %s' % (searchName, searchPaths) )
    return result
