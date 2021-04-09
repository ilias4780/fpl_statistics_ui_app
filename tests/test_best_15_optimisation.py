"""
Test Suite for best 15 optimisation, using unittest.

Classes in the source file:
    * :func:`Best15OptimizationTests`: Test class for best 15 optimization script.
"""

import unittest

from best_15_optimisation import find_best_15_players_by_value


class Best15OptimizationTests(unittest.TestCase):
    """Test class for best 15 optimization script."""

    def test_maximization_of_value(self):
        """Here we check whether the optimization aims to maximize the value."""

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [  # According to the values below, the first player of each position (with the least value)
                    # should not be selected.
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        prices = [  # We don't care about the price in this test
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 54
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[3], expected_value_outcome)

    def test_goalkeeper_position_constraints(self):
        """Here we check if the constraint for the number of goalkeepers is satisfied."""

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [  # without the position constraints it would select more than 2 goalkeepers according to value
            7, 8, 9,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        prices = [  # We don't care about the price in this test
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 66
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[3], expected_value_outcome)

    def test_defender_position_constraints(self):
        """Here we check if the constraint for the number of defenders is satisfied."""

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [  # without the position constraints it would select more than 5 defenders according to value
            1, 2, 3,
            7, 8, 9, 10, 11, 12,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        prices = [  # We don't care about the price in this test
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 84
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[3], expected_value_outcome)

    def test_midfield_position_constraints(self):
        """Here we check if the constraint for the number of midfielders is satisfied."""

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [  # without the position constraints it would select more than 5 midfielders according to value
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            7, 8, 9, 10, 11, 12,
            1, 2, 3, 4
        ]
        prices = [  # We don't care about the price in this test
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 84
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[3], expected_value_outcome)

    def test_forward_position_constraints(self):
        """Here we check if the constraint for the number of forwards is satisfied."""

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [  # without the position constraints it would select more than 3 forwards according to value
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            7, 8, 9, 10
        ]
        prices = [  # We don't care about the price in this test
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 72
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[3], expected_value_outcome)

    def test_players_per_team_constraint(self):
        """Here we check if the constraints for the number of players per team are satisfied."""

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [  # we change the values of chelsea players (plus jesus's) to be the maximum
            1, 2, 3,
            1, 7, 3, 4, 5, 6,
            1, 2, 7, 4, 5, 6,
            1, 2, 7, 8
        ]
        prices = [  # We don't care about the price in this test
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        teams = [  # we change jesus to be Chelsea's player so that we have 4 top value Chelsea players
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'Chelsea'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            # Lampard should not be chosen as he is the the lowest value of the 4 Chelsea players
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'westwood', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 65
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[3], expected_value_outcome)

    def test_price_constraint_greater_than_100(self):
        """
        Here we check if the constraint for the total price of the 15 players selection is satisfied
        on the upper limit.
        """

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        prices = [  # We put a price of 99 to a top value player (henderson) so that we check
                    # that he is not selected although he is top value.
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 99,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'westwood',
            'rashford', 'giroud', 'jesus'
        ]
        expected_price_outcome = 49
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[2], expected_price_outcome)

    def test_price_constraint_equal_to_100(self):
        """
        Here we check if the constraint for the total price of the 15 players selection is satisfied
        on the equal limit.
        """

        # Arrange
        names = [
            'degea', 'martinez', 'pope',
            'yedlin', 'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'westwood', 'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'firminio', 'rashford', 'giroud', 'jesus'
        ]
        positions = [
            'Goalkeeper', 'Goalkeeper', 'Goalkeeper',
            'Defender', 'Defender', 'Defender', 'Defender', 'Defender', 'Defender',
            'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder', 'Midfielder',
            'Forward', 'Forward', 'Forward', 'Forward'
        ]
        values = [
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4
        ]
        prices = [  # We put a price of 52 to a top value player (henderson) so that we check
                    # that he is selected and the total team price is 100.
            1, 2, 3,
            1, 2, 3, 4, 5, 6,
            1, 2, 3, 4, 5, 52,
            1, 2, 3, 4
        ]
        teams = [  # We don't care to check this for now so I have used data to not trigger the constraint
            'ManUtd', 'Villa', 'Burnley',
            'Newcastle', 'Chelsea', 'Tottenham', 'ManUtd', 'ManCity', 'Newcastle',
            'Burnley', 'ManCity', 'Chelsea', 'Tottenham', 'Liverpool', 'Liverpool',
            'Liverpool', 'ManUtd', 'Chelsea', 'ManCity'
        ]
        value_to_use_for_optimisation = 'value'

        # Act
        result_df, total_stats = find_best_15_players_by_value(names, positions, values, prices, teams,
                                                               value_to_use_for_optimisation)

        # Assert
        players_outcome = result_df['player'].tolist()
        stats_outcomes = total_stats.loc[1].tolist()

        expected_players_outcome = [
            'martinez', 'pope',
            'terry', 'rose', 'bissaka', 'stones', 'lascelles',
            'debruyne', 'lampard', 'alli', 'salah', 'henderson',
            'rashford', 'giroud', 'jesus'
        ]
        expected_value_outcome = 100
        self.assertCountEqual(players_outcome, expected_players_outcome)
        self.assertEqual(stats_outcomes[2], expected_value_outcome)
