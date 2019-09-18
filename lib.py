import os
import numpy as np
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET

class Annotation:
    def __init__(self, id: str, label: str, coord_groups: list):
        self.id = id
        self.label = label
        self.coord_groups = coord_groups

    def make_label_file(self, output_path: str):
        with open(output_path, 'w') as f:
            print(self.label, file=f)

    def make_image_file(self, output_path: str, line_width, dpi):
        figure = plt.figure(dpi=dpi)
        plt.gca().set_aspect('equal', adjustable='box')
        plt.gca().invert_yaxis()
        plt.axis('off')

        for group in self.coord_groups:
            data = np.array(group)
            x, y = zip(*data)
            plt.plot(x, y, linewidth=line_width, c='black')
        figure.savefig(output_path, bbox_inches='tight')
        plt.close()

    def make_files(self, output_label_path: str, output_image_path: str, line_width=2, dpi=300):
        self.make_image_file(output_image_path, line_width, dpi)
        self.make_label_file(output_label_path)

    @staticmethod
    def from_file(inkml_filepath: str):
        tree = ET.parse(inkml_filepath)
        root = tree.getroot()

        annotations = []

        for annotation in root.findall('traceGroup'):
            label = annotation.find('.//Tg_Truth').text

            coord_groups = []
            for trace_tag in annotation.findall('trace'):
                coord_group = []
                for coord_text in trace_tag.text.split(','):
                    if coord_text == '':
                        continue
                    coords = coord_text.split(' ')
                    coords = np.array([int(coord) for coord in coords if coord != ''])
                    assert len(coords) == 2
                    coord_group.append(coords)
                coord_groups.append(coord_group)

            annotations.append(Annotation(annotation.get('id'), label, np.array(coord_groups)))
        return annotations

def make_annotations(input_inkml, output_dir, line_width=2, dpi=300):
    annotations = Annotation.from_file(input_inkml)
    for annotation in annotations:
        output_basename = os.path.splitext(
            os.path.basename(input_inkml))[0]
        output_filename = output_basename + '_' + annotation.id
        output_image_name = output_filename + '.png'
        output_label_name = output_filename + '.txt'

        output_image_path = os.path.join(output_dir, output_image_name)
        output_label_path = os.path.join(output_dir, output_label_name)
        annotation.make_files(output_label_path, output_image_path, line_width, dpi)