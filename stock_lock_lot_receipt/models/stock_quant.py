# -*- coding: utf-8 -*-
# © 2016 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, api


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    @api.model
    def quants_move(self, quants, move, location_to, location_from=False,
                    lot_id=False, owner_id=False, src_package_id=False,
                    dest_package_id=False):
        """Permit moves between explicitly allowed locations"""
        # Temporarily unblock the lot
        if lot_id:
            lot = self.env['stock.production.lot'].browse(lot_id)
            locked = lot.locked
            if location_to.allow_locked_lots:
                lot.sudo().locked = False
        super(StockQuant, self).quants_move(
            quants, move, location_to, location_from=location_from,
            lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id,
            dest_package_id=dest_package_id)
        # Restore the blocking
        if lot_id and (lot.locked != locked):
            lot.sudo().locked = locked
