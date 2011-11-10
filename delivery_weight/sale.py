# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL. All Rights Reserved
#
##############################################################################

from osv import osv, fields

class sale_order(osv.osv):
    _inherit = 'sale.order'
    
    # estimate the weight of the picking lists created by sale orders
    def action_ship_create(self, cr, uid, ids, *args):
        result = super(sale_order, self).action_ship_create(cr, uid, ids, *args)
        for order in self.browse(cr, uid, ids, context={}):
            pickings = [ x.id for x in order.picking_ids]
            self.pool.get('stock.picking').estimate_weight(cr, uid, pickings)
        return result
sale_order()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
