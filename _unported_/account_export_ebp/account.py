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

from openerp.osv import fields, osv
from openerp.tools.translate import _


class account_fiscalyear(osv.osv):
    _inherit = "account.fiscalyear"
    _columns = {
        # make the company id mandatory
        'company_id': fields.many2one('res.company', 'Company', required=True,
            help="The company this fiscal year belongs to."),
        'ebp_nb': fields.integer('EBP Fiscal Year Number',
            help="""This value should reflect the number of the fiscal year as used by the EBP accounting software. This should be set to the number of fiscal years recorded in EBP accounting before this one - So for the first year the number is 0, for the second year the number is 1 and so on. This is used for exporting accounting moves to EBP."""),
    }
    _defaults = {
        'ebp_nb': lambda * a: 0
    }


class account_move(osv.osv):
    _inherit = "account.move"
    _columns = {
        'exported_ebp': fields.boolean('Transfered to EBP', select=1,
            help="""Indicates whether the move has already been exported to EBP or not. It is changed automatically."""),
    }
    _defaults = {
        'exported_ebp': False,
    }

    def write(self, cr, uid, ids, vals, context=None):
        """Refuse to change changes exported Moves"""
        if 'exported_ebp' not in vals:
            exported_move_ids = self.search(cr, uid, [('exported_ebp', '=', True), ('id', 'in', ids)])
            if exported_move_ids:
                exported_moves = self.browse(cr, uid, exported_move_ids, context=context)
                raise osv.except_osv(_('Exported move!'),
                                     _('You cannot modify exported moves: %s!')
                                        % ', '.join([m.name for m in exported_moves]))
        return super(osv.osv, self).write(cr, uid, ids, vals, context=context)

    def unlink(self, cr, uid, ids, context=None, check=True):
        """Refuse to delete exported Moves"""
        exported_move_ids = self.search(cr, uid, [('exported_ebp', '=', True), ('id', 'in', ids)])
        if exported_move_ids:
            exported_moves = self.browse(cr, uid, exported_move_ids, context=context)
            raise osv.except_osv(_('Exported move!'),
                                 _('You cannot delete exported moves: %s!')
                                     % ', '.join([m.name for m in exported_moves]))
        return super(account_move, self).unlink(cr, uid, ids, context)

