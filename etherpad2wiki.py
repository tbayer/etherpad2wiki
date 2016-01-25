#!/usr/bin/python
# Quick-and-dirty script to export the content of an Etherpad in a form
# that is suitable for posting as a wiki page
# Basically, it adds "<br />" tags to the end of every line
# of the Etherpad, except those where MediaWiki will keep the line break
# anyway when parsing it as wikitext (e.g. after a line that starts
# with "*"). 
# Optionally it embeds pages of a PDF file from Wikimedia Commons
# where indicated ("[slide n]" is replaced by an embedding of page n)
# parameters:
# sourceurl points to an Etherpad
# slidesfilename is the file name of a PDF on Wikimedia Commons, without "File:"
# By T. Bayer ([[user:HaeB]])
# Based on https://github.com/tbayer/wikibrs
 
import os
import sys
import re
import codecs
import urllib2

usageexplanation = 'usage: etherpad2wiki.py sourceurl outputfile.txt [slidesfilename]'


class etherpad2wiki(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

if len(sys.argv) < 3 or len(sys.argv) > 4:
    raise etherpad2wiki(usageexplanation)


sourceurl = sys.argv[1]+'/export/txt'
#e.g. https://etherpad.wikimedia.org/p/NamespacesHidingInTheShadows/export/txt

outputfilename = sys.argv[2]

if len(sys.argv) == 4:
    slidesfilename = sys.argv[3].decode("utf-8")
    # e.g. 'Team Practices Group quarterly review - FY2015Q2.pdf'
else:
    slidesfilename = ''

slidelineoldpat = r'\[[sS]lide ([\d]*)\]$' # e.g. "[slide 19]\n"
slidelinenewpat = u'{{clear}}[[File:'+slidesfilename+r'|thumb|380px|page=\1|slide \1]]'


User_agent = 'etherpad2wiki.py'
headers = { 'User-Agent' : User_agent }
req = urllib2.Request(sourceurl, None, headers)
urlresponse = urllib2.urlopen(req)
sourcetext = urlresponse.read()
f = unicode(sourcetext, 'utf-8').splitlines(True)

outputfile = codecs.open(outputfilename, mode='w', encoding='utf-8')


line = ''
for nextline in f:
    
    if re.match(slidelineoldpat, line):

        if slidesfilename != '':
            
            line = re.sub(slidelineoldpat, slidelinenewpat, line).strip()+line

    else:

        if re.match('[^*#;:=\n]', nextline):
            # don't append '<br />' if next line is empty,
            # or starts with *, #, ;, :, or =
            old = r'([^=])\n' # don't append '<br />' if line ends with a '='
            new = r'\1<br />\n'
            # see also https://en.wikipedia.org/wiki/User:Davidgothberg/The_br_tag
            line = re.sub(old, new, line)
                 

    outputfile.write(line)
    
    line = nextline


outputfile.close()
