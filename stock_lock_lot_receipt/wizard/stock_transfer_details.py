# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2015 Numérigraphe SARL.
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

from openerp import models, api, exceptions


class StockTransfer_DetailsItems(models.TransientModel):
    _inherit = 'stock.transfer_details_items'

    @api.one
    @api.constrains('lot_id', 'destinationloc_id')
    def check_lot_in_receipt_location(self):
        if (self.lot_id and self.lot_id.locked
            and not (self.destinationloc_id.allow_locked_lots
                     and self.destinationloc_id.usage == 'internal')):
            raise exceptions.ValidationError(
                "The lot %s is locked and cannot be moved to the location "
                "%s." % (self.lot_id.name, self.destinationloc_id.name))
