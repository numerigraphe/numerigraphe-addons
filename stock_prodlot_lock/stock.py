# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL.
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


from openerp.osv import osv, fields
from openerp.tools.translate import _


class stock_location(osv.osv):
    _inherit = 'stock.location'

    def onchange_usage(self, cr, uid, ids, usage, context=None):
        if usage != "production":
            return {'value': {'need_quality': False}}

    _columns = {
        'receipt': fields.boolean(
            'Receipt Location',
            help="Checking this indicates if this location is receipt type."),
        'need_quality': fields.boolean(
            'Quality Control',
            help="If checked, new production lots will be locked by default, "
                 "allowing quality control to take place."),
    }

    _defaults = {
        'receipt': False,
        'need_quality': False,
    }


class stock_production_lot(osv.osv):
    _inherit = 'stock.production.lot'

    _columns = {
        'locked': fields.boolean(
            'Awaiting Quality Control',
            help="Checking this indicates that this Production Lot is locked "
                 "until Quality Control is made, and no Stock Move can be "
                 "created."),
    }

    _defaults = {
        'locked': False,
    }

    def search(self, cr, uid, args, offset=0, limit=None, order=None,
               context=None, count=False):
        """Only select only the unlocked lot.

        Inherit this method to do like active field, we want select only the
        unlocked lot.
        In the context the value locked_test can be let search the unlocked
        and the locked lot
        """
        if context is None:
            context = {}
        if args:
            new_args = list(args)
        else:
            new_args = []
        if context.get('locked_test', True) and context.get('active_test', True):
            lock_in_args = False
            for arg in args:
                if arg[0] == 'locked':
                    lock_in_args = True
            if not lock_in_args:
                new_args.append(('locked', '=', False))
        return super(stock_production_lot, self).search(
            cr, uid, new_args, offset=offset, limit=limit, order=order,
            context=context, count=count)

    def lock(self, cr, uid, id, context=None):
        """API friendly method to lock the lot)"""
        self.write(cr, uid, [id], {'locked': True}, context=context)

    def unlock(self, cr, uid, id, context=None):
        """API friendly method to unlock the lot)"""
        self.write(cr, uid, [id], {'locked': False}, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        """Log locking/unlocking as prodlot revisions"""
        values = super(stock_production_lot, self).write(
            cr, uid, ids, vals, context=context)
        if 'locked' in vals:
            msg = (vals['locked'] and _('Lot was locked')
                   or _('Lot was unlocked'))
            if not isinstance(ids, list):
                ids = [ids]
            for lot_id in ids:
                self.pool.get("stock.production.lot.revision").create(
                    cr, uid,
                    {'lot_id': lot_id, 'name': msg}, context=context)
        return values

    def create(self, cr, uid, values, context=None):
        """Lock the lot if needed

        Lots get locked if the product category or product label requires it
        or state in product is first use"""
        product_obj = self.pool.get("product.product")
        product = product_obj.browse(
            cr, uid, values['product_id'], context=context)
        new_values = values.copy()

        # test need control quality for labels
        for obj in product.product_tmpl_id.label_ids:
            if obj.need_quality:
                new_values['locked'] = True
                break

        # test need control quality for product in first use
        if product.product_tmpl_id.state == 'first':
            new_values['locked'] = True

        # test need control quality for product category
        if product.product_tmpl_id.categ_id.need_quality:
            new_values['locked'] = True

        return super(stock_production_lot, self).create(
            cr, uid, new_values, context=context)


class stock_move(osv.osv):

    _inherit = 'stock.move'

    def _check_prodlot(self, cr, uid, ids, context=None):
        """Prevent stock moves on locked prodlots"""
        if context is None:
            context = {}
        if not context.get('locked_move', True):
            return True
        message = ""
        for move in self.browse(cr, uid, ids, context=context):
            if (
                move.prodlot_id and move.prodlot_id.locked
                and move.location_id.usage not in ['supplier', 'inventory',
                                                   'production']
                and move.location_dest_id.usage != 'inventory'
                and move.location_id.id != move.location_dest_id.id
                and not(move.location_dest_id.usage == 'internal'
                        and move.location_dest_id.receipt)
                and move.state == 'done'
            ):
                message += _(" - Lot %s: %s.\n") % (move.prodlot_id.name,
                                                    move.product_id.name)
        if message:
            raise osv.except_osv(
                _('Production Lot Locked'),
                _('One or more lots are awaiting quality control and cannot '
                  'be moved:\n%s') % message)
        return True

    _constraints = [
        (_check_prodlot,
         "One or more lots are awaiting quality control and cannot be moved.",
         ['prodlot_id']),
    ]

    def action_done(self, cr, uid, ids, context=None):
        """Lock the prodlot when a move is "done"

        Lots are locked when they are moves from a location needing quality
        check"""
        prodlot_ids = [m.prodlot_id.id
                       for m in self.browse(cr, uid, ids, context=context)
                       if m.location_id.need_quality and m.prodlot_id]
        if prodlot_ids:
            self.pool.get('stock.production.lot').write(
                cr, uid, prodlot_ids, {'locked': True}, context=context)
        return super(stock_move, self).action_done(
            cr, uid, ids, context=context)
