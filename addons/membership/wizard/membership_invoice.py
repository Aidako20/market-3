#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models


classMembershipInvoice(models.TransientModel):
    _name="membership.invoice"
    _description="MembershipInvoice"

    product_id=fields.Many2one('product.product',string='Membership',required=True)
    member_price=fields.Float(string='MemberPrice',digits='ProductPrice',required=True)

    @api.onchange('product_id')
    defonchange_product(self):
        """Thisfunctionreturnsvalueof product'smemberpricebasedonproductid.
        """
        price_dict=self.product_id.price_compute('list_price')
        self.member_price=price_dict.get(self.product_id.id)orFalse

    defmembership_invoice(self):
        invoice_list=self.env['res.partner'].browse(self._context.get('active_ids')).create_membership_invoice(self.product_id,self.member_price)

        search_view_ref=self.env.ref('account.view_account_invoice_filter',False)
        form_view_ref=self.env.ref('account.view_move_form',False)
        tree_view_ref=self.env.ref('account.view_move_tree',False)

        return {
            'domain':[('id','in',invoice_list.ids)],
            'name':'MembershipInvoices',
            'res_model':'account.move',
            'type':'ir.actions.act_window',
            'views':[(tree_view_ref.id,'tree'),(form_view_ref.id,'form')],
            'search_view_id':search_view_refandsearch_view_ref.id,
        }
