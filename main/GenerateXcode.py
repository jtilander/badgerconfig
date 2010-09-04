#!/usr/bin/python
#
# Generates a visual studio compatible project from a template through the tinyconfig engine.
#
# (C) 2007 Jim Tilander
#
#
#
#
# Main Xcode docs: http://developer.apple.com/referencelibrary/DeveloperTools/idxXcode-date.html#doclist
#
# Official docs of all the environment variables in xcode:  http://developer.apple.com/documentation/DeveloperTools/Reference/XcodeBuildSettingRef/1-Build_Setting_Reference/build_setting_ref.html
#
#
#
import logging
import os
import sys
import string
import ConfigParser
import Engine
import FileItem
import PathHelp
import getopt

VERBOSE = True
COUNTER = 0x100

XCODE_TEMPLATE = 'project.pbxproj'

RESOURCE_EXTS = ['.xib', '.png', '.pak', '.txt', '.ini']
SOURCE_EXTS = ['.cpp', '.m', '.mm', '.c']
HEADER_EXTS = ['.h', '.hh', '.hpp']

FRAMEWORKPATHS = {
	'coregraphics.framework'	: 'System/Library/Frameworks/CoreGraphics.framework',
	'foundation.framework'		: 'System/Library/Frameworks/Foundation.framework',
	'uikit.framework'			: 'System/Library/Frameworks/UIKit.framework',
	'opengles.framework'		: 'System/Library/Frameworks/OpenGLES.framework',
	'quartzcore.framework'		: 'System/Library/Frameworks/QuartzCore.framework',
	'coreaudio.framework'		: 'System/Library/Frameworks/CoreAudio.framework',
	'openal.framework'			: 'System/Library/Frameworks/OpenAL.framework',
	'audiotoolbox.framework'	: 'System/Library/Frameworks/AudioToolbox.framework',
	'avfoundation.framework'	: 'System/Library/Frameworks/AVFoundation.framework',
	'mediaplayer.framework'		: 'System/Library/Frameworks/MediaPlayer.framework',
}

FILETYPES = {
	'.cpp'		: 'sourcecode.cpp.cpp',
	'.h'		: 'sourcecode.c.h',
	'.mm'		: 'sourcecode.cpp.objcpp',
	'.m'		: 'sourcecode.c.objc',
	'.xml'		: 'text.xml',
	'.plist'	: 'text.plist.xml',
	'.txt'		: 'text',
	'.a'		: 'archive.ar',
	'.framework': 'wrapper.framework',
	'.app'		: 'wrapper.application',
	'.xib'		: 'file.xib',
	'.png'		: 'image.png',
	'.pak'		: 'file',
	'.ini'		: 'text',
}

