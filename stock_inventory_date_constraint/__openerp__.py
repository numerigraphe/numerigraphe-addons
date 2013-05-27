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
    "name": "Refuse stock move happening before the date of any inventory done",
    "version": "1.0",
    "depends": ["stock"],
    "author": u"Numérigraphe",
    "category": "Stock / Inventory",
    "description": """
        The goal of the module is to refuse stock move happening before the date of any inventory done
        for a product/lot/location.

        This module corrects the following bug / feature (#588154):
            "I setup a physical inventory with date 2010/05/19. Stock is 5 for product x
            When I have an internal move for 1 piece of product x with date 2010/05/01, 
            the current calculated stock at 2010/06/01 is 4 which seems to me incorrect as the current stock 
            should reflect the physical inventory on 2010/05/19 and be 5."
        url : https://bugs.launchpad.net/openobject-addons/+bug/588154
    """,
    "test": ["test/stock_inventory_date.yml"],
    "demo": ["stock_demo.xml"]
}
