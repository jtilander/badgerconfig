#!/usr/bin/python
#
# Generates a Visual Studio 2013 project file
#
# (C) 2010 Jim Tilander
#
# Upgrade Guide: http://msdnrss.thecoderblogs.com/2010/03/02/visual-studio-2010-c-project-upgrade-guide/
#
#
import logging
import os
import sys
import string
import Engine
import FileItem
import PathHelp
import copy

VERIFY_FILES = 1

VERBOSE = True
HELP = 'Usage: %s <configfile>' % sys.argv[0]
VISUAL_STUDIO_MASTER_TEMPLATE = 'CppBuildTemplate.vcxproj'
VISUAL_STUDIO_TEMPLATES = {
    'ConsoleApplication'    : 'CppConsoleLink.vcxproj',
    'StaticLibrary'         : 'CppLibraryLink.vcxproj',
    'DynamicLibrary'        : 'CppConsoleLink.vcxproj',
    'MfcApplication'        : 'CppWindowsLink.vcxproj',
    'MfcDynamicLibrary'     : 'CppConsoleLink.vcxproj',
    'WindowsApplication'    : 'CppWindowsLink.vcxproj',
}

CONFIGTYPE_TABLE = {
    'ConsoleApplication'    : 'Application',
    'MfcApplication'        : 'Application',
    'MfcDynamicLibrary'     : 'DynamicLibrary',
    'StaticLibrary'         : 'StaticLibrary',
    'DynamicLibrary'        : 'DynamicLibrary',
    'WindowsApplication'    : 'Application',
}

MFC_USAGE_TABLE = {
    'ConsoleApplication'    : 'false',
    'MfcApplication'        : 'Dynamic',
    'MfcDynamicLibrary'     : 'Dynamic',
    'StaticLibrary'         : 'false',
    'DynamicLibrary'        : 'false',
    'WindowsApplication'    : 'false'
}

CHARACTER_SET_TABLE = {
    'ConsoleApplication'    : 'MultiByte',
    'MfcApplication'        : 'Unicode',
    'MfcDynamicLibrary'     : 'Unicode',
    'StaticLibrary'         : 'MultiByte',
    'DynamicLibrary'        : 'MultiByte',
    'WindowsApplication'    : 'Unicode'
}

FILTER_GROUPS = [
    ('ClInclude',           ['.h', '.hxx', '.inl']), 
    ('ClCompile',           ['.cpp', '.c', '.cxx']),
    ('ResourceCompile',     ['.rc']),
    ('Object',              ['.obj', '.o']),
    ('Library',             ['.lib', '.a'])
]

def readTemplate(generalDict, projectdict):
    dir = Engine.getTemplatesDir(generalDict)
    
    try:
        filename = os.path.join(dir, VISUAL_STUDIO_MASTER_TEMPLATE)
        template = file(filename).read()
    except IOError:
        return ''
    
    typefilename = os.path.join(dir, VISUAL_STUDIO_TEMPLATES[generalDict['type']])
    typetemplate = file(typefilename).read()

    for config in Engine.CONFIGURATION_NAMES__NAKED:
        ttp = typetemplate.replace('{{{CONFIG}}}', config.upper())
        template = template.replace( '{{{%sLINKSECTION}}}' % config.upper(), ttp )

    template = template.replace('{{{MFC_USAGE}}}', MFC_USAGE_TABLE[generalDict['type']])
    template = template.replace('{{{CHARACTER_SET}}}', CHARACTER_SET_TABLE[generalDict['type']])
    return template

def addBraces(value):
    return "{" + value + "}"

def getGlobalPCHString(sourceFiles, projectDict):
    if 'nopch' in projectDict:
        return ''
    for item in sourceFiles:
        if 'precompiled' not in item.options.keys():
            continue
        pch = item.options['precompiled']
        if '0' == pch:
            continue
        result = ''
        result += "\t\t<PrecompiledHeader>Use</PrecompiledHeader>\n"
        name = os.path.splitext(item.name)[0]
        result += "\t\t<PrecompiledHeaderFile>%s</PrecompiledHeaderFile>\n" % (name + '.h')
        return result
    return ''

