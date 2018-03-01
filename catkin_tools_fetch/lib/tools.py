"""Module that contains tools class.

Attributes:
    log (logging.Log): current logger
"""
import subprocess
import logging
import re

from termcolor import colored

log = logging.getLogger('deps')


class GitBridge(object):
    """A bridge to git and its cmd functions."""

    STATUS_CMD = "git status --porcelain --branch"
    PULL_CMD_MASK = "git pull origin {branch}"

    CHECK_CMD_MASK = "git ls-remote {url}"
    CLONE_CMD_MASK = "git clone --recursive --branch {branch} {url} {path}"

    BRANCH_REGEX = re.compile("## (?!HEAD)([\w\-_]+)")

    EXISTS_TAG = colored("[ALREADY EXISTS]", "green")
    CLONED_TAG = colored("[CLONED]", "green") + " [BRANCH: '{branch}']"
    ERROR_TAG = colored("[ERROR]", "red")

    @staticmethod
    def status(repo_folder):
        """Get output from `git pull --porcelain --branch` for a repo."""
        output = subprocess.check_output(GitBridge.STATUS_CMD,
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         cwd=repo_folder)
        branch = GitBridge.get_branch_name(output)
        # when no changes - output is single line with name of branch
        has_changes = False
        if output.count(b'\n') > 1:
            has_changes = True
        return output, branch, has_changes

    @staticmethod
    def pull(repo_folder, branch):
        """Pull the repo's branch and return the output."""
        git_pull_cmd = GitBridge.PULL_CMD_MASK.format(branch=branch)
        output = subprocess.check_output(git_pull_cmd,
                                         stderr=subprocess.STDOUT,
                                         shell=True,
                                         cwd=repo_folder)
        return output

    @staticmethod
    def clone(name, url, clone_path, branch="master"):
        """Clone the repo from url into clone_path."""
        cmd_clone = GitBridge.CLONE_CMD_MASK.format(url=url,
                                                    path=clone_path,
                                                    branch=branch)
        log.debug(" clone url: %s", cmd_clone)
        try:
            subprocess.check_output(cmd_clone,
                                    stderr=subprocess.STDOUT,
                                    shell=True)
            return name, GitBridge.CLONED_TAG.format(branch=branch)
        except subprocess.CalledProcessError as e:
            out_str = e.output.decode("utf8")
            if "already exists" in out_str:
                return name, GitBridge.EXISTS_TAG
            log.critical("Git error: %s", out_str)
            return name, GitBridge.ERROR_TAG

    @staticmethod
    def repository_exists(dependency):
        """Check if repository exists.

        Uses `git ls-remote` to check if the repository exists.

        Args:
            url (str): Url to check.

        Returns:
            bool: True if exists, False otherwise
        """
        from os import environ
        urls = []
        if dependency.url:
            urls.append(dependency.url)
        else:
            urls.extend(dependency.default_urls)
        log.debug(" Checking urls: %s", urls)
        # Disable git interactive promts. Just fail silently.
        new_env = environ
        new_env["GIT_TERMINAL_PROMPT"] = "0"
        # Check all urls.
        for url in urls:
            git_cmd = GitBridge.CHECK_CMD_MASK.format(url=url)
            try:
                log.debug(" Searching for package '%s' under url '%s'",
                          dependency.name, url)
                subprocess.check_call(git_cmd,
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE,
                                      shell=True,
                                      env=new_env)
                # Update the working url if needed.
                dependency.url = url
                return dependency, True
            except subprocess.CalledProcessError as e:
                log.debug(
                    'Package "%s" was not found under: "%s" with error: %s',
                    dependency.name, url, e)
        # If we reached here we failed to find the dependency.
        return dependency, False

    @staticmethod
    def get_branch_name(git_status_output):
        """Parse branch name from the output of git status."""
        try:
            output = git_status_output.decode("utf-8")
        except AttributeError:
            output = git_status_output
        match = GitBridge.BRANCH_REGEX.match(output)
        if not match:
            return None
        branch = match.groups()[0]
        return branch


