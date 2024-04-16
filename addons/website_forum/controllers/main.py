#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importjson
importlxml
importrequests
importlogging
importwerkzeug.exceptions
importwerkzeug.urls
importwerkzeug.wrappers

fromdatetimeimportdatetime

fromflectraimporthttp,tools,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.addons.website.models.ir_httpimportsitemap_qs2dom
fromflectra.addons.website_profile.controllers.mainimportWebsiteProfile
fromflectra.addons.portal.controllers.portalimport_build_url_w_params

fromflectra.exceptionsimportUserError
fromflectra.httpimportrequest
fromflectra.osvimportexpression


_logger=logging.getLogger(__name__)


classWebsiteForum(WebsiteProfile):
    _post_per_page=10
    _user_per_page=30

    def_prepare_user_values(self,**kwargs):
        values=super(WebsiteForum,self)._prepare_user_values(**kwargs)
        values['forum_welcome_message']=request.httprequest.cookies.get('forum_welcome_message',False)
        values.update({
            'header':kwargs.get('header',dict()),
            'searches':kwargs.get('searches',dict()),
        })
        ifkwargs.get('forum'):
            values['forum']=kwargs.get('forum')
        elifkwargs.get('forum_id'):
            values['forum']=request.env['forum.forum'].browse(kwargs.pop('forum_id'))
        returnvalues

    #Forum
    #--------------------------------------------------

    @http.route(['/forum'],type='http',auth="public",website=True,sitemap=True)
    defforum(self,**kwargs):
        domain=request.website.website_domain()
        forums=request.env['forum.forum'].search(domain)
        iflen(forums)==1:
            returnwerkzeug.utils.redirect('/forum/%s'%slug(forums[0]),code=302)

        returnrequest.render("website_forum.forum_all",{
            'forums':forums
        })

    @http.route('/forum/new',type='json',auth="user",methods=['POST'],website=True)
    defforum_create(self,forum_name="NewForum",forum_mode="questions",forum_privacy="public",forum_privacy_group=False,add_menu=False):
        forum={
            'name':forum_name,
            'mode':forum_mode,
            'privacy':forum_privacy,
            'website_id':request.website.id,
        }
        ifforum_privacy=='private'andforum_privacy_group:
            forum['authorized_group_id']=forum_privacy_group
        forum_id=request.env['forum.forum'].create(forum)
        ifadd_menu:
            group=[int(forum_privacy_group)]ifforum_privacy=='private'else[request.env.ref('base.group_portal').id,request.env.ref('base.group_user').id]
            menu_id=request.env['website.menu'].create({
                'name':forum_name,
                'url':"/forum/%s"%slug(forum_id),
                'parent_id':request.website.menu_id.id,
                'website_id':request.website.id,
                'group_ids':[(6,0,group)]
            })
            forum_id.menu_id=menu_id
        return"/forum/%s"%slug(forum_id)

    defsitemap_forum(env,rule,qs):
        Forum=env['forum.forum']
        dom=sitemap_qs2dom(qs,'/forum',Forum._rec_name)
        dom+=env['website'].get_current_website().website_domain()
        forfinForum.search(dom):
            loc='/forum/%s'%slug(f)
            ifnotqsorqs.lower()inloc:
                yield{'loc':loc}

    @http.route(['/forum/<model("forum.forum"):forum>',
                 '/forum/<model("forum.forum"):forum>/page/<int:page>',
                 '''/forum/<model("forum.forum"):forum>/tag/<model("forum.tag"):tag>/questions''',
                 '''/forum/<model("forum.forum"):forum>/tag/<model("forum.tag"):tag>/questions/page/<int:page>''',
                 ],type='http',auth="public",website=True,sitemap=sitemap_forum)
    defquestions(self,forum,tag=None,page=1,filters='all',my=None,sorting=None,search='',**post):
        ifnotforum.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        Post=request.env['forum.post']

        domain=[('forum_id','=',forum.id),('parent_id','=',False),('state','=','active'),('can_view','=',True)]
        ifsearch:
            domain+=['|',('name','ilike',search),('content','ilike',search)]
        iftag:
            domain+=[('tag_ids','in',tag.id)]
        iffilters=='unanswered':
            domain+=[('child_ids','=',False)]
        eliffilters=='solved':
            domain+=[('has_validated_answer','=',True)]
        eliffilters=='unsolved':
            domain+=[('has_validated_answer','=',False)]

        user=request.env.user

        ifmy=='mine':
            domain+=[('create_uid','=',user.id)]
        elifmy=='followed':
            domain+=[('message_partner_ids','=',user.partner_id.id)]
        elifmy=='tagged':
            domain+=[('tag_ids.message_partner_ids','=',user.partner_id.id)]
        elifmy=='favourites':
            domain+=[('favourite_ids','=',user.id)]

        ifsorting:
            #checkthatsortingisvalid
            #retro-compatibilyforV8andgooglelinks
            try:
                sorting=werkzeug.urls.url_unquote_plus(sorting)
                Post._generate_order_by(sorting,None)
            except(UserError,ValueError):
                sorting=False

        ifnotsorting:
            sorting=forum.default_order

        question_count=Post.search_count(domain)

        iftag:
            url="/forum/%s/tag/%s/questions"%(slug(forum),slug(tag))
        else:
            url="/forum/%s"%slug(forum)

        url_args={
            'sorting':sorting
        }
        ifsearch:
            url_args['search']=search
        iffilters:
            url_args['filters']=filters
        ifmy:
            url_args['my']=my
        pager=request.website.pager(url=url,total=question_count,page=page,
                                      step=self._post_per_page,scope=self._post_per_page,
                                      url_args=url_args)

        question_ids=Post.search(domain,limit=self._post_per_page,offset=pager['offset'],order=sorting)

        values=self._prepare_user_values(forum=forum,searches=post,header={'ask_hide':notforum.active})
        values.update({
            'main_object':tagorforum,
            'edit_in_backend':nottag,
            'question_ids':question_ids,
            'question_count':question_count,
            'pager':pager,
            'tag':tag,
            'filters':filters,
            'my':my,
            'sorting':sorting,
            'search':search,
        })
        returnrequest.render("website_forum.forum_index",values)

    @http.route(['''/forum/<model("forum.forum"):forum>/faq'''],type='http',auth="public",website=True,sitemap=True)
    defforum_faq(self,forum,**post):
        values=self._prepare_user_values(forum=forum,searches=dict(),header={'is_guidelines':True},**post)
        returnrequest.render("website_forum.faq",values)

    @http.route(['/forum/<model("forum.forum"):forum>/faq/karma'],type='http',auth="public",website=True,sitemap=False)
    defforum_faq_karma(self,forum,**post):
        values=self._prepare_user_values(forum=forum,header={'is_guidelines':True,'is_karma':True},**post)
        returnrequest.render("website_forum.faq_karma",values)

    @http.route('/forum/get_tags',type='http',auth="public",methods=['GET'],website=True,sitemap=False)
    deftag_read(self,query='',limit=25,**post):
        #TODO:Inmasteralwayschecktheforum_iddomainpartandaddforum_id
        #      asrequiredmethodparam,notin**post
        forum_id=post.get('forum_id')
        domain=[('name','=ilike',(queryor'')+"%")]
        ifforum_id:
            domain=expression.AND([domain,[('forum_id','=',int(forum_id))]])
        data=request.env['forum.tag'].search_read(
            domain=domain,
            fields=['id','name'],
            limit=int(limit),
        )
        returnrequest.make_response(
            json.dumps(data),
            headers=[("Content-Type","application/json")]
        )

    @http.route(['/forum/<model("forum.forum"):forum>/tag','/forum/<model("forum.forum"):forum>/tag/<string:tag_char>'],type='http',auth="public",website=True,sitemap=False)
    deftags(self,forum,tag_char=None,**post):
        #buildthelistoftagfirstchar,withtheirvalueastag_charparamEx:[('All','all'),('C','c'),('G','g'),('Z',z)]
        first_char_tag=forum.get_tags_first_char()
        first_char_list=[(t,t.lower())fortinfirst_char_tagift.isalnum()]
        first_char_list.insert(0,(_('All'),'all'))

        active_char_tag=tag_charandtag_char.lower()or'all'

        #generatedomainforsearchedtags
        domain=[('forum_id','=',forum.id),('posts_count','>',0)]
        order_by='name'
        ifactive_char_tagandactive_char_tag!='all':
            domain.append(('name','=ilike',tools.escape_psql(active_char_tag)+'%'))
            order_by='posts_countDESC'
        tags=request.env['forum.tag'].search(domain,limit=None,order=order_by)
        #preparevaluesandrendertemplate
        values=self._prepare_user_values(forum=forum,searches={'tags':True},**post)

        values.update({
            'tags':tags,
            'pager_tag_chars':first_char_list,
            'active_char_tag':active_char_tag,
        })
        returnrequest.render("website_forum.tag",values)

    #Questions
    #--------------------------------------------------

    @http.route('/forum/get_url_title',type='json',auth="user",methods=['POST'],website=True)
    defget_url_title(self,**kwargs):
        try:
            req=requests.get(kwargs.get('url'))
            req.raise_for_status()
            arch=lxml.html.fromstring(req.content)
            returnarch.find(".//title").text
        exceptIOError:
            returnFalse

    @http.route(['''/forum/<model("forum.forum"):forum>/question/<model("forum.post","[('forum_id','=',forum.id),('parent_id','=',False),('can_view','=',True)]"):question>'''],
                type='http',auth="public",website=True,sitemap=False)
    defold_question(self,forum,question,**post):
        #Compatibilitypre-v14
        returnrequest.redirect(_build_url_w_params("/forum/%s/%s"%(slug(forum),slug(question)),request.params),code=301)

    @http.route(['''/forum/<model("forum.forum"):forum>/<model("forum.post","[('forum_id','=',forum.id),('parent_id','=',False),('can_view','=',True)]"):question>'''],
                type='http',auth="public",website=True,sitemap=True)
    defquestion(self,forum,question,**post):
        ifnotforum.active:
            returnrequest.render("website_forum.header",{'forum':forum})

        #Hidepostsfromabusers(negativekarma),exceptformoderators
        ifnotquestion.can_view:
            raisewerkzeug.exceptions.NotFound()

        #Hidependingpostsfromnon-moderatorsandnon-creator
        user=request.env.user
        ifquestion.state=='pending'anduser.karma<forum.karma_postandquestion.create_uid!=user:
            raisewerkzeug.exceptions.NotFound()

        ifquestion.parent_id:
            redirect_url="/forum/%s/%s"%(slug(forum),slug(question.parent_id))
            returnwerkzeug.utils.redirect(redirect_url,301)
        filters='question'
        values=self._prepare_user_values(forum=forum,searches=post)
        values.update({
            'main_object':question,
            'question':question,
            'can_bump':(question.forum_id.allow_bumpandnotquestion.child_countand(datetime.today()-question.write_date).days>9),
            'header':{'question_data':True},
            'filters':filters,
            'reversed':reversed,
        })
        if(request.httprequest.referreror"").startswith(request.httprequest.url_root):
            values['back_button_url']=request.httprequest.referrer

        #incrementviewcounter
        question.sudo()._set_viewed()

        returnrequest.render("website_forum.post_description_full",values)

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/toggle_favourite',type='json',auth="user",methods=['POST'],website=True)
    defquestion_toggle_favorite(self,forum,question,**post):
        ifnotrequest.session.uid:
            return{'error':'anonymous_user'}
        favourite=notquestion.user_favourite
        question.sudo().favourite_ids=[(favouriteand4or3,request.uid)]
        iffavourite:
            #Automaticallyaddtheuserasfollowerofthepoststhathe
            #favorites(onunfavoritewechosetokeephimasafolloweruntil
            #hedecidestonotfollowanymore).
            question.sudo().message_subscribe(request.env.user.partner_id.ids)
        returnfavourite

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/ask_for_close',type='http',auth="user",methods=['POST'],website=True)
    defquestion_ask_for_close(self,forum,question,**post):
        reasons=request.env['forum.post.reason'].search([('reason_type','=','basic')])

        values=self._prepare_user_values(**post)
        values.update({
            'question':question,
            'forum':forum,
            'reasons':reasons,
        })
        returnrequest.render("website_forum.close_post",values)

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/edit_answer',type='http',auth="user",website=True)
    defquestion_edit_answer(self,forum,question,**kwargs):
        forrecordinquestion.child_ids:
            ifrecord.create_uid.id==request.uid:
                answer=record
                break
        returnwerkzeug.utils.redirect("/forum/%s/post/%s/edit"%(slug(forum),slug(answer)))

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/close',type='http',auth="user",methods=['POST'],website=True)
    defquestion_close(self,forum,question,**post):
        question.close(reason_id=int(post.get('reason_id',False)))
        returnwerkzeug.utils.redirect("/forum/%s/question/%s"%(slug(forum),slug(question)))

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/reopen',type='http',auth="user",methods=['POST'],website=True)
    defquestion_reopen(self,forum,question,**kwarg):
        question.reopen()
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/delete',type='http',auth="user",methods=['POST'],website=True)
    defquestion_delete(self,forum,question,**kwarg):
        question.active=False
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    @http.route('/forum/<model("forum.forum"):forum>/question/<model("forum.post"):question>/undelete',type='http',auth="user",methods=['POST'],website=True)
    defquestion_undelete(self,forum,question,**kwarg):
        question.active=True
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    #Post
    #--------------------------------------------------
    @http.route(['/forum/<model("forum.forum"):forum>/ask'],type='http',auth="user",website=True)
    defforum_post(self,forum,**post):
        user=request.env.user
        ifnotuser.emailornottools.single_email_re.match(user.email):
            returnwerkzeug.utils.redirect("/forum/%s/user/%s/edit?email_required=1"%(slug(forum),request.session.uid))
        values=self._prepare_user_values(forum=forum,searches={},header={'ask_hide':True},new_question=True)
        returnrequest.render("website_forum.new_question",values)

    @http.route(['/forum/<model("forum.forum"):forum>/new',
                 '/forum/<model("forum.forum"):forum>/<model("forum.post"):post_parent>/reply'],
                type='http',auth="user",methods=['POST'],website=True)
    defpost_create(self,forum,post_parent=None,**post):
        ifpost.get('content','')=='<p><br></p>':
            returnrequest.render('http_routing.http_error',{
                'status_code':_('BadRequest'),
                'status_message':post_parentand_('Replyshouldnotbeempty.')or_('Questionshouldnotbeempty.')
            })

        post_tag_ids=forum._tag_to_write_vals(post.get('post_tags',''))

        ifrequest.env.user.forum_waiting_posts_count:
            returnwerkzeug.utils.redirect("/forum/%s/ask"%slug(forum))

        new_question=request.env['forum.post'].create({
            'forum_id':forum.id,
            'name':post.get('post_name')or(post_parentand'Re:%s'%(post_parent.nameor''))or'',
            'content':post.get('content',False),
            'parent_id':post_parentandpost_parent.idorFalse,
            'tag_ids':post_tag_ids
        })
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),post_parentandslug(post_parent)ornew_question.id))

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/comment',type='http',auth="user",methods=['POST'],website=True)
    defpost_comment(self,forum,post,**kwargs):
        question=post.parent_idifpost.parent_idelsepost
        ifkwargs.get('comment')andpost.forum_id.id==forum.id:
            #TDEFIXME:checkthatpost_idisthequestionoroneofitsanswers
            body=tools.mail.plaintext2html(kwargs['comment'])
            post.with_context(mail_create_nosubscribe=True).message_post(
                body=body,
                message_type='comment',
                subtype_xmlid='mail.mt_comment')
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/toggle_correct',type='json',auth="public",website=True)
    defpost_toggle_correct(self,forum,post,**kwargs):
        ifpost.parent_idisFalse:
            returnrequest.redirect('/')
        ifnotrequest.session.uid:
            return{'error':'anonymous_user'}

        #setallanswerstoFalse,onlyonecanbeaccepted
        (post.parent_id.child_ids-post).write(dict(is_correct=False))
        post.is_correct=notpost.is_correct
        returnpost.is_correct

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/delete',type='http',auth="user",methods=['POST'],website=True)
    defpost_delete(self,forum,post,**kwargs):
        question=post.parent_id
        post.unlink()
        ifquestion:
            werkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))
        returnwerkzeug.utils.redirect("/forum/%s"%slug(forum))

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/edit',type='http',auth="user",website=True)
    defpost_edit(self,forum,post,**kwargs):
        tags=[dict(id=tag.id,name=tag.name)fortaginpost.tag_ids]
        tags=json.dumps(tags)
        values=self._prepare_user_values(forum=forum)
        values.update({
            'tags':tags,
            'post':post,
            'is_edit':True,
            'is_answer':bool(post.parent_id),
            'searches':kwargs,
            'content':post.name,
        })
        returnrequest.render("website_forum.edit_post",values)

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/save',type='http',auth="user",methods=['POST'],website=True)
    defpost_save(self,forum,post,**kwargs):
        vals={
            'content':kwargs.get('content'),
        }

        if'post_name'inkwargs:
            ifnotkwargs.get('post_name').strip():
                returnrequest.render('http_routing.http_error',{
                    'status_code':_('BadRequest'),
                    'status_message':_('Titleshouldnotbeempty.')
                })

            vals['name']=kwargs.get('post_name')
        vals['tag_ids']=forum._tag_to_write_vals(kwargs.get('post_tags',''))
        post.write(vals)
        question=post.parent_idifpost.parent_idelsepost
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    # JSONutilities
    #--------------------------------------------------

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/upvote',type='json',auth="public",website=True)
    defpost_upvote(self,forum,post,**kwargs):
        ifnotrequest.session.uid:
            return{'error':'anonymous_user'}
        ifrequest.uid==post.create_uid.id:
            return{'error':'own_post'}
        upvote=Trueifnotpost.user_vote>0elseFalse
        returnpost.vote(upvote=upvote)

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/downvote',type='json',auth="public",website=True)
    defpost_downvote(self,forum,post,**kwargs):
        ifnotrequest.session.uid:
            return{'error':'anonymous_user'}
        ifrequest.uid==post.create_uid.id:
            return{'error':'own_post'}
        upvote=Trueifpost.user_vote<0elseFalse
        returnpost.vote(upvote=upvote)

    @http.route('/forum/post/bump',type='json',auth="public",website=True)
    defpost_bump(self,post_id,**kwarg):
        post=request.env['forum.post'].browse(int(post_id))
        ifnotpost.exists()orpost.parent_id:
            returnFalse
        returnpost.bump()

    #ModerationTools
    #--------------------------------------------------

    @http.route('/forum/<model("forum.forum"):forum>/validation_queue',type='http',auth="user",website=True)
    defvalidation_queue(self,forum,**kwargs):
        user=request.env.user
        ifuser.karma<forum.karma_moderate:
            raisewerkzeug.exceptions.NotFound()

        Post=request.env['forum.post']
        domain=[('forum_id','=',forum.id),('state','=','pending')]
        posts_to_validate_ids=Post.search(domain)

        values=self._prepare_user_values(forum=forum)
        values.update({
            'posts_ids':posts_to_validate_ids.sudo(),
            'queue_type':'validation',
        })

        returnrequest.render("website_forum.moderation_queue",values)

    @http.route('/forum/<model("forum.forum"):forum>/flagged_queue',type='http',auth="user",website=True)
    defflagged_queue(self,forum,**kwargs):
        user=request.env.user
        ifuser.karma<forum.karma_moderate:
            raisewerkzeug.exceptions.NotFound()

        Post=request.env['forum.post']
        domain=[('forum_id','=',forum.id),('state','=','flagged')]
        ifkwargs.get('spam_post'):
            domain+=[('name','ilike',kwargs.get('spam_post'))]
        flagged_posts_ids=Post.search(domain,order='write_dateDESC')

        values=self._prepare_user_values(forum=forum)
        values.update({
            'posts_ids':flagged_posts_ids.sudo(),
            'queue_type':'flagged',
            'flagged_queue_active':1,
        })

        returnrequest.render("website_forum.moderation_queue",values)

    @http.route('/forum/<model("forum.forum"):forum>/offensive_posts',type='http',auth="user",website=True)
    defoffensive_posts(self,forum,**kwargs):
        user=request.env.user
        ifuser.karma<forum.karma_moderate:
            raisewerkzeug.exceptions.NotFound()

        Post=request.env['forum.post']
        domain=[('forum_id','=',forum.id),('state','=','offensive'),('active','=',False)]
        offensive_posts_ids=Post.search(domain,order='write_dateDESC')

        values=self._prepare_user_values(forum=forum)
        values.update({
            'posts_ids':offensive_posts_ids.sudo(),
            'queue_type':'offensive',
        })

        returnrequest.render("website_forum.moderation_queue",values)

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/validate',type='http',auth="user",website=True)
    defpost_accept(self,forum,post,**kwargs):
        url="/forum/%s/validation_queue"%(slug(forum))
        ifpost.state=='flagged':
            url="/forum/%s/flagged_queue"%(slug(forum))
        elifpost.state=='offensive':
            url="/forum/%s/offensive_posts"%(slug(forum))
        post.validate()
        returnwerkzeug.utils.redirect(url)

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/refuse',type='http',auth="user",website=True)
    defpost_refuse(self,forum,post,**kwargs):
        post.refuse()
        returnself.question_ask_for_close(forum,post)

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/flag',type='json',auth="public",website=True)
    defpost_flag(self,forum,post,**kwargs):
        ifnotrequest.session.uid:
            return{'error':'anonymous_user'}
        returnpost.flag()[0]

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/ask_for_mark_as_offensive',type='http',auth="user",methods=['GET'],website=True)
    defpost_ask_for_mark_as_offensive(self,forum,post,**kwargs):
        offensive_reasons=request.env['forum.post.reason'].search([('reason_type','=','offensive')])

        values=self._prepare_user_values(forum=forum)
        values.update({
            'question':post,
            'forum':forum,
            'reasons':offensive_reasons,
            'offensive':True,
        })
        returnrequest.render("website_forum.close_post",values)

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/mark_as_offensive',type='http',auth="user",methods=["POST"],website=True)
    defpost_mark_as_offensive(self,forum,post,**kwargs):
        post.mark_as_offensive(reason_id=int(kwargs.get('reason_id',False)))
        url=''
        ifpost.parent_id:
            url="/forum/%s/%s/#answer-%s"%(slug(forum),post.parent_id.id,post.id)
        else:
            url="/forum/%s/%s"%(slug(forum),slug(post))
        returnwerkzeug.utils.redirect(url)

    #User
    #--------------------------------------------------
    @http.route(['/forum/<model("forum.forum"):forum>/partner/<int:partner_id>'],type='http',auth="public",website=True)
    defopen_partner(self,forum,partner_id=0,**post):
        ifpartner_id:
            partner=request.env['res.partner'].sudo().search([('id','=',partner_id)])
            ifpartnerandpartner.user_ids:
                returnwerkzeug.utils.redirect("/forum/%s/user/%d"%(slug(forum),partner.user_ids[0].id))
        returnwerkzeug.utils.redirect("/forum/%s"%slug(forum))

    #Profile
    #-----------------------------------

    @http.route(['/forum/<model("forum.forum"):forum>/user/<int:user_id>'],type='http',auth="public",website=True)
    defview_user_forum_profile(self,forum,user_id,forum_origin,**post):
        returnwerkzeug.utils.redirect('/profile/user/'+str(user_id)+'?forum_id='+str(forum.id)+'&forum_origin='+str(forum_origin))

    def_prepare_user_profile_values(self,user,**post):
        values=super(WebsiteForum,self)._prepare_user_profile_values(user,**post)
        ifnotpost.get('no_forum'):
            ifpost.get('forum'):
                forums=post['forum']
            elifpost.get('forum_id'):
                forums=request.env['forum.forum'].browse(int(post['forum_id']))
                values.update({
                    'edit_button_url_param':'forum_id=%s'%str(post['forum_id']),
                    'forum_filtered':forums.name,
                })
            else:
                forums=request.env['forum.forum'].search([])

            values.update(self._prepare_user_values(forum=forums[0]iflen(forums)==1elseTrue,**post))
            ifforums:
                values.update(self._prepare_open_forum_user(user,forums))
        returnvalues

    def_prepare_open_forum_user(self,user,forums,**kwargs):
        Post=request.env['forum.post']
        Vote=request.env['forum.post.vote']
        Activity=request.env['mail.message']
        Followers=request.env['mail.followers']
        Data=request.env["ir.model.data"]

        #questionsandanswersbyuser
        user_question_ids=Post.search([
            ('parent_id','=',False),
            ('forum_id','in',forums.ids),('create_uid','=',user.id)],
            order='create_datedesc')
        count_user_questions=len(user_question_ids)
        min_karma_unlink=min(forums.mapped('karma_unlink_all'))

        #limitlengthofvisiblepostsbydefaultforperformancereasons,exceptforthehigh
        #karmausers(notmanyofthem,andtheyneedittoproperlymoderatetheforum)
        post_display_limit=None
        ifrequest.env.user.karma<min_karma_unlink:
            post_display_limit=20

        user_questions=user_question_ids[:post_display_limit]
        user_answer_ids=Post.search([
            ('parent_id','!=',False),
            ('forum_id','in',forums.ids),('create_uid','=',user.id)],
            order='create_datedesc')
        count_user_answers=len(user_answer_ids)
        user_answers=user_answer_ids[:post_display_limit]

        #showingquestionswhichuserfollowing
        post_ids=[follower.res_idforfollowerinFollowers.sudo().search(
            [('res_model','=','forum.post'),('partner_id','=',user.partner_id.id)])]
        followed=Post.search([('id','in',post_ids),('forum_id','in',forums.ids),('parent_id','=',False)])

        #showingFavouritequestionsofuser.
        favourite=Post.search(
            [('favourite_ids','=',user.id),('forum_id','in',forums.ids),('parent_id','=',False)])

        #voteswhichgivenonusersquestionsandanswers.
        data=Vote.read_group([('forum_id','in',forums.ids),('recipient_id','=',user.id)],["vote"],
                               groupby=["vote"])
        up_votes,down_votes=0,0
        forrecindata:
            ifrec['vote']=='1':
                up_votes=rec['vote_count']
            elifrec['vote']=='-1':
                down_votes=rec['vote_count']

        #Voteswhichgivenbyusersonothersquestionsandanswers.
        vote_ids=Vote.search([('user_id','=',user.id),('forum_id','in',forums.ids)])

        #activitybyuser.
        model,comment=Data.get_object_reference('mail','mt_comment')
        activities=Activity.search(
            [('res_id','in',(user_question_ids+user_answer_ids).ids),('model','=','forum.post'),
             ('subtype_id','!=',comment)],
            order='dateDESC',limit=100)

        posts={}
        foractinactivities:
            posts[act.res_id]=True
        posts_ids=Post.search([('id','in',list(posts))])
        posts={x.id:(x.parent_idorx,x.parent_idandxorFalse)forxinposts_ids}

        #TDECLEANMEMASTER:couldn'titberewrittenusinga'menu'keyinsteadofonekeyforeachmenu?
        ifuser==request.env.user:
            kwargs['my_profile']=True
        else:
            kwargs['users']=True

        values={
            'uid':request.env.user.id,
            'user':user,
            'main_object':user,
            'searches':kwargs,
            'questions':user_questions,
            'count_questions':count_user_questions,
            'answers':user_answers,
            'count_answers':count_user_answers,
            'followed':followed,
            'favourite':favourite,
            'up_votes':up_votes,
            'down_votes':down_votes,
            'activities':activities,
            'posts':posts,
            'vote_post':vote_ids,
            'is_profile_page':True,
            'badge_category':'forum',
        }

        returnvalues

    #Messaging
    #--------------------------------------------------

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/comment/<model("mail.message"):comment>/convert_to_answer',type='http',auth="user",methods=['POST'],website=True)
    defconvert_comment_to_answer(self,forum,post,comment,**kwarg):
        post=request.env['forum.post'].convert_comment_to_answer(comment.id)
        ifnotpost:
            returnwerkzeug.utils.redirect("/forum/%s"%slug(forum))
        question=post.parent_idifpost.parent_idelsepost
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/convert_to_comment',type='http',auth="user",methods=['POST'],website=True)
    defconvert_answer_to_comment(self,forum,post,**kwarg):
        question=post.parent_id
        new_msg=post.convert_answer_to_comment()
        ifnotnew_msg:
            returnwerkzeug.utils.redirect("/forum/%s"%slug(forum))
        returnwerkzeug.utils.redirect("/forum/%s/%s"%(slug(forum),slug(question)))

    @http.route('/forum/<model("forum.forum"):forum>/post/<model("forum.post"):post>/comment/<model("mail.message"):comment>/delete',type='json',auth="user",website=True)
    defdelete_comment(self,forum,post,comment,**kwarg):
        ifnotrequest.session.uid:
            return{'error':'anonymous_user'}
        returnpost.unlink_comment(comment.id)[0]
