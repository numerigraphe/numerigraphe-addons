# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2009 Numérigraphe SARL.
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

from osv import osv, fields

class partner(osv.osv):
    _inherit = 'res.partner'
    _columns = {
        'partner_ref_ids': fields.one2many('res.partner.ref', 'partner_id', 'Partner References', help="The references attributed by the partner to the companies managed in this database.")
    }
partner()

class partner_ref(osv.osv):
    _name = 'res.partner.ref'
    _description = 'Partner Reference'
    _order = 'partner_id, company_id, type, name'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'type': fields.selection((('customer', 'Customer Ref.'),
                                   ('supplier', 'Supplier Ref.')),
                   'Reference Type', required=True, help="The type of reference attributed to this company by the partner: Customer Ref. if the partner is a supplier, Supplier Ref. if it's a customer"),
        'name': fields.char('Reference', size=64, help="The reference attributed to this company by the partner.", required=True),
    }
    _defaults = {
         'company_id': lambda self, cr, uid, context: self.pool.get('res.users').browse(cr, uid, uid, context=context).company_id.id,
         'type': lambda * a: 'customer'
    }
partner_ref()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

