#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime,timedelta

fromflectraimportfields
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.testsimportcommon


classTestEventCommon(common.SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestEventCommon,cls).setUpClass()

        #Testuserstousethroughthevarioustests
        cls.user_portal=mail_new_test_user(
            cls.env,login='portal_test',
            name='PatrickPortal',email='patrick.portal@test.example.com',
            notification_type='email',company_id=cls.env.ref("base.main_company").id,
            groups='base.group_portal')
        cls.user_employee=mail_new_test_user(
            cls.env,login='user_employee',
            name='EglantineEmployee',email='eglantine.employee@test.example.com',
            tz='Europe/Brussels',notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user',
        )
        cls.user_eventuser=mail_new_test_user(
            cls.env,login='user_eventuser',
            name='UrsuleEventUser',email='ursule.eventuser@test.example.com',
            tz='Europe/Brussels',notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,event.group_event_user',
        )
        cls.user_eventmanager=mail_new_test_user(
            cls.env,login='user_eventmanager',
            name='MartineEventManager',email='martine.eventmanager@test.example.com',
            tz='Europe/Brussels',notification_type='inbox',
            company_id=cls.env.ref("base.main_company").id,
            groups='base.group_user,event.group_event_manager',
        )

        cls.event_customer=cls.env['res.partner'].create({
            'name':'ConstantinCustomer',
            'email':'constantin@test.example.com',
            'country_id':cls.env.ref('base.be').id,
            'phone':'0485112233',
            'mobile':False,
        })
        cls.event_customer2=cls.env['res.partner'].create({
            'name':'ConstantinCustomer2',
            'email':'constantin2@test.example.com',
            'country_id':cls.env.ref('base.be').id,
            'phone':'0456987654',
            'mobile':'0456654321',
        })

        cls.event_type_complex=cls.env['event.type'].create({
            'name':'UpdateType',
            'auto_confirm':True,
            'has_seats_limitation':True,
            'seats_max':30,
            'use_timezone':True,
            'default_timezone':'Europe/Paris',
            'use_ticket':True,
            'event_type_ticket_ids':[(0,0,{
                    'name':'FirstTicket',
                }),(0,0,{
                    'name':'SecondTicket',
                })
            ],
            'use_mail_schedule':True,
            'event_type_mail_ids':[
                (0,0,{ #rightatsubscription
                    'interval_unit':'now',
                    'interval_type':'after_sub',
                    'template_id':cls.env['ir.model.data'].xmlid_to_res_id('event.event_subscription')}),
                (0,0,{ #1daysbeforeevent
                    'interval_nbr':1,
                    'interval_unit':'days',
                    'interval_type':'before_event',
                    'template_id':cls.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')}),
            ],
        })
        cls.event_0=cls.env['event.event'].create({
            'name':'TestEvent',
            'auto_confirm':True,
            'date_begin':fields.Datetime.to_string(datetime.today()+timedelta(days=1)),
            'date_end':fields.Datetime.to_string(datetime.today()+timedelta(days=15)),
            'date_tz':'Europe/Brussels',
        })

        #setcountryinordertoformatBelgiannumbers
        cls.event_0.company_id.write({'country_id':cls.env.ref('base.be').id})

    @classmethod
    def_create_registrations(cls,event,reg_count):
        #createsomeregistrations
        registrations=cls.env['event.registration'].create([{
            'event_id':event.id,
            'name':'TestRegistration%s'%x,
            'email':'_test_reg_%s@example.com'%x,
            'phone':'04560000%s%s'%(x,x),
        }forxinrange(0,reg_count)])
        returnregistrations
