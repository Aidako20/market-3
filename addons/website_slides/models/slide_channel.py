#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importuuid
fromcollectionsimportdefaultdict

fromdateutil.relativedeltaimportrelativedelta
importast

fromflectraimportapi,fields,models,tools,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.exceptionsimportAccessError
fromflectra.osvimportexpression


classChannelUsersRelation(models.Model):
    _name='slide.channel.partner'
    _description='Channel/Partners(Members)'
    _table='slide_channel_partner'

    channel_id=fields.Many2one('slide.channel',index=True,required=True,ondelete='cascade')
    completed=fields.Boolean('IsCompleted',help='Channelvalidated,evenifslides/lessonsareaddedoncedone.')
    completion=fields.Integer('%CompletedSlides')
    completed_slides_count=fields.Integer('#CompletedSlides')
    partner_id=fields.Many2one('res.partner',index=True,required=True,ondelete='cascade')
    partner_email=fields.Char(related='partner_id.email',readonly=True)

    def_recompute_completion(self):
        read_group_res=self.env['slide.slide.partner'].sudo().read_group(
            ['&','&',('channel_id','in',self.mapped('channel_id').ids),
             ('partner_id','in',self.mapped('partner_id').ids),
             ('completed','=',True),
             ('slide_id.is_published','=',True),
             ('slide_id.active','=',True)],
            ['channel_id','partner_id'],
            groupby=['channel_id','partner_id'],lazy=False)
        mapped_data=dict()
        foriteminread_group_res:
            mapped_data.setdefault(item['channel_id'][0],dict())
            mapped_data[item['channel_id'][0]][item['partner_id'][0]]=item['__count']

        partner_karma=dict.fromkeys(self.mapped('partner_id').ids,0)
        forrecordinself:
            record.completed_slides_count=mapped_data.get(record.channel_id.id,dict()).get(record.partner_id.id,0)
            record.completion=100.0ifrecord.completedelseround(100.0*record.completed_slides_count/(record.channel_id.total_slidesor1))
            ifnotrecord.completedandrecord.channel_id.activeandrecord.completed_slides_count>=record.channel_id.total_slides:
                record.completed=True
                partner_karma[record.partner_id.id]+=record.channel_id.karma_gen_channel_finish

        partner_karma={partner_id:karma_to_add
                         forpartner_id,karma_to_addinpartner_karma.items()ifkarma_to_add>0}

        ifpartner_karma:
            users=self.env['res.users'].sudo().search([('partner_id','in',list(partner_karma.keys()))])
            foruserinusers:
                users.add_karma(partner_karma[user.partner_id.id])

    defunlink(self):
        """
        Overrideunlinkmethod:
        Removeattendeefromachannel,thenalsoremoveslide.slide.partnerrelatedto.
        """
        removed_slide_partner_domain=[]
        forchannel_partnerinself:
            #findallslidelinktothechannelandthepartner
            removed_slide_partner_domain=expression.OR([
                removed_slide_partner_domain,
                [('partner_id','=',channel_partner.partner_id.id),
                 ('slide_id','in',channel_partner.channel_id.slide_ids.ids)]
            ])
        ifremoved_slide_partner_domain:
            self.env['slide.slide.partner'].search(removed_slide_partner_domain).unlink()
        returnsuper(ChannelUsersRelation,self).unlink()


