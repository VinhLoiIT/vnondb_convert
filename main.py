import lib

import os
import sys
import argparse
import concurrent.futures

def make_annotations_worker(args):
    inkml_file, output_dir, line_width, dpi = args
    lib.make_annotations(inkml_file, output_dir, line_width, dpi)

def create_dir_if_not_exist(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
        print(f'Created {dir_path}')

def get_list_files_from_file(input_file):
    print(f'Get list files from {input_file}')
    with open(input_file) as f:
        lines = f.readlines()
    return [line.rstrip() for line in lines]  # remove '\n'

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('inkml_dir', type=str)
    parser.add_argument('output_dir', type=str)
    parser.add_argument('-s', '--split_dir_path', type=str,
                        default='VNOnDB_ICFHR2018_dataSplit')
    parser.add_argument('--line_width', type=float, default=2.)
    parser.add_argument('--dpi', type=int, default=300)

    args = parser.parse_args()

    if not os.path.exists(args.inkml_dir):
        print('{} not found'.format(args.inkml_dir))
        exit()

    train_dir = args.output_dir + '_train'
    val_dir = args.output_dir + '_val'
    test_dir = args.output_dir + '_test'

    create_dir_if_not_exist(train_dir)
    create_dir_if_not_exist(val_dir)
    create_dir_if_not_exist(test_dir)

    train_files = get_list_files_from_file(
        os.path.join(args.split_dir_path, 'train_set.txt'))
    val_files = get_list_files_from_file(
        os.path.join(args.split_dir_path, 'validation_set.txt'))
    test_files = get_list_files_from_file(
        os.path.join(args.split_dir_path, 'test_set.txt'))

    train_files = [os.path.join(args.inkml_dir, file) for file in train_files]
    val_files = [os.path.join(args.inkml_dir, file) for file in val_files]
    test_files = [os.path.join(args.inkml_dir, file) for file in test_files]

    with concurrent.futures.ProcessPoolExecutor() as executor:
        total = len(train_files) + len(val_files) + len(test_files)
        convert_files = train_files + val_files + test_files
        output_dirs = [train_dir]*len(train_files) + [val_dir]*len(val_files) + [test_dir]*len(test_files)
        line_width = [args.line_width] * total
        dpi = [args.dpi] * total

        assert len(convert_files) == len(output_dirs) == len(line_width) == len(dpi) == total
        convert_info = zip(convert_files, output_dirs, line_width, dpi)

        print('Start converting')
        count = 0
        for _ in executor.map(make_annotations_worker, convert_info):
            count = count + 1
            print(f'Converted {count}/{total}')
    print('Done!')
