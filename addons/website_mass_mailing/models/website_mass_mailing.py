#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportfields,models


classMassMailingPopup(models.Model):
    _name='website.mass_mailing.popup'
    _description="Mailinglistpopup"

    def_default_popup_content(self):
        returnself.env['ir.ui.view']._render_template('website_mass_mailing.s_newsletter_subscribe_popup_content')

    mailing_list_id=fields.Many2one('mailing.list')
    website_id=fields.Many2one('website')
    popup_content=fields.Html(string="WebsitePopupContent",default=_default_popup_content,translate=True,sanitize=False)
