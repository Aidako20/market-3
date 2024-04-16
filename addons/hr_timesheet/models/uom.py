#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classUom(models.Model):
    _inherit='uom.uom'

    timesheet_widget=fields.Char("Widget",help="Widgetusedinthewebclientwhenthisunitistheoneusedtoencodetimesheets.")
