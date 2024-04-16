#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importlogging
importre
fromuuidimportuuid4

fromflectraimport_,api,fields,models,modules,tools
fromflectra.exceptionsimportUserError,ValidationError
fromflectra.osvimportexpression
fromflectra.toolsimportormcache
fromflectra.exceptionsimportAccessError
fromflectra.addons.base.models.ir_modelimportMODULE_UNINSTALL_FLAG
fromflectra.toolsimporthtml_escape

MODERATION_FIELDS=['moderation','moderator_ids','moderation_ids','moderation_notify','moderation_notify_msg','moderation_guidelines','moderation_guidelines_msg']
_logger=logging.getLogger(__name__)


classChannelPartner(models.Model):
    _name='mail.channel.partner'
    _description='ListenersofaChannel'
    _table='mail_channel_partner'
    _rec_name='partner_id'

    custom_channel_name=fields.Char('Customchannelname')
    partner_id=fields.Many2one('res.partner',string='Recipient',ondelete='cascade')
    partner_email=fields.Char('Email',related='partner_id.email',depends=['partner_id'],related_sudo=False)
    channel_id=fields.Many2one('mail.channel',string='Channel',ondelete='cascade')
    fetched_message_id=fields.Many2one('mail.message',string='LastFetched')
    seen_message_id=fields.Many2one('mail.message',string='LastSeen')
    fold_state=fields.Selection([('open','Open'),('folded','Folded'),('closed','Closed')],string='ConversationFoldState',default='open')
    is_minimized=fields.Boolean("Conversationisminimized")
    is_pinned=fields.Boolean("Ispinnedontheinterface",default=True)

    @api.model
    defcreate(self,vals):
        """Similaraccessruleastheaccessruleofthemailchannel.

        ItcannotbeimplementedinXML,becausewhentherecordwillbecreated,the
        partnerwillbeaddedinthechannelandthesecurityrulewillalwaysauthorize
        thecreation.
        """
        if'channel_id'invalsandnotself.env.is_admin():
            channel_id=self.env['mail.channel'].browse(vals['channel_id'])
            ifnotchannel_id._can_invite(vals.get('partner_id')):
                raiseAccessError(_('Thisusercannotbeaddedinthischannel'))
        returnsuper(ChannelPartner,self).create(vals)

    defwrite(self,vals):
        ifnotself.env.is_admin():
            if{'channel_id','partner_id','partner_email'}&set(vals):
                raiseAccessError(_('Youcannotwriteonthisfield'))
        returnsuper(ChannelPartner,self).write(vals)


classModeration(models.Model):
    _name='mail.moderation'
    _description='Channelblack/whitelist'

    email=fields.Char(string="Email",index=True,required=True)
    status=fields.Selection([
        ('allow','AlwaysAllow'),
        ('ban','PermanentBan')],
        string="Status",required=True)
    channel_id=fields.Many2one('mail.channel',string="Channel",index=True,required=True)

    _sql_constraints=[
        ('channel_email_uniq','unique(email,channel_id)','Theemailaddressmustbeuniqueperchannel!')
    ]


