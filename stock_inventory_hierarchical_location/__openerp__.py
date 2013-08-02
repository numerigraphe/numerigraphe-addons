# -*- encoding: utf-8 -*-
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
    "name": "Exhaustive and hierachical Stock Inventories",
    "version": "1.0",
    "depends": ["stock_inventory_hierarchical", "stock_inventory_location"],
    "author": u"Numérigraphe",
    "category": "stock inventory",
    "description": """
This module makes exhaustive Inventories aware of their Sub-Inventories.
========================================================================

It must be installed if both modules "stock_inventory_location" and "stock_inventory_hierarchical" are installed.

This module allows an inventory to contain a general Location, and it's sub-inventories to contain some of it's sub-Locations.
    """,
    "init_xml": [],
    "update_xml": [
                   "wizard/stock_inventory_missing_locations_view.xml",
                   "inventory_hierarchical_location_view.xml",
                   ],
    # Will work with v6.1 and later
    "auto_install": True,
}
