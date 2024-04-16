#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromlxmlimportetree
fromlxml.htmlimportbuilderashtml

fromflectraimport_,api,fields,models
fromflectra.exceptionsimportUserError


classInvite(models.TransientModel):
    """Wizardtoinvitepartners(orchannels)andmakethemfollowers."""
    _name='mail.wizard.invite'
    _description='Invitewizard'

    @api.model
    defdefault_get(self,fields):
        result=super(Invite,self).default_get(fields)
        ifself._context.get('mail_invite_follower_channel_only'):
            result['send_mail']=False
        if'message'notinfields:
            returnresult

        user_name=self.env.user.display_name
        model=result.get('res_model')
        res_id=result.get('res_id')
        ifmodelandres_id:
            document=self.env['ir.model']._get(model).display_name
            title=self.env[model].browse(res_id).display_name
            msg_fmt=_('%(user_name)sinvitedyoutofollow%(document)sdocument:%(title)s')
        else:
            msg_fmt=_('%(user_name)sinvitedyoutofollowanewdocument.')

        text=msg_fmt%locals()
        message=html.DIV(
            html.P(_('Hello,')),
            html.P(text)
        )
        result['message']=etree.tostring(message)
        returnresult

    res_model=fields.Char('RelatedDocumentModel',required=True,index=True,help='Modelofthefollowedresource')
    res_id=fields.Integer('RelatedDocumentID',index=True,help='Idofthefollowedresource')
    partner_ids=fields.Many2many('res.partner',string='Recipients',help="Listofpartnersthatwillbeaddedasfollowerofthecurrentdocument.",
                                   domain=[('type','!=','private')])
    channel_ids=fields.Many2many('mail.channel',string='Channels',help='Listofchannelsthatwillbeaddedaslistenersofthecurrentdocument.',
                                   domain=[('channel_type','=','channel')])
    message=fields.Html('Message')
    send_mail=fields.Boolean('SendEmail',default=True,help="Ifchecked,thepartnerswillreceiveanemailwarningtheyhavebeenaddedinthedocument'sfollowers.")

    defadd_followers(self):
        ifnotself.env.user.email:
            raiseUserError(_("Unabletopostmessage,pleaseconfigurethesender'semailaddress."))
        email_from=self.env.user.email_formatted
        forwizardinself:
            Model=self.env[wizard.res_model]
            document=Model.browse(wizard.res_id)

            #filterpartner_idstogetthenewfollowers,toavoidsendingemailtoalreadyfollowingpartners
            new_partners=wizard.partner_ids-document.sudo().message_partner_ids
            new_channels=wizard.channel_ids-document.message_channel_ids
            document.message_subscribe(new_partners.ids,new_channels.ids)

            model_name=self.env['ir.model']._get(wizard.res_model).display_name
            #sendanemailifoptioncheckedandifamessageexists(donotsendvoidemails)
            ifwizard.send_mailandwizard.messageandnotwizard.message=='<br>': #whendeletingthemessage,cleditorkeepsa<br>
                message=self.env['mail.message'].create({
                    'subject':_('Invitationtofollow%(document_model)s:%(document_name)s',document_model=model_name,document_name=document.display_name),
                    'body':wizard.message,
                    'record_name':document.display_name,
                    'email_from':email_from,
                    'reply_to':email_from,
                    'model':wizard.res_model,
                    'res_id':wizard.res_id,
                    'no_auto_thread':True,
                    'add_sign':True,
                })
                partners_data=[]
                recipient_data=self.env['mail.followers']._get_recipient_data(document,'comment',False,pids=new_partners.ids)
                forpid,cid,active,pshare,ctype,notif,groupsinrecipient_data:
                    pdata={'id':pid,'share':pshare,'active':active,'notif':'email','groups':groupsor[]}
                    ifnotpshareandnotif: #hasanuserandisnotshared,isthereforeuser
                        partners_data.append(dict(pdata,type='user'))
                    elifpshareandnotif: #hasanuserandisshared,isthereforeportal
                        partners_data.append(dict(pdata,type='portal'))
                    else: #hasnouser,isthereforecustomer
                        partners_data.append(dict(pdata,type='customer'))

                document._notify_record_by_email(message,{'partners':partners_data,'channels':[]},send_after_commit=False)
                #incaseoffailure,thewebclientmustknowthemessagewas
                #deletedtodiscardtherelatedfailurenotification
                self.env['bus.bus'].sendone(
                    (self._cr.dbname,'res.partner',self.env.user.partner_id.id),
                    {'type':'deletion','message_ids':message.ids}
                )
                message.unlink()
        return{'type':'ir.actions.act_window_close'}
