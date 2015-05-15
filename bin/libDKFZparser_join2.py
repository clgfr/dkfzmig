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

        # _bibliographic holds all data we get from the input file, where each
        # record is an entry in the dict. As keys we use the old record id
        _bibliographic = {}
        _transdict     = self._setupTransdict()
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
        transdict['Journal']     = '440__t'
        transdict['Volume']      = '440__v'
        transdict['Issue']       = '440__n'
        transdict['KEYWORD']     = '653__a'

        # fields that will require special treatment
        transdict['StrtPage']    = 'spage'
        transdict['EndPage']     = 'epage'
        transdict['KST']         = 'KST'
        transdict['Author']      = 'Author'


        return transdict

    def _appendBibliographic(self, data):
        """
        Append data to the _bibliographic entries which are keyed by old id (970)
        """
        return

    def _ParseData(self, filename):
        import xml.etree.ElementTree as ET

        tree = ET.parse(filename)
        root = tree.getroot()

        for rw in root:
            dataset = {}
            for child in rw:
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

            print dataset
            # TODO move dataset to _bibliographic

        return

    def fillCurdir(self, basedir):
        """
        """
        return

    ### def getAuthors(self):
    ### return

    ### def getTitle(self):
    ### return

    ### def get970(self):
    ### return

    ### def getPubyear(self):
    ### return

    ### def get440__t(self):
    ### return

    ### def get440__y(self):
    ### return

    ### def get440__n(self):
    ### return

    ### def get440__v(self):
    ### return

    ### def get440__p(self):
    ### return

    ### def get0247_(self)
    ### return

    ### def getWorkflowStatus(self)
    ### return

    ### def getInstitute(self)
    ### return

#======================================================================
def main():
    """
    """
    logger.info("Entering main")

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
    logger.setLevel(log_level)
    main()

