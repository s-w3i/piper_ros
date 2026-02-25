from moveit_configs_utils import MoveItConfigsBuilder

from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
)
from moveit_configs_utils.launch_utils import (
    add_debuggable_node,
    DeclareBooleanLaunchArg,
)
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("piper", package_name="piper_with_gripper_moveit").to_moveit_configs()

    ld = LaunchDescription()
    # Build a complete joint state stream for MoveIt:
    # - consumes raw /joint_states
    # - publishes /joint_states_complete
    # - synthesizes joint8 from joint7 (opposite motion)
    my_generate_joint_state_augmenter_launch(ld, moveit_config)

    # 启动move_group
    my_generate_move_group_launch(ld, moveit_config)
    # 启动rviz
    my_generate_moveit_rviz_launch(ld, moveit_config)

    return ld


def my_generate_joint_state_augmenter_launch(ld, moveit_config):
    ld.add_action(
        Node(
            package="joint_state_publisher",
            executable="joint_state_publisher",
            name="joint_state_augmenter",
            output="screen",
            parameters=[
                moveit_config.robot_description,
                {
                    "rate": 200,
                    "source_list": ["/joint_states"],
                    "use_mimic_tags": True,
                    "dependent_joints.joint8.parent": "joint7",
                    "dependent_joints.joint8.factor": -1.0,
                    "dependent_joints.joint8.offset": 0.0,
                    "use_sim_time": True,
                },
            ],
            remappings=[("joint_states", "/joint_states_complete")],
        )
    )
    return ld


def my_generate_move_group_launch(ld, moveit_config):

    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(
        DeclareBooleanLaunchArg("allow_trajectory_execution", default_value=True)
    )
    ld.add_action(
        DeclareBooleanLaunchArg("publish_monitored_planning_scene", default_value=True)
    )
    # load non-default MoveGroup capabilities (space separated)
    ld.add_action(DeclareLaunchArgument("capabilities", default_value=""))
    # inhibit these default MoveGroup capabilities (space separated)
    ld.add_action(DeclareLaunchArgument("disable_capabilities", default_value=""))

    # do not copy dynamics information from /joint_states to internal robot monitoring
    # default to false, because almost nothing in move_group relies on this information
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
            default_value="3.0",
            description="Maximum distance (m) used by MoveIt occupancy mapping",
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
        # Note: Wrapping the following values is necessary so that the parameter value can be the empty string
        "capabilities": ParameterValue(
            LaunchConfiguration("capabilities"), value_type=str
        ),
        "disable_capabilities": ParameterValue(
            LaunchConfiguration("disable_capabilities"), value_type=str
        ),
        # Publish the planning scene of the physical robot so that rviz plugin can know actual robot
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
            "point_subsample": 1,
            "padding_offset": 0.02,
            "padding_scale": 1.0,
            "max_update_rate": 5.0,
            "filtered_cloud_topic": LaunchConfiguration("dc1_filtered_cloud_topic"),
        },
        "octomap_frame": LaunchConfiguration("octomap_frame"),
        "octomap_resolution": ParameterValue(
            LaunchConfiguration("octomap_resolution"), value_type=float
        ),
    }

    move_group_params = [
        moveit_config.to_dict(),
        move_group_configuration,
        sensor_configuration,
    ]
    move_group_params.append({"use_sim_time": True})

    add_debuggable_node(
        ld,
        package="moveit_ros_move_group",
        executable="move_group",
        commands_file=str(moveit_config.package_path / "launch" / "gdb_settings.gdb"),
        output="screen",
        parameters=move_group_params,
        remappings=[("joint_states", "/joint_states_complete")],
        extra_debug_args=["--debug"],
        # Set the display variable, in case OpenGL code is used internally
        additional_env={"DISPLAY": ":0"},
    )
    return ld

def my_generate_moveit_rviz_launch(ld, moveit_config):
    """Launch file for rviz"""

    ld.add_action(DeclareBooleanLaunchArg("debug", default_value=False))
    ld.add_action(
        DeclareLaunchArgument(
            "rviz_config",
            default_value=str(moveit_config.package_path / "config/moveit.rviz"),
        )
    )

    rviz_parameters = [
        moveit_config.planning_pipelines,
        moveit_config.robot_description_kinematics,
    ]
    rviz_parameters.append({"use_sim_time": True})

    add_debuggable_node(
        ld,
        package="rviz2",
        executable="rviz2",
        output="log",
        respawn=False,
        arguments=["-d", LaunchConfiguration("rviz_config")],
        parameters=rviz_parameters,
    )

    return ld
