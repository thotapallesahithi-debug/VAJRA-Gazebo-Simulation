cmake_minimum_required(VERSION 3.8)

project(vajra_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY
    urdf
    launch
    worlds
    config
  DESTINATION
    share/${PROJECT_NAME}
)

install(
  PROGRAMS
    vajra_description/odom_to_tf.py
    vajra_description/stereo_camera_info.py
    vajra_description/stereo_camera_simulator.py
  DESTINATION
    lib/${PROJECT_NAME}
)

ament_package()
