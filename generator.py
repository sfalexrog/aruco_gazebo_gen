#!/usr/bin/env python3

import cv2
import numpy as np
import os
import string

# FIXME: Add support for additional dictionaries
aruco_dict = cv2.aruco_Dictionary.get(cv2.aruco.DICT_4X4_1000)
marker_bits = 4
marker_outer_bits = marker_bits + 2
marker_border_bits = marker_outer_bits + 2
include_template = string.Template('''
    <include>
      <uri>model://aruco_$marker_id</uri>
      <pose>$x $y $z $roll $pitch $yaw</pose>
    </include>
''')
world_string = ''


def create_aruco(marker_id: int, size: float) -> None:
    model_dir = 'aruco_{}'.format(marker_id)
    script_dir = '{}/materials/scripts'.format(model_dir)
    texture_dir = '{}/materials/textures'.format(model_dir)
    os.makedirs(model_dir, exist_ok=True)
    os.makedirs(script_dir, exist_ok=True)
    os.makedirs(texture_dir, exist_ok=True)
    marker_image = np.zeros((marker_border_bits, marker_border_bits), dtype=np.uint8)
    marker_image[:,:] = 255
    marker_image[1:marker_border_bits - 1, 1:marker_border_bits - 1] = cv2.aruco.drawMarker(
        aruco_dict, marker_id, marker_outer_bits)
    cv2.imwrite('{}/aruco_marker_{}.png'.format(texture_dir, marker_id), marker_image)
    script_template_str = ''.join(open('templates/materials/scripts/aruco.material').readlines())
    script_template = string.Template(script_template_str)
    with open('{}/aruco_{}.material'.format(script_dir, marker_id), 'w') as f:
        f.write(script_template.substitute(marker_id=marker_id))
    model_template_str = ''.join(open('templates/marker_template.sdf').readlines())
    model_template = string.Template(model_template_str)
    full_size = size * marker_border_bits / marker_outer_bits
    with open('{}/marker_{}.sdf'.format(model_dir, marker_id), 'w') as f:
        f.write(model_template.substitute(marker_id=marker_id, marker_full_size=full_size))
    desc_template_str = model_template_str = ''.join(open('templates/model.config').readlines())
    desc_template = string.Template(desc_template_str)
    with open('{}/model.config'.format(model_dir), 'w') as f:
        f.write(desc_template.substitute(marker_id=marker_id))


def add_marker(marker_id: int, size: float, x: float, y: float, z: float = 0,
                yaw: float = 0, pitch: float = 0, roll: float = 0) -> None:
    global world_string
    create_aruco(marker_id, size)
    world_string += include_template.substitute(marker_id=marker_id,
        x=x, y=y, z=z, yaw=yaw, pitch=pitch, roll=roll)


def create_world():
    world_template_str = ''.join(open('templates/world_template.world').readlines())
    world_template = string.Template(world_template_str)
    with open('aruco_world.world', 'w') as f:
        f.write(world_template.substitute(model_inclusions=world_string))


# Returns a tuple: parse_result (bool), parser message (str)
# parse_result is True if there is no error, False otherwise
# a value of True does not mean a marker was added
def parse_line(line: str) -> (bool, str):
    if line.startswith('#'):
        return (True, 'Comment line - not parsing')
    marker_params = line.split()
    if len(marker_params) == 0:
        return (True, 'Empty line - not parsing')
    if len(marker_params) < 4:
        return (False, 'Not enough data for aruco generation: {}'.format(line))
    try:
        marker_id = int(marker_params[0])
        size = float(marker_params[1])
        x = float(marker_params[2])
        y = float(marker_params[3])
        z = float(marker_params[4]) if len(marker_params) > 4 else 0
        yaw = float(marker_params[5]) if len(marker_params) > 5 else 0
        pitch = float(marker_params[6]) if len(marker_params) > 6 else 0
        roll = float(marker_params[7]) if len(marker_params) > 7 else 0
    except ValueError as ve:
        return (False, 'Could not process line: {}'.format(ve))
    add_marker(marker_id, size, x, y, z, yaw, pitch, roll)
    return (True, 'Added marker {}'.format(marker_id))


def parse_file(map_file: str) -> None:
    with open(map_file) as f:
        for linenum, line in enumerate(f.readlines()):
            res, msg = parse_line(line)
            if not res:
                print('Error while parsing line {}: {}'.format(linenum, msg))
    create_world()

if __name__ == '__main__':
    import sys
    if (len(sys.argv) < 2):
        print("Usage: {} map_file.txt".format(sys.argv[0]))
        exit()
    parse_file(sys.argv[1])
