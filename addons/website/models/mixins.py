#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importlogging

fromwerkzeug.urlsimporturl_join

fromflectraimportapi,fields,models,_
fromflectra.addons.http_routing.models.ir_httpimporturl_for
fromflectra.httpimportrequest
fromflectra.osvimportexpression
fromflectra.exceptionsimportAccessError
fromflectra.tools.jsonimportscriptsafeasjson_scriptsafe

logger=logging.getLogger(__name__)


classSeoMetadata(models.AbstractModel):

    _name='website.seo.metadata'
    _description='SEOmetadata'

    is_seo_optimized=fields.Boolean("SEOoptimized",compute='_compute_is_seo_optimized')
    website_meta_title=fields.Char("Websitemetatitle",translate=True)
    website_meta_description=fields.Text("Websitemetadescription",translate=True)
    website_meta_keywords=fields.Char("Websitemetakeywords",translate=True)
    website_meta_og_img=fields.Char("Websiteopengraphimage")
    seo_name=fields.Char("Seoname",translate=True)

    def_compute_is_seo_optimized(self):
        forrecordinself:
            record.is_seo_optimized=record.website_meta_titleandrecord.website_meta_descriptionandrecord.website_meta_keywords

    def_default_website_meta(self):
        """Thismethodwillreturndefaultmetainformation.Itreturnthedict
            containsmetapropertyasakeyandmetacontentasavalue.
            e.g.'og:type':'website'.

            Overridethismethodincaseyouwanttochangedefaultvalue
            fromanymodel.e.g.changevalueofog:imagetoproductspecific
            imagesinsteadofdefaultimages
        """
        self.ensure_one()
        company=request.website.company_id.sudo()
        title=(request.websiteorcompany).name
        if'name'inself:
            title='%s|%s'%(self.name,title)

        img_field='social_default_image'ifrequest.website.has_social_default_imageelse'logo'

        #DefaultmetaforOpenGraph
        default_opengraph={
            'og:type':'website',
            'og:title':title,
            'og:site_name':company.name,
            'og:url':url_join(request.httprequest.url_root,url_for(request.httprequest.path)),
            'og:image':request.website.image_url(request.website,img_field),
        }
        #DefaultmetaforTwitter
        default_twitter={
            'twitter:card':'summary_large_image',
            'twitter:title':title,
            'twitter:image':request.website.image_url(request.website,img_field,size='300x300'),
        }
        ifcompany.social_twitter:
            default_twitter['twitter:site']="@%s"%company.social_twitter.split('/')[-1]

        return{
            'default_opengraph':default_opengraph,
            'default_twitter':default_twitter
        }

    defget_website_meta(self):
        """Thismethodwillreturnfinalmetainformation.Itwillreplace
            defaultvalueswithuser'scustomvalue(ifusermodifieditfrom
            theseopopupoffrontend)

            Thismethodisnotmeantforoverridden.Tocustomizemetavalues
            override`_default_website_meta`methodinsteadofthismethod.This
            methodonlyreplacesusercustomvaluesindefaults.
        """
        root_url=request.httprequest.url_root.strip('/')
        default_meta=self._default_website_meta()
        opengraph_meta,twitter_meta=default_meta['default_opengraph'],default_meta['default_twitter']
        ifself.website_meta_title:
            opengraph_meta['og:title']=self.website_meta_title
            twitter_meta['twitter:title']=self.website_meta_title
        ifself.website_meta_description:
            opengraph_meta['og:description']=self.website_meta_description
            twitter_meta['twitter:description']=self.website_meta_description
        opengraph_meta['og:image']=url_join(root_url,url_for(self.website_meta_og_imgoropengraph_meta['og:image']))
        twitter_meta['twitter:image']=url_join(root_url,url_for(self.website_meta_og_imgortwitter_meta['twitter:image']))
        return{
            'opengraph_meta':opengraph_meta,
            'twitter_meta':twitter_meta,
            'meta_description':default_meta.get('default_meta_description')
        }


classWebsiteCoverPropertiesMixin(models.AbstractModel):

    _name='website.cover_properties.mixin'
    _description='CoverPropertiesWebsiteMixin'

    cover_properties=fields.Text('CoverProperties',default=lambdas:json_scriptsafe.dumps(s._default_cover_properties()))

    def_default_cover_properties(self):
        return{
            "background_color_class":"o_cc3",
            "background-image":"none",
            "opacity":"0.2",
            "resize_class":"o_half_screen_height",
        }

    defwrite(self,vals):
        if'cover_properties'notinvals:
            returnsuper().write(vals)

        cover_properties=json_scriptsafe.loads(vals['cover_properties'])
        resize_classes=cover_properties.get('resize_class','').split()
        classes=['o_half_screen_height','o_full_screen_height','cover_auto']
        ifnotset(resize_classes).isdisjoint(classes):
            #Updatingcoverpropertiesandthegiven'resize_class'setis
            #valid,normalwrite.
            returnsuper().write(vals)

        #Ifwedonotreceiveavalidresize_classviathecover_properties,we
        #keeptheoriginalone(preventsupdatesonlistdisplaysfrom
        #destroyingresize_class).
        copy_vals=dict(vals)
        foriteminself:
            old_cover_properties=json_scriptsafe.loads(item.cover_properties)
            cover_properties['resize_class']=old_cover_properties.get('resize_class',classes[0])
            copy_vals['cover_properties']=json_scriptsafe.dumps(cover_properties)
            super(WebsiteCoverPropertiesMixin,item).write(copy_vals)
        returnTrue


