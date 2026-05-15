% --- Input Data (Example) ---
% element(1..5).
% set(s1,1). set(s1,2).
% set(s2,2). set(s2,4). set(s2,5).
% set(s3,1). set(s3,3). set(s3,4).
% set(s4,3). set(s4,5).

% --- Problem Formulation ---

% 1. Selection: Choose a subset of sets.
{ select(S) : set(S, E) } :- set(S, _).

% 2. Coverage: Every element must be covered by a selected set.
:- element(E), not covered(E).
covered(E) :- select(S), set(S, E).

% 3. Optimization: Minimize the number of selected sets.
#minimize { 1,S : select(S) }.
