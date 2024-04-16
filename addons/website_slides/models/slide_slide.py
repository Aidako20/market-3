#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importdatetime
importio
importre
importrequests
importPyPDF2
importjson

fromdateutil.relativedeltaimportrelativedelta
fromPILimportImage
fromwerkzeugimporturls

fromflectraimportapi,fields,models,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.exceptionsimportUserError,AccessError
fromflectra.httpimportrequest
fromflectra.addons.http_routing.models.ir_httpimporturl_for
fromflectra.toolsimportsql


classSlidePartnerRelation(models.Model):
    _name='slide.slide.partner'
    _description='Slide/Partnerdecoratedm2m'
    _table='slide_slide_partner'

    slide_id=fields.Many2one('slide.slide',ondelete="cascade",index=True,required=True)
    channel_id=fields.Many2one(
        'slide.channel',string="Channel",
        related="slide_id.channel_id",store=True,index=True,ondelete='cascade')
    partner_id=fields.Many2one('res.partner',index=True,required=True,ondelete='cascade')
    vote=fields.Integer('Vote',default=0)
    completed=fields.Boolean('Completed')
    quiz_attempts_count=fields.Integer('Quizattemptscount',default=0)

    defcreate(self,values):
        res=super(SlidePartnerRelation,self).create(values)
        completed=res.filtered('completed')
        ifcompleted:
            completed._set_completed_callback()
        returnres

    defwrite(self,values):
        res=super(SlidePartnerRelation,self).write(values)
        ifvalues.get('completed'):
            self._set_completed_callback()
        returnres

    def_set_completed_callback(self):
        self.env['slide.channel.partner'].search([
            ('channel_id','in',self.channel_id.ids),
            ('partner_id','in',self.partner_id.ids),
        ])._recompute_completion()


classSlideLink(models.Model):
    _name='slide.slide.link'
    _description="ExternalURLforaparticularslide"

    slide_id=fields.Many2one('slide.slide',required=True,ondelete='cascade')
    name=fields.Char('Title',required=True)
    link=fields.Char('Link',required=True)


classSlideResource(models.Model):
    _name='slide.slide.resource'
    _description="Additionalresourceforaparticularslide"

    slide_id=fields.Many2one('slide.slide',required=True,ondelete='cascade')
    name=fields.Char('Name',required=True)
    data=fields.Binary('Resource')


classEmbeddedSlide(models.Model):
    """Embeddinginthirdpartywebsites.Trackviewcount,generatestatistics."""
    _name='slide.embed'
    _description='EmbeddedSlidesViewCounter'
    _rec_name='slide_id'

    slide_id=fields.Many2one('slide.slide',string="Presentation",required=True,index=True)
    url=fields.Char('ThirdPartyWebsiteURL',required=True)
    count_views=fields.Integer('#Views',default=1)

    def_add_embed_url(self,slide_id,url):
        baseurl=urls.url_parse(url).netloc
        ifnotbaseurl:
            return0
        embeds=self.search([('url','=',baseurl),('slide_id','=',int(slide_id))],limit=1)
        ifembeds:
            embeds.count_views+=1
        else:
            embeds=self.create({
                'slide_id':slide_id,
                'url':baseurl,
            })
        returnembeds.count_views


classSlideTag(models.Model):
    """Tagtosearchslidesaccrosschannels."""
    _name='slide.tag'
    _description='SlideTag'

    name=fields.Char('Name',required=True,translate=True)

    _sql_constraints=[
        ('slide_tag_unique','UNIQUE(name)','Atagmustbeunique!'),
    ]


