import os
import pprint
import numpy
import logging
import json
import nfldb
import argparse
import Ranking

logging.basicConfig(level=logging.INFO)

QB = 'qb'
RB = 'rb'
WR = 'wr'
TE = 'te'
POSITIONS = [QB, RB, WR, TE]
STANDARD = 'standard'
HALFPPR = 'half_ppr'
PPR = 'ppr'
Test = False

class NotEnoughRulesError(Exception):
    pass

class PlayerDB:
    def __init__(self):
        self.guesser = Guesser()

    def aggpps_to_players(self, aggpp_list):
        seen = set()
        players = []
        for aggpp in aggpp_list:
            if aggpp.player.full_name not in seen:
                players.append(self.aggpp_to_player(aggpp))
                seen.add(aggpp.player.full_name)
        return players


    def aggpp_to_player(self, aggPP):
        player = Player()
        for attribute in get_attributes():
            setattr(player, attribute, int(getattr(aggPP, attribute)))
        if str(aggPP.player.position) == 'UNK':
            name = aggPP.player.full_name
            logging.debug('Retrieving manual position for {}.'.format(name))
            player.position = self.guesser.get_position(name)
            logging.debug('Found position {} for {}.'.format(player.position, name))
        else:
            player.position = str(aggPP.player.position)
        return player

    def query_players_by_year(self, year):
        db = nfldb.connect()
        q = nfldb.Query(db)
        q.game(season_year=year, season_type='Regular')

        # Only retrieving a limited amount to avoid more manual position tagging
        rushers = q.sort('rushing_yds').limit(100).as_aggregate()
        receivers = q.sort('receiving_yds').limit(100).as_aggregate()
        passers = q.sort('passing_yds').limit(35).as_aggregate()

        players = self.aggpps_to_players(rushers + receivers + passers)
        return players

class Player:
    def __init__(self):
        self.set_attributes()

    def set_attributes(self):
        for attribute in get_attributes():
            setattr(self, attribute, 0)

    def __repr__(self):
        return json.dumps(self.__dict__, default=str, indent=2)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__


class Calculator:
    def __init__(self, scoring):
        self.scoring = scoring

    def score(self, player):
        total = 0.0
        for stat in self.scoring:
            total += self.scoring[stat] * getattr(player, stat)
        return round(total, 2)

    def score_players(self, player_list):
        scores = []
        for player in player_list:
            scores.append(self.score(player))
        return scores

    def sort_position(self, players, position):
        filtered = [p for p in players if p.position == position]
        return sorted(self.score_players(filtered), reverse=True)

    def sort_position_more(self, players, position):
        filtered = [(p.receiving_yds, p.receiving_rec, self.score(p)) for p in players if p.position == position]
        sort = sorted(filtered, key=lambda x: x[2], reverse=True)
        return [(s[1], s[0]) for s in sort]


def get_resource(path):
    global Test
    resource = ''

    if Test:
        full_path = os.path.join('testdata', path)
    else:
        full_path = os.path.join('resources', path)

    with open(full_path, 'r') as f:
        resource = f.read()
    return resource


def write_resource(path, contents):
    global Test

    if Test:
        full_path = os.path.join('testdata', path)
    else:
        full_path = os.path.join('resources', path)

    with open(full_path, 'w') as f:
        f.write(contents)


def average_lists(*lists):
    logging.debug('')
    logging.debug('----------------------------------------------------------------------')
    avgs = []
    short = len(lists[0])
    for lst in lists:
        if len(lst) < short:
            short = len(lst)
    row_format = '{:>15}' * len(lists)
    for i in range(short):
        tot = 0.0
        values = [lst[i] for lst in lists]
        logging.debug(row_format.format(*values))
        #logging.debug(numpy.median(numpy.array(values)))
        if len(values) > 2:
            tot = sum(values) - min(values) - max(values)
            avg = tot / float(len(lists) - 2)
        else:
            avg = sum(values) / float(len(lists))
        avgs.append(round(avg,2))
    return avgs


def read_scoring_file(file_contents):
    scoring = json.loads(file_contents)
    for attribute in get_attributes():
        if not attribute in scoring:
            raise NotEnoughRulesError('Rule for {} not found in {}'.format(attribute,scoring))
    return scoring


def extend_scoring_file(original, extension):
    scoring = read_scoring_file(original)
    ext = json.loads(extension)
    for attribute,value in ext.iteritems():
        scoring[attribute] = value
    return scoring


def get_attributes():
    attributes = []
    for attribute in get_resource('attributes.txt').splitlines():
        attributes.append(attribute.rstrip())
    return attributes

class Guesser:
    def __init__(self):
        self.positions = json.loads(get_resource('unk.json'))

    def get_position(self, name):
        pos = self.positions.get(name)
        if pos:
            return pos
        raise Exception('No manual position found for {}'.format(name))


def suffix(d):
    return 'th' if 11<=d<=13 else {1:'st',2:'nd',3:'rd'}.get(d%10, 'th')


def get_averages(scoring, position):
    averages = get_resource('history/{}_{}_2009-2014.json'.format(scoring, position))
    return json.loads(averages)


def fast_guess_points(scoring, player_name, position):
    averages = get_averages(scoring, position)
    ranking = Ranking.get_ranking(scoring, player_name, position)
    avg_score = averages[ranking]
    logging.info('Guessing expected points for {} ({}) with {} scoring'.format(player_name, position, scoring))
    logging.info('Rest of season {} ranking: {}'.format(position, ranking+1))
    logging.info('On average (from 2009-2015) players that finished with the {}{} '
                 'most points scored {} points in a year, or {}/game.'
                 .format(ranking+1, suffix(ranking+1), avg_score, avg_score/16.0))
    return round(avg_score / 16.0, 2)


# TODO: Probably need a fake database to really test this function
def guess_points(player_name, position):
    url = Ranking.create_standard_link(position)
    rankings = Ranking.read_tsv(Ranking.download_rankings(url))
    rank = rankings.index(player_name)
    logging.info('{}\'s rest of season ranking is {}.'.format(player_name, rank+1))

    db = PlayerDB()
    year_scores = []
    calc = Calculator(read_scoring_file(get_resource('standard.json')))
    for year in range(2009, 2015):
        year_scores.append(calc.sort_position(db.query_players_by_year(year), position))
    avg_scores = average_lists(*year_scores)
    avg_score = avg_scores[rank]
    logging.info('On average (from 2009-2015) players that finished with the {}{} '
                 'most points scored {} points in a year, or {}/game.'
                 .format(rank+1, suffix(rank+1), avg_score, avg_score/16.0))

    # TODO: What do we divide this number by? Not all players play 16 games
    return avg_score / 16.0

def get_args():
    parser = argparse.ArgumentParser(description='Guess the expected number of points per game that a player will produce.')
    parser.add_argument('player_name', type=str, help='the name of the player')
    parser.add_argument('position', type=str, help='the position of the player')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    print guess_points(args.player_name, args.position)
