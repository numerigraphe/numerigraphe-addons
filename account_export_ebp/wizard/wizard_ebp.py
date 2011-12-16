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

import os
import codecs

import wizard
import pooler
import tools
from tools.translate import _
import netsvc

# XXX We should write to a temporary file instead, for security and reliability.
# XXX We should raise a clean exception if something goes wrong.
# TODO Add an option to download files instead of storing them on the server

# Form for the 1st step
export_form = '''
<form string="export_ebp">
    <field name="fiscalyear_id" colspan="4" />
    <group colspan="4">
        <field name="ignore_draft" colspan="4" />
        <field name="ignore_exported" colspan="4" />
        <field name="partner_accounts" colspan="4" />
    </group>
</form>
'''
# Fields for the 1st step
export_fields = {
    'fiscalyear_id': {
        'string': 'Fiscal year',
        'help': 'Only the moves in this fiscal will be exported',
        'type': 'many2one',
        'relation': 'account.fiscalyear',
        'required': True,
    },
    'partner_accounts': {
        'string': "Append partners' code to accounts",
        'help': "When this is checked, the partner's special code will be appended to the receivable and payable accounts' numbers in the exported files on every move line where a partner has been specified. By default it has no effect, but can by customized by OpenERP developers.",
        'default': lambda * a: True,
        'type': 'boolean',
        'required': True,
    },
    'ignore_draft': {
        'string': 'Ignore draft moves',
        'help': 'Please be aware that draft moves do not not have a move number attached to them. As a consequence, they might not be imported correctly into EBP accounting software',
        'default': lambda * a: True,
        'type': 'boolean',
        'required': True,
    },
    'ignore_exported': {
        'string': 'Ignore moves already exported',
        'help': 'Check this box unless you want to re-export moves to EBP',
        'default': lambda * a: True,
        'type': 'boolean',
        'required': True,
    },
}

# Form for the end step
result_form = '''
<form string="export_ebp_end">
    <separator string="Moves exported to EBP" colspan="4"/>
    <field name="exported_moves" colspan="4"/>
    <field name="exported_lines" colspan="4"/>
    <separator colspan="4"/>
    <field name="ignored_moves" colspan="4"/>
    <separator colspan="4"/>
    <field name="exported_accounts" colspan="4"/>
    <separator colspan="4"/>
    <label string="You may need to close and reopen the folder for EBP to detect the new data files." colspan="4"/>
</form>
'''
# Fields for the end step
result_fields = {
    'exported_moves': {
        'string': "Number of moves exported",
        'type': 'integer',
        'readonly': True
    },
    'ignored_moves': {
        'string': "Number of moves ignored",
        'type': 'integer',
        'readonly': True,
    },
    'exported_lines': {
        'string': "Number of lines exported",
        'type': 'integer',
        'readonly': True
    },
    'exported_accounts': {
        'string': "Number of accounts exported",
        'type': 'integer',
        'readonly': True
    },
}