def getGUIDByBdcfg(configfile):
    """
    Given a path to a .bdgcfg file, figure out the UUID for that file.
    """
    generalDict, projectDict, solutionDict = Engine.readConfiguration(configfile)
    return projectDict['uuid']

def generateFilters( baseDir, sourceFiles_, uuidBase ):
    result  = '<?xml version="1.0" encoding="utf-8"?>\n'
    result += '<Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">\n'
    
    sourceFiles = copy.deepcopy(sourceFiles_)
    worklist = []
    
    # Generate the folder structure
    result += '\t<ItemGroup>\n'
    folderComponents = set()
    for folder in [x.folderPath for x in sourceFiles]:
        if len(folder) == 0:
            continue
        #print folder
        candidate = []
        for i in xrange(len(folder)):
            folderComponents.add( '\\'.join(folder[0:i+1]) )
    
    for folder in sorted(folderComponents):
        if len(folder) == 0:
            continue
        uuid = Engine.generateUUID(uuidBase, folder)
        result += '\t\t<Filter Include="%s">\n' % folder
        result += '\t\t\t<UniqueIdentifier>{%s}</UniqueIdentifier>\n' % uuid
        result += '\t\t</Filter>\n'
    result += '\t</ItemGroup>\n'
    
    # Insert references to the actual files
    for rule, exts in FILTER_GROUPS:
        result += '\t<ItemGroup>\n'
        for item in sorted(sourceFiles, FileItem.sortOnFileName):
            if item.ext in exts:
                folder = '\\'.join(item.folderPath)
                relative = PathHelp.relative(baseDir, item.fullpath)
                if len(folder) == 0:
                    result += '\t\t<%s Include="%s" />\n' % (rule, relative)
                else:
                    result += '\t\t<%s Include="%s">\n' % (rule, relative)
                    result += '\t\t\t<Filter>%s</Filter>\n' % folder
                    result += '\t\t</%s>\n' % rule
            else:
                worklist.append(item)
        sourceFiles = worklist
        worklist = []
            
        result += '\t</ItemGroup>\n'

    result += '\t<ItemGroup>\n'
    for item in sorted(sourceFiles, FileItem.sortOnFileName):
        folder = '\\'.join(item.folderPath)
        relative = PathHelp.relative(baseDir, item.fullpath)
        rule = 'None'
        if 'customrule' in item.options.keys():
            rule = 'CustomBuild'
        if 'customvcbuild' in item.options.keys():
            rule = 'CustomBuild'
        if len(folder) == 0:
            result += '\t\t<%s Include="%s" />\n' % (rule, relative)
        else:
            result += '\t\t<%s Include="%s">\n' % (rule, relative)
            result += '\t\t\t<Filter>%s</Filter>\n' % folder
            result += '\t\t</%s>\n' % rule
    result += '\t</ItemGroup>\n'

    result += '</Project>\n'
    return result

