#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importdatetime

fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.event.tests.commonimportTestEventCommon
fromflectra.exceptionsimportValidationError
fromflectra.tests.commonimportForm
fromflectra.toolsimportmute_logger


classTestEventUI(TestEventCommon):

    deftest_event_registration_partner_sync(self):
        """Ensureonchangeonpartner_idiskeptforinterface,notforcomputed
        fields."""
        registration_form=Form(self.env['event.registration'].with_context(
            default_name='WrongName',
            default_event_id=self.event_0.id
        ))
        self.assertEqual(registration_form.event_id,self.event_0)
        self.assertEqual(registration_form.name,'WrongName')
        self.assertFalse(registration_form.email)
        self.assertFalse(registration_form.phone)
        self.assertFalse(registration_form.mobile)

        #triggeronchange
        registration_form.partner_id=self.event_customer
        self.assertEqual(registration_form.name,self.event_customer.name)
        self.assertEqual(registration_form.email,self.event_customer.email)
        self.assertEqual(registration_form.phone,self.event_customer.phone)
        self.assertEqual(registration_form.mobile,self.event_customer.mobile)

        #save,checkrecordmatchesFormvalues
        registration=registration_form.save()
        self.assertEqual(registration.partner_id,self.event_customer)
        self.assertEqual(registration.name,self.event_customer.name)
        self.assertEqual(registration.email,self.event_customer.email)
        self.assertEqual(registration.phone,self.event_customer.phone)
        self.assertEqual(registration.mobile,self.event_customer.mobile)

        #allowwritingonsomefieldsindependentlyfromcustomerconfig
        registration.write({'phone':False,'mobile':False})
        self.assertFalse(registration.phone)
        self.assertFalse(registration.mobile)

        #resetpartnershouldnotresetotherfields
        registration.write({'partner_id':False})
        self.assertEqual(registration.partner_id,self.env['res.partner'])
        self.assertEqual(registration.name,self.event_customer.name)
        self.assertEqual(registration.email,self.event_customer.email)
        self.assertFalse(registration.phone)
        self.assertFalse(registration.mobile)

        #updatetoanewpartnernotthroughUI->updateonlyvoidfeilds
        registration.write({'partner_id':self.event_customer2.id})
        self.assertEqual(registration.partner_id,self.event_customer2)
        self.assertEqual(registration.name,self.event_customer.name)
        self.assertEqual(registration.email,self.event_customer.email)
        self.assertEqual(registration.phone,self.event_customer2.phone)
        self.assertEqual(registration.mobile,self.event_customer2.mobile)


classTestEventFlow(TestEventCommon):

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_event_auto_confirm(self):
        """Basiceventmanagementwithautoconfirmation"""
        #EventUsercreatesanewevent:ok
        test_event=self.env['event.event'].with_user(self.user_eventmanager).create({
            'name':'TestEvent',
            'auto_confirm':True,
            'date_begin':datetime.datetime.now()+relativedelta(days=-1),
            'date_end':datetime.datetime.now()+relativedelta(days=1),
            'seats_max':2,
            'seats_limited':True,
        })
        self.assertTrue(test_event.auto_confirm)

        #EventUsercreateregistrationsforthisevent
        test_reg1=self.env['event.registration'].with_user(self.user_eventuser).create({
            'name':'TestReg1',
            'event_id':test_event.id,
        })
        self.assertEqual(test_reg1.state,'open','Event:auto_confirmationofregistrationfailed')
        self.assertEqual(test_event.seats_reserved,1,'Event:wrongnumberofreservedseatsafterconfirmedregistration')
        test_reg2=self.env['event.registration'].with_user(self.user_eventuser).create({
            'name':'TestReg2',
            'event_id':test_event.id,
        })
        self.assertEqual(test_reg2.state,'open','Event:auto_confirmationofregistrationfailed')
        self.assertEqual(test_event.seats_reserved,2,'Event:wrongnumberofreservedseatsafterconfirmedregistration')

        #EventUsercreateregistrationsforthisevent:toomuchregistrations
        withself.assertRaises(ValidationError):
            self.env['event.registration'].with_user(self.user_eventuser).create({
                'name':'TestReg3',
                'event_id':test_event.id,
            })

        #EventUservalidatesregistrations
        test_reg1.action_set_done()
        self.assertEqual(test_reg1.state,'done','Event:wrongstateofattendedregistration')
        self.assertEqual(test_event.seats_used,1,'Event:incorrectnumberofattendeesafterclosingregistration')
        test_reg2.action_set_done()
        self.assertEqual(test_reg1.state,'done','Event:wrongstateofattendedregistration')
        self.assertEqual(test_event.seats_used,2,'Event:incorrectnumberofattendeesafterclosingregistration')

    @mute_logger('flectra.addons.base.models.ir_model','flectra.models')
    deftest_event_flow(self):
        """Advancedeventflow:noautoconfirmation,manageminimum/maximum
        seats,..."""
        #EventUsercreatesanewevent:ok
        test_event=self.env['event.event'].with_user(self.user_eventmanager).create({
            'name':'TestEvent',
            'date_begin':datetime.datetime.now()+relativedelta(days=-1),
            'date_end':datetime.datetime.now()+relativedelta(days=1),
            'seats_limited':True,
            'seats_max':10,
        })
        self.assertFalse(test_event.auto_confirm)

        #EventUsercreateregistrationsforthisevent->noautoconfirmation
        test_reg1=self.env['event.registration'].with_user(self.user_eventuser).create({
            'name':'TestReg1',
            'event_id':test_event.id,
        })
        self.assertEqual(
            test_reg1.state,'draft',
            'Event:newregistrationshouldnotbeconfirmedwithauto_confirmationparameterbeingFalse')
