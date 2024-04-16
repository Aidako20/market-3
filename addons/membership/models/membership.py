#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models

STATE=[
    ('none','NonMember'),
    ('canceled','CancelledMember'),
    ('old','OldMember'),
    ('waiting','WaitingMember'),
    ('invoiced','InvoicedMember'),
    ('free','FreeMember'),
    ('paid','PaidMember'),
]


classMembershipLine(models.Model):
    _name='membership.membership_line'
    _rec_name='partner'
    _order='iddesc'
    _description='MembershipLine'

    partner=fields.Many2one('res.partner',string='Partner',ondelete='cascade',index=True)
    membership_id=fields.Many2one('product.product',string="Membership",required=True)
    date_from=fields.Date(string='From',readonly=True)
    date_to=fields.Date(string='To',readonly=True)
    date_cancel=fields.Date(string='Canceldate')
    date=fields.Date(string='JoinDate',
        help="Dateonwhichmemberhasjoinedthemembership")
    member_price=fields.Float(string='MembershipFee',
        digits='ProductPrice',required=True,
        help='Amountforthemembership')
    account_invoice_line=fields.Many2one('account.move.line',string='AccountInvoiceline',readonly=True,ondelete='cascade')
    account_invoice_id=fields.Many2one('account.move',related='account_invoice_line.move_id',string='Invoice',readonly=True)
    company_id=fields.Many2one('res.company',related='account_invoice_line.move_id.company_id',string="Company",readonly=True,store=True)
    state=fields.Selection(STATE,compute='_compute_state',string='MembershipStatus',store=True,
        help="Itindicatesthemembershipstatus.\n"
             "-NonMember:Amemberwhohasnotappliedforanymembership.\n"
             "-CancelledMember:Amemberwhohascancelledhismembership.\n"
             "-OldMember:Amemberwhosemembershipdatehasexpired.\n"
             "-WaitingMember:Amemberwhohasappliedforthemembershipandwhoseinvoiceisgoingtobecreated.\n"
             "-InvoicedMember:Amemberwhoseinvoicehasbeencreated.\n"
             "-PaidMember:Amemberwhohaspaidthemembershipamount.")

    @api.depends('account_invoice_id.state',
                 'account_invoice_id.amount_residual',
                 'account_invoice_id.payment_state')
    def_compute_state(self):
        """Computethestatelines"""
        ifnotself:
            return

        self._cr.execute('''
            SELECTreversed_entry_id,COUNT(id)
            FROMaccount_move
            WHEREreversed_entry_idIN%s
            GROUPBYreversed_entry_id
        ''',[tuple(self.mapped('account_invoice_id.id'))])
        reverse_map=dict(self._cr.fetchall())
        forlineinself:
            move_state=line.account_invoice_id.state
            payment_state=line.account_invoice_id.payment_state

            line.state='none'
            ifmove_state=='draft':
                line.state='waiting'
            elifmove_state=='posted':
                ifpayment_state=='paid':
                    ifreverse_map.get(line.account_invoice_id.id):
                        line.state='canceled'
                    else:
                        line.state='paid'
                elifpayment_state=='in_payment':
                    line.state='paid'
                elifpayment_statein('not_paid','partial'):
                    line.state='invoiced'
            elifmove_state=='cancel':
                line.state='canceled'
