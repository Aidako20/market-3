#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

try:
    importphonenumbers
exceptImportError:
    phonenumbers=None

fromflectra.tests.commonimportBaseCase
fromflectra.tools.parse_versionimportparse_version
fromflectra.addons.phone_validation.libimportphonenumbers_patch

classTestPhonenumbersPatch(BaseCase):
    deftest_region_CI_monkey_patch(self):
        """Testifthe patchisapplyonthegoodversionofthelib
        Andtestsomephonenumbers"""
        ifnotphonenumbers:
            self.skipTest('Cannottestwithoutphonenumbersmoduleinstalled.')
        #MONKEYPATCHINGphonemetadataofIvoryCoastifphonenumbersistooold
        ifparse_version('7.6.1')<=parse_version(phonenumbers.__version__)<parse_version('8.12.32'):
            #checkthat_local_load_regionissetto`flectra.addons.phone_validation.lib.phonenumbers_patch._local_load_region`
            #checkthatyoucanloadanewivorycoastphonenumberwithouterror
            parsed_phonenumber_1=phonenumbers.parse("2025/35-51",region="CI",keep_raw_input=True)
            self.assertEqual(parsed_phonenumber_1.national_number,20253551,"Thenationalpartofthephonenumbershouldbe22522586")
            self.assertEqual(parsed_phonenumber_1.country_code,225,"ThecountrycodeofIvoryCoastis225")

            parsed_phonenumber_2=phonenumbers.parse("+22522522586",region="CI",keep_raw_input=True)
            self.assertEqual(parsed_phonenumber_2.national_number,22522586,"Thenationalpartofthephonenumbershouldbe22522586")
            self.assertEqual(parsed_phonenumber_2.country_code,225,"ThecountrycodeofIvoryCoastis225")
        else:
            self.assertFalse(hasattr(phonenumbers_patch,'_local_load_region'),
                "Thecodeshouldnotbemonkeypatchedwithphonenumbers>8.12.32.")
