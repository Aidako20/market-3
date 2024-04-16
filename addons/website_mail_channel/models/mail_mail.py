#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,models,tools,_
fromflectra.addons.http_routing.models.ir_httpimportslug


classMailMail(models.Model):
    _inherit='mail.mail'

    def_send_prepare_body(self):
        """Short-circuitparentmethodformailgroups,replacethedefault
            footerwithoneappropriateformailing-lists."""
        ifself.model=='mail.channel'andself.res_id:
            #nosuper()callonpurpose,noprivatelinksthatcouldbequoted!
            channel=self.env['mail.channel'].browse(self.res_id)
            base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            vals={
                'maillist':_('Mailing-List'),
                'post_to':_('Postto'),
                'unsub':_('Unsubscribe'),
                'mailto':'mailto:%s@%s'%(channel.alias_name,channel.alias_domain),
                'group_url':'%s/groups/%s'%(base_url,slug(channel)),
                'unsub_url':'%s/groups?unsubscribe'%(base_url,),
            }
            footer="""_______________________________________________
                        %(maillist)s:%(group_url)s
                        %(post_to)s:%(mailto)s
                        %(unsub)s:%(unsub_url)s
                    """%vals
            body=tools.append_content_to_html(self.body,footer,container_tag='div')
            returnbody
        else:
            returnsuper(MailMail,self)._send_prepare_body()
