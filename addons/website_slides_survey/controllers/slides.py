#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importwerkzeug
importwerkzeug.utils
importwerkzeug.exceptions

fromflectraimport_
fromflectraimporthttp
fromflectra.exceptionsimportAccessError
fromflectra.httpimportrequest
fromflectra.osvimportexpression

fromflectra.addons.website_slides.controllers.mainimportWebsiteSlides


classWebsiteSlidesSurvey(WebsiteSlides):

    @http.route(['/slides_survey/slide/get_certification_url'],type='http',auth='user',website=True)
    defslide_get_certification_url(self,slide_id,**kw):
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            raisewerkzeug.exceptions.NotFound()
        slide=fetch_res['slide']
        ifslide.channel_id.is_member:
            slide.action_set_viewed()
        certification_url=slide._generate_certification_url().get(slide.id)
        ifnotcertification_url:
            raisewerkzeug.exceptions.NotFound()
        returnwerkzeug.utils.redirect(certification_url)

    @http.route(['/slides_survey/certification/search_read'],type='json',auth='user',methods=['POST'],website=True)
    defslides_certification_search_read(self,fields):
        can_create=request.env['survey.survey'].check_access_rights('create',raise_exception=False)
        return{
            'read_results':request.env['survey.survey'].search_read([('certification','=',True)],fields),
            'can_create':can_create,
        }

    #------------------------------------------------------------
    #Overrides
    #------------------------------------------------------------

    @http.route(['/slides/add_slide'],type='json',auth='user',methods=['POST'],website=True)
    defcreate_slide(self,*args,**post):
        create_new_survey=post['slide_type']=="certification"andpost.get('survey')andnotpost['survey']['id']
        linked_survey_id=int(post.get('survey',{}).get('id')or0)

        ifcreate_new_survey:
            #Ifusercannotcreateanewsurvey,noneedtocreatetheslideeither.
            ifnotrequest.env['survey.survey'].check_access_rights('create',raise_exception=False):
                return{'error':_('Youarenotallowedtocreateasurvey.')}

            #Createsurveyfirstascertificationslideneedsasurvey_id(constraint)
            post['survey_id']=request.env['survey.survey'].create({
                'title':post['survey']['title'],
                'questions_layout':'page_per_question',
                'is_attempts_limited':True,
                'attempts_limit':1,
                'is_time_limited':False,
                'scoring_type':'scoring_without_answers',
                'certification':True,
                'scoring_success_min':70.0,
                'certification_mail_template_id':request.env.ref('survey.mail_template_certification').id,
            }).id
        eliflinked_survey_id:
            try:
                request.env['survey.survey'].browse([linked_survey_id]).read(['title'])
            exceptAccessError:
                return{'error':_('Youarenotallowedtolinkacertification.')}

            post['survey_id']=post['survey']['id']

        #Thencreatetheslide
        result=super(WebsiteSlidesSurvey,self).create_slide(*args,**post)

        ifcreate_new_survey:
            #Settheredirect_urlusedintoaster
            action_id=request.env.ref('survey.action_survey_form').id
            result.update({
                'redirect_url':'/web#id=%s&action=%s&model=survey.survey&view_type=form'%(post['survey_id'],action_id),
                'redirect_to_certification':True
            })

        returnresult

    #Utils
    #---------------------------------------------------
    def_set_completed_slide(self,slide):
        ifslide.slide_type=='certification':
            raisewerkzeug.exceptions.Forbidden(_("Certificationslidesarecompletedwhenthesurveyissucceeded."))
        returnsuper(WebsiteSlidesSurvey,self)._set_completed_slide(slide)

    def_get_valid_slide_post_values(self):
        result=super(WebsiteSlidesSurvey,self)._get_valid_slide_post_values()
        result.append('survey_id')
        returnresult

    #Profile
    #---------------------------------------------------
    def_prepare_user_slides_profile(self,user):
        values=super(WebsiteSlidesSurvey,self)._prepare_user_slides_profile(user)
        values.update({
            'certificates':self._get_users_certificates(user)[user.id]
        })
        returnvalues

    #AllUsersPage
    #---------------------------------------------------
    def_prepare_all_users_values(self,users):
        result=super(WebsiteSlidesSurvey,self)._prepare_all_users_values(users)
        certificates_per_user=self._get_users_certificates(users)
        forindex,userinenumerate(users):
            result[index].update({
                'certification_count':len(certificates_per_user.get(user.id,[]))
            })
        returnresult

    def_get_users_certificates(self,users):
        partner_ids=[user.partner_id.idforuserinusers]
        domain=[
            ('slide_partner_id.partner_id','in',partner_ids),
            ('scoring_success','=',True),
            ('slide_partner_id.survey_scoring_success','=',True)
        ]
        certificates=request.env['survey.user_input'].sudo().search(domain)
        users_certificates={
            user.id:[
                certificateforcertificateincertificatesifcertificate.partner_id==user.partner_id
            ]foruserinusers
        }
        returnusers_certificates

    #Badges&RanksPage
    #---------------------------------------------------
    def_prepare_ranks_badges_values(self,**kwargs):
        """Extractcertificationbadges,torendertheminranks/badgespageinanothersection.
        Orderthembynumberofgrantedusersdescandshowonlybadgeslinkedtoopenedcertifications."""
        values=super(WebsiteSlidesSurvey,self)._prepare_ranks_badges_values(**kwargs)

        #1.Gettingallcertificationbadges,sortedbygranteduserdesc
        domain=expression.AND([[('survey_id','!=',False)],self._prepare_badges_domain(**kwargs)])
        certification_badges=request.env['gamification.badge'].sudo().search(domain)
        #keeponlythebadgewithchallengecategory=slides(therestwillbedisplayedunder'normalbadges'section
        certification_badges=certification_badges.filtered(
            lambdab:'slides'inb.challenge_ids.mapped('challenge_category'))

        ifnotcertification_badges:
            returnvalues

        #2.sortbygrantedusers(donehere,andnotinsearchdirectly,becausenonstoredfield)
        certification_badges=certification_badges.sorted("granted_users_count",reverse=True)

        #3.Removecertificationbadgefrombadgesandkeeponlycertificationbadgelinkedtoopenedsurvey
        badges=values['badges']-certification_badges
        certification_badges=certification_badges.filtered(lambdab:b.survey_id.state=='open')

        #4.Gettingallcourseurlforeachbadge
        certification_slides=request.env['slide.slide'].sudo().search([('survey_id','in',certification_badges.mapped('survey_id').ids)])
        certification_badge_urls={slide.survey_id.certification_badge_id.id:slide.channel_id.website_urlforslideincertification_slides}

        #5.Applyingchanges
        values.update({
            'badges':badges,
            'certification_badges':certification_badges,
            'certification_badge_urls':certification_badge_urls
        })
        returnvalues
