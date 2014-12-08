# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields

class partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'property_supplier_ref': fields.property(None, method=True, type='char',
            string='Our Supplier Ref.', size=128,
            help="The reference attributed by the partner to the current "
                 "company as a supplier of theirs.",
            readonly=""),
        'property_customer_ref': fields.property(None, method=True, type='char',
            string='Our Customer Ref.', size=128,
            help="The reference attributed by the partner to the current "
                 "company as a customer of theirs."),
    }



