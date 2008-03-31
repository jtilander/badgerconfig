#!/usr/bin/python
#
# Generates a visual studio compatible project from a template through the tinyconfig engine.
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
VISUAL_STUDIO_TEMPLATE = 'CppBuildTemplate.vcproj'

LINK_SECTION =  {
	'debug':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="true"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="2"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>""",

	'release':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="true"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="2"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>""",

	'profile':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="1"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>""",

	'final':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="1"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>"""
}


DLL_LINK_SECTION = {
	'debug':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="true"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="2"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>""",

	'release':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="true"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="2"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>""",

	'profile':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="1"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>""",

	'final':
"""			<Tool
				Name="VCLinkerTool"
				LinkLibraryDependencies="true"
				UseLibraryDependencyInputs="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				ShowProgress="0"
				OutputFile="%%%OUTPUTFILE%%%"
				LinkIncremental="1"
				SuppressStartupBanner="true"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				GenerateManifest="true"
				ModuleDefinitionFile=""
				GenerateDebugInformation="true"
				GenerateMapFile="true"
				MapFileName="$(TargetDir)$(TargetName).map"
				MapExports="false"
				SubSystem="1"
				StackReserveSize="1048576"
				StackCommitSize="1048576"
				LargeAddressAware="2"
				TargetMachine="1"
				AllowIsolation="true"
				Profile="false"
			/>"""
}

LIBRARIAN_SECTION = {
	'debug': 
"""			<Tool
				Name="VCLibrarianTool"
				LinkLibraryDependencies="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				OutputFile="%%%OUTPUTFILE%%%"
				SuppressStartupBanner="true"
				AdditionalOptions="/IGNORE:4221 /IGNORE:4006"
			/>""",
	'release' :
"""			<Tool
				Name="VCLibrarianTool"
				LinkLibraryDependencies="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				OutputFile="%%%OUTPUTFILE%%%"
				SuppressStartupBanner="true"
				AdditionalOptions="/IGNORE:4221  /IGNORE:4006"
			/>""",
	'profile' :
"""			<Tool
				Name="VCLibrarianTool"
				LinkLibraryDependencies="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				OutputFile="%%%OUTPUTFILE%%%"
				SuppressStartupBanner="true"
				AdditionalOptions="/IGNORE:4221  /IGNORE:4006"
			/>""",
	'final' :
"""			<Tool
				Name="VCLibrarianTool"
				LinkLibraryDependencies="false"
				AdditionalDependencies="%%%LIBRARIES%%% %%%{{{CONFIG}}}LIBRARIES%%%"
				AdditionalLibraryDirectories="%%%LIBRARYPATHS%%% %%%{{{CONFIG}}}LIBRARYPATHS%%%"
				OutputFile="%%%OUTPUTFILE%%%"
				SuppressStartupBanner="true"
				AdditionalOptions="/IGNORE:4221  /IGNORE:4006"
			/>"""
}

def xmlEnsureFileDirectory( element, folderItems, nodeFactory ):
	if 0 == len(folderItems):
		return element
	for child in element.childNodes:
		if child.tagName != 'Filter':
			continue
		if child.getAttribute('Name') == folderItems[0]:
			return xmlEnsureFileDirectory( child, folderItems[1:], nodeFactory )
	filter = nodeFactory( 'Filter' )
	filter.setAttribute( 'Name', folderItems[0] )
	element.appendChild( filter )
	return xmlEnsureFileDirectory( filter, folderItems[1:], nodeFactory )
	
def xmlCreateSingleFileElement( document, baseDir, item ):
	nodeToAddTo = xmlEnsureFileDirectory( document.documentElement, item.folderPath, document.createElement )
	node = document.createElement( 'File' )
	nodeToAddTo.appendChild(node)
	
	relativePath = PathHelp.relative(baseDir, item.fullpath)
	node.setAttribute( 'RelativePath', relativePath )
	
	try:
		customrule = item.options['customrule']
		for config in Engine.CONFIGURATION_NAMES:
			configNode = document.createElement( 'FileConfiguration' )
			configNode.setAttribute( 'Name', config )
			toolNode = document.createElement( 'Tool' )
			command, extension = customrule.split(',')
			outputName = '$(InputDir)$(InputName)%s' % extension
			toolNode.setAttribute( 'Name', 'VCCustomBuildTool' )
			toolNode.setAttribute( 'Description', "%s %s" % (command, "$(InputFileName)") )
			toolNode.setAttribute( 'CommandLine', '%s $(InputDir)$(InputFileName) %s' % (command, outputName) )
			toolNode.setAttribute( 'Outputs', outputName )
			configNode.appendChild(toolNode)
			node.appendChild(configNode)
	except KeyError:
		pass

	haveCompilerOption = False
	if len( item.outputBase ):
		haveCompilerOption = True
	if 'precompiled' in item.options.keys():
		haveCompilerOption = True
	if 'languageextensions' in item.options.keys():
		haveCompilerOption = True
	
	if haveCompilerOption:
		for config in Engine.CONFIGURATION_NAMES:
			configNode = document.createElement( 'FileConfiguration' )
			configNode.setAttribute( 'Name', config )
			toolNode = document.createElement( 'Tool' )
			toolNode.setAttribute( 'Name', 'VCCLCompilerTool' )
			
			if len( item.outputBase ):
				toolNode.setAttribute( 'ObjectFile', '$(IntDir)\%s.obj' % item.outputBase )
			
			if 'precompiled' in item.options.keys():
				toolNode.setAttribute( 'UsePrecompiledHeader', item.options['precompiled'] )
			if 'languageextensions' in item.options.keys():
				value = item.options['languageextensions']
				if value == '1':
					disableFlag = 'false'
				else:
					disableFlag = 'true'
				toolNode.setAttribute( 'DisableLanguageExtensions', disableFlag )
			
			configNode.appendChild(toolNode)
			node.appendChild(configNode)
	if len(node.childNodes) == 0:
		node.appendChild( document.createTextNode('') )
	
def xmlCreateNewDocument(topTagName):
	from xml.dom.minidom import getDOMImplementation
	impl = getDOMImplementation()
	doc = impl.createDocument( None, topTagName, None )
	return doc

def xmlSortAttributeKeys(keys):
	keys.sort()
	if 'Name' in keys:
		del keys[keys.index('Name')]
		keys = ['Name'] + keys
	return keys

def xmlPrettyPrint( elementNode, indent ):
	if elementNode.nodeType != elementNode.ELEMENT_NODE:
		return ''
	result = ''
	
	attributeCount = len(elementNode.attributes.keys())
	childCount = len(elementNode.childNodes)
	
	result += '%s<%s\n' % (indent, elementNode.tagName)
	keys = xmlSortAttributeKeys(elementNode.attributes.keys())
	for key in keys:
		result += '%s\t%s="%s"\n' % (indent, key, elementNode.getAttribute(key))
	if childCount == 0:
		result += '%s/>\n' % indent
	else:
		result += '%s\t>\n' % indent
		for child in elementNode.childNodes:
			result += xmlPrettyPrint( child, indent + '\t' )
		result += '%s</%s>\n' % (indent, elementNode.tagName)
	return result

def generateFiles( baseDir, sourceFiles ):
	document = xmlCreateNewDocument('Files')
	for item in sourceFiles:
		xmlCreateSingleFileElement( document, baseDir, item )
	
	result  = '\t<Files>\n'
	for node in document.documentElement.childNodes:
		result += xmlPrettyPrint( node, '\t\t' )
	result += '\t</Files>'
	return result

def readTemplate(generalDict):
	dir = Engine.getTemplatesDir(generalDict)
	filename = os.path.join(dir, VISUAL_STUDIO_TEMPLATE )
	
	if generalDict['type'] == 'ConsoleApplication':
		linkSectionTemplate = LINK_SECTION
		configType = '1'
		defaultOutput = r'$(OutDir)\$(ProjectName).exe'
	elif generalDict['type'] == 'StaticLibrary':
		linkSectionTemplate = LIBRARIAN_SECTION
		configType = '4'
		defaultOutput = r'$(OutDir)\$(ProjectName).lib'
	elif generalDict['type'] == 'DynamicLibrary':
		configType = '2'
		defaultOutput = r'$(OutDir)\$(ProjectName).dll'
		linkSectionTemplate = DLL_LINK_SECTION
	else:
		raise SyntaxError( 'Unsupported type!' )
	
	template = file(filename).read()
	# Replace the link section
	for config, platform in [x.split('|') for x in Engine.CONFIGURATION_NAMES]:
		linkSection = linkSectionTemplate[config.lower()].replace( '{{{CONFIG}}}', config.upper() )
		template = template.replace( '{{{%s_LINK_SECTION}}}' % config.upper(), linkSection )
	
	template = template.replace( '{{{CONFIG_TYPE}}}', configType )
	return template, defaultOutput

def getConfigType(generalDict):
	if generalDict['type'] == 'ConsoleApplication':
		return '1'
	elif generalDict['type'] == 'StaticLibrary':
		return '4'
	elif generalDict['type'] == 'DynamicLibrary':
		return '2'
	else:
		raise SyntaxError( 'Unsupported type!' )

def getPrecompiledHeaderFlag(sourceFiles):
	for item in sourceFiles:
		try:
			if 'precompiled' in item.options.keys():
				logging.debug( 'Project is using precompiled headers' )
				return "2"
		except KeyError:
			pass
	logging.debug( 'Project is not using precompiled headers' )
	return "0"

def addBraces(value):
	return "{" + value + "}"

def main( argv ):
	if len(argv) != 1:
		print HELP
		return 1
	
	configFileName = os.path.abspath(argv[0])
	basePath = os.path.dirname(configFileName)
	try:
		# Load the overall configuration from the file.
		generalDict, projectDict, solutionDict = Engine.readConfiguration(configFileName)
		
		# Determine the output product path.
		targetName = os.path.join( basePath, generalDict['name'] + '.vcproj' )
		
		# Transform the sourcefiles keyword to a .vcproj compatible xml section and replace it in the template
		# before the general substiution engine can have it's turn
		sourceFiles = FileItem.readSourceFiles( basePath, generalDict['sourcefiles'] )
		filesSection = generateFiles( os.path.dirname(targetName), sourceFiles )
		template, defaultOutput = readTemplate(generalDict)
		template = template.replace( r'%%%FILES%%%', filesSection )
		
		if 'outputfile' not in projectDict:
			projectDict['outputfile'] = defaultOutput
		if 'debuginformationformat' not in projectDict:
			projectDict['debuginformationformat'] = '3'
		
		projectDict['configurationtype'] = getConfigType(generalDict)
		
		# Precompiled headers support
		projectDict['precompiledheaders'] = getPrecompiledHeaderFlag(sourceFiles)
		
		# Some of the keywords needs some special attention before they can be inserted into the xml file.
		# Set the rules before calling the substiution engine.
		fixupRules = {}
		fixupRules['uuid'] = [addBraces, string.upper]
		fixupRules['includepaths'] = [lambda x: Engine.ensureLeadingSeparator(x,';')]
		fixupRules['defines'] = [lambda x: Engine.ensureLeadingSeparator(x,';')]
		fixupRules['disabledvcwarnings'] = [lambda x: Engine.ensureLeadingSeparator(x,';')]
		project = Engine.replaceKeywords(basePath, template, projectDict, fixupRules)
		
		# All is now done, try to write the target file to disk...
		Engine.writeConfigFile( targetName, project )
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
