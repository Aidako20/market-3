#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importjson
importlogging
importwerkzeug
importmath

fromastimportliteral_eval
fromcollectionsimportdefaultdict

fromflectraimporthttp,tools,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.website_profile.controllers.mainimportWebsiteProfile
fromflectra.addons.website.models.ir_httpimportsitemap_qs2dom
fromflectra.exceptionsimportAccessError,UserError
fromflectra.httpimportrequest
fromflectra.osvimportexpression

_logger=logging.getLogger(__name__)


classWebsiteSlides(WebsiteProfile):
    _slides_per_page=12
    _slides_per_aside=20
    _slides_per_category=4
    _channel_order_by_criterion={
        'vote':'total_votesdesc',
        'view':'total_viewsdesc',
        'date':'create_datedesc',
    }

    defsitemap_slide(env,rule,qs):
        Channel=env['slide.channel']
        dom=sitemap_qs2dom(qs=qs,route='/slides/',field=Channel._rec_name)
        dom+=env['website'].get_current_website().website_domain()
        forchannelinChannel.search(dom):
            loc='/slides/%s'%slug(channel)
            ifnotqsorqs.lower()inloc:
                yield{'loc':loc}

    #SLIDEUTILITIES
    #--------------------------------------------------

    def_fetch_slide(self,slide_id):
        slide=request.env['slide.slide'].browse(int(slide_id)).exists()
        ifnotslide:
            return{'error':'slide_wrong'}
        try:
            slide.check_access_rights('read')
            slide.check_access_rule('read')
        exceptAccessError:
            return{'error':'slide_access'}
        return{'slide':slide}

    def_set_viewed_slide(self,slide,quiz_attempts_inc=False):
        ifrequest.env.user._is_public()ornotslide.website_publishedornotslide.channel_id.is_member:
            viewed_slides=request.session.setdefault('viewed_slides',list())
            ifslide.idnotinviewed_slides:
                iftools.sql.increment_field_skiplock(slide,'public_views'):
                    viewed_slides.append(slide.id)
                    request.session['viewed_slides']=viewed_slides
        else:
            slide.action_set_viewed(quiz_attempts_inc=quiz_attempts_inc)
        returnTrue

    def_set_completed_slide(self,slide):
        #quizusetheirspecificmechanismtobemarkedasdone
        ifslide.slide_type=='quiz'orslide.question_ids:
            raiseUserError(_("Slidewithquestionsmustbemarkedasdonewhensubmittingallgoodanswers"))
        ifslide.website_publishedandslide.channel_id.is_member:
            slide.action_set_completed()
        returnTrue

    def_get_slide_detail(self,slide):
        base_domain=self._get_channel_slides_base_domain(slide.channel_id)
        ifslide.channel_id.channel_type=='documentation':
            related_domain=expression.AND([base_domain,[('category_id','=',slide.category_id.id)]])

            most_viewed_slides=request.env['slide.slide'].search(base_domain,limit=self._slides_per_aside,order='total_viewsdesc')
            related_slides=request.env['slide.slide'].search(related_domain,limit=self._slides_per_aside)
            category_data=[]
            uncategorized_slides=request.env['slide.slide']
        else:
            most_viewed_slides,related_slides=request.env['slide.slide'],request.env['slide.slide']
            category_data=slide.channel_id._get_categorized_slides(
                base_domain,order=request.env['slide.slide']._order_by_strategy['sequence'],
                force_void=True)
            #temporarilykeptforfullscreen,toremoveasap
            uncategorized_domain=expression.AND([base_domain,[('channel_id','=',slide.channel_id.id),('category_id','=',False)]])
            uncategorized_slides=request.env['slide.slide'].search(uncategorized_domain)

        channel_slides_ids=slide.channel_id.slide_content_ids.ids
        slide_index=channel_slides_ids.index(slide.id)
        previous_slide=slide.channel_id.slide_content_ids[slide_index-1]ifslide_index>0elseNone
        next_slide=slide.channel_id.slide_content_ids[slide_index+1]ifslide_index<len(channel_slides_ids)-1elseNone

        values={
            #slide
            'slide':slide,
            'main_object':slide,
            'most_viewed_slides':most_viewed_slides,
            'related_slides':related_slides,
            'previous_slide':previous_slide,
            'next_slide':next_slide,
            'uncategorized_slides':uncategorized_slides,
            'category_data':category_data,
            #user
            'user':request.env.user,
            'is_public_user':request.website.is_public_user(),
            #ratingandcomments
            'comments':slide.website_message_idsor[],
        }

        #allowratingandcomments
        ifslide.channel_id.allow_comment:
            values.update({
                'message_post_pid':request.env.user.partner_id.id,
            })

        returnvalues

    def_get_slide_quiz_partner_info(self,slide,quiz_done=False):
        returnslide._compute_quiz_info(request.env.user.partner_id,quiz_done=quiz_done)[slide.id]

    def_get_slide_quiz_data(self,slide):
        slide_completed=slide.user_membership_id.sudo().completed
        values={
            'slide_questions':[{
                'id':question.id,
                'question':question.question,
                'answer_ids':[{
                    'id':answer.id,
                    'text_value':answer.text_value,
                    'is_correct':answer.is_correctifslide_completedorrequest.website.is_publisher()elseNone,
                    'comment':answer.commentifrequest.website.is_publisher()elseNone
                }foranswerinquestion.sudo().answer_ids],
            }forquestioninslide.question_ids]
        }
        if'slide_answer_quiz'inrequest.session:
            slide_answer_quiz=json.loads(request.session['slide_answer_quiz'])
            ifstr(slide.id)inslide_answer_quiz:
                values['session_answers']=slide_answer_quiz[str(slide.id)]
        values.update(self._get_slide_quiz_partner_info(slide))
        returnvalues

    def_get_new_slide_category_values(self,channel,name):
        return{
            'name':name,
            'channel_id':channel.id,
            'is_category':True,
            'is_published':True,
            'sequence':channel.slide_ids[-1]['sequence']+1ifchannel.slide_idselse1,
        }

    #CHANNELUTILITIES
    #--------------------------------------------------

    def_get_channel_slides_base_domain(self,channel):
        """basedomainwhenfetchingslidelistdatarelatedtoagivenchannel

         *websiterelateddomain,andrestrictedtothechannelandisnota
           categoryslide(behaviorisdifferentfromclassicslide);
         *ifpublisher:everythingisok;
         *ifnotpublisherbuthasuser:eitherslideispublished,either
           currentuseristheonethatuploadedit;
         *ifnotpublisherandpublic:published;
        """
        base_domain=expression.AND([request.website.website_domain(),['&',('channel_id','=',channel.id),('is_category','=',False)]])
        ifnotchannel.can_publish:
            ifrequest.website.is_public_user():
                base_domain=expression.AND([base_domain,[('website_published','=',True)]])
            else:
                base_domain=expression.AND([base_domain,['|',('website_published','=',True),('user_id','=',request.env.user.id)]])
        returnbase_domain

    def_get_channel_progress(self,channel,include_quiz=False):
        """Replacementtouser_progress.Bothmayexistinsometransientstate."""
        slides=request.env['slide.slide'].sudo().search([('channel_id','=',channel.id)])
        channel_progress=dict((sid,dict())forsidinslides.ids)
        ifnotrequest.env.user._is_public()andchannel.is_member:
            slide_partners=request.env['slide.slide.partner'].sudo().search([
                ('channel_id','=',channel.id),
                ('partner_id','=',request.env.user.partner_id.id),
                ('slide_id','in',slides.ids)
            ])
            forslide_partnerinslide_partners:
                channel_progress[slide_partner.slide_id.id].update(slide_partner.read()[0])
                ifslide_partner.slide_id.question_ids:
                    gains=[slide_partner.slide_id.quiz_first_attempt_reward,
                             slide_partner.slide_id.quiz_second_attempt_reward,
                             slide_partner.slide_id.quiz_third_attempt_reward,
                             slide_partner.slide_id.quiz_fourth_attempt_reward]
                    channel_progress[slide_partner.slide_id.id]['quiz_gain']=gains[slide_partner.quiz_attempts_count]ifslide_partner.quiz_attempts_count<len(gains)elsegains[-1]

        ifinclude_quiz:
            quiz_info=slides._compute_quiz_info(request.env.user.partner_id,quiz_done=False)
            forslide_id,slide_infoinquiz_info.items():
                channel_progress[slide_id].update(slide_info)

        returnchannel_progress

    def_extract_channel_tag_search(self,**post):
        tags=request.env['slide.channel.tag']
        ifpost.get('tags'):
            try:
                tag_ids=literal_eval(post['tags'])
            except:
                pass
            else:
                #performasearchtofilteronexisting/validtagsimplicitely
                tags=request.env['slide.channel.tag'].search([('id','in',tag_ids)])
        returntags

    def_build_channel_domain(self,base_domain,slide_type=None,my=False,**post):
        search_term=post.get('search')
        tags=self._extract_channel_tag_search(**post)

        domain=base_domain
        ifsearch_term:
            domain=expression.AND([
                domain,
                ['|',('name','ilike',search_term),('description','ilike',search_term)]])

        iftags:
            #Groupbygroup_id
            grouped_tags=defaultdict(list)
            fortagintags:
                grouped_tags[tag.group_id].append(tag)

            #ORinsideagroup,ANDbetweengroups.
            group_domain_list=[]
            forgroupingrouped_tags:
                group_domain_list.append([('tag_ids','in',[tag.idfortagingrouped_tags[group]])])

            domain=expression.AND([domain,*group_domain_list])

        ifslide_typeand'nbr_%s'%slide_typeinrequest.env['slide.channel']:
            domain=expression.AND([domain,[('nbr_%s'%slide_type,'>',0)]])

        ifmy:
            domain=expression.AND([domain,[('partner_ids','=',request.env.user.partner_id.id)]])
        returndomain

    def_channel_remove_session_answers(self,channel,slide=False):
        """Willremovetheanswerssavedinthesessionforaspecificchannel/slide."""

        if'slide_answer_quiz'notinrequest.session:
            return

        slides_domain=[('channel_id','=',channel.id)]
        ifslide:
            slides_domain=expression.AND([slides_domain,[('id','=',slide.id)]])
        slides=request.env['slide.slide'].search_read(slides_domain,['id'])

        session_slide_answer_quiz=json.loads(request.session['slide_answer_quiz'])
        forslideinslides:
            session_slide_answer_quiz.pop(str(slide['id']),None)
        request.session['slide_answer_quiz']=json.dumps(session_slide_answer_quiz)

    #TAGUTILITIES
    #--------------------------------------------------

    def_create_or_get_channel_tag(self,tag_id,group_id):
        ifnottag_id:
            returnrequest.env['slide.channel.tag']
        #handlecreationofnewchanneltag
        iftag_id[0]==0:
            group_id=self._create_or_get_channel_tag_group(group_id)
            ifnotgroup_id:
                return{'error':_('Missing"TagGroup"forcreatinganew"Tag".')}

            new_tag=request.env['slide.channel.tag'].create({
                'name':tag_id[1]['name'],
                'group_id':group_id,
            })
            returnnew_tag
        returnrequest.env['slide.channel.tag'].browse(tag_id[0])

    def_create_or_get_channel_tag_group(self,group_id):
        ifnotgroup_id:
            returnFalse
        #handlecreationofnewchanneltaggroup
        ifgroup_id[0]==0:
            tag_group=request.env['slide.channel.tag.group'].create({
                'name':group_id[1]['name'],
            })
            group_id=tag_group.id
        #useexistingchanneltaggroup
        returngroup_id[0]

    #--------------------------------------------------
    #SLIDE.CHANNELMAIN/SEARCH
    #--------------------------------------------------

    @http.route('/slides',type='http',auth="public",website=True,sitemap=True)
    defslides_channel_home(self,**post):
        """HomepageforeLearningplatform.Ismainlyacontainerpage,doesnotallowsearch/filter."""
        domain=request.website.website_domain()
        channels_all=request.env['slide.channel'].search(domain)
        ifnotrequest.env.user._is_public():
            #Ifacourseiscompleted,wedon'twanttoseeitinfirstpositionbutinlast
            channels_my=channels_all.filtered(lambdachannel:channel.is_member).sorted(lambdachannel:0ifchannel.completedelsechannel.completion,reverse=True)[:3]
        else:
            channels_my=request.env['slide.channel']
        channels_popular=channels_all.sorted('total_votes',reverse=True)[:3]
        channels_newest=channels_all.sorted('create_date',reverse=True)[:3]

        achievements=request.env['gamification.badge.user'].sudo().search([('badge_id.is_published','=',True)],limit=5)
        ifrequest.env.user._is_public():
            challenges=None
            challenges_done=None
        else:
            challenges=request.env['gamification.challenge'].sudo().search([
                ('challenge_category','=','slides'),
                ('reward_id.is_published','=',True)
            ],order='idasc',limit=5)
            challenges_done=request.env['gamification.badge.user'].sudo().search([
                ('challenge_id','in',challenges.ids),
                ('user_id','=',request.env.user.id),
                ('badge_id.is_published','=',True)
            ]).mapped('challenge_id')

        users=request.env['res.users'].sudo().search([
            ('karma','>',0),
            ('website_published','=',True)],limit=5,order='karmadesc')

        values=self._prepare_user_values(**post)
        values.update({
            'channels_my':channels_my,
            'channels_popular':channels_popular,
            'channels_newest':channels_newest,
            'achievements':achievements,
            'users':users,
            'top3_users':self._get_top3_users(),
            'challenges':challenges,
            'challenges_done':challenges_done,
            'search_tags':request.env['slide.channel.tag']
        })

        returnrequest.render('website_slides.courses_home',values)

    @http.route('/slides/all',type='http',auth="public",website=True,sitemap=True)
    defslides_channel_all(self,slide_type=None,my=False,**post):
        """Homepagedisplayingalistofcoursesdisplayedaccordingtosome
        criterionandsearchterms.

          :paramstringslide_type:ifprovided,filterthecoursetocontainat
           leastoneslideoftype'slide_type'.Usednotablytodisplaycourses
           withcertifications;
          :paramboolmy:ifprovided,filtertheslide.channelsforwhichthe
           currentuserisamemberof
          :paramdictpost:postparameters,including

           *``search``:filteroncoursedescription/name;
           *``channel_tag_id``:filteroncoursescontainingthistag;
           *``channel_tag_group_id_<id>``:filteroncoursescontainingthistag
             inthetaggroupgivenby<id>(usedinnavigationbasedontaggroup);
        """
        domain=request.website.website_domain()
        domain=self._build_channel_domain(domain,slide_type=slide_type,my=my,**post)

        order=self._channel_order_by_criterion.get(post.get('sorting'))

        channels=request.env['slide.channel'].search(domain,order=order)
        #channels_layouted=list(itertools.zip_longest(*[iter(channels)]*4,fillvalue=None))

        tag_groups=request.env['slide.channel.tag.group'].search(
            ['&',('tag_ids','!=',False),('website_published','=',True)])
        search_tags=self._extract_channel_tag_search(**post)

        values=self._prepare_user_values(**post)
        values.update({
            'channels':channels,
            'tag_groups':tag_groups,
            'search_term':post.get('search'),
            'search_slide_type':slide_type,
            'search_my':my,
            'search_tags':search_tags,
            'search_channel_tag_id':post.get('channel_tag_id'),
            'top3_users':self._get_top3_users(),
        })

        returnrequest.render('website_slides.courses_all',values)

    def_prepare_additional_channel_values(self,values,**kwargs):
        returnvalues

    def_get_top3_users(self):
        returnrequest.env['res.users'].sudo().search_read([
            ('karma','>',0),
            ('website_published','=',True),
            ('image_1920','!=',False)],['id'],limit=3,order='karmadesc')

    @http.route([
        '/slides/<model("slide.channel"):channel>',
        '/slides/<model("slide.channel"):channel>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>',
        '/slides/<model("slide.channel"):channel>/tag/<model("slide.tag"):tag>/page/<int:page>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>',
        '/slides/<model("slide.channel"):channel>/category/<model("slide.slide"):category>/page/<int:page>',
    ],type='http',auth="public",website=True,sitemap=sitemap_slide)
    defchannel(self,channel,category=None,tag=None,page=1,slide_type=None,uncategorized=False,sorting=None,search=None,**kw):
        """
        Willreturnallnecessarydatatodisplaytherequestedslide_channelalongwithapossiblecategory.
        """
        ifnotchannel.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        domain=self._get_channel_slides_base_domain(channel)

        pager_url="/slides/%s"%(channel.id)
        pager_args={}
        slide_types=dict(request.env['slide.slide']._fields['slide_type']._description_selection(request.env))

        ifsearch:
            domain+=[
                '|','|',
                ('name','ilike',search),
                ('description','ilike',search),
                ('html_content','ilike',search)]
            pager_args['search']=search
        else:
            ifcategory:
                domain+=[('category_id','=',category.id)]
                pager_url+="/category/%s"%category.id
            eliftag:
                domain+=[('tag_ids.id','=',tag.id)]
                pager_url+="/tag/%s"%tag.id
            ifuncategorized:
                domain+=[('category_id','=',False)]
                pager_args['uncategorized']=1
            elifslide_type:
                domain+=[('slide_type','=',slide_type)]
                pager_url+="?slide_type=%s"%slide_type

        #sortingcriterion
        ifchannel.channel_type=='documentation':
            default_sorting='latest'ifchannel.promote_strategyin['specific','none',False]elsechannel.promote_strategy
            actual_sorting=sortingifsortingandsortinginrequest.env['slide.slide']._order_by_strategyelsedefault_sorting
        else:
            actual_sorting='sequence'
        order=request.env['slide.slide']._order_by_strategy[actual_sorting]
        pager_args['sorting']=actual_sorting

        slide_count=request.env['slide.slide'].sudo().search_count(domain)
        page_count=math.ceil(slide_count/self._slides_per_page)
        pager=request.website.pager(url=pager_url,total=slide_count,page=page,
                                      step=self._slides_per_page,url_args=pager_args,
                                      scope=page_countifpage_count<self._pager_max_pageselseself._pager_max_pages)

        query_string=None
        ifcategory:
            query_string="?search_category=%s"%category.id
        eliftag:
            query_string="?search_tag=%s"%tag.id
        elifslide_type:
            query_string="?search_slide_type=%s"%slide_type
        elifuncategorized:
            query_string="?search_uncategorized=1"

        values={
            'channel':channel,
            'main_object':channel,
            'active_tab':kw.get('active_tab','home'),
            #search
            'search_category':category,
            'search_tag':tag,
            'search_slide_type':slide_type,
            'search_uncategorized':uncategorized,
            'query_string':query_string,
            'slide_types':slide_types,
            'sorting':actual_sorting,
            'search':search,
            #chatter
            'rating_avg':channel.rating_avg,
            'rating_count':channel.rating_count,
            #displaydata
            'user':request.env.user,
            'pager':pager,
            'is_public_user':request.website.is_public_user(),
            #displayuploadmodal
            'enable_slide_upload':'enable_slide_upload'inkw,
        }
        ifnotrequest.env.user._is_public():
            subtype_comment_id=request.env['ir.model.data'].xmlid_to_res_id('mail.mt_comment')
            last_message=request.env['mail.message'].search([
                ('model','=',channel._name),
                ('res_id','=',channel.id),
                ('author_id','=',request.env.user.partner_id.id),
                ('message_type','=','comment'),
                ('subtype_id','=',subtype_comment_id)
            ],order='write_dateDESC',limit=1)
            iflast_message:
                last_message_values=last_message.read(['body','rating_value','attachment_ids'])[0]
                last_message_attachment_ids=last_message_values.pop('attachment_ids',[])
                iflast_message_attachment_ids:
                    #usesudoasportalusercannotreadaccess_token,necessaryforupdatingattachments
                    #throughfrontendchatter->accessisalreadygrantedandlimitedtocurrentusermessage
                    last_message_attachment_ids=json.dumps(
                        request.env['ir.attachment'].sudo().browse(last_message_attachment_ids).read(
                            ['id','name','mimetype','file_size','access_token']
                        )
                    )
            else:
                last_message_values={}
                last_message_attachment_ids=[]
            values.update({
                'last_message_id':last_message_values.get('id'),
                'last_message':tools.html2plaintext(last_message_values.get('body','')),
                'last_rating_value':last_message_values.get('rating_value'),
                'last_message_attachment_ids':last_message_attachment_ids,
            })
            ifchannel.can_review:
                values.update({
                    'message_post_hash':channel._sign_token(request.env.user.partner_id.id),
                    'message_post_pid':request.env.user.partner_id.id,
                })

        #fetchslidesandhandleuncategorizedslides;doneassudobecausewewanttodisplayall
        #ofthembutunreachableoneswon'tbeclickable(+slidecontrollerwillcrashanyway)
        #documentationmodemaydisplaylessslidesthancontentbycategorybutoverheadof
        #computationisreasonable
        ifchannel.promote_strategy=='specific':
            values['slide_promoted']=channel.sudo().promoted_slide_id
        else:
            values['slide_promoted']=request.env['slide.slide'].sudo().search(domain,limit=1,order=order)

        limit_category_data=False
        ifchannel.channel_type=='documentation':
            ifcategoryoruncategorized:
                limit_category_data=self._slides_per_page
            else:
                limit_category_data=self._slides_per_category

        values['category_data']=channel._get_categorized_slides(
            domain,order,
            force_void=notcategory,
            limit=limit_category_data,
            offset=pager['offset'])
        values['channel_progress']=self._get_channel_progress(channel,include_quiz=True)

        #forsysadmins:preparedatatoinstalldirectlymodulesfromeLearningwhen
        #uploadingslides.Currentlysupportingonlysurvey,becausewhynot.
        ifrequest.env.user.has_group('base.group_system'):
            module=request.env.ref('base.module_survey')
            ifmodule.state!='installed':
                values['modules_to_install']=[{
                    'id':module.id,
                    'name':module.shortdesc,
                    'motivational':_('Evaluateandcertifyyourstudents.'),
                }]

        values=self._prepare_additional_channel_values(values,**kw)
        returnrequest.render('website_slides.course_main',values)

    #SLIDE.CHANNELUTILS
    #--------------------------------------------------

    @http.route('/slides/channel/add',type='http',auth='user',methods=['POST'],website=True)
    defslide_channel_create(self,*args,**kw):
        channel=request.env['slide.channel'].create(self._slide_channel_prepare_values(**kw))
        returnwerkzeug.utils.redirect("/slides/%s"%(slug(channel)))

    def_slide_channel_prepare_values(self,**kw):
        #`tag_ids`isastringrepresentingalistofintwithcoma.i.e.:'2,5,7'
        #Wedon'twanttoallowusertocreatetagsandtaggroupsonthefly.
        tag_ids=[]
        ifkw.get('tag_ids'):
            tag_ids=[int(item)foriteminkw['tag_ids'].split(',')]

        return{
            'name':kw['name'],
            'description':kw.get('description'),
            'channel_type':kw.get('channel_type','documentation'),
            'user_id':request.env.user.id,
            'tag_ids':[(6,0,tag_ids)],
            'allow_comment':bool(kw.get('allow_comment')),
        }

    @http.route('/slides/channel/enroll',type='http',auth='public',website=True)
    defslide_channel_join_http(self,channel_id):
        #TDEFIXME:why2routes?
        ifnotrequest.website.is_public_user():
            channel=request.env['slide.channel'].browse(int(channel_id))
            channel.action_add_member()
        returnwerkzeug.utils.redirect("/slides/%s"%(slug(channel)))

    @http.route(['/slides/channel/join'],type='json',auth='public',website=True)
    defslide_channel_join(self,channel_id):
        ifrequest.website.is_public_user():
            return{'error':'public_user','error_signup_allowed':request.env['res.users'].sudo()._get_signup_invitation_scope()=='b2c'}
        success=request.env['slide.channel'].browse(channel_id).action_add_member()
        ifnotsuccess:
            return{'error':'join_done'}
        returnsuccess

    @http.route(['/slides/channel/leave'],type='json',auth='user',website=True)
    defslide_channel_leave(self,channel_id):
        channel=request.env['slide.channel'].browse(channel_id)
        channel._remove_membership(request.env.user.partner_id.ids)
        self._channel_remove_session_answers(channel)
        returnTrue

    @http.route(['/slides/channel/tag/search_read'],type='json',auth='user',methods=['POST'],website=True)
    defslide_channel_tag_search_read(self,fields,domain):
        can_create=request.env['slide.channel.tag'].check_access_rights('create',raise_exception=False)
        return{
            'read_results':request.env['slide.channel.tag'].search_read(domain,fields),
            'can_create':can_create,
        }

    @http.route(['/slides/channel/tag/group/search_read'],type='json',auth='user',methods=['POST'],website=True)
    defslide_channel_tag_group_search_read(self,fields,domain):
        can_create=request.env['slide.channel.tag.group'].check_access_rights('create',raise_exception=False)
        return{
            'read_results':request.env['slide.channel.tag.group'].search_read(domain,fields),
            'can_create':can_create,
        }

    @http.route('/slides/channel/tag/add',type='json',auth='user',methods=['POST'],website=True)
    defslide_channel_tag_add(self,channel_id,tag_id=None,group_id=None):
        """Addsaslidechanneltagtothespecifiedslidechannel.

        :paramintegerchannel_id:ChannelID
        :paramlisttag_id:ChannelTagIDasfirstvalueoflist.Ifid=0,thenthisisanewtagto
                            generateandexpectsasecondlistvalueofthenameofthenewtag.
        :paramlistgroup_id:ChannelTagGroupIDasfirstvalueoflist.Ifid=0,thenthisisanew
                              taggrouptogenerateandexpectsasecondlistvalueofthenameofthe
                              newtaggroup.Thisvalueisrequiredforwhenanewtagisbeingcreated.

        tag_idandgroup_idvaluesareprovidedbyaSelect2.Default"None"valuesallowfor
        gracefulfailuresinexceptionalcaseswhenvaluesarenotprovided.

        :return:channel'scoursepage
        """

        #handleexceptionduringadditionofcoursetagandsenderrornotificationtotheclient
        #otherwiseclientslidecreatedialogboxcontinueprocessingevenserverfailtocreateaslide
        try:
            channel=request.env['slide.channel'].browse(int(channel_id))
            can_upload=channel.can_upload
            can_publish=channel.can_publish
        exceptUserErrorase:
            _logger.error(e)
            return{'error':e.args[0]}
        else:
            ifnotcan_uploadornotcan_publish:
                return{'error':_('Youcannotaddtagstothiscourse.')}

        tag=self._create_or_get_channel_tag(tag_id,group_id)
        tag.write({'channel_ids':[(4,channel.id,0)]})

        return{'url':"/slides/%s"%(slug(channel))}

    @http.route(['/slides/channel/subscribe'],type='json',auth='user',website=True)
    defslide_channel_subscribe(self,channel_id):
        returnrequest.env['slide.channel'].browse(channel_id).message_subscribe(partner_ids=[request.env.user.partner_id.id])

    @http.route(['/slides/channel/unsubscribe'],type='json',auth='user',website=True)
    defslide_channel_unsubscribe(self,channel_id):
        request.env['slide.channel'].browse(channel_id).message_unsubscribe(partner_ids=[request.env.user.partner_id.id])
        returnTrue

    #--------------------------------------------------
    #SLIDE.SLIDEMAIN/SEARCH
    #--------------------------------------------------

    @http.route('''/slides/slide/<model("slide.slide"):slide>''',type='http',auth="public",website=True,sitemap=True)
    defslide_view(self,slide,**kwargs):
        ifnotslide.channel_id.can_access_from_current_website()ornotslide.active:
            raisewerkzeug.exceptions.NotFound()
        #redirectiontochannel'shomepageforcategoryslides
        ifslide.is_category:
            returnwerkzeug.utils.redirect(slide.channel_id.website_url)
        self._set_viewed_slide(slide)

        values=self._get_slide_detail(slide)
        #quiz-specific:updatewithkarmaandquizinformation
        ifslide.question_ids:
            values.update(self._get_slide_quiz_data(slide))
        #sidebar:updatewithuserchannelprogress
        values['channel_progress']=self._get_channel_progress(slide.channel_id,include_quiz=True)

        #Allowstohavebreadcrumbforthepreviouslyusedfilter
        values.update({
            'search_category':slide.category_idifkwargs.get('search_category')elseNone,
            'search_tag':request.env['slide.tag'].browse(int(kwargs.get('search_tag')))ifkwargs.get('search_tag')elseNone,
            'slide_types':dict(request.env['slide.slide']._fields['slide_type']._description_selection(request.env))ifkwargs.get('search_slide_type')elseNone,
            'search_slide_type':kwargs.get('search_slide_type'),
            'search_uncategorized':kwargs.get('search_uncategorized')
        })

        values['channel']=slide.channel_id
        values=self._prepare_additional_channel_values(values,**kwargs)
        values.pop('channel',None)

        values['signup_allowed']=request.env['res.users'].sudo()._get_signup_invitation_scope()=='b2c'

        ifkwargs.get('fullscreen')=='1':
            returnrequest.render("website_slides.slide_fullscreen",values)
        returnrequest.render("website_slides.slide_main",values)

    @http.route('''/slides/slide/<model("slide.slide"):slide>/pdf_content''',
                type='http',auth="public",website=True,sitemap=False)
    defslide_get_pdf_content(self,slide):
        response=werkzeug.wrappers.Response()
        response.data=slide.datasandbase64.b64decode(slide.datas)orb''
        response.mimetype='application/pdf'
        returnresponse

    @http.route('/slides/slide/<int:slide_id>/get_image',type='http',auth="public",website=True,sitemap=False)
    defslide_get_image(self,slide_id,field='image_128',width=0,height=0,crop=False):
        #Protectinfographicsbylimitingaccessto256px(large)images
        iffieldnotin('image_128','image_256','image_512','image_1024','image_1920'):
            returnwerkzeug.exceptions.Forbidden()

        slide=request.env['slide.slide'].sudo().browse(slide_id).exists()
        ifnotslide:
            raisewerkzeug.exceptions.NotFound()

        status,headers,image_base64=request.env['ir.http'].sudo().binary_content(
            model='slide.slide',id=slide.id,field=field,
            default_mimetype='image/png')
        ifstatus==301:
            returnrequest.env['ir.http']._response_by_status(status,headers,image_base64)
        ifstatus==304:
            returnwerkzeug.wrappers.Response(status=304)

        ifnotimage_base64:
            image_base64=self._get_default_avatar()
            ifnot(widthorheight):
                width,height=tools.image_guess_size_from_field_name(field)

        image_base64=tools.image_process(image_base64,size=(int(width),int(height)),crop=crop)

        content=base64.b64decode(image_base64)
        headers=http.set_safe_image_headers(headers,content)
        response=request.make_response(content,headers)
        response.status_code=status
        returnresponse

    #SLIDE.SLIDEUTILS
    #--------------------------------------------------

    @http.route('/slides/slide/get_html_content',type="json",auth="public",website=True)
    defget_html_content(self,slide_id):
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        return{
            'html_content':fetch_res['slide'].html_content
        }

    @http.route('/slides/slide/<model("slide.slide"):slide>/set_completed',website=True,type="http",auth="user")
    defslide_set_completed_and_redirect(self,slide,next_slide_id=None):
        self._set_completed_slide(slide)
        next_slide=None
        ifnext_slide_id:
            next_slide=self._fetch_slide(next_slide_id).get('slide',None)
        returnwerkzeug.utils.redirect("/slides/slide/%s"%(slug(next_slide)ifnext_slideelseslug(slide)))

    @http.route('/slides/slide/set_completed',website=True,type="json",auth="public")
    defslide_set_completed(self,slide_id):
        ifrequest.website.is_public_user():
            return{'error':'public_user'}
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        self._set_completed_slide(fetch_res['slide'])
        return{
            'channel_completion':fetch_res['slide'].channel_id.completion
        }

    @http.route('/slides/slide/like',type='json',auth="public",website=True)
    defslide_like(self,slide_id,upvote):
        ifrequest.website.is_public_user():
            return{'error':'public_user','error_signup_allowed':request.env['res.users'].sudo()._get_signup_invitation_scope()=='b2c'}
        slide_partners=request.env['slide.slide.partner'].sudo().search([
            ('slide_id','=',slide_id),
            ('partner_id','=',request.env.user.partner_id.id)
        ])
        if(upvoteandslide_partners.vote==1)or(notupvoteandslide_partners.vote==-1):
            return{'error':'vote_done'}
        #checkslideaccess
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        #checkslideoperation
        slide=fetch_res['slide']
        ifnotslide.channel_id.is_member:
            return{'error':'channel_membership_required'}
        ifnotslide.channel_id.allow_comment:
            return{'error':'channel_comment_disabled'}
        ifnotslide.channel_id.can_vote:
            return{'error':'channel_karma_required'}
        ifupvote:
            slide.action_like()
        else:
            slide.action_dislike()
        slide.invalidate_cache()
        returnslide.read(['likes','dislikes','user_vote'])[0]

    @http.route('/slides/slide/archive',type='json',auth='user',website=True)
    defslide_archive(self,slide_id):
        """Thisrouteallowschannelpublisherstoarchiveslides.
        Ithastobedoneinsudomodesinceonlywebsite_publisherscanwriteonslidesinACLs"""
        slide=request.env['slide.slide'].browse(int(slide_id))
        ifslide.channel_id.can_publish:
            slide.sudo().active=False
            returnTrue

        returnFalse

    @http.route('/slides/slide/toggle_is_preview',type='json',auth='user',website=True)
    defslide_preview(self,slide_id):
        slide=request.env['slide.slide'].browse(int(slide_id))
        ifslide.channel_id.can_publish:
            slide.is_preview=notslide.is_preview
        returnslide.is_preview

    @http.route(['/slides/slide/send_share_email'],type='json',auth='user',website=True)
    defslide_send_share_email(self,slide_id,email,fullscreen=False):
        slide=request.env['slide.slide'].browse(int(slide_id))
        result=slide._send_share_email(email,fullscreen)
        returnresult

    #--------------------------------------------------
    #TAGSSECTION
    #--------------------------------------------------

    @http.route('/slide_channel_tag/add',type='json',auth='user',methods=['POST'],website=True)
    defslide_channel_tag_create_or_get(self,tag_id,group_id):
        tag=self._create_or_get_channel_tag(tag_id,group_id)
        return{'tag_id':tag.id}

    #--------------------------------------------------
    #QUIZSECTION
    #--------------------------------------------------

    @http.route('/slides/slide/quiz/question_add_or_update',type='json',methods=['POST'],auth='user',website=True)
    defslide_quiz_question_add_or_update(self,slide_id,question,sequence,answer_ids,existing_question_id=None):
        """Addanewquestiontoanexistingslide.Completedfieldofslide.partner
        linkissettoFalsetomakesurethatthecreatorcantakethequizagain.

        Anoptionalquestion_idtoudpatecanbegiven.Inthiscasequestionis
        deletedfirstbeforecreatinganewonetosimplifymanagement.

        :paramintegerslide_id:SlideID
        :paramstringquestion:QuestionTitle
        :paramintegersequence:QuestionSequence
        :paramarrayanswer_ids:Arraycontainingalltheanswers:
                [
                    'sequence':AnswerSequence(Integer),
                    'text_value':AnswerTitle(String),
                    'is_correct':AnswerIsCorrect(Boolean)
                ]
        :paramintegerexisting_question_id:questionIDifthisisanupdate

        :return:renderedquestiontemplate
        """
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        slide=fetch_res['slide']
        ifexisting_question_id:
            request.env['slide.question'].search([
                ('slide_id','=',slide.id),
                ('id','=',int(existing_question_id))
            ]).unlink()

        request.env['slide.slide.partner'].search([
            ('slide_id','=',slide_id),
            ('partner_id','=',request.env.user.partner_id.id)
        ]).write({'completed':False})

        slide_question=request.env['slide.question'].create({
            'sequence':sequence,
            'question':question,
            'slide_id':slide_id,
            'answer_ids':[(0,0,{
                'sequence':answer['sequence'],
                'text_value':answer['text_value'],
                'is_correct':answer['is_correct'],
                'comment':answer['comment']
            })foranswerinanswer_ids]
        })
        returnrequest.env.ref('website_slides.lesson_content_quiz_question')._render({
            'slide':slide,
            'question':slide_question,
        })

    @http.route('/slides/slide/quiz/get',type="json",auth="public",website=True)
    defslide_quiz_get(self,slide_id):
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        slide=fetch_res['slide']
        returnself._get_slide_quiz_data(slide)

    @http.route('/slides/slide/quiz/reset',type="json",auth="user",website=True)
    defslide_quiz_reset(self,slide_id):
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        request.env['slide.slide.partner'].search([
            ('slide_id','=',fetch_res['slide'].id),
            ('partner_id','=',request.env.user.partner_id.id)
        ]).write({'completed':False,'quiz_attempts_count':0})

    @http.route('/slides/slide/quiz/submit',type="json",auth="public",website=True)
    defslide_quiz_submit(self,slide_id,answer_ids):
        ifrequest.website.is_public_user():
            return{'error':'public_user'}
        fetch_res=self._fetch_slide(slide_id)
        iffetch_res.get('error'):
            returnfetch_res
        slide=fetch_res['slide']

        ifslide.user_membership_id.sudo().completed:
            self._channel_remove_session_answers(slide.channel_id,slide)
            return{'error':'slide_quiz_done'}

        all_questions=request.env['slide.question'].sudo().search([('slide_id','=',slide.id)])

        user_answers=request.env['slide.answer'].sudo().search([('id','in',answer_ids)])
        ifuser_answers.mapped('question_id')!=all_questions:
            return{'error':'slide_quiz_incomplete'}

        user_bad_answers=user_answers.filtered(lambdaanswer:notanswer.is_correct)

        self._set_viewed_slide(slide,quiz_attempts_inc=True)
        quiz_info=self._get_slide_quiz_partner_info(slide,quiz_done=True)

        rank_progress={}
        ifnotuser_bad_answers:
            rank_progress['previous_rank']=self._get_rank_values(request.env.user)
            slide._action_set_quiz_done()
            slide.action_set_completed()
            rank_progress['new_rank']=self._get_rank_values(request.env.user)
            rank_progress.update({
                'description':request.env.user.rank_id.description,
                'last_rank':notrequest.env.user._get_next_rank(),
                'level_up':rank_progress['previous_rank']['lower_bound']!=rank_progress['new_rank']['lower_bound']
            })
        self._channel_remove_session_answers(slide.channel_id,slide)
        return{
            'answers':{
                answer.question_id.id:{
                    'is_correct':answer.is_correct,
                    'comment':answer.comment
                }foranswerinuser_answers
            },
            'completed':slide.user_membership_id.sudo().completed,
            'channel_completion':slide.channel_id.completion,
            'quizKarmaWon':quiz_info['quiz_karma_won'],
            'quizKarmaGain':quiz_info['quiz_karma_gain'],
            'quizAttemptsCount':quiz_info['quiz_attempts_count'],
            'rankProgress':rank_progress,
        }

    @http.route(['/slides/slide/quiz/save_to_session'],type='json',auth='public',website=True)
    defslide_quiz_save_to_session(self,quiz_answers):
        session_slide_answer_quiz=json.loads(request.session.get('slide_answer_quiz','{}'))
        slide_id=quiz_answers['slide_id']
        session_slide_answer_quiz[str(slide_id)]=quiz_answers['slide_answers']
        request.session['slide_answer_quiz']=json.dumps(session_slide_answer_quiz)

    def_get_rank_values(self,user):
        lower_bound=user.rank_id.karma_minor0
        next_rank=user._get_next_rank()
        upper_bound=next_rank.karma_min
        progress=100
        ifnext_rankand(upper_bound-lower_bound)!=0:
            progress=100*((user.karma-lower_bound)/(upper_bound-lower_bound))
        return{
            'lower_bound':lower_bound,
            'upper_bound':upper_bound,
            'karma':user.karma,
            'motivational':next_rank.description_motivational,
            'progress':progress
        }
    #--------------------------------------------------
    #CATEGORYMANAGEMENT
    #--------------------------------------------------

    @http.route(['/slides/category/search_read'],type='json',auth='user',methods=['POST'],website=True)
    defslide_category_search_read(self,fields,domain):
        category_slide_domain=domainifdomainelse[]
        category_slide_domain=expression.AND([category_slide_domain,[('is_category','=',True)]])
        can_create=request.env['slide.slide'].check_access_rights('create',raise_exception=False)
        return{
            'read_results':request.env['slide.slide'].search_read(category_slide_domain,fields),
            'can_create':can_create,
        }

    @http.route('/slides/category/add',type="http",website=True,auth="user",methods=['POST'])
    defslide_category_add(self,channel_id,name):
        """Addsacategorytothespecifiedchannel.Slideisaddedattheend
        ofslidelistbasedonsequence."""
        channel=request.env['slide.channel'].browse(int(channel_id))
        ifnotchannel.can_uploadornotchannel.can_publish:
            raisewerkzeug.exceptions.NotFound()

        request.env['slide.slide'].create(self._get_new_slide_category_values(channel,name))

        returnwerkzeug.utils.redirect("/slides/%s"%(slug(channel)))

    #--------------------------------------------------
    #SLIDE.UPLOAD
    #--------------------------------------------------

    @http.route(['/slides/prepare_preview'],type='json',auth='user',methods=['POST'],website=True)
    defprepare_preview(self,**data):
        Slide=request.env['slide.slide']
        unused,document_id=Slide._find_document_data_from_url(data['url'])
        preview={}
        ifnotdocument_id:
            preview['error']=_('Pleaseentervalidyoutubeorgoogledocurl')
            returnpreview
        existing_slide=Slide.search([('channel_id','=',int(data['channel_id'])),('document_id','=',document_id)],limit=1)
        ifexisting_slide:
            preview['error']=_('Thisvideoalreadyexistsinthischannelonthefollowingslide:%s',existing_slide.name)
            returnpreview
        values=Slide._parse_document_url(data['url'],only_preview_fields=True)
        ifvalues.get('error'):
            preview['error']=values['error']
            returnpreview
        returnvalues

    @http.route(['/slides/add_slide'],type='json',auth='user',methods=['POST'],website=True)
    defcreate_slide(self,*args,**post):
        #checkthesizeonlywhenweuploadafile.
        ifpost.get('datas'):
            file_size=len(post['datas'])*3/4 #base64
            if(file_size/1024.0/1024.0)>25:
                return{'error':_('Fileistoobig.Filesizecannotexceed25MB')}

        values=dict((fname,post[fname])forfnameinself._get_valid_slide_post_values()ifpost.get(fname))

        #handleexceptionduringcreationofslideandsenterrornotificationtotheclient
        #otherwiseclientslidecreatedialogboxcontinueprocessingevenserverfailtocreateaslide
        try:
            channel=request.env['slide.channel'].browse(values['channel_id'])
            can_upload=channel.can_upload
            can_publish=channel.can_publish
        exceptUserErrorase:
            _logger.error(e)
            return{'error':e.args[0]}
        else:
            ifnotcan_upload:
                return{'error':_('Youcannotuploadonthischannel.')}

        ifpost.get('duration'):
            #minutestohoursconversion
            values['completion_time']=int(post['duration'])/60

        category=False
        #handlecreationofnewcategoriesonthefly
        ifpost.get('category_id'):
            category_id=post['category_id'][0]
            ifcategory_id==0:
                category=request.env['slide.slide'].create(self._get_new_slide_category_values(channel,post['category_id'][1]['name']))
                values['sequence']=category.sequence+1
            else:
                category=request.env['slide.slide'].browse(category_id)
                values.update({
                    'sequence':request.env['slide.slide'].browse(post['category_id'][0]).sequence+1
                })

        #createslideitself
        try:
            values['user_id']=request.env.uid
            values['is_published']=values.get('is_published',False)andcan_publish
            slide=request.env['slide.slide'].sudo().create(values)
        exceptUserErrorase:
            _logger.error(e)
            return{'error':e.args[0]}
        exceptExceptionase:
            _logger.error(e)
            return{'error':_('Internalservererror,pleasetryagainlaterorcontactadministrator.\nHereistheerrormessage:%s',e)}

        #ensurecorrectorderingbyresequencingslidesinfront-end(backendshouldbeokthankstolistview)
        channel._resequence_slides(slide,force_category=category)

        redirect_url="/slides/slide/%s"%(slide.id)
        ifchannel.channel_type=="training"andnotslide.slide_type=="webpage":
            redirect_url="/slides/%s"%(slug(channel))
        ifslide.slide_type=='webpage':
            redirect_url+="?enable_editor=1"
        return{
            'url':redirect_url,
            'channel_type':channel.channel_type,
            'slide_id':slide.id,
            'category_id':slide.category_id
        }

    def_get_valid_slide_post_values(self):
        return['name','url','tag_ids','slide_type','channel_id','is_preview',
                'mime_type','datas','description','image_1920','is_published']

    @http.route(['/slides/tag/search_read'],type='json',auth='user',methods=['POST'],website=True)
    defslide_tag_search_read(self,fields,domain):
        can_create=request.env['slide.tag'].check_access_rights('create',raise_exception=False)
        return{
            'read_results':request.env['slide.tag'].search_read(domain,fields),
            'can_create':can_create,
        }

    #--------------------------------------------------
    #EMBEDINTHIRDPARTYWEBSITES
    #--------------------------------------------------

    @http.route('/slides/embed/<int:slide_id>',type='http',auth='public',website=True,sitemap=False)
    defslides_embed(self,slide_id,page="1",**kw):
        #Note:don'tusethe'model'intheroute(use'slide_id'),otherwiseifpubliccannotaccesstheembedded
        #slide,theerrorwillbethewebsite.403pageinsteadoftheoneofthewebsite_slides.embed_slide.
        #Donotforgettherenderingherewillbedisplayedintheembeddediframe

        #determineifitisembeddedfromexternalwebpage
        referrer_url=request.httprequest.headers.get('Referer','')
        base_url=request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        is_embedded=referrer_urlandnotbool(base_urlinreferrer_url)orFalse
        #tryaccessingslide,anddisplaytocorrespondingtemplate
        try:
            slide=request.env['slide.slide'].browse(slide_id)
            ifnotslide.active:
                raisewerkzeug.exceptions.NotFound()
            ifis_embedded:
                request.env['slide.embed'].sudo()._add_embed_url(slide.id,referrer_url)
            values=self._get_slide_detail(slide)
            values['page']=page
            values['is_embedded']=is_embedded
            self._set_viewed_slide(slide)
            returnrequest.render('website_slides.embed_slide',values)
        exceptAccessError:#TODO:please,makeitcleanoneday,orfindanothersecurewaytodetect
                            #iftheslidecanbeembedded,andproperlydisplaytheerrormessage.
            returnrequest.render('website_slides.embed_slide_forbidden',{})

    #--------------------------------------------------
    #PROFILE
    #--------------------------------------------------

    def_prepare_user_values(self,**kwargs):
        values=super(WebsiteSlides,self)._prepare_user_values(**kwargs)
        channel=self._get_channels(**kwargs)
        ifchannel:
            values['channel']=channel
        returnvalues

    def_get_channels(self,**kwargs):
        channels=[]
        ifkwargs.get('channel'):
            channels=kwargs['channel']
        elifkwargs.get('channel_id'):
            channels=request.env['slide.channel'].browse(int(kwargs['channel_id']))
        returnchannels

    def_prepare_user_slides_profile(self,user):
        courses=request.env['slide.channel.partner'].sudo().search([('partner_id','=',user.partner_id.id)])
        courses_completed=courses.filtered(lambdac:c.completed)
        courses_ongoing=courses-courses_completed
        values={
            'uid':request.env.user.id,
            'user':user,
            'main_object':user,
            'courses_completed':courses_completed,
            'courses_ongoing':courses_ongoing,
            'is_profile_page':True,
            'badge_category':'slides',
        }
        returnvalues

    def_prepare_user_profile_values(self,user,**post):
        values=super(WebsiteSlides,self)._prepare_user_profile_values(user,**post)
        ifpost.get('channel_id'):
            values.update({'edit_button_url_param':'channel_id='+str(post['channel_id'])})
        channels=self._get_channels(**post)
        ifnotchannels:
            channels=request.env['slide.channel'].search([])
        values.update(self._prepare_user_values(channel=channels[0]iflen(channels)==1elseTrue,**post))
        values.update(self._prepare_user_slides_profile(user))
        returnvalues
