from __future__ import print_function
from datetime import datetime
import os
import json
import util_methods as util


def test():
    """
    Just run some simple tests.
    :return: None
    """

    vehicle_list, edge_list, point_list = util.set_lists()
    print("hello")
    print("Edge w/ shape:")
    print(util.edge_to_xy_list(edge_list, point_list, "141294961#0"))
    print("Edge wo/ shape:")
    print(util.edge_to_xy_list(edge_list, point_list, ":1113784206_0"))
    print(util.edge_to_xy_list(edge_list, point_list, "141294961#3"))


def main():
    """
    The main function. Will produce mobcons compatible paths and extract routes then save it to files.
    :return:
    """

    # Create a tag with current datetime
    time_tag = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    mobcons_paths_file = open(os.path.join(os.getcwd(), "output", "mobcons_constraints_" + time_tag + ".json"), "w")
    json_file = open(os.path.join(os.getcwd(), "output", "route_dict_" + time_tag + ".json"), "w")

    # Set the lists
    vehicle_list, edge_list, point_list = util.set_lists()
    route_dict = util.generate_route_dict(vehicle_list, edge_list, point_list)
    paths = util.export_route_dict_to_mobcons_path(route_dict)

    # Save mobcons path export
    mobcons_paths_file.writelines(paths)
    mobcons_paths_file.close()

    # Save route dict
    util.save_route_dict_to_json_file(route_dict, json_file, True)

    # Test
    json_file = open(os.path.join(os.getcwd(), "output", "route_dict_" + time_tag + ".json"), "r")
    route_dict2 = util.load_route_dict_from_json_file(json_file, True)

    keys = set(route_dict.keys())
    if keys != set(route_dict2.keys()):
        print("Not the same key set")
    else:
        print("Same keys!")
    # I do not test the values because the loaded strings are in unicode

    json_file = open(os.path.join(os.getcwd(), "output", "mobcons_constraints_" + time_tag + ".json"), "r")
    jsonobj = json.loads(json_file.read())


if __name__ == '__main__':
    main()
