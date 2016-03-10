#!/usr/bin/python

import sys
import codecs
import json

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

langs = []
lang_map = {}
root = {"languages": langs}


def parse(cols, dest, key_dict):
    for count, val in enumerate(cols):
        # tripple strip is kinda ugly, could be a regex match, but hey, it works
        dest[key_dict[count]] = val.strip().strip('"\'').strip()


def parse_card(cols):
    card = {}
    parse(cols, card, card_keys)

    # convert language to iso code and record
    try:
        iso_lang = iso_map[card['dest_language'].lower()]
        del card['dest_language']  # don't need it anymore
        lang = None
        if iso_lang in lang_map.keys():
            lang = langs[lang_map[iso_lang]]
        else:
            lang = {'iso_code': iso_lang, "cards": []}
            langs.append(lang)
            lang_map[iso_lang] = len(langs) - 1
        lang['cards'].append(card)
    except:
        # leave it alone, language not in map
        sys.stderr.write('Could not find language: %s. Card skipped' % card['dest_language'])


def read_pipe():
    # read in creating the two dicts
    for line in sys.stdin:
        cols = line.split(DELIN)
        if cols[0].startswith(META_MARK):
            # remove meta marker from first col
            cols[0] = cols[0].split(META_MARK)[1]
            parse(cols, root, meta_keys)
        else:
            parse_card(cols)


def write_json():
    json.dump(root, sys.stdout, ensure_ascii=False, encoding="utf_8", indent=2)


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

    read_pipe()
    write_json()
