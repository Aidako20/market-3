#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.common.tagged('post_install','-at_install')
classTestWebsiteSequence(flectra.tests.TransactionCase):

    defsetUp(self):
        super(TestWebsiteSequence,self).setUp()

        ProductTemplate=self.env['product.template']
        product_templates=ProductTemplate.search([])
        #ifstockisinstalledwecan'tarchivesincethereisorderpoints
        ifhasattr(self.env['product.product'],'orderpoint_ids'):
            product_templates.mapped('product_variant_ids.orderpoint_ids').write({'active':False})
        #ifposloyaltyisinstalledwecan'tarchivesincethereareloyaltyrulesandrewards
        if'loyalty.rule'inself.env:
            rules=self.env['loyalty.rule'].search([])
            rules.unlink()
        if'loyalty.reward'inself.env:
            rewards=self.env['loyalty.reward'].search([])
            rewards.unlink()
        product_templates.write({'active':False})
        self.p1,self.p2,self.p3,self.p4=ProductTemplate.create([{
            'name':'FirstProduct',
            'website_sequence':100,
        },{
            'name':'SecondProduct',
            'website_sequence':180,
        },{
            'name':'ThirdProduct',
            'website_sequence':225,
        },{
            'name':'LastProduct',
            'website_sequence':250,
        }])

        self._check_correct_order(self.p1+self.p2+self.p3+self.p4)

    def_search_website_sequence_order(self,order='ASC'):
        '''HelpermethodtolimitthesearchonlytothesetUpproducts'''
        returnself.env['product.template'].search([
        ],order='website_sequence%s'%(order))

    def_check_correct_order(self,products):
        product_ids=self._search_website_sequence_order().ids
        self.assertEqual(product_ids,products.ids,"Wrongsequenceorder")

    deftest_01_website_sequence(self):
        #100:1,180:2,225:3,250:4
        self.p2.set_sequence_down()
        #100:1,180:3,225:2,250:4
        self._check_correct_order(self.p1+self.p3+self.p2+self.p4)
        self.p4.set_sequence_up()
        #100:1,180:3,225:4,250:2
        self._check_correct_order(self.p1+self.p3+self.p4+self.p2)
        self.p2.set_sequence_top()
        #95:2,100:1,180:3,225:4
        self._check_correct_order(self.p2+self.p1+self.p3+self.p4)
        self.p1.set_sequence_bottom()
        #95:2,180:3,225:4,230:1
        self._check_correct_order(self.p2+self.p3+self.p4+self.p1)

        current_sequences=self._search_website_sequence_order().mapped('website_sequence')
        self.assertEqual(current_sequences,[95,180,225,230],"Wrongsequenceorder(2)")

        self.p2.website_sequence=1
        self.p3.set_sequence_top()
        #-4:3,1:2,225:4,230:1
        self.assertEqual(self.p3.website_sequence,-4,"`website_sequence`shouldgobelow0")

        new_product=self.env['product.template'].create({
            'name':'LastNewlyCreatedProduct',
        })

        self.assertEqual(self._search_website_sequence_order()[-1],new_product,"newproductshouldbelast")
