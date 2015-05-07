#! /usr/bin/python27     genauer path - Todo
# -*- coding: cp1252 -*-
import xml.etree.ElementTree as ET
import sys
import os


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


tree = ET.parse('ABSTRACT_AOP.xml')
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
        
        if child.tag == 'publishedID':
            pubid = child.text
            print pubid
            verz= os.mkdir("D:\\temp\\abstract\\" + pubid)
            #print verz
            path = "D:\\temp\\abstract\\" + pubid + "\\"
            #print path
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
    
