#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.testsimportTransactionCase
fromflectra.exceptionsimportUserError

importflectra.tests


@flectra.tests.tagged('external','-standard')
classTestGeoLocalize(TransactionCase):

    deftest_default_openstreetmap(self):
        """Testthatopenstreetmaplocalizeserviceworks."""
        test_partner=self.env.ref('base.res_partner_2')
        test_partner.geo_localize()
        self.assertTrue(test_partner.partner_longitude)
        self.assertTrue(test_partner.partner_latitude)
        self.assertTrue(test_partner.date_localization)

        #wedon'tcheckherethatthelocalizationisatrightplace
        #butjustthatresultisrealisticfloatcoordonates
        self.assertTrue(float(test_partner.partner_longitude)!=0.0)
        self.assertTrue(float(test_partner.partner_latitude)!=0.0)

    deftest_googlemap_without_api_key(self):
        """WithoutprovidingAPIkeytogooglemaps,
        theservicedoesn'twork."""
        test_partner=self.env.ref('base.res_partner_address_4')
        google_map=self.env.ref('base_geolocalize.geoprovider_google_map').id
        self.env['ir.config_parameter'].set_param('base_geolocalize.geo_provider',google_map)
        withself.assertRaises(UserError):
            test_partner.geo_localize()
        self.assertFalse(test_partner.partner_longitude)
        self.assertFalse(test_partner.partner_latitude)
        self.assertFalse(test_partner.date_localization)
