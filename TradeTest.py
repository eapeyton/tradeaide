import nfldb
import unittest
import mock
import collections
import Trade
import json

STD = Trade.read_scoring_file('standard.json')
PURE = Trade.read_scoring_file('pure.json')

"""
    def testMe(self):
        return
        db = nfldb.connect()
        rb_lists = []
        calc = Trade.Calculator(STD)
        for year in range(2009,2015):
            q = nfldb.Query(db)
            q.game(season_year=year, season_type='Regular')
            rushers = q.sort('rushing_yds').limit(100).as_aggregate()
            receivers = q.sort('receiving_yds').limit(100).as_aggregate()
            passers = q.sort('passing_yds').limit(35).as_aggregate()
            players = Trade.aggpps_to_players(rushers + receivers + passers)
            rb_lists.append(calc.sort_position(players, 'RB'))

        avgs = Trade.average_lists(*rb_lists)
        print avgs[:5]
"""
class PlayerDBTests(unittest.TestCase):
    def setUp(self):
        self.test_player1 = createQB(363, 1, 2, rushing_yds=3, rushing_att=1)
        self.test_player2 = createRB(57, 0, 11, receiving_rec=1, rushing_att=15)
        self.test_aggpps = [createPP('QB'), createPP('RB'), createPP('WR'),
                            createPP('TE'), createPP('RB'), createPP('RB')]


    def testAggPPToPlayer(self):
        playerDB = Trade.PlayerDB()
        db = nfldb.connect()
        q = nfldb.Query(db)
        q.game(gsis_id='2009091000')

        player1 = q.sort('passing_yds').limit(1).as_aggregate()[0]
        self.assertEqual(playerDB.aggpp_to_player(player1), self.test_player1)

        player2 = q.sort('rushing_yds').limit(1).as_aggregate()[0]
        self.assertEqual(playerDB.aggpp_to_player(player2), self.test_player2)
        
        player_list = [player1, player2]
        self.assertEqual(playerDB.aggpps_to_players(player_list), 
                        [self.test_player1, self.test_player2])

    @mock.patch.object(nfldb, 'connect')
    @mock.patch.object(nfldb, 'Query')
    def testQueryPlayersByYear(self, query_mock, *unused_mocks):
        query_mock.return_value.sort.return_value.limit.return_value.as_aggregate.return_value = self.test_aggpps

        playerDB = Trade.PlayerDB()
        players = playerDB.query_players_by_year(2012)
    
        query_mock.return_value.game.assert_called_once_with(season_year=2012,
                                                             season_type='Regular')

        # Really should equal 18 because there are 3 calls but the other 12 are
        # thrown out by PlayerDB because they are 'duplicates'
        self.assertEqual(len(players), 6)
        self.assertTrue(all(isinstance(p,Trade.Player) for p in players))


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.test_player1 = createQB(363, 1, 2, rushing_yds=3, rushing_att=1)
        self.test_player2 = createRB(57, 0, 11, receiving_rec=1, rushing_att=15)
        self.test_player3 = createQB(50, 2, 1, rushing_yds=10, receiving_rec=3)

    def testScorePlayers(self):
        calc = Trade.Calculator(STD)

        player_list = [self.test_player1, self.test_player2, self.test_player3]
        self.assertEqual(calc.score_players(player_list),
                         [14.82, 6.8, 9.0])

    def testScore(self):
        calc = Trade.Calculator(STD)
        self.assertEqual(calc.score(self.test_player3), 9.0)