CONFIGURATION_TEMPLATES = {
	"Debug" :			
			"""\t\t%(configuuid)s /* NativeTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer"; 
				ALWAYS_SEARCH_USER_PATHS = NO;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_ENABLE_FIX_AND_CONTINUE = NO;
				GCC_FAST_MATH = YES;
				GCC_OPTIMIZATION_LEVEL = 0;
				GCC_PRECOMPILE_PREFIX_HEADER = NO;
				GCC_THUMB_SUPPORT = NO;
				"GCC_THUMB_SUPPORT[arch=armv6]" = NO;
				"GCC_THUMB_SUPPORT[arch=armv7]" = YES;
				GCC_DEBUGGING_SYMBOLS = "full";
				GCC_ENABLE_CPP_EXCEPTIONS = NO;
				GCC_ENABLE_CPP_RTTI = NO;
				COMPRESS_PNG_FILES = NO;
				DEAD_CODE_STRIPPING = NO;
				PRESERVE_DEAD_CODE_INITS_AND_TERMS = NO;
				OTHER_LDFLAGS = "";
				INFOPLIST_FILE = Info.plist;
				PREBINDING = NO;
				PRODUCT_NAME = %(productname)s;
				WARNING_CFLAGS = "-Wall";
				GCC_PREPROCESSOR_DEFINITIONS = (
					"AURORA_IPHONE=1",
					"AURORA_DEBUGG",
					"_DEBUG=1",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv6]" = (
					"AURORA_IPHONE=1",
					"AURORA_DEBUGG",
					"AURORA_ARM6",
					"_DEBUG=1",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv7]" = (
					"AURORA_IPHONE=1",
					"AURORA_DEBUGG",
					"AURORA_ARM7",
					"_DEBUG=1",
%(defines)s
				);
				HEADER_SEARCH_PATHS = (
%(headersearchpath)s
				);
				LIBRARY_SEARCH_PATHS = (
					"$(inherited)",
					"\\"$(SRCROOT)/build/Debug-iphonesimulator\\"",
%(librarysearchpath)s					
				);				
				OTHER_CFLAGS = (
%(gccflags)s					
				);
				OTHER_LDFLAGS = (
%(ldflags)s
				);
			};
			name = Debug;
		};\n""",
	"Release" :			
			"""\t\t%(configuuid)s /* NativeTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer"; 
				ALWAYS_SEARCH_USER_PATHS = NO;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_FAST_MATH = YES;
				GCC_OPTIMIZATION_LEVEL = 2;
				GCC_ENABLE_FIX_AND_CONTINUE = NO;
				GCC_PRECOMPILE_PREFIX_HEADER = NO;
				GCC_THUMB_SUPPORT = NO;
				"GCC_THUMB_SUPPORT[arch=armv6]" = NO;
				"GCC_THUMB_SUPPORT[arch=armv7]" = YES;
				GCC_DEBUGGING_SYMBOLS = "full";
				GCC_ENABLE_CPP_EXCEPTIONS = NO;
				GCC_ENABLE_CPP_RTTI = NO;
				COMPRESS_PNG_FILES = NO;
				DEAD_CODE_STRIPPING = YES;
				PRESERVE_DEAD_CODE_INITS_AND_TERMS = NO;
				INFOPLIST_FILE = Info.plist;
				PREBINDING = NO;
				PRODUCT_NAME = %(productname)s;
				WARNING_CFLAGS = "-Wall";
				GCC_PREPROCESSOR_DEFINITIONS = (
					"AURORA_IPHONE=1",
					"AURORA_RELEASE",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv6]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM6",
					"AURORA_RELEASE",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv7]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM7",
					"AURORA_RELEASE",
%(defines)s
				);
				HEADER_SEARCH_PATHS = (
%(headersearchpath)s
				);
				LIBRARY_SEARCH_PATHS = (
					"$(inherited)",
					"\\"$(SRCROOT)/build/Debug-iphonesimulator\\"",
%(librarysearchpath)s					
				);
				OTHER_CFLAGS = (
%(gccflags)s					
				);
				OTHER_LDFLAGS = (
%(ldflags)s
				);
			};
			name = Release;
		};\n""",
	"Profile" :			
			"""\t\t%(configuuid)s /* NativeTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer"; 
				ALWAYS_SEARCH_USER_PATHS = NO;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_FAST_MATH = YES;
				GCC_OPTIMIZATION_LEVEL = 2;
				GCC_ENABLE_FIX_AND_CONTINUE = NO;
				GCC_PRECOMPILE_PREFIX_HEADER = NO;
				GCC_THUMB_SUPPORT = NO;
				"GCC_THUMB_SUPPORT[arch=armv6]" = NO;
				"GCC_THUMB_SUPPORT[arch=armv7]" = YES;
				GCC_DEBUGGING_SYMBOLS = "full";
				GCC_ENABLE_CPP_EXCEPTIONS = NO;
				GCC_ENABLE_CPP_RTTI = NO;
				COMPRESS_PNG_FILES = YES;
				INFOPLIST_FILE = Info.plist;
				PREBINDING = NO;
				PRODUCT_NAME = %(productname)s;
				WARNING_CFLAGS = "-Wall";
				GCC_PREPROCESSOR_DEFINITIONS = (
					"AURORA_IPHONE=1",
					"AURORA_PROFILE",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv6]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM6",
					"AURORA_PROFILE",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv7]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM7",
					"AURORA_PROFILE",
%(defines)s
				);
				HEADER_SEARCH_PATHS = (
%(headersearchpath)s
				);
				LIBRARY_SEARCH_PATHS = (
					"$(inherited)",
					"\\"$(SRCROOT)/build/Debug-iphonesimulator\\"",
%(librarysearchpath)s					
				);				
				OTHER_CFLAGS = (
%(gccflags)s					
				);
				OTHER_LDFLAGS = (
%(ldflags)s
				);
			};
			name = Profile;
		};\n""",
	"Final" :			
			"""\t\t%(configuuid)s /* NativeTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				CODE_SIGN_ENTITLEMENTS = Entitlements.plist;
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Distribution"; 
				ALWAYS_SEARCH_USER_PATHS = NO;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_FAST_MATH = YES;
				GCC_OPTIMIZATION_LEVEL = 2;
				GCC_ENABLE_FIX_AND_CONTINUE = NO;
				GCC_PRECOMPILE_PREFIX_HEADER = NO;
				GCC_THUMB_SUPPORT = NO;
				"GCC_THUMB_SUPPORT[arch=armv6]" = NO;
				"GCC_THUMB_SUPPORT[arch=armv7]" = YES;
				GCC_DEBUGGING_SYMBOLS = "full";
				GCC_ENABLE_CPP_EXCEPTIONS = NO;
				GCC_ENABLE_CPP_RTTI = NO;
				COMPRESS_PNG_FILES = YES;
				INFOPLIST_FILE = Info.plist;
				PREBINDING = NO;
				PRODUCT_NAME = %(productname)s;
				WARNING_CFLAGS = "-Wall";
				GCC_PREPROCESSOR_DEFINITIONS = (
					"AURORA_IPHONE=1",
					"AURORA_FINAL",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv6]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM6",
					"AURORA_FINAL",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv7]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM7",
					"AURORA_FINAL",
%(defines)s
				);
				HEADER_SEARCH_PATHS = (
%(headersearchpath)s
				);
				LIBRARY_SEARCH_PATHS = (
					"$(inherited)",
					"\\"$(SRCROOT)/build/Debug-iphonesimulator\\"",
%(librarysearchpath)s					
				);				
				OTHER_CFLAGS = (
%(gccflags)s					
				);
				OTHER_LDFLAGS = (
%(ldflags)s
				);
			};
			name = Final;
		};\n""",
	"Distribution" :			
			"""\t\t%(configuuid)s /* NativeTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Distribution"; 
				ALWAYS_SEARCH_USER_PATHS = NO;
				COPY_PHASE_STRIP = NO;
				DEBUG_INFORMATION_FORMAT = "dwarf-with-dsym";
				GCC_DYNAMIC_NO_PIC = NO;
				GCC_FAST_MATH = YES;
				GCC_OPTIMIZATION_LEVEL = 2;
				GCC_ENABLE_FIX_AND_CONTINUE = NO;
				GCC_PRECOMPILE_PREFIX_HEADER = NO;
				GCC_THUMB_SUPPORT = NO;
				"GCC_THUMB_SUPPORT[arch=armv6]" = NO;
				"GCC_THUMB_SUPPORT[arch=armv7]" = YES;
				GCC_DEBUGGING_SYMBOLS = "full";
				GCC_ENABLE_CPP_EXCEPTIONS = NO;
				GCC_ENABLE_CPP_RTTI = NO;
				INFOPLIST_FILE = Info.plist;
				PREBINDING = NO;
				PRODUCT_NAME = %(productname)s;
				WARNING_CFLAGS = "-Wall";
				GCC_PREPROCESSOR_DEFINITIONS = (
					"AURORA_IPHONE=1",
					"AURORA_FINAL",
					"AURORA_DISTRIBUTION",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv6]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM6",
					"AURORA_FINAL",
					"AURORA_DISTRIBUTION",
%(defines)s
				);
				"GCC_PREPROCESSOR_DEFINITIONS[arch=armv7]" = (
					"AURORA_IPHONE=1",
					"AURORA_ARM7",
					"AURORA_FINAL",
					"AURORA_DISTRIBUTION",
%(defines)s
				);
				HEADER_SEARCH_PATHS = (
%(headersearchpath)s
				);
				LIBRARY_SEARCH_PATHS = (
					"$(inherited)",
					"\\"$(SRCROOT)/build/Debug-iphonesimulator\\"",
%(librarysearchpath)s					
				);				
				OTHER_CFLAGS = (
%(gccflags)s					
				);
				OTHER_LDFLAGS = (
%(ldflags)s
				);
			};
			name = Distribution;
		};\n""",
}

