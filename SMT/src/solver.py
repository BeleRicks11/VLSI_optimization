import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib.patches as patches
from matplotlib.ticker import ScalarFormatter
from model import solve_instance


def solve_all(min_instance, max_instance, rotation, ordered, path):
    n_solved = 0
    time_statistics = []
    for i in range(min_instance, max_instance+1):
        print("Solving: ", i)
        instance_dict = {}
        d, instance_dict["w"], instance_dict["n"] = read_instance(i, path)
        if ordered:
            d.sort(key=lambda x: x[0]*x[1], reverse=True)
        instance_dict["heights"] = [i[1] for i in d]
        instance_dict["widths"] = [i[0] for i in d]
        x, y, obj, solve_time = solve_instance(instance_dict, rotation)
        if obj != None:
            if rotation:
                f = open(path + "SMT/out_rotation/out-" + str(i) + ".txt", "w")
            else:
                f = open(path + "SMT/out/out-" + str(i) + ".txt", "w")
            f.write(str(instance_dict["w"]) + " " + str(obj) + "\n")
            f.write(str(instance_dict["n"]) + "\n")
            for i in range(instance_dict["n"]):
                if i < instance_dict["n"]-1:
                    f.write(str(d[i][0]) + " " + str(d[i][1]) + " " +
                            str(x[i]) + " " + str(y[i]) + "\n")
                else:
                    f.write(str(d[i][0]) + " " + str(d[i][1]) + " " +
                            str(x[i]) + " " + str(y[i]))
            f.close()
            n_solved += 1
            time_statistics.append(solve_time)
        else:
            time_statistics.append(0)
    print(f"Solved {n_solved}/{max_instance} instances")
    return time_statistics


def read_instance(instance_id, path):
    filepath = path + "Instances/instances_txt/ins-" + \
        str(instance_id) + ".txt"
    with open(filepath, "r") as f_in:
        f = f_in.readlines()
        for i in range(len(f)):
            if not f[i][-1].isnumeric():
                f[i] = f[i][:-1]

        W = int(f[0])
        n = int(f[1])
        dims_line = f[2].split(" ")
        dims = [[int(dims_line[0]), int(dims_line[1])]]
        for i in range(1, int(f[1])-1):
            dims_line = f[2 + i].split(" ")
            dims.append([int(dims_line[0]), int(dims_line[1])])
        dims_line = f[-1].split(" ")
        dims.append([int(dims_line[0]), int(dims_line[1])])
    return dims, W, n


if __name__ == "__main__":
    n_instances = 40
    PATH = "/home/belericks7/Documenti/optimization/VLSI_optimization/"
    time_stats = solve_all(
        min_instance=1, max_instance=n_instances, rotation=False, ordered=True, path=PATH)
