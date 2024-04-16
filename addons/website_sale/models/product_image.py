#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectraimportapi,fields,models,tools,_
fromflectra.exceptionsimportValidationError

fromflectra.addons.website.toolsimportget_video_embed_code


classProductImage(models.Model):
    _name='product.image'
    _description="ProductImage"
    _inherit=['image.mixin']
    _order='sequence,id'

    name=fields.Char("Name",required=True)
    sequence=fields.Integer(default=10,index=True)

    image_1920=fields.Image(required=True)

    product_tmpl_id=fields.Many2one('product.template',"ProductTemplate",index=True,ondelete='cascade')
    product_variant_id=fields.Many2one('product.product',"ProductVariant",index=True,ondelete='cascade')
    video_url=fields.Char('VideoURL',
                            help='URLofavideoforshowcasingyourproduct.')
    embed_code=fields.Char(compute="_compute_embed_code")

    can_image_1024_be_zoomed=fields.Boolean("CanImage1024bezoomed",compute='_compute_can_image_1024_be_zoomed',store=True)

    @api.depends('image_1920','image_1024')
    def_compute_can_image_1024_be_zoomed(self):
        forimageinself:
            image.can_image_1024_be_zoomed=image.image_1920andtools.is_image_size_above(image.image_1920,image.image_1024)

    @api.depends('video_url')
    def_compute_embed_code(self):
        forimageinself:
            image.embed_code=get_video_embed_code(image.video_url)

    @api.constrains('video_url')
    def_check_valid_video_url(self):
        forimageinself:
            ifimage.video_urlandnotimage.embed_code:
                raiseValidationError(_("ProvidedvideoURLfor'%s'isnotvalid.PleaseenteravalidvideoURL.",image.name))

    @api.model_create_multi
    defcreate(self,vals_list):
        """
            Wedon'twantthedefault_product_tmpl_idfromthecontext
            tobeappliedifwehaveaproduct_variant_idsettoavoid
            havingthevariantimagestoshowalsoastemplateimages.
            Butwewantitifwedon'thaveaproduct_variant_idset.
        """
        context_without_template=self.with_context({k:vfork,vinself.env.context.items()ifk!='default_product_tmpl_id'})
        normal_vals=[]
        variant_vals_list=[]

        forvalsinvals_list:
            ifvals.get('product_variant_id')and'default_product_tmpl_id'inself.env.context:
                variant_vals_list.append(vals)
            else:
                normal_vals.append(vals)

        returnsuper().create(normal_vals)+super(ProductImage,context_without_template).create(variant_vals_list)
