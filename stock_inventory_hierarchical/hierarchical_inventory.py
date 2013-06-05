# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL. All Rights Reserved.
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
# parent_left and parent_right : see account_account column declaration and Performance Optimization chapter on the memento.
##############################################################################
from osv import osv, fields
from tools.translate import _


class stock_inventory_hierarchical(osv.osv):
    _inherit = 'stock.inventory'

    _parent_store = True
    _parent_order = 'date, name'
    _order = 'parent_left'

    _columns = {
        'parent_id': fields.many2one('stock.inventory', 'Parent', ondelete='cascade', readonly=True, states={'draft': [('readonly', False)]}),
        #'lock_stock_mvt': fields.boolean('Needed to lock stock movement'),  # lock stock move during the inventory (for future use)
        'inventory_ids': fields.one2many('stock.inventory', 'parent_id', 'List of inventory children', readonly=True, states={'draft': [('readonly', False)]}),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        }

    _constraints = [(osv.osv._check_recursion, 'Error! You can not create recursive inventories.', ['parent_id']), ]

    def open_sub_inventory(self, cr, uid, id, context=None):
        """ Method to open sub inventory from one2many list on new tab, with specific view. """
        if type(id) != list:
            id = [id]
        id = id[0]
        res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_inventory_form')
        res_id = res and res[1] or False
        inv = self.browse(cr, uid, id, context=context)
        return {
            'type': 'ir.actions.act_window',
            'name': _("Sub inventory : %s") % inv.name,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [res_id],
            'res_model': self._name,
            'res_id': id,
        }

    def write(self, cr, uid, ids, vals, context=None):
        """ Override write method to copy date of parent to children.
        """
        if context is None:
            context = {}
        if vals is None:
            return super(stock_inventory_hierarchical, self).write(cr, uid, ids, vals, context=context)
        values = super(stock_inventory_hierarchical, self).write(cr, uid, ids, vals, context=context)
        if 'date' not in vals or context.get('norecurs'):
            return values
        if type(ids) != list:
            ids = [ids]
        children_ids = self.search(cr, uid, [('parent_id', 'child_of', ids)])
        ctx = context.copy()
        ctx['norecurs'] = True  # needed to write children once.
        return self.write(cr, uid, children_ids, {'date': vals['date']}, context=ctx)

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm inventory only if all the children are confirmed """
        children_count = self.search(cr, uid, [('parent_id', 'child_of', ids),
                                             ('state', 'not in', ['confirm', 'done'])], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some children are not confirmed.'))
        return super(stock_inventory_hierarchical, self).action_confirm(cr, uid, ids, context=context)

    def action_done(self, cr, uid, ids, context=None):
        """ Perform validation only if all the children states are 'done'.
        """
        children_count = self.search(cr, uid, [('parent_id', 'child_of', ids),
                                             ('state', '!=', 'done')], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some children are not done.'))
        return super(stock_inventory_hierarchical, self).action_done(cr, uid, ids, context=context)

stock_inventory_hierarchical()
