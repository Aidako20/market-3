#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.exceptionsimportUserError
fromflectra.tests.commonimportusers
fromflectra.addons.website.toolsimportMockRequest
fromflectra.addons.website_blog.tests.commonimportTestWebsiteBlogCommon
fromflectra.addons.portal.controllers.mailimportPortalChatter


classTestWebsiteBlogFlow(TestWebsiteBlogCommon):
    defsetUp(self):
        super(TestWebsiteBlogFlow,self).setUp()
        group_portal=self.env.ref('base.group_portal')
        self.user_portal=self.env['res.users'].with_context({'no_reset_password':True}).create({
            'name':'DorianPortal',
            'login':'portal_user',
            'email':'portal_user@example.com',
            'notification_type':'inbox',
            'groups_id':[(6,0,[group_portal.id])]
        })

    deftest_website_blog_followers(self):
        """Testtheflowoffollowersandnotificationsforblogs.Intended
        flow:

         -peoplesubscribetoablog
         -whencreatinganewpost,nobodyexceptthecreatorfollowsit
         -peoplesubscribedtotheblogdoesnotreceivecommentsonposts
         -whenpublished,anotificationissenttoallblogfollowers
         -ifsomeonesubscribetothepostorcommentit,itbecomefollower
           andreceivenotificationforfuturecomments."""

        #Createanewblog,subscribetheemployeetotheblog
        self.assertIn(
            self.user_blogmanager.partner_id,self.test_blog.message_partner_ids,
            'website_blog:blogcreateshouldbeintheblogfollowers')
        self.test_blog.message_subscribe([self.user_employee.partner_id.id,self.user_public.partner_id.id])

        #Createanewpost,blogfollowersshouldnotfollowthepost
        self.assertNotIn(
            self.user_employee.partner_id,self.test_blog_post.message_partner_ids,
            'website_blog:subscribingtoablogshouldnotsubscribetoitsposts')
        self.assertNotIn(
            self.user_public.partner_id,self.test_blog_post.message_partner_ids,
            'website_blog:subscribingtoablogshouldnotsubscribetoitsposts')

        #Publishtheblog
        self.test_blog_post.write({'website_published':True})

        #Checkpublishmessagehasbeensenttoblogfollowers
        publish_message=next((mforminself.test_blog_post.blog_id.message_idsifm.subtype_id.id==self.ref('website_blog.mt_blog_blog_published')),None)
        self.assertEqual(
            publish_message.notified_partner_ids,
            self.user_employee.partner_id|self.user_public.partner_id,
            'website_blog:peuplefollowingablogshouldbenotifiedofapublishedpost')

        #Armandpostsamessage->becomesfollower
        self.test_blog_post.sudo().message_post(
            body='ArmandeBlogUserCommented',
            message_type='comment',
            author_id=self.user_employee.partner_id.id,
            subtype_xmlid='mail.mt_comment',
        )
        self.assertIn(
            self.user_employee.partner_id,self.test_blog_post.message_partner_ids,
            'website_blog:peoplecommentingapostshouldfollowitafterwards')

    @users('portal_user')
    deftest_blog_comment(self):
        """Testcommentonblogpostwithattachment."""
        attachment=self.env['ir.attachment'].sudo().create({
            'name':'some_attachment.pdf',
            'res_model':'mail.compose.message',
            'datas':'test',
            'type':'binary',
            'access_token':'azerty',
        })

        withMockRequest(self.env):
            PortalChatter().portal_chatter_post(
                'blog.post',
                self.test_blog_post.id,
                'Testmessageblogpost',
                attachment_ids=str(attachment.id),
                attachment_tokens=attachment.access_token
            )

        self.assertTrue(self.env['mail.message'].sudo().search(
            [('model','=','blog.post'),('attachment_ids','in',attachment.ids)]))

        second_attachment=self.env['ir.attachment'].sudo().create({
            'name':'some_attachment.pdf',
            'res_model':'mail.compose.message',
            'datas':'test',
            'type':'binary',
            'access_token':'azerty',
        })

        withself.assertRaises(UserError),MockRequest(self.env):
            PortalChatter().portal_chatter_post(
                'blog.post',
                self.test_blog_post.id,
                'Testmessageblogpost',
                attachment_ids=str(second_attachment.id),
                attachment_tokens='wrong_token'
            )

        self.assertFalse(self.env['mail.message'].sudo().search(
            [('model','=','blog.post'),('attachment_ids','in',second_attachment.ids)]))
