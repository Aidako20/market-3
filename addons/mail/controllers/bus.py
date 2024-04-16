#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportSUPERUSER_ID,tools
fromflectra.httpimportrequest,route
fromflectra.addons.bus.controllers.mainimportBusController


classMailChatController(BusController):

    def_default_request_uid(self):
        """ForAnonymouspeople,theyreceivetheaccessrightofSUPERUSER_IDsincetheyhaveNOaccess(auth=none)
            !!!Eachtimeamethodfromthiscontrolleriscall,thereisacheckiftheuser(whocanbeanonymousandSudoaccess)
            canaccesstotheresource.
        """
        returnrequest.session.uidandrequest.session.uidorSUPERUSER_ID

    #--------------------------
    #ExtendsBUSControllerPoll
    #--------------------------
    def_poll(self,dbname,channels,last,options):
        ifrequest.session.uid:
            partner_id=request.env.user.partner_id.id

            ifpartner_id:
                channels=list(channels)      #donotalteroriginallist
                formail_channelinrequest.env['mail.channel'].search([('channel_partner_ids','in',[partner_id])]):
                    channels.append((request.db,'mail.channel',mail_channel.id))
                #personalandneedactionchannel
                channels.append((request.db,'res.partner',partner_id))
                channels.append((request.db,'ir.needaction',partner_id))
        returnsuper(MailChatController,self)._poll(dbname,channels,last,options)

    #--------------------------
    #Anonymousroutes(CommonMethods)
    #--------------------------
    @route('/mail/chat_post',type="json",auth="public",cors="*")
    defmail_chat_post(self,uuid,message_content,**kwargs):
        mail_channel=request.env["mail.channel"].sudo().search([('uuid','=',uuid)],limit=1)
        ifnotmail_channel:
            returnFalse

        #findtheauthorfromtheusersession
        ifrequest.session.uid:
            author=request.env['res.users'].sudo().browse(request.session.uid).partner_id
            author_id=author.id
            email_from=author.email_formatted
        else: #IfPublicUser,usecatchallemailfromcompany
            author_id=False
            email_from=mail_channel.anonymous_nameormail_channel.create_uid.company_id.catchall_formatted
        #postamessagewithoutaddingfollowerstothechannel.email_from=Falseavoidtogetauthorfromemaildata
        body=tools.plaintext2html(message_content)
        message=mail_channel.with_context(mail_create_nosubscribe=True).message_post(author_id=author_id,
                                                                                       email_from=email_from,body=body,
                                                                                       message_type='comment',
                                                                                       subtype_xmlid='mail.mt_comment')
        returnmessageandmessage.idorFalse

    @route(['/mail/chat_history'],type="json",auth="public",cors="*")
    defmail_chat_history(self,uuid,last_id=False,limit=20):
        channel=request.env["mail.channel"].sudo().search([('uuid','=',uuid)],limit=1)
        ifnotchannel:
            return[]
        else:
            returnchannel.channel_fetch_message(last_id,limit)
