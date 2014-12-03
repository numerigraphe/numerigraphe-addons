# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


{
    'name': 'Lock production lots',
    'version': '1.0',
    'author': u'Sylëam, Numérigraphe',
    'category': 'Custom',
    'description': """
This module lets users lock a production lot, forbidding any new stock move
from being confirmed.
Based on custom module by Sylëam.
    """,
    'depends': [
        'stock',
        'product_label',
    ],
    'update_xml': [
        'stock_view.xml',
        'product_view.xml',
    ],
    'license': 'AGPL-3',
}
