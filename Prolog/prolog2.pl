write('What''s your name: '),read(Name),write('Hello, '),write(Name),write('!'),nl.
# if i want to enter the name with a capial first letter i have to write it between ''

open(pippo, write, S),write(S,ciao),writeln(S,pippo),portray_clause(S,(h :- b,c,d,e)),close(S).
open(pippo,read,S),read(S,X),close(S).
open(pippo,read,S),read(S,(H :- B)),close(S).

open(pippo,read,S),read(S,(H :- B)),close(S), B = (F, X, _), F = ..[P].
open(pippo,read,S),read(S,(H :- B)),close(S), B = (F, X, _), functor(F, FN, FA).
functor(F, p, 3).
P = .. [f,X,a,q(r)].
P = .. [f,X,a,q(r)], call(P).
P = .. [f,X,a,q(r)], P.
P = .. [f,X,a,q(r)], /+ P.
asserta((naf(X) :- X, !, fail)).
assertz(naf(_)).
# clause(H,B) doesn't work, the head has to be specified
clause(naf(A), B) ? .
P = .. [f,X,a,q(r)], naf(P).
assert(p(a)).
p(X).
naf(p(X)).

# Functor
functor(p(a,X),F,A).
functor(A,p,2).
functor(A,p,2),assert(A).


#######
[family].
setof(X,ancestor(X,stefano),Z).
setof(X,ancestor(X,stefano),Z),member(pietro,Z).    # member is not defined so we use a library
use_module(library(lists)).
setof(X,ancestor(X,stefano),Z),member(pietro,Z).
setof(X,ancestor(X,stefano),Z),member(Y,Z).
bagof(X,ancestor(X,stefano),Z). # includes duplicates
findall(X,ancestor(X,stefano),Z). # doesn't include duplicates but is unordered
setof(X,parent(marcella,X),Z).  # if marcella has no children it returns false because it fails
bagof(X,parent(marcella,X),Z).  # also fails
findall(X,parent(marcella,X),Z). # returns []
setof(X,parent(alfonso,X),Z). 
setof([Y,X],parent(Y,X),Z).
setof(X,parent(Y,X),Z). # people who are son of someone, but we are locking Y
# to avoid this:
setof(X,Y^parent(Y,X),Z).
findall(X,parent(Y,X),Z).
bagof(X,parent(Y,X),Z).
setof(c(X,Y),parent(Y,X),Z).
setof(X,Y^parent(Y,X),Z),nth(3,Z,E).    # who is the 3rd (son of someone) element of this list
setof(X,Y^parent(Y,X),Z),nth(3,Z,E,R). # R is the rest of the list afther removing the third element
setof(X,Y^parent(Y,X),Z),nth(3,L,pippo,Z).  # L has pippo as the third element of the list and the rest of the list is Z

# how to enumerate the items in the list
setof(X,Y^parent(Y,X),Z),nth(N,Z,E). # N is the index of the element in the list, returns the element in position N of the list Z
nth(4,L,_).
nth(4,L,a). # a list where the 4th element is a
nth(3, [a,b,c,d], c)    # yes
nth(3, [a,b,c,d], a)    # no

# dictionary:
[1-pippo,2-ciccio,3-gino] = D, member(2-X,D).   # returns the value associated with key 2 in this dictionary (ciccio)
[1-pippo,2-ciccio,3-gino] = D, memberchk(2-X,D).   # avoids backtracking, stops after finding the first solution


3 = X.
3 == X.
X = 3
X == 3
X <= 3.   # error
4 \== 3.
X is 2 + 2, X > 3.
X is 2 + 2, X < 3.
X is (3 + 2)/sqrt(16).
X is X + 1.   # error
# to do this:
assert(counter(0)).
counter(N). # reads the value of the counter (N = 0)
counter(N),retract(counter(N)),assert(counter(N+1)). # increments the counter
counter(X) # reads the value of the counter (X = 0+1)

assert(counter(0)).
counter(N),retract(counter(N)),N1 is N + 1,assert(counter(N1)).
counter(X).
