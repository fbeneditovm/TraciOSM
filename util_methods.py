from math import ceil
import xml.etree.ElementTree as ET


def set_lists(vehicle_list=[], edge_list=[], point_list=[], route_files=["osm.bus.rou.xml"], net_file="osm.net.xml"):
    """
    Sets the lists using information from sumo input files.
    :param vehicle_list: the list that will be set with all vehicles in the route files
    :param point_list: the list that will be set with all junctions in the net file
    :param edge_list:  the list that will be set will all edge in the net file
    :param route_files: a list with *.rou.xml files
    :param net_file: a list with *.net.xml files
    :return: None
    """
    for route_file in route_files:
        # We are accessing this xml as a tree structure
        xml_file = ET.parse(route_file)
        xml_root = xml_file.getroot()

        # Get the vehicle routes definitions from the file
        vehicle_list += [x for x in xml_root if x.tag == "vehicle"]

    # Doing the same for the point and edge lists
    xml_file = ET.parse(net_file)
    xml_root = xml_file.getroot()
    point_list += [x for x in xml_root if x.tag == "junction"]
    edge_list += [x for x in xml_root if x.tag == "edge"]
    return vehicle_list, edge_list, point_list


def get_xy_from_point(point_list, point_id):
    """
    Gets the xy position for a point in the sumo net
    :param point_list: a list with all the points (generated using the set_lists function)
    :param point_id: the id of the point
    :return: a float tuple in the format (x, y)
    """
    for point in point_list:
        if point.get("id") == point_id:
            xy = (float(point.get("x")), float(point.get("y")))
            return xy


def edge_to_xy_list(edge_list, point_list, edge_id):
    """
    Produces an xy list from the edge shape in the sumo net
    :param edge_list: a list with all the edges (generated using the set_lists function)
    :param point_list: a list with all the points (generated using the set_lists function)
    :param edge_id: the id of the edge
    :return: a list of float tuples each in the format (x, y)
    """
    xy_list = []
    for edge in edge_list:
        if edge.get("id") == edge_id:

            # First we add the position of the starting point
            if "from" in edge.attrib:
                xy_list.append(get_xy_from_point(point_list, edge.get("from")))

            # If the edge has a shape we will use it
            if "shape" in edge.attrib:
                shape = edge.get("shape").split(" ")

            # Otherwise we will just use the shape of the edge's middle lane
            else:
                lanes = [x for x in edge if x.tag == "lane"]
                mid_lane = lanes[int(ceil(len(lanes)/2.0))-1]
                shape = mid_lane.get("shape").split(" ")

            # Each item of shape is a string in the format "x,y" we convert to to a float tuples (x, y)
            for xy_string in shape:
                xy_tuple = (float(xy_string.split(",")[0]), float(xy_string.split(",")[1]))
                if not (len(xy_list) > 0 and xy_tuple == xy_list[-1]):  # Avoid duplicates
                    xy_list.append(xy_tuple)

            # Lastly we add the position of the ending point
            if "to" in edge.attrib:
                xy_list.append(get_xy_from_point(point_list, edge.get("to")))

            return xy_list


def generate_route_dict(vehicle_list=None, edge_list=None, point_list=None):
    """
    Produce a route dict representing the route of every vehicle in the simulation.
    Dict format: {<vehicle_id>: {"edges":<list_of_edges_in_route>, "xy": <list_of_xy_positions_in_the_route>}}
    :param vehicle_list: a list with all the vehicles (generated using the set_lists function)
    :param edge_list: a list with all the edges (generated using the set_lists function)
    :param point_list: a list with all the points (generated using the set_lists function)
    :return: a Python dict
    """
    # Setting the lists if they are not set
    if vehicle_list is None:
        if edge_list is None:
            if point_list is None:
                vehicle_list, edge_list, point_list = set_lists()
            else:
                vehicle_list, edge_list, _ = set_lists()
        else:
            if point_list is None:
                vehicle_list, _, point_list = set_lists()
            else:
                vehicle_list, _, _ = set_lists()
    else:
        if edge_list is None:
            if point_list is None:
                _, edge_list, point_list = set_lists()
            else:
                _, edge_list, _ = set_lists()
        else:
            if point_list is None:
                _, _, point_list = set_lists()
            # else: do nothing because every list is already set

    # Start building the route_dict
    route_dict = {}
    for vehicle in vehicle_list:
        # Checks if the vehicle has a sub_element whose tag is "route". It's python
        if "route" in [x.tag for x in vehicle]:

            route_edges = []
            # Get the edges that compose the route
            for sub_elm in vehicle:
                if sub_elm.tag == "route":  # We know there is only one route per vehicle
                    route_edges = sub_elm.get("edges").split(" ")
                    break

            # add to the route_dict
            route_dict[vehicle.get("id")] = {"edges": route_edges, "xy": []}
            for edge in route_edges:
                route_dict[vehicle.get("id")]["xy"] += edge_to_xy_list(edge_list, point_list, edge)

    return route_dict
