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

"""Parameters for EBP export"""

from osv import fields, osv

class res_company(osv.osv):
    """Add parameters to export accounting moves to EBP's software"""
    _inherit = 'res.company'
    _columns = {
        'ebp_uri': fields.char('EBP Share URI', size=256,
            help="The URI of the network share containing the company's EBP folder. Format: smb://SERVER/SHARE/DIR"),
        'ebp_domain': fields.char('EBP User Domain', size=256,
            help="The domain of the user to access the company's EBP folder."),
        'ebp_username': fields.char('EBP User Name', size=256,
            help="The name of the user to access the company's EBP folder."),
        'ebp_password': fields.char('EBP User Password', size=256,
            help="The password of the user to access the company's EBP folder."),
    }
res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
