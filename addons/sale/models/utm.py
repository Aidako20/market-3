#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models,api,SUPERUSER_ID

classUtmCampaign(models.Model):
    _inherit='utm.campaign'
    _description='UTMCampaign'

    quotation_count=fields.Integer('QuotationCount',groups='sales_team.group_sale_salesman',compute="_compute_quotation_count")
    invoiced_amount=fields.Integer(default=0,compute="_compute_sale_invoiced_amount",string="Revenuesgeneratedbythecampaign")
    company_id=fields.Many2one('res.company',string='Company',readonly=True,states={'draft':[('readonly',False)],'refused':[('readonly',False)]},default=lambdaself:self.env.company)
    currency_id=fields.Many2one('res.currency',related='company_id.currency_id',string='Currency')

    def_compute_quotation_count(self):
        quotation_data=self.env['sale.order'].read_group([
            ('campaign_id','in',self.ids)],
            ['campaign_id'],['campaign_id'])
        data_map={datum['campaign_id'][0]:datum['campaign_id_count']fordatuminquotation_data}
        forcampaigninself:
            campaign.quotation_count=data_map.get(campaign.id,0)

    def_compute_sale_invoiced_amount(self):
        self.env['account.move.line'].flush(['balance','move_id','account_id','exclude_from_invoice_tab'])
        self.env['account.move'].flush(['state','campaign_id','move_type'])
        query="""SELECTmove.campaign_id,-SUM(line.balance)asprice_subtotal
                    FROMaccount_move_lineline
                    INNERJOINaccount_movemoveONline.move_id=move.id
                    WHEREmove.statenotin('draft','cancel')
                        ANDmove.campaign_idIN%s
                        ANDmove.move_typeIN('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt')
                        ANDline.account_idISNOTNULL
                        ANDNOTline.exclude_from_invoice_tab
                    GROUPBYmove.campaign_id
                    """

        self._cr.execute(query,[tuple(self.ids)])
        query_res=self._cr.dictfetchall()

        campaigns=self.browse()
        fordatuminquery_res:
            campaign=self.browse(datum['campaign_id'])
            campaign.invoiced_amount=datum['price_subtotal']
            campaigns|=campaign
        forcampaignin(self-campaigns):
            campaign.invoiced_amount=0

    defaction_redirect_to_quotations(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['domain']=[('campaign_id','=',self.id)]
        action['context']={
            'create':False,
            'edit':False,
            'default_campaign_id':self.id
        }
        returnaction

    defaction_redirect_to_invoiced(self):
        action=self.env["ir.actions.actions"]._for_xml_id("account.action_move_journal_line")
        invoices=self.env['account.move'].search([('campaign_id','=',self.id)])
        action['context']={
            'create':False,
            'edit':False,
            'view_no_maturity':True
        }
        action['domain']=[
            ('id','in',invoices.ids),
            ('move_type','in',('out_invoice','out_refund','in_invoice','in_refund','out_receipt','in_receipt')),
            ('state','notin',['draft','cancel'])
        ]
        returnaction
