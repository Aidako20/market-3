#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestName(TransactionCase):

    defsetUp(self):
        super().setUp()
        self.product_name='ProductTestName'
        self.product_code='PTN'
        self.product=self.env['product.product'].create({
            'name':self.product_name,
            'default_code':self.product_code,
        })

    deftest_10_product_name(self):
        display_name=self.product.display_name
        self.assertEqual(display_name,"[%s]%s"%(self.product_code,self.product_name),
                         "Codeshouldbepreprendedthethenameasthecontextisnotpreventingit.")
        display_name=self.product.with_context(display_default_code=False).display_name
        self.assertEqual(display_name,self.product_name,
                         "Codeshouldnotbepreprendedtothenameascontextshouldpreventit.")

    deftest_default_code_and_negative_operator(self):
        res=self.env['product.template'].name_search(name='PTN',operator='notilike')
        res_ids=[r[0]forrinres]
        self.assertNotIn(self.product.id,res_ids)
