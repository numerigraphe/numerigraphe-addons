# -*- encoding: utf-8 -*-
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
    'name': 'Search sales by partner category',
    'version': '0.1',
    'author' : u'Numérigraphe SARL',
    'website': 'http://numerigraphe.com',
    'category': 'Sale',
    'description': """This module lets you search sales by partner category.""",
    'depends': [
        'sale',
        'account_partner_category',
    ],
    'init_xml': [],
    'update_xml': [
        'sale_partner_category_view.xml',
    ],
    'demo_xml': [],
    'active': False,
    'installable': True,
#    'license': 'AGPL-3', # XXX Bug #520854: Missing license options

}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
