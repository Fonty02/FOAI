/*
def fattoriale(n):
    if n == 0:
        return 1
    return n * fattoriale(n - 1)

print(fattoriale(5))  # Output: 120
*/

fattoriale(0, 1).
fattoriale(N, F) :- 
    N > 0,
    N1 is N - 1,
    fattoriale(N1, F1),
    F is N * F1.



/*
def pari(n):
    return n % 2 == 0

print(pari(4))  # Output: True
print(pari(5))  # Output: False
*/

pari(0).
pari(X):-
    X>=2,
    X1 is X-2,
    pari(X1).


dispari(1).
dispari(X):-
    X>=3,
    X1 is X-2,
    dispari(X1).


/*

def massimo(a, b):
    return a if a > b else b

print(massimo(10, 20))  # Output: 20

*/


massimo(A,B,C):-
    A>=B,
    C is A.

massimo(A,B,C):-
    A<B,
    C is B.

/*
def potenza(base, esp):
    if esp == 0:
        return 1
    return base * potenza(base, esp - 1)

print(potenza(2, 3))  # Output: 8

*/

potenza(B,0,X):- 
    X is 1.

potenza(Base,Esponente,X):-
    Esponente>0,
    E1 is Esponente-1,
    potenza(Base,E1,X1),
    X is Base*X1.



/*
def conta_pari(n):
    count = 0
    i = 1
    while i <= n:  # Ciclo while
        if i % 2 == 0:  # Condizione if
            count += 1
        i += 1
    return count

print(conta_pari(10))  # Output: 5 (2, 4, 6, 8, 10)
*/


contaPari(0,1).
contaPari(N,Result):-
    N>0,
    pari(N),
    N1 is N-1,
    contaPari(N1,R1),
    Result is R1+1.

contaPari(N,Result):-
    N>0,
    dispari(N),
    N1 is N-1,
    contaPari(N1,R1),
    Result is R1+0. 