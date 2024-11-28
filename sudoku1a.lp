% Sudoku Solver
%
% Hints:
% For subgrid of size n, subgrids can be identified by labels 1..n*n
% A cell (x,y) can be mapped to the subgrid labeled 1+(((x-1)/n)*n+(y-1)/n)

% Your implementation please...
%by Daniel M. Kaseya

% Define the rows, columns, and values of the 4x4 sudoku
row(1..4).
column(1..4).
size(1..4).
n(2).  % Size of the subgrid (2x2)

% Each cell gets exactly one value
1 { sudoku(X, Y, Z) : size(Z) } 1 :- row(X), column(Y).

% Ensure each value appears exactly once in each row
:- sudoku(X, A, Z), sudoku(X, B, Z), A != B.

% Ensure each value appears exactly once in each column
:- sudoku(C, Y, Z), sudoku(D, Y, Z), C != D.

% Mapping of the subgrid for a cell (X, Y)
subgrid(X, Y, Label) :- 
    Label = 1 + (((X - 1) / n) * n + ((Y - 1) / n)).

% Predefined initial vallues in the instance folder
sudoku(X, Y, Z) :- initial(X, Y, Z).

% Ensure the predefined from the instances are respected
:- sudoku(X, Y, Z), initial(X, Y, M), Z != M.


% Show the solution
#show sudoku/3.