SOLUTION_TEMPLATES = {
	"Debug" :
		"""\t\t%(configuuid)s /* SolutionTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ARCHS = "$(ARCHS_STANDARD_32_BIT)";
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";
				GCC_C_LANGUAGE_STANDARD = c99;
				GCC_WARN_ABOUT_RETURN_TYPE = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				GCC_VERSION = 4.2;
				ONLY_ACTIVE_ARCH = YES;
				PREBINDING = NO;
				SDKROOT = iphoneos3.2;
			};
			name = Debug;
		};\n""",
	"Release" :
		"""\t\t%(configuuid)s /* SolutionTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ARCHS = "$(ARCHS_STANDARD_32_BIT)";
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";
				GCC_C_LANGUAGE_STANDARD = c99;
				GCC_WARN_ABOUT_RETURN_TYPE = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				GCC_VERSION = 4.2;
				ONLY_ACTIVE_ARCH = YES;
				PREBINDING = NO;
				SDKROOT = iphoneos3.2;
			};
			name = Release;
		};\n""",
	"Profile" :
		"""\t\t%(configuuid)s /* SolutionTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ARCHS = "$(ARCHS_STANDARD_32_BIT)";
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Developer";
				GCC_C_LANGUAGE_STANDARD = c99;
				GCC_WARN_ABOUT_RETURN_TYPE = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				GCC_VERSION = 4.2;
				ONLY_ACTIVE_ARCH = YES;
				PREBINDING = NO;
				SDKROOT = iphoneos3.2;
			};
			name = Profile;
		};\n""",
	"Final" :
		"""\t\t%(configuuid)s /* SolutionTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ARCHS = "$(ARCHS_STANDARD_32_BIT)";
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Distribution";
				GCC_C_LANGUAGE_STANDARD = c99;
				GCC_WARN_ABOUT_RETURN_TYPE = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				GCC_VERSION = 4.2;
				ONLY_ACTIVE_ARCH = NO;
				PREBINDING = NO;
				SDKROOT = iphoneos3.2;
			};
			name = Final;
		};\n""",
	"Distribution" :
		"""\t\t%(configuuid)s /* SolutionTarget %(configname)s */ = {
			isa = XCBuildConfiguration;
			buildSettings = {
				ALWAYS_SEARCH_USER_PATHS = NO;
				ARCHS = "$(ARCHS_STANDARD_32_BIT)";
				"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Distribution";
				GCC_C_LANGUAGE_STANDARD = c99;
				GCC_WARN_ABOUT_RETURN_TYPE = YES;
				GCC_WARN_UNUSED_VARIABLE = YES;
				GCC_VERSION = 4.2;
				ONLY_ACTIVE_ARCH = NO;
				PREBINDING = NO;
				SDKROOT = iphoneos3.2;
			};
			name = Distribution;
		};\n""",
}

