#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSaleOrder(models.Model):
    _inherit='sale.order'

    opportunity_id=fields.Many2one(
        'crm.lead',string='Opportunity',check_company=True,
        domain="[('type','=','opportunity'),'|',('company_id','=',False),('company_id','=',company_id)]")

    defaction_confirm(self):
        returnsuper(SaleOrder,self.with_context({k:vfork,vinself._context.items()ifk!='default_tag_ids'})).action_confirm()
