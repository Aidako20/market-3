#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.mail.tests.commonimportmail_new_test_user
fromflectra.exceptionsimportAccessError
fromflectra.testsimporttagged,common,new_test_user
fromflectra.toolsimportmute_logger


@tagged('security')
classTestAccessRating(common.SavepointCase):

    @classmethod
    defsetUpClass(cls):
        super(TestAccessRating,cls).setUpClass()

        cls.user_manager_partner=mail_new_test_user(
            cls.env,name='JeanAdmin',login='user_mana',email='admin@example.com',
            groups='base.group_partner_manager,base.group_system'
        )

        cls.user_emp=mail_new_test_user(
            cls.env,name='EglantineEmployee',login='user_emp',email='employee@example.com',
            groups='base.group_user'
        )

        cls.user_portal=mail_new_test_user(
            cls.env,name='PatrickPortal',login='user_portal',email='portal@example.com',
            groups='base.group_portal'
        )

        cls.user_public=mail_new_test_user(
            cls.env,name='PaulinePublic',login='user_public',email='public@example.com',
            groups='base.group_public'
        )

        cls.partner_to_rate=cls.env['res.partner'].with_user(cls.user_manager_partner).create({
            "name":"PartnertoRate:("
        })


    @mute_logger('flectra.addons.base.models.ir_model')
    deftest_rating_access(self):
        """Securitytest:onlyaemployee(usergroup)cancreateandwriteratingobject"""
        #Publicandportalusercan'tAccessdirecltytotheratings
        withself.assertRaises(AccessError):
            self.env['rating.rating'].with_user(self.user_portal).create({
                'res_model_id':self.env['ir.model'].sudo().search([('model','=','res.partner')],limit=1).id,
                'res_model':'res.partner',
                'res_id':self.partner_to_rate.id,
                'rating':1
            })
        withself.assertRaises(AccessError):
            self.env['rating.rating'].with_user(self.user_public).create({
                'res_model_id':self.env['ir.model'].sudo().search([('model','=','res.partner')],limit=1).id,
                'res_model':'res.partner',
                'res_id':self.partner_to_rate.id,
                'rating':3
            })

        #Noerrorwithemployee
        ratting=self.env['rating.rating'].with_user(self.user_emp).create({
            'res_model_id':self.env['ir.model'].sudo().search([('model','=','res.partner')],limit=1).id,
            'res_model':'res.partner',
            'res_id':self.partner_to_rate.id,
            'rating':3
        })

        withself.assertRaises(AccessError):
            ratting.with_user(self.user_portal).write({
                'feedback':'Youshouldnotpass!'
            })
        withself.assertRaises(AccessError):
            ratting.with_user(self.user_public).write({
                'feedback':'Youshouldnotpass!'
            })