def getNewUUID(prefix = '00'):
	"""
		Returns a file unique identifier that xcode can use.
	"""
	global COUNTER
	COUNTER = COUNTER + 1
	return '%s%022X' % (prefix, COUNTER)

def readTemplate(generalDict):
	dir = Engine.getTemplatesDir(generalDict)
	filename = os.path.join(dir, XCODE_TEMPLATE )
	template = file(filename).read()
	return template

def getHeaderSearchPath(project, baseDir):
	includes = project.projectDict['includepaths']
	item = ''
	for include in string.split(includes, ';'):
		if len( include.strip() ) == 0:
			continue
		relinclude = PathHelp.relative(baseDir, include).replace('\\', '/')
		item += '\t\t\t\t\t"\\"$(SRCROOT)/%s\\"",\n' % relinclude
		#print "found include %s -> %s"  %(include, relinclude)
		
	return item

def getLibrarySearchPath(project, baseDir):
	libpaths = project.projectDict['librarypaths']
	item = ''
	for libpath in string.split(libpaths, ';'):
		if len( libpath.strip() ) == 0:
			continue
		rellibpath = PathHelp.relative(baseDir, libpath).replace('\\', '/')
		item += '\t\t\t\t\t"\\"$(SRCROOT)/%s\\"",\n' % rellibpath
		
	return item

def getDefines(project):
	defines = project.projectDict['defines']
	item = ''
	for define in string.split(defines, ';'):
		if len( define.strip() ) == 0:
			continue
		item += '\t\t\t\t\t"%s",\n' % define
	return item

def getGccflags(project):
	try:
		gccflags = project.projectDict['gccflags']
		item = ''
		for flag in string.split(gccflags, ' '):
			if len( flag.strip() ) == 0:
				continue
			item += '\t\t\t\t\t"%s",\n' % flag
		return item
	except KeyError:
		return ''
		
def getLdFlags(project):
	try:
		ldflags = project.projectDict['ldflags']
		item = ''
		for flag in string.split(ldflags, ' '):
			if len( flag.strip() ) == 0:
				continue
			item += '\t\t\t\t\t"%s",\n' % flag
		return item
	except KeyError:
		return ''