def _export(self, cr, uid, data, context):
    """
    Export moves files usable by accounting software by EBP version 3 and above.
    
    2 files will be produced : 
      - a file of accounting moves (ECRITURES.TXT)
      - a file of accounts  (COMPTES.TXT)
    If stored in the right folder, these files will automatically be imported
    next time you open the folder in EBP.
    
    Lines with an amount of 0 are not ignored even though EBP complains about
    them. This is to raise the attention of the person importing them into EBP.
    Also, journals with a code which does not meet EBP's requirements are not
    ignored.
    
    Returns a dictionary containing the number of moves and lines exported and
    the number of moves ignored.
    """

    logger = netsvc.Logger()
    pool = pooler.get_pool(cr.dbname)
    logger.notifyChannel("ebp", netsvc.LOG_DEBUG, "Form data: %s" %
        data['form'])

    # Read the EBP year number name from the selected fiscal year
    fiscalyear = pool.get('account.fiscalyear').browse(cr, uid,
        data['form']['fiscalyear_id'], context)

    # Construct the path where files will be stored 
    path = os.sep.join([fiscalyear.company_id.ebp_folder or '',
        'Compta.%s' % fiscalyear.ebp_nb])
    # Sanity checks
    if data['model'] != 'account.move':
        raise wizard.except_wizard(_('Wrong Object'),
            _('''This wizard should only be used on accounting moves'''))
    if not os.path.exists(path):
        raise wizard.except_wizard(_('Path does not exist'),
           _('''The path "%s" does not exist in the server's file system hierarchy.''') % path)

    # dictionary to store accounts while we loop through move lines
    accounts_data = {}
    # Line counter
    l = 0
    moves = pool.get('account.move').browse(cr, uid, data['ids'], context)
    # The move summaries will be written to a CSV file encoded in win-latin-1
    moves_file = codecs.open(os.sep.join([path, 'ECRITURES.TXT']), 'w', 'cp1252')
    exported_move_ids = []
    ignored_move_ids = []
    for move in moves:
        # Ignore draft moves unless the user asked for them
        ignore_draft = (data['form']['ignore_draft'] and move.state == 'draft')
        # Ignore moves in other fiscal years
        ignore_year = (move.period_id.fiscalyear_id.id !=
                       data['form']['fiscalyear_id'])
        # Ignore moves already exported
        ignore_exported = (data['form']['ignore_exported']
                           and move.exported_ebp)
        # Skip to next move if this one should be ignored
        if ignore_draft or ignore_year or ignore_exported:
            logger.notifyChannel("ebp", netsvc.LOG_DEBUG,
                "Ignoring move %d - draft: %s, wrong year: %s, exported: %s" %
                (move.id, ignore_draft, ignore_year, ignore_exported))
            ignored_move_ids.append(move.id)
            continue

        logger.notifyChannel("ebp", netsvc.LOG_DEBUG,
            "Exporting move %d" % move.id)
        moves_data = {} # dictionary to summarize the lines of the move by account
        for line in move.line_id:
            logger.notifyChannel("ebp", netsvc.LOG_DEBUG,
                "Examining move line %d" % line.id)

            if line.credit == line.debit:
                logger.notifyChannel("ebp", netsvc.LOG_DEBUG,
                    "Move line %d has a sum equal to zero and will not be exported." % line.id)
                continue

            # Make up the account number
            account_nb = line.account_id.code
            if (data['form']['partner_accounts']
                and line.partner_id
                and line.partner_id.ref_nb
                and (line.account_id.type in ('payable', 'receivable'))):
                # Partner account
                account_nb = account_nb + line.partner_id.ref_nb

            # Check the most important fields are not above the maximum length
            # so as not to export wrong data with catastrophic consequence
            if len(move.journal_id.code) > 4:
                raise wizard.except_wizard(_('Journal code too long'),
                    _('Journal code "%s" is too long to be exported to EBP.') %
                        move.journal_id.code)
            # The docs from EBP state that account codes may be up to 
            # 15 characters but "EBP Comptabilité" v13 will refuse anything
            # longer than 10 characters
            if len(account_nb) > 10:
                raise wizard.except_wizard(_('Account code too long'),
                    _('Account code "%s" is too long to be exported to EBP.') %
                        account_nb)
            if len(move.name) > 15:
                raise wizard.except_wizard(_('Move name too long'),
                    _('Move name "%s" is too long to be exported to EBP.') %
                        move.name)

            # Collect data for the file of move lines
            if account_nb not in moves_data.keys():
                moves_data[account_nb] = {
                    'date' : move.date,
                    'journal' : move.journal_id.code,
                    'ref' : move.ref or move.name,
                    'name' : move.name,
                    'credit' : line.credit - line.debit,
                    'date_maturity' : line.date_maturity,
                }
            else:
                moves_data[account_nb]['credit'] += line.credit - line.debit;
                # Keep the earliest maturity date
                if line.date_maturity < moves_data[account_nb]['date_maturity']:
                    moves_data[account_nb]['date_maturity'] = line.date_maturity

            # Collect data for the file of accounts
            # We can't just keep the account_id object because the data we want
            # to export may be partner specific 
            if account_nb not in accounts_data.keys():
                if (data['form']['partner_accounts']
                    and line.partner_id
                    and line.partner_id.ref_nb
                    and line.account_id.type in ('payable', 'receivable')):
                    # Partner account
                    # Get the default address
                    address_id = pool.get('res.partner').address_get(cr, uid,
                        [line.partner_id.id])['default']
                    address = pool.get('res.partner.address').browse(cr, uid,
                        [address_id], context)[0]
                    accounts_data[account_nb] = {
                        'name': line.partner_id.name,
                        'partner_name': line.partner_id.name,
                        'address': address.street or address.street2,
                        'zip': address.zip,
                        'city': address.city,
                        'country': address.country_id.name,
                        'contact': address.name,
                        'phone': address.phone or address.mobile,
                        'fax': address.fax,
                    }
                else:
                    # Normal account
                    accounts_data[account_nb] = {
                        'name': line.account_id.name,
                        'partner_name': '',
                        'address': '',
                        'zip': '',
                        'city': '',
                        'country': '',
                        'contact': '',
                        'phone': '',
                        'fax': '',
                    }

        # Write the move summary to the file
        logger.notifyChannel("ebp", netsvc.LOG_DEBUG,
            "Writing the move summary to the file")
        for account_nb, line in moves_data.iteritems():
            l += 1
            moves_file.write(','.join([
                # Line number
                '%d' % l,
                # Date (ddmmyy)
                '%s%s%s' % (line['date'][8:10], line['date'][5:7],
                    line['date'][2:4]),
                # Journal
                line['journal'].replace(',', '')[:4],
                # Account number (possibly with the partner code appended to it)
                account_nb.replace(',', ''),
                # Automatic title (empty)
                '',
                # Manual title
                '"%s"' % line['ref'][:40],
                # Accountable receipt number
                '"%s"' % line['name'][:15],
                # Amount
                '%f' % abs(line['credit']),
                # [C]redit or [D]ebit
                (line['credit'] > 0) and 'C' or 'D',
                # Date of maturity (ddmmyy)
                line['date_maturity'] and '%s%s%s' % (
                    line['date_maturity'][8:10],
                    line['date_maturity'][5:7],
                    line['date_maturity'][2:4]) or '',
                # Currency
                fiscalyear.company_id.currency_id.name.replace(',', ''),
            ]))
            moves_file.write('\r\n')
        exported_move_ids.append(move.id)

    # Mark the moves as exported to EBP
    if len(exported_move_ids):
        pool.get('account.move').write(cr, uid, exported_move_ids,
            {'exported_ebp': True, })

    # Close the move summaries file
    moves_file.close()
    logger.notifyChannel("ebp", netsvc.LOG_INFO,
        "%d line(s) representing %d move(s) exported to ECRITURES.TXT in %s - %d move(s) ignored" %
        (l, len(exported_move_ids), path, len(ignored_move_ids)))

    # Write the accounts to a CSV file encoded in windows latin-1
    accounts_file = codecs.open(os.sep.join([path, 'COMPTES.TXT']), 'w',
        'cp1252')
    for account_nb, account in accounts_data.iteritems():
        accounts_file.write(','.join([
            account_nb.replace(',', ''), # Account number
            (account['name'] or '').replace(',', '')[:60], # Account name
            (account['partner_name'] or '').replace(',', '')[:30], # Partner
            (account['address'] or '').replace(',', '')[:100], # Partner address
            (account['zip'] or '').replace(',', '')[:5], # Zip code
            (account['city'] or '').replace(',', '')[:30], # City
            (account['country'] or '').replace(',', '')[:35], # Country
            (account['contact'] or '').replace(',', '')[:35], # Contact
            (account['phone'] or '').replace(',', '')[:20], # Phone
            (account['fax'] or '').replace(',', '')[:20], # Fax
        ]))
        accounts_file.write('\r\n')
    accounts_file.close()
    logger.notifyChannel("ebp", netsvc.LOG_INFO,
        "%d accounts(s) exported to COMPTES.TXT in %s" %
        (len(accounts_data), path)
    )

    return {
        'exported_moves': len(exported_move_ids),
        'ignored_moves': len(ignored_move_ids),
        'exported_lines': l,
        'exported_accounts': len(accounts_data),
    }

class wizard_ebp(wizard.interface):
    states = {
        'init': {
            'actions':[],
            'result': {
                'type': 'form',
                'arch': export_form,
                'fields': export_fields,
                'state': [
                    ('end', 'Cancel', 'gtk-cancel'),
                    ('export', 'Export', 'gtk-go-forward')
                ]
            }
        },
        'export': {
            'actions':[_export],
            'result': {
                'type': 'state',
                'state':'end_form',
            }
        },
        'end_form': {
            'actions':[],
            'result': {
                'type': 'form',
                'arch': result_form,
                'fields': result_fields,
                'state': [('end', 'OK')],
            }
        },
    }
wizard_ebp('account.export.ebp')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
