#!/usr/bin/env python3

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import rclpy
from rclpy.node import Node

from std_msgs.msg import String
from nav_msgs.msg import Odometry


# ================================================================
# SHARED DASHBOARD DATA
# ================================================================

dashboard_data = {
    "connected": False,

    "ch4": 0.0,
    "co": 0.0,
    "h2s": 0.0,

    "temperature": 0.0,
    "humidity": 0.0,
    "vibration": 0.0,

    "hazard_zone": "WAITING",

    "x": 0.0,
    "y": 0.0,
}


# ================================================================
# DASHBOARD HTML
# ================================================================

HTML = r"""
<!DOCTYPE html>

<html>

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width, initial-scale=1.0">

<title>VAJRA Mine Rescue Rover</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background: #0b0f14;
    color: #ffffff;
    font-family: Arial, Helvetica, sans-serif;
}

.header {
    background: #111820;
    border-bottom: 1px solid #26313c;
    padding: 18px 28px;

    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    font-size: 28px;
    font-weight: bold;
    letter-spacing: 2px;
}

.subtitle {
    color: #8e9aa7;
    margin-top: 4px;
    font-size: 13px;
}

.connection {
    display: flex;
    align-items: center;
    gap: 9px;
    font-size: 14px;
}

.status-dot {
    width: 11px;
    height: 11px;
    border-radius: 50%;
    background: #777;
}

.status-dot.online {
    background: #19d36b;
    box-shadow: 0 0 10px #19d36b;
}

.status-dot.offline {
    background: #e74c3c;
}

.container {
    padding: 24px;
    max-width: 1500px;
    margin: auto;
}

.section-title {
    color: #8e9aa7;
    font-size: 13px;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

.sensor-grid {
    display: grid;

    grid-template-columns:
        repeat(3, 1fr);

    gap: 16px;
}

.card {
    background: #111820;
    border: 1px solid #26313c;
    border-radius: 12px;
    padding: 20px;
    min-height: 145px;
}

.card-title {
    color: #8e9aa7;
    font-size: 14px;
    margin-bottom: 14px;
}

.value {
    font-size: 34px;
    font-weight: bold;
}

.unit {
    color: #8e9aa7;
    font-size: 15px;
    margin-left: 5px;
}

.normal {
    border-color: #26313c;
}

.warning {
    border-color: #e8a317;
    box-shadow: 0 0 15px rgba(232,163,23,0.15);
}

.danger {
    border-color: #e74c3c;
    box-shadow: 0 0 20px rgba(231,76,60,0.2);
}

.status-panel {
    margin-top: 24px;

    background: #111820;

    border: 1px solid #26313c;

    border-radius: 12px;

    padding: 24px;

    display: grid;

    grid-template-columns:
        1fr 1fr 1fr;

    gap: 20px;
}

.hazard {
    font-size: 26px;
    font-weight: bold;
}

.hazard.normal {
    color: #19d36b;
}

.hazard.medium {
    color: #e8a317;
}

.hazard.high {
    color: #e74c3c;
}

.position {
    font-size: 20px;
}

.footer {
    margin-top: 25px;
    color: #687582;
    font-size: 12px;
    text-align: center;
}

@media(max-width: 900px) {

    .sensor-grid {
        grid-template-columns: 1fr 1fr;
    }

    .status-panel {
        grid-template-columns: 1fr;
    }
}

@media(max-width: 600px) {

    .sensor-grid {
        grid-template-columns: 1fr;
    }

    .header {
        padding: 15px;
    }

    .container {
        padding: 15px;
    }
}

</style>

</head>


<body>


<div class="header">

    <div>

        <div class="logo">
            VAJRA
        </div>

        <div class="subtitle">
            Mine Rescue Rover — Receiver Dashboard
        </div>

    </div>


    <div class="connection">

        <div id="statusDot"
             class="status-dot">
        </div>

        <span id="connectionText">
            Connecting...
        </span>

    </div>

</div>


<div class="container">


    <div class="section-title">
        ENVIRONMENTAL SENSORS
    </div>


    <div class="sensor-grid">


        <!-- CH4 -->

        <div id="ch4Card"
             class="card">

            <div class="card-title">
                METHANE — CH₄
            </div>

            <div class="value">

                <span id="ch4">
                    --
                </span>

                <span class="unit">
                    %
                </span>

            </div>

        </div>


        <!-- CO -->

        <div id="coCard"
             class="card">

            <div class="card-title">
                CARBON MONOXIDE — CO
            </div>

            <div class="value">

                <span id="co">
                    --
                </span>

                <span class="unit">
                    ppm
                </span>

            </div>

        </div>


        <!-- H2S -->

        <div id="h2sCard"
             class="card">

            <div class="card-title">
                HYDROGEN SULFIDE — H₂S
            </div>

            <div class="value">

                <span id="h2s">
                    --
                </span>

                <span class="unit">
                    ppm
                </span>

            </div>

        </div>


        <!-- Temperature -->

        <div class="card">

            <div class="card-title">
                TEMPERATURE
            </div>

            <div class="value">

                <span id="temperature">
                    --
                </span>

                <span class="unit">
                    °C
                </span>

            </div>

        </div>


        <!-- Humidity -->

        <div class="card">

            <div class="card-title">
                HUMIDITY
            </div>

            <div class="value">

                <span id="humidity">
                    --
                </span>

                <span class="unit">
                    %
                </span>

            </div>

        </div>


        <!-- Vibration -->

        <div id="vibrationCard"
             class="card">

            <div class="card-title">
                VIBRATION
            </div>

            <div class="value">

                <span id="vibration">
                    --
                </span>

            </div>

        </div>


    </div>


    <!-- SYSTEM STATUS -->

    <div class="status-panel">


        <div>

            <div class="section-title">
                HAZARD STATUS
            </div>

            <div id="hazard"
                 class="hazard">
                WAITING
            </div>

        </div>


        <div>

            <div class="section-title">
                ROVER POSITION
            </div>

            <div class="position">

                X:
                <span id="x">
                    0.00
                </span>

                m

                <br>

                Y:
                <span id="y">
                    0.00
                </span>

                m

            </div>

        </div>


        <div>

            <div class="section-title">
                SYSTEM
            </div>

            <div class="position">
                VAJRA ONLINE
            </div>

        </div>


    </div>


    <div class="footer">

        VAJRA Mine Rescue System • ROS 2 Humble • Gazebo Harmonic

    </div>


</div>


<script>


function setText(id, value)
{
    document.getElementById(id).textContent = value;
}


function setCardStatus(id, status)
{
    const card = document.getElementById(id);

    card.classList.remove(
        "normal",
        "warning",
        "danger"
    );

    if (status === "danger")
    {
        card.classList.add("danger");
    }

    else if (status === "warning")
    {
        card.classList.add("warning");
    }

    else
    {
        card.classList.add("normal");
    }
}


function updateDashboard(data)
{

    setText(
        "ch4",
        Number(data.ch4).toFixed(2)
    );

    setText(
        "co",
        Number(data.co).toFixed(1)
    );

    setText(
        "h2s",
        Number(data.h2s).toFixed(2)
    );

    setText(
        "temperature",
        Number(data.temperature).toFixed(1)
    );

    setText(
        "humidity",
        Number(data.humidity).toFixed(1)
    );

    setText(
        "vibration",
        Number(data.vibration).toFixed(3)
    );

    setText(
        "x",
        Number(data.x).toFixed(2)
    );

    setText(
        "y",
        Number(data.y).toFixed(2)
    );


    // ------------------------------------------------------------
    // HAZARD STATUS
    // ------------------------------------------------------------

    const hazard =
        document.getElementById("hazard");


    hazard.classList.remove(
        "normal",
        "medium",
        "high"
    );


    if (data.hazard_zone === "HIGH")
    {
        hazard.textContent =
            "HIGH HAZARD";

        hazard.classList.add("high");
    }

    else if (data.hazard_zone === "MEDIUM")
    {
        hazard.textContent =
            "MEDIUM HAZARD";

        hazard.classList.add("medium");
    }

    else
    {
        hazard.textContent =
            "NORMAL";

        hazard.classList.add("normal");
    }


    // ------------------------------------------------------------
    // SENSOR CARD STATUS
    // ------------------------------------------------------------

    setCardStatus(
        "ch4Card",
        data.ch4 >= 2.0
            ? "danger"
            : data.ch4 >= 0.8
            ? "warning"
            : "normal"
    );


    setCardStatus(
        "coCard",
        data.co >= 50
            ? "danger"
            : data.co >= 20
            ? "warning"
            : "normal"
    );


    setCardStatus(
        "h2sCard",
        data.h2s >= 8
            ? "danger"
            : data.h2s >= 3
            ? "warning"
            : "normal"
    );


    setCardStatus(
        "vibrationCard",
        data.vibration >= 0.35
            ? "danger"
            : data.vibration >= 0.10
            ? "warning"
            : "normal"
    );
}


async function update()
{

    try
    {

        const response =
            await fetch("/api/data");


        const data =
            await response.json();


        updateDashboard(data);


        document
            .getElementById("statusDot")
            .classList
            .remove("offline");


        document
            .getElementById("statusDot")
            .classList
            .add("online");


        setText(
            "connectionText",
            "CONNECTED"
        );

    }

    catch(error)
    {

        document
            .getElementById("statusDot")
            .classList
            .remove("online");


        document
            .getElementById("statusDot")
            .classList
            .add("offline");


        setText(
            "connectionText",
            "DISCONNECTED"
        );

    }

}


setInterval(
    update,
    500
);


update();


</script>


</body>

</html>
"""


