#!/usr/bin/env python3

import math

import rclpy
from rclpy.node import Node

from geometry_msgs.msg import Twist
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class VajraOdom(Node):

    def __init__(self):
        super().__init__('vajra_odom')

        self.x = 0.0
        self.y = 0.0
        self.yaw = 0.0

        self.linear = 0.0
        self.angular = 0.0

        self.last_time = self.get_clock().now()

        self.create_subscription(
            Twist,
            '/model/vajra/cmd_vel',
            self.cmd_callback,
            10
        )

        self.odom_pub = self.create_publisher(
            Odometry,
            '/odom',
            10
        )

        self.tf_broadcaster = TransformBroadcaster(self)

        self.create_timer(0.02, self.update)

    def cmd_callback(self, msg):
        self.linear = msg.linear.x
        self.angular = msg.angular.z

    def update(self):

        now = self.get_clock().now()
        dt = (now - self.last_time).nanoseconds / 1e9
        self.last_time = now

        if dt <= 0.0:
            return

        self.x += self.linear * math.cos(self.yaw) * dt
        self.y += self.linear * math.sin(self.yaw) * dt
        self.yaw += self.angular * dt

        qz = math.sin(self.yaw / 2.0)
        qw = math.cos(self.yaw / 2.0)

        # -------------------------
        # Publish odometry
        # -------------------------

        odom = Odometry()

        odom.header.stamp = now.to_msg()
        odom.header.frame_id = 'odom'
        odom.child_frame_id = 'base_link'

        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0

        odom.pose.pose.orientation.z = qz
        odom.pose.pose.orientation.w = qw

        odom.twist.twist.linear.x = self.linear
        odom.twist.twist.angular.z = self.angular

        self.odom_pub.publish(odom)

        # -------------------------
        # Publish TF
        # -------------------------

        tf = TransformStamped()

        tf.header.stamp = now.to_msg()
        tf.header.frame_id = 'odom'
        tf.child_frame_id = 'base_link'

        tf.transform.translation.x = self.x
        tf.transform.translation.y = self.y
        tf.transform.translation.z = 0.0

        tf.transform.rotation.z = qz
        tf.transform.rotation.w = qw

        self.tf_broadcaster.sendTransform(tf)


def main(args=None):

    rclpy.init(args=args)

    node = VajraOdom()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
