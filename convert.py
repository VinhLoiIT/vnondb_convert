import os
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

import pandas as pd
import argparse
from tqdm import trange, tqdm

def make_image_file(coord_groups, output_path: str, line_width=2, dpi=300):
    figure = plt.figure(dpi=dpi)
    plt.gca().set_aspect('equal', adjustable='box')
    plt.gca().invert_yaxis()
    plt.axis('off')

    for group in coord_groups:
        data = np.array(group)
        x, y = zip(*data)
        plt.plot(x, y, linewidth=line_width, c='black')
    figure.savefig(output_path, bbox_inches='tight')
    plt.close()

def convert(ink_files, out_img_dir, out_label_path, line_width=2, dpi=300):
    if not os.path.exists(out_img_dir):
        os.mkdir(out_img_dir)
        
    annotations = pd.DataFrame(columns=['id', 'label'])
    total_files = len(ink_files)
    for _, inkml_file in zip(trange(len(ink_files), desc='Progress'), ink_files):
        tree = ET.parse(inkml_file)
        root = tree.getroot()

        for sample in root.findall('traceGroup'):
            sample_id = os.path.splitext(os.path.basename(inkml_file))[0] + '_' + sample.get('id')
            sample_label = sample.find('.//Tg_Truth').text
            annotations = annotations.append({'id': sample_id, 'label': sample_label}, ignore_index=True)

            coord_groups = []
            for trace_tag in sample.findall('trace'):
                coord_group = []
                for coord_text in trace_tag.text.split(','):
                    if coord_text == '':
                        continue
                    coords = coord_text.split(' ')
                    coords = np.array([int(coord) for coord in coords if coord != ''])
                    assert len(coords) == 2
                    coord_group.append(coords)
                coord_groups.append(coord_group)
            make_image_file(coord_groups, os.path.join(out_img_dir, sample_id) + '.png', line_width, dpi)
    annotations.to_csv(out_label_path, sep='\t')


def convert_label_only(ink_files, out_label_path):
    annotations = pd.DataFrame(columns=['id', 'label'])
    total_files = len(ink_files)
    for _, inkml_file in zip(trange(len(ink_files), desc='Progress'), ink_files):
        tree = ET.parse(inkml_file)
        root = tree.getroot()

        for sample in root.findall('traceGroup'):
            sample_id = os.path.splitext(os.path.basename(inkml_file))[0] + '_' + sample.get('id')
            sample_label = sample.find('.//Tg_Truth').text
            annotations = annotations.append({'id': sample_id, 'label': sample_label}, ignore_index=True)

    annotations.to_csv(out_label_path, sep='\t')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(type=str, dest='level', choices=['word', 'line', 'paragraph'])
    parser.add_argument('-w', '--line_width', type=float, dest='line_width', default=2)
    parser.add_argument('-dpi', '--dpi', type=int, dest='dpi', default=300)
    parser.add_argument('--label_only', action='store_true', dest='label_only')

    args = parser.parse_args()

    # config path
    data_dir = './data'

    level = args.level

    inkml_dir = os.path.join(data_dir, f'InkData_{level}')
    out_label_train = os.path.join(data_dir, f'train_{level}.csv')
    out_label_validation = os.path.join(data_dir, f'validation_{level}.csv')
    out_label_test = os.path.join(data_dir, f'test_{level}.csv')
    out_label_all = os.path.join(data_dir, f'all_{level}.csv')

    icfhr_datasplit_dir = os.path.join(data_dir, 'VNOnDB_ICFHR2018_dataSplit')
    train_set = os.path.join(icfhr_datasplit_dir, 'train_set.txt')
    val_set = os.path.join(icfhr_datasplit_dir, 'validation_set.txt')
    test_set = os.path.join(icfhr_datasplit_dir, 'test_set.txt')

    with open(train_set) as f:
        train_ink_files = [os.path.join(inkml_dir, line.rstrip()) for line in f]
    with open(val_set) as f:
        val_ink_files = [os.path.join(inkml_dir, line.rstrip()) for line in f]
    with open(test_set) as f:
        test_ink_files = [os.path.join(inkml_dir, line.rstrip()) for line in f]

    print('number train_ink_files:', len(train_ink_files))
    print('number val_ink_files:', len(val_ink_files))
    print('number test_ink_files:', len(test_ink_files))

    if args.label_only:
        convert_label_only(train_ink_files, out_label_train)
        convert_label_only(val_ink_files, out_label_validation)
        convert_label_only(test_ink_files, out_label_test)
    else:
        out_img_train = os.path.join(data_dir, f'train_{level}')
        out_img_validation = os.path.join(data_dir, f'validation_{level}')
        out_img_test = os.path.join(data_dir, f'test_{level}')

        if not os.path.exists(out_img_train):
            os.mkdir(out_img_train)
        if not os.path.exists(out_img_validation):
            os.mkdir(out_img_validation)
        if not os.path.exists(out_img_test):
            os.mkdir(out_img_test)

        line_width = args.line_width
        dpi = args.dpi

        convert(train_ink_files, out_img_train, out_label_train, line_width, dpi)
        convert(val_ink_files, out_img_validation, out_label_validation, line_width, dpi)
        convert(test_ink_files, out_img_test, out_label_test, line_width, dpi)

    convert_label_only(train_ink_files+val_ink_files+test_ink_files, out_label_all)