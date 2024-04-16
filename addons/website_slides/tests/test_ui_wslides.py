#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64

fromdateutil.relativedeltaimportrelativedelta

fromflectraimporttests
fromflectra.addons.base.tests.commonimportHttpCaseWithUserPortal
fromflectra.addons.gamification.tests.commonimportHttpCaseGamification
fromflectra.fieldsimportDatetime
fromflectra.modules.moduleimportget_module_resource


classTestUICommon(HttpCaseGamification,HttpCaseWithUserPortal):
    
    defsetUp(self):
        super(TestUICommon,self).setUp()
        #Loadpdfandimgcontents
        pdf_path=get_module_resource('website_slides','static','src','img','presentation.pdf')
        pdf_content=base64.b64encode(open(pdf_path,"rb").read())
        img_path=get_module_resource('website_slides','static','src','img','slide_demo_gardening_1.jpg')
        img_content=base64.b64encode(open(img_path,"rb").read())

        self.channel=self.env['slide.channel'].create({
            'name':'BasicsofGardening-Test',
            'user_id':self.env.ref('base.user_admin').id,
            'enroll':'public',
            'channel_type':'training',
            'allow_comment':True,
            'promote_strategy':'most_voted',
            'is_published':True,
            'description':'Learnthebasicsofgardening!',
            'create_date':Datetime.now()-relativedelta(days=8),
            'slide_ids':[
                (0,0,{
                    'name':'Gardening:TheKnow-How',
                    'sequence':1,
                    'datas':pdf_content,
                    'slide_type':'presentation',
                    'is_published':True,
                    'is_preview':True,
                }),(0,0,{
                    'name':'HomeGardening',
                    'sequence':2,
                    'image_1920':img_content,
                    'slide_type':'infographic',
                    'is_published':True,
                }),(0,0,{
                    'name':'MightyCarrots',
                    'sequence':3,
                    'image_1920':img_content,
                    'slide_type':'infographic',
                    'is_published':True,
                }),(0,0,{
                    'name':'HowtoGrowandHarvestTheBestStrawberries|Basics',
                    'sequence':4,
                    'datas':pdf_content,
                    'slide_type':'document',
                    'is_published':True,
                }),(0,0,{
                    'name':'Testyourknowledge',
                    'sequence':5,
                    'slide_type':'quiz',
                    'is_published':True,
                    'question_ids':[
                        (0,0,{
                            'question':'Whatisastrawberry?',
                            'answer_ids':[
                                (0,0,{
                                    'text_value':'Afruit',
                                    'is_correct':True,
                                    'sequence':1,
                                }),(0,0,{
                                    'text_value':'Avegetable',
                                    'sequence':2,
                                }),(0,0,{
                                    'text_value':'Atable',
                                    'sequence':3,
                                })
                            ]
                        }),(0,0,{
                            'question':'Whatisthebesttooltodigaholeforyourplants?',
                            'answer_ids':[
                                (0,0,{
                                    'text_value':'Ashovel',
                                    'is_correct':True,
                                    'sequence':1,
                                }),(0,0,{
                                    'text_value':'Aspoon',
                                    'sequence':2,
                                })
                            ]
                        })
                    ]
                })
            ]
        })


@tests.common.tagged('post_install','-at_install')
classTestUi(TestUICommon):

    deftest_course_member_employee(self):
        user_demo=self.user_demo
        user_demo.flush()
        user_demo.write({
            'groups_id':[(5,0),(4,self.env.ref('base.group_user').id)]
        })

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("course_member")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.course_member.ready',
            login=user_demo.login)

    deftest_course_member_elearning_officer(self):
        user_demo=self.user_demo
        user_demo.flush()
        user_demo.write({
            'groups_id':[(5,0),(4,self.env.ref('base.group_user').id),(4,self.env.ref('website_slides.group_website_slides_officer').id)]
        })

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("course_member")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.course_member.ready',
            login=user_demo.login)

    deftest_course_member_portal(self):
        user_portal=self.user_portal
        user_portal.flush()

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("course_member")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.course_member.ready',
            login=user_portal.login)

    deftest_full_screen_edition_website_publisher(self):
        #group_website_designer
        user_demo=self.env.ref('base.user_demo')
        user_demo.flush()
        user_demo.write({
            'groups_id':[(5,0),(4,self.env.ref('base.group_user').id),(4,self.env.ref('website.group_website_publisher').id)]
        })

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("full_screen_web_editor")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.full_screen_web_editor.ready',
            login=user_demo.login)

    deftest_course_reviews_elearning_officer(self):
        user_demo=self.user_demo
        user_demo.write({
            'groups_id':[(6,0,(self.env.ref('base.group_user')|self.env.ref(
                'website_slides.group_website_slides_officer')).ids)]
        })

        #Theusermustbeacoursememberbeforebeingabletopostalognote.
        self.channel._action_add_members(user_demo.partner_id)
        self.channel.with_user(user_demo).message_post(
            body='Lognote',subtype_xmlid='mail.mt_note',message_type='comment')

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("course_reviews")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.course_reviews.ready',
            login=user_demo.login)


@tests.common.tagged('external','post_install','-standard','-at_install')
classTestUiYoutube(HttpCaseGamification):

    deftest_course_member_yt_employee(self):
        #removemembershipbecauseweneedtobeabletojointhecourseduringthetour
        user_demo=self.user_demo
        user_demo.flush()
        user_demo.write({
            'groups_id':[(5,0),(4,self.env.ref('base.group_user').id)]
        })
        self.env.ref('website_slides.slide_channel_demo_3_furn0')._remove_membership(self.env.ref('base.partner_demo').ids)

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("course_member_youtube")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.course_member_youtube.ready',
            login=user_demo.login)

    deftest_course_publisher_elearning_manager(self):
        user_demo=self.user_demo
        user_demo.flush()
        user_demo.write({
            'groups_id':[(5,0),(4,self.env.ref('base.group_user').id),(4,self.env.ref('website_slides.group_website_slides_manager').id)]
        })

        self.browser_js(
            '/slides',
            'flectra.__DEBUG__.services["web_tour.tour"].run("course_publisher")',
            'flectra.__DEBUG__.services["web_tour.tour"].tours.course_publisher.ready',
            login=user_demo.login)
