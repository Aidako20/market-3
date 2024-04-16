#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug
fromwerkzeugimporturls
fromwerkzeug.exceptionsimportNotFound,Forbidden

fromflectraimporthttp,_
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.toolsimportconsteq,plaintext2html
fromflectra.addons.mail.controllers.mainimportMailController
fromflectra.addons.portal.controllers.portalimportCustomerPortal
fromflectra.exceptionsimportAccessError,MissingError,UserError


def_check_special_access(res_model,res_id,token='',_hash='',pid=False):
    record=request.env[res_model].browse(res_id).sudo()
    if_hashandpid: #SignedTokenCase:hashimpliestokenissignedbypartnerpid
        returnconsteq(_hash,record._sign_token(pid))
    eliftoken: #TokenCase:tokenistheglobaloneofthedocument
        token_field=request.env[res_model]._mail_post_token_field
        return(tokenandrecordandconsteq(record[token_field],token))
    else:
        raiseForbidden()


def_message_post_helper(res_model,res_id,message,token='',_hash=False,pid=False,nosubscribe=True,**kw):
    """Genericchatterfunction,allowingtowriteon*any*objectthatinheritsmail.thread.We
        distinguish2cases:
            1/Ifatokenisspecified,allloggedinuserswillbeabletowriteamessageregardless
            ofaccessrights;iftheuseristhepublicuser,themessagewillbepostedunderthename
            ofthepartner_idoftheobject(orthepublicuserifthereisnopartner_idontheobject).

            2/Ifasignedtokenisspecified(`hash`)andalsoapartner_id(`pid`),allpostmessagewill
            bedoneunderthenameofthepartner_id(asitissigned).Thisshouldbeusedtoavoidleaking
            tokentoallusers.

        Requiredparameters
        :paramstringres_model:modelnameoftheobject
        :paramintres_id:idoftheobject
        :paramstringmessage:contentofthemessage

        Optionalkeywordsarguments:
        :paramstringtoken:accesstokeniftheobject'smodelusessomekindofpublicaccess
                             usingtokens(usuallyauuid4)tobypassaccessrules
        :paramstringhash:signedtokenbyapartnerifmodelusessometokenfieldtobypassaccessright
                            postmessages.
        :paramstringpid:identifieroftheres.partnerusedtosignthehash
        :paramboolnosubscribe:setFalseifyouwantthepartnertobesetasfolloweroftheobjectwhenposting(defaulttoTrue)

        Therestofthekwargsarepassedontomessage_post()
    """
    record=request.env[res_model].browse(res_id)

    #checkifusercanpostwithspecialtoken/signedtoken.The"else"willtrytopostmessagewiththe
    #currentuseraccessrights(_mail_post_accessusecase).
    iftokenor(_hashandpid):
        pid=int(pid)ifpidelseFalse
        if_check_special_access(res_model,res_id,token=token,_hash=_hash,pid=pid):
            record=record.sudo()
        else:
            raiseForbidden()

    #deduceauthorofmessage
    author_id=request.env.user.partner_id.idifrequest.env.user.partner_idelseFalse

    #SignedTokenCase:author_idisforced
    if_hashandpid:
        author_id=pid
    #TokenCase:authorisdocumentcustomer(ifnotlogged)oritselfevenifuserhasnottheaccess
    eliftoken:
        ifrequest.env.user._is_public():
            #TODO:Afteraddingthepidandsign_tokeninaccess_urlwhensendinvoicebyemail,removethisline
            #TODO:AuthormustbePublicUser(torenameto'Anonymous')
            author_id=record.partner_id.idifhasattr(record,'partner_id')andrecord.partner_id.idelseauthor_id
        else:
            ifnotauthor_id:
                raiseNotFound()

    email_from=None
    ifauthor_idand'email_from'notinkw:
        partner=request.env['res.partner'].sudo().browse(author_id)
        email_from=partner.email_formattedifpartner.emailelseNone

    message_post_args=dict(
        body=message,
        message_type=kw.pop('message_type',"comment"),
        subtype_xmlid=kw.pop('subtype_xmlid',"mail.mt_comment"),
        author_id=author_id,
        **kw
    )

    #Thisisnecessaryasmail.messagechecksthepresence
    #ofthekeytocomputeitsdefaultemailfrom
    ifemail_from:
        message_post_args['email_from']=email_from

    returnrecord.with_context(mail_create_nosubscribe=nosubscribe).message_post(**message_post_args)


