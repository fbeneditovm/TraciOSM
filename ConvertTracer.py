from __future__ import print_function

import xml.etree.ElementTree as ET
import os
import time
from statistics import mean


class StrToInt:
    """
    Codes each unique string to an int.
    Keeps a set of the previous converted string.
    If string to convert is in the set return its index in the set.
    If not add it to the set and return the index it is at after the addition
    """
    def __init__(self):
        self.strSet = []

    def get_int(self, str_buffer):
        """
        Keeps a set of the previous converted string.
        If string to convert is in the set return its index in the set.
        If not add it to the set and return the index it is at after the addition
        :param str_buffer: the string to code to int
        :return: an int that represents the string
        """
        if self.strSet.count(str_buffer) > 0:
            return (self.strSet.index(str_buffer) + 1) * 100
        else:
            self.strSet.append(str_buffer)
            return (self.strSet.index(str_buffer) + 1) * 100


def sumo_tracer_to_mobcons(tracerfile):
    """
    Converts a sumo generated tracer to a mobcons compatible tracer.
    Will create mobcons tracer file with the same name as the sumo tracer file, however with the .txt extension.
    :param tracerfile: the sumo tracer file
    :return: None
    """

    # MUID_CONTAINS_STRING = True

    try:
        with open(os.path.join("output", "ConstBreakLog.txt"), "r") as breakLog:
            breakLog_lines = breakLog.readlines()
            now = long(float(breakLog_lines[0]))
    except IOError:
        now = long(round(time.time() * 1000))
        # now = 1530615660000 # 8:01
        # now = 1530625560000 # 10:45

    tree = ET.parse(tracerfile)
    root = tree.getroot()
    i = 0
    line_list = []
    str_to_int = StrToInt()  # This will code the string parts of vehicle.id to int
    all_speed_by_kind = {}
    statistics_by_kind = {}

    for timestep in root:
        timestamp = str(now + int(float(timestep.get('time'))*1000))
        for vehicle in timestep:
            # if MUID_CONTAINS_STRING:
            #     id_parts = str(vehicle.get('id')).split('.')
            #     mu_id = id_parts[0]
            #     mu_id = str(str_to_int.get_int(mu_id))
            #     mu_id = mu_id + id_parts[1]
            # else:
            #     mu_id = str(vehicle.get('id'))

            mu_id = str(vehicle.get('id'))
            x = str(vehicle.get('x'))
            y = str(vehicle.get('y'))
            kind_of_mu = str(vehicle.get('type'))
            speed_float = round(float(vehicle.get('speed')) * 3.6, 3)  # convert m/s to km/s and round to 3 dec. places
            speed_str = str(speed_float)

            line_list.append(mu_id + ',' + x + ',' + y + ',' + speed_str + ',' + timestamp + ',' + kind_of_mu + '\n')

            if kind_of_mu in all_speed_by_kind:
                all_speed_by_kind[kind_of_mu].append(speed_float)
            else:
                all_speed_by_kind[kind_of_mu] = []
                all_speed_by_kind[kind_of_mu].append(speed_float)
                statistics_by_kind[kind_of_mu] = {}

    for kind in all_speed_by_kind:
        statistics_by_kind[kind]['total'] = len(all_speed_by_kind[kind])
        statistics_by_kind[kind]['mean'] = mean(all_speed_by_kind[kind])
        statistics_by_kind[kind]['max'] = max(all_speed_by_kind[kind])
        statistics_by_kind[kind]['n_above_40'] = sum(spd > 40 for spd in all_speed_by_kind[kind])
        statistics_by_kind[kind]['n_above_60'] = sum(spd > 60 for spd in all_speed_by_kind[kind])
        statistics_by_kind[kind]['n_above_80'] = sum(spd > 80 for spd in all_speed_by_kind[kind])

    for kind in statistics_by_kind:
        print('Statistics for '+kind+str(statistics_by_kind[kind]))

    with open(tracerfile[:-3]+"txt", "w") as mobcons_tracer:
        mobcons_tracer.writelines(line_list)

    print(line_list[20])


def main():
    """
    The main function.
    Will run through the output folder generating mobcons tracer files to all sumo tracer files
    :return: None
    """
    import os

    for root, dirs, files in os.walk(os.path.join(os.getcwd(), "output")):
        for filename in files:
            # Check for sumo tracers without a respective mobcons tracer
            if filename.startswith("tracer") and filename.endswith(".xml") \
               and not os.path.isfile(os.path.join(root, filename[:-3]+"txt")):
                sumo_tracer_to_mobcons(os.path.join(root, filename))


if __name__ == '__main__':
    main()

