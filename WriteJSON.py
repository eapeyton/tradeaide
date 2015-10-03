import Trade
import logging
import os
import json


def write_scores(scores, file_name):
    with open(os.path.join('history', file_name), 'w') as f:
        json.dump(scores, f, indent=2)

def write_json():
    std = Trade.read_scoring_file(Trade.get_resource('standard.json'))
    hppr = Trade.extend_scoring_file(Trade.get_resource('standard.json'),
                                     Trade.get_resource('halfppr.json'))
    ppr = Trade.extend_scoring_file(Trade.get_resource('standard.json'),
                                    Trade.get_resource('ppr.json'))

    year_players = []
    db = Trade.PlayerDB()
    years_range = range(2009, 2015)
    for year in years_range:
        year_players.append(db.query_players_by_year(year))

    for scoring, name in [(std, 'standard'), (hppr, 'half_ppr'), (ppr, 'ppr')]:
        calc = Trade.Calculator(scoring)
        for position in ['QB', 'RB', 'WR', 'TE']:
            year_scores = []
            for players in year_players:
                year_scores.append(calc.sort_position(players, position))
            avg_scores = Trade.average_lists(*year_scores)
            write_scores(avg_scores, '{}_{}_{}-{}.json'.format(name, 
                                                               position,
                                                               years_range[0],
                                                               years_range[-1]))

if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    write_json()
