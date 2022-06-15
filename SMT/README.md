# Constraint Programming model

## Requirements
The following packages are required:
- minizinc
- matplotlib
- numpy

## Usage
The models can be executed by launching the `solver.py` file that is in the `src` directory.

You can modify the following arguments of the main function:

| Argument                                         | Description                                                                  |
| ------------------------------------------------ | -----------------------------------------------------------------------------|
| `n_instances`                                    | The number of instances that you want to solve                               |
| `rotation`                                       | If you want to launch the model that allows rotation or not                  |
| `ordered`                                        | If you want to apply the sorting of the circuits by dimension or not         |
