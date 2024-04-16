#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classcompany(models.Model):
    _inherit='res.company'

    security_lead=fields.Float(
        'SalesSafetyDays',default=0.0,required=True,
        help="Marginoferrorfordatespromisedtocustomers."
             "Productswillbescheduledforprocurementanddelivery"
             "thatmanydaysearlierthantheactualpromiseddate,to"
             "copewithunexpecteddelaysinthesupplychain.")
