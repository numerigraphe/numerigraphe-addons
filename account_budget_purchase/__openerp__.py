# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2013 Numérigraphe SARL. All Rights Reserved.
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
    'name': "Warn when a Purchase Order goes beyond a Budget line",
    'version': '1.0',
    'author': u'Numérigraphe SARL',
    'category': 'Generic Modules/Accounting',
    'description': '''This will display a warning when validating a purchase order if the remaining budget from a Budget Line is not sufficient to pay the expected invoice.''',
    'depends' : ['account_budget', 'purchase'],
    'data': [
        'purchase_workflow.xml',
        'purchase_view.xml',
        'wizard/purchase_budget_view.xml',
        'security/ir.model.access.csv',
    ],
    'test': [
        # FIXME
    ]
}