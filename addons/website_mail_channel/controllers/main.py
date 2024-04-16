#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

fromdatetimeimportdatetime
fromdateutilimportrelativedelta

fromflectraimporthttp,fields,tools,_
fromflectra.httpimportrequest
fromflectra.addons.http_routing.models.ir_httpimportslug


classMailGroup(http.Controller):
    _thread_per_page=20
    _replies_per_page=10

    def_get_archives(self,group_id):
        MailMessage=request.env['mail.message']
        #usesudotoavoidside-effectsduetocustomACLs
        groups=MailMessage.sudo()._read_group_raw(
            [('model','=','mail.channel'),('res_id','=',group_id),('message_type','!=','notification')],
            ['subject','date'],
            groupby=["date"],orderby="datedesc")
        forgroupingroups:
            (r,label)=group['date']
            start,end=r.split('/')
            group['date']=label
            group['date_begin']=self._to_date(start)
            group['date_end']=self._to_date(end)
        returngroups

    def_to_date(self,dt):
        """dateis(ofcourse)adatetimesostartandendaredatetime
        strings,butwejustwantdatestrings
        """
        return(datetime
            .strptime(dt,tools.DEFAULT_SERVER_DATETIME_FORMAT)
            .date()#maybeunnecessary?
            .strftime(tools.DEFAULT_SERVER_DATE_FORMAT))

    @http.route("/groups",type='http',auth="public",website=True,sitemap=True)
    defview(self,**post):
        groups=request.env['mail.channel'].search([('alias_id.alias_name','!=',False)])

        #computestatistics
        month_date=datetime.today()-relativedelta.relativedelta(months=1)
        #usesudotoavoidside-effectsduetocustomACLs
        messages=request.env['mail.message'].sudo().read_group([
            ('model','=','mail.channel'),
            ('date','>=',fields.Datetime.to_string(month_date)),
            ('message_type','!=','notification'),
            ('res_id','in',groups.ids),
        ],['res_id'],['res_id'])
        message_data=dict((message['res_id'],message['res_id_count'])formessageinmessages)

        group_data=dict(
            (group.id,{'monthly_message_nbr':message_data.get(group.id,0),
                        'members_count':len(group.channel_partner_ids)})
            forgroupingroups.sudo())
        returnrequest.render('website_mail_channel.mail_channels',{'groups':groups,'group_data':group_data})

    @http.route(["/groups/is_member"],type='json',auth="public",website=True)
    defis_member(self,channel_id=0,**kw):
        """Determineifthecurrentuserismemberofthegivenchannel_id
            :paramchannel_id:thechannel_idtocheck
        """
        current_user=request.env.user
        session_partner_id=request.session.get('partner_id')
        public_user=request.website.user_id
        partner=None
        #findthecurrentpartner
        ifcurrent_user!=public_user:
            partner=current_user.partner_id
        elifsession_partner_id:
            partner=request.env['res.partner'].sudo().browse(session_partner_id)

        values={
            'is_user':current_user!=public_user,
            'email':partner.emailifpartnerelse"",
            'is_member':False,
            'alias_name':False,
        }
        #checkifthecurrentpartnerismemberornot
        channel=request.env['mail.channel'].browse(int(channel_id))
        ifchannel.exists()andpartnerisnotNone:
            values['is_member']=bool(partnerinchannel.sudo().channel_partner_ids)
        returnvalues

    @http.route(["/groups/subscription"],type='json',auth="public",website=True)
    defsubscription(self,channel_id=0,subscription="on",email='',**kw):
        """Subscribetoamailinglist:thiswillcreateapartnerwithitsemailaddress(ifpublicusernot
            registeredyet)andadditaschannelmember
            :paramchannel_id:thechannelidtojoin/quit
            :paramsubscription:'on'tounsubscribetheuser,'off'tosubscribe
        """
        unsubscribe=subscription=='on'
        channel=request.env['mail.channel'].browse(int(channel_id))
        ifnotchannel.exists():
            returnFalse

        partner_ids=[]

        #searchpartner_id
        ifrequest.env.user!=request.website.user_id:
            #connectedusersaredirectly(un)subscribed
            partner_ids=request.env.user.partner_id.ids

            #addorremovechannelmembers
            ifunsubscribe:
                channel.check_access_rule('read')
                channel.sudo().write({'channel_partner_ids':[(3,partner_id)forpartner_idinpartner_ids]})
                return"off"
            else: #addpartnertothechannel
                request.session['partner_id']=partner_ids[0]
                channel.check_access_rule('read')
                channel.sudo().write({'channel_partner_ids':[(4,partner_id)forpartner_idinpartner_ids]})
            return"on"

        else:
            #publicuserswillrecieveconfirmationemail
            partner_ids=[p.idforpinrequest.env['mail.thread'].sudo()._mail_find_partner_from_emails([email],records=channel.sudo())ifp]
            ifnotpartner_idsornotpartner_ids[0]:
                name=email.split('@')[0]
                partner_ids=[request.env['res.partner'].sudo().create({'name':name,'email':email}).id]

            channel.sudo()._send_confirmation_email(partner_ids,unsubscribe)
            return"email"

    @http.route([
        '''/groups/<model('mail.channel',"[('channel_type','=','channel')]"):group>''',
        '''/groups/<model('mail.channel'):group>/page/<int:page>'''
    ],type='http',auth="public",website=True,sitemap=True)
    defthread_headers(self,group,page=1,mode='thread',date_begin=None,date_end=None,**post):
        ifgroup.channel_type!='channel':
            raisewerkzeug.exceptions.NotFound()

        Message=request.env['mail.message']

        domain=[('model','=','mail.channel'),('res_id','=',group.id),('message_type','!=','notification')]
        ifmode=='thread':
            domain+=[('parent_id','=',False)]
        ifdate_beginanddate_end:
            domain+=[('date','>=',date_begin),('date','<=',date_end)]

        pager=request.website.pager(
            url='/groups/%s'%slug(group),
            total=Message.search_count(domain),
            page=page,
            step=self._thread_per_page,
            url_args={'mode':mode,'date_begin':date_beginor'','date_end':date_endor''},
        )
        messages=Message.search(domain,limit=self._thread_per_page,offset=pager['offset'])
        values={
            'messages':messages,
            'group':group,
            'pager':pager,
            'mode':mode,
            'archives':self._get_archives(group.id),
            'date_begin':date_begin,
            'date_end':date_end,
            'replies_per_page':self._replies_per_page,
        }
        returnrequest.render('website_mail_channel.group_messages',values)

    @http.route([
        '''/groups/<model('mail.channel',"[('channel_type','=','channel')]"):group>/<model('mail.message',"[('model','=','mail.channel'),('res_id','=',group.id)]"):message>''',
    ],type='http',auth="public",website=True,sitemap=True)
    defthread_discussion(self,group,message,mode='thread',date_begin=None,date_end=None,**post):
        ifgroup.channel_type!='channel':
            raisewerkzeug.exceptions.NotFound()

        Message=request.env['mail.message']
        ifmode=='thread':
            base_domain=[('model','=','mail.channel'),('res_id','=',group.id),('parent_id','=',message.parent_idandmessage.parent_id.idorFalse)]
        else:
            base_domain=[('model','=','mail.channel'),('res_id','=',group.id)]
        next_message=Message.search(base_domain+[('date','<',message.date)],order="dateDESC",limit=1)orNone
        prev_message=Message.search(base_domain+[('date','>',message.date)],order="date",limit=1)orNone
        values={
            'message':message,
            'group':group,
            'mode':mode,
            'archives':self._get_archives(group.id),
            'date_begin':date_begin,
            'date_end':date_end,
            'replies_per_page':self._replies_per_page,
            'next_message':next_message,
            'prev_message':prev_message,
        }
        returnrequest.render('website_mail_channel.group_message',values)

    @http.route(
        '''/groups/<model('mail.channel',"[('channel_type','=','channel')]"):group>/<model('mail.message',"[('model','=','mail.channel'),('res_id','=',group.id)]"):message>/get_replies''',
        type='json',auth="public",methods=['POST'],website=True)
    defrender_messages(self,group,message,**post):
        ifgroup.channel_type!='channel':
            returnFalse

        last_displayed_id=post.get('last_displayed_id')
        ifnotlast_displayed_id:
            returnFalse

        replies_domain=[('id','<',int(last_displayed_id)),('parent_id','=',message.id)]
        messages=request.env['mail.message'].search(replies_domain,limit=self._replies_per_page)
        message_count=request.env['mail.message'].search_count(replies_domain)
        values={
            'group':group,
            'thread_header':message,
            'messages':messages,
            'msg_more_count':message_count-self._replies_per_page,
            'replies_per_page':self._replies_per_page,
        }
        returnrequest.env.ref('website_mail_channel.messages_short')._render(values,engine='ir.qweb')

    @http.route("/groups/<int:group_id>/get_alias_info",type='json',auth='public',website=True)
    defget_alias_info(self,group_id,**post):
        group=request.env['mail.channel'].search([('id','=',group_id)])
        ifnotgroup: #doesn'texistordoesn'thavetherighttoaccessit
            return{}

        return{
            'alias_name':group.alias_idandgroup.alias_id.alias_nameandgroup.alias_id.alias_domainand'%s@%s'%(group.alias_id.alias_name,group.alias_id.alias_domain)orFalse
        }

    @http.route("/groups/subscribe/<model('mail.channel'):channel>/<int:partner_id>/<string:token>",type='http',auth='public',website=True)
    defconfirm_subscribe(self,channel,partner_id,token,**kw):
        subscriber=request.env['mail.channel.partner'].search([('channel_id','=',channel.id),('partner_id','=',partner_id)])
        ifsubscriber:
            #alreadyregistered,maybeclickedtwice
            returnrequest.render('website_mail_channel.invalid_token_subscription')

        subscriber_token=channel._generate_action_token(partner_id,action='subscribe')
        iftoken!=subscriber_token:
            returnrequest.render('website_mail_channel.invalid_token_subscription')

        #addpartner
        channel.sudo().write({'channel_partner_ids':[(4,partner_id)]})

        returnrequest.render("website_mail_channel.confirmation_subscription",{'subscribing':True})

    @http.route("/groups/unsubscribe/<model('mail.channel'):channel>/<int:partner_id>/<string:token>",type='http',auth='public',website=True)
    defconfirm_unsubscribe(self,channel,partner_id,token,**kw):
        subscriber=request.env['mail.channel.partner'].search([('channel_id','=',channel.id),('partner_id','=',partner_id)])
        ifnotsubscriber:
            partner=request.env['res.partner'].browse(partner_id).sudo().exists()
            #FIXME:removetry/exceptinmaster
            try:
                response=request.render(
                    'website_mail_channel.not_subscribed',
                    {'partner_id':partner})
                #makesuretherendering(andthuserroriftemplateis
                #missing)happensinsidethetryblock
                response.flatten()
                returnresponse
            exceptValueError:
                return_("Theaddress%sisalreadyunsubscribedorwasneversubscribedtoanymailinglist")%(
                    partner.email
                )

        subscriber_token=channel._generate_action_token(partner_id,action='unsubscribe')
        iftoken!=subscriber_token:
            returnrequest.render('website_mail_channel.invalid_token_subscription')

        #removepartner
        channel.sudo().write({'channel_partner_ids':[(3,partner_id)]})

        returnrequest.render("website_mail_channel.confirmation_subscription",{'subscribing':False})
