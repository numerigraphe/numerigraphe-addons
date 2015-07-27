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

"""Compute the net weight of sale orders."""
from openerp import api, models, fields


class SaleOrder(models.Model):
    """Add the total net weight to the object "Sale Order"."""

    _inherit = "sale.order"
    
    total_weight_net = fields.Float(
        compute='_total_weight_net',
        readonly=True, string='Total Net Weight',
        help="The cumulated net weight of all the order lines.",
        store=True)

    @api.one
    @api.depends('order_line',
                 'order_line.product_uom_qty',
                 'order_line.product_uom',
                 'order_line.product_id')
    def _total_weight_net(self):
        """Compute the total net weight of the given Sale Orders."""
        result = 0.0
        for line in self.order_line:
            if line.product_id:
                result += (line.product_id.weight_net
                           * line.product_uom_qty / line.product_uom.factor)
        self.total_weight_net = result
