#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime
fromdateutil.relativedeltaimportrelativedelta

fromflectra.addons.event.tests.commonimportTestEventCommon
fromflectra.exceptionsimportAccessError
fromflectra.tests.commonimportusers
fromflectra.toolsimportmute_logger


classTestEventSecurity(TestEventCommon):

    @users('user_employee')
    @mute_logger('flectra.models.unlink','flectra.addons.base.models.ir_model')
    deftest_event_access_employee(self):
        #employeecanreadevents(sure?)
        event=self.event_0.with_user(self.env.user)
        event.read(['name'])
        #event.stage_id.read(['name','description'])
        #event.event_type_id.read(['name','has_seats_limitation'])

        withself.assertRaises(AccessError):
            self.env['event.event'].create({
                'name':'TestEvent',
                'date_begin':datetime.now()+relativedelta(days=-1),
                'date_end':datetime.now()+relativedelta(days=1),
                'seats_limited':True,
                'seats_max':10,
            })

        withself.assertRaises(AccessError):
            event.write({
                'name':'TestEventModified',
            })

        withself.assertRaises(AccessError):
            self.env['event.stage'].create({
                'name':'TestStage',
            })

    @users('user_eventuser')
    @mute_logger('flectra.models.unlink','flectra.addons.base.models.ir_model')
    deftest_event_access_event_user(self):
        event=self.event_0.with_user(self.env.user)
        event.read(['name','user_id','kanban_state_label'])

        withself.assertRaises(AccessError):
            self.env['event.event'].create({
                'name':'TestEvent',
                'date_begin':datetime.now()+relativedelta(days=-1),
                'date_end':datetime.now()+relativedelta(days=1),
            })

        withself.assertRaises(AccessError):
            event.write({
                'name':'TestEventModified',
            })

    @users('user_eventmanager')
    @mute_logger('flectra.models.unlink','flectra.addons.base.models.ir_model')
    deftest_event_access_event_manager(self):
        #EventManagercandoabouteverything
        event_type=self.env['event.type'].create({
            'name':'ManagerEventType',
            'use_mail_schedule':True,
            'event_type_mail_ids':[(5,0),(0,0,{
                'interval_nbr':1,'interval_unit':'days','interval_type':'before_event',
                'template_id':self.env['ir.model.data'].xmlid_to_res_id('event.event_reminder')})]
        })
        event=self.env['event.event'].create({
            'name':'ManagerEvent',
            'event_type_id':event_type.id,
            'date_begin':datetime.now()+relativedelta(days=-1),
            'date_end':datetime.now()+relativedelta(days=1),
        })

        registration=self.env['event.registration'].create({'event_id':event.id,'name':'Myself'})
        registration.write({'name':'Myself2'})

        stage=self.env['event.stage'].create({'name':'test'})
        stage.write({'name':'ManagerTest'})
        event.write({'stage_id':stage.id})

        registration.unlink()
        event.unlink()
        stage.unlink()
        event_type.unlink()

        #Settingsaccessrightsrequiredtoenablesomefeatures
        self.user_eventmanager.write({'groups_id':[
            (3,self.env.ref('base.group_system').id),
            (4,self.env.ref('base.group_erp_manager').id)
        ]})
        withself.assertRaises(AccessError):
            event_config=self.env['res.config.settings'].with_user(self.user_eventmanager).create({
            })
            event_config.execute()
