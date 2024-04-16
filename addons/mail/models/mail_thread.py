#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast
importbase64
importdatetime
importdateutil
importemail
importemail.policy
importhashlib
importhmac
importlxml
importlogging
importpytz
importre
importsocket
importtime
importthreading

fromcollectionsimportnamedtuple
fromemail.messageimportEmailMessage
fromemailimportmessage_from_string,policy
fromlxmlimportetree
fromwerkzeugimporturls
fromxmlrpcimportclientasxmlrpclib

fromflectraimport_,api,exceptions,fields,models,tools,registry,SUPERUSER_ID
fromflectra.exceptionsimportMissingError
fromflectra.osvimportexpression

fromflectra.toolsimportustr
fromflectra.tools.miscimportclean_context,split_every

_logger=logging.getLogger(__name__)


classMailThread(models.AbstractModel):
    '''mail_threadmodelismeanttobeinheritedbyanymodelthatneedsto
        actasadiscussiontopiconwhichmessagescanbeattached.Public
        methodsareprefixedwith``message_``inordertoavoidname
        collisionswithmethodsofthemodelsthatwillinheritfromthisclass.

        ``mail.thread``definesfieldsusedtohandleanddisplaythe
        communicationhistory.``mail.thread``alsomanagesfollowersof
        inheritingclasses.Allfeaturesandexpectedbehavioraremanaged
        bymail.thread.Widgetshasbeendesignedforthe7.0andfollowing
        versionsofFlectra.

        Inheritingclassesarenotrequiredtoimplementanymethod,asthe
        defaultimplementationwillworkforanymodel.Howeveritiscommon
        tooverrideatleastthe``message_new``and``message_update``
        methods(calling``super``)toaddmodel-specificbehaviorat
        creationandupdateofathreadwhenprocessingincomingemails.

        Options:
            -_mail_flat_thread:ifsettoTrue,allmessageswithoutparent_id
                areautomaticallyattachedtothefirstmessagepostedonthe
                ressource.IfsettoFalse,thedisplayofChatterisdoneusing
                threads,andnoparent_idisautomaticallyset.

    MailThreadfeaturescanbesomewhatcontrolledthroughcontextkeys:

     -``mail_create_nosubscribe``:atcreateormessage_post,donotsubscribe
       uidtotherecordthread
     -``mail_create_nolog``:atcreate,donotlogtheautomatic'<Document>
       created'message
     -``mail_notrack``:atcreateandwrite,donotperformthevaluetracking
       creatingmessages
     -``tracking_disable``:atcreateandwrite,performnoMailThreadfeatures
       (autosubscription,tracking,post,...)
     -``mail_notify_force_send``:iflessthan50emailnotificationstosend,
       sendthemdirectlyinsteadofusingthequeue;Truebydefault
    '''
    _name='mail.thread'
    _description='EmailThread'
    _mail_flat_thread=True #flattenthediscussinohistory
    _mail_post_access='write' #accessrequiredonthedocumenttopostonit
    _Attachment=namedtuple('Attachment',('fname','content','info'))

    message_is_follower=fields.Boolean(
        'IsFollower',compute='_compute_is_follower',search='_search_is_follower')
    message_follower_ids=fields.One2many(
        'mail.followers','res_id',string='Followers',groups='base.group_user')
    message_partner_ids=fields.Many2many(
        comodel_name='res.partner',string='Followers(Partners)',
        compute='_get_followers',search='_search_follower_partners',
        groups='base.group_user')
    message_channel_ids=fields.Many2many(
        comodel_name='mail.channel',string='Followers(Channels)',
        compute='_get_followers',search='_search_follower_channels',
        groups='base.group_user')
    message_ids=fields.One2many(
        'mail.message','res_id',string='Messages',
        domain=lambdaself:[('message_type','!=','user_notification')],auto_join=True)
    message_unread=fields.Boolean(
        'UnreadMessages',compute='_get_message_unread',
        help="Ifchecked,newmessagesrequireyourattention.")
    message_unread_counter=fields.Integer(
        'UnreadMessagesCounter',compute='_get_message_unread',
        help="Numberofunreadmessages")
    message_needaction=fields.Boolean(
        'ActionNeeded',compute='_get_message_needaction',search='_search_message_needaction',
        help="Ifchecked,newmessagesrequireyourattention.")
    message_needaction_counter=fields.Integer(
        'NumberofActions',compute='_get_message_needaction',
        help="Numberofmessageswhichrequiresanaction")
    message_has_error=fields.Boolean(
        'MessageDeliveryerror',compute='_compute_message_has_error',search='_search_message_has_error',
        help="Ifchecked,somemessageshaveadeliveryerror.")
    message_has_error_counter=fields.Integer(
        'Numberoferrors',compute='_compute_message_has_error',
        help="Numberofmessageswithdeliveryerror")
    message_attachment_count=fields.Integer('AttachmentCount',compute='_compute_message_attachment_count',groups="base.group_user")
    message_main_attachment_id=fields.Many2one(string="MainAttachment",comodel_name='ir.attachment',index=True,copy=False)

    @api.depends('message_follower_ids')
    def_get_followers(self):
        forthreadinself:
            thread.message_partner_ids=thread.message_follower_ids.mapped('partner_id')
            thread.message_channel_ids=thread.message_follower_ids.mapped('channel_id')

    @api.model
    def_search_follower_partners(self,operator,operand):
        """Searchfunctionformessage_follower_ids

        Donotusewithoperator'notin'.Useinsteadmessage_is_followers
        """
        #TOFIXmakeitworkwithnotin
        assertoperator!="notin","Donotsearchmessage_follower_idswith'notin'"
        followers=self.env['mail.followers'].sudo().search([
            ('res_model','=',self._name),
            ('partner_id',operator,operand)])
        #usingread()belowismuchfasterthanfollowers.mapped('res_id')
        return[('id','in',[res['res_id']forresinfollowers.read(['res_id'])])]

    @api.model
    def_search_follower_channels(self,operator,operand):
        """Searchfunctionformessage_follower_ids

        Donotusewithoperator'notin'.Useinsteadmessage_is_followers
        """
        #TOFIXmakeitworkwithnotin
        assertoperator!="notin","Donotsearchmessage_follower_idswith'notin'"
        followers=self.env['mail.followers'].sudo().search([
            ('res_model','=',self._name),
            ('channel_id',operator,operand)])
        #usingread()belowismuchfasterthanfollowers.mapped('res_id')
        return[('id','in',[res['res_id']forresinfollowers.read(['res_id'])])]

    @api.depends('message_follower_ids')
    def_compute_is_follower(self):
        followers=self.env['mail.followers'].sudo().search([
            ('res_model','=',self._name),
            ('res_id','in',self.ids),
            ('partner_id','=',self.env.user.partner_id.id),
            ])
        #usingread()belowismuchfasterthanfollowers.mapped('res_id')
        following_ids=[res['res_id']forresinfollowers.read(['res_id'])]
        forrecordinself:
            record.message_is_follower=record.idinfollowing_ids

    @api.model
    def_search_is_follower(self,operator,operand):
        followers=self.env['mail.followers'].sudo().search([
            ('res_model','=',self._name),
            ('partner_id','=',self.env.user.partner_id.id),
            ])
        #Cases('message_is_follower','=',True)or ('message_is_follower','!=',False)
        if(operator=='='andoperand)or(operator=='!='andnotoperand):
            #usingread()belowismuchfasterthanfollowers.mapped('res_id')
            return[('id','in',[res['res_id']forresinfollowers.read(['res_id'])])]
        else:
            #usingread()belowismuchfasterthanfollowers.mapped('res_id')
            return[('id','notin',[res['res_id']forresinfollowers.read(['res_id'])])]

    def_get_message_unread(self):
        partner_id=self.env.user.partner_id.id
        res=dict.fromkeys(self.ids,0)
        ifself.ids:
            #searchforunreadmessages,directlyinSQLtoimproveperformances
            self._cr.execute("""SELECTmsg.res_idFROMmail_messagemsg
                                 RIGHTJOINmail_message_mail_channel_relrel
                                 ONrel.mail_message_id=msg.id
                                 RIGHTJOINmail_channel_partnercp
                                 ON(cp.channel_id=rel.mail_channel_idANDcp.partner_id=%sAND
                                    (cp.seen_message_idISNULLORcp.seen_message_id<msg.id))
                                 WHEREmsg.model=%sANDmsg.res_id=ANY(%s)AND
                                        msg.message_type!='user_notification'AND
                                       (msg.author_idISNULLORmsg.author_id!=%s)AND
                                       (msg.message_typenotin('notification','user_notification')ORmsg.model!='mail.channel')""",
                             (partner_id,self._name,list(self.ids),partner_id,))
            forresultinself._cr.fetchall():
                res[result[0]]+=1

        forrecordinself:
            record.message_unread_counter=res.get(record._origin.id,0)
            record.message_unread=bool(record.message_unread_counter)

    def_get_message_needaction(self):
        res=dict.fromkeys(self.ids,0)
        ifself.ids:
            #searchforunreadmessages,directlyinSQLtoimproveperformances
            self._cr.execute("""SELECTmsg.res_idFROMmail_messagemsg
                                 RIGHTJOINmail_message_res_partner_needaction_relrel
                                 ONrel.mail_message_id=msg.idANDrel.res_partner_id=%sAND(rel.is_read=falseORrel.is_readISNULL)
                                 WHEREmsg.model=%sANDmsg.res_idin%sANDmsg.message_type!='user_notification'""",
                             (self.env.user.partner_id.id,self._name,tuple(self.ids),))
            forresultinself._cr.fetchall():
                res[result[0]]+=1

        forrecordinself:
            record.message_needaction_counter=res.get(record._origin.id,0)
            record.message_needaction=bool(record.message_needaction_counter)

    @api.model
    def_search_message_needaction(self,operator,operand):
        return[('message_ids.needaction',operator,operand)]

    def_compute_message_has_error(self):
        res={}
        ifself.ids:
            self._cr.execute("""SELECTmsg.res_id,COUNT(msg.res_id)FROMmail_messagemsg
                                 RIGHTJOINmail_message_res_partner_needaction_relrel
                                 ONrel.mail_message_id=msg.idANDrel.notification_statusin('exception','bounce')
                                 WHEREmsg.author_id=%sANDmsg.model=%sANDmsg.res_idin%sANDmsg.message_type!='user_notification'
                                 GROUPBYmsg.res_id""",
                             (self.env.user.partner_id.id,self._name,tuple(self.ids),))
            res.update(self._cr.fetchall())

        forrecordinself:
            record.message_has_error_counter=res.get(record._origin.id,0)
            record.message_has_error=bool(record.message_has_error_counter)

    @api.model
    def_search_message_has_error(self,operator,operand):
        message_ids=self.env['mail.message']._search([('has_error',operator,operand),('author_id','=',self.env.user.partner_id.id)])
        return[('message_ids','in',message_ids)]

    def_compute_message_attachment_count(self):
        read_group_var=self.env['ir.attachment'].read_group([('res_id','in',self.ids),('res_model','=',self._name)],
                                                              fields=['res_id'],
                                                              groupby=['res_id'])

        attachment_count_dict=dict((d['res_id'],d['res_id_count'])fordinread_group_var)
        forrecordinself:
            record.message_attachment_count=attachment_count_dict.get(record.id,0)

    #------------------------------------------------------------
    #CRUD
    #------------------------------------------------------------

    @api.model_create_multi
    defcreate(self,vals_list):
        """Chatteroverride:
            -subscribeuid
            -subscribefollowersofparent
            -logacreationmessage
        """
        ifself._context.get('tracking_disable'):
            threads=super(MailThread,self).create(vals_list)
            threads._discard_tracking()
            returnthreads

        threads=super(MailThread,self).create(vals_list)
        #subscribeuidunlessaskednotto
        ifnotself._context.get('mail_create_nosubscribe'):
            forthreadinthreads:
                self.env['mail.followers']._insert_followers(
                    thread._name,thread.ids,self.env.user.partner_id.ids,
                    None,None,None,
                    customer_ids=[],
                    check_existing=False
                )

        #auto_subscribe:takevaluesanddefaultsintoaccount
        create_values_list={}
        forthread,valuesinzip(threads,vals_list):
            create_values=dict(values)
            forkey,valinself._context.items():
                ifkey.startswith('default_')andkey[8:]notincreate_values:
                    create_values[key[8:]]=val
            thread._message_auto_subscribe(create_values,followers_existing_policy='update')
            create_values_list[thread.id]=create_values

        #automaticloggingunlessaskednotto(mainlyforvarioustestingpurpose)
        ifnotself._context.get('mail_create_nolog'):
            threads_no_subtype=self.env[self._name]
            forthreadinthreads:
                subtype=thread._creation_subtype()
                ifsubtype: #ifwehaveasubtype,postmessagetonotifyusersfrom_message_auto_subscribe
                    thread.sudo().message_post(subtype_id=subtype.id,author_id=self.env.user.partner_id.id)
                else:
                    threads_no_subtype+=thread
            ifthreads_no_subtype:
                bodies=dict(
                    (thread.id,thread._creation_message())
                    forthreadinthreads_no_subtype)
                threads_no_subtype._message_log_batch(bodies=bodies)

        #posttracktemplateifatrackedfieldchanged
        threads._discard_tracking()
        ifnotself._context.get('mail_notrack'):
            fnames=self._get_tracked_fields()
            forthreadinthreads:
                create_values=create_values_list[thread.id]
                changes=[fnameforfnameinfnamesifcreate_values.get(fname)]
                #basedontrackedfieldtostayconsistentwithwrite
                #wedon'tconsiderthatafalsyfieldisachange,tostayconsistentwithpreviousimplementation,
                #butwemaywanttochangethatbehaviourlater.
                thread._message_track_post_template(changes)

        returnthreads

    defwrite(self,values):
        ifself._context.get('tracking_disable'):
            returnsuper(MailThread,self).write(values)

        ifnotself._context.get('mail_notrack'):
            self._prepare_tracking(self._fields)

        #Performwrite
        result=super(MailThread,self).write(values)

        #updatefollowers
        self._message_auto_subscribe(values)

        returnresult

    defunlink(self):
        """Overrideunlinktodeletemessagesandfollowers.Thiscannotbe
        cascaded,becauselinkisdonethrough(res_model,res_id)."""
        ifnotself:
            returnTrue
        #discardpendingtracking
        self._discard_tracking()
        self.env['mail.message'].sudo().search([('model','=',self._name),('res_id','in',self.ids)]).unlink()
        res=super(MailThread,self).unlink()
        self.env['mail.followers'].sudo().search(
            [('res_model','=',self._name),('res_id','in',self.ids)]
        ).unlink()
        returnres

    defcopy_data(self,default=None):
        #avoidtrackingmultipletemporarychangesduringcopy
        returnsuper(MailThread,self.with_context(mail_notrack=True)).copy_data(default=default)

    @api.model
    defget_empty_list_help(self,help):
        """OverrideofBaseModel.get_empty_list_help()togenerateanhelpmessage
        thataddsaliasinformation."""
        model=self._context.get('empty_list_help_model')
        res_id=self._context.get('empty_list_help_id')
        catchall_domain=self.env['ir.config_parameter'].sudo().get_param("mail.catchall.domain")
        document_name=self._context.get('empty_list_help_document_name',_('document'))
        nothing_here=nothelp
        alias=None

        ifcatchall_domainandmodelandres_id: #specificres_id->finditsalias(i.e.section_idspecified)
            record=self.env[model].sudo().browse(res_id)
            #checkthatthealiaseffectivelycreatesnewrecords
            ifrecord.alias_idandrecord.alias_id.alias_nameand\
                    record.alias_id.alias_model_idand\
                    record.alias_id.alias_model_id.model==self._nameand\
                    record.alias_id.alias_force_thread_id==0:
                alias=record.alias_id
        ifnotaliasandcatchall_domainandmodel: #nores_idorres_idnotlinkedtoanalias->generichelpmessage,takeagenericaliasofthemodel
            Alias=self.env['mail.alias']
            aliases=Alias.search([
                ("alias_parent_model_id.model","=",model),
                ("alias_name","!=",False),
                ('alias_force_thread_id','=',False),
                ('alias_parent_thread_id','=',False)],order='idASC')
            ifaliasesandlen(aliases)==1:
                alias=aliases[0]

        ifalias:
            email_link="<ahref='mailto:%(email)s'>%(email)s</a>"%{'email':alias.display_name}
            ifnothing_here:
                return"<pclass='o_view_nocontent_smiling_face'>%(dyn_help)s</p>"%{
                    'dyn_help':_("Addanew%(document)sorsendanemailto%(email_link)s",
                        document=document_name,
                        email_link=email_link,
                    )
                }
            #donotaddaliastwotimesifitwasaddedpreviously
            if"oe_view_nocontent_alias"notinhelp:
                return"%(static_help)s<pclass='oe_view_nocontent_alias'>%(dyn_help)s</p>"%{
                    'static_help':help,
                    'dyn_help':_("Createnew%(document)sbysendinganemailto%(email_link)s",
                        document=document_name,
                        email_link=email_link,
                    )
                }

        ifnothing_here:
            return"<pclass='o_view_nocontent_smiling_face'>%(dyn_help)s</p>"%{
                'dyn_help':_("Createnew%(document)s",document=document_name),
            }

        returnhelp

    #------------------------------------------------------
    #MODELS/CRUDHELPERS
    #------------------------------------------------------

    def_compute_field_value(self,field):
        ifnotself._context.get('tracking_disable')andnotself._context.get('mail_notrack'):
            self._prepare_tracking(f.nameforfinself.pool.field_computed[field]iff.store)

        returnsuper()._compute_field_value(field)

    def_creation_subtype(self):
        """Givethesubtypestriggeredbythecreationofarecord

        :returns:asubtypebrowserecord(emptyifnosubtypeistriggered)
        """
        returnself.env['mail.message.subtype']

    def_get_creation_message(self):
        """Deprecated,removein14+"""
        returnself._creation_message()

    def_creation_message(self):
        """Getthecreationmessagetologintothechatterattherecord'screation.
        :returns:Themessage'sbodytolog.
        """
        self.ensure_one()
        doc_name=self.env['ir.model']._get(self._name).name
        return_('%screated',doc_name)

    @api.model
    defget_mail_message_access(self,res_ids,operation,model_name=None):
        """Deprecated,removewithv14+"""
        returnself._get_mail_message_access(res_ids,operation,model_name=model_name)

    @api.model
    def_get_mail_message_access(self,res_ids,operation,model_name=None):
        """mail.messagecheckpermissionrulesforrelateddocument.Thismethodis
            meanttobeinheritedinordertoimplementaddons-specificbehavior.
            Acommonbehaviorwouldbetoallowcreatingmessageswhenhavingread
            accessruleonthedocument,forportaldocumentsuchasissues."""

        DocModel=self.env[model_name]ifmodel_nameelseself
        create_allow=getattr(DocModel,'_mail_post_access','write')

        ifoperationin['write','unlink']:
            check_operation='write'
        elifoperation=='create'andcreate_allowin['create','read','write','unlink']:
            check_operation=create_allow
        elifoperation=='create':
            check_operation='write'
        else:
            check_operation=operation
        returncheck_operation

    def_valid_field_parameter(self,field,name):
        #allowtrackingonmodelsinheritingfrom'mail.thread'
        returnname=='tracking'orsuper()._valid_field_parameter(field,name)

    defwith_lang(self):
        """Deprecated,removein14+"""
        returnself._fallback_lang()

    def_fallback_lang(self):
        ifnotself._context.get("lang"):
            returnself.with_context(lang=self.env.user.lang)
        returnself

    #------------------------------------------------------
    #WRAPPERSANDTOOLS
    #------------------------------------------------------

    defmessage_change_thread(self,new_thread):
        """
        Transferthelistofthemailthreadmessagesfromanmodeltoanother

        :paramid:theoldres_idofthemail.message
        :paramnew_res_id:thenewres_idofthemail.message
        :paramnew_model:thenameofthenewmodelofthemail.message

        Example:  my_lead.message_change_thread(my_project_task)
                    willtransferthecontextofthethreadofmy_leadtomy_project_task
        """
        self.ensure_one()
        #getthesubtypeofthecommentMessage
        subtype_comment=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

        #gettheidsofthecommentandnot-commentofthethread
        #TDEcheck:sudoonmail.message,tobesureallmessagesaremoved?
        MailMessage=self.env['mail.message']
        msg_comment=MailMessage.search([
            ('model','=',self._name),
            ('res_id','=',self.id),
            ('message_type','!=','user_notification'),
            ('subtype_id','=',subtype_comment)])
        msg_not_comment=MailMessage.search([
            ('model','=',self._name),
            ('res_id','=',self.id),
            ('message_type','!=','user_notification'),
            ('subtype_id','!=',subtype_comment)])

        #updatethemessages
        msg_comment.write({"res_id":new_thread.id,"model":new_thread._name})
        msg_not_comment.write({"res_id":new_thread.id,"model":new_thread._name,"subtype_id":None})
        returnTrue

    #------------------------------------------------------
    #TRACKING/LOG
    #------------------------------------------------------

    def_prepare_tracking(self,fields):
        """Preparethetrackingof``fields``for``self``.

        :paramfields:iterableoffieldsnamestopotentiallytrack
        """
        fnames=self._get_tracked_fields().intersection(fields)
        ifnotfnames:
            return
        self.env.cr.precommit.add(self._finalize_tracking)
        initial_values=self.env.cr.precommit.data.setdefault(f'mail.tracking.{self._name}',{})
        forrecordinself:
            ifnotrecord.id:
                continue
            values=initial_values.setdefault(record.id,{})
            ifvaluesisnotNone:
                forfnameinfnames:
                    values.setdefault(fname,record[fname])

    def_discard_tracking(self):
        """Preventanytrackingoffieldson``self``."""
        ifnotself._get_tracked_fields():
            return
        self.env.cr.precommit.add(self._finalize_tracking)
        initial_values=self.env.cr.precommit.data.setdefault(f'mail.tracking.{self._name}',{})
        #disabletrackingbysettinginitialvaluestoNone
        forid_inself.ids:
            initial_values[id_]=None

    def_finalize_tracking(self):
        """Generatethetrackingmessagesfortherecordsthathavebeen
        preparedwith``_prepare_tracking``.
        """
        initial_values=self.env.cr.precommit.data.pop(f'mail.tracking.{self._name}',{})
        ids=[id_forid_,valsininitial_values.items()ifvals]
        ifnotids:
            return
        records=self.browse(ids).sudo()
        fnames=self._get_tracked_fields()
        context=clean_context(self._context)
        tracking=records.with_context(context).message_track(fnames,initial_values)
        forrecordinrecords:
            changes,tracking_value_ids=tracking.get(record.id,(None,None))
            record._message_track_post_template(changes)
        #thismethodiscalledafterthemainflush()andjustbeforecommit();
        #wehavetoflush()againincasewetriggeredsomerecomputations
        self.flush()

    @tools.ormcache('self.env.uid','self.env.su')
    def_get_tracked_fields(self):
        """Returnthesetoftrackedfieldsnamesforthecurrentmodel."""
        fields={
            name
            forname,fieldinself._fields.items()
            ifgetattr(field,'tracking',None)orgetattr(field,'track_visibility',None)
        }

        returnfieldsandset(self.fields_get(fields))

    def_message_track_post_template(self,changes):
        ifnotchanges:
            returnTrue
        #Cleanthecontexttogetridofresidualdefault_*keys
        #thatcouldcauseissuesafterwardduringthemail.message
        #generation.Example:'default_parent_id'wouldreferto
        #theparent_idofthecurrentrecordthatwasusedduring
        #itscreation,butcouldrefertowrongparentmessageid,
        #leadingtoatracebackincasetherelatedmessage_id
        #doesn'texist
        self=self.with_context(clean_context(self._context))
        templates=self._track_template(changes)
        forfield_name,(template,post_kwargs)intemplates.items():
            ifnottemplate:
                continue
            ifisinstance(template,str):
                self._fallback_lang().message_post_with_view(template,**post_kwargs)
            else:
                self._fallback_lang().message_post_with_template(template.id,**post_kwargs)
        returnTrue

    def_track_template(self,changes):
        returndict()

    defmessage_track(self,tracked_fields,initial_values):
        """Trackupdatedvalues.Comparingtheinitialandcurrentvaluesof
        thefieldsgivenintracked_fields,itgeneratesamessagecontaining
        theupdatedvalues.Thismessagecanbelinkedtoamail.message.subtype
        givenbythe``_track_subtype``method.

        :paramtracked_fields:iterableoffieldnamestotrack
        :paraminitial_values:mapping{record_id:{field_name:value}}
        :return:mapping{record_id:(changed_field_names,tracking_value_ids)}
            containingexistingrecordsonly
        """
        ifnottracked_fields:
            returnTrue

        tracked_fields=self.fields_get(tracked_fields)
        tracking=dict()
        forrecordinself:
            try:
                tracking[record.id]=record._message_track(tracked_fields,initial_values[record.id])
            exceptMissingError:
                continue

        forrecordinself:
            changes,tracking_value_ids=tracking.get(record.id,(None,None))
            ifnotchanges:
                continue

            #findsubtypesandpostmessagesorlogifnosubtypefound
            subtype=False
            #Bypassingthiskey,thatallowstoletthesubtypeemptyandsodon'tsentemailbecausepartners_to_notifyfrommail_message._notifywillbeempty
            ifnotself._context.get('mail_track_log_only'):
                subtype=record._track_subtype(dict((col_name,initial_values[record.id][col_name])forcol_nameinchanges))
            ifsubtype:
                ifnotsubtype.exists():
                    _logger.debug('subtype"%s"notfound'%subtype.name)
                    continue
                record.message_post(subtype_id=subtype.id,tracking_value_ids=tracking_value_ids)
            eliftracking_value_ids:
                record._message_log(tracking_value_ids=tracking_value_ids)

        returntracking

    defstatic_message_track(self,record,tracked_fields,initial):
        """Deprecated,removeinv14+"""
        returnrecord._mail_track(tracked_fields,initial)

    def_message_track(self,tracked_fields,initial):
        """Movedto``BaseModel._mail_track()``"""
        returnself._mail_track(tracked_fields,initial)

    def_track_subtype(self,init_values):
        """Givethesubtypestriggeredbythechangesontherecordaccording
        tovaluesthathavebeenupdated.

        :paraminit_values:theoriginalvaluesoftherecord;onlymodifiedfields
                            arepresentinthedict
        :typeinit_values:dict
        :returns:asubtypebrowserecordorFalseifnosubtypeistrigerred
        """
        returnFalse

    #------------------------------------------------------
    #MAILGATEWAY
    #------------------------------------------------------

    def_routing_warn(self,error_message,message_id,route,raise_exception=True):
        """Toolsmethodusedin_routing_check_route:whethertologawarningorraiseanerror"""
        short_message=_("Mailboxunavailable-%s",error_message)
        full_message=('RoutingmailwithMessage-Id%s:route%s:%s'%
                        (message_id,route,error_message))
        _logger.info(full_message)
        ifraise_exception:
            #sendershouldnotseeprivatediagnosticsinfo,justtheerror
            raiseValueError(short_message)

    def_routing_create_bounce_email(self,email_from,body_html,message,**mail_values):
        bounce_to=tools.decode_message_header(message,'Return-Path')oremail_from
        bounce_mail_values={
            'author_id':False,
            'body_html':body_html,
            'subject':'Re:%s'%message.get('subject'),
            'email_to':bounce_to,
            'auto_delete':True,
        }
        bounce_from=self.env['ir.mail_server']._get_default_bounce_address()
        ifbounce_from:
            bounce_mail_values['email_from']=tools.formataddr(('MAILER-DAEMON',bounce_from))
        elifself.env['ir.config_parameter'].sudo().get_param("mail.catchall.alias")notinmessage['To']:
            bounce_mail_values['email_from']=tools.decode_message_header(message,'To')
        else:
            bounce_mail_values['email_from']=tools.formataddr(('MAILER-DAEMON',self.env.user.email_normalized))
        bounce_mail_values.update(mail_values)
        self.env['mail.mail'].sudo().create(bounce_mail_values).send()

    @api.model
    def_routing_handle_bounce(self,email_message,message_dict):
        """Handlebounceofincomingemail.Basedonvaluesofthebounce(email
        andrelatedpartner,sendmessageanditsmessageID)

          *findblacklist-enabledrecordswithemail_normalized=bouncedemail
            andcall``_message_receive_bounce``oneachofthemtopropagate
            bounceinformationthroughvariousrecordslinkedtosameemail;
          *ifnotalreadydone(i.e.iforiginalrecordisnotblacklistenabled
            likeabounceonanapplicant),findrecordlinkedtobouncedmessage
            andcall``_message_receive_bounce``;

        :paramemail_message:incomingemail;
        :typeemail_message:email.message;
        :parammessage_dict:dictionaryholdingalready-parsedvaluesandin
            whichbounce-relatedvalueswillbeadded;
        :typemessage_dict:dictionary;
        """
        bounced_record,bounced_record_done=False,False
        bounced_email,bounced_partner=message_dict['bounced_email'],message_dict['bounced_partner']
        bounced_msg_id,bounced_message=message_dict['bounced_msg_id'],message_dict['bounced_message']

        ifbounced_email:
            bounced_model,bounced_res_id=bounced_message.model,bounced_message.res_id

            ifbounced_modelandbounced_modelinself.envandbounced_res_id:
                bounced_record=self.env[bounced_model].sudo().browse(bounced_res_id).exists()

            bl_models=self.env['ir.model'].sudo().search(['&',('is_mail_blacklist','=',True),('model','!=','mail.thread.blacklist')])
            formodelin[bl_modelforbl_modelinbl_modelsifbl_model.modelinself.env]: #transienttestmode
                rec_bounce_w_email=self.env[model.model].sudo().search([('email_normalized','=',bounced_email)])
                rec_bounce_w_email._message_receive_bounce(bounced_email,bounced_partner)
                bounced_record_done=bounced_record_doneor(bounced_recordandmodel.model==bounced_modelandbounced_recordinrec_bounce_w_email)

            #setrecordasbouncedunlessalreadydoneduetoblacklistmixin
            ifbounced_recordandnotbounced_record_doneandisinstance(bounced_record,self.pool['mail.thread']):
                bounced_record._message_receive_bounce(bounced_email,bounced_partner)

            ifbounced_partnerandbounced_message:
                self.env['mail.notification'].sudo().search([
                    ('mail_message_id','=',bounced_message.id),
                    ('res_partner_id','in',bounced_partner.ids)]
                ).write({'notification_status':'bounce'})

        ifbounced_record:
            _logger.info('Routingmailfrom%sto%swithMessage-Id%s:notroutingbounceemailfrom%sreplyingto%s(model%sID%s)',
                         message_dict['email_from'],message_dict['to'],message_dict['message_id'],bounced_email,bounced_msg_id,bounced_model,bounced_res_id)
        elifbounced_email:
            _logger.info('Routingmailfrom%sto%swithMessage-Id%s:notroutingbounceemailfrom%sreplyingto%s(nodocumentfound)',
                         message_dict['email_from'],message_dict['to'],message_dict['message_id'],bounced_email,bounced_msg_id)
        else:
            _logger.info('Routingmailfrom%sto%swithMessage-Id%s:notroutingbounceemail.',
                         message_dict['email_from'],message_dict['to'],message_dict['message_id'])

    @api.model
    def_routing_check_route(self,message,message_dict,route,raise_exception=True):
        """Verifyroutevalidity.Checkandrules:
            1-ifthread_id->checkthatdocumenteffectivelyexists;otherwise
                fallbackonamessage_newbyresettingthread_id
            2-checkthatmessage_updateexistsifthread_idisset;oratleast
                thatmessage_newexist
            3-ifthereisanalias,checkalias_contact:
                'followers'andthread_id:
                    checkontargetdocumentthattheauthorisinthefollowers
                'followers'andalias_parent_thread_id:
                    checkonaliasparentdocumentthattheauthorisinthe
                    followers
                'partners':checkthatauthor_ididset

        :parammessage:anemail.messageinstance
        :parammessage_dict:dictionaryofvaluesthatwillbegivento
                             mail_message.create()
        :paramroute:routetocheckwhichisatuple(model,thread_id,
                      custom_values,uid,alias)
        :paramraise_exception:ifanerroroccurs,tellwhethertoraiseanerror
                                orjustlogawarningandtryotherprocessingor
                                invalidateroute
        """

        assertisinstance(route,(list,tuple)),'Arouteshouldbealistoratuple'
        assertlen(route)==5,'Arouteshouldcontain5elements:model,thread_id,custom_values,uid,aliasrecord'

        message_id=message_dict['message_id']
        email_from=message_dict['email_from']
        author_id=message_dict.get('author_id')
        model,thread_id,alias=route[0],route[1],route[4]
        record_set=None

        #Wrongmodel
        ifnotmodel:
            self._routing_warn(_('targetmodelunspecified'),message_id,route,raise_exception)
            return()
        elifmodelnotinself.env:
            self._routing_warn(_('unknowntargetmodel%s',model),message_id,route,raise_exception)
            return()
        record_set=self.env[model].browse(thread_id)ifthread_idelseself.env[model]

        #ExistingDocument:checkifexistsandmodelacceptsthemailgateway;ifnot,fallbackoncreateifallowed
        ifthread_id:
            ifnotrecord_set.exists():
                self._routing_warn(
                    _('replytomissingdocument(%(model)s,%(thread)s),fallbackondocumentcreation',model=model,thread=thread_id),
                    message_id,
                    route,
                    False
                )
                thread_id=None
            elifnothasattr(record_set,'message_update'):
                self._routing_warn(_('replytomodel%sthatdoesnotacceptdocumentupdate,fallbackondocumentcreation',model),message_id,route,False)
                thread_id=None

        #NewDocument:checkmodelacceptsthemailgateway
        ifnotthread_idandmodelandnothasattr(record_set,'message_new'):
            self._routing_warn(_('model%sdoesnotacceptdocumentcreation',model),message_id,route,raise_exception)
            return()

        #Updatemessageauthor.Wedoitnowbecauseweneeditforaliases(contactsettings)
        ifnotauthor_id:
            ifrecord_set:
                authors=self._mail_find_partner_from_emails([email_from],records=record_set)
            elifaliasandalias.alias_parent_model_idandalias.alias_parent_thread_id:
                records=self.env[alias.alias_parent_model_id.model].browse(alias.alias_parent_thread_id)
                authors=self._mail_find_partner_from_emails([email_from],records=records)
            else:
                authors=self._mail_find_partner_from_emails([email_from],records=None)
            ifauthors:
                message_dict['author_id']=authors[0].id

        #Alias:checkalias_contactsettings
        ifalias:
            ifthread_id:
                obj=record_set[0]
            elifalias.alias_parent_model_idandalias.alias_parent_thread_id:
                obj=self.env[alias.alias_parent_model_id.model].browse(alias.alias_parent_thread_id)
            else:
                obj=self.env[model]
            error_message=obj._alias_get_error_message(message,message_dict,alias)
            iferror_message:
                self._routing_warn(
                    _('alias%(name)s:%(error)s',name=alias.alias_name,error=error_messageor_('unknownerror')),
                    message_id,
                    route,
                    False
                )
                body=alias._get_alias_bounced_body(message_dict)
                self._routing_create_bounce_email(email_from,body,message,references=message_id)
                returnFalse

        return(model,thread_id,route[2],route[3],route[4])

    @api.model
    def_routing_reset_bounce(self,email_message,message_dict):
        """Calledby``message_process``whenanewmailisreceivedfromanemailaddress.
        Iftheemailisrelatedtoapartner,weconsiderthatthenumberofmessage_bounce
        isnotrelevantanymoreastheemailisvalid-aswereceivedanemailfromthis
        address.Themodelisherehardcodedbecausewecannotknowwithwhichmodelthe
        incommingmailmatch.Weconsiderthatifamailarrives,wehavetoclearbouncefor
        eachmodelhavingbouncecount.

        :paramemail_from:emailaddressthatsenttheincomingemail."""
        valid_email=message_dict['email_from']
        ifvalid_email:
            bl_models=self.env['ir.model'].sudo().search(['&',('is_mail_blacklist','=',True),('model','!=','mail.thread.blacklist')])
            formodelin[bl_modelforbl_modelinbl_modelsifbl_model.modelinself.env]: #transienttestmode
                self.env[model.model].sudo().search([('message_bounce','>',0),('email_normalized','=',valid_email)])._message_reset_bounce(valid_email)

    @api.model
    defmessage_route(self,message,message_dict,model=None,thread_id=None,custom_values=None):
        """Attempttofigureoutthecorrecttargetmodel,thread_id,
        custom_valuesanduser_idtouseforanincomingmessage.
        Multiplevaluesmaybereturned,ifamessagehadmultiple
        recipientsmatchingexistingmail.aliases,forexample.

        Thefollowingheuristicsareused,inthisorder:

         *ifthemessagerepliestoanexistingthreadbyhavingaMessage-Id
           thatmatchesanexistingmail_message.message_id,wetaketheoriginal
           messagemodel/thread_idpairandignorecustom_valueasnocreationwill
           takeplace;
         *lookforamail.aliasentrymatchingthemessagerecipientsandusethe
           correspondingmodel,thread_id,custom_valuesanduser_id.Thiscould
           leadtoathreadupdateorcreationdependingonthealias;
         *fallbackonprovided``model``,``thread_id``and``custom_values``;
         *raiseanexceptionasnoroutehasbeenfound

        :paramstringmessage:anemail.messageinstance
        :paramdictmessage_dict:dictionaryholdingparsedmessagevariables
        :paramstringmodel:thefallbackmodeltouseifthemessagedoesnotmatch
            anyofthecurrentlyconfiguredmailaliases(maybeNoneifamatching
            aliasissupposedtobepresent)
        :typedictcustom_values:optionaldictionaryofdefaultfieldvalues
            topassto``message_new``ifanewrecordneedstobecreated.
            Ignoredifthethreadrecordalreadyexists,andalsoifamatching
            mail.aliaswasfound(aliasesdefinetheirowndefaults)
        :paramintthread_id:optionalIDoftherecord/threadfrom``model``to
            whichthismailshouldbeattached.Onlyusedifthemessagedoesnot
            replytoanexistingthreadanddoesnotmatchanymailalias.
        :return:listofroutes[(model,thread_id,custom_values,user_id,alias)]

        :raises:ValueError,TypeError
        """
        ifnotisinstance(message,EmailMessage):
            raiseTypeError('messagemustbeanemail.message.EmailMessageatthispoint')
        catchall_alias=self.env['ir.config_parameter'].sudo().get_param("mail.catchall.alias")
        catchall_domain_lowered=self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain","").strip().lower()
        catchall_domains_allowed=self.env["ir.config_parameter"].sudo().get_param("mail.catchall.domain.allowed")
        ifcatchall_domain_loweredandcatchall_domains_allowed:
            catchall_domains_allowed=catchall_domains_allowed.split(',')+[catchall_domain_lowered]
        bounce_alias=self.env['ir.config_parameter'].sudo().get_param("mail.bounce.alias")
        bounce_alias_static=tools.str2bool(self.env['ir.config_parameter'].sudo().get_param("mail.bounce.alias.static","False"))
        fallback_model=model

        #getemail.message.Messagevariablesforfutureprocessing
        local_hostname=socket.gethostname()
        message_id=message_dict['message_id']

        #computereferencestofindifmessageisareplytoanexistingthread
        thread_references=message_dict['references']ormessage_dict['in_reply_to']
        msg_references=[
            re.sub(r'[\r\n\t]+',r'',ref) #"Unfold"buggyreferences
            forrefintools.mail_header_msgid_re.findall(thread_references)
            if'reply_to'notinref
        ]
        mail_messages=self.env['mail.message'].sudo().search([('message_id','in',msg_references)],limit=1,order='iddesc,message_id')
        is_a_reply=bool(mail_messages)
        reply_model,reply_thread_id=mail_messages.model,mail_messages.res_id

        #authorandrecipients
        email_from=message_dict['email_from']
        email_from_localpart=(tools.email_split(email_from)or[''])[0].split('@',1)[0].lower()
        email_to=message_dict['to']
        email_to_localparts=[
            e.split('@',1)[0].lower()
            forein(tools.email_split(email_to)or[''])
        ]
        #Delivered-ToisasafebetinmostmodernMTAs,butwehavetofallbackonTo+Ccvalues
        #foralltheoddMTAsoutthere,asthereisnostandardheaderfortheenvelope's`rcpt_to`value.
        rcpt_tos_localparts=[]
        forrecipientintools.email_split(message_dict['recipients']):
            to_local,to_domain=recipient.split('@',maxsplit=1)
            ifnotcatchall_domains_allowedorto_domain.lower()incatchall_domains_allowed:
                rcpt_tos_localparts.append(to_local.lower())
        rcpt_tos_valid_localparts=[tofortoinrcpt_tos_localparts]

        #0.Handlebounce:verifywhetherthisisabouncedemailanduseittocollectbouncedataandupdatenotificationsforcustomers
        #   Bounceregex:typicalformofbounceisbounce_alias+128-crm.lead-34@domain
        #      group(1)=themailID;group(2)=themodel(ifany);group(3)=therecordID
        #   Bouncemessage(notalias)
        #      Seehttp://datatracker.ietf.org/doc/rfc3462/?include_text=1
        #       AsallMTAdoesnotrespectthisRFC(googlemailisoneofthem),
        #      wealsoneedtoverifyifthemessagecomefrom"mailer-daemon"
        #   Ifnotabounce:resetbounceinformation
        ifbounce_aliasandany(email.startswith(bounce_alias)foremailinemail_to_localparts):
            bounce_re=re.compile("%s\+(\d+)-?([\w.]+)?-?(\d+)?"%re.escape(bounce_alias),re.UNICODE)
            bounce_match=bounce_re.search(email_to)
            ifbounce_match:
                self._routing_handle_bounce(message,message_dict)
                return[]
        ifbounce_aliasandbounce_alias_staticandany(email==bounce_aliasforemailinemail_to_localparts):
            self._routing_handle_bounce(message,message_dict)
            return[]
        ifmessage.get_content_type()=='multipart/report'oremail_from_localpart=='mailer-daemon':
            self._routing_handle_bounce(message,message_dict)
            return[]
        self._routing_reset_bounce(message,message_dict)

        #1.Handlereply
        #   ifdestination=aliaswithdifferentmodel->consideritisaforwardandnotareply
        #   ifdestination=aliaswithsamemodel->checkcontactsettingsastheystillapply
        ifreply_modelandreply_thread_id:
            other_model_aliases=self.env['mail.alias'].search([
                '&','&',
                ('alias_name','!=',False),
                ('alias_name','in',email_to_localparts),
                ('alias_model_id.model','!=',reply_model),
            ])
            ifother_model_aliases:
                is_a_reply=False
                rcpt_tos_valid_localparts=[tofortoinrcpt_tos_valid_localpartsiftoinother_model_aliases.mapped('alias_name')]

        ifis_a_reply:
            dest_aliases=self.env['mail.alias'].search([
                ('alias_name','in',rcpt_tos_localparts),
                ('alias_model_id.model','=',reply_model)
            ],limit=1)

            user_id=self._mail_find_user_for_gateway(email_from,alias=dest_aliases).idorself._uid
            route=self._routing_check_route(
                message,message_dict,
                (reply_model,reply_thread_id,custom_values,user_id,dest_aliases),
                raise_exception=False)
            ifroute:
                _logger.info(
                    'Routingmailfrom%sto%swithMessage-Id%s:directreplytomsg:model:%s,thread_id:%s,custom_values:%s,uid:%s',
                    email_from,email_to,message_id,reply_model,reply_thread_id,custom_values,self._uid)
                return[route]
            elifrouteisFalse:
                return[]

        #2.Handlenewincomingemailbycheckingaliasesandapplyingtheirsettings
        ifrcpt_tos_localparts:
            #noroutefoundforamatchingreference(orreply),soparentisinvalid
            message_dict.pop('parent_id',None)

            #checkitdoesnotdirectlycontactcatchall
            ifcatchall_aliasandemail_to_localpartsandall(email_localpart==catchall_aliasforemail_localpartinemail_to_localparts):
                _logger.info('Routingmailfrom%sto%swithMessage-Id%s:directwritetocatchall,bounce',email_from,email_to,message_id)
                body=self.env.ref('mail.mail_bounce_catchall')._render({
                    'message':message,
                },engine='ir.qweb')
                self._routing_create_bounce_email(email_from,body,message,references=message_id,reply_to=self.env.company.email)
                return[]

            dest_aliases=self.env['mail.alias'].search([('alias_name','in',rcpt_tos_valid_localparts)])
            ifdest_aliases:
                routes=[]
                foraliasindest_aliases:
                    user_id=self._mail_find_user_for_gateway(email_from,alias=alias).idorself._uid
                    route=(alias.alias_model_id.model,alias.alias_force_thread_id,ast.literal_eval(alias.alias_defaults),user_id,alias)
                    route=self._routing_check_route(message,message_dict,route,raise_exception=True)
                    ifroute:
                        _logger.info(
                            'Routingmailfrom%sto%swithMessage-Id%s:directaliasmatch:%r',
                            email_from,email_to,message_id,route)
                        routes.append(route)
                returnroutes

        #3.Fallbacktotheprovidedparameters,iftheywork
        iffallback_model:
            #noroutefoundforamatchingreference(orreply),soparentisinvalid
            message_dict.pop('parent_id',None)
            user_id=self._mail_find_user_for_gateway(email_from).idorself._uid
            route=self._routing_check_route(
                message,message_dict,
                (fallback_model,thread_id,custom_values,user_id,None),
                raise_exception=True)
            ifroute:
                _logger.info(
                    'Routingmailfrom%sto%swithMessage-Id%s:fallbacktomodel:%s,thread_id:%s,custom_values:%s,uid:%s',
                    email_from,email_to,message_id,fallback_model,thread_id,custom_values,user_id)
                return[route]

        #ValueErrorifnoroutesfoundandifnobounceoccured
        raiseValueError(
            'Nopossibleroutefoundforincomingmessagefrom%sto%s(Message-Id%s:).'
            'Createanappropriatemail.aliasorforcethedestinationmodel.'%
            (email_from,email_to,message_id)
        )

    @api.model
    def_message_route_process(self,message,message_dict,routes):
        self=self.with_context(attachments_mime_plainxml=True)#importXMLattachmentsastext
        #postponesettingmessage_dict.partner_idsaftermessage_post,toavoiddoublenotifications
        original_partner_ids=message_dict.pop('partner_ids',[])
        thread_id=False
        formodel,thread_id,custom_values,user_id,aliasinroutesor():
            subtype_id=False
            related_user=self.env['res.users'].browse(user_id)
            Model=self.env[model].with_context(mail_create_nosubscribe=True,mail_create_nolog=True)
            ifnot(thread_idandhasattr(Model,'message_update')orhasattr(Model,'message_new')):
                raiseValueError(
                    "UndeliverablemailwithMessage-Id%s,model%sdoesnotacceptincomingemails"%
                    (message_dict['message_id'],model)
                )

            #disabledsubscriptionsduringmessage_new/updatetoavoidhavingthesystemuserrunningthe
            #emailgatewaybecomeafollowerofallinboundmessages
            ModelCtx=Model.with_user(related_user).sudo()
            ifthread_idandhasattr(ModelCtx,'message_update'):
                thread=ModelCtx.browse(thread_id)
                thread.message_update(message_dict)
            else:
                #ifanewthreadiscreated,parentisirrelevant
                message_dict.pop('parent_id',None)
                thread=ModelCtx.message_new(message_dict,custom_values)
                thread_id=thread.id
                subtype_id=thread._creation_subtype().id

            #repliestointernalmessageareconsideredasnotes,butparentmessage
            #authorisaddedinrecipientstoensureheisnotifiedofaprivateanswer
            parent_message=False
            ifmessage_dict.get('parent_id'):
                parent_message=self.env['mail.message'].sudo().browse(message_dict['parent_id'])
            partner_ids=[]
            ifnotsubtype_id:
                ifmessage_dict.get('is_internal'):
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')
                    ifparent_messageandparent_message.author_id:
                        partner_ids=[parent_message.author_id.id]
                else:
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

            post_params=dict(subtype_id=subtype_id,partner_ids=partner_ids,**message_dict)
            #removecomputationalvaluesnotstoredonmail.messageandavoidwarningswhencreatingit
            forxin('from','to','cc','recipients','references','in_reply_to','bounced_email','bounced_message','bounced_msg_id','bounced_partner'):
                post_params.pop(x,None)
            new_msg=False
            ifthread._name=='mail.thread': #messagewithparent_idnotlinkedtorecord
                new_msg=thread.message_notify(**post_params)
            else:
                #parsingshouldfindanauthorindependentlyofuserrunningmailgateway,andensureitisnotflectrabot
                partner_from_found=message_dict.get('author_id')andmessage_dict['author_id']!=self.env['ir.model.data'].xmlid_to_res_id('base.partner_root')
                thread=thread.with_context(mail_create_nosubscribe=notpartner_from_found)
                new_msg=thread.message_post(**post_params)

            ifnew_msgandoriginal_partner_ids:
                #postponedaftermessage_post,becausethisisanexternalmessageandwedon'twanttocreate
                #duplicateemailsduetonotifications
                new_msg.write({'partner_ids':original_partner_ids})
        returnthread_id

    @api.model
    defmessage_process(self,model,message,custom_values=None,
                        save_original=False,strip_attachments=False,
                        thread_id=None):
        """ProcessanincomingRFC2822emailmessage,relyingon
            ``mail.message.parse()``fortheparsingoperation,
            and``message_route()``tofigureoutthetargetmodel.

            Oncethetargetmodelisknown,its``message_new``method
            iscalledwiththenewmessage(ifthethreadrecorddidnotexist)
            orits``message_update``method(ifitdid).

           :paramstringmodel:thefallbackmodeltouseifthemessage
               doesnotmatchanyofthecurrentlyconfiguredmailaliases
               (maybeNoneifamatchingaliasissupposedtobepresent)
           :parammessage:sourceoftheRFC2822message
           :typemessage:stringorxmlrpclib.Binary
           :typedictcustom_values:optionaldictionaryoffieldvalues
                topassto``message_new``ifanewrecordneedstobecreated.
                Ignoredifthethreadrecordalreadyexists,andalsoifa
                matchingmail.aliaswasfound(aliasesdefinetheirowndefaults)
           :paramboolsave_original:whethertokeepacopyoftheoriginal
                emailsourceattachedtothemessageafteritisimported.
           :paramboolstrip_attachments:whethertostripallattachments
                beforeprocessingthemessage,inordertosavesomespace.
           :paramintthread_id:optionalIDoftherecord/threadfrom``model``
               towhichthismailshouldbeattached.Whenprovided,this
               overridestheautomaticdetectionbasedonthemessage
               headers.
        """
        #extractmessagebytes-weareforcedtopassthemessageasbinarybecause
        #wedon'tknowitsencodinguntilweparseitsheadersandhencecan't
        #convertittoutf-8fortransportbetweenthemailgatescriptandhere.
        ifisinstance(message,xmlrpclib.Binary):
            message=bytes(message.data)
        ifisinstance(message,str):
            message=message.encode('utf-8')
        message=email.message_from_bytes(message,policy=email.policy.SMTP)

        #parsethemessage,verifywearenotinaloopbycheckingmessage_idisnotduplicated
        msg_dict=self.message_parse(message,save_original=save_original)
        ifstrip_attachments:
            msg_dict.pop('attachments',None)

        existing_msg_ids=self.env['mail.message'].search([('message_id','=',msg_dict['message_id'])],limit=1)
        ifexisting_msg_ids:
            _logger.info('Ignoredmailfrom%sto%swithMessage-Id%s:foundduplicatedMessage-Idduringprocessing',
                         msg_dict.get('email_from'),msg_dict.get('to'),msg_dict.get('message_id'))
            returnFalse

        #findpossibleroutesforthemessage
        routes=self.message_route(message,msg_dict,model,thread_id,custom_values)
        thread_id=self._message_route_process(message,msg_dict,routes)
        returnthread_id

    @api.model
    defmessage_new(self,msg_dict,custom_values=None):
        """Calledby``message_process``whenanewmessageisreceived
           foragiventhreadmodel,ifthemessagedidnotbelongto
           anexistingthread.
           Thedefaultbehavioristocreateanewrecordofthecorresponding
           model(basedonsomeverybasicinfoextractedfromthemessage).
           Additionalbehaviormaybeimplementedbyoverridingthismethod.

           :paramdictmsg_dict:amapcontainingtheemaildetailsand
                                 attachments.See``message_process``and
                                ``mail.message.parse``fordetails.
           :paramdictcustom_values:optionaldictionaryofadditional
                                      fieldvaluestopasstocreate()
                                      whencreatingthenewthreadrecord.
                                      Becareful,thesevaluesmayoverride
                                      anyothervaluescomingfromthemessage.
           :rtype:int
           :return:theidofthenewlycreatedthreadobject
        """
        data={}
        ifisinstance(custom_values,dict):
            data=custom_values.copy()
        fields=self.fields_get()
        name_field=self._rec_nameor'name'
        ifname_fieldinfieldsandnotdata.get('name'):
            data[name_field]=msg_dict.get('subject','')
        returnself.create(data)

    defmessage_update(self,msg_dict,update_vals=None):
        """Calledby``message_process``whenanewmessageisreceived
           foranexistingthread.Thedefaultbehavioristoupdatetherecord
           withupdate_valstakenfromtheincomingemail.
           Additionalbehaviormaybeimplementedbyoverridingthis
           method.
           :paramdictmsg_dict:amapcontainingtheemaildetailsand
                               attachments.See``message_process``and
                               ``mail.message.parse()``fordetails.
           :paramdictupdate_vals:adictcontainingvaluestoupdaterecords
                              giventheirids;ifthedictisNoneoris
                              void,nowriteoperationisperformed.
        """
        ifupdate_vals:
            self.write(update_vals)
        returnTrue

    def_message_receive_bounce(self,email,partner):
        """Calledby``message_process``whenabounceemail(suchasUndelivered
        MailReturnedtoSender)isreceivedforanexistingthread.Thedefault
        behavioristodonothing.Thismethodismeanttobeoverriddeninvarious
        modulestoaddsomespecificbehaviorlikeblacklistmanagementormass
        mailingstatisticsupdate.checkisaninteger ``message_bounce``columnexists.
        Ifitisthecase,itscontentisincremented.

        :paramstringemail:emailthatcausedthebounce;
        :paramrecordpartner:partnermatchingthebouncedemailaddress,ifany;
        """
        pass

    def_message_reset_bounce(self,email):
        """Calledby``message_process``whenanemailisconsideredasnotbeing
        abounce.Thedefaultbehavioristodonothing.Thismethodismeantto
        beoverriddeninvariousmodulestoaddsomespecificbehaviorlike
        blacklistmanagement.

        :paramstringemail:emailforwhichtoresetbounceinformation
        """
        pass

    def_message_parse_extract_payload_postprocess(self,message,payload_dict):
        """Performsomecleaning/postprocessinthebodyandattachments
        extractedfromtheemail.Notethatthisprocessingisspecifictothe
        mailmodule,andshouldnotcontainsecurityorgenerichtmlcleaning.
        Indeedthoseaspectsshouldbecoveredbythehtml_sanitizemethod
        locatedintools."""
        body,attachments=payload_dict['body'],payload_dict['attachments']
        ifnotbody.strip():
            return{'body':body,'attachments':attachments}
        try:
            root=lxml.html.fromstring(body)
        exceptValueError:
            #IncasetheemailclientsentXHTML,fromstringwillfailbecause'Unicodestrings
            #withencodingdeclarationarenotsupported'.
            root=lxml.html.fromstring(body.encode('utf-8'))

        postprocessed=False
        to_remove=[]
        fornodeinroot.iter():
            if'o_mail_notification'in(node.get('class')or'')or'o_mail_notification'in(node.get('summary')or''):
                postprocessed=True
                ifnode.getparent()isnotNone:
                    to_remove.append(node)
            ifnode.tag=='img'andnode.get('src','').startswith('cid:'):
                cid=node.get('src').split(':',1)[1]
                related_attachment=[attachforattachinattachmentsifattach[2]andattach[2].get('cid')==cid]
                ifrelated_attachment:
                    node.set('data-filename',related_attachment[0][0])
                    postprocessed=True

        fornodeinto_remove:
            node.getparent().remove(node)
        ifpostprocessed:
            body=etree.tostring(root,pretty_print=False,encoding='unicode')
        return{'body':body,'attachments':attachments}

    def_message_parse_extract_payload(self,message,save_original=False):
        """ExtractbodyasHTMLandattachmentsfromthemailmessage"""
        attachments=[]
        body=u''
        ifsave_original:
            attachments.append(self._Attachment('original_email.eml',message.as_string(),{}))

        #Becareful,content-typemaycontaintrickycontentlikeinthe
        #followingexamplesotesttheMIMEtypewithstartswith()
        #
        #Content-Type:multipart/related;
        #  boundary="_004_3f1e4da175f349248b8d43cdeb9866f1AMSPR06MB343eurprd06pro_";
        #  type="text/html"
        ifmessage.get_content_maintype()=='text':
            encoding=message.get_content_charset()
            body=message.get_content()
            body=tools.ustr(body,encoding,errors='replace')
            ifmessage.get_content_type()=='text/plain':
                #text/plain-><pre/>
                body=tools.append_content_to_html(u'',body,preserve=True)
            elifmessage.get_content_type()=='text/html':
                #weonlystrip_classeshereeverythingelsewillbedoneinbyhtmlfieldofmail.message
                body=tools.html_sanitize(body,sanitize_tags=False,strip_classes=True)
        else:
            alternative=False
            mixed=False
            html=u''
            forpartinmessage.walk():
                ifpart.get_content_type()=='binary/octet-stream':
                    _logger.warning("MessagecontaininganunexpectedContent-Type'binary/octet-stream',assuming'application/octet-stream'")
                    part.replace_header('Content-Type','application/octet-stream')
                ifpart.get_content_type()=='multipart/alternative':
                    alternative=True
                ifpart.get_content_type()=='multipart/mixed':
                    mixed=True
                ifpart.get_content_maintype()=='multipart':
                    continue #skipcontainer

                filename=part.get_filename() #Imaynotproperlyhandleallcharsets
                ifpart.get_content_type()=='text/xml'andnotpart.get_param('charset'):
                    #fortext/xmlwithomittedcharset,thecharsetisassumedtobeASCIIbythe`email`module
                    #althoughthepayloadmightbeinUTF8
                    part.set_charset('utf-8')
                encoding=part.get_content_charset() #Noneifattachment

                content=part.get_content()
                info={'encoding':encoding}
                #0)InlineAttachments->attachments,withathirdpartinthetupletomatchcid/attachment
                iffilenameandpart.get('content-id'):
                    info['cid']=part.get('content-id').strip('><')
                    attachments.append(self._Attachment(filename,content,info))
                    continue
                #1)ExplicitAttachments->attachments
                iffilenameorpart.get('content-disposition','').strip().startswith('attachment'):
                    attachments.append(self._Attachment(filenameor'attachment',content,info))
                    continue
                #2)text/plain-><pre/>
                ifpart.get_content_type()=='text/plain'and(notalternativeornotbody):
                    body=tools.append_content_to_html(body,tools.ustr(content,
                                                                         encoding,errors='replace'),preserve=True)
                #3)text/html->raw
                elifpart.get_content_type()=='text/html':
                    #mutlipart/alternativehaveonetextandahtmlpart,keeponlythesecond
                    #mixedallowsseveralhtmlparts,appendhtmlcontent
                    append_content=notalternativeor(htmlandmixed)
                    html=tools.ustr(content,encoding,errors='replace')
                    ifnotappend_content:
                        body=html
                    else:
                        body=tools.append_content_to_html(body,html,plaintext=False)
                    #weonlystrip_classeshereeverythingelsewillbedoneinbyhtmlfieldofmail.message
                    body=tools.html_sanitize(body,sanitize_tags=False,strip_classes=True)
                #4)Anythingelse->attachment
                else:
                    attachments.append(self._Attachment(filenameor'attachment',content,info))

        returnself._message_parse_extract_payload_postprocess(message,{'body':body,'attachments':attachments})

    def_message_parse_extract_bounce(self,email_message,message_dict):
        """Parseemailandextractbounceinformationtobeusedinfuture
        processing.

        :paramemail_message:anemail.messageinstance;
        :parammessage_dict:dictionaryholdingalready-parsedvalues;

        :returndict:bounce-relatedvalueswillbeadded,containing

          *bounced_email:emailthatbounced(normalized);
          *bounce_partner:res.partnerrecordsetwhoseemail_normalized=
            bounced_email;
          *bounced_msg_id:listofmessage_IDreferences(<...@myserver>)linked
            totheemailthatbounced;
          *bounced_message:iffound,mail.messagerecordsetmatchingbounced_msg_id;
        """
        ifnotisinstance(email_message,EmailMessage):
            raiseTypeError('messagemustbeanemail.message.EmailMessageatthispoint')

        email_part=next((partforpartinemail_message.walk()ifpart.get_content_type()in{'message/rfc822','text/rfc822-headers'}),None)
        dsn_part=next((partforpartinemail_message.walk()ifpart.get_content_type()=='message/delivery-status'),None)

        bounced_email=False
        bounced_partner=self.env['res.partner'].sudo()
        ifdsn_partandlen(dsn_part.get_payload())>1:
            dsn=dsn_part.get_payload()[1]
            final_recipient_data=tools.decode_message_header(dsn,'Final-Recipient')
            #oldserversmayholdvoidorinvalidFinal-Recipientheader
            iffinal_recipient_dataand";"infinal_recipient_data:
                bounced_email=tools.email_normalize(final_recipient_data.split(';',1)[1].strip())
            ifbounced_email:
                bounced_partner=self.env['res.partner'].sudo().search([('email_normalized','=',bounced_email)])

        bounced_msg_id=False
        bounced_message=self.env['mail.message'].sudo()
        ifemail_part:
            ifemail_part.get_content_type()=='text/rfc822-headers':
                #Convertthemessagebodyintoamessageitself
                email_payload=message_from_string(email_part.get_content(),policy=policy.SMTP)
            else:
                email_payload=email_part.get_payload()[0]
            bounced_msg_id=tools.mail_header_msgid_re.findall(tools.decode_message_header(email_payload,'Message-Id'))
            ifbounced_msg_id:
                bounced_message=self.env['mail.message'].sudo().search([('message_id','in',bounced_msg_id)])

        return{
            'bounced_email':bounced_email,
            'bounced_partner':bounced_partner,
            'bounced_msg_id':bounced_msg_id,
            'bounced_message':bounced_message,
        }

    @api.model
    defmessage_parse(self,message,save_original=False):
        """Parsesanemail.message.MessagerepresentinganRFC-2822email
        andreturnsagenericdictholdingthemessagedetails.

        :parammessage:emailtoparse
        :typemessage:email.message.Message
        :paramboolsave_original:whetherthereturneddictshouldinclude
            an``original``attachmentcontainingthesourceofthemessage
        :rtype:dict
        :return:Adictwiththefollowingstructure,whereeachfieldmaynot
            bepresentifmissinginoriginalmessage::

            {'message_id':msg_id,
              'subject':subject,
              'email_from':from,
              'to':to+delivered-to,
              'cc':cc,
              'recipients':delivered-to+to+cc+resent-to+resent-cc,
              'partner_ids':partnersfoundbasedonrecipientsemails,
              'body':unified_body,
              'references':references,
              'in_reply_to':in-reply-to,
              'parent_id':parentmail.messagebasedonin_reply_toorreferences,
              'is_internal':answertoaninternalmessage(note),
              'date':date,
              'attachments':[('file1','bytes'),
                              ('file2','bytes')}
            }
        """
        ifnotisinstance(message,EmailMessage):
            raiseValueError(_('MessageshouldbeavalidEmailMessageinstance'))
        msg_dict={'message_type':'email'}

        message_id=message.get('Message-Id')
        ifnotmessage_id:
            #Veryunusualsituation,beweshouldbefault-toleranthere
            message_id="<%s@localhost>"%time.time()
            _logger.debug('ParsingMessagewithoutmessage-id,generatingarandomone:%s',message_id)
        msg_dict['message_id']=message_id.strip()

        ifmessage.get('Subject'):
            msg_dict['subject']=tools.decode_message_header(message,'Subject')

        email_from=tools.decode_message_header(message,'From')
        email_cc=tools.decode_message_header(message,'cc')
        email_from_list=tools.email_split_and_format(email_from)
        email_cc_list=tools.email_split_and_format(email_cc)
        msg_dict['email_from']=email_from_list[0]ifemail_from_listelseemail_from
        msg_dict['from']=msg_dict['email_from'] #compatibilityformessage_new
        msg_dict['cc']=','.join(email_cc_list)ifemail_cc_listelseemail_cc
        #Delivered-ToisasafebetinmostmodernMTAs,butwehavetofallbackonTo+Ccvalues
        #foralltheoddMTAsoutthere,asthereisnostandardheaderfortheenvelope's`rcpt_to`value.
        msg_dict['recipients']=','.join(set(formatted_email
            foraddressin[
                tools.decode_message_header(message,'Delivered-To'),
                tools.decode_message_header(message,'To'),
                tools.decode_message_header(message,'Cc'),
                tools.decode_message_header(message,'Resent-To'),
                tools.decode_message_header(message,'Resent-Cc')
            ]ifaddress
            forformatted_emailintools.email_split_and_format(address))
        )
        msg_dict['to']=','.join(set(formatted_email
            foraddressin[
                tools.decode_message_header(message,'Delivered-To'),
                tools.decode_message_header(message,'To')
            ]ifaddress
            forformatted_emailintools.email_split_and_format(address))
        )
        partner_ids=[x.idforxinself._mail_find_partner_from_emails(tools.email_split(msg_dict['recipients']),records=self)ifx]
        msg_dict['partner_ids']=partner_ids
        #computereferencestofindifemail_messageisareplytoanexistingthread
        msg_dict['references']=tools.decode_message_header(message,'References')
        msg_dict['in_reply_to']=tools.decode_message_header(message,'In-Reply-To').strip()

        ifmessage.get('Date'):
            try:
                date_hdr=tools.decode_message_header(message,'Date')
                parsed_date=dateutil.parser.parse(date_hdr,fuzzy=True)
                ifparsed_date.utcoffset()isNone:
                    #naivedatetime,sowearbitrarilydecidetomakeit
                    #UTC,there'snobetterchoice.Shouldnothappen,
                    #asRFC2822requirestimezoneoffsetinDateheaders.
                    stored_date=parsed_date.replace(tzinfo=pytz.utc)
                else:
                    stored_date=parsed_date.astimezone(tz=pytz.utc)
            exceptException:
                _logger.info('FailedtoparseDateheader%rinincomingmail'
                             'withmessage-id%r,assumingcurrentdate/time.',
                             message.get('Date'),message_id)
                stored_date=datetime.datetime.now()
            msg_dict['date']=stored_date.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)

        parent_ids=False
        ifmsg_dict['in_reply_to']:
            parent_ids=self.env['mail.message'].search(
                [('message_id','=',msg_dict['in_reply_to'])],
                order='create_dateDESC,idDESC',
                limit=1)
        ifmsg_dict['references']andnotparent_ids:
            references_msg_id_list=tools.mail_header_msgid_re.findall(msg_dict['references'])
            parent_ids=self.env['mail.message'].search(
                [('message_id','in',[x.strip()forxinreferences_msg_id_list])],
                order='create_dateDESC,idDESC',
                limit=1)
        ifparent_ids:
            msg_dict['parent_id']=parent_ids.id
            msg_dict['is_internal']=parent_ids.subtype_idandparent_ids.subtype_id.internalorFalse

        msg_dict.update(self._message_parse_extract_payload(message,save_original=save_original))
        msg_dict.update(self._message_parse_extract_bounce(message,msg_dict))
        returnmsg_dict

    #------------------------------------------------------
    #RECIPIENTSMANAGEMENTTOOLS
    #------------------------------------------------------

    @api.model
    def_message_get_default_recipients_on_records(self,records):
        """Movedto``BaseModel._message_get_default_recipients()``"""
        returnrecords._message_get_default_recipients()

    def_message_add_suggested_recipient(self,result,partner=None,email=None,reason=''):
        """Calledby_message_get_suggested_recipients,toaddasuggested
            recipientintheresultdictionary.Theformis:
                partner_id,partner_name<partner_email>orpartner_name,reason"""
        self.ensure_one()
        partner_info={}
        ifemailandnotpartner:
            #getpartnerinfofromemail
            partner_info=self._message_partner_info_from_emails([email])[0]
            ifpartner_info.get('partner_id'):
                partner=self.env['res.partner'].sudo().browse([partner_info['partner_id']])[0]
        ifemailandemailin[val[1]forvalinresult[self.ids[0]]]: #alreadyexistingemail->skip
            returnresult
        ifpartnerandpartnerinself.message_partner_ids: #recipientalreadyinthefollowers->skip
            returnresult
        ifpartnerandpartner.idin[val[0]forvalinresult[self.ids[0]]]: #alreadyexistingpartnerID->skip
            returnresult
        ifpartnerandpartner.email: #completeprofile:id,name<email>
            result[self.ids[0]].append((partner.id,partner.email_formatted,reason))
        elifpartner: #incompleteprofile:id,name
            result[self.ids[0]].append((partner.id,partner.nameor'',reason))
        else: #unknownpartner,weareprobablymanaginganemailaddress
            result[self.ids[0]].append((False,partner_info.get('full_name')oremail,reason))
        returnresult

    def_message_get_suggested_recipients(self):
        """Returnssuggestedrecipientsforids.Thosearealistof
        tuple(partner_id,partner_name,reason),tobemanagedbyChatter."""
        result=dict((res_id,[])forres_idinself.ids)
        if'user_id'inself._fields:
            forobjinself.sudo(): #SUPERUSERbecauseofareadonres.usersthatwouldcrashotherwise
                ifnotobj.user_idornotobj.user_id.partner_id:
                    continue
                obj._message_add_suggested_recipient(result,partner=obj.user_id.partner_id,reason=self._fields['user_id'].string)
        returnresult

    def_mail_search_on_user(self,normalized_emails,extra_domain=False):
        """Findpartnerslinkedtousers,givenanemailaddressthatwill
        benormalized.Searchisdoneassudoonres.usersmodeltoavoiddomain
        onpartnerlike('user_ids','!=',False)thatwouldnotbeefficient."""
        domain=[('email_normalized','in',normalized_emails)]
        ifextra_domain:
            domain=expression.AND([domain,extra_domain])
        partners=self.env['res.users'].sudo().search(domain).mapped('partner_id')
        #returnasearchonpartnertofilterresultscurrentusershouldnotsee(multicompanyforexample)
        returnself.env['res.partner'].search([('id','in',partners.ids)])

    def_mail_search_on_partner(self,normalized_emails,extra_domain=False):
        domain=[('email_normalized','in',normalized_emails)]
        ifextra_domain:
            domain=expression.AND([domain,extra_domain])
        returnself.env['res.partner'].search(domain)

    def_mail_find_user_for_gateway(self,email,alias=None):
        """Utilitymethodtofinduserfromemailaddressthatcancreatedocuments
        inthetargetmodel.Purposeistolinkdocumentcreationtouserswhenever
        possible,forexamplewhencreatingdocumentthroughmailgateway.

        Heuristic

          *aliasownerrecord:fetchinitsfollowersforuserwithmatchingemail;
          *findanyuserwithmatchingemails;
          *tryaliasownerasfallback;

        Notethatstandardsearchorderisapplied.

        :paramstremail:willbesanitizedandparsedtofindemail;
        :parammail.aliasalias:optionalalias.Usedtofetchownerfollowers
          orfallbackuser(aliasowner);
        :paramfallback_model:ifnotalias,relatedmodeltocheckaccessrights;

        :returnres.useruser:usermatchingemailorvoidrecordsetifnonefound
        """
        #findnormalizedemailsandexcludealiases(toavoidsubscribingaliasemailstorecords)
        normalized_email=tools.email_normalize(email)
        ifnotnormalized_email:
            returnself.env['res.users']

        catchall_domain=self.env['ir.config_parameter'].sudo().get_param("mail.catchall.domain")
        ifcatchall_domain:
            left_part=normalized_email.split('@')[0]ifnormalized_email.split('@')[1]==catchall_domain.lower()elseFalse
            ifleft_part:
                ifself.env['mail.alias'].sudo().search_count([('alias_name','=',left_part)]):
                    returnself.env['res.users']

        ifaliasandalias.alias_parent_model_idandalias.alias_parent_thread_id:
            followers=self.env['mail.followers'].search([
                ('res_model','=',alias.alias_parent_model_id.model),
                ('res_id','=',alias.alias_parent_thread_id)]
            ).mapped('partner_id')
        else:
            followers=self.env['res.partner']

        follower_users=self.env['res.users'].search([
            ('partner_id','in',followers.ids),('email_normalized','=',normalized_email)
        ],limit=1)iffollowerselseself.env['res.users']
        matching_user=follower_users[0]iffollower_userselseself.env['res.users']
        ifmatching_user:
            returnmatching_user

        ifnotmatching_user:
            std_users=self.env['res.users'].sudo().search([('email_normalized','=',normalized_email)],limit=1)
            matching_user=std_users[0]ifstd_userselseself.env['res.users']
        ifmatching_user:
            returnmatching_user

        ifnotmatching_userandaliasandalias.alias_user_id:
            matching_user=aliasandalias.alias_user_id
        ifmatching_user:
            returnmatching_user

        returnmatching_user

    @api.model
    def_mail_find_partner_from_emails(self,emails,records=None,force_create=False,extra_domain=False):
        """Utilitymethodtofindpartnersfromemailaddresses.Ifnopartneris
        found,createnewpartnersifforce_createisenabled.Searchheuristics

          *0:cleanincomingemaillisttouseonlynormalizedemails.Exclude
               thoseusedinaliasestoavoidsettingpartneremailstoemails
               usedasaliases;
          *1:checkinrecords(recordset)followersifrecordsismail.thread
               enabledandifcheck_followersparameterisenabled;
          *2:searchforpartnerswithuser;
          *3:searchforpartners;

        :paramrecords:recordsetonwhichtocheckfollowers;
        :paramlistemails:listofemailaddressesforfindingpartner;
        :parambooleanforce_create:createanewpartnerifnotfound

        :returnlistpartners:alistofpartnerrecordsorderedasgivenemails.
          Ifnopartnerhasbeenfoundand/orcreatedforagivenemailsits
          matchingpartnerisanemptyrecord.
        """
        ifrecordsandisinstance(records,self.pool['mail.thread']):
            followers=records.mapped('message_partner_ids')
        else:
            followers=self.env['res.partner']
        catchall_domain=self.env['ir.config_parameter'].sudo().get_param("mail.catchall.domain")

        #first,buildanormalizedemaillistandremovethoselinkedtoaliases
        #toavoidaddingaliasesaspartners.Incaseofmulti-emailinput,use
        #thefirstfoundvalidonetobetolerantagainstmultiemailsencoding
        normalized_emails=[email_normalized
                             foremail_normalizedin(tools.email_normalize(contact,force_single=False)forcontactinemails)
                             ifemail_normalized
                            ]
        ifcatchall_domain:
            domain_left_parts=[email.split('@')[0]foremailinnormalized_emailsifemailandemail.split('@')[1]==catchall_domain.lower()]
            ifdomain_left_parts:
                found_alias_names=self.env['mail.alias'].sudo().search([('alias_name','in',domain_left_parts)]).mapped('alias_name')
                normalized_emails=[emailforemailinnormalized_emailsifemail.split('@')[0]notinfound_alias_names]

        done_partners=[followerforfollowerinfollowersiffollower.email_normalizedinnormalized_emails]
        remaining=[emailforemailinnormalized_emailsifemailnotin[partner.email_normalizedforpartnerindone_partners]]

        user_partners=self._mail_search_on_user(remaining,extra_domain=extra_domain)
        done_partners+=[user_partnerforuser_partnerinuser_partners]
        remaining=[emailforemailinnormalized_emailsifemailnotin[partner.email_normalizedforpartnerindone_partners]]

        partners=self._mail_search_on_partner(remaining,extra_domain=extra_domain)
        done_partners+=[partnerforpartnerinpartners]
        remaining=[emailforemailinnormalized_emailsifemailnotin[partner.email_normalizedforpartnerindone_partners]]

        #iterateandkeepordering
        partners=[]
        forcontactinemails:
            normalized_email=tools.email_normalize(contact,force_single=False)
            partner=next((partnerforpartnerindone_partnersifpartner.email_normalized==normalized_email),self.env['res.partner'])
            ifnotpartnerandforce_createandnormalized_emailinnormalized_emails:
                partner=self.env['res.partner'].browse(self.env['res.partner'].name_create(contact)[0])
            partners.append(partner)
        returnpartners

    def_message_partner_info_from_emails(self,emails,link_mail=False):
        """Convertalistofemailsintoalistpartner_idsandalist
            new_partner_ids.Thereturnvalueisnonconventionalbecause
            itismeanttobeusedbythemailwidget.

            :returndict:partner_idsandnew_partner_ids"""
        self.ensure_one()
        MailMessage=self.env['mail.message'].sudo()
        partners=self._mail_find_partner_from_emails(emails,records=self)
        result=list()
        foridx,contactinenumerate(emails):
            partner=partners[idx]
            partner_info={'full_name':partner.email_formattedifpartnerelsecontact,'partner_id':partner.id}
            result.append(partner_info)
            #linkmailwiththisfrommailtothenewpartnerid
            iflink_mailandpartner:
                MailMessage.search([
                    ('email_from','=ilike',partner.email_normalized),
                    ('author_id','=',False)
                ]).write({'author_id':partner.id})
        returnresult

    #------------------------------------------------------
    #MESSAGEPOSTAPI
    #------------------------------------------------------

    def_message_post_process_attachments(self,attachments,attachment_ids,message_values):
        """Preprocessattachmentsformail_thread.message_post()ormail_mail.create().

        :paramlistattachments:listofattachmenttuplesintheform``(name,content)``,#todoxdoupdatethat
                                 wherecontentisNOTbase64encoded
        :paramlistattachment_ids:alistofattachmentids,notintomanycommandform
        :paramdictmessage_data:model:themodeloftheattachmentsparentrecord,
          res_id:theidoftheattachmentsparentrecord
        """
        return_values={}
        body=message_values.get('body')
        model=message_values['model']
        res_id=message_values['res_id']

        m2m_attachment_ids=[]
        ifattachment_ids:
            #takingadvantageofcachelooksbetterinthiscase,tocheck
            filtered_attachment_ids=self.env['ir.attachment'].sudo().browse(attachment_ids).filtered(
                lambdaa:a.res_model=='mail.compose.message'anda.create_uid.id==self._uid)
            #updatefiltered(pending)attachmentstolinkthemtotheproperrecord
            iffiltered_attachment_ids:
                filtered_attachment_ids.write({'res_model':model,'res_id':res_id})
            #preventpublicandportalusersfromusingattachmentsthatarenottheirs
            ifnotself.env.user.has_group('base.group_user'):
                attachment_ids=filtered_attachment_ids.ids

            m2m_attachment_ids+=[(4,id)foridinattachment_ids]
        #Handleattachmentsparameter,thatisadictionaryofattachments

        ifattachments:#generate
            cids_in_body=set()
            names_in_body=set()
            cid_list=[]
            name_list=[]

            ifbody:
                root=lxml.html.fromstring(tools.ustr(body))
                #firstlistallattachmentsthatwillbeneededinbody
                fornodeinroot.iter('img'):
                    ifnode.get('src','').startswith('cid:'):
                        cids_in_body.add(node.get('src').split('cid:')[1])
                    elifnode.get('data-filename'):
                        names_in_body.add(node.get('data-filename'))
            attachement_values_list=[]

            #generatevalues
            forattachmentinattachments:
                cid=False
                iflen(attachment)==2:
                    name,content=attachment
                    info={}
                eliflen(attachment)==3:
                    name,content,info=attachment
                    cid=infoandinfo.get('cid')
                else:
                    continue
                ifisinstance(content,str):
                    encoding=infoandinfo.get('encoding')
                    try:
                        content=content.encode(encodingor"utf-8")
                    exceptUnicodeEncodeError:
                        content=content.encode("utf-8")
                elifisinstance(content,EmailMessage):
                    content=content.as_bytes()
                elifcontentisNone:
                    continue
                attachement_values={
                    'name':name,
                    'datas':base64.b64encode(content),
                    'type':'binary',
                    'description':name,
                    'res_model':model,
                    'res_id':res_id,
                }
                ifbodyand(cidandcidincids_in_bodyornameinnames_in_body):
                    attachement_values['access_token']=self.env['ir.attachment']._generate_access_token()
                attachement_values_list.append(attachement_values)
                #keepcidandnamelistsyncedwithattachement_values_listlengthtomatchidslatter
                cid_list.append(cid)
                name_list.append(name)
            new_attachments=self.env['ir.attachment'].create(attachement_values_list)
            cid_mapping={}
            name_mapping={}
            forcounter,new_attachmentinenumerate(new_attachments):
                cid=cid_list[counter]
                if'access_token'inattachement_values_list[counter]:
                    ifcid:
                        cid_mapping[cid]=(new_attachment.id,attachement_values_list[counter]['access_token'])
                    name=name_list[counter]
                    name_mapping[name]=(new_attachment.id,attachement_values_list[counter]['access_token'])
                m2m_attachment_ids.append((4,new_attachment.id))

            #note:rightknowweareonlytakingattachmentsandignoringattachment_ids.
            if(cid_mappingorname_mapping)andbody:
                postprocessed=False
                fornodeinroot.iter('img'):
                    attachment_data=False
                    ifnode.get('src','').startswith('cid:'):
                        cid=node.get('src').split('cid:')[1]
                        attachment_data=cid_mapping.get(cid)
                    ifnotattachment_dataandnode.get('data-filename'):
                        attachment_data=name_mapping.get(node.get('data-filename'),False)
                    ifattachment_data:
                        node.set('src','/web/image/%s?access_token=%s'%attachment_data)
                        postprocessed=True
                ifpostprocessed:
                    return_values['body']=lxml.html.tostring(root,pretty_print=False,encoding='unicode')
        return_values['attachment_ids']=m2m_attachment_ids
        returnreturn_values

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,*,
                     body='',subject=None,message_type='notification',
                     email_from=None,author_id=None,parent_id=False,
                     subtype_xmlid=None,subtype_id=False,partner_ids=None,channel_ids=None,
                     attachments=None,attachment_ids=None,
                     add_sign=True,record_name=False,
                     **kwargs):
        """Postanewmessageinanexistingthread,returningthenew
            mail.messageID.
            :paramstrbody:bodyofthemessage,usuallyrawHTMLthatwill
                besanitized
            :paramstrsubject:subjectofthemessage
            :paramstrmessage_type:seemail_message.message_typefield.Canbeanythingbut
                user_notification,reservedformessage_notify
            :paramintparent_id:handlethreadformation
            :paramintsubtype_id:subtype_idofthemessage,mainlyusefore
                followersmechanism
            :paramlist(int)partner_ids:partner_idstonotify
            :paramlist(int)channel_ids:channel_idstonotify
            :paramlist(tuple(str,str),tuple(str,str,dict)orint)attachments:listofattachmenttuplesintheform
                ``(name,content)``or``(name,content,info)``,wherecontentisNOTbase64encoded
            :paramlistidattachment_ids:listofexistingattachementtolinktothismessage
                -Shouldonlybesettedbychatter
                -Attachementobjectattachedtomail.compose.message(0)willbeattached
                    totherelateddocument.
            Extrakeywordargumentswillbeusedasdefaultcolumnvaluesforthe
            newmail.messagerecord.
            :returnint:IDofnewlycreatedmail.message
        """
        self.ensure_one() #shouldalwaysbepostedonarecord,usemessage_notifyifnorecord
        #splitmessageadditionalvaluesfromnotifyadditionalvalues
        msg_kwargs=dict((key,val)forkey,valinkwargs.items()ifkeyinself.env['mail.message']._fields)
        notif_kwargs=dict((key,val)forkey,valinkwargs.items()ifkeynotinmsg_kwargs)

        ifself._name=='mail.thread'ornotself.idormessage_type=='user_notification':
            raiseValueError('message_postshouldonlybecalltopostmessageonrecord.Usemessage_notifyinstead')

        if'model'inmsg_kwargsor'res_id'inmsg_kwargs:
            raiseValueError("message_postdoesn'tsupportmodelandres_idparametersanymore.Pleasecallmessage_postonrecord.")
        if'subtype'inkwargs:
            raiseValueError("message_postdoesn'tsupportsubtypeparameteranymore.Pleasegiveavalidsubtype_idorsubtype_xmlidvalueinstead.")

        self=self._fallback_lang()#addlangtocontextimediatlysinceitwillbeusefullinvariousflowslatter.

        #Explicitaccessrightscheck,becausedisplay_nameiscomputedassudo.
        self.check_access_rights('read')
        self.check_access_rule('read')
        record_name=record_nameorself.display_name

        partner_ids=set(partner_idsor[])
        channel_ids=set(channel_idsor[])

        ifany(notisinstance(pc_id,int)forpc_idinpartner_ids|channel_ids):
            raiseValueError('message_postpartner_idsandchannel_idsmustbeintegerlist,notcommands')

        #Findthemessage'sauthor
        author_id,email_from=self._message_compute_author(author_id,email_from,raise_exception=True)

        ifsubtype_xmlid:
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id(subtype_xmlid)
        ifnotsubtype_id:
            subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note')

        #automaticallysubscriberecipientsifaskedto
        ifself._context.get('mail_post_autofollow')andpartner_ids:
            self.message_subscribe(list(partner_ids))

        #parentmanagement,dependingon``_mail_flat_thread``
        #``_mail_flat_thread``True:nofreemessage.Ifnoparent,findthefirst
        #postedmessageandattachnewmessagetoit.Ifparent,getbacktothefirst
        #ancestorandattachit.Wedon'tkeephierarchy(onelevelofthreading).
        #``_mail_flat_thread``False:freemessage=newthread(thinkofmailinglists).
        #Ifparentgetuponeleveltotrytoflattenthreadswithoutcompletely
        #removinghierarchy.
        MailMessage_sudo=self.env['mail.message'].sudo()
        ifself._mail_flat_threadandnotparent_id:
            parent_message=MailMessage_sudo.search([('res_id','=',self.id),('model','=',self._name),('message_type','!=','user_notification')],order="idASC",limit=1)
            #parent_messagesearchedinsudoforperformance,onlyusedforid.
            #Notethatwithsudowewillmatchmessagewithinternalsubtypes.
            parent_id=parent_message.idifparent_messageelseFalse
        elifparent_id:
            current_ancestor=MailMessage_sudo.search([('id','=',parent_id),('parent_id','!=',False)])
            ifself._mail_flat_thread:
                ifcurrent_ancestor:
                    #avoidloopswhenfindingancestors
                    processed_list=[]
                    while(current_ancestor.parent_idandcurrent_ancestor.parent_idnotinprocessed_list):
                        processed_list.append(current_ancestor)
                        current_ancestor=current_ancestor.parent_id
                    parent_id=current_ancestor.id
            else:
                parent_id=current_ancestor.parent_id.idifcurrent_ancestor.parent_idelseparent_id

        values=dict(msg_kwargs)
        values.update({
            'author_id':author_id,
            'email_from':email_from,
            'model':self._name,
            'res_id':self.id,
            'body':body,
            'subject':subjectorFalse,
            'message_type':message_type,
            'parent_id':parent_id,
            'subtype_id':subtype_id,
            'partner_ids':partner_ids,
            'channel_ids':channel_ids,
            'add_sign':add_sign,
            'record_name':record_name,
        })
        attachments=attachmentsor[]
        attachment_ids=attachment_idsor[]
        attachement_values=self._message_post_process_attachments(attachments,attachment_ids,values)
        values.update(attachement_values) #attachement_ids,[body]

        new_message=self._message_create(values)

        #Setmainattachmentfieldifnecessary
        self._message_set_main_attachment_id(values['attachment_ids'])

        ifvalues['author_id']andvalues['message_type']!='notification'andnotself._context.get('mail_create_nosubscribe'):
            ifself.env['res.partner'].browse(values['author_id']).active: #wedontwanttoaddflectrabot/inactiveasafollower
                self._message_subscribe([values['author_id']])

        self._message_post_after_hook(new_message,values)
        self._notify_thread(new_message,values,**notif_kwargs)
        returnnew_message

    def_message_set_main_attachment_id(self,attachment_ids): #todomovethisoutofmail.thread
        ifnotself._abstractandattachment_idsandnotself.message_main_attachment_id:
            all_attachments=self.env['ir.attachment'].browse([attachment_tuple[1]forattachment_tupleinattachment_ids])
            prioritary_attachments=all_attachments.filtered(lambdax:x.mimetype.endswith('pdf'))\
                                     orall_attachments.filtered(lambdax:x.mimetype.startswith('image'))\
                                     orall_attachments
            self.sudo().with_context(tracking_disable=True).write({'message_main_attachment_id':prioritary_attachments[0].id})

    def_message_post_after_hook(self,message,msg_vals):
        """Hooktoaddcustombehaviorafterhavingpostedthemessage.Both
        messageandcomputedvaluearegiven,totrytolessenquerycountby
        usingalready-computedvaluesinsteadofhavingtorebrowsethings."""
        pass

    #------------------------------------------------------
    #MESSAGEPOSTTOOLS
    #------------------------------------------------------

    defmessage_post_with_view(self,views_or_xmlid,**kwargs):
        """Helpermethodtosendamail/postamessageusingaview_idto
        renderusingtheir.qwebengine.Thismethodisstandalone,because
        thereisnothingintemplateandcomposerthatallowstohandle
        viewsinbatch.Thismethodshouldprobablydisappearwhentemplates
        handleiruiviews."""
        values=kwargs.pop('values',None)ordict()
        try:
            fromflectra.addons.http_routing.models.ir_httpimportslug
            values['slug']=slug
        exceptImportError:
            values['slug']=lambdaself:self.id
        ifisinstance(views_or_xmlid,str):
            views=self.env.ref(views_or_xmlid,raise_if_not_found=False)
        else:
            views=views_or_xmlid
        ifnotviews:
            return
        forrecordinself:
            values['object']=record
            rendered_template=views._render(values,engine='ir.qweb',minimal_qcontext=True)
            kwargs['body']=rendered_template
            record.message_post_with_template(False,**kwargs)

    defmessage_post_with_template(self,template_id,email_layout_xmlid=None,auto_commit=False,**kwargs):
        """Helpermethodtosendamailwithatemplate
            :paramtemplate_id:theidofthetemplatetorendertocreatethebodyofthemessage
            :param**kwargs:parametertocreateamail.compose.messagewoaerd(whichinheritfrommail.message)
        """
        #Getcompositionmode,orforceitaccordingtothenumberofrecordinself
        ifnotkwargs.get('composition_mode'):
            kwargs['composition_mode']='comment'iflen(self.ids)==1else'mass_mail'
        ifnotkwargs.get('message_type'):
            kwargs['message_type']='notification'
        res_id=kwargs.get('res_id',self.idsandself.ids[0]or0)
        res_ids=kwargs.get('res_id')and[kwargs['res_id']]orself.ids

        #Createthecomposer
        composer=self.env['mail.compose.message'].with_context(
            active_id=res_id,
            active_ids=res_ids,
            active_model=kwargs.get('model',self._name),
            default_composition_mode=kwargs['composition_mode'],
            default_model=kwargs.get('model',self._name),
            default_res_id=res_id,
            default_template_id=template_id,
            custom_layout=email_layout_xmlid,
        ).create(kwargs)
        #Simulatetheonchange(liketriggerinformtheview)only
        #whenhavingatemplateinsingle-emailmode
        iftemplate_id:
            update_values=composer.onchange_template_id(template_id,kwargs['composition_mode'],self._name,res_id)['value']
            composer.write(update_values)
        returncomposer.send_mail(auto_commit=auto_commit)

    defmessage_notify(self,*,
                       partner_ids=False,parent_id=False,model=False,res_id=False,
                       author_id=None,email_from=None,body='',subject=False,**kwargs):
        """Shortcutallowingtonotifypartnersofmessagesthatshouldn'tbe
        displayedonadocument.Itpushesnotificationsoninboxorbyemaildepending
        ontheuserconfiguration,likeothernotifications."""
        ifself:
            self.ensure_one()
        #splitmessageadditionalvaluesfromnotifyadditionalvalues
        msg_kwargs=dict((key,val)forkey,valinkwargs.items()ifkeyinself.env['mail.message']._fields)
        notif_kwargs=dict((key,val)forkey,valinkwargs.items()ifkeynotinmsg_kwargs)

        author_id,email_from=self._message_compute_author(author_id,email_from,raise_exception=True)

        ifnotpartner_ids:
            _logger.warning('Messagenotifycalledwithoutrecipient_ids,skipping')
            returnself.env['mail.message']

        ifnot(modelandres_id): #bothvalueshouldbesetornoneshouldbeset(record)
            model=False
            res_id=False

        MailThread=self.env['mail.thread']
        values={
            'parent_id':parent_id,
            'model':self._nameifselfelsemodel,
            'res_id':self.idifselfelseres_id,
            'message_type':'user_notification',
            'subject':subject,
            'body':body,
            'author_id':author_id,
            'email_from':email_from,
            'partner_ids':partner_ids,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'is_internal':True,
            'record_name':False,
            'reply_to':MailThread._notify_get_reply_to(default=email_from,records=None)[False],
            'message_id':tools.generate_tracking_message_id('message-notify'),
        }
        values.update(msg_kwargs)
        new_message=MailThread._message_create(values)
        MailThread._notify_thread(new_message,values,**notif_kwargs)
        returnnew_message

    def_message_log(self,*,body='',author_id=None,email_from=None,subject=False,message_type='notification',**kwargs):
        """Shortcutallowingtopostnoteonadocument.Itdoesnotperform
        anynotificationandpre-computessomevaluestohaveashortcode
        asoptimizedaspossible.Thismethodisprivateasitdoesnotcheck
        accessrightsandperformthemessagecreationassudotospeedup
        thelogprocess.Thismethodshouldbecalledwithinmethodswhere
        accessrightsarealreadygrantedtoavoidprivilegeescalation."""
        self.ensure_one()
        author_id,email_from=self._message_compute_author(author_id,email_from,raise_exception=False)

        message_values={
            'subject':subject,
            'body':body,
            'author_id':author_id,
            'email_from':email_from,
            'message_type':message_type,
            'model':kwargs.get('model',self._name),
            'res_id':self.ids[0]ifself.idselseFalse,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'is_internal':True,
            'record_name':False,
            'reply_to':self.env['mail.thread']._notify_get_reply_to(default=email_from,records=None)[False],
            'message_id':tools.generate_tracking_message_id('message-notify'), #why?thisisallbutanotify
        }
        message_values.update(kwargs)
        returnself.sudo()._message_create(message_values)

    def_message_log_batch(self,bodies,author_id=None,email_from=None,subject=False,message_type='notification'):
        """Shortcutallowingtopostnotesonabatchofdocuments.Itachievethe
        samepurposeas_message_log,doneinbatchtospeedupquicknotelog.

          :parambodies:dict{record_id:body}
        """
        author_id,email_from=self._message_compute_author(author_id,email_from,raise_exception=False)

        base_message_values={
            'subject':subject,
            'author_id':author_id,
            'email_from':email_from,
            'message_type':message_type,
            'model':self._name,
            'subtype_id':self.env['ir.model.data'].xmlid_to_res_id('mail.mt_note'),
            'is_internal':True,
            'record_name':False,
            'reply_to':self.env['mail.thread']._notify_get_reply_to(default=email_from,records=None)[False],
            'message_id':tools.generate_tracking_message_id('message-notify'), #why?thisisallbutanotify
        }
        values_list=[dict(base_message_values,
                            res_id=record.id,
                            body=bodies.get(record.id,''))
                       forrecordinself]
        returnself.sudo()._message_create(values_list)

    def_message_compute_author(self,author_id=None,email_from=None,raise_exception=True):
        """Toolmethodcomputingauthorinformationformessages.Purposeis
        toensuremaximumcoherencebetweenauthor/currentuser/email_from
        whensendingemails."""
        ifauthor_idisNone:
            ifemail_from:
                author=self._mail_find_partner_from_emails([email_from])[0]
            else:
                author=self.env.user.partner_id
                email_from=author.email_formatted
            author_id=author.id

        ifemail_fromisNone:
            ifauthor_id:
                author=self.env['res.partner'].browse(author_id)
                email_from=author.email_formatted

        #superusermodewithoutauthoremail->probablypublicuser;anywaywedon'twanttocrash
        ifnotemail_fromandnotself.env.suandraise_exception:
            raiseexceptions.UserError(_("Unabletologmessage,pleaseconfigurethesender'semailaddress."))

        returnauthor_id,email_from

    def_message_create(self,values_list):
        ifnotisinstance(values_list,(list)):
            values_list=[values_list]
        create_values_list=[]
        forvaluesinvalues_list:
            create_values=dict(values)
            #Avoidwarningsaboutnon-existingfields
            forxin('from','to','cc','canned_response_ids'):
                create_values.pop(x,None)
            create_values['partner_ids']=[(4,pid)forpidincreate_values.get('partner_ids',[])]
            create_values['channel_ids']=[(4,cid)forcidincreate_values.get('channel_ids',[])]
            create_values_list.append(create_values)

        #removecontext,notablyfordefaultkeys,asthisthreadmethodisnot
        #meanttopropagatedefaultvaluesformessages,onlyformasterrecords
        returnself.env['mail.message'].with_context(
            clean_context(self.env.context)
        ).create(create_values_list)

    #------------------------------------------------------
    #NOTIFICATIONAPI
    #------------------------------------------------------

    def_notify_thread(self,message,msg_vals=False,notify_by_email=True,**kwargs):
        """Mainnotificationmethod.Thismethodbasicallydoestwothings

         *call``_notify_compute_recipients``thatcomputesrecipientsto
           notifybasedonmessagerecordormessagecreationvaluesifgiven
           (tooptimizeperformanceifwealreadyhavedatacomputed);
         *performsthenotificationprocessbycallingthevariousnotification
           methodsimplemented;

        Thismethodcnnbeoverriddentointerceptandpostponenotification
        mechanismlikemail.channelmoderation.

        :parammessage:mail.messagerecordtonotify;
        :parammsg_vals:dictionaryofvaluesusedtocreatethemessage.Ifgiven
          itisusedinsteadofaccessing``self``tolessenquerycountinsome
          simplecaseswherenonotificationisactuallyrequired;

        Kwargsallowtopassvariousparametersthataregiventosubnotification
        methods.Seethosemethodsformoredetailsabouttheadditionalparameters.
        Parametersusedforemail-stylenotifications
        """
        msg_vals=msg_valsifmsg_valselse{}
        rdata=self._notify_compute_recipients(message,msg_vals)
        ifnotrdata:
            returnFalse

        message_values={}
        ifrdata['channels']:
            message_values['channel_ids']=[(6,0,[r['id']forrinrdata['channels']])]

        self._notify_record_by_inbox(message,rdata,msg_vals=msg_vals,**kwargs)
        ifnotify_by_email:
            self._notify_record_by_email(message,rdata,msg_vals=msg_vals,**kwargs)

        returnrdata

    def_notify_record_by_inbox(self,message,recipients_data,msg_vals=False,**kwargs):
        """Notificationmethod:inbox.Dotwomainthings

          *createaninboxnotificationforusers;
          *createchannel/messagelink(channel_idsfieldofmail.message);
          *sendbusnotifications;

        TDE/XDOTODO:flagrdatadirectly,withforexampler['notif']='ocn_client'andr['needaction']=False
        andcorrectlyoverridenotify_recipients
        """
        channel_ids=[r['id']forrinrecipients_data['channels']]
        ifchannel_ids:
            message.write({'channel_ids':[(6,0,channel_ids)]})

        inbox_pids=[r['id']forrinrecipients_data['partners']ifr['notif']=='inbox']
        ifinbox_pids:
            notif_create_values=[{
                'mail_message_id':message.id,
                'res_partner_id':pid,
                'notification_type':'inbox',
                'notification_status':'sent',
            }forpidininbox_pids]
            self.env['mail.notification'].sudo().create(notif_create_values)

        bus_notifications=[]
        ifinbox_pidsorchannel_ids:
            message_format_values=False
            ifinbox_pids:
                message_format_values=message.message_format()[0]
                forpartner_idininbox_pids:
                    bus_notifications.append([(self._cr.dbname,'ir.needaction',partner_id),dict(message_format_values)])
            ifchannel_ids:
                channels=self.env['mail.channel'].sudo().browse(channel_ids)
                bus_notifications+=channels._channel_message_notifications(message,message_format_values)

        ifbus_notifications:
            self.env['bus.bus'].sudo().sendmany(bus_notifications)

    def_notify_record_by_email(self,message,recipients_data,msg_vals=False,
                                model_description=False,mail_auto_delete=True,check_existing=False,
                                force_send=True,send_after_commit=True,
                                **kwargs):
        """Methodtosendemaillinkedtonotifiedmessages.

        :parammessage:mail.messagerecordtonotify;
        :paramrecipients_data:see``_notify_thread``;
        :parammsg_vals:see``_notify_thread``;

        :parammodel_description:modeldescriptionusedinemailnotificationprocess
          (computedifnotgiven);
        :parammail_auto_delete:deletenotificationemailsoncesent;
        :paramcheck_existing:checkforexistingnotificationstoupdatebasedon
          mailedrecipient,otherwisecreatenewnotifications;

        :paramforce_send:sendemailsdirectlyinsteadofusingqueue;
        :paramsend_after_commit:ifforce_send,tellswhethertosendemailsafter
          thetransactionhasbeencommittedusingapost-commithook;
        """
        partners_data=[rforrinrecipients_data['partners']ifr['notif']=='email']
        ifnotpartners_data:
            returnTrue

        model=msg_vals.get('model')ifmsg_valselsemessage.model
        model_name=model_descriptionor(self._fallback_lang().env['ir.model']._get(model).display_nameifmodelelseFalse)#onequeryfordisplayname
        recipients_groups_data=self._notify_classify_recipients(partners_data,model_name,msg_vals=msg_vals)

        ifnotrecipients_groups_data:
            returnTrue
        force_send=self.env.context.get('mail_notify_force_send',force_send)

        template_values=self._notify_prepare_template_context(message,msg_vals,model_description=model_description)#10queries

        email_layout_xmlid=msg_vals.get('email_layout_xmlid')ifmsg_valselsemessage.email_layout_xmlid
        template_xmlid=email_layout_xmlidifemail_layout_xmlidelse'mail.message_notification_email'
        try:
            base_template=self.env.ref(template_xmlid,raise_if_not_found=True).with_context(lang=template_values['lang'])#1query
        exceptValueError:
            _logger.warning('QWebtemplate%snotfoundwhensendingnotificationemails.Sendingwithoutlayouting.'%(template_xmlid))
            base_template=False

        mail_subject=message.subjector(message.record_nameand'Re:%s'%message.record_name)#incache,noqueries
        #Replacenewlinesbyspacestoconformtoemailheadersrequirements
        mail_subject=''.join((mail_subjector'').splitlines())
        #computereferences:setreferencestotheparentandaddcurrentmessagejustto
        #haveafallbackincaserepliesmesswithMesssage-IdintheIn-Reply-To(e.g.amazon
        #SESSMTPmayreplaceMessage-IdandIn-Reply-TorefersaninternalIDnotstoredinFlectra)
        message_sudo=message.sudo()
        ifmessage_sudo.parent_id:
            references=f'{message_sudo.parent_id.message_id}{message_sudo.message_id}'
        else:
            references=message_sudo.message_id
        #preparenotificationmailvalues
        base_mail_values={
            'mail_message_id':message.id,
            'mail_server_id':message.mail_server_id.id,#2query,checkacces+read,maybeuseless,Falsy,whenwillitbeused?
            'auto_delete':mail_auto_delete,
            #duetoir.rule,userhavenorighttoaccessparentmessageifmessageisnotpublished
            'references':references,
            'subject':mail_subject,
        }
        base_mail_values=self._notify_by_email_add_values(base_mail_values)

        #Cleanthecontexttogetridofresidualdefault_*keysthatcouldcauseissuesduring
        #themail.mailcreation.
        #Example:'default_state'wouldrefertothedefaultstateofapreviouslycreatedrecord
        #fromanothermodelthatinturnstriggersanassignationnotificationthatendsuphere.
        #Thiswillleadtoatracebackwhentryingtocreateamail.mailwiththisstatevaluethat
        #doesn'texist.
        SafeMail=self.env['mail.mail'].sudo().with_context(clean_context(self._context))
        SafeNotification=self.env['mail.notification'].sudo().with_context(clean_context(self._context))
        emails=self.env['mail.mail'].sudo()

        #loopongroups(customer,portal,user, ...+modelspecificlikegroup_sale_salesman)
        notif_create_values=[]
        recipients_max=50
        forrecipients_group_datainrecipients_groups_data:
            #generatenotificationemailcontent
            recipients_ids=recipients_group_data.pop('recipients')
            render_values={**template_values,**recipients_group_data}
            #{company,is_discussion,lang,message,model_description,record,record_name,signature,subtype,tracking_values,website_url}
            #{actions,button_access,has_button_access,recipients}

            ifbase_template:
                mail_body=base_template._render(render_values,engine='ir.qweb',minimal_qcontext=True)
            else:
                mail_body=message.body
            mail_body=self.env['mail.render.mixin']._replace_local_links(mail_body)

            #createemail
            forrecipients_ids_chunkinsplit_every(recipients_max,recipients_ids):
                recipient_values=self._notify_email_recipient_values(recipients_ids_chunk)
                email_to=recipient_values['email_to']
                recipient_ids=recipient_values['recipient_ids']

                create_values={
                    'body_html':mail_body,
                    'subject':mail_subject,
                    'recipient_ids':[(4,pid)forpidinrecipient_ids],
                }
                ifemail_to:
                    create_values['email_to']=email_to
                create_values.update(base_mail_values) #mail_message_id,mail_server_id,auto_delete,references,headers
                email=SafeMail.create(create_values)

                ifemailandrecipient_ids:
                    tocreate_recipient_ids=list(recipient_ids)
                    ifcheck_existing:
                        existing_notifications=self.env['mail.notification'].sudo().search([
                            ('mail_message_id','=',message.id),
                            ('notification_type','=','email'),
                            ('res_partner_id','in',tocreate_recipient_ids)
                        ])
                        ifexisting_notifications:
                            tocreate_recipient_ids=[ridforridinrecipient_idsifridnotinexisting_notifications.mapped('res_partner_id.id')]
                            existing_notifications.write({
                                'notification_status':'ready',
                                'mail_id':email.id,
                            })
                    notif_create_values+=[{
                        'mail_message_id':message.id,
                        'res_partner_id':recipient_id,
                        'notification_type':'email',
                        'mail_id':email.id,
                        'is_read':True, #discardInboxnotification
                        'notification_status':'ready',
                    }forrecipient_idintocreate_recipient_ids]
                emails|=email

        ifnotif_create_values:
            SafeNotification.create(notif_create_values)

        #NOTE:
        #  1.formorethan50followers,usethequeuesystem
        #  2.donotsendemailsimmediatelyiftheregistryisnotloaded,
        #     topreventsendingemailduringasimpleupdateofthedatabase
        #     usingthecommand-line.
        test_mode=getattr(threading.currentThread(),'testing',False)
        ifforce_sendandlen(emails)<recipients_maxand(notself.pool._initortest_mode):
            #unlessaskedspecifically,sendemailsafterthetransactionto
            #avoidsideeffectsduetoemailsbeingsentwhilethetransactionfails
            ifnottest_modeandsend_after_commit:
                email_ids=emails.ids
                dbname=self.env.cr.dbname
                _context=self._context

                @self.env.cr.postcommit.add
                defsend_notifications():
                    db_registry=registry(dbname)
                    withapi.Environment.manage(),db_registry.cursor()ascr:
                        env=api.Environment(cr,SUPERUSER_ID,_context)
                        env['mail.mail'].browse(email_ids).send()
            else:
                emails.send()

        returnTrue

    @api.model
    def_notify_prepare_template_context(self,message,msg_vals,model_description=False,mail_auto_delete=True):
        #computesenduseranditsrelatedsignature
        signature=''
        user=self.env.user
        author=message.env['res.partner'].browse(msg_vals.get('author_id'))ifmsg_valselsemessage.author_id
        model=msg_vals.get('model')ifmsg_valselsemessage.model
        add_sign=msg_vals.get('add_sign')ifmsg_valselsemessage.add_sign
        subtype_id=msg_vals.get('subtype_id')ifmsg_valselsemessage.subtype_id.id
        message_id=message.id
        record_name=msg_vals.get('record_name')ifmsg_valselsemessage.record_name
        author_user=userifuser.partner_id==authorelseauthor.user_ids[0]ifauthorandauthor.user_idselseFalse
        #tryingtouseuser(self.env.user)insteadofbrowinguser_idsifheistheauthorwillgiveasudouser,
        #improvingaccessperformancesandcacheusage.
        ifauthor_user:
            user=author_user
            ifadd_sign:
                signature=user.signature
        else:
            ifadd_sign:
                signature="<p>--<br/>%s</p>"%author.name

        #companyvalueshouldfallbackonenv.companyif:
        #-nocompany_idfieldonrecord
        #-company_idfieldavailablebutnotset
        company=self.company_id.sudo()ifselfand'company_id'inselfandself.company_idelseself.env.company
        ifcompany.website:
            website_url='http://%s'%company.websiteifnotcompany.website.lower().startswith(('http:','https:'))elsecompany.website
        else:
            website_url=False

        #Retrievethelanguageinwhichthetemplatewasrendered,inordertorenderthecustom
        #layoutinthesamelanguage.
        #TDEFIXME:thiswholebrolshouldbecleaned!
        lang=self.env.context.get('lang')
        if{'default_template_id','default_model','default_res_id'}<=self.env.context.keys():
            template=self.env['mail.template'].browse(self.env.context['default_template_id'])
            iftemplateandtemplate.lang:
                lang=template._render_lang([self.env.context['default_res_id']])[self.env.context['default_res_id']]

        ifnotmodel_descriptionandmodel:
            model_description=self.env['ir.model'].with_context(lang=lang)._get(model).display_name

        tracking=[]
        ifmsg_vals.get('tracking_value_ids',True)ifmsg_valselsebool(self):#couldbetracking
            fortracking_valueinself.env['mail.tracking.value'].sudo().search([('mail_message_id','=',message.id)]):
                groups=tracking_value.field_groups
                ifnotgroupsorself.env.is_superuser()orself.user_has_groups(groups):
                    tracking.append((tracking_value.field_desc,
                                    tracking_value.get_old_display_value()[0],
                                    tracking_value.get_new_display_value()[0]))

        is_discussion=subtype_id==self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

        return{
            'message':message,
            'signature':signature,
            'website_url':website_url,
            'company':company,
            'model_description':model_description,
            'record':self,
            'record_name':record_name,
            'tracking_values':tracking,
            'is_discussion':is_discussion,
            'subtype':message.subtype_id,
            'lang':lang,
        }

    def_notify_by_email_add_values(self,base_mail_values):
        """Addmodel-specificvaluestothedictionaryusedtocreatethe
        notificationemail.Itsbasebehavioristocomputemodel-specific
        headers.

        :paramdictbase_mail_values:basemail.mailvalues,holdingmessage
        tonotify(mail_message_idanditsfields),server,references,subject.
        """
        headers=self._notify_email_headers()
        ifheaders:
            base_mail_values['headers']=headers
        returnbase_mail_values

    def_notify_compute_recipients(self,message,msg_vals):
        """Computerecipientstonotifybasedonsubtypeandfollowers.This
        methodreturnsdatastructuredasexpectedfor``_notify_recipients``."""
        msg_sudo=message.sudo()
        #getvaluesfrommsg_valsorfrommessageifmsg_valsdoen'texists
        pids=msg_vals.get('partner_ids',[])ifmsg_valselsemsg_sudo.partner_ids.ids
        cids=msg_vals.get('channel_ids',[])ifmsg_valselsemsg_sudo.channel_ids.ids
        message_type=msg_vals.get('message_type')ifmsg_valselsemsg_sudo.message_type
        subtype_id=msg_vals.get('subtype_id')ifmsg_valselsemsg_sudo.subtype_id.id
        #isitpossibletohaverecordbutnosubtype_id?
        recipient_data={
            'partners':[],
            'channels':[],
        }
        res=self.env['mail.followers']._get_recipient_data(self,message_type,subtype_id,pids,cids)
        ifnotres:
            returnrecipient_data

        author_id=msg_vals.get('author_id')ormessage.author_id.id
        forpid,cid,active,pshare,ctype,notif,groupsinres:
            ifpidandpid==author_idandnotself.env.context.get('mail_notify_author'): #donotnotifytheauthorofitsownmessages
                continue
            ifpid:
                ifactiveisFalse:
                    continue
                pdata={'id':pid,'active':active,'share':pshare,'groups':groupsor[]}
                ifnotif=='inbox':
                    recipient_data['partners'].append(dict(pdata,notif=notif,type='user'))
                elifnotpshareandnotif: #hasanuserandisnotshared,isthereforeuser
                    recipient_data['partners'].append(dict(pdata,notif=notif,type='user'))
                elifpshareandnotif: #hasanuserbutisshared,isthereforeportal
                    recipient_data['partners'].append(dict(pdata,notif=notif,type='portal'))
                else: #hasnouser,isthereforecustomer
                    recipient_data['partners'].append(dict(pdata,notif=notififnotifelse'email',type='customer'))
            elifcid:
                recipient_data['channels'].append({'id':cid,'notif':notif,'type':ctype})

        #addpartneridsinemailchannels
        email_cids=[r['id']forrinrecipient_data['channels']ifr['notif']=='email']
        ifemail_cids:
            #wearedoingasimilarsearchinocn_client
            #Couldbeinterestingtomakeeverythinginasinglequery.
            #ocn_client:(searchingallpartnerslinkedtochannelsoftypechat).
            #here     :(searchingallpartnerslinkedtochannelswithnotifemailifemailisnottheauthorone)
            #TDEFIXME:useemail_sanitized
            email_from=msg_vals.get('email_from')ormessage.email_from
            email_from=self.env['res.partner']._parse_partner_name(email_from)[1]
            exept_partner=[r['id']forrinrecipient_data['partners']]
            ifauthor_id:
                exept_partner.append(author_id)

            sql_query="""selectdistincton(p.id)p.idfromres_partnerp
                            leftjoinmail_channel_partnermcponp.id=mcp.partner_id
                            leftjoinmail_channelconc.id=mcp.channel_id
                            leftjoinres_usersuonp.id=u.partner_id
                                where(u.notification_type!='inbox'oru.idisnull)
                                and(p.email!=ANY(%s)orp.emailisnull)
                                andc.id=ANY(%s)
                                andp.id!=ANY(%s)"""

            self.env.cr.execute(sql_query,(([email_from],),(email_cids,),(exept_partner,)))
            forpartner_idinself._cr.fetchall():
                #ocn_client:willaddpartnerstorecipientrecipient_data.moreocnnotifications.Weneeedtofilterthemmaybe
                recipient_data['partners'].append({'id':partner_id[0],'share':True,'active':True,'notif':'email','type':'channel_email','groups':[]})

        returnrecipient_data

    @api.model
    def_notify_encode_link(self,base_link,params):
        secret=self.env['ir.config_parameter'].sudo().get_param('database.secret')
        token='%s?%s'%(base_link,''.join('%s=%s'%(key,params[key])forkeyinsorted(params)))
        hm=hmac.new(secret.encode('utf-8'),token.encode('utf-8'),hashlib.sha1).hexdigest()
        returnhm

    def_notify_get_action_link(self,link_type,**kwargs):
        """Preparelinktoanaction:viewdocument,followdocument,..."""
        params={
            'model':kwargs.get('model',self._name),
            'res_id':kwargs.get('res_id',self.idsandself.ids[0]orFalse),
        }
        #whitelistacceptedparameters:action(deprecated),token(assign),access_token
        #(view),auth_signup_tokenandauth_login(forauth_signupsupport)
        params.update(dict(
            (key,value)
            forkey,valueinkwargs.items()
            ifkeyin('action','token','access_token','auth_signup_token','auth_login')
        ))

        iflink_typein['view','assign','follow','unfollow']:
            base_link='/mail/%s'%link_type
        eliflink_type=='controller':
            controller=kwargs.get('controller')
            params.pop('model')
            base_link='%s'%controller
        else:
            return''

        iflink_typenotin['view']:
            token=self._notify_encode_link(base_link,params)
            params['token']=token

        link='%s?%s'%(base_link,urls.url_encode(params))
        ifself:
            link=self[0].get_base_url()+link

        returnlink

    def_notify_get_groups(self,msg_vals=None):
        """Returngroupsusedtoclassifyrecipientsofanotificationemail.
        Groupsisalistoftuplecontainingofform(group_name,group_func,
        group_data)where
         *group_nameisanidentifierusedonlytobeabletooverrideandmanipulate
           groups.Defaultgroupsareuser(recipientslinkedtoanemployeeuser),
           portal(recipientslinkedtoaportaluser)andcustomer(recipientsnot
           linkedtoanyuser).Anexampleofoverrideusewouldbetoaddagroup
           linkedtoares.groupslikeHrOfficerstosetspecificactionbuttonsto
           them.
         *group_funcisafunctionpointertakingapartnerrecordasparameter.This
           methodwillbeappliedonrecipientstoknowwhethertheybelongtoagiven
           groupornot.Onlyfirstmatchinggroupiskept.Evaluationorderisthe
           listorder.
         *group_dataisadictcontainingparametersforthenotificationemail
          *has_button_access:whethertodisplayAccess<Document>inemail.True
            bydefaultfornewgroups,Falseforportal/customer.
          *button_access:dictwithurlandtitleofthebutton
          *actions:listofactionbuttonstodisplayinthenotificationemail.
            Eachactionisadictcontainingurlandtitleofthebutton.
        Groupshasadefaultvaluethatyoucanfindinmail_thread
        ``_notify_classify_recipients``method.
        """
        return[
            (
                'user',
                lambdapdata:pdata['type']=='user',
                {}
            ),(
                'portal',
                lambdapdata:pdata['type']=='portal',
                {'has_button_access':False}
            ),(
                'customer',
                lambdapdata:True,
                {'has_button_access':False}
            )
        ]

    def_notify_classify_recipients(self,recipient_data,model_name,msg_vals=None):
        """Classifyrecipientstobenotifiedofamessageingroupstohave
        specificrenderingdependingontheirgroup.Forexampleuserscould
        haveaccesstobuttonscustomersshouldnothaveintheiremails.
        Module-specificgroupingshouldbedonebyoverriding``_notify_get_groups``
        methoddefinedhere-under.
        :paramrecipient_data:todoxdoUPDATEME
        returnexample:
        [{
            'actions':[],
            'button_access':{'title':'ViewSimpleChatterModel',
                                'url':'/mail/view?model=mail.test.simple&res_id=1497'},
            'has_button_access':False,
            'recipients':[11]
        },
        {
            'actions':[],
            'button_access':{'title':'ViewSimpleChatterModel',
                            'url':'/mail/view?model=mail.test.simple&res_id=1497'},
            'has_button_access':False,
            'recipients':[4,5,6]
        },
        {
            'actions':[],
            'button_access':{'title':'ViewSimpleChatterModel',
                                'url':'/mail/view?model=mail.test.simple&res_id=1497'},
            'has_button_access':True,
            'recipients':[10,11,12]
        }]
        onlyreturngroupswithrecipients
        """
        #keepalocalcopyofmsg_valsasitmaybemodifiedtoincludemoreinformationaboutgroupsorlinks
        local_msg_vals=dict(msg_vals)ifmsg_valselse{}
        groups=self._notify_get_groups(msg_vals=local_msg_vals)
        access_link=self._notify_get_action_link('view',**local_msg_vals)

        ifmodel_name:
            view_title=_('View%s',model_name)
        else:
            view_title=_('View')

        #fillgroup_datawithdefault_valuesiftheyarenotcomplete
        forgroup_name,group_func,group_dataingroups:
            group_data.setdefault('notification_group_name',group_name)
            group_data.setdefault('notification_is_customer',False)
            is_thread_notification=self._notify_get_recipients_thread_info(msg_vals=msg_vals)['is_thread_notification']
            group_data.setdefault('has_button_access',is_thread_notification)
            group_button_access=group_data.setdefault('button_access',{})
            group_button_access.setdefault('url',access_link)
            group_button_access.setdefault('title',view_title)
            group_data.setdefault('actions',list())
            group_data.setdefault('recipients',list())

        #classifyrecipientsineachgroup
        forrecipientinrecipient_data:
            forgroup_name,group_func,group_dataingroups:
                ifgroup_func(recipient):
                    group_data['recipients'].append(recipient['id'])
                    break

        result=[]
        forgroup_name,group_method,group_dataingroups:
            ifgroup_data['recipients']:
                result.append(group_data)

        returnresult

    def_notify_get_recipients_thread_info(self,msg_vals=None):
        """Toolmethodtocomputethreadinfousedin``_notify_classify_recipients``
        anditssub-methods."""
        res_model=msg_vals['model']ifmsg_valsand'model'inmsg_valselseself._name
        res_id=msg_vals['res_id']ifmsg_valsand'res_id'inmsg_valselseself.ids[0]ifself.idselseFalse
        return{
            'is_thread_notification':res_modeland(res_model!='mail.thread')andres_id
        }

    @api.model
    def_notify_get_reply_to_on_records(self,default=None,records=None,company=None,doc_names=None):
        """Movedto``BaseModel._notify_get_reply_to()``"""
        records=recordsifrecordselseself
        returnrecords._notify_get_reply_to(default=default,company=company,doc_names=doc_names)

    def_notify_email_recipient_values(self,recipient_ids):
        """Formatemailnotificationrecipientvaluestostoreonthenotification
        mail.mail.Basicmethodjustsettherecipientpartnersasmail_mail
        recipients.Overridetogenerateothermailvalueslikeemail_toor
        email_cc.
        :paramrecipient_ids:res.partnerrecordsettonotify
        """
        return{
            'email_to':False,
            'recipient_ids':recipient_ids,
        }

    #------------------------------------------------------
    #FOLLOWERSAPI
    #------------------------------------------------------

    defmessage_subscribe(self,partner_ids=None,channel_ids=None,subtype_ids=None):
        """MainpublicAPItoaddfollowerstoarecordset.Itsmainpurposeis
        toperformaccessrightschecksbeforecalling``_message_subscribe``."""
        ifnotselfor(notpartner_idsandnotchannel_ids):
            returnTrue

        partner_ids=partner_idsor[]
        channel_ids=channel_idsor[]
        adding_current=set(partner_ids)==set([self.env.user.partner_id.id])
        customer_ids=[]ifadding_currentelseNone

        ifnotchannel_idsandpartner_idsandadding_current:
            try:
                self.check_access_rights('read')
                self.check_access_rule('read')
            exceptexceptions.AccessError:
                returnFalse
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')

        #filterinactiveandprivateaddresses
        ifpartner_idsandnotadding_current:
            partner_ids=self.env['res.partner'].sudo().search([('id','in',partner_ids),('active','=',True),('type','!=','private')]).ids

        returnself._message_subscribe(partner_ids,channel_ids,subtype_ids,customer_ids=customer_ids)

    def_message_subscribe(self,partner_ids=None,channel_ids=None,subtype_ids=None,customer_ids=None):
        """MainprivateAPItoaddfollowerstoarecordset.Thismethodadds
        partnersandchannels,giventheirIDs,asfollowersofallrecords
        containedintherecordset.

        Ifsubtypesaregivenexistingfollowersareerasedwithnewsubtypes.
        Ifdefaultonehavetobecomputedonlymissingfollowerswillbeadded
        withdefaultsubtypesmatchingtherecordsetmodel.

        Thisprivatemethoddoesnotspecificallycheckforaccessright.Use
        ``message_subscribe``publicAPIwhennotsureaboutaccessrights.

        :paramcustomer_ids:see``_insert_followers``"""
        ifnotself:
            returnTrue

        ifnotsubtype_ids:
            self.env['mail.followers']._insert_followers(
                self._name,self.ids,partner_ids,None,channel_ids,None,
                customer_ids=customer_ids,check_existing=True,existing_policy='skip')
        else:
            self.env['mail.followers']._insert_followers(
                self._name,self.ids,
                partner_ids,dict((pid,subtype_ids)forpidinpartner_ids),
                channel_ids,dict((cid,subtype_ids)forcidinchannel_ids),
                customer_ids=customer_ids,check_existing=True,existing_policy='replace')

        returnTrue

    defmessage_unsubscribe(self,partner_ids=None,channel_ids=None):
        """Removepartnersfromtherecordsfollowers."""
        #notnecessaryforcomputation,butsavesanaccessrightcheck
        ifnotpartner_idsandnotchannel_ids:
            returnTrue
        user_pid=self.env.user.partner_id.id
        ifnotchannel_idsandset(partner_ids)==set([user_pid]):
            self.check_access_rights('read')
            self.check_access_rule('read')
        else:
            self.check_access_rights('write')
            self.check_access_rule('write')
        self.env['mail.followers'].sudo().search([
            ('res_model','=',self._name),
            ('res_id','in',self.ids),
            '|',
            ('partner_id','in',partner_idsor[]),
            ('channel_id','in',channel_idsor[])
        ]).unlink()

    def_message_auto_subscribe_followers(self,updated_values,default_subtype_ids):
        """Optionalmethodtooverrideinaddonsinheritingfrommail.thread.
        Returnalisttuplescontaining(
          partnerID,
          subtypeIDs(orFalseifmodel-baseddefaultsubtypes),
          QWebtemplateXMLIDfornotification(orFalseisnospecific
            notificationisrequired),
          ),akapartnersandtheirsubtypeandpossiblenotificationtosend
        usingtheautosubscriptionmechanismlinkedtoupdatedvalues.

        Defaultvalueofthismethodistoreturnthenewresponsibleof
        documents.Thisisdoneusingrelationalfieldslinkingtores.users
        withtrack_visibilityset.SinceOpenERPv7itisconsideredasbeing
        responsibleforthedocumentandthereforestandardbehavioristo
        subscribetheuserandsendhimanotification.

        Overridethismethodtochangethatbehaviorand/ortoaddpeopleto
        notify,usingpossiblecustomnotification.

        :paramupdated_values:see``_message_auto_subscribe``
        :paramdefault_subtype_ids:comingfrom``_get_auto_subscription_subtypes``
        """
        fnames=[]
        field=self._fields.get('user_id')
        user_id=updated_values.get('user_id')
        iffieldanduser_idandfield.comodel_name=='res.users'and(getattr(field,'track_visibility',False)orgetattr(field,'tracking',False)):
            user=self.env['res.users'].sudo().browse(user_id)
            try:#avoidtomakeanexists,letsbeoptimisticandtrytoreadit.
                ifuser.active:
                    return[(user.partner_id.id,default_subtype_ids,'mail.message_user_assigned'ifuser!=self.env.userelseFalse)]
            except:
                pass
        return[]

    def_message_auto_subscribe_notify(self,partner_ids,template):
        """Notifynewfollowers,usingatemplatetorenderthecontentofthe
        notificationmessage.Notificationspushedaredoneusingthestandard
        notificationmechanisminmail.thread.Itiseitherinboxeitheremail
        dependingonthepartnerstate:nouser(email,customer),shareuser
        (email,customer)orclassicuser(notification_type)

        :parampartner_ids:IDsofpartnertonotify;
        :paramtemplate:XMLIDoftemplateusedforthenotification;
        """
        ifnotselforself.env.context.get('mail_auto_subscribe_no_notify'):
            return
        ifnotself.env.registry.ready: #Don'tsendnotificationduringinstall
            return

        view=self.env['ir.ui.view'].browse(self.env['ir.model.data'].xmlid_to_res_id(template))

        forrecordinself:
            model_description=self.env['ir.model']._get(record._name).display_name
            values={
                'object':record,
                'model_description':model_description,
                'access_link':record._notify_get_action_link('view'),
            }
            assignation_msg=view._render(values,engine='ir.qweb',minimal_qcontext=True)
            assignation_msg=self.env['mail.render.mixin']._replace_local_links(assignation_msg)
            record.message_notify(
                subject=_('Youhavebeenassignedto%s',record.display_name),
                body=assignation_msg,
                partner_ids=partner_ids,
                record_name=record.display_name,
                email_layout_xmlid='mail.mail_notification_light',
                model_description=model_description,
            )

    def_message_auto_subscribe(self,updated_values,followers_existing_policy='skip'):
        """Handleautosubscription.Autosubscriptionisdonebasedontwo
        mainmechanisms

         *usingsubtypesparentrelationship.Forexamplefollowingaparentrecord
           (i.e.project)withsubtypeslinkedtochildrecords(i.e.task).See
           mail.message.subtype``_get_auto_subscription_subtypes``;
         *calling_message_auto_subscribe_notifythatreturnsalistofpartner
           tosubscribe,aswellasdataaboutthesubtypesandnotification
           tosend.Basebehavioristosubscriberesponsibleandnotifythem;

        Addingapplication-specificautosubscriptionshouldbedonebyoverriding
        ``_message_auto_subscribe_followers``.Itshouldreturnstructureddata
        fornewpartnertosubscribe,withsubtypesandeventualnotification
        toperform.Seethatmethodformoredetails.

        :paramupdated_values:valuesmodifyingtherecordtrigerringautosubscription
        """
        ifnotself:
            returnTrue

        new_partners,new_channels=dict(),dict()

        #returndatarelatedtoautosubscriptionbasedonsubtypematching(aka:
        #defaulttasksubtypesorsubtypesfromprojecttriggeringtasksubtypes)
        updated_relation=dict()
        child_ids,def_ids,all_int_ids,parent,relation=self.env['mail.message.subtype']._get_auto_subscription_subtypes(self._name)

        #checkeffectivelymodifiedrelationfield
        forres_model,fnamesinrelation.items():
            forfieldin(fnameforfnameinfnamesifupdated_values.get(fname)):
                updated_relation.setdefault(res_model,set()).add(field)
        udpated_fields=[fnameforfnamesinupdated_relation.values()forfnameinfnamesifupdated_values.get(fname)]

        ifudpated_fields:
            #fetch"parent"subscriptiondata(aka:subtypesonprojecttopropagateontask)
            doc_data=[(model,[updated_values[fname]forfnameinfnames])formodel,fnamesinupdated_relation.items()]
            res=self.env['mail.followers']._get_subscription_data(doc_data,None,None,include_pshare=True,include_active=True)
            forfid,rid,pid,cid,subtype_ids,pshare,activeinres:
                #useproject.task_new->task.newlink
                sids=[parent[sid]forsidinsubtype_idsifparent.get(sid)]
                #addcheckedsubtypesmatchingmodel_name
                sids+=[sidforsidinsubtype_idsifsidnotinparentandsidinchild_ids]
                ifpidandactive: #autosubscribeonlyactivepartners
                    ifpshare: #removeinternalsubtypesforcustomers
                        new_partners[pid]=set(sids)-set(all_int_ids)
                    else:
                        new_partners[pid]=set(sids)
                ifcid: #neversubscribechannelstointernalsubtypes
                    new_channels[cid]=set(sids)-set(all_int_ids)

        notify_data=dict()
        res=self._message_auto_subscribe_followers(updated_values,def_ids)
        forpid,sids,templateinres:
            new_partners.setdefault(pid,sids)
            iftemplate:
                partner=self.env['res.partner'].browse(pid)
                lang=partner.langifpartnerelseNone
                notify_data.setdefault((template,lang),list()).append(pid)

        self.env['mail.followers']._insert_followers(
            self._name,self.ids,
            list(new_partners),new_partners,
            list(new_channels),new_channels,
            check_existing=True,existing_policy=followers_existing_policy)

        #notifypeoplefromautosubscription,forexamplelikeassignation
        for(template,lang),pidsinnotify_data.items():
            self.with_context(lang=lang)._message_auto_subscribe_notify(pids,template)

        returnTrue

    #------------------------------------------------------
    #CONTROLLERS
    #------------------------------------------------------

    def_get_mail_redirect_suggested_company(self):
        """Returnthesuggestedcompanytobesetonthecontext
        incaseofamailredirectiontotherecord.Toavoidmulti
        companyissueswhenclickingonalinksentbyemail,this
        couldbecalledtotrysettingthemostsuitedcompanyon
        theallowed_company_idsinthecontext.Thismethodcanbe
        overridden,forexampleonthehr.leavemodel,wherethe
        mostsuitedcompanyisthecompanyoftheleavetype,as
        specifiedbytheir.rule.
        """
        if'company_id'inself:
            returnself.company_id
        returnFalse
