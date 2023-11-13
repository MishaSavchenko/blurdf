import bpy
import yaml
import numpy as np
from pprint import pprint

print("lets move a bit")
all_scene_objects = bpy.ops.object.select_all(action='SELECT')

#for k,v in bpy.context.scene.objects.items():
#    print(k)

#link_3 = bpy.data.objects["link_3"]
#joint_rot = link_3.rotation_euler[1]
#for i in range(20):
#    link_3.rotation_euler[1] = np.deg2rad(i * 90.0/20.0)
#    res = link_3.keyframe_insert(data_path="rotation_euler", frame=i)

file_path = "/home/misha/code/blurdf/config/controller_feedback/test.yaml"

trajectory = []

with open(file_path, "r") as stream:
    try:
        traj_stream = stream.read()
        for tp in traj_stream.split("---"):
            trajectory.append(yaml.safe_load(tp))
    except yaml.YAMLError as exc:
        print(exc)

      
a = { "joint_1": 2,
      "joint_2": 1,
      "joint_3": 1,
      "joint_4": 0,
      "joint_5": 1,
      "joint_6": 0,
      }
b = {"joint_1": "link_1",
      "joint_2": "link_2",
      "joint_3": "link_3",
      "joint_4": "link_4",
      "joint_5": "link_5",
      "joint_6": "link_6",


}

cnt = 0 
for t in trajectory:
    names = t["feedback"]["joint_names"]
    positions = t["feedback"]["actual"]["positions"]
    
    for indx, name in enumerate(names):
        bpy.data.objects[b[name]].rotation_euler[a[name]] = positions[indx]
        bpy.data.objects[b[name]].keyframe_insert(data_path="rotation_euler", frame=cnt )
    cnt+=1 