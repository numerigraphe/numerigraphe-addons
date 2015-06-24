# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL.
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
    'name': 'Effective gross weight of a delivery',
    'version': '1.0',
    'author': u'Numérigraphe',
    'category': 'Generic Modules/Sales & Purchases',
    'depends': ['stock', 'delivery', ],
    'data': ['stock_view.xml'],
    'description': """
Adds a new field to the packings to let users key in the effective weight of deliveries.""",
}
