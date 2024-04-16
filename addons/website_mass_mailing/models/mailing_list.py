#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models
fromflectra.tools.translateimport_


classMailingList(models.Model):
    _inherit='mailing.list'

    def_default_toast_content(self):
        return_('<p>Thanksforsubscribing!</p>')

    website_popup_ids=fields.One2many('website.mass_mailing.popup','mailing_list_id',string="WebsitePopups")
    toast_content=fields.Html(default=_default_toast_content,translate=True)
