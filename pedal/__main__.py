## utilities ##
import argparse
from genericpath import isfile
import sys
import os
from . import utils_loading, utils_fx, dashboard

class MyParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

def main():
    """ Main Function reads a gpx, converts, and calculates basic features"""
    
    parser = MyParser()
    parser.add_argument(
        '-input',
        nargs='+',
        type = str,
        help='input gpx filename or folder',
        default=os.getcwd(),
    )
    parser.add_argument(
    '-output_path',
    nargs='+',
    type=str,
    help='output folder',
    default=os.getcwd(),
    )

    args = parser.parse_args()
    args.input = args.input[0]
    args.output_path = args.output_path
    if os.path.isdir(args.input):
        print("Begin Batch Conversion For Folder: %s \n to output path", args.input[0], args.output_path)
        utils_loading.batch_convert(input_path=args.input, output_format='csv', output_path=args.output_path)
        #launch dash app in browser
        dashboard.run_server()

    elif os.path.isfile(args.input):
        print("Begin Conversion For File: \n to output path", args.input, args.output_path)
        utils_loading.gpx_to_csv(input_path=os.getcwd(), activity_name=args.input, output_path=args.output_path)
        #launch dash app in browser
        dashboard.run_server()

if __name__ == '__main__':
    main()