def generateXcodeProject(baseDir, template, projects):
	"""
		This is the big function that generates the main template.
	"""
	result = template
	
	# This contains a list of uppercase sections with a corresponding string.
	SECTIONS = {
		'PBXNATIVETARGET'			: '',	# The main section, this references the others
		'PBXSOURCESBUILDPHASE'		: '',	# Here are all the .cpp source files
		'PBXRESOURCESBUILDPHASE'	: '',	# This contains the resources
		'PBXHEADERSBUILDPHASE'		: '',	# Holds all the headers
		'PBXCOPYFILESBUILDPHASE'	: '',	# Holds all the copyfile statments for all the projects
		'XCCONFIGURATIONLIST'		: '',	# The configuration list.
		'XCBUILDCONFIGURATION'		: '',
		'PBXSOURCESBUILDPHASE'		: '', 
		'PBXRESOURCESBUILDPHASE'	: '',
		'PBXFRAMEWORKSBUILDPHASE'	: '',
	} 
	
	# Handle the first project as the special projects since it's going to be the main app (game app)
	for project in projects[:1]:
		projectuuid = project.uuid
		projectname = project.name
		projectrefuuid = project.refuuid
		configlistuuid = project.configlistuuid
		
		copyfilesuuid = project.copyfilesuuid
		resourcesuuid = project.resourcesuuid
		sourcesuuid = project.sourcesuuid
		frameworksuuid = project.frameworksuuid
		
		
		item = """\t\t%(projectuuid)s /* %(projectname)s */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = %(configlistuuid)s;
			buildPhases = (
				%(resourcesuuid)s /* Resources */,
				%(copyfilesuuid)s /* CopyFiles */,
				%(sourcesuuid)s /* Sources */,
				%(frameworksuuid)s /* Frameworks */,
			);
			buildRules = (
			);
			dependencies = (
{{{DEPENDENCIES_LIST}}}
			);
			name = %(projectname)s;
			productName = %(projectname)s;
			productReference = %(projectrefuuid)s /* %(projectname)s.app */;
			productType = "com.apple.product-type.application";
		};\n""" % locals()
		
		SECTIONS['PBXNATIVETARGET'] += item
	
	# Now we can go through the other projects and do them in order
	# Let's just assume they are all static libraries.
	for project in projects[1:]:
		projectuuid = project.uuid
		projectname = project.name
		projectrefuuid = project.refuuid
		configlistuuid = project.configlistuuid
		
		resourcesuuid = project.resourcesuuid
		sourcesuuid = project.sourcesuuid
		frameworksuuid = project.frameworksuuid
		
		item = """\t\t%(projectuuid)s /* %(projectname)s */ = {
			isa = PBXNativeTarget;
			buildConfigurationList = %(configlistuuid)s;
			buildPhases = (
				%(resourcesuuid)s /* Resources */,
				%(sourcesuuid)s /* Sources */,
				%(frameworksuuid)s /* Frameworks */,
			);
			buildRules = (
			);
			dependencies = (
			);
			name = %(projectname)s;
			productName = %(projectname)s;
			productReference = %(projectrefuuid)s /* lib%(projectname)s.a */;
			productType = "com.apple.product-type.library.static";
		};\n""" % locals()		
		
		SECTIONS['PBXNATIVETARGET'] += item
	
	#
	# Generate the configuration references.
	#
	uuidlist = []
	for project in projects:
		configlistuuid = project.configlistuuid
		projectname = project.name
		defaultname = CONFIGURATION_TEMPLATES.keys()[0]
		configlist = ''
		for configname in CONFIGURATION_TEMPLATES.keys():
			uuid = getNewUUID('1A')
			uuidlist.append((configname, uuid, project))
			configlist += '\t\t\t\t%s /* %16s */,\n' % (uuid, configname)
		
		item = """\t\t%(configlistuuid)s /* Build configuration list for PBXNativeTarget "%(projectname)s" */ = {
			isa = XCConfigurationList;
			buildConfigurations = (
%(configlist)s
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = %(defaultname)s;
		};\n""" % locals()
			
		SECTIONS['XCCONFIGURATIONLIST'] += item
		
	#
	# The main project seems to have it's own list of configurations...
	#
	if 1:
		mainProjectConfigListUUID = getNewUUID()
		result = result.replace('{{{MAINCONFIGLISTUUID}}}', mainProjectConfigListUUID)
		projectname = projects[0].name
		defaultname = SOLUTION_TEMPLATES.keys()[0]		
		configlist = ''
		solutionuuidlist = []
		for configname in SOLUTION_TEMPLATES.keys():
			uuid = getNewUUID('1A')
			solutionuuidlist.append((configname, uuid, projects[0]))
			configlist += '\t\t\t\t%s /* %16s */,\n' % (uuid, configname)
		
		item = """\t\t%(mainProjectConfigListUUID)s /* Build configuration list for PBXProject "%(projectname)s"  (main solution one)*/ = {
			isa = XCConfigurationList;
			buildConfigurations = (
%(configlist)s
			);
			defaultConfigurationIsVisible = 0;
			defaultConfigurationName = %(defaultname)s;
		};\n""" % locals()
			
		SECTIONS['XCCONFIGURATIONLIST'] += item
		
		for configname, configuuid, project in solutionuuidlist:
			configtemplate = SOLUTION_TEMPLATES[configname]
			productname = project.name
			item = configtemplate % locals()
			SECTIONS['XCBUILDCONFIGURATION'] += item

	for configname, configuuid, project in uuidlist:
		configtemplate = CONFIGURATION_TEMPLATES[configname]
		productname = project.name
		username = os.environ['USERNAME']
		headersearchpath = getHeaderSearchPath(project, baseDir)
		librarysearchpath = getLibrarySearchPath(project, baseDir)
		defines = getDefines(project)
		gccflags = getGccflags(project)
		ldflags = getLdFlags(project)
		
		item = configtemplate % locals()
		
		SECTIONS['XCBUILDCONFIGURATION'] += item
	
	#
	# Create the section with files
	#
	PBXBuildFile = ''
	for project in projects:
		for file in project.sourceFiles:
			line = '\t\t%s /* %-48s */ = {isa = PBXBuildFile; fileRef = %s; };\n' % (file.uuid, file.contextname + '/' + file.name, file.refuuid)
			PBXBuildFile += line
	for project in projects[1:]:
		line = '\t\t%s /* %-48s */ = {isa = PBXBuildFile; fileRef = %s /* lib%s.a */; };\n' % (project.libuuid, 'lib' + project.name + '.a', project.refuuid, project.name)
		PBXBuildFile += line
	result = result.replace('{{{PBXBUILDFILE}}}', PBXBuildFile)
	
	#
	# Create the proxy section
	#
	PBXContainerItemProxy = ''
	for project in projects[1:]:
		section = """		%s /* PBXContainerItemProxy */ = {
			isa = PBXContainerItemProxy;
			containerPortal = %s /* Project object (%s)*/;
			proxyType = 1;
			remoteGlobalIDString = %s;
			remoteInfo = %s;
		};\n""" % (project.proxyuuid, '000000000000000000000001', projects[0].name, project.uuid, project.name)
		
		PBXContainerItemProxy += section
	result = result.replace('{{{PBXCONTAINERITEMPROXY}}}', PBXContainerItemProxy)
	
	#
	# Create the section with the references
	#
	PBXFileReference = ''
	for project in projects:
		for file in project.sourceFiles:
			relpath = PathHelp.relative(baseDir, file.fullpath).replace('\\', '/')
			try:
				filetype = FILETYPES[file.ext.lower()]
			except KeyError:
				filetype = 'text'
			
			if filetype == 'wrapper.framework':
				frameworkpath = FRAMEWORKPATHS[file.name.lower()]
				line ='\t\t%s /* %-48s */ = {isa = PBXFileReference; lastKnownFileType = %-24s name = %-32s path = %-48s sourceTree = SDKROOT; };\n' % (file.refuuid, file.name, filetype + ';', file.name + ';', frameworkpath + ';')
			else:
				line ='\t\t%s /* %-48s */ = {isa = PBXFileReference; fileEncoding = 4; lastKnownFileType = %-24s name = %-32s path = %-48s sourceTree = SOURCE_ROOT; };\n' % (file.refuuid, file.contextname + '/' + file.name, filetype + ';', file.name + ';', relpath + ';')
			PBXFileReference += line
	for project in projects[:1]:
		# We need to treat the first project as the application specially.
		line = '\t\t%s /* %-48s */ = {isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = %s.app; sourceTree = BUILT_PRODUCTS_DIR; };\n' % (project.refuuid, project.name + '.app', project.name)
		PBXFileReference += line
		
	for project in projects[1:]:
		# We also need to create a reference for the static library coming out of all the other projects. We
		# Kind of assume here that the dependencies are all static libraries...
		line = '\t\t%s /* %-48s */ = {isa = PBXFileReference; explicitFileType = archive.ar; includeInIndex = 0; path = lib%s.a; sourceTree = BUILT_PRODUCTS_DIR; };\n' % (project.refuuid, 'lib' + project.name + '.a', project.name)
		PBXFileReference += line
	result = result.replace('{{{PBXFILEREFERENCE}}}', PBXFileReference)
	
	#
	# We need to list the different libraries as "Products".
	#
	Group_Products = ''
	for project in projects[:1]:
		line = '\t\t\t\t%s /* %s.app */,\n' % (project.refuuid, project.name)
		Group_Products += line;
	for project in projects[1:]:
		line = '\t\t\t\t%s /* lib%s.a */,\n' % (project.refuuid, project.name)
		Group_Products += line;
	result = result.replace('{{{GROUP_PRODUCTS}}}', Group_Products)
	
	#
	# TODO: Understand this?
	#
	Group_List = ''
	for project in projects:
		line = '\t\t\t\t%s /* %s */,\n' % (project.groupuuid, project.name)
		Group_List += line
	result = result.replace('{{{GROUP_LIST}}}', Group_List)
	
	#
	# Write down the groups for all the sources.
	#
	PBXGroup_Items = ''
	for project in projects:
		
		item = '\t\t%s /* %s */ = {\n\t\t\tisa = PBXGroup;\n\t\t\tchildren = (\n' % (project.groupuuid, project.name)
		
		for file in project.sourceFiles:
			
			if file.ext not in SOURCE_EXTS + HEADER_EXTS:
				continue
			item += '\t\t\t\t%s /* %s */,\n' % (file.refuuid, file.name)
		
		
		reldir = project.relativeDir(baseDir).replace('\\', '/')
		if len(reldir) == 0:
			reldir = '.'
		
		item += """\t\t\t);
			name = %s;
			sourceTree = "<group>";
		};\n""" % (project.name)
		
		PBXGroup_Items += item
	result = result.replace('{{{PBXGROUP_ITEMS}}}', PBXGroup_Items)
	
	# 
	# Write down the group for all the resources
	#
	item = ''
	for project in projects:
		for file in project.sourceFiles:
			if file.ext not in RESOURCE_EXTS:
				if 'resource' not in file.options.keys():
					continue
			item += '\t\t\t\t\t%s /* %s */,\n' % (file.refuuid, file.name)
	result = result.replace( '{{{GROUP_RESOURCES}}}', item )
	
	#
	# Write down the group for all the frameworks.
	#
	item = ''
	builditem = ''
	for i, project in enumerate(projects):
		builditem += """\t\t%s /* Frameworks */ = {
			isa = PBXFrameworksBuildPhase;
			buildActionMask = 2147483647;
			files = (\n""" % (project.frameworksuuid)
		
		for file in project.sourceFiles:
			if file.ext not in ['.framework']:
				continue
			item += '\t\t\t\t\t%s /* %s */,\n' % (file.refuuid, file.name)
			builditem += '\t\t\t\t%s /* %s */,\n' % (file.uuid, file.name)
		
		if i == 0:
			for project in projects[1:]:
				builditem += '\t\t\t\t%s /* lib%s.a */,\n' % (project.libuuid, project.name)
		
		builditem += """\t\t\t);
			runOnlyForDeploymentPostprocessing = 0;
		};\n"""
	result = result.replace( '{{{GROUP_FRAMEWORKS}}}', item )
	result = result.replace( '{{{PBXFRAMEWORKSBUILDPHASE}}}', builditem )
	
	# write down all the UUID for all the projects.
	PROJECTS_UUID_LIST = ''
	for project in projects:
		PROJECTS_UUID_LIST += '\t\t\t\t%s /* %s */,\n' % (project.uuid, project.name)
	result = result.replace('{{{PROJECTS_UUID_LIST}}}', PROJECTS_UUID_LIST)
	#
	# Write down the main project's UUID
	#
	result = result.replace('{{{MAIN_PROJECT_UUID}}}', projects[0].uuid)
	
	#
	# Write down the dependencies to target translation table
	#
	DEPENDENCIES_TABLE = ''
	for project in projects[1:]:
		DEPENDENCIES_TABLE += """\t\t%s /* PBXTargetDependency */ = {
			isa = PBXTargetDependency;
			target = %s /* %s */;
			targetProxy = %s /* PBXContainerItemProxy */;
		};\n""" % (project.depuuid, project.uuid, project.name, project.proxyuuid)
	result = result.replace('{{{DEPENDENCIES_TABLE}}}', DEPENDENCIES_TABLE)
	
	
	# Write down all the sources to build
	for project in projects:
		filelist = ''
		for file in project.sourceFiles:
			if file.ext in SOURCE_EXTS:
				filelist += '\t\t\t%s /* %s in %s*/,\n' % (file.uuid, file.name, project.name)
		
		sectionuuid = project.sourcesuuid

		item = """\t\t%(sectionuuid)s /* Sources */ = {
			isa = PBXSourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
%(filelist)s			
			);
			runOnlyForDeploymentPostprocessing = 0;
		};\n""" % locals()
		
		SECTIONS['PBXSOURCESBUILDPHASE'] += item
		
	# Write down all the headers to build
	for project in projects:
		filelist = ''
		for file in project.sourceFiles:
			if file.ext in HEADER_EXTS:
				filelist += '\t\t\t%s /* %s in %s*/,\n' % (file.uuid, file.name, project.name)
		
		sectionuuid = project.headersuuid

		item = """\t\t%(sectionuuid)s /* Headers */ = {
			isa = PBXHeadersBuildPhase;
			buildActionMask = 2147483647;
			files = (
%(filelist)s			
			);
			runOnlyForDeploymentPostprocessing = 0;
		};\n""" % locals()
		
		SECTIONS['PBXHEADERSBUILDPHASE'] += item
	
	# Write down all the resources to build
	for project in projects:
		filelist = ''
		for file in project.sourceFiles:
			if file.ext in RESOURCE_EXTS:
				filelist += '\t\t\t%s /* %s in %s*/,\n' % (file.uuid, file.name, project.name)
		
		sectionuuid = project.resourcesuuid

		item = """\t\t%(sectionuuid)s /* Resources */ = {
			isa = PBXResourcesBuildPhase;
			buildActionMask = 2147483647;
			files = (
%(filelist)s			
			);
			runOnlyForDeploymentPostprocessing = 0;
		};\n""" % locals()
		
		SECTIONS['PBXRESOURCESBUILDPHASE'] += item
	
	# Write down all the files to copy
	
	# Go through the main dictionary and replace the entries as we've produced them.
	for k,v in SECTIONS.iteritems():
		result = result.replace('{{{%s}}}' % k, v)
	
	
	#
	# Write down the dependencies, need to do this after almost all the other references have resolved
	#
	DEPENDENCIES_LIST = ''
	for project in projects[1:]:
		DEPENDENCIES_LIST += '\t\t\t\t%s /* PBXTargetDependency %s */,\n' % (project.depuuid, project.name)
	result = result.replace('{{{DEPENDENCIES_LIST}}}', DEPENDENCIES_LIST)
	
	return result

