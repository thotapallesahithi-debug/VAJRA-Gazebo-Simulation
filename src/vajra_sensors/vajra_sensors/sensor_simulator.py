#!/usr/bin/env python3

import json
import math
import random
import time

import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32, String
from nav_msgs.msg import Odometry


class VajraSensorSimulator(Node):

    def __init__(self):
        super().__init__('vajra_sensor_simulator')

        # ============================================================
        # SENSOR PUBLISHERS
        # ============================================================

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
            Float32,
            '/vajra/sensors/vibration',
            10
        )

        self.json_pub = self.create_publisher(
            String,
            '/vajra/sensors/json',
            10
        )

        # ============================================================
        # ROBOT POSITION
        # ============================================================

        self.x = 0.0
        self.y = 0.0

        self.odom_sub = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10
        )

        # ============================================================
        # TIMER
        # ============================================================

        self.timer = self.create_timer(
            0.5,
            self.publish_sensor_data
        )

        self.get_logger().info(
            'VAJRA sensor simulator started.'
        )

        self.get_logger().info(
            'Waiting for rover position from /odom...'
        )

    # ================================================================
    # ODOMETRY CALLBACK
    # ================================================================

    def odom_callback(self, msg):

        self.x = msg.pose.pose.position.x
        self.y = msg.pose.pose.position.y

    # ================================================================
    # CHECK HAZARD ZONES
    # ================================================================

    def get_hazard_zone(self):

        distance_from_hazard = math.sqrt(
            (self.x - 5.0) ** 2 +
            (self.y - 0.0) ** 2
        )

        if distance_from_hazard < 2.0:
            return "HIGH"

        distance_from_hazard = math.sqrt(
            (self.x + 5.0) ** 2 +
            (self.y - 3.0) ** 2
        )

        if distance_from_hazard < 2.0:
            return "MEDIUM"

        return "NORMAL"

    # ================================================================
    # GENERATE SENSOR VALUES
    # ================================================================

    def generate_sensor_values(self):

        zone = self.get_hazard_zone()

        # ------------------------------------------------------------
        # NORMAL CONDITIONS
        # ------------------------------------------------------------

        if zone == "NORMAL":

            ch4 = random.uniform(0.20, 0.45)
            co = random.uniform(5.0, 12.0)
            h2s = random.uniform(0.5, 2.0)

            temperature = random.uniform(25.0, 29.0)
            humidity = random.uniform(55.0, 70.0)

            vibration = random.uniform(0.01, 0.08)

        # ------------------------------------------------------------
        # MEDIUM HAZARD
        # ------------------------------------------------------------

        elif zone == "MEDIUM":

            ch4 = random.uniform(0.8, 1.5)
            co = random.uniform(20.0, 40.0)
            h2s = random.uniform(3.0, 7.0)

            temperature = random.uniform(29.0, 34.0)
            humidity = random.uniform(65.0, 80.0)

            vibration = random.uniform(0.10, 0.30)

        # ------------------------------------------------------------
        # HIGH HAZARD
        # ------------------------------------------------------------

        else:

            ch4 = random.uniform(2.0, 3.5)
            co = random.uniform(50.0, 90.0)
            h2s = random.uniform(8.0, 15.0)

            temperature = random.uniform(34.0, 42.0)
            humidity = random.uniform(70.0, 90.0)

            vibration = random.uniform(0.35, 0.80)

        return {
            "ch4": round(ch4, 2),
            "co": round(co, 2),
            "h2s": round(h2s, 2),
            "temperature": round(temperature, 2),
            "humidity": round(humidity, 2),
            "vibration": round(vibration, 3),
            "hazard_zone": zone
        }

    # ================================================================
    # PUBLISH SENSOR DATA
    # ================================================================

    def publish_sensor_data(self):

        data = self.generate_sensor_values()

        # ------------------------------------------------------------
        # Publish individual ROS topics
        # ------------------------------------------------------------

        ch4_msg = Float32()
        ch4_msg.data = float(data["ch4"])
        self.ch4_pub.publish(ch4_msg)

        co_msg = Float32()
        co_msg.data = float(data["co"])
        self.co_pub.publish(co_msg)

        h2s_msg = Float32()
        h2s_msg.data = float(data["h2s"])
        self.h2s_pub.publish(h2s_msg)

        temperature_msg = Float32()
        temperature_msg.data = float(data["temperature"])
        self.temperature_pub.publish(temperature_msg)

        humidity_msg = Float32()
        humidity_msg.data = float(data["humidity"])
        self.humidity_pub.publish(humidity_msg)

        vibration_msg = Float32()
        vibration_msg.data = float(data["vibration"])
        self.vibration_pub.publish(vibration_msg)

        # ------------------------------------------------------------
        # Create combined JSON packet
        # ------------------------------------------------------------

        json_data = {
            "timestamp": time.time(),

            "robot": {
                "x": round(self.x, 3),
                "y": round(self.y, 3)
            },

            "sensors": {
                "CH4": data["ch4"],
                "CO": data["co"],
                "H2S": data["h2s"],
                "temperature": data["temperature"],
                "humidity": data["humidity"],
                "vibration": data["vibration"]
            },

            "hazard": {
                "zone": data["hazard_zone"]
            }
        }

        json_msg = String()
        json_msg.data = json.dumps(json_data)

        self.json_pub.publish(json_msg)

        # ------------------------------------------------------------
        # Console output
        # ------------------------------------------------------------

        self.get_logger().info(
            f"ZONE={data['hazard_zone']} | "
            f"CH4={data['ch4']}% | "
            f"CO={data['co']}ppm | "
            f"H2S={data['h2s']}ppm | "
            f"T={data['temperature']}C | "
            f"RH={data['humidity']}% | "
            f"VIB={data['vibration']}"
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
        rclpy.shutdown()


if __name__ == '__main__':
    main()
