%comments

%coprime example

#const lower =2.
#const upper =20.
#const k= 2.

noncoprime(N) :-  N = lower..upper, I=2..N, N\I=0, k\I=0.

coprime(N) :- N =lower..upper, N !=1, not noncoprime(N).

#show coprime /1.
