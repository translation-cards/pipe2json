#!/usr/bin/python

import sys
import codecs

DELIN = '|'
META_MARK = 'META:'

# put key names in order they appear in the meta row of the pipe csv
meta_keys = [
    'label',
    'publisher',
    'id',
    'timestamp',
    'source_language',
    'locked'
]

# put key names in order they appear in the card rows of the pipe csv
card_keys = [
    'source_text',
    'dest_audio',
    'dest_language',
    'dest_txt'
]

iso_map = {
    'arabic': 'ar',
    'english': 'en',
    'farsi': 'fa',
    'pashto': 'ps',
    'urdu': 'ur'
}

meta = {}
cards = []


def parse(cols, dest, key_dict):
    for count, val in enumerate(cols):
        dest[key_dict[count]] = val.strip()


def parse_card(cols):
    card = {}
    parse(cols, card, card_keys)

    # convert language to iso code
    try:
        card['dest_language'] = iso_map[card['dest_language'].lower()]
    except:
        # leave it alone, language not in map
        pass
    cards.append(card)


def convert():
    # read in creating the two dicts
    for line in sys.stdin:
        cols = line.split(DELIN)
        if cols[0].startswith(META_MARK):
            # remove meta marker from first col
            cols[0] = cols[0].split(META_MARK)[1]
            parse(cols, meta, meta_keys)
        else:
            parse_card(cols)

def write():
    # write header
    sys.stdout.write('{\n')

    # write metas
    for key, val in meta.items():
        sys.stdout.write('"%s":"%s",\n' % (key, val))

    # write cards
    sys.stdout.write('"cards": [ \n')
    for card_count, card in enumerate(cards):
        sys.stdout.write('{\n')
        for key_count, (key, val) in enumerate(card.items()):
            sys.stdout.write('"%s":"%s"%s\n' %
                             (key, val, (',' if key_count < len(card) - 1 else '')))
        sys.stdout.write('}%s\n' % (',' if card_count < len(cards) - 1 else ''))
    sys.stdout.write(']\n')

    # write footer
    sys.stdout.write('}\n')



if __name__ == "__main__":
    if len(sys.argv) > 1:
        try:
            sys.stdin = codecs.open(sys.argv[1], 'r', 'utf_8')
        except:
            sys.stderr.write("Cannot read file: %s\n" % sys.argv[1])
            sys.exit(-1)
    if len(sys.argv) > 2:
        try:
            sys.stdout = codecs.open(sys.argv[2], 'w', 'utf_8')
        except:
            sys.stderr.write("Cannot write file: %s\n" % sys.argv[2])
            sys.exit(-1)
    if len(sys.argv) > 3:
        sys.stderr.write("Usage: pipe2json <infile> <outfile>\n")
        sys.exit(-1)

    convert()
    write()
