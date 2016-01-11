# -*- coding: utf-8 -*-
# © 2016 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.addons.stock_lock_lot.tests import test_locking
from openerp import exceptions


class TestReceipt(test_locking.TestLockingUnlocking):
    """Redo all the same tests as stock_lock_lot, and some more"""
    def setUp(self):
        super(TestReceipt, self).setUp()
        # Create a location to which blocked lots can be moved
        self.qc_location = self.env['stock.location'].create(
            {'location_id': self.stock_location,
             'name': 'Quality control',
             'allow_locked_lots': True})

    def test_allowed_location(self):
        """We can move locked lots to allowed locations"""
        # Lock the lot and Direct the move to the allowed location
        self.lot.button_lock()
        move = self.picking_out.move_lines[0]
        move.location_dest_id = self.qc_location.id
        # must not raise an error
        self.picking_out.action_done()
