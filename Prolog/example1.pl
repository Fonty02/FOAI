cousin(X,Y) :- 
    parent(Z,X), 
    parent(W,Y), 
    sibling(Z,W).  %non devo aggiungere X\=Y perché non è necessario, se i genitori non sono la stessa persona, i figli non possono essere la stessa persona

sibling(X,Y) :- 
    parent(Z,X), 
    parent(Z,Y), 
    X \= Y.

brother(X,Y) :- 
    sibling(X,Y),
    male(X).   %per efficienza conviene prima controllare se sono fratelli e poi controllare se X è maschio, piuttosto che controllare prima se X è maschio e poi se sono fratelli.

sister(X,Y) :-
    sibling(X,Y),
    female(X).

parent(carlo,stefano).
parent(giovanni,carlo).
parent(alfonso,marcella).
parent(anna,stefano).
parent(francesco,alfonso).
parent(lucia,alfonso).
parent(iginia,carlo).
parent(alfonso,carlo).
parent(iginia,marcella).
parent(pietro,francesco).
parent(giovanni,anna).
parent(immacolata,anna).


%Exercise : Extend with others family relationsShips like uncle, aunt, nephew, niece, grandparent, grandchild, etc.




