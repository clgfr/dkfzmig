#!/usr/bin/env python
# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 join2
##
## Invenio is free software; you can redistribute it and/or modify it under the
## terms of the GNU General Public License as published by the Free Software
## Foundation; either version 2 of the License, or (at your option) any later
## version.
##
## Invenio is distributed in the hope that it will be useful, but WITHOUT ANY
## WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
## A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License along with
## Invenio; if not, write to the
## Free Software Foundation, Inc., 59 Temple Place,
## Suite 330, Boston, MA 02111-1307, USA.

"""
What it does, try to adopt docstring right away.

TODO it's easier to use english texts and variables
TODO try to like "logger". Some samples below. It makes debugging and output
     handling easier
"""

# Variable naming conventions: we use Uppercase for function names:
# pylint: disable-msg=C0103

import xml.etree.ElementTree as ET
import sys
import os

from invenio.websubmit_functions.Websubmit_Helpers_hgf import \
    write_file,                                               \
    write_json


# TODO consider using a dict like:
# pubdta = {}
# pubdta['ptype']
# pubdta['pubid']

# TODO try to follow a 80 chars per line convention. (pep8)
blank = " " # damit die Variablen, die vorkommen koennen definiert und vorbelegt sind
pubid=blank #970__a PublishedId der alten Datenbank
#vdbrel="yes" alle zu migrierenden Datentypen sind vdb-relevant (Stand Mai 2015: ausser Hochschulschriften)
ptyp=blank  #technisches Feld nur fuer Array fk_publication_type der alten Datenbank
aopepub=blank  #technisches Feld nur fuer Array ahead_of_print=1 oder epub=1 in der alten Datenbank
journb=blank #245__a Titel des Journals oder des Buches
pyear=blank #440__y Erscheinungsjahr des Journals
pubvol=blank #440__v Volume des Journals
pubiss=blank #440__n Issue des Journals
strtp=blank #Startpage des Journalartikels
endp=blank #Endpage des Journalartikels
pages=blank #440__pStartpage-Endpage
jourges=blank #440__g Volume(Issue)Pages
namefaut=blank #1001_a Name des Erstautors, in 1001_b Pos und bei Dissertationen in 1001_g das Geschlecht
nameaut=blank #7001_a Name weiterer Autoren, in 7001_b Pos - TODO hier muss ich mehrere Autoren in ein File schreiben
autstring =blank
autdkfz=blank #9101_ b und k
i=0 #Zähler für DKFZ-Authoren wegen Komma beim dict
abt=blank #9201_ k
keyw=blank #653__2 freie Schlagwoerter
INSTANZ ='DKFZ' # Kürzel für die Instanz, die Teilmenge des Instanznamens ist


