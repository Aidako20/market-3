#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64

fromflectra.exceptionsimportAccessError
fromflectra.testsimportSavepointCase


classtestAttachmentAccess(SavepointCase):
    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.user=cls.env['res.users'].create({
            'name':"foo",
            'login':"foo",
            'email':"foo@bar.com",
            'groups_id':[(6,0,[
                cls.env.ref('base.group_user').id,
                cls.env.ref('base.group_partner_manager').id,
            ])]
        })
        cls.letter_defaults={
            'model':cls.user.partner_id._name,
            'res_id':cls.user.partner_id.id,
            'partner_id':cls.user.partner_id.id,
        }

    deftest_user_letter_attachment_without_res_fields(self):
        """Testanemployeecancreatealetterlinkedtoanattachmentwithoutres_model/res_id"""
        env_user=self.env(user=self.user)
        #Asuser,createanattachmentwithoutres_model/res_id
        attachment=env_user['ir.attachment'].create({'name':'foo','datas':base64.b64encode(b'foo')})
        #Asuser,createasnailmail.letterlinkedtothatattachment
        letter=env_user['snailmail.letter'].create({'attachment_id':attachment.id,**self.letter_defaults})
        #Asuser,ensurethecontentoftheattachmentcanbereadthroughtheletter
        self.assertEqual(base64.b64decode(letter.attachment_datas),b'foo')
        #Asuser,createanotherattachmentwithoutres_model/res_id
        attachment_2=env_user['ir.attachment'].create({'name':'foo','datas':base64.b64encode(b'bar')})
        #Asuser,changetheattachmentofthelettertothissecondattachment
        letter.write({'attachment_id':attachment_2.id})
        #Asuser,ensurethecontentofthissecondattachmentcanbereadthroughtheletter
        self.assertEqual(base64.b64decode(letter.attachment_datas),b'bar')

    deftest_user_letter_attachment_without_res_fields_created_by_admin(self):
        """Testanemployeecanreadthecontentoftheletter'sattachmentcreatedbyanotheruser,theadmin,
        andtheattachmentdoesnothaveares_model/res_id
        """
        #Asadmin,createanattachmentwithoutres_model/res_id
        attachment=self.env['ir.attachment'].create({'name':'foo','datas':base64.b64encode(b'foo')})
        #Asadmin,createasnailmail.letterlinkedtothatattachment
        letter=self.env['snailmail.letter'].create({'attachment_id':attachment.id,**self.letter_defaults})

        #Asuser,ensuretheattachmentitselfcannotberead
        attachment.invalidate_cache()
        withself.assertRaises(AccessError):
            attachment.with_user(self.user).datas
        #But,asuser,thecontentoftheattachmentcanbereadthroughtheletter
        self.assertEqual(base64.b64decode(letter.with_user(self.user).attachment_datas),b'foo')

        #Asadmin,createasecondattachmentwithoutres_model/res_id
        attachment=self.env['ir.attachment'].create({'name':'bar','datas':base64.b64encode(b'bar')})
        #Asadmin,linkthissecondattachmenttothepreviouslycreatedletter(writeinsteadofcreate)
        letter.write({'attachment_id':attachment.id})

        #Asuserensuretheattachmentitselfcannotberead
        attachment.invalidate_cache()
        withself.assertRaises(AccessError):
            self.assertEqual(base64.b64decode(attachment.with_user(self.user).datas),b'bar')
        #But,asuser,thecontentoftheattachmentcanbereadthroughtheletter
        self.assertEqual(base64.b64decode(letter.with_user(self.user).attachment_datas),b'bar')

    deftest_user_read_unallowed_attachment(self):
        """Testausercannotaccessanattachmentheisnotsupposedtothroughasnailmail.letter"""
        #Asadmin,createanattachmentforwhichyourequirethesettingsgrouptoaccess
        base_module=self.env.ref('base.module_base')
        attachment_forbidden=self.env['ir.attachment'].create({
            'name':'foo','datas':base64.b64encode(b'foo'),
            'res_model':base_module._name,'res_id':base_module.id,
        })
        #Asuser,makesurethisisindeednotpossibletoaccessthatattachmentdatadirectly
        attachment_forbidden.invalidate_cache()
        withself.assertRaises(AccessError):
            attachment_forbidden.with_user(self.user).datas
        #Asuser,createaletterpointingtothatattachment
        #andmakesureitraisesanaccesserror
        withself.assertRaises(AccessError):
            letter=self.env['snailmail.letter'].with_user(self.user).create({
                'attachment_id':attachment_forbidden.id,
                **self.letter_defaults,
            })
            letter.attachment_datas

        #Asuser,updatetheattachmentofanexistinglettertotheunallowedattachment
        #andmakesureitraisesanaccesserror
        attachment_tmp=self.env['ir.attachment'].with_user(self.user).create({
            'name':'bar','datas':base64.b64encode(b'bar'),
        })
        letter=self.env['snailmail.letter'].with_user(self.user).create({
            'attachment_id':attachment_tmp.id,
            **self.letter_defaults,
        })
        withself.assertRaises(AccessError):
            letter.write({'attachment_id':attachment_forbidden.id})
            letter.attachment_datas
