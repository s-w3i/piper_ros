from moveit_configs_utils import MoveItConfigsBuilder
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    moveit_config = MoveItConfigsBuilder("piper", package_name="piper_with_gripper_moveit").to_moveit_configs()
    ld = LaunchDescription()

    ld.add_action(DeclareLaunchArgument("publish_frequency", default_value="30.0"))

    # Build a complete joint stream that includes joint8 (mirrored from joint7),
    # then feed that to robot_state_publisher.
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
                    "publish_default_positions": False,
                    "publish_default_velocities": False,
                    "publish_default_efforts": False,
                    "dependent_joints.joint8.parent": "joint7",
                    "dependent_joints.joint8.factor": -1.0,
                    "dependent_joints.joint8.offset": 0.0,
                },
            ],
            remappings=[("joint_states", "/joint_states_complete")],
        )
    )

    ld.add_action(
        Node(
            package="robot_state_publisher",
            executable="robot_state_publisher",
            respawn=True,
            output="screen",
            parameters=[
                moveit_config.robot_description,
                {
                    "publish_frequency": LaunchConfiguration("publish_frequency"),
                },
            ],
            remappings=[("joint_states", "/joint_states_complete")],
        )
    )

    return ld
