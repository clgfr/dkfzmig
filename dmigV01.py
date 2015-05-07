#! /usr/bin/python27     genauer path - Todo
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
namefaut=blank #1001_a Name des Erstautors, in 1001_b Pos und bei Dissertationen in 1001_g das Geschlecht
nameaut=blank #7001_a Name weiterer Autoren, in 7001_b Pos - TODO hier muss ich mehrere Autoren in ein File schreiben
autstring = ""
abt=blank
keyw=blank


tree = ET.parse('ABSTRACT_AOP.xml')
root = tree.getroot()

rt = root.tag

for rw in root:
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
            artitle = child.text
            d.write(artitle)
            d.close()
        elif child.tag == 'Journal':
            journ = unicode(child.text)
            print journ
        elif child.tag == 'PubYear':
            pyear = child.text
            print pyear
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
                namefaut = child.attrib['name']
                d.write('[{"a": "'+namefaut+'", "b": "'+child.attrib['Pos']+'"}]')
                d.close()
            else:
                try:
                    daut = open(path + 'hgf_7001_' ,'w')
                except:
                    print('Datei hgf_7001__ konnte nicht geoeffnet werden')
                nameaut = child.attrib['name']
                autstring += '{"a": "'+nameaut+'", "b": "'+child.attrib['Pos']+'"},'
                                       
                #if child.attrib['IsDKFZ'] == '1':
                    #print 'is dkfz', child.attrib[name].text, child.attrib[Pos].text
                #elif child.attrib == 'IsDKFZ' and child.text == 0:
                    #print 'not dkfz', child.attrib[name].text, child.attrib[Pos].text
        elif child.tag == 'KEYWORD':
            keyw = child.text
            print keyw
        else:
            print 'Da fehlt dann wohl noch etwas'
    daut.write('['+autstring+']')
    daut.close()
    try:
        d = open(path + 'hgf_440__' ,'w')
    except:
        print('Datei hgf_440__ konnte nicht geoeffnet werden')

    d.write('[{"t": "'+journ+'", "y": "'+pyear+'"}]')
        #d.close()
    print journ
    d.close()
    
