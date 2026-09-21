from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

import os


def generate_launch_description():

    pkg_vajra = get_package_share_directory(
        "vajra_description"
    )

    pkg_ros_gz_sim = get_package_share_directory(
        "ros_gz_sim"
    )

    world_file = os.path.join(
        pkg_vajra,
        "worlds",
        "vajra_mine.sdf"
    )

    bridge_file = os.path.join(
        pkg_vajra,
        "config",
        "bridge.yaml"
    )

    robot_file = os.path.join(
        pkg_vajra,
        "urdf",
        "vajra.urdf"
    )

    with open(robot_file, "r") as f:
        robot_description = f.read()

    return LaunchDescription([

        # Gazebo Harmonic
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    pkg_ros_gz_sim,
                    "launch",
                    "gz_sim.launch.py"
                )
            ),
            launch_arguments={
                "gz_args": f"-r {world_file}"
            }.items()
        ),

        # Robot state publisher
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            name="robot_state_publisher",
            output="screen",
            parameters=[{
                "robot_description": robot_description,
                "use_sim_time": True
            }]
        ),

        # Spawn VAJRA
        Node(
            package="ros_gz_sim",
            executable="create",
            name="spawn_robot",
            output="screen",
            arguments=[
                "-name",
                "vajra",
                "-topic",
                "robot_description",
                "-x",
                "0.0",
                "-y",
                "0.0",
                "-z",
                "0.25"
            ]
        ),

        # Gazebo <-> ROS bridge
        Node(
            package="ros_gz_bridge",
            executable="parameter_bridge",
            name="vajra_bridge",
            output="screen",
            parameters=[{
                "config_file": bridge_file
            }]
        ),

        # LEFT REAL GAZEBO CAMERA
        Node(
            package="ros_gz_image",
            executable="image_bridge",
            name="left_camera_bridge",
            output="screen",
            arguments=[
                "/camera/left/image_raw"
            ]
        ),

        # RIGHT REAL GAZEBO CAMERA
        Node(
            package="ros_gz_image",
            executable="image_bridge",
            name="right_camera_bridge",
            output="screen",
            arguments=[
                "/camera/right/image_raw"
            ]
        ),

        # Odometry TF
        Node(
            package="vajra_description",
            executable="odom_to_tf.py",
            name="odom_to_tf",
            output="screen"
        ),

        # Stereo camera info
        Node(
            package="vajra_description",
            executable="stereo_camera_info.py",
            name="stereo_camera_info",
            output="screen"
        ),
    ])
