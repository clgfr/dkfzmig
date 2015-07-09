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
Migration script for DFKZ
"""

# Variable naming conventions: we use Uppercase for function names:
# pylint: disable-msg=C0103

#import argparse
import logging
import sys
logging.basicConfig()
logger = logging.getLogger(__name__)

from libDKFZparser_join2 import DKFZData

def GetSubmissionType(pubtypes):
    """
    Derive the submission type, ie. the type we would use in websubmit

    @param pubtypes: list of dicts containing pubtypes
    """

    submissiontype = ''

    for pubtype in pubtypes:
        if 's' in pubtype:
            submissiontype = pubtype['m']

    # TODO should we handle more than one submission type?

    return submissiontype


def PrepareWebsubmit(basedir, data):
    """
    Prepare records for websubmission. This should build up the proper
    submission structure and run up to creation of `recmysql`.

    @param basedir: base for the curdir structure of Invenio
    """
    from invenio.libwebsubmit_hgf import                          \
        generateCurdir,                                           \
        prepareUpload
    from invenio.websubmit_functions.Websubmit_Helpers_hgf import \
        write_done_file,                                          \
        write_file,                                               \
        write_json,                                               \
        write_all_files

    if '3367_' in data:
        pubtypes = data['3367_']
    else:
        # TODO we need document types in 3367_
        pubtypes = [{ "0": "PUB:(DE-HGF)1",
                      "2": "PUB:(DE-HGF)",
                      "a": "Abstract",
                      "m": "abstract",
                      "s": "--maintype--"
                    },
                    {
                      "2": "DRIVER",
                      "a": "conferenceObject"
                    },
                    {
                      "2": "BibTeX",
                      "a": "INPROCEEDINGS"
                    },
                    {
                      "0": "33",
                      "2": "EndNote",
                      "a": "Conference Paper"
                    }]

    submissiontype = GetSubmissionType(pubtypes)

    create_recid = True

    (curdir, form, user_info) = generateCurdir(recid=None, uid=1,
                                               access = 'TEST',
                                               basedir=basedir, mode='SBI',
                                               type=submissiontype,
                                               create_recid=create_recid)
    write_all_files(curdir, data)
    prepareUpload(curdir, form, user_info, mode='SBI')

    return

def Pack4Upload(basedir, uploadir):
    """
    Pack all recmysql in a given websubmit structure up for submission in one
    go.

    @param basedir: base for the curdir structure of Invenio
    @param uploaddir: directory for the packages
    """

    # TODO
    return


#======================================================================
def main():
    """
    """
    logger.info("Entering main")
    import cPickle as pickle

    dataP = 'data.p'

    # AOP == Ahead of Print?
    # Abstract = Abstract submissions?

    # data = DFKZData('../samples/ABSTRACT_AOP.xml')

   # basedir = './websubmit'
    basedir = '/tmp/websubmit'

    #try:
    #    # we do not have etree on python 2.4!
    #    data = pickle.load(open(dataP, 'rb'))
    #except:
        #data = DKFZData('../samples/ABSTRACT_PUB.xml')
        #data = DKFZData('ABSTRACT_PUB.xml')

    data = DKFZData('6026.xml')
    #data = DKFZData('ABSTRACT_AOP.xml')
    #data = DKFZData('ABSTRACT_AOP.xml', simulation=True)

    #pickle.dump(data, open(dataP, 'wb'))

    import pprint
    for key in data.getBibliographic():
        print key
        #pprint.pprint(data.getBibliographic()[key])
        PrepareWebsubmit(basedir, data.getBibliographic()[key])
        # TODO remove:
        #die


    return

if __name__ == '__main__':
    main()
    sys.exit(0)

    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', default = 0, action='count')
    args = parser.parse_args()

    logger.info('Migrating data for DFZK')

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

