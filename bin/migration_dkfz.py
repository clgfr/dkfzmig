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

import argparse
import logging
logging.basicConfig()
logger = logging.getLogger(__name__)

from libDKFZparser_join2 import DFKZData


#======================================================================
def main():
    """
    """
    logger.info("Entering main")

    # data = DFKZData('../samples/ABSTRACT_AOP.xml')
    data = DFKZData('../samples/ABSTRACT_PUB.xml')


    return

if __name__ == '__main__':
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

