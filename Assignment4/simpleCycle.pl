:- dynamic node/2.
:- dynamic arc/4.
:- dynamic edge/2. % Helper predicate for faster edge lookup

% --- Main Predicate ---

find_simple_cycles(SimpleCycles) :-
    write('Initializing... Generating edge/2 facts...\n'), nl,
    generate_edges, % Create helper edge/2 facts for efficiency
    write('Finding all elementary cycles...\n'), nl,
    find_all_elementary_cycles(ElementaryCycles), % Find all elementary cycles
    length(ElementaryCycles, NumElementary),
    write('Found '), write(NumElementary), write(' elementary cycles.\n'), nl,
    % *** Print elementary cycles if found ***
    ( NumElementary > 0 ->
        print_cycles_list('Elementary Cycles Found (before filtering):', ElementaryCycles),
        write('Filtering for "simple" cycles (this may take time)...\n'), nl,
        filter_simple_cycles(ElementaryCycles, NormalizedSimpleCycles),
        % Use setof to ensure uniqueness based on normalized representation
        ( setof(NormCycle, Member^(member(Member, NormalizedSimpleCycles), NormCycle = Member), SimpleCycles) ->
            length(SimpleCycles, NumSimple),
            write('Found '), write(NumSimple), write(' simple cycles.\n'), nl,
            % *** ADDED: Print final simple cycles ***
            print_cycles_list('Simple Cycles Found (final result):', SimpleCycles)
        ;   write('Found 0 simple cycles after filtering.\n'), nl, % No simple cycles found
            SimpleCycles = []
        )
    ;   write('No elementary cycles to filter.\n'), nl, % Already printed "Found 0 elementary cycles."
        SimpleCycles = [] % No elementary cycles found
    ).


% --- Generate Helper Edges ---
generate_edges :-
    retractall(edge(_, _)),
    forall(arc(_, _, N, M), assertz(edge(N, M))).

% --- Find Elementary Cycles ---
find_all_elementary_cycles(Cycles) :-
    findall(N, node(N, _), Nodes),
    find_cycles_starting_from_nodes(Nodes, Cycles).

find_cycles_starting_from_nodes(Nodes, Cycles) :-
    findall(
        Cycle,
        (member(StartNode, Nodes),
         edge(StartNode, Neighbor),
         dfs_find_cycle(Neighbor, StartNode, [Neighbor, StartNode], Cycle)
        ),
        Cycles
    ).

dfs_find_cycle(CurrentNode, TargetNode, PathSoFar, Cycle) :-
    edge(CurrentNode, NextNode),
    (   NextNode == TargetNode ->
        Cycle = [TargetNode | PathSoFar]
    ;   \+ memberchk(NextNode, PathSoFar),
        dfs_find_cycle(NextNode, TargetNode, [NextNode | PathSoFar], Cycle)
    ).

% --- Filter for "Simple" Cycles ---
filter_simple_cycles([], []).
filter_simple_cycles([Cycle | RestCandidates], [NormalizedCycle | SimpleRest]) :-
    is_simple_cycle(Cycle),
    !,
    normalize_cycle(Cycle, NormalizedCycle),
    filter_simple_cycles(RestCandidates, SimpleRest).
filter_simple_cycles([_Cycle | RestCandidates], SimpleRest) :-
    filter_simple_cycles(RestCandidates, SimpleRest).

is_simple_cycle(Cycle) :-
    reverse(Cycle, ForwardCycle),
    ForwardCycle = [Start | PathNodes],
    append(PathNodesWithoutEnd, [Start], PathNodes),
    NodesInCycle = [Start | PathNodesWithoutEnd],
    check_all_pairs_shortest_path(NodesInCycle, NodesInCycle).

check_all_pairs_shortest_path([], _).
check_all_pairs_shortest_path([N1 | RestN1], OriginalCycleNodes) :-
    check_pairs_from_node(N1, OriginalCycleNodes, OriginalCycleNodes),
    check_all_pairs_shortest_path(RestN1, OriginalCycleNodes).

