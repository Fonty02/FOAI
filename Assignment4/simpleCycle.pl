:- dynamic node/2. % Stores node information, e.g., node(node_id, type_label). Made dynamic for flexible test case setup.
:- dynamic arc/4.  % Stores directed graph arcs, e.g., arc(arc_id, type_label, source_node, destination_node). Dynamic for test setups.
:- dynamic edge/2. % A simplified 'edge(SourceNode, DestinationNode)' relation. This is derived from arc/4 for faster lookups during graph traversal. Dynamic.

% --- Main Execution Block ---
% This is the primary entry point of the program.
main :-
    write('Select test case (1, 2, 3, or 4): '), % Prompt the user to choose a predefined graph.
    read(TestCaseNumber),
    (   setup_test_graph(TestCaseNumber) % Attempt to load the graph data for the chosen test case.
    ->  find_simple_cycles(SimpleCyclesList), % If graph setup is successful, proceed to find simple cycles.
        write('SimpleCycles = '), writeln(SimpleCyclesList) % Display the identified simple cycles.
    ;   write('Unknown test case!'), nl % Handle invalid test case selection.
    ),
    halt. % Terminate the program.

% --- Utility: Generate simplified edge/2 facts from arc/4 ---
% This predicate populates the edge/2 relation from the arc/4 facts.
% The edge/2 relation simplifies graph traversal by omitting arc ID and type,
% focusing only on the source-destination relationship.
generate_edges_from_arcs :-
    retractall(edge(_, _)), % Clear any pre-existing edge/2 facts to ensure a clean state.
    forall(arc(_ArcID, _ArcType, SourceNode, DestinationNode), % For every arc defined in the graph...
           assertz(edge(SourceNode, DestinationNode))). % ...assert a corresponding edge/2 fact.

% --- Default Node Declarations ---
% Provides default node/2 facts. These are used by find_all_elementary_cycles
% to get a list of all nodes from which to start cycle searches.
% This is a fallback in case test setups (arc/4 facts) involve nodes
% not explicitly declared via node/2.
node(a, type_default).
node(b, type_default).
node(c, type_default).
node(d, type_default).
node(e, type_default).
node(f, type_default).
node(g, type_default).

% --- Test Case Data Setup ---
% These predicates define various graph structures for testing the cycle detection algorithm.
% Each setup_test_graph/1 clause retracts previous arc/4 data before asserting its specific graph structure.

setup_test_graph(1) :-
    retractall(arc(_,_,_,_)),
    % Test Case 1: Defines a simple triangular cycle: a -> b -> c -> a.
    assertz(arc(t1_ab, type_edge, a, b)),
    assertz(arc(t1_bc, type_edge, b, c)),
    assertz(arc(t1_ca, type_edge, c, a)).

setup_test_graph(2) :-
    retractall(arc(_,_,_,_)),
    % Test Case 2: Defines a square (a-b-c-d-a) with a "chord" (b-d).
    % Expected simple cycles: a-b-d-a and b-c-d-b.
    % The cycle a-b-c-d-a is elementary, but not simple due to the b-d chord,
    % as the path b-d is shorter than b-c-d.
    assertz(arc(t2_ab, type_edge, a, b)),
    assertz(arc(t2_bc, type_edge, b, c)),
    assertz(arc(t2_cd, type_edge, c, d)),
    assertz(arc(t2_da, type_edge, d, a)),
    assertz(arc(t2_bd_chord, type_edge, b, d)). % This arc acts as a chord.

setup_test_graph(3) :-
    retractall(arc(_,_,_,_)),
    % Test Case 3: A graph with a 2-node cycle (a-b-a) and two separate triangular cycles.
    % Expected simple cycles: a-b-a, c-d-e-c, d-f-g-d.
    assertz(arc(t3_ab, type_edge, a, b)), % Part of the 2-node cycle
    assertz(arc(t3_ba, type_edge, b, a)), % Completes the 2-node cycle
    assertz(arc(t3_cd, type_edge, c, d)), % Triangle 1
    assertz(arc(t3_de, type_edge, d, e)),
    assertz(arc(t3_ec, type_edge, e, c)),
    assertz(arc(t3_df, type_edge, d, f)), % Triangle 2
    assertz(arc(t3_fg, type_edge, f, g)),
    assertz(arc(t3_gd, type_edge, g, d)).

