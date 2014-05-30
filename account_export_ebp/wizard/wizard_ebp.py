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
from openerp.tools.translate import _
from openerp.osv import osv, fields
from account.account import _logger
import base64
import codecs
import smbc


class wizard_ebp(osv.TransientModel):

    _name = 'wizard.export_ebp'
    _description = 'Export to EBP'

    _columns = {
        'fiscalyear_id': fields.many2one('account.fiscalyear',
                                         'Fiscal year',
                                         required=True,
                                         help='Only the moves in this fiscal will be exported'),
        'ignore_draft': fields.boolean('Ignore draft moves',
                                       help='Please be aware that draft moves do not not have a move number attached to them. ' \
                                       'As a consequence, they might not be imported correctly into EBP accounting software'),
        'ignore_exported': fields.boolean('Ignore moves already exported',
                                          help='Check this box unless you want to re-export moves to EBP'),
        'partner_accounts': fields.boolean("Append partners' code to accounts",
                                           help="When this is checked, the partner's special code will be appended to the " \
                                           "receivable and payable accounts' numbers in the exported files on every move line " \
                                           "where a partner has been specified. " \
                                           "By default it has no effect, but can by customized by OpenERP developers."),
        'state': fields.selection((
                    ('choose', 'choose'),   # choose options
                    ('get', 'get'),         # get the files
                    )),
        'export_type': fields.selection((
                    ('smb', 'Write directly on server'),  # use smb protocol to write files (old method)
                    ('download', 'Download from browser'),  # download file in local computer (new method)
                    )),
        'data_writes': fields.binary('File', readonly=True),
        'name_writes': fields.char('Filename writes', 255, readonly=True),
        'data_accounts': fields.binary('File', readonly=True),
        'name_accounts': fields.char('Filename accounts', 255, readonly=True),

        'exported_moves': fields.float('Number of exported moves', digits=(12, 0)),
        'exported_lines': fields.float('Number of exported moves', digits=(12, 0)),
        'ignored_moves': fields.float('Number of exported moves', digits=(12, 0)),
        'exported_accounts': fields.float('Number of exported moves', digits=(12, 0))
                }

    _defaults = {
        'partner_accounts': lambda * a: True,
        'ignore_draft': lambda * a: True,
        'ignore_exported': lambda * a: True,
        'state': lambda *a: 'choose',
        'export_type': lambda *a: 'smb',
    }

    def export(self, cr, uid, ids, context=None):
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
        wizard = self.browse(cr, uid, ids[0], context=context)

        # Read the EBP year number name from the selected fiscal year
        fiscalyear = self.pool['account.fiscalyear'].browse(cr, uid,
            [wizard.fiscalyear_id.id], context)

        # Sanity checks
        if context['active_model'] != 'account.move':
            raise osv.except_osv(_('Wrong Object'),
                _('''This wizard should only be used on accounting moves'''))

        # dictionary to store accounts while we loop through move lines
        accounts_data = {}
        # Line counter
        l = 0
        moves = self.pool['account.move'].browse(cr, uid, context['active_ids'], context)
        moves_lines = []

        exported_move_ids = []
        ignored_move_ids = []
        for move in moves:
            # Ignore draft moves unless the user asked for them
            ignore_draft = (wizard.ignore_draft and move.state == 'draft')
            # Ignore moves in other fiscal years
            ignore_year = (move.period_id.fiscalyear_id.id != wizard.fiscalyear_id.id)
            # Ignore moves already exported
            ignore_exported = (wizard.ignore_exported and move.exported_ebp)
            # Skip to next move if this one should be ignored
            if ignore_draft or ignore_year or ignore_exported:
                _logger.debug("Ignoring move %d - draft: %s, wrong year: %s, exported: %s" %
                    (move.id, ignore_draft, ignore_year, ignore_exported))
                ignored_move_ids.append(move.id)
                continue

            _logger.debug("Exporting move %d" % move.id)
            moves_data = {}  # dictionary to summarize the lines of the move by account
            for line in move.line_id:
                _logger.debug(
                    "Examining move line %d" % line.id)

                if line.credit == line.debit:
                    _logger.debug(
                        "Move line %d has a sum equal to zero and will not be exported." % line.id)
                    continue

                # Make up the account number
                account_nb = line.account_id.code
                if (wizard.partner_accounts
                    and line.partner_id
                    and line.partner_id.ref_nb
                    and (line.account_id.type in ('payable', 'receivable'))):
                    # Partner account
                    account_nb = account_nb + line.partner_id.ref_nb

                # Check the most important fields are not above the maximum length
                # so as not to export wrong data with catastrophic consequence
                if len(move.journal_id.code) > 4:
                    raise osv.except_osv(_('Journal code too long'),
                        _('Journal code "%s" is too long to be exported to EBP.') %
                            move.journal_id.code)
                # The docs from EBP state that account codes may be up to
                # 15 characters but "EBP Comptabilité" v13 will refuse anything
                # longer than 10 characters
                if len(account_nb) > 10:
                    raise osv.except_osv(_('Account code too long'),
                        _('Account code "%s" is too long to be exported to EBP.') %
                            account_nb)
                if len(move.name) > 15:
                    raise osv.except_osv(_('Move name too long'),
                        _('Move name "%s" is too long to be exported to EBP.') %
                            move.name)

                # Collect data for the file of move lines
                if account_nb not in moves_data.keys():
                    moves_data[account_nb] = {
                        'date': move.date,
                        'journal': move.journal_id.code,
                        'ref': move.ref or move.name,
                        'name': move.name,
                        'credit': line.credit - line.debit,
                        'date_maturity': line.date_maturity,
                    }
                else:
                    moves_data[account_nb]['credit'] += line.credit - line.debit
                    # Keep the earliest maturity date
                    if line.date_maturity < moves_data[account_nb]['date_maturity']:
                        moves_data[account_nb]['date_maturity'] = line.date_maturity

                # Collect data for the file of accounts
                # We can't just keep the account_id object because the data we want
                # to export may be partner specific
                if account_nb not in accounts_data.keys():
                    if (wizard.partner_accounts
                        and line.partner_id
                        and line.partner_id.ref_nb
                        and line.account_id.type in ('payable', 'receivable')):
                        # Partner account
                        # Get the default address
                        address_id = self.pool['res.partner'].address_get(cr, uid,
                            [line.partner_id.id])['default']
                        address = self.pool['res.partner.address'].browse(cr, uid,
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
            _logger.debug("Exporting the move summary")
            for account_nb, line in moves_data.iteritems():
                l += 1
                #moves_file.write(','.join([
                moves_lines.append(','.join([
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
                    #fiscalyear.company_id.currency_id.name.replace(',', ''),
                ]))
                #moves_file.write('\r\n')
            exported_move_ids.append(move.id)

        # Mark the moves as exported to EBP
        if len(exported_move_ids):
            self.pool['account.move'].write(cr, uid, exported_move_ids,
                {'exported_ebp': True, })

        account_lines = []

        for account_nb, account in accounts_data.iteritems():
            account_lines.append(','.join([
                account_nb.replace(',', ''),  # Account number
                (account['name'] or '').replace(',', '')[:60],  # Account name
                (account['partner_name'] or '').replace(',', '')[:30],  # Partner
                (account['address'] or '').replace(',', '')[:100],  # Partner address
                (account['zip'] or '').replace(',', '')[:5],  # Zip code
                (account['city'] or '').replace(',', '')[:30],  # City
                (account['country'] or '').replace(',', '')[:35],  # Country
                (account['contact'] or '').replace(',', '')[:35],  # Contact
                (account['phone'] or '').replace(',', '')[:20],  # Phone
                (account['fax'] or '').replace(',', '')[:20],  # Fax
            ]))

        if wizard.export_type == 'smb':
            # Stream writer to convert Unicode to Windows Latin-1
            win_writer = codecs.getwriter('cp1252')
            path = '%s/Compta.%s' % (fiscalyear.company_id.ebp_uri, fiscalyear.ebp_nb)
            win_share = smbc.Context(
                auth_fn=lambda server, share, workgroup, username, password:
                    (fiscalyear.company_id.ebp_domain,
                     fiscalyear.company_id.ebp_username,
                     fiscalyear.company_id.ebp_password))
            moves_file = win_writer(win_share.creat('%s/ECRITURES.TXT' % path))
            for line in moves_lines:
                moves_file.write(line)
                moves_file.write('\r\n')
            moves_file.close()

            accounts_file = win_writer(win_share.creat('%s/COMPTES.TXT' % path))
            for line in account_lines:
                accounts_file.write(line)
                accounts_file.write('\r\n')
            accounts_file.close()
            res = True

        elif wizard.export_type == 'download':
            data_writes = u"\n".join(moves_lines)
            out_writes = base64.encodestring(data_writes.encode("cp1252"))
            data_accounts = u"\n".join(account_lines)
            out_accounts = base64.encodestring(data_accounts.encode("cp1252"))

            self.write(cr, uid, ids, {'state': 'get', 'data_writes': out_writes, 'name_writes': 'ECRITURES.TXT',
                                              'data_accounts': out_accounts, 'name_accounts': 'COMPTES.TXT',
                                              'exported_moves': len(exported_move_ids), 'ignored_moves': len(ignored_move_ids),
                                              'exported_lines': l, 'exported_accounts': len(accounts_data)
                                              }, context=context)
            view_id = self.pool['ir.ui.view'].search(cr, uid, [('model', '=', 'wizard.export_ebp')])
            res = {
                    'type': 'ir.actions.act_window',
                    'res_model': 'wizard.export_ebp',
                    'name': _('Export EBP'),
                    'res_id': ids[0],
                    'view_type': 'form',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'target': 'new',
                    'nodestroy': True,
                    'context': context
                    }
        else:
            raise osv.except_osv(_('Wrong export type'),
                _('Export option is not valid or undefined !'))

        return res
