#!/usr/bin/env python3

import copy

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from sensor_msgs.msg import CameraInfo


class StereoCameraInfo(Node):

    def __init__(self):

        super().__init__('stereo_camera_info')

        self.baseline = 0.12

        self.left_info = None
        self.right_info = None

        self.left_pub = self.create_publisher(
            CameraInfo,
            '/camera/left/camera_info_stereo',
            10
        )

        self.right_pub = self.create_publisher(
            CameraInfo,
            '/camera/right/camera_info_stereo',
            10
        )

        self.create_subscription(
            CameraInfo,
            '/camera/left/camera_info',
            self.left_info_callback,
            10
        )

        self.create_subscription(
            CameraInfo,
            '/camera/right/camera_info',
            self.right_info_callback,
            10
        )

        self.create_subscription(
            Image,
            '/camera/left/image_raw',
            self.left_image_callback,
            10
        )

        self.create_subscription(
            Image,
            '/camera/right/image_raw',
            self.right_image_callback,
            10
        )

        self.get_logger().info(
            'VAJRA stereo calibration started'
        )

        self.get_logger().info(
            'Stereo baseline = 0.120 m'
        )

    def left_info_callback(self, msg):

        self.left_info = msg

    def right_info_callback(self, msg):

        self.right_info = msg

    def left_image_callback(self, image):

        if self.left_info is None:
            return

        out = copy.deepcopy(self.left_info)

        fx = self.left_info.k[0]
        fy = self.left_info.k[4]
        cx = self.left_info.k[2]
        cy = self.left_info.k[5]

        out.header.stamp = image.header.stamp
        out.header.frame_id = 'left_camera_link'

        out.p[0] = fx
        out.p[1] = 0.0
        out.p[2] = cx
        out.p[3] = 0.0

        out.p[4] = 0.0
        out.p[5] = fy
        out.p[6] = cy
        out.p[7] = 0.0

        out.p[8] = 0.0
        out.p[9] = 0.0
        out.p[10] = 1.0
        out.p[11] = 0.0

        self.left_pub.publish(out)

    def right_image_callback(self, image):

        if self.right_info is None:
            return

        out = copy.deepcopy(self.right_info)

        fx = self.right_info.k[0]
        fy = self.right_info.k[4]
        cx = self.right_info.k[2]
        cy = self.right_info.k[5]

        out.header.stamp = image.header.stamp
        out.header.frame_id = 'right_camera_link'

        out.p[0] = fx
        out.p[1] = 0.0
        out.p[2] = cx
        out.p[3] = -fx * self.baseline

        out.p[4] = 0.0
        out.p[5] = fy
        out.p[6] = cy
        out.p[7] = 0.0

        out.p[8] = 0.0
        out.p[9] = 0.0
        out.p[10] = 1.0
        out.p[11] = 0.0

        self.right_pub.publish(out)


def main(args=None):

    rclpy.init(args=args)

    node = StereoCameraInfo()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