# ================================================================
# HTTP SERVER
# ================================================================

class DashboardHandler(BaseHTTPRequestHandler):

    def do_GET(self):

        if self.path == "/":

            content = HTML.encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "text/html; charset=utf-8"
            )

            self.send_header(
                "Content-Length",
                str(len(content))
            )

            self.end_headers()

            self.wfile.write(content)

            return


        if self.path == "/api/data":

            content = json.dumps(
                dashboard_data
            ).encode("utf-8")

            self.send_response(200)

            self.send_header(
                "Content-Type",
                "application/json"
            )

            self.send_header(
                "Content-Length",
                str(len(content))
            )

            self.end_headers()

            self.wfile.write(content)

            return


        self.send_response(404)

        self.end_headers()


    def log_message(
        self,
        format,
        *args
    ):
        pass


# ================================================================
# ROS NODE
# ================================================================

class VajraDashboard(Node):

    def __init__(self):

        super().__init__(
            "vajra_dashboard"
        )


        self.sensor_sub = self.create_subscription(
            String,
            "/vajra/sensors/json",
            self.sensor_callback,
            10
        )


        self.odom_sub = self.create_subscription(
            Odometry,
            "/odom",
            self.odom_callback,
            10
        )


        self.get_logger().info(
            "VAJRA dashboard ROS node started."
        )


    def sensor_callback(self, msg):

        try:

            data = json.loads(
                msg.data
            )


            sensors = data.get(
                "sensors",
                {}
            )


            hazard = data.get(
                "hazard",
                {}
            )


            dashboard_data["ch4"] = sensors.get(
                "CH4",
                0.0
            )


            dashboard_data["co"] = sensors.get(
                "CO",
                0.0
            )


            dashboard_data["h2s"] = sensors.get(
                "H2S",
                0.0
            )


            dashboard_data["temperature"] = sensors.get(
                "temperature",
                0.0
            )


            dashboard_data["humidity"] = sensors.get(
                "humidity",
                0.0
            )


            dashboard_data["vibration"] = sensors.get(
                "vibration",
                0.0
            )


            dashboard_data["hazard_zone"] = hazard.get(
                "zone",
                "NORMAL"
            )


            dashboard_data["connected"] = True


        except Exception as error:

            self.get_logger().error(
                f"JSON error: {error}"
            )


    def odom_callback(self, msg):

        dashboard_data["x"] = (
            msg.pose.pose.position.x
        )

        dashboard_data["y"] = (
            msg.pose.pose.position.y
        )


# ================================================================
# HTTP SERVER THREAD
# ================================================================

def start_http_server():

    server = HTTPServer(
        (
            "0.0.0.0",
            8080
        ),
        DashboardHandler
    )

    print(
        ""
    )

    print(
        "================================================"
    )

    print(
        " VAJRA DASHBOARD"
    )

    print(
        "================================================"
    )

    print(
        " Open your browser:"
    )

    print(
        " http://localhost:8080"
    )

    print(
        "================================================"
    )

    print(
        ""
    )

    server.serve_forever()


# ================================================================
# MAIN
# ================================================================

def main(args=None):

    rclpy.init(
        args=args
    )


    node = VajraDashboard()


    server_thread = threading.Thread(
        target=start_http_server,
        daemon=True
    )

    server_thread.start()


    try:

        rclpy.spin(
            node
        )

    except KeyboardInterrupt:

        pass

    finally:

        node.destroy_node()

        rclpy.shutdown()


if __name__ == "__main__":

    main()
