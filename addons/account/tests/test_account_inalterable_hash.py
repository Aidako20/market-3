fromflectra.addons.account.tests.commonimportAccountTestInvoicingCommon
fromflectra.modelsimportModel
fromflectra.testsimporttagged
fromflectraimportfields
fromflectra.exceptionsimportUserError
fromflectra.toolsimportformat_date


@tagged('post_install','-at_install')
classTestAccountMoveInalterableHash(AccountTestInvoicingCommon):
    @classmethod
    defsetUpClass(cls,chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

    deftest_account_move_inalterable_hash(self):
        """Testthatwecannotalterafieldusedforthecomputationoftheinalterablehash"""
        self.company_data['default_journal_sale'].restrict_mode_hash_table=True
        move=self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000],post=True)

        withself.assertRaisesRegex(UserError,"Youcannotoverwritethevaluesensuringtheinalterabilityoftheaccounting."):
            move.inalterable_hash='fake_hash'
        withself.assertRaisesRegex(UserError,"Youcannotoverwritethevaluesensuringtheinalterabilityoftheaccounting."):
            move.secure_sequence_number=666
        withself.assertRaisesRegex(UserError,"Youcannoteditthefollowingfieldsduetorestrictmodebeingactivated.*"):
            move.name="fakename"
        withself.assertRaisesRegex(UserError,"Youcannoteditthefollowingfieldsduetorestrictmodebeingactivated.*"):
            move.date=fields.Date.from_string('2023-01-02')
        withself.assertRaisesRegex(UserError,"Youcannoteditthefollowingfieldsduetorestrictmodebeingactivated.*"):
            move.company_id=666
        withself.assertRaisesRegex(UserError,"Youcannoteditthefollowingfieldsduetorestrictmodebeingactivated.*"):
            move.write({
                'company_id':666,
                'date':fields.Date.from_string('2023-01-03')
            })

        withself.assertRaisesRegex(UserError,"Youcannoteditthefollowingfields.*Account.*"):
            move.line_ids[0].account_id=move.line_ids[1]['account_id']
        withself.assertRaisesRegex(UserError,"Youcannoteditthefollowingfields.*Partner.*"):
            move.line_ids[0].partner_id=666

        #Thefollowingfieldsarenotpartofthehashsotheycanbemodified
        move.invoice_date_due=fields.Date.from_string('2023-01-02')
        move.line_ids[0].date_maturity=fields.Date.from_string('2023-01-02')

    deftest_account_move_hash_integrity_report(self):
        """Testthehashintegrityreport"""
        moves=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-02",amounts=[1000,2000])
        )
        moves.action_post()

        #Norecordstobehashedbecausetherestrictmodeisnotactivatedyet
        integrity_check=moves.company_id._check_hash_integrity()['results'][0] #Firstjournal
        self.assertEqual(integrity_check['msg_cover'],'Thisjournalisnotinstrictmode.')

        #Norecordstobehashedeveniftherestrictmodeisactivatedbecausethehashingisnotretroactive
        self.company_data['default_journal_sale'].restrict_mode_hash_table=True
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],'Thereisn\'tanyjournalentryflaggedfordatainalterabilityyetforthisjournal.')

        #Everythingshouldbecorrectlyhashedandverified
        new_moves=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-03",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-04",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_a,"2023-01-05",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-06",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_a,"2023-01-07",amounts=[1000,2000])
        )
        new_moves.action_post()
        moves|=new_moves
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertRegex(integrity_check['msg_cover'],f'Entriesarehashedfrom{moves[2].name}.*')
        self.assertEqual(integrity_check['first_move_date'],format_date(self.env,fields.Date.to_string(moves[2].date)))
        self.assertEqual(integrity_check['last_move_date'],format_date(self.env,fields.Date.to_string(moves[-1].date)))

        #Let'schangeoneofthefieldsusedbythehash.Itshouldbedetectedbytheintegrityreport.
        #Weneedtobypassthewritemethodofaccount.movetodoso.
        Model.write(moves[4],{'date':fields.Date.from_string('2023-01-07')})
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves[4].id}.')

        #Let'strywiththeoneofthesubfields
        Model.write(moves[4],{'date':fields.Date.from_string("2023-01-05")}) #Revertthepreviouschange
        Model.write(moves[-1].line_ids[0],{'partner_id':self.partner_b.id})
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves[-1].id}.')

        #Let'strywiththeinalterable_hashfielditself
        Model.write(moves[-1].line_ids[0],{'partner_id':self.partner_a.id}) #Revertthepreviouschange
        Model.write(moves[-1],{'inalterable_hash':'fake_hash'})
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves[-1].id}.')

    deftest_account_move_hash_versioning_1(self):
        """Weareupdatingthehashalgorithm.Wewanttomakesurethatwedonotbreaktheintegrityreport.
        Thistestfocusesonthecasewheretheuserhasonlymoveswiththeoldhashalgorithm."""
        self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000],post=True) #Nothashed
        self.company_data['default_journal_sale'].restrict_mode_hash_table=True
        moves=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-02",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-03",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-04",amounts=[1000,2000])
        )
        moves.with_context(hash_version=1).action_post()
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertRegex(integrity_check['msg_cover'],f'Entriesarehashedfrom{moves[0].name}.*')
        self.assertEqual(integrity_check['first_move_date'],format_date(self.env,fields.Date.to_string(moves[0].date)))
        self.assertEqual(integrity_check['last_move_date'],format_date(self.env,fields.Date.to_string(moves[-1].date)))

        #Let'schangeoneofthefieldsusedbythehash.Itshouldbedetectedbytheintegrityreport
        #independentlyofthehashversionused.I.e.wefirsttrythev1hash,thenthev2hashandneithershouldwork.
        #Weneedtobypassthewritemethodofaccount.movetodoso.
        Model.write(moves[1],{'date':fields.Date.from_string('2023-01-07')})
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves[1].id}.')

    deftest_account_move_hash_versioning_2(self):
        """Weareupdatingthehashalgorithm.Wewanttomakesurethatwedonotbreaktheintegrityreport.
        Thistestfocusesonthecasewheretheuserhasonlymoveswiththenewhashalgorithm."""
        self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000],post=True) #Nothashed
        self.company_data['default_journal_sale'].restrict_mode_hash_table=True
        moves=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-02",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-03",amounts=[1000,2000])
        )
        moves.action_post()
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertRegex(integrity_check['msg_cover'],f'Entriesarehashedfrom{moves[0].name}.*')
        self.assertEqual(integrity_check['first_move_date'],format_date(self.env,fields.Date.to_string(moves[0].date)))
        self.assertEqual(integrity_check['last_move_date'],format_date(self.env,fields.Date.to_string(moves[-1].date)))

        #Let'schangeoneofthefieldsusedbythehash.Itshouldbedetectedbytheintegrityreport
        #independentlyofthehashversionused.I.e.wefirsttrythev1hash,thenthev2hashandneithershouldwork.
        #Weneedtobypassthewritemethodofaccount.movetodoso.
        Model.write(moves[1],{'date':fields.Date.from_string('2023-01-07')})
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves[1].id}.')

    deftest_account_move_hash_versioning_v1_to_v2(self):
        """Weareupdatingthehashalgorithm.Wewanttomakesurethatwedonotbreaktheintegrityreport.
        Thistestfocusesonthecasewheretheuserhasmoveswithbothhashalgorithms."""
        self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000],post=True) #Nothashed
        self.company_data['default_journal_sale'].restrict_mode_hash_table=True
        moves_v1=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-02",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-03",amounts=[1000,2000])
        )
        moves_v1.with_context(hash_version=1).action_post()
        fields_v1=moves_v1.with_context(hash_version=1)._get_integrity_hash_fields()
        moves_v2=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-01",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-02",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-03",amounts=[1000,2000])
        )
        moves_v2.with_context(hash_version=2).action_post()
        fields_v2=moves_v2._get_integrity_hash_fields()
        self.assertNotEqual(fields_v1,fields_v2) #Makesuretwodifferenthashalgorithmswereused

        moves=moves_v1|moves_v2
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertRegex(integrity_check['msg_cover'],f'Entriesarehashedfrom{moves[0].name}.*')
        self.assertEqual(integrity_check['first_move_date'],format_date(self.env,fields.Date.to_string(moves[0].date)))
        self.assertEqual(integrity_check['last_move_date'],format_date(self.env,fields.Date.to_string(moves[-1].date)))

        #Let'schangeoneofthefieldsusedbythehash.Itshouldbedetectedbytheintegrityreport
        #independentlyofthehashversionused.I.e.wefirsttrythev1hash,thenthev2hashandneithershouldwork.
        #Weneedtobypassthewritemethodofaccount.movetodoso.
        Model.write(moves[4],{'date':fields.Date.from_string('2023-01-07')})
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves[4].id}.')

        #Let'srevertthechangeandmakesurethatwecannotusethev1afterthev2.
        #Thismeanswedon'tsimplycheckwhetherthemoveiscorrectlyhashedwitheitheralgorithms,
        #butthatwecanonlyusev2afterv1andnotgobacktov1afterwards.
        Model.write(moves[4],{'date':fields.Date.from_string("2023-01-02")}) #Revertthepreviouschange
        moves_v1_bis=(
            self.init_invoice("out_invoice",self.partner_a,"2023-01-10",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-11",amounts=[1000,2000])
            |self.init_invoice("out_invoice",self.partner_b,"2023-01-12",amounts=[1000,2000])
        )
        moves_v1_bis.with_context(hash_version=1).action_post()
        integrity_check=moves.company_id._check_hash_integrity()['results'][0]
        self.assertEqual(integrity_check['msg_cover'],f'Corrupteddataonjournalentrywithid{moves_v1_bis[0].id}.')
