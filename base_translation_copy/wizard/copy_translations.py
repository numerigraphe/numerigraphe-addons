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

import wizard
import tools
import pooler
import netsvc
from osv import fields, osv
from tools.translate import _

class wizard_copy_translations(osv.osv_memory):
    """Wizard to copy the translations from a language to en_US
    
    When object model fields are translatable, only the English version is
    stored in the database table.
    The translations into other languages are stored as
    ir_translation object resources.
    This method will copy a translation to the English version in every
    object."""

    def _get_languages(self, cr, uid, context):
        """Find which languages are maintained in the database"""
        lang_obj = pooler.get_pool(cr.dbname).get('res.lang')
        ids = lang_obj.search(cr, uid, ['&', ('active', '=', True), ('code', '<>', 'en_US'), ('translatable', '=', True), ])
        langs = lang_obj.browse(cr, uid, ids)
        return [(lang.code, lang.name) for lang in langs]
    
    def act_destroy(self, *args):
        """Close the wizard window"""
        return {'type':'ir.actions.act_window_close' }

    def act_copy(self, cr, uid, ids, context=None):
        """Copy the translations from a language to en_US"""
    
        class BogusTranslation(Exception):
            """Exception class for bogus translation entries"""
            pass

        logger = netsvc.Logger()
        wizard = self.browse(cr, uid, ids)[0]
        trans_obj = pooler.get_pool(cr.dbname).get('ir.translation')
        logger.notifyChannel(self._name, netsvc.LOG_INFO,
                             "Copying translations from %s to en_US" % wizard.lang)
        
        # Read all the model translations in the new language (except system objects and XML data)
        trans_ids = trans_obj.search(cr, uid, [
                ('type', '=', 'model'),
                ('lang', '=', wizard.lang),
                ('value', '!=', ''),
                ('name', 'not ilike', 'ir.%'),
                ('xml_id', '=', False),
            ], context=None)
        for trans in trans_obj.browse(cr, uid, trans_ids, context=None):
            try:
                # Get the object and field name
                (model, field) = trans.name.split(',', 1)
                # Read the English version from the object
                object = pooler.get_pool(cr.dbname).get(model)
                if object is None:
                    raise BogusTranslation(trans.id, "unknown model %s" % model)
                value = object.read(cr, uid, trans.res_id, fields=[field],
                    context=None)
                if not value:
                    raise BogusTranslation(trans.id, "record not found: %s,%d" % (model, trans.res_id))
                if field not in value:
                    raise BogusTranslation(trans.id, "unknown field: %s.%s" % (model, field))
                if value[field] != trans.src:
                    raise BogusTranslation(trans.id, u"source string does not match the record")
                if value[field] != trans.value:
                    logger.notifyChannel(self._name, netsvc.LOG_DEBUG,
                        "Changing %s in %s,%d from %s to %s" % (
                            field, model, trans.res_id, value[field], trans.value))
                    # Copy the versions in the new language to the English version
                    # We could pass trans.res_id as a single integer,
                    # but some buggy objects would break
                    object.write(cr, uid, [trans.res_id], {field: trans.value}, context=None)
                    # Remove the translation, it's now useless
                    trans_obj.unlink(cr, uid, trans.id, context=None)
            except BogusTranslation as error:
                # Useless translation detected
                logger.notifyChannel(self._name, netsvc.LOG_DEBUG,
                                     "Bogus translation with id %d: %s" % tuple(error.args))
                if wizard.delete_bogus:
                    trans_obj.unlink(cr, uid, error.args[0], context=None)
                continue
        logger.notifyChannel(self._name, netsvc.LOG_INFO, "Done")
        return self.write(cr, uid, ids, {'state':'done'}, context=context)

    def run(self, cr, uid, lang, delete_bogus=False, context=None):
        """Run the wizard on a given language - useful as a cron task"""
        id = self.create(cr, uid, {'lang':lang, 'delete_bogus': delete_bogus},
                         context=context)
        self.act_copy(cr, uid, [id], context=context)
        return True
    
    _name = "wizard.translation.copy"
    _columns = {
            'lang': fields.selection(_get_languages, 'Language', required=True,
                 help='All the strings in English will be overwritten with the translations from language.'),
            'state': fields.selection((('choose', 'choose'), # step 1: choose language
                                         ('done', 'done'), # step 2: copy done
                                       ), required=True),
            'delete_bogus': fields.boolean('Delete bogus translations')
            }
    _defaults = {
                 'state': lambda *a: 'choose',
                 'delete_bogus': lambda *a: False,
                }
wizard_copy_translations()
