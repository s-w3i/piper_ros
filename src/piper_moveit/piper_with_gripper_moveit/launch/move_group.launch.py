from moveit_configs_utils import MoveItConfigsBuilder
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.parameter_descriptions import ParameterValue
from moveit_configs_utils.launch_utils import add_debuggable_node, DeclareBooleanLaunchArg


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("piper", package_name="piper_with_gripper_moveit").to_moveit_configs()
    ld = LaunchDescription()

    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(
        DeclareBooleanLaunchArg("allow_trajectory_execution", default_value=True)
    )
    ld.add_action(
        DeclareBooleanLaunchArg("publish_monitored_planning_scene", default_value=True)
    )
    ld.add_action(DeclareLaunchArgument("capabilities", default_value=""))
    ld.add_action(DeclareLaunchArgument("disable_capabilities", default_value=""))
    ld.add_action(DeclareBooleanLaunchArg("monitor_dynamics", default_value=False))

    ld.add_action(
        DeclareLaunchArgument(
            "dc1_point_cloud_topic",
            default_value="/camera/depth/points",
            description="PointCloud2 topic from DaBai DC1 for MoveIt occupancy mapping",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "dc1_filtered_cloud_topic",
            default_value="/moveit/filtered_cloud",
            description="Filtered cloud output topic published by MoveIt",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "dc1_max_range",
            default_value="2.0",
            description="Maximum distance (m) used by MoveIt occupancy mapping",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "dc1_point_subsample",
            default_value="8",
            description="Use every Nth point from the input cloud to reduce octomap load",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "dc1_max_update_rate",
            default_value="10.0",
            description="Maximum octomap updater frequency in Hz",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "octomap_frame",
            default_value="base_link",
            description="Planning frame used by MoveIt octomap",
        )
    )
    ld.add_action(
        DeclareLaunchArgument(
            "octomap_resolution",
            default_value="0.02",
            description="Octomap voxel resolution in meters",
        )
    )

    should_publish = LaunchConfiguration("publish_monitored_planning_scene")
    move_group_configuration = {
        "publish_robot_description_semantic": True,
        "allow_trajectory_execution": LaunchConfiguration("allow_trajectory_execution"),
        "capabilities": ParameterValue(
            LaunchConfiguration("capabilities"), value_type=str
        ),
        "disable_capabilities": ParameterValue(
            LaunchConfiguration("disable_capabilities"), value_type=str
        ),
        "publish_planning_scene": should_publish,
        "publish_geometry_updates": should_publish,
        "publish_state_updates": should_publish,
        "publish_transforms_updates": should_publish,
        "monitor_dynamics": False,
    }

    sensor_configuration = {
        "sensors": ["dabai_dc1_pointcloud"],
        "dabai_dc1_pointcloud": {
            "sensor_plugin": "occupancy_map_monitor/PointCloudOctomapUpdater",
            "point_cloud_topic": LaunchConfiguration("dc1_point_cloud_topic"),
            "max_range": ParameterValue(
                LaunchConfiguration("dc1_max_range"), value_type=float
            ),
            "point_subsample": ParameterValue(
                LaunchConfiguration("dc1_point_subsample"), value_type=int
            ),
            "padding_offset": 0.02,
            "padding_scale": 1.0,
            "max_update_rate": ParameterValue(
                LaunchConfiguration("dc1_max_update_rate"), value_type=float
            ),
            "filtered_cloud_topic": LaunchConfiguration("dc1_filtered_cloud_topic"),
        },
        "octomap_frame": LaunchConfiguration("octomap_frame"),
        "octomap_resolution": ParameterValue(
            LaunchConfiguration("octomap_resolution"), value_type=float
        ),
    }

    add_debuggable_node(
        ld,
        package="moveit_ros_move_group",
        executable="move_group",
        commands_file=str(moveit_config.package_path / "launch" / "gdb_settings.gdb"),
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            move_group_configuration,
            sensor_configuration,
        ],
        remappings=[("joint_states", "/joint_states_complete")],
        extra_debug_args=["--debug"],
        additional_env={"DISPLAY": ":0"},
    )
    return ld
