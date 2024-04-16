#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportMailCommon
fromflectra.tests.commonimportForm,users
fromflectra.testsimporttagged


@tagged('res_partner')
classTestPartner(MailCommon):

    deftest_res_partner_find_or_create(self):
        Partner=self.env['res.partner']

        existing=Partner.create({
            'name':'PatrickPoilvache',
            'email':'"PatrickDaBeastPoilvache"<PATRICK@example.com>',
        })
        self.assertEqual(existing.name,'PatrickPoilvache')
        self.assertEqual(existing.email,'"PatrickDaBeastPoilvache"<PATRICK@example.com>')
        self.assertEqual(existing.email_normalized,'patrick@example.com')

        new=Partner.find_or_create('PatrickCaché<patrick@EXAMPLE.COM>')
        self.assertEqual(new,existing)

        new2=Partner.find_or_create('PatrickCaché<2patrick@EXAMPLE.COM>')
        self.assertTrue(new2.id>new.id)
        self.assertEqual(new2.name,'PatrickCaché')
        self.assertEqual(new2.email,'2patrick@example.com')
        self.assertEqual(new2.email_normalized,'2patrick@example.com')

    @users('admin')
    deftest_res_partner_find_or_create_email(self):
        """Test'find_or_create'toolusedinmail,notablywhenlinkingemails
        foundinrecipientstopartnerswhensendingemailsusingthemail
        composer."""
        partners=self.env['res.partner'].create([
            {
                'email':'classic.format@test.example.com',
                'name':'ClassicFormat',
            },
            {
                'email':'"FindMeFormat"<find.me.format@test.example.com>',
                'name':'FindMeFormat',
            },{
                'email':'find.me.multi.1@test.example.com,"FindMeMulti"<find.me.multi.2@test.example.com>',
                'name':'FindMeMulti',
            },
        ])
        #checkdatausedforfinding/searching
        self.assertEqual(
            partners.mapped('email_formatted'),
            ['"ClassicFormat"<classic.format@test.example.com>',
             '"FindMeFormat"<find.me.format@test.example.com>',
             '"FindMeMulti"<find.me.multi.1@test.example.com,find.me.multi.2@test.example.com>']
        )
        #whenhavingmultiemails,firstfoundoneistakenasnormalizedemail
        self.assertEqual(
            partners.mapped('email_normalized'),
            ['classic.format@test.example.com','find.me.format@test.example.com',
             'find.me.multi.1@test.example.com']
        )

        #classicfindorcreate:usenormalizedemailtocomparerecords
        foremailin('CLASSIC.FORMAT@TEST.EXAMPLE.COM','"AnotherName"<classic.format@test.example.com>'):
            withself.subTest(email=email):
                self.assertEqual(self.env['res.partner'].find_or_create(email),partners[0])
        #findonencapsulatedemail:comparisonofnormalizedshouldwork
        foremailin('FIND.ME.FORMAT@TEST.EXAMPLE.COM','"DifferentFormat"<find.me.format@test.example.com>'):
            withself.subTest(email=email):
                self.assertEqual(self.env['res.partner'].find_or_create(email),partners[1])
        #multi-emails->nonormalizedemail->failseachtime,createnewpartner(FIXME)
        foremail_input,match_partnerin[
            ('find.me.multi.1@test.example.com',partners[2]),
            ('find.me.multi.2@test.example.com',self.env['res.partner']),
        ]:
            withself.subTest(email_input=email_input):
                partner=self.env['res.partner'].find_or_create(email_input)
                #eithermatchingexisting,eithernewpartner
                ifmatch_partner:
                    self.assertEqual(partner,match_partner)
                else:
                    self.assertNotIn(partner,partners)
                    self.assertEqual(partner.email,email_input)
                partner.unlink() #donotmesswithsubsequenttests

        #nowinputismultiemail->'_parse_partner_name'usedin'find_or_create'
        #beforetryingtonormalizeisquitetolerant,allowingpositivechecks
        foremail_input,match_partner,exp_email_partnerin[
            ('classic.format@test.example.com,another.email@test.example.com',
              partners[0],'classic.format@test.example.com'), #firstfoundemailmatchesexisting
            ('another.email@test.example.com,classic.format@test.example.com',
             self.env['res.partner'],'another.email@test.example.com'), #firstfoundemaildoesnotmatch
            ('find.me.multi.1@test.example.com,find.me.multi.2@test.example.com',
             self.env['res.partner'],'find.me.multi.1@test.example.com'),
        ]:
            withself.subTest(email_input=email_input):
                partner=self.env['res.partner'].find_or_create(email_input)
                #eithermatchingexisting,eithernewpartner
                ifmatch_partner:
                    self.assertEqual(partner,match_partner)
                else:
                    self.assertNotIn(partner,partners)
                self.assertEqual(partner.email,exp_email_partner)
                ifpartnernotinpartners:
                    partner.unlink() #donotmesswithsubsequenttests

    @users('admin')
    deftest_res_partner_merge_wizards(self):
        Partner=self.env['res.partner']

        p1=Partner.create({'name':'Customer1','email':'test1@test.example.com'})
        p1_msg_ids_init=p1.message_ids
        p2=Partner.create({'name':'Customer2','email':'test2@test.example.com'})
        p2_msg_ids_init=p2.message_ids
        p3=Partner.create({'name':'Other(dupemail)','email':'test1@test.example.com'})

        #addsomemailrelateddocuments
        p1.message_subscribe(partner_ids=p3.ids)
        p1_act1=p1.activity_schedule(act_type_xmlid='mail.mail_activity_data_todo')
        p1_msg1=p1.message_post(
            body='<p>LogonP1</p>',
            subtype_id=self.env.ref('mail.mt_comment').id
        )
        self.assertEqual(p1.activity_ids,p1_act1)
        self.assertEqual(p1.message_follower_ids.partner_id,self.partner_admin+p3)
        self.assertEqual(p1.message_ids,p1_msg_ids_init+p1_msg1)
        self.assertEqual(p2.activity_ids,self.env['mail.activity'])
        self.assertEqual(p2.message_follower_ids.partner_id,self.partner_admin)
        self.assertEqual(p2.message_ids,p2_msg_ids_init)

        MergeForm=Form(self.env['base.partner.merge.automatic.wizard'].with_context(
            active_model='res.partner',
            active_ids=(p1+p2).ids
        ))
        self.assertEqual(MergeForm.partner_ids[:],p1+p2)
        self.assertEqual(MergeForm.dst_partner_id,p2)
        merge_form=MergeForm.save()
        merge_form.action_merge()

        #checkdestinationandremoval
        self.assertFalse(p1.exists())
        self.assertTrue(p2.exists())
        #checkmaildocumentshavebeenmoved
        self.assertEqual(p2.activity_ids,p1_act1)
        #TDEnote:currentlynotworkingassoonasthereisasinglepartnerduplicated->shouldbeimproved
        #self.assertEqual(p2.message_follower_ids.partner_id,self.partner_admin+p3)
        all_msg=p2_msg_ids_init+p1_msg_ids_init+p1_msg1
        self.assertEqual(len(p2.message_ids),len(all_msg)+1,'Shouldhaveoriginalmessages+alog')
        self.assertTrue(all(msginp2.message_idsformsginall_msg))
