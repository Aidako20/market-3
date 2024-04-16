#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classCompany(models.Model):
    _inherit='res.company'

    hr_presence_control_email_amount=fields.Integer(string="#emailstosend")
    hr_presence_control_ip_list=fields.Char(string="ValidIPaddresses")
