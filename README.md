## Notes:

Figured out how to get access to external paths and packages in the blender environment 


1. Source your ROS workspace
```
/opt/ros/humble/setup.bash
```

2. Launch blender with environment flag
```
blender --python-use-system-env 
```