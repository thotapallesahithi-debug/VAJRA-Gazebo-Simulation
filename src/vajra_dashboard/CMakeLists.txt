cmake_minimum_required(VERSION 3.8)

project(vajra_dashboard)

find_package(ament_cmake REQUIRED)

install(
  PROGRAMS
    vajra_dashboard/dashboard_node.py
    vajra_dashboard/sensor_simulator.py
  DESTINATION
    lib/${PROJECT_NAME}
)

ament_package()
