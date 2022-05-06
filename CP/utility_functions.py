import numpy as np
import matplotlib.pyplot as plt
import random
import os
import matplotlib.patches as patches
from matplotlib.ticker import ScalarFormatter


def plot_result(result, dims, w, n):
    ys = np.array(result.solution.y)
    xs = np.array(result.solution.x)

    fig1 = plt.figure(figsize=(10, 10))
    ax1 = fig1.add_subplot(111, aspect='equal')
    for i in range(len(xs)):
        ax1.add_patch(patches.Rectangle(
            (xs[i], ys[i]), dims[i][0], dims[i][1], edgecolor='black', facecolor=random.choice(['r', 'g', 'y'])))

    plt.xticks(range(w+1))
    plt.yticks(range(max([ys[i]+dims[i][1] for i in range(len(ys))])+1))
    # plt.show()
    plt.savefig('plate_plot.png')


def plot_statistics(n_instances, time_stats, time_stats_rotation=None):
    fig, ax = plt.subplots(1, 1, figsize=(15, 9))
    w = 0.4
    x = np.arange(n_instances)
    r1 = ax.bar(x - w*1.1 + 1, time_stats, width=w, color='C0', align='center',
                label='Best model CP with rotation')
    if time_stats_rotation != None:
        r2 = ax.bar(x - w/5 + 1, time_stats_rotation, width=w, color='C3', align='center',
                    label='Best model SMT with rotation')
    ax.set_xlabel('instances')
    ax.set_ylabel('time (s)')
    ax.set_xlim(0, n_instances)
    ax.set_xticks(list(range(1, n_instances + 1)))
    ax.set_yscale('log')
    ax.set_yticks([0.1, 1, 10, 60, 150, 300])
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.legend()
    plt.savefig('time_statistics' + str(random.randint(1, 1000)) + '.png')


def read_instance_dzn(instance_id, ordered):
    if ordered:
        filepath = (
            "/home/belericks7/Documenti/optimization/VLSI/Instances/sorted_instances_dzn/ins-" + str(instance_id) + ".dzn")
    else:
        filepath = (
            "/home/belericks7/Documenti/optimization/VLSI/Instances/instances_dzn/ins-" + str(instance_id) + ".dzn")

    with open(filepath, "r") as f_in:
        f = f_in.readlines()
        W = int([c for c in f[0] if c.isnumeric()][0])
        n = int([c for c in f[1] if c.isnumeric()][0])
        widths = [int(c) for c in f[2][10:-3].split(',')]
        heights = [int(c) for c in f[3][11:-2].split(',')]
        dims = [[widths[i], heights[i]] for i in range(len(widths))]
    return dims, W, n


def create_sorted_instances_dzn():
    folder_in = "/home/belericks7/Documenti/optimization/VLSI/Instances/instances_txt/"
    folder_out = "/home/belericks7/Documenti/optimization/VLSI/Instances/sorted_instances_dzn/"

    for txt_file in os.listdir(folder_in):
        l1 = []
        with open(os.path.join(folder_out, txt_file[:-3])+"dzn", "w") as f_out:
            f_in = open(os.path.join(folder_in, txt_file), "r").readlines()
            for i in range(len(f_in)):
                if not f_in[i][-1].isnumeric():
                    f_in[i] = f_in[i][:-1]
            f_out.write("w = " + f_in[0] + ";\n")
            f_out.write("n = " + f_in[1] + ";\n")
            for i in range(2, len(f_in)):
                values = f_in[i].split(" ")
                l1.append(values)
            l1.sort(key=lambda x: int(x[0])*int(x[1]), reverse=True)
            f_out.write("widths = [")
            for i in range(len(l1)):
                f_out.write(l1[i][0])
                if i != len(l1)-1:
                    f_out.write(",")
            f_out.write("];\n")
            f_out.write("heights = [")
            for i in range(len(l1)):
                f_out.write(l1[i][1])
                if i != len(l1)-1:
                    f_out.write(",")
            f_out.write("];")


def create_instances_dzn():
    folder_in = "/home/belericks7/Documenti/optimization/VLSI/Instances/instances_txt//"
    folder_out = "/home/belericks7/Documenti/optimization/VLSI/Instances/instances_dzn//"

    for txt_file in os.listdir(folder_in):
        with open(os.path.join(folder_out, txt_file[:-3])+"dzn", "w") as f_out:
            f_in = open(os.path.join(folder_in, txt_file), "r").readlines()
            for i in range(len(f_in)):
                if not f_in[i][-1].isnumeric():
                    f_in[i] = f_in[i][:-1]
            f_out.write("w = " + f_in[0] + ";\n")
            f_out.write("n = " + f_in[1] + ";\n")
            dims_line = f_in[2].split(" ")
            f_out.write("widths = [")
            for i in range(2, len(f_in)):
                values = f_in[i].split(" ")
                f_out.write(values[0])
                if i != len(f_in)-1:
                    f_out.write(",")
            f_out.write("];\n")
            f_out.write("heights = [")
            for i in range(2, len(f_in)):
                values = f_in[i].split(" ")
                f_out.write(values[1])
                if i != len(f_in)-1:
                    f_out.write(",")
            f_out.write("];")
