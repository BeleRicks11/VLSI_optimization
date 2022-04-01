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

% Implied constraints
constraint forall (i in circuits) (x[i] <= w-widths[i])::domain;
constraint forall (i in circuits) (y[i] <= plate_height-heights[i])::domain;

constraint forall (i in circuits) (x[i]+widths[i] <= w /\ y[i]+heights[i] <=  plate_height);

constraint cumulative(x, widths, heights, w)::domain;
constraint cumulative(y, heights, widths, plate_height)::domain;
% No-overlapping constraits
constraint diffn(x, y, widths, heights)::domain;

% Simmetry breaking constraints
% rows and column symmetry
constraint forall (i,j in circuits where i < j) ((widths[i]+widths[j]==w /\ y[1]==y[2]) -> x[1] < x[2]);
constraint forall (i,j in circuits where i < j) ((heights[i]+heights[j]==plate_height /\ x[1]==x[2]) -> y[1] < y[2]);



% Search
ann: search_ann;
search_ann = int_search([plate_height], dom_w_deg, indomain_random);

solve
  :: search_ann
  minimize plate_height;

output [
  "obj: ", show(plate_height), "\n",
  "Solution: ", 
  show([x[c] | c in circuits]),
  show([y[c] | c in circuits])
];

