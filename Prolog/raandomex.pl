father(albero,carlo).
father(albero,giovanna).
father(marco,giulio).
mother(franca,carlo).
mother(franca,giovanna).
mother(maria,giulio).
male(albero).
male(carlo).
female(giovanna).
male(marco).
male(giulio).
female(franca).
female(maria).
parent(X,Y) :- father(X,Y).
parent(X,Y) :- mother(X,Y).
diff(X,Y) :- X \= Y.

isMother(X):-
    mother(X,_).
isFather(X):-
    father(X,_).
isSon(X):-
    male(X),
    parent(_,X).

% flatten(L,LF) to flatten a list L into LF

flatten([], []).  % Caso base: una lista vuota resta vuota.

flatten([X|T], L) :-  
    flatten(X, FX),   % Se X è una lista, la appiattiamo
    flatten(T, FT),   % Ricorsione sulla coda
    conc(FX, FT, L).  % Concatenazione senza append/3

flatten(X, [X]) :-  
    X \= [], X \= [_|_].  % Se X non è una lista, è un atomo e lo restituiamo in una lista

% Definiamo la concatenazione manualmente senza usare append/3
conc([], L, L).  
conc([H|T], L, [H|R]) :- conc(T, L, R). 


%find the last element of a list

lastElement([X|[]],X).
lastElement([H|T],E):-
    lastElement(T,E).


penultimo([X|T],M):-
    T=[F|[]],
    M=X.

penultimo([X|T],M):-
    penultimo(T,M).


element_at(E,[H|T],P):-
    P=1,
    E=H.
element_at(E,[H|T],P):-
    K is P-1,
    element_at(E,T,K).

numberElement([],0).
numberElement([H|T],X):-
    numberElement(T,K),
    X is K+1.

reverseList([],[]).
reverseList([H|[]],L):-
    L=[H|[]].
reverseList([H|T],L):-
    reverse(T,PL),
    L=[PL|H].


palindrome([]).
palindrome(X):-
    reverse(X,Y),
    X=Y.


my_flatten([], []).  % Caso base: una lista vuota resta vuota.
my_flatten(X,L):-
    \+ is_list(X),
    L=[X].
my_flatten([H|T],L):-
    my_flatten(H,HF),
    my_flatten(T,TF),
    append(HF,TF,L).

eliminateDuplicate([],[]).
eliminateDuplicate([H|T],L):-
    member(H,T),
    !,
    eliminateDuplicate(T,PL),
    L=PL.
eliminateDuplicate([H|T],L):-
    eliminateDuplicate(T,PL),
    L=[H|PL].
    


pack([], []).  
pack([H|T], [ [H|Ts] | R ]) :- 
    take_same(H, T, Ts, Rest),
    pack(Rest, R).

take_same(H, [H|T], [H|Ts], Rest) :-  
    take_same(H, T, Ts, Rest).
take_same(H, [X|T], [], [X|T]) :-  
    H \= X.
take_same(_, [], [], []).

/**
 *  H -> valore da raccogliere
 * [H|T] -> lista su cui si opera
 * [H|Ts] -> lista con elementi uguali a H
 * Rest -> resto della lista
 * 
 * */

%insertAt(E,L,Pos,NewList)
insertAt(X,L,1,N):-
    append([X],L,N).

insertAt(X,[H|T],P,N):-
    P>1,
    P1 is P-1,
    insertAt(X,T,P1,N2),
    append([H],N2,N).
 