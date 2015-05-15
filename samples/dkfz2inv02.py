#! /usr/bin/python27     genauer path - Todo
# -*- coding: cp1252 -*-
import xml.etree.ElementTree as ET
import sys
import os


#XML_WORK_DIR = 'E:\\pubs\\work25'
#XML_FILE     = 'ABSTRACT_AOP.xml'

XML_WORK_DIR = '.'
XML_FILE     = 'sample.xml'

DKFZ       = 'DKFZ'

PUBLISHED_ID = 'publishedID'
ARTIKEL = 'Artikel'
JOURNAL = 'Journal'
PUBYEAR = 'PubYear'
AUTHOR  = 'Author'
KST     = 'KST'
KEYWORD = 'KEYWORD'
ABSTR   = 'ABSTr'
ERSCHIN = 'ErschIn'
PMID    = 'PMID'

FELD596 = 'Feld596'
PUBVOL  = 'PubVol'
PUBISS  = 'PubIss'
STRTP   = 'Strtp'
ENDP    = 'Endp'

HGF_440_MAP = [ 
        {JOURNAL  : 't'},
        {PUBYEAR  : 'y'},
        {PUBVOL   : 'v'},
        {PUBISS   : 'n'},
        {FELD596  : 'g'},
        {STRTP    : 'p'},
          ]
             

tagFileDict = {
        PUBLISHED_ID : ['hgf_vdb', 'hgf_970__a', 'hgf_536__'], 
        ARTIKEL : 'hgf_245__a', 
        JOURNAL : 'hgf_440__', 
        ABSTR   : 'hgf_520__',
        AUTHOR  : ['hgf_1001_', 'hgf_910__', 'hgf_7001_'], 
        KST     : 'hgf_9201_',
        PMID    : 'hgf_0247_', 
        KEYWORD : 'hgf_65320', 
        ERSCHIN : 'hgf_260__' 
           }

if sys.platform == 'win32':
    ROOT_DIR = 'C:' + os.sep + 'temp' + os.sep + 'abstract' + os.sep
else:
    ROOT_DIR = '~' + os.sep + 'temp'+ os.sep + 'abstract' + os.sep

def createPubDir(publishedId):
    pubDir = ROOT_DIR + publishedId + "\\"
    if not os.path.exists(pubDir):
        os.mkdir(pubDir)
    return pubDir

def createFile(pubDir, pubId, fileName):
    try:
        file = open(pubDir + fileName ,'w')
    except:
        print('Datei ' + fileName + ' konnte nicht geoeffnet werden')
    return file
    

def getXMLTree(path, xmlFileName):
    tree = ET.parse(path + os.sep + xmlFileName)
    root = tree.getroot()
    return root

def initialize():
    if not os.path.exists(ROOT_DIR):
        os.mkdir(ROOT_DIR)
    
def processPubID(pubDir, publishedId):

        file = createFile(pubDir, publishedId, tagFileDict[PUBLISHED_ID][0])
        file.write('yes')
        file.close()

        file = createFile(pubDir, publishedId, tagFileDict[PUBLISHED_ID][1])
        file.write(publishedId)
        file.close()


def processPubTitle(pubDir, pubId, artikel):

    article = unicode(artikel.text)
    file = createFile(pubDir, pubId, tagFileDict[ARTIKEL])
    file.write(article)
    file.close()


def getTag(row, tagName):
    return row.find(tagName)

def getKeyVal(key, val):
    return '{' + '"' + key + '"' +  ':' + '"' + val + '"' + '}'

def getAsString(objs):
	objs_str = str(objs)
	objs_str = objs_str.replace('\'','',100000)
	return objs_str

def composePages(row):
    start = getTag(row, STRTP)
    end   = getTag(row, ENDP)
    if start != None and start.text != '':
        startPage = start.text
    if end != None and end.text != '':
        endPage = end.text
    pages = startPage + '-' + endPage
    return  pages

def processKeywords(pubDir, pubId, keywords):
    keywordCounter = 0
    content = ''
    obj_list = []
    if keywords != None:
        file = createFile(pubDir, pubId, tagFileDict[KEYWORD])
        for keyword in keywords:
            print 'keyword', keyword.text
            keywordCounter = keywordCounter + 1

            content = '{"a" : "' +  keyword.text + '",' + '"x" : "' +  str(keywordCounter) + '"}' 
	    obj_list.append(content)

        file.write(getAsString(obj_list))
        file.close()

def processAuthors(pubDir, pubId, authors):

    secondAuthor = 0
    secondDKFZ   = 0

    obj_list = []
    obj_list_dkfz = []

    content = ''
    fileForOtherAuthors = None
    fileForOtherDKFZ    = None

    for author in authors:
        pos    = author.attrib['Pos']
        name   = author.attrib['name']
        isDKFZ = author.attrib['IsDKFZ']

        if isDKFZ == '1':
            if secondDKFZ == 0:
                obj_list_dkfz = []
                fileForOtherDKFZ = createFile(pubDir, pubId, tagFileDict[AUTHOR][1])
                secondDKFZ = 1

            content = '{"k" : "' +  DKFZ + '",' + '"b" : "' +  pos + '"}' 
	    obj_list_dkfz.append(content)

        if pos == '0':
            file = createFile(pubDir, pubId, tagFileDict[AUTHOR][0])

            content = '{"a" : "' +  name + '",' + '"b" : "' +  pos + '"}' 
	    obj_list.append(content)

            file.write(getAsString(obj_list))
            file.close()
        else:
            if secondAuthor == 0:
                obj_list = []
                fileForOtherAuthors = createFile(pubDir, pubId, tagFileDict[AUTHOR][2])
                secondAuthor = 1

            content = '{"a" : "' +  name + '",'  + '"b" : "' +  pos + '"}' 
	    obj_list.append(content)

    if secondAuthor == 1:
        fileForOtherAuthors.write(getAsString(obj_list))
        fileForOtherAuthors.close()

    if secondDKFZ == 1:
        fileForOtherDKFZ.write(getAsString(obj_list_dkfz))
        fileForOtherDKFZ.close()


def processJournal(pubDir, pubId, row):

    file = createFile(pubDir, pubId, tagFileDict[JOURNAL])

    obj_list = []
    for elem in HGF_440_MAP:
        for key, val in elem.iteritems():
            tagName = key
            marcSubTag = val
            tag = getTag(row, tagName)

            if tag != None and tag.text != '':
                if tagName == STRTP:
                    content = composePages(row)
                else:
                    content = tag.text

                obj_list.append(getKeyVal(marcSubTag, content))

    file.write(getAsString(obj_list))
    file.close()


def parseXML(root):
    for row in root:
        pubId = row.find(PUBLISHED_ID).text
        pubDir = createPubDir(pubId)

        # publishedID    
        processPubID(pubDir, pubId)

        # Artikel
        processPubTitle(pubDir, pubId, row.find(ARTIKEL))

        # Journal
        processJournal(pubDir, pubId, row)
    
        # Author+
        processAuthors(pubDir, pubId, row.findall(AUTHOR))
        # KST+
        # KEYWORD 0+
        processKeywords(pubDir, pubId, row.findall(KEYWORD))

def main():
    
    initialize()
    root = getXMLTree(XML_WORK_DIR, XML_FILE)
    parseXML(root)

if __name__ == '__main__':
    main()
