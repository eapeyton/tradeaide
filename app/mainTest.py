import os
import json
import main
import unittest
import tempfile
import Trade

class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, main.app.config['DATABASE'] = tempfile.mkstemp()
        main.app.config['TESTING'] = True
        self.app = main.app.test_client()
        Trade.Test = True
        #main.init_db()

    def testTest(self):
        rv = self.app.get('/')
        self.assertIn('Hello World!', rv.data)
    
    def testPostTradeAddsExpectedPointsToPlayers(self):
        #TODO: Test that all autocomplete players are in database
        data = {}
        data['scoring'] = 'standard'
        data['give'] = []
        data['give'].append(player('Adrian Peterson', 'RB'))
        data['give'].append(player('Peyton Manning', 'QB'))
        data['they_bench'] = []
        data['they_bench'].append(player('Ryan Mathews', 'RB'))
        data['they_bench'].append(player('Derek Carr', 'QB'))
        data['receive'] = []
        data['receive'].append(player('Reggie Bush', 'RB'))
        data['receive'].append(player('Johnny Manziel', 'QB'))
        data['i_bench'] = []
        data['i_bench'].append(player('Le\'Veon Bell', 'RB'))
        data['i_bench'].append(player('Andrew Luck', 'QB'))
        json_str = json.dumps(data)

        resp = self.app.post('/trade', data=json_str, content_type='application/json')

        rdata = json.loads(resp.data)
        self.assertEqual(rdata['give'][0]['expected'], 17.13)
        self.assertEqual(rdata['give'][1]['expected'], 17.32)
        self.assertEqual(rdata['they_bench'][0]['expected'], 5.72)
        self.assertEqual(rdata['they_bench'][1]['expected'], 12.51)
        self.assertEqual(rdata['receive'][0]['expected'], 3.14)
        self.assertEqual(rdata['receive'][1]['expected'], 4.79)
        self.assertEqual(rdata['i_bench'][0]['expected'], 19.13)
        self.assertEqual(rdata['i_bench'][1]['expected'], 19.23)
        self.assertEqual(rdata['my_net'], -30.43) 
        self.assertEqual(rdata['their_net'], 16.22)
        self.assertEqual(rdata['net'], -46.65)

    def testPostTradeAddsExpectedPointsToPPRQBs(self):
        data = {}
        data['scoring'] = 'ppr'
        data['give'] = []
        data['give'].append(player('Andrew luck', 'QB'))
        json_str = json.dumps(data)

        resp = self.app.post('/trade', data=json_str, content_type='application/json')

        rdata = json.loads(resp.data)
        self.assertEqual(rdata['give'][0]['expected'], 18.53)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(main.app.config['DATABASE'])

def player(name, position, ppg=None):
    d = {}
    d['name'] = name
    d['position'] = position
    if ppg:
        d['expected'] = ppg
    return d

if __name__ == '__main__':
    unittest.main()
