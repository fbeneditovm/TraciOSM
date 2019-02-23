from __future__ import print_function
import datetime
import os
import sys
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
    The main function. Will produce mobcons compatible paths from sumo route files.
    :return:
    """

    time_tag = datetime.now().strftime("%Y-%m-%d %H-%M-%S")

    mampbib_paths_file = open(os.path.join(os.getcwd(), "output", "mobcons_paths"+time_tag+".txt"), "a")

    # Set the lists
    vehicle_list, edge_list, point_list = util.set_lists()

    route_dict = util.generate_route_dict(vehicle_list, edge_list, point_list)

    paths = util.export_route_dict_to_mobcons_path(route_dict)
    for vehicle_id in route_dict:
        line = vehicle_id+"="
        for xy in route_dict[vehicle_id]["xy"]:
            line += str(xy[0]) + "," + str(xy[1]) + " "
            if len(line) > len(vehicle_id+"="):
                line = line[:-1] + "\n"  # Remove the last space and add a line break
                mampbib_paths_file.write(line)
        i += 1
        if i >= 3:
            break


if __name__ == '__main__':
    main()