class Project:
	""" Describes one single project. Very much modeled upon the visual studio behaviour, but the concepts should be portable to other environments """
	def __init__(self, configFileName):
		logging.debug( 'Loading project %s' % configFileName )
		self.configFileName = configFileName
		self.generalDict, self.projectDict, self.solutionDict = Engine.readConfiguration(configFileName)
		self.platformName = self.generalDict['platform']
		self.sourceFiles = FileItem.readSourceFiles( os.path.dirname(configFileName), self.generalDict['sourcefiles'] )
		self.uuid = ''
		self.refuuid = ''
		self.proxyuuid = ''
		self.groupuuid = ''
		self.depuuid = ''
		logging.debug('Constructed project %s' % configFileName)
		

	def __repr__(self):
		includes = self.projectDict['includepaths']
		defines = self.projectDict['defines']
		files = ','.join([str(x) for x in self.sourceFiles])
		return 'includes = %(includes)s | defines = %(defines)s | files = %(files)s' % locals()

	def __load(configFileName):
		logging.debug( 'Loading project from %s' % configFileName )
		project = Project(configFileName)
		project.uuid = getNewUUID('0A')
		project.refuuid = getNewUUID('0B')
		project.proxyuuid = getNewUUID('0C')
		project.groupuuid = getNewUUID('0D')
		project.depuuid = getNewUUID('0E')
		project.configlistuuid = getNewUUID('0F')
		project.copyfilesuuid = getNewUUID('2A')
		project.resourcesuuid = getNewUUID('2B')
		project.sourcesuuid = getNewUUID('2C')
		project.frameworksuuid = getNewUUID('2D')
		project.headersuuid = getNewUUID('2E')
		project.libuuid = getNewUUID('3E')
		
		for x in project.sourceFiles:
			x.uuid = getNewUUID('0A')
			x.refuuid = getNewUUID('0B')
		return project
	
	def __name(self):
		return self.projectDict['name']
	def relativeDir(self, basePath):
		configDir = os.path.dirname(self.configFileName)
		return PathHelp.relative(basePath, configDir)

	name = property(__name)
	load = staticmethod(__load)

