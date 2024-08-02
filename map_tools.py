import os
import argparse
import pprint
import math
#from statistics import median

import kml
import tools
import gpx
import optimize


pp = pprint.PrettyPrinter(indent= 4)


def _get_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='subcommands',
                                   description='valid subcommands',
                                   help='additional help')

    parser_combine_files = subparsers.add_parser('combine-files', 
            help='combine lines from mult files into one or more lines in one file')
    parser_combine_files.add_argument("--verbose", '-v',  action ='store_true')  
    parser_combine_files.set_defaults(func=combine_files)
    parser_combine_files.add_argument("paths", nargs='+', help="path of file")
    parser_combine_files.add_argument("--out", '-o',  required = True, help="out-path")

    parser_convert_gpx = subparsers.add_parser('convert-to-gpx', help='convert to gpx')
    parser_convert_gpx.set_defaults(func=convert_to_gpx)
    parser_convert_gpx.add_argument("path", help="path of file")
    parser_convert_gpx.add_argument("--verbose", '-v',  action ='store_true')  
    parser_convert_gpx.add_argument("--out", "-o", required = False,  
            help="out path of file")

    parser_create_mile_markers = subparsers.add_parser(
            'mile-markers', help='create mile markers')
    parser_create_mile_markers.add_argument("--verbose", '-v',  action ='store_true')  
    parser_create_mile_markers.set_defaults(func=create_mile_markers)
    parser_create_mile_markers.add_argument("path", help="path of file")
    parser_create_mile_markers.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    parser_create_mile_markers.add_argument("--reverse", '-r',  
            action ='store_true', help = 'route is up and back, so double points')  

    parser_prune_by_mark = subparsers.add_parser(
            'prune-by-location', help='prune by location')
    parser_prune_by_mark.add_argument("--verbose", '-v',  action ='store_true')  
    parser_prune_by_mark.add_argument("path", help="path of file")
    parser_prune_by_mark.add_argument("--start", '-s',  type = str, help = 'start location')  
    parser_prune_by_mark.add_argument("--end", '-e',  type = str, help = 'end location')  
    parser_prune_by_mark.set_defaults(func=prune_by_location)
    parser_prune_by_mark.add_argument("--out", '-o',  required = True,  
            help="out path of file")

    parser_mult_files_one_line = subparsers.add_parser(
            'mult-lines-to-one', 
            help='use multpile files to create one line')
    parser_mult_files_one_line.add_argument("paths", nargs='+', help="path of file")
    parser_mult_files_one_line.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    parser_mult_files_one_line.add_argument("--verbose", '-v',  action ='store_true')  
    parser_mult_files_one_line.set_defaults(func=mult_lines_to_one)

    parser_prune_to_top = subparsers.add_parser(
            'prune-to-top', help='prune just the first half of hike')
    parser_prune_to_top.add_argument("--verbose", '-v',  action ='store_true')  
    parser_prune_to_top.add_argument("path", help="path of file")
    parser_prune_to_top.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    parser_prune_to_top.set_defaults(func=prune_to_top)

    parser_polygon_from_files = subparsers.add_parser(
            'polygon-from-files', 
            help='use multpile files to create one polygon')
    parser_polygon_from_files.add_argument("paths", nargs='+', help="path of file")
    parser_polygon_from_files.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    parser_polygon_from_files.add_argument("--verbose", '-v',  action ='store_true')  
    parser_polygon_from_files.set_defaults(func=polygon_from_files)

    parser_smooth = subparsers.add_parser(
            'smooth', 
            help='smooth')
    parser_smooth.add_argument("--verbose", '-v',  action ='store_true')  
    parser_smooth.add_argument("path", help="path of file")
    parser_smooth.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    parser_smooth.set_defaults(func=smooth_func)

    optimize = subparsers.add_parser(
            'optimize', 
            help='optimize')
    optimize.add_argument("--verbose", '-v',  action ='store_true')  
    optimize.add_argument("path", help="path of file")
    optimize.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    optimize.set_defaults(func=optimize_func)

    optimize = subparsers.add_parser(
            'csv', 
            help='make csv file')
    optimize.add_argument("--verbose", '-v',  action ='store_true')  
    optimize.add_argument("path", help="path of file")
    optimize.add_argument("--out", '-o',  required = True,  
            help="out path of file")
    optimize.set_defaults(func=csv_func)
    

    args = parser.parse_args()
    args.func(args)

    return args

def main():
    args = _get_args()

def combine_files(args):
    tools.combine_lines_to_one_file(
            paths = args.paths,
            out = args.out,
            verbose = args.verbose
            )

def combine(args):
    in_path = args.path
    root = combine_lines(root_or_path = in_path)
    write_to_path(root = root, path = _make_out_path(in_path))

def convert_to_gpx(args):
    tools.convert_to_gpx(path = args.path, 
            verbose = args.verbose,
            out = args.out)

def create_mile_markers(args):
    tools.mile_markers(
            path = args.path,
            out = args.out,
            reverse = args.reverse,
            verbose = args.verbose)

def prune_by_location(args):
    tools.location_prune(path = args.path,
            verbose = args.verbose,
            out = args.out,
            start = tools.convert_string_to_points(args.start),
            end = tools.convert_string_to_points(args.end)
            )

def mult_lines_to_one(args):
    tools.mult_lines_to_one(
            paths = args.paths,
            out = args.out,
            verbose = args.verbose
            )

def prune_to_top(args):
    tools.prune_to_top(
            path = args.path,
            out = args.out,
            verbose = args.verbose
            )

def polygon_from_files(args):
    tools.polygon_from_files(
            paths = args.paths,
            out = args.out,
            verbose = args.verbose
            )

def smooth_func(args):
    tools.smooth_func(
            path = args.path,
            out = args.out,
            verbose = args.verbose)

def optimize_func(args):
    tools.optimize_func(
            path = args.path,
            out = args.out,
            verbose = args.verbose)

def csv_func(args):
    tools.csv_func(
            path = args.path,
            out = args.out,
            verbose = args.verbose)



if __name__== '__main__':
    main()