classPortalChatter(http.Controller):

    def_portal_post_filter_params(self):
        return['token','pid']

    def_portal_post_check_attachments(self,attachment_ids,attachment_tokens):
        iflen(attachment_tokens)!=len(attachment_ids):
            raiseUserError(_("Anaccesstokenmustbeprovidedforeachattachment."))
        for(attachment_id,access_token)inzip(attachment_ids,attachment_tokens):
            try:
                CustomerPortal._document_check_access(self,'ir.attachment',attachment_id,access_token)
            except(AccessError,MissingError):
                raiseUserError(_("Theattachment%sdoesnotexistoryoudonothavetherightstoaccessit.",attachment_id))

    @http.route(['/mail/chatter_post'],type='http',methods=['POST'],auth='public',website=True)
    defportal_chatter_post(self,res_model,res_id,message,redirect=None,attachment_ids='',attachment_tokens='',**kw):
        """Createanew`mail.message`withthegiven`message`and/or
        `attachment_ids`andredirecttheusertothenewlycreatedmessage.

        Themessagewillbeassociatedtotherecord`res_id`ofthemodel
        `res_model`.Theusermusthaveaccessrightsonthistargetdocumentor
        mustprovidevalididentifiersthrough`kw`.See`_message_post_helper`.
        """
        url=redirector(request.httprequest.referrerandrequest.httprequest.referrer+"#discussion")or'/my'

        res_id=int(res_id)

        attachment_ids=[int(attachment_id)forattachment_idinattachment_ids.split(',')ifattachment_id]
        attachment_tokens=[attachment_tokenforattachment_tokeninattachment_tokens.split(',')ifattachment_token]
        self._portal_post_check_attachments(attachment_ids,attachment_tokens)

        ifmessageorattachment_ids:
            #messageisreceivedinplaintextandsavedinhtml
            ifmessage:
                message=plaintext2html(message)
            post_values={
                'res_model':res_model,
                'res_id':res_id,
                'message':message,
                'send_after_commit':False,
                'attachment_ids':False, #willbeaddedafterward
            }
            post_values.update((fname,kw.get(fname))forfnameinself._portal_post_filter_params())
            post_values['_hash']=kw.get('hash')
            message=_message_post_helper(**post_values)

            ifattachment_ids:
                #sudowritetheattachmenttobypassthereadaccess
                #verificationinmailmessage
                record=request.env[res_model].browse(res_id)
                message_values={'res_id':res_id,'model':res_model}
                attachments=record._message_post_process_attachments([],attachment_ids,message_values)

                ifattachments.get('attachment_ids'):
                    message.sudo().write(attachments)

        returnrequest.redirect(url)

    @http.route('/mail/chatter_init',type='json',auth='public',website=True)
    defportal_chatter_init(self,res_model,res_id,domain=False,limit=False,**kwargs):
        is_user_public=request.env.user.has_group('base.group_public')
        message_data=self.portal_message_fetch(res_model,res_id,domain=domain,limit=limit,**kwargs)
        display_composer=False
        ifkwargs.get('allow_composer'):
            display_composer=kwargs.get('token')ornotis_user_public
        return{
            'messages':message_data['messages'],
            'options':{
                'message_count':message_data['message_count'],
                'is_user_public':is_user_public,
                'is_user_employee':request.env.user.has_group('base.group_user'),
                'is_user_publisher':request.env.user.has_group('website.group_website_publisher'),
                'display_composer':display_composer,
                'partner_id':request.env.user.partner_id.id
            }
        }

    @http.route('/mail/chatter_fetch',type='json',auth='public',website=True)
    defportal_message_fetch(self,res_model,res_id,domain=False,limit=10,offset=0,**kw):
        ifnotdomain:
            domain=[]
        #Onlysearchintowebsite_message_ids,soapplythesamedomaintoperformonlyonesearch
        #extractdomainfromthe'website_message_ids'field
        model=request.env[res_model]
        field=model._fields['website_message_ids']
        field_domain=field.get_domain_list(model)
        domain=expression.AND([
            domain,
            field_domain,
            [('res_id','=',res_id),'|',('body','!=',''),('attachment_ids','!=',False)]
        ])

        #Checkaccess
        Message=request.env['mail.message']
        ifkw.get('token'):
            access_as_sudo=_check_special_access(res_model,res_id,token=kw.get('token'))
            ifnotaccess_as_sudo: #iftokenisnotcorrect,raiseForbidden
                raiseForbidden()
            #Non-employeeseeonlymessageswithnotinternalsubtype(aka,nointernallogs)
            ifnotrequest.env['res.users'].has_group('base.group_user'):
                domain=expression.AND([Message._get_search_domain_share(),domain])
            Message=request.env['mail.message'].sudo()
        return{
            'messages':Message.search(domain,limit=limit,offset=offset).portal_message_format(),
            'message_count':Message.search_count(domain)
        }

    @http.route(['/mail/update_is_internal'],type='json',auth="user",website=True)
    defportal_message_update_is_internal(self,message_id,is_internal):
        message=request.env['mail.message'].browse(int(message_id))
        message.write({'is_internal':is_internal})
        returnmessage.is_internal


