#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importlogging
importpsycopg2
importwerkzeug.utils
importwerkzeug.wrappers

fromwerkzeug.urlsimporturl_encode

fromflectraimportapi,http,registry,SUPERUSER_ID,_
fromflectra.exceptionsimportAccessError
fromflectra.httpimportrequest
fromflectra.toolsimportconsteq

_logger=logging.getLogger(__name__)


classMailController(http.Controller):
    _cp_path='/mail'

    @classmethod
    def_redirect_to_messaging(cls):
        url='/web#%s'%url_encode({'action':'mail.action_discuss'})
        returnwerkzeug.utils.redirect(url)

    @classmethod
    def_check_token(cls,token):
        base_link=request.httprequest.path
        params=dict(request.params)
        params.pop('token','')
        valid_token=request.env['mail.thread']._notify_encode_link(base_link,params)
        returnconsteq(valid_token,str(token))

    @classmethod
    def_check_token_and_record_or_redirect(cls,model,res_id,token):
        comparison=cls._check_token(token)
        ifnotcomparison:
            _logger.warning('Invalidtokeninroute%s',request.httprequest.url)
            returncomparison,None,cls._redirect_to_messaging()
        try:
            record=request.env[model].browse(res_id).exists()
        exceptException:
            record=None
            redirect=cls._redirect_to_messaging()
        else:
            redirect=cls._redirect_to_record(model,res_id)
        returncomparison,record,redirect

    @classmethod
    def_redirect_to_record(cls,model,res_id,access_token=None,**kwargs):
        #access_tokenandkwargsareusedintheportalcontrolleroverridefortheSendbyemailorShareLink
        #togiveaccesstotherecordtoarecipientthathasnormallynoaccess.
        uid=request.session.uid
        user=request.env['res.users'].sudo().browse(uid)
        cids=False

        #nomodel/res_id,meaningnopossiblerecord->redirecttologin
        ifnotmodelornotres_idormodelnotinrequest.env:
            returncls._redirect_to_messaging()

        #findtheaccessactionusingsudotohavethedetailsabouttheaccesslink
        RecordModel=request.env[model]
        record_sudo=RecordModel.sudo().browse(res_id).exists()
        ifnotrecord_sudo:
            #recorddoesnotseemtoexist->redirecttologin
            returncls._redirect_to_messaging()

        #therecordhasawindowredirection:checkaccessrights
        ifuidisnotNone:
            ifnotRecordModel.with_user(uid).check_access_rights('read',raise_exception=False):
                returncls._redirect_to_messaging()
            try:
                #Weneedheretoextendthe"allowed_company_ids"toallowaredirection
                #toanyrecordthattheusercanaccess,regardlessofcurrentlyvisible
                #recordsbasedonthe"currentlyallowedcompanies".
                cids=request.httprequest.cookies.get('cids',str(user.company_id.id))
                cids=[int(cid)forcidincids.split(',')]
                try:
                    record_sudo.with_user(uid).with_context(allowed_company_ids=cids).check_access_rule('read')
                exceptAccessError:
                    #Incasetheallowed_company_idsfromthecookies(i.e.thelastuserconfiguration
                    #onhisbrowser)isnotsufficienttoavoidanir.ruleaccesserror,trytofollowing
                    #heuristic:
                    #-Guessthesupposednecessarycompanytoaccesstherecordviathemethod
                    #  _get_mail_redirect_suggested_company
                    #  -Ifnocompany,thenredirecttothemessaging
                    #  -Mergethesuggestedcompanywiththecompaniesonthecookie
                    #-Makeanewaccesstestifitsucceeds,redirecttotherecord.Otherwise,
                    #  redirecttothemessaging.
                    suggested_company=record_sudo._get_mail_redirect_suggested_company()
                    ifnotsuggested_company:
                        raiseAccessError('')
                    cids=cids+[suggested_company.id]
                    record_sudo.with_user(uid).with_context(allowed_company_ids=cids).check_access_rule('read')
            exceptAccessError:
                returncls._redirect_to_messaging()
            else:
                record_action=record_sudo.get_access_action(access_uid=uid)
        else:
            record_action=record_sudo.get_access_action()
            ifrecord_action['type']=='ir.actions.act_url'andrecord_action.get('target_type')!='public':
                url_params={
                    'model':model,
                    'id':res_id,
                    'active_id':res_id,
                    'action':record_action.get('id'),
                }
                view_id=record_sudo.get_formview_id()
                ifview_id:
                    url_params['view_id']=view_id
                url='/web/login?redirect=#%s'%url_encode(url_params)
                returnwerkzeug.utils.redirect(url)

        record_action.pop('target_type',None)
        #therecordhasanURLredirection:useitdirectly
        ifrecord_action['type']=='ir.actions.act_url':
            returnwerkzeug.utils.redirect(record_action['url'])
        #otherchoice:act_window(nosupportofanythingelsecurrently)
        elifnotrecord_action['type']=='ir.actions.act_window':
            returncls._redirect_to_messaging()

        url_params={
            'model':model,
            'id':res_id,
            'active_id':res_id,
            'action':record_action.get('id'),
        }
        view_id=record_sudo.get_formview_id()
        ifview_id:
            url_params['view_id']=view_id

        ifcids:
            url_params['cids']=','.join([str(cid)forcidincids])
        url='/web?#%s'%url_encode(url_params)
        returnwerkzeug.utils.redirect(url)

    @http.route('/mail/thread/data',methods=['POST'],type='json',auth='user')
    defmail_thread_data(self,thread_model,thread_id,request_list,**kwargs):
        res={}
        thread=request.env[thread_model].with_context(active_test=False).search([('id','=',thread_id)])
        if'attachments'inrequest_list:
            res['attachments']=thread.env['ir.attachment'].search([('res_id','=',thread.id),('res_model','=',thread._name)],order='iddesc')._attachment_format(commands=True)
        returnres

    @http.route('/mail/read_followers',type='json',auth='user')
    defread_followers(self,res_model,res_id):
        request.env['mail.followers'].check_access_rights("read")
        request.env[res_model].check_access_rights("read")
        request.env[res_model].browse(res_id).check_access_rule("read")
        follower_recs=request.env['mail.followers'].search([('res_model','=',res_model),('res_id','=',res_id)])

        followers=[]
        follower_id=None
        forfollowerinfollower_recs:
            iffollower.partner_id==request.env.user.partner_id:
                follower_id=follower.id
            followers.append({
                'id':follower.id,
                'partner_id':follower.partner_id.id,
                'channel_id':follower.channel_id.id,
                'name':follower.name,
                'display_name':follower.display_name,
                'email':follower.email,
                'is_active':follower.is_active,
                #Wheneditingthefollowers,the"pencil"iconthatleadstotheeditionofsubtypes
                #shouldbealwaysbedisplayedandnotonlywhen"debug"modeisactivated.
                'is_editable':True
            })
        return{
            'followers':followers,
            'subtypes':self.read_subscription_data(follower_id)iffollower_idelseNone
        }

    @http.route('/mail/read_subscription_data',type='json',auth='user')
    defread_subscription_data(self,follower_id):
        """Computes:
            -message_subtype_data:dataaboutdocumentsubtypes:whichare
                available,whicharefollowedifany"""
        request.env['mail.followers'].check_access_rights("read")
        follower=request.env['mail.followers'].sudo().browse(follower_id)
        follower.ensure_one()
        request.env[follower.res_model].check_access_rights("read")
        request.env[follower.res_model].browse(follower.res_id).check_access_rule("read")

        #findcurrentmodelsubtypes,addthemtoadictionary
        subtypes=request.env['mail.message.subtype'].search([
            '&',('hidden','=',False),
            '|',('res_model','=',follower.res_model),('res_model','=',False)])
        followed_subtypes_ids=set(follower.subtype_ids.ids)
        subtypes_list=[{
            'name':subtype.name,
            'res_model':subtype.res_model,
            'sequence':subtype.sequence,
            'default':subtype.default,
            'internal':subtype.internal,
            'followed':subtype.idinfollowed_subtypes_ids,
            'parent_model':subtype.parent_id.res_model,
            'id':subtype.id
        }forsubtypeinsubtypes]
        returnsorted(subtypes_list,
                      key=lambdait:(it['parent_model']or'',it['res_model']or'',it['internal'],it['sequence']))

    @http.route('/mail/view',type='http',auth='public')
    defmail_action_view(self,model=None,res_id=None,access_token=None,**kwargs):
        """Genericaccesspointfromnotificationemails.Theheuristicto
            choosewheretoredirecttheuseristhefollowing:

         -findapublicURL
         -ifnonefound
          -userswithareadaccessareredirectedtothedocument
          -userswithoutreadaccessareredirectedtotheMessaging
          -notloggedusersareredirectedtotheloginpage

            modelsthathaveanaccess_tokenmayapplyvariationsonthis.
        """
        #==============================================================================================
        #Thisblockofcodedisappearedonsaas-11.3tobereintroducedbyTBE.
        #Thisisneededbecauseafteramigrationfromanolderversiontosaas-11.3,thelink
        #receivedbymailwithamessage_idnolongerwork.
        #Sothisblockofcodeisneededtoguaranteethebackwardcompatibilityofthoselinks.
        ifkwargs.get('message_id'):
            try:
                message=request.env['mail.message'].sudo().browse(int(kwargs['message_id'])).exists()
            except:
                message=request.env['mail.message']
            ifmessage:
                model,res_id=message.model,message.res_id
        #==============================================================================================

        ifres_idandisinstance(res_id,str):
            try:
                res_id=int(res_id)
            exceptValueError:
                res_id=False
        returnself._redirect_to_record(model,res_id,access_token,**kwargs)

    @http.route('/mail/assign',type='http',auth='user',methods=['GET'])
    defmail_action_assign(self,model,res_id,token=None):
        comparison,record,redirect=self._check_token_and_record_or_redirect(model,int(res_id),token)
        ifcomparisonandrecord:
            try:
                record.write({'user_id':request.uid})
            exceptException:
                returnself._redirect_to_messaging()
        returnredirect

    @http.route('/mail/<string:res_model>/<int:res_id>/avatar/<int:partner_id>',type='http',auth='public')
    defavatar(self,res_model,res_id,partner_id):
        headers=[('Content-Type','image/png')]
        status=200
        content='R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==' #defaultimageisonewhitepixel
        ifres_modelinrequest.env:
            try:
                #ifthecurrentuserhasaccesstothedocument,getthepartneravatarassudo()
                request.env[res_model].browse(res_id).check_access_rule('read')
                ifpartner_idinrequest.env[res_model].browse(res_id).sudo().exists().message_ids.mapped('author_id').ids:
                    status,headers,_content=request.env['ir.http'].sudo().binary_content(
                        model='res.partner',id=partner_id,field='image_128',default_mimetype='image/png')
                    #binarycontentreturnanemptystringandnotaplaceholderifobj[field]isFalse
                    if_content!='':
                        content=_content
                    ifstatus==304:
                        returnwerkzeug.wrappers.Response(status=304)
            exceptAccessError:
                pass
        image_base64=base64.b64decode(content)
        headers.append(('Content-Length',len(image_base64)))
        response=request.make_response(image_base64,headers)
        response.status=str(status)
        returnresponse

    @http.route('/mail/needaction',type='json',auth='user')
    defneedaction(self):
        returnrequest.env['res.partner'].get_needaction_count()

    @http.route('/mail/init_messaging',type='json',auth='user')
    defmail_init_messaging(self):
        values={
            'needaction_inbox_counter':request.env['res.partner'].get_needaction_count(),
            'starred_counter':request.env['res.partner'].get_starred_count(),
            'channel_slots':request.env['mail.channel'].channel_fetch_slot(),
            'mail_failures':request.env['mail.message'].message_fetch_failed(),
            'commands':request.env['mail.channel'].get_mention_commands(),
            'mention_partner_suggestions':request.env['res.partner'].get_static_mention_suggestions(),
            'shortcodes':request.env['mail.shortcode'].sudo().search_read([],['source','substitution','description']),
            'menu_id':request.env['ir.model.data'].xmlid_to_res_id('mail.menu_root_discuss'),
            'moderation_counter':request.env.user.moderation_counter,
            'moderation_channel_ids':request.env.user.moderation_channel_ids.ids,
            'partner_root':request.env.ref('base.partner_root').sudo().mail_partner_format(),
            'public_partner':request.env.ref('base.public_partner').sudo().mail_partner_format(),
            'public_partners':[partner.mail_partner_format()forpartnerinrequest.env.ref('base.group_public').sudo().with_context(active_test=False).users.partner_id],
            'current_partner':request.env.user.partner_id.mail_partner_format(),
            'current_user_id':request.env.user.id,
        }
        returnvalues

    @http.route('/mail/get_partner_info',type='json',auth='user')
    defmessage_partner_info_from_emails(self,model,res_ids,emails,link_mail=False):
        records=request.env[model].browse(res_ids)
        try:
            records.check_access_rule('read')
            records.check_access_rights('read')
        except:
            return[]
        returnrecords._message_partner_info_from_emails(emails,link_mail=link_mail)

    @http.route('/mail/get_suggested_recipients',type='json',auth='user')
    defmessage_get_suggested_recipients(self,model,res_ids):
        records=request.env[model].browse(res_ids)
        try:
            records.check_access_rule('read')
            records.check_access_rights('read')
        except:
            return{}
        returnrecords._message_get_suggested_recipients()
