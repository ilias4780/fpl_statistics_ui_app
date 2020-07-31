import pandas
import requests


def get_fpl_database_in_json():
    fpl_api_url = 'https://fantasy.premierleague.com/api/bootstrap-static/'
    the_whole_db = requests.get(fpl_api_url)
    return the_whole_db.json()


def main():
    the_whole_db_in_json = get_fpl_database_in_json()
    all_db_elements = pandas.DataFrame(the_whole_db_in_json['elements'])
    all_team_ids = pandas.DataFrame(the_whole_db_in_json['teams'])
    useful_player_attributes = all_db_elements[['first_name', 'second_name', 'selected_by_percent', 'value_season',
                                                'minutes', 'goals_scored', 'assists', 'clean_sheets', 'own_goals',
                                                'penalties_saved', 'penalties_missed', 'saves', 'yellow_cards',
                                                'red_cards', 'bonus', 'total_points']]
    print(useful_player_attributes)
    # useful_player_attributes.to_csv('FplStatisticsSummary2020.csv')


if __name__ == '__main__':
    main()
