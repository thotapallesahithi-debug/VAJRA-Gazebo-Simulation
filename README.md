# VAJRA Mine Rescue Rover — Gazebo Simulation

This repository contains the working VAJRA underground mine-rescue rover simulation developed in ROS 2 Humble with Gazebo Sim / Gazebo Harmonic.

## Included

- VAJRA rover URDF with six-wheel differential drive
- Underground mine environment
- Real Gazebo stereo RGB camera sensors
- ROS 2 ↔ Gazebo topic bridging
- Rover velocity control and odometry
- Web dashboard with live left/right camera feeds
- Simulated CH4, CO, H2S, temperature, humidity, and vibration sensing
- Hazard values that vary with rover position
- Supporting stereo camera information and odometry-to-TF nodes
- RTAB-Map/SLAM-related launch and configuration files retained for future development

## Current demo architecture

Gazebo camera sensors → Gazebo Sensors system → `ros_gz_image` → ROS camera topics → VAJRA dashboard

Rover controls → ROS `/model/vajra/cmd_vel` → `ros_gz_bridge` → Gazebo

Gazebo odometry → `ros_gz_bridge` → ROS `/odom` → dashboard/sensor simulation

## Software

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Sim / Gazebo Harmonic

## Workspace

The ROS 2 workspace is under `vajra_ws/src/`.

Build from the workspace root:

```bash
cd vajra_ws
colcon build --symlink-install
source install/setup.bash
```

The generated `build/`, `install/`, and `log/` directories are intentionally not included in this repository archive.

## Notes

This archive preserves the working source files from the frozen simulation workspace. SLAM/RTAB-Map files are retained but are not required for the current demo configuration.
