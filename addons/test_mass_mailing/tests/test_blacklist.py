#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportusers
fromflectra.addons.test_mass_mailing.testsimportcommon
fromflectra.exceptionsimportAccessError


classTestBLAccessRights(common.TestMassMailCommon):

    @classmethod
    defsetUpClass(cls):
        super(TestBLAccessRights,cls).setUpClass()
        cls._create_portal_user()

        cls.bl_rec=cls.env['mail.blacklist'].create([
            {'email':'NotAStark<john.snow@example.com>'},
        ])
        cls.bl_previous=cls.env['mail.blacklist'].search([])

    @users('employee')
    deftest_bl_crud_employee(self):
        withself.assertRaises(AccessError):
            self.env['mail.blacklist'].create([{'email':'Arya.Stark@example.com'}])

        withself.assertRaises(AccessError):
            self.bl_rec.with_user(self.env.user).read([])

        withself.assertRaises(AccessError):
            self.bl_rec.with_user(self.env.user).write({'email':'jaimie.lannister@example.com'})

        withself.assertRaises(AccessError):
            self.bl_rec.with_user(self.env.user).unlink()

    @users('portal_test')
    deftest_bl_crud_portal(self):
        withself.assertRaises(AccessError):
            self.env['mail.blacklist'].create([{'email':'Arya.Stark@example.com'}])

        withself.assertRaises(AccessError):
            self.bl_rec.with_user(self.env.user).read([])

        withself.assertRaises(AccessError):
            self.bl_rec.with_user(self.env.user).write({'email':'jaimie.lannister@example.com'})

        withself.assertRaises(AccessError):
            self.bl_rec.with_user(self.env.user).unlink()

    @users('user_marketing')
    deftest_bl_crud_marketing(self):
        self.env['mail.blacklist'].create([{'email':'Arya.Stark@example.com'}])

        read_res=self.bl_rec.with_user(self.env.user).read([])
        self.assertEqual(read_res[0]['id'],self.bl_rec.id)

        self.bl_rec.with_user(self.env.user).write({'email':'jaimie.lannister@example.com'})
        self.assertEqual(self.bl_rec.email,'jaimie.lannister@example.com')

        self.bl_rec.with_user(self.env.user).unlink()


classTestBLConsistency(common.TestMassMailCommon):
    _base_list=['Arya.Stark@example.com','ned.stark@example.com']

    defsetUp(self):
        super(TestBLConsistency,self).setUp()
        self.bl_rec=self.env['mail.blacklist'].create([
            {'email':'NotAStark<john.snow@example.com>'},
        ])

        self.bl_previous=self.env['mail.blacklist'].search([])

    @users('user_marketing')
    deftest_bl_check_case_add(self):
        """Testemailscasewhenaddingthrough_add"""
        bl_sudo=self.env['mail.blacklist'].sudo()
        existing=bl_sudo.create({
            'email':'arya.stark@example.com',
            'active':False,
        })

        added=self.env['mail.blacklist']._add('Arya.Stark@EXAMPLE.com')
        self.assertEqual(existing,added)
        self.assertTrue(existing.active)

    @users('user_marketing')
    deftest_bl_check_case_remove(self):
        """Testemailscasewhendeactivatingthrough_remove"""
        bl_sudo=self.env['mail.blacklist'].sudo()
        existing=bl_sudo.create({
            'email':'arya.stark@example.com',
            'active':True,
        })

        added=self.env['mail.blacklist']._remove('Arya.Stark@EXAMPLE.com')
        self.assertEqual(existing,added)
        self.assertFalse(existing.active)

    @users('user_marketing')
    deftest_bl_create_duplicate(self):
        """Testemailsareinsertedonlyonceifduplicated"""
        bl_sudo=self.env['mail.blacklist'].sudo()
        self.env['mail.blacklist'].create([
            {'email':self._base_list[0]},
            {'email':self._base_list[1]},
            {'email':'AnotherNedStark<%s>'%self._base_list[1]},
        ])

        new_bl=bl_sudo.search([('id','notin',self.bl_previous.ids)])

        self.assertEqual(len(new_bl),2)
        self.assertEqual(
            set(v.lower()forvinself._base_list),
            set(v.lower()forvinnew_bl.mapped('email'))
        )

    @users('user_marketing')
    deftest_bl_create_parsing(self):
        """Testemailiscorrectlyextractedfromgivenentries"""
        bl_sudo=self.env['mail.blacklist'].sudo()
        self.env['mail.blacklist'].create([
            {'email':self._base_list[0]},
            {'email':self._base_list[1]},
            {'email':'NotNedStark<jaimie.lannister@example.com>'},
        ])

        new_bl=bl_sudo.search([('id','notin',self.bl_previous.ids)])

        self.assertEqual(len(new_bl),3)
        self.assertEqual(
            set(v.lower()forvinself._base_list+['jaimie.lannister@example.com']),
            set(v.lower()forvinnew_bl.mapped('email'))
        )

    @users('user_marketing')
    deftest_bl_search_exact(self):
        search_res=self.env['mail.blacklist'].search([('email','=','john.snow@example.com')])
        self.assertEqual(search_res,self.bl_rec)

    @users('user_marketing')
    deftest_bl_search_parsing(self):
        search_res=self.env['mail.blacklist'].search([('email','=','NotAStark<john.snow@example.com>')])

        self.assertEqual(search_res,self.bl_rec)

        search_res=self.env['mail.blacklist'].search([('email','=','"JohnJ.Snow"<john.snow@example.com>')])
        self.assertEqual(search_res,self.bl_rec)

        search_res=self.env['mail.blacklist'].search([('email','=','Aegon?<john.snow@example.com>')])
        self.assertEqual(search_res,self.bl_rec)

        search_res=self.env['mail.blacklist'].search([('email','=','"John;\"YouknowNothing\"Snow"<john.snow@example.com>')])
        self.assertEqual(search_res,self.bl_rec)

    @users('user_marketing')
    deftest_bl_search_case(self):
        search_res=self.env['mail.blacklist'].search([('email','=','john.SNOW@example.COM>')])
        self.assertEqual(search_res,self.bl_rec)

    @users('user_marketing')
    deftest_bl_search_partial(self):
        search_res=self.env['mail.blacklist'].search([('email','ilike','John')])
        self.assertEqual(search_res,self.bl_rec)
        search_res=self.env['mail.blacklist'].search([('email','ilike','n.SNOW@example.cO>')])
        self.assertEqual(search_res,self.bl_rec)
