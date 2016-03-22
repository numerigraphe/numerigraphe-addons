# -*- coding: utf-8 -*-
# © 2009-2016 Numérigraphe SARL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    property_supplier_ref = fields.Char(
        string='Our Supplier Ref.',
        company_dependent=True,
        help="The reference attributed by the partner to the current "
             "company as a supplier of theirs.")
    property_customer_ref = fields.Char(
        string='Our Customer Ref.',
        company_dependent=True,
        help="The reference attributed by the partner to the current "
             "company as a customer of theirs.")
