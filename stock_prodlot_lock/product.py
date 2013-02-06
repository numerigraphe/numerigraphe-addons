# -*- encoding: utf-8 -*-
##############################################################################
#
#    This module is copyright (C) 2011 Numérigraphe SARL. All Rights Reserved.
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

from osv import osv
from osv import fields
from tools.translate import _

class product_category(osv.osv):

    _inherit = 'product.category'

    _columns = {
        'need_quality': fields.boolean('Quality Control', help="If checked, new production lots will be locked by default, allowing quality control to take place."),
    }

    _defaults = {
         'need_quality': lambda *a: False,
    }

    def create(self, cr, uid, values, context=None):
        """
        check if the parent need quality
        """
        if 'parent_id' in values and 'need_quality' not in values:
            values['need_quality'] = self.read(cr, uid, values.get('parent_id'), ['need_quality'], context=context).get('need_quality', False)
        return  super(product_category, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        """
        check if the parent need quality and force need quality in children
        """
        if not isinstance(ids, list):
            ids = [ids]
        need_quality = values.get('need_quality', None)
        if need_quality is None and 'parent_id' in values:
            need_quality = self.read(cr, uid, values.get('parent_id'), ['need_quality'], context=context).get('need_quality', False)
        # the variable need quality can be change
        if need_quality is not None:
            # add need quality in values to force it
            values['need_quality'] = need_quality
            # force children
            child_ids = self.search(cr, uid, [('parent_id', 'in', ids)], context=context)
            if child_ids:
                self.write(cr, uid, child_ids, {'need_quality': need_quality}, context=context)
        return super(product_category, self).write(cr, uid, ids, values, context=context)
product_category()

class product_template(osv.osv):
    
    _inherit = 'product.template'
    
    _columns = {
        'state': fields.selection([('',''),
            ('draft', 'In Development'),
            ('first', 'First in Use'),
            ('sellable','Normal'),
            ('end','End of Lifecycle'),
            ('obsolete','Obsolete')], 'Status', help="Tells the user if he can use the product or not.")
    }
    
product_template()
    
class product_label(osv.osv):

    _inherit = 'product.label'

    _columns = {
        'need_quality': fields.boolean('Quality Control', help="If checked, new production lots will be locked by default, allowing quality control to take place."),
    }

    _defaults = {
         'need_quality': lambda *a: False,
    }

    def create(self, cr, uid, values, context=None):
        """
        check if the parent need quality
        """
        if 'parent_id' in values and 'need_quality' not in values:
            values['need_quality'] = self.read(cr, uid, values.get('parent_id'), ['need_quality'], context=context).get('need_quality', False)
        return  super(product_label, self).create(cr, uid, values, context=context)

    def write(self, cr, uid, ids, values, context=None):
        """
        check if the parent need quality and force need quality in children
        """
        if not isinstance(ids, list):
            ids = [ids]
        need_quality = values.get('need_quality', None)
        if need_quality is None and 'parent_id' in values:
            need_quality = self.read(cr, uid, values.get('parent_id'), ['need_quality'], context=context).get('need_quality', False)
        # the variable need quality can be change
        if need_quality is not None:
            # add need quality in values to force it
            values['need_quality'] = need_quality
            # force children
            child_ids = self.search(cr, uid, [('parent_id', 'in', ids)], context=context)
            if child_ids:
                self.write(cr, uid, child_ids, {'need_quality': need_quality}, context=context)
        return super(product_label, self).write(cr, uid, ids, values, context=context)
product_label()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
