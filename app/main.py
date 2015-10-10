import flask
import json
import Trade

app = flask.Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


@app.route('/')
def hello():
    """Return a friendly HTTP greeting."""
    return 'Hello World!'

@app.route('/trade', methods=['POST'])
def trade():
    resp = flask.request.json
    to_give = resp['give'] if 'give' in resp else []
    they_bench = resp['they_bench'] if 'they_bench' in resp else []
    to_receive = resp['receive'] if 'receive' in resp else []
    i_bench = resp['i_bench'] if 'i_bench' in resp else []

    scoring = resp['scoring']
    for player in to_give + they_bench + to_receive + i_bench:
        player['expected'] = Trade.fast_guess_points(scoring.lower(),
                                                     player['name'].lower(), 
                                                     player['position'].lower())

    resp['my_net'] = round(sum_expected(to_receive) - sum_expected(i_bench), 2)
    resp['their_net'] = round(sum_expected(to_give) - sum_expected(they_bench), 2)
    resp['net'] = resp['my_net'] - resp['their_net']
    return flask.jsonify(**resp)

def sum_expected(player_list):
    return sum([player['expected'] for player in player_list])

@app.errorhandler(404)
def page_not_found(e):
    """Return a custom 404 error."""
    return 'Sorry, nothing at this URL.', 404

if __name__ == '__main__':
    app.run()
