#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromunittest.mockimportpatch

fromflectra.addons.test_mail.tests.commonimportTestMailCommon
fromflectra.tests.commonimporttagged
fromflectra.testsimportForm


@tagged('mail_track')
classTestTracking(TestMailCommon):

    defsetUp(self):
        super(TestTracking,self).setUp()

        record=self.env['mail.test.ticket'].with_user(self.user_employee).with_context(self._test_context).create({
            'name':'Test',
        })
        self.flush_tracking()
        self.record=record.with_context(mail_notrack=False)

    deftest_message_track_no_tracking(self):
        """Updateasetofnontrackedfields->nomessage,notracking"""
        self.record.write({
            'name':'Trackingornot',
            'count':32,
        })
        self.flush_tracking()
        self.assertEqual(self.record.message_ids,self.env['mail.message'])

    deftest_message_track_no_subtype(self):
        """Updatesometrackedfieldsnotlinkedtosomesubtype->messagewithonchange"""
        customer=self.env['res.partner'].create({'name':'Customer','email':'cust@example.com'})
        withself.mock_mail_gateway():
            self.record.write({
                'name':'Test2',
                'customer_id':customer.id,
            })
            self.flush_tracking()

        #onenewmessagecontainingtracking;withoutsubtypelinkedtotracking,anoteisgenerated
        self.assertEqual(len(self.record.message_ids),1)
        self.assertEqual(self.record.message_ids.subtype_id,self.env.ref('mail.mt_note'))

        #nospecificrecipientsexceptthosefollowingnotes,noemail
        self.assertEqual(self.record.message_ids.partner_ids,self.env['res.partner'])
        self.assertEqual(self.record.message_ids.notified_partner_ids,self.env['res.partner'])
        self.assertNotSentEmail()

        #verifytrackedvalue
        self.assertTracking(
            self.record.message_ids,
            [('customer_id','many2one',False,customer) #onchangetrackedfield
             ])

    deftest_message_track_subtype(self):
        """Updatesometrackedfieldslinkedtosomesubtype->messagewithonchange"""
        self.record.message_subscribe(
            partner_ids=[self.user_admin.partner_id.id],
            subtype_ids=[self.env.ref('test_mail.st_mail_test_ticket_container_upd').id]
        )

        container=self.env['mail.test.container'].with_context(mail_create_nosubscribe=True).create({'name':'Container'})
        self.record.write({
            'name':'Test2',
            'email_from':'noone@example.com',
            'container_id':container.id,
        })
        self.flush_tracking()
        #onenewmessagecontainingtracking;subtypelinkedtotracking
        self.assertEqual(len(self.record.message_ids),1)
        self.assertEqual(self.record.message_ids.subtype_id,self.env.ref('test_mail.st_mail_test_ticket_container_upd'))

        #nospecificrecipientsexceptthosefollowingcontainer
        self.assertEqual(self.record.message_ids.partner_ids,self.env['res.partner'])
        self.assertEqual(self.record.message_ids.notified_partner_ids,self.user_admin.partner_id)

        #verifytrackedvalue
        self.assertTracking(
            self.record.message_ids,
            [('container_id','many2one',False,container) #onchangetrackedfield
             ])

    deftest_message_track_template(self):
        """Updatesometrackedfieldslinkedtosometemplate->messagewithonchange"""
        self.record.write({'mail_template':self.env.ref('test_mail.mail_test_ticket_tracking_tpl').id})
        self.assertEqual(self.record.message_ids,self.env['mail.message'])

        withself.mock_mail_gateway():
            self.record.write({
                'name':'Test2',
                'customer_id':self.user_admin.partner_id.id,
            })
            self.flush_tracking()

        self.assertEqual(len(self.record.message_ids),2,'shouldhave2newmessages:onefortracking,onefortemplate')

        #onenewmessagecontainingthetemplatelinkedtotracking
        self.assertEqual(self.record.message_ids[0].subject,'TestTemplate')
        self.assertEqual(self.record.message_ids[0].body,'<p>HelloTest2</p>')

        #oneemailsendduetotemplate
        self.assertSentEmail(self.record.env.user.partner_id,[self.partner_admin],body='<p>HelloTest2</p>')

        #onenewmessagecontainingtracking;withoutsubtypelinkedtotracking
        self.assertEqual(self.record.message_ids[1].subtype_id,self.env.ref('mail.mt_note'))
        self.assertTracking(
            self.record.message_ids[1],
            [('customer_id','many2one',False,self.user_admin.partner_id) #onchangetrackedfield
             ])

    deftest_message_track_template_at_create(self):
        """Createarecordwithtrackingtemplateoncreate,templateshouldbesent."""

        Model=self.env['mail.test.ticket'].with_user(self.user_employee).with_context(self._test_context)
        Model=Model.with_context(mail_notrack=False)
        withself.mock_mail_gateway():
            record=Model.create({
                'name':'Test',
                'customer_id':self.user_admin.partner_id.id,
                'mail_template':self.env.ref('test_mail.mail_test_ticket_tracking_tpl').id,
            })
            self.flush_tracking()

        self.assertEqual(len(record.message_ids),1,'shouldhave1newmessagesfortemplate')
        #onenewmessagecontainingthetemplatelinkedtotracking
        self.assertEqual(record.message_ids[0].subject,'TestTemplate')
        self.assertEqual(record.message_ids[0].body,'<p>HelloTest</p>')
        #oneemailsendduetotemplate
        self.assertSentEmail(self.record.env.user.partner_id,[self.partner_admin],body='<p>HelloTest</p>')

    deftest_create_partner_from_tracking_multicompany(self):
        company1=self.env['res.company'].create({'name':'company1'})
        self.env.user.write({'company_ids':[(4,company1.id,False)]})
        self.assertNotEqual(self.env.company,company1)

        email_new_partner="diamonds@rust.com"
        Partner=self.env['res.partner']
        self.assertFalse(Partner.search([('email','=',email_new_partner)]))

        template=self.env['mail.template'].create({
            'model_id':self.env['ir.model']._get('mail.test.track').id,
            'name':'AutoTemplate',
            'subject':'autoresponse',
            'email_from':self.env.user.email_formatted,
            'email_to':"${object.email_from}",
            'body_html':"<div>Anicebody</div>",
        })

        defpatched_message_track_post_template(*args,**kwargs):
            ifargs[0]._name=="mail.test.track":
                args[0].message_post_with_template(template.id)
            returnTrue

        withpatch('flectra.addons.mail.models.mail_thread.MailThread._message_track_post_template',patched_message_track_post_template):
            self.env['mail.test.track'].create({
                'email_from':email_new_partner,
                'company_id':company1.id,
                'user_id':self.env.user.id,#triggertracktemplate
            })
            self.flush_tracking()

        new_partner=Partner.search([('email','=',email_new_partner)])
        self.assertTrue(new_partner)
        self.assertEqual(new_partner.company_id,company1)

    deftest_track_invalid_selection(self):
        #Test:Checkthatinitialinvalidselectionvaluesareallowedwhentracking
        #Createarecordwithaninitiallyinvalidselectionvalue
        invalid_value='Ilovewritingtests!'
        record=self.env['mail.test.track.selection'].create({
            'name':'TestInvalidSelectionValues',
            "type":"first",
        })

        self.flush_tracking()
        self.env.cr.execute(
            """
            UPDATEmail_test_track_selection
               SETtype=%s
             WHEREid=%s
            """,
            [invalid_value,record.id]
        )

        record.invalidate_cache()

        self.assertEqual(record.type,invalid_value)

        #Writeavalidselectionvalue
        record.type="second"

        self.flush_tracking()
        self.assertTracking(record.message_ids,[
            ('type','char',invalid_value,'Second'),
        ])

    deftest_track_template(self):
        #Test:Checkthatdefault_*keysarenottakenintoaccountin_message_track_post_template
        magic_code='Up-Up-Down-Down-Left-Right-Left-Right-Square-Triangle'

        mt_name_changed=self.env['mail.message.subtype'].create({
            'name':'MAGICCODEWOOPWOOP',
            'description':'SPECIALCONTENTUNLOCKED'
        })
        self.env['ir.model.data'].create({
            'name':'mt_name_changed',
            'model':'mail.message.subtype',
            'module':'mail',
            'res_id':mt_name_changed.id
        })
        mail_template=self.env['mail.template'].create({
            'name':'SPECIALCONTENTUNLOCKED',
            'subject':'SPECIALCONTENTUNLOCKED',
            'model_id':self.env.ref('test_mail.model_mail_test_container').id,
            'auto_delete':True,
            'body_html':'''<div>WOOPWOOP</div>''',
        })

        def_track_subtype(self,init_values):
            if'name'ininit_valuesandinit_values['name']==magic_code:
                return'mail.mt_name_changed'
            returnFalse
        self.registry('mail.test.container')._patch_method('_track_subtype',_track_subtype)

        def_track_template(self,changes):
            res={}
            if'name'inchanges:
                res['name']=(mail_template,{'composition_mode':'mass_mail'})
            returnres
        self.registry('mail.test.container')._patch_method('_track_template',_track_template)

        cls=type(self.env['mail.test.container'])
        self.assertFalse(hasattr(getattr(cls,'name'),'track_visibility'))
        getattr(cls,'name').track_visibility='always'

        @self.addCleanup
        defcleanup():
            delgetattr(cls,'name').track_visibility

        test_mail_record=self.env['mail.test.container'].create({
            'name':'Zizizatestmailname',
            'description':'Zizizatestmaildescription',
        })
        test_mail_record.with_context(default_parent_id=2147483647).write({'name':magic_code})

    deftest_message_track_multiple(self):
        """checkthatmultipleupdatesgenerateasingletrackingmessage"""
        container=self.env['mail.test.container'].with_context(mail_create_nosubscribe=True).create({'name':'Container'})
        self.record.name='Zboub'
        self.record.customer_id=self.user_admin.partner_id
        self.record.user_id=self.user_admin
        self.record.container_id=container
        self.flush_tracking()

        #shouldhaveasinglemessagewithalltrackedfields
        self.assertEqual(len(self.record.message_ids),1,'shouldhave1trackingmessage')
        self.assertTracking(self.record.message_ids[0],[
            ('customer_id','many2one',False,self.user_admin.partner_id),
            ('user_id','many2one',False,self.user_admin),
            ('container_id','many2one',False,container),
        ])

    deftest_tracked_compute(self):
        #notrackingatcreation
        record=self.env['mail.test.track.compute'].create({})
        self.flush_tracking()
        self.assertEqual(len(record.message_ids),1)
        self.assertEqual(len(record.message_ids[0].tracking_value_ids),0)

        #assignpartner_id:onetrackingmessageforthemodifiedfieldandall
        #thestoredandnon-storedcomputedfieldsontherecord
        partner=self.env['res.partner'].create({
            'name':'Foo',
            'email':'foo@example.com',
            'phone':'1234567890',
        })
        record.partner_id=partner
        self.flush_tracking()
        self.assertEqual(len(record.message_ids),2)
        self.assertEqual(len(record.message_ids[0].tracking_value_ids),4)
        self.assertTracking(record.message_ids[0],[
            ('partner_id','many2one',False,partner),
            ('partner_name','char',False,'Foo'),
            ('partner_email','char',False,'foo@example.com'),
            ('partner_phone','char',False,'1234567890'),
        ])

        #modifypartner:onetrackingmessagefortheonlyrecomputedfield
        partner.write({'name':'Fool'})
        self.flush_tracking()
        self.assertEqual(len(record.message_ids),3)
        self.assertEqual(len(record.message_ids[0].tracking_value_ids),1)
        self.assertTracking(record.message_ids[0],[
            ('partner_name','char','Foo','Fool'),
        ])

        #modifypartner:onetrackingmessageforbothstoredcomputedfields;
        #thenon-storedcomputedfieldshavenotracking
        partner.write({
            'name':'Bar',
            'email':'bar@example.com',
            'phone':'0987654321',
        })
        #forcerecomputationof'partner_phone'tomakesureitdoesnot
        #generatetrackingvalues
        self.assertEqual(record.partner_phone,'0987654321')
        self.flush_tracking()
        self.assertEqual(len(record.message_ids),4)
        self.assertEqual(len(record.message_ids[0].tracking_value_ids),2)
        self.assertTracking(record.message_ids[0],[
            ('partner_name','char','Fool','Bar'),
            ('partner_email','char','foo@example.com','bar@example.com'),
        ])


