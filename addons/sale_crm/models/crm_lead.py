#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdateutil.relativedeltaimportrelativedelta

fromflectraimportapi,fields,models


classCrmLead(models.Model):
    _inherit='crm.lead'

    sale_amount_total=fields.Monetary(compute='_compute_sale_data',string="SumofOrders",help="UntaxedTotalofConfirmedOrders",currency_field='company_currency')
    quotation_count=fields.Integer(compute='_compute_sale_data',string="NumberofQuotations")
    sale_order_count=fields.Integer(compute='_compute_sale_data',string="NumberofSaleOrders")
    order_ids=fields.One2many('sale.order','opportunity_id',string='Orders')

    @api.depends('order_ids.state','order_ids.currency_id','order_ids.amount_untaxed','order_ids.date_order','order_ids.company_id')
    def_compute_sale_data(self):
        forleadinself:
            total=0.0
            quotation_cnt=0
            sale_order_cnt=0
            company_currency=lead.company_currencyorself.env.company.currency_id
            fororderinlead.order_ids:
                iforder.statein('draft','sent'):
                    quotation_cnt+=1
                iforder.statenotin('draft','sent','cancel'):
                    sale_order_cnt+=1
                    total+=order.currency_id._convert(
                        order.amount_untaxed,company_currency,order.company_id,order.date_orderorfields.Date.today())
            lead.sale_amount_total=total
            lead.quotation_count=quotation_cnt
            lead.sale_order_count=sale_order_cnt

    defaction_sale_quotations_new(self):
        ifnotself.partner_id:
            returnself.env["ir.actions.actions"]._for_xml_id("sale_crm.crm_quotation_partner_action")
        else:
            returnself.action_new_quotation()

    defaction_new_quotation(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale_crm.sale_action_quotations_new")
        action['context']={
            'search_default_opportunity_id':self.id,
            'default_opportunity_id':self.id,
            'search_default_partner_id':self.partner_id.id,
            'default_partner_id':self.partner_id.id,
            'default_campaign_id':self.campaign_id.id,
            'default_medium_id':self.medium_id.id,
            'default_origin':self.name,
            'default_source_id':self.source_id.id,
            'default_company_id':self.company_id.idorself.env.company.id,
            'default_tag_ids':[(6,0,self.tag_ids.ids)]
        }
        ifself.team_id:
            action['context']['default_team_id']=self.team_id.id,
        ifself.user_id:
            action['context']['default_user_id']=self.user_id.id
        returnaction

    defaction_view_sale_quotation(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_quotations_with_onboarding")
        action['context']={
            'search_default_draft':1,
            'search_default_partner_id':self.partner_id.id,
            'default_partner_id':self.partner_id.id,
            'default_opportunity_id':self.id
        }
        action['domain']=[('opportunity_id','=',self.id),('state','in',['draft','sent'])]
        quotations=self.mapped('order_ids').filtered(lambdal:l.statein('draft','sent'))
        iflen(quotations)==1:
            action['views']=[(self.env.ref('sale.view_order_form').id,'form')]
            action['res_id']=quotations.id
        returnaction

    defaction_view_sale_order(self):
        action=self.env["ir.actions.actions"]._for_xml_id("sale.action_orders")
        action['context']={
            'search_default_partner_id':self.partner_id.id,
            'default_partner_id':self.partner_id.id,
            'default_opportunity_id':self.id,
        }
        action['domain']=[('opportunity_id','=',self.id),('state','notin',('draft','sent','cancel'))]
        orders=self.mapped('order_ids').filtered(lambdal:l.statenotin('draft','sent','cancel'))
        iflen(orders)==1:
            action['views']=[(self.env.ref('sale.view_order_form').id,'form')]
            action['res_id']=orders.id
        returnaction
