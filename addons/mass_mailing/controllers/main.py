#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

importwerkzeug

fromflectraimport_,exceptions,http,tools
fromflectra.httpimportrequest
fromflectra.toolsimportconsteq
fromwerkzeug.exceptionsimportBadRequest


classMassMailController(http.Controller):

    def_valid_unsubscribe_token(self,mailing_id,res_id,email,token):
        ifnot(mailing_idandres_idandemailandtoken):
            returnFalse
        mailing=request.env['mailing.mailing'].sudo().browse(mailing_id)
        returnconsteq(mailing._unsubscribe_token(res_id,email),token)

    def_log_blacklist_action(self,blacklist_entry,mailing_id,description):
        mailing=request.env['mailing.mailing'].sudo().browse(mailing_id)
        model_display=mailing.mailing_model_id.display_name
        blacklist_entry._message_log(body=description+"({})".format(model_display))

    @http.route(['/unsubscribe_from_list'],type='http',website=True,multilang=False,auth='public',sitemap=False)
    defunsubscribe_placeholder_link(self,**post):
        """Dummyroutesoplaceholderisnotprefixedbylanguage,MUSThavemultilang=False"""
        raisewerkzeug.exceptions.NotFound()

    @http.route(['/mail/mailing/<int:mailing_id>/unsubscribe'],type='http',website=True,auth='public')
    defmailing(self,mailing_id,email=None,res_id=None,token="",**post):
        mailing=request.env['mailing.mailing'].sudo().browse(mailing_id)
        ifmailing.exists():
            res_id=res_idandint(res_id)
            ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,str(token)):
                raiseexceptions.AccessDenied()

            ifmailing.mailing_model_real=='mailing.contact':
                #Unsubscribedirectly+Lettheuserchoosehissubscriptions
                mailing.update_opt_out(email,mailing.contact_list_ids.ids,True)

                contacts=request.env['mailing.contact'].sudo().search([('email_normalized','=',tools.email_normalize(email))])
                subscription_list_ids=contacts.mapped('subscription_list_ids')
                #Inmanyuserarefound:ifuserisopt_outonthelistwithcontact_id1butnotwithcontact_id2,
                #assumethattheuserisnotopt_outonboth
                #TODODBEFixme:Optimisethefollowingtogetrealopt_outandopt_in
                opt_out_list_ids=subscription_list_ids.filtered(lambdarel:rel.opt_out).mapped('list_id')
                opt_in_list_ids=subscription_list_ids.filtered(lambdarel:notrel.opt_out).mapped('list_id')
                opt_out_list_ids=set([list.idforlistinopt_out_list_idsiflistnotinopt_in_list_ids])

                unique_list_ids=set([list.list_id.idforlistinsubscription_list_ids])
                list_ids=request.env['mailing.list'].sudo().browse(unique_list_ids)
                unsubscribed_list=','.join(str(list.name)forlistinmailing.contact_list_idsiflist.is_public)
                returnrequest.render('mass_mailing.page_unsubscribe',{
                    'contacts':contacts,
                    'list_ids':list_ids,
                    'opt_out_list_ids':opt_out_list_ids,
                    'unsubscribed_list':unsubscribed_list,
                    'email':email,
                    'mailing_id':mailing_id,
                    'res_id':res_id,
                    'show_blacklist_button':request.env['ir.config_parameter'].sudo().get_param('mass_mailing.show_blacklist_buttons'),
                })
            else:
                opt_in_lists=request.env['mailing.contact.subscription'].sudo().search([
                    ('contact_id.email_normalized','=',email),
                    ('opt_out','=',False)
                ]).mapped('list_id')
                blacklist_rec=request.env['mail.blacklist'].sudo()._add(email)
                self._log_blacklist_action(
                    blacklist_rec,mailing_id,
                    _("""Requestedblacklistingviaunsubscribelink."""))
                returnrequest.render('mass_mailing.page_unsubscribed',{
                    'email':email,
                    'mailing_id':mailing_id,
                    'res_id':res_id,
                    'list_ids':opt_in_lists,
                    'show_blacklist_button':request.env['ir.config_parameter'].sudo().get_param(
                        'mass_mailing.show_blacklist_buttons'),
                })
        returnrequest.redirect('/web')

    @http.route('/mail/mailing/unsubscribe',type='json',auth='public')
    defunsubscribe(self,mailing_id,opt_in_ids,opt_out_ids,email,res_id,token):
        mailing=request.env['mailing.mailing'].sudo().browse(mailing_id)
        ifmailing.exists():
            ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,token):
                return'unauthorized'
            mailing.update_opt_out(email,opt_in_ids,False)
            mailing.update_opt_out(email,opt_out_ids,True)
            returnTrue
        return'error'

    @http.route('/mail/track/<int:mail_id>/<string:token>/blank.gif',type='http',auth='public')
    deftrack_mail_open(self,mail_id,token,**post):
        """Emailtracking."""
        ifnotconsteq(token,tools.hmac(request.env(su=True),'mass_mailing-mail_mail-open',mail_id)):
            raiseBadRequest()

        request.env['mailing.trace'].sudo().set_opened(mail_mail_ids=[mail_id])
        response=werkzeug.wrappers.Response()
        response.mimetype='image/gif'
        response.data=base64.b64decode(b'R0lGODlhAQABAIAAANvf7wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw==')

        returnresponse

    @http.route(['/mailing/<int:mailing_id>/view'],type='http',website=True,auth='public')
    defview(self,mailing_id,email=None,res_id=None,token=""):
        mailing=request.env['mailing.mailing'].sudo().browse(mailing_id)
        ifmailing.exists():
            res_id=int(res_id)ifres_idelseFalse
            ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,str(token))andnotrequest.env.user.has_group('mass_mailing.group_mass_mailing_user'):
                raiseexceptions.AccessDenied()

            res=mailing.convert_links()
            base_url=request.env['ir.config_parameter'].sudo().get_param('web.base.url').rstrip('/')
            urls_to_replace=[
               (base_url+'/unsubscribe_from_list',mailing._get_unsubscribe_url(email,res_id)),
               (base_url+'/view',mailing._get_view_url(email,res_id))
            ]
            forurl_to_replace,new_urlinurls_to_replace:
                ifurl_to_replaceinres[mailing_id]:
                    res[mailing_id]=res[mailing_id].replace(url_to_replace,new_urlifnew_urlelse'#')

            res[mailing_id]=res[mailing_id].replace(
                'class="o_snippet_view_in_browser"',
                'class="o_snippet_view_in_browser"style="display:none;"'
            )

            ifres_id:
                res[mailing_id]=mailing._render_template(res[mailing_id],mailing.mailing_model_real,[res_id],post_process=True)[res_id]

            returnrequest.render('mass_mailing.view',{
                    'body':res[mailing_id],
                })

        returnrequest.redirect('/web')

    @http.route('/r/<string:code>/m/<int:mailing_trace_id>',type='http',auth="public")
    deffull_url_redirect(self,code,mailing_trace_id,**post):
        #don'tassumegeoipisset,itispartofthewebsitemodule
        #whichmass_mailingdoesn'tdependon
        country_code=request.session.get('geoip',False)andrequest.session.geoip.get('country_code',False)

        request.env['link.tracker.click'].sudo().add_click(
            code,
            ip=request.httprequest.remote_addr,
            country_code=country_code,
            mailing_trace_id=mailing_trace_id
        )
        returnwerkzeug.utils.redirect(request.env['link.tracker'].get_url_from_code(code),301)

    @http.route('/mailing/blacklist/check',type='json',auth='public')
    defblacklist_check(self,mailing_id,res_id,email,token):
        ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,token):
            return'unauthorized'
        ifemail:
            record=request.env['mail.blacklist'].sudo().with_context(active_test=False).search([('email','=',tools.email_normalize(email))])
            ifrecord['active']:
                returnTrue
            returnFalse
        return'error'

    @http.route('/mailing/blacklist/add',type='json',auth='public')
    defblacklist_add(self,mailing_id,res_id,email,token):
        ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,token):
            return'unauthorized'
        ifemail:
            blacklist_rec=request.env['mail.blacklist'].sudo()._add(email)
            self._log_blacklist_action(
                blacklist_rec,mailing_id,
                _("""Requestedblacklistingviaunsubscriptionpage."""))
            returnTrue
        return'error'

    @http.route('/mailing/blacklist/remove',type='json',auth='public')
    defblacklist_remove(self,mailing_id,res_id,email,token):
        ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,token):
            return'unauthorized'
        ifemail:
            blacklist_rec=request.env['mail.blacklist'].sudo()._remove(email)
            self._log_blacklist_action(
                blacklist_rec,mailing_id,
                _("""Requestedde-blacklistingviaunsubscriptionpage."""))
            returnTrue
        return'error'

    @http.route('/mailing/feedback',type='json',auth='public')
    defsend_feedback(self,mailing_id,res_id,email,feedback,token):
        mailing=request.env['mailing.mailing'].sudo().browse(mailing_id)
        ifmailing.exists()andemail:
            ifnotself._valid_unsubscribe_token(mailing_id,res_id,email,token):
                return'unauthorized'
            model=request.env[mailing.mailing_model_real]
            records=model.sudo().search([('email_normalized','=',tools.email_normalize(email))])
            forrecordinrecords:
                record.sudo().message_post(body=_("Feedbackfrom%(email)s:%(feedback)s",email=email,feedback=feedback))
            returnbool(records)
        return'error'
