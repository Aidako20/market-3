#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.addons.project.tests.test_project_baseimportTestProjectCommon
fromflectra.exceptionsimportAccessError,ValidationError
fromflectra.tests.commonimportusers


classTestAccessRights(TestProjectCommon):

    defsetUp(self):
        super().setUp()
        self.task=self.create_task('Maketheworldabetterplace')
        self.user=mail_new_test_user(self.env,'Internaluser',groups='base.group_user')
        self.portal=mail_new_test_user(self.env,'Portaluser',groups='base.group_portal')

    defcreate_task(self,name,*,with_user=None,**kwargs):
        values=dict(name=name,project_id=self.project_pigs.id,**kwargs)
        returnself.env['project.task'].with_user(with_userorself.env.user).create(values)


classTestCRUDVisibilityFollowers(TestAccessRights):

    defsetUp(self):
        super().setUp()
        self.project_pigs.privacy_visibility='followers'

    @users('Internaluser','Portaluser')
    deftest_project_no_write(self):
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletowriteontheproject"%self.env.user.name):
            self.project_pigs.with_user(self.env.user).name="Takeovertheworld"

        self.project_pigs.allowed_user_ids=self.env.user
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletowriteontheproject"%self.env.user.name):
            self.project_pigs.with_user(self.env.user).name="Takeovertheworld"

    @users('Internaluser','Portaluser')
    deftest_project_no_unlink(self):
        self.project_pigs.task_ids.unlink()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletounlinktheproject"%self.env.user.name):
            self.project_pigs.with_user(self.env.user).unlink()

        self.project_pigs.allowed_user_ids=self.env.user
        self.project_pigs.task_ids.unlink()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletounlinktheproject"%self.env.user.name):
            self.project_pigs.with_user(self.env.user).unlink()

    @users('Internaluser','Portaluser')
    deftest_project_no_read(self):
        self.project_pigs.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadtheproject"%self.env.user.name):
            self.project_pigs.with_user(self.env.user).name

    @users('Portaluser')
    deftest_project_allowed_portal_no_read(self):
        self.project_pigs.allowed_user_ids=self.env.user
        self.project_pigs.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadtheproject"%self.env.user.name):
            self.project_pigs.with_user(self.env.user).name

    @users('Internaluser')
    deftest_project_allowed_internal_read(self):
        self.project_pigs.allowed_user_ids=self.env.user
        self.project_pigs.invalidate_cache()
        self.project_pigs.with_user(self.env.user).name

    @users('Internaluser','Portaluser')
    deftest_task_no_read(self):
        self.task.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Portaluser')
    deftest_task_allowed_portal_no_read(self):
        self.project_pigs.allowed_user_ids=self.env.user
        self.task.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Internaluser')
    deftest_task_allowed_internal_read(self):
        self.project_pigs.allowed_user_ids=self.env.user
        self.task.invalidate_cache()
        self.task.with_user(self.env.user).name

    @users('Internaluser','Portaluser')
    deftest_task_no_write(self):
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletowriteonthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name="Painttheworldinblack&white"

        self.project_pigs.allowed_user_ids=self.env.user
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletowriteonthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name="Painttheworldinblack&white"

    @users('Internaluser','Portaluser')
    deftest_task_no_create(self):
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletocreateatask"%self.env.user.name):
            self.create_task("Archivetheworld,it'snotneededanymore")

        self.project_pigs.allowed_user_ids=self.env.user
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletocreateatask"%self.env.user.name):
            self.create_task("Archivetheworld,it'snotneededanymore")

    @users('Internaluser','Portaluser')
    deftest_task_no_unlink(self):
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletounlinkthetask"%self.env.user.name):
            self.task.with_user(self.env.user).unlink()

        self.project_pigs.allowed_user_ids=self.env.user
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletounlinkthetask"%self.env.user.name):
            self.task.with_user(self.env.user).unlink()


classTestCRUDVisibilityPortal(TestAccessRights):

    defsetUp(self):
        super().setUp()
        self.project_pigs.privacy_visibility='portal'

    @users('Portaluser')
    deftest_task_portal_no_read(self):
        self.task.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Portaluser')
    deftest_task_allowed_portal_read(self):
        self.project_pigs.allowed_user_ids=self.env.user
        self.task.invalidate_cache()
        self.task.with_user(self.env.user).name

    @users('Internaluser')
    deftest_task_internal_read(self):
        self.task.with_user(self.env.user).name


