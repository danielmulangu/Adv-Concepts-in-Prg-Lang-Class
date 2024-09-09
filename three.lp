% of 3 squares

%input positive integer n.

#const n=30.

three(N) :- N=1..n, I=0..N, J=0..N, K=0..N, N=I**2 + J**2 +K**2.

more_than_three(N) :- N = 1..n, not three(N).

#show more_than_three/1.
			