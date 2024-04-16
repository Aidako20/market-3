#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromcollectionsimportOrderedDict
fromitertoolsimportchain

fromflectra.addons.hr.tests.commonimportTestHrCommon
fromflectra.testsimportnew_test_user,tagged,Form
fromflectra.exceptionsimportAccessError

@tagged('post_install','-at_install')
classTestSelfAccessProfile(TestHrCommon):

    deftest_access_my_profile(self):
        """Asimpleusershouldbeabletoreadallfieldsinhisprofile"""
        james=new_test_user(self.env,login='hel',groups='base.group_user',name='Simpleemployee',email='ric@example.com')
        james=james.with_user(james)
        self.env['hr.employee'].create({
            'name':'James',
            'user_id':james.id,
        })
        view=self.env.ref('hr.res_users_view_form_profile')
        view_infos=james.fields_view_get(view_id=view.id)
        fields=view_infos['fields'].keys()
        james.read(fields)

    deftest_readonly_fields(self):
        """Employeerelatedfieldsshouldbereadonlyifselfeditingisnotallowed"""
        self.env['ir.config_parameter'].sudo().set_param('hr.hr_employee_self_edit',False)
        james=new_test_user(self.env,login='hel',groups='base.group_user',name='Simpleemployee',email='ric@example.com')
        james=james.with_user(james)
        self.env['hr.employee'].create({
            'name':'James',
            'user_id':james.id,
        })

        view=self.env.ref('hr.res_users_view_form_profile')
        view_infos=james.fields_view_get(view_id=view.id)

        employee_related_fields={
            field_name
            forfield_name,field_attrsinview_infos['fields'].items()
            iffield_attrs.get('related',(None,))[0]=='employee_id'
        }

        form=Form(james,view=view)
        forfieldinemployee_related_fields:
            withself.assertRaises(AssertionError,msg="Field'%s'shouldbereadonlyintheemployeeprofilewhenselfeditingisnotallowed."%field):
                form.__setattr__(field,'somevalue')


    deftest_profile_view_fields(self):
        """Asimpleusershouldseeallfieldsinprofileview,eveniftheyareprotectedbygroups"""
        view=self.env.ref('hr.res_users_view_form_profile')

        #Forreference,checktheviewwithuserwitheverygroupsprotectinguserfields
        all_groups_xml_ids=chain(*[
            field.groups.split(',')
            forfieldinself.env['res.users']._fields.values()
            iffield.groups
            iffield.groups!='.'#"no-access"grouponpurpose
        ])
        all_groups=self.env['res.groups']
        forxml_idinall_groups_xml_ids:
            all_groups|=self.env.ref(xml_id.strip())
        user_all_groups=new_test_user(self.env,groups='base.group_user',login='hel',name='God')
        user_all_groups.write({'groups_id':[(4,group.id,False)forgroupinall_groups]})
        view_infos=self.env['res.users'].with_user(user_all_groups).fields_view_get(view_id=view.id)
        full_fields=view_infos['fields']

        #Nowchecktheviewforasimpleuser
        user=new_test_user(self.env,login='gro',name='Grouillot')
        view_infos=self.env['res.users'].with_user(user).fields_view_get(view_id=view.id)
        fields=view_infos['fields']

        #Compareboth
        self.assertEqual(full_fields.keys(),fields.keys(),"Viewfieldsshouldnotdependonuser'sgroups")

    deftest_access_my_profile_toolbar(self):
        """Asimpleusershouldn'thavethepossibilitiestoseethe'ChangePassword'action"""
        james=new_test_user(self.env,login='jam',groups='base.group_user',name='Simpleemployee',email='jam@example.com')
        james=james.with_user(james)
        self.env['hr.employee'].create({
            'name':'James',
            'user_id':james.id,
        })
        view=self.env.ref('hr.res_users_view_form_profile')
        available_actions=james.fields_view_get(view_id=view.id,toolbar=True)['toolbar']['action']
        change_password_action=self.env.ref("base.change_password_wizard_action")

        self.assertFalse(any(x['id']==change_password_action.idforxinavailable_actions))

        """AnERPmanagershouldhavethepossibilitiestoseethe'ChangePassword'"""
        john=new_test_user(self.env,login='joh',groups='base.group_erp_manager',name='ERPManager',email='joh@example.com')
        john=john.with_user(john)
        self.env['hr.employee'].create({
            'name':'John',
            'user_id':john.id,
        })
        view=self.env.ref('hr.res_users_view_form_profile')
        available_actions=john.fields_view_get(view_id=view.id,toolbar=True)['toolbar']['action']
        self.assertTrue(any(x['id']==change_password_action.idforxinavailable_actions))


