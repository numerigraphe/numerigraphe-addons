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

from openerp import api, models, fields


class sale_order_line(models.Model):
    """Add the net weight to the object "Sale Order Line"."""

    _inherit = 'sale.order.line'

    weight_net = fields.Float(
        compute='_weight_net',
        readonly=True,
        string='Net Weight', help="The net weight in Kg.",
        store=True
    )

    @api.one
    @api.depends('product_uom_qty', 'product_uom', 'product_id')
    def _weight_net(self):
        """Compute the net weight of the given Sale Order Lines."""
        result = 0.0
        if self.product_id and self.product_id.weight_net > 0.00:
            qty = self.product_uom_qty
            # Convert the qty to the right unit of measure
            if self.product_uom <> self.product_id.uom_id:
                qty = self.product_uom._compute_qty(
                    self.product_uom.id,
                    self.product_uom_qty,
                    self.product_id.uom_id.id)
            result += qty * self.product_id.weight_net
        self.weight_net = result