classTestCRUDVisibilityEmployees(TestAccessRights):

    defsetUp(self):
        super().setUp()
        self.project_pigs.privacy_visibility='employees'

    @users('Portaluser')
    deftest_task_portal_no_read(self):
        self.task.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name

        self.project_pigs.allowed_user_ids=self.env.user
        self.task.invalidate_cache()
        withself.assertRaises(AccessError,msg="%sshouldnotbeabletoreadthetask"%self.env.user.name):
            self.task.with_user(self.env.user).name

    @users('Internaluser')
    deftest_task_allowed_portal_read(self):
        self.task.invalidate_cache()
        self.task.with_user(self.env.user).name


classTestAllowedUsers(TestAccessRights):

    defsetUp(self):
        super().setUp()
        self.project_pigs.privacy_visibility='followers'

    deftest_project_permission_added(self):
        self.project_pigs.allowed_user_ids=self.user
        self.assertIn(self.user,self.task.allowed_user_ids)

    deftest_project_default_permission(self):
        self.project_pigs.allowed_user_ids=self.user
        task=self.create_task("Reviewtheendoftheworld")
        self.assertIn(self.user,task.allowed_user_ids)

    deftest_project_default_customer_permission(self):
        self.project_pigs.privacy_visibility='portal'
        self.project_pigs.partner_id=self.portal.partner_id
        self.assertIn(self.portal,self.task.allowed_user_ids)
        self.assertIn(self.portal,self.project_pigs.allowed_user_ids)

    deftest_project_permission_removed(self):
        self.project_pigs.allowed_user_ids=self.user
        self.project_pigs.allowed_user_ids-=self.user
        self.assertNotIn(self.user,self.task.allowed_user_ids)

    deftest_project_specific_permission(self):
        self.project_pigs.allowed_user_ids=self.user
        john=mail_new_test_user(self.env,login='John')
        self.task.allowed_user_ids|=john
        self.project_pigs.allowed_user_ids-=self.user
        self.assertIn(john,self.task.allowed_user_ids,"Johnshouldstillbeallowedtoreadthetask")

    deftest_project_specific_remove_mutliple_tasks(self):
        self.project_pigs.allowed_user_ids=self.user
        john=mail_new_test_user(self.env,login='John')
        task=self.create_task('task')
        self.task.allowed_user_ids|=john
        self.project_pigs.allowed_user_ids-=self.user
        self.assertIn(john,self.task.allowed_user_ids)
        self.assertNotIn(john,task.allowed_user_ids)
        self.assertNotIn(self.user,task.allowed_user_ids)
        self.assertNotIn(self.user,self.task.allowed_user_ids)

    deftest_no_portal_allowed(self):
        withself.assertRaises(ValidationError,msg="Itshouldnotallowtoaddportalusers"):
            self.task.allowed_user_ids=self.portal

    deftest_visibility_changed(self):
        self.project_pigs.privacy_visibility='portal'
        self.task.allowed_user_ids|=self.portal
        self.assertNotIn(self.user,self.task.allowed_user_ids,"Internalusershouldhavebeenremovedfromallowedusers")
        self.project_pigs.privacy_visibility='employees'
        self.assertNotIn(self.portal,self.task.allowed_user_ids,"Portalusershouldhavebeenremovedfromallowedusers")

    deftest_write_task(self):
        self.user.groups_id|=self.env.ref('project.group_project_user')
        self.assertNotIn(self.user,self.project_pigs.allowed_user_ids)
        self.task.allowed_user_ids=self.user
        self.project_pigs.invalidate_cache()
        self.task.invalidate_cache()
        self.task.with_user(self.user).name="Icaneditatask!"

    deftest_no_write_project(self):
        self.user.groups_id|=self.env.ref('project.group_project_user')
        self.assertNotIn(self.user,self.project_pigs.allowed_user_ids)
        withself.assertRaises(AccessError,msg="Usershouldnotbeabletoeditproject"):
            self.project_pigs.with_user(self.user).name="Ican'teditatask!"
