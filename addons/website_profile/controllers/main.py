#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importwerkzeug
importwerkzeug.exceptions
importwerkzeug.urls
importwerkzeug.wrappers
importmath

fromdateutil.relativedeltaimportrelativedelta
fromoperatorimportitemgetter

fromflectraimportfields,http,modules,tools
fromflectra.httpimportrequest
fromflectra.osvimportexpression


classWebsiteProfile(http.Controller):
    _users_per_page=30
    _pager_max_pages=5

    #Profile
    #---------------------------------------------------

    def_check_avatar_access(self,user_id,**post):
        """Baseconditiontoseeuseravatarindependentlyformaccessrights
        istoseepublishedusershavingkarma,meaningtheyparticipatedto
        frontendapplicationslikeforumorelearning."""
        try:
            user=request.env['res.users'].sudo().browse(user_id).exists()
        except:
            returnFalse
        ifuser:
            returnuser.website_publishedanduser.karma>0
        returnFalse

    def_get_default_avatar(self):
        img_path=modules.get_module_resource('web','static/src/img','placeholder.png')
        withopen(img_path,'rb')asf:
            returnbase64.b64encode(f.read())

    def_check_user_profile_access(self,user_id):
        user_sudo=request.env['res.users'].sudo().browse(user_id)
        #Usercanaccess-nomatterwhat-hisownprofile
        ifuser_sudo.id==request.env.user.id:
            returnuser_sudo
        ifuser_sudo.karma==0ornotuser_sudo.website_publishedor\
            (user_sudo.id!=request.session.uidandrequest.env.user.karma<request.website.karma_profile_min):
            returnFalse
        returnuser_sudo

    def_prepare_user_values(self,**kwargs):
        kwargs.pop('edit_translations',None)#avoidnukingedit_translations
        values={
            'user':request.env.user,
            'is_public_user':request.website.is_public_user(),
            'validation_email_sent':request.session.get('validation_email_sent',False),
            'validation_email_done':request.session.get('validation_email_done',False),
        }
        values.update(kwargs)
        returnvalues

    def_prepare_user_profile_parameters(self,**post):
        returnpost

    def_prepare_user_profile_values(self,user,**post):
        return{
            'uid':request.env.user.id,
            'user':user,
            'main_object':user,
            'is_profile_page':True,
            'edit_button_url_param':'',
        }

    @http.route([
        '/profile/avatar/<int:user_id>',
    ],type='http',auth="public",website=True,sitemap=False)
    defget_user_profile_avatar(self,user_id,field='image_256',width=0,height=0,crop=False,**post):
        iffieldnotin('image_128','image_256'):
            returnwerkzeug.exceptions.Forbidden()

        can_sudo=self._check_avatar_access(user_id,**post)
        ifcan_sudo:
            status,headers,image_base64=request.env['ir.http'].sudo().binary_content(
                model='res.users',id=user_id,field=field,
                default_mimetype='image/png')
        else:
            status,headers,image_base64=request.env['ir.http'].binary_content(
                model='res.users',id=user_id,field=field,
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

    @http.route(['/profile/user/<int:user_id>'],type='http',auth="public",website=True)
    defview_user_profile(self,user_id,**post):
        user=self._check_user_profile_access(user_id)
        ifnotuser:
            returnrequest.render("website_profile.private_profile")
        values=self._prepare_user_values(**post)
        params=self._prepare_user_profile_parameters(**post)
        values.update(self._prepare_user_profile_values(user,**params))
        returnrequest.render("website_profile.user_profile_main",values)

    #EditProfile
    #---------------------------------------------------
    @http.route('/profile/edit',type='http',auth="user",website=True)
    defview_user_profile_edition(self,**kwargs):
        user_id=int(kwargs.get('user_id',0))
        countries=request.env['res.country'].search([])
        ifuser_idandrequest.env.user.id!=user_idandrequest.env.user._is_admin():
            user=request.env['res.users'].browse(user_id)
            values=self._prepare_user_values(searches=kwargs,user=user,is_public_user=False)
        else:
            values=self._prepare_user_values(searches=kwargs)
        values.update({
            'email_required':kwargs.get('email_required'),
            'countries':countries,
            'url_param':kwargs.get('url_param'),
        })
        returnrequest.render("website_profile.user_profile_edit_main",values)

    def_profile_edition_preprocess_values(self,user,**kwargs):
        values={
            'name':kwargs.get('name'),
            'website':kwargs.get('website'),
            'email':kwargs.get('email'),
            'city':kwargs.get('city'),
            'country_id':int(kwargs.get('country'))ifkwargs.get('country')elseFalse,
            'website_description':kwargs.get('description'),
        }

        if'clear_image'inkwargs:
            values['image_1920']=False
        elifkwargs.get('ufile'):
            image=kwargs.get('ufile').read()
            values['image_1920']=base64.b64encode(image)

        ifrequest.uid==user.id: #thecontrollerallowstoeditonlyitsownprivacysettings;usepartnermanagementforothercases
            values['website_published']=kwargs.get('website_published')=='True'
        returnvalues

    @http.route('/profile/user/save',type='http',auth="user",methods=['POST'],website=True)
    defsave_edited_profile(self,**kwargs):
        user_id=int(kwargs.get('user_id',0))
        ifuser_idandrequest.env.user.id!=user_idandrequest.env.user._is_admin():
            user=request.env['res.users'].browse(user_id)
        else:
            user=request.env.user
        values=self._profile_edition_preprocess_values(user,**kwargs)
        whitelisted_values={key:values[key]forkeyinrequest.env.registry['res.users'].SELF_WRITEABLE_FIELDSifkeyinvalues}
        user.write(whitelisted_values)
        ifkwargs.get('url_param'):
            returnwerkzeug.utils.redirect("/profile/user/%d?%s"%(user.id,kwargs['url_param']))
        else:
            returnwerkzeug.utils.redirect("/profile/user/%d"%user.id)

    #RanksandBadges
    #---------------------------------------------------
    def_prepare_badges_domain(self,**kwargs):
        """
        Hookforothermodulestorestrictthebadgesshowedonprofilepage,dependingofthecontext
        """
        domain=[('website_published','=',True)]
        if'badge_category'inkwargs:
            domain=expression.AND([[('challenge_ids.challenge_category','=',kwargs.get('badge_category'))],domain])
        returndomain

    def_prepare_ranks_badges_values(self,**kwargs):
        ranks=[]
        if'badge_category'notinkwargs:
            Rank=request.env['gamification.karma.rank']
            ranks=Rank.sudo().search([],order='karma_minDESC')

        Badge=request.env['gamification.badge']
        badges=Badge.sudo().search(self._prepare_badges_domain(**kwargs))
        badges=badges.sorted("granted_users_count",reverse=True)
        values=self._prepare_user_values(searches={'badges':True})

        values.update({
            'ranks':ranks,
            'badges':badges,
            'user':request.env.user,
        })
        returnvalues

    @http.route('/profile/ranks_badges',type='http',auth="public",website=True,sitemap=True)
    defview_ranks_badges(self,**kwargs):
        values=self._prepare_ranks_badges_values(**kwargs)
        returnrequest.render("website_profile.rank_badge_main",values)

    #AllUsersPage
    #---------------------------------------------------
    def_prepare_all_users_values(self,users):
        user_values=[]
        foruserinusers:
            user_values.append({
                'id':user.id,
                'name':user.name,
                'company_name':user.company_id.name,
                'rank':user.rank_id.name,
                'karma':user.karma,
                'badge_count':len(user.badge_ids),
                'website_published':user.website_published
            })
        returnuser_values

    @http.route(['/profile/users',
                 '/profile/users/page/<int:page>'],type='http',auth="public",website=True,sitemap=True)
    defview_all_users_page(self,page=1,**kwargs):
        User=request.env['res.users']
        dom=[('karma','>',1),('website_published','=',True)]

        #Searches
        search_term=kwargs.get('search')
        group_by=kwargs.get('group_by',False)
        render_values={
            'search':search_term,
            'group_by':group_byor'all',
        }
        ifsearch_term:
            dom=expression.AND([['|',('name','ilike',search_term),('partner_id.commercial_company_name','ilike',search_term)],dom])

        user_count=User.sudo().search_count(dom)
        my_user=request.env.user
        current_user_values=False
        ifuser_count:
            page_count=math.ceil(user_count/self._users_per_page)
            pager=request.website.pager(url="/profile/users",total=user_count,page=page,step=self._users_per_page,
                                          scope=page_countifpage_count<self._pager_max_pageselseself._pager_max_pages,
                                          url_args=kwargs)

            users=User.sudo().search(dom,limit=self._users_per_page,offset=pager['offset'],order='karmaDESC')
            user_values=self._prepare_all_users_values(users)

            #Getkarmapositionforusers(onlywebsite_published)
            position_domain=[('karma','>',1),('website_published','=',True)]
            position_map=self._get_position_map(position_domain,users,group_by)

            max_position=max([user_data['karma_position']foruser_datainposition_map.values()],default=1)
            foruserinuser_values:
                user_data=position_map.get(user['id'],dict())
                user['position']=user_data.get('karma_position',max_position+1)
                user['karma_gain']=user_data.get('karma_gain_total',0)
            user_values.sort(key=itemgetter('position'))

            ifmy_user.website_publishedandmy_user.karmaandmy_user.idnotinusers.ids:
                #Needtokeepthedomtosearchonlyforusersthatappearintherankingpage
                current_user=User.sudo().search(expression.AND([[('id','=',my_user.id)],dom]))
                ifcurrent_user:
                    current_user_values=self._prepare_all_users_values(current_user)[0]

                    user_data=self._get_position_map(position_domain,current_user,group_by).get(current_user.id,{})
                    current_user_values['position']=user_data.get('karma_position',0)
                    current_user_values['karma_gain']=user_data.get('karma_gain_total',0)

        else:
            user_values=[]
            pager={'page_count':0}
        render_values.update({
            'top3_users':user_values[:3]ifnotsearch_termandpage==1else[],
            'users':user_values,
            'my_user':current_user_values,
            'pager':pager,
        })
        returnrequest.render("website_profile.users_page_main",render_values)

    def_get_position_map(self,position_domain,users,group_by):
        ifgroup_by:
            position_map=self._get_user_tracking_karma_gain_position(position_domain,users.ids,group_by)
        else:
            position_results=users._get_karma_position(position_domain)
            position_map=dict((user_data['user_id'],dict(user_data))foruser_datainposition_results)
        returnposition_map

    def_get_user_tracking_karma_gain_position(self,domain,user_ids,group_by):
        """Helpermethodcomputingboundariestogiveto_get_tracking_karma_gain_position.
        Seethatmethodformoredetails."""
        to_date=fields.Date.today()
        ifgroup_by=='week':
            from_date=to_date-relativedelta(weeks=1)
        elifgroup_by=='month':
            from_date=to_date-relativedelta(months=1)
        else:
            from_date=None
        results=request.env['res.users'].browse(user_ids)._get_tracking_karma_gain_position(domain,from_date=from_date,to_date=to_date)
        returndict((item['user_id'],dict(item))foriteminresults)

    #Userandvalidation
    #--------------------------------------------------

    @http.route('/profile/send_validation_email',type='json',auth='user',website=True)
    defsend_validation_email(self,**kwargs):
        ifrequest.env.uid!=request.website.user_id.id:
            request.env.user._send_profile_validation_email(**kwargs)
        request.session['validation_email_sent']=True
        returnTrue

    @http.route('/profile/validate_email',type='http',auth='public',website=True,sitemap=False)
    defvalidate_email(self,token,user_id,email,**kwargs):
        done=request.env['res.users'].sudo().browse(int(user_id))._process_profile_validation_token(token,email)
        ifdone:
            request.session['validation_email_done']=True
        url=kwargs.get('redirect_url','/')
        returnrequest.redirect(url)

    @http.route('/profile/validate_email/close',type='json',auth='public',website=True)
    defvalidate_email_done(self,**kwargs):
        request.session['validation_email_done']=False
        returnTrue
