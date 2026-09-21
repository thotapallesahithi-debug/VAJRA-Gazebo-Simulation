from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():

    return LaunchDescription([

        Node(
            package='rtabmap_odom',
            executable='stereo_odometry',
            name='stereo_odometry',
            output='screen',

            parameters=[{
                'use_sim_time': True,

                'frame_id': 'base_link',
                'odom_frame_id': 'visual_odom',

                'publish_tf': True,

                'approx_sync': True,
                'approx_sync_max_interval': 0.1,

                'wait_for_transform': 0.5,

                # ORB features
                'Vis/FeatureType': '2',
                'Kp/DetectorStrategy': '2',

                # Stereo visual odometry
                'Vis/EstimationType': '1',
                'Odom/Strategy': '0',

                # RTAB-Map string parameter
                'Odom/GuessMotion': 'false',

                'Odom/FilteringStrategy': '0',
            }],

            remappings=[

                ('left/image_rect',
                 '/camera/left/image_raw'),

                ('right/image_rect',
                 '/camera/right/image_raw'),

                ('left/camera_info',
                 '/camera/left/camera_info_stereo'),

                ('right/camera_info',
                 '/camera/right/camera_info_stereo'),

                ('odom',
                 '/visual_odom'),
            ]
        )
    ])
