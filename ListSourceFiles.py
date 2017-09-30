#!/usr/bin/python
#
# Steps through a .sln file or a .vcproj file and lists all the files referenced relative the current path. Output is suitable for piping directly to a SourceFiles format.
#
# (C) 2007 Jim Tilander
import logging
import os
import sys
import string
import re
import PathHelp

VERBOSE = False
HELP = 'Usage: %s <.sln|.vcproj file>' % sys.argv[0]

def findFilesFromProject( filename ):
    from xml.dom.minidom import parse
    dom = parse(filename)
    nodes = dom.documentElement.getElementsByTagName('File')
    base = os.path.dirname(filename)
    result = []
    for node in nodes:
        relativePath = node.getAttribute('RelativePath').encode('ascii', 'replace')
        result.append( os.path.join(base, relativePath) )
    return result

def findFilesFromSolution( filename ):
    projectPattern = re.compile( r'Project\("\{8BC9CEB8-8B4A-11D0-8D11-00A0C91BC942\}"\) = .*, "(.*)",' )
    result = []
    baseDir = os.path.dirname(filename)
    for line in open(filename).readlines():
        m = projectPattern.match(line)
        if not m:
            continue
        projectName = m.group(1)
        logging.debug( 'Found project %s' % projectName )
        fullPath = os.path.join( baseDir, projectName)
        result += findFilesFromProject(fullPath)
    return result

def findFilesFromDir( directory ):
    result = []
    for root, dirs, files in os.walk( directory ):
        for name in files:
            fullname = os.path.join(root, name)
            result.append(fullname)
    return result

def main( argv ):
    if len(argv) != 1:
        print HELP
        return 1
    
    fileName = os.path.abspath(argv[0])
    baseDir = os.path.abspath(os.getcwd())
    
    print fileName
    if os.path.isdir(fileName):
        files = findFilesFromDir(fileName)
    else:
        ext = os.path.splitext(fileName)[1]
        if '.sln' == ext:
            files = findFilesFromSolution(fileName)
        elif '.vcproj' == ext:
            files = findFilesFromProject(fileName)
        else:
            print 'Unknown file type ' + ext
            return 1
    
    files.sort()
    for name in files:
        relative = PathHelp.relative( baseDir, name )
        print '\t' + relative.replace(os.sep, '/')
    return 0

if __name__ == '__main__':
    if VERBOSE:
        logging.basicConfig( level = logging.DEBUG, format = '%(levelname)s %(message)s' )
    else:
        logging.basicConfig( level = logging.ERROR, format = '%(levelname)s %(message)s' )
    sys.exit( main( sys.argv[1:] ) )
