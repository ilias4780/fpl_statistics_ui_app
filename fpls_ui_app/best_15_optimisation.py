"""
Source file that holds the model formulation of the best 15 players optimisation problem.

Functions in the source file:
    * :class:`OptimisationValuesAllZeroError`: Exception for when the values chosen to be used as the
        main optimisation values in :func:`find_best_15_players_by_value` are all zero.
    * :func:`preprocess_data`: Preprocesses the data needed for the optimisation.
    * :func:`post_process_data`: Separate the results returned by the optimisation and bring it to a format suitable for
        display.
    * :func:`find_best_15_players_by_value`: Calculates the best 15 player selection according
        to the value passed as an argument.
"""
from typing import (
    List
)

import pandas
import pandas as pd
import pulp as p


class OptimisationValuesAllZeroError(Exception):
    """
    Exception for when the values chosen to be used as the main optimisation values in
    :func:`find_best_15_players_by_value` are all zero. This would technically happen only
    in the pre-season period when for example 'Form' is zero for all players.
    """
    pass


def post_process_data(players_df: pd.DataFrame,
                      results: pd.DataFrame,
                      statistics: pd.DataFrame):
    """
    Separate the results returned by the optimisation and bring it to a format suitable for
    display.

    :param players_df: Dataframe containing the uid, first and last name of players
    :type players_df: pandas.dataframe
    :param results: The results of the optimisation
    :type results: pandas.dataframe
    :param statistics: pandas dataframe containing the statistics of the optimisation process
    :type statistics: pandas.dataframe
    """
    # Create the players names and replace the ids in results df
    name_mapping = dict(zip(players_df['uid'], players_df['name']))
    results['player'] = results['player'].map(name_mapping)

    # Create the output data in the format wanted
    gks = results['player'].loc[results['position'] == "Goalkeeper"].tolist()
    defs = results['player'].loc[results['position'] == "Defender"].tolist()
    mfs = results['player'].loc[results['position'] == "Midfielder"].tolist()
    fwds = results['player'].loc[results['position'] == "Forward"].tolist()
    stats_names = statistics.loc[0].tolist()
    stats_values = statistics.loc[1].tolist()
    stats = dict()
    for count, item in enumerate(stats_names):
        stats[item] = stats_values[count]

    df_for_view = pandas.concat([results, statistics], ignore_index=True)

    return df_for_view, gks, defs, mfs, fwds, stats


def find_best_15_players_by_value(player_ids: List,
                                  player_positions: List,
                                  player_values: List,
                                  player_prices: List,
                                  player_teams: List,
                                  opt_target: str,
                                  players_pre_selected: List = None):
    """
    Calculates the best 15 player selection according to the value passed as an argument. Uses the PULP library and
    default CBC solver. It satisfies the max 3 players per team constraint and the 100 cost constraint.

    :param player_ids: Player unique ids
    :type player_ids: list
    :param player_positions: Player positions
    :type player_positions: list
    :param player_values: Player values
    :type player_values: list
    :param player_prices: Player prices
    :type player_prices: list
    :param player_teams: Player teams
    :type player_teams: list
    :param opt_target: optimisation target (the target value)
    :type opt_target: str
    :param players_pre_selected: Players pre-selected by the user (forced to be included)
    :type players_pre_selected: list
    :returns: two pandas dataframes, first containing the players and their details, the second the
              optimisation information
    """

    # Check that there are values to be compared (only relevant for when the season has not started yet)
    if not any([float(value) for value in player_values]):
        raise OptimisationValuesAllZeroError

    # Extract the players' names, positions, values and prices
    players = list()
    values = dict()
    prices = dict()
    gks = list()
    defs = list()
    mfs = list()
    fwds = list()
    for index in range(len(player_ids)):
        uid = player_ids[index]
        players.append(uid)
        values[uid] = float(player_values[index])
        prices[uid] = float(player_prices[index])
        if player_positions[index] == "Goalkeeper":
            gks.append(uid)
        elif player_positions[index] == "Defender":
            defs.append(uid)
        elif player_positions[index] == "Midfielder":
            mfs.append(uid)
        elif player_positions[index] == "Forward":
            fwds.append(uid)

    # Create lists of players per team
    teams_list = set(player_teams)
    team_players_dict = dict()
    for team in teams_list:
        team_players_dict[team] = list()
        for index in range(len(player_ids)):
            if player_teams[index] == team:
                team_players_dict[team].append(player_ids[index])

    # Create the problem and set it to maximization (we want to maximize value)
    prob = p.LpProblem("The_FPL_problem", p.LpMaximize)

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
    for team in teams_list:
        prob += p.lpSum([all_player_vars[i] for i in team_players_dict[team]]) <= 3, f"Max per {team} constraint"

    # Force the players pre-selected by the user
    if players_pre_selected:
        for player in set(players_pre_selected):
            if player in all_player_vars:
                prob += all_player_vars[player] == 1

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

    # Assign the player stats
    best_15_positions = list()
    best_15_prices = list()
    best_15_target_values = list()
    for player in best_15_corrected:
        best_15_positions.append(player_positions[player_ids.index(player)])
        best_15_prices.append(player_prices[player_ids.index(player)])
        best_15_target_values.append(player_values[player_ids.index(player)])

    # Round the values in best_15_prices
    best_15_prices_rounded = list()
    for item in best_15_prices:
        best_15_prices_rounded.append(round(item, 2))

    # Assign the total value
    total_value = p.value(prob.objective)

    # Create the dataframe to return
    result_df = pandas.DataFrame(columns=['player', 'position', 'price', 'target_value'])
    result_df['player'] = best_15_corrected
    result_df['position'] = best_15_positions
    result_df['price'] = best_15_prices_rounded
    result_df['target_value'] = best_15_target_values
    total_stats = pandas.DataFrame(columns=['player', 'position', 'price', 'target_value'])
    total_stats.loc[0] = ['Opt_Status', 'Opt_Target', 'Total_Price', 'Total_Target_Value']
    total_stats.loc[1] = [status, opt_target,
                          round(total_price, 2) if isinstance(total_price, float) else total_price,
                          round(total_value, 2)]

    return result_df, total_stats