classChannel(models.Model):
    """Achannelisacontainerofslides."""
    _name='slide.channel'
    _description='Course'
    _inherit=[
        'mail.thread','rating.mixin',
        'mail.activity.mixin',
        'image.mixin',
        'website.seo.metadata','website.published.multi.mixin']
    _order='sequence,id'

    def_default_access_token(self):
        returnstr(uuid.uuid4())

    def_get_default_enroll_msg(self):
        return_('ContactResponsible')

    #description
    name=fields.Char('Name',translate=True,required=True)
    active=fields.Boolean(default=True,tracking=100)
    description=fields.Text('Description',translate=True,help="Thedescriptionthatisdisplayedontopofthecoursepage,justbelowthetitle")
    description_short=fields.Text('ShortDescription',translate=True,help="Thedescriptionthatisdisplayedonthecoursecard")
    description_html=fields.Html('DetailedDescription',translate=tools.html_translate,sanitize_attributes=False,sanitize_form=False)
    channel_type=fields.Selection([
        ('training','Training'),('documentation','Documentation')],
        string="Coursetype",default="training",required=True)
    sequence=fields.Integer(default=10,help='Displayorder')
    user_id=fields.Many2one('res.users',string='Responsible',default=lambdaself:self.env.uid)
    color=fields.Integer('ColorIndex',default=0,help='Usedtodecoratekanbanview')
    tag_ids=fields.Many2many(
        'slide.channel.tag','slide_channel_tag_rel','channel_id','tag_id',
        string='Tags',help='Usedtocategorizeandfilterdisplayedchannels/courses')
    #slides:promote,statistics
    slide_ids=fields.One2many('slide.slide','channel_id',string="Slidesandcategories")
    slide_content_ids=fields.One2many('slide.slide',string='Slides',compute="_compute_category_and_slide_ids")
    slide_category_ids=fields.One2many('slide.slide',string='Categories',compute="_compute_category_and_slide_ids")
    slide_last_update=fields.Date('LastUpdate',compute='_compute_slide_last_update',store=True)
    slide_partner_ids=fields.One2many(
        'slide.slide.partner','channel_id',string="SlideUserData",
        copy=False,groups='website_slides.group_website_slides_officer')
    promote_strategy=fields.Selection([
        ('latest','LatestPublished'),
        ('most_voted','MostVoted'),
        ('most_viewed','MostViewed'),
        ('specific','Specific'),
        ('none','None')],
        string="PromotedContent",default='latest',required=False,
        help='Dependingthepromotestrategy,aslidewillappearonthetopofthecourse\'spage:\n'
             '*LatestPublished:theslidecreatedlast.\n'
             '*MostVoted:theslidewhichhastomostvotes.\n'
             '*MostViewed;theslidewhichhasbeenviewedthemost.\n'
             '*Specific:Youchoosetheslidetoappear.\n'
             '*None:Noslideswillbeshown.\n')
    promoted_slide_id=fields.Many2one('slide.slide',string='PromotedSlide')
    access_token=fields.Char("SecurityToken",copy=False,default=_default_access_token)
    nbr_presentation=fields.Integer('Presentations',compute='_compute_slides_statistics',store=True)
    nbr_document=fields.Integer('Documents',compute='_compute_slides_statistics',store=True)
    nbr_video=fields.Integer('Videos',compute='_compute_slides_statistics',store=True)
    nbr_infographic=fields.Integer('Infographics',compute='_compute_slides_statistics',store=True)
    nbr_webpage=fields.Integer("Webpages",compute='_compute_slides_statistics',store=True)
    nbr_quiz=fields.Integer("NumberofQuizs",compute='_compute_slides_statistics',store=True)
    total_slides=fields.Integer('Content',compute='_compute_slides_statistics',store=True)
    total_views=fields.Integer('Visits',compute='_compute_slides_statistics',store=True)
    total_votes=fields.Integer('Votes',compute='_compute_slides_statistics',store=True)
    total_time=fields.Float('Duration',compute='_compute_slides_statistics',digits=(10,2),store=True)
    rating_avg_stars=fields.Float("RatingAverage(Stars)",compute='_compute_rating_stats',digits=(16,1),compute_sudo=True)
    #configuration
    allow_comment=fields.Boolean(
        "AllowratingonCourse",default=True,
        help="Ifcheckeditallowsmemberstoeither:\n"
             "*likecontentandpostcommentsondocumentationcourse;\n"
             "*postcommentandreviewontrainingcourse;")
    publish_template_id=fields.Many2one(
        'mail.template',string='NewContentEmail',
        help="Emailtemplatetosendslidepublicationthroughemail",
        default=lambdaself:self.env['ir.model.data'].xmlid_to_res_id('website_slides.slide_template_published'))
    share_template_id=fields.Many2one(
        'mail.template',string='ShareTemplate',
        help="Emailtemplateusedwhensharingaslide",
        default=lambdaself:self.env['ir.model.data'].xmlid_to_res_id('website_slides.slide_template_shared'))
    enroll=fields.Selection([
        ('public','Public'),('invite','OnInvitation')],
        default='public',string='EnrollPolicy',required=True,
        help='Conditiontoenroll:everyone,oninvite,onpayment(salebridge).')
    enroll_msg=fields.Html(
        'EnrollMessage',help="Messageexplainingtheenrollprocess",
        default=_get_default_enroll_msg,translate=tools.html_translate,sanitize_attributes=False)
    enroll_group_ids=fields.Many2many('res.groups',string='AutoEnrollGroups',help="Membersofthosegroupsareautomaticallyaddedasmembersofthechannel.")
    visibility=fields.Selection([
        ('public','Public'),('members','MembersOnly')],
        default='public',string='Visibility',required=True,
        help='ApplieddirectlyasACLs.Allowtohidechannelsandtheircontentfornonmembers.')
    partner_ids=fields.Many2many(
        'res.partner','slide_channel_partner','channel_id','partner_id',
        string='Members',help="Allmembersofthechannel.",context={'active_test':False},copy=False,depends=['channel_partner_ids'])
    members_count=fields.Integer('Attendeescount',compute='_compute_members_count')
    members_done_count=fields.Integer('AttendeesDoneCount',compute='_compute_members_done_count')
    has_requested_access=fields.Boolean(string='AccessRequested',compute='_compute_has_requested_access',compute_sudo=False)
    is_member=fields.Boolean(string='IsMember',compute='_compute_is_member',compute_sudo=False)
    channel_partner_ids=fields.One2many('slide.channel.partner','channel_id',string='MembersInformation',groups='website_slides.group_website_slides_officer',depends=['partner_ids'])
    upload_group_ids=fields.Many2many(
        'res.groups','rel_upload_groups','channel_id','group_id',string='UploadGroups',
        help="Groupofusersallowedtopublishcontentsonadocumentationcourse.")
    #notstoredaccessfields,dependingoneachuser
    completed=fields.Boolean('Done',compute='_compute_user_statistics',compute_sudo=False)
    completion=fields.Integer('Completion',compute='_compute_user_statistics',compute_sudo=False)
    can_upload=fields.Boolean('CanUpload',compute='_compute_can_upload',compute_sudo=False)
    partner_has_new_content=fields.Boolean(compute='_compute_partner_has_new_content',compute_sudo=False)
    #karmageneration
    karma_gen_slide_vote=fields.Integer(string='Lessonvoted',default=1)
    karma_gen_channel_rank=fields.Integer(string='Courseranked',default=5)
    karma_gen_channel_finish=fields.Integer(string='Coursefinished',default=10)
    #Karmabasedactions
    karma_review=fields.Integer('AddReview',default=10,help="Karmaneededtoaddareviewonthecourse")
    karma_slide_comment=fields.Integer('AddComment',default=3,help="Karmaneededtoaddacommentonaslideofthiscourse")
    karma_slide_vote=fields.Integer('Vote',default=3,help="Karmaneededtolike/dislikeaslideofthiscourse.")
    can_review=fields.Boolean('CanReview',compute='_compute_action_rights',compute_sudo=False)
    can_comment=fields.Boolean('CanComment',compute='_compute_action_rights',compute_sudo=False)
    can_vote=fields.Boolean('CanVote',compute='_compute_action_rights',compute_sudo=False)

    @api.depends('slide_ids.is_published')
    def_compute_slide_last_update(self):
        forrecordinself:
            record.slide_last_update=fields.Date.today()

    @api.depends('channel_partner_ids.channel_id')
    def_compute_members_count(self):
        read_group_res=self.env['slide.channel.partner'].sudo().read_group([('channel_id','in',self.ids)],['channel_id'],'channel_id')
        data=dict((res['channel_id'][0],res['channel_id_count'])forresinread_group_res)
        forchannelinself:
            channel.members_count=data.get(channel.id,0)

    @api.depends('channel_partner_ids.channel_id','channel_partner_ids.completed')
    def_compute_members_done_count(self):
        read_group_res=self.env['slide.channel.partner'].sudo().read_group(['&',('channel_id','in',self.ids),('completed','=',True)],['channel_id'],'channel_id')
        data=dict((res['channel_id'][0],res['channel_id_count'])forresinread_group_res)
        forchannelinself:
            channel.members_done_count=data.get(channel.id,0)

    @api.depends('activity_ids.request_partner_id')
    @api.depends_context('uid')
    @api.model
    def_compute_has_requested_access(self):
        requested_cids=self.sudo().activity_search(
            ['website_slides.mail_activity_data_access_request'],
            additional_domain=[('request_partner_id','=',self.env.user.partner_id.id)]
        ).mapped('res_id')
        forchannelinself:
            channel.has_requested_access=channel.idinrequested_cids

    @api.depends('channel_partner_ids.partner_id')
    @api.depends_context('uid')
    @api.model
    def_compute_is_member(self):
        channel_partners=self.env['slide.channel.partner'].sudo().search([
            ('channel_id','in',self.ids),
        ])
        result=dict()
        forcpinchannel_partners:
            result.setdefault(cp.channel_id.id,[]).append(cp.partner_id.id)
        forchannelinself:
            channel.is_member=channel.is_member=self.env.user.partner_id.idinresult.get(channel.id,[])

    @api.depends('slide_ids.is_category')
    def_compute_category_and_slide_ids(self):
        forchannelinself:
            channel.slide_category_ids=channel.slide_ids.filtered(lambdaslide:slide.is_category)
            channel.slide_content_ids=channel.slide_ids-channel.slide_category_ids

    @api.depends('slide_ids.slide_type','slide_ids.is_published','slide_ids.completion_time',
                 'slide_ids.likes','slide_ids.dislikes','slide_ids.total_views','slide_ids.is_category','slide_ids.active')
    def_compute_slides_statistics(self):
        default_vals=dict(total_views=0,total_votes=0,total_time=0,total_slides=0)
        keys=['nbr_%s'%slide_typeforslide_typeinself.env['slide.slide']._fields['slide_type'].get_values(self.env)]
        default_vals.update(dict((key,0)forkeyinkeys))

        result=dict((cid,dict(default_vals))forcidinself.ids)
        read_group_res=self.env['slide.slide'].read_group(
            [('active','=',True),('is_published','=',True),('channel_id','in',self.ids),('is_category','=',False)],
            ['channel_id','slide_type','likes','dislikes','total_views','completion_time'],
            groupby=['channel_id','slide_type'],
            lazy=False)
        forres_groupinread_group_res:
            cid=res_group['channel_id'][0]
            result[cid]['total_views']+=res_group.get('total_views',0)
            result[cid]['total_votes']+=res_group.get('likes',0)
            result[cid]['total_votes']-=res_group.get('dislikes',0)
            result[cid]['total_time']+=res_group.get('completion_time',0)

        type_stats=self._compute_slides_statistics_type(read_group_res)
        forcid,cdataintype_stats.items():
            result[cid].update(cdata)

        forrecordinself:
            record.update(result.get(record.id,default_vals))

    def_compute_slides_statistics_type(self,read_group_res):
        """Computestatisticsbasedonallexistingslidetypes"""
        slide_types=self.env['slide.slide']._fields['slide_type'].get_values(self.env)
        keys=['nbr_%s'%slide_typeforslide_typeinslide_types]
        result=dict((cid,dict((key,0)forkeyinkeys+['total_slides']))forcidinself.ids)
        forres_groupinread_group_res:
            cid=res_group['channel_id'][0]
            slide_type=res_group.get('slide_type')
            ifslide_type:
                slide_type_count=res_group.get('__count',0)
                result[cid]['nbr_%s'%slide_type]=slide_type_count
                result[cid]['total_slides']+=slide_type_count
        returnresult

    def_compute_rating_stats(self):
        super(Channel,self)._compute_rating_stats()
        forrecordinself:
            record.rating_avg_stars=record.rating_avg

    @api.depends('slide_partner_ids','total_slides')
    @api.depends_context('uid')
    def_compute_user_statistics(self):
        current_user_info=self.env['slide.channel.partner'].sudo().search(
            [('channel_id','in',self.ids),('partner_id','=',self.env.user.partner_id.id)]
        )
        mapped_data=dict((info.channel_id.id,(info.completed,info.completed_slides_count))forinfoincurrent_user_info)
        forrecordinself:
            completed,completed_slides_count=mapped_data.get(record.id,(False,0))
            record.completed=completed
            record.completion=100.0ifcompletedelseround(100.0*completed_slides_count/(record.total_slidesor1))

    @api.depends('upload_group_ids','user_id')
    @api.depends_context('uid')
    def_compute_can_upload(self):
        forrecordinself:
            ifrecord.user_id==self.env.userorself.env.is_superuser():
                record.can_upload=True
            elifrecord.upload_group_ids:
                record.can_upload=bool(record.upload_group_ids&self.env.user.groups_id)
            else:
                record.can_upload=self.env.user.has_group('website_slides.group_website_slides_manager')

    @api.depends('channel_type','user_id','can_upload')
    @api.depends_context('uid')
    def_compute_can_publish(self):
        """Forchannelsoftype'training',onlytheresponsible(seeuser_idfield)canpublishslides.
        The'sudo'userneedstobehandledbecausehe'stheoneusedforuploadsdoneonthefront-endwhenthe
        loggedinuserisnotpublisherbutfulfillstheupload_group_idscondition."""
        forrecordinself:
            ifnotrecord.can_upload:
                record.can_publish=False
            elifrecord.user_id==self.env.userorself.env.is_superuser():
                record.can_publish=True
            else:
                record.can_publish=self.env.user.has_group('website_slides.group_website_slides_manager')

    @api.model
    def_get_can_publish_error_message(self):
        return_("Publishingisrestrictedtotheresponsibleoftrainingcoursesormembersofthepublishergroupfordocumentationcourses")

    @api.depends('slide_partner_ids')
    @api.depends_context('uid')
    def_compute_partner_has_new_content(self):
        new_published_slides=self.env['slide.slide'].sudo().search([
            ('is_published','=',True),
            ('date_published','>',fields.Datetime.now()-relativedelta(days=7)),
            ('channel_id','in',self.ids),
            ('is_category','=',False)
        ])
        slide_partner_completed=self.env['slide.slide.partner'].sudo().search([
            ('channel_id','in',self.ids),
            ('partner_id','=',self.env.user.partner_id.id),
            ('slide_id','in',new_published_slides.ids),
            ('completed','=',True)
        ]).mapped('slide_id')
        forchannelinself:
            new_slides=new_published_slides.filtered(lambdaslide:slide.channel_id==channel)
            channel.partner_has_new_content=any(slidenotinslide_partner_completedforslideinnew_slides)

    @api.depends('name','website_id.domain')
    def_compute_website_url(self):
        super(Channel,self)._compute_website_url()
        forchannelinself:
            ifchannel.id: #avoidtoperformaslugonanotyetsavedrecordincaseofanonchange.
                base_url=channel.get_base_url()
                channel.website_url='%s/slides/%s'%(base_url,slug(channel))

    @api.depends('can_publish','is_member','karma_review','karma_slide_comment','karma_slide_vote')
    @api.depends_context('uid')
    def_compute_action_rights(self):
        user_karma=self.env.user.karma
        forchannelinself:
            ifchannel.can_publish:
                channel.can_vote=channel.can_comment=channel.can_review=True
            elifnotchannel.is_member:
                channel.can_vote=channel.can_comment=channel.can_review=False
            else:
                channel.can_review=user_karma>=channel.karma_review
                channel.can_comment=user_karma>=channel.karma_slide_comment
                channel.can_vote=user_karma>=channel.karma_slide_vote

    #---------------------------------------------------------
    #ORMOverrides
    #---------------------------------------------------------

    def_init_column(self,column_name):
        """Initializethevalueofthegivencolumnforexistingrows.
            Overriddenherebecauseweneedtogeneratedifferentaccesstokens
            andbydefault_init_columncallsthedefaultmethodonceandapplies
            itforeveryrecord.
        """
        ifcolumn_name!='access_token':
            super(Channel,self)._init_column(column_name)
        else:
            query="""
                UPDATE%(table_name)s
                SETaccess_token=md5(md5(random()::varchar||id::varchar)||clock_timestamp()::varchar)::uuid::varchar
                WHEREaccess_tokenISNULL
            """%{'table_name':self._table}
            self.env.cr.execute(query)

    @api.model
    defcreate(self,vals):
        #Ensurecreatorismemberofitschannelitiseasierforhimtomanageit(unlessitisflectrabot)
        ifnotvals.get('channel_partner_ids')andnotself.env.is_superuser():
            vals['channel_partner_ids']=[(0,0,{
                'partner_id':self.env.user.partner_id.id
            })]
        ifvals.get('description')andnotvals.get('description_short'):
            vals['description_short']=vals['description']
        channel=super(Channel,self.with_context(mail_create_nosubscribe=True)).create(vals)

        ifchannel.user_id:
            channel._action_add_members(channel.user_id.partner_id)
        if'enroll_group_ids'invals:
            channel._add_groups_members()

        returnchannel

    defwrite(self,vals):
        #Ifdescription_shortwasn'tmanuallymodified,thereisanimplicitlinkbetweenthisfieldanddescription.
        ifvals.get('description')andnotvals.get('description_short')andself.description==self.description_short:
            vals['description_short']=vals.get('description')

        res=super(Channel,self).write(vals)

        ifvals.get('user_id'):
            self._action_add_members(self.env['res.users'].sudo().browse(vals['user_id']).partner_id)
            self.activity_reschedule(['website_slides.mail_activity_data_access_request'],new_user_id=vals.get('user_id'))
        if'enroll_group_ids'invals:
            self._add_groups_members()

        returnres

    deftoggle_active(self):
        """Archiving/unarchivingachanneldoesitonitsslides,too.
        1.Whenarchiving
        WewanttobearchivingthechannelFIRST.
        Sothatwhenslidesarearchivedandtherecomputeistriggered,
        itdoesnottrytomarkthechannelas"completed".
        Thathappensbecauseitcountsslide_done/slide_total,butslide_total
        willbe0sincealltheslidesforthecoursehavebeenarchivedaswell.

        2.Whenun-archiving
        WewanttoarchivethechannelLAST.
        Sothatwhenitrecomputesstatsforthechannelandcompletion,itcorrectly
        countstheslides_totalbycountingslidesthatarealreadyun-archived."""

        to_archive=self.filtered(lambdachannel:channel.active)
        to_activate=self.filtered(lambdachannel:notchannel.active)
        ifto_archive:
            super(Channel,to_archive).toggle_active()
            to_archive.is_published=False
            to_archive.mapped('slide_ids').action_archive()
        ifto_activate:
            to_activate.with_context(active_test=False).mapped('slide_ids').action_unarchive()
            super(Channel,to_activate).toggle_active()

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,*,parent_id=False,subtype_id=False,**kwargs):
        """Temporaryworkaroundtoavoidspam.Ifsomeonerepliesonachannel
        throughthe'PresentationPublished'email,itshouldbeconsideredasa
        noteaswedon'twantallchannelfollowerstobenotifiedofthisanswer."""
        self.ensure_one()
        ifkwargs.get('message_type')=='comment'andnotself.can_review:
            raiseAccessError(_('Notenoughkarmatoreview'))
        ifparent_id:
            parent_message=self.env['mail.message'].sudo().browse(parent_id)
            ifparent_message.subtype_idandparent_message.subtype_id==self.env.ref('website_slides.mt_channel_slide_published'):
                subtype_id=self.env.ref('mail.mt_note').id
        returnsuper(Channel,self).message_post(parent_id=parent_id,subtype_id=subtype_id,**kwargs)

    #---------------------------------------------------------
    #Business/Actions
    #---------------------------------------------------------

    defaction_redirect_to_members(self,state=None):
        action=self.env["ir.actions.actions"]._for_xml_id("website_slides.slide_channel_partner_action")
        action['domain']=[('channel_id','in',self.ids)]
        iflen(self)==1:
            action['display_name']=_('Attendeesof%s',self.name)
            action['context']={'active_test':False,'default_channel_id':self.id}
        ifstate:
            action['domain']+=[('completed','=',state=='completed')]
        returnaction

    defaction_redirect_to_running_members(self):
        returnself.action_redirect_to_members('running')

    defaction_redirect_to_done_members(self):
        returnself.action_redirect_to_members('completed')

    defaction_channel_invite(self):
        self.ensure_one()
        template=self.env.ref('website_slides.mail_template_slide_channel_invite',raise_if_not_found=False)

        local_context=dict(
            self.env.context,
            default_channel_id=self.id,
            default_use_template=bool(template),
            default_template_id=templateandtemplate.idorFalse,
            notif_layout='website_slides.mail_notification_channel_invite',
        )
        return{
            'type':'ir.actions.act_window',
            'view_mode':'form',
            'res_model':'slide.channel.invite',
            'target':'new',
            'context':local_context,
        }

    defaction_add_member(self,**member_values):
        """Addstheloggedinuserinthechannelmembers.
        (see'_action_add_members'formoreinfo)

        ReturnsTrueifaddedsuccessfully,Falseotherwise."""
        returnbool(self._action_add_members(self.env.user.partner_id,**member_values))

    def_action_add_members(self,target_partners,**member_values):
        """Addthetarget_partnerasamemberofthechannel(toitsslide.channel.partner).
        Thiswillmakethecontent(slides)ofthechannelavailabletothatpartner.

        Returnstheadded'slide.channel.partner's(!assudo!)
        """
        to_join=self._filter_add_members(target_partners,**member_values)
        ifto_join:
            existing=self.env['slide.channel.partner'].sudo().search([
                ('channel_id','in',self.ids),
                ('partner_id','in',target_partners.ids)
            ])
            existing_map=dict((cid,list())forcidinself.ids)
            foriteminexisting:
                existing_map[item.channel_id.id].append(item.partner_id.id)

            to_create_values=[
                dict(channel_id=channel.id,partner_id=partner.id,**member_values)
                forchannelinto_join
                forpartnerintarget_partnersifpartner.idnotinexisting_map[channel.id]
            ]
            slide_partners_sudo=self.env['slide.channel.partner'].sudo().create(to_create_values)
            to_join.message_subscribe(partner_ids=target_partners.ids,subtype_ids=[self.env.ref('website_slides.mt_channel_slide_published').id])
            returnslide_partners_sudo
        returnself.env['slide.channel.partner'].sudo()

    def_filter_add_members(self,target_partners,**member_values):
        allowed=self.filtered(lambdachannel:channel.enroll=='public')
        on_invite=self.filtered(lambdachannel:channel.enroll=='invite')
        ifon_invite:
            try:
                on_invite.check_access_rights('write')
                on_invite.check_access_rule('write')
            except:
                pass
            else:
                allowed|=on_invite
        returnallowed

    def_add_groups_members(self):
        forchannelinself:
            channel._action_add_members(channel.mapped('enroll_group_ids.users.partner_id'))

    def_get_earned_karma(self,partner_ids):
        """Computethenumberofkarmaearnedbypartnersonachannel
        Warning:thiscountwillnotbeaccurateiftheconfigurationhasbeen
        modifiedafterthecompletionofacourse!
        """
        total_karma=defaultdict(int)

        slide_completed=self.env['slide.slide.partner'].sudo().search([
            ('partner_id','in',partner_ids),
            ('channel_id','in',self.ids),
            ('completed','=',True),
            ('quiz_attempts_count','>',0)
        ])
        forpartner_slideinslide_completed:
            slide=partner_slide.slide_id
            ifnotslide.question_ids:
                continue
            gains=[slide.quiz_first_attempt_reward,
                     slide.quiz_second_attempt_reward,
                     slide.quiz_third_attempt_reward,
                     slide.quiz_fourth_attempt_reward]
            attempts=min(partner_slide.quiz_attempts_count-1,3)
            total_karma[partner_slide.partner_id.id]+=gains[attempts]

        channel_completed=self.env['slide.channel.partner'].sudo().search([
            ('partner_id','in',partner_ids),
            ('channel_id','in',self.ids),
            ('completed','=',True)
        ])
        forpartner_channelinchannel_completed:
            channel=partner_channel.channel_id
            total_karma[partner_channel.partner_id.id]+=channel.karma_gen_channel_finish

        returntotal_karma

    def_remove_membership(self,partner_ids):
        """Unlink(!!!)therelationshipsbetweenthepassedpartner_ids
        andthechannelsandtheirslides(doneintheunlinkofslide.channel.partnermodel).
        Removeearnedkarmawhencompletedquizz"""
        ifnotpartner_ids:
            raiseValueError("Donotusethismethodwithanemptypartner_idrecordset")

        earned_karma=self._get_earned_karma(partner_ids)
        users=self.env['res.users'].sudo().search([
            ('partner_id','in',list(earned_karma)),
        ])
        foruserinusers:
            ifearned_karma[user.partner_id.id]:
                user.add_karma(-1*earned_karma[user.partner_id.id])

        removed_channel_partner_domain=[]
        forchannelinself:
            removed_channel_partner_domain=expression.OR([
                removed_channel_partner_domain,
                [('partner_id','in',partner_ids),
                 ('channel_id','=',channel.id)]
            ])
        self.message_unsubscribe(partner_ids=partner_ids)

        ifremoved_channel_partner_domain:
            self.env['slide.channel.partner'].sudo().search(removed_channel_partner_domain).unlink()

    defaction_view_slides(self):
        action=self.env["ir.actions.actions"]._for_xml_id("website_slides.slide_slide_action")
        action['context']={
            'search_default_published':1,
            'default_channel_id':self.id
        }
        action['domain']=[('channel_id',"=",self.id),('is_category','=',False)]
        returnaction

    defaction_view_ratings(self):
        action=self.env["ir.actions.actions"]._for_xml_id("website_slides.rating_rating_action_slide_channel")
        action['name']=_('Ratingof%s')%(self.name)
        action['domain']=expression.AND([ast.literal_eval(action.get('domain','[]')),[('res_id','in',self.ids)]])
        returnaction

    defaction_request_access(self):
        """Requestaccesstothechannel.Returnsadictwithkeysbeingeither'error'
        (specificerrorraised)or'done'(requestdoneornot)."""
        ifself.env.user.has_group('base.group_public'):
            return{'error':_('Youhavetosigninbefore')}
        ifnotself.is_published:
            return{'error':_('Coursenotpublishedyet')}
        ifself.is_member:
            return{'error':_('Alreadymember')}
        ifself.enroll=='invite':
            activities=self.sudo()._action_request_access(self.env.user.partner_id)
            ifactivities:
                return{'done':True}
            return{'error':_('AlreadyRequested')}
        return{'done':False}

    defaction_grant_access(self,partner_id):
        partner=self.env['res.partner'].browse(partner_id).exists()
        ifpartner:
            ifself._action_add_members(partner):
                self.activity_search(
                    ['website_slides.mail_activity_data_access_request'],
                    user_id=self.user_id.id,additional_domain=[('request_partner_id','=',partner.id)]
                ).action_feedback(feedback=_('AccessGranted'))

    defaction_refuse_access(self,partner_id):
        partner=self.env['res.partner'].browse(partner_id).exists()
        ifpartner:
            self.activity_search(
                ['website_slides.mail_activity_data_access_request'],
                user_id=self.user_id.id,additional_domain=[('request_partner_id','=',partner.id)]
            ).action_feedback(feedback=_('AccessRefused'))

    #---------------------------------------------------------
    #MailingMixinAPI
    #---------------------------------------------------------

    def_rating_domain(self):
        """Onlytakethepublishedratingintoaccounttocomputeavgandcount"""
        domain=super(Channel,self)._rating_domain()
        returnexpression.AND([domain,[('is_internal','=',False)]])

    def_action_request_access(self,partner):
        activities=self.env['mail.activity']
        requested_cids=self.sudo().activity_search(
            ['website_slides.mail_activity_data_access_request'],
            additional_domain=[('request_partner_id','=',partner.id)]
        ).mapped('res_id')
        forchannelinself:
            ifchannel.idnotinrequested_cids:
                activities+=channel.activity_schedule(
                    'website_slides.mail_activity_data_access_request',
                    note=_('<b>%s</b>isrequestingaccesstothiscourse.')%partner.name,
                    user_id=channel.user_id.id,
                    request_partner_id=partner.id
                )
        returnactivities

    #---------------------------------------------------------
    #Data/Misc
    #---------------------------------------------------------

    def_get_categorized_slides(self,base_domain,order,force_void=True,limit=False,offset=False):
        """Returnanorderedstructureofslidesbycategorieswithinagiven
        base_domainthatmustfulfillslides.Asacoursestructureisbasedon
        itsslidessequences,uncategorizedslidesmusthavethelowestsequences.

        Example
          *category1(sequence1),category2(sequence3)
          *slide1(sequence0),slide2(sequence2)
          *coursestructureis:slide1,category1,slide2,category2
            *slide1isuncategorized,
            *category1hasoneslide:Slide2
            *category2isempty.

        Backendandfrontendorderingisthesame,uncategorizedfirst.It
        easesresequencingbasedonDOM/displayedorder,notablywhen
        dragndropisinvolved."""
        self.ensure_one()
        all_categories=self.env['slide.slide'].sudo().search([('channel_id','=',self.id),('is_category','=',True)])
        all_slides=self.env['slide.slide'].sudo().search(base_domain,order=order)
        category_data=[]

        #Prepareallcategoriesbynaturalorder
        forcategoryinall_categories:
            category_slides=all_slides.filtered(lambdaslide:slide.category_id==category)
            ifnotcategory_slidesandnotforce_void:
                continue
            category_data.append({
                'category':category,'id':category.id,
                'name':category.name,'slug_name':slug(category),
                'total_slides':len(category_slides),
                'slides':category_slides[(offsetor0):(limit+offsetorlen(category_slides))],
            })

        #Adduncategorizedslidesinfirstposition
        uncategorized_slides=all_slides.filtered(lambdaslide:notslide.category_id)
        ifuncategorized_slidesorforce_void:
            category_data.insert(0,{
                'category':False,'id':False,
                'name':_('Uncategorized'),'slug_name':_('Uncategorized'),
                'total_slides':len(uncategorized_slides),
                'slides':uncategorized_slides[(offsetor0):(offset+limitorlen(uncategorized_slides))],
            })

        returncategory_data

    def_move_category_slides(self,category,new_category):
        ifnotcategory.slide_ids:
            return
        truncated_slide_ids=[slide_idforslide_idinself.slide_ids.idsifslide_idnotincategory.slide_ids.ids]
        ifnew_category:
            place_idx=truncated_slide_ids.index(new_category.id)
            ordered_slide_ids=truncated_slide_ids[:place_idx]+category.slide_ids.ids+truncated_slide_ids[place_idx]
        else:
            ordered_slide_ids=category.slide_ids.ids+truncated_slide_ids
        forindex,slide_idinenumerate(ordered_slide_ids):
            self.env['slide.slide'].browse([slide_id]).sequence=index+1

    def_resequence_slides(self,slide,force_category=False):
        ids_to_resequence=self.slide_ids.ids
        index_of_added_slide=ids_to_resequence.index(slide.id)
        next_category_id=None
        ifself.slide_category_ids:
            force_category_id=force_category.idifforce_categoryelseslide.category_id.id
            index_of_category=self.slide_category_ids.ids.index(force_category_id)ifforce_category_idelseNone
            ifindex_of_categoryisNone:
                next_category_id=self.slide_category_ids.ids[0]
            elifindex_of_category<len(self.slide_category_ids.ids)-1:
                next_category_id=self.slide_category_ids.ids[index_of_category+1]

        ifnext_category_id:
            added_slide_id=ids_to_resequence.pop(index_of_added_slide)
            index_of_next_category=ids_to_resequence.index(next_category_id)
            ids_to_resequence.insert(index_of_next_category,added_slide_id)
            fori,recordinenumerate(self.env['slide.slide'].browse(ids_to_resequence)):
                record.write({'sequence':i+1}) #startat1tomakepeoplescream
        else:
            slide.write({
                'sequence':self.env['slide.slide'].browse(ids_to_resequence[-1]).sequence+1
            })

    defget_backend_menu_id(self):
        returnself.env.ref('website_slides.website_slides_menu_root').id