def generateFiles( baseDir, sourceFiles_, projectDict ):
    from xml.sax.saxutils import escape
    result = ''

    projectName = projectDict['name']
    sourceFiles = copy.deepcopy(sourceFiles_)
    worklist = []

    #
    # Make sure that all the files exist, since the VS2010 build system gets confused otherwise...
    #
    if VERIFY_FILES:
        for file in sourceFiles:
            fullname = file.fullpath
            if not os.path.isfile( fullname ):
                logging.warning( '    ! Missing file: %s' % fullname )
    
    #
    # Go through all the "compile" like simple options
    #
    for rule, exts in FILTER_GROUPS:
        result += '\t<ItemGroup>\n'
        for item in sorted(sourceFiles, FileItem.sortOnFileName):
            if 'customrule' in item.options.keys():
                worklist.append(item)
                continue
            if 'customvcbuild' in item.options.keys():
                worklist.append(item)
                continue
            if item.ext in exts:
                options = ''
                if 'precompiled' in item.options.keys() and 'nopch' not in projectDict:
                    pch = item.options['precompiled']
                    if '0' == pch:
                        options += """\t\t\t<PrecompiledHeader>NotUsing</PrecompiledHeader>"""
                    elif '1' == pch:
                        options += """\t\t\t<PrecompiledHeader>Create</PrecompiledHeader>\n"""
                        options += """\t\t\t<AdditionalOptions>/Ylsm_%s_library_pch %%(AdditionalOptions)</AdditionalOptions>""" % projectName
                if len(options):
                    options += '\n'
                relative = PathHelp.relative(baseDir, item.fullpath)
                line = '\t\t<%s Include="%s">\n%s\t\t</%s>\n' % (rule, relative, options, rule)
                result += line
            else:
                worklist.append(item)
        result += '\t</ItemGroup>\n'
        sourceFiles = worklist
        worklist = []

    #
    # Process the custom rules...
    #
    for item in sorted(sourceFiles, FileItem.sortOnFileName):
        if 'customrule' not in item.options.keys():
            worklist.append(item)
        else:
            customrule = item.options['customrule']
            command, extension = customrule.split(',')
            relative = PathHelp.relative(baseDir, item.fullpath)
            src = '$(ProjectDir)%s' % relative
            dst = '$(ProjectDir)%s' % os.path.splitext(relative)[0] + extension
            
            # Ahrg! VS2010 launches the command as part of a batch script it seems! If we don't prefix the command with "cmd /c", it will only run the *first* one!
            # Fuuuuuuuuu! How stupid is that?
            result += '\t<ItemGroup>\n'
            result += '\t\t<CustomBuild Include="%s">\n' % relative
            result += '\t\t\t<Command>cmd /c %s "%s" "%s"</Command>\n' % (escape(command), src, dst)
            result += '\t\t\t<Message>%s %s</Message>\n' % (escape(command), src)
            result += '\t\t\t<Outputs>%s</Outputs>\n' % (dst)
            result += '\t\t</CustomBuild>\n'
            result += '\t</ItemGroup>\n'

    sourceFiles = worklist
    worklist = []


    #
    # Process the newstyle custom rules
    #
    for item in sorted(sourceFiles, FileItem.sortOnFileName):
        if 'customvcbuild' not in item.options.keys():
            worklist.append(item)
        else:
            customrule = item.options['customvcbuild']
            
            # We need to patch the input, since it's VS2005 specific and they change the variable names for 2010...
            customrule = customrule.replace( '$(InputPath)', '%(FullPath)' )
            customrule = customrule.replace( '$(InputName)', '%(Filename)' )
            customrule = customrule.replace( '$(InputDir)', '%(RelativeDir)' )
            customrule = customrule.replace( '$(InputExt)', '%(Extension)' )
            
            command, dependencies, outputs = customrule.split(',')
            relative = PathHelp.relative(baseDir, item.fullpath)
            #src = '$(ProjectDir)%s' % relative
            
            # Ahrg! VS2010 launches the command as part of a batch script it seems! If we don't prefix the command with "cmd /c", it will only run the *first* one!
            # Fuuuuuuuuu! How stupid is that?
            result += '\t<ItemGroup>\n'
            result += '\t\t<CustomBuild Include="%s">\n' % relative
            result += '\t\t\t<Command>cmd /c %s</Command>\n' % (escape(command))
            result += '\t\t\t<Message>Custom Compiling %(Filename)</Message>\n'
            result += '\t\t\t<Outputs>%s</Outputs>\n' % (outputs)
            result += '\t\t\t<AdditionalInputs>%s</AdditionalInputs>\n' % (dependencies)
            result += '\t\t</CustomBuild>\n'
            result += '\t</ItemGroup>\n'

    sourceFiles = worklist
    worklist = []
    


    #
    # Place the rest of the files in the none group (just to be listed, but not compiled)
    #
    result += '\t<ItemGroup>\n'
    for item in sorted(sourceFiles, FileItem.sortOnFileName):
        relative = PathHelp.relative(baseDir, item.fullpath)
        line = '\t\t<None Include="%s"/>\n' % relative
        result += line
            
    result += '\t</ItemGroup>\n'
    
    return result