class TradeTests(unittest.TestCase):
    def testGetPosition(self):
        guesser = Trade.Guesser()
        self.assertEqual(guesser.get_position('LaDainian Tomlinson'), 'RB')
        self.assertEqual(guesser.get_position('Jermichael Finley'), 'TE')

    def testAverageLists(self):
        a = [1.0, 2.0, 3.0]
        b = [5.0, 4.0, 3.0]
        c = [3.0, 8.0, 3.0]
        self.assertEqual(Trade.average_lists(a, b, c), [3.0, 4.0, 3.0])

        lists = [[10, 20], [30, 5], [8, 6], [9, 9], [1, 50]]
        self.assertEqual(Trade.average_lists(*lists), [9.0, 11.67])

        a = [2.5, 3.0, 3.5]
        b = [20, 30]
        self.assertEqual(Trade.average_lists(a, b), [11.25, 16.5])

    def testSortPosition(self):
        players = []
        players.append(createQB(4000, 4, 1))
        players.append(createQB(2000, 8, 0))
        players.append(createRB(1000, 10, 200))
        players.append(createRB(800, 20, 500))
        players.append(createWR(1500))
        players.append(createWR(1800))
        players.append(createWR(300))

        calc = Trade.Calculator(STD)
        self.assertEqual([174.0,112.0], calc.sort_position(players, 'QB'))
        self.assertEqual([250.0,180.0], calc.sort_position(players, 'RB'))
        self.assertEqual([180.0,150.0,30.0], calc.sort_position(players, 'WR'))

    def testReadScoring(self):
        self.maxDiff = None
        exp_scoring = {'passing_yds': .04,
                       'passing_tds': 4,
                       'passing_int': -2,
                       'passing_twoptm': 2,
                       'rushing_yds': .1,
                       'rushing_tds': 6,
                       'rushing_att': 0,
                       'rushing_twoptm': 2,
                       'receiving_yds': .1,
                       'receiving_tds': 6,
                       'receiving_rec': 0,
                       'receiving_twoptm': 2,
                       'fumbles_tot': -2,
                       'kicking_fgm': 3,
                       'kicking_fgmissed': -1,
                       'kicking_xpmade': 1,
                       'kicking_xpmissed': -1}
        scoring = Trade.read_scoring_file('standard.json')
        self.assertEqual(scoring, exp_scoring)

        with self.assertRaises(Trade.NotEnoughRulesError):
            Trade.read_scoring_file('notenoughrules.json')

    def testSuffix(self):
        self.assertEqual(Trade.suffix(1), 'st')
        self.assertEqual(Trade.suffix(8), 'th')
        self.assertEqual(Trade.suffix(22), 'nd')
        self.assertEqual(Trade.suffix(133), 'rd')
        self.assertEqual(Trade.suffix(1891), 'st')

    def testTest(self):
        return
        db = nfldb.connect()
        q = nfldb.Query(db)

        uplayers = set()
        for year in range(2009, 2015):
            q = nfldb.Query(db)
            q.game(season_year=year, season_type='Regular')
            for stat in ['receiving_yds']:
                aggpps = q.sort(stat).limit(85).as_aggregate()
                for aggpp in aggpps:
                    if str(aggpp.player.position) == 'UNK':
                        uplayers.add(aggpp.player.full_name)

        d = collections.OrderedDict()
        for player in uplayers:
            if not Trade.get_position(player):
                first_name = player.split(' ')[0]
                last_name = player.split(' ')[1]
                print 'http://www.pro-football-reference.com/players/{}/{}{}00.htm'.format(last_name[0], last_name[:4], first_name[:2])
                d[player] = 'WR'

        print json.dumps(d)

    def testCheck(self):
        return
        db = nfldb.connect()
        calc = Trade.Calculator(PURE)
        q = nfldb.Query(db)
        q.game(season_year=2009, season_type='Regular')
        rushers = q.sort('rushing_yds').limit(100).as_aggregate()
        receivers = q.sort('receiving_yds').limit(100).as_aggregate()
        passers = q.sort('passing_yds').limit(35).as_aggregate()
        players = Trade.aggpps_to_players(rushers + receivers + passers)
        for rec,yds in calc.sort_position_more(players, 'TE'):
            print "{} {}".format(rec,yds)

def createPP(position):
    aggpp = mock.MagicMock()
    aggpp.position = position
    return aggpp

def createQB(yds, tds, ints, **other):
    player = Trade.Player()
    player.position = 'QB'
    player.passing_yds = yds
    player.passing_tds = tds
    player.passing_int = ints
    return createPlayer(player, **other)


def createRB(yds, tds, rcyds, **other):
    player = Trade.Player()
    player.position = 'RB'
    player.rushing_yds = yds
    player.rushing_tds = tds
    player.receiving_yds = rcyds
    return createPlayer(player, **other)


def createWR(yds, **other):
    player = Trade.Player()
    player.position = 'WR'
    player.receiving_yds = yds
    return createPlayer(player, **other)


def createPlayer(player, **other):
    for att,value in other.items():
        setattr(player, att, value)
    return player


if __name__ == '__main__':
    unittest.main()