classChannel(models.Model):
    """Amail.channelisadiscussiongroupthatmaybehavelikealistener
    ondocuments."""
    _description='DiscussionChannel'
    _name='mail.channel'
    _mail_flat_thread=False
    _mail_post_access='read'
    _inherit=['mail.thread','mail.alias.mixin']

    MAX_BOUNCE_LIMIT=10

    @api.model
    defdefault_get(self,fields):
        res=super(Channel,self).default_get(fields)
        ifnotres.get('alias_contact')and(notfieldsor'alias_contact'infields):
            res['alias_contact']='everyone'ifres.get('public','private')=='public'else'followers'
        returnres

    def_get_default_image(self):
        image_path=modules.get_module_resource('mail','static/src/img','groupdefault.png')
        returnbase64.b64encode(open(image_path,'rb').read())

    name=fields.Char('Name',required=True,translate=True)
    active=fields.Boolean(default=True,help="Setactivetofalsetohidethechannelwithoutremovingit.")
    channel_type=fields.Selection([
        ('chat','ChatDiscussion'),
        ('channel','Channel')],
        'ChannelType',default='channel')
    is_chat=fields.Boolean(string='Isachat',compute='_compute_is_chat',default=False)
    description=fields.Text('Description')
    uuid=fields.Char('UUID',size=50,index=True,default=lambdaself:str(uuid4()),copy=False)
    email_send=fields.Boolean('Sendmessagesbyemail',default=False)
    #multiuserschannel
    #depends=['...']isfor`test_mail/tests/common.py`,classModeration,`setUpClass`
    channel_last_seen_partner_ids=fields.One2many('mail.channel.partner','channel_id',string='LastSeen',depends=['channel_partner_ids'])
    channel_partner_ids=fields.Many2many('res.partner','mail_channel_partner','channel_id','partner_id',string='Listeners',depends=['channel_last_seen_partner_ids'])
    channel_message_ids=fields.Many2many('mail.message','mail_message_mail_channel_rel',copy=False)
    is_member=fields.Boolean('Isamember',compute='_compute_is_member')
    #access
    public=fields.Selection([
        ('public','Everyone'),
        ('private','Invitedpeopleonly'),
        ('groups','Selectedgroupofusers')],
        'Privacy',required=True,default='groups',
        help='Thisgroupisvisiblebynonmembers.Invisiblegroupscanaddmembersthroughtheinvitebutton.')
    group_public_id=fields.Many2one('res.groups',string='AuthorizedGroup',
                                      default=lambdaself:self.env.ref('base.group_user'))
    group_ids=fields.Many2many(
        'res.groups',string='AutoSubscription',
        help="Membersofthosegroupswillautomaticallyaddedasfollowers."
             "Notethattheywillbeabletomanagetheirsubscriptionmanually"
             "ifnecessary.")
    image_128=fields.Image("Image",max_width=128,max_height=128,default=_get_default_image)
    is_subscribed=fields.Boolean(
        'IsSubscribed',compute='_compute_is_subscribed')
    #moderation
    moderation=fields.Boolean(string='Moderatethischannel')
    moderator_ids=fields.Many2many('res.users','mail_channel_moderator_rel',string='Moderators')
    is_moderator=fields.Boolean(help="Currentuserisamoderatorofthechannel",string='Moderator',compute="_compute_is_moderator")
    moderation_ids=fields.One2many(
        'mail.moderation','channel_id',string='ModeratedEmails',
        groups="base.group_user")
    moderation_count=fields.Integer(
        string='Moderatedemailscount',compute='_compute_moderation_count',
        groups="base.group_user")
    moderation_notify=fields.Boolean(string="Automaticnotification",help="Peoplereceiveanautomaticnotificationabouttheirmessagebeingwaitingformoderation.")
    moderation_notify_msg=fields.Text(string="Notificationmessage")
    moderation_guidelines=fields.Boolean(string="Sendguidelinestonewsubscribers",help="Newcomersonthismoderatedchannelwillautomaticallyreceivetheguidelines.")
    moderation_guidelines_msg=fields.Text(string="Guidelines")

    @api.depends('channel_partner_ids')
    def_compute_is_subscribed(self):
        forchannelinself:
            channel.is_subscribed=self.env.user.partner_idinchannel.channel_partner_ids

    @api.depends('moderator_ids')
    def_compute_is_moderator(self):
        forchannelinself:
            channel.is_moderator=self.env.userinchannel.moderator_ids

    @api.depends('moderation_ids')
    def_compute_moderation_count(self):
        read_group_res=self.env['mail.moderation'].read_group([('channel_id','in',self.ids)],['channel_id'],'channel_id')
        data=dict((res['channel_id'][0],res['channel_id_count'])forresinread_group_res)
        forchannelinself:
            channel.moderation_count=data.get(channel.id,0)

    @api.constrains('moderator_ids')
    def_check_moderator_email(self):
        ifany(notmoderator.emailforchannelinselfformoderatorinchannel.moderator_ids):
            raiseValidationError(_("Moderatorsmusthaveanemailaddress."))

    @api.constrains('moderator_ids','channel_partner_ids','channel_last_seen_partner_ids')
    def_check_moderator_is_member(self):
        forchannelinself:
            ifnot(channel.mapped('moderator_ids.partner_id')<=channel.sudo().channel_partner_ids):
                raiseValidationError(_("Moderatorsshouldbemembersofthechanneltheymoderate."))

    @api.constrains('moderation','email_send')
    def_check_moderation_parameters(self):
        ifany(notchannel.email_sendandchannel.moderationforchannelinself):
            raiseValidationError(_('Onlymailinglistscanbemoderated.'))

    @api.constrains('moderator_ids')
    def_check_moderator_existence(self):
        ifany(notchannel.moderator_idsforchannelinselfifchannel.moderation):
            raiseValidationError(_('Moderatedchannelsmusthavemoderators.'))

    def_compute_is_member(self):
        memberships=self.env['mail.channel.partner'].sudo().search([
            ('channel_id','in',self.ids),
            ('partner_id','=',self.env.user.partner_id.id),
            ])
        membership_ids=memberships.mapped('channel_id')
        forrecordinself:
            record.is_member=recordinmembership_ids

    def_compute_is_chat(self):
        forrecordinself:
            ifrecord.channel_type=='chat':
                record.is_chat=True
            else:
                record.is_chat=False

    @api.onchange('public')
    def_onchange_public(self):
        ifself.public!='public'andself.alias_contact=='everyone':
            self.alias_contact='followers'

    @api.onchange('moderator_ids')
    def_onchange_moderator_ids(self):
        missing_partner_ids=set(self.mapped('moderator_ids.partner_id').ids)-set(self.mapped('channel_last_seen_partner_ids.partner_id').ids)
        ifmissing_partner_ids:
            self.channel_last_seen_partner_ids=[
                (0,0,{'partner_id':partner_id})
                forpartner_idinmissing_partner_ids
            ]

    @api.onchange('email_send')
    def_onchange_email_send(self):
        ifnotself.email_send:
            self.moderation=False

    @api.onchange('moderation')
    def_onchange_moderation(self):
        ifnotself.moderation:
            self.moderation_notify=False
            self.moderation_guidelines=False
            self.moderator_ids=False
        else:
            self.moderator_ids|=self.env.user

    @api.model
    defcreate(self,vals):
        #ensureimageatquickcreate
        ifnotvals.get('image_128'):
            defaults=self.default_get(['image_128'])
            vals['image_128']=defaults['image_128']

        current_partner=self.env.user.partner_id.id
        #alwaysaddcurrentusertonewchannel,gothrough
        #channel_last_seen_partner_idsotherwiseinv14thechannelisnot
        #visiblefortheuser(becauseis_pinnedisfalseandtakeninaccount)
        if'channel_partner_ids'invals:
            vals['channel_partner_ids']=[
                entry
                forentryinvals['channel_partner_ids']
                ifentry[0]!=4orentry[1]!=current_partner
            ]
        membership=vals.setdefault('channel_last_seen_partner_ids',[])
        ifall(entry[0]!=0orentry[2].get('partner_id')!=current_partnerforentryinmembership):
            membership.append((0,False,{'partner_id':current_partner}))

        visibility_default=self._fields['public'].default(self)
        visibility=vals.pop('public',visibility_default)
        vals['public']='public'
        #Createchannelandalias
        channel=super(Channel,self.with_context(
            mail_create_nolog=True,mail_create_nosubscribe=True)
        ).create(vals)
        ifvisibility!='public':
            channel.sudo().public=visibility

        ifvals.get('group_ids'):
            channel._subscribe_users()

        #makechannellistenitself:postingonachannelnotifiesthechannel
        ifnotself._context.get('mail_channel_noautofollow'):
            channel.message_subscribe(channel_ids=[channel.id])

        returnchannel

    defunlink(self):
        #Deletemail.channel
        try:
            all_emp_group=self.env.ref('mail.channel_all_employees')
        exceptValueError:
            all_emp_group=None
        ifall_emp_groupandall_emp_groupinselfandnotself._context.get(MODULE_UNINSTALL_FLAG):
            raiseUserError(_('Youcannotdeletethosegroups,astheWholeCompanygroupisrequiredbyothermodules.'))
        self.env['bus.bus'].sendmany([[(self._cr.dbname,'mail.channel',channel.id),{'info':'delete'}]forchannelinself])
        returnsuper(Channel,self).unlink()

    defwrite(self,vals):
        #Firstchecksifusertriestomodifymoderationfieldsandhasnottherighttodoit.
        ifany(keyforkeyinMODERATION_FIELDSifvals.get(key))andany(self.env.usernotinchannel.moderator_idsforchannelinselfifchannel.moderation):
            ifnotself.env.user.has_group('base.group_system'):
                raiseUserError(_("Youdonothavetherightstomodifyfieldsrelatedtomoderationononeofthechannelsyouaremodifying."))

        result=super(Channel,self).write(vals)

        ifvals.get('group_ids'):
            self._subscribe_users()

        #avoidkeepingmessagestomoderateandacceptthem
        ifvals.get('moderation')isFalse:
            self.env['mail.message'].search([
                ('moderation_status','=','pending_moderation'),
                ('model','=','mail.channel'),
                ('res_id','in',self.ids)
            ])._moderate_accept()

        returnresult

    def_alias_get_creation_values(self):
        values=super(Channel,self)._alias_get_creation_values()
        values['alias_model_id']=self.env['ir.model']._get('mail.channel').id
        ifself.id:
            values['alias_force_thread_id']=self.id
        returnvalues

    def_subscribe_users(self):
        to_create=[]
        formail_channelinself:
            partners_to_add=mail_channel.group_ids.users.partner_id-mail_channel.channel_partner_ids
            to_create+=[{
                'channel_id':mail_channel.id,
                'partner_id':partner.id,
            }forpartnerinpartners_to_add]

        self.env['mail.channel.partner'].create(to_create)

    defaction_follow(self):
        self.ensure_one()
        channel_partner=self.mapped('channel_last_seen_partner_ids').filtered(lambdacp:cp.partner_id==self.env.user.partner_id)
        ifnotchannel_partner:
            returnself.write({'channel_last_seen_partner_ids':[(0,0,{'partner_id':self.env.user.partner_id.id})]})
        returnFalse

    defaction_unfollow(self):
        returnself._action_unfollow(self.env.user.partner_id)

    def_action_unfollow(self,partner):
        self.message_unsubscribe(partner.ids)
        ifpartnernotinself.with_context(active_test=False).channel_partner_ids:
            returnTrue
        channel_info=self.channel_info('unsubscribe')[0] #mustbecomputedbeforeleavingthechannel(accessrights)
        result=self.write({'channel_partner_ids':[(3,partner.id)]})
        #sideeffectofunsubscribethatwasn'ttakenintoaccountbecause
        #channel_infoiscalledbeforeactuallyunpinningthechannel
        channel_info['is_pinned']=False
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',partner.id),channel_info)
        ifnotself.email_send:
            notification=_('<divclass="o_mail_notification">left<ahref="#"class="o_channel_redirect"data-oe-id="%s">#%s</a></div>',self.id,self.name)
            #post'channelleft'messageasrootsincethepartnerjustunsubscribedfromthechannel
            self.sudo().message_post(body=notification,subtype_xmlid="mail.mt_comment",author_id=partner.id)
        returnresult

    def_notify_get_groups(self,msg_vals=None):
        """Allrecipientsofamessageonachannelareconsideredaspartners.
        Thismeanstheywillreceiveaminimalemail,withoutalinktoaccess
        inthebackend.Mailinglistsshouldindeedsendminimalemailstoavoid
        thenoise."""
        groups=super(Channel,self)._notify_get_groups(msg_vals=msg_vals)
        for(index,(group_name,group_func,group_data))inenumerate(groups):
            ifgroup_name!='customer':
                groups[index]=(group_name,lambdapartner:False,group_data)
        returngroups

    def_notify_email_header_dict(self):
        headers=super(Channel,self)._notify_email_header_dict()
        headers['Precedence']='list'
        #avoidout-of-officerepliesfromMSExchange
        #http://blogs.technet.com/b/exchange/archive/2006/10/06/3395024.aspx
        headers['X-Auto-Response-Suppress']='OOF'
        ifself.alias_domainandself.alias_name:
            headers['List-Id']='<%s.%s>'%(self.alias_name,self.alias_domain)
            headers['List-Post']='<mailto:%s@%s>'%(self.alias_name,self.alias_domain)
            #Avoidusersthinkingitwasapersonalmessage
            #X-Forge-To:willreplaceTo:afterSMTPenvelopeisdeterminedbyir.mail.server
            list_to='"%s"<%s@%s>'%(self.name,self.alias_name,self.alias_domain)
            headers['X-Forge-To']=list_to
        returnheaders

    def_message_receive_bounce(self,email,partner):
        """Overridebouncemanagementtounsubscribebouncingaddresses"""
        forpinpartner:
            ifp.message_bounce>=self.MAX_BOUNCE_LIMIT:
                self._action_unfollow(p)
        returnsuper(Channel,self)._message_receive_bounce(email,partner)

    def_notify_email_recipient_values(self,recipient_ids):
        #ExcludedBlacklisted
        whitelist=self.env['res.partner'].sudo().browse(recipient_ids).filtered(lambdap:notp.is_blacklisted)
        #realmailinglist:multiplerecipients(hiddenbyX-Forge-To)
        ifself.alias_domainandself.alias_name:
            return{
                'email_to':','.join(partner.email_formattedforpartnerinwhitelistifpartner.email_normalized),
                'recipient_ids':[],
            }
        returnsuper(Channel,self)._notify_email_recipient_values(whitelist.ids)

    def_extract_moderation_values(self,message_type,**kwargs):
        """Thismethodisusedtocomputemoderationstatusbeforethecreation
        ofamessage. Forthisoperationthemessage'sauthoremailaddressisrequired.
        Thisaddressisreturnedwithstatusforothercomputations."""
        moderation_status='accepted'
        email=''
        ifself.moderationandmessage_typein['email','comment']:
            author_id=kwargs.get('author_id')
            ifauthor_idandisinstance(author_id,int):
                email=self.env['res.partner'].browse([author_id]).email
            elifauthor_id:
                email=author_id.email
            elifkwargs.get('email_from'):
                email=tools.email_split(kwargs['email_from'])[0]
            else:
                email=self.env.user.email
            ifemailinself.mapped('moderator_ids.email'):
                returnmoderation_status,email
            status=self.env['mail.moderation'].sudo().search([('email','=',email),('channel_id','in',self.ids)]).mapped('status')
            ifstatusandstatus[0]=='allow':
                moderation_status='accepted'
            elifstatusandstatus[0]=='ban':
                moderation_status='rejected'
            else:
                moderation_status='pending_moderation'
        returnmoderation_status,email

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,*,message_type='notification',**kwargs):
        moderation_status,email=self._extract_moderation_values(message_type,**kwargs)
        ifmoderation_status=='rejected':
            returnself.env['mail.message']

        self.filtered(lambdachannel:channel.is_chat).mapped('channel_last_seen_partner_ids').sudo().write({'is_pinned':True})

        #mail_post_autofollow=Falseisnecessarytopreventaddingfollowers
        #whenusingmentionsinchannels.Followersshouldnotbeaddedto
        #channels,andespeciallynotautomatically(becausechannelmembership
        #shouldbemanagedwithchannel.partnerinstead).
        #ThecurrentclientcodemightbesettingthekeytoTrueonsending
        #messagebutitisonlyusefulwhentargetingcustomersinchatter.
        #ThisvalueshouldsimplybesettoFalseinchannelsnomatterwhat.
        message=super(Channel,self.with_context(mail_create_nosubscribe=True,mail_post_autofollow=False)).message_post(message_type=message_type,moderation_status=moderation_status,**kwargs)

        #Notifiesthemessageauthorwhenhismessageispendingmoderationifrequiredonchannel.
        #Thefields"email_from"and"reply_to"arefilledinautomaticallybymethodcreateinmodelmail.message.
        ifself.moderation_notifyandself.moderation_notify_msgandmessage_typein['email','comment']andmoderation_status=='pending_moderation':
            self.env['mail.mail'].sudo().create({
                'author_id':self.env.user.partner_id.id,
                'email_from':self.env.user.company_id.catchall_formattedorself.env.user.company_id.email_formatted,
                'body_html':self.moderation_notify_msg,
                'subject':'Re:%s'%(kwargs.get('subject','')),
                'email_to':email,
                'auto_delete':True,
                'state':'outgoing'
            })
        returnmessage

    def_message_post_after_hook(self,message,msg_vals):
        """
        Automaticallysetthemessagepostedbythecurrentuserasseenforhimself.
        """
        self._set_last_seen_message(message)
        returnsuper()._message_post_after_hook(message=message,msg_vals=msg_vals)

    def_alias_get_error_message(self,message,message_dict,alias):
        ifalias.alias_contact=='followers'andself.ids:
            author=self.env['res.partner'].browse(message_dict.get('author_id',False))
            ifnotauthororauthornotinself.channel_partner_ids:
                return_('restrictedtochannelmembers')
            returnFalse
        returnsuper(Channel,self)._alias_get_error_message(message,message_dict,alias)

    definit(self):
        self._cr.execute('SELECTindexnameFROMpg_indexesWHEREindexname=%s',('mail_channel_partner_seen_message_id_idx',))
        ifnotself._cr.fetchone():
            self._cr.execute('CREATEINDEXmail_channel_partner_seen_message_id_idxONmail_channel_partner(channel_id,partner_id,seen_message_id)')

    #--------------------------------------------------
    #Moderation
    #--------------------------------------------------

    defsend_guidelines(self):
        """Sendguidelinestoallchannelmembers."""
        ifself.env.userinself.moderator_idsorself.env.user.has_group('base.group_system'):
            success=self._send_guidelines(self.channel_partner_ids)
            ifnotsuccess:
                raiseUserError(_('View"mail.mail_channel_send_guidelines"wasnotfound.Noemailhasbeensent.Pleasecontactanadministratortofixthisissue.'))
        else:
            raiseUserError(_("Onlyanadministratororamoderatorcansendguidelinestochannelmembers!"))

    def_send_guidelines(self,partners):
        """Sendguidelinesofagivenchannel.ReturnsFalseiftemplateusedforguidelines
        notfound.Callermayhavetohandlethisreturnvalue."""
        self.ensure_one()
        view=self.env.ref('mail.mail_channel_send_guidelines',raise_if_not_found=False)
        ifnotview:
            _logger.warning('View"mail.mail_channel_send_guidelines"wasnotfound.')
            returnFalse
        banned_emails=self.env['mail.moderation'].sudo().search([
            ('status','=','ban'),
            ('channel_id','in',self.ids)
        ]).mapped('email')
        forpartnerinpartners.filtered(lambdap:p.emailandnot(p.emailinbanned_emails)):
            company=partner.company_idorself.env.company
            create_values={
                'email_from':company.catchall_formattedorcompany.email_formatted,
                'author_id':self.env.user.partner_id.id,
                'body_html':view._render({'channel':self,'partner':partner},engine='ir.qweb',minimal_qcontext=True),
                'subject':_("Guidelinesofchannel%s",self.name),
                'recipient_ids':[(4,partner.id)]
            }
            mail=self.env['mail.mail'].sudo().create(create_values)
        returnTrue

    def_update_moderation_email(self,emails,status):
        """Thismethodaddsemailsintoeitherwhiteorblackofthechannellistofemails
            accordingtostatus.Ifanemailinemailsisalreadymoderated,themethodupdatestheemailstatus.
            :paramemails:listofemailaddressestoputinwhiteorblacklistofchannel.
            :paramstatus:valueis'allow'or'ban'.Emailsareputinwhitelistif'allow',inblacklistif'ban'.
        """
        self.ensure_one()
        splitted_emails=[tools.email_split(email)[0]foremailinemailsiftools.email_split(email)]
        moderated=self.env['mail.moderation'].sudo().search([
            ('email','in',splitted_emails),
            ('channel_id','in',self.ids)
        ])
        cmds=[(1,record.id,{'status':status})forrecordinmoderated]
        not_moderated=[emailforemailinsplitted_emailsifemailnotinmoderated.mapped('email')]
        cmds+=[(0,0,{'email':email,'status':status})foremailinnot_moderated]
        returnself.write({'moderation_ids':cmds})

    #------------------------------------------------------
    #InstantMessagingAPI
    #------------------------------------------------------
    #Achannelheadershouldbebroadcasted:
    #  -whenaddingusertochannel(onlytothenewaddedpartners)
    #  -whenfolding/minimizingachannel(onlytotheusermakingtheaction)
    #Amessageshouldbebroadcasted:
    #  -whenamessageispostedonachannel(tothechannel,using_notify()method)

    #Anonymousmethod
    def_broadcast(self,partner_ids):
        """Broadcastthecurrentchannelheadertothegivenpartnerids
            :parampartner_ids:thepartnertonotify
        """
        notifications=self._channel_channel_notifications(partner_ids)
        self.env['bus.bus'].sendmany(notifications)

    def_channel_channel_notifications(self,partner_ids):
        """Generatethebusnotificationsofcurrentchannelforthegivenpartnerids
            :parampartner_ids:thepartnertosendthecurrentchannelheader
            :returnslistofbusnotifications(tuple(bus_channe,message_content))
        """
        notifications=[]
        forpartnerinself.env['res.partner'].browse(partner_ids):
            user_id=partner.user_idsandpartner.user_ids[0]orFalse
            ifuser_id:
                user_channels=self.with_user(user_id).with_context(
                    allowed_company_ids=user_id.company_ids.ids
                )
                forchannel_infoinuser_channels.channel_info():
                    notifications.append([(self._cr.dbname,'res.partner',partner.id),channel_info])
        returnnotifications

    def_notify_thread(self,message,msg_vals=False,**kwargs):
        #Whenpostingamessageonamailchannel,managemoderationandpostponenotifyusers
        ifnotmsg_valsormsg_vals.get('moderation_status')!='pending_moderation':
            super(Channel,self)._notify_thread(message,msg_vals=msg_vals,**kwargs)
        else:
            message._notify_pending_by_chat()

    def_channel_message_notifications(self,message,message_format=False):
        """Generatethebusnotificationsforthegivenmessage
            :parammessage:themail.messagetosent
            :returnslistofbusnotifications(tuple(bus_channe,message_content))
        """
        message_format=message_formatormessage.message_format()[0]
        notifications=[]
        forchannelinself:
            notifications.append([(self._cr.dbname,'mail.channel',channel.id),dict(message_format)])
            #adduuidtoallowanonymoustolisten
            ifchannel.public=='public':
                notifications.append([channel.uuid,dict(message_format)])
        returnnotifications

    @api.model
    defpartner_info(self,all_partners,direct_partners):
        """
        Returntheinformationneededbychanneltodisplaychannelmembers
            :paramall_partners:listofres.parner():
            :paramdirect_partners:listofres.parner():
            :returns:alistof{'id','name','email'}foreachpartnerandadds{im_status}fordirect_partners.
            :rtype:list(dict)
        """
        partner_infos={partner['id']:partnerforpartnerinall_partners.sudo().read(['id','name','email'])}
        #addim_statusfordirect_partners
        direct_partners_im_status={partner['id']:partnerforpartnerindirect_partners.sudo().read(['im_status'])}

        foriindirect_partners_im_status.keys():
            partner_infos[i].update(direct_partners_im_status[i])

        returnpartner_infos

    defchannel_info(self,extra_info=False):
        """Gettheinformationsheaderforthecurrentchannels
            :returnsalistofchannelsvalues
            :rtype:list(dict)
        """
        ifnotself:
            return[]
        channel_infos=[]
        #allrelationspartner_channelonthosechannels
        all_partner_channel=self.env['mail.channel.partner'].search([('channel_id','in',self.ids)])

        #allpartnerinfosonthosechannels
        channel_dict={channel.id:channelforchannelinself}
        all_partners=all_partner_channel.mapped('partner_id')
        direct_channel_partners=all_partner_channel.filtered(lambdapc:channel_dict[pc.channel_id.id].channel_type=='chat')
        direct_partners=direct_channel_partners.mapped('partner_id')
        partner_infos=self.partner_info(all_partners,direct_partners)
        channel_last_message_ids=dict((r['id'],r['message_id'])forrinself._channel_last_message_ids())

        forchannelinself:
            info={
                'id':channel.id,
                'name':channel.name,
                'uuid':channel.uuid,
                'state':'open',
                'is_minimized':False,
                'channel_type':channel.channel_type,
                'public':channel.public,
                'mass_mailing':channel.email_send,
                'moderation':channel.moderation,
                'is_moderator':self.env.uidinchannel.moderator_ids.ids,
                'group_based_subscription':bool(channel.group_ids),
                'create_uid':channel.create_uid.id,
            }
            ifextra_info:
                info['info']=extra_info

            #addlastmessagepreview(onlyusedinmobile)
            info['last_message_id']=channel_last_message_ids.get(channel.id,False)
            #listenersofthechannel
            channel_partners=all_partner_channel.filtered(lambdapc:channel.id==pc.channel_id.id)

            #findthechannelpartnerstate,ifloggeduser
            ifself.env.userandself.env.user.partner_id:
                #addneedactionandunreadcounter,sincetheuserislogged
                info['message_needaction_counter']=channel.message_needaction_counter
                info['message_unread_counter']=channel.message_unread_counter

                #addusersessionstate,ifavailableandifuserislogged
                partner_channel=channel_partners.filtered(lambdapc:pc.partner_id.id==self.env.user.partner_id.id)
                ifpartner_channel:
                    partner_channel=partner_channel[0]
                    info['state']=partner_channel.fold_stateor'open'
                    info['is_minimized']=partner_channel.is_minimized
                    info['seen_message_id']=partner_channel.seen_message_id.id
                    info['custom_channel_name']=partner_channel.custom_channel_name
                    info['is_pinned']=partner_channel.is_pinned

            #addmembersinfos
            ifchannel.channel_type!='channel':
                #avoidsendingpotentiallyalotofmembersforbigchannels
                #excludechatandothersmallchannelsfromthisoptimizationbecausetheyare
                #assumedtobesmallerandit'simportanttoknowthememberlistforthem
                info['members']=[channel._channel_info_format_member(partner,partner_infos[partner.id])forpartnerinchannel_partners.partner_id.sudo().with_prefetch(all_partners.ids)]
            ifchannel.channel_type!='channel':
                info['seen_partners_info']=[{
                    'id':cp.id,
                    'partner_id':cp.partner_id.id,
                    'fetched_message_id':cp.fetched_message_id.id,
                    'seen_message_id':cp.seen_message_id.id,
                }forcpinchannel_partners]

            channel_infos.append(info)
        returnchannel_infos

    def_channel_info_format_member(self,partner,partner_info):
        """Returnsmemberinformationinthecontextofselfchannel."""
        self.ensure_one()
        returnpartner_info

    defchannel_fetch_message(self,last_id=False,limit=20):
        """Returnmessagevaluesofthecurrentchannel.
            :paramlast_id:lastmessageidtostarttheresearch
            :paramlimit:maximumnumberofmessagestofetch
            :returnslistofmessagesvalues
            :rtype:list(dict)
        """
        self.ensure_one()
        domain=[("channel_ids","in",self.ids)]
        iflast_id:
            domain.append(("id","<",last_id))
        returnself.env['mail.message'].message_fetch(domain=domain,limit=limit)

    #Usermethods
    @api.model
    defchannel_get(self,partners_to,pin=True):
        """Getthecanonicalprivatechannelbetweensomepartners,createitifneeded.
            Toreuseanoldchannel(conversation),thisonemustbeprivate,andcontains
            onlythegivenpartners.
            :parampartners_to:listofres.partneridstoaddtotheconversation
            :parampin:Trueifgettingthechannelshouldpinitforthecurrentuser
            :returns:channel_infoofthecreatedorexistingchannel
            :rtype:dict
        """
        ifself.env.user.partner_id.idnotinpartners_to:
            partners_to.append(self.env.user.partner_id.id)
        #determinetypeaccordingtothenumberofpartnerinthechannel
        self.flush()
        self.env.cr.execute("""
            SELECTP.channel_id
            FROMmail_channelC,mail_channel_partnerP
            WHEREP.channel_id=C.id
                ANDC.publicLIKE'private'
                ANDP.partner_idIN%s
                ANDC.channel_typeLIKE'chat'
                ANDNOTEXISTS(
                    SELECT*
                    FROMmail_channel_partnerP2
                    WHEREP2.channel_id=C.id
                        ANDP2.partner_idNOTIN%s
                )
            GROUPBYP.channel_id
            HAVINGARRAY_AGG(DISTINCTP.partner_idORDERBYP.partner_id)=%s
            LIMIT1
        """,(tuple(partners_to),tuple(partners_to),sorted(list(partners_to)),))
        result=self.env.cr.dictfetchall()
        ifresult:
            #gettheexistingchannelbetweenthegivenpartners
            channel=self.browse(result[0].get('channel_id'))
            #pinupthechannelforthecurrentpartner
            ifpin:
                self.env['mail.channel.partner'].search([('partner_id','=',self.env.user.partner_id.id),('channel_id','=',channel.id),('is_pinned','=',False)]).write({'is_pinned':True})
            channel._broadcast(self.env.user.partner_id.ids)
        else:
            #createanewone
            channel=self.create({
                'channel_partner_ids':[(4,partner_id)forpartner_idinpartners_to],
                'public':'private',
                'channel_type':'chat',
                'email_send':False,
                'name':','.join(self.env['res.partner'].sudo().browse(partners_to).mapped('name')),
            })
            channel._broadcast(partners_to)
        returnchannel.channel_info()[0]

    @api.model
    defchannel_get_and_minimize(self,partners_to):
        channel=self.channel_get(partners_to)
        ifchannel:
            self.channel_minimize(channel['uuid'])
        returnchannel

    @api.model
    defchannel_fold(self,uuid,state=None):
        """Updatethefold_stateofthegivensession.Inordertosyncronizewebbrowser
            tabs,thechangewillbebroadcasttohimself(thecurrentuserchannel).
            Note:theuserneedtobelogged
            :paramstate:thenewstatusofthesessionforthecurrentuser.
        """
        domain=[('partner_id','=',self.env.user.partner_id.id),('channel_id.uuid','=',uuid)]
        forsession_stateinself.env['mail.channel.partner'].search(domain):
            ifnotstate:
                state=session_state.fold_state
                ifsession_state.fold_state=='open':
                    state='folded'
                else:
                    state='open'
            is_minimized=bool(state!='closed')
            vals={}
            ifsession_state.fold_state!=state:
                vals['fold_state']=state
            ifsession_state.is_minimized!=is_minimized:
                vals['is_minimized']=is_minimized
            ifvals:
                session_state.write(vals)
            self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),session_state.channel_id.channel_info()[0])

    @api.model
    defchannel_minimize(self,uuid,minimized=True):
        values={
            'fold_state':minimizedand'open'or'closed',
            'is_minimized':minimized
        }
        domain=[('partner_id','=',self.env.user.partner_id.id),('channel_id.uuid','=',uuid)]
        channel_partners=self.env['mail.channel.partner'].search(domain,limit=1)
        channel_partners.write(values)
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),channel_partners.channel_id.channel_info()[0])

    @api.model
    defchannel_pin(self,uuid,pinned=False):
        #addthepersoninthechannel,andpinit(orunpinit)
        channel=self.search([('uuid','=',uuid)])
        channel._execute_channel_pin(pinned)

    def_execute_channel_pin(self,pinned=False):
        """Hookforwebsite_livechatchannelunpinandcleaning"""
        self.ensure_one()
        channel_partners=self.env['mail.channel.partner'].search(
            [('partner_id','=',self.env.user.partner_id.id),('channel_id','=',self.id),('is_pinned','!=',pinned)])
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),self.channel_info('unsubscribe'ifnotpinnedelseFalse)[0])
        ifchannel_partners:
            channel_partners.write({'is_pinned':pinned})

    defchannel_seen(self,last_message_id=None):
        """
        Markchannelasseenbyupdatingseenmessageidofthecurrentloggedpartner
        :paramlast_message_id:theidofthemessagetobemarkedasseen,lastmessageofthe
        threadbydefault.ThisparamSHOULDberequired,thedefaultbehaviourisDEPRECATEDand
        keptonlyforcompatibilityreasons.
        """
        self.ensure_one()
        domain=[('channel_ids','in',self.ids)]
        iflast_message_id:
            domain=expression.AND([domain,[('id','<=',last_message_id)]])
        last_message=self.env['mail.message'].search(domain,order="idDESC",limit=1)
        ifnotlast_message:
            return

        self._set_last_seen_message(last_message)

        data={
            'info':'channel_seen',
            'last_message_id':last_message.id,
            'partner_id':self.env.user.partner_id.id,
        }
        ifself.channel_type=='chat':
            self.env['bus.bus'].sendmany([[(self._cr.dbname,'mail.channel',self.id),data]])
        else:
            data['channel_id']=self.id
            self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),data)
        returnlast_message.id

    def_set_last_seen_message(self,last_message):
        """
        Setlastseenmessageof`self`channelsforthecurrentuser.
        :paramlast_message:themessagetosetaslastseenmessage
        """
        channel_partner_domain=expression.AND([
            [('channel_id','in',self.ids)],
            [('partner_id','=',self.env.user.partner_id.id)],
            expression.OR([
                [('seen_message_id','=',False)],
                [('seen_message_id','<',last_message.id)]
            ])
        ])
        channel_partner=self.env['mail.channel.partner'].search(channel_partner_domain)
        channel_partner.write({
            'fetched_message_id':last_message.id,
            'seen_message_id':last_message.id,
        })

    defchannel_fetched(self):
        """Broadcastthechannel_fetchednotificationtochannelmembers
            :paramchannel_ids:listofchannelidthathasbeenfetchedbycurrentuser
        """
        forchannelinself:
            ifnotchannel.channel_message_ids.ids:
                return
            ifchannel.channel_type!='chat':
                return
            last_message_id=channel.channel_message_ids.ids[0]#zeroistheindexofthelastmessage
            channel_partner=self.env['mail.channel.partner'].search([('channel_id','=',channel.id),('partner_id','=',self.env.user.partner_id.id)],limit=1)
            ifchannel_partner.fetched_message_id.id==last_message_id:
                #lastmessagefetchedbyuserisalreadyup-to-date
                return
            #Avoidserializationerrorwhenmultipletabsareopened.
            query="""
                UPDATEmail_channel_partner
                SETfetched_message_id=%s
                WHEREidIN(
                    SELECTidFROMmail_channel_partnerWHEREid=%s
                    FORNOKEYUPDATESKIPLOCKED
                )
            """
            self.env.cr.execute(query,(last_message_id,channel_partner.id))
            data={
                'id':channel_partner.id,
                'info':'channel_fetched',
                'last_message_id':last_message_id,
                'partner_id':self.env.user.partner_id.id,
            }
            self.env['bus.bus'].sendmany([[(self._cr.dbname,'mail.channel',channel.id),data]])

    defchannel_invite(self,partner_ids):
        """Addthegivenpartner_idstothecurrentchannelsandbroadcastthechannelheadertothem.
            :parampartner_ids:listofpartneridtoadd
        """
        partners=self.env['res.partner'].browse(partner_ids)
        self._invite_check_access(partners)

        #addthepartner
        forchannelinself:
            partners_to_add=partners-channel.channel_partner_ids
            channel.write({'channel_last_seen_partner_ids':[(0,0,{'partner_id':partner_id})forpartner_idinpartners_to_add.ids]})
            forpartnerinpartners_to_add:
                ifpartner.id!=self.env.user.partner_id.id:
                    notification=_('<divclass="o_mail_notification">%(author)sinvited%(new_partner)sto<ahref="#"class="o_channel_redirect"data-oe-id="%(channel_id)s">#%(channel_name)s</a></div>',
                        author=self.env.user.display_name,
                        new_partner=partner.display_name,
                        channel_id=channel.id,
                        channel_name=channel.name,
                    )
                else:
                    notification=_('<divclass="o_mail_notification">joined<ahref="#"class="o_channel_redirect"data-oe-id="%s">#%s</a></div>',channel.id,channel.name)
                self.message_post(body=notification,message_type="notification",subtype_xmlid="mail.mt_comment",author_id=partner.id,notify_by_email=False)

        #broadcastthechannelheadertotheaddedpartner
        self._broadcast(partner_ids)

    def_invite_check_access(self,partners):
        """Checkinvitedpartnerscouldmatchchannelaccess"""
        failed=[]
        ifany(channel.public=='groups'forchannelinself):
            forchannelinself.filtered(lambdac:c.public=='groups'):
                invalid_partners=[partnerforpartnerinpartnersifchannel.group_public_idnotinpartner.mapped('user_ids.groups_id')]
                failed+=[(channel,partner)forpartnerininvalid_partners]

        iffailed:
            raiseUserError(
                _('Followinginvitesareinvalidasusergroupsdonotmatch:%s')%
                  ','.join('%s(channel%s)'%(partner.name,channel.name)forchannel,partnerinfailed)
            )

    def_can_invite(self,partner_id):
        """ReturnTrueifthecurrentusercaninvitethepartnertothechannel."""
        self.ensure_one()
        sudo_self=self.sudo()
        ifsudo_self.public=='public':
            returnTrue
        ifsudo_self.public=='private':
            returnself.is_member

        #gettheuserrelatedtotheinvitedpartner
        partner=self.env['res.partner'].browse(partner_id).exists()
        invited_user_id=partner.user_ids[:1]
        ifinvited_user_id:
            return(self.env.user|invited_user_id)<=sudo_self.group_public_id.users
        returnFalse

    @api.model
    defchannel_set_custom_name(self,channel_id,name=False):
        domain=[('partner_id','=',self.env.user.partner_id.id),('channel_id.id','=',channel_id)]
        channel_partners=self.env['mail.channel.partner'].search(domain,limit=1)
        channel_partners.write({
            'custom_channel_name':name,
        })

    defnotify_typing(self,is_typing):
        """Broadcastthetypingnotificationtochannelmembers
            :paramis_typing:(boolean)tellswhetherthecurrentuseristypingornot
        """
        notifications=[]
        forchannelinself:
            data=dict({
                'info':'typing_status',
                'is_typing':is_typing,
            },**channel._notify_typing_partner_data())
            notifications.append([(self._cr.dbname,'mail.channel',channel.id),data])#notifybackendusers
            notifications.append([channel.uuid,data])#notifyfrontendusers
        self.env['bus.bus'].sendmany(notifications)

    def_notify_typing_partner_data(self):
        """Returnstypingpartnerdataforselfchannel."""
        self.ensure_one()
        return{
            'partner_id':self.env.user.partner_id.id,
            'partner_name':self.env.user.partner_id.name,
        }

    #------------------------------------------------------
    #InstantMessagingViewSpecific(SlackClientAction)
    #------------------------------------------------------
    @api.model
    defchannel_fetch_slot(self):
        """Returnthechannelsoftheusergroupedby'slot'(channel,direct_messageorprivate_group),and
            themappingbetweenpartner_id/channel_idfordirect_messagechannels.
            :returnsdict:thegroupedchannelsandthemapping
        """
        values={}
        my_partner_id=self.env.user.partner_id.id
        pinned_channels=self.env['mail.channel.partner'].search([('partner_id','=',my_partner_id),('is_pinned','=',True)]).mapped('channel_id')

        #getthegroup/publicchannels
        values['channel_channel']=self.search([('channel_type','=','channel'),('public','in',['public','groups']),('channel_partner_ids','in',[my_partner_id])]).channel_info()

        #getthepinned'directmessage'channel
        direct_message_channels=self.search([('channel_type','=','chat'),('id','in',pinned_channels.ids)])
        values['channel_direct_message']=direct_message_channels.channel_info()

        #gettheprivategroup
        values['channel_private_group']=self.search([('channel_type','=','channel'),('public','=','private'),('channel_partner_ids','in',[my_partner_id])]).channel_info()
        returnvalues

    @api.model
    defchannel_search_to_join(self,name=None,domain=None):
        """Returnthechannelinfoofthechannelthecurrentpartnercanjoin
            :paramname:thenameoftheresearchedchannels
            :paramdomain:thebasedomainoftheresearch
            :returnsdict:channeldict
        """
        ifnotdomain:
            domain=[]
        domain=expression.AND([
            [('channel_type','=','channel')],
            [('channel_partner_ids','notin',[self.env.user.partner_id.id])],
            [('public','!=','private')],
            domain
        ])
        ifname:
            domain=expression.AND([domain,[('name','ilike','%'+name+'%')]])
        returnself.search(domain).read(['name','public','uuid','channel_type'])

    defchannel_join_and_get_info(self):
        self.ensure_one()
        added=self.action_follow()
        ifaddedandself.channel_type=='channel'andnotself.email_send:
            notification=_('<divclass="o_mail_notification">joined<ahref="#"class="o_channel_redirect"data-oe-id="%s">#%s</a></div>',self.id,self.name)
            self.message_post(body=notification,message_type="notification",subtype_xmlid="mail.mt_comment")

        ifaddedandself.moderation_guidelines:
            self._send_guidelines(self.env.user.partner_id)

        channel_info=self.channel_info('join')[0]
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),channel_info)
        returnchannel_info

    @api.model
    defchannel_create(self,name,privacy='groups'):
        """Createachannelandaddthecurrentpartner,broadcastit(tomaketheuserdirectly
            listentoitwhenpolling)
            :paramname:thenameofthechanneltocreate
            :paramprivacy:privacyofthechannel.Shouldbe'public'or'private'.
            :returndict:channelheader
        """
        #createthechannel
        new_channel=self.create({
            'name':name,
            'public':privacy,
            'email_send':False,
        })
        notification=_('<divclass="o_mail_notification">created<ahref="#"class="o_channel_redirect"data-oe-id="%s">#%s</a></div>',new_channel.id,new_channel.name)
        new_channel.message_post(body=notification,message_type="notification",subtype_xmlid="mail.mt_comment")
        channel_info=new_channel.channel_info('creation')[0]
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),channel_info)
        returnchannel_info

    @api.model
    defget_mention_suggestions(self,search,limit=8):
        """Return'limit'-firstchannels'id,nameandpublicfieldssuchthatthenamematchesa
            'search'string.Excludechannelsoftypechat(DM),andprivatechannelsthecurrent
            userisn'tregisteredto."""
        domain=expression.AND([
                        [('name','ilike',search)],
                        [('channel_type','=','channel')],
                        expression.OR([
                            [('public','!=','private')],
                            [('channel_partner_ids','in',[self.env.user.partner_id.id])]
                        ])
                    ])
        returnself.search_read(domain,['id','name','public','channel_type'],limit=limit)

    @api.model
    defchannel_fetch_listeners(self,uuid):
        """Returntheid,nameandemailofpartnerslisteningtothegivenchannel"""
        self._cr.execute("""
            SELECTP.id,P.name,P.email
            FROMmail_channel_partnerCP
                INNERJOINres_partnerPONCP.partner_id=P.id
                INNERJOINmail_channelCONCP.channel_id=C.id
            WHEREC.uuid=%s""",(uuid,))
        returnself._cr.dictfetchall()

    defchannel_fetch_preview(self):
        """Returnthelastmessageofthegivenchannels"""
        ifnotself:
            return[]
        channels_last_message_ids=self._channel_last_message_ids()
        channels_preview=dict((r['message_id'],r)forrinchannels_last_message_ids)
        last_messages=self.env['mail.message'].browse(channels_preview).message_format()
        formessageinlast_messages:
            channel=channels_preview[message['id']]
            del(channel['message_id'])
            channel['last_message']=message
        returnlist(channels_preview.values())

    def_channel_last_message_ids(self):
        """Returnthelastmessageofthegivenchannels."""
        ifnotself:
            return[]
        self.flush()
        self.env.cr.execute("""
            SELECTmail_channel_idASid,MAX(mail_message_id)ASmessage_id
            FROMmail_message_mail_channel_rel
            WHEREmail_channel_idIN%s
            GROUPBYmail_channel_id
            """,(tuple(self.ids),))
        returnself.env.cr.dictfetchall()

    #------------------------------------------------------
    #Commands
    #------------------------------------------------------
    @api.model
    @ormcache()
    defget_mention_commands(self):
        """Returnstheallowedcommandsinchannels"""
        commands=[]
        fornindir(self):
            match=re.search('^_define_command_(.+?)$',n)
            ifmatch:
                command=getattr(self,n)()
                command['name']=match.group(1)
                commands.append(command)
        returncommands

    defexecute_command(self,command='',**kwargs):
        """Executesagivencommand"""
        self.ensure_one()
        command_callback=getattr(self,'_execute_command_'+command,False)
        ifcommand_callback:
            command_callback(**kwargs)

    def_send_transient_message(self,partner_to,content):
        """Notifiespartner_tothatamessage(notstoredinDB)hasbeen
            writteninthischannel"""
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',partner_to.id),{
            'body':"<spanclass='o_mail_notification'>"+content+"</span>",
            'channel_ids':[self.id],
            'info':'transient_message',
        })

    def_define_command_help(self):
        return{'help':_("Showahelpermessage")}

    def_execute_command_help(self,**kwargs):
        partner=self.env.user.partner_id
        ifself.channel_type=='channel':
            msg=_("Youareinchannel<b>#%s</b>.",html_escape(self.name))
            ifself.public=='private':
                msg+=_("Thischannelisprivate.Peoplemustbeinvitedtojoinit.")
        else:
            all_channel_partners=self.env['mail.channel.partner'].with_context(active_test=False)
            channel_partners=all_channel_partners.search([('partner_id','!=',partner.id),('channel_id','=',self.id)])
            msg=_("Youareinaprivateconversationwith<b>@%s</b>.",_("@").join(html_escape(member.partner_id.name)formemberinchannel_partners)ifchannel_partnerselse_('Anonymous'))
        msg+=_("""<br><br>
            Type<b>@username</b>tomentionsomeone,andgrabhisattention.<br>
            Type<b>#channel</b>tomentionachannel.<br>
            Type<b>/command</b>toexecuteacommand.<br>
            Type<b>:shortcut</b>toinsertacannedresponseinyourmessage.<br>""")

        self._send_transient_message(partner,msg)

    def_define_command_leave(self):
        return{'help':_("Leavethischannel")}

    def_execute_command_leave(self,**kwargs):
        ifself.channel_type=='channel':
            self.action_unfollow()
        else:
            self.channel_pin(self.uuid,False)

    def_define_command_who(self):
        return{
            'channel_types':['channel','chat'],
            'help':_("Listusersinthecurrentchannel")
        }

    def_execute_command_who(self,**kwargs):
        partner=self.env.user.partner_id
        members=[
            '<ahref="#"data-oe-id='+str(p.id)+'data-oe-model="res.partner">@'+p.name+'</a>'
            forpinself.channel_partner_ids[:30]ifp!=partner
        ]
        iflen(members)==0:
            msg=_("Youarealoneinthischannel.")
        else:
            dots="..."iflen(members)!=len(self.channel_partner_ids)-1else""
            msg=_("Usersinthischannel:%(members)s%(dots)sandyou.",members=",".join(members),dots=dots)

        self._send_transient_message(partner,msg)
