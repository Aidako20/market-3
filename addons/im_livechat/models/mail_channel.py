#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,_
fromflectra.toolsimporthtml_escape

classChannelPartner(models.Model):
    _inherit='mail.channel.partner'

    @api.autovacuum
    def_gc_unpin_livechat_sessions(self):
        """Unpinlivechatsessionswithnoactivityforatleastonedayto
            cleantheoperator'sinterface"""
        self.env.cr.execute("""
            UPDATEmail_channel_partner
            SETis_pinned=false
            WHEREidin(
                SELECTcp.idFROMmail_channel_partnercp
                INNERJOINmail_channelconc.id=cp.channel_id
                WHEREc.channel_type='livechat'ANDcp.is_pinnedistrueAND
                    cp.write_date<current_timestamp-interval'1day'
            )
        """)


classMailChannel(models.Model):
    """ChatSession
        Reprensentingaconversationbetweenusers.
        Itextendsthebasemethodforanonymoususage.
    """

    _name='mail.channel'
    _inherit=['mail.channel','rating.mixin']

    anonymous_name=fields.Char('AnonymousName')
    channel_type=fields.Selection(selection_add=[('livechat','LivechatConversation')])
    livechat_active=fields.Boolean('Islivechatongoing?',help='Livechatsessionisactiveuntilvisitorleavetheconversation.')
    livechat_channel_id=fields.Many2one('im_livechat.channel','Channel')
    livechat_operator_id=fields.Many2one('res.partner',string='Operator',help="""Operatorforthisspecificchannel""")
    country_id=fields.Many2one('res.country',string="Country",help="Countryofthevisitorofthechannel")

    _sql_constraints=[('livechat_operator_id',"CHECK((channel_type='livechat'andlivechat_operator_idisnotnull)or(channel_type!='livechat'))",
                         'LivechatOperatorIDisrequiredforachanneloftypelivechat.')]

    def_compute_is_chat(self):
        super(MailChannel,self)._compute_is_chat()
        forrecordinself:
            ifrecord.channel_type=='livechat':
                record.is_chat=True

    def_channel_message_notifications(self,message,message_format=False):
        """Whenaanonymoususercreateamail.channel,theoperatorisnotnotify(toavoidmassivepollingwhen
            clickingonlivechatbutton).SowhentheanonymouspersonissendingitsFIRSTmessage,thechannelheader
            shouldbeaddedtothenotification,sincetheusercannotbelistiningtothechannel.
        """
        notifications=super()._channel_message_notifications(message=message,message_format=message_format)
        forchannelinself:
            #adduuidforprivatelivechatchannelstoallowanonymoustolisten
            ifchannel.channel_type=='livechat'andchannel.public=='private':
                notifications.append([channel.uuid,notifications[0][1]])
        ifnotmessage.author_id:
            unpinned_channel_partner=self.mapped('channel_last_seen_partner_ids').filtered(lambdacp:notcp.is_pinned)
            ifunpinned_channel_partner:
                unpinned_channel_partner.write({'is_pinned':True})
                notifications=self._channel_channel_notifications(unpinned_channel_partner.mapped('partner_id').ids)+notifications
        returnnotifications

    defchannel_info(self,extra_info=False):
        """Extendsthechannelheaderbyaddingthelivechatoperatorandthe'anonymous'profile
            :rtype:list(dict)
        """
        channel_infos=super(MailChannel,self).channel_info(extra_info)
        channel_infos_dict=dict((c['id'],c)forcinchannel_infos)
        forchannelinself:
            #addthelastmessagedate
            ifchannel.channel_type=='livechat':
                #addtheoperatorid
                ifchannel.livechat_operator_id:
                    display_name=channel.livechat_operator_id.user_livechat_usernameorchannel.livechat_operator_id.display_name
                    channel_infos_dict[channel.id]['operator_pid']=(channel.livechat_operator_id.id,display_name.replace(',',''))
                #addtheanonymousorpartnername
                channel_infos_dict[channel.id]['livechat_visitor']=channel._channel_get_livechat_visitor_info()
        returnlist(channel_infos_dict.values())

    def_channel_info_format_member(self,partner,partner_info):
        """Overridetoremovesensitiveinformationinlivechat."""
        ifself.channel_type=='livechat':
            return{
                'id':partner.id,
                'name':partner.user_livechat_usernameorpartner.name, #forAPIcompatibilityinstable
                'email':False, #forAPIcompatibilityinstable
                'im_status':False, #forAPIcompatibilityinstable
                'livechat_username':partner.user_livechat_username,
            }
        returnsuper()._channel_info_format_member(partner=partner,partner_info=partner_info)

    def_notify_typing_partner_data(self):
        """Overridetoremovenameandreturnlivechatusernameifapplicable."""
        data=super()._notify_typing_partner_data()
        ifself.channel_type=='livechat'andself.env.user.partner_id.user_livechat_username:
            data['partner_name']=self.env.user.partner_id.user_livechat_username #forAPIcompatibilityinstable
            data['livechat_username']=self.env.user.partner_id.user_livechat_username
        returndata

    @api.model
    defchannel_fetch_slot(self):
        values=super(MailChannel,self).channel_fetch_slot()
        pinned_channels=self.env['mail.channel.partner'].search([('partner_id','=',self.env.user.partner_id.id),('is_pinned','=',True)]).mapped('channel_id')
        values['channel_livechat']=self.search([('channel_type','=','livechat'),('id','in',pinned_channels.ids)]).channel_info()
        returnvalues

    def_channel_get_livechat_visitor_info(self):
        self.ensure_one()
        #removeactivetesttoensurepublicpartneristakenintoaccount
        channel_partner_ids=self.with_context(active_test=False).channel_partner_ids
        partners=channel_partner_ids-self.livechat_operator_id
        ifnotpartners:
            #operatorprobablytestingthelivechatwithhisownuser
            partners=channel_partner_ids
        first_partner=partnersandpartners[0]
        iffirst_partnerand(notfirst_partner.user_idsornotany(user._is_public()foruserinfirst_partner.user_ids)):
            #legitnon-publicpartner
            return{
                'country':first_partner.country_id.name_get()[0]iffirst_partner.country_idelseFalse,
                'id':first_partner.id,
                'name':first_partner.name,
            }
        return{
            'country':self.country_id.name_get()[0]ifself.country_idelseFalse,
            'id':False,
            'name':self.anonymous_nameor_("Visitor"),
        }

    def_channel_get_livechat_partner_name(self):
        ifself.livechat_operator_idinself.channel_partner_ids:
            partners=self.channel_partner_ids-self.livechat_operator_id
            ifpartners:
                partner_name=False
                forpartnerinpartners:
                    ifnotpartner_name:
                        partner_name=partner.name
                    else:
                        partner_name+=',%s'%partner.name
                    ifpartner.country_id:
                        partner_name+='(%s)'%partner.country_id.name
                returnpartner_name
        ifself.anonymous_name:
            returnself.anonymous_name
        return_("Visitor")

    @api.autovacuum
    def_gc_empty_livechat_sessions(self):
        hours=1 #neverremoveemptysessioncreatedwithinthelasthour
        self.env.cr.execute("""
            SELECTidasid
            FROMmail_channelC
            WHERENOTEXISTS(
                SELECT*
                FROMmail_message_mail_channel_relR
                WHERER.mail_channel_id=C.id
            )ANDC.channel_type='livechat'ANDlivechat_channel_idISNOTNULLAND
                COALESCE(write_date,create_date,(now()attimezone'UTC'))::timestamp
                <((now()attimezone'UTC')-interval%s)""",("%shours"%hours,))
        empty_channel_ids=[item['id']foriteminself.env.cr.dictfetchall()]
        self.browse(empty_channel_ids).unlink()

    def_define_command_history(self):
        return{
            'channel_types':['livechat'],
            'help':_('See15lastvisitedpages')
        }

    def_execute_command_history(self,**kwargs):
        notification=[]
        notification_values={
            '_type':'history_command',
        }
        notification.append([self.uuid,dict(notification_values)])
        returnself.env['bus.bus'].sendmany(notification)

    def_send_history_message(self,pid,page_history):
        message_body=_('Nohistoryfound')
        ifpage_history:
            html_links=['<li><ahref="%s"target="_blank">%s</a></li>'%(html_escape(page),html_escape(page))forpageinpage_history]
            message_body='<spanclass="o_mail_notification"><ul>%s</ul></span>'%(''.join(html_links))
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',pid),{
            'body':message_body,
            'channel_ids':self.ids,
            'info':'transient_message',
        })

    def_get_visitor_leave_message(self,operator=False,cancel=False):
        return_('Visitorhaslefttheconversation.')

    def_close_livechat_session(self,**kwargs):
        """Setdeactivatethelivechatchannelandnotify(theoperator)thereasonofclosingthesession."""
        self.ensure_one()
        ifself.livechat_active:
            self.livechat_active=False
            #avoiduselessnotificationifthechannelisempty
            ifnotself.channel_message_ids:
                return
            #Notifythatthevisitorhaslefttheconversation
            self.message_post(author_id=self.env.ref('base.partner_root').id,
                              body=self._get_visitor_leave_message(**kwargs),message_type='comment',subtype_xmlid='mail.mt_comment')

    #RatingMixin

    def_rating_get_parent_field_name(self):
        return'livechat_channel_id'

    def_email_livechat_transcript(self,email):
        company=self.env.user.company_id
        render_context={
            "company":company,
            "channel":self,
        }
        template=self.env.ref('im_livechat.livechat_email_template')
        mail_body=template._render(render_context,engine='ir.qweb',minimal_qcontext=True)
        mail_body=self.env['mail.render.mixin']._replace_local_links(mail_body)
        mail=self.env['mail.mail'].sudo().create({
            'subject':_('Conversationwith%s',self.livechat_operator_id.user_livechat_usernameorself.livechat_operator_id.name),
            'email_from':company.catchall_formattedorcompany.email_formatted,
            'author_id':self.env.user.partner_id.id,
            'email_to':email,
            'body_html':mail_body,
        })
        mail.send()
