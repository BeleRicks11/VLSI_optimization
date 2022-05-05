
from z3 import *
import time
import numpy as np
import matplotlib.pyplot as plt
import random
import matplotlib.patches as patches
from matplotlib.ticker import ScalarFormatter


def solve_instance(instance, rotation):

    def min_z3(vars):
        min = vars[0]
        for v in vars[1:]:
            min = If(v < min, v, min)
        return min

    def z3_cumulative(start, duration, resources, total):
        decomposition = []
        for u in resources:
            decomposition.append(
                sum([If(And(start[i] <= u, u < start[i] + duration[i]), resources[i], 0)
                    for i in range(len(start))]) <= total
            )
        return decomposition

    w = instance["w"]
    n_circuits = instance["n"]
    heights = instance["heights"]
    widths = instance["widths"]

    x = IntVector('x', n_circuits)
    y = IntVector('y', n_circuits)

    plate_height = Int('plate_height')
    min_height = max(heights)
    max_height = sum(heights)

    big_circuit_idx = np.argmax([heights[i]*widths[i]
                                for i in range(n_circuits)])

    opt = Optimize()

    # Handle rotation
    if rotation:
        rotations = BoolVector("rotations", n_circuits)
        copy_widths = widths
        widths = [If(rotations[i], heights[i], widths[i])
                  for i in range(n_circuits)]
        heights = [If(rotations[i], copy_widths[i], heights[i])
                   for i in range(n_circuits)]
        big_circuit_idx = 0

    # Bounds on variables
    # Plate height bounds
    opt.add(And(plate_height >= min_height, plate_height <= max_height))
    for i in range(n_circuits):

        # X and Y bounds
        opt.add(And(x[i] >= 0, x[i] <= w - min_z3(widths)))
        opt.add(And(y[i] >= 0, y[i] <= max_height - min_z3(heights)))

        # Main constraints
        opt.add(x[i] <= w-widths[i])
        opt.add(y[i] <= plate_height-heights[i])

        if rotation:
            # Constraint to avoid rotation of square circuits
            opt.add(Implies(widths[i] == heights[i], Not(rotations[i])))

        for j in range(n_circuits):
            if i != j:
                # Non overlaping constraints
                opt.add(Or(x[i] + widths[i] <= x[j], x[j] + widths[j] <= x[i],
                           y[i] + heights[i] <= y[j], y[j] + heights[j] <= y[i]))

                # Ordering constraint between equal circuits
                opt.add(Implies(And(heights[i] == heights[j], widths[i] == widths[j]), And(
                    x[i] <= x[j], Implies(x[i] == x[j], y[i] <= y[j]))))

    # Adding comulative constraints
    opt.add(z3_cumulative(x, widths, heights, plate_height))
    opt.add(z3_cumulative(y, heights, widths, w))

    # Largest circuit in the origin
    opt.add(And(x[big_circuit_idx] == 0, y[big_circuit_idx] == 0))

    opt.minimize(plate_height)

    opt.set("timeout", 300*1000)  # 5 minutes timeout
    start_time = time.time()

    if opt.check() == sat:
        model = opt.model()
        print("Solving time (s): ", round(time.time()-start_time, 3))
        height = model.eval(plate_height).as_long()
        print("Height:", height)
        print("\n")
        xs, ys = [], []
        for i in range(n_circuits):
            xs.append(model.evaluate(x[i]))
            ys.append(model.evaluate(y[i]))

        return xs, ys, height, time.time()-start_time
    else:
        print("Time limit excedeed\n")
        return [], [], None, 0


def solve_all(min_instance, max_instance, rotation, ordered):
    n_solved = 0
    time_statistics = []
    for i in range(min_instance, max_instance+1):
        print("Solving: ", i)
        instance_dict = {}
        d, instance_dict["w"], instance_dict["n"] = read_instance(i)
        if ordered:
            d.sort(key=lambda x: x[0]*x[1], reverse=True)
        instance_dict["heights"] = [i[1] for i in d]
        instance_dict["widths"] = [i[0] for i in d]
        x, y, obj, solve_time = solve_instance(instance_dict, rotation)
        if obj != None:
            if rotation:
                f = open(
                    "/home/belericks7/Documenti/optimization/VLSI/smt/out_rotation/out-" + str(i) + ".txt", "w")
            else:
                f = open(
                    "/home/belericks7/Documenti/optimization/VLSI/smt/out/out-" + str(i) + ".txt", "w")
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


def read_instance(instance_id):
    filepath = "/home/belericks7/Documenti/optimization/VLSI/Instances/instances_txt/ins-" + \
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


def plot_statistics(time_stats, time_stats_rotation, n_instances):
    fig, ax = plt.subplots(1, 1, figsize=(15, 9))
    w = 0.4
    x = np.arange(n_instances)
    r1 = ax.bar(x - w*1.1 + 1, time_stats, width=w, color='C0', align='center',
                label='Best model')
    r2 = ax.bar(x - w/5 + 1, time_stats_rotation, width=w, color='C3', align='center',
                label='Best rotation model')
    ax.set_xlabel('instances')
    ax.set_ylabel('time (s)')
    ax.set_xlim(0, n_instances)
    ax.set_xticks(list(range(1, n_instances + 1)))
    ax.set_yscale('log')
    ax.set_yticks([0.1, 1, 10, 60, 150, 300])
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.legend()
    plt.savefig('time_statistics' + str(random.randint(1, 1000)) + '.png')


if __name__ == "__main__":
    n_instances = 40
    #time_stats = solve_all(min_instance=1, max_instance=n_instances,rotation=False, ordered=True)
    #time_stats_rotation = solve_all(min_instance=1, max_instance=n_instances, rotation=True, ordered=True)
    #plot_statistics(time_stats, time_stats_rotation, n_instances=n_instances)

    smt_general = [0.007, 0.012, 0.017, 0.036, 0.049, 0.099, 0.109, 0.084, 0.214, 0.538, 181.756, 3.181, 1.831, 3.448, 3.476, 0,
                   13.71, 12.112, 0, 111.214, 0, 0, 66.964, 9.576, 0, 59.244, 39.07, 75.423, 108.17, 0, 8.73, 0, 12.155, 0, 0, 0, 0, 0, 0, 0]
    smt_rotation = [0.017, 0.063, 0.085, 0.438, 0.791, 3.55, 3.494, 1.201, 5.65, 129.954, 0, 0, 0, 0,
                    76.637, 0, 0, 0, 0, 0, 0, 0, 0, 244.127, 0, 0, 0, 0, 0, 0, 237.634, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    plot_statistics(smt_general, smt_rotation, n_instances=n_instances)
