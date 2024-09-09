% Factorial of n.
% input: nonnegative integer n.

#const n=10

% achieved: fac/2 = { (0,0!), ... (n,n!)}.
%fact(0,1) :- fact(N,N-1), N>0.
fact(X,Y):- X=1..n, Y=X*Z, fact(X-1,Z).


% achieved: fac/1 = { n! }.

#show fac/1.

