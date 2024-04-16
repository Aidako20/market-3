#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportmodels,_
fromflectra.toolsimporthtml2plaintext,html_escape


classMailChannel(models.Model):
    _inherit='mail.channel'

    def_define_command_lead(self):
        return{'help':_('Createanewlead(/leadleadtitle)')}

    def_execute_command_lead(self,**kwargs):
        partner=self.env.user.partner_id
        key=kwargs['body']
        channel_partners=self.env['mail.channel.partner'].search([
            ('partner_id','!=',partner.id),
            ('channel_id','=',self.id)],limit=1
        )
        ifkey.strip()=='/lead':
            msg=self._define_command_lead()['help']
        else:
            lead=self._convert_visitor_to_lead(partner,channel_partners,key)
            msg=_('Createdanewlead:<ahref="#"data-oe-id="%s"data-oe-model="crm.lead">%s</a>')%(lead.id,html_escape(lead.name))
        self._send_transient_message(partner,msg)

    def_convert_visitor_to_lead(self,partner,channel_partners,key):
        """Createaleadfromchannel/leadcommand
        :parampartner:internaluserpartner(operator)thatcreatedthelead;
        :paramchannel_partners:channelmembers;
        :paramkey:operatorinputinchat('/leadLeadaboutProduct')
        """
        description=''.join(
            '%s:%s\n'%(message.author_id.nameorself.anonymous_name,message.body)
            formessageinself.channel_message_ids.sorted('id')
        )
        #ifpublicuserispartofthechat:considerleadtobelinkedtoan
        #anonymoususerwhatevertheparticipants.Otherwisekeeponlyshare
        #partners(nouserorportaluser)tolinktothelead.
        customers=self.env['res.partner']
        forcustomerinchannel_partners.partner_id.filtered('partner_share').with_context(active_test=False):
            ifcustomer.user_idsandall(user._is_public()foruserincustomer.user_ids):
                customers=self.env['res.partner']
                break
            else:
                customers|=customer

        utm_source=self.env.ref('crm_livechat.utm_source_livechat',raise_if_not_found=False)
        returnself.env['crm.lead'].create({
            'name':html2plaintext(key[5:]),
            'partner_id':customers[0].idifcustomerselseFalse,
            'user_id':False,
            'team_id':False,
            'description':html2plaintext(description),
            'referred':partner.name,
            'source_id':utm_sourceandutm_source.id,
        })
