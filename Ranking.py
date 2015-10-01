import csv
import urllib2

def download_rankings(url):
    response = urllib2.urlopen(url)
    tsv_str = response.read()
    return read_rankings(tsv_str)


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
    rankings = [r[1] for r in rows]
    return rankings


def create_standard_link(position):
    return create_link('', position)


def create_ppr_link(position):
    return create_link('ppr-', position)


def create_halfppr_link(position):
    return create_link('half-point-ppr-', position)


def create_link(keyword, position):
    return 'http://www.fantasypros.com/nfl/rankings/ros-{}{}.php?export=xls'.format(keyword, position.lower())
