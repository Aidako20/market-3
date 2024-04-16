#-*-coding:utf-8-*-
fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.testsimporttagged


@tagged('post_install','-at_install')
classTaxReportTest(AccountTestInvoicingCommon):

    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.test_country_1=cls.env['res.country'].create({
            'name':"TheOldWorld",
            'code':'YY',
        })

        cls.test_country_2=cls.env['res.country'].create({
            'name':"ThePrincipalityofZeon",
            'code':'ZZ',
        })
        cls.test_country_3=cls.env['res.country'].create({
            'name':"Alagaësia",
            'code':'QQ',
        })

        cls.tax_report_1=cls.env['account.tax.report'].create({
            'name':"Taxreport1",
            'country_id':cls.test_country_1.id,
        })

        cls.tax_report_line_1_1=cls.env['account.tax.report.line'].create({
            'name':"[01]Line01",
            'tag_name':'01',
            'report_id':cls.tax_report_1.id,
            'sequence':2,
        })

        cls.tax_report_line_1_2=cls.env['account.tax.report.line'].create({
            'name':"[01]Line02",
            'tag_name':'02',
            'report_id':cls.tax_report_1.id,
            'sequence':3,
        })

        cls.tax_report_line_1_3=cls.env['account.tax.report.line'].create({
            'name':"[03]Line03",
            'tag_name':'03',
            'report_id':cls.tax_report_1.id,
            'sequence':4,
        })

        cls.tax_report_line_1_4=cls.env['account.tax.report.line'].create({
            'name':"[04]Line04",
            'report_id':cls.tax_report_1.id,
            'sequence':5,
        })

        cls.tax_report_line_1_5=cls.env['account.tax.report.line'].create({
            'name':"[05]Line05",
            'report_id':cls.tax_report_1.id,
            'sequence':6,
        })

        cls.tax_report_line_1_55=cls.env['account.tax.report.line'].create({
            'name':"[55]Line55",
            'tag_name':'55',
            'report_id':cls.tax_report_1.id,
            'sequence':7,
        })

        cls.tax_report_line_1_6=cls.env['account.tax.report.line'].create({
            'name':"[100]Line100",
            'tag_name':'100',
            'report_id':cls.tax_report_1.id,
            'sequence':8,
        })

        cls.tax_report_2=cls.env['account.tax.report'].create({
            'name':"Taxreport2",
            'country_id':cls.test_country_1.id,
        })

        cls.tax_report_line_2_1=cls.env['account.tax.report.line'].create({
            'name':"[01]Line01,butinreport2",
            'tag_name':'01',
            'report_id':cls.tax_report_2.id,
            'sequence':1,
        })

        cls.tax_report_line_2_2=cls.env['account.tax.report.line'].create({
            'name':"[02]Line02,butinreport2",
            'report_id':cls.tax_report_2.id,
            'sequence':2,
        })

        cls.tax_report_line_2_42=cls.env['account.tax.report.line'].create({
            'name':"[42]Line42",
            'tag_name':'42',
            'report_id':cls.tax_report_2.id,
            'sequence':3,
        })

        cls.tax_report_line_2_6=cls.env['account.tax.report.line'].create({
            'name':"[100]Line100",
            'tag_name':'100',
            'report_id':cls.tax_report_2.id,
            'sequence':4,
        })

    def_get_tax_tags(self,tag_name=None,active_test=True):
        domain=[('country_id','=',self.test_country_1.id),('applicability','=','taxes')]
        iftag_name:
            domain.append(('name','like','_'+tag_name))
        returnself.env['account.account.tag'].with_context(active_test=active_test).search(domain)

    deftest_write_add_tagname(self):
        """Addingatag_nametoalinewithoutanyshouldcreatenewtags.
        """
        tags_before=self._get_tax_tags()
        self.tax_report_line_2_2.tag_name='tournicoti'
        tags_after=self._get_tax_tags()

        self.assertEqual(len(tags_after),len(tags_before)+2,"Twotagsshouldhavebeencreated,+tournicotiand-tournicoti.")

    deftest_write_single_line_tagname(self):
        """Writingonthetag_nameofalinewithanon-nulltag_nameusedin
        nootherlineshouldoverwritethenameoftheexistingtags.
        """
        start_tags=self._get_tax_tags()
        original_tag_name=self.tax_report_line_1_55.tag_name
        original_tags=self.tax_report_line_1_55.tag_ids
        self.tax_report_line_1_55.tag_name='Millesabords!'

        self.assertEqual(len(self._get_tax_tags(tag_name=original_tag_name)),0,"Theoriginaltagnameofthelineshouldnotcorrespondtoanytaganymore.")
        self.assertEqual(original_tags,self.tax_report_line_1_55.tag_ids,"Thetaxreportlineshouldstillbelinkedtothesametags.")
        self.assertEqual(len(self._get_tax_tags()),len(start_tags),"Nonewtagshouldhavebeencreated.")

    deftest_write_single_line_remove_tagname(self):
        """SettingNoneasthetag_nameofalinewithanon-nulltag_nameused
        inauniquelineshoulddeletethetags,alsoremovingallthereferencestoit
        fromtaxrepartitionlinesandaccountmovelines
        """

        test_tax=self.env['account.tax'].create({
            'name':"Testtax",
            'amount_type':'percent',
            'amount':25,
            'type_tax_use':'sale',
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                }),

                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'tag_ids':[(6,0,self.tax_report_line_1_55.tag_ids[0].ids)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                }),

                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                }),
            ],
        })

        test_invoice=self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':self.partner_a.id,
            'date':'1992-12-22',
            'invoice_line_ids':[
                (0,0,{'quantity':1,'price_unit':42,'tax_ids':[(6,0,test_tax.ids)]}),
            ],
        })
        test_invoice.action_post()

        self.assertTrue(any(line.tax_tag_ids==self.tax_report_line_1_55.tag_ids[0]forlineintest_invoice.line_ids),"Thetestinvoiceshouldcontainataxlinewithtag55")
        tag_name_before=self.tax_report_line_1_55.tag_name
        tag_nber_before=len(self._get_tax_tags())
        self.tax_report_line_1_55.tag_name=None
        self.assertFalse(self.tax_report_line_1_55.tag_name,"Thetagnameforline55shouldnowbeNone")
        self.assertEqual(len(self._get_tax_tags(tag_name=tag_name_before)),0,"Noneoftheoriginaltagsforthislineshouldbeleftaftersettingtag_nametoNoneifnootherlinewasusingthistag_name.")
        self.assertEqual(len(self._get_tax_tags()),tag_nber_before-2,"Nonewtagshouldhavebeencreated,andthetwothatwereassignedtothereportlineshouldhavebeenremoved.")
        self.assertFalse(test_tax.mapped('invoice_repartition_line_ids.tag_ids'),"Thereshouldbenotagleftontesttax'srepartitionlinesaftertheremovaloftag55.")
        self.assertFalse(test_invoice.mapped('line_ids.tax_tag_ids'),"Thelinkbetweentestinvoiceandtag55shouldhavebeenbroken.Thereshouldbenotagleftontheinvoice'slines.")

    deftest_write_multi_no_change(self):
        """Writingthesametag_nameastheyalreadyuseonasetoftaxreport
        lineswiththesametag_nameshouldnotdoanything.
        """
        tags_before=self._get_tax_tags().ids
        (self.tax_report_line_1_1+self.tax_report_line_2_1).write({'tag_name':'01'})
        tags_after=self._get_tax_tags().ids
        self.assertEqual(tags_before,tags_after,"Re-assigningthesametag_nameshouldkeepthesametags.")

    deftest_edit_line_shared_tags(self):
        """Settingthetag_nameofataxreportlinesharingitstagswithanotherline
        shouldeditthetags'nameandthetag_nameofthisotherreportline,to
        keepconsistency.
        """
        original_tag_name=self.tax_report_line_1_1.tag_name
        self.tax_report_line_1_1.tag_name='Groucha'
        self.assertEqual(self.tax_report_line_2_1.tag_name,self.tax_report_line_1_1.tag_name,"Modifyingthetagnameofataxreportlinesharingitwithanotheroneshouldalsomodifytheother's.")

    deftest_edit_multi_line_tagname_all_different_new(self):
        """Writingatag_nameonmultiplelineswithdistincttag_namesshould
        deletealltheformertagsandreplacethembynewones(alsoonlines
        sharingtagswiththem).
        """
        lines=self.tax_report_line_1_1+self.tax_report_line_2_2+self.tax_report_line_2_42
        previous_tag_ids=lines.mapped('tag_ids.id')
        lines.write({'tag_name':'crabe'})
        new_tags=lines.mapped('tag_ids')

        self.assertNotEqual(new_tags.ids,previous_tag_ids,"Allthetagsshouldhavechanged")
        self.assertEqual(len(new_tags),2,"Onlytwodistincttagsshouldbeassignedtoallthelinesafterwritingtag_nameonthemall")
        surviving_tags=self.env['account.account.tag'].search([('id','in',previous_tag_ids)])
        self.assertEqual(len(surviving_tags),0,"Allformertagsshouldhavebeendeleted")
        self.assertEqual(self.tax_report_line_1_1.tag_ids,self.tax_report_line_2_1.tag_ids,"Thereportlinesinitiallysharingtheirtag_namewiththewritten-onlinesshouldalsohavebeenimpacted")

    deftest_remove_line_dependency(self):
        """SettingtoNonethetag_nameofareportlinesharingitstagswith
        otherlinesshouldonlyimpactthisline;theotheronesshouldkeeptheir
        linktotheinitialtags(theirtag_namewillhencedifferintheend).
        """
        tags_before=self.tax_report_line_1_1.tag_ids
        self.tax_report_line_1_1.tag_name=None
        self.assertEqual(len(self.tax_report_line_1_1.tag_ids),0,"Settingthetag_nametoNoneshouldhaveremovedthetags.")
        self.assertEqual(self.tax_report_line_2_1.tag_ids,tags_before,"Settingtag_nametoNoneonalinelinkedtoanotheroneviatag_nameshouldbreakthislink.")

    deftest_tax_report_change_country(self):
        """Teststhatduplicatingandmodifyingthecountryofataxreportworks
        asintended(countrieswantingtousethetaxreportofanother
        countryneedthat).
        """
        #Copyourfirstreport
        tags_before=self._get_tax_tags().ids
        copied_report_1=self.tax_report_1.copy()
        copied_report_2=self.tax_report_1.copy()
        tags_after=self._get_tax_tags().ids
        self.assertEqual(tags_before,tags_after,"Reportduplicationshouldnotcreateorremoveanytag")

        fororiginal,copyinzip(self.tax_report_1.get_lines_in_hierarchy(),copied_report_1.get_lines_in_hierarchy()):
            self.assertEqual(original.tag_ids,copy.tag_ids,"Copyingthelinesofataxreportshouldkeepthesametagsonlines")

        #Assignanothercountrytooneofthecopies
        copied_report_1.country_id=self.test_country_2
        fororiginal,copyinzip(self.tax_report_1.get_lines_in_hierarchy(),copied_report_1.get_lines_in_hierarchy()):
            iforiginal.tag_idsorcopy.tag_ids:
                self.assertNotEqual(original.tag_ids,copy.tag_ids,"Changingthecountryofacopiedreportshouldcreatebrandnewtagsforallofitslines")

        fororiginal,copyinzip(self.tax_report_1.get_lines_in_hierarchy(),copied_report_2.get_lines_in_hierarchy()):
            self.assertEqual(original.tag_ids,copy.tag_ids,"Changingthecountryofacopiedreportshouldnotimpacttheothercopiesortheoriginalreport")


        #Direcltychangethecountryofareportwithoutcopyingitfirst(someofitstagsareshared,butnotall)
        original_report_2_tags={line.id:line.tag_ids.idsforlineinself.tax_report_2.get_lines_in_hierarchy()}
        self.tax_report_2.country_id=self.test_country_2
        forlineinself.tax_report_2.get_lines_in_hierarchy():
            ifline==self.tax_report_line_2_42:
                #Thislineistheonlyoneofthereportnotsharingitstags
                self.assertEqual(line.tag_ids.ids,original_report_2_tags[line.id],"Thetaxreportlinesnotsharingtheirtagswithanyotherreportshouldkeepthesametagswhenthecountryoftheirreportischanged")
            elifline.tag_idsororiginal_report_2_tags[line.id]:
                self.assertNotEqual(line.tag_ids.ids,original_report_2_tags[line.id],"Thetaxreportlinessharingtheirtagswithotherreportshouldreceivenewtagswhenthecountryoftheirreportischanged")

    deftest_unlink_report_line_tags(self):
        """Undercertaincircumstances,unlinkingataxreportlineshouldalsounlink
        thetagsthatarelinkedtoit.Wetestthosecaseshere.
        """
        defcheck_tags_unlink(tag_name,report_lines,unlinked,error_message):
            report_lines.unlink()
            surviving_tags=self._get_tax_tags(tag_name=tag_name)
            required_len=0ifunlinkedelse2#2for+and-tag
            self.assertEqual(len(surviving_tags),required_len,error_message)

        check_tags_unlink('42',self.tax_report_line_2_42,True,"Unlinkingonelinenotsharingitstagsshouldalsounlinkthem")
        check_tags_unlink('01',self.tax_report_line_1_1,False,"Unlinkingonelinesharingitstagswithothersshouldkeepthetags")
        check_tags_unlink('100',self.tax_report_line_1_6+self.tax_report_line_2_6,True,"Unlinkinkallthelinessharingthesametagsshouldalsounlinkthem")

    deftest_unlink_report_line_tags_used_by_amls(self):
        """
        Deletionofareportlinewhosetagsarestillreferencedbyanamlshouldarchivetagsandnotdeletethem.
        """
        test_tax=self.env['account.tax'].create({
            'name':"Testtax",
            'amount_type':'percent',
            'amount':25,
            'type_tax_use':'sale',
            'invoice_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                }),

                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                    'tag_ids':[(6,0,self.tax_report_line_1_55.tag_ids.filtered(lambdatag:nottag.tax_negate).ids)],
                }),
            ],
            'refund_repartition_line_ids':[
                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'base',
                }),

                (0,0,{
                    'factor_percent':100,
                    'repartition_type':'tax',
                }),
            ],
        })

        test_invoice=self.env['account.move'].create({
            'move_type':'out_invoice',
            'partner_id':self.partner_a.id,
            'date':'1992-12-22',
            'invoice_line_ids':[
                (0,0,{'quantity':1,'price_unit':42,'tax_ids':[(6,0,test_tax.ids)]}),
            ],
        })
        test_invoice.action_post()

        tag_name=self.tax_report_line_1_55.tag_name
        self.tax_report_line_1_55.unlink()
        tags_after=self._get_tax_tags(tag_name=tag_name,active_test=False)
        #onlythe+tag_nameshouldbekept(andarchived),-tag_nameshouldbeunlinked
        self.assertEqual(tags_after.mapped('tax_negate'),[False],"Unlinkingareportlineshouldkeepthetagifitwasusedonmovelines,andunlinkitotherwise.")
        self.assertEqual(tags_after.mapped('active'),[False],"Unlinkingareportlineshouldarchivethetagifitwasusedonmovelines,andunlinkitotherwise.")
        self.assertEqual(len(test_tax.invoice_repartition_line_ids.tag_ids),0,"Afteratagisarchiveditshouldn'tbeontaxrepartitionlines.")

    deftest_unlink_report_line_tags_used_by_other_report_line(self):
        """
        Deletionofareportlinewhosetagsarestillreferencedinotherreportlineshouldnotdeletenorarchivetags.
        """
        tag_name=self.tax_report_line_1_1.tag_name #tag"O1"isusedinbothline1.1andline2.1
        tags_before=self._get_tax_tags(tag_name=tag_name,active_test=False)
        tags_archived_before=tags_before.filtered(lambdatag:nottag.active)
        self.tax_report_line_1_1.unlink()
        tags_after=self._get_tax_tags(tag_name=tag_name,active_test=False)
        tags_archived_after=tags_after.filtered(lambdatag:nottag.active)
        self.assertEqual(len(tags_after),len(tags_before),"Unlinkingareportlinewhosetagsareusedbyanotherlineshouldnotdeletethem.")
        self.assertEqual(len(tags_archived_after),len(tags_archived_before),"Unlinkingareportlinewhosetagsareusedbyanotherlineshouldnotarchivethem.")

    deftest_tag_recreation_archived(self):
        """
        Inasituationwherewehaveonlyoneofthetwo(+and-)signthatexist
        wewantonlythemissingsigntobere-createdifwetrytoreusethesametagname.
        (Wecangetintothisstatewhenonlyoneofthesignswasusedbyaml:thenwearchiveditanddeletedthecomplement.)
        """
        tag_name=self.tax_report_line_1_55.tag_name
        tags_before=self._get_tax_tags(tag_name=tag_name,active_test=False)
        tags_before[0].unlink() #weunlinkoneandarchivetheother,doesn'tmatterwhichone
        tags_before[1].active=False
        self.env['account.tax.report.line'].create({
            'name':"[55]Line55bis",
            'tag_name':tag_name,
            'report_id':self.tax_report_1.id,
            'sequence':9,
        })
        tags_after=self._get_tax_tags(tag_name=tag_name,active_test=False)
        self.assertEqual(len(tags_after),2,"Whencreatingataxreportlinewithanarchivedtaganditscomplementdoesn'texist,itshouldbere-created.")
        self.assertEqual(
            tags_after.mapped('name'),['+'+tag_name,'-'+tag_name],
            "Aftercreatingataxreportlinewithanarchivedtagandwhenitscomplementdoesn'texist,bothanegativeandapositivetagshould"
            "exist(themissingonebeingrecreated)."
        )