def generateSearchName(name):
	return name + '.bdgcfg'

def processSingleSolution(configFileName):
	try:
		# Load the overall configuration from the .tcfg file.
		generalDict, projectDict, solutionDict = Engine.readConfiguration(configFileName)
		if len(solutionDict) == 0:
			logging.debug('No solution section found, bailing out of solution generation (offending file %s)' % configFileName)
			return 1

		logging.debug( 'Loaded %s' % configFileName )
		
		basePath = os.path.dirname(configFileName)
		platformName = generalDict['platform']
		projectName = generalDict['name']
		
		if 'iphone' != platformName.lower():
			logging.debug( 'Ignoring non-iphone xcode generation' )
			return 0
		
		# Determine the output product path.
		
		# Make sure that we know where to write the data...
		targetFileName = os.path.join(os.path.dirname(configFileName), '%s.xcodeproj' % projectName, 'project.pbxproj')
		if not os.path.isdir(os.path.dirname(targetFileName)):
			os.mkdir(os.path.dirname(targetFileName))
		
		logging.debug( '---------------------------------------------------------------------' )
		logging.debug( 'Search path: %s' % solutionDict['dependenciespaths'] )
		logging.debug( '---------------------------------------------------------------------' )

		dependencies = Engine.findDependencies( basePath, solutionDict['dependencies'], solutionDict['dependenciespaths'], generalDict['platform'], generateSearchName )
		logging.debug( '---------------------------------------------------------------------' )
		dependencies = [configFileName] + dependencies
		logging.debug( 'Deps:\n%s' % '\n'.join(dependencies) )
		projects = map(Project.load, dependencies)
		logging.debug( '---------------------------------------------------------------------' )
		
		template = readTemplate(generalDict)
		
		template = generateXcodeProject(basePath, template, projects)
		
		#print template 
		
		fixupRules = {}
		
		# Do the final global fixup on the main project's dictionary.
		xcodefile = Engine.replaceKeywords(basePath, template, projectDict, fixupRules)		

		# All is now done, try to write the target file to disk...
		logging.info( 'Writing %s' % targetFileName )
		Engine.writeConfigFile( targetFileName, xcodefile )
	except SyntaxError, e:
		logging.error( str(e) )
		return 1
	return 0

def main(argv):
	"""
Usage: GenerateXcode <config name>	
	"""
	
	try:
		opts, args = getopt.getopt( argv, 'vh' )
	except getopt.GetoptError:
		print main.__doc__
		return 1
	
	if len(args) != 1:
		print main.__doc__
		return 1
	
	verbose = 1
	for o,a in opts:
		if '-v' == o:
			verbose = 1
		if '-h' == o:
			print main.__doc__
			return 1	
	
	if verbose:
		logging.basicConfig( level = logging.DEBUG, format = '%(levelname)s %(message)s' )
	else:
		logging.basicConfig( level = logging.INFO, format = '%(levelname)s %(message)s' )
	
	mainConfigFileName = os.path.abspath(args[0])
	return processSingleSolution(mainConfigFileName)

if __name__ == '__main__':
	sys.exit( main( sys.argv[1:] ) )
