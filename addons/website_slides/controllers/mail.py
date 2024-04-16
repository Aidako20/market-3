#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug

fromwerkzeug.exceptionsimportNotFound,Forbidden

fromflectraimporthttp
fromflectra.httpimportrequest
fromflectra.addons.portal.controllers.mailimport_check_special_access,PortalChatter
fromflectra.toolsimportplaintext2html,html2plaintext


classSlidesPortalChatter(PortalChatter):

    @http.route(['/mail/chatter_post'],type='http',methods=['POST'],auth='public',website=True)
    defportal_chatter_post(self,res_model,res_id,message,**kw):
        result=super(SlidesPortalChatter,self).portal_chatter_post(res_model,res_id,message,**kw)
        ifres_model=='slide.channel':
            rating_value=kw.get('rating_value',False)
            slide_channel=request.env[res_model].sudo().browse(int(res_id))
            ifrating_valueandslide_channelandrequest.env.user.partner_id.id==int(kw.get('pid')):
                #applykarmagainruleonlyonce
                request.env.user.add_karma(slide_channel.karma_gen_channel_rank)
        returnresult

    @http.route([
        '/slides/mail/update_comment',
        '/mail/chatter_update',
        ],type='http',auth="user",methods=['POST'])
    defmail_update_message(self,res_model,res_id,message,message_id,redirect=None,attachment_ids='',attachment_tokens='',**post):
        #keepthismechanisminterntoslidecurrently(saas12.5)asitis
        #consideredexperimental
        ifres_model!='slide.channel':
            raiseForbidden()
        res_id=int(res_id)

        attachment_ids=[int(attachment_id)forattachment_idinattachment_ids.split(',')ifattachment_id]
        attachment_tokens=[attachment_tokenforattachment_tokeninattachment_tokens.split(',')ifattachment_token]
        self._portal_post_check_attachments(attachment_ids,attachment_tokens)

        pid=int(post['pid'])ifpost.get('pid')elseFalse
        ifnot_check_special_access(res_model,res_id,token=post.get('token'),_hash=post.get('hash'),pid=pid):
            raiseForbidden()

        #fetchandupdatemail.message
        message_id=int(message_id)
        message_body=plaintext2html(message)
        subtype_comment_id=request.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
        domain=[
            ('model','=',res_model),
            ('res_id','=',res_id),
            ('subtype_id','=',subtype_comment_id),
            ('author_id','=',request.env.user.partner_id.id),
            ('message_type','=','comment'),
            ('id','=',message_id)
        ] #restricttothegivenmessage_id
        message=request.env['mail.message'].search(domain,limit=1)
        ifnotmessage:
            raiseNotFound()
        message.sudo().write({
            'body':message_body,
            'attachment_ids':[(4,aid)foraidinattachment_ids],
        })

        #updaterating
        ifpost.get('rating_value'):
            domain=[('res_model','=',res_model),('res_id','=',res_id),('message_id','=',message.id)]
            rating=request.env['rating.rating'].sudo().search(domain,order='write_dateDESC',limit=1)
            rating.write({
                'rating':float(post['rating_value']),
                'feedback':html2plaintext(message.body),
            })

        #redirecttospecifiedorreferrerorsimplychannelpageasfallback
        redirect_url=redirector(request.httprequest.referrerandrequest.httprequest.referrer+'#review')or'/slides/%s'%res_id
        returnwerkzeug.utils.redirect(redirect_url,302)
