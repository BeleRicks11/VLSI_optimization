include "globals.mzn";

% Input variables
int: w; % width of the plate
int: n; % number of circuits to be placed

set of int: circuits = 1..n;
array [circuits] of int: heights; % heights of each circuit
array [circuits] of int: widths; % weights of each circuit

% Output variables
array [circuits] of var 0..w-min(widths): x; % horizontal vertex
array [circuits] of var 0..max_height-min(heights): y; % vertical vertex
var min_height..max_height: plate_height; % height of the plate
array [circuits] of var bool: rotations; % boolean values that encode the circuits are rotated  

% Other variables
int: max_height = sum(heights); % Plate height upper bound
int: min_height = max(heights); % Plate height lower bound

int : big_circuit_idx = arg_max([heights[c]*widths[c] | c in circuits]); % index of the circuit with the biggest area

array [circuits] of var int: actual_widths = [(if rotations[i] then heights[i] else widths[i] endif) | i in circuits]; % actual heights after rotation or not
array [circuits] of var int: actual_heights = [(if rotations[i] then widths[i] else heights[i] endif) | i in circuits]; % actual widths after rotation of not

% Implied constraints
constraint forall (i in circuits) (x[i] <= w-actual_widths[i])::domain;
constraint forall (i in circuits) (y[i] <= plate_height-actual_heights[i])::domain;

% Implied constraints
constraint cumulative(x, actual_widths, actual_heights, w)::domain;
constraint cumulative(y, actual_heights, actual_widths, plate_height)::domain;

% No-overlapping constraits
constraint diffn(x, y, actual_widths, actual_heights)::domain;

% Simmetry breaking constraints
% Largest circuit in position (0,0)
constraint symmetry_breaking_constraint(x[big_circuit_idx] = 0 /\ y[big_circuit_idx] = 0 );

constraint forall(i in 1..n-1, j in 2..n where i<j) (
  (widths[i]==widths[j] /\ heights[i]==heights[j]) -> lex_less([x[i], y[i]], [x[j], y[j]]) );

% Avoid rotation of square circuits
constraint symmetry_breaking_constraint(
    forall (i in circuits) (if actual_heights[i] == actual_widths[i] then rotations[i] = 0 endif)
);

% Search
ann: search_ann;
%ann: search_bool_ann;

%search_bool_ann = bool_search(rotations, input_order, indomain_min, complete);

search_ann = int_search([plate_height], input_order, indomain_min, complete);
%search_ann = int_search([plate_height], dom_w_deg, indomain_min, complete);
%search_ann = int_search([plate_height], first_fail, indomain_min, complete);

ann: restart_ann;
%restart_ann = restart_luby(100);
%restart_ann = restart_geometric(1.5, 100);

solve
    ::search_ann
    %:: search_bool_ann
    %:: restart_ann
  minimize plate_height;