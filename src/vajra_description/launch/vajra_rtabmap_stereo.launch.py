from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    common_params = {
        'use_sim_time': True,

        'frame_id': 'base_link',
        'odom_frame_id': '',

        'subscribe_odom': True,
        'subscribe_stereo': True,

        'approx_sync': True,
        'approx_sync_max_interval': 0.30,
        'sync_queue_size': 50,

        'Rtabmap/DetectionRate': '5.0',

        'Mem/IncrementalMemory': 'true',
        'Mem/InitWMWithAllNodes': 'false',

        'Stereo/MaxDisparity': '128',
        'Stereo/MinDisparity': '0',

        'Kp/DetectorStrategy': '2',
        'Vis/FeatureType': '2',

        'RGBD/LinearUpdate': '0.05',
        'RGBD/AngularUpdate': '0.05',

        'subscribe_scan': False,
        'subscribe_scan_cloud': False,
    }

    stereo_remappings = [
        ('odom', '/odom'),

        ('left/image_rect',
         '/camera/left/image_raw'),

        ('right/image_rect',
         '/camera/right/image_raw'),

        ('left/camera_info',
         '/camera/left/camera_info_stereo'),

        ('right/camera_info',
         '/camera/right/camera_info_stereo'),
    ]

    return LaunchDescription([

        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',

            parameters=[common_params],

            remappings=stereo_remappings,

            arguments=[
                '--delete_db_on_start'
            ]
        ),

        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            name='rtabmap_viz',
            output='screen',

            parameters=[{
                'use_sim_time': True,
                'frame_id': 'base_link',
                'odom_frame_id': '',

                'subscribe_odom': True,
                'subscribe_stereo': True,

                'approx_sync': True,
                'approx_sync_max_interval': 0.30,
                'sync_queue_size': 50,
            }],

            remappings=stereo_remappings
        )
    ])