classTestSelfAccessRights(TestHrCommon):

    defsetUp(self):
        super(TestSelfAccessRights,self).setUp()
        self.richard=new_test_user(self.env,login='ric',groups='base.group_user',name='Simpleemployee',email='ric@example.com')
        self.richard_emp=self.env['hr.employee'].create({
            'name':'Richard',
            'user_id':self.richard.id,
            'address_home_id':self.env['res.partner'].create({'name':'Richard','phone':'21454','type':'private'}).id,
        })
        self.hubert=new_test_user(self.env,login='hub',groups='base.group_user',name='Simpleemployee',email='hub@example.com')
        self.hubert_emp=self.env['hr.employee'].create({
            'name':'Hubert',
            'user_id':self.hubert.id,
            'address_home_id':self.env['res.partner'].create({'name':'Hubert','type':'private'}).id,
        })

        self.protected_fields_emp=OrderedDict([(k,v)fork,vinself.env['hr.employee']._fields.items()ifv.groups=='hr.group_hr_user'])
        #Computefieldsandidfieldarealwaysreadablebyeveryone
        self.read_protected_fields_emp=OrderedDict([(k,v)fork,vinself.env['hr.employee']._fields.items()ifnotv.computeandk!='id'])
        self.self_protected_fields_user=OrderedDict([
            (k,v)
            fork,vinself.env['res.users']._fields.items()
            ifv.groups=='hr.group_hr_user'andkinself.env['res.users'].SELF_READABLE_FIELDS
        ])

    #Readhr.employee#
    deftestReadSelfEmployee(self):
        withself.assertRaises(AccessError):
            self.hubert_emp.with_user(self.richard).read(self.protected_fields_emp.keys())

    deftestReadOtherEmployee(self):
        withself.assertRaises(AccessError):
            self.hubert_emp.with_user(self.richard).read(self.protected_fields_emp.keys())

    #Writehr.employee#
    deftestWriteSelfEmployee(self):
        forfinself.protected_fields_emp:
            withself.assertRaises(AccessError):
                self.richard_emp.with_user(self.richard).write({f:'dummy'})

    deftestWriteOtherEmployee(self):
        forfinself.protected_fields_emp:
            withself.assertRaises(AccessError):
                self.hubert_emp.with_user(self.richard).write({f:'dummy'})

    #Readres.users#
    deftestReadSelfUserEmployee(self):
        forfinself.self_protected_fields_user:
            self.richard.with_user(self.richard).read([f]) #shouldnotraise

    deftestReadOtherUserEmployee(self):
        withself.assertRaises(AccessError):
            self.hubert.with_user(self.richard).read(self.self_protected_fields_user)

    #Writeres.users#
    deftestWriteSelfUserEmployeeSettingFalse(self):
        forf,vinself.self_protected_fields_user.items():
            withself.assertRaises(AccessError):
                self.richard.with_user(self.richard).write({f:'dummy'})

    deftestWriteSelfUserEmployee(self):
        self.env['ir.config_parameter'].set_param('hr.hr_employee_self_edit',True)
        forf,vinself.self_protected_fields_user.items():
            val=None
            ifv.type=='char'orv.type=='text':
                val='0000'iff=='pin'else'dummy'
            ifvalisnotNone:
                self.richard.with_user(self.richard).write({f:val})

    deftestWriteSelfUserPreferencesEmployee(self):
        #selfshouldalwaysbeabletoupdatenonhr.employeefieldsif
        #theyareinSELF_READABLE_FIELDS
        self.env['ir.config_parameter'].set_param('hr.hr_employee_self_edit',False)
        #shouldnotraise
        vals=[
            {'tz':"Australia/ACT"},
            {'email':"new@example.com"},
            {'signature':"<p>I'mRichard!</p>"},
            {'notification_type':"email"},
        ]
        forvinvals:
            #shouldnotraise
            self.richard.with_user(self.richard).write(v)

    deftestWriteOtherUserPreferencesEmployee(self):
        #selfshouldalwaysbeabletoupdatenonhr.employeefieldsif
        #theyareinSELF_READABLE_FIELDS
        self.env['ir.config_parameter'].set_param('hr.hr_employee_self_edit',False)
        vals=[
            {'tz':"Australia/ACT"},
            {'email':"new@example.com"},
            {'signature':"<p>I'mRichard!</p>"},
            {'notification_type':"email"},
        ]
        forvinvals:
            withself.assertRaises(AccessError):
                self.hubert.with_user(self.richard).write(v)

    deftestWriteSelfPhoneEmployee(self):
        #phoneisarelatedfromres.partner(frombase)butaddedinSELF_READABLE_FIELDS
        self.env['ir.config_parameter'].set_param('hr.hr_employee_self_edit',False)
        withself.assertRaises(AccessError):
            self.richard.with_user(self.richard).write({'phone':'2154545'})

    deftestWriteOtherUserEmployee(self):
        forfinself.self_protected_fields_user:
            withself.assertRaises(AccessError):
                self.hubert.with_user(self.richard).write({f:'dummy'})

    deftestSearchUserEMployee(self):
        #Searchinguserbasedonemployee_idfieldshouldnotraisebadqueryerror
        self.env['res.users'].with_user(self.richard).search([('employee_id','ilike','Hubert')])
