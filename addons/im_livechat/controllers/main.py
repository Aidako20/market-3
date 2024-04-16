#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromflectraimporthttp,tools,_
fromflectra.httpimportrequest
fromflectra.addons.base.models.assetsbundleimportAssetsBundle


classLivechatController(http.Controller):

    #Note:the`cors`attributeonmanyroutesismeanttoallowthelivechat
    #tobeembeddedinanexternalwebsite.

    @http.route('/im_livechat/external_lib.<any(css,js):ext>',type='http',auth='public')
    deflivechat_lib(self,ext,**kwargs):
        #_get_assetreturnthebundlehtmlcode(scriptandlinklist)butwewanttousetheattachmentcontent
        xmlid='im_livechat.external_lib'
        files,remains=request.env["ir.qweb"]._get_asset_content(xmlid,options=request.context)
        asset=AssetsBundle(xmlid,files)

        mock_attachment=getattr(asset,ext)()
        ifisinstance(mock_attachment,list): #supposethatCSSassetwillnotrequiredtobesplitinpages
            mock_attachment=mock_attachment[0]
        #can'tuse/web/contentdirectlybecausewedon'thaveattachmentids(attachmentsmustbecreated)
        status,headers,content=request.env['ir.http'].binary_content(id=mock_attachment.id,unique=asset.checksum)
        content_base64=base64.b64decode(content)ifcontentelse''
        headers.append(('Content-Length',len(content_base64)))
        returnrequest.make_response(content_base64,headers)

    @http.route('/im_livechat/load_templates',type='json',auth='none',cors="*")
    defload_templates(self,**kwargs):
        base_url=request.httprequest.base_url
        templates=[
            'im_livechat/static/src/legacy/public_livechat.xml',
        ]
        return[tools.file_open(tmpl,'rb').read()fortmplintemplates]

    @http.route('/im_livechat/support/<int:channel_id>',type='http',auth='public')
    defsupport_page(self,channel_id,**kwargs):
        channel=request.env['im_livechat.channel'].sudo().browse(channel_id)
        returnrequest.render('im_livechat.support_page',{'channel':channel})

    @http.route('/im_livechat/loader/<int:channel_id>',type='http',auth='public')
    defloader(self,channel_id,**kwargs):
        username=kwargs.get("username",_("Visitor"))
        channel=request.env['im_livechat.channel'].sudo().browse(channel_id)
        info=channel.get_livechat_info(username=username)
        returnrequest.render('im_livechat.loader',{'info':info,'web_session_required':True},headers=[('Content-Type','application/javascript')])

    @http.route('/im_livechat/init',type='json',auth="public",cors="*")
    deflivechat_init(self,channel_id):
        available=len(request.env['im_livechat.channel'].sudo().browse(channel_id)._get_available_users())
        rule={}
        ifavailable:
            #findthecountryfromtherequest
            country_id=False
            country_code=request.session.geoipandrequest.session.geoip.get('country_code')orFalse
            ifcountry_code:
                country_ids=request.env['res.country'].sudo().search([('code','=',country_code)])
                ifcountry_ids:
                    country_id=country_ids[0].id
            #extracturl
            url=request.httprequest.headers.get('Referer')
            #findthefirstmatchingruleforthegivencountryandurl
            matching_rule=request.env['im_livechat.channel.rule'].sudo().match_rule(channel_id,url,country_id)
            ifmatching_rule:
                rule={
                    'action':matching_rule.action,
                    'auto_popup_timer':matching_rule.auto_popup_timer,
                    'regex_url':matching_rule.regex_url,
                }
        return{
            'available_for_me':availableand(notruleorrule['action']!='hide_button'),
            'rule':rule,
        }

    @http.route('/im_livechat/get_session',type="json",auth='public',cors="*")
    defget_session(self,channel_id,anonymous_name,previous_operator_id=None,**kwargs):
        user_id=None
        country_id=None
        #iftheuserisidentifiy(eg:portaluseronthefrontend),don'tusetheanonymousname.Theuserwillbeaddedtosession.
        ifrequest.session.uid:
            user_id=request.env.user.id
            country_id=request.env.user.country_id.id
        else:
            #ifgeoip,addthecountrynametotheanonymousname
            ifrequest.session.geoip:
                #getthecountryoftheanonymousperson,ifany
                country_code=request.session.geoip.get('country_code',"")
                country=request.env['res.country'].sudo().search([('code','=',country_code)],limit=1)ifcountry_codeelseNone
                ifcountry:
                    anonymous_name="%s(%s)"%(anonymous_name,country.name)
                    country_id=country.id

        ifprevious_operator_id:
            previous_operator_id=int(previous_operator_id)

        returnrequest.env["im_livechat.channel"].with_context(lang=False).sudo().browse(channel_id)._open_livechat_mail_channel(anonymous_name,previous_operator_id,user_id,country_id)

    @http.route('/im_livechat/feedback',type='json',auth='public',cors="*")
    deffeedback(self,uuid,rate,reason=None,**kwargs):
        Channel=request.env['mail.channel']
        channel=Channel.sudo().search([('uuid','=',uuid)],limit=1)
        ifchannel:
            #limitthecreation:onlyONEratingpersession
            values={
                'rating':rate,
                'consumed':True,
                'feedback':reason,
                'is_internal':False,
            }
            ifnotchannel.rating_ids:
                res_model_id=request.env['ir.model'].sudo().search([('model','=',channel._name)],limit=1).id
                values.update({
                    'res_id':channel.id,
                    'res_model_id':res_model_id,
                })
                #findthepartner(operator)
                ifchannel.channel_partner_ids:
                    values['rated_partner_id']=channel.channel_partner_ids[0]andchannel.channel_partner_ids[0].idorFalse
                #ifloggedinuser,setitspartneronrating
                values['partner_id']=request.env.user.partner_id.idifrequest.session.uidelseFalse
                #createtherating
                rating=request.env['rating.rating'].sudo().create(values)
            else:
                rating=channel.rating_ids[0]
                rating.write(values)
            returnrating.id
        returnFalse

    @http.route('/im_livechat/history',type="json",auth="public",cors="*")
    defhistory_pages(self,pid,channel_uuid,page_history=None):
        partner_ids=(pid,request.env.user.partner_id.id)
        channel=request.env['mail.channel'].sudo().search([('uuid','=',channel_uuid),('channel_partner_ids','in',partner_ids)])
        ifchannel:
            channel._send_history_message(pid,page_history)
        returnTrue

    @http.route('/im_livechat/notify_typing',type='json',auth='public',cors="*")
    defnotify_typing(self,uuid,is_typing):
        """Broadcastthetypingnotificationofthewebsiteusertootherchannelmembers
            :paramuuid:(string)theUUIDofthelivechatchannel
            :paramis_typing:(boolean)tellswhetherthewebsiteuseristypingornot.
        """
        Channel=request.env['mail.channel']
        channel=Channel.sudo().search([('uuid','=',uuid)],limit=1)
        channel.notify_typing(is_typing=is_typing)

    @http.route('/im_livechat/email_livechat_transcript',type='json',auth='public',cors="*")
    defemail_livechat_transcript(self,uuid,email):
        channel=request.env['mail.channel'].sudo().search([
            ('channel_type','=','livechat'),
            ('uuid','=',uuid)],limit=1)
        ifchannel:
            channel._email_livechat_transcript(email)

    @http.route('/im_livechat/visitor_leave_session',type='json',auth="public")
    defvisitor_leave_session(self,uuid):
        """Calledwhenthelivechatvisitorleavestheconversation.
         Thiswillcleanthechatrequestandwarntheoperatorthattheconversationisover.
         Thisallowsalsotore-sendanewchatrequesttothevisitor,aswhilethevisitoris
         inconversationwithanoperator,it'snotpossibletosendthevisitorachatrequest."""
        mail_channel=request.env['mail.channel'].sudo().search([('uuid','=',uuid)])
        ifmail_channel:
            mail_channel._close_livechat_session()
