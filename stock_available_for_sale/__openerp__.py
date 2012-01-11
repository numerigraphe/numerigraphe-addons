# -*- encoding: utf-8 -*-
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
    'name' : 'Compute the stock available for sale',
    'version' : '1.1',
    'author' : u'Numérigraphe SÀRL',
    'category' : 'Stock',
    'depends' : [
                 'stock',
                 'sale',
                 'sale_order_dates',
                 ],
    'description': "This module computes the quantities available for sale for "
                   "a product in a given context.\n"
                   "This is computed in real time as the virtual stock minus "
                   "the sum of the quantities in Quotations (draft Sale "
                   "Orders).",
    'update_xml' : [
                    'product_view.xml',
                    ],
    'active': False,
    'installable': True,
    'license' : 'GPL-3',
}
