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
# pylint: disable=C0103

import argparse
import logging
import sys
logging.basicConfig()
logger = logging.getLogger(__name__)

from libDKFZparser_join2 import DKFZData

def PrepareWebsubmit(basedir, data, submissiontype, submissionrole):
    """
    Prepare records for websubmission. This should build up the proper
    submission structure and run up to creation of `recmysql`.

    @param basedir: base for the curdir structure of Invenio
    """
    import os
    import glob
    from invenio.search_engine                             import \
        perform_request_search
    from invenio.libwebsubmit_hgf                          import \
        generateCurdir,                                           \
        prepareUpload
    from invenio.websubmit_functions.Websubmit_Helpers_hgf import \
        write_file,                                               \
        write_all_files
        # write_done_file,                                          \
        # write_json,                                               \

    create_recid = True

    if submissionrole == 'EDITOR':
        # FIXME for EDITOR we need proper uid of an editor. Till now dkfz
        # database has no editors however
        # Check group EDITORS and select one. Probably we can correlate it with
        # the institute.
        submissionuid = 2
        # TODO check why we still get STAFF submissions in this case.
    if submissionrole == 'STAFF':
        submissionuid = 1

    existingRecid = perform_request_search(p='970__a:"%s"' % data['970__']['a'])

    if len(existingRecid) > 0:
        (curdir, form, user_info) = generateCurdir(recid=existingRecid[0],
                                                   uid=submissionuid,
                                                   access=data['970__']['a'],
                                                   basedir=basedir,
                                                   mode='MBI')
        if curdir == '':
            logger.error('Insufficient permissions to modify %s for uid %i' %
                        (existingRecid[0],  submissionuid))
            logger.error('Most likely STAFF permissions are required.')
            logger.error('Record not updated %s', existingRecid[0])
            return
        for f in glob.glob('%s/%s' % (curdir, 'hgf_*')):
            os.remove(f)
        write_file(curdir, 'doctype', submissiontype)
    else:
        (curdir, form, user_info) = generateCurdir(recid=None,
                                                   uid=submissionuid,
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

def RoleAndTypeMapping():
    """
    Print boilerplate with descriptions of the input files

    Return mappings of file name parts to role and pubtype
    """
    logger.info("Setting up role and pubtype mappings")

    submissionrole = {}
    submissionrole['AOP'] = 'EDITOR'
    submissionrole['PUB'] = 'STAFF'

    descr = {}
    descr['AOP']   = 'Ahead of print'
    descr['PUB']   = 'Published article'

    # Note due to historical reasons websubmit does not use pubtype
    # identifiers but its own naming convention.
    pubtype = {}
    pubtype['ABSTRACT']     = 'abstract'
    pubtype['ARTICLE']      = 'journal'
    pubtype['BACHELOR']     = 'bachelor'
    pubtype['BOOK']         = 'book'
    pubtype['BOOK_CHAPTER'] = 'contb'
    pubtype['COURSE']       = 'course'
    pubtype['DIPL']         = 'diploma'
    pubtype['DISS']         = 'phd'
    pubtype['HABIL']        = 'habil'
    pubtype['MASTER']       = 'master'
    pubtype['PATENT']       = 'patent'
    pubtype['PROCEEDING']   = 'contrib'

    for role in submissionrole:
        logger.info('If filename contains %s (= %s) submit as %s' %
                      (role, descr[role], submissionrole[role]))

    for typ in pubtype:
        logger.info('If filename contains %s use pubtype %s' %
                      (typ, pubtype[typ]))

    return submissionrole, pubtype

def GetFiles2Process(directory, criterion, pubtype):
    """
    Get all files in direcotry and return those matching the (glob) criterion

    @param directory: dir to scan
    @param criterion: glob files to process have to match
    """
    import glob
    logger.info("Scanning %s for files matching %s" % (directory, criterion))

    allfiles = glob.glob('%s/%s' % (directory, criterion))

    print allfiles
    print pubtype

    files2process = []
    filesunique   = {}
    for f in allfiles:
        for typ in sorted(pubtype, reverse=True):
            if typ in f:
                filesunique[f] = 1

    for f in filesunique:
        files2process.append(f)
        logger.info("Inputfile found: %s" %f)

    return files2process

def GetSubmissionType(filename, pubtype, defaultvalue):
    """
    Derive the submission type, ie. the type we would use in websubmit

    @param filename: scan which key in pubtypes matches
    @param pubtypes: list of dicts containing pubtypes
    @param defaultvalue: if none matches return this
    """

    logger.debug("Checking %s for %s" % (filename, str(pubtype)))

    res = defaultvalue
    NotMatched = True
    # sort longest type first
    for typ in sorted(pubtype, reverse=True):
        if (typ in filename) and (NotMatched):
            # Match only if we did not have a _longer_ match
            # BOOK vs. BOOK_CHAPTER => BOOK_CHAPTER is correct
            res = pubtype[typ]
            NotMatched = False

    return res

#======================================================================
def main():
    """
    Process all files in a given dir and websubmit them.
    """
    import os
    import shutil
    from invenio.libRelease2OpenAccess_join2 import UploadBatches

    logger.info("Starting conversion")

    basedir   = '/tmp/websubmit'
    batchdir  = '/tmp/batch'
    sampledir = '../samples/'


    logger.info("Base dir: %s" % basedir)
    logger.info("Sample dir: %s" % sampledir)

    logger.info("Removing old dirs")
    try:
        shutil.rmtree(basedir)
        shutil.rmtree(batchdir)
    except:
        logger.error("Can not delete dirs")
    logger.info("Creating %s and %s" %(basedir, batchdir))
    try:
        os.makedirs(basedir)
        os.makedirs(batchdir)
    except:
        logger.error("Can not create dirs")


    submissionrole, pubtype = RoleAndTypeMapping()
    files2process = GetFiles2Process(sampledir, '*.xml', pubtype)

    for f in files2process:
        logger.info("Processing file: %s" % f)
        subtype = GetSubmissionType(f, pubtype, 'journal')
        subrole = GetSubmissionType(f, submissionrole, 'STAFF')
        logger.info("Submission type: %s" % subtype)
        logger.info("Submission role: %s" % subrole)

        data = DKFZData(f)

        for key in data.getBibliographic():
            print key
            #pprint.pprint(data.getBibliographic()[key])
            PrepareWebsubmit(basedir, data.getBibliographic()[key],
                             subtype, subrole)

    UploadBatches(basedir, batchdir, packagesize=1000)

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verbose', '-v', default = 0, action='count')
    args = parser.parse_args()


    if args.verbose == 0:
        # Default
        log_level = logging.WARNING
    elif args.verbose == 1:
        log_level = logging.INFO
    elif args.verbose == 2:
        log_level = logging.DEBUG
    else:
        log_level = logging.ERROR

    logger.setLevel(logging.INFO)

    logger.info('Migrating data for DKFZ')

    main()
    sys.exit(0)
