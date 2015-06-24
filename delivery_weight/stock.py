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
from openerp.osv import fields, orm
import openerp.addons.decimal_precision as dp


class stock_picking(orm.Model):
    """Add the real weight"""
    _inherit = 'stock.picking'

    def action_confirm(self, cr, uid, ids, context=None):
        """Estimate the real gross weight from the computed weight."""
        super(stock_picking, self).action_confirm(cr, uid, ids,
                                                  context=context)
        for picking in self.browse(cr, uid, ids, context=context):
            self.write(cr, uid, picking.id, {'weight_real': picking.weight},
                       context=context)
        return True

    _columns = {
        'weight_real': fields.float('Real Weight',
                               digits_compute=dp.get_precision('Stock Weight'))
    }
