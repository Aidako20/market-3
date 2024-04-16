#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging
importre

frombinasciiimportErrorasbinascii_error
fromcollectionsimportdefaultdict
fromoperatorimportitemgetter

fromflectraimport_,api,fields,models,modules,tools
fromflectra.exceptionsimportAccessError,UserError
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.toolsimportgroupby
fromflectra.tools.miscimportclean_context

_logger=logging.getLogger(__name__)
_image_dataurl=re.compile(r'(data:image/[a-z]+?);base64,([a-z0-9+/\n]{3,}=*)\n*([\'"])(?:data-filename="([^"]*)")?',re.I)


classMessage(models.Model):
    """Messagesmodel:systemnotification(replacingres.lognotifications),
        comments(OpenChatterdiscussion)andincomingemails."""
    _name='mail.message'
    _description='Message'
    _order='iddesc'
    _rec_name='record_name'

    @api.model
    defdefault_get(self,fields):
        res=super(Message,self).default_get(fields)
        missing_author='author_id'infieldsand'author_id'notinres
        missing_email_from='email_from'infieldsand'email_from'notinres
        ifmissing_authorormissing_email_from:
            author_id,email_from=self.env['mail.thread']._message_compute_author(res.get('author_id'),res.get('email_from'),raise_exception=False)
            ifmissing_email_from:
                res['email_from']=email_from
            ifmissing_author:
                res['author_id']=author_id
        returnres

    #content
    subject=fields.Char('Subject')
    date=fields.Datetime('Date',default=fields.Datetime.now)
    body=fields.Html('Contents',default='',sanitize_style=True)
    description=fields.Char(
        'Shortdescription',compute="_compute_description",
        help='Messagedescription:eitherthesubject,orthebeginningofthebody')
    attachment_ids=fields.Many2many(
        'ir.attachment','message_attachment_rel',
        'message_id','attachment_id',
        string='Attachments',
        help='Attachmentsarelinkedtoadocumentthroughmodel/res_idandtothemessage'
             'throughthisfield.')
    parent_id=fields.Many2one(
        'mail.message','ParentMessage',index=True,ondelete='setnull',
        help="Initialthreadmessage.")
    child_ids=fields.One2many('mail.message','parent_id','ChildMessages')
    #relateddocument
    model=fields.Char('RelatedDocumentModel',index=True)
    res_id=fields.Many2oneReference('RelatedDocumentID',index=True,model_field='model')
    record_name=fields.Char('MessageRecordName',help="Namegetoftherelateddocument.")
    #characteristics
    message_type=fields.Selection([
        ('email','Email'),
        ('comment','Comment'),
        ('notification','Systemnotification'),
        ('user_notification','UserSpecificNotification')],
        'Type',required=True,default='email',
        help="Messagetype:emailforemailmessage,notificationforsystem"
             "message,commentforothermessagessuchasuserreplies",
        )
    subtype_id=fields.Many2one('mail.message.subtype','Subtype',ondelete='setnull',index=True)
    mail_activity_type_id=fields.Many2one(
        'mail.activity.type','MailActivityType',
        index=True,ondelete='setnull')
    is_internal=fields.Boolean('EmployeeOnly',help='Hidetopublic/portalusers,independentlyfromsubtypeconfiguration.')
    #origin
    email_from=fields.Char('From',help="Emailaddressofthesender.Thisfieldissetwhennomatchingpartnerisfoundandreplacestheauthor_idfieldinthechatter.")
    author_id=fields.Many2one(
        'res.partner','Author',index=True,ondelete='setnull',
        help="Authorofthemessage.Ifnotset,email_frommayholdanemailaddressthatdidnotmatchanypartner.")
    author_avatar=fields.Binary("Author'savatar",related='author_id.image_128',depends=['author_id'],readonly=False)
    #recipients:includeinactivepartners(theymayhavebeenarchivedafter
    #themessagewassent,buttheyshouldremainvisibleintherelation)
    partner_ids=fields.Many2many('res.partner',string='Recipients',context={'active_test':False})
    #listofpartnerhavinganotification.Caution:listmaychangeovertimebecauseofnotifgccron.
    #mainlyusefullfortesting
    notified_partner_ids=fields.Many2many(
        'res.partner','mail_message_res_partner_needaction_rel',string='PartnerswithNeedAction',
        context={'active_test':False},depends=['notification_ids'],copy=False)
    needaction=fields.Boolean(
        'NeedAction',compute='_get_needaction',search='_search_needaction',
        help='NeedAction')
    has_error=fields.Boolean(
        'Haserror',compute='_compute_has_error',search='_search_has_error',
        help='Haserror')
    channel_ids=fields.Many2many(
        'mail.channel','mail_message_mail_channel_rel',string='Channels')
    #notifications
    notification_ids=fields.One2many(
        'mail.notification','mail_message_id','Notifications',
        auto_join=True,copy=False,depends=['notified_partner_ids'])
    #userinterface
    starred_partner_ids=fields.Many2many(
        'res.partner','mail_message_res_partner_starred_rel',string='FavoritedBy')
    starred=fields.Boolean(
        'Starred',compute='_get_starred',search='_search_starred',compute_sudo=False,
        help='Currentuserhasastarrednotificationlinkedtothismessage')
    #tracking
    tracking_value_ids=fields.One2many(
        'mail.tracking.value','mail_message_id',
        string='Trackingvalues',
        groups="base.group_system",
        help='Trackedvaluesarestoredinaseparatemodel.Thisfieldallowtoreconstruct'
             'thetrackingandtogeneratestatisticsonthemodel.')
    #mailgateway
    no_auto_thread=fields.Boolean(
        'Nothreadingforanswers',
        help='Answersdonotgointheoriginaldocumentdiscussionthread.Thishasanimpactonthegeneratedmessage-id.')
    message_id=fields.Char('Message-Id',help='Messageuniqueidentifier',index=True,readonly=1,copy=False)
    reply_to=fields.Char('Reply-To',help='Replyemailaddress.Settingthereply_tobypassestheautomaticthreadcreation.')
    mail_server_id=fields.Many2one('ir.mail_server','Outgoingmailserver')
    #moderation
    moderation_status=fields.Selection([
        ('pending_moderation','PendingModeration'),
        ('accepted','Accepted'),
        ('rejected','Rejected')],string="ModerationStatus",index=True)
    moderator_id=fields.Many2one('res.users',string="ModeratedBy",index=True)
    need_moderation=fields.Boolean('Needmoderation',compute='_compute_need_moderation',search='_search_need_moderation')
    #keepnotificationlayoutinformationstobeabletogeneratemailagain
    email_layout_xmlid=fields.Char('Layout',copy=False) #xmlidoflayout
    add_sign=fields.Boolean(default=True)
    #`test_adv_activity`,`test_adv_activity_full`,`test_message_assignation_inbox`,...
    #Bysettinganinverseformail.mail_message_id,thenumberofSQLqueriesdoneby`modified`isreduced.
    #'mail.mail'inheritsfrom`mail.message`:`_inherits={'mail.message':'mail_message_id'}`
    #Therefore,whenchangingafieldon`mail.message`,thistriggersthemodificationofthesamefieldon`mail.mail`
    #Bysettinguptheinverseone2many,weavoidtohavetodoasearchtofindthemailslinkedtothe`mail.message`
    #asthecachevalueforthisinverseone2manyisup-to-date.
    #Besidesfornewmessages,andmessagesneversendingemails,therewasnomail,anditwassearchingfornothing.
    mail_ids=fields.One2many('mail.mail','mail_message_id',string='Mails',groups="base.group_system")
    canned_response_ids=fields.One2many('mail.shortcode','message_ids',string="CannedResponses",store=False)

    def_compute_description(self):
        formessageinself:
            ifmessage.subject:
                message.description=message.subject
            else:
                plaintext_ct=''ifnotmessage.bodyelsetools.html2plaintext(message.body)
                message.description=plaintext_ct[:30]+'%s'%('[...]'iflen(plaintext_ct)>=30else'')

    def_get_needaction(self):
        """Needactiononamail.message=notifiedonmychannel"""
        my_messages=self.env['mail.notification'].sudo().search([
            ('mail_message_id','in',self.ids),
            ('res_partner_id','=',self.env.user.partner_id.id),
            ('is_read','=',False)]).mapped('mail_message_id')
        formessageinself:
            message.needaction=messageinmy_messages

    @api.model
    def_search_needaction(self,operator,operand):
        is_read=Falseifoperator=='='andoperandelseTrue
        notification_ids=self.env['mail.notification']._search([('res_partner_id','=',self.env.user.partner_id.id),('is_read','=',is_read)])
        return[('notification_ids','in',notification_ids)]

    def_compute_has_error(self):
        error_from_notification=self.env['mail.notification'].sudo().search([
            ('mail_message_id','in',self.ids),
            ('notification_status','in',('bounce','exception'))]).mapped('mail_message_id')
        formessageinself:
            message.has_error=messageinerror_from_notification

    def_search_has_error(self,operator,operand):
        ifoperator=='='andoperand:
            return[('notification_ids.notification_status','in',('bounce','exception'))]
        return['!',('notification_ids.notification_status','in',('bounce','exception'))] #thiswontworkandwillbeequivalentto"notin"beacauseoformrestrictions.Dontuse"has_error=False"

    @api.depends('starred_partner_ids')
    @api.depends_context('uid')
    def_get_starred(self):
        """Computeifthemessageisstarredbythecurrentuser."""
        #TDEFIXME:useSQL
        starred=self.sudo().filtered(lambdamsg:self.env.user.partner_idinmsg.starred_partner_ids)
        formessageinself:
            message.starred=messageinstarred

    @api.model
    def_search_starred(self,operator,operand):
        ifoperator=='='andoperand:
            return[('starred_partner_ids','in',[self.env.user.partner_id.id])]
        return[('starred_partner_ids','notin',[self.env.user.partner_id.id])]

    def_compute_need_moderation(self):
        formessageinself:
            message.need_moderation=False

    @api.model
    def_search_need_moderation(self,operator,operand):
        ifoperator=='='andoperandisTrue:
            return['&','&',
                    ('moderation_status','=','pending_moderation'),
                    ('model','=','mail.channel'),
                    ('res_id','in',self.env.user.moderation_channel_ids.ids)]

        #nosupportforotheroperators
        raiseUserError(_('Unsupportedsearchfilteronmoderationstatus'))

    #------------------------------------------------------
    #CRUD/ORM
    #------------------------------------------------------

    definit(self):
        self._cr.execute("""SELECTindexnameFROMpg_indexesWHEREindexname='mail_message_model_res_id_idx'""")
        ifnotself._cr.fetchone():
            self._cr.execute("""CREATEINDEXmail_message_model_res_id_idxONmail_message(model,res_id)""")

    @api.model
    def_search(self,args,offset=0,limit=None,order=None,count=False,access_rights_uid=None):
        """Overridethataddsspecificaccessrightsofmail.message,toremove
        idsuidcouldnotseeaccordingtoourcustomrules.Pleasereferto
        check_access_ruleformoredetailsaboutthoserules.

        Nonemployeesusersseeonlymessagewithsubtype(akadonotsee
        internallogs).

        Afterhavingreceivedidsofaclassicsearch,keeponly:
        -ifauthor_id==pid,uidistheauthor,OR
        -uidbelongstoanotifiedchannel,OR
        -uidisinthespecifiedrecipients,OR
        -uidhasanotificationonthemessage
        -otherwise:removetheid
        """
        #Rulesdonotapplytoadministrator
        ifself.env.is_superuser():
            returnsuper(Message,self)._search(
                args,offset=offset,limit=limit,order=order,
                count=count,access_rights_uid=access_rights_uid)
        #Non-employeeseeonlymessageswithasubtypeandnotinternal
        ifnotself.env['res.users'].has_group('base.group_user'):
            args=expression.AND([self._get_search_domain_share(),args])
        #PerformasuperwithcountasFalse,tohavetheids,notacounter
        ids=super(Message,self)._search(
            args,offset=offset,limit=limit,order=order,
            count=False,access_rights_uid=access_rights_uid)
        ifnotidsandcount:
            return0
        elifnotids:
            returnids

        pid=self.env.user.partner_id.id
        author_ids,partner_ids,channel_ids,allowed_ids=set([]),set([]),set([]),set([])
        model_ids={}

        #checkreadaccessrightsbeforecheckingtheactualrulesonthegivenids
        super(Message,self.with_user(access_rights_uidorself._uid)).check_access_rights('read')

        self.flush(['model','res_id','author_id','message_type','partner_ids','channel_ids'])
        self.env['mail.notification'].flush(['mail_message_id','res_partner_id'])
        self.env['mail.channel'].flush(['channel_message_ids'])
        self.env['mail.channel.partner'].flush(['channel_id','partner_id'])
        forsub_idsinself._cr.split_for_in_conditions(ids):
            self._cr.execute("""
                SELECTDISTINCTm.id,m.model,m.res_id,m.author_id,m.message_type,
                                COALESCE(partner_rel.res_partner_id,needaction_rel.res_partner_id),
                                channel_partner.channel_idaschannel_id
                FROM"%s"m
                LEFTJOIN"mail_message_res_partner_rel"partner_rel
                ONpartner_rel.mail_message_id=m.idANDpartner_rel.res_partner_id=%%(pid)s
                LEFTJOIN"mail_message_res_partner_needaction_rel"needaction_rel
                ONneedaction_rel.mail_message_id=m.idANDneedaction_rel.res_partner_id=%%(pid)s
                LEFTJOIN"mail_message_mail_channel_rel"channel_rel
                ONchannel_rel.mail_message_id=m.id
                LEFTJOIN"mail_channel"channel
                ONchannel.id=channel_rel.mail_channel_id
                LEFTJOIN"mail_channel_partner"channel_partner
                ONchannel_partner.channel_id=channel.idANDchannel_partner.partner_id=%%(pid)s

                WHEREm.id=ANY(%%(ids)s)"""%self._table,dict(pid=pid,ids=list(sub_ids)))
            forid,rmod,rid,author_id,message_type,partner_id,channel_idinself._cr.fetchall():
                ifauthor_id==pid:
                    author_ids.add(id)
                elifpartner_id==pid:
                    partner_ids.add(id)
                elifchannel_id:
                    channel_ids.add(id)
                elifrmodandridandmessage_type!='user_notification':
                    model_ids.setdefault(rmod,{}).setdefault(rid,set()).add(id)

        allowed_ids=self._find_allowed_doc_ids(model_ids)

        final_ids=author_ids|partner_ids|channel_ids|allowed_ids

        ifcount:
            returnlen(final_ids)
        else:
            #re-constructalistbasedonids,becausesetdidnotkeeptheoriginalorder
            id_list=[idforidinidsifidinfinal_ids]
            returnid_list

    @api.model
    def_find_allowed_model_wise(self,doc_model,doc_dict):
        doc_ids=list(doc_dict)
        allowed_doc_ids=self.env[doc_model].with_context(active_test=False).search([('id','in',doc_ids)]).ids
        returnset([message_idforallowed_doc_idinallowed_doc_idsformessage_idindoc_dict[allowed_doc_id]])

    @api.model
    def_find_allowed_doc_ids(self,model_ids):
        IrModelAccess=self.env['ir.model.access']
        allowed_ids=set()
        fordoc_model,doc_dictinmodel_ids.items():
            ifnotIrModelAccess.check(doc_model,'read',False):
                continue
            allowed_ids|=self._find_allowed_model_wise(doc_model,doc_dict)
        returnallowed_ids

    defcheck_access_rule(self,operation):
        """Accessrulesofmail.message:
            -read:if
                -author_id==pid,uidistheauthorOR
                -uidisintherecipients(partner_ids)OR
                -uidhasbeennotified(needaction)OR
                -uidismemberofalisternchannel(channel_ids.partner_ids)OR
                -uidhavereadaccesstotherelateddocumentifmodel,res_id
                -otherwise:raise
            -create:if
                -nomodel,nores_id(privatemessage)OR
                -pidinmessage_follower_idsifmodel,res_idOR
                -uidcanreadtheparentOR
                -uidhavewriteorcreateaccessontherelateddocumentifmodel,res_id,OR
                -otherwise:raise
            -write:if
                -author_id==pid,uidistheauthor,OR
                -uidisintherecipients(partner_ids)OR
                -uidismoderatorofthechannelandmoderation_statusispending_moderationOR
                -uidhaswriteorcreateaccessontherelateddocumentifmodel,res_idandmoderation_statusisnotpending_moderation
                -otherwise:raise
            -unlink:if
                -uidismoderatorofthechannelandmoderation_statusispending_moderationOR
                -uidhaswriteorcreateaccessontherelateddocumentifmodel,res_idandmoderation_statusisnotpending_moderation
                -otherwise:raise

        Specificcase:nonemployeeusersseeonlymessageswithsubtype(akado
        notseeinternallogs).
        """
        def_generate_model_record_ids(msg_val,msg_ids):
            """:parammodel_record_ids:{'model':{'res_id':(msg_id,msg_id)},...}
                :parammessage_values:{'msg_id':{'model':..,'res_id':..,'author_id':..}}
            """
            model_record_ids={}
            foridinmsg_ids:
                vals=msg_val.get(id,{})
                ifvals.get('model')andvals.get('res_id'):
                    model_record_ids.setdefault(vals['model'],set()).add(vals['res_id'])
            returnmodel_record_ids

        ifself.env.is_superuser():
            return
        #Nonemployeesseeonlymessageswithasubtype(aka,notinternallogs)
        ifnotself.env['res.users'].has_group('base.group_user'):
            self._cr.execute('''SELECTDISTINCTmessage.id,message.subtype_id,subtype.internal
                                FROM"%s"ASmessage
                                LEFTJOIN"mail_message_subtype"assubtype
                                ONmessage.subtype_id=subtype.id
                                WHEREmessage.message_type=%%sAND
                                    (message.is_internalISTRUEORmessage.subtype_idISNULLORsubtype.internalISTRUE)AND
                                    message.id=ANY(%%s)'''%(self._table),('comment',self.ids,))
            ifself._cr.fetchall():
                raiseAccessError(
                    _('Therequestedoperationcannotbecompletedduetosecurityrestrictions.Pleasecontactyoursystemadministrator.\n\n(Documenttype:%s,Operation:%s)',self._description,operation)
                    +'-({}{},{}{})'.format(_('Records:'),self.ids[:6],_('User:'),self._uid)
                )

        #Readmail_message.idstohavetheirvalues
        message_values=dict((message_id,{})formessage_idinself.ids)

        self.flush(['model','res_id','author_id','parent_id','moderation_status','message_type','partner_ids','channel_ids'])
        self.env['mail.notification'].flush(['mail_message_id','res_partner_id'])
        self.env['mail.channel'].flush(['channel_message_ids','moderator_ids'])
        self.env['mail.channel.partner'].flush(['channel_id','partner_id'])
        self.env['res.users'].flush(['moderation_channel_ids'])

        ifoperation=='read':
            self._cr.execute("""
                SELECTDISTINCTm.id,m.model,m.res_id,m.author_id,m.parent_id,
                                COALESCE(partner_rel.res_partner_id,needaction_rel.res_partner_id),
                                channel_partner.channel_idaschannel_id,m.moderation_status,
                                m.message_typeasmessage_type
                FROM"%s"m
                LEFTJOIN"mail_message_res_partner_rel"partner_rel
                ONpartner_rel.mail_message_id=m.idANDpartner_rel.res_partner_id=%%(pid)s
                LEFTJOIN"mail_message_res_partner_needaction_rel"needaction_rel
                ONneedaction_rel.mail_message_id=m.idANDneedaction_rel.res_partner_id=%%(pid)s
                LEFTJOIN"mail_message_mail_channel_rel"channel_rel
                ONchannel_rel.mail_message_id=m.id
                LEFTJOIN"mail_channel"channel
                ONchannel.id=channel_rel.mail_channel_id
                LEFTJOIN"mail_channel_partner"channel_partner
                ONchannel_partner.channel_id=channel.idANDchannel_partner.partner_id=%%(pid)s
                WHEREm.id=ANY(%%(ids)s)"""%self._table,dict(pid=self.env.user.partner_id.id,ids=self.ids))
            formid,rmod,rid,author_id,parent_id,partner_id,channel_id,moderation_status,message_typeinself._cr.fetchall():
                message_values[mid]={
                    'model':rmod,
                    'res_id':rid,
                    'author_id':author_id,
                    'parent_id':parent_id,
                    'moderation_status':moderation_status,
                    'moderator_id':False,
                    'notified':any((message_values[mid].get('notified'),partner_id,channel_id)),
                    'message_type':message_type,
                }
        elifoperation=='write':
            self._cr.execute("""
                SELECTDISTINCTm.id,m.model,m.res_id,m.author_id,m.parent_id,m.moderation_status,
                                COALESCE(partner_rel.res_partner_id,needaction_rel.res_partner_id),
                                channel_partner.channel_idaschannel_id,channel_moderator_rel.res_users_idasmoderator_id,
                                m.message_typeasmessage_type
                FROM"%s"m
                LEFTJOIN"mail_message_res_partner_rel"partner_rel
                ONpartner_rel.mail_message_id=m.idANDpartner_rel.res_partner_id=%%(pid)s
                LEFTJOIN"mail_message_res_partner_needaction_rel"needaction_rel
                ONneedaction_rel.mail_message_id=m.idANDneedaction_rel.res_partner_id=%%(pid)s
                LEFTJOIN"mail_message_mail_channel_rel"channel_rel
                ONchannel_rel.mail_message_id=m.id
                LEFTJOIN"mail_channel"channel
                ONchannel.id=channel_rel.mail_channel_id
                LEFTJOIN"mail_channel_partner"channel_partner
                ONchannel_partner.channel_id=channel.idANDchannel_partner.partner_id=%%(pid)s
                LEFTJOIN"mail_channel"moderated_channel
                ONm.moderation_status='pending_moderation'ANDm.res_id=moderated_channel.id
                LEFTJOIN"mail_channel_moderator_rel"channel_moderator_rel
                ONchannel_moderator_rel.mail_channel_id=moderated_channel.idANDchannel_moderator_rel.res_users_id=%%(uid)s
                WHEREm.id=ANY(%%(ids)s)"""%self._table,dict(pid=self.env.user.partner_id.id,uid=self.env.user.id,ids=self.ids))
            formid,rmod,rid,author_id,parent_id,moderation_status,partner_id,channel_id,moderator_id,message_typeinself._cr.fetchall():
                message_values[mid]={
                    'model':rmod,
                    'res_id':rid,
                    'author_id':author_id,
                    'parent_id':parent_id,
                    'moderation_status':moderation_status,
                    'moderator_id':moderator_id,
                    'notified':any((message_values[mid].get('notified'),partner_id,channel_id)),
                    'message_type':message_type,
                }
        elifoperation=='create':
            self._cr.execute("""SELECTDISTINCTid,model,res_id,author_id,parent_id,moderation_status,message_typeFROM"%s"WHEREid=ANY(%%s)"""%self._table,(self.ids,))
            formid,rmod,rid,author_id,parent_id,moderation_status,message_typeinself._cr.fetchall():
                message_values[mid]={
                    'model':rmod,
                    'res_id':rid,
                    'author_id':author_id,
                    'parent_id':parent_id,
                    'moderation_status':moderation_status,
                    'moderator_id':False,
                    'message_type':message_type,
                }
        else: #unlink
            self._cr.execute("""SELECTDISTINCTm.id,m.model,m.res_id,m.author_id,m.parent_id,m.moderation_status,channel_moderator_rel.res_users_idasmoderator_id,m.message_typeasmessage_type
                FROM"%s"m
                LEFTJOIN"mail_channel"moderated_channel
                ONm.moderation_status='pending_moderation'ANDm.res_id=moderated_channel.id
                LEFTJOIN"mail_channel_moderator_rel"channel_moderator_rel
                ONchannel_moderator_rel.mail_channel_id=moderated_channel.idANDchannel_moderator_rel.res_users_id=(%%s)
                WHEREm.id=ANY(%%s)"""%self._table,(self.env.user.id,self.ids,))
            formid,rmod,rid,author_id,parent_id,moderation_status,moderator_id,message_typeinself._cr.fetchall():
                message_values[mid]={
                    'model':rmod,
                    'res_id':rid,
                    'author_id':author_id,
                    'parent_id':parent_id,
                    'moderation_status':moderation_status,
                    'moderator_id':moderator_id,
                    'message_type':message_type,
                }

        #Authorcondition(READ,WRITE,CREATE(private))
        author_ids=[]
        ifoperation=='read':
            author_ids=[midformid,messageinmessage_values.items()
                          ifmessage.get('author_id')andmessage.get('author_id')==self.env.user.partner_id.id]
        elifoperation=='write':
            author_ids=[midformid,messageinmessage_values.items()
                          ifmessage.get('moderation_status')!='pending_moderation'andmessage.get('author_id')==self.env.user.partner_id.id]
        elifoperation=='create':
            author_ids=[midformid,messageinmessage_values.items()
                          ifnotself.is_thread_message(message)]

        #Moderatorcondition:allowtoWRITE,UNLINKifmoderatorofapendingmessage
        moderator_ids=[]
        ifoperationin['write','unlink']:
            moderator_ids=[midformid,messageinmessage_values.items()ifmessage.get('moderator_id')]
        messages_to_check=self.ids
        messages_to_check=set(messages_to_check).difference(set(author_ids),set(moderator_ids))
        ifnotmessages_to_check:
            return

        #Recipientscondition,forreadandwrite(partner_ids)
        #keepontop,usefullforsystraynotifications
        notified_ids=[]
        model_record_ids=_generate_model_record_ids(message_values,messages_to_check)
        ifoperationin['read','write']:
            notified_ids=[midformid,messageinmessage_values.items()ifmessage.get('notified')]

        messages_to_check=set(messages_to_check).difference(set(notified_ids))
        ifnotmessages_to_check:
            return

        #CRUD:Accessrightsrelatedtothedocument
        document_related_ids=[]
        document_related_candidate_ids=[midformid,messageinmessage_values.items()
                if(message.get('model')andmessage.get('res_id')and
                    message.get('message_type')!='user_notification'and
                    (message.get('moderation_status')!='pending_moderation'oroperationnotin['write','unlink']))]
        model_record_ids=_generate_model_record_ids(message_values,document_related_candidate_ids)
        formodel,doc_idsinmodel_record_ids.items():
            DocumentModel=self.env[model]
            ifhasattr(DocumentModel,'_get_mail_message_access'):
                check_operation=DocumentModel._get_mail_message_access(doc_ids,operation) ##whynotgivingmodelhere?
            else:
                check_operation=self.env['mail.thread']._get_mail_message_access(doc_ids,operation,model_name=model)
            records=DocumentModel.browse(doc_ids)
            records.check_access_rights(check_operation)
            mids=records.browse(doc_ids)._filter_access_rules(check_operation)
            document_related_ids+=[
                midformid,messageinmessage_values.items()
                if(message.get('model')==modeland
                    message.get('res_id')inmids.idsand
                    message.get('message_type')!='user_notification'and
                    (message.get('moderation_status')!='pending_moderation'or
                    operationnotin['write','unlink']))]

        messages_to_check=messages_to_check.difference(set(document_related_ids))

        ifnotmessages_to_check:
            return

        #Parentcondition,forcreate(checkforreceivednotificationsforthecreatedmessageparent)
        notified_ids=[]
        ifoperation=='create':
            #TDE:probablycleanme
            parent_ids=[message.get('parent_id')formessageinmessage_values.values()
                          ifmessage.get('parent_id')]
            self._cr.execute("""SELECTDISTINCTm.id,partner_rel.res_partner_id,channel_partner.partner_idFROM"%s"m
                LEFTJOIN"mail_message_res_partner_rel"partner_rel
                ONpartner_rel.mail_message_id=m.idANDpartner_rel.res_partner_id=(%%s)
                LEFTJOIN"mail_message_mail_channel_rel"channel_rel
                ONchannel_rel.mail_message_id=m.id
                LEFTJOIN"mail_channel"channel
                ONchannel.id=channel_rel.mail_channel_id
                LEFTJOIN"mail_channel_partner"channel_partner
                ONchannel_partner.channel_id=channel.idANDchannel_partner.partner_id=(%%s)
                WHEREm.id=ANY(%%s)"""%self._table,(self.env.user.partner_id.id,self.env.user.partner_id.id,parent_ids,))
            not_parent_ids=[mid[0]formidinself._cr.fetchall()ifany([mid[1],mid[2]])]
            notified_ids+=[midformid,messageinmessage_values.items()
                             ifmessage.get('parent_id')innot_parent_ids]

        messages_to_check=messages_to_check.difference(set(notified_ids))
        ifnotmessages_to_check:
            return

        #Recipientsconditionforcreate(message_follower_ids)
        ifoperation=='create':
            fordoc_model,doc_idsinmodel_record_ids.items():
                followers=self.env['mail.followers'].sudo().search([
                    ('res_model','=',doc_model),
                    ('res_id','in',list(doc_ids)),
                    ('partner_id','=',self.env.user.partner_id.id),
                    ])
                fol_mids=[follower.res_idforfollowerinfollowers]
                notified_ids+=[midformid,messageinmessage_values.items()
                                 ifmessage.get('model')==doc_modeland
                                 message.get('res_id')infol_midsand
                                 message.get('message_type')!='user_notification'
                                 ]

        messages_to_check=messages_to_check.difference(set(notified_ids))
        ifnotmessages_to_check:
            return

        ifnotself.browse(messages_to_check).exists():
            return
        raiseAccessError(
            _('Therequestedoperationcannotbecompletedduetosecurityrestrictions.Pleasecontactyoursystemadministrator.\n\n(Documenttype:%s,Operation:%s)',self._description,operation)
            +'-({}{},{}{})'.format(_('Records:'),list(messages_to_check)[:6],_('User:'),self._uid)
        )

    @api.model_create_multi
    defcreate(self,values_list):
        tracking_values_list=[]
        forvaluesinvalues_list:
            if'email_from'notinvalues: #neededtocomputereply_to
                author_id,email_from=self.env['mail.thread']._message_compute_author(values.get('author_id'),email_from=None,raise_exception=False)
                values['email_from']=email_from
            ifnotvalues.get('message_id'):
                values['message_id']=self._get_message_id(values)
            if'reply_to'notinvalues:
                values['reply_to']=self._get_reply_to(values)
            if'record_name'notinvaluesand'default_record_name'notinself.env.context:
                values['record_name']=self._get_record_name(values)

            if'attachment_ids'notinvalues:
                values['attachment_ids']=[]
            #extractbase64images
            if'body'invalues:
                Attachments=self.env['ir.attachment'].with_context(clean_context(self._context))
                data_to_url={}
                defbase64_to_boundary(match):
                    key=match.group(2)
                    ifnotdata_to_url.get(key):
                        name=match.group(4)ifmatch.group(4)else'image%s'%len(data_to_url)
                        try:
                            attachment=Attachments.create({
                                'name':name,
                                'datas':match.group(2),
                                'res_model':values.get('model'),
                                'res_id':values.get('res_id'),
                            })
                        exceptbinascii_error:
                            _logger.warning("Impossibletocreateanattachmentoutofbadlyformatedbase64embeddedimage.Imagehasbeenremoved.")
                            returnmatch.group(3) #group(3)istheurlendingsingle/doublequotematchedbytheregexp
                        else:
                            attachment.generate_access_token()
                            values['attachment_ids'].append((4,attachment.id))
                            data_to_url[key]=['/web/image/%s?access_token=%s'%(attachment.id,attachment.access_token),name]
                    return'%s%salt="%s"'%(data_to_url[key][0],match.group(3),data_to_url[key][1])
                values['body']=_image_dataurl.sub(base64_to_boundary,tools.ustr(values['body']))

            #delegatecreationoftrackingafterthecreateassudotoavoidaccessrightsissues
            tracking_values_list.append(values.pop('tracking_value_ids',False))

        messages=super(Message,self).create(values_list)

        check_attachment_access=[]
        ifall(isinstance(command,int)orcommand[0]in(4,6)forvaluesinvalues_listforcommandinvalues.get('attachment_ids')):
            forvaluesinvalues_list:
                forcommandinvalues.get('attachment_ids'):
                    ifisinstance(command,int):
                        check_attachment_access+=[command]
                    elifcommand[0]==6:
                        check_attachment_access+=command[2]
                    else: #command[0]==4:
                        check_attachment_access+=[command[1]]
        else:
            check_attachment_access=messages.mapped('attachment_ids').ids #fallbackonreadifanyunknowcommand
        ifcheck_attachment_access:
            self.env['ir.attachment'].browse(check_attachment_access).check(mode='read')

        formessage,values,tracking_values_cmdinzip(messages,values_list,tracking_values_list):
            iftracking_values_cmd:
                vals_lst=[dict(cmd[2],mail_message_id=message.id)forcmdintracking_values_cmdiflen(cmd)==3andcmd[0]==0]
                other_cmd=[cmdforcmdintracking_values_cmdiflen(cmd)!=3orcmd[0]!=0]
                ifvals_lst:
                    self.env['mail.tracking.value'].sudo().create(vals_lst)
                ifother_cmd:
                    message.sudo().write({'tracking_value_ids':tracking_values_cmd})

            ifmessage.is_thread_message(values):
                message._invalidate_documents(values.get('model'),values.get('res_id'))

        returnmessages

    defread(self,fields=None,load='_classic_read'):
        """Overridetoexplicitelycallcheck_access_rule,thatisnotcalled
            bytheORM.Itinsteaddirectlyfetchesir.rulesandapplythem."""
        self.check_access_rule('read')
        returnsuper(Message,self).read(fields=fields,load=load)

    defwrite(self,vals):
        record_changed='model'invalsor'res_id'invals
        ifrecord_changedor'message_type'invals:
            self._invalidate_documents()
        res=super(Message,self).write(vals)
        ifvals.get('attachment_ids'):
            formailinself:
                mail.attachment_ids.check(mode='read')
        if'notification_ids'invalsorrecord_changed:
            self._invalidate_documents()
        returnres

    defunlink(self):
        #cascade-deleteattachmentsthataredirectlyattachedtothemessage(shouldonlyhappen
        #formail.messagesthatactasparentforastandalonemail.mailrecord).
        ifnotself:
            returnTrue
        self.check_access_rule('unlink')
        self.mapped('attachment_ids').filtered(
            lambdaattach:attach.res_model==self._nameand(attach.res_idinself.idsorattach.res_id==0)
        ).unlink()
        foreleminself:
            ifelem.is_thread_message():
                elem._invalidate_documents()
        returnsuper(Message,self).unlink()

    @api.model
    def_read_group_raw(self,domain,fields,groupby,offset=0,limit=None,orderby=False,lazy=True):
        ifnotself.env.is_admin():
            raiseAccessError(_("Onlyadministratorsareallowedtousegroupedreadonmessagemodel"))

        returnsuper(Message,self)._read_group_raw(
            domain=domain,fields=fields,groupby=groupby,offset=offset,
            limit=limit,orderby=orderby,lazy=lazy,
        )

    defexport_data(self,fields_to_export):
        ifnotself.env.is_admin():
            raiseAccessError(_("Onlyadministratorsareallowedtoexportmailmessage"))

        returnsuper(Message,self).export_data(fields_to_export)

    #------------------------------------------------------
    #DISCUSSAPI
    #------------------------------------------------------

    @api.model
    defmark_all_as_read(self,domain=None):
        #notreallyefficientmethod:itdoesonedbrequestforthe
        #search,andoneforeachmessageintheresultsetis_readtoTrueinthe
        #currentnotificationsfromtherelation.
        partner_id=self.env.user.partner_id.id
        notif_domain=[
            ('res_partner_id','=',partner_id),
            ('is_read','=',False)]
        ifdomain:
            messages=self.search(domain)
            messages.set_message_done()
            returnmessages.ids

        notifications=self.env['mail.notification'].sudo().search(notif_domain)
        notifications.write({'is_read':True})

        ids=[n['mail_message_id']forninnotifications.read(['mail_message_id'])]

        notification={'type':'mark_as_read','message_ids':[id[0]foridinids],'needaction_inbox_counter':self.env.user.partner_id.get_needaction_count()}
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',partner_id),notification)

        returnids

    defset_message_done(self):
        """Removetheneedactionfrommessagesforthecurrentpartner."""
        partner_id=self.env.user.partner_id

        notifications=self.env['mail.notification'].sudo().search([
            ('mail_message_id','in',self.ids),
            ('res_partner_id','=',partner_id.id),
            ('is_read','=',False)])

        ifnotnotifications:
            return

        #notifieschangesinmessagesthroughthebus. Tominimizethenumberof
        #notifications,weneedtogroupthemessagesdependingontheirchannel_ids
        groups=[]
        messages=notifications.mapped('mail_message_id')
        current_channel_ids=messages[0].channel_ids
        current_group=[]
        forrecordinmessages:
            ifrecord.channel_ids==current_channel_ids:
                current_group.append(record.id)
            else:
                groups.append((current_group,current_channel_ids))
                current_group=[record.id]
                current_channel_ids=record.channel_ids

        groups.append((current_group,current_channel_ids))
        current_group=[record.id]
        current_channel_ids=record.channel_ids

        notifications.write({'is_read':True})

        for(msg_ids,channel_ids)ingroups:
            #channel_idsinresultisdeprecatedandwillberemovedinafutureversion
            notification={'type':'mark_as_read','message_ids':msg_ids,'channel_ids':[c.idforcinchannel_ids],'needaction_inbox_counter':self.env.user.partner_id.get_needaction_count()}
            self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',partner_id.id),notification)

    @api.model
    defunstar_all(self):
        """Unstarmessagesforthecurrentpartner."""
        partner_id=self.env.user.partner_id.id

        starred_messages=self.search([('starred_partner_ids','in',partner_id)])
        starred_messages.write({'starred_partner_ids':[(3,partner_id)]})

        ids=[m.idforminstarred_messages]
        notification={'type':'toggle_star','message_ids':ids,'starred':False}
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),notification)

    deftoggle_message_starred(self):
        """Togglemessagesas(un)starred.Technically,thenotificationsrelated
            touidaresetto(un)starred.
        """
        #ausershouldalwaysbeabletostaramessagehecanread
        self.check_access_rule('read')
        starred=notself.starred
        ifstarred:
            self.sudo().write({'starred_partner_ids':[(4,self.env.user.partner_id.id)]})
        else:
            self.sudo().write({'starred_partner_ids':[(3,self.env.user.partner_id.id)]})

        notification={'type':'toggle_star','message_ids':[self.id],'starred':starred}
        self.env['bus.bus'].sendone((self._cr.dbname,'res.partner',self.env.user.partner_id.id),notification)

    #--------------------------------------------------
    #MODERATIONAPI
    #--------------------------------------------------

    defmoderate(self,decision,**kwargs):
        """Moderatemessages.Acheckisdoneonmoderationstatusofthe
        currentusertoensureweonlymoderatevalidmessages."""
        moderated_channels=self.env.user.moderation_channel_ids
        to_moderate=[message.idformessageinself
                       ifmessage.model=='mail.channel'and
                       message.res_idinmoderated_channels.idsand
                       message.moderation_status=='pending_moderation']
        ifto_moderate:
            self.browse(to_moderate)._moderate(decision,**kwargs)

    def_moderate(self,decision,**kwargs):
        """:paramdecision
                 *accept      -moderatemessageandbroadcastthatmessagetofollowersofrelevantchannels.
                 *reject      -messagewillbedeletedfromthedatabasewithoutbroadcast
                                  anemailsenttotheauthorwithanexplanationthatthemoderatorscanedit.
                 *discard     -messagewillbedeletedfromthedatabasewithoutbroadcast.
                 *allow       -addemailaddresstowhitelistpeopleofspecificchannel,
                                  sothatnexttimeifamessagecomefromsameemailaddressonsamechannel,
                                  itwillbeautomaticallybroadcastedtorelevantchannelswithoutanyapprovalfrommoderator.
                 *ban         -addemailaddresstoblacklistofemailsforthespecificchannel.
                                  Fromnexttime,apersonsendingamessageusingthatemailaddresswillnotneedmoderation.
                                  message_postwillnotcreatemessageswiththecorrespondingexpeditor.
        """
        ifdecision=='accept':
            self._moderate_accept()
        elifdecision=='reject':
            self._moderate_send_reject_email(kwargs.get('title'),kwargs.get('comment'))
            self._moderate_discard()
        elifdecision=='discard':
            self._moderate_discard()
        elifdecision=='allow':
            channels=self.env['mail.channel'].browse(self.mapped('res_id'))
            forchannelinchannels:
                channel._update_moderation_email(
                    list({message.email_fromformessageinselfifmessage.res_id==channel.id}),
                    'allow'
                )
            self._search_from_same_authors()._moderate_accept()
        elifdecision=='ban':
            channels=self.env['mail.channel'].browse(self.mapped('res_id'))
            forchannelinchannels:
                channel._update_moderation_email(
                    list({message.email_fromformessageinselfifmessage.res_id==channel.id}),
                    'ban'
                )
            self._search_from_same_authors()._moderate_discard()

    def_moderate_accept(self):
        self.write({
            'moderation_status':'accepted',
            'moderator_id':self.env.uid
        })
        #proceedwithnotificationprocesstosendnotificationemailsandInboxmessages
        formessageinself:
            ifmessage.is_thread_message():#note,sincewewillonlyintercept_notify_threadformessagepostedonchannel,
                #messagewillalwaysbeathread_message.Thischeckshouldalwaysbetrue.
                self.env[message.model].browse(message.res_id)._notify_thread(message)

    def_moderate_send_reject_email(self,subject,comment):
        formsginself:
            ifnotmsg.email_from:
                continue
            body_html=tools.append_content_to_html('<div>%s</div>'%tools.ustr(comment),msg.body,plaintext=False)
            vals={
                'subject':subject,
                'body_html':body_html,
                'author_id':self.env.user.partner_id.id,
                'email_from':self.env.user.email_formattedorself.env.company.catchall_formatted,
                'email_to':msg.email_from,
                'auto_delete':True,
                'state':'outgoing'
            }
            self.env['mail.mail'].sudo().create(vals)

    def_search_from_same_authors(self):
        """Returnsallpendingmoderationmessagesthathavesameemail_fromand
        sameres_idasgivenrecordset."""
        messages=self.env['mail.message'].sudo()
        formessageinself:
            messages|=messages.search([
                ('moderation_status','=','pending_moderation'),
                ('email_from','=',message.email_from),
                ('model','=','mail.channel'),
                ('res_id','=',message.res_id)
            ])
        returnmessages

    def_moderate_discard(self):
        """Notifydeletionofmessagestotheirmoderatorsandauthorsandthendeletethem.
        """
        channel_ids=self.mapped('res_id')
        moderators=self.env['mail.channel'].browse(channel_ids).mapped('moderator_ids')
        authors=self.mapped('author_id')
        partner_to_pid={}
        formoderatorinmoderators:
            partner_to_pid.setdefault(moderator.partner_id.id,set())
            partner_to_pid[moderator.partner_id.id]|=set([message.idformessageinselfifmessage.res_idinmoderator.moderation_channel_ids.ids])
        forauthorinauthors:
            partner_to_pid.setdefault(author.id,set())
            partner_to_pid[author.id]|=set([message.idformessageinselfifmessage.author_id==author])

        notifications=[]
        forpartner_id,message_idsinpartner_to_pid.items():
            notifications.append([
                (self._cr.dbname,'res.partner',partner_id),
                {'type':'deletion','message_ids':sorted(list(message_ids))} #sortedtomakedeterministicfortests
            ])
        self.env['bus.bus'].sendmany(notifications)
        self.unlink()

    def_notify_pending_by_chat(self):
        """Generatethebusnotificationsforthegivenmessageandsendthem
        totheappropriatemoderatorsandtheauthor(iftheauthorhasnotbeen
        electedmoderatormeanwhile).Theauthornotificationcanbeconsidered
        asafeedbacktotheauthor.
        """
        self.ensure_one()
        message=self.message_format()[0]
        partners=self.env['mail.channel'].browse(self.res_id).mapped('moderator_ids.partner_id')
        notifications=[]
        forpartnerinpartners:
            notifications.append([
                (self._cr.dbname,'res.partner',partner.id),
                {'type':'moderator','message':message}
            ])
        ifself.author_idnotinpartners:
            notifications.append([
                (self._cr.dbname,'res.partner',self.author_id.id),
                {'type':'author','message':message}
            ])
        self.env['bus.bus'].sendmany(notifications)

    @api.model
    def_notify_moderators(self):
        """Pushanotification(Inbox/email)tomoderatorshavingmessages
        waitingformoderation.Thismethodiscalledonceadaybyacron.
        """
        channels=self.env['mail.channel'].browse(self.search([('moderation_status','=','pending_moderation')]).mapped('res_id'))
        moderators_to_notify=channels.mapped('moderator_ids')
        template=self.env.ref('mail.mail_channel_notify_moderation',raise_if_not_found=False)
        ifnottemplate:
            _logger.warning('Template"mail.mail_channel_notify_moderation"wasnotfound.Cannotsendremindernotifications.')
            return
        MailThread=self.env['mail.thread'].with_context(mail_notify_author=True)
        formoderatorinmoderators_to_notify:
            MailThread.message_notify(
                partner_ids=moderator.partner_id.ids,
                subject=_('Messagearependingmoderation'), #tocheck:targetlanguage
                body=template._render({'record':moderator.partner_id},engine='ir.qweb',minimal_qcontext=True),
                email_from=moderator.company_id.catchall_formattedormoderator.company_id.email_formatted,
            )

    #------------------------------------------------------
    #MESSAGEREAD/FETCH/FAILUREAPI
    #------------------------------------------------------

    def_message_format(self,fnames):
        """Readsvaluesfrommessagesandformatsthemforthewebclient."""
        self.check_access_rule('read')
        vals_list=self._read_format(fnames)
        safari=requestandrequest.httprequest.user_agent.browser=='safari'

        thread_ids_by_model_name=defaultdict(set)
        formessageinself:
            ifmessage.modelandmessage.res_id:
                thread_ids_by_model_name[message.model].add(message.res_id)

        forvalsinvals_list:
            message_sudo=self.browse(vals['id']).sudo().with_prefetch(self.ids)

            #Author
            ifmessage_sudo.author_id:
                author=(message_sudo.author_id.id,message_sudo.author_id.display_name)
            else:
                author=(0,message_sudo.email_from)

            #Trackingvalues
            tracking_value_ids=[]
            fortrackinginmessage_sudo.tracking_value_ids:
                groups=tracking.field_groups
                ifnotgroupsorself.env.is_superuser()orself.user_has_groups(groups):
                    tracking_value_ids.append({
                        'id':tracking.id,
                        'changed_field':tracking.field_desc,
                        'old_value':tracking.get_old_display_value()[0],
                        'new_value':tracking.get_new_display_value()[0],
                        'field_type':tracking.field_type,
                    })

            ifmessage_sudo.modelandmessage_sudo.res_id:
                record_name=self.env[message_sudo.model]\
                    .browse(message_sudo.res_id)\
                    .sudo()\
                    .with_prefetch(thread_ids_by_model_name[message_sudo.model])\
                    .display_name
            else:
                record_name=False

            vals.update({
                'author_id':author,
                'notifications':message_sudo.notification_ids._filtered_for_web_client()._notification_format(),
                'attachment_ids':message_sudo.attachment_ids._attachment_format(),
                'tracking_value_ids':tracking_value_ids,
                'record_name':record_name,
            })

        returnvals_list

    defmessage_fetch_failed(self):
        """Returnsfirst100messages,sentbythecurrentuser,thathave
        errors,intheformatexpectedbythewebclient."""
        messages=self.search([
            ('has_error','=',True),
            ('author_id','=',self.env.user.partner_id.id),
            ('res_id','!=',0),
            ('model','!=',False),
            ('message_type','!=','user_notification')
        ],limit=100)
        returnmessages._message_notification_format()

    @api.model
    defmessage_fetch(self,domain,limit=20,moderated_channel_ids=None):
        """Getalimitedamountofformattedmessageswithprovideddomain.
            :paramdomain:thedomaintofiltermessages;
            :paramlimit:themaximumamountofmessagestoget;
            :paramlist(int)moderated_channel_ids:ifset,itcontainstheID
              ofamoderatedchannel.Fetchedmessagesshouldincludepending
              moderationmessagesformoderators.Ifthecurrentuserisnot
              moderator,itshouldstillgetself-authoredmessagesthatare
              pendingmoderation;
            :returnslist(dict).
        """
        messages=self.search(domain,limit=limit)
        ifmoderated_channel_ids:
            #Splitloadmoderatedandregularmessages,astheOReddomaincan
            #causeperformanceissuesonlargedatabases.
            moderated_messages_dom=[
                ('model','=','mail.channel'),
                ('res_id','in',moderated_channel_ids),
                '|',
                ('author_id','=',self.env.user.partner_id.id),
                ('need_moderation','=',True),
            ]
            messages|=self.search(moderated_messages_dom,limit=limit)
            #Truncatetheresultsto`limit`
            messages=messages.sorted(key='id',reverse=True)[:limit]
        returnmessages.message_format()

    defmessage_format(self):
        """Getthemessagevaluesintheformatforwebclient.Sincemessagevaluescanbebroadcasted,
            computedfieldsMUSTNOTBEREADandbroadcasted.
            :returnslist(dict).
             Example:
                {
                    'body':HTMLcontentofthemessage
                    'model':u'res.partner',
                    'record_name':u'Agrolait',
                    'attachment_ids':[
                        {
                            'file_type_icon':u'webimage',
                            'id':45,
                            'name':u'sample.png',
                            'filename':u'sample.png'
                        }
                    ],
                    'needaction_partner_ids':[],#listofpartnerids
                    'res_id':7,
                    'tracking_value_ids':[
                        {
                            'old_value':"",
                            'changed_field':"Customer",
                            'id':2965,
                            'new_value':"Axelor"
                        }
                    ],
                    'author_id':(3,u'Administrator'),
                    'email_from':'sacha@pokemon.com'#emailaddressorFalse
                    'subtype_id':(1,u'Discussions'),
                    'channel_ids':[],#listofchannelids
                    'date':'2015-06-3008:22:33',
                    'partner_ids':[[7,"SachaDuBourg-Palette"]],#listofpartnername_get
                    'message_type':u'comment',
                    'id':59,
                    'subject':False
                    'is_note':True#onlyifthemessageisanote(subtype==note)
                    'is_discussion':False#onlyifthemessageisadiscussion(subtype==discussion)
                    'is_notification':False#onlyifthemessageisanotebutisanotificationakanotlinkedtoadocumentlikeassignation
                    'moderation_status':'pending_moderation'
                }
        """
        vals_list=self._message_format(self._get_message_format_fields())

        com_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
        note_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        forvalsinvals_list:
            message_sudo=self.browse(vals['id']).sudo().with_prefetch(self.ids)
            notifs=message_sudo.notification_ids.filtered(lambdan:n.res_partner_id)
            vals.update({
                'needaction_partner_ids':notifs.filtered(lambdan:notn.is_read).res_partner_id.ids,
                'history_partner_ids':notifs.filtered(lambdan:n.is_read).res_partner_id.ids,
                'is_note':message_sudo.subtype_id.id==note_id,
                'is_discussion':message_sudo.subtype_id.id==com_id,
                'subtype_description':message_sudo.subtype_id.description,
                'is_notification':vals['message_type']=='user_notification',
            })
            ifvals['model']andself.env[vals['model']]._original_module:
                vals['module_icon']=modules.module.get_module_icon(self.env[vals['model']]._original_module)
        returnvals_list

    def_get_message_format_fields(self):
        return[
            'id','body','date','author_id','email_from', #basemessagefields
            'message_type','subtype_id','subject', #messagespecific
            'model','res_id','record_name', #documentrelated
            'channel_ids','partner_ids', #recipients
            'starred_partner_ids', #listofpartneridsforwhomthemessageisstarred
            'moderation_status',
        ]

    def_message_notification_format(self):
        """Returnsthecurrentmessagesandtheircorrespondingnotificationsin
        theformatexpectedbythewebclient.

        Notificationsholdtheinformationabouteachrecipientofamessage:if
        themessagewassuccessfullysentorifanexceptionorbounceoccurred.
        """
        return[{
            'id':message.id,
            'res_id':message.res_id,
            'model':message.model,
            'res_model_name':message.env['ir.model']._get(message.model).display_name,
            'date':message.date,
            'message_type':message.message_type,
            'notifications':message.notification_ids._filtered_for_web_client()._notification_format(),
        }formessageinself]

    def_notify_message_notification_update(self):
        """Sendbusnotificationstoupdatestatusofnotificationsintheweb
        client.Purposeistosendtheupdatedstatusperauthor."""
        messages=self.env['mail.message']
        formessageinself:
            #Checkifuserhasaccesstotherecordbeforedisplayinganotificationaboutit.
            #Incasetheuserswitchesfromonecompanytoanother,itmighthappenthathedoesn't
            #haveaccesstotherecordrelatedtothenotification.Inthiscase,weskipit.
            #YTIFIXME:checkallowed_company_idsifnecessary
            ifmessage.modelandmessage.res_id:
                record=self.env[message.model].browse(message.res_id)
                try:
                    record.check_access_rights('read')
                    record.check_access_rule('read')
                exceptAccessError:
                    continue
                else:
                    messages|=message
        updates=[[
            (self._cr.dbname,'res.partner',author.id),
            {'type':'message_notification_update','elements':self.env['mail.message'].concat(*author_messages)._message_notification_format()}
        ]forauthor,author_messagesingroupby(messages.sorted('author_id'),itemgetter('author_id'))]
        self.env['bus.bus'].sendmany(updates)

    #------------------------------------------------------
    #TOOLS
    #------------------------------------------------------

    @api.model
    def_get_record_name(self,values):
        """Returntherelateddocumentname,usingname_get.Itisdoneusing
            SUPERUSER_ID,tobesuretohavetherecordnamecorrectlystored."""
        model=values.get('model',self.env.context.get('default_model'))
        res_id=values.get('res_id',self.env.context.get('default_res_id'))
        ifnotmodelornotres_idormodelnotinself.env:
            returnFalse
        returnself.env[model].sudo().browse(res_id).display_name

    @api.model
    def_get_reply_to(self,values):
        """Returnaspecificreply_toforthedocument"""
        model=values.get('model',self._context.get('default_model'))
        res_id=values.get('res_id',self._context.get('default_res_id'))orFalse
        email_from=values.get('email_from')
        message_type=values.get('message_type')
        records=None
        ifself.is_thread_message({'model':model,'res_id':res_id,'message_type':message_type}):
            records=self.env[model].browse([res_id])
        else:
            records=self.env[model]ifmodelelseself.env['mail.thread']
        returnrecords._notify_get_reply_to(default=email_from)[res_id]

    @api.model
    def_get_message_id(self,values):
        ifvalues.get('no_auto_thread',False)isTrue:
            message_id=tools.generate_tracking_message_id('reply_to')
        elifself.is_thread_message(values):
            message_id=tools.generate_tracking_message_id('%(res_id)s-%(model)s'%values)
        else:
            message_id=tools.generate_tracking_message_id('private')
        returnmessage_id

    defis_thread_message(self,vals=None):
        ifvals:
            res_id=vals.get('res_id')
            model=vals.get('model')
            message_type=vals.get('message_type')
        else:
            self.ensure_one()
            res_id=self.res_id
            model=self.model
            message_type=self.message_type
        returnres_idandmodelandmessage_type!='user_notification'

    def_invalidate_documents(self,model=None,res_id=None):
        """Invalidatethecacheofthedocumentsfollowedby``self``."""
        forrecordinself:
            model=modelorrecord.model
            res_id=res_idorrecord.res_id
            ifmodelandissubclass(self.pool[model],self.pool['mail.thread']):
                self.env[model].invalidate_cache(fnames=[
                    'message_ids',
                    'message_unread',
                    'message_unread_counter',
                    'message_needaction',
                    'message_needaction_counter',
                ],ids=[res_id])

    def_get_search_domain_share(self):
        return['&','&',('is_internal','=',False),('subtype_id','!=',False),('subtype_id.internal','=',False)]
