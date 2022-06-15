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

% Other variables
int: max_height = sum(heights); % Plate height upper bound
int: min_height = max(heights); % Plate height lower bound

int : big_circuit_idx = arg_max([heights[c]*widths[c] | c in circuits]); % index of the circuit with the biggest area


% Main constraints
constraint forall (i in circuits) (x[i] <= w-widths[i])::domain;
constraint forall (i in circuits) (y[i] <= plate_height-heights[i])::domain;

% Implied constraints
constraint cumulative(x, widths, heights, plate_height)::domain;
constraint cumulative(y, heights, widths, w)::domain;
% No-overlapping constraits
constraint diffn(x, y, widths, heights)::domain;

% Simmetry breaking constraints
% Ordering constraints between same size rectangles
constraint forall(i in 1..n-1, j in 2..n where i<j) (
  (widths[i]==widths[j] /\ heights[i]==heights[j]) -> lex_less([x[i], y[i]], [x[j], y[j]]) );

% Highest circuit in position (0,0)
constraint symmetry_breaking_constraint(x[big_circuit_idx] = 0 /\ y[big_circuit_idx] = 0);


% Search
ann: search_ann;

search_ann = int_search([plate_height], input_order, indomain_min, complete);
%search_ann = int_search([plate_height], dom_w_deg, indomain_min, complete);
%search_ann = int_search([plate_height], first_fail, indomain_min, complete);


%ann: restart_ann;
%restart_ann = restart_luby(100);
%restart_ann = restart_geometric(1.5, 100);

solve
  :: search_ann
  %:: restart_ann
  minimize plate_height;

%output [
%  "obj: ", show(plate_height), "\n",
%  "Solution: ", 
%  show([x[c] | c in circuits]),  
%  show([y[c] | c in circuits])
%];
