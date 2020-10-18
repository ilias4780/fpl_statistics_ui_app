import pandas
import pulp as p


def find_best_15_players_by_value(player_names, player_positions, player_values, player_prices, logger):

    # Extract the players' names, positions, values and prices
    players = list()
    values = dict()
    prices = dict()
    gks = list()
    defs = list()
    mfs = list()
    fwds = list()
    for index in range(len(player_names)):
        name = player_names[index]
        players.append(name)
        values[name] = float(player_values[index])
        prices[name] = float(player_prices[index])
        if player_positions[index] == "Goalkeeper":
            gks.append(name)
        elif player_positions[index] == "Defender":
            defs.append(name)
        elif player_positions[index] == "Midfielder":
            mfs.append(name)
        elif player_positions[index] == "Forward":
            fwds.append(name)

    # Create the problem and set it to maximization (we want to maximize value)
    prob = p.LpProblem("The FPL problem", p.LpMaximize)

    # Create the dictionaries to contain the referenced player variables
    gk_vars = p.LpVariable.dicts("gk", gks, cat=p.LpBinary)
    def_vars = p.LpVariable.dicts("df", defs, cat=p.LpBinary)
    mf_vars = p.LpVariable.dicts("mf", mfs, cat=p.LpBinary)
    fwds_vars = p.LpVariable.dicts("fwd", fwds, cat=p.LpBinary)
    all_player_vars = {**gk_vars, **def_vars, **mf_vars, **fwds_vars}

    # Create the objective
    prob += p.lpSum([values[i]*all_player_vars[i] for i in players]), "Value objective"

    # Create the constraints
    prob += p.lpSum([gk_vars[i] for i in gks]) == 2, "Number of goalkeepers wanted"
    prob += p.lpSum([def_vars[i] for i in defs]) == 5, "Number of defenders wanted"
    prob += p.lpSum([mf_vars[i] for i in mfs]) == 5, "Number of midfielders wanted"
    prob += p.lpSum([fwds_vars[i] for i in fwds]) == 3, "Number of forwards wanted"
    prob += p.lpSum([prices[i]*all_player_vars[i] for i in players]) <= 100, "Price constraint"

    # Solve the problem
    prob.solve()

    # Assign the status of the problem
    status = p.LpStatus[prob.status]

    # Put the selected player names to a list
    best_15 = list()
    for v in prob.variables():
        if v.varValue > 0:
            best_15.append(v.name)

    # Put the correct player names to a list
    inv_player_names = {v.name: k for k, v in all_player_vars.items()}
    best_15_corrected = list()
    for player in best_15:
        best_15_corrected.append(inv_player_names[player])
    # Assign the total price
    total_price = 0
    for player in best_15_corrected:
        total_price += prices[player]

    # Assign the player positions
    best_15_positions = list()
    for player in best_15_corrected:
        best_15_positions.append(player_positions[player_names.index(player)])

    # Assign the total value
    total_value = p.value(prob.objective)

    # Create the dataframe to return
    result_df = pandas.DataFrame(columns=['player', 'position', 'total_price', 'total_target_value', 'status'])
    result_df['player'] = best_15_corrected
    result_df['position'] = best_15_positions
    result_df['total_price'][0] = round(total_price, 2) if isinstance(total_price, float) else total_price
    result_df['total_target_value'][0] = round(total_value, 2)
    result_df['status'][0] = status

    # Return the results
    return result_df
