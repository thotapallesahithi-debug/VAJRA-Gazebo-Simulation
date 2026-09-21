#!/usr/bin/env python3

import math
import time

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, Bool
from nav_msgs.msg import Odometry


class VajraSensorSimulator(Node):

    def __init__(self):

        super().__init__('vajra_sensor_simulator')

        self.start_time = time.time()

        self.x = 0.0
        self.y = 0.0

        # -------------------------
        # SENSOR PUBLISHERS
        # -------------------------

        self.ch4_pub = self.create_publisher(
            Float32,
            '/vajra/sensors/ch4',
            10
        )

        self.co_pub = self.create_publisher(
            Float32,
            '/vajra/sensors/co',
            10
        )

        self.h2s_pub = self.create_publisher(
            Float32,
            '/vajra/sensors/h2s',
            10
        )

        self.temperature_pub = self.create_publisher(
            Float32,
            '/vajra/sensors/temperature',
            10
        )

        self.humidity_pub = self.create_publisher(
            Float32,
            '/vajra/sensors/humidity',
            10
        )

        self.vibration_pub = self.create_publisher(
            Bool,
            '/vajra/sensors/vibration',
            10
        )

        # -------------------------
        # ODOMETRY
        # -------------------------

        self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # -------------------------
        # TIMER
        # -------------------------

        self.timer = self.create_timer(
            0.25,
            self.publish_sensors
        )

        self.get_logger().info(
            'VAJRA hazard sensor simulator started'
        )

    # ==================================================
    # ODOMETRY
    # ==================================================

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    # ==================================================
    # FLOAT MESSAGE
    # ==================================================

    def float_msg(self, value):

        msg = Float32()
        msg.data = float(value)

        return msg

    # ==================================================
    # HAZARD MODEL
    # ==================================================

    def calculate_hazards(self):

        t = time.time() - self.start_time

        # ----------------------------------------------
        # BASE MINE CONDITIONS
        # ----------------------------------------------

        ch4 = 18.0
        co = 4.0
        h2s = 0.4

        temperature = 27.0
        humidity = 65.0

        # ----------------------------------------------
        # HAZARD ZONE 1
        # METHANE
        #
        # Around x = 8 m
        # ----------------------------------------------

        methane_distance = math.sqrt(
            (self.x - 8.0) ** 2 +
            (self.y - 0.0) ** 2
        )

        if methane_distance < 4.0:

            strength = 1.0 - methane_distance / 4.0

            ch4 += 70.0 * strength

        # ----------------------------------------------
        # HAZARD ZONE 2
        # CO
        #
        # Around x = 15 m
        # ----------------------------------------------

        co_distance = math.sqrt(
            (self.x - 15.0) ** 2 +
            (self.y - 0.5) ** 2
        )

        if co_distance < 4.0:

            strength = 1.0 - co_distance / 4.0

            co += 45.0 * strength

        # ----------------------------------------------
        # HAZARD ZONE 3
        # H2S
        #
        # Around x = 22 m
        # ----------------------------------------------

        h2s_distance = math.sqrt(
            (self.x - 22.0) ** 2 +
            (self.y + 0.5) ** 2
        )

        if h2s_distance < 4.0:

            strength = 1.0 - h2s_distance / 4.0

            h2s += 12.0 * strength

        # ----------------------------------------------
        # GENERAL MINE ENVIRONMENT
        # ----------------------------------------------

        temperature += (
            1.5 * math.sin(t * 0.15)
        )

        humidity += (
            5.0 * math.sin(t * 0.12)
        )

        # ----------------------------------------------
        # SMALL SENSOR NOISE
        # ----------------------------------------------

        ch4 += 2.0 * math.sin(t * 1.7)
        co += 0.8 * math.sin(t * 1.4)
        h2s += 0.15 * math.sin(t * 1.9)

        # Prevent impossible values
        ch4 = max(0.0, ch4)
        co = max(0.0, co)
        h2s = max(0.0, h2s)

        return (
            ch4,
            co,
            h2s,
            temperature,
            humidity
        )

    # ==================================================
    # PUBLISH
    # ==================================================

    def publish_sensors(self):

        (
            ch4,
            co,
            h2s,
            temperature,
            humidity
        ) = self.calculate_hazards()

        # -------------------------
        # GAS
        # -------------------------

        self.ch4_pub.publish(
            self.float_msg(ch4)
        )

        self.co_pub.publish(
            self.float_msg(co)
        )

        self.h2s_pub.publish(
            self.float_msg(h2s)
        )

        # -------------------------
        # ENVIRONMENT
        # -------------------------

        self.temperature_pub.publish(
            self.float_msg(temperature)
        )

        self.humidity_pub.publish(
            self.float_msg(humidity)
        )

        # -------------------------
        # VIBRATION
        # -------------------------

        # Vibration increases near hazard areas
        hazard_distance = min(
            math.sqrt((self.x - 8.0) ** 2 + self.y ** 2),
            math.sqrt((self.x - 15.0) ** 2 + (self.y - 0.5) ** 2),
            math.sqrt((self.x - 22.0) ** 2 + (self.y + 0.5) ** 2)
        )

        vibration = (
            hazard_distance < 2.5
            and int(time.time() * 3) % 3 != 0
        )

        vibration_msg = Bool()
        vibration_msg.data = vibration

        self.vibration_pub.publish(
            vibration_msg
        )


def main(args=None):

    rclpy.init(args=args)

    node = VajraSensorSimulator()

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
