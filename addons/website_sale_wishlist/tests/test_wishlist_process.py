#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importflectra.tests


@flectra.tests.tagged('-at_install','post_install')
classTestUi(flectra.tests.HttpCase):
    deftest_01_wishlist_tour(self):

        self.env['product.template'].search([]).write({'website_published':False})
        #Setupattributesandattributesvalues
        self.product_attribute_1=self.env['product.attribute'].create({
            'name':'Legs',
            'sequence':10,
        })
        product_attribute_value_1=self.env['product.attribute.value'].create({
            'name':'Steel',
            'attribute_id':self.product_attribute_1.id,
            'sequence':1,
        })
        product_attribute_value_2=self.env['product.attribute.value'].create({
            'name':'Aluminium',
            'attribute_id':self.product_attribute_1.id,
            'sequence':2,
        })
        product_attribute_2=self.env['product.attribute'].create({
            'name':'Color',
            'sequence':20,
        })
        product_attribute_value_3=self.env['product.attribute.value'].create({
            'name':'White',
            'attribute_id':product_attribute_2.id,
            'sequence':1,
        })
        product_attribute_value_4=self.env['product.attribute.value'].create({
            'name':'Black',
            'attribute_id':product_attribute_2.id,
            'sequence':2,
        })

        #Createproducttemplate
        self.product_product_4_product_template=self.env['product.template'].create({
            'name':'CustomizableDesk(TEST)',
            'standard_price':500.0,
            'list_price':750.0,
            'website_published':True,
        })

        #Generatevariants
        self.env['product.template.attribute.line'].create([{
            'product_tmpl_id':self.product_product_4_product_template.id,
            'attribute_id':self.product_attribute_1.id,
            'value_ids':[(4,product_attribute_value_1.id),(4,product_attribute_value_2.id)],
        },{
            'product_tmpl_id':self.product_product_4_product_template.id,
            'attribute_id':product_attribute_2.id,
            'value_ids':[(4,product_attribute_value_3.id),(4,product_attribute_value_4.id)],

        }])

        self.env.ref('base.user_admin').name='MitchellAdmin'

        self.start_tour("/",'shop_wishlist')

    deftest_02_wishlist_admin_tour(self):
        self.start_tour("/",'shop_wishlist_admin',login="admin")