setup_test_graph(4) :-
    retractall(arc(_,_,_,_)),
    % Test Case 4: A more complex graph with overlapping cycles and a chord.
    % Cycle 1 (potential): a -> b -> c -> d -> a
    assertz(arc(t4_ab, type_edge, a, b)),
    assertz(arc(t4_bc, type_edge, b, c)),
    assertz(arc(t4_cd, type_edge, c, d)),
    assertz(arc(t4_da, type_edge, d, a)),
    % Cycle 2 (potential): b -> e -> d -> c -> b (shares nodes/edges with Cycle 1)
    assertz(arc(t4_be, type_edge, b, e)),
    assertz(arc(t4_ed, type_edge, e, d)),
    assertz(arc(t4_dc, type_edge, d, c)), % Note: d-c is an edge here, c-d is in Cycle 1
    assertz(arc(t4_cb, type_edge, c, b)), % Note: c-b is an edge here, b-c is in Cycle 1
    % A "short" chord: a -> d. This may render a-b-c-d-a non-simple.
    assertz(arc(t4_ad_chord, type_edge, a, d)).


% --- Main Logic for Finding Simple Cycles ---
% Orchestrates the process of finding simple cycles in the graph.
find_simple_cycles(SimpleCyclesList) :-
    write('Initializing... Generating edge/2 facts for efficient traversal...\n'), nl,
    generate_edges_from_arcs, % Prepare the simplified edge/2 relation.

    write('Step 1: Finding all elementary cycles (no repeated vertices except start/end)...\n'), nl,
    find_all_elementary_cycles(ElementaryCyclesRaw), % Identify all elementary cycles.
    length(ElementaryCyclesRaw, NumElementary),
    write('Found '), write(NumElementary), write(' elementary cycles.\n'), nl,

    ( NumElementary > 0 ->
        % For diagnostic purposes, we display the elementary cycles found. These are in reverse traversal order from DFS.
        print_cycles_list_reversed('Elementary Cycles Found (raw, reverse traversal order):', ElementaryCyclesRaw),
        write('Step 2: Filtering elementary cycles to retain only "simple" cycles (no chords)...\n'), nl,
        % A "simple" cycle has no "chords" - i.e., no shorter path exists in the graph between any two nodes of the cycle
        % than the path along the cycle itself.
        filter_to_simple_cycles(ElementaryCyclesRaw, NormalizedSimpleCyclesCandidates),
        % Employ setof/3 to ensure the final list contains unique, canonically represented simple cycles.
        % Normalization to a canonical form (e.g., starting with the smallest node) is crucial for setof/3
        % to correctly identify and keep only unique cycles.
        ( setof(NormalizedCycle, MemberCycle^(member(MemberCycle, NormalizedSimpleCyclesCandidates), NormalizedCycle = MemberCycle), SimpleCyclesList) ->
            length(SimpleCyclesList, NumSimple),
            write('Found '), write(NumSimple), write(' simple cycles (unique, normalized).\n'), nl,
            print_cycles_list('Simple Cycles Found (final, normalized):', SimpleCyclesList)
        ;   write('Found 0 simple cycles after filtering.\n'), nl, % All candidates were filtered out.
            SimpleCyclesList = []
        )
    ;   write('No elementary cycles were found to filter.\n'), nl, % No elementary cycles to begin with.
        SimpleCyclesList = []
    ).

% --- Step 1.1: Find All Elementary Cycles (no repeated vertices except start/end) ---
% An elementary cycle is one where vertices are not repeated, except for the start/end vertex.
find_all_elementary_cycles(ElementaryCyclesList) :-
    % Retrieve all nodes present in the graph to serve as potential starting points for cycles.
    % If node/2 facts are not explicitly defined for all nodes in arcs, this might miss some.
    % The default node declarations at the end help mitigate this for common node names.
    findall(NodeID, node(NodeID, _NodeType), AllNodes),
    find_cycles_from_potential_starts(AllNodes, ElementaryCyclesList).

% Iterates through each node, considering it as a potential start of a cycle, and initiates DFS.
find_cycles_from_potential_starts(PotentialStartNodes, ElementaryCyclesList) :-
    findall( % Collect all cycles found.
        RawCycle, % Each cycle found by dfs_for_cycle.
        (   member(StartNode, PotentialStartNodes),     % Select a StartNode.
            edge(StartNode, FirstNeighbor), % Find an edge leading out of it to a FirstNeighbor.
            % Initiate Depth First Search from FirstNeighbor, aiming to return to StartNode.
            % The path is initialized with [FirstNeighbor, StartNode]. The DFS explores from FirstNeighbor;
            % StartNode is the ultimate target. Path is built in reverse.
            dfs_for_cycle(FirstNeighbor, StartNode, [FirstNeighbor, StartNode], RawCycle)
        ),
        ElementaryCyclesList % List of all raw cycles found.
    ).