def generateReferences(basePath, platform, solutionDict):
    """
    Goes through any of the dependencies, tries to resolve them and put the uuid references in the project file.
    """
    try:
        deps = solutionDict['dependencies']
        depspath = solutionDict['dependenciespaths']
    except KeyError:
        return ''
    
    linkLibraries = 0
    try:
        if int(solutionDict['linklibraries']):
            linkLibraries = 1
    except KeyError:
        pass
    
    libraryOptions = ''
    if linkLibraries:
        libraryOptions = '\t\t\t<LinkLibraryDependencies>true</LinkLibraryDependencies>\n'


    dependencies = Engine.findDependencies( basePath, deps, depspath, platform, lambda x: x+'.bdgcfg' )    
    if len(dependencies) == 0:
        return ''

    result = '\t<ItemGroup>\n'


    for bdgcfg in dependencies:
        uuid = getGUIDByBdcfg(bdgcfg)
        vcxproj = os.path.splitext(bdgcfg)[0] + '.vcxproj'
        vcxproj = PathHelp.relative(basePath, vcxproj)
        result += '\t\t<ProjectReference Include="%s">\n\t\t\t<Project>{%s}</Project>\n%s\t\t</ProjectReference>\n' % (vcxproj, uuid, libraryOptions)
    
    result += '\t</ItemGroup>\n'
    return result

def convertSpaceToSemicolon(src):
    r = src.replace(' ', ';')
    r = r.strip()
    if len(r):
        r = r + ';'
    return r

def transformToVS2010(number):
    if int(number) == 0:
        return "None"
    if int(number) == 1:
        return "OldStyle"
    if int(number) == 3:
        return "ProgramDatabase"
    return "None"

