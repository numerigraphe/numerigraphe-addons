# -*- encoding: utf-8 -*-
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
    'name': 'RIB',
    'version': '0.1',
    'category': 'Generic Modules/Base',
    'description': '''
This module install the base for RIB bank accounts (French standard for bank accounts). 
To make it easier to enter RIB data, it will also allow to search for banks by code.

    ''',
    'author' : u'Numérigraphe SARL',
    'depends': ['base', 'account'],
    'init_xml': ['base_rib_data.xml', ],
    'update_xml': ['base_rib_view.xml', ],
    'installable': True,
    'active': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
