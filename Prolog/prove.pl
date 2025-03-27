%?-write('What''s  your name:' ),read(Name),write('Hello, '),write(Name),write('!'),nl.  %il nome tra ' ' e non tra " "



/**
 *    ?- setof(X,ancestor(X,kevin),Z), member(Y,Z).
Y = john,
Z = [john,mary,robert,susan] ? 

Y è l head 
; per gli altri
**/


%DEFINE SOME USEFULL code

%prodotto cartesiano tra liste prod(L1,L2,L).

prod([],_L2,[]).
prod([H|T],L2,L) :-
    comb(L2,H,PL),
    prod(T,L2,RL),
    app(PL,RL,L).

comb([],_E,[]).
comb([H|T],E,[[E,H] | PL]) :-
    comb(T,E,PL).


app([],L,L).
app(L,[],L).  %usefull for efficiency, but useless in general. Very special case
app([H|T],L,[H|PL]) :-
    app(T,L,PL).

%SOOO
prod2(L1,L2,L):-
    setof([X,Y],(member(X,L1),member(Y,L2)),L).