check_pairs_from_node(_, [], _).
check_pairs_from_node(N1, [N2 | RestN2], OriginalCycleNodes) :-
    ( N1 == N2 -> true
    ; get_cycle_distance(N1, N2, OriginalCycleNodes, CycleDist),
      shortest_path_length(N1, N2, ShortestDist),
      ( ShortestDist == -1 -> % If no path exists outside the cycle
         (CycleDist > 0 -> true ; !, fail) % It's simple if it's a valid cycle path
      ; ShortestDist >= CycleDist % The shortest path must be >= the cycle path
      )
    ),
    !,
    check_pairs_from_node(N1, RestN2, OriginalCycleNodes).
check_pairs_from_node(_, _, _) :- !, fail. % Removed failure print for cleaner output

get_cycle_distance(NodeA, NodeB, CycleNodes, Distance) :-
    nth0(IndexA, CycleNodes, NodeA),
    nth0(IndexB, CycleNodes, NodeB),
    length(CycleNodes, Len),
    ( IndexB >= IndexA ->
        Distance is IndexB - IndexA
    ;
        Distance is Len - IndexA + IndexB
    ).

% --- Find Shortest Path (BFS) ---
shortest_path_length(Start, End, Length) :-
    bfs([[Start, 0]], End, [Start], Length),
    !.
shortest_path_length(_, _, -1). % Simplified failure case

bfs([], _, _, _) :- !, fail.
bfs([[Target, Length] | _], Target, _, Length) :- !.
bfs([[Current, Dist] | RestQueue], Target, Visited, Length) :-
    findall(Next, (edge(Current, Next), \+ member(Next, Visited)), Neighbors),
    NewDist is Dist + 1,
    add_neighbors_to_queue(Neighbors, NewDist, RestQueue, NewQueue),
    append(Visited, Neighbors, NewVisited),
    list_to_set(NewVisited, UniqueVisited), % list_to_set is from SWI-Prolog library(lists)
    bfs(NewQueue, Target, UniqueVisited, Length).

add_neighbors_to_queue(Neighbors, Distance, CurrentQueue, NewQueue) :-
    findall([N, Distance], member(N, Neighbors), NeighborEntries),
    append(CurrentQueue, NeighborEntries, NewQueue).

% --- Normalize Cycles for Uniqueness ---

% normalize_cycle(+RawCycle, -NormalizedNodeList)
% Input RawCycle: [a, d, c, b, a] (reverse order from DFS)
% Output NormalizedNodeList: [a, b, c, d] (forward order, starts from minimum, no duplicate end node)
normalize_cycle(RawCycle, NormalizedNodeList) :-
    RawCycle = [Start | RevPathNodes], % E.g., Start=a, RevPathNodes=[d, c, b, a]
    reverse(RevPathNodes, [_ | ForwardPathNodes]), % E.g., ForwardPathNodes=[b, c, d] (removes the last 'a')
    ForwardCycleNodes = [Start | ForwardPathNodes], % E.g., [a, b, c, d]
    find_min_node(ForwardCycleNodes, MinNode),
    rotate_list_to_start_with(ForwardCycleNodes, MinNode, NormalizedNodeList). % Output is already the normalized list

find_min_node([M], M) :- !.
find_min_node([H | T], Min) :-
    find_min_node(T, MinTail),
    ( H @< MinTail -> Min = H ; Min = MinTail ).

rotate_list_to_start_with(List, Element, RotatedList) :-
    append(Before, [Element | After], List),
    !,
    append([Element | After], Before, RotatedList).
rotate_list_to_start_with(List, _, List). % If Element is already the first, list remains the same


% *** Helper Predicate for Printing ***
% print_cycles_list(+Header, +ListOfCycles)
print_cycles_list(_, []) :- !. % Print nothing if the list is empty
print_cycles_list(Header, ListOfCycles) :-
    writeln(Header),
    forall(member(Cycle, ListOfCycles), (write('  '), writeln(Cycle))).


% --- Example Data (ensure these are uncommented) ---

node(a, type1).
node(b, type1).
node(c, type1).
node(d, type1).
node(e, type1). % Node to create a shorter path

% Cycle a -> b -> c -> d -> a
arc(1, t, a, b).
arc(2, t, b, c).
arc(3, t, c, d).
arc(4, t, d, a).

% Cycle b -> e -> d -> c -> b
arc(5, t, b, e).
arc(6, t, e, d).
arc(7, t, d, c).
arc(8, t, c, b).

% Shorter path making the first cycle NOT simple: a -> d
arc(9, t, a, d). % Makes distance a->d = 1, while in the cycle it's 3