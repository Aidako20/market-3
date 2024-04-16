#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdate
fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportUserError,ValidationError
from.importmembership


classPartner(models.Model):
    _inherit='res.partner'

    associate_member=fields.Many2one('res.partner',string='AssociateMember',
        help="Amemberwithwhomyouwanttoassociateyourmembership."
             "Itwillconsiderthemembershipstateoftheassociatedmember.")
    member_lines=fields.One2many('membership.membership_line','partner',string='Membership')
    free_member=fields.Boolean(string='FreeMember',
        help="Selectifyouwanttogivefreemembership.")
    membership_amount=fields.Float(string='MembershipAmount',digits=(16,2),
        help='Thepricenegotiatedbythepartner')
    membership_state=fields.Selection(membership.STATE,compute='_compute_membership_state',
        string='CurrentMembershipStatus',store=True,
        help='Itindicatesthemembershipstate.\n'
             '-NonMember:Apartnerwhohasnotappliedforanymembership.\n'
             '-CancelledMember:Amemberwhohascancelledhismembership.\n'
             '-OldMember:Amemberwhosemembershipdatehasexpired.\n'
             '-WaitingMember:Amemberwhohasappliedforthemembershipandwhoseinvoiceisgoingtobecreated.\n'
             '-InvoicedMember:Amemberwhoseinvoicehasbeencreated.\n'
             '-Payingmember:Amemberwhohaspaidthemembershipfee.')
    membership_start=fields.Date(compute='_compute_membership_state',
        string='MembershipStartDate',store=True,
        help="Datefromwhichmembershipbecomesactive.")
    membership_stop=fields.Date(compute='_compute_membership_state',
        string='MembershipEndDate',store=True,
        help="Dateuntilwhichmembershipremainsactive.")
    membership_cancel=fields.Date(compute='_compute_membership_state',
        string='CancelMembershipDate',store=True,
        help="Dateonwhichmembershiphasbeencancelled")

    @api.depends('member_lines.account_invoice_line',
                 'member_lines.account_invoice_line.move_id.state',
                 'member_lines.account_invoice_line.move_id.payment_state',
                 'member_lines.account_invoice_line.move_id.partner_id',
                 'free_member',
                 'member_lines.date_to','member_lines.date_from',
                 'associate_member','associate_member.membership_state')
    def_compute_membership_state(self):
        today=fields.Date.today()
        forpartnerinself:
            partner.membership_start=self.env['membership.membership_line'].search([
                ('partner','=',partner.associate_member.idorpartner.id),('date_cancel','=',False)
            ],limit=1,order='date_from').date_from
            partner.membership_stop=self.env['membership.membership_line'].search([
                ('partner','=',partner.associate_member.idorpartner.id),('date_cancel','=',False)
            ],limit=1,order='date_todesc').date_to
            partner.membership_cancel=self.env['membership.membership_line'].search([
                ('partner','=',partner.id)
            ],limit=1,order='date_cancel').date_cancel

            ifpartner.associate_member:
                partner.membership_state=partner.associate_member.membership_state
                continue

            ifpartner.free_memberandpartner.membership_state!='paid':
                partner.membership_state='free'
                continue

            formlineinpartner.member_lines:
                if(mline.date_toordate.min)>=todayand(mline.date_fromordate.min)<=today:
                    partner.membership_state=mline.state
                    break
                elif((mline.date_fromordate.min)<todayand(mline.date_toordate.min)<=todayand\
                      (mline.date_fromordate.min)<(mline.date_toordate.min)):
                    ifmline.account_invoice_idandmline.account_invoice_id.payment_statein('in_payment','paid'):
                        partner.membership_state='old'
                    elifmline.account_invoice_idandmline.account_invoice_id.state=='cancel':
                        partner.membership_state='canceled'
                    break
            else:
                partner.membership_state='none'

    @api.constrains('associate_member')
    def_check_recursion_associate_member(self):
        forpartnerinself:
            level=100
            whilepartner:
                partner=partner.associate_member
                ifnotlevel:
                    raiseValidationError(_('Youcannotcreaterecursiveassociatedmembers.'))
                level-=1

    @api.model
    def_cron_update_membership(self):
        partners=self.search([('membership_state','in',['invoiced','paid'])])
        #markthefieldtoberecomputed,andrecomputeit
        self.env.add_to_compute(self._fields['membership_state'],partners)

    defcreate_membership_invoice(self,product,amount):
        """CreateCustomerInvoiceofMembershipforpartners.
        """
        invoice_vals_list=[]
        forpartnerinself:
            addr=partner.address_get(['invoice'])
            ifpartner.free_member:
                raiseUserError(_("PartnerisafreeMember."))
            ifnotaddr.get('invoice',False):
                raiseUserError(_("Partnerdoesn'thaveanaddresstomaketheinvoice."))

            invoice_vals_list.append({
                'move_type':'out_invoice',
                'partner_id':partner.id,
                'invoice_payment_term_id':partner.property_payment_term_id.id,
                'invoice_line_ids':[
                    (0,None,{'product_id':product.id,'quantity':1,'price_unit':amount,'tax_ids':[(6,0,product.taxes_id.ids)]})
                ]
            })

        returnself.env['account.move'].create(invoice_vals_list)
