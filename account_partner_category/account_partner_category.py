# -*- coding: utf-8 -*-
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

"""Allow searching invoices by partner category."""

from openerp.osv import osv, fields

class account_invoice(osv.osv):
    """Add the partner categories to the object "Invoice"."""

    _inherit = 'account.invoice'

    _columns = {
        'partner_category_ids':  fields.related('partner_id', 'category_id',
             type='many2many', relation='res.partner.category',
             string='Partner Categories'),
    }


