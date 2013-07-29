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

from osv import fields, osv

class PurchaseBudget(osv.osv_memory):
    _name = 'purchase.budget.wizard'
    _columns = {
        'budget_line_ids': fields.many2many("crossovered.budget.lines",
                                            rel='purchase_budget_lines_rel',
                                            id1='order_id', id2='line_id',
                                            string='Budget Lines',
                                            readonly=True),
    }
PurchaseBudget()
