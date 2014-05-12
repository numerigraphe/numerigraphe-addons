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
    'name': 'Stock available quoted',
    'version': '2.0',
    'author': u'Numérigraphe SÀRL',
    'category': 'Stock',
    'depends': ['stock_available',
                'sale_order_dates',
                'sale_stock',
                ],
    'description': """
This module computes and displays the quantities available for sale minor by quoted products.

new quantities are computed in real-time:
- "Quoted" = the sum of the quantities of this product in Quotations,
taking the context's shop or warehouse into account

When entering sale orders with this module installed, the salesperson gets warned 
if the quantity available for sale
is insufficient, instead of the virtual available quantity.""",
    'update_xml': [
        'product_view.xml',
    ],
    'test': [
        'test/quoted_qty.yml',
     ],
    'license': 'GPL-3',
}
