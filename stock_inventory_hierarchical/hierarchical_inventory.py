# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
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

from osv import osv, fields
from tools.translate import _

class stock_inventory_hierarchical(osv.osv):
    _inherit = 'stock.inventory'

    _parent_store = True
    _parent_order = 'date, name'
    _order = 'parent_left'

    def name_get(self, cr, uid, ids, context=None):
        """Show the parent inventory's name in the name of the children"""
        if isinstance(ids, (list, tuple)) and not len(ids):
            return []
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1] + ' / ' + name
            res.append((record['id'], name))
        return res
    
    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        """Allow search on value returned by name_get ("parent/ child")"""
        if not args:
            args = []
        if not context:
            context = {}
        if name:
            # Be sure name_search is symetric to name_get
            name = name.split(' / ')[-1]
            ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context=context)

    def _name_get_fnc(self, cr, uid, ids, field_name, arg, context=None):
        """Function field containing the long name"""
        res = self.name_get(cr, uid, ids, context=context)
        return dict(res)

    def _confirmed_rate(self, cr, uid, ids, field_name, arg, context=None):
        """Number of (sub)inventories confirmed/total"""
        rates = {}
        for id in ids:
            nb = self.search(cr, uid, [('parent_id', 'child_of', id)], context=context, count=True)
            nb_confirmed = self.search(cr, uid, [('parent_id', 'child_of', id),
                                                 ('state', 'in', ('confirm', 'done'))], context=context, count=True)
            rates[id] = 100 * nb_confirmed / nb
        return rates
    
    _columns = {
        # XXX remove "method=True" in v7 ?
        'complete_name': fields.function(_name_get_fnc, method=True, type="char", string='Complete reference'),
        'parent_id': fields.many2one('stock.inventory', 'Parent', ondelete='cascade', readonly=True, states={'draft': [('readonly', False)]}),
        'inventory_ids': fields.one2many('stock.inventory', 'parent_id', 'List of Sub-inventories', readonly=True, states={'draft': [('readonly', False)]}),
        'parent_left': fields.integer('Parent Left', select=1),
        'parent_right': fields.integer('Parent Right', select=1),
        'confirmed_rate': fields.function(_confirmed_rate, method=True, string='Confirmed', type='float'),
        }

    # XXX: drop this in v7
    def _check_recursion(self, cr, uid, ids, context=None, parent=None):
        """Backport of osv.osv._check_recursion from v7.0, to allow writing parents and children in the same write()"""
        if not parent:
            parent = self._parent_name

        # must ignore 'active' flag, ir.rules, etc. => direct SQL query
        query = 'SELECT "%s" FROM "%s" WHERE id = %%s' % (parent, self._table)
        for id in ids:
            current_id = id
            while current_id is not None:
                cr.execute(query, (current_id,))
                result = cr.fetchone()
                current_id = result[0] if result else None
                if current_id == id:
                    return False
        return True
    # XXX: use this in v7
    # _constraints = [(osv.osv._check_recursion, 'Error! You can not create recursive inventories.', ['parent_id']), ]
    _constraints = [
        (_check_recursion,
         _('Error! You can not create recursive inventories.'), ['parent_id']),
    ]
    
# XXX: Ideally we would have liked to have a button to open Sub-inventories,
# but unfortunately the v6.0 GTK client crashes, and the 6.0 web client opens a windows without action buttons.
# Maybe we may try that again with the new web client one day... 
#     def open_sub_inventory(self, cr, uid, id, context=None):
#         """ Method to open Sub-inventory from one2many list on new tab, with specific view. """
#         # Find out the form view id
#         if not isinstance(id, list):
#             id = [id]
#         id = id[0]
#         res = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_inventory_form')
#         view_id = res and res[1] or False
#         inv = self.browse(cr, uid, id, context=context)
#         return {
#             'type': 'ir.actions.act_window',
#             'name': _("Sub-inventory : %s") % inv.name,
#             'view_type': 'form',
#             'view_mode': 'form',
#             'view_id': [view_id],
#             'res_model': 'stock.inventory',
#             'res_id': id,
#         }
#         return True
    
    def create(self, cr, user, vals, context=None):
        """ Copy date of parent to children"""
        if vals and vals.get('parent_id'):
            parent_date = self.read(cr, user, [vals['parent_id']], ['date'], context=context)
            vals = vals.copy()
            vals['date'] = parent_date[0]['date']
        return super(stock_inventory_hierarchical, self).create(cr, user, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """ Copy date of parent to children"""
        if context is None:
            context = {}

        values = super(stock_inventory_hierarchical, self).write(cr, uid, ids, vals, context=context)
        if not vals or 'date' not in vals or context.get('norecurs'):
            return values

        if not isinstance(ids, list):
            ids = [ids]
        children_ids = self.search(cr, uid, [('parent_id', 'child_of', ids)])
        ctx = context.copy()
        ctx['norecurs'] = True  # needed to write children once.
        return self.write(cr, uid, children_ids, {'date': vals['date']}, context=ctx)

    def action_cancel_inventary(self, cr, uid, ids, context=None):
        """ Cancel inventory only if all the parents are canceled """
        inventories = self.browse(cr, uid, ids, context=context)
        for inventory in inventories:
            while inventory.parent_id:
                inventory = inventory.parent_id
                if inventory.state != 'cancel':
                    raise osv.except_osv(_('Warning !'), _('One of the parent Inventories is not canceled.'))
        return super(stock_inventory_hierarchical, self).action_cancel_inventary(cr, uid, ids, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirm inventory only if all the children are confirmed """
        children_count = self.search(cr, uid, [('parent_id', 'child_of', ids),
                                             ('state', 'not in', ['confirm', 'done'])], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some Sub-inventories are not confirmed.'))
        return super(stock_inventory_hierarchical, self).action_confirm(cr, uid, ids, context=context)

    def action_done(self, cr, uid, ids, context=None):
        """ Perform validation only if all the children states are 'done'. """
        children_count = self.search(cr, uid, [('parent_id', 'child_of', ids),
                                             ('state', '!=', 'done')], context=context, count=True)
        if children_count > 1:
            raise osv.except_osv(_('Warning !'), _('Some Sub-inventories are not done.'))
        return super(stock_inventory_hierarchical, self).action_done(cr, uid, ids, context=context)

stock_inventory_hierarchical()
