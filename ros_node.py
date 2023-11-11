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
        bpy.ops.object.empty_add(radius=0.25) 
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
        
        links[joint.child].parent = links[joint.parent]
        links[joint.child].matrix_local = T
        
        bpy.ops.object.empty_add(radius=0.01)
        
        joint_frame = bpy.context.object
        joint_frame.name = joint.name
        joint_frame.parent = links[joint.parent]
        joint_frame.matrix_local = T 

#        bpy.context.view_layer.update()
#        if(True):

#        if(joint.type == "fixed"):

        lim_loc = links[joint.child].constraints.new("LIMIT_LOCATION")
        lim_loc.owner_space = "CUSTOM"
        lim_loc.space_object = joint_frame

        lim_loc.use_min_x = True
        lim_loc.use_min_y = True
        lim_loc.use_min_z = True
        
        lim_loc.use_max_x = True
        lim_loc.use_max_y = True
        lim_loc.use_max_z = True

        lim_rot = links[joint.child].constraints.new("LIMIT_ROTATION")
        lim_rot.owner_space = "CUSTOM"
        lim_rot.space_object = joint_frame

        lim_rot.use_limit_x = True
        lim_rot.use_limit_y = True
        lim_rot.use_limit_z = True
        
        if joint.type == "revolute":
    
            print(joint.limit)
            low = joint.limit.lower
            high = joint.limit.upper
            
            norm_axis = np.abs(joint.axis / np.linalg.norm(joint.axis))
            if norm_axis[0]: 
                print("x axis") 
                lim_rot.min_x, lim_rot.max_x = low, high
            elif norm_axis[1]:
                print("y axis") 
                lim_rot.min_y, lim_rot.max_y = low, high
            elif norm_axis[2]:
                print("z axis") 
                lim_rot.min_z, lim_rot.max_z = low, high
            else: 
                lim_rot.use_limit_x = False
                lim_rot.use_limit_y = False
                lim_rot.use_limit_z = False


if __name__ == "__main__":
    main()