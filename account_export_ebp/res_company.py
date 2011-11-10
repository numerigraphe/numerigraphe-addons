# -*- encoding: utf-8 -*-
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

"""Parameters for EBP export"""

from osv import fields, osv

class res_company(osv.osv):
    """Add parameters to export accounting moves to EBP's software"""
    _inherit = 'res.company'
    _columns = {
        'ebp_folder': fields.char('EBP folder', size = 256,
            help = """This is the path to the company's folder in the EBP accounting software, as seen from the server's file system.
On a typical setup, the accountant would host EBP's software on his computer and share the EBP folders (usually in C:\Documents and Settings\All Users\Documents\EBP\Partage\Dossiers\<YOUR_COMPANY>).
This share would then be mounted (by means of SMB, or NFS for example) into the server's file system hierarchy.  
This is used for exporting accounting moves to EBP."""),
    }
res_company()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
