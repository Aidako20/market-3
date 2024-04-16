#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_forum.tests.commonimportTestForumCommon


classTestForumTag(TestForumCommon):
    @classmethod
    defsetUpClass(cls):
        super().setUpClass()
        cls.env['forum.tag'].search([]).unlink()
        cls.tags=cls.env['forum.tag'].create(
            [{'forum_id':cls.forum.id,'name':f'TestTag{tag_idx}'}fortag_idxinrange(1,3)]
        )
        cls.env['forum.post'].create(
            [{'name':'Postingabouttag1','forum_id':cls.forum.id,'tag_ids':[[6,0,[cls.tags[0].id]]]}]
        )

    def_check_tags_post_counts(self,tags,expected_counts):
        self.assertEqual(tags.mapped('posts_count'),expected_counts)

    deftest_tag_posts_count(self):
        self._check_tags_post_counts(self.tags,[1,0])
        post_tag_1=self.env['forum.post'].create(
            [{'name':'Postingabouttag1again','forum_id':self.forum.id,'tag_ids':[[6,0,[self.tags[0].id]]]}]
        )
        self._check_tags_post_counts(self.tags,[2,0])
        post_tags=self.env['forum.post'].create(
            [{'name':'Postingabouttag2now','forum_id':self.forum.id,'tag_ids':[[6,0,self.tags.ids]]}]
        )
        self._check_tags_post_counts(self.tags,[3,1])
        post_tag_1.active=False
        self._check_tags_post_counts(self.tags,[2,1])
        post_tags.close(None)
        self._check_tags_post_counts(self.tags,[1,0])