classSlide(models.Model):
    _name='slide.slide'
    _inherit=[
        'mail.thread',
        'image.mixin',
        'website.seo.metadata','website.published.mixin']
    _description='Slides'
    _mail_post_access='read'
    _order_by_strategy={
        'sequence':'sequenceasc,idasc',
        'most_viewed':'total_viewsdesc',
        'most_voted':'likesdesc',
        'latest':'date_publisheddesc',
    }
    _order='sequenceasc,is_categoryasc,idasc'

    #description
    name=fields.Char('Title',required=True,translate=True)
    active=fields.Boolean(default=True,tracking=100)
    sequence=fields.Integer('Sequence',default=0)
    user_id=fields.Many2one('res.users',string='Uploadedby',default=lambdaself:self.env.uid)
    description=fields.Text('Description',translate=True)
    channel_id=fields.Many2one('slide.channel',string="Course",required=True)
    tag_ids=fields.Many2many('slide.tag','rel_slide_tag','slide_id','tag_id',string='Tags')
    is_preview=fields.Boolean('AllowPreview',default=False,help="Thecourseisaccessiblebyanyone:theusersdon'tneedtojointhechanneltoaccessthecontentofthecourse.")
    is_new_slide=fields.Boolean('IsNewSlide',compute='_compute_is_new_slide')
    completion_time=fields.Float('Duration',digits=(10,4),help="Theestimatedcompletiontimeforthisslide")
    #Categories
    is_category=fields.Boolean('Isacategory',default=False)
    category_id=fields.Many2one('slide.slide',string="Section",compute="_compute_category_id",store=True)
    slide_ids=fields.One2many('slide.slide',"category_id",string="Slides")
    #subscribers
    partner_ids=fields.Many2many('res.partner','slide_slide_partner','slide_id','partner_id',
                                   string='Subscribers',groups='website_slides.group_website_slides_officer',copy=False)
    slide_partner_ids=fields.One2many('slide.slide.partner','slide_id',string='Subscribersinformation',groups='website_slides.group_website_slides_officer',copy=False)
    user_membership_id=fields.Many2one(
        'slide.slide.partner',string="Subscriberinformation",
        compute='_compute_user_membership_id',compute_sudo=False,
        help="Subscriberinformationforthecurrentloggedinuser")
    #Quizrelatedfields
    question_ids=fields.One2many("slide.question","slide_id",string="Questions")
    questions_count=fields.Integer(string="NumbersofQuestions",compute='_compute_questions_count')
    quiz_first_attempt_reward=fields.Integer("Reward:firstattempt",default=10)
    quiz_second_attempt_reward=fields.Integer("Reward:secondattempt",default=7)
    quiz_third_attempt_reward=fields.Integer("Reward:thirdattempt",default=5,)
    quiz_fourth_attempt_reward=fields.Integer("Reward:everyattemptafterthethirdtry",default=2)
    #content
    slide_type=fields.Selection([
        ('infographic','Infographic'),
        ('webpage','WebPage'),
        ('presentation','Presentation'),
        ('document','Document'),
        ('video','Video'),
        ('quiz',"Quiz")],
        string='Type',required=True,
        default='document',
        help="ThedocumenttypewillbesetautomaticallybasedonthedocumentURLandproperties(e.g.heightandwidthforpresentationanddocument).")
    datas=fields.Binary('Content',attachment=True)
    url=fields.Char('DocumentURL',help="YoutubeorGoogleDocumentURL")
    document_id=fields.Char('DocumentID',help="YoutubeorGoogleDocumentID")
    link_ids=fields.One2many('slide.slide.link','slide_id',string="ExternalURLforthisslide")
    slide_resource_ids=fields.One2many('slide.slide.resource','slide_id',string="AdditionalResourceforthisslide")
    slide_resource_downloadable=fields.Boolean('AllowDownload',default=True,help="Allowtheusertodownloadthecontentoftheslide.")
    mime_type=fields.Char('Mime-type')
    html_content=fields.Html("HTMLContent",help="CustomHTMLcontentforslidesoftype'WebPage'.",translate=True,sanitize_attributes=False,sanitize_form=False)
    #website
    website_id=fields.Many2one(related='channel_id.website_id',readonly=True)
    date_published=fields.Datetime('PublishDate',readonly=True,tracking=1)
    likes=fields.Integer('Likes',compute='_compute_like_info',store=True,compute_sudo=False)
    dislikes=fields.Integer('Dislikes',compute='_compute_like_info',store=True,compute_sudo=False)
    user_vote=fields.Integer('Uservote',compute='_compute_user_membership_id',compute_sudo=False)
    embed_code=fields.Text('EmbedCode',readonly=True,compute='_compute_embed_code')
    #views
    embedcount_ids=fields.One2many('slide.embed','slide_id',string="EmbedCount")
    slide_views=fields.Integer('#ofWebsiteViews',store=True,compute="_compute_slide_views")
    public_views=fields.Integer('#ofPublicViews',copy=False)
    total_views=fields.Integer("Views",default="0",compute='_compute_total',store=True)
    #comments
    comments_count=fields.Integer('Numberofcomments',compute="_compute_comments_count")
    #channel
    channel_type=fields.Selection(related="channel_id.channel_type",string="Channeltype")
    channel_allow_comment=fields.Boolean(related="channel_id.allow_comment",string="Allowscomment")
    #Statisticsincasetheslideisacategory
    nbr_presentation=fields.Integer("NumberofPresentations",compute='_compute_slides_statistics',store=True)
    nbr_document=fields.Integer("NumberofDocuments",compute='_compute_slides_statistics',store=True)
    nbr_video=fields.Integer("NumberofVideos",compute='_compute_slides_statistics',store=True)
    nbr_infographic=fields.Integer("NumberofInfographics",compute='_compute_slides_statistics',store=True)
    nbr_webpage=fields.Integer("NumberofWebpages",compute='_compute_slides_statistics',store=True)
    nbr_quiz=fields.Integer("NumberofQuizs",compute="_compute_slides_statistics",store=True)
    total_slides=fields.Integer(compute='_compute_slides_statistics',store=True)

    _sql_constraints=[
        ('exclusion_html_content_and_url',"CHECK(html_contentISNULLORurlISNULL)","AslideiseitherfilledwithadocumenturlorHTMLcontent.Notboth.")
    ]

    @api.depends('date_published','is_published')
    def_compute_is_new_slide(self):
        forslideinself:
            slide.is_new_slide=slide.date_published>fields.Datetime.now()-relativedelta(days=7)ifslide.is_publishedelseFalse

    @api.depends('channel_id.slide_ids.is_category','channel_id.slide_ids.sequence')
    def_compute_category_id(self):
        """Willtakealltheslidesofthechannelforwhichtheindexishigher
        thantheindexofthiscategoryandlowerthantheindexofthenextcategory.

        Listsaremanuallysortedbecausewhenaddinganewbrowserecordorder
        willnotbecorrectastheaddedslidewouldactuallyendupatthe
        firstplacenomatteritssequence."""
        self.category_id=False #initializewhateverthestate

        channel_slides={}
        forslideinself:
            ifslide.channel_id.idnotinchannel_slides:
                channel_slides[slide.channel_id.id]=slide.channel_id.slide_ids

        forcid,slidesinchannel_slides.items():
            current_category=self.env['slide.slide']
            slide_list=list(slides)
            slide_list.sort(key=lambdas:(s.sequence,nots.is_category))
            forslideinslide_list:
                ifslide.is_category:
                    current_category=slide
                elifslide.category_id!=current_category:
                    slide.category_id=current_category.id

    @api.depends('question_ids')
    def_compute_questions_count(self):
        forslideinself:
            slide.questions_count=len(slide.question_ids)

    def_has_additional_resources(self):
        """Sudorequiredforpublicusertoknowifthecoursehasadditional
        resourcesthattheywillbeabletoaccessonceamember."""
        self.ensure_one()
        returnbool(self.sudo().slide_resource_ids)

    @api.depends('website_message_ids.res_id','website_message_ids.model','website_message_ids.message_type')
    def_compute_comments_count(self):
        forslideinself:
            slide.comments_count=len(slide.website_message_ids)

    @api.depends('slide_views','public_views')
    def_compute_total(self):
        forrecordinself:
            record.total_views=record.slide_views+record.public_views

    @api.depends('slide_partner_ids.vote')
    def_compute_like_info(self):
        ifnotself.ids:
            self.update({'likes':0,'dislikes':0})
            return

        rg_data_like=self.env['slide.slide.partner'].sudo().read_group(
            [('slide_id','in',self.ids),('vote','=',1)],
            ['slide_id'],['slide_id']
        )
        rg_data_dislike=self.env['slide.slide.partner'].sudo().read_group(
            [('slide_id','in',self.ids),('vote','=',-1)],
            ['slide_id'],['slide_id']
        )
        mapped_data_like=dict(
            (rg_data['slide_id'][0],rg_data['slide_id_count'])
            forrg_datainrg_data_like
        )
        mapped_data_dislike=dict(
            (rg_data['slide_id'][0],rg_data['slide_id_count'])
            forrg_datainrg_data_dislike
        )

        forslideinself:
            slide.likes=mapped_data_like.get(slide.id,0)
            slide.dislikes=mapped_data_dislike.get(slide.id,0)

    @api.depends('slide_partner_ids.vote')
    @api.depends_context('uid')
    def_compute_user_info(self):
        """Deprecated.Nowcomputeddirectlyby_compute_user_membership_id
        foruser_voteand_compute_like_infoforlikes/dislikes.Removemein
        master."""
        default_stats={'likes':0,'dislikes':0,'user_vote':False}

        ifnotself.ids:
            self.update(default_stats)
            return

        slide_data=dict.fromkeys(self.ids,default_stats)
        slide_partners=self.env['slide.slide.partner'].sudo().search([
            ('slide_id','in',self.ids)
        ])

        forslide_partnerinslide_partners:
            ifslide_partner.vote==1:
                slide_data[slide_partner.slide_id.id]['likes']+=1
                ifslide_partner.partner_id==self.env.user.partner_id:
                    slide_data[slide_partner.slide_id.id]['user_vote']=1
            elifslide_partner.vote==-1:
                slide_data[slide_partner.slide_id.id]['dislikes']+=1
                ifslide_partner.partner_id==self.env.user.partner_id:
                    slide_data[slide_partner.slide_id.id]['user_vote']=-1

        forslideinself:
            slide.update(slide_data[slide.id])

    @api.depends('slide_partner_ids.slide_id')
    def_compute_slide_views(self):
        #TODOawa:triedcompute_sudo,forsomereasonitdoesn'tworkinhere...
        read_group_res=self.env['slide.slide.partner'].sudo().read_group(
            [('slide_id','in',self.ids)],
            ['slide_id'],
            groupby=['slide_id']
        )
        mapped_data=dict((res['slide_id'][0],res['slide_id_count'])forresinread_group_res)
        forslideinself:
            slide.slide_views=mapped_data.get(slide.id,0)

    @api.depends('slide_ids.sequence','slide_ids.slide_type','slide_ids.is_published','slide_ids.is_category')
    def_compute_slides_statistics(self):
        #Donotusedict.fromkeys(self.ids,dict())otherwiseitwillusethesamedictionnaryforallkeys.
        #Therefore,whenupdatingthedictofonekey,itupdatesthedictofallkeys.
        keys=['nbr_%s'%slide_typeforslide_typeinself.env['slide.slide']._fields['slide_type'].get_values(self.env)]
        default_vals=dict((key,0)forkeyinkeys+['total_slides'])

        res=self.env['slide.slide'].read_group(
            [('is_published','=',True),('category_id','in',self.ids),('is_category','=',False)],
            ['category_id','slide_type'],['category_id','slide_type'],
            lazy=False)

        type_stats=self._compute_slides_statistics_type(res)

        forrecordinself:
            record.update(type_stats.get(record._origin.id,default_vals))

    def_compute_slides_statistics_type(self,read_group_res):
        """Computestatisticsbasedonallexistingslidetypes"""
        slide_types=self.env['slide.slide']._fields['slide_type'].get_values(self.env)
        keys=['nbr_%s'%slide_typeforslide_typeinslide_types]
        result=dict((cid,dict((key,0)forkeyinkeys+['total_slides']))forcidinself.ids)
        forres_groupinread_group_res:
            cid=res_group['category_id'][0]
            slide_type=res_group.get('slide_type')
            ifslide_type:
                slide_type_count=res_group.get('__count',0)
                result[cid]['nbr_%s'%slide_type]=slide_type_count
                result[cid]['total_slides']+=slide_type_count
        returnresult

    @api.depends('slide_partner_ids.partner_id','slide_partner_ids.vote')
    @api.depends('uid')
    def_compute_user_membership_id(self):
        slide_partners=self.env['slide.slide.partner'].sudo().search([
            ('slide_id','in',self.ids),
            ('partner_id','=',self.env.user.partner_id.id),
        ])

        forrecordinself:
            record.user_membership_id=next(
                (slide_partnerforslide_partnerinslide_partnersifslide_partner.slide_id==record),
                self.env['slide.slide.partner']
            )
            record.user_vote=record.user_membership_id.vote

    @api.depends('document_id','slide_type','mime_type')
    def_compute_embed_code(self):
        base_url=requestandrequest.httprequest.url_rootorself.env['ir.config_parameter'].sudo().get_param('web.base.url')
        ifbase_url[-1]=='/':
            base_url=base_url[:-1]
        forrecordinself:
            ifrecord.datasand(notrecord.document_idorrecord.slide_typein['document','presentation']):
                slide_url=base_url+url_for('/slides/embed/%s?page=1'%record.id)
                record.embed_code='<iframesrc="%s"class="o_wslides_iframe_viewer"allowFullScreen="true"height="%s"width="%s"frameborder="0"></iframe>'%(slide_url,315,420)
            elifrecord.slide_type=='video'andrecord.document_id:
                ifnotrecord.mime_type:
                    #embedyoutubevideo
                    query=urls.url_parse(record.url).query
                    query=query+'&theme=light'ifqueryelse'theme=light'
                    record.embed_code='<iframesrc="//www.youtube-nocookie.com/embed/%s?%s"allowFullScreen="true"frameborder="0"></iframe>'%(record.document_id,query)
                else:
                    #embedgoogledocvideo
                    record.embed_code='<iframesrc="//drive.google.com/file/d/%s/preview"allowFullScreen="true"frameborder="0"></iframe>'%(record.document_id)
            else:
                record.embed_code=False

    @api.onchange('url')
    def_on_change_url(self):
        self.ensure_one()
        ifself.url:
            res=self._parse_document_url(self.url)
            ifres.get('error'):
                raiseUserError(res.get('error'))
            values=res['values']
            ifnotvalues.get('document_id'):
                raiseUserError(_('PleaseentervalidYoutubeorGoogleDocURL'))
            forkey,valueinvalues.items():
                self[key]=value

    @api.onchange('datas')
    def_on_change_datas(self):
        """ForPDFs,weassumethatittakes5minutestoreadapage.
            IftheselectedfileisnotaPDF,itisanimage(Youcan
            onlyuploadPDForImagefile)thentheslide_typeischanged
            intoinfographicandtheuploadeddataSistransferedtothe
            imagefield.(ItavoidstheinfiniteloadinginPDFviewer)"""
        ifself.datas:
            data=base64.b64decode(self.datas)
            ifdata.startswith(b'%PDF-'):
                pdf=PyPDF2.PdfFileReader(io.BytesIO(data),overwriteWarnings=False,strict=False)
                try:
                    pdf.getNumPages()
                exceptPyPDF2.utils.PdfReadError:
                    return
                self.completion_time=(5*len(pdf.pages))/60
            else:
                self.slide_type='infographic'
                self.image_1920=self.datas
                self.datas=None

    @api.depends('name','channel_id.website_id.domain')
    def_compute_website_url(self):
        #TDEFIXME:clenathislink.trackerstrangestuff
        super(Slide,self)._compute_website_url()
        forslideinself:
            ifslide.id: #avoidtoperformaslugonanotyetsavedrecordincaseofanonchange.
                base_url=slide.channel_id.get_base_url()
                #link_trackerisnotindependencies,souseittoshortenurlonlyifinstalled.
                ifself.env.registry.get('link.tracker'):
                    url=self.env['link.tracker'].sudo().create({
                        'url':'%s/slides/slide/%s'%(base_url,slug(slide)),
                        'title':slide.name,
                    }).short_url
                else:
                    url='%s/slides/slide/%s'%(base_url,slug(slide))
                slide.website_url=url

    @api.depends('channel_id.can_publish')
    def_compute_can_publish(self):
        forrecordinself:
            record.can_publish=record.channel_id.can_publish

    @api.model
    def_get_can_publish_error_message(self):
        return_("Publishingisrestrictedtotheresponsibleoftrainingcoursesormembersofthepublishergroupfordocumentationcourses")

    #---------------------------------------------------------
    #ORMOverrides
    #---------------------------------------------------------

    @api.model
    defcreate(self,values):
        #Donotpublishslideifuserhasnotpublisherrights
        channel=self.env['slide.channel'].browse(values['channel_id'])
        ifnotchannel.can_publish:
            #'website_published'ishandledbymixin
            values['date_published']=False

        ifvalues.get('slide_type')=='infographic'andnotvalues.get('image_1920'):
            values['image_1920']=values['datas']
        ifvalues.get('is_category'):
            values['is_preview']=True
            values['is_published']=True
        ifvalues.get('is_published')andnotvalues.get('date_published'):
            values['date_published']=datetime.datetime.now()
        ifvalues.get('url')andnotvalues.get('document_id'):
            doc_data=self._parse_document_url(values['url']).get('values',dict())
            forkey,valueindoc_data.items():
                values.setdefault(key,value)

        slide=super(Slide,self).create(values)

        ifslide.is_publishedandnotslide.is_category:
            slide._post_publication()
        returnslide

    defwrite(self,values):
        ifvalues.get('url')andvalues['url']!=self.url:
            doc_data=self._parse_document_url(values['url']).get('values',dict())
            forkey,valueindoc_data.items():
                values.setdefault(key,value)
        ifvalues.get('is_category'):
            values['is_preview']=True
            values['is_published']=True

        res=super(Slide,self).write(values)
        ifvalues.get('is_published'):
            self.date_published=datetime.datetime.now()
            self._post_publication()

        if'is_published'invaluesor'active'invalues:
            #iftheslideispublished/unpublished,recomputethecompletionforthepartners
            self.slide_partner_ids._set_completed_callback()

        returnres

    @api.returns('self',lambdavalue:value.id)
    defcopy(self,default=None):
        """Setsthesequencetozerosothatitalwayslandsatthebeginning
        ofthenewlyselectedcourseasanuncategorizedslide"""
        rec=super(Slide,self).copy(default)
        rec.sequence=0
        returnrec

    defunlink(self):
        ifself.question_idsandself.channel_id.channel_partner_ids:
            raiseUserError(_("Peoplealreadytookthisquiz.Tokeepcourseprogressionitshouldnotbedeleted."))
        forcategoryinself.filtered(lambdaslide:slide.is_category):
            category.channel_id._move_category_slides(category,False)
        super(Slide,self).unlink()

    deftoggle_active(self):
        #archiving/unarchivingachanneldoesitonitsslides,too
        to_archive=self.filtered(lambdaslide:slide.active)
        res=super(Slide,self).toggle_active()
        ifto_archive:
            to_archive.filtered(lambdaslide:notslide.is_category).is_published=False
        returnres

    #---------------------------------------------------------
    #Mail/Rating
    #---------------------------------------------------------

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,*,message_type='notification',**kwargs):
        self.ensure_one()
        ifmessage_type=='comment'andnotself.channel_id.can_comment: #usercommentshavearestrictiononkarma
            raiseAccessError(_('Notenoughkarmatocomment'))
        returnsuper(Slide,self).message_post(message_type=message_type,**kwargs)

    defget_access_action(self,access_uid=None):
        """Insteadoftheclassicformview,redirecttowebsiteifitispublished."""
        self.ensure_one()
        ifself.website_published:
            return{
                'type':'ir.actions.act_url',
                'url':'%s'%self.website_url,
                'target':'self',
                'target_type':'public',
                'res_id':self.id,
            }
        returnsuper(Slide,self).get_access_action(access_uid)

    def_notify_get_groups(self,msg_vals=None):
        """Addaccessbuttontoeveryoneifthedocumentisactive."""
        groups=super(Slide,self)._notify_get_groups(msg_vals=msg_vals)

        ifself.website_published:
            forgroup_name,group_method,group_dataingroups:
                group_data['has_button_access']=True

        returngroups

    #---------------------------------------------------------
    #BusinessMethods
    #---------------------------------------------------------

    def_post_publication(self):
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        forslideinself.filtered(lambdaslide:slide.website_publishedandslide.channel_id.publish_template_id):
            publish_template=slide.channel_id.publish_template_id
            html_body=publish_template.with_context(base_url=base_url)._render_field('body_html',slide.ids)[slide.id]
            subject=publish_template._render_field('subject',slide.ids)[slide.id]
            #Wewanttousethe'reply_to'ofthetemplateifset.However,`mail.message`willcheck
            #ifthekey'reply_to'isinthekwargsbeforecalling_get_reply_to.Ifthevalueis
            #falsy,wedon'tincludeitinthe'message_post'call.
            kwargs={}
            reply_to=publish_template._render_field('reply_to',slide.ids)[slide.id]
            ifreply_to:
                kwargs['reply_to']=reply_to
            slide.channel_id.with_context(mail_create_nosubscribe=True).message_post(
                subject=subject,
                body=html_body,
                subtype_xmlid='website_slides.mt_channel_slide_published',
                email_layout_xmlid='mail.mail_notification_light',
                **kwargs,
            )
        returnTrue

    def_generate_signed_token(self,partner_id):
        """Lazygeneratetheacces_tokenandreturnitsignedbythegivenpartner_id
            :rtypetuple(string,int)
            :return(signed_token,partner_id)
        """
        ifnotself.access_token:
            self.write({'access_token':self._default_access_token()})
        returnself._sign_token(partner_id)

    def_send_share_email(self,email,fullscreen):
        #TDEFIXME:templatetocheck
        mail_ids=[]
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        forrecordinself:
            template=record.channel_id.share_template_id.with_context(
                user=self.env.user,
                email=email,
                base_url=base_url,
                fullscreen=fullscreen
            )
            email_values={'email_to':email}
            ifself.env.user.has_group('base.group_portal'):
                template=template.sudo()
                email_values['email_from']=self.env.company.catchall_formattedorself.env.company.email_formatted

            mail_ids.append(template.send_mail(record.id,notif_layout='mail.mail_notification_light',email_values=email_values))
        returnmail_ids

    defaction_like(self):
        self.check_access_rights('read')
        self.check_access_rule('read')
        returnself._action_vote(upvote=True)

    defaction_dislike(self):
        self.check_access_rights('read')
        self.check_access_rule('read')
        returnself._action_vote(upvote=False)

    def_action_vote(self,upvote=True):
        """Privateimplementationofvoting.Itdoesnotcheckforanyrealaccess
        rights;publicmethodsshouldgrantaccessbeforecallingthismethod.

          :paramupvote:ifTrue,isalike;ifFalse,isadislike
        """
        self_sudo=self.sudo()
        SlidePartnerSudo=self.env['slide.slide.partner'].sudo()
        slide_partners=SlidePartnerSudo.search([
            ('slide_id','in',self.ids),
            ('partner_id','=',self.env.user.partner_id.id)
        ])
        slide_id=slide_partners.mapped('slide_id')
        new_slides=self_sudo-slide_id
        channel=slide_id.channel_id
        karma_to_add=0

        forslide_partnerinslide_partners:
            ifupvote:
                new_vote=0ifslide_partner.vote==-1else1
                ifslide_partner.vote!=1:
                    karma_to_add+=channel.karma_gen_slide_vote
            else:
                new_vote=0ifslide_partner.vote==1else-1
                ifslide_partner.vote!=-1:
                    karma_to_add-=channel.karma_gen_slide_vote
            slide_partner.vote=new_vote

        fornew_slideinnew_slides:
            new_vote=1ifupvoteelse-1
            new_slide.write({
                'slide_partner_ids':[(0,0,{'vote':new_vote,'partner_id':self.env.user.partner_id.id})]
            })
            karma_to_add+=new_slide.channel_id.karma_gen_slide_vote*(1ifupvoteelse-1)

        ifkarma_to_add:
            self.env.user.add_karma(karma_to_add)

    defaction_set_viewed(self,quiz_attempts_inc=False):
        ifany(notslide.channel_id.is_memberforslideinself):
            raiseUserError(_('Youcannotmarkaslideasviewedifyouarenotamongitsmembers.'))

        returnbool(self._action_set_viewed(self.env.user.partner_id,quiz_attempts_inc=quiz_attempts_inc))

    def_action_set_viewed(self,target_partner,quiz_attempts_inc=False):
        self_sudo=self.sudo()
        SlidePartnerSudo=self.env['slide.slide.partner'].sudo()
        existing_sudo=SlidePartnerSudo.search([
            ('slide_id','in',self.ids),
            ('partner_id','=',target_partner.id)
        ])
        ifquiz_attempts_incandexisting_sudo:
            sql.increment_field_skiplock(existing_sudo,'quiz_attempts_count')
            SlidePartnerSudo.invalidate_cache(fnames=['quiz_attempts_count'],ids=existing_sudo.ids)

        new_slides=self_sudo-existing_sudo.mapped('slide_id')
        returnSlidePartnerSudo.create([{
            'slide_id':new_slide.id,
            'channel_id':new_slide.channel_id.id,
            'partner_id':target_partner.id,
            'quiz_attempts_count':1ifquiz_attempts_incelse0,
            'vote':0}fornew_slideinnew_slides])

    defaction_set_completed(self):
        ifany(notslide.channel_id.is_memberforslideinself):
            raiseUserError(_('Youcannotmarkaslideascompletedifyouarenotamongitsmembers.'))

        returnself._action_set_completed(self.env.user.partner_id)

    def_action_set_completed(self,target_partner):
        self_sudo=self.sudo()
        SlidePartnerSudo=self.env['slide.slide.partner'].sudo()
        existing_sudo=SlidePartnerSudo.search([
            ('slide_id','in',self.ids),
            ('partner_id','=',target_partner.id)
        ])
        existing_sudo.write({'completed':True})

        new_slides=self_sudo-existing_sudo.mapped('slide_id')
        SlidePartnerSudo.create([{
            'slide_id':new_slide.id,
            'channel_id':new_slide.channel_id.id,
            'partner_id':target_partner.id,
            'vote':0,
            'completed':True}fornew_slideinnew_slides])

        returnTrue

    def_action_set_quiz_done(self):
        ifany(notslide.channel_id.is_memberforslideinself):
            raiseUserError(_('Youcannotmarkaslidequizascompletedifyouarenotamongitsmembers.'))

        points=0
        forslideinself:
            user_membership_sudo=slide.user_membership_id.sudo()
            ifnotuser_membership_sudooruser_membership_sudo.completedornotuser_membership_sudo.quiz_attempts_count:
                continue

            gains=[slide.quiz_first_attempt_reward,
                     slide.quiz_second_attempt_reward,
                     slide.quiz_third_attempt_reward,
                     slide.quiz_fourth_attempt_reward]
            points+=gains[user_membership_sudo.quiz_attempts_count-1]ifuser_membership_sudo.quiz_attempts_count<=len(gains)elsegains[-1]

        returnself.env.user.sudo().add_karma(points)

    def_compute_quiz_info(self,target_partner,quiz_done=False):
        result=dict.fromkeys(self.ids,False)
        slide_partners=self.env['slide.slide.partner'].sudo().search([
            ('slide_id','in',self.ids),
            ('partner_id','=',target_partner.id)
        ])
        slide_partners_map=dict((sp.slide_id.id,sp)forspinslide_partners)
        forslideinself:
            ifnotslide.question_ids:
                gains=[0]
            else:
                gains=[slide.quiz_first_attempt_reward,
                         slide.quiz_second_attempt_reward,
                         slide.quiz_third_attempt_reward,
                         slide.quiz_fourth_attempt_reward]
            result[slide.id]={
                'quiz_karma_max':gains[0], #whatcouldbegainedifsucceedatfirsttry
                'quiz_karma_gain':gains[0], #whatwouldbegainedatnexttest
                'quiz_karma_won':0, #whathasbeengained
                'quiz_attempts_count':0, #numberofattempts
            }
            slide_partner=slide_partners_map.get(slide.id)
            ifslide.question_idsandslide_partnerandslide_partner.quiz_attempts_count:
                result[slide.id]['quiz_karma_gain']=gains[slide_partner.quiz_attempts_count]ifslide_partner.quiz_attempts_count<len(gains)elsegains[-1]
                result[slide.id]['quiz_attempts_count']=slide_partner.quiz_attempts_count
                ifquiz_doneorslide_partner.completed:
                    result[slide.id]['quiz_karma_won']=gains[slide_partner.quiz_attempts_count-1]ifslide_partner.quiz_attempts_count<len(gains)elsegains[-1]
        returnresult

    #--------------------------------------------------
    #Parsingmethods
    #--------------------------------------------------

    @api.model
    def_fetch_data(self,base_url,params,content_type=False):
        result={'values':dict()}
        try:
            response=requests.get(base_url,timeout=3,params=params)
            response.raise_for_status()
            ifcontent_type=='json':
                result['values']=response.json()
            elifcontent_typein('image','pdf'):
                result['values']=base64.b64encode(response.content)
            else:
                result['values']=response.content
        exceptrequests.exceptions.HTTPErrorase:
            result['error']=e.response.content
        exceptrequests.exceptions.ConnectionErrorase:
            result['error']=str(e)
        returnresult

    def_find_document_data_from_url(self,url):
        url_obj=urls.url_parse(url)
        ifurl_obj.ascii_host=='youtu.be':
            return('youtube',url_obj.path[1:]ifurl_obj.pathelseFalse)
        elifurl_obj.ascii_hostin('youtube.com','www.youtube.com','m.youtube.com','www.youtube-nocookie.com'):
            v_query_value=url_obj.decode_query().get('v')
            ifv_query_value:
                return('youtube',v_query_value)
            split_path=url_obj.path.split('/')
            iflen(split_path)>=3andsplit_path[1]in('v','embed'):
                return('youtube',split_path[2])

        expr=re.compile(r'(^https:\/\/docs.google.com|^https:\/\/drive.google.com).*\/d\/([^\/]*)')
        arg=expr.match(url)
        document_id=argandarg.group(2)orFalse
        ifdocument_id:
            return('google',document_id)

        return(None,False)

    def_parse_document_url(self,url,only_preview_fields=False):
        document_source,document_id=self._find_document_data_from_url(url)
        ifdocument_sourceandhasattr(self,'_parse_%s_document'%document_source):
            returngetattr(self,'_parse_%s_document'%document_source)(document_id,only_preview_fields)
        return{'error':_('Unknowndocument')}

    def_parse_youtube_document(self,document_id,only_preview_fields):
        """Ifwereceiveaduration(YTvideo),weuseittodeterminetheslideduration.
        Thereceiveddurationisunderaspecialformat(e.g:PT1M21S15,meaning1h21m15s)."""

        key=self.env['website'].get_current_website().sudo().website_slide_google_app_key
        fetch_res=self._fetch_data('https://www.googleapis.com/youtube/v3/videos',{'id':document_id,'key':key,'part':'snippet,contentDetails','fields':'items(id,snippet,contentDetails)'},'json')
        iffetch_res.get('error'):
            return{'error':self._extract_google_error_message(fetch_res.get('error'))}

        values={'slide_type':'video','document_id':document_id}
        items=fetch_res['values'].get('items')
        ifnotitems:
            return{'error':_('PleaseentervalidYoutubeorGoogleDocURL')}
        youtube_values=items[0]

        youtube_duration=youtube_values.get('contentDetails',{}).get('duration')
        ifyoutube_duration:
            parsed_duration=re.search(r'^PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$',youtube_duration)
            ifparsed_duration:
                values['completion_time']=(int(parsed_duration.group(1)or0))+\
                                            (int(parsed_duration.group(2)or0)/60)+\
                                            (int(parsed_duration.group(3)or0)/3600)

        ifyoutube_values.get('snippet'):
            snippet=youtube_values['snippet']
            ifonly_preview_fields:
                values.update({
                    'url_src':snippet['thumbnails']['high']['url'],
                    'title':snippet['title'],
                    'description':snippet['description']
                })

                returnvalues

            values.update({
                'name':snippet['title'],
                'image_1920':self._fetch_data(snippet['thumbnails']['high']['url'],{},'image')['values'],
                'description':snippet['description'],
                'mime_type':False,
            })
        return{'values':values}

    def_extract_google_error_message(self,error):
        """
        SeehereforGoogleerrorformat
        https://developers.google.com/drive/api/v3/handle-errors
        """
        try:
            error=json.loads(error)
            error=(error.get('error',{}).get('errors',[])or[{}])[0].get('reason')
        exceptjson.decoder.JSONDecodeError:
            error=str(error)

        iferror=='keyInvalid':
            return_('YourGoogleAPIkeyisinvalid,pleaseupdateitinyoursettings.\nSettings>Website>Features>APIKey')

        return_('Couldnotfetchdatafromurl.Documentoraccessrightnotavailable:\n%s',error)

    @api.model
    def_parse_google_document(self,document_id,only_preview_fields):
        defget_slide_type(vals):
            #TDEFIXME:WTF??
            slide_type='presentation'
            ifvals.get('image_1920'):
                image=Image.open(io.BytesIO(base64.b64decode(vals['image_1920'])))
                width,height=image.size
                ifheight>width:
                    return'document'
            returnslide_type

        #Googledrivedoesn'tuseasimpleAPIkeytoaccessthedata,butrequiresanaccess
        #token.However,thistokenisgeneratedinmodulegoogle_drive,whichisnotinthe
        #dependenciesofwebsite_slides.Westillkeepthe'key'parameterjustincase,butthat
        #isprobablyuseless.
        params={}
        params['projection']='BASIC'
        if'google.drive.config'inself.env:
            access_token=self.env['google.drive.config'].get_access_token()
            ifaccess_token:
                params['access_token']=access_token
        ifnotparams.get('access_token'):
            params['key']=self.env['website'].get_current_website().sudo().website_slide_google_app_key

        fetch_res=self._fetch_data('https://www.googleapis.com/drive/v2/files/%s'%document_id,params,"json")
        iffetch_res.get('error'):
            return{'error':self._extract_google_error_message(fetch_res.get('error'))}

        google_values=fetch_res['values']
        ifonly_preview_fields:
            return{
                'url_src':google_values['thumbnailLink'],
                'title':google_values['title'],
            }

        values={
            'name':google_values['title'],
            'image_1920':self._fetch_data(google_values['thumbnailLink'].replace('=s220',''),{},'image')['values'],
            'mime_type':google_values['mimeType'],
            'document_id':document_id,
        }
        ifgoogle_values['mimeType'].startswith('video/'):
            values['slide_type']='video'
        elifgoogle_values['mimeType'].startswith('image/'):
            values['datas']=values['image_1920']
            values['slide_type']='infographic'
        elifgoogle_values['mimeType'].startswith('application/vnd.google-apps'):
            values['slide_type']=get_slide_type(values)
            if'exportLinks'ingoogle_values:
                values['datas']=self._fetch_data(google_values['exportLinks']['application/pdf'],params,'pdf')['values']
        elifgoogle_values['mimeType']=='application/pdf':
            #TODO:GoogleDrivePDFdocumentdoesn'tprovideplaintexttranscript
            values['datas']=self._fetch_data(google_values['webContentLink'],{},'pdf')['values']
            values['slide_type']=get_slide_type(values)

        return{'values':values}

    def_default_website_meta(self):
        res=super(Slide,self)._default_website_meta()
        res['default_opengraph']['og:title']=res['default_twitter']['twitter:title']=self.name
        res['default_opengraph']['og:description']=res['default_twitter']['twitter:description']=self.description
        res['default_opengraph']['og:image']=res['default_twitter']['twitter:image']=self.env['website'].image_url(self,'image_1024')
        res['default_meta_description']=self.description
        returnres

    #---------------------------------------------------------
    #Data/Misc
    #---------------------------------------------------------

    defget_backend_menu_id(self):
        returnself.env.ref('website_slides.website_slides_menu_root').id
