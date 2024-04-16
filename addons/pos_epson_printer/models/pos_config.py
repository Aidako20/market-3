#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models

classPosConfig(models.Model):
    _inherit='pos.config'

    epson_printer_ip=fields.Char(string='EpsonPrinterIP',help="LocalIPaddressofanEpsonreceiptprinter.")

    @api.onchange('epson_printer_ip')
    def_onchange_epson_printer_ip(self):
        ifself.epson_printer_ipin(False,''):
            self.iface_cashdrawer=False
