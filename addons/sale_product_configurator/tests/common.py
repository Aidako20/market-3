#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectra.tests.commonimportSavepointCase
fromflectra.modules.moduleimportget_module_resource


classTestProductConfiguratorCommon(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        #Setupattributesandattributesvalues
        cls.product_attribute_1=cls.env['product.attribute'].create({
            'name':'Legs',
            'sequence':10,
        })
        product_attribute_value_1=cls.env['product.attribute.value'].create({
            'name':'Steel',
            'attribute_id':cls.product_attribute_1.id,
            'sequence':1,
        })
        product_attribute_value_2=cls.env['product.attribute.value'].create({
            'name':'Aluminium',
            'attribute_id':cls.product_attribute_1.id,
            'sequence':2,
        })
        product_attribute_2=cls.env['product.attribute'].create({
            'name':'Color',
            'sequence':20,
        })
        product_attribute_value_3=cls.env['product.attribute.value'].create({
            'name':'White',
            'attribute_id':product_attribute_2.id,
            'sequence':1,
        })
        product_attribute_value_4=cls.env['product.attribute.value'].create({
            'name':'Black',
            'attribute_id':product_attribute_2.id,
            'sequence':2,
        })

        #Createproducttemplate
        cls.product_product_custo_desk=cls.env['product.template'].create({
            'name':'CustomizableDesk(TEST)',
            'standard_price':500.0,
            'list_price':750.0,
        })

        #Generatevariants
        cls.env['product.template.attribute.line'].create([{
            'product_tmpl_id':cls.product_product_custo_desk.id,
            'attribute_id':cls.product_attribute_1.id,
            'value_ids':[(4,product_attribute_value_1.id),(4,product_attribute_value_2.id)],
        },{
            'product_tmpl_id':cls.product_product_custo_desk.id,
            'attribute_id':product_attribute_2.id,
            'value_ids':[(4,product_attribute_value_3.id),(4,product_attribute_value_4.id)],

        }])

        #Applyaprice_extrafortheattributeAluminium
        cls.product_product_custo_desk.attribute_line_ids[0].product_template_value_ids[1].price_extra=50.40

        #AddaCustomattribute
        product_attribute_value_custom=cls.env['product.attribute.value'].create({
            'name':'Custom',
            'attribute_id':cls.product_attribute_1.id,
            'sequence':3,
            'is_custom':True
        })
        cls.product_product_custo_desk.attribute_line_ids[0].write({'value_ids':[(4,product_attribute_value_custom.id)]})

        #Disablethealuminium+blackproduct
        cls.product_product_custo_desk.product_variant_ids[3].active=False

        #Setupafirstoptionalproduct
        img_path=get_module_resource('product','static','img','product_product_11-image.png')
        img_content=base64.b64encode(open(img_path,"rb").read())
        cls.product_product_conf_chair=cls.env['product.template'].create({
            'name':'ConferenceChair(TEST)',
            'image_1920':img_content,
            'list_price':16.50,
        })

        cls.env['product.template.attribute.line'].create({
            'product_tmpl_id':cls.product_product_conf_chair.id,
            'attribute_id':cls.product_attribute_1.id,
            'value_ids':[(4,product_attribute_value_1.id),(4,product_attribute_value_2.id)],
        })
        cls.product_product_conf_chair.attribute_line_ids[0].product_template_value_ids[1].price_extra=6.40
        cls.product_product_custo_desk.optional_product_ids=[(4,cls.product_product_conf_chair.id)]

        #Setupasecondoptionalproduct
        cls.product_product_conf_chair_floor_protect=cls.env['product.template'].create({
            'name':'Chairfloorprotection',
            'list_price':12.0,
        })
        cls.product_product_conf_chair.optional_product_ids=[(4,cls.product_product_conf_chair_floor_protect.id)]


    def_create_pricelist(cls,pricelists):
        forpricelistinpricelists:
            ifnotpricelist.item_ids.filtered(lambdai:i.product_tmpl_id==cls.product_product_custo_deskandi.price_discount==20):
                cls.env['product.pricelist.item'].create({
                    'base':'list_price',
                    'applied_on':'1_product',
                    'pricelist_id':pricelist.id,
                    'product_tmpl_id':cls.product_product_custo_desk.id,
                    'price_discount':20,
                    'min_quantity':2,
                    'compute_price':'formula',
                })
            pricelist.discount_policy='without_discount'
