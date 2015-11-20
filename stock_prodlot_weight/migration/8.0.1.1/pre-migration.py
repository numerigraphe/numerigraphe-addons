# -*- coding: utf-8 -*-
#    Copyright 2015 Numérigraphe
#
#    This module is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License

import logging
_logger = logging.getLogger(__name__)

def migrate(cr, version):
    _logger.info("Updating Stock Production Lot")
    # Add column to stock_production_lot table
    cr.execute("""
        ALTER TABLE stock_production_lot
        ADD COLUMN weight_observed numeric""")

    # import data from stock_quant to stock_production_lot
    cr.execute("""
        UPDATE stock_production_lot SET weight_observed = SQ.weight_observed
            FROM (SELECT DISTINCT lot_id, weight_observed FROM stock_quant WHERE weight_observed > 0) AS SQ
        WHERE stock_production_lot.id = SQ.lot_id""")

    _logger.info("Migration Ends")