#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models

classRestaurantPrinter(models.Model):

    _inherit='restaurant.printer'

    printer_type=fields.Selection(selection_add=[('epson_epos','UseanEpsonprinter')])
    epson_printer_ip=fields.Char(string='EpsonReceiptPrinterIPAddress',help="LocalIPaddressofanEpsonreceiptprinter.")
