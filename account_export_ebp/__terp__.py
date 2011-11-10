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

{
    'name' : "Export accounting moves to EBP's accounting software",
    'version' : '0.5',
    'author' : u'Numérigraphe SARL',
    'website': 'http://numerigraphe.com',
    'category': 'Generic Modules/Accounting',
    'description': '''This module lets you export accounting moves and accounts to flat text files readable by 'EBP Comptabilité', an accounting software package widely spread in France.
The files are in the text format for EBP's software, version 3 and above.

The export feature is in the form of a wizard related to accounting moves, so that the person exporting the data can select which moves to export.

Three pieces of configuration need to be set:
- the company for each fiscal year
- the path to folder for each company in EBP's software
- the number of each fiscal year in these folders
If those are properly set, the files should be imported automatically as simulation moves by the EBP software next time the folder is opened.

Please note that the files will be generated in the server's file system hierarchy, which may demand some sort of remote access (CIFS mount points for example) if the machine hosting EBP's software is not the same.  
''',
    'depends' : ['base', 'account'],
    'init_xml' : [
    ],
    'update_xml' : [
        'account_export_ebp_wizard.xml',
        'res_company_view.xml',
        'account_view.xml',
    ],
    'demo_xml' : [],
    'active': False,
    'installable': True
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
