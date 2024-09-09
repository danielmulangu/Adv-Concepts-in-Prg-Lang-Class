% of 3 squares

%input positive integer n.

#const n=30.

three(N, I, J, K) :- N=1..n, I=0..N, J=0..N, K=0..N, N=I**2 + J**2 +K**2, I>=J>=K.


 #show three/4.