def main( argv ):
    if len(argv) != 1:
        print HELP
        return 1
    
    configFileName = os.path.abspath(argv[0])
    basePath = os.path.dirname(configFileName)
    try:
        # Load the overall configuration from the file.
        generalDict, projectDict, solutionDict = Engine.readConfiguration(configFileName)
        platformName = generalDict['platform']
        
        projectDict['configtype'] = CONFIGTYPE_TABLE[generalDict['type']]
        
        # Determine the output product path.
        targetName = os.path.join( basePath, generalDict['name'] + '.vcxproj' )
        
        # Transform the sourcefiles keyword to a .vcproj compatible xml section and replace it in the template
        # before the general substiution engine can have it's turn
        sourceFiles = FileItem.readSourceFiles( basePath, generalDict['sourcefiles'] )

        # Setup Default outputfolder and targetname entries
        if 'outputfolder' not in projectDict:
            projectDict['outputfolder'] = '$(OBJDIR)\\$(ProjectName)_$(PlatformName)_$(Configuration)_$(ProjectGuid)_VS2013\\'
        if 'outputfilename' not in projectDict:
            projectDict['outputfilename'] = '$(ProjectName)'

        outputfile = '$(TargetName)$(TargetExt)'
        if 'outputfile' in projectDict:
            outputfile = os.path.normpath(projectDict['outputfile'])
            outputdir = os.path.dirname(outputfile)
            projectDict['outputfolder'] = outputdir + '\\'
            projectDict['outputfilename'] = os.path.splitext(os.path.basename(outputfile))[0]

        for configType in Engine.CONFIGURATION_NAMES__NAKED:
            configOutputfolder = configType.lower() + 'outputfolder'
            if configOutputfolder not in projectDict:
                projectDict[configOutputfolder] = projectDict['outputfolder']
            
            #the output file needs to use the outdir
            configOutputfile = configType.lower() + 'outputfile'
            configOutputfilename = configType.lower() + 'outputfilename'
            projectDict[configOutputfile] = '$(OutDir)\\' + os.path.basename(outputfile)
            projectDict[configOutputfilename] = projectDict['outputfilename']

        # Ensure that we have a debuginformation format
        if 'debuginformationformat' not in projectDict:
            projectDict['debuginformationformat'] = '3'
            projectDict['debuginformationformat_debug'] = '3'
        if 'debuginformationformat_debug' not in projectDict:
            projectDict['debuginformationformat_debug'] = projectDict['debuginformationformat']

        projectDict['debuginformationformat'] = transformToVS2010(projectDict['debuginformationformat'])
        projectDict['debuginformationformat_debug'] = transformToVS2010(projectDict['debuginformationformat_debug'])

        # Make sure that we have something for the OpenMP key.
        if 'openmp' not in projectDict:
            projectDict['openmp'] = 'false'

        # read the template
        template = readTemplate(generalDict, projectDict)
        if len(template) == 0:
            logging.debug('No template found for this platform')
            return 0
        
        template = template.replace('{{{DEBUGNAME}}}', Engine.CONFIGURATION_NAMES__NAKED[0].upper())
        template = template.replace('{{{RELEASENAME}}}', Engine.CONFIGURATION_NAMES__NAKED[1].upper())
        template = template.replace('{{{PROFILENAME}}}', Engine.CONFIGURATION_NAMES__NAKED[2].upper())
        template = template.replace('{{{FINALNAME}}}', Engine.CONFIGURATION_NAMES__NAKED[3].upper())
        template = template.replace('{{{PRECOMPILEDUSAGE}}}', getGlobalPCHString(sourceFiles, projectDict))
        
        fileSection = generateFiles( os.path.dirname(targetName), sourceFiles, projectDict )
        template = template.replace('{{{FILESECTION}}}', fileSection )
        
        referenceSection = generateReferences(basePath, platformName, solutionDict)
        template = template.replace('{{{REFERENCESSECTION}}}', referenceSection )

        #
        # Now we can override the postbuild commands for each configuration...
        #
        postbuildCommand = ''
        if 'postbuildcommand' in projectDict.keys():
            postbuildCommand = projectDict['postbuildcommand']
        for config in Engine.CONFIGURATION_NAMES__NAKED:
            name = config.lower() + 'postbuildcommand'
            if name in projectDict.keys():
                continue
            projectDict[name] = postbuildCommand
            #print 'KEY: %32s = %s' % (name, postbuildCommand)
        
        #
        # Some of the keywords needs some special attention before they can be inserted into the xml file.
        # Set the rules before calling the substiution engine.
        fixupRules = {}
        fixupRules['uuid'] = [addBraces, string.upper]
        fixupRules['includepaths'] = [lambda x: Engine.ensureLeadingSeparator(x,';')]
        fixupRules['defines'] = [lambda x: Engine.ensureLeadingSeparator(x,';')]
        fixupRules['disabledvcwarnings'] = [lambda x: Engine.ensureLeadingSeparator(x,';')]
        fixupRules['libraries'] = [lambda x: convertSpaceToSemicolon(x)]
        project = Engine.replaceKeywords(basePath, template, projectDict, fixupRules)
        
        # All is now done, try to write the target file to disk...
        Engine.writeConfigFile( targetName, project )
        
        # VS2010 has a user defined filters file on the side...
        filters = generateFilters(os.path.dirname(targetName), sourceFiles, generalDict['name'] + platformName)
        Engine.writeConfigFile( targetName + '.filters', filters )
        
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
