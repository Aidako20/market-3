#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
importrandom

fromflectraimportapi,models,fields,_
fromflectra.addons.http_routing.models.ir_httpimportslug
fromflectra.tools.jsonimportscriptsafeasjson_scriptsafe
fromflectra.tools.translateimporthtml_translate
fromflectra.toolsimporthtml2plaintext


classBlog(models.Model):
    _name='blog.blog'
    _description='Blog'
    _inherit=['mail.thread','website.seo.metadata','website.multi.mixin','website.cover_properties.mixin']
    _order='name'

    name=fields.Char('BlogName',required=True,translate=True)
    subtitle=fields.Char('BlogSubtitle',translate=True)
    active=fields.Boolean('Active',default=True)
    content=fields.Html('Content',translate=html_translate,sanitize=False)
    blog_post_ids=fields.One2many('blog.post','blog_id','BlogPosts')
    blog_post_count=fields.Integer("Posts",compute='_compute_blog_post_count')

    @api.depends('blog_post_ids')
    def_compute_blog_post_count(self):
        forrecordinself:
            record.blog_post_count=len(record.blog_post_ids)

    defwrite(self,vals):
        res=super(Blog,self).write(vals)
        if'active'invals:
            #archiving/unarchivingablogdoesitonitsposts,too
            post_ids=self.env['blog.post'].with_context(active_test=False).search([
                ('blog_id','in',self.ids)
            ])
            forblog_postinpost_ids:
                blog_post.active=vals['active']
        returnres

    @api.returns('mail.message',lambdavalue:value.id)
    defmessage_post(self,*,parent_id=False,subtype_id=False,**kwargs):
        """Temporaryworkaroundtoavoidspam.Ifsomeonerepliesonachannel
        throughthe'PresentationPublished'email,itshouldbeconsideredasa
        noteaswedon'twantallchannelfollowerstobenotifiedofthisanswer."""
        self.ensure_one()
        ifparent_id:
            parent_message=self.env['mail.message'].sudo().browse(parent_id)
            ifparent_message.subtype_idandparent_message.subtype_id==self.env.ref('website_blog.mt_blog_blog_published'):
                subtype_id=self.env.ref('mail.mt_note').id
        returnsuper(Blog,self).message_post(parent_id=parent_id,subtype_id=subtype_id,**kwargs)

    defall_tags(self,join=False,min_limit=1):
        BlogTag=self.env['blog.tag']
        req="""
            SELECT
                p.blog_id,count(*),r.blog_tag_id
            FROM
                blog_post_blog_tag_relr
                    joinblog_postponr.blog_post_id=p.id
            WHERE
                p.blog_idin%s
            GROUPBY
                p.blog_id,
                r.blog_tag_id
            ORDERBY
                count(*)DESC
        """
        self._cr.execute(req,[tuple(self.ids)])
        tag_by_blog={i.id:[]foriinself}
        all_tags=set()
        forblog_id,freq,tag_idinself._cr.fetchall():
            iffreq>=min_limit:
                ifjoin:
                    all_tags.add(tag_id)
                else:
                    tag_by_blog[blog_id].append(tag_id)

        ifjoin:
            returnBlogTag.browse(all_tags)

        forblog_idintag_by_blog:
            tag_by_blog[blog_id]=BlogTag.browse(tag_by_blog[blog_id])

        returntag_by_blog


classBlogTagCategory(models.Model):
    _name='blog.tag.category'
    _description='BlogTagCategory'
    _order='name'

    name=fields.Char('Name',required=True,translate=True)
    tag_ids=fields.One2many('blog.tag','category_id',string='Tags')

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagcategoryalreadyexists!"),
    ]


classBlogTag(models.Model):
    _name='blog.tag'
    _description='BlogTag'
    _inherit=['website.seo.metadata']
    _order='name'

    name=fields.Char('Name',required=True,translate=True)
    category_id=fields.Many2one('blog.tag.category','Category',index=True)
    post_ids=fields.Many2many('blog.post',string='Posts')

    _sql_constraints=[
        ('name_uniq','unique(name)',"Tagnamealreadyexists!"),
    ]


