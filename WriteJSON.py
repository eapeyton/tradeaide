def write_json():
    url = Ranking.create_standard_link(position)
    rankings = Ranking.download_rankings(url)
    rank = rankings.index(player_name)
    logging.info('{}\'s rest of season ranking is {}.'.format(player_name, rank+1))

    db = PlayerDB()
    year_scores = []
    calc = Calculator(read_scoring_file('standard.json'))
    for year in range(2009, 2015):
        year_scores.append(calc.sort_position(db.query_players_by_year(year), position))
    avg_scores = average_lists(*year_scores)
    avg_score = avg_scores[rank]
    logging.info('On average (from 2009-2015) players that finished with the {}{} '
                 'most points scored {} points in a year, or {}/game.'
                 .format(rank+1, suffix(rank+1), avg_score, avg_score/16.0))

    # TODO: What do we divide this number by? Not all players play 16 games
    return avg_score / 16.0
