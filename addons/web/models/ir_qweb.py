#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importhashlib
fromcollectionsimportOrderedDict
fromwerkzeug.urlsimporturl_quote

fromflectraimportapi,models
fromflectra.toolsimportpycompat
fromflectra.toolsimporthtml_escapeasescape


classImage(models.AbstractModel):
    """
    Widgetoptions:

    ``class``
        setasattributeonthegenerated<img>tag
    """
    _name='ir.qweb.field.image'
    _description='QwebFieldImage'
    _inherit='ir.qweb.field.image'

    def_get_src_urls(self,record,field_name,options):
        """Consideringtherenderingoptions,returnsthesrcanddata-zoom-imageurls.

        :return:src,src_zoomurls
        :rtype:tuple
        """
        max_size=None
        ifoptions.get('resize'):
            max_size=options.get('resize')
        else:
            max_width,max_height=options.get('max_width',0),options.get('max_height',0)
            ifmax_widthormax_height:
                max_size='%sx%s'%(max_width,max_height)

        sha=hashlib.sha512(str(getattr(record,'__last_update')).encode('utf-8')).hexdigest()[:7]
        max_size=''ifmax_sizeisNoneelse'/%s'%max_size

        ifoptions.get('filename-field')andoptions['filename-field']inrecordandrecord[options['filename-field']]:
            filename=record[options['filename-field']]
        elifoptions.get('filename'):
            filename=options['filename']
        else:
            filename=record.display_name
        filename=filename.replace('/','-').replace('\\','-').replace('..','--')

        src='/web/image/%s/%s/%s%s/%s?unique=%s'%(record._name,record.id,options.get('preview_image',field_name),max_size,url_quote(filename),sha)

        src_zoom=None
        ifoptions.get('zoom')andgetattr(record,options['zoom'],None):
            src_zoom='/web/image/%s/%s/%s%s/%s?unique=%s'%(record._name,record.id,options['zoom'],max_size,url_quote(filename),sha)
        elifoptions.get('zoom'):
            src_zoom=options['zoom']

        returnsrc,src_zoom

    @api.model
    defrecord_to_html(self,record,field_name,options):
        assertoptions['tagName']!='img',\
            "Oddlyenough,theroottagofanimagefieldcannotbeimg."\
            "Thatisbecausetheimagegoesintothetag,oritgetsthe"\
            "hoseagain."

        ifoptions.get('qweb_img_raw_data',False):
            returnsuper(Image,self).record_to_html(record,field_name,options)

        aclasses=['img','img-fluid']ifoptions.get('qweb_img_responsive',True)else['img']
        aclasses+=options.get('class','').split()
        classes=''.join(map(escape,aclasses))

        src,src_zoom=self._get_src_urls(record,field_name,options)

        ifoptions.get('alt-field')andoptions['alt-field']inrecordandrecord[options['alt-field']]:
            alt=escape(record[options['alt-field']])
        elifoptions.get('alt'):
            alt=options['alt']
        else:
            alt=escape(record.display_name)

        itemprop=None
        ifoptions.get('itemprop'):
            itemprop=options['itemprop']

        atts=OrderedDict()
        atts["src"]=src
        atts["itemprop"]=itemprop
        atts["class"]=classes
        atts["style"]=options.get('style')
        atts["alt"]=alt
        atts["data-zoom"]=src_zoomandu'1'orNone
        atts["data-zoom-image"]=src_zoom
        atts["data-no-post-process"]=options.get('data-no-post-process')

        atts=self.env['ir.qweb']._post_processing_att('img',atts,options.get('template_options'))

        img=['<img']
        forname,valueinatts.items():
            ifvalue:
                img.append('')
                img.append(escape(pycompat.to_text(name)))
                img.append('="')
                img.append(escape(pycompat.to_text(value)))
                img.append('"')
        img.append('/>')

        returnu''.join(img)

classImageUrlConverter(models.AbstractModel):
    _description='QwebFieldImage'
    _inherit='ir.qweb.field.image_url'

    def_get_src_urls(self,record,field_name,options):
        image_url=record[options.get('preview_image',field_name)]
        returnimage_url,options.get("zoom",None)
