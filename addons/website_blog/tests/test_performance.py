#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website.tests.test_performanceimportUtilPerf
importrandom


classTestBlogPerformance(UtilPerf):
    defsetUp(self):
        super().setUp()
        #ifwebsite_livechatisinstalled,disableit
        if'channel_id'inself.env['website']:
            self.env['website'].search([]).channel_id=False

    deftest_10_perf_sql_blog_standard_data(self):
        self.assertEqual(self._get_url_hot_query('/blog'),28)

    deftest_20_perf_sql_blog_bigger_data_scaling(self):
        BlogPost=self.env['blog.post']
        BlogTag=self.env['blog.tag']
        blogs=self.env['blog.blog'].search([])
        blog_tags=BlogTag.create([{'name':'BlogTagTest%s'%i}foriinrange(1,20)])
        BlogPost.create([{'name':'BlogPostTest%s'%i,'is_published':True,'blog_id':blogs[i%2].id}foriinrange(1,20)])
        blog_posts=BlogPost.search([])
        forblog_postinblog_posts:
            blog_post.tag_ids+=blog_tags
            blog_tags=blog_tags[:-1]
        self.assertEqual(self._get_url_hot_query('/blog'),28)
        self.assertEqual(self._get_url_hot_query(blog_post[0].website_url),31)

    deftest_30_perf_sql_blog_bigger_data_scaling(self):
        BlogPost=self.env['blog.post']
        BlogTag=self.env['blog.tag']
        blogs=self.env['blog.blog'].search([])
        blog_tags=BlogTag.create([{'name':'NewBlogTagTest%s'%i}foriinrange(1,50)])
        BlogPost.create([{'name':'NewBlogPostTest%s'%i,'is_published':True,'blog_id':blogs[random.randint(0,1)].id}foriinrange(1,100)])
        blog_posts=BlogPost.search([])
        forblog_postinblog_posts:
            blog_post.write({'tag_ids':[[6,0,random.choices(blog_tags.ids,k=random.randint(0,len(blog_tags)))]]})

        self.assertLessEqual(self._get_url_hot_query('/blog'),28)
        self.assertLessEqual(self._get_url_hot_query(blog_post[0].website_url),31)
