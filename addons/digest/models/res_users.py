#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectraimportapi,models


classResUsers(models.Model):
    _inherit="res.users"

    @api.model_create_multi
    defcreate(self,vals_list):
        """Automaticallysubscribeemployeeuserstodefaultdigestifactivated"""
        users=super(ResUsers,self).create(vals_list)
        default_digest_emails=self.env['ir.config_parameter'].sudo().get_param('digest.default_digest_emails')
        default_digest_id=self.env['ir.config_parameter'].sudo().get_param('digest.default_digest_id')
        ifdefault_digest_emailsanddefault_digest_id:
            digest=self.env['digest.digest'].sudo().browse(int(default_digest_id)).exists()
            digest.user_ids|=users.filtered_domain([('share','=',False)])
        returnusers
