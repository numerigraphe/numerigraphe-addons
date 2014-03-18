# -*- coding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2014 Numérigraphe SARL. All Rights Reserved.
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
    'name': "Take uninvoiced Purchase Orders into account in Budget Lines",
    'version': '1.0',
    'author': u'Numérigraphe SARL',
    'category': 'Generic Modules/Accounting',
    'description': '''This module lets Budget manager take pending Purchase Orders into account in Budget Lines.
Normally the Budgets are based on the Entries of General Accounting, and may be filtered by Analytic Account.
The problem for purchase Budgets is that invoices may come in very late in the
process. This often hides future problems from the sight of the managers.

To help with this problem, this module lets Budget Manager include the amounts
of Purchase Order Lines that have been confirmed but not yet invoiced.''',
    'depends' : ['account_budget', 'purchase'],
    'data': [
        'account_budget_view.xml',
    ],
}