def ProcessXML(filename='ABSTRACT_AOP.xml',
               outputpath='"D:\\temp\\abstract\\"'):
    """
    What it does

    @param filename: xml file to process
    @param outputpath: we should use cannoical names here
    """
    logger.info("ProcessXML for %s, writing to %s" % (filename, outputpath))

    tree = ET.parse(filename)
    root = tree.getroot()

    rt = root.tag

    for rw in root:
        autdkfz=""
        strtp=''
        endp=''
        pubvol=''
        pubiss=''
        i=0
        for child in rw:

            # TODO try thinking in dicts, then you could ease up this like
            #      data[child.tag] = child.text
            # for all bibliographic stuff and you need only to handle special
            # cases like publishedID that need to create paths and stuff.
            if child.tag == 'publishedID':
                pubid = child.text
                print pubid
                verz= os.makedirs(outputpath + pubid)
                #print verz
                # TODO we should go for / instead of \ for path delimiters
                # TODO common conventional name for this path is 'curdir'
                path = outputpath + pubid + "\\"
                #print path

                # Rewrite using functions like write_file()
                try:
                    d = open(path + 'hgf_vdb' ,'w')
                except:
                    print('Datei hgf_vdb konnte nicht geoeffnet werden')
                d.write('yes')
                d.close()
                try:
                    d = open(path + 'hgf_970__a' ,'w')
                except:
                    print('Datei hgf_970__a konnte nicht geoeffnet werden')
                d.write(pubid)
                d.close()
            elif child.tag == 'Artikel':
                try:
                    d = open(path + 'hgf_245__a' ,'w')
                except:
                    print('Datei hgf_245__a konnte nicht geoeffnet werden')
                # TODO these unicode-calls can cause trouble
                artitle = unicode(child.text)
                d.write(artitle)
                d.close()
            elif child.tag == 'PubYear':
                try:
                    dj = open(path + 'hgf_440__' ,'w')
                except:
                    print('Datei hgf_440__ konnte nicht geoeffnet werden')
                pyear = child.text
                print pyear
            elif child.tag == 'Journal':
                journ = unicode(child.text)
                print journ
            elif child.tag == 'PubVol':
                pubvol = child.text
            elif child.tag == 'PubIss':
                pubiss = child.text
            elif child.tag == 'StrtPage':
                strtp = child.text
            elif child.tag == 'EndPage':
                endp = child.text
            elif child.tag == 'KST':
                abt = child.text
                print abt
            elif child.tag == 'Author':
                # TODO author is by definition something like a list of dicts.
                # Build up this list of dicts and then adopt write_json.
                # DO NOT write json by hand.
                # The author structure looks like this:
                #
                # data['Author'] = []
                # for each author:
                #     audict = {}
                #     audict['a'] = authorName
                #     audict['b'] = counter
                #     audict['0'] = authorID
                #     if isDKFZ:
                #        audict['u'] = 'DKFZ'
                #     data['Author'].apend(audict)
                # write_json(data['Author'])
                #
                # TODO for local authors we use another field 910 which needs to
                # be connected by means fo $b. We come to that later.
                print child.attrib['name'],'isdkfz:', child.attrib['IsDKFZ'], 'Pos:', child.attrib['Pos']
                if child.attrib['Pos'] == '0':
                    try:
                        d = open(path + 'hgf_1001_' ,'w')
                    except:
                        print('Datei hgf_1001__ konnte nicht geoeffnet werden')
                    namefaut = unicode(child.attrib['name'])
                    d.write('[{"a": "'+unicode(namefaut)+'", "b": "'+child.attrib['Pos']+'"}]')
                    d.close()
                else:
                    try:
                        daut = open(path + 'hgf_7001_' ,'w')
                    except:
                        print('Datei hgf_7001__ konnte nicht geoeffnet werden')
                    nameaut = unicode(child.attrib['name'])
                    if child.attrib['Pos']== '1':
                        autstring = '{"a": "'+unicode(nameaut)+'", "b": "'+child.attrib['Pos']+'"}'
                    else:
                        autstring += ',{"a": "'+unicode(nameaut)+'", "b": "'+child.attrib['Pos']+'"}'
                if child.attrib['IsDKFZ']=='1':
                    i+=1
                    try:
                        dk = open(path + 'hgf_9101_' ,'w')
                    except:
                        print('Datei hgf_9101__ konnte nicht geoeffnet werden')
                    if i == 1:
                        autdkfz= '{"b": "'+child.attrib['Pos']+'", "k": "'+INSTANZ+'"}'
                    elif i > 1:
                        autdkfz += ',{"b": "'+child.attrib['Pos']+'", "k": "'+INSTANZ+'"}'

            elif child.tag == 'KEYWORD':
                keyw = child.text
                print keyw
            else:
                print 'Da fehlt dann wohl noch etwas'
        daut.write('['+unicode(autstring)+']')
        daut.close()
        dk.write('['+autdkfz+']')
        dk.close()
        #jourges=pubvol+'('+pubiss+')'+pages
        #print jourges
        journstring = '"t": "'+journ+'", "y": "'+pyear
        if endp =='':
            pages=strtp
        else:
            pages=strtp+'-'+endp
        print pages
        if pages != '':
            journstring = journstring +',"p": "'+pages+'"'
        if pubvol != '':
            journstring = journstring +',"v": "'+pubvol+'"'
        if pubiss != '':
            journstring = journstring +',"v": "'+pubiss+'"'
        dj.write('[{'+journstring+'}]')
            #d.close()
        #print ('Issue:'+pubiss)
        #print ('Volume:'+pubvol)
        print journ
        dj.close()

def main():
    """
    """
    logger.info("Entering main")

    # TODO adopt unix file name conventions
    # TODO path should be given in unix-style. Test if not D:/temp/abstract is
    # evaluated correctly on Windows
    ProcessXML(filename='ABSTRACT_AOP.xml', outputpath='"D:\\temp\\abstract\\"')

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', default = 0, action='count')
    args = parser.parse_args()

    logger.info('FIXME What do we do?')

    if args.verbose == 0:
        # Default
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose == 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    logger.setLevel(loggin.DEBUG)
    # logger.setLevel(log_level)

    main()
    main()
