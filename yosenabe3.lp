%% Your code here

%cell(X,Y).         % the cell (X,Y) belongs to the grid
%area(X,Y,A).       % the cell (X,Y) belongs to area A
%number(X,Y,N).     % the cell (X,Y) initially contains number N
%goal(A,G).         % the goal number of area A is number G

%target(X,Y,XX,YY).  % the number in the cell (X,Y) is moved to the cell (XX,YY)

1{target(X,Y,XX,YY) : area(XX,YY,A)}1 :- number(X,Y,N).

:- target(X,Y,XX,YY), X!=XX, Y!=YY.

:- area(_, _, A), not {target(_, _, XX, YY) : area(XX, YY, A)} >= 1.

path(X..XX, Y..YY,X,Y) :- target(X,Y,XX,YY).
path(XX..X, Y..YY,X,Y) :- target(X,Y,XX,YY).
path(X..XX, YY..Y,X,Y) :- target(X,Y,XX,YY).
path(XX..X, YY..Y,X,Y) :- target(X,Y,XX,YY).

:- path(X,Y,XX,YY), path(X,Y,A,B), A!= XX.
:- path(X,Y,XX,YY), path(X,Y,A,B), B!= YY. 



#show target/4.