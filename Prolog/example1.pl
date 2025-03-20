%-----------------------------------------------
% Example Prolog Family Tree
%-----------------------------------------------

ancestor(X, Y) :-
    parent(X, Y).
ancestor(X, Y) :-
    parent(Z, Y),
    ancestor(X, Z).


related(X, Y) :-
    ancestor(Z, X),
    ancestor(Z, Y).



sibling(X, Y) :-
    parent(Z, X),
    parent(Z, Y),
    X \= Y.


cousin(X, Y) :-
    parent(Z, X),
    parent(W, Y),
    sibling(Z, W).


brother(X, Y) :-
    sibling(X, Y),
    male(X).


sister(X, Y) :-
    sibling(X, Y),
    female(X).


mother(X, Y) :-
    parent(X, Y),
    female(X).


father(X, Y) :-
    parent(X, Y),
    male(X).


child(X, Y) :-
    parent(Y, X).


grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).


grandchild(X, Y) :-
    parent(Z, X),
    parent(Y, Z).


aunt(X, Y) :-
    sibling(X, Z),
    parent(Z, Y),
    female(X).


uncle(X, Y) :-
    sibling(X, Z),
    parent(Z, Y),
    male(X).


nephew(X, Y) :-
    sibling(Y, Z),
    parent(Z, X),
    male(X).


niece(X, Y) :-
    sibling(Y, Z),
    parent(Z, X),
    female(X).


mother_in_law(X, Y) :-
    parent(X, Z),
    married(Z, Y),
    female(X).


father_in_law(X, Y) :-
    parent(X, Z),
    married(Z, Y),
    male(X).

% Facts



parent(john, mary).
parent(john, michael).
parent(susan, mary).
parent(susan, michael).
parent(mary, lisa).
parent(mary, kevin).
parent(robert, lisa).
parent(robert, kevin).


male(david).
male(steve).
male(robert).
male(kevin).
male(john).
male(michael).


female(susan).
female(mary).
female(diane).
female(lisa).

married(john, susan).
married(mary, david).






% Albero genealogico:
% Generazione 1:
%    john (maschio) e susan (femmina) sono sposati.
%       |- Figli: mary e michael.
%
% Generazione 2:
%    mary (figlia di john e susan) è sposata con david.
%       |- Con mary:
%             - Con robert (genitore alternativo dei figli) si hanno: lisa (femmina) e kevin (maschio).
%             - Con david (marito di mary) insieme a diane si ha: steve (maschio).
%

