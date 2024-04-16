#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.tests.commonimportSavepointCase,users
fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.exceptionsimportAccessError
fromflectra.testsimporttagged
fromflectra.toolsimportmute_logger


@tagged('post_install','-at_install')
classTestSmsTemplateAccessRights(SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.user_admin=mail_new_test_user(cls.env,login='user_system',groups='base.group_system')
        cls.basic_user=mail_new_test_user(cls.env,login='user_employee',groups='base.group_user')
        sms_enabled_models=cls.env['ir.model'].search([('is_mail_thread','=',True),('transient','=',False)])
        vals=[]
        formodelinsms_enabled_models:
            vals.append({
                'name':'SMSTemplate'+model.name,
                'body':'BodyTest',
                'model_id':model.id,
            })
        cls.sms_templates=cls.env['sms.template'].create(vals)

    @users('user_employee')
    @mute_logger('flectra.models.unlink')
    deftest_access_rights_user(self):
        #Checkifamemberofgroup_usercanonlyreadonsms.template
        forsms_templateinself.env['sms.template'].browse(self.sms_templates.ids):
            self.assertTrue(bool(sms_template.name))
            withself.assertRaises(AccessError):
                sms_template.write({'name':'UpdateTemplate'})
            withself.assertRaises(AccessError):
                self.env['sms.template'].create({
                    'name':'NewSMSTemplate'+sms_template.model_id.name,
                    'body':'BodyTest',
                    'model_id':sms_template.model_id.id,
                })
            withself.assertRaises(AccessError):
                sms_template.unlink()

    @users('user_system')
    @mute_logger('flectra.models.unlink','flectra.addons.base.models.ir_model')
    deftest_access_rights_system(self):
        admin=self.env.ref('base.user_admin')
        forsms_templateinself.env['sms.template'].browse(self.sms_templates.ids):
            self.assertTrue(bool(sms_template.name))
            sms_template.write({'body':'Newbodyfromadmin'})
            self.env['sms.template'].create({
                'name':'NewSMSTemplate'+sms_template.model_id.name,
                'body':'BodyTest',
                'model_id':sms_template.model_id.id,
            })

            #checkadminisallowedtoreadalltemplatessincehecanbeamemberof
            #othergroupsapplyingrestrictionsbasedonthemodel
            self.assertTrue(bool(self.env['sms.template'].with_user(admin).browse(sms_template.ids).name))

            sms_template.unlink()
