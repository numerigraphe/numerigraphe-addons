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
    'name': 'Partner references on Product lists',
    'version': '1.0',
    "category" : "Generic Modules/Inventory Control",
    'description': """This modules adds an option to select a Partner whose references will be displayed along with the Product list in the wizard 'Stock by Location'.
It will also add the Partner's reference on any Product list when a Partner is in the context.""",
    'author': u'Numérigraphe SARL',
    'depends': [
        'product',
        'stock',
    ],
    'init_xml': [
    ],
    'update_xml': [
        'product.xml',
        'wizard/stock_location_product_view.xml'
    ],
    'demo_xml': [
    ],
    'installable': True,
    'active': False,
}


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
