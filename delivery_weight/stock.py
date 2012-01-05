# -*- encoding: utf-8 -*-
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

from osv import fields, osv

# Add a method to estimate the weight
class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def estimate_weight(self, cr, uid, ids, *args):
        pickings = self.browse(cr, uid, ids)
        for picking in pickings:
            weight = 0.0
            for move in picking.move_lines:
                weight += move.product_id.weight * move.product_qty / move.product_uom.factor  
                self.write(cr, uid, picking.id, {'weight': weight, })
        return True
stock_picking()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
