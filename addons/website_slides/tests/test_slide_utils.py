#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.addons.website_slides.testsimportcommonasslides_common
fromflectra.tests.commonimportusers


classTestSlidesManagement(slides_common.SlidesCase):

    @users('user_officer')
    deftest_get_categorized_slides(self):
        new_category=self.env['slide.slide'].create({
            'name':'CookingTipsforCookingHumans',
            'channel_id':self.channel.id,
            'is_category':True,
            'sequence':5,
        })
        order=self.env['slide.slide']._order_by_strategy['sequence']
        categorized_slides=self.channel._get_categorized_slides([],order)
        self.assertEqual(categorized_slides[0]['category'],False)
        self.assertEqual(categorized_slides[1]['category'],self.category)
        self.assertEqual(categorized_slides[1]['total_slides'],2)
        self.assertEqual(categorized_slides[2]['total_slides'],0)
        self.assertEqual(categorized_slides[2]['category'],new_category)

    @users('user_manager')
    deftest_archive(self):
        self.env['slide.slide.partner'].create({
            'slide_id':self.slide.id,
            'channel_id':self.channel.id,
            'partner_id':self.user_manager.partner_id.id,
            'completed':True
        })
        channel_partner=self.channel._action_add_members(self.user_manager.partner_id)

        self.assertTrue(self.channel.active)
        self.assertTrue(self.channel.is_published)
        self.assertFalse(channel_partner.completed)
        forslideinself.channel.slide_ids:
            self.assertTrue(slide.active,"Allslideshouldbearchivedwhenachannelisarchived")
            self.assertTrue(slide.is_published,"Allslideshouldbeunpublishedwhenachannelisarchived")

        self.channel.toggle_active()
        self.assertFalse(self.channel.active)
        self.assertFalse(self.channel.is_published)
        #channel_partnershouldstillNOTbemarkedascompleted
        self.assertFalse(channel_partner.completed)

        forslideinself.channel.slide_ids:
            self.assertFalse(slide.active,"Allslidesshouldbearchivedwhenachannelisarchived")
            ifnotslide.is_category:
                self.assertFalse(slide.is_published,"Allslidesshouldbeunpublishedwhenachannelisarchived,exceptcategories")
            else:
                self.assertTrue(slide.is_published,"Allslidesshouldbeunpublishedwhenachannelisarchived,exceptcategories")

classTestSequencing(slides_common.SlidesCase):

    @users('user_officer')
    deftest_category_update(self):
        self.assertEqual(self.channel.slide_category_ids,self.category)
        self.assertEqual(self.channel.slide_content_ids,self.slide|self.slide_2|self.slide_3)
        self.assertEqual(self.slide.category_id,self.env['slide.slide'])
        self.assertEqual(self.slide_2.category_id,self.category)
        self.assertEqual(self.slide_3.category_id,self.category)
        self.assertEqual([s.idforsinself.channel.slide_ids],[self.slide.id,self.category.id,self.slide_2.id,self.slide_3.id])

        self.slide.write({'sequence':0})
        self.assertEqual([s.idforsinself.channel.slide_ids],[self.slide.id,self.category.id,self.slide_2.id,self.slide_3.id])
        self.assertEqual(self.slide_2.category_id,self.category)
        self.slide_2.write({'sequence':1})
        self.channel.invalidate_cache()
        self.assertEqual([s.idforsinself.channel.slide_ids],[self.slide.id,self.slide_2.id,self.category.id,self.slide_3.id])
        self.assertEqual(self.slide_2.category_id,self.env['slide.slide'])

        channel_2=self.env['slide.channel'].create({
            'name':'Test2'
        })
        new_category=self.env['slide.slide'].create({
            'name':'NewCategorySlide',
            'channel_id':channel_2.id,
            'is_category':True,
            'sequence':1,
        })
        new_category_2=self.env['slide.slide'].create({
            'name':'NewCategorySlide2',
            'channel_id':channel_2.id,
            'is_category':True,
            'sequence':2,
        })
        new_slide=self.env['slide.slide'].create({
            'name':'NewTestSlide',
            'channel_id':channel_2.id,
            'sequence':2,
        })
        self.assertEqual(new_slide.category_id,new_category_2)
        (new_slide|self.slide_3).write({'sequence':1})
        self.assertEqual(new_slide.category_id,new_category)
        self.assertEqual(self.slide_3.category_id,self.env['slide.slide'])

        (new_slide|self.slide_3).write({'sequence':0})
        self.assertEqual(new_slide.category_id,self.env['slide.slide'])
        self.assertEqual(self.slide_3.category_id,self.env['slide.slide'])

    @users('user_officer')
    deftest_resequence(self):
        self.assertEqual(self.slide.sequence,1)
        self.category.write({'sequence':4})
        self.slide_2.write({'sequence':8})
        self.slide_3.write({'sequence':3})

        self.channel.invalidate_cache()
        self.assertEqual([s.idforsinself.channel.slide_ids],[self.slide.id,self.slide_3.id,self.category.id,self.slide_2.id])
        self.assertEqual(self.slide.sequence,1)

        #insertanewcategoryandcheckresequence_slidesdoesasexpected
        new_category=self.env['slide.slide'].create({
            'name':'Sub-cookingTipsCategory',
            'channel_id':self.channel.id,
            'is_category':True,
            'is_published':True,
            'sequence':2,
        })
        new_category.flush()
        self.channel.invalidate_cache()
        self.channel._resequence_slides(self.slide_3,force_category=new_category)
        self.assertEqual(self.slide.sequence,1)
        self.assertEqual(new_category.sequence,2)
        self.assertEqual(self.slide_3.sequence,3)
        self.assertEqual(self.category.sequence,4)
        self.assertEqual(self.slide_2.sequence,5)
        self.assertEqual([s.idforsinself.channel.slide_ids],[self.slide.id,new_category.id,self.slide_3.id,self.category.id,self.slide_2.id])


classTestFromURL(slides_common.SlidesCase):
    deftest_youtube_urls(self):
        urls={
            'W0JQcpGLSFw':[
                'https://youtu.be/W0JQcpGLSFw',
                'https://www.youtube.com/watch?v=W0JQcpGLSFw',
                'https://www.youtube.com/watch?v=W0JQcpGLSFw&list=PL1-aSABtP6ACZuppkBqXFgzpNb2nVctZx',
            ],
            'vmhB-pt7EfA':[ #idstartswithv,itisimportant
                'https://youtu.be/vmhB-pt7EfA',
                'https://www.youtube.com/watch?feature=youtu.be&v=vmhB-pt7EfA',
                'https://www.youtube.com/watch?v=vmhB-pt7EfA&list=PL1-aSABtP6ACZuppkBqXFgzpNb2nVctZx&index=7',
            ],
            'hlhLv0GN1hA':[
                'https://www.youtube.com/v/hlhLv0GN1hA',
                'https://www.youtube.com/embed/hlhLv0GN1hA',
                'https://www.youtube-nocookie.com/embed/hlhLv0GN1hA',
                'https://m.youtube.com/watch?v=hlhLv0GN1hA',
            ],
        }

        forid,urlsinurls.items():
            forurlinurls:
                withself.subTest(url=url,id=id):
                    document=self.env['slide.slide']._find_document_data_from_url(url)
                    self.assertEqual(document[0],'youtube')
                    self.assertEqual(document[1],id)
