#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models
fromflectra.addons.base.models.res_partnerimportWARNING_MESSAGE,WARNING_HELP


classResPartner(models.Model):
    _inherit='res.partner'

    sale_order_count=fields.Integer(compute='_compute_sale_order_count',string='SaleOrderCount')
    sale_order_ids=fields.One2many('sale.order','partner_id','SalesOrder')
    sale_warn=fields.Selection(WARNING_MESSAGE,'SalesWarnings',default='no-message',help=WARNING_HELP)
    sale_warn_msg=fields.Text('MessageforSalesOrder')

    def_compute_sale_order_count(self):
        #retrieveallchildrenpartnersandprefetch'parent_id'onthem
        all_partners=self.with_context(active_test=False).search([('id','child_of',self.ids)])
        all_partners.read(['parent_id'])

        sale_order_groups=self.env['sale.order'].read_group(
            domain=[('partner_id','in',all_partners.ids)],
            fields=['partner_id'],groupby=['partner_id']
        )
        partners=self.browse()
        forgroupinsale_order_groups:
            partner=self.browse(group['partner_id'][0])
            whilepartner:
                ifpartnerinself:
                    partner.sale_order_count+=group['partner_id_count']
                    partners|=partner
                partner=partner.parent_id
        (self-partners).sale_order_count=0

    defcan_edit_vat(self):
        '''Can'tedit`vat`ifthereis(nondraft)issuedSO.'''
        can_edit_vat=super(ResPartner,self).can_edit_vat()
        ifnotcan_edit_vat:
            returncan_edit_vat
        SaleOrder=self.env['sale.order']
        has_so=SaleOrder.search([
            ('partner_id','child_of',self.commercial_partner_id.id),
            ('state','in',['sent','sale','done'])
        ],limit=1)
        returncan_edit_vatandnotbool(has_so)

    defaction_view_sale_order(self):
        action=self.env['ir.actions.act_window']._for_xml_id('sale.act_res_partner_2_sale_order')
        all_child=self.with_context(active_test=False).search([('id','child_of',self.ids)])
        action["domain"]=[("partner_id","in",all_child.ids)]
        returnaction
