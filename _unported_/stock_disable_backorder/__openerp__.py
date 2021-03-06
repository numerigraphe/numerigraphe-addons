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
    'name': 'Disable back-orders',
    'version': '1.0',
    'author': u'Numérigraphe',
    'category': 'Warehouse',
    'description': """
Disable back-orders on logistic operations
==========================================

This module disables the creation of back-orders for Stock Moves, Receptions
and Deliveries. Doing so improves the feedback given to the persons who passed
the orders (usually sales people, purchases managers or manufacturing managers),
by bringing logistic problems directly to their attention.

Partial operations
------------------
Operations which cannot be done, or can only be done partially, are entered by
simply splitting the Stock Moves to enter the Serials of the goods processed,
and canceling the remaining Stock Move.
Usually this Stock Move will have been associated to a procurement order:
canceling the Stock Move will then put the Procurement Order in a special 
"exception" state which OpenERP will propagate to the original document
(Purchase Order, Sale Order...).

Sale/Purchase menus
-------------------
This module adds menu entries to easily find the sale/purchase orders which are
in an exception state, so that the commercial teams can handle them.

Purchase workflow
-----------------
The workflows of Purchase Orders is changed to take into account that some
reception lines may be cancelled while others are done in the same reception
picking. In such cases, the Purchase Order will go to the state
"Delivery exception" as if the whole reception had been cancelled.
""",
    # TODOv7: write to the sale/purchase order's chat when a stock move is cancelled
    # TODO: Warn (or block?) when making a picking which contains unassigned moves (or cancel them?)
    # TODO: split the dependency on "purchase" to a 2nd module (auto-install)
    'depends': [
        'stock',
        'purchase',
        'sale',
    ],
    'data': [
        'stock_view.xml',
        'stock_workflow.xml',
        'purchase_workflow.xml',
        'sale_view.xml',
        'purchase_view.xml',
    ],
    'license': 'AGPL-3',
}
