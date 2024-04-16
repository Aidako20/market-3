#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,fields


classPartners(models.Model):
    """Updateofres.partnerclasstotakeintoaccountthelivechatusername."""
    _inherit='res.partner'

    user_livechat_username=fields.Char(compute='_compute_user_livechat_username')

    @api.depends('user_ids.livechat_username')
    def_compute_user_livechat_username(self):
        forpartnerinself:
            partner.user_livechat_username=next(iter(partner.user_ids.mapped('livechat_username')),False)
