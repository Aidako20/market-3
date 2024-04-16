#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.website_slides.testsimportcommon
fromflectra.exceptionsimportAccessError
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


@tagged('security')
classTestAccess(common.SlidesCase):

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_access_channel_invite(self):
        """Invitechannelsdon'tgiveenrollifnotmember"""
        self.channel.write({'enroll':'invite'})

        self.channel.with_user(self.user_officer).read(['name'])
        self.channel.with_user(self.user_manager).read(['name'])
        self.channel.with_user(self.user_emp).read(['name'])
        self.channel.with_user(self.user_portal).read(['name'])
        self.channel.with_user(self.user_public).read(['name'])

        self.slide.with_user(self.user_officer).read(['name'])
        self.slide.with_user(self.user_manager).read(['name'])

        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_portal).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_portal).read(['name'])

        #ifmember->canread
        membership=self.env['slide.channel.partner'].create({
            'channel_id':self.channel.id,
            'partner_id':self.user_emp.partner_id.id,
        })
        self.channel.with_user(self.user_emp).read(['name'])
        self.slide.with_user(self.user_emp).read(['name'])

        #notmemberanymore->cannotread
        membership.unlink()
        self.channel.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_emp).read(['name'])

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_access_channel_public(self):
        """Publicchannelsdon'tgiveenrollifnotmember"""
        self.channel.write({'enroll':'public'})

        self.channel.with_user(self.user_officer).read(['name'])
        self.channel.with_user(self.user_manager).read(['name'])
        self.channel.with_user(self.user_emp).read(['name'])
        self.channel.with_user(self.user_portal).read(['name'])
        self.channel.with_user(self.user_public).read(['name'])

        self.slide.with_user(self.user_officer).read(['name'])
        self.slide.with_user(self.user_manager).read(['name'])

        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_portal).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.with_user(self.user_public).read(['name'])

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_access_channel_publish(self):
        """UnpublishedchannelsandtheircontentarevisibleonlytoeLearningpeople"""
        self.channel.write({'is_published':False,'enroll':'public'})
        self.channel.flush(['is_published','website_published','enroll'])

        #channelavailableonlytoeLearning
        self.channel.invalidate_cache(['name'])
        self.channel.with_user(self.user_officer).read(['name'])
        self.channel.invalidate_cache(['name'])
        self.channel.with_user(self.user_manager).read(['name'])
        withself.assertRaises(AccessError):
            self.channel.invalidate_cache(['name'])
            self.channel.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.channel.invalidate_cache(['name'])
            self.channel.with_user(self.user_portal).read(['name'])
        withself.assertRaises(AccessError):
            self.channel.invalidate_cache(['name'])
            self.channel.with_user(self.user_public).read(['name'])

        #slideavailableonlytoeLearning
        self.channel.invalidate_cache(['name'])
        self.slide.with_user(self.user_officer).read(['name'])
        self.channel.invalidate_cache(['name'])
        self.slide.with_user(self.user_manager).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_portal).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_public).read(['name'])

        #evenmemberscannotseeunpublishedcontent
        self.env['slide.channel.partner'].create({
            'channel_id':self.channel.id,
            'partner_id':self.user_emp.partner_id.id,
        })
        withself.assertRaises(AccessError):
            self.channel.invalidate_cache(['name'])
            self.channel.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_emp).read(['name'])

        #publishchannelbutcontentunpublished(evenifcanbepreviewed)stillunavailable
        self.channel.write({'is_published':True})
        self.slide.write({
            'is_preview':True,
            'is_published':False,
        })
        self.channel.flush(['website_published'])
        self.slide.flush(['is_preview','website_published'])

        self.slide.invalidate_cache(['name'])
        self.slide.with_user(self.user_officer).read(['name'])
        self.slide.invalidate_cache(['name'])
        self.slide.with_user(self.user_manager).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_emp).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_portal).read(['name'])
        withself.assertRaises(AccessError):
            self.slide.invalidate_cache(['name'])
            self.slide.with_user(self.user_public).read(['name'])

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_access_slide_preview(self):
        """Slideswithpreviewflagarealwaysvisibleeventononmembersifpublished"""
        self.channel.write({'enroll':'invite'})
        self.slide.write({'is_preview':True})
        self.slide.flush(['is_preview'])

        self.slide.with_user(self.user_officer).read(['name'])
        self.slide.with_user(self.user_manager).read(['name'])
        self.slide.with_user(self.user_emp).read(['name'])
        self.slide.with_user(self.user_portal).read(['name'])
        self.slide.with_user(self.user_public).read(['name'])


