# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2015 Numérigraphe SARL.
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
    'name': 'Allow users to move locked lots in receipt locations',
    'version': '1.0',
    'author': u'Numérigraphe',
    'category': 'Custom',
    'description': """
Normally locked lots can't be selected in pickings. This module lets you
define receipt locations to which locked lots can be moved.

This allows stock workers to put away the received goods within certain
limits.
    """,
    'depends': [
        'stock_lock_lot',
    ],
    'data': [
        'stock_view.xml',
        'wizard/stock_transfer_details_view.xml',
    ],
    'license': 'AGPL-3',
}
