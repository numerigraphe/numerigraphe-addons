# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2010 Numérigraphe SARL. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import string
import re

from osv import osv, fields

class partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
        # Partner's account number in EBP
        'ref_nb': fields.char("Partner's Account suffix in EBP", size=64,
            help="When exporting Entries to EBP, this suffix will be appended "
                 "to the Account Number to make it a Partner Account.",),    }

partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
