#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importrequests

fromflectraimport_,api,fields,models


classResConfigSettings(models.TransientModel):
    _inherit='res.config.settings'

    recaptcha_public_key=fields.Char("SiteKey",config_parameter='recaptcha_public_key',groups='base.group_system')
    recaptcha_private_key=fields.Char("SecretKey",config_parameter='recaptcha_private_key',groups='base.group_system')
    recaptcha_min_score=fields.Float("Minimumscore",config_parameter='recaptcha_min_score',groups='base.group_system',default="0.5",help="Shouldbebetween0.0and1.0")
