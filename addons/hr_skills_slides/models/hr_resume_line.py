#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classResumeLine(models.Model):
    _inherit='hr.resume.line'

    display_type=fields.Selection(selection_add=[('course','Course')])
    channel_id=fields.Many2one('slide.channel',string="Course",readonly=True)
