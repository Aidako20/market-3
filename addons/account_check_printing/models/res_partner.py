#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectraimportmodels,fields


classResPartner(models.Model):
    _inherit='res.partner'

    property_payment_method_id=fields.Many2one(
        comodel_name='account.payment.method',
        string='PaymentMethod',
        company_dependent=True,
        domain="[('payment_type','=','outbound')]",
        help="Preferredpaymentmethodwhenpayingthisvendor.Thisisusedtofiltervendorbills"
             "bypreferredpaymentmethodtoregisterpaymentsinmass.Usecases:createbank"
             "filesforbatchwires,checkruns.",
    )
