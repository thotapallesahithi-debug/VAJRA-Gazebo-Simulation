from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    use_sim_time = LaunchConfiguration('use_sim_time')

    params = {
        'use_sim_time': use_sim_time,

        'frame_id': 'base_link',
        'map_frame_id': 'map',
        'odom_frame_id': 'odom',

        # External wheel odometry
        'subscribe_odom': True,
        'subscribe_odom_info': False,

        # Monocular camera
        'subscribe_rgb': True,
        'subscribe_depth': False,
        'subscribe_rgbd': False,
        'subscribe_stereo': False,

        # No LiDAR
        'subscribe_scan': False,
        'subscribe_scan_cloud': False,

        # Synchronization
        'approx_sync': True,
        'queue_size': 30,
        'topic_queue_size': 30,
        'sync_queue_size': 30,

        # Monocular structure from motion
        'Mem/StereoFromMotion': 'true',

        # Monocular 2D-2D visual registration
        'Vis/EstimationType': '2',
        'Vis/MinInliers': '6',
        'Vis/MaxDepth': '20.0',
        'Vis/InlierDistance': '0.1',

        # ORB
        'Kp/DetectorStrategy': '2',
        'Kp/MaxFeatures': '2000',

        # Memory
        'Mem/IncrementalMemory': 'true',
        'Mem/InitWMWithAllNodes': 'true',
        'Mem/UseOdomFeatures': 'false',

        # Loop closure
        'Rtabmap/DetectionRate': '5.0',

        # Do not pretend we have depth
        'RGBD/Enabled': 'true',
        'RGBD/CreateOccupancyGrid': 'false',
        'Grid/FromDepth': 'false',

        # RTAB-Map publishes map -> odom
        'publish_tf': True,

        # Important for Gazebo simulation
        'wait_for_transform': 0.5,
        'tf_tolerance': 0.2,
    }

    viz_params = {
        'use_sim_time': use_sim_time,

        'frame_id': 'base_link',
        'odom_frame_id': 'odom',

        'subscribe_odom': True,
        'subscribe_rgb': True,
        'subscribe_depth': False,
        'subscribe_rgbd': False,
        'subscribe_stereo': False,

        'approx_sync': True,
        'queue_size': 30,
    }

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true'
        ),

        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',

            parameters=[params],

            remappings=[
                ('rgb/image', '/camera/image_raw'),
                ('rgb/camera_info', '/camera/camera_info'),
                ('odom', '/odom'),
            ],

            arguments=[
                '--delete_db_on_start',
                '--ros-args',
                '--log-level',
                'rtabmap:=info'
            ]
        ),

        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            name='rtabmapviz',
            output='screen',

            parameters=[viz_params],

            remappings=[
                ('rgb/image', '/camera/image_raw'),
                ('rgb/camera_info', '/camera/camera_info'),
                ('odom', '/odom'),
            ]
        ),
    ])