@tagged('mail_track')
classTestTrackingInternals(TestMailCommon):

    defsetUp(self):
        super(TestTrackingInternals,self).setUp()

        record=self.env['mail.test.ticket'].with_user(self.user_employee).with_context(self._test_context).create({
            'name':'Test',
        })
        self.flush_tracking()
        self.record=record.with_context(mail_notrack=False)

    deftest_track_groups(self):
        field=self.record._fields['email_from']
        self.addCleanup(setattr,field,'groups',field.groups)
        field.groups='base.group_erp_manager'

        self.record.sudo().write({'email_from':'X'})
        self.flush_tracking()

        msg_emp=self.record.message_ids.message_format()
        msg_sudo=self.record.sudo().message_ids.message_format()
        self.assertFalse(msg_emp[0].get('tracking_value_ids'),"shouldnothaveprotectedtrackingvalues")
        self.assertTrue(msg_sudo[0].get('tracking_value_ids'),"shouldhaveprotectedtrackingvalues")

        msg_emp=self.record._notify_prepare_template_context(self.record.message_ids,{})
        msg_sudo=self.record.sudo()._notify_prepare_template_context(self.record.message_ids,{})
        self.assertFalse(msg_emp.get('tracking_values'),"shouldnothaveprotectedtrackingvalues")
        self.assertTrue(msg_sudo.get('tracking_values'),"shouldhaveprotectedtrackingvalues")

        #testeditingtherecordwithusernotinthegroupofthefield
        self.record.invalidate_cache()
        self.record.clear_caches()
        record_form=Form(self.record.with_user(self.user_employee))
        record_form.name='TestDoNoCrash'
        #theemployeeusermustbeabletosavethefieldsonwhichhecanwrite
        #ifwefetchallthetrackedfields,ignoringthegroupofthecurrentuser
        #itwillcrashanditshouldn't
        record=record_form.save()
        self.assertEqual(record.name,'TestDoNoCrash')

    deftest_track_sequence(self):
        """Updatesometrackedfieldsandcheckthatthemail.tracking.valueareorderedaccordingtotheirtracking_sequence"""
        self.record.write({
            'name':'Zboub',
            'customer_id':self.user_admin.partner_id.id,
            'user_id':self.user_admin.id,
            'container_id':self.env['mail.test.container'].with_context(mail_create_nosubscribe=True).create({'name':'Container'}).id
        })
        self.flush_tracking()
        self.assertEqual(len(self.record.message_ids),1,'shouldhave1trackingmessage')

        tracking_values=self.env['mail.tracking.value'].search([('mail_message_id','=',self.record.message_ids.id)])
        self.assertEqual(tracking_values[0].tracking_sequence,1)
        self.assertEqual(tracking_values[1].tracking_sequence,2)
        self.assertEqual(tracking_values[2].tracking_sequence,100)

    deftest_unlinked_field(self):
        record_sudo=self.record.sudo()
        record_sudo.write({'email_from':'new_value'}) #createatrackingvalue
        self.flush_tracking()
        self.assertEqual(len(record_sudo.message_ids.tracking_value_ids),1)
        ir_model_field=self.env['ir.model.fields'].search([
            ('model','=','mail.test.ticket'),
            ('name','=','email_from')])
        ir_model_field.with_context(_force_unlink=True).unlink()
        self.assertEqual(len(record_sudo.message_ids.tracking_value_ids),0)
