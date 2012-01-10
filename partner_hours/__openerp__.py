# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2009 Numérigraphe SARL. All Rights Reserved.
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
    'name' : 'Opening hours and days off of the partners',
    'version' : '1.0',
    'author' : u'Numerigraphe',
    'category' : 'Custom',
    'depends' : ['base'],
    'description': """
This module adds fields to enter the weekly day off and opening hours of a contact.""",
    'demo_xml' : [],
    'init_xml' : [],
    'update_xml' : ['partner_view.xml'],
    'active': False,
    'installable': True,
    'license' : 'GPL-3',
}

