father(john, sam).
mother(alice, sam).
father(john, isabella).
mother(alice, isabella).
gender(john, male).
gender(sam, male).
gender(alice, female).

parent(X, Y) :- father(X, Y).
parent(X, Y) :- mother(X, Y).



child(X, Y) :- father(Y, X).
child(X, Y) :- mother(Y, X).



grandchild(X, Y) :- parent(Y, Z), parent (Z, X).


sibling(X, Y) :- parent(Z,X), parent(Z, Y), X!=Y.

addition("5+2", 5+2).
