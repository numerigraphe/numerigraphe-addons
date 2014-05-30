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
and Deliveries. Doing improves the feedback given to the persons who give the
orders (usually sales people, purchases managers or manufacturing managers),
by bringing logistic problems directly to their attention.

Simpler interface for logistic workers
--------------------------------------
Instead of letting partial operations be recorded through various wizards and
buttons, those are instead entered by only 3 buttons displayed consistently on
every documents:
 - cancel the move
 - split the stock move in two
 - confirm the move

Partial operations
------------------
Operations which cannot be done, or can only be done partially, are entered by
simply canceling the corresponding Stock Move.
Usually this Stock Move will have been associated to a procurement order:
canceling the Stock Move will then put the Procurement Order in a special state
which OpenERP will propagate to the original document (Purchase Order, Sale
Order...).

Purchase workflow
-----------------
The workflows of Purchase Orders is changed to take into account that some
reception lines may be cancelled while others are done in the same reception
picking. In such cases, the Purchase Order will go to the state
"Delivery exception" as if the whole reception had been cancelled.

API and external use
--------------------
This module exposes a simple method to split Stock Moves that is through
webservices.
This module does NOT disable the standard API for partial moves: it may still
be used through XML-RPC or custom modules.

Credits
-------
Split icon ©Yusuke Kamiyamane - http://p.yusukekamiyamane.com/. Licensed under
a Creative Commons Attribution 3.0 License.
""",
    # FIXME+TODOv7: average price is not updated anymore
    # FIXME+TODOv7: receptions cannot be recreated from purchase orders in exception state
    # TODOv7: make the move trees editable to let users enter the prodlot directly, make the other fields read-only
    # TODOv7: write to the sale/purchase order's chat when a stock move is cancelled
    # TODO: split the dependency on "purchase" to a 2nd module (auto-install)
    'depends': [
        'stock',
        'purchase',
    ],
    'data': [
        'wizard/stock_split_simple_view.xml',
        'stock_view.xml',
        'stock_workflow.xml',
        'purchase_workflow.xml',
    ],
    'license': 'AGPL-3',
}
