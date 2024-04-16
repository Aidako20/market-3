#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportfields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    digest_emails=fields.Boolean(string="DigestEmails",config_parameter='digest.default_digest_emails')
    digest_id=fields.Many2one('digest.digest',string='DigestEmail',config_parameter='digest.default_digest_id')
