# import cProfile
# import pstats
# from CAT.wsgi import application
# from django.core.management import execute_from_command_line
# import sys
#
# if __name__ == "__main__":
#     profiler = cProfile.Profile()
#     profiler.enable()
#
#     execute_from_command_line(sys.argv)
#
#     profiler.disable()
#     stats = pstats.Stats(profiler).sort_stats("cumtime")
#     stats.dump_stats("profile_result.prof")
