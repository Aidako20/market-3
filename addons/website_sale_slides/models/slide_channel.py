#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classChannel(models.Model):
    _inherit='slide.channel'

    enroll=fields.Selection(selection_add=[
        ('payment','Onpayment')
    ],ondelete={'payment':lambdarecs:recs.write({'enroll':'invite'})})
    product_id=fields.Many2one('product.product','Product',index=True)
    product_sale_revenues=fields.Monetary(
        string='Totalrevenues',compute='_compute_product_sale_revenues',
        groups="sales_team.group_sale_salesman")
    currency_id=fields.Many2one(related='product_id.currency_id')

    _sql_constraints=[
        ('product_id_check',"CHECK(enroll!='payment'ORproduct_idISNOTNULL)","Productisrequiredforonpaymentchannels.")
    ]

    @api.depends('product_id')
    def_compute_product_sale_revenues(self):
        domain=[
            ('state','in',self.env['sale.report']._get_done_states()),
            ('product_id','in',self.product_id.ids),
        ]
        rg_data=dict(
            (item['product_id'][0],item['price_total'])
            foriteminself.env['sale.report'].read_group(domain,['product_id','price_total'],['product_id'])
        )
        forchannelinself:
            channel.product_sale_revenues=rg_data.get(channel.product_id.id,0)

    @api.model
    defcreate(self,vals):
        channel=super(Channel,self).create(vals)
        ifchannel.enroll=='payment':
            channel._synchronize_product_publish()
        returnchannel

    defwrite(self,vals):
        res=super(Channel,self).write(vals)
        if'is_published'invals:
            self.filtered(lambdachannel:channel.enroll=='payment')._synchronize_product_publish()
        returnres

    def_synchronize_product_publish(self):
        self.filtered(lambdachannel:channel.is_publishedandnotchannel.product_id.is_published).sudo().product_id.write({'is_published':True})
        self.filtered(lambdachannel:notchannel.is_publishedandchannel.product_id.is_published).sudo().product_id.write({'is_published':False})

    defaction_view_sales(self):
        action=self.env["ir.actions.actions"]._for_xml_id("website_sale_slides.sale_report_action_slides")
        action['domain']=[('product_id','in',self.product_id.ids)]
        returnaction

    def_filter_add_members(self,target_partners,**member_values):
        """Overriddentoadd'payment'channelstothefilteredchannels.People
        thatcanwriteonpayment-basedchannelscanaddmembers."""
        result=super(Channel,self)._filter_add_members(target_partners,**member_values)
        on_payment=self.filtered(lambdachannel:channel.enroll=='payment')
        ifon_payment:
            try:
                on_payment.check_access_rights('write')
                on_payment.check_access_rule('write')
            except:
                pass
            else:
                result|=on_payment
        returnresult
