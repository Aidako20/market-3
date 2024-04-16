#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importast
importbase64
importre

fromflectraimport_,api,fields,models,tools
fromflectra.exceptionsimportUserError


#mainmako-likeexpressionpattern
EXPRESSION_PATTERN=re.compile('(\$\{.+?\})')


def_reopen(self,res_id,model,context=None):
    #saveoriginalmodelincontext,becauseselectingthelistofavailable
    #templatesrequiresamodelincontext
    context=dict(contextor{},default_model=model)
    return{'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_id':res_id,
            'res_model':self._name,
            'target':'new',
            'context':context,
            }


classMailComposer(models.TransientModel):
    """Genericmessagecompositionwizard.Youmayinheritfromthiswizard
        atmodelandviewlevelstoprovidespecificfeatures.

        Thebehaviorofthewizarddependsonthecomposition_modefield:
        -'comment':postonarecord.Thewizardispre-populatedvia``get_record_data``
        -'mass_mail':wizardinmassmailingmodewherethemaildetailscan
            containtemplateplaceholdersthatwillbemergedwithactualdata
            beforebeingsenttoeachrecipient.
    """
    _name='mail.compose.message'
    _description='Emailcompositionwizard'
    _log_access=True
    _batch_size=500

    @api.model
    defdefault_get(self,fields):
        """Handlecompositionmode.Somedetailsaboutcontextkeys:
            -comment:defaultmode,modelandIDofarecordtheusercomments
                -default_modeloractive_model
                -default_res_idoractive_id
            -mass_mail:modelandIDsofrecordstheusermass-mails
                -active_ids:recordIDs
                -default_modeloractive_model
        """
        result=super(MailComposer,self).default_get(fields)

        #author
        missing_author='author_id'infieldsand'author_id'notinresult
        missing_email_from='email_from'infieldsand'email_from'notinresult
        ifmissing_authorormissing_email_from:
            author_id,email_from=self.env['mail.thread']._message_compute_author(result.get('author_id'),result.get('email_from'),raise_exception=False)
            ifmissing_email_from:
                result['email_from']=email_from
            ifmissing_author:
                result['author_id']=author_id

        if'model'infieldsand'model'notinresult:
            result['model']=self._context.get('active_model')
        if'res_id'infieldsand'res_id'notinresult:
            result['res_id']=self._context.get('active_id')
        if'no_auto_thread'infieldsand'no_auto_thread'notinresultandresult.get('model'):
            #doesn'tsupportthreading
            ifresult['model']notinself.envornothasattr(self.env[result['model']],'message_post'):
                result['no_auto_thread']=True

        if'active_domain'inself._context: #notcontext.get()becausewewanttokeepglobal[]domains
            result['active_domain']='%s'%self._context.get('active_domain')
        ifresult.get('composition_mode')=='comment'and(set(fields)&set(['model','res_id','partner_ids','record_name','subject'])):
            result.update(self.get_record_data(result))

        #whenbeinginnewmode,create_uidisnotgranted->ACLsissuemayarise
        if'create_uid'infieldsand'create_uid'notinresult:
            result['create_uid']=self.env.uid

        filtered_result=dict((fname,result[fname])forfnameinresultiffnameinfields)
        returnfiltered_result

    #content
    subject=fields.Char('Subject')
    body=fields.Html('Contents',default='',sanitize_style=True)
    parent_id=fields.Many2one(
        'mail.message','ParentMessage',index=True,ondelete='setnull',
        help="Initialthreadmessage.")
    template_id=fields.Many2one(
        'mail.template','Usetemplate',index=True,
        domain="[('model','=',model)]")
    attachment_ids=fields.Many2many(
        'ir.attachment','mail_compose_message_ir_attachments_rel',
        'wizard_id','attachment_id','Attachments')
    layout=fields.Char('Layout',copy=False) #xmlidoflayout
    add_sign=fields.Boolean(default=True)
    #origin
    email_from=fields.Char('From',help="Emailaddressofthesender.Thisfieldissetwhennomatchingpartnerisfoundandreplacestheauthor_idfieldinthechatter.")
    author_id=fields.Many2one(
        'res.partner','Author',index=True,
        help="Authorofthemessage.Ifnotset,email_frommayholdanemailaddressthatdidnotmatchanypartner.")
    #composition
    composition_mode=fields.Selection(selection=[
        ('comment','Postonadocument'),
        ('mass_mail','EmailMassMailing'),
        ('mass_post','PostonMultipleDocuments')],string='Compositionmode',default='comment')
    model=fields.Char('RelatedDocumentModel',index=True)
    res_id=fields.Integer('RelatedDocumentID',index=True)
    record_name=fields.Char('MessageRecordName',help="Namegetoftherelateddocument.")
    use_active_domain=fields.Boolean('Useactivedomain')
    active_domain=fields.Text('Activedomain',readonly=True)
    #characteristics
    message_type=fields.Selection([
        ('comment','Comment'),
        ('notification','Systemnotification')],
        'Type',required=True,default='comment',
        help="Messagetype:emailforemailmessage,notificationforsystem"
             "message,commentforothermessagessuchasuserreplies")
    subtype_id=fields.Many2one(
        'mail.message.subtype','Subtype',ondelete='setnull',index=True,
        default=lambdaself:self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment'))
    mail_activity_type_id=fields.Many2one(
        'mail.activity.type','MailActivityType',
        index=True,ondelete='setnull')
    #destination
    reply_to=fields.Char('Reply-To',help='Replyemailaddress.Settingthereply_tobypassestheautomaticthreadcreation.')
    no_auto_thread=fields.Boolean(
        'Nothreadingforanswers',
        help='Answersdonotgointheoriginaldocumentdiscussionthread.Thishasanimpactonthegeneratedmessage-id.')
    is_log=fields.Boolean('LoganInternalNote',
                            help='Whetherthemessageisaninternalnote(commentmodeonly)')
    partner_ids=fields.Many2many(
        'res.partner','mail_compose_message_res_partner_rel',
        'wizard_id','partner_id','AdditionalContacts',
        domain=[('type','!=','private')])
    #massmodeoptions
    notify=fields.Boolean('Notifyfollowers',help='Notifyfollowersofthedocument(masspostonly)')
    auto_delete=fields.Boolean('DeleteEmails',
        help='Thisoptionpermanentlyremovesanytrackofemailafterit\'sbeensent,includingfromtheTechnicalmenuintheSettings,inordertopreservestoragespaceofyourFlectradatabase.')
    auto_delete_message=fields.Boolean('DeleteMessageCopy',help='Donotkeepacopyoftheemailinthedocumentcommunicationhistory(massmailingonly)')
    mail_server_id=fields.Many2one('ir.mail_server','Outgoingmailserver')

    @api.model
    defget_record_data(self,values):
        """Returnsadefaults-likedictwithinitialvaluesforthecomposition
        wizardwhensendinganemailrelatedapreviousemail(parent_id)or
        adocument(model,res_id).Thisisbasedonpreviouslycomputeddefault
        values."""
        result,subject={},False
        ifvalues.get('parent_id'):
            parent=self.env['mail.message'].browse(values.get('parent_id'))
            result['record_name']=parent.record_name,
            subject=tools.ustr(parent.subjectorparent.record_nameor'')
            ifnotvalues.get('model'):
                result['model']=parent.model
            ifnotvalues.get('res_id'):
                result['res_id']=parent.res_id
            partner_ids=values.get('partner_ids',list())+parent.partner_ids.ids
            result['partner_ids']=partner_ids
        elifvalues.get('model')andvalues.get('res_id'):
            doc_name_get=self.env[values.get('model')].browse(values.get('res_id')).name_get()
            result['record_name']=doc_name_getanddoc_name_get[0][1]or''
            subject=tools.ustr(result['record_name'])

        re_prefix=_('Re:')
        ifsubjectandnot(subject.startswith('Re:')orsubject.startswith(re_prefix)):
            subject="%s%s"%(re_prefix,subject)
        result['subject']=subject

        returnresult

    #------------------------------------------------------------
    #ACTIONS
    #------------------------------------------------------------
    #actionbuttonscallwithpositionnalargumentsonly,soweneedanintermediaryfunction
    #toensurethecontextispassedcorrectly
    defaction_send_mail(self):
        self.send_mail()
        return{'type':'ir.actions.act_window_close'}

    defsend_mail(self,auto_commit=False):
        """Processthewizardcontentandproceedwithsendingtherelated
            email(s),renderinganytemplatepatternsontheflyifneeded."""
        notif_layout=self._context.get('custom_layout')
        #Severalcustomlayoutsmakeuseofthemodeldescriptionatrendering,e.g.inthe
        #'View<document>'button.Somemodelsareusedfordifferentbusinessconcepts,suchas
        #'purchase.order'whichisusedforaRFQandandPO.Toavoidconfusion,wemustusea
        #differentwordingdependingonthestateoftheobject.
        #Therefore,wecansetthedescriptioninthecontextfromthebeginningtoavoidfalling
        #backontheregulardisplay_nameretrievedin'_notify_prepare_template_context'.
        model_description=self._context.get('model_description')
        forwizardinself:
            #Duplicateattachmentslinkedtotheemail.template.
            #Indeed,basicmail.compose.messagewizardduplicatesattachmentsinmass
            #mailingmode.Butin'singlepost'mode,attachmentsofanemailtemplate
            #alsohavetobeduplicatedtoavoidchangingtheirownership.
            ifwizard.attachment_idsandwizard.composition_mode!='mass_mail'andwizard.template_id:
                new_attachment_ids=[]
                forattachmentinwizard.attachment_ids:
                    ifattachmentinwizard.template_id.attachment_ids:
                        new_attachment_ids.append(attachment.copy({'res_model':'mail.compose.message','res_id':wizard.id}).id)
                    else:
                        new_attachment_ids.append(attachment.id)
                new_attachment_ids.reverse()
                wizard.write({'attachment_ids':[(6,0,new_attachment_ids)]})

            #MassMailing
            mass_mode=wizard.composition_modein('mass_mail','mass_post')

            ActiveModel=self.env[wizard.model]ifwizard.modelandhasattr(self.env[wizard.model],'message_post')elseself.env['mail.thread']
            ifwizard.composition_mode=='mass_post':
                #donotsendemailsdirectlybutusethequeueinstead
                #addcontextkeytoavoidsubscribingtheauthor
                ActiveModel=ActiveModel.with_context(mail_notify_force_send=False,mail_create_nosubscribe=True)
            #wizardworksinbatchmode:[res_id]oractive_idsoractive_domain
            ifmass_modeandwizard.use_active_domainandwizard.model:
                res_ids=self.env[wizard.model].search(ast.literal_eval(wizard.active_domain)).ids
            elifmass_modeandwizard.modelandself._context.get('active_ids'):
                res_ids=self._context['active_ids']
            else:
                res_ids=[wizard.res_id]

            batch_size=int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size'))orself._batch_size
            sliced_res_ids=[res_ids[i:i+batch_size]foriinrange(0,len(res_ids),batch_size)]

            ifwizard.composition_mode=='mass_mail'orwizard.is_logor(wizard.composition_mode=='mass_post'andnotwizard.notify): #loganote:subtypeisFalse
                subtype_id=False
            elifwizard.subtype_id:
                subtype_id=wizard.subtype_id.id
            else:
                subtype_id=self.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')

            forres_idsinsliced_res_ids:
                #massmailmode:mailaresudo-ed,aswhengoingthroughget_mail_values
                #standardaccessrightsonrelatedrecordswillbecheckedwhenbrowsingthem
                #tocomputemailvalues.Ifpeoplehaveaccesstotherecordstheyhaverights
                #tocreatelotsofemailsinsudoasitisconsdieredasatechnicalmodel.
                batch_mails_sudo=self.env['mail.mail'].sudo()
                all_mail_values=wizard.get_mail_values(res_ids)
                forres_id,mail_valuesinall_mail_values.items():
                    ifwizard.composition_mode=='mass_mail':
                        batch_mails_sudo|=self.env['mail.mail'].sudo().create(mail_values)
                    else:
                        post_params=dict(
                            message_type=wizard.message_type,
                            subtype_id=subtype_id,
                            email_layout_xmlid=notif_layout,
                            add_sign=notbool(wizard.template_id),
                            mail_auto_delete=wizard.template_id.auto_deleteifwizard.template_idelseself._context.get('mail_auto_delete',True),
                            model_description=model_description)
                        post_params.update(mail_values)
                        ifActiveModel._name=='mail.thread':
                            ifwizard.model:
                                post_params['model']=wizard.model
                                post_params['res_id']=res_id
                            ifnotActiveModel.message_notify(**post_params):
                                #ifmessage_notifyreturnsanemptyrecordset,norecipientswherefound.
                                raiseUserError(_("Norecipientfound."))
                        else:
                            ActiveModel.browse(res_id).message_post(**post_params)

                ifwizard.composition_mode=='mass_mail':
                    batch_mails_sudo.send(auto_commit=auto_commit)

    defget_mail_values(self,res_ids):
        """Generatethevaluesthatwillbeusedbysend_mailtocreatemail_messages
        ormail_mails."""
        self.ensure_one()
        results=dict.fromkeys(res_ids,False)
        rendered_values={}
        mass_mail_mode=self.composition_mode=='mass_mail'

        #renderalltemplate-basedvalueatonce
        ifmass_mail_modeandself.model:
            rendered_values=self.render_message(res_ids)
        #computealias-basedreply-toinbatch
        reply_to_value=dict.fromkeys(res_ids,None)
        ifmass_mail_modeandnotself.no_auto_thread:
            records=self.env[self.model].browse(res_ids)
            reply_to_value=records._notify_get_reply_to(default=False)
            #whenhavingnospecificreply-to,fetchrenderedemail_fromvalue
            forres_id,reply_toinreply_to_value.items():
                ifnotreply_to:
                    reply_to_value[res_id]=rendered_values.get(res_id,{}).get('email_from',False)

        blacklisted_rec_ids=set()
        ifmass_mail_modeandisinstance(self.env[self.model],self.pool['mail.thread.blacklist']):
            self.env['mail.blacklist'].flush(['email'])
            self._cr.execute("SELECTemailFROMmail_blacklistWHEREactive=true")
            blacklist={x[0]forxinself._cr.fetchall()}
            ifblacklist:
                targets=self.env[self.model].browse(res_ids).read(['email_normalized'])
                #Firstextractemailfromrecipientbeforecomparingwithblacklist
                blacklisted_rec_ids.update(target['id']fortargetintargets
                                           iftarget['email_normalized']inblacklist)

        forres_idinres_ids:
            #staticwizard(mail.message)values
            mail_values={
                'subject':self.subject,
                'body':self.bodyor'',
                'parent_id':self.parent_idandself.parent_id.id,
                'partner_ids':[partner.idforpartnerinself.partner_ids],
                'attachment_ids':[attach.idforattachinself.attachment_ids],
                'author_id':self.author_id.id,
                'email_from':self.email_from,
                'record_name':self.record_name,
                'no_auto_thread':self.no_auto_thread,
                'mail_server_id':self.mail_server_id.id,
                'mail_activity_type_id':self.mail_activity_type_id.id,
            }

            #massmailing:renderingoverridewizardstaticvalues
            ifmass_mail_modeandself.model:
                record=self.env[self.model].browse(res_id)
                mail_values['headers']=record._notify_email_headers()
                #keepacopyunlessspecificallyrequested,resetrecordname(avoidbrowsingrecords)
                mail_values.update(notification=notself.auto_delete_message,model=self.model,res_id=res_id,record_name=False)
                #autodeletionofmail_mail
                ifself.auto_deleteorself.template_id.auto_delete:
                    mail_values['auto_delete']=True
                #renderedvaluesusingtemplate
                email_dict=rendered_values[res_id]
                mail_values['partner_ids']+=email_dict.pop('partner_ids',[])
                mail_values.update(email_dict)
                ifnotself.no_auto_thread:
                    mail_values.pop('reply_to')
                    ifreply_to_value.get(res_id):
                        mail_values['reply_to']=reply_to_value[res_id]
                ifself.no_auto_threadandnotmail_values.get('reply_to'):
                    mail_values['reply_to']=mail_values['email_from']
                #mail_mailvalues:body->body_html,partner_ids->recipient_ids
                mail_values['body_html']=mail_values.get('body','')
                mail_values['recipient_ids']=[(4,id)foridinmail_values.pop('partner_ids',[])]

                #processattachments:shouldnotbeencodedbeforebeingprocessedbymessage_post/mail_mailcreate
                mail_values['attachments']=[(name,base64.b64decode(enc_cont))forname,enc_continemail_dict.pop('attachments',list())]
                attachment_ids=[]
                forattach_idinmail_values.pop('attachment_ids'):
                    new_attach_id=self.env['ir.attachment'].browse(attach_id).copy({'res_model':self._name,'res_id':self.id})
                    attachment_ids.append(new_attach_id.id)
                attachment_ids.reverse()
                mail_values['attachment_ids']=self.env['mail.thread'].with_context(attached_to=record)._message_post_process_attachments(
                    mail_values.pop('attachments',[]),
                    attachment_ids,
                    {'model':'mail.message','res_id':0}
                )['attachment_ids']
                #Filterouttheblacklistedrecordsbysettingthemailstatetocancel->UsedforMassMailingstats
                ifres_idinblacklisted_rec_ids:
                    mail_values['state']='cancel'
                    #Donotpostthemailintotherecipient'schatter
                    mail_values['notification']=False

            results[res_id]=mail_values
        returnresults

    #------------------------------------------------------------
    #TEMPLATES
    #------------------------------------------------------------

    @api.onchange('template_id')
    defonchange_template_id_wrapper(self):
        self.ensure_one()
        values=self.onchange_template_id(self.template_id.id,self.composition_mode,self.model,self.res_id)['value']
        forfname,valueinvalues.items():
            setattr(self,fname,value)

    defonchange_template_id(self,template_id,composition_mode,model,res_id):
        """-mass_mailing:wecannotrender,soreturnthetemplatevalues
            -normalmode:returnrenderedvalues
            /!\forx2manyfield,thisonchangereturncommandinsteadofids
        """
        iftemplate_idandcomposition_mode=='mass_mail':
            template=self.env['mail.template'].browse(template_id)
            fields=['subject','body_html','email_from','reply_to','mail_server_id']
            values=dict((field,getattr(template,field))forfieldinfieldsifgetattr(template,field))
            iftemplate.attachment_ids:
                values['attachment_ids']=[att.idforattintemplate.attachment_ids]
            iftemplate.mail_server_id:
                values['mail_server_id']=template.mail_server_id.id
        eliftemplate_id:
            values=self.generate_email_for_composer(
                template_id,[res_id],
                ['subject','body_html','email_from','email_to','partner_to','email_cc', 'reply_to','attachment_ids','mail_server_id']
            )[res_id]
            #transformattachmentsintoattachment_ids;notattachedtothedocumentbecausethiswill
            #bedonefurtherinthepostingprocess,allowingtocleandatabaseifemailnotsend
            attachment_ids=[]
            Attachment=self.env['ir.attachment']
            forattach_fname,attach_datasinvalues.pop('attachments',[]):
                data_attach={
                    'name':attach_fname,
                    'datas':attach_datas,
                    'res_model':'mail.compose.message',
                    'res_id':0,
                    'type':'binary', #overridedefault_typefromcontext,possiblymeantforanothermodel!
                }
                attachment_ids.append(Attachment.create(data_attach).id)
            ifvalues.get('attachment_ids',[])orattachment_ids:
                values['attachment_ids']=[(6,0,values.get('attachment_ids',[])+attachment_ids)]
        else:
            default_values=self.with_context(default_composition_mode=composition_mode,default_model=model,default_res_id=res_id).default_get(['composition_mode','model','res_id','parent_id','partner_ids','subject','body','email_from','reply_to','attachment_ids','mail_server_id'])
            values=dict((key,default_values[key])forkeyin['subject','body','partner_ids','email_from','reply_to','attachment_ids','mail_server_id']ifkeyindefault_values)

        ifvalues.get('body_html'):
            values['body']=values.pop('body_html')

        #Thisonchangeshouldreturncommandinsteadofidsforx2manyfield.
        values=self._convert_to_write(values)

        return{'value':values}

    defsave_as_template(self):
        """hitsaveastemplatebutton:currentformvaluewillbeanew
            templateattachedtothecurrentdocument."""
        forrecordinself:
            model=self.env['ir.model']._get(record.modelor'mail.message')
            model_name=model.nameor''
            template_name="%s:%s"%(model_name,tools.ustr(record.subject))
            values={
                'name':template_name,
                'subject':record.subjectorFalse,
                'body_html':record.bodyorFalse,
                'model_id':model.idorFalse,
                'use_default_to':True,
            }
            template=self.env['mail.template'].create(values)

            ifrecord.attachment_ids:
                #transferpendingattachmentstothenewtemplate
                attachments=self.env['ir.attachment'].sudo().browse(record.attachment_ids.ids).filtered(
                    lambdaa:a.res_model=='mail.compose.message'anda.create_uid.id==self._uid)
                ifattachments:
                    attachments.write({'res_model':template._name,'res_id':template.id})
                template.attachment_ids|=record.attachment_ids

            #generatethesavedtemplate
            record.write({'template_id':template.id})
            record.onchange_template_id_wrapper()
            return_reopen(self,record.id,record.model,context=self._context)

    #------------------------------------------------------------
    #RENDERING
    #------------------------------------------------------------

    defrender_message(self,res_ids):
        """Generatetemplate-basedvaluesofwizard,forthedocumentrecordsgiven
        byres_ids.Thismethodismeanttobeinheritedbyemail_templatethat
        willproduceamorecompletedictionary,usingJinja2templates.

        Eachtemplateisgeneratedforallres_ids,allowingtoparsethetemplate
        once,andrenderitmultipletimes.Thisisusefulformassmailingwhere
        templaterenderingrepresentasignificantpartoftheprocess.

        Defaultrecipientsarealsocomputed,basedonmail_threadmethod
        _message_get_default_recipients.Thisallowstoensureamassmailinghas
        alwayssomerecipientsspecified.

        :parambrowsewizard:currentmail.compose.messagebrowserecord
        :paramlistres_ids:listofrecordids

        :returndictresults:foreachres_id,thegeneratedtemplatevaluesfor
                              subject,body,email_fromandreply_to
        """
        self.ensure_one()
        multi_mode=True
        ifisinstance(res_ids,int):
            multi_mode=False
            res_ids=[res_ids]

        subjects=self.env['mail.render.mixin']._render_template(self.subject,self.model,res_ids)
        bodies=self.env['mail.render.mixin']._render_template(self.body,self.model,res_ids,post_process=True)
        emails_from=self.env['mail.render.mixin']._render_template(self.email_from,self.model,res_ids)
        replies_to=self.env['mail.render.mixin']._render_template(self.reply_to,self.model,res_ids)
        default_recipients={}
        ifnotself.partner_ids:
            records=self.env[self.model].browse(res_ids).sudo()
            default_recipients=records._message_get_default_recipients()

        results=dict.fromkeys(res_ids,False)
        forres_idinres_ids:
            results[res_id]={
                'subject':subjects[res_id],
                'body':bodies[res_id],
                'email_from':emails_from[res_id],
                'reply_to':replies_to[res_id],
            }
            results[res_id].update(default_recipients.get(res_id,dict()))

        #generatetemplate-basedvalues
        ifself.template_id:
            template_values=self.generate_email_for_composer(
                self.template_id.id,res_ids,
                ['email_to','partner_to','email_cc','attachment_ids','mail_server_id'])
        else:
            template_values={}

        forres_idinres_ids:
            iftemplate_values.get(res_id):
                #recipientsaremanagedbythetemplate
                results[res_id].pop('partner_ids',None)
                results[res_id].pop('email_to',None)
                results[res_id].pop('email_cc',None)
                #removeattachmentsfromtemplatevaluesastheyshouldnotberendered
                template_values[res_id].pop('attachment_ids',None)
            else:
                template_values[res_id]=dict()
            #updatetemplatevaluesbycomposervalues
            template_values[res_id].update(results[res_id])

        returnmulti_modeandtemplate_valuesortemplate_values[res_ids[0]]

    @api.model
    defgenerate_email_for_composer(self,template_id,res_ids,fields):
        """Callemail_template.generate_email(),getfieldsrelevantfor
            mail.compose.message,transformemail_ccandemail_tointopartner_ids"""
        multi_mode=True
        ifisinstance(res_ids,int):
            multi_mode=False
            res_ids=[res_ids]

        returned_fields=fields+['partner_ids','attachments']
        values=dict.fromkeys(res_ids,False)

        template_values=self.env['mail.template'].with_context(tpl_partners_only=True).browse(template_id).generate_email(res_ids,fields)
        forres_idinres_ids:
            res_id_values=dict((field,template_values[res_id][field])forfieldinreturned_fieldsiftemplate_values[res_id].get(field))
            res_id_values['body']=res_id_values.pop('body_html','')
            values[res_id]=res_id_values

        returnmulti_modeandvaluesorvalues[res_ids[0]]

    @api.autovacuum
    def_gc_lost_attachments(self):
        """Garbagecollectlostmailattachments.Thoseareattachments
            -linkedtores_model'mail.compose.message',thecomposerwizard
            -withres_id0,becausetheywerecreatedoutsideofanexisting
                wizard(typicallyuserinputthroughChatterorreports
                createdon-the-flybythetemplates)
            -unusedsinceatleastoneday(create_dateandwrite_date)
        """
        limit_date=fields.Datetime.subtract(fields.Datetime.now(),days=1)
        self.env['ir.attachment'].search([
            ('res_model','=',self._name),
            ('res_id','=',0),
            ('create_date','<',limit_date),
            ('write_date','<',limit_date)]
        ).unlink()
