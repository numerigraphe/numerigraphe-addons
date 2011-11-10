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

    
    def _get_ref_nb(self, cr, uid, ids, field_name, arg, context):
        """ This function just returns an empty string as the EBP account number.
        It may be overridden in another module to make it more useful.""" 
        return map (lambda x: (x,''),  ids)

    _columns = {
        # Account number suffix
        'ref_nb': fields.function(_get_ref_nb, type="char",
              string='EBP Account Suffix', method=True, size=64,
              help="This field makes the second part of the Partner's Account in EBP"),
    }

partner()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
