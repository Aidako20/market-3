#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
importhmac

fromwerkzeugimporturls

fromflectraimportmodels
fromflectra.addons.http_routing.models.ir_httpimportslug


classMailGroup(models.Model):
    _inherit='mail.channel'

    def_notify_email_header_dict(self):
        headers=super(MailGroup,self)._notify_email_header_dict()
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        headers['List-Archive']='<%s/groups/%s>'%(base_url,slug(self))
        headers['List-Subscribe']='<%s/groups>'%(base_url)
        headers['List-Unsubscribe']='<%s/groups?unsubscribe>'%(base_url,)
        returnheaders

    def_send_confirmation_email(self,partner_ids,unsubscribe=False):
        website=self.env['website'].get_current_website()
        base_url=website.get_base_url()

        route="/groups/%(action)s/%(channel)s/%(partner)s/%(token)s"
        ifunsubscribe:
            template=self.env.ref('website_mail_channel.mail_template_list_unsubscribe')
            action='unsubscribe'
        else:
            template=self.env.ref('website_mail_channel.mail_template_list_subscribe')
            action='subscribe'

        forpartner_idinpartner_ids:
            #generateanewtokenpersubscriber
            token=self._generate_action_token(partner_id,action=action)

            token_url=urls.url_join(base_url,route%{
                'action':action,
                'channel':self.id,
                'partner':partner_id,
                'token':token,
            })
            template.with_context(token_url=token_url).send_mail(
                self.id,
                force_send=True,
                email_values={
                    'recipient_ids':[(4,partner_id)],
                    'email_from':website.company_id.email,
                }
            )

        returnTrue

    def_generate_action_token(self,partner_id,action='unsubscribe'):
        self.ensure_one()
        secret=self.env['ir.config_parameter'].sudo().get_param('database.secret')
        data='$'.join([
                str(self.id),
                str(partner_id),
                action])
        returnhmac.new(secret.encode('utf-8'),data.encode('utf-8'),hashlib.md5).hexdigest()
