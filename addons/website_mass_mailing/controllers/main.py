#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimport_
fromflectra.httpimportroute,request
fromflectra.osvimportexpression
fromflectra.addons.mass_mailing.controllers.mainimportMassMailController


classMassMailController(MassMailController):

    @route('/website_mass_mailing/is_subscriber',type='json',website=True,auth="public")
    defis_subscriber(self,list_id,**post):
        email=None
        ifnotrequest.env.user._is_public():
            email=request.env.user.email
        elifrequest.session.get('mass_mailing_email'):
            email=request.session['mass_mailing_email']

        is_subscriber=False
        ifemail:
            contacts_count=request.env['mailing.contact.subscription'].sudo().search_count([('list_id','in',[int(list_id)]),('contact_id.email','=',email),('opt_out','=',False)])
            is_subscriber=contacts_count>0

        return{'is_subscriber':is_subscriber,'email':email}

    @route('/website_mass_mailing/subscribe',type='json',website=True,auth="public")
    defsubscribe(self,list_id,email,**post):
        #FIXMEthe14.0wasreleasedwiththisbutwithoutthegoogle_recaptcha
        #modulebeingaddedasadependencyofthewebsite_mass_mailingmodule.
        #Thisistobefixedinmasterofcoursebutinstable,we'llhaveto
        #usethisworkaround.
        ifhasattr(request.env['ir.http'],'_verify_request_recaptcha_token')\
                andnotrequest.env['ir.http']._verify_request_recaptcha_token('website_mass_mailing_subscribe'):
            return{
                'toast_type':'danger',
                'toast_content':_("SuspiciousactivitydetectedbyGooglereCaptcha."),
            }
        ContactSubscription=request.env['mailing.contact.subscription'].sudo()
        Contacts=request.env['mailing.contact'].sudo()
        name,email=Contacts.get_name_email(email)

        subscription=ContactSubscription.search([('list_id','=',int(list_id)),('contact_id.email','=',email)],limit=1)
        ifnotsubscription:
            #inlineadd_to_listaswe'vealreadycalledhalfofit
            contact_id=Contacts.search([('email','=',email)],limit=1)
            ifnotcontact_id:
                contact_id=Contacts.create({'name':name,'email':email})
            ContactSubscription.create({'contact_id':contact_id.id,'list_id':int(list_id)})
        elifsubscription.opt_out:
            subscription.opt_out=False
        #addemailtosession
        request.session['mass_mailing_email']=email
        mass_mailing_list=request.env['mailing.list'].sudo().browse(list_id)
        return{
            'toast_type':'success',
            'toast_content':mass_mailing_list.toast_content
        }

    @route(['/website_mass_mailing/get_content'],type='json',website=True,auth="public")
    defget_mass_mailing_content(self,newsletter_id,**post):
        PopupModel=request.env['website.mass_mailing.popup'].sudo()
        data=self.is_subscriber(newsletter_id,**post)
        domain=expression.AND([request.website.website_domain(),[('mailing_list_id','=',newsletter_id)]])
        mass_mailing_popup=PopupModel.search(domain,limit=1)
        ifmass_mailing_popup:
            data['popup_content']=mass_mailing_popup.popup_content
        else:
            data.update(PopupModel.default_get(['popup_content']))
        returndata

    @route(['/website_mass_mailing/set_content'],type='json',website=True,auth="user")
    defset_mass_mailing_content(self,newsletter_id,content,**post):
        PopupModel=request.env['website.mass_mailing.popup']
        domain=expression.AND([request.website.website_domain(),[('mailing_list_id','=',newsletter_id)]])
        mass_mailing_popup=PopupModel.search(domain,limit=1)
        ifmass_mailing_popup:
            mass_mailing_popup.write({'popup_content':content})
        else:
            PopupModel.create({
                'mailing_list_id':newsletter_id,
                'popup_content':content,
                'website_id':request.website.id,
            })
        returnTrue
