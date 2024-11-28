% Sudoku Solver
%
% Hints:
% For subgrid of size n, subgrids can be identified by labels 1..n*n
% A cell (x,y) can be mapped to the subgrid labeled 1+(((x-1)/n)*n+(y-1)/n)

% Your implementation please...
%by Daniel M. Kaseya

% Define the size of the Sudoku grid, the rows, columns, and values of the 4x4 sudoku
row(1..4).
column(1..4).
size(1..4).


% Each cell gets exactly one value
1 { sudoku(X, Y, Z) : size(Z) } 1 :- row(X), column(Y).

% Ensure each value appears exactly once in each row
:- sudoku(X, A, Z), sudoku(X, B, Z), A != B.

% Ensure each value appears exactly once in each column
:- sudoku(C, Y, Z), sudoku(D, Y, Z), C != D.

% Define the subgrid for each cell
% Cells (1,1), (1,2), (2,1), (2,2) → Subgrid 1
% Cells (1,3), (1,4), (2,3), (2,4) → Subgrid 2
% Cells (3,1), (3,2), (4,1), (4,2) → Subgrid 3
% Cells (3,3), (3,4), (4,3), (4,4) → Subgrid 4
subgrid(X, Y, G) :- 
    row(X), column(Y),
    G = 1 + (((X - 1) / 2) * 2 + ((Y - 1) / 2)).
 %Removed the contrainst just as the professor suggested and it should be all working now.

% Predefined initial values in the instance folder
sudoku(X, Y, Z) :- initial(X, Y, Z).

% Ensure the predefined from the instances are respected
:- sudoku(X, Y, Z), initial(X, Y, M), Z != M.

% Show the solution
#show subgrid/3.
#show sudoku/3.