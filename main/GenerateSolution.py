#!/usr/bin/python
#
# Generates a visual studio compatible project from a template through the tinyconfig engine.
#
# (C) 2007 Jim Tilander
import logging
import os
import sys
import string
import Engine
import PathHelp

VERBOSE = False
HELP = 'Usage: %s <configfile> or <solutionfile> <platform>' % sys.argv[0]

VS2013HEADER = "Microsoft Visual Studio Solution File, Format Version 12.00\n# Visual Studio 2013\nVisualStudioVersion = 12.0.21005.1\nMinimumVisualStudioVersion = 10.0.40219.1"

def getProjectInfo(configPath):
    configPath = os.path.splitext(configPath)[0] + '.bdgcfg'
    generalDict, projectDict, solutionDict = Engine.readConfiguration(configPath)
    return generalDict['name'], '{%s}' % (projectDict['uuid'].upper())

def writeSolution( basePath, projectsList, platform, configurations ):
    projects = []
    project2dependency = {}
    
    # Generate the map of dependencies and the list of all the projects
    logging.debug( "Generating the dependencies map" )
    for lol in projectsList:
        if len(lol) == 0:
            continue
        head = lol[0]
        deps = lol[1:]
        project2dependency[ head ] = deps
        if head not in projects:
            projects.append(head)
        for dep in deps:
            if dep not in projects:
                projects.append(dep)
    
    logging.debug( "Now starting to get the projectinfos" )
    # This section holds all the different project references and the dependencies.
    projectInfos = [ getProjectInfo(x) for x in projects ]
    
    logging.debug( "Now writing the dependencies info to the solution" )
    projectSection = ''
    for i, project in enumerate(projects):
        logging.debug( "Now processing the project %s" % project )
        logging.debug( "Resolving relative path %s, %s" % (basePath, project) )
        relativePath = PathHelp.relative( basePath, project )
        name, uuid = projectInfos[i]
        projectSection += 'Project("{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942}") = "%s", "%s", "%s"\n' % (str(name), str(relativePath), uuid)
        
        if project in project2dependency:
            dependencies = project2dependency[project]
            logging.debug( "Project have dependencies, %s" % string.join(dependencies, ", " ) )
            projectSection += '\tProjectSection(ProjectDependencies) = postProject\n'
            for dependency in dependencies:
                index = projects.index(dependency)
                guid = projectInfos[index][1]
                projectSection += '\t\t%s = %s\n' % (guid, guid)
            projectSection += '\tEndProjectSection\n'
        projectSection += 'EndProject\n'
    
    # This section declares the live configurations in the solution
    platformConfigSection = ''
    for config in configurations:
        configName1 = config.split('|')[0] + '|' + platform
        configName2 = config.split('|')[0] + '|' + platform
        platformConfigSection += '\t\t%s = %s\n' % (configName1, configName2)

    # This section defines the mappings between the configuration in the solution and the 
    # ones in the projects
    configurationSection = ''
    for i, project in enumerate(projects):
        guid = projectInfos[i][1]
        for config in configurations:
            solutionConfig = config.split('|')[0] + '|' + platform
            projectConfig = config
            configurationSection += '\t\t%s.%s.Build.0 = %s\n' % (guid, solutionConfig, projectConfig)
            configurationSection += '\t\t%s.%s.ActiveCfg = %s\n' % (guid, solutionConfig, projectConfig)

    return """%s
Global
    GlobalSection(SolutionConfigurationPlatforms) = preSolution
%s
    EndGlobalSection
    GlobalSection(ProjectConfigurationPlatforms) = postSolution
%s
    EndGlobalSection
    GlobalSection(SolutionProperties) = preSolution
        HideSolutionNode = FALSE
    EndGlobalSection
EndGlobal
""" % (projectSection.rstrip(), platformConfigSection.rstrip(), configurationSection.rstrip())