@tagged('functional','security')
classTestRemoveMembership(common.SlidesCase):

    defsetUp(self):
        super(TestRemoveMembership,self).setUp()
        self.channel_partner=self.env['slide.channel.partner'].create({
            'channel_id':self.channel.id,
            'partner_id':self.customer.id,
        })

        self.slide_partner=self.env['slide.slide.partner'].create({
            'slide_id':self.slide.id,
            'channel_id':self.channel.id,
            'partner_id':self.customer.id
        })

    deftest_security_unlink(self):
        #Onlythepublishercanunlinkchannel_partner(andslide_partnerbyextension)
        withself.assertRaises(AccessError):
            self.channel_partner.with_user(self.user_public).unlink()
        withself.assertRaises(AccessError):
            self.channel_partner.with_user(self.user_portal).unlink()
        withself.assertRaises(AccessError):
            self.channel_partner.with_user(self.user_emp).unlink()

    deftest_slide_partner_remove(self):
        id_slide_partner=self.slide_partner.id
        id_channel_partner=self.channel_partner.id
        self.channel_partner.with_user(self.user_officer).unlink()
        self.assertFalse(self.env['slide.channel.partner'].search([('id','=','%d'%id_channel_partner)]))
        #Slide(s)relatedtothechannelandthepartnerisunlinktoo.
        self.assertFalse(self.env['slide.slide.partner'].search([('id','=','%d'%id_slide_partner)]))


