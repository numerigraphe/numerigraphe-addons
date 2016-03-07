# -*- coding: utf-8 -*-
# © 2016 Numérigraphe
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ProductCategory(models.Model):
    _inherit = 'product.category'

    lot_firstuse_locked = fields.Boolean(
        string='Block new "First Use" lots', default=True,
        help='If checked, future Serial Numbers/lots of products in the state '
             '"First Use" will be created blocked by default')
