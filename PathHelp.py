#!/usr/bin/python
#
# Defines some utilitiy functions for path manipulations (with tests at the bottom)
#
# (C) 2007 Jim Tilander

import os
import string

def normalize( path ):
	elements = path.replace('/', os.sep).split(os.sep)
	try:
		while 1:
			index = elements.index( '.' )
			del elements[index:index+1]
	except ValueError:
		pass
	try:
		while 1:
			index = elements.index( '..' )
			del elements[index-1:index+1]
	except ValueError:
		pass
	return string.join(elements,os.sep)

def relative( base, target ):
	base = normalize(base).split(os.sep)
	target = normalize(target).split(os.sep)
	i = 0
	for a, b in zip(base, target):
		if a.lower() != b.lower():
			break
		i += 1
	elements = ['..'] * (len(base) - i) + target[i:]
	return string.join(elements, os.sep)

if __name__ == '__main__':
	import unittest

	class TestNormalize( unittest.TestCase ):
		def testTipsTheSlashes(self):
			self.assertEqual( r'Foobar\Main.cpp', normalize(r'Foobar/Main.cpp') )
		
		def testCanPassThrough(self):
			self.assertEqual( r'Foobar\Main.cpp', normalize(r'Foobar\Main.cpp') )
	
		def testCanReduceDotDot(self):
			self.assertEqual( r'Foobar\Main.cpp', normalize(r'Foobar\Hello\..\Main.cpp') )

		def testCanReduceMultipleDotDots(self):
			self.assertEqual( r'Foobar\Main.cpp', normalize(r'Foobar\Hello\World\..\..\Main.cpp') )

		def testCanReduceDot(self):
			self.assertEqual( r'Foobar\Main.cpp', normalize(r'Foobar\.\Main.cpp') )

	class TestRelative( unittest.TestCase ):
		def testCanResolveSameDir(self):
			self.assertEqual( 'Main.cpp', relative('Foobar', r'Foobar\Main.cpp' ) )

		def testCanGiveOneRelativePath(self):
			self.assertEqual( r'..\LibraryA\Main.cpp', relative(r'Foobar\LibraryB', r'Foobar\LibraryA\Main.cpp' ) )

		def testCanStepThroughSeveralRelativePaths(self):
			self.assertEqual( r'..\..\..\LibraryA\Main.cpp', relative(r'Foobar\usr/local/LibraryB', r'Foobar\LibraryA\Main.cpp' ) )

	unittest.main()