classMailController(MailController):

    @classmethod
    def_redirect_to_record(cls,model,res_id,access_token=None,**kwargs):
        """Ifthecurrentuserdoesn'thaveaccesstothedocument,butprovided
        avalidaccesstoken,redirecthimtothefront-endview.
        Ifthepartner_idandhashparametersaregiven,addthoseparameterstotheredirecturl
        toauthentifytherecipientinthechatter,ifany.

        :parammodel:themodelnameoftherecordthatwillbevisualized
        :paramres_id:theidoftherecord
        :paramaccess_token:tokenthatgivesaccesstotherecord
            bypassingtherightsandrulesrestrictionoftheuser.
        :paramkwargs:Typically,itcanreceiveapartner_idandahash(sign_token).
            Ifso,thosetwoparametersareusedtoauthentifytherecipientinthechatter,ifany.
        :return:
        """
        #nomodel/res_id,meaningnopossiblerecord->directskiptosuper
        ifnotmodelornotres_idormodelnotinrequest.env:
            returnsuper(MailController,cls)._redirect_to_record(model,res_id,access_token=access_token,**kwargs)

        ifisinstance(request.env[model],request.env.registry['portal.mixin']):
            uid=request.session.uidorrequest.env.ref('base.public_user').id
            record_sudo=request.env[model].sudo().browse(res_id).exists()
            try:
                record_sudo.with_user(uid).check_access_rights('read')
                record_sudo.with_user(uid).check_access_rule('read')
            exceptAccessError:
                ifrecord_sudo.access_tokenandaccess_tokenandconsteq(record_sudo.access_token,access_token):
                    record_action=record_sudo.with_context(force_website=True).get_access_action()
                    ifrecord_action['type']=='ir.actions.act_url':
                        pid=kwargs.get('pid')
                        hash=kwargs.get('hash')
                        url=record_action['url']
                        ifpidandhash:
                            url=urls.url_parse(url)
                            url_params=url.decode_query()
                            url_params.update([("pid",pid),("hash",hash)])
                            url=url.replace(query=urls.url_encode(url_params)).to_url()
                        returnwerkzeug.utils.redirect(url)
        returnsuper(MailController,cls)._redirect_to_record(model,res_id,access_token=access_token,**kwargs)
