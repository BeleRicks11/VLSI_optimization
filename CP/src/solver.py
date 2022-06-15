from minizinc import Instance, Model, Solver
from minizinc.result import Status
from utility_functions import read_instance_dzn, plot_statistics, plot_result
import numpy as np
import datetime


def solve_all(max_instance, rotation, ordered, path):
    n_solved = 0
    time_stats = []
    for i in range(1, max_instance+1):
        print("Solving: ", i)
        res = solve_instance(i, rotation, ordered, path)
        print("\tObj: ", res.objective)
        print("\tTime: ", res.statistics["solveTime"])
        print("\tFailures: ", res.statistics["failures"])
        print("\tStatus: ", res.status)
        print("\n")

        dims, w, n = read_instance_dzn(i, ordered, path)

        if res.status == Status.OPTIMAL_SOLUTION:
            # plot_result(res, dims, w, n)
            time_stats.append(res.statistics["solveTime"])
            if rotation:
                f = open(path + "CP/out_rotation/out-" + str(i) + ".txt", "w")
            else:
                f = open(path + "CP/out/out-" + str(i) + ".txt", "w")
            f.write(str(w) + " " + str(res.objective) + "\n")
            f.write(str(n) + "\n")
            for i in range(n):
                if i < n-1:
                    f.write(str(dims[i][0]) + " " + str(dims[i][1]) + " " +
                            str(res.solution.x[i]) + " " + str(res.solution.y[i]) + "\n")
                else:
                    f.write(str(dims[i][0]) + " " + str(dims[i][1]) + " " +
                            str(res.solution.x[i]) + " " + str(res.solution.y[i]))
            f.close()
            n_solved += 1
        else:
            time_stats.append(0)
    print(f"Solved {n_solved}/{max_instance} instances")
    print(time_stats)
    return time_stats


def solve_instance(instance_id, rotation, ordered, path):
    # Load model from file
    if rotation:
        model = Model(path + "CP/src/model_rotation.mzn")
        print("Model-rotation")
    else:
        model = Model(path + "/CP/src/base_model.mzn")
        print("Model-base")

    # Find the MiniZinc solver configuration for Gecode or Chuffed
    solver = Solver.lookup("gecode")
    # solver = Solver.lookup("chuffed")

    # Assign data
    if ordered:
        model.add_file(
            path + "VLSI/Instances/sorted_instances_dzn/ins-" + str(instance_id) + ".dzn")
    else:
        model.add_file(
            path + "VLSI/Instances/instances_dzn/ins-" + str(instance_id) + ".dzn")

    # Create an Instance of model for the solver
    instance = Instance(solver, model)

    timeout = datetime.timedelta(seconds=300)
    return instance.solve(timeout=timeout)


if __name__ == "__main__":
    n_instances = 40
    PATH = '/home/belericks7/Documenti/optimization/VLSI_optimization/'
    time_stats = solve_all(n_instances, rotation=False,
                           ordered=True, path=PATH)
