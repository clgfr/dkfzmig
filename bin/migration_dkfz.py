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

    create_recid = False

    (curdir, form, user_info) = generateCurdir(recid=None, uid=1,
                                               access = data['970__']['a'],
                                               basedir=basedir, mode='SBI',
                                               type=submissiontype,
                                               create_recid=create_recid)
    write_file(curdir, 'hgf_release', 'yes')
    write_file(curdir, 'hgf_vdb', 'yes')
    write_all_files(curdir, data)
    # 245__ is special, as we have the structured subfield $h that gets
    # flattened in websubmit procedures.
    write_file(curdir, 'hgf_245__a', data['245__']['a'])
    prepareUpload(curdir, form, user_info, mode='SBI')

    return

def Pack4Upload(basedir, batchdir, packagesize=1000):
    """
    Pack all files from our webmodifications to larger bunches to upload them in
    one go. This saves significant time and keeps the bibsched queue short in
    case we have many uploads to process.

    Note that we need to keep batchdir as the acutal upload is asynchronous.
    So bibupload needs to find it's files probably a lot later (say the queue
    is on halt) otherwise it will die.
    Here we use a subdir of /tmp and rely on *nix for the house keeping of
    /tmp. For very long delays this might fail as *nix will clean up. If we
    have a huge number of files and are tight on disk space this might also
    result in trouble.

    @type basedir: string / path
    @param basedir: base of the websubmission tree, where we extract the
                    recmysql-xml-files from
    @type uploaddir: string / path
    @param uploaddir: dir where to place our bunch files in
    @type packagesize: integer
    @param packagesize: number of records to pack into one bunch

    """
    from os import listdir, makedirs
    from shutil import rmtree
    import invenio.libwebsubmit_hgf  as webmodify

    try:
        rmtree(batchdir)
    except OSError:
        pass
    makedirs(batchdir)

    webmodify.pack_files(batchdir, basedir, pack_no=packagesize)
    for xmlfile in listdir(batchdir):
        # upload2invenio does not need form or user_info. They are just there
        # for compatiblity issues in the rest of invenios code.
        webmodify.upload2invenio(dir=batchdir,
                                 form='', user_info='',
                                 filename=xmlfile)

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

    basedir = './websubmit'

    #try:
    #    # we do not have etree on python 2.4!
    #    data = pickle.load(open(dataP, 'rb'))
    #except:
        #data = DKFZData('../samples/ABSTRACT_PUB.xml')
        #data = DKFZData('ABSTRACT_PUB.xml')

    data = DKFZData('../samples/ABSTRACT_AOP.xml')
    #data = DKFZData('ABSTRACT_AOP.xml', simulation=True)

    #pickle.dump(data, open(dataP, 'wb'))

    import pprint
    for key in data.getBibliographic():
        print key
        #pprint.pprint(data.getBibliographic()[key])
        PrepareWebsubmit(basedir, data.getBibliographic()[key])
        # TODO remove:
        #die

    Pack4Upload(basedir, '/tmp/batch', packagesize=1000)

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

