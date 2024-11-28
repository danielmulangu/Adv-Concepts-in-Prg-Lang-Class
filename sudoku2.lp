% Sudoku Solver
%
% Hints:
% For subgrid of size n, subgrids can be identified by labels 1..n*n
% A cell (x,y) can be mapped to the subgrid labeled 1+(((x-1)/n)*n+(y-1)/n)

% Your implementation please...
%by Daniel M. Kaseya

% Define the size of the Sudoku grid the rows, columns, and values of the 9x9 sudoku
row(1..9).
column(1..9).
size(1..9).

% Each cell gets exactly one value
1 { sudoku(X, Y, N) : size(N) } 1 :- row(X), column(Y).

% Ensure each value appears exactly once in each row
:- sudoku(X, A, N), sudoku(X, B, N), A != B.

% Ensure each value appears exactly once in each column
:- sudoku(C, Y, N), sudoku(D, Y, N), C != D.

% Define the subgrid for each cell(X,Y)
subgrid(X, Y, N) :- row(X), column(Y), N = 1+ (((X-1) / 3) * 3 + (Y-1) / 3).

% Ensure each value appears exactly once in everry subgrid
:- sudoku(C, A, N), sudoku(D, B, N), subgrid(C, A, S), subgrid(D, B, S), (C, A) != (D, B).

% Predefined initial values in the instance folder
sudoku(X, Y, N) :- initial(X, Y, N).

% Ensure the predefined from the instances are respected
:- sudoku(X, Y, N), initial(X, Y, M), N != M.

% Show the solution
#show sudoku/3.