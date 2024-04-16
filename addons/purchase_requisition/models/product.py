#-*-encoding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classSupplierInfo(models.Model):
    _inherit='product.supplierinfo'

    purchase_requisition_id=fields.Many2one('purchase.requisition',related='purchase_requisition_line_id.requisition_id',string='Agreement',readonly=False)
    purchase_requisition_line_id=fields.Many2one('purchase.requisition.line')


classProductProduct(models.Model):
    _inherit='product.product'

    def_prepare_sellers(self,params=False):
        sellers=super(ProductProduct,self)._prepare_sellers(params=params)
        ifparamsandparams.get('order_id'):
            returnsellers.filtered(lambdas:nots.purchase_requisition_idors.purchase_requisition_id==params['order_id'].requisition_id)
        else:
            returnsellers


classProductTemplate(models.Model):
    _inherit='product.template'

    purchase_requisition=fields.Selection(
        [('rfq','Createadraftpurchaseorder'),
         ('tenders','Proposeacallfortenders')],
        string='Procurement',default='rfq',
        help="Createadraftpurchaseorder:Basedonyourproductconfiguration,thesystemwillcreateadraft"
             "purchaseorder.Proposeacallfortender:Ifthe'purchase_requisition'moduleisinstalledandthisoption"
             "isselected,thesystemwillcreateadraftcallfortender.")
