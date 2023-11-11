import re
import os
import pprint
import numpy as np
from scipy.spatial.transform import Rotation as R
import shlex
import subprocess

import rclpy

import bpy
import urdf_parser_py
from urdf_parser_py import urdf
from ament_index_python.packages import get_package_share_directory

import mathutils

def parse_file_name(file_name): 
    p = re.compile("package://(.*?)/")
    result = p.search(file_name)
        
    package_name = result.group(1)
    package_share_directory = get_package_share_directory(package_name)
    file_name = file_name.replace(result.group(0), "")
    full_file_name = os.path.join(package_share_directory, file_name)
    return full_file_name


def load_geometry(geom): 
    if isinstance(geom, urdf_parser_py.urdf.Box): 
        bpy.ops.mesh.primitive_cube_add(size=1.0, 
                                        calc_uvs=True, 
                                        enter_editmode=False, 
                                        align='WORLD', 
                                        location=(0.0, 0.0, 0.0), 
                                        rotation=(0.0, 0.0, 0.0), 
                                        scale=geom.size)
    elif isinstance(geom, urdf_parser_py.urdf.Mesh): 
        file_name = parse_file_name(geom.filename)
        bpy.ops.import_mesh.stl(filepath=file_name)
    
def load_visual(visual):
    if visual is None: 
        bpy.ops.object.empty_add() 
    else:
        load_geometry(visual.geometry)
        
    return bpy.context.object 

def main():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False, confirm=False)

    urdf_path = "/home/misha/code/blurdf/config/fanuc.urdf"

    with open(urdf_path) as f:
        data = f.read()
    robot = urdf.Robot.from_xml_string(data)
    
    
    links = {}
    
    for link in robot.links:
        loaded_visual = load_visual(link.visual)
        loaded_visual.name = link.name
        links[link.name] = loaded_visual
        
    for joint in robot.joints:
        print("---------------------------------")
        
        T = mathutils.Euler(joint.origin.rpy, 'XYZ').to_matrix()
        T.resize_4x4()
        t = mathutils.Matrix.Translation(joint.origin.xyz).translation
        T.translation = t
        

        links[joint.child].matrix_world = T
        links[joint.child].parent = links[joint.parent]
        
        lim_loc = links[joint.child].constraints.new("LIMIT_LOCATION")
        lim_loc.owner_space = "LOCAL"
        lim_loc.use_min_x = True
        lim_loc.use_min_y = True
        lim_loc.use_min_z = True
        
        lim_loc.use_max_x = True
        lim_loc.use_max_y = True
        lim_loc.use_max_z = True
        lim_rot = links[joint.child].constraints.new("LIMIT_ROTATION")


        links[joint.child].matrix_world = T
        links[joint.child].parent = links[joint.parent]
#        links[joint.child].matrix_local = T

#        print(links[joint.child].constraints)
#        print(links[joint.child].matrix_world)
#        print(links[joint.child].matrix_local)
#        print(links[joint.child].matrix_parent_inverse)
#        print(links[joint.child].matrix_basis)



if __name__ == "__main__":
    main()