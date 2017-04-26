#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib2


def get_xml():
    """
    Get xml file from a server and save it.
    """
    url = 'http://sargo.bolt.stxnext.pl/users.xml'
    source = urllib2.urlopen(url)
    contents = source.read()

    with open('runtime/data/users.xml', 'w') as export:
        export.write(contents)


get_xml()
