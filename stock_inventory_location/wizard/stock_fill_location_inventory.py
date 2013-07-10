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

from osv import fields, osv
from tools.translate import _
from product._common import rounding
from collections import OrderedDict


class stock_fill_location_inventory(osv.osv_memory):
    _inherit = 'stock.fill.inventory'

    _columns = {
         'location_id': fields.many2one('stock.location', 'Location'),
         }

    def view_init(self, cr, uid, fields_list, context=None):
        """ inherit from original to add multiple selection of location
        and exclude from location list the locations already choosen by another inventory """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_state = inventory_obj.read(cr, uid, [context.get('active_id')], ['state'], context=context)[0]
        if inventory_state['state'] != 'open':
            raise osv.except_osv(_('Error !'), _('the inventory must be in "Open" state.'))

        nb_inventory = inventory_obj.search(cr, uid, [('id', '=', context.get('active_id'))], count=True, context=context)
        if nb_inventory == 0:
            raise osv.except_osv(_('Warning !'), _('No locations found for the inventory.'))

        return super(stock_fill_location_inventory, self).view_init(cr, uid, fields_list, context=context)

    def fill_inventory(self, cr, uid, ids, context=None):
        """ Fill the inventory only with open locations on the inventory.
        Add line far empty location with empty product or virtual product.
        """
        if context is None:
            context = {}

        inventory_obj = self.pool.get('stock.inventory')
        inventory_line_obj = self.pool.get('stock.inventory.line')
        location_obj = self.pool.get('stock.location')
        move_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get('product.uom')

        # TODO : look if order option will be added on v
        location_ids = inventory_obj.read(cr, uid, [context.get('active_id')], ['location_ids'])

        fill_inventory = self.browse(cr, uid, ids[0], context=context)
        if fill_inventory.recursive:
            location_ids = location_obj.get_children(cr, uid, location_ids[0].get('location_ids'), context=context)
        else:
            location_ids = location_ids[0].get('location_ids')

        location_ids = list(OrderedDict.fromkeys(location_ids))

        res = []
        flag = False

        for location in location_ids:
            datas = {}

            move_ids = move_obj.search(cr, uid, ['|', ('location_dest_id', '=', location),
                                                        ('location_id', '=', location),
                                                        ('state', '=', 'done')], context=context)

            for move in move_obj.browse(cr, uid, move_ids, context=context):
                lot_id = move.prodlot_id.id
                prod_id = move.product_id.id

                if move.location_dest_id.id == location:
                    qty = uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)
                else:
                    qty = -uom_obj._compute_qty(cr, uid, move.product_uom.id, move.product_qty, move.product_id.uom_id.id)

                if datas.get((prod_id, lot_id)):
                    # Floating point sum could introduce some tiny rounding errors.
                    qty = rounding(qty + datas[(prod_id, lot_id)]['product_qty'], move.product_id.uom_id.rounding)

                datas[(prod_id, lot_id)] = {'product_id': prod_id,
                                            'location_id': location,
                                            'product_qty': qty,
                                            'product_uom': move.product_id.uom_id.id,
                                            'prod_lot_id': lot_id,
                                            'default_code': move.product_id.default_code,
                                            'prodlot_name': move.prodlot_id.name}

            if datas:
                flag = True
                res.append(datas)

        if not flag:
            raise osv.except_osv(_('Warning !'), _('No product in this location.'))

        for stock_move in res:
            prod_lots = sorted(stock_move, key=lambda k: (stock_move[k]['default_code'], stock_move[k]['prodlot_name']))
            for prod_lot in prod_lots:
                stock_move_details = stock_move.get(prod_lot)

                if abs(stock_move_details['product_qty']) == 0:
                    continue  # ignore product if stock equal 0

                stock_move_details.update({'inventory_id': context['active_ids'][0]})

                if fill_inventory.set_stock_zero:
                    stock_move_details.update({'product_qty': 0})

                domain = [(field, '=', stock_move_details[field])
                           for field in ['location_id',
                                         'product_id',
                                         'prod_lot_id',
                                         'inventory_id']
                          ]

                line_ids = inventory_line_obj.search(cr, uid, domain, context=context)

                if not line_ids:
                    inventory_line_obj.create(cr, uid, stock_move_details, context=context)

        return {'type': 'ir.actions.act_window_close'}

stock_fill_location_inventory()
