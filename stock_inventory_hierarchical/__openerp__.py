# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL. All Rights Reserved.
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
    "name": "Hierarchical Physical Inventory",
    "version": "1.0",
    "depends": ["stock"],
    "author": "Numérigraphe",
    "category": "stock inventory",
    "description": """
    This module have the following features :
        - hierarchical structure of inventory and sub inventories,
        - a location can be linked with only one sub-inventory during inventory,
        - check empty locations,
        - prepare paper inventory filled with formations about products and location, but empty quantity,
        - prepare paper inventory filled with empty locations to check only,
    """,
    "update_xml": ["hierarchical_inventory_view.xml"],
    "installable": True,
    "active": False,
}