classBlogPost(models.Model):
    _name="blog.post"
    _description="BlogPost"
    _inherit=['mail.thread','website.seo.metadata','website.published.multi.mixin','website.cover_properties.mixin']
    _order='idDESC'
    _mail_post_access='read'

    def_compute_website_url(self):
        super(BlogPost,self)._compute_website_url()
        forblog_postinself:
            blog_post.website_url="/blog/%s/%s"%(slug(blog_post.blog_id),slug(blog_post))

    def_default_content(self):
        return'''
            <pclass="o_default_snippet_text">'''+_("Startwritinghere...")+'''</p>
        '''
    name=fields.Char('Title',required=True,translate=True,default='')
    subtitle=fields.Char('SubTitle',translate=True)
    author_id=fields.Many2one('res.partner','Author',default=lambdaself:self.env.user.partner_id)
    author_avatar=fields.Binary(related='author_id.image_128',string="Avatar",readonly=False)
    author_name=fields.Char(related='author_id.display_name',string="AuthorName",readonly=False,store=True)
    active=fields.Boolean('Active',default=True)
    blog_id=fields.Many2one('blog.blog','Blog',required=True,ondelete='cascade')
    tag_ids=fields.Many2many('blog.tag',string='Tags')
    content=fields.Html('Content',default=_default_content,translate=html_translate,sanitize=False)
    teaser=fields.Text('Teaser',compute='_compute_teaser',inverse='_set_teaser')
    teaser_manual=fields.Text(string='TeaserContent')

    website_message_ids=fields.One2many(domain=lambdaself:[('model','=',self._name),('message_type','=','comment')])

    #creation/updatestuff
    create_date=fields.Datetime('Createdon',index=True,readonly=True)
    published_date=fields.Datetime('PublishedDate')
    post_date=fields.Datetime('Publishingdate',compute='_compute_post_date',inverse='_set_post_date',store=True,
                                help="Theblogpostwillbevisibleforyourvisitorsasofthisdateonthewebsiteifitissetaspublished.")
    create_uid=fields.Many2one('res.users','Createdby',index=True,readonly=True)
    write_date=fields.Datetime('LastUpdatedon',index=True,readonly=True)
    write_uid=fields.Many2one('res.users','LastContributor',index=True,readonly=True)
    visits=fields.Integer('NoofViews',copy=False,default=0)
    website_id=fields.Many2one(related='blog_id.website_id',readonly=True,store=True)

    @api.depends('content','teaser_manual')
    def_compute_teaser(self):
        forblog_postinself:
            ifblog_post.teaser_manual:
                blog_post.teaser=blog_post.teaser_manual
            else:
                content=html2plaintext(blog_post.content).replace('\n','')
                blog_post.teaser=content[:200]+'...'

    def_set_teaser(self):
        forblog_postinself:
            blog_post.teaser_manual=blog_post.teaser

    @api.depends('create_date','published_date')
    def_compute_post_date(self):
        forblog_postinself:
            ifblog_post.published_date:
                blog_post.post_date=blog_post.published_date
            else:
                blog_post.post_date=blog_post.create_date

    def_set_post_date(self):
        forblog_postinself:
            blog_post.published_date=blog_post.post_date
            ifnotblog_post.published_date:
                blog_post._write(dict(post_date=blog_post.create_date))#donttriggerinversefunction

    def_check_for_publication(self,vals):
        ifvals.get('is_published'):
            forpostinself.filtered(lambdap:p.active):
                post.blog_id.message_post_with_view(
                    'website_blog.blog_post_template_new_post',
                    subject=post.name,
                    values={'post':post},
                    subtype_id=self.env['ir.model.data'].xmlid_to_res_id('website_blog.mt_blog_blog_published'))
            returnTrue
        returnFalse

    @api.model
    defcreate(self,vals):
        post_id=super(BlogPost,self.with_context(mail_create_nolog=True)).create(vals)
        post_id._check_for_publication(vals)
        returnpost_id

    defwrite(self,vals):
        result=True
        #archivingablogpost,unpublishedtheblogpost
        if'active'invalsandnotvals['active']:
            vals['is_published']=False
        forpostinself:
            copy_vals=dict(vals)
            published_in_vals=set(vals.keys())&{'is_published','website_published'}
            if(published_in_valsand'published_date'notinvalsand
                    (notpost.published_dateorpost.published_date<=fields.Datetime.now())):
                copy_vals['published_date']=vals[list(published_in_vals)[0]]andfields.Datetime.now()orFalse
            result&=super(BlogPost,post).write(copy_vals)
        self._check_for_publication(vals)
        returnresult

    @api.returns('self',lambdavalue:value.id)
    defcopy_data(self,default=None):
        self.ensure_one()
        name=_("%s(copy)",self.name)
        default=dict(defaultor{},name=name)
        returnsuper(BlogPost,self).copy_data(default)

    defget_access_action(self,access_uid=None):
        """Insteadoftheclassicformview,redirecttothepostonwebsite
        directlyifuserisanemployeeorifthepostispublished."""
        self.ensure_one()
        user=access_uidandself.env['res.users'].sudo().browse(access_uid)orself.env.user
        ifuser.shareandnotself.sudo().website_published:
            returnsuper(BlogPost,self).get_access_action(access_uid)
        return{
            'type':'ir.actions.act_url',
            'url':self.website_url,
            'target':'self',
            'target_type':'public',
            'res_id':self.id,
        }

    def_notify_get_groups(self,msg_vals=None):
        """Addaccessbuttontoeveryoneifthedocumentispublished."""
        groups=super(BlogPost,self)._notify_get_groups(msg_vals=msg_vals)

        ifself.website_published:
            forgroup_name,group_method,group_dataingroups:
                group_data['has_button_access']=True

        returngroups

    def_notify_record_by_inbox(self,message,recipients_data,msg_vals=False,**kwargs):
        """Overridetoavoidkeepingallnotifiedrecipientsofacomment.
        Weavoidtrackingneedactiononpostcomments.Onlyemailsshouldbe
        sufficient."""
        ifmsg_vals.get('message_type',message.message_type)=='comment':
            return
        returnsuper(BlogPost,self)._notify_record_by_inbox(message,recipients_data,msg_vals=msg_vals,**kwargs)

    def_default_website_meta(self):
        res=super(BlogPost,self)._default_website_meta()
        res['default_opengraph']['og:description']=res['default_twitter']['twitter:description']=self.subtitle
        res['default_opengraph']['og:type']='article'
        res['default_opengraph']['article:published_time']=self.post_date
        res['default_opengraph']['article:modified_time']=self.write_date
        res['default_opengraph']['article:tag']=self.tag_ids.mapped('name')
        #background-imagemightcontainsinglequoteseg`url('/my/url')`
        res['default_opengraph']['og:image']=res['default_twitter']['twitter:image']=json_scriptsafe.loads(self.cover_properties).get('background-image','none')[4:-1].strip("'")
        res['default_opengraph']['og:title']=res['default_twitter']['twitter:title']=self.name
        res['default_meta_description']=self.subtitle
        returnres
