# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2010 Numérigraphe SARL. All Rights Reserved.
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
    'name' : 'Search invoices by partner category',
    'version' : '1.0',
    'author' : u'Numérigraphe SARL',
    'website': 'http://numerigraphe.com',
    'category': 'Generic Modules/Accounting',
    'description': """This module lets you search invoices by partner category.""",
    'depends' : [
        'account',
    ],
    'init_xml' : [],
    'update_xml' : [
        'account_partner_category_view.xml',
    ],
    'demo_xml': [],
    'active': False,
    'installable': True,
}


