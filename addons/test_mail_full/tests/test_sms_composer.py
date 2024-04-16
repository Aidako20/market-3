#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.test_mail_full.tests.commonimportTestMailFullCommon,TestRecipients


classTestSMSComposerComment(TestMailFullCommon,TestRecipients):
    """TODOLIST

     *addtestfordefault_res_model/default_res_idandstufflikethat;
     *addtestforcommentputinqueue;
     *addtestforlanguagesupport(settemplatelangcontext);
     *addtestforsanitized/wrongnumbers;
    """

    @classmethod
    defsetUpClass(cls):
        super(TestSMSComposerComment,cls).setUpClass()
        cls._test_body='VOIDCONTENT'

        cls.test_record=cls.env['mail.test.sms'].with_context(**cls._test_context).create({
            'name':'Test',
            'customer_id':cls.partner_1.id,
            'mobile_nbr':cls.test_numbers[0],
            'phone_nbr':cls.test_numbers[1],
        })
        cls.test_record=cls._reset_mail_context(cls.test_record)

        cls.sms_template=cls.env['sms.template'].create({
            'name':'TestTemplate',
            'model_id':cls.env['ir.model']._get('mail.test.sms').id,
            'body':'Dear${object.display_name}thisisanSMS.',
        })

    deftest_composer_comment_not_mail_thread(self):
        withself.with_user('employee'):
            record=self.env['test_performance.base'].create({'name':'TestBase'})
            composer=self.env['sms.composer'].with_context(
                active_model='test_performance.base',active_id=record.id
            ).create({
                'body':self._test_body,
                'numbers':','.join(self.random_numbers),
            })

            withself.mockSMSGateway():
                composer._action_send_sms()

        #usesms.apidirectly,doesnotcreatesms.sms
        self.assertNoSMS()
        self.assertSMSIapSent(self.random_numbers_san,self._test_body)

    deftest_composer_comment_default(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                active_model='mail.test.sms',active_id=self.test_record.id
            ).create({
                'body':self._test_body,
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        self.assertSMSNotification([{'partner':self.test_record.customer_id,'number':self.test_numbers_san[1]}],self._test_body,messages)

    deftest_composer_comment_field_1(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                active_model='mail.test.sms',active_id=self.test_record.id,
            ).create({
                'body':self._test_body,
                'number_field_name':'mobile_nbr',
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        self.assertSMSNotification([{'partner':self.test_record.customer_id,'number':self.test_numbers_san[0]}],self._test_body,messages)

    deftest_composer_comment_field_2(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                active_model='mail.test.sms',active_id=self.test_record.id,
            ).create({
                'body':self._test_body,
                'number_field_name':'phone_nbr',
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        self.assertSMSNotification([{'partner':self.test_record.customer_id,'number':self.test_numbers_san[1]}],self._test_body,messages)

    deftest_composer_comment_field_w_numbers(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                active_model='mail.test.sms',active_id=self.test_record.id,
                default_number_field_name='mobile_nbr',
            ).create({
                'body':self._test_body,
                'numbers':','.join(self.random_numbers),
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        self.assertSMSNotification([
            {'partner':self.test_record.customer_id,'number':self.test_record.mobile_nbr},
            {'number':self.random_numbers_san[0]},{'number':self.random_numbers_san[1]}],self._test_body,messages)

    deftest_composer_comment_field_w_template(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                active_model='mail.test.sms',active_id=self.test_record.id,
                default_template_id=self.sms_template.id,
                default_number_field_name='mobile_nbr',
            ).create({})

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        self.assertSMSNotification([{'partner':self.test_record.customer_id,'number':self.test_record.mobile_nbr}],'Dear%sthisisanSMS.'%self.test_record.display_name,messages)

    deftest_composer_comment_nofield(self):
        """TesttheSendMessageinSMSComposerwhenaModeldoesnotcontainanyphonenumberrelatedfield"""
        test_record=self.env['mail.test.sms.partner'].create({'name':'Test'})
        sms_composer=self.env['sms.composer'].create({
            'body':self._test_body,
            'recipient_single_number_itf':self.random_numbers_san[0],
            'res_id':test_record.id,
            'res_model':'mail.test.sms.partner'
        })
        withself.mockSMSGateway():
            sms_composer._action_send_sms()
        self.assertSMSNotification([{'number':self.random_numbers_san[0]}],self._test_body)

    deftest_composer_default_recipient(self):
        """TestdefaultdescriptionofSMScomposermustbepartnername"""
        self.test_record.write({
            'phone_nbr':'0123456789',
        })
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                    default_res_model='mail.test.sms',default_res_id=self.test_record.id,
                ).create({
                    'body':self._test_body,
                    'number_field_name':'phone_nbr',
                })

        self.assertEqual(composer.recipient_single_description,self.test_record.customer_id.display_name)

    deftest_composer_nofield_w_customer(self):
        """TestSMScomposerwithoutnumberfield,thenumberonpartnermustbeusedinstead"""
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                    default_res_model='mail.test.sms',default_res_id=self.test_record.id,
                ).create({
                    'body':self._test_body,
                })

        self.assertTrue(composer.recipient_single_valid)
        self.assertEqual(composer.recipient_single_number,self.test_numbers[1])
        self.assertEqual(composer.recipient_single_number_itf,self.test_numbers[1])

    deftest_composer_internals(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_res_model='mail.test.sms',default_res_id=self.test_record.id,
            ).create({
                'body':self._test_body,
                'number_field_name':'phone_nbr',
            })

        self.assertEqual(composer.res_model,self.test_record._name)
        self.assertEqual(composer.res_id,self.test_record.id)
        self.assertEqual(composer.number_field_name,'phone_nbr')
        self.assertTrue(composer.comment_single_recipient)
        self.assertEqual(composer.recipient_single_description,self.test_record.customer_id.display_name)
        self.assertEqual(composer.recipient_single_number,self.test_numbers[1])
        self.assertEqual(composer.recipient_single_number_itf,self.test_numbers[1])
        self.assertTrue(composer.recipient_single_valid)
        self.assertEqual(composer.recipient_valid_count,1)
        self.assertEqual(composer.recipient_invalid_count,0)

        withself.with_user('employee'):
            composer.update({'recipient_single_number_itf':'0123456789'})

        self.assertFalse(composer.recipient_single_valid)

        withself.with_user('employee'):
            composer.update({'recipient_single_number_itf':self.random_numbers[0]})

        self.assertTrue(composer.recipient_single_valid)

        withself.with_user('employee'):
            withself.mockSMSGateway():
                composer.action_send_sms()

        self.test_record.flush()
        self.assertEqual(self.test_record.phone_nbr,self.random_numbers[0])

    deftest_composer_comment_wo_partner_wo_value_update(self):
        """Testrecordwithoutpartnerandwithoutphonevalues:shouldallowupdatingfirstfoundphonefield"""
        self.test_record.write({
            'customer_id':False,
            'phone_nbr':False,
            'mobile_nbr':False,
        })
        default_field_name=self.env['mail.test.sms']._sms_get_number_fields()[0]

        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                active_model='mail.test.sms',active_id=self.test_record.id,
                default_composition_mode='comment',
            ).create({
                'body':self._test_body,
            })
            self.assertFalse(composer.recipient_single_number_itf)
            self.assertFalse(composer.recipient_single_number)
            self.assertEqual(composer.number_field_name,default_field_name)

            composer.write({
                'recipient_single_number_itf':self.random_numbers_san[0],
            })
            self.assertEqual(composer.recipient_single_number_itf,self.random_numbers_san[0])
            self.assertFalse(composer.recipient_single_number)

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        self.assertEqual(self.test_record[default_field_name],self.random_numbers_san[0])
        self.assertSMSNotification([{'partner':self.env['res.partner'],'number':self.random_numbers_san[0]}],self._test_body,messages)

    deftest_composer_numbers_no_model(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='numbers'
            ).create({
                'body':self._test_body,
                'numbers':','.join(self.random_numbers),
            })

            withself.mockSMSGateway():
                composer._action_send_sms()

        #usesms.apidirectly,doesnotcreatesms.sms
        self.assertNoSMS()
        self.assertSMSIapSent(self.random_numbers_san,self._test_body)


classTestSMSComposerBatch(TestMailFullCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestSMSComposerBatch,cls).setUpClass()
        cls._test_body='Hello${object.name}zizisseanSMS.'

        cls._create_records_for_batch('mail.test.sms',3)
        cls.sms_template=cls._create_sms_template('mail.test.sms')

    deftest_composer_batch_active_domain(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='comment',
                default_res_model='mail.test.sms',
                default_use_active_domain=True,
                active_domain=[('id','in',self.records.ids)],
            ).create({
                'body':self._test_body,
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        forrecord,messageinzip(self.records,messages):
            self.assertSMSNotification(
                [{'partner':record.customer_id}],
                'Hello%szizisseanSMS.'%record.name,
                message
            )

    deftest_composer_batch_active_ids(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='comment',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids
            ).create({
                'body':self._test_body,
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        forrecord,messageinzip(self.records,messages):
            self.assertSMSNotification(
                [{'partner':record.customer_id}],
                'Hello%szizisseanSMS.'%record.name,
                message
            )

    deftest_composer_batch_domain(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='comment',
                default_res_model='mail.test.sms',
                default_use_active_domain=True,
                default_active_domain=repr([('id','in',self.records.ids)]),
            ).create({
                'body':self._test_body,
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        forrecord,messageinzip(self.records,messages):
            self.assertSMSNotification(
                [{'partner':record.customer_id}],
                'Hello%szizisseanSMS.'%record.name,
                message
            )

    deftest_composer_batch_res_ids(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='comment',
                default_res_model='mail.test.sms',
                default_res_ids=repr(self.records.ids),
            ).create({
                'body':self._test_body,
            })

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        forrecord,messageinzip(self.records,messages):
            self.assertSMSNotification(
                [{'partner':record.customer_id}],
                'Hello%szizisseanSMS.'%record.name,
                message
            )


classTestSMSComposerMass(TestMailFullCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestSMSComposerMass,cls).setUpClass()
        cls._test_body='Hello${object.name}zizisseanSMS.'

        cls._create_records_for_batch('mail.test.sms',10)
        cls.sms_template=cls._create_sms_template('mail.test.sms')

    deftest_composer_mass_active_domain(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                default_use_active_domain=True,
                active_domain=[('id','in',self.records.ids)],
            ).create({
                'body':self._test_body,
                'mass_keep_log':False,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forrecordinself.records:
            self.assertSMSOutgoing(
                record.customer_id,None,
                content='Hello%szizisseanSMS.'%record.name
            )

    deftest_composer_mass_active_domain_w_template(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                default_use_active_domain=True,
                active_domain=[('id','in',self.records.ids)],
                default_template_id=self.sms_template.id,
            ).create({
                'mass_keep_log':False,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forrecordinself.records:
            self.assertSMSOutgoing(
                record.customer_id,None,
                content='Dear%sthisisanSMS.'%record.display_name
            )

    deftest_composer_mass_active_ids(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
            ).create({
                'body':self._test_body,
                'mass_keep_log':False,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forpartner,recordinzip(self.partners,self.records):
            self.assertSMSOutgoing(
                partner,None,
                content='Hello%szizisseanSMS.'%record.name
            )

    deftest_composer_mass_active_ids_w_blacklist(self):
        self.env['phone.blacklist'].create([{
            'number':p.phone_sanitized,
            'active':True,
        }forpinself.partners[:5]])

        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
            ).create({
                'body':self._test_body,
                'mass_keep_log':False,
                'mass_use_blacklist':True,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forpartner,recordinzip(self.partners[5:],self.records[5:]):
            self.assertSMSOutgoing(
                partner,partner.phone_sanitized,
                content='Hello%szizisseanSMS.'%record.name
            )
        forpartner,recordinzip(self.partners[:5],self.records[:5]):
            self.assertSMSCanceled(
                partner,partner.phone_sanitized,
                error_code='sms_blacklist',
                content='Hello%szizisseanSMS.'%record.name
            )

    deftest_composer_mass_active_ids_wo_blacklist(self):
        self.env['phone.blacklist'].create([{
            'number':p.phone_sanitized,
            'active':True,
        }forpinself.partners[:5]])

        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
            ).create({
                'body':self._test_body,
                'mass_keep_log':False,
                'mass_use_blacklist':False,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forpartner,recordinzip(self.partners,self.records):
            self.assertSMSOutgoing(
                partner,partner.phone_sanitized,
                content='Hello%szizisseanSMS.'%record.name
            )

    deftest_composer_mass_active_ids_w_blacklist_and_done(self):
        """Createsomeduplicates+blacklist.record[5]willhaveduplicated
        numberon6and7."""
        self.env['phone.blacklist'].create([{
            'number':p.phone_sanitized,
            'active':True,
        }forpinself.partners[:5]])
        forpinself.partners[5:8]:
            p.mobile=self.partners[5].mobile
            self.assertEqual(p.phone_sanitized,self.partners[5].phone_sanitized)

        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
            ).create({
                'body':self._test_body,
                'mass_keep_log':False,
                'mass_use_blacklist':True,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        self.assertSMSOutgoing(
            self.partners[5],self.partners[5].phone_sanitized,
            content='Hello%szizisseanSMS.'%self.records[5].name
        )
        forpartner,recordinzip(self.partners[8:],self.records[8:]):
            self.assertSMSOutgoing(
                partner,partner.phone_sanitized,
                content='Hello%szizisseanSMS.'%record.name
            )
        #duplicates
        forpartner,recordinzip(self.partners[6:8],self.records[6:8]):
            self.assertSMSCanceled(
                partner,partner.phone_sanitized,
                error_code='sms_duplicate',
                content='Hello%szizisseanSMS.'%record.name
            )
        #blacklist
        forpartner,recordinzip(self.partners[:5],self.records[:5]):
            self.assertSMSCanceled(
                partner,partner.phone_sanitized,
                error_code='sms_blacklist',
                content='Hello%szizisseanSMS.'%record.name
            )

    deftest_composer_mass_active_ids_w_template(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
                default_template_id=self.sms_template.id,
            ).create({
                'mass_keep_log':False,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forrecordinself.records:
            self.assertSMSOutgoing(
                record.customer_id,None,
                content='Dear%sthisisanSMS.'%record.display_name
            )

    deftest_composer_mass_active_ids_w_template_and_lang(self):
        self.env['res.lang']._activate_lang('fr_FR')
        self.env['ir.translation'].create({
            'type':'model',
            'name':'sms.template,body',
            'lang':'fr_FR',
            'res_id':self.sms_template.id,
            'src':self.sms_template.body,
            'value':'Cher·e·${object.display_name}ceciestunSMS.',
        })
        #settemplatetotrytousecustomerlang
        self.sms_template.write({
            'lang':'${object.customer_id.lang}',
        })
        #setonecustomerasfrenchspeaking
        self.partners[2].write({'lang':'fr_FR'})

        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
                default_template_id=self.sms_template.id,
            ).create({
                'mass_keep_log':False,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forrecordinself.records:
            ifrecord.customer_id==self.partners[2]:
                self.assertSMSOutgoing(
                    record.customer_id,None,
                    content='Cher·e·%sceciestunSMS.'%record.display_name
                )
            else:
                self.assertSMSOutgoing(
                    record.customer_id,None,
                    content='Dear%sthisisanSMS.'%record.display_name
                )

    deftest_composer_mass_active_ids_w_template_and_log(self):
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                default_composition_mode='mass',
                default_res_model='mail.test.sms',
                active_ids=self.records.ids,
                default_template_id=self.sms_template.id,
            ).create({
                'mass_keep_log':True,
            })

            withself.mockSMSGateway():
                composer.action_send_sms()

        forrecordinself.records:
            self.assertSMSOutgoing(
                record.customer_id,None,
                content='Dear%sthisisanSMS.'%record.display_name
            )
            self.assertSMSLogged(record,'Dear%sthisisanSMS.'%record.display_name)

    deftest_composer_template_context_action(self):
        """TestthecontextactionfromaSMStemplate(Addcontextactionbutton)
        andtheusagewiththesmscomposer"""
        #Createthelanginfo
        self.env['res.lang']._activate_lang('fr_FR')
        self.env['ir.translation'].create({
            'type':'model',
            'name':'sms.template,body',
            'lang':'fr_FR',
            'res_id':self.sms_template.id,
            'src':self.sms_template.body,
            'value':"Hello${object.display_name}ceciestenfrançais.",
        })
        #settemplatetotrytousecustomerlang
        self.sms_template.write({
            'lang':'${object.customer_id.lang}',
        })
        #createasecondrecordlinkedtoacustomerinanotherlanguage
        self.partners[2].write({'lang':'fr_FR'})
        test_record_2=self.env['mail.test.sms'].create({
            'name':'Test',
            'customer_id':self.partners[2].id,
        })
        test_record_1=self.env['mail.test.sms'].create({
            'name':'Test',
            'customer_id':self.partners[1].id,
        })
        #Composercreationwithcontextfromatemplatecontextaction(simulate)-comment(singlerecipient)
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                sms_composition_mode='guess',
                default_res_ids=[test_record_2.id],
                default_res_id=test_record_2.id,
                active_ids=[test_record_2.id],
                active_id=test_record_2.id,
                active_model='mail.test.sms',
                default_template_id=self.sms_template.id,
            ).create({
                'mass_keep_log':False,
            })
            self.assertEqual(composer.composition_mode,"comment")
            self.assertEqual(composer.body,"Hello%sceciestenfrançais."%test_record_2.display_name)

            withself.mockSMSGateway():
                messages=composer._action_send_sms()

        number=self.partners[2].phone_get_sanitized_number()
        self.assertSMSNotification(
            [{'partner':test_record_2.customer_id,'number':number}],
            "Hello%sceciestenfrançais."%test_record_2.display_name,messages
        )

        #Composercreationwithcontextfromatemplatecontextaction(simulate)-mass(multiplerecipient)
        withself.with_user('employee'):
            composer=self.env['sms.composer'].with_context(
                sms_composition_mode='guess',
                default_res_ids=[test_record_1.id,test_record_2.id],
                default_res_id=test_record_1.id,
                active_ids=[test_record_1.id,test_record_2.id],
                active_id=test_record_1.id,
                active_model='mail.test.sms',
                default_template_id=self.sms_template.id,
            ).create({
                'mass_keep_log':True,
            })
            self.assertEqual(composer.composition_mode,"mass")
            #Inenglishbecausebydefaultbutwhensindingdependingofrecord
            self.assertEqual(composer.body,"Dear${object.display_name}thisisanSMS.")

            withself.mockSMSGateway():
                composer.action_send_sms()

        self.assertSMSOutgoing(
            test_record_1.customer_id,None,
            content='Dear%sthisisanSMS.'%test_record_1.display_name
        )
        self.assertSMSOutgoing(
            test_record_2.customer_id,None,
            content="Hello%sceciestenfrançais."%test_record_2.display_name
        )
