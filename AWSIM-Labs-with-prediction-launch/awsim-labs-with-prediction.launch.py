# Copyright 2024 Tier IV, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from ament_index_python.packages import get_package_share_directory
import launch
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration
import yaml

def generate_launch_description():

    #set prediction-node
    map_based_prediction_param_file = os.path.join(
        get_package_share_directory("awsim_map_based_prediction"), "config/map_based_prediction.param.yaml"
    )
    with open(map_based_prediction_param_file, "r") as f:
        map_based_prediction_param = yaml.safe_load(f)["/**"]["ros__parameters"]
    prediction_Node = Node(
        package="awsim_map_based_prediction",
        namespace="AWSIM",
        executable="map_based_prediction",
        name="map_based_prediction",
        output="both",
        parameters=[map_based_prediction_param],
        remappings=[
            ('/vector_map','map/vector_map'),
            ('/traffic_signals','perception/traffic_light_recognition/traffic_signals'),
            ('~/output/objects','perception/object_recognition/objects'),
            ('~/input/objects','perception/object_recognition/tracking/objects')
        ]
    )

    # set map-loader-node
    lanelet2_map_loader_param_file = os.path.join(
        get_package_share_directory("awsim_map_loader"), "config/lanelet2_map_loader.param.yaml"
    )
    with open(lanelet2_map_loader_param_file, "r") as f:
        lanelet2_map_loader_param = yaml.safe_load(f)["/**"]["ros__parameters"]
    map_loader_Node = Node(
        package="awsim_map_loader",
        namespace="AWSIM",
        executable="lanelet2_map_loader",
        name="lanelet2_map_loader",
        output="both",
        parameters=[
            lanelet2_map_loader_param,
            {
                'lanelet2_map_path': LaunchConfiguration('lanelet2_map_path'),
            }
        ],
        remappings=[
            ('/map/map_projector_info','map/map_projector_info'),
            ('output/lanelet2_map','map/vector_map')
        ]
    )

    # set map-projection-node
    map_projection_loader_param_file = os.path.join(
        get_package_share_directory("awsim_map_projection_loader"), "config/map_projection_loader.param.yaml"
    )
    with open(map_projection_loader_param_file, "r") as f:
        map_projection_loader_param = yaml.safe_load(f)["/**"]["ros__parameters"]
    map_projection_Node = Node(
        package="awsim_map_projection_loader",
        namespace="AWSIM",
        executable="awsim_map_projection_loader_node",
        name="map_projection_loader",
        output="both",
        parameters=[
            map_projection_loader_param,
            {
                'lanelet2_map_path': LaunchConfiguration('lanelet2_map_path'),
            }
        ],
        remappings=[
            ('/map/map_projector_info','map/map_projector_info')
        ]
    )

    # set AWSIM
    awsim_with_prediction = ExecuteProcess(
        cmd=[[
            LaunchConfiguration('AWSIM_path')
        ]],
        shell=True
    )

    return launch.LaunchDescription(
        [
        prediction_Node,
        map_loader_Node,
        map_projection_Node,
        awsim_with_prediction,
        ]
    )

