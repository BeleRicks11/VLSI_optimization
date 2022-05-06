from z3 import *
import time
import numpy as np


def solve_instance(instance, rotation):

    def min_z3(vars):
        min = vars[0]
        for v in vars[1:]:
            min = If(v < min, v, min)
        return min

    def cumulative_z3(start, duration, resources, total):
        c = []
        for u in resources:
            c.append(sum([If(And(start[i] <= u, u < start[i] + duration[i]), resources[i], 0)
                          for i in range(len(start))]) <= total)
        return c

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
    opt.add(cumulative_z3(x, widths, heights, plate_height))
    opt.add(cumulative_z3(y, heights, widths, w))

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