class Tools(object):
    """Some useful tools.

    Attributes:
        default_ros_packages (str[]): default packages for ROS
    """

    PACKAGE_TAG = '{package}'

    @staticmethod
    def prepare_default_urls(default_urls):
        """Insert {package} statement into the URL.

        Args:
            default_urls (str): Default urls, single string, comma separated.
                Each can be one of the following styles:
                - git@<path>
                - https://<path>

        Returns:
            set(str): Urls with {package} tag placed inside of them.
        """
        all_urls = default_urls.split(",")
        prepared_urls = set()
        for url in all_urls:
            prepared_url = Tools.prepare_default_url(url)
            if prepared_url:
                prepared_urls.add(prepared_url)
                log.debug("Prepared url: '%s'", prepared_url)
        return prepared_urls

    @staticmethod
    def prepare_default_url(url):
        """Insert {package} statement into the URL.

        Args:
            url (str): Default url, single string.
                Can be one of the following styles:
                - git@<path>
                - https://<path>

        Returns:
            str: Url with {package} tag placed inside of it.
        """
        if Tools.PACKAGE_TAG in url:
            return url
        if not url.endswith('/') and not url.endswith('.git'):
            url += '/'
        if url.startswith('git'):
            if not url.endswith('.git'):
                return url + Tools.PACKAGE_TAG + '.git'
            if Tools.PACKAGE_TAG not in url:
                log.error("Skipping url with no tag place:'%s'", url)
                return None
        if url.startswith('http'):
            return url + Tools.PACKAGE_TAG

    @staticmethod
    def populate_urls_with_name(urls, pkg_name):
        """Populate all urls with the package name."""
        populated_urls = []
        for url in urls:
            if Tools.PACKAGE_TAG not in url:
                log.error("Url '%s' is malformed. Should contain tag: '%s'",
                          url, Tools.PACKAGE_TAG)
                continue
            populated_urls.append(url.format(package=pkg_name))
        return populated_urls

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
            try:
                str_output = output.decode("utf-8")
            except AttributeError:
                str_output = output
            output = str_output.splitlines()
            for pkg_line in output:
                pkg_line_list = pkg_line.split(' ')
                pkg_name = pkg_line_list[0]
                pkg_path = pkg_line_list[1]
                if not pkg_path.startswith('/home/'):
                    pkg_list.append(pkg_name)
            log.info(" [ROS]: Ignoring %s packages.", len(pkg_list))
            return set(pkg_list)
        except subprocess.CalledProcessError:
            log.info(" [ROS]: Not found. Ignoring pre-defined ROS packages.")
            return set(Tools.default_ros_packages)

    @staticmethod
    def decorate(pkg_name, max_width=25):
        """Decorate a package name."""
        decorated = "[" + pkg_name + "]"
        return decorated.ljust(max_width)

    @staticmethod
    def update_deps_dict(base_dict, new_dict):
        """We don't want to overwrite any value, but check for conflicts."""
        for dep_name in new_dict.keys():
            dep = new_dict[dep_name]
            if dep_name in base_dict:
                old_dep = base_dict[dep_name]
                if not old_dep.branch or old_dep.branch == 'None':
                    old_dep.branch = dep.branch
                if dep.branch \
                        and dep.branch != 'None' \
                        and dep.branch != old_dep.branch:
                    log.critical(
                        " Dependency '%s': conflicting branches: '%s' vs '%s'",
                        dep_name, dep.branch, old_dep.branch)
                    return None
                if dep.url != old_dep.url:
                    log.critical(
                        " Dependency '%s': conflicting urls: '%s' vs '%s'",
                        dep_name, dep.url, old_dep.url)
                    return None
            else:
                base_dict[dep_name] = dep
        return base_dict

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