def writeSingleSolution(configFileName, projectExt, solutionExt, solutionHeader, is2010):
    basePath = os.path.dirname(configFileName)
    try:
        # Load the overall configuration from the .tcfg file.
        generalDict, projectDict, solutionDict = Engine.readConfiguration(configFileName)
        if len(solutionDict) == 0:
            logging.debug('No solution section found, bailing out of solution generation (offending file %s)' % configFileName)
            return 1

        if 'dependencies' not in solutionDict:
            solutionDict['dependencies'] = ''
        if 'dependenciespaths' not in solutionDict:
            solutionDict['dependenciespaths'] = ''

        if 'additionalprojects' not in solutionDict:
            solutionDict['additionalprojects'] = ''
        if 'additionalprojectspaths' not in solutionDict:
            solutionDict['additionalprojectspaths'] = ''

        # Determine the output product path.
        targetName = os.path.join( basePath, generalDict['name'] + solutionExt )
        logging.debug( 'Now generating solution %s' % targetName )
        
        baseProject = os.path.splitext(configFileName)[0] + projectExt
        dependencies = Engine.findDependencies( basePath, solutionDict['dependencies'], solutionDict['dependenciespaths'], generalDict['platform'], lambda x: x+'.bdgcfg')

        additionalProjects = Engine.findDependencies( basePath, solutionDict['additionalprojects'], solutionDict['additionalprojectspaths'], generalDict['platform'], lambda x: x+'.bdgcfg')
        
        platform = projectDict['platform']
        solution = writeSolution( basePath, [[baseProject] + [os.path.splitext(x)[0] + projectExt for x in dependencies]] + [[os.path.splitext(x)[0] + projectExt for x in additionalProjects]], platform, Engine.getConfigurations(projectDict))

        # All is now done, try to write the target file to disk...
        Engine.writeConfigFile( targetName, solutionHeader + '\n' + solution )
    except SyntaxError, e:
        logging.error( str(e) )
        return 1
    return 0

def writeMultiSolution(targetSolutionName, candidates, projectExt, solutionHeader, is2010):
    basePath = os.path.dirname(targetSolutionName)
    projects = []
    for item in map(os.path.abspath, candidates):
        generalDict, projectDict, solutionDict = Engine.readConfiguration(item)
        if len(solutionDict) == 0:
            logging.debug('No solution section found, skipping (offending file %s)' % item)
            continue

        baseProject = os.path.splitext(item)[0] + projectExt
        try:
            dependencies = Engine.findDependencies( basePath, solutionDict['dependencies'], solutionDict['dependenciespaths'], generalDict['platform'], lambda x: x+'.bdgcfg' )
        except KeyError:
            dependencies = []
        
        # HACK: The platform will just be the last one referenced.
        platform = projectDict['platform']
        projects.append( [baseProject] + [os.path.splitext(x)[0] + projectExt for x in dependencies] )

    solution = writeSolution( basePath, projects, platform, Engine.getConfigurations(projectDict) )
    # All is now done, try to write the target file to disk...
    Engine.writeConfigFile( targetSolutionName, solutionHeader + '\n' + solution )    

def main( argv ):
    if len(argv) == 0:
        print HELP
        return 1

    if len(argv) == 1:
        # Single configuration mode. Deduce the 
        configFileName = os.path.abspath(argv[0])
        writeSingleSolution(configFileName, '.vcxproj', '.sln', VS2013HEADER, 1)
        return 0
    
    # Multiple project into one single solution mode.
    targetSolutionName = os.path.abspath(os.path.splitext(argv[0])[0])
    platform = argv[1]
    startdir = os.path.abspath('.')
    if len(argv) > 2:
        startdir = os.path.abspath(argv[2])
        print 'Startdir = ' + startdir

    candidates = []
    for root, dirs, files in os.walk(startdir):
        for name in files:
            if platform.lower() != os.path.basename(root).lower():
                continue
            ext = os.path.splitext(name)[1]
            if ".bdgcfg" != ext:
                continue
            fullname = os.path.join(root, name)
            candidates.append(fullname)
    
    writeMultiSolution(targetSolutionName + '.sln', candidates, '.vcxproj', VS2013HEADER, 1)
    return 0
    

if __name__ == '__main__':
    if VERBOSE:
        logging.basicConfig( level = logging.DEBUG, format = '%(levelname)s %(message)s' )
    else:
        logging.basicConfig( level = logging.INFO, format = '%(levelname)s %(message)s' )
    sys.exit( main( sys.argv[1:] ) )
