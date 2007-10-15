import hotshot
import GenerateAll
import hotshot.stats

PROFILEFILE = "GenerateAll.profile"

#profiler = hotshot.Profile( PROFILEFILE, lineevents=0 )
#command = '''GenerateAll.main([])'''
#profiler.runctx( command, globals(), locals())
#profiler.close()
stats = hotshot.stats.load(PROFILEFILE)
stats.strip_dirs()
stats.sort_stats('time', 'calls')
stats.print_stats(40)
