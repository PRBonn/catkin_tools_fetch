"""Module that contains tools class.

Attributes:
    log (logging.Log): current logger
"""
import subprocess
import logging

log = logging.getLogger('fetch')


class Tools(object):
    """Some useful tools.

    Attributes:
        default_ros_packages (str[]): default packages for ROS
    """

    @staticmethod
    def prepare_default_url(default_url):
        """Insert {package} statement into the URL.

        Args:
            default_url (str): Defatul url. Can be one of the following styles:
                - git@<path>
                - https://<path>

        Returns:
            str: Url with {package} tag placed inside of it.
        """
        package_tag = '{package}'
        if len(default_url) == 0:
            return default_url
        if not default_url.endswith('/'):
            default_url += '/'
        if default_url.startswith('git'):
            return default_url + package_tag + '.git'
        if default_url.startswith('http'):
            return default_url + package_tag
        return default_url

    @staticmethod
    def list_all_ros_pkgs():
        """List all available ROS packages.

        Returns:
            str[]: list of ROS package names
        """
        log.info(" Avoid fetching ROS packages.")
        log.info(" [ROS]: Searching all packages.")
        get_ros_packages_command = 'rospack list'
        pkg_list = []
        try:
            output = subprocess.check_output(
                get_ros_packages_command,
                stderr=subprocess.STDOUT,
                shell=True)
            output = str(output)
            output = output.splitlines()
            for pkg_line in output:
                pkg_list.append(pkg_line.split(' ')[0])
            log.info(" [ROS]: Ignoring %s packages.", len(pkg_list))
            return set(pkg_list)
        except subprocess.CalledProcessError:
            log.info(" [ROS]: Not found. Ignoring pre-defined ROS packages.")
            return set(Tools.default_ros_packages)

    @staticmethod
    def decorate(pkg_name):
        """Decorate a package name."""
        return "[" + pkg_name + "]"

    default_ros_packages = ['actionlib',
                            'actionlib_msgs',
                            'actionlib_tutorials',
                            'angles',
                            'bond',
                            'bondcpp',
                            'bondpy',
                            'camera_calibration',
                            'camera_calibration_parsers',
                            'camera_info_manager',
                            'catkin',
                            'class_loader',
                            'cmake_modules',
                            'collada_parser',
                            'collada_urdf',
                            'compressed_depth_image_transport',
                            'compressed_image_transport',
                            'control_msgs',
                            'control_toolbox',
                            'controller_interface',
                            'controller_manager',
                            'controller_manager_msgs',
                            'cpp_common',
                            'cv_bridge',
                            'depth_image_proc',
                            'diagnostic_aggregator',
                            'diagnostic_analysis',
                            'diagnostic_common_diagnostics',
                            'diagnostic_msgs',
                            'diagnostic_updater',
                            'driver_base',
                            'dynamic_reconfigure',
                            'eigen_conversions',
                            'eigen_stl_containers',
                            'filters',
                            'gazebo_msgs',
                            'gazebo_plugins',
                            'gazebo_ros',
                            'gazebo_ros_control',
                            'gencpp',
                            'genlisp',
                            'genmsg',
                            'genpy',
                            'geometric_shapes',
                            'geometry_msgs',
                            'hardware_interface',
                            'image_geometry',
                            'image_proc',
                            'image_rotate',
                            'image_transport',
                            'image_view',
                            'interactive_marker_tutorials',
                            'interactive_markers',
                            'joint_limits_interface',
                            'joint_state_publisher',
                            'kdl_conversions',
                            'kdl_parser',
                            'laser_assembler',
                            'laser_filters',
                            'laser_geometry',
                            'librviz_tutorial',
                            'map_msgs',
                            'media_export',
                            'message_filters',
                            'message_generation',
                            'message_runtime',
                            'mk',
                            'nav_msgs',
                            'nodelet',
                            'nodelet_topic_tools',
                            'nodelet_tutorial_math',
                            'octomap',
                            'opencv_apps',
                            'openni2_camera',
                            'openni2_launch',
                            'orocos_kdl',
                            'pcl_conversions',
                            'pcl_msgs',
                            'pcl_ros',
                            'pluginlib',
                            'pluginlib_tutorials',
                            'pointcloud_to_laserscan',
                            'polled_camera',
                            'pr2_description',
                            'python_orocos_kdl',
                            'python_qt_binding',
                            'qt_dotgraph',
                            'qt_gui',
                            'qt_gui_cpp',
                            'qt_gui_py_common',
                            'random_numbers',
                            'realtime_tools',
                            'resource_retriever',
                            'rgbd_launch',
                            'robot_state_publisher',
                            'rosbag',
                            'rosbag_migration_rule',
                            'rosbag_storage',
                            'rosbash',
                            'rosboost_cfg',
                            'rosbuild',
                            'rosclean',
                            'rosconsole',
                            'rosconsole_bridge',
                            'roscpp',
                            'roscpp_serialization',
                            'roscpp_traits',
                            'roscpp_tutorials',
                            'roscreate',
                            'rosgraph',
                            'rosgraph_msgs',
                            'roslang',
                            'roslaunch',
                            'roslib',
                            'roslint',
                            'roslisp',
                            'roslz4',
                            'rosmake',
                            'rosmaster',
                            'rosmsg',
                            'rosnode',
                            'rosout',
                            'rospack',
                            'rosparam',
                            'rospy',
                            'rospy_tutorials',
                            'rosserial_arduino',
                            'rosserial_client',
                            'rosserial_msgs',
                            'rosserial_python',
                            'rosservice',
                            'rostest',
                            'rostime',
                            'rostopic',
                            'rosunit',
                            'roswtf',
                            'rqt_action',
                            'rqt_bag',
                            'rqt_bag_plugins',
                            'rqt_console',
                            'rqt_dep',
                            'rqt_graph',
                            'rqt_gui',
                            'rqt_gui_cpp',
                            'rqt_gui_py',
                            'rqt_image_view',
                            'rqt_launch',
                            'rqt_logger_level',
                            'rqt_moveit',
                            'rqt_msg',
                            'rqt_nav_view',
                            'rqt_plot',
                            'rqt_pose_view',
                            'rqt_publisher',
                            'rqt_py_common',
                            'rqt_py_console',
                            'rqt_reconfigure',
                            'rqt_robot_dashboard',
                            'rqt_robot_monitor',
                            'rqt_robot_steering',
                            'rqt_runtime_monitor',
                            'rqt_rviz',
                            'rqt_service_caller',
                            'rqt_shell',
                            'rqt_srv',
                            'rqt_tf_tree',
                            'rqt_top',
                            'rqt_topic',
                            'rqt_web',
                            'rviz',
                            'rviz_plugin_tutorials',
                            'rviz_python_tutorial',
                            'self_test',
                            'sensor_msgs',
                            'shape_msgs',
                            'smach',
                            'smach_msgs',
                            'smach_ros',
                            'smclib',
                            'stage',
                            'stage_ros',
                            'std_msgs',
                            'std_srvs',
                            'stereo_image_proc',
                            'stereo_msgs',
                            'tf',
                            'tf2',
                            'tf2_geometry_msgs',
                            'tf2_kdl',
                            'tf2_msgs',
                            'tf2_py',
                            'tf2_ros',
                            'tf2_sensor_msgs',
                            'tf_conversions',
                            'theora_image_transport',
                            'topic_tools',
                            'trajectory_msgs',
                            'transmission_interface',
                            'turtle_actionlib',
                            'turtle_tf',
                            'turtle_tf2',
                            'turtlesim',
                            'urdf',
                            'urdf_parser_plugin',
                            'urdf_tutorial',
                            'urdfdom_py',
                            'velodyne_driver',
                            'velodyne_msgs',
                            'velodyne_pointcloud',
                            'visualization_marker_tutorials',
                            'visualization_msgs',
                            'xacro',
                            'xmlrpcpp']
