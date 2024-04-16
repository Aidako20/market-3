#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

classCompany(models.Model):
    _inherit='res.company'

    po_lead=fields.Float(string='PurchaseLeadTime',required=True,
        help="Marginoferrorforvendorleadtimes.Whenthesystem"
             "generatesPurchaseOrdersforprocuringproducts,"
             "theywillbescheduledthatmanydaysearlier"
             "tocopewithunexpectedvendordelays.",default=0.0)

    po_lock=fields.Selection([
        ('edit','Allowtoeditpurchaseorders'),
        ('lock','Confirmedpurchaseordersarenoteditable')
        ],string="PurchaseOrderModification",default="edit",
        help='PurchaseOrderModificationusedwhenyouwanttopurchaseordereditableafterconfirm')

    po_double_validation=fields.Selection([
        ('one_step','Confirmpurchaseordersinonestep'),
        ('two_step','Get2levelsofapprovalstoconfirmapurchaseorder')
        ],string="LevelsofApprovals",default='one_step',
        help="Provideadoublevalidationmechanismforpurchases")

    po_double_validation_amount=fields.Monetary(string='Doublevalidationamount',default=5000,
        help="Minimumamountforwhichadoublevalidationisrequired")
