#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
fromflectra.tests.commonimportSavepointCase,tagged
fromflectra.exceptionsimportValidationError
fromunittest.mockimportpatch

importstdnum.eu.vat


classTestStructure(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        defcheck_vies(vat_number):
            return{'valid':vat_number=='BE0477472701'}

        super().setUpClass()
        cls.env.user.company_id.vat_check_vies=False
        cls._vies_check_func=check_vies

    deftest_peru_ruc_format(self):
        """Onlyvaluesthathasthelengthof11willbecheckedasRUC,that'swhatweareproving.Thesecondpart
        willcheckforavalidrucandtherewillbenoproblematall.
        """
        partner=self.env['res.partner'].create({'name':"Dummypartner",'country_id':self.env.ref('base.pe').id})

        withself.assertRaises(ValidationError):
            partner.vat='11111111111'
        partner.vat='20507822470'

    deftest_vat_country_difference(self):
        """Testthevalidationwhencountrycodeisdifferentfromvatcode"""
        partner=self.env['res.partner'].create({
            'name':"Test",
            'country_id':self.env.ref('base.mx').id,
            'vat':'RORO790707I47',
        })
        self.assertEqual(partner.vat,'RORO790707I47',"PartnerVATshouldnotbealtered")

    deftest_parent_validation(self):
        """Testthevalidationwithcompanyandcontact"""

        #setaninvalidvatnumber
        self.env.user.company_id.vat_check_vies=False
        company=self.env["res.partner"].create({
            "name":"WorldCompany",
            "country_id":self.env.ref("base.be").id,
            "vat":"ATU12345675",
            "company_type":"company",
        })

        #reactivateitandcorrectthevatnumber
        withpatch('flectra.addons.base_vat.models.res_partner.check_vies',type(self)._vies_check_func):
            self.env.user.company_id.vat_check_vies=True

    deftest_vat_syntactic_validation(self):
        """TestsVATvalidation(bothsuccessesandfailures),withthedifferentcountry
        detectioncasespossible.
        """
        test_partner=self.env['res.partner'].create({'name':"JohnDex"})

        #VATstartingwithcountrycode:usethestartingcountrycode
        test_partner.write({'vat':'BE0477472701','country_id':self.env.ref('base.fr').id})
        test_partner.write({'vat':'BE0477472701','country_id':None})

        withself.assertRaises(ValidationError):
            test_partner.write({'vat':'BE42','country_id':self.env.ref('base.fr').id})

        withself.assertRaises(ValidationError):
            test_partner.write({'vat':'BE42','country_id':None})

        #NocountrycodeinVAT:usethepartner'scountry
        test_partner.write({'vat':'0477472701','country_id':self.env.ref('base.be').id})

        withself.assertRaises(ValidationError):
            test_partner.write({'vat':'42','country_id':self.env.ref('base.be').id})

        #Ifnocountrycanbeguessed:VATnumbershouldalwaysbeconsideredvalid
        #(fortechnicalreasonsduetoORMandres.companymakingrelatedfieldstowardsres.partnerforcountry_idandvat)
        test_partner.write({'vat':'0477472701','country_id':None})

    deftest_vat_eu(self):
        """Foreigncompaniesthattradewithnon-enterprisesintheEUmayhaveaVATINstartingwith"EU"insteadof
        acountrycode.
        """
        test_partner=self.env['res.partner'].create({'name':"Turlututu",'country_id':self.env.ref('base.fr').id})
        test_partner.write({'vat':"EU528003646",'country_id':None})


@tagged('-standard','external')
classTestStructureVIES(TestStructure):
    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.env.user.company_id.vat_check_vies=True
        cls._vies_check_func=stdnum.eu.vat.check_vies
