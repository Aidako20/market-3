#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.


fromflectra.tests.commonimportSavepointCase
fromflectra.exceptionsimportAccessError,UserError


classTestMailSecurity(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.secret_group=cls.env['res.groups'].create({
            'name':'secretgroup',
        })
        cls.user_1=cls.env['res.users'].create({
            'name':'User1',
            'login':'user_1',
            'email':'---',
            'groups_id':[(6,0,[cls.secret_group.id,cls.env.ref('base.group_user').id])],
        })
        cls.user_2=cls.env['res.users'].create({
            'name':'User2',
            'login':'user_2',
            'email':'---',
            'groups_id':[(6,0,[cls.secret_group.id,cls.env.ref('base.group_user').id])],
        })
        cls.user_3=cls.env['res.users'].create({
            'name':'User3',
            'login':'user_3',
            'email':'---',
        })

        cls.private_channel_1=cls.env['mail.channel'].create({
            'name':'Secretchannel',
            'public':'private',
            'channel_type':'channel',
        })
        cls.group_channel_1=cls.env['mail.channel'].create({
            'name':'Groupchannel',
            'public':'groups',
            'channel_type':'channel',
            'group_public_id':cls.secret_group.id,
        })
        cls.public_channel_1=cls.env['mail.channel'].create({
            'name':'Publicchannelofuser1',
            'public':'public',
            'channel_type':'channel',
        })
        cls.private_channel_1.channel_last_seen_partner_ids.unlink()
        cls.group_channel_1.channel_last_seen_partner_ids.unlink()
        cls.public_channel_1.channel_last_seen_partner_ids.unlink()

    ###########################
    #PRIVATECHANNEL&BASIC#
    ###########################

    deftest_channel_acls_01(self):
        """Testaccessonprivatechannel."""
        res=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertFalse(res)

        #User1canjoinprivatechannelwithSUDO
        self.private_channel_1.with_user(self.user_1).sudo().action_follow()
        res=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(res.partner_id,self.user_1.partner_id)

        #User2cannotjoinprivatechannel
        withself.assertRaises(AccessError):
            self.private_channel_1.with_user(self.user_2).action_follow()

        #Butuser2canjoinpublicchannel
        self.public_channel_1.with_user(self.user_2).action_follow()
        res=self.env['mail.channel.partner'].search([('channel_id','=',self.public_channel_1.id)])
        self.assertEqual(res.partner_id,self.user_2.partner_id)

        #User2cannotcreatea`mail.channel.partner`tojointheprivatechannel
        withself.assertRaises(AccessError):
            self.env['mail.channel.partner'].with_user(self.user_2).create({
                'partner_id':self.user_2.partner_id.id,
                'channel_id':self.private_channel_1.id,
            })

        #User2cannotwriteon`mail.channel.partner`tojointheprivatechannel
        channel_partner=self.env['mail.channel.partner'].with_user(self.user_2).search([('partner_id','=',self.user_2.partner_id.id)])[0]
        withself.assertRaises(AccessError):
            channel_partner.channel_id=self.private_channel_1.id
        withself.assertRaises(AccessError):
            channel_partner.write({'channel_id':self.private_channel_1.id})

        #ButwithSUDO,User2can
        channel_partner.sudo().channel_id=self.private_channel_1.id

        #User2cannotwriteonthe`partner_id`of`mail.channel.partner`
        #ofanotherpartnertojoinaprivatechannel
        channel_partner_1=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id),('partner_id','=',self.user_1.partner_id.id)])
        withself.assertRaises(AccessError):
            channel_partner_1.with_user(self.user_2).partner_id=self.user_2.partner_id
        self.assertEqual(channel_partner_1.partner_id,self.user_1.partner_id)

        #butwithSUDOhecan...
        channel_partner_1.with_user(self.user_2).sudo().partner_id=self.user_2.partner_id
        self.assertEqual(channel_partner_1.partner_id,self.user_2.partner_id)

    deftest_channel_acls_03(self):
        """Testinvitationinprivatechannelpart1(inviteusingcrudmethods)."""
        self.private_channel_1.with_user(self.user_1).sudo().action_follow()
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(len(channel_partners),1)

        #User2isnotintheprivatechannel,hecannotinviteuser3
        withself.assertRaises(AccessError):
            self.env['mail.channel.partner'].with_user(self.user_2).create({
                'partner_id':self.user_3.partner_id.id,
                'channel_id':self.private_channel_1.id,
            })

        #User1isintheprivatechannel,hecaninviteotherusers
        self.env['mail.channel.partner'].with_user(self.user_1).create({
            'partner_id':self.user_3.partner_id.id,
            'channel_id':self.private_channel_1.id,
        })
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id|self.user_3.partner_id)

        #ButUser3cannotwriteonthe`mail.channel.partner`ofotheruser
        channel_partner_1=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id),('partner_id','=',self.user_1.partner_id.id)])
        channel_partner_3=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id),('partner_id','=',self.user_3.partner_id.id)])
        channel_partner_3.with_user(self.user_3).custom_channel_name='Test'
        withself.assertRaises(AccessError):
            channel_partner_1.with_user(self.user_2).custom_channel_name='Blabla'
        self.assertNotEqual(channel_partner_1.custom_channel_name,'Blabla')

    deftest_channel_acls_04(self):
        """Testinvitationinprivatechannelpart2(use`invite`action)."""
        self.private_channel_1.with_user(self.user_1).sudo().action_follow()
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id)

        #User2isnotinthechannel,hecannotinviteuser3
        withself.assertRaises(AccessError):
            self.private_channel_1.with_user(self.user_2).channel_invite([self.user_3.partner_id.id])
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id)

        #User1isinthechannel,hecannotinviteuser3
        self.private_channel_1.with_user(self.user_1).channel_invite([self.user_3.partner_id.id])
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id|self.user_3.partner_id)

    deftest_channel_acls_05(self):
        """Testkick/leavechannel."""
        self.private_channel_1.with_user(self.user_1).sudo().action_follow()
        self.private_channel_1.with_user(self.user_3).sudo().action_follow()
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.private_channel_1.id)])
        self.assertEqual(len(channel_partners),2)

        #User2isnotinthechannel,hecannotkickuser1
        withself.assertRaises(AccessError):
            channel_partners.with_user(self.user_2).unlink()

        #User3isinthechannel,hecankickuser1
        channel_partners.with_user(self.user_3).unlink()

    #################
    #GROUPCHANNEL#
    #################
    deftest_channel_acls_06(self):
        """Testbasicsongroupchannel."""
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.group_channel_1.id)])
        self.assertFalse(channel_partners)

        #user1isinthegroup,hecanjointhechannel
        self.group_channel_1.with_user(self.user_1).action_follow()
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.group_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id)

        #user3isnotinthegroup,hecannotjoin
        withself.assertRaises(AccessError):
            self.group_channel_1.with_user(self.user_3).action_follow()

        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.group_channel_1.id)])
        withself.assertRaises(AccessError):
            channel_partners.with_user(self.user_3).partner_id=self.user_3.partner_id

        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.group_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id)

        #user1cannotinviteuser3becausehe'snotinthegroup
        withself.assertRaises(UserError):
            self.group_channel_1.with_user(self.user_1).channel_invite([self.user_3.partner_id.id])
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.group_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id)

        #butuser2isinthegroupandcanbeinvitedbyuser1
        self.group_channel_1.with_user(self.user_1).channel_invite([self.user_2.partner_id.id])
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.group_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id|self.user_2.partner_id)

    ##################
    #PUBLICCHANNEL#
    ##################
    deftest_channel_acls_07(self):
        """Testbasicsonpublicchannel."""
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.public_channel_1.id)])
        self.assertFalse(channel_partners)

        self.public_channel_1.with_user(self.user_1).action_follow()
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.public_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id)

        self.public_channel_1.with_user(self.user_2).action_follow()
        channel_partners=self.env['mail.channel.partner'].search([('channel_id','=',self.public_channel_1.id)])
        self.assertEqual(channel_partners.mapped('partner_id'),self.user_1.partner_id|self.user_2.partner_id)
