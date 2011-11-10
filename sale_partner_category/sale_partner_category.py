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

"""Allow searching sale orders by partner category."""

from osv import osv, fields

class sale_order(osv.osv):
    """Add the partner categories to the object "Sale Order"."""

    _inherit = 'sale.order'

    def _get_partner_categories(self, cr, uid, ids, field_name, args,
        context=None):
        """"Find the partner categories of customers for the specified orders"""
        categories_by_order = {}
        orders = self.browse(cr, uid, ids, context=context)
        for order in orders:
            categories_by_order[order.id] = (
                 order.partner_id and
                 [category.id for category in order.partner_id.category_id]
             ) or []
        return categories_by_order

    def _partner_categories_search(self, cr, uid, obj, name, args, context=None):
        """"Find orders of customers in the specified categories"""
        #XXX do we really have to return all the partners'ids? This can be big!
        
        for arg in args:
            if arg[0] == 'partner_category_ids':
                operator = arg[1]
                search_term = arg[2]
        if operator and search_term:
            cat_obj = self.pool.get('res.partner.category')
            category_ids = cat_obj.search(cr, uid,
                [('name', operator, search_term)], context=context
            )
            children_ids = cat_obj.search(cr, uid,
                [('parent_id', 'child_of', category_ids)], context=context
            )
            partner_ids = self.pool.get('res.partner').search(cr, uid,
                [('category_id', 'in', children_ids)], context=context
            )
        else:
            partner_ids = []
        return [('partner_id', 'in', partner_ids)]

    _columns = {
        'partner_category_ids': fields.function(_get_partner_categories,
             fnct_search=_partner_categories_search, method=True, readonly=True,
             type='many2many', relation='res.partner.category', select=True,
             string='Partner Categories'),
    }
sale_order()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
