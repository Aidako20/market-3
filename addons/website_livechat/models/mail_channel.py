#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportAccessError


classMailChannel(models.Model):
    _inherit='mail.channel'

    livechat_visitor_id=fields.Many2one('website.visitor',string='Visitor')

    def_execute_channel_pin(self,pinned=False):
        """Overridetocleananemptylivechatchannel.
         Thisistypicallycalledwhentheoperatorsendachatrequesttoawebsite.visitor
         butdon'tspeaktohimandclosesthechatter.
         Thisallowsoperatorstosendthevisitoranewchatrequest.
         Ifactiveemptylivechatchannel,
         deletemail_channelasnotusefultokeepemptychat
         """
        super(MailChannel,self)._execute_channel_pin(pinned)
        ifself.livechat_activeandnotself.channel_message_ids:
            self.unlink()

    defchannel_info(self,extra_info=False):
        """
        Overridetoaddvisitorinformationonthemailchannelinfos.
        Thiswillbeusedtodisplayabannerwithvisitorinformations
        atthetopofthelivechatchanneldiscussionviewindiscussmodule.
        """
        channel_infos=super(MailChannel,self).channel_info(extra_info)
        channel_infos_dict=dict((c['id'],c)forcinchannel_infos)
        forchannelinself.filtered('livechat_visitor_id'):
            visitor=channel.livechat_visitor_id
            try:
                channel_infos_dict[channel.id]['visitor']={
                    'name':visitor.display_name,
                    'country_code':visitor.country_id.code.lower()ifvisitor.country_idelseFalse,
                    'country_id':visitor.country_id.id,
                    'is_connected':visitor.is_connected,
                    'history':self.sudo()._get_visitor_history(visitor),
                    'website':visitor.website_id.name,
                    'lang':visitor.lang_id.name,
                    'partner_id':visitor.partner_id.id,
                }
            exceptAccessError:
                pass
        returnlist(channel_infos_dict.values())

    def_get_visitor_history(self,visitor):
        """
        Preparehistorystringtorenderitinthevisitorinfodivondiscusslivechatchannelview.
        :paramvisitor:website.visitorofthechannel
        :return:arrowseparatedstringcontainingnavigationhistoryinformation
        """
        recent_history=self.env['website.track'].search([('page_id','!=',False),('visitor_id','=',visitor.id)],limit=3)
        return'→'.join(visit.page_id.name+'('+visit.visit_datetime.strftime('%H:%M')+')'forvisitinreversed(recent_history))

    def_get_visitor_leave_message(self,operator=False,cancel=False):
        name=_('Thevisitor')ifnotself.livechat_visitor_idelseself.livechat_visitor_id.display_name
        ifcancel:
            message=_("""%shasstartedaconversationwith%s.
                        Thechatrequesthasbeencanceled.""")%(name,operatoror_('anoperator'))
        else:
            message=_('%shaslefttheconversation.',name)

        returnmessage

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,**kwargs):
        """Overridetomarkthevisitorasstillconnected.
        Ifthemessagesentisnotfromtheoperator(soifit'sthevisitoror
        flectrabotsendingclosingchatnotification,thevisitorlastactiondateisupdated."""
        message=super(MailChannel,self).message_post(**kwargs)
        message_author_id=message.author_id
        visitor=self.livechat_visitor_id
        iflen(self)==1andvisitorandmessage_author_id!=self.livechat_operator_id:
            visitor._update_visitor_last_visit()
        returnmessage
