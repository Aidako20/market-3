#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classIrConfigParameter(models.Model):
    _inherit='ir.config_parameter'

    definit(self,force=False):
        super(IrConfigParameter,self).init(force=force)
        ifforce:
            oauth_oe=self.env.ref('auth_oauth.provider_openerp')
            ifnotoauth_oe:
                return
            dbuuid=self.sudo().get_param('database.uuid')
            oauth_oe.write({'client_id':dbuuid})
