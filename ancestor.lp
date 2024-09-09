%compute the parents of a person given its name


%input: name of a person



%     a database of facts containing the father and mother relation


parent(X,Y) :- father(X,Y)
parent(X,Y) :- mother(X,Y)

%achieved: parent(X,Y) iff X is a parent of Y

parent(X) :-parent(X, name).

%achieved: parent(X) iff X is the parent of name

#show parent/1.