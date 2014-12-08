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

"""Allow searching sale orders by partner category."""

from openerp.osv import osv, fields

class sale_order(osv.osv):
    """Add the partner categories to the object "Sale Order"."""

    _inherit = 'sale.order'
    
    _columns = {
        'partner_category_ids':  fields.related('partner_id', 'category_id',
             type='many2many', relation='res.partner.category',
             string='Partner Categories'),
    }


