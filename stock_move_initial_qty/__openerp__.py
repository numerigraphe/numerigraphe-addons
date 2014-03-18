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
    'name' : 'Initial quantity of stock moves',
    'version' : '1.0',
    'author' : u'Numérigraphe',
    'category': 'Custom',
    'description': """
    This module keeps track of the initial quantity planned for each stock move.

    # TODO : Add procurements to the view.
    """,
    'depends' : [
        'stock',
    ],
    'init_xml' : [
                  ],
    'update_xml' : [
                    'stock_view.xml',
                    ],
    'active': False,
    'installable': True,
    'license' : 'GPL-3',
}



