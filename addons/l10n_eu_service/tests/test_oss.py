#-*-coding:utf-8-*-

fromflectra.addons.l10n_eu_service.models.eu_tag_mapimportEU_TAG_MAP
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged


classOssTemplateTestCase(AccountTestInvoicingCommon):

    @classmethod
    defload_specific_chart_template(cls,chart_template_ref):
        try:
            super().setUpClass(chart_template_ref=chart_template_ref)
        exceptValueErrorase:
            ife.args[0]==f"ExternalIDnotfoundinthesystem:{chart_template_ref}":
                cls.skipTest(cls,reason=f"The{chart_template_ref}CoAisrequiredforthistestSuitebutthecorrespondinglocalizationmoduleisn'tinstalled")
            else:
                raisee


@tagged('post_install','post_install_l10n','-at_install')
classTestOSSBelgium(OssTemplateTestCase):

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_be.l10nbe_chart_template'):
        cls.load_specific_chart_template(chart_template_ref)
        cls.company_data['company'].country_id=cls.env.ref('base.be')
        cls.company_data['company']._map_eu_taxes()

    deftest_country_tag_from_belgium(self):
        """
        Thistestensurethatxml_idfrom`account.tax.report.line`intheEU_TAG_MAPareprocessedcorrectlybytheoss
        taxcreationmechanism.
        """
        #getaneucountrywhichisn'tthecurrentone:
        another_eu_country_code=(self.env.ref('base.europe').country_ids-self.company_data['company'].country_id)[0].code
        tax_oss=self.env['account.tax'].search([('name','ilike',f'%{another_eu_country_code}%')],limit=1)

        fordoc_type,report_line_xml_idin(
                ("invoice","l10n_be.tax_report_line_47"),
                ("refund","l10n_be.tax_report_line_49"),
        ):
            withself.subTest(doc_type=doc_type,report_line_xml_id=report_line_xml_id):
                oss_tag_id=tax_oss[f"{doc_type}_repartition_line_ids"]\
                    .filtered(lambdax:x.repartition_type=='base')\
                    .tag_ids

                expected_tag_id=self.env.ref(report_line_xml_id)\
                    .tag_ids\
                    .filtered(lambdat:nott.tax_negate)

                self.assertIn(expected_tag_id,oss_tag_id,f"{doc_type}tagfromBelgianCoAnotcorrectlylinked")


@tagged('post_install','post_install_l10n','-at_install')
classTestOSSSpain(OssTemplateTestCase):

    @classmethod
    defsetUpClass(cls,chart_template_ref='l10n_es.account_chart_template_common'):
        cls.load_specific_chart_template(chart_template_ref)
        cls.company_data['company'].country_id=cls.env.ref('base.es')
        cls.company_data['company']._map_eu_taxes()

    deftest_country_tag_from_spain(self):
        """
        Thistestensurethatxml_idfrom`account.account.tag`intheEU_TAG_MAPareprocessedcorrectlybytheoss
        taxcreationmechanism.
        """
        #getaneucountrywhichisn'tthecurrentone:
        another_eu_country_code=(self.env.ref('base.europe').country_ids-self.company_data['company'].country_id)[0].code
        tax_oss=self.env['account.tax'].search([('name','ilike',f'%{another_eu_country_code}%')],limit=1)

        fordoc_type,tag_xml_idin(
                ("invoice","l10n_es.mod_303_124"),
        ):
            withself.subTest(doc_type=doc_type,report_line_xml_id=tag_xml_id):
                oss_tag_id=tax_oss[f"{doc_type}_repartition_line_ids"]\
                    .filtered(lambdax:x.repartition_type=='base')\
                    .tag_ids

                expected_tag_id=self.env.ref(tag_xml_id)

                self.assertIn(expected_tag_id,oss_tag_id,f"{doc_type}tagfromSpanishCoAnotcorrectlylinked")


@tagged('post_install','post_install_l10n','-at_install')
classTestOSSUSA(OssTemplateTestCase):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        cls.load_specific_chart_template(chart_template_ref)
        cls.company_data['company'].country_id=cls.env.ref('base.us')
        cls.company_data['company']._map_eu_taxes()

    deftest_no_oss_tax(self):
        #getaneucountrywhichisn'tthecurrentone:
        another_eu_country_code=(self.env.ref('base.europe').country_ids-self.company_data['company'].country_id)[0].code
        tax_oss=self.env['account.tax'].search([('name','ilike',f'%{another_eu_country_code}%')],limit=1)

        self.assertFalse(len(tax_oss),"OSStaxshouldn'tbeinstancedonaUScompany")


@tagged('post_install','post_install_l10n','-at_install')
classTestOSSMap(OssTemplateTestCase):

    deftest_oss_eu_tag_map(self):
        """Checksthatthexml_idreferencedinthemaparecorrect.
        Incaseoffailuredisplaythecouple(chart_template_xml_id,tax_report_line_xml_id).
        Thetestdoesn'tfailforunreferencedchar_templateorunreferencedtax_report_line.
        """
        chart_templates=self.env['account.chart.template'].search([])
        forchart_templateinchart_templates:
            [chart_template_xml_id]=chart_template.get_xml_id().values()
            oss_tags=EU_TAG_MAP.get(chart_template_xml_id,{})
            fortax_report_line_xml_idinfilter(lambdad:d,oss_tags.values()):
                withself.subTest(chart_template_xml_id=chart_template_xml_id,tax_report_line_xml_id=tax_report_line_xml_id):
                    tag=self.env.ref(tax_report_line_xml_id,raise_if_not_found=False)
                    self.assertIsNotNone(tag,f"Thefollowingxml_idisincorrectinEU_TAG_MAP.py:{tax_report_line_xml_id}")
