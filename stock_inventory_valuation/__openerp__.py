# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
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

{
    "name": "Stock inventory valuation",
    "version": "2.0",
    "depends": ["stock"],
    "author": u"Numérigraphe",
    "category": "Pricing",
    "description": """
Lets you record Stock Valuations.
* Adds a wizard to record the current Stock Valuation of a location (with sub-locations)
* Adds an API to record the Stock Valuation by Product ID or by search domain. The location, warehouse or shop can be set in the context.
* Proposes a scheduled task to record the valuation once a week.
    """,
    "init_xml": ["stock_inventory_valuation_data.xml"],
    "update_xml": ["stock_inventory_valuation_view.xml",
                   "wizard/compute_stock_valuation_wizard_view.xml",
                   "security/ir.model.access.csv"],
     "test": ["test/valuation_inventory_test.yml"],
     "demo": ["stock_inventory_valuation_demo.xml"]
}
