#!/usr/bin/env python3

import math
import time

import cv2
import numpy as np
import rclpy

from rclpy.node import Node
from sensor_msgs.msg import Image
from nav_msgs.msg import Odometry
from cv_bridge import CvBridge


class StereoCameraSimulator(Node):

    def __init__(self):

        super().__init__('stereo_camera_simulator')

        self.bridge = CvBridge()

        self.left_pub = self.create_publisher(
            Image,
            '/camera/left/image_raw',
            10
        )

        self.right_pub = self.create_publisher(
            Image,
            '/camera/right/image_raw',
            10
        )

        self.x = 0.0
        self.y = 0.0

        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        self.start = time.time()

        self.timer = self.create_timer(
            1.0 / 20.0,
            self.publish
        )

        self.get_logger().info(
            'VAJRA LIVE STEREO CAMERA STARTED'
        )

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    def create_camera(self, right=False):

        width = 640
        height = 480

        image = np.zeros(
            (height, width, 3),
            dtype=np.uint8
        )

        t = time.time() - self.start

        # Simulated forward movement
        motion = self.x * 80.0

        if right:
            motion += 12

        # Dark tunnel
        image[:] = (22, 22, 22)

        # Tunnel walls
        cv2.fillPoly(
            image,
            [np.array([
                [0, 80],
                [120, 120],
                [120, 270],
                [0, 480]
            ])],
            (65, 55, 45)
        )

        cv2.fillPoly(
            image,
            [np.array([
                [640, 80],
                [520, 120],
                [520, 270],
                [640, 480]
            ])],
            (65, 55, 45)
        )

        # Ceiling
        cv2.fillPoly(
            image,
            [np.array([
                [0, 0],
                [640, 0],
                [520, 120],
                [120, 120]
            ])],
            (15, 15, 15)
        )

        # Floor
        cv2.fillPoly(
            image,
            [np.array([
                [0, 480],
                [640, 480],
                [520, 260],
                [120, 260]
            ])],
            (42, 39, 34)
        )

        # Perspective tracks
        cv2.line(
            image,
            (220, 480),
            (285, 250),
            (110, 110, 110),
            5
        )

        cv2.line(
            image,
            (420, 480),
            (355, 250),
            (110, 110, 110),
            5
        )

        # Moving sleepers
        offset = int(motion) % 40

        for y in range(260 + offset, 500, 40):

            depth = max(0.2, (y - 250) / 230)

            left = int(285 - 65 * depth)
            right_edge = int(355 + 65 * depth)

            cv2.line(
                image,
                (left, y),
                (right_edge, y),
                (85, 70, 55),
                4
            )

        # Rocks change position as rover moves
        rocks = [
            (120, 310, 35, 1.0),
            (520, 335, 42, 0.8),
            (160, 220, 24, 0.6),
            (475, 255, 30, 1.2),
            (330, 205, 20, 0.5)
        ]

        for base_x, base_y, radius, speed in rocks:

            px = base_x - int(
                motion * speed
            ) % 700

            px = px % 700 - 30

            cv2.circle(
                image,
                (px, base_y),
                radius,
                (78, 70, 60),
                -1
            )

            cv2.circle(
                image,
                (px - 8, base_y - 8),
                max(3, radius // 5),
                (105, 95, 80),
                -1
            )

        # Mine lights
        for i in range(5):

            lx = 100 + i * 110

            flicker = int(
                8 * math.sin(t * 4 + i)
            )

            brightness = 100 + flicker

            cv2.circle(
                image,
                (lx, 105),
                8,
                (brightness, brightness, brightness),
                -1
            )

        # HUD
        label = (
            "VAJRA  RIGHT CAMERA"
            if right
            else
            "VAJRA  LEFT CAMERA"
        )

        cv2.putText(
            image,
            label,
            (18, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 210, 255),
            2
        )

        cv2.putText(
            image,
            "LIVE • UNDERGROUND MINE",
            (18, 460),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (190, 190, 190),
            1
        )

        return image

    def publish(self):

        left = self.create_camera(False)
        right = self.create_camera(True)

        left_msg = self.bridge.cv2_to_imgmsg(
            left,
            encoding='bgr8'
        )

        right_msg = self.bridge.cv2_to_imgmsg(
            right,
            encoding='bgr8'
        )

        stamp = self.get_clock().now().to_msg()

        left_msg.header.stamp = stamp
        right_msg.header.stamp = stamp

        left_msg.header.frame_id = 'left_camera_link'
        right_msg.header.frame_id = 'right_camera_link'

        self.left_pub.publish(left_msg)
        self.right_pub.publish(right_msg)


def main(args=None):

    rclpy.init(args=args)

    node = StereoCameraSimulator()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        node.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