@tagged('functional')
classTestAccessFeatures(common.SlidesCase):

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_channel_auto_subscription(self):
        user_employees=self.env['res.users'].search([('groups_id','in',self.ref('base.group_user'))])

        channel=self.env['slide.channel'].with_user(self.user_officer).create({
            'name':'Test',
            'enroll':'invite',
            'is_published':True,
            'enroll_group_ids':[(4,self.ref('base.group_user'))]
        })
        channel.invalidate_cache(['partner_ids'])
        self.assertEqual(channel.partner_ids,user_employees.mapped('partner_id'))

        new_user=self.env['res.users'].create({
            'name':'NewUser',
            'login':'NewUser',
            'groups_id':[(6,0,[self.ref('base.group_user')])]
        })
        channel.invalidate_cache()
        self.assertEqual(channel.partner_ids,user_employees.mapped('partner_id')|new_user.partner_id)

        new_user_2=self.env['res.users'].create({
            'name':'NewUser2',
            'login':'NewUser2',
            'groups_id':[(5,0)]
        })
        channel.invalidate_cache()
        self.assertEqual(channel.partner_ids,user_employees.mapped('partner_id')|new_user.partner_id)
        new_user_2.write({'groups_id':[(4,self.ref('base.group_user'))]})
        channel.invalidate_cache()
        self.assertEqual(channel.partner_ids,user_employees.mapped('partner_id')|new_user.partner_id|new_user_2.partner_id)

        new_user_3=self.env['res.users'].create({
            'name':'NewUser3',
            'login':'NewUser3',
            'groups_id':[(5,0)]
        })
        channel.invalidate_cache()
        self.assertEqual(channel.partner_ids,user_employees.mapped('partner_id')|new_user.partner_id|new_user_2.partner_id)
        self.env.ref('base.group_user').write({'users':[(4,new_user_3.id)]})
        channel.invalidate_cache()
        self.assertEqual(channel.partner_ids,user_employees.mapped('partner_id')|new_user.partner_id|new_user_2.partner_id|new_user_3.partner_id)

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_channel_access_fields_employee(self):
        channel_manager=self.channel.with_user(self.user_manager)
        channel_emp=self.channel.with_user(self.user_emp)
        channel_portal=self.channel.with_user(self.user_portal)
        self.assertFalse(channel_emp.can_upload)
        self.assertFalse(channel_emp.can_publish)
        self.assertFalse(channel_portal.can_upload)
        self.assertFalse(channel_portal.can_publish)

        #allowemployeestoupload
        channel_manager.write({'upload_group_ids':[(4,self.ref('base.group_user'))]})
        self.assertTrue(channel_emp.can_upload)
        self.assertFalse(channel_emp.can_publish)
        self.assertFalse(channel_portal.can_upload)
        self.assertFalse(channel_portal.can_publish)

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_channel_access_fields_officer(self):
        self.assertEqual(self.channel.user_id,self.user_officer)

        channel_officer=self.channel.with_user(self.user_officer)
        self.assertTrue(channel_officer.can_upload)
        self.assertTrue(channel_officer.can_publish)

        channel_officer.write({'upload_group_ids':[(4,self.ref('base.group_system'))]})
        self.assertTrue(channel_officer.can_upload)
        self.assertTrue(channel_officer.can_publish)

        channel_manager=self.channel.with_user(self.user_manager)
        channel_manager.write({
            'upload_group_ids':[(5,0)],
            'user_id':self.user_manager.id
        })
        self.assertFalse(channel_officer.can_upload)
        self.assertFalse(channel_officer.can_publish)
        self.assertTrue(channel_manager.can_upload)
        self.assertTrue(channel_manager.can_publish)

    @mute_logger('flectra.models','flectra.addons.base.models.ir_rule')
    deftest_channel_access_fields_manager(self):
        channel_manager=self.channel.with_user(self.user_manager)
        self.assertTrue(channel_manager.can_upload)
        self.assertTrue(channel_manager.can_publish)

        #testuploadgrouplimitation:memberofgroup_systemORresponsibleORmanager
        channel_manager.write({'upload_group_ids':[(4,self.ref('base.group_system'))]})
        self.assertFalse(channel_manager.can_upload)
        self.assertFalse(channel_manager.can_publish)
        channel_manager.write({'user_id':self.user_manager.id})
        self.assertTrue(channel_manager.can_upload)
        self.assertTrue(channel_manager.can_publish)

        #Needsthemanagertowriteonchannelasuser_officerisnottheresponsibleanymore
        channel_manager.write({'upload_group_ids':[(5,0)]})
        self.assertTrue(channel_manager.can_upload)
        self.assertTrue(channel_manager.can_publish)
        channel_manager.write({'user_id':self.user_officer.id})
        self.assertTrue(channel_manager.can_upload)
        self.assertTrue(channel_manager.can_publish)

        #superusershouldalwaysbeabletopublishevenifhe'snottheresponsible
        channel_superuser=self.channel.sudo()
        channel_superuser.invalidate_cache(['can_upload','can_publish'])
        self.assertTrue(channel_superuser.can_upload)
        self.assertTrue(channel_superuser.can_publish)

    @mute_logger('flectra.models.unlink','flectra.addons.base.models.ir_rule','flectra.addons.base.models.ir_model')
    deftest_resource_access(self):
        resource_values={
            'name':'Image',
            'slide_id':self.slide_3.id,
            'data':base64.b64encode(b'Somecontent')
        }
        resource1,resource2=self.env['slide.slide.resource'].with_user(self.user_officer).create(
            [resource_valuesfor_inrange(2)])

        #Nopublicaccess
        withself.assertRaises(AccessError):
            resource1.with_user(self.user_public).read(['name'])
        withself.assertRaises(AccessError):
            resource1.with_user(self.user_public).write({'name':'othername'})

        #Norandomportalaccess
        withself.assertRaises(AccessError):
            resource1.with_user(self.user_portal).read(['name'])

        #Memberscanonlyread
        self.env['slide.channel.partner'].create({
            'channel_id':self.channel.id,
            'partner_id':self.user_portal.partner_id.id,
        })
        resource1.with_user(self.user_portal).read(['name'])
        withself.assertRaises(AccessError):
            resource1.with_user(self.user_portal).write({'name':'othername'})

        #Otherofficerscanonlyread
        user_officer_other=mail_new_test_user(
            self.env,name='OrnellaOfficer',login='user_officer_2',email='officer2@example.com',
            groups='base.group_user,website_slides.group_website_slides_officer'
        )
        resource1.with_user(user_officer_other).read(['name'])
        withself.assertRaises(AccessError):
            resource1.with_user(user_officer_other).write({'name':'Anothername'})

        withself.assertRaises(AccessError):
            self.env['slide.slide.resource'].with_user(user_officer_other).create(resource_values)
        withself.assertRaises(AccessError):
            resource1.with_user(user_officer_other).unlink()

        #Responsibleofficercandoanythingontheirownchannels
        resource1.with_user(self.user_officer).write({'name':'othername'})
        resource1.with_user(self.user_officer).unlink()

        #Managerscandoanythingonallchannels
        resource2.with_user(self.user_manager).write({'name':'Anothername'})
        resource2.with_user(self.user_manager).unlink()
        self.env['slide.slide.resource'].with_user(self.user_manager).create(resource_values)