% Performs Depth First Search to find a path from CurrentNode back to TargetNode.
% PathBackToStart is [CurrentNode, PrevNode, ..., TargetNode], i.e., nodes in reverse order of traversal from TargetNode.
dfs_for_cycle(CurrentNode, TargetNode, PathBackToStart, FoundCycleInReverse) :-
    edge(CurrentNode, NextNode), % Explore an edge from CurrentNode to NextNode.
    (   NextNode == TargetNode -> % Cycle detected: CurrentNode has an edge back to TargetNode.
        % PathBackToStart is [CurrentNode, P(CurrentNode), ..., StartNode_from_main_call].
        % Prepending TargetNode (which is StartNode_from_main_call) completes the cycle.
        % E.g., if path was c -> b -> a (TargetNode=a), PathBackToStart=[c,b,a].
        % FoundCycleInReverse becomes [a,c,b,a]. This represents cycle a-b-c-a.
        FoundCycleInReverse = [TargetNode | PathBackToStart]
    ;   % To maintain elementarity (no repeated nodes in path, except start/end of cycle):
        \+ memberchk(NextNode, PathBackToStart), % Ensure NextNode has not been visited in the current path.
        % Continue DFS from NextNode, adding it to the path.
        dfs_for_cycle(NextNode, TargetNode, [NextNode | PathBackToStart], FoundCycleInReverse)
    ).

