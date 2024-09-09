%comments

%coprime example

#const lower =2.
#const upper =20.
#k= 2.

composite(N) :- N = lower..upper, I=2..N-1, N\I=0.

Prime(N) :- N= lower..upper, N !=1, not composite(N).