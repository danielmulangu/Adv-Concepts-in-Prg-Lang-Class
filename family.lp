father(john, sam).
mother(alice, sam).
father(john, isabella).
mother(alice, isabella).
gender(john, male).
gender(sam, male).
gender(alice, female).

parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).

child(X, Y) :- father(Y, X)
child(X, Y) :- mother(Y, X)


// x is the parent of y if x is the father of Y.
//x is the parent of Y if X is the mother of Y.

// x is the son of y if Y is the father of x.
//x is the daughter of Y if Y is the mother of X.