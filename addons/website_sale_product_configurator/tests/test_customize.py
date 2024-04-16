#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportHttpSavepointCase
fromflectra.addons.sale_product_configurator.tests.commonimportTestProductConfiguratorCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTestUi(HttpSavepointCase,TestProductConfiguratorCommon):

    deftest_01_admin_shop_custom_attribute_value_tour(self):
        #fixrunbot,sometimesonepricelistischosen,sometimestheother...
        pricelists=self.env['website'].get_current_website().get_current_pricelist()|self.env.ref('product.list0')
        self._create_pricelist(pricelists)
        self.start_tour("/",'a_shop_custom_attribute_value',login="admin")
