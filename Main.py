from __future__ import print_function
from __future__ import absolute_import
import xml.etree.ElementTree as ET
import sys
import optparse
from datetime import datetime
from statistics import mean
import math
import os

from sumolib import checkBinary

# # we need to import python modules from the $SUMO_HOME/tools directory
# try:
#     sys.path.append(os.path.join(os.path.dirname(
#         __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
#     sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
#         os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
#     from sumolib import checkBinary  # noqa
# except ImportError:
#     sys.exit(
#         "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation "
#         "(it should contain folders 'bin', 'tools' and 'docs')")

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

import traci

######################################################################################
#################-------- Definition of functions -----------------###################
######################################################################################

def distance(x1,y1, x2,y2):
    """
    Caculates the distance between the points (x1,y1) and (x1,y2) in the cartesian plane.
    :param x1: the x position of the first point
    :param y1: the y position of the first point
    :param x2: the x position of the second point
    :param y2: the y position of the second point
    :return: a float with the distance between the two points
    """
    dist = float(((x1-x2)**2)+((y1-y2)**2))
    return math.sqrt(dist)


def get_all_vehicles_active(vehicle_list=[], simulation=traci.simulation):
    """
    Adds departed cars and removes arrived cars from the list. Needs to be executed at each simulation step.
    :param vehicle_list: the current list of cars (default create a new list)
    :param simulation: the sumo simulation (default will use the traci.simulation method to get it)
    :return: the cars list updated
    """
    for car in simulation.getDepartedIDList():  # Adds the cars that departed in the current step
        vehicle_list.append(car)

    vehicle_list = list(set(vehicle_list) - set(simulation.getArrivedIDList()))  # Removes the cars that arrived in the current step

    return vehicle_list


def get_all_vehicles_in_simulation_edge_by_edge(net_file="osm.net.xml"):  # Do not use.
    xml_tree = ET.parse(net_file)
    root = xml_tree.getroot();
    edges = root.findall("edge")
    car_li = []
    for edge in edges:
        car_li = set(car_li+traci.edge.getLastStepVehicleIDs(edge))  # get the cars at the edge
    return car_li


def log_distance_violations(min_dist_bus, min_dist_car, vehicle_list, simulation, distances, use_curr_step=False,
                            out_file=open("[DISTANCE]" + datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".txt", "w")):
    """
    Log distance violations into a text file. Needs to be executed at each simulation step.
    :param min_dist_bus: The minimum allowed distance between any vehicle and a bus
    :param min_dist_car: The minimum distance between two passenger cars
    :param vehicle_list: The list of cars currently active
    :param simulation: the sumo simulation
    :param distances: The log of all distances
    :param use_curr_step: If false will just add distances  to the distances dictionary;
                          If true will also calculate statistics and log then at the current step
    :param out_file: The file to register distance violations (default will create a new file)
    :return: The log_file
    """
    if not "bus" in distances:
        distances["bus"] = []
    if not "car" in distances:
        distances["car"] = []
    statistics_by_kind = {}

    if vehicle_list is None:
        vehicle_list = get_all_vehicles_active(simulation=simulation)

    # Will get every pair of vehicles currently in the simulation
    for i in range(len(vehicle_list)):
        for j in range(i+1, len(vehicle_list)):
            # Get the vehicle id and type for both vehicles
            vehicle1 = vehicle_list[i]
            type1 = traci.vehicle.getTypeID(vehicle1)
            vehicle2 = vehicle_list[j]
            type2 = traci.vehicle.getTypeID(vehicle2)

            # Calculate the distance between the 2 vehicles
            x1, y1 = traci.vehicle.getPosition(vehicle1)
            x2, y2 = traci.vehicle.getPosition(vehicle2)
            dist = distance(x1, y1, x2, y2)

            # Check if one of the vehicles is a bus
            if "bus_bus" in [type1, type2]:
                distances["bus"].append(dist)

            else:
                distances["car"].append(dist)

    if use_curr_step:
        for kind in distances.keys():
            if len(distances[kind]) > 1:
                if kind not in statistics_by_kind:
                    statistics_by_kind[kind] = {}
                statistics_by_kind[kind]['mean'] = mean(distances[kind])
                statistics_by_kind[kind]['min'] = min(distances[kind])
        for kind in statistics_by_kind:
            print('Statistics for ' + kind + str(statistics_by_kind[kind]))
        print("\n")


def get_options():
    optParser = optparse.OptionParser()
    optParser.add_option("--nogui", action="store_true",
                         default=False, help="run the commandline version of sumo")
    options, args = optParser.parse_args()
    return options


def run_simulation():
    step = 0
    vehicle_list = []
    simulation = traci.simulation
    distances = {}
    output_dir = os.path.join(os.getcwd(), "output")
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    dis_file_name = "[DISTANCE]"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".txt"
    dist_out_file = open(os.path.join(output_dir, dis_file_name), "w")
    while simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()  # Run a simulation step
        vehicle_list = get_all_vehicles_active(vehicle_list=vehicle_list, simulation=simulation)
        log_distance_violations(3, 2, vehicle_list, simulation, distances, (step % 50 == 0), dist_out_file)
        step += 1


# this is the main entry point of this script
if __name__ == "__main__":
    options = get_options()

    output_file = os.path.join(os.getcwd(), "output", "tracer_"+datetime.now().strftime("%Y-%m-%d_%H-%M-%S")+".xml")

    # this script has been called from the command line. It will start sumo as a
    # server, then connect and run
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo-gui')

    traci.start([sumoBinary, "-c", "osm2.sumocfg",
                 "--fcd-output", output_file])

    run_simulation()
