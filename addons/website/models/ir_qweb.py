#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importre
fromcollectionsimportOrderedDict

fromflectraimportmodels
fromflectra.httpimportrequest
fromflectra.addons.base.models.assetsbundleimportAssetsBundle
fromflectra.addons.http_routing.models.ir_httpimporturl_for
fromflectra.osvimportexpression
fromflectra.addons.website.modelsimportir_http
fromflectra.toolsimporthtml_escapeasescape

re_background_image=re.compile(r"(background-image\s*:\s*url\(\s*['\"]?\s*)([^)'\"]+)")


classAssetsBundleMultiWebsite(AssetsBundle):
    def_get_asset_url_values(self,id,unique,extra,name,sep,type):
        website_id=self.env.context.get('website_id')
        website_id_path=website_idand('%s/'%website_id)or''
        extra=website_id_path+extra
        res=super(AssetsBundleMultiWebsite,self)._get_asset_url_values(id,unique,extra,name,sep,type)
        returnres

    def_get_assets_domain_for_already_processed_css(self,assets):
        res=super(AssetsBundleMultiWebsite,self)._get_assets_domain_for_already_processed_css(assets)
        current_website=self.env['website'].get_current_website(fallback=False)
        res=expression.AND([res,current_website.website_domain()])
        returnres

classQWeb(models.AbstractModel):
    """QWebobjectforrenderingstuffinthewebsitecontext"""

    _inherit='ir.qweb'

    URL_ATTRS={
        'form':  'action',
        'a':     'href',
        'link':  'href',
        'script':'src',
        'img':   'src',
    }

    defget_asset_bundle(self,xmlid,files,env=None):
        returnAssetsBundleMultiWebsite(xmlid,files,env=env)

    def_post_processing_att(self,tagName,atts,options):
        ifatts.get('data-no-post-process'):
            returnatts

        atts=super(QWeb,self)._post_processing_att(tagName,atts,options)

        iftagName=='img'and'loading'notinatts:
            atts['loading']='lazy' #defaultisauto

        ifoptions.get('inherit_branding')oroptions.get('rendering_bundle')or\
           options.get('edit_translations')oroptions.get('debug')or(requestandrequest.session.debug):
            returnatts

        website=ir_http.get_request_website()
        ifnotwebsiteandoptions.get('website_id'):
            website=self.env['website'].browse(options['website_id'])

        ifnotwebsite:
            returnatts

        name=self.URL_ATTRS.get(tagName)
        ifrequestandnameandnameinatts:
            atts[name]=url_for(atts[name])

        ifnotwebsite.cdn_activated:
            returnatts

        data_name=f'data-{name}'
        ifnameand(nameinattsordata_nameinatts):
            atts=OrderedDict(atts)
            ifnameinatts:
                atts[name]=website.get_cdn_url(atts[name])
            ifdata_nameinatts:
                atts[data_name]=website.get_cdn_url(atts[data_name])
        ifisinstance(atts.get('style'),str)and'background-image'inatts['style']:
            atts=OrderedDict(atts)
            atts['style']=re_background_image.sub(lambdam:'%s%s'%(m.group(1),website.get_cdn_url(m.group(2))),atts['style'])

        returnatts
