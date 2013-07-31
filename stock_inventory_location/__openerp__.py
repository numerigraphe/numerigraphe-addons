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
    "name": "Stock Inventory Location",
    "version": "1.0",
    "depends": ["stock"],
    "author": u"Numérigraphe",
    "category": "Inventory",
    "description": """
        Create a link between inventory and locations.
        You can easily follow the inventory progression and mark the empty locations.
    """,
    "update_xml": [
                   "wizard/stock_confirm_uninventoried_location.xml",
                   "stock_inventory_location_view.xml",
                   "wizard/stock_fill_location_inventory_view.xml",
                   ],
    "installable": True,
    "active": False,
}
