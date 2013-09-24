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
    'name' : "Manage references at the partner's",
    'version' : '2.0',
    'author' : u'Numérigraphe SARL',
    'category' : 'Custom',
    'depends' : ['base',],
    'description': '''This module Lets you enter the customer and supplier references attributed by the partners in their information systems.
These references may be different for each company managed in the OpenERP database.''',
    'demo_xml' : [],
    'init_xml' : [],
    'update_xml' : [
        'partner_view.xml',
    ],
    'active': False,
    'installable': True
}


