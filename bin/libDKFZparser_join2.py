#!/usr/bin/env python

# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2015 join2
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.

"""
Process DFKZ data to structures for later reuse
"""

# Variable naming conventions: we use Uppercase for function names:
# pylint: disable-msg=C0103

#import argparse
import logging
from pprint import pprint
import sys
import string
import simplejson as json
from invenio.websubmit_functions.Websubmit_Helpers_hgf import washJSONinput
from invenio.search_engine import perform_request_search, print_record


logging.basicConfig()
logger = logging.getLogger(__name__)

# from invenio.libStatistics_hgf import AutoVivification

class DKFZData:
    """
    Implement a parser for the old DKFZ data to allow easy access for websubmit
    procedures
    """

    _FIRST_AUTH = '1001_'
    _OTHER_AUTH = '7001_'
    _DKFZ_AUTH  = '9101_'

    def __init__(self, filename, minidom='default'):

        # primary keys of initial data
        self._bibkeys       = {}

        # _bibliographic holds all data we get from the input file, where each
        # record is an entry in the dict. As keys we use the old record id
        self._bibliographic = {}

        # translation dictionary of input tags => Marc fields
        self._transdict     = self._setupTransdict()
        
        #Constants as well as list of relevant DKFZ POF-programs
        self._KREBSFORSCHUNG = 'Krebsforschung'
        self._HERZ_KREISLAUF = 'Herz-Kreislauf'
        self._PROG_UNGEBUNDEN = 'Programmungebunden'
        self._progs = [self._KREBSFORSCHUNG, self._HERZ_KREISLAUF, self._PROG_UNGEBUNDEN]

        #mapping each POF-prog which is relevant for DKFZ, to Invenio searchstring of Invenio
        self._pofsearchdict = self._setupPofSearchDict()

        #writing once POF-Fields from Invenio database to dict of DKFZ relevant POF-Prog-Dict  
        self._pofdict = self._setupPofDict()
        #print ('self._pofdict #####:', self._pofdict)

	(pubType, pubStatus) = self._getPubDetails(filename)
	#print 'pubDetails', pubType, pubStatus
	if minidom == 'minidom':
            #print 'using minidom'
            self._ParseDataMinidom(filename, pubType, pubStatus)
	else:
            self._ParseData(filename, pubType, pubStatus)
        return

    def _getDict(self, idtype, idvalue):
        return {'2': idtype, 'a': idvalue}

    def _getPubDetails(self, filename):
	    (filename, suffix) = string.split(filename, '.')
	    if not filename == 'BOOK_CHAPTER' and '_' in filename:
	        (pubType, pubStatus) = string.split(filename, '_')
		if pubStatus == 'AOP':
	            pubStatus = 'Abstract'
		elif pubStatus == 'PUB':
		    pubStatus = 'published'
		else:
		    print "%s: unknown pubStatus ." % pubStatus
	    else:
		pubType = filename
		pubStatus = 'published'
	    return pubType, pubStatus

    def _getAuthority(self, prog):

        import simplejson as json
        from invenio.websubmit_functions.Websubmit_Helpers_hgf import washJSONinput
        from invenio.search_engine import perform_request_search, print_record
        search_str = self._pofsearchdict[prog]
        #print 'search_string:', search_str
 
        authrec = perform_request_search(p=search_str)
        if len(authrec) == 1:
           jsontext = print_record(authrec[0], format='js')
           #print jsontext
           jsontext = washJSONinput(jsontext)
           #print jsontext
           jsondict = json.loads(jsontext, 'utf8')
           return jsondict
           #return authrec[0]

    def _getPOF(self, key):
	pof = {}
	if key == 'Krebsforschung':
            pof['I536__0'] =  'G:(DE-HGF)POF3-311', 
            pof['I536__a'] =  '311 - Signalling pathways, cell and tumor biology (POF3-311)', 
            pof['I536__c'] =  'POF3-311', 
            pof['I536__f'] =  'POF III', 
            pof['I9131_0'] =  'G:(DE-HGF)POF3-311', 
            pof['I9131_1'] =  'G:(DE-HGF)POF3-310', 
            pof['I9131_2'] =  'G:(DE-HGF)POF3-300', 
            pof['I9131_a'] =  'DE-HGF', 
            pof['I9131_b'] =  'Forschungsbereich Gesundheit', 
            pof['I9131_l'] =  'Krebsforschung', 
            pof['I9131_v'] =  'Signalling pathways, cell and tumor biology', 
            pof['label'] =  '311 - Signalling pathways, cell and tumor biology (POF III: 2015 - 2019)'
            return pof

    def _setupPofSearchDict(self):
        """
        We need to store the contents of the MARC fields for each DKFZ PROG in a dictionary

        This prevents database queries for each publication 
        """
        pofsearchdict = {}
        pofsearchdict[self._KREBSFORSCHUNG] = 'id:311 2015'
        pofsearchdict[self._HERZ_KREISLAUF] = 'id:321 2015'
        pofsearchdict[self._PROG_UNGEBUNDEN] = 'id:899 2019'
        return pofsearchdict

    def _setupTransdict(self):
        """
        The local XML file does not contain our final marc so we need to
        translate field names to marc tags. This routine just defines this
        mapping.
        """
        transdict = {}
        transdict['publishedID'] = '970__a'
        transdict['Artikel']     = '245__a'
        transdict['PubYear']     = '260__c'
        transdict['PubVol']      = '440__v'
        transdict['PubIss']      = '440__n'
        transdict['Journal']     = '440__t'
        #transdict['KEYWORD']     = '653__a'
        transdict['ABSTr']       = '520__a' # is this correct

        transdict['PubType']       = '3367_a' # is this correct
        transdict['PubStatus']       = '999__a' # is this correct


        # fields that will require special treatment
        #transdict['DOI']         = '#0247_2doia'
        transdict['DOI']         = '#0247_'
        transdict['PMID']        = '#0247_'
        transdict['MOUSE']       = '#0247_'

        transdict['Strtp']    = '#440__'
        transdict['Endp']     = '#epage'
        #transdict['KST']         = '#KST'
        transdict['KST']         = '#9201_'
        transdict['Author']      = '#Author'
        transdict['Feld596']     = '#Feld596'  
        #transdict['PMID']     = '#PMID'
        #transdict['KEYWORD']     = '#KEYWORD' # 65320
        transdict['KEYWORD']     = '#65320'
        transdict['Prog']     = '#Prog'


        return transdict

    def _setupPofDict(self):
        pofdict ={}
        for prog in self._progs:
            pofdict[prog] = self._getAuthority(prog)
            print('prog:', prog)
            pprint(pofdict)
        print('vor return:')
        pprint(pofdict)
        return pofdict

    def _processPages(self, bibkey, field, data):

        start = data['Strtp']
	if data.has_key('Endp'):
            end = data['Endp']
	    if end[0] == None:
                end = start
	#reminder TODO: if end[0]==' '	
        else:	
            end = start
        pages = str(start[0]) + '-' + str(end[0])
	content = {}
	content['p'] = pages

        self._bibliographic[bibkey][field].update(content)

    def _processAuthors(self, pubId, authors):
    
        auth_list = []
        auth_list_dkfz = []
    
        for author in authors:
	    
            pos    = author['pos']
            name   = author['name']
            isDKFZ = author['IsDKFZ']

            if isDKFZ == True:
                content = {} 
    	        content['k'] = 'DKFZ'
    	        content['x'] = pos
		auth_list_dkfz.append(content)
    
            if pos == '0':
                content = {} 
    	        content['a'] = name
    	        content['b'] = pos
        
		first_auth = []
        	first_auth.append(content)
    
                self._bibliographic[pubId][self._FIRST_AUTH] = first_auth
            else:
    
                content = {} 
    	        content['a'] = name
    	        content['b'] = pos
    	        auth_list.append(content)
    

	if len(auth_list) > 1: # we have more than one author
            self._bibliographic[pubId][self._OTHER_AUTH] = auth_list
    
	if len(auth_list_dkfz) > 0: # we have at least one DKFZ author
            self._bibliographic[pubId][self._DKFZ_AUTH] = auth_list_dkfz

    def _processKST(self, pubId, field, ksts):
        idx = 0
	kst_list = []

	for kst in ksts:
	    content = {}

	    content['k'] = kst
	    content['x'] = idx

	    kst_list.append(content)

	    idx = idx + 1

        self._bibliographic[pubId][field] = kst_list

    def _processKeywords(self, pubId, field, keywords):
	keyword_list = []

	for keyword in keywords:
            content = self._getDict('Author', keyword)

	    keyword_list.append(content)

        self._bibliographic[pubId][field] = keyword_list

    def _processIDs(self, bibkey, field, idtype, id_list):

        if not field in self._bibliographic[bibkey]:
                        self._bibliographic[bibkey][field] = [] 

	id_list_res = self._bibliographic[bibkey][field]

	for entry in id_list:
            id_dict = self._getDict(idtype, entry)
	    id_list_res.append(id_dict)

        self._bibliographic[bibkey][field] = id_list_res

    def _processProg(self, pubId, field, progs):

	for prog in progs:
            #print 'PROG', prog
	    #pof_dict = self._getPOF(key=prog)
	    pof_dict = self._pofdict[prog]
	    for key in pof_dict.keys():
		    if key != 'label':
		        field = key[1:6]
                        sf    = key[6]
		        #print key, field, sf
			if not self._bibliographic[pubId].has_key(field):
                            self._bibliographic[pubId][field] = {}
                            self._bibliographic[pubId][field]['x'] = '0'
                        self._bibliographic[pubId][field][sf] = pof_dict[key]

    def _appendBibliographic(self, data):
        """
        Append data to the _bibliographic entries which are keyed by old id.
        Also store old ids as _bibkey for future reference

        TODO handle special fields
        """
        bibkey = data['publishedID'][0]
        self._bibkeys[bibkey] = 1
        self._bibliographic[bibkey] = {}
        for key in data:
	    #if not self._transdict.has_key(key):
            #    print "%s does not exist _transdict." % key
	    #	return
                
            if '#' in self._transdict[key]:
                field = self._transdict[key][1:]
		#print 'FIELD', field
		if key == 'Author':
		    self._processAuthors(bibkey, data[key])
	        elif key == 'Strtp':
		    self._processPages(bibkey, field, data)
	        elif key == 'Endp':
		    pass
	        elif key == 'KST':
		    self._processKST(bibkey, field, data[key])
	        elif key == 'KEYWORD':
		     self._processKeywords(bibkey, field, data[key])
	        elif key in ['PMID', 'DOI', 'MOUSE']:
		    self._processIDs(bibkey, field, key, data[key])
	        elif key == 'Feld596':
		    pass
	        elif key == 'Prog':
		     self._processProg(bibkey, field, data[key])
                else:
                    print "%s needs special treatment" % key

            else:
                if len(data[key]) == 1:
                    if data[key] != None:
                        field = self._transdict[key][0:5]
                        sf    = self._transdict[key][5]
                        #if not field in self._bibliographic[bibkey]:
			if not self._bibliographic[bibkey].has_key(field):
                            self._bibliographic[bibkey][field] = {}
                        self._bibliographic[bibkey][field][sf] = data[key][0]
                else:
                    print "%s should not be repeatable." % key
        return

    def _ParseData(self, filename, pubType, pubStatus):
        """
        Parse data from an xml file into python structures with ElementTree
        """
        import xml.etree.ElementTree as ET

        tree = ET.parse(filename)
        root = tree.getroot()

        for node in root:
            dataset = {}
            for child in node:
                if child.tag == 'Author':
                    # Authors encode all data in attributes
                    audict = {}
                    if 'name' in child.attrib:
                        audict['name'] = child.attrib['name']

                    if 'IsDKFZ' in child.attrib:
			# audict['IsDKFZ'] = False if child.attrib['IsDKFZ'] == '0' else True
			if child.attrib['IsDKFZ'] == '0': 
			    audict['IsDKFZ'] = False
			else:
			    audict['IsDKFZ'] = True

                    if 'Pos' in child.attrib:
                        audict['pos'] = child.attrib['Pos']

                    if not child.tag in dataset:
                        dataset[child.tag] = []

                    dataset[child.tag].append(audict)

                else:
                    # treat all fields as repeatable
                    if not child.tag in dataset:
                        dataset[child.tag] = []
                    dataset[child.tag].append(child.text)
	    dataset['PubType'] = []
	    dataset['PubType'].append(pubType)
	    dataset['PubStatus'] = []
	    dataset['PubStatus'].append(pubStatus)
            self._appendBibliographic(dataset)

        return

    def _ParseDataMinidom(self, filename, pubType, pubStatus):
        """
        Parse data from an xml file into python structures with Minidom
        """
	
	from xml2py import XML2Dict
        xd = XML2Dict(filename, pubType, pubStatus)
        pubList = xd.adapt()

        # List of dictionaries
        for pub in pubList:
	    #import pprint
	    #pprint.pprint(pub)
            self._appendBibliographic(pub)

        return

    def getBibliographic(self):
        """
        Return all bibliographic data collected by the parser
        """
        return self._bibliographic

    def getBibKeys(self):
        """
        Return all bibkeys we have in the bibliographic data. They are derived
        from the primary keys of our intial datasets.
        """
        return self._bibkeys

# for testing
# usage: libDKFZparser_join2.py <filename> [False (default: use ElementTree) | True (use minidom) ]
if __name__=='__main__':
    if len(sys.argv) == 3:
        myData = DKFZData(sys.argv[1], sys.argv[2])
    else:
        myData = DKFZData(sys.argv[1])
    #sys.exit(0)
    bibliographic = myData.getBibliographic()
    #pprint(bibliographic)
