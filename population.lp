% instance
population(france,65).
population(italy,61).
population(germany,83).
population(uk,64). 

% encoding
large(C) :- population(C,S1), population(uk,S2), S1 > S2.
#show large/1.