% --- Step 2.1: Filter Elementary Cycles to Get "Simple" Cycles ---
% A "simple" cycle is an elementary cycle that does not contain any "chords".
% A chord is an edge in the graph (not part of the cycle's own edges) that connects
% two non-adjacent nodes of the cycle, effectively offering a shortcut.
% More formally, for any two nodes N1, N2 in a simple cycle, the shortest path
% between N1 and N2 in the *entire graph* must not be shorter than their path along the cycle itself.

filter_to_simple_cycles([], []). % Base case: No more elementary cycles to check.
filter_to_simple_cycles([CandidateCycle | RemainingCandidates], [NormalizedCycle | FilteredSimpleCycles]) :-
    is_simple_cycle_candidate(CandidateCycle), % Verify if CandidateCycle meets the "simple" criteria.
    !, % If it is simple, commit to this choice.
    normalize_cycle_representation(CandidateCycle, NormalizedCycle), % Convert the cycle to its canonical form for uniqueness.
    filter_to_simple_cycles(RemainingCandidates, FilteredSimpleCycles). % Process the rest.
filter_to_simple_cycles([_NonSimpleCycle | RemainingCandidates], FilteredSimpleCycles) :-
    % If is_simple_cycle_candidate failed, _NonSimpleCycle is not simple. Discard it.
    filter_to_simple_cycles(RemainingCandidates, FilteredSimpleCycles).

% Checks if a given elementary cycle (in reverse order from DFS) is "simple".
is_simple_cycle_candidate(ReversedCycleFromDFS) :-
    % Input ReversedCycleFromDFS is e.g., [a,c,b,a] for cycle a-b-c-a.
    % Convert to forward order and get unique nodes: e.g., [a,b,c].
    reverse(ReversedCycleFromDFS, ForwardCycleWithRepeatEnd), % E.g., [a,b,c,a]
    ForwardCycleWithRepeatEnd = [StartNode | PathNodesWithRepeatEndAtEnd], % StartNode=a, PathNodesWithRepeatEndAtEnd=[b,c,a]
    append(UniqueNodesInSequence, [StartNode], PathNodesWithRepeatEndAtEnd), % UniqueNodesInSequence=[b,c]
    CycleNodesInOrder = [StartNode | UniqueNodesInSequence], % E.g., [a,b,c] - unique nodes in cycle traversal order.

    % The core "simple" criterion: for any two distinct nodes N1, N2 in CycleNodesInOrder,
    % the shortest path distance between N1 and N2 in the *entire graph* must not be less
    % than their path distance *along this cycle*.
    check_all_node_pairs_for_chords(CycleNodesInOrder, CycleNodesInOrder).

% Iterates through N1 from CycleNodesInOrder.
check_all_node_pairs_for_chords([], _). % Base case: All N1s processed.
check_all_node_pairs_for_chords([Node1 | RestOfNodes1], OriginalCycleNodesOrdered) :-
    % For the current Node1, verify the simple path condition against all other nodes (Node2) in the cycle.
    check_one_node_against_all_others(Node1, OriginalCycleNodesOrdered, OriginalCycleNodesOrdered),
    check_all_node_pairs_for_chords(RestOfNodes1, OriginalCycleNodesOrdered). % Recurse for next Node1.

% Iterates through N2 from OriginalCycleNodesOrdered for a given N1.
check_one_node_against_all_others(_, [], _). % Base case: Node1 checked against all Node2s.
check_one_node_against_all_others(Node1, [Node2 | RestOfNodes2], OriginalCycleNodesOrdered) :-
    ( Node1 == Node2 -> true % A node compared to itself trivially satisfies the condition (distance 0).
    ;   % Determine CyclePathDistance: number of edges from Node1 to Node2 *along the cycle path*.
        get_distance_along_cycle(Node1, Node2, OriginalCycleNodesOrdered, CyclePathDistance),
        % Determine GraphShortestDistance: length of shortest path between Node1 and Node2 in the *entire graph*.
        find_shortest_path_length(Node1, Node2, GraphShortestDistance),

        % The "simple" condition: GraphShortestDistance must not be less than CyclePathDistance.
        % If GraphShortestDistance < CyclePathDistance, a "chord" exists, making the cycle non-simple.
        ( GraphShortestDistance == -1 -> % No path found in the entire graph between Node1 and Node2.
                                         % This shouldn't happen if Node1 and Node2 are part of a valid cycle
                                         % from which CyclePathDistance could be derived.
                                         % However, if it implies an infinitely long path, it's "longer"
                                         % than any finite CyclePathDistance, so it's simple for this pair.
                                         % This case needs careful consideration for graph disconnectedness.
                                         % Assuming CyclePathDistance > 0 (distinct nodes in cycle).
           (CyclePathDistance > 0 -> true ; !, fail) % If no path in graph, but there's one in cycle, it's simple for this pair.
        ; GraphShortestDistance >= CyclePathDistance
        )
    ),
    !, % If the check for this Node1-Node2 pair succeeded, commit.
    check_one_node_against_all_others(Node1, RestOfNodes2, OriginalCycleNodesOrdered). % Check Node1 against next Node2.
check_one_node_against_all_others(_, _, _) :- !, fail. % If any Node1-Node2 pair fails, this predicate (and thus is_simple_cycle_candidate) fails.

% Calculates the number of edges between NodeA and NodeB when traversing *only* along the provided CycleNodesOrdered path.
% CycleNodesOrdered is like [n1, n2, n3, n4] for cycle n1-n2-n3-n4-n1.
get_distance_along_cycle(NodeA, NodeB, CycleNodesOrdered, Distance) :-
    nth0(IndexA, CycleNodesOrdered, NodeA), % 0-based index of NodeA.
    nth0(IndexB, CycleNodesOrdered, NodeB), % 0-based index of NodeB.
    length(CycleNodesOrdered, PathLength),  % Total number of unique nodes in the cycle path.
    ( IndexB >= IndexA -> % If NodeB appears after or at the same position as NodeA.
        Distance is IndexB - IndexA % Direct distance along the list.
    ; % NodeB appears before NodeA; the path "wraps around".
      % E.g., in [a,b,c,d], distance from d (idx 3) to b (idx 1):
      % (PathLength - IndexA) = edges from NodeA to end of list (effectively to start via cycle edge).
      % Then add IndexB = edges from start of list to NodeB.
      % (4 - 3) + 1 = 1 + 1 = 2. (Path d-a-b, 2 edges).
        Distance is (PathLength - IndexA) + IndexB
    ).

% --- Utility: Find Shortest Path Length (using BFS) ---
% Finds the length of the shortest path between StartNode and EndNode in the entire graph.
find_shortest_path_length(StartNode, EndNode, Length) :-
    % Initial queue for BFS: [[Node, DistanceFromStartNode]]. VisitedNodes tracks nodes already processed or in queue.
    bfs_shortest_path([[StartNode, 0]], EndNode, [StartNode], Length),
    !. % Found a path, commit to this Length.
find_shortest_path_length(_StartNode, _EndNode, -1). % If bfs_shortest_path fails, no path exists; return -1.

% Breadth-First Search implementation.
bfs_shortest_path([], _TargetNode, _VisitedNodes, _) :- !, fail. % Queue is empty, TargetNode not found: no path.
bfs_shortest_path([[TargetNode, PathLength] | _QueueRest], TargetNode, _VisitedNodes, PathLength) :- !. % TargetNode is at head of queue: path found.
bfs_shortest_path([[CurrentNode, CurrentDist] | QueueRest], TargetNode, VisitedNodes, PathLength) :-
    % Process CurrentNode. Find all its neighbors not yet in VisitedNodes.
    findall(NextNode, (edge(CurrentNode, NextNode), \+ memberchk(NextNode, VisitedNodes)), UnvisitedNeighbors),
    NewDistToNeighbors is CurrentDist + 1, % Neighbors are one step further.
    add_unvisited_neighbors_to_queue(UnvisitedNeighbors, NewDistToNeighbors, QueueRest, NewQueue), % Enqueue newly found neighbors.
    append(VisitedNodes, UnvisitedNeighbors, UpdatedVisitedWithDuplicates),
    list_to_set(UpdatedVisitedWithDuplicates, UpdatedVisitedUnique), % Keep VisitedNodes list unique and efficient.
    bfs_shortest_path(NewQueue, TargetNode, UpdatedVisitedUnique, PathLength). % Continue search with new queue and visited set.

% Helper to construct queue entries [Node, Distance] for each neighbor and append them (BFS strategy).
add_unvisited_neighbors_to_queue(UnvisitedNeighbors, DistanceToThem, CurrentQueue, NewQueue) :-
    findall([NeighborNode, DistanceToThem], member(NeighborNode, UnvisitedNeighbors), NeighborEntries),
    append(CurrentQueue, NeighborEntries, NewQueue). % Append to end of queue for BFS.

% --- Utility: Normalize Cycle Representation for Uniqueness ---
% Normalization ensures that a cycle is represented in a canonical way,
% typically by starting with its lexicographically smallest node and listing nodes in traversal order.
% This is essential for identifying unique cycles, as DFS might find the same cycle
% starting from different nodes or in different (but equivalent) sequences.

% normalize_cycle_representation(+RawReversedCycle, -NormalizedNodeList)
% Input RawReversedCycle (e.g., [a,d,c,b,a] for cycle a-b-c-d-a) is the cycle as found by DFS:
% nodes in reverse traversal order, with start/end node duplicated.
% Output NormalizedNodeList (e.g., [a,b,c,d] for the example) is the canonical form:
% nodes in forward traversal order, starting with the lexicographically smallest node in the cycle,
% and with the duplicate end node removed.
normalize_cycle_representation(RawReversedCycle, NormalizedNodeList) :-
    RawReversedCycle = [StartNode | PathReversedWithStartNodeAtEnd], % E.g., StartNode=a, PathReversedWithStartNodeAtEnd=[d,c,b,a]
    reverse(PathReversedWithStartNodeAtEnd, [_StartNodeAgain | PathForwardWithoutStartNode]), % E.g., PathForwardWithoutStartNode=[b,c,d]
    CycleNodesInForwardOrder = [StartNode | PathForwardWithoutStartNode], % E.g., [a,b,c,d]
    find_lexicographically_smallest_node(CycleNodesInForwardOrder, SmallestNode), % Find the 'smallest' node (e.g., 'a').
    rotate_list_to_start_with_element(CycleNodesInForwardOrder, SmallestNode, NormalizedNodeList). % Rotate list so SmallestNode is first.

% Finds the lexicographically smallest node in a list of nodes.
find_lexicographically_smallest_node([Min], Min) :- !. % Base case: list with one element.
find_lexicographically_smallest_node([Head | Tail], Min) :-
    find_lexicographically_smallest_node(Tail, MinOfTail),
    ( Head @< MinOfTail -> Min = Head ; Min = MinOfTail ). % Standard term comparison for atoms.

% Reorders OriginalList such that StartElement is the first element, preserving cyclic order.
% e.g., rotate_list_to_start_with_element([b,c,d,a], a, RotatedList) -> RotatedList = [a,b,c,d].
rotate_list_to_start_with_element(OriginalList, StartElement, RotatedList) :-
    append(PartBeforeElement, [StartElement | PartAfterElement], OriginalList), % Split list at StartElement.
    !, % Commit if StartElement found and split successful.
    append([StartElement | PartAfterElement], PartBeforeElement, RotatedList). % New order.
rotate_list_to_start_with_element(OriginalList, _StartElement, OriginalList). % Fallback: if StartElement is already first, or not found (latter shouldn't happen here).

% --- Helper Predicates for Printing ---
print_cycles_list(_Header, []) :- !. % Do nothing if the list of cycles is empty.
print_cycles_list(Header, ListOfCycles) :-
    writeln(Header),
    forall(member(Cycle, ListOfCycles), (write('  '), writeln(Cycle))).

% Used for printing elementary cycles which are typically found by DFS in reverse order of traversal.
% Reversing them for display shows the path as it would be traversed.
print_cycles_list_reversed(Header, CyclesInReverseOrder) :-
    writeln(Header),
    forall(member(ReversedCycle, CyclesInReverseOrder), (
       reverse(ReversedCycle, ForwardCycle),
       write('  '), writeln(ForwardCycle)
    )).