classWebsiteMultiMixin(models.AbstractModel):

    _name='website.multi.mixin'
    _description='MultiWebsiteMixin'

    website_id=fields.Many2one(
        "website",
        string="Website",
        ondelete="restrict",
        help="Restrictpublishingtothiswebsite.",
        index=True,
    )

    defcan_access_from_current_website(self,website_id=False):
        can_access=True
        forrecordinself:
            if(website_idorrecord.website_id.id)notin(False,request.website.id):
                can_access=False
                continue
        returncan_access


classWebsitePublishedMixin(models.AbstractModel):

    _name="website.published.mixin"
    _description='WebsitePublishedMixin'

    website_published=fields.Boolean('Visibleoncurrentwebsite',related='is_published',readonly=False)
    is_published=fields.Boolean('IsPublished',copy=False,default=lambdaself:self._default_is_published(),index=True)
    can_publish=fields.Boolean('CanPublish',compute='_compute_can_publish')
    website_url=fields.Char('WebsiteURL',compute='_compute_website_url',help='ThefullURLtoaccessthedocumentthroughthewebsite.')

    @api.depends_context('lang')
    def_compute_website_url(self):
        forrecordinself:
            record.website_url='#'

    def_default_is_published(self):
        returnFalse

    defwebsite_publish_button(self):
        self.ensure_one()
        returnself.write({'website_published':notself.website_published})

    defopen_website_url(self):
        return{
            'type':'ir.actions.act_url',
            'url':self.website_url,
            'target':'self',
        }

    @api.model_create_multi
    defcreate(self,vals_list):
        records=super(WebsitePublishedMixin,self).create(vals_list)
        is_publish_modified=any(
            [set(v.keys())&{'is_published','website_published'}forvinvals_list]
        )
        ifis_publish_modifiedandany(notrecord.can_publishforrecordinrecords):
            raiseAccessError(self._get_can_publish_error_message())

        returnrecords

    defwrite(self,values):
        if'is_published'invaluesandany(notrecord.can_publishforrecordinself):
            raiseAccessError(self._get_can_publish_error_message())

        returnsuper(WebsitePublishedMixin,self).write(values)

    defcreate_and_get_website_url(self,**kwargs):
        returnself.create(kwargs).website_url

    def_compute_can_publish(self):
        """Thismethodcanbeoverriddenifyouneedmorecomplexrightsmanagementthanjust'website_publisher'
        Thepublishwidgetwillbehiddenandtheuserwon'tbeabletochangethe'website_published'value
        ifthismethodsetscan_publishFalse"""
        forrecordinself:
            record.can_publish=True

    @api.model
    def_get_can_publish_error_message(self):
        """Overridethismethodtocustomizetheerrormessageshownwhentheuserdoesn't
        havetherightstopublish/unpublish."""
        return_("Youdonothavetherightstopublish/unpublish")


classWebsitePublishedMultiMixin(WebsitePublishedMixin):

    _name='website.published.multi.mixin'
    _inherit=['website.published.mixin','website.multi.mixin']
    _description='MultiWebsitePublishedMixin'

    website_published=fields.Boolean(compute='_compute_website_published',
                                       inverse='_inverse_website_published',
                                       search='_search_website_published',
                                       related=False,readonly=False)

    @api.depends('is_published','website_id')
    @api.depends_context('website_id')
    def_compute_website_published(self):
        current_website_id=self._context.get('website_id')
        forrecordinself:
            ifcurrent_website_id:
                record.website_published=record.is_publishedand(notrecord.website_idorrecord.website_id.id==current_website_id)
            else:
                record.website_published=record.is_published

    def_inverse_website_published(self):
        forrecordinself:
            record.is_published=record.website_published

    def_search_website_published(self,operator,value):
        ifnotisinstance(value,bool)oroperatornotin('=','!='):
            logger.warning('unsupportedsearchonwebsite_published:%s,%s',operator,value)
            return[()]

        ifoperatorinexpression.NEGATIVE_TERM_OPERATORS:
            value=notvalue

        current_website_id=self._context.get('website_id')
        is_published=[('is_published','=',value)]
        ifcurrent_website_id:
            on_current_website=self.env['website'].website_domain(current_website_id)
            return(['!']ifvalueisFalseelse[])+expression.AND([is_published,on_current_website])
        else: #shouldbeinthebackend,returnthingsthatarepublishedanywhere
            returnis_published
