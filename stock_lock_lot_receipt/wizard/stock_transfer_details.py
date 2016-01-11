# -*- coding: utf-8 -*-
# © 2015 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
