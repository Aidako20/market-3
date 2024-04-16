#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportapi,fields,models,_,tools


classMassMailing(models.Model):
    _name='mailing.mailing'
    _inherit='mailing.mailing'

    sale_quotation_count=fields.Integer('QuotationCount',groups='sales_team.group_sale_salesman',compute='_compute_sale_quotation_count')
    sale_invoiced_amount=fields.Integer('InvoicedAmount',groups='sales_team.group_sale_salesman',compute='_compute_sale_invoiced_amount')

    @api.depends('mailing_domain')
    def_compute_sale_quotation_count(self):
        has_so_access=self.env['sale.order'].check_access_rights('read',raise_exception=False)
        formass_mailinginself:
            mass_mailing.sale_quotation_count=self.env['sale.order'].search_count(mass_mailing._get_sale_utm_domain())ifhas_so_accesselse0

    @api.depends('mailing_domain')
    def_compute_sale_invoiced_amount(self):
        formass_mailinginself:
            ifself.user_has_groups('sales_team.group_sale_salesman')andself.user_has_groups('account.group_account_invoice'):
                domain=mass_mailing._get_sale_utm_domain()+[('state','notin',['draft','cancel'])]
                moves=self.env['account.move'].search_read(domain,['amount_untaxed_signed'])
                mass_mailing.sale_invoiced_amount=sum(i['amount_untaxed_signed']foriinmoves)
            else:
                mass_mailing.sale_invoiced_amount=0

    defaction_redirect_to_quotations(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain']=self._get_sale_utm_domain()
        action['context']={'create':False}
        returnaction

    defaction_redirect_to_invoiced(self):
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        moves=self.env['account.move'].search(self._get_sale_utm_domain())
        action['context']={
            'create':False,
            'edit':False,
            'view_no_maturity':True
        }
        action['domain']=[
            ('id','in',moves.ids),
            ('move_type','in',('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt')),
            ('state','notin',['draft','cancel'])
        ]
        action['context']={'create':False}
        returnaction

    def_get_sale_utm_domain(self):
        res=[]
        ifself.campaign_id:
            res.append(('campaign_id','=',self.campaign_id.id))
        ifself.source_id:
            res.append(('source_id','=',self.source_id.id))
        ifself.medium_id:
            res.append(('medium_id','=',self.medium_id.id))
        ifnotres:
            res.append((0,'=',1))
        returnres

    def_prepare_statistics_email_values(self):
        self.ensure_one()
        values=super(MassMailing,self)._prepare_statistics_email_values()
        ifnotself.user_id:
            returnvalues

        self_with_company=self.with_company(self.user_id.company_id)
        currency=self.user_id.company_id.currency_id
        formated_amount=tools.format_decimalized_amount(self_with_company.sale_invoiced_amount,currency)

        values['kpi_data'][1]['kpi_col2']={
            'value':self.sale_quotation_count,
            'col_subtitle':_('QUOTATIONS'),
        }
        values['kpi_data'][1]['kpi_col3']={
            'value':formated_amount,
            'col_subtitle':_('INVOICED'),
        }
        returnvalues
