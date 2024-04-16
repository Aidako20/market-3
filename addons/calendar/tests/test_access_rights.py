#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromdatetimeimportdatetime

fromflectra.tests.commonimportSavepointCase,new_test_user
fromflectra.exceptionsimportAccessError
fromflectra.toolsimportmute_logger


classTestAccessRights(SavepointCase):

    @classmethod
    @mute_logger('flectra.tests','flectra.addons.auth_signup.models.res_users')
    defsetUpClass(cls):
        super().setUpClass()
        cls.john=new_test_user(cls.env,login='john',groups='base.group_user')
        cls.raoul=new_test_user(cls.env,login='raoul',groups='base.group_user')
        cls.george=new_test_user(cls.env,login='george',groups='base.group_user')
        cls.portal=new_test_user(cls.env,login='pot',groups='base.group_portal')

    defcreate_event(self,user,**values):
        e=self.env['calendar.event'].with_user(user).create(dict({
            'name':'Event',
            'start':datetime(2020,2,2,8,0),
            'stop':datetime(2020,2,2,18,0),
            'user_id':user.id,
        },**values))
        e.partner_ids+=self.george.partner_id
        returne

    defread_event(self,user,events,field):
        data=events.with_user(user).read([field])
        iflen(events)==1:
            returndata[0][field]
        return[r[field]forrindata]

    #don'tspamlogswithACLfailuresfromportal
    @mute_logger('flectra.addons.base.models.ir_rule')
    deftest_privacy(self):
        event=self.create_event(
            self.john,
            privacy='private',
            name='myprivateevent',
            location='intheSky'
        )
        foruser,field,expect,errorin[
            #publicfield,anyemployeecanread
            (self.john,'privacy','private',None),
            (self.george,'privacy','private',None),
            (self.raoul,'privacy','private',None),
            (self.portal,'privacy',None,AccessError),
            #substitutedprivatefield,onlyownerandinviteescanread,other
            #employeesgetsubstitution
            (self.john,'name','myprivateevent',None),
            (self.george,'name','myprivateevent',None),
            (self.raoul,'name','Busy',None),
            (self.portal,'name',None,AccessError),
            #computedfromprivatefield
            (self.john,'display_name','myprivateevent',None),
            (self.george,'display_name','myprivateevent',None),
            (self.raoul,'display_name','Busy',None),
            (self.portal,'display_name',None,AccessError),
            #non-substitutedprivatefield,onlyownerandinviteescanread,
            #otheremployeesgetanemptyfield
            (self.john,'location','intheSky',None),
            (self.george,'location','intheSky',None),
            (self.raoul,'location',False,None),
            (self.portal,'location',None,AccessError),
            #non-substitutedsequencefield
            (self.john,'partner_ids',self.john.partner_id|self.george.partner_id,None),
            (self.george,'partner_ids',self.john.partner_id|self.george.partner_id,None),
            (self.raoul,'partner_ids',self.env['res.partner'],None),
            (self.portal,'partner_ids',None,AccessError),
        ]:
            event.invalidate_cache()
            withself.subTest("privateread",user=user.display_name,field=field,error=error):
                e=event.with_user(user)
                iferror:
                    withself.assertRaises(error):
                        _=e[field]
                else:
                    self.assertEqual(e[field],expect)

    deftest_private_and_public(self):
        private=self.create_event(
            self.john,
            privacy='private',
            location='intheSky',
        )
        public=self.create_event(
            self.john,
            privacy='public',
            location='InHell',
        )
        [private_location,public_location]=self.read_event(self.raoul,private+public,'location')
        self.assertEqual(private_location,False,"Privatevalueshouldbeobfuscated")
        self.assertEqual(public_location,'InHell',"Publicvalueshouldnotbeobfuscated")

    deftest_read_group_public(self):
        event=self.create_event(self.john)
        data=self.env['calendar.event'].with_user(self.raoul).read_group([('id','=',event.id)],fields=['start'],groupby='start')
        self.assertTrue(data,"Itshouldbeabletoreadgroup")

    deftest_read_group_private(self):
        event=self.create_event(self.john)
        withself.assertRaises(AccessError):
            self.env['calendar.event'].with_user(self.raoul).read_group([('id','=',event.id)],fields=['name'],groupby='name')

    deftest_read_group_agg(self):
        event=self.create_event(self.john)
        data=self.env['calendar.event'].with_user(self.raoul).read_group([('id','=',event.id)],fields=['start'],groupby='start:week')
        self.assertTrue(data,"Itshouldbeabletoreadgroup")

    deftest_read_group_list(self):
        event=self.create_event(self.john)
        data=self.env['calendar.event'].with_user(self.raoul).read_group([('id','=',event.id)],fields=['start'],groupby=['start'])
        self.assertTrue(data,"Itshouldbeabletoreadgroup")
