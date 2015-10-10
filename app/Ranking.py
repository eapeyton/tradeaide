import csv
import urllib2
import Trade

def get_ranking(scoring, player_name, position):
    tsv_str = Trade.get_resource(get_filepath(scoring, position))
    rankings = read_rankings(tsv_str)
    return rankings.index(player_name)


def write_latest():
    for position in Trade.POSITIONS:
        for name, link in create_all_links(position):
            tsv_str = download_rankings(link)
            Trade.write_resource(get_filepath(name, position), tsv_str)


def get_filepath(scoring, position):
    return 'rankings/{}_{}_rankings.tsv'.format(scoring, position)


def download_rankings(url):
    response = urllib2.urlopen(url)
    tsv_str = response.read()
    return tsv_str


def read_tsv(tsv_str):
    tsvin = csv.reader(tsv_str.splitlines(), delimiter='\t')
    append = False
    rows = []
    for row in tsvin:
        if len(row) > 1 and row[0] == '1':
            append = True
        if append:
           rows.append([c.strip() for c in row if c.strip()])
    return rows

    
def read_rankings(tsv_str):
    rows = read_tsv(tsv_str)
    rankings = [r[1].lower() for r in rows]
    return rankings


def create_all_links(position):
    links = []
    standard_link = create_standard_link(position)
    links.append((Trade.STANDARD, standard_link))
    if position == Trade.QB:
        links.append((Trade.HALFPPR, standard_link))
        links.append((Trade.PPR, standard_link))
    else:
        links.append((Trade.HALFPPR, create_halfppr_link(position)))
        links.append((Trade.PPR, create_ppr_link(position)))
    return links


def create_standard_link(position):
    return create_link('', position)


def create_ppr_link(position):
    return create_link('ppr-', position)


def create_halfppr_link(position):
    return create_link('half-point-ppr-', position)


def create_link(keyword, position):
    return 'http://www.fantasypros.com/nfl/rankings/ros-{}{}.php?export=xls'.format(keyword, position.lower())


if __name__ == '__main__':
    write_latest()
