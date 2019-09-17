import lib

import os
import glob
import sys
import argparse
import concurrent.futures

def make_annotations_worker(args):
    inkml_file, output_dir, line_width, dpi = args
    lib.make_annotations(inkml_file, output_dir, line_width, dpi)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inkml_dir', type=str)
    parser.add_argument('output_dir', type=str)
    parser.add_argument('--line_width', type=float, default=2)
    parser.add_argument('--dpi', type=int, default=300)

    args = parser.parse_args()

    if not os.path.exists(args.inkml_dir):
        print('{} not found'.format(args.inkml_dir))
        exit()

    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    with concurrent.futures.ProcessPoolExecutor() as executor:
        files = glob.glob(args.inkml_dir+'/*')
        total = len(files)
        l = list(zip(
            files, 
            [args.output_dir] * total,
            [args.line_width] * total,
            [args.dpi] * total))
        
        count = 0
        for inkfile, imagefile in zip(files, executor.map(make_annotations_worker, l)):
            count = count + 1
            print(f'Process: {count/total}')
    print('Done!')