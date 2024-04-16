#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.event.tests.commonimportTestEventCommon
fromflectra.addons.sales_team.tests.commonimportTestSalesCommon


classTestEventSaleCommon(TestEventCommon,TestSalesCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestEventSaleCommon,cls).setUpClass()

        cls.event_product=cls.env['product.product'].create({
            'name':'TestRegistrationProduct',
            'description_sale':'MightyDescription',
            'list_price':10,
            'event_ok':True,
            'standard_price':30.0,
            'type':'service',
        })
