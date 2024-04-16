#coding:utf-8
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels


classPosConfig(models.Model):
    _inherit='pos.config'

    def_force_http(self):
        enforce_https=self.env['ir.config_parameter'].sudo().get_param('point_of_sale.enforce_https')
        ifnotenforce_httpsandself.payment_method_ids.filtered(lambdapm:pm.use_payment_terminal=='six'):
            returnTrue
        returnsuper(PosConfig,self)._force_http()
