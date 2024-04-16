#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromwerkzeug.urlsimporturl_quote

fromflectraimportapi,models,fields,tools

SUPPORTED_IMAGE_MIMETYPES=['image/gif','image/jpe','image/jpeg','image/jpg','image/gif','image/png','image/svg+xml']

classIrAttachment(models.Model):

    _inherit="ir.attachment"

    local_url=fields.Char("AttachmentURL",compute='_compute_local_url')
    image_src=fields.Char(compute='_compute_image_src')
    image_width=fields.Integer(compute='_compute_image_size')
    image_height=fields.Integer(compute='_compute_image_size')
    original_id=fields.Many2one('ir.attachment',string="Original(unoptimized,unresized)attachment",index=True)

    def_compute_local_url(self):
        forattachmentinself:
            ifattachment.url:
                attachment.local_url=attachment.url
            else:
                attachment.local_url='/web/image/%s?unique=%s'%(attachment.id,attachment.checksum)

    @api.depends('mimetype','url','name')
    def_compute_image_src(self):
        forattachmentinself:
            #Onlyaddasrcforsupportedimages
            ifattachment.mimetypenotinSUPPORTED_IMAGE_MIMETYPES:
                attachment.image_src=False
                continue

            ifattachment.type=='url':
                attachment.image_src=attachment.url
            else:
                #AddinguniqueinURLsforcache-control
                unique=attachment.checksum[:8]
                ifattachment.url:
                    #Forattachments-by-url,uniqueisusedasacachebuster.They
                    #currentlydonotleveragemax-ageheaders.
                    attachment.image_src='%s?unique=%s'%(attachment.url,unique)
                else:
                    name=url_quote(attachment.name)
                    attachment.image_src='/web/image/%s-%s/%s'%(attachment.id,unique,name)

    @api.depends('datas')
    def_compute_image_size(self):
        forattachmentinself:
            try:
                image=tools.base64_to_image(attachment.datas)
                attachment.image_width=image.width
                attachment.image_height=image.height
            exceptException:
                attachment.image_width=0
                attachment.image_height=0

    def_get_media_info(self):
        """Returnadictwiththevaluesthatweneedonthemediadialog."""
        self.ensure_one()
        returnself._read_format(['id','name','description','mimetype','checksum','url','type','res_id','res_model','public','access_token','image_src','image_width','image_height','original_id'])[0]
