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

import argparse
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

# from invenio.libStatistics_hgf import AutoVivification

class DFKZData:
    """
    Implement a parser for the old DKFZ data to allow easy access for websubmit
    procedures
    """

    def __init__(self, filename):

        # primary keys of initial data
        self._bibkeys       = {}

        # _bibliographic holds all data we get from the input file, where each
        # record is an entry in the dict. As keys we use the old record id
        self._bibliographic = {}

        # translation dictionary of input tags => Marc fields
        self._transdict     = self._setupTransdict()

        self._ParseData(filename)
        return

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
        transdict['KEYWORD']     = '653__a'
        transdict['ABSTr']       = '520__a' # is this correct

        # fields that will require special treatment
        transdict['DOI']         = '#0247_2doia'
        transdict['StrtPage']    = '#spage'
        transdict['EndPage']     = '#epage'
        transdict['KST']         = '#KST'
        transdict['Author']      = '#Author'
        transdict['Feld596']     = '#Feld596'


        return transdict

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
            if '#' in self._transdict[key]:
                print "%s needs special treatment" % key
            else:
                if len(data[key]) == 1:
                    if data[key] != None:
                        field = self._transdict[key][0:5]
                        sf    = self._transdict[key][5]
                        if not field in self._bibliographic[bibkey]:
                            self._bibliographic[bibkey][field] = {}
                        self._bibliographic[bibkey][field][sf] = data[key][0]
                else:
                    print "%s should not be repeatable." % key
        return

    def _ParseData(self, filename):
        """
        Parse data from an xml file into python structures
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
                        audict['name'] = child.attrib

                    if 'IsDKFZ' in child.attrib:
                        audict['IsDKFZ'] = True
                    else:
                        audict['IsDKFZ'] = False

                    if 'Pos' in child.attrib:
                        audict['pos'] = child.attrib

                    if not child.tag in dataset:
                        dataset[child.tag] = []

                    dataset[child.tag].append(audict)

                else:
                    # treat all fields as repeatable
                    if not child.tag in dataset:
                        dataset[child.tag] = []
                    dataset[child.tag].append(child.text)
            self._appendBibliographic(dataset)

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

