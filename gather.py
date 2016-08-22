#!/usr/bin/env python
__author__ = 'Tony Beltramelli www.tonybeltramelli.com - 09/07/2016'

import argparse
import os
import urllib2
import re
from threading import Thread
from HTMLParser import HTMLParser

DOMAIN = "songmeanings.com/"
ARTIST_PATH = 'artist/view/songs/'


def start_new_thread(task, arg):
    thread = Thread(target=task, args=(arg,))
    thread.start()


def write_to_file(path, data):
    output_file = open(path, 'a')
    output_file.write(data)
    output_file.write("\n")
    output_file.close()


def get_url(path, arg = ""):
    return 'http://' + DOMAIN + path + arg


def get_page_content(url):
    response = urllib2.urlopen(url)
    return response.read()


class SongPageParser(HTMLParser):
    record = False
    lyrics = ""
    output_path = ""

    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            if attr[0] == "class" and attr[1].find('lyric-box') != -1:
                self.record = True

            if attr[0] == "id" and attr[1].find('lyrics-edit') != -1:
                self.record = False
                write_to_file(self.output_path, self.lyrics)
                self.lyrics = ""

    def handle_data(self, data):
        if self.record:
            self.lyrics += re.sub(r'[^\x00-\x7F]+', '\'', data.lstrip()) + "\n"


class ArtistPageParser(HTMLParser):
    match = 0
    url = ""
    title = ""
    output_path = ""

    def handle_starttag(self, tag, attrs):
        href = None
        for attr in attrs:
            if attr[0] == "id" and attr[1].find('lyric-') != -1:
                self.match += 1

            if attr[0] == "href" and attr[1].find(DOMAIN) != -1:
                self.match += 1
                href = attr[1]

        if self.match > 1 and href is not None:
            self.url = href[href.find(DOMAIN) + len(DOMAIN):]

    def handle_endtag(self, tag):
        self.match = 0

    def handle_data(self, data):
        if self.match > 1:
            self.title = data
            html = get_page_content(get_url(self.url))
            song_parser = SongPageParser()
            song_parser.output_path = self.output_path
            start_new_thread(song_parser.feed, html)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output_file', type=str, required=True)
    parser.add_argument('--artists', type=str, required=True)
    args = parser.parse_args()

    output_file = args.output_file
    artists = args.artists.replace(' ', '').split(',')

    try:
        os.remove(output_file)
    except OSError:
        print "The output file doesn't exist, creating it"

    print "Gathering lyrics..."
    for i, artist in enumerate(artists):
        html = get_page_content(get_url(ARTIST_PATH, artist))
        artist_parser = ArtistPageParser()
        artist_parser.output_path = output_file
        artist_parser.feed(html)
        print "Progress: {}%".format(((i + 1) * 100) / len(artists))
    print "Lyrics saved in {}".format(output_file)

if __name__ == "__main__":
    main()
