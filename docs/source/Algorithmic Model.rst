Algorithmic Model
==================

The mathematical problem that the best 15 optimisation solves is a MIP problem of maximizing the objective value selected
by the user (selection between: Value, Form, Total Point, ICT Index), while also respecting the following constraints:
    1. Maximum of 3 players can be selected by each team.
    2. Exactly 2 Goalkeepers, 5 Defenders, 5 Midfielders and 3 Forwards should be selected.
    3. Cost of players selected has a maximum of 100 units.

Mathematical modelling
------------------------

* Pi: player of team i
* G: goalkeeper - binary
* D: defender - binary
* M: midfielder - binary
* F: forward - binary
* T: set of teams
* Cp: cost of player
* Vp: objective value of player

- Pi ε {G, D, M, F}
- Σ(Pi) = 2G + 5D + 5M + 3F
- Σ(Pi * Cp) <= 100
- Σ(Pi) <= 3 for every i ε T
- max(Σ(Pi * Vp))