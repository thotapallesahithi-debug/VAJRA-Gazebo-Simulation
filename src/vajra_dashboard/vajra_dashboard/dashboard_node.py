#!/usr/bin/env python3

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import cv2
import rclpy
from rclpy.node import Node
from cv_bridge import CvBridge
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Image
from std_msgs.msg import Float32, Bool


HOST = "0.0.0.0"
PORT = 8080
dashboard = None


class VajraDashboard(Node):

    def __init__(self):
        super().__init__("vajra_dashboard")

        self.bridge = CvBridge()
        self.lock = threading.Lock()

        self.left_frame = None
        self.right_frame = None

        self.sensors = {
            "ch4": 0.0,
            "co": 0.0,
            "h2s": 0.0,
            "temperature": 0.0,
            "humidity": 0.0,
            "vibration": False,
        }

        self.last_command = {
            "linear": 0.0,
            "angular": 0.0,
        }

        self.cmd_pub = self.create_publisher(Twist, "/model/vajra/cmd_vel", 10)

        self.create_subscription(Image, "/camera/left/image_raw", self.left_camera, 10)
        self.create_subscription(Image, "/camera/right/image_raw", self.right_camera, 10)

        self.create_subscription(Float32, "/vajra/sensors/ch4", self.ch4, 10)
        self.create_subscription(Float32, "/vajra/sensors/co", self.co, 10)
        self.create_subscription(Float32, "/vajra/sensors/h2s", self.h2s, 10)
        self.create_subscription(Float32, "/vajra/sensors/temperature", self.temperature, 10)
        self.create_subscription(Float32, "/vajra/sensors/humidity", self.humidity, 10)
        self.create_subscription(Bool, "/vajra/sensors/vibration", self.vibration, 10)

        self.get_logger().info("VAJRA dashboard node started")

    def left_camera(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            with self.lock:
                self.left_frame = frame.copy()
        except Exception as e:
            self.get_logger().error(f"Left camera: {e}")

    def right_camera(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, "bgr8")
            with self.lock:
                self.right_frame = frame.copy()
        except Exception as e:
            self.get_logger().error(f"Right camera: {e}")

    def ch4(self, msg):
        with self.lock:
            self.sensors["ch4"] = float(msg.data)

    def co(self, msg):
        with self.lock:
            self.sensors["co"] = float(msg.data)

    def h2s(self, msg):
        with self.lock:
            self.sensors["h2s"] = float(msg.data)

    def temperature(self, msg):
        with self.lock:
            self.sensors["temperature"] = float(msg.data)

    def humidity(self, msg):
        with self.lock:
            self.sensors["humidity"] = float(msg.data)

    def vibration(self, msg):
        with self.lock:
            self.sensors["vibration"] = bool(msg.data)

    def command(self, linear, angular):
        msg = Twist()
        msg.linear.x = float(linear)
        msg.angular.z = float(angular)
        self.cmd_pub.publish(msg)

        with self.lock:
            self.last_command["linear"] = float(linear)
            self.last_command["angular"] = float(angular)

    def state(self):
        with self.lock:
            return {
                "sensors": dict(self.sensors),
                "command": dict(self.last_command),
                "left_camera": self.left_frame is not None,
                "right_camera": self.right_frame is not None,
                "time": time.time(),
            }


HTML = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>VAJRA Dashboard</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#090d12;color:#eee;font-family:Arial,sans-serif}
header{padding:18px 24px;background:#121820;border-bottom:2px solid #28323d;display:flex;justify-content:space-between;align-items:center}
.logo{font-size:30px;font-weight:800;letter-spacing:4px;color:#ffc400}
.sub{font-size:13px;color:#8995a3;margin-top:4px}
.online{color:#4ade80;font-weight:bold}
main{max-width:1500px;margin:auto;padding:18px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.panel{background:#121820;border:1px solid #28323d;border-radius:10px;overflow:hidden}
.title{padding:12px 16px;color:#ffc400;font-weight:bold;border-bottom:1px solid #28323d}
.camera{width:100%;aspect-ratio:16/9;object-fit:contain;background:#000;display:block}
.map{height:260px;background-color:#080c11;background-image:linear-gradient(#ffffff08 1px,transparent 1px),linear-gradient(90deg,#ffffff08 1px,transparent 1px);background-size:40px 40px;display:flex;align-items:center;justify-content:center;color:#66717d;font-size:18px}
.mapbox{margin-top:16px}
.sensors{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}
.sensor{padding:16px;background:#121820;border:1px solid #28323d;border-radius:10px}
.name{color:#8995a3;font-size:13px;margin-bottom:8px}
.value{font-size:27px;font-weight:bold}
.unit{color:#8995a3;font-size:13px}
.safe{color:#4ade80}
.warn{color:#facc15}
.controls{margin-top:16px;padding-bottom:20px}
.buttons{display:grid;grid-template-columns:80px 80px 80px;gap:10px;justify-content:center;padding:20px}
button{height:60px;background:#1d2732;color:#fff;border:1px solid #394553;border-radius:8px;font-size:22px;font-weight:bold;cursor:pointer}
button:hover{background:#2b3744}
.stop{background:#8b2222}
.status{text-align:center;color:#8995a3;font-size:13px}
@media(max-width:800px){.grid2{grid-template-columns:1fr}.sensors{grid-template-columns:repeat(2,1fr)}}
@media(max-width:500px){.sensors{grid-template-columns:1fr}}
</style>
</head>

<body>

<header>
<div>
<div class="logo">VAJRA</div>
<div class="sub">Underground Mine Rescue Rover</div>
</div>
<div class="online" id="online">● ONLINE</div>
</header>

<main>

<div class="grid2">

<div class="panel">
<div class="title">LEFT STEREO CAMERA</div>
<img class="camera" src="/left.mjpg">
</div>

<div class="panel">
<div class="title">RIGHT STEREO CAMERA</div>
<img class="camera" src="/right.mjpg">
</div>

</div>


</div>

<div class="sensors">

<div class="sensor">
<div class="name">CH₄ — METHANE</div>
<span id="ch4" class="value safe">0.0</span>
<span class="unit">ppm</span>
</div>

<div class="sensor">
<div class="name">CO — CARBON MONOXIDE</div>
<span id="co" class="value safe">0.0</span>
<span class="unit">ppm</span>
</div>

<div class="sensor">
<div class="name">H₂S — HYDROGEN SULFIDE</div>
<span id="h2s" class="value safe">0.0</span>
<span class="unit">ppm</span>
</div>

<div class="sensor">
<div class="name">TEMPERATURE</div>
<span id="temperature" class="value safe">0.0</span>
<span class="unit">°C</span>
</div>

<div class="sensor">
<div class="name">HUMIDITY</div>
<span id="humidity" class="value safe">0.0</span>
<span class="unit">%</span>
</div>

<div class="sensor">
<div class="name">VIBRATION</div>
<span id="vibration" class="value safe">NORMAL</span>
</div>

</div>

<div class="panel controls">
<div class="title">ROVER CONTROL</div>

<div class="buttons">

<div></div>
<button onclick="move(1,0)">▲</button>
<div></div>

<button onclick="move(0,1)">◀</button>
<button class="stop" onclick="move(0,0)">■</button>
<button onclick="move(0,-1)">▶</button>

<div></div>
<button onclick="move(-1,0)">▼</button>
<div></div>

</div>

<div class="status" id="status">Rover stopped</div>
</div>

</main>

<script>

async function update(){

    try{

        const r=await fetch("/state");
        const d=await r.json();
        const s=d.sensors;

        const ch4=document.getElementById("ch4");
        const co=document.getElementById("co");
        const h2s=document.getElementById("h2s");
        const temperature=document.getElementById("temperature");
        const humidity=document.getElementById("humidity");

        ch4.textContent=s.ch4.toFixed(1);
        co.textContent=s.co.toFixed(1);
        h2s.textContent=s.h2s.toFixed(2);
        temperature.textContent=s.temperature.toFixed(1);
        humidity.textContent=s.humidity.toFixed(1);

        // -------------------------
        // GAS HAZARD STATUS
        // -------------------------

        setGasStatus(ch4, s.ch4, 50, 80);
        setGasStatus(co, s.co, 10, 25);
        setGasStatus(h2s, s.h2s, 2, 8);

        temperature.className =
            s.temperature >= 35
            ? "value warn"
            : "value safe";

        humidity.className =
            s.humidity >= 85
            ? "value warn"
            : "value safe";

        const v=document.getElementById("vibration");

        if(s.vibration){
            v.textContent="DETECTED";
            v.className="value warn";
        }else{
            v.textContent="NORMAL";
            v.className="value safe";
        }

        document.getElementById("online").textContent="● ONLINE";

    }catch(e){

        document.getElementById("online").textContent="● CONNECTION ERROR";

    }

}

function setGasStatus(element, value, warning, critical){

    if(value >= critical){
        element.className="value";
        element.style.color="#ff4444";
    }
    else if(value >= warning){
        element.className="value warn";
        element.style.color="#facc15";
    }
    else{
        element.className="value safe";
        element.style.color="#4ade80";
    }
}

async function move(linear,angular){

    await fetch("/cmd?linear="+linear+"&angular="+angular);

    document.getElementById("status").textContent=
        "Command: linear "+linear+" | angular "+angular;

}

setInterval(update,500);
update();

</script>

</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        pass

    def send_data(self, data, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):

        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self.send_data(HTML.encode(), "text/html; charset=utf-8")
            return

        if path == "/state":
            data = json.dumps(dashboard.state()).encode()
            self.send_data(data, "application/json")
            return

        if path == "/cmd":
            q = parse_qs(parsed.query)

            try:
                linear = float(q.get("linear", ["0"])[0])
                angular = float(q.get("angular", ["0"])[0])

                linear = max(-2.0, min(2.0, linear))
                angular = max(-2.0, min(2.0, angular))

                dashboard.command(linear, angular)

                data = json.dumps({
                    "ok": True,
                    "linear": linear,
                    "angular": angular
                }).encode()

                self.send_data(data, "application/json")

            except ValueError:
                self.send_response(400)
                self.end_headers()

            return

        if path == "/left.mjpg":
            self.camera_stream("left")
            return

        if path == "/right.mjpg":
            self.camera_stream("right")
            return

        self.send_response(404)
        self.end_headers()

    def camera_stream(self, side):

        self.send_response(200)
        self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        while rclpy.ok():

            try:

                with dashboard.lock:

                    if side == "left":
                        frame = dashboard.left_frame
                    else:
                        frame = dashboard.right_frame

                    if frame is not None:
                        frame = frame.copy()

                if frame is None:
                    time.sleep(0.1)
                    continue

                result = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])

                if not result[0]:
                    continue

                encoded = result[1].tobytes()

                self.wfile.write(b"--frame\r\n")
                self.wfile.write(b"Content-Type: image/jpeg\r\n\r\n")
                self.wfile.write(encoded)
                self.wfile.write(b"\r\n")

                time.sleep(0.05)

            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                break

            except Exception:
                break


def start_server():

    server = ThreadingHTTPServer((HOST, PORT), Handler)

    print(f"VAJRA dashboard available at http://localhost:{PORT}")

    try:
        server.serve_forever()
    finally:
        server.server_close()


def main(args=None):

    global dashboard

    rclpy.init(args=args)

    dashboard = VajraDashboard()

    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()

    try:
        rclpy.spin(dashboard)
    except KeyboardInterrupt:
        pass
    finally:
        dashboard.destroy_node()

        if rclpy.ok():
            rclpy.shutdown()


if __name__ == "__main__":
    main()
