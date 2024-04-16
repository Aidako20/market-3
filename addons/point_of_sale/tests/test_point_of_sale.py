#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportTransactionCase


classTestPointOfSale(TransactionCase):
    defsetUp(self):
        super(TestPointOfSale,self).setUp()

        #ignorepre-existingpricelistsforthepurposeofthistest
        self.env["product.pricelist"].search([]).write({"active":False})

        self.currency=self.env.ref("base.USD")
        self.company1=self.env["res.company"].create({
            "name":"company1",
            "currency_id":self.currency.id
        })
        self.company2=self.env["res.company"].create({
            "name":"company2",
            "currency_id":self.currency.id
        })
        self.company2_pricelist=self.env["product.pricelist"].create({
            "name":"company2pricelist",
            "currency_id":self.currency.id,
            "company_id":self.company2.id,
            "sequence":1, #forcethispricelisttobefirst
        })

        self.env.user.company_id=self.company1

    deftest_default_pricelist_with_company(self):
        """Verifythatthedefaultpricelistbelongstothesamecompanyastheconfig"""
        company1_pricelist=self.env["product.pricelist"].create({
            "name":"company1pricelist",
            "currency_id":self.currency.id,
            "company_id":self.company1.id,
            "sequence":2,
        })

        #makesurethisdoesn'tpickthecompany2pricelist
        new_config=self.env["pos.config"].create({
            "name":"usdconfig"
        })

        self.assertEqual(new_config.pricelist_id,company1_pricelist,
                         "POSconfigincorrectlyhaspricelist%s"%new_config.pricelist_id.display_name)

    deftest_default_pricelist_without_company(self):
        """Verifythatadefaultpricelistwithoutacompanyworks"""
        universal_pricelist=self.env["product.pricelist"].create({
            "name":"universalpricelist",
            "currency_id":self.currency.id,
            "sequence":2,
        })

        #makesurethisdoesn'tpickthecompany2pricelist
        new_config=self.env["pos.config"].create({
            "name":"usdconfig"
        })

        self.assertEqual(new_config.pricelist_id,universal_pricelist,
                         "POSconfigincorrectlyhaspricelist%s"%new_config.pricelist_id.display_name)
