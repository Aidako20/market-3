#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importre
importwerkzeug
importitertools
importpytz
importbabel.dates
fromcollectionsimportOrderedDict

fromflectraimporthttp,fields
fromflectra.addons.http_routing.models.ir_httpimportslug,unslug
fromflectra.addons.website.controllers.mainimportQueryURL
fromflectra.addons.portal.controllers.portalimport_build_url_w_params
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.toolsimporthtml2plaintext
fromflectra.tools.miscimportget_lang
fromflectra.toolsimportsql


classWebsiteBlog(http.Controller):
    _blog_post_per_page=12 #multipleof2,3,4
    _post_comment_per_page=10

    deftags_list(self,tag_ids,current_tag):
        tag_ids=list(tag_ids) #requiredtoavoidusingthesamelist
        ifcurrent_tagintag_ids:
            tag_ids.remove(current_tag)
        else:
            tag_ids.append(current_tag)
        tag_ids=request.env['blog.tag'].browse(tag_ids)
        return','.join(slug(tag)fortagintag_ids)

    defnav_list(self,blog=None):
        dom=blogand[('blog_id','=',blog.id)]or[]
        ifnotrequest.env.user.has_group('website.group_website_designer'):
            dom+=[('post_date','<=',fields.Datetime.now())]
        groups=request.env['blog.post']._read_group_raw(
            dom,
            ['name','post_date'],
            groupby=["post_date"],orderby="post_datedesc")
        forgroupingroups:
            (r,label)=group['post_date']
            start,end=r.split('/')
            group['post_date']=label
            group['date_begin']=start
            group['date_end']=end

            locale=get_lang(request.env).code
            start=pytz.UTC.localize(fields.Datetime.from_string(start))
            tzinfo=pytz.timezone(request.context.get('tz','utc')or'utc')

            group['month']=babel.dates.format_datetime(start,format='MMMM',tzinfo=tzinfo,locale=locale)
            group['year']=babel.dates.format_datetime(start,format='yyyy',tzinfo=tzinfo,locale=locale)

        returnOrderedDict((year,[mforminmonths])foryear,monthsinitertools.groupby(groups,lambdag:g['year']))

    def_prepare_blog_values(self,blogs,blog=False,date_begin=False,date_end=False,tags=False,state=False,page=False,search=None):
        """Prepareallvaluestodisplaytheblogsindexpageoronespecificblog"""
        BlogPost=request.env['blog.post']
        BlogTag=request.env['blog.tag']

        #preparedomain
        domain=request.website.website_domain()

        ifblog:
            domain+=[('blog_id','=',blog.id)]

        ifdate_beginanddate_end:
            domain+=[("post_date",">=",date_begin),("post_date","<=",date_end)]
        active_tag_ids=tagsand[unslug(tag)[1]fortagintags.split(',')]or[]
        active_tags=BlogTag
        ifactive_tag_ids:
            active_tags=BlogTag.browse(active_tag_ids).exists()
            fixed_tag_slug=",".join(slug(t)fortinactive_tags)
            iffixed_tag_slug!=tags:
                path=request.httprequest.full_path
                new_url=path.replace("/tag/%s"%tags,fixed_tag_slugand"/tag/%s"%fixed_tag_slugor"",1)
                ifnew_url!=path: #checkthatreallyreplacedandavoidloop
                    returnrequest.redirect(new_url,301)
            domain+=[('tag_ids','in',active_tags.ids)]

        ifrequest.env.user.has_group('website.group_website_designer'):
            count_domain=domain+[("website_published","=",True),("post_date","<=",fields.Datetime.now())]
            published_count=BlogPost.search_count(count_domain)
            unpublished_count=BlogPost.search_count(domain)-published_count

            ifstate=="published":
                domain+=[("website_published","=",True),("post_date","<=",fields.Datetime.now())]
            elifstate=="unpublished":
                domain+=['|',("website_published","=",False),("post_date",">",fields.Datetime.now())]
        else:
            domain+=[("post_date","<=",fields.Datetime.now())]

        use_cover=request.website.is_view_active('website_blog.opt_blog_cover_post')
        fullwidth_cover=request.website.is_view_active('website_blog.opt_blog_cover_post_fullwidth_design')

        #ifblog,weshowblogtitle,ifuse_coverandnotfullwidth_coverweneedpager+latestalways
        offset=(page-1)*self._blog_post_per_page
        first_post=BlogPost
        ifnotblog:
            #TODOadaptnextlineinmaster.
            first_post=BlogPost.search(domain+[('website_published','=',True)],order="post_datedesc,idasc",limit=1)ifnotsearchelsefirst_post
            ifuse_coverandnotfullwidth_coverandnottagsandnotdate_beginandnotdate_endandnotsearch:
                offset+=1

        ifsearch:
            tags_like_search=BlogTag.search([('name','ilike',search)])
            domain+=['|','|','|',('author_name','ilike',search),('name','ilike',search),('content','ilike',search),('tag_ids','in',tags_like_search.ids)]

        posts=BlogPost.search(domain,offset=offset,limit=self._blog_post_per_page,order="is_publisheddesc,post_datedesc,idasc")
        total=BlogPost.search_count(domain)

        pager=request.website.pager(
            url=request.httprequest.path.partition('/page/')[0],
            total=total,
            page=page,
            step=self._blog_post_per_page,
            url_args={'search':search,'date_begin':date_begin,'date_end':date_end},
        )

        ifnotblogs:
            all_tags=request.env['blog.tag']
        else:
            all_tags=blogs.all_tags(join=True)ifnotblogelseblogs.all_tags().get(blog.id,request.env['blog.tag'])
        tag_category=sorted(all_tags.mapped('category_id'),key=lambdacategory:category.name.upper())
        other_tags=sorted(all_tags.filtered(lambdax:notx.category_id),key=lambdatag:tag.name.upper())

        #forperformanceprefetchthefirstpostwiththeothers
        post_ids=(first_post|posts).ids

        return{
            'date_begin':date_begin,
            'date_end':date_end,
            'first_post':first_post.with_prefetch(post_ids),
            'other_tags':other_tags,
            'tag_category':tag_category,
            'nav_list':self.nav_list(),
            'tags_list':self.tags_list,
            'pager':pager,
            'posts':posts.with_prefetch(post_ids),
            'tag':tags,
            'active_tag_ids':active_tags.ids,
            'domain':domain,
            'state_info':stateand{"state":state,"published":published_count,"unpublished":unpublished_count},
            'blogs':blogs,
            'blog':blog,
            'search':search,
            'search_count':total,
        }

    @http.route([
        '/blog',
        '/blog/page/<int:page>',
        '/blog/tag/<string:tag>',
        '/blog/tag/<string:tag>/page/<int:page>',
        '''/blog/<model("blog.blog"):blog>''',
        '''/blog/<model("blog.blog"):blog>/page/<int:page>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>''',
        '''/blog/<model("blog.blog"):blog>/tag/<string:tag>/page/<int:page>''',
    ],type='http',auth="public",website=True,sitemap=True)
    defblog(self,blog=None,tag=None,page=1,search=None,**opt):
        Blog=request.env['blog.blog']

        #TODOadaptinmaster.Thisisafixfortemplateswronglyusingthe
        #'blog_url'QueryURLwhichisdefinedbelow.Indeed,inthecasewhere
        #wearerenderingablogpagewherenospecificblogisselectedwe
        #define(d)thatas`QueryURL('/blog',['tag'],...)`butthensome
        #partsofthetemplateuseditlikethis:`blog_url(blog=XXX)`thus
        #generatinganURLlike"/blog?blog=blog.blog(2,)".Adding"blog"to
        #thelistofparamswouldnotberightaswouldcreate"/blog/blog/2"
        #whichisstillwrongaswewant"/blog/2".Andofcoursethe"/blog"
        #prefixintheQueryURLdefinitionisneededincaseweonlyspecifya
        #tagvia`blog_url(tab=X)`(weexpect/blog/tag/X).PatchingQueryURL
        #ormakingblog_urlacustomfunctioninsteadofaQueryURLinstance
        #couldbeasolutionbutitwasjudgednotstableenough.We'lldothat
        #inmaster.Hereweonlysupport"/blog?blog=blog.blog(2,)"URLs.
        ifisinstance(blog,str):
            blog=Blog.browse(int(re.search(r'\d+',blog)[0]))
            ifnotblog.exists():
                raisewerkzeug.exceptions.NotFound()

        ifblogandnotblog.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        blogs=Blog.search(request.website.website_domain(),order="create_dateasc,idasc")

        ifnotblogandlen(blogs)==1:
            url=QueryURL('/blog/%s'%slug(blogs[0]),search=search,**opt)()
            returnwerkzeug.utils.redirect(url,code=302)

        date_begin,date_end,state=opt.get('date_begin'),opt.get('date_end'),opt.get('state')

        iftagandrequest.httprequest.method=='GET':
            #redirectgettag-1,tag-2->gettag-1
            tags=tag.split(',')
            iflen(tags)>1:
                url=QueryURL(''ifblogelse'/blog',['blog','tag'],blog=blog,tag=tags[0],date_begin=date_begin,date_end=date_end,search=search)()
                returnrequest.redirect(url,code=302)

        values=self._prepare_blog_values(blogs=blogs,blog=blog,date_begin=date_begin,date_end=date_end,tags=tag,state=state,page=page,search=search)

        #incaseofaredirectionneedby`_prepare_blog_values`wefollowit
        ifisinstance(values,werkzeug.wrappers.Response):
            returnvalues

        ifblog:
            values['main_object']=blog
            values['edit_in_backend']=True
            values['blog_url']=QueryURL('',['blog','tag'],blog=blog,tag=tag,date_begin=date_begin,date_end=date_end,search=search)
        else:
            values['blog_url']=QueryURL('/blog',['tag'],date_begin=date_begin,date_end=date_end,search=search)

        returnrequest.render("website_blog.blog_post_short",values)

    @http.route(['''/blog/<model("blog.blog"):blog>/feed'''],type='http',auth="public",website=True,sitemap=True)
    defblog_feed(self,blog,limit='15',**kwargs):
        v={}
        v['blog']=blog
        v['base_url']=blog.get_base_url()
        v['posts']=request.env['blog.post'].search([('blog_id','=',blog.id)],limit=min(int(limit),50),order="post_dateDESC")
        v['html2plaintext']=html2plaintext
        r=request.render("website_blog.blog_feed",v,headers=[('Content-Type','application/atom+xml')])
        returnr

    @http.route([
        '''/blog/<model("blog.blog"):blog>/post/<model("blog.post","[('blog_id','=',blog.id)]"):blog_post>''',
    ],type='http',auth="public",website=True,sitemap=False)
    defold_blog_post(self,blog,blog_post,tag_id=None,page=1,enable_editor=None,**post):
        #Compatibilitypre-v14
        returnrequest.redirect(_build_url_w_params("/blog/%s/%s"%(slug(blog),slug(blog_post)),request.params),code=301)

    @http.route([
        '''/blog/<model("blog.blog"):blog>/<model("blog.post","[('blog_id','=',blog.id)]"):blog_post>''',
    ],type='http',auth="public",website=True,sitemap=True)
    defblog_post(self,blog,blog_post,tag_id=None,page=1,enable_editor=None,**post):
        """Prepareallvaluestodisplaytheblog.

        :returndictvalues:valuesforthetemplates,containing

         -'blog_post':browseofthecurrentpost
         -'blog':browseofthecurrentblog
         -'blogs':listofbrowserecordsofblogs
         -'tag':currenttag,iftag_idinparameters
         -'tags':alltags,fortag-basednavigation
         -'pager':apageronthecomments
         -'nav_list':adict[year][month]forarchivesnavigation
         -'next_post':nextblogpost,todirecttheusertowardsthenextinterestingpost
        """
        ifnotblog.can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        BlogPost=request.env['blog.post']
        date_begin,date_end=post.get('date_begin'),post.get('date_end')

        domain=request.website.website_domain()
        blogs=blog.search(domain,order="create_date,idasc")

        tag=None
        iftag_id:
            tag=request.env['blog.tag'].browse(int(tag_id))
        blog_url=QueryURL('',['blog','tag'],blog=blog_post.blog_id,tag=tag,date_begin=date_begin,date_end=date_end)

        ifnotblog_post.blog_id.id==blog.id:
            returnrequest.redirect("/blog/%s/%s"%(slug(blog_post.blog_id),slug(blog_post)),code=301)

        tags=request.env['blog.tag'].search([])

        #FindnextPost
        blog_post_domain=[('blog_id','=',blog.id)]
        ifnotrequest.env.user.has_group('website.group_website_designer'):
            blog_post_domain+=[('post_date','<=',fields.Datetime.now())]

        all_post=BlogPost.search(blog_post_domain)

        ifblog_postnotinall_post:
            returnrequest.redirect("/blog/%s"%(slug(blog_post.blog_id)))

        #shouldalwaysreturnatleastthecurrentpost
        all_post_ids=all_post.ids
        current_blog_post_index=all_post_ids.index(blog_post.id)
        nb_posts=len(all_post_ids)
        next_post_id=all_post_ids[(current_blog_post_index+1)%nb_posts]ifnb_posts>1elseNone
        next_post=next_post_idandBlogPost.browse(next_post_id)orFalse

        values={
            'tags':tags,
            'tag':tag,
            'blog':blog,
            'blog_post':blog_post,
            'blogs':blogs,
            'main_object':blog_post,
            'nav_list':self.nav_list(blog),
            'enable_editor':enable_editor,
            'next_post':next_post,
            'date':date_begin,
            'blog_url':blog_url,
        }
        response=request.render("website_blog.blog_post_complete",values)

        ifblog_post.idnotinrequest.session.get('posts_viewed',[]):
            ifsql.increment_field_skiplock(blog_post,'visits'):
                ifnotrequest.session.get('posts_viewed'):
                    request.session['posts_viewed']=[]
                request.session['posts_viewed'].append(blog_post.id)
                request.session.modified=True
        returnresponse

    @http.route('/blog/<int:blog_id>/post/new',type='http',auth="user",website=True)
    defblog_post_create(self,blog_id,**post):
        #Usesudosothislinepreventsbotheditorandadmintoaccessblogfromanotherwebsite
        #asbrowse()willreturntherecordevenifforbiddenbysecurityrulesbuteditorwon't
        #beabletoaccessit
        ifnotrequest.env['blog.blog'].browse(blog_id).sudo().can_access_from_current_website():
            raisewerkzeug.exceptions.NotFound()

        new_blog_post=request.env['blog.post'].create({
            'blog_id':blog_id,
            'is_published':False,
        })
        returnwerkzeug.utils.redirect("/blog/%s/%s?enable_editor=1"%(slug(new_blog_post.blog_id),slug(new_blog_post)))

    @http.route('/blog/post_duplicate',type='http',auth="user",website=True,methods=['POST'])
    defblog_post_copy(self,blog_post_id,**post):
        """Duplicateablog.

        :paramblog_post_id:idoftheblogpostcurrentlybrowsed.

        :returnredirecttothenewblogcreated
        """
        new_blog_post=request.env['blog.post'].with_context(mail_create_nosubscribe=True).browse(int(blog_post_id)).copy()
        returnwerkzeug.utils.redirect("/blog/%s/%s?enable_editor=1"%(slug(new_blog_post.blog_id),slug(new_blog_post)))

    @http.route(['/blog/render_latest_posts'],type='json',auth='public',website=True)
    defrender_latest_posts(self,template,domain,limit=None,order='published_datedesc'):
        dom=expression.AND([
            [('website_published','=',True),('post_date','<=',fields.Datetime.now())],
            request.website.website_domain()
        ])
        ifdomain:
            dom=expression.AND([dom,domain])
        posts=request.env['blog.post'].search(dom,limit=limit,order=order)
        returnrequest.website.viewref(template)._render({'posts':posts})
