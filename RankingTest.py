import unittest
import Ranking
import mock

class UnitTests(unittest.TestCase):
    def testReadFile(self):
        rows = Ranking.read_tsv(TestData('qbs.tsv'))
        self.assertEqual(['1', 'Aaron Rodgers', 'GB', 'vs.  KC', '1', '1', '1', '0'],
                         rows[0])
        self.assertEqual(['37','Jimmy Clausen','CHI','at  SEA','34','34','34','0'],
                         rows[36])
        self.assertEqual(37, len(rows)) 

    def testReadRankings(self):
        rankings = Ranking.read_rankings(TestData('qbs.tsv'))
        self.assertEqual('Aaron Rodgers', rankings[0])
        self.assertEqual('Jimmy Clausen', rankings[36])
        self.assertEqual(37, len(rankings))

    def testCreateFPLink(self):
        self.assertEqual('http://www.fantasypros.com/nfl/rankings/ros-qb.php?export=xls',
                         Ranking.create_standard_link('QB'))
        self.assertEqual('http://www.fantasypros.com/nfl/rankings/ros-ppr-te.php?export=xls',
                         Ranking.create_ppr_link('TE'))
        self.assertEqual('http://www.fantasypros.com/nfl/rankings/ros-half-point-ppr-flex.php?export=xls',
                         Ranking.create_halfppr_link('FLEX'))

    @mock.patch.object(Ranking.urllib2, 'urlopen')
    def testDownloadRankings(self, urllib_mock):
        urllib_mock.return_value.read.return_value = TestData('rbs.tsv')
        link = Ranking.create_ppr_link('RB')
        rankings = Ranking.download_rankings(link)
        self.assertEqual('Darren Sproles', rankings[35])
        self.assertEqual('Stevan Ridley', rankings[84])
        self.assertEqual('Le\'Veon Bell', rankings[0])

def TestData(path):
    data = None
    with open('testdata/{}'.format(path)) as f:
        data = f.read()
    return data

if __name__ == '__main__':
    unittest.main()
