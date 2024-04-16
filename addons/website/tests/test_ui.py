#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra
importflectra.tests


@flectra.tests.tagged('-at_install','post_install')
classTestUiCustomizeTheme(flectra.tests.HttpCase):
    deftest_01_attachment_website_unlink(self):
        '''Someir.attachmentneedstobeunlinkedwhenawebsiteisunlink,
            otherwisesomeflowswilljustcrash.That'sthecasewhen2website
            havetheirthemecolorcustomized.Removingawebsitewillmakeits
            customizedattachmentgeneric,thushaving2attachmentswiththe
            sameURLavailableforotherwebsites,leadingtosingletonerrors
            (amongother).

            Butnoallattachmentshouldbedeleted,egwedon'twanttodelete
            aSOorinvoicePDFcomingfromanecommerceorder.
        '''
        Website=self.env['website']
        Page=self.env['website.page']
        Attachment=self.env['ir.attachment']

        website_default=Website.browse(1)
        website_test=Website.create({'name':'WebsiteTest'})

        #simulateattachmentstatewhenediting2themethroughcustomize
        custom_url='/TEST/website/static/src/scss/options/colors/user_theme_color_palette.custom.web.assets_common.scss'
        scss_attachment=Attachment.create({
            'name':custom_url,
            'type':'binary',
            'mimetype':'text/scss',
            'datas':'',
            'url':custom_url,
            'website_id':website_default.id
        })
        scss_attachment.copy({'website_id':website_test.id})

        #simulatePDFfromecommerceorder
        #Note:itwillonlyhaveitswebsite_idflagifthewebsitehasadomain
        #equaltothecurrentURL(fallbackorget_current_website())
        so_attachment=Attachment.create({
            'name':'SO036.pdf',
            'type':'binary',
            'mimetype':'application/pdf',
            'datas':'',
            'website_id':website_test.id
        })

        #avoidsqlerroronpagewebsite_idrestrict
        Page.search([('website_id','=',website_test.id)]).unlink()
        website_test.unlink()
        self.assertEqual(Attachment.search_count([('url','=',custom_url)]),1,'Shouldnotleftduplicateswhendeletingawebsite')
        self.assertTrue(so_attachment.exists(),'Mostattachmentshouldnotbedeleted')
        self.assertFalse(so_attachment.website_id,'Websiteshouldberemoved')


@flectra.tests.tagged('-at_install','post_install')
classTestUiHtmlEditor(flectra.tests.HttpCase):
    deftest_html_editor_multiple_templates(self):
        Website=self.env['website']
        View=self.env['ir.ui.view']
        Page=self.env['website.page']

        self.generic_view=View.create({
            'name':'Generic',
            'type':'qweb',
            'arch':'''
                <div>content</div>
            ''',
            'key':'test.generic_view',
        })

        self.generic_page=Page.create({
            'view_id':self.generic_view.id,
            'url':'/generic',
        })

        generic_page=Website.viewref('test.generic_view')
        #Useanemptypagelayoutwithoe_structureidforthistest
        oe_structure_layout='''
            <tname="Generic"t-name="test.generic_view">
                <tt-call="website.layout">
                    <divid="oe_structure_test_ui"class="oe_structureoe_empty"/>
                </t>
            </t>
        '''
        generic_page.arch=oe_structure_layout
        self.start_tour("/",'html_editor_multiple_templates',login='admin')
        self.assertEqual(View.search_count([('key','=','test.generic_view')]),2,"homepageviewshouldhavebeenCOW'd")
        self.assertTrue(generic_page.arch==oe_structure_layout,"Generichomepageviewshouldbeuntouched")
        self.assertEqual(len(generic_page.inherit_children_ids.filtered(lambdav:'oe_structure'inv.name)),0,"oe_structureviewshouldhavebeendeletedwhenaboutuswasCOW")
        specific_page=Website.with_context(website_id=1).viewref('test.generic_view')
        self.assertTrue(specific_page.arch!=oe_structure_layout,"Specifichomepageviewshouldhavebeenchanged")
        self.assertEqual(len(specific_page.inherit_children_ids.filtered(lambdav:'oe_structure'inv.name)),1,"oe_structureviewshouldhavebeencreatedonthespecifictree")

    deftest_html_editor_scss(self):
        self.env.ref('base.user_demo').write({
            'groups_id':[(6,0,[
                self.env.ref('base.group_user').id,
                self.env.ref('website.group_website_designer').id
            ])]
        })
        self.start_tour("/",'test_html_editor_scss',login='admin')


@flectra.tests.tagged('-at_install','post_install')
classTestUiTranslate(flectra.tests.HttpCase):
    deftest_admin_tour_rte_translator(self):
        self.env['res.lang'].create({
            'name':'Parseltongue',
            'code':'pa_GB',
            'iso_code':'pa_GB',
            'url_code':'pa_GB',
        })
        self.start_tour("/",'rte_translator',login='admin',timeout=120)


@flectra.tests.common.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):

    deftest_01_admin_tour_homepage(self):
        self.start_tour("/?enable_editor=1",'homepage',login='admin')

    deftest_02_restricted_editor(self):
        self.restricted_editor=self.env['res.users'].create({
            'name':'RestrictedEditor',
            'login':'restricted',
            'password':'restricted',
            'groups_id':[(6,0,[
                    self.ref('base.group_user'),
                    self.ref('website.group_website_publisher')
                ])]
        })
        self.start_tour("/",'restricted_editor',login='restricted')

    deftest_03_backend_dashboard(self):
        self.start_tour("/",'backend_dashboard',login='admin')

    deftest_04_website_navbar_menu(self):
        website=self.env['website'].search([],limit=1)
        self.env['website.menu'].create({
            'name':'TestTourMenu',
            'url':'/test-tour-menu',
            'parent_id':website.menu_id.id,
            'sequence':0,
            'website_id':website.id,
        })
        self.start_tour("/",'website_navbar_menu')

    deftest_05_specific_website_editor(self):
        website_default=self.env['website'].search([],limit=1)
        new_website=self.env['website'].create({'name':'NewWebsite'})
        website_editor_assets_view=self.env.ref('website.assets_wysiwyg')
        self.env['ir.ui.view'].create({
            'name':'EditorExtension',
            'type':'qweb',
            'inherit_id':website_editor_assets_view.id,
            'website_id':new_website.id,
            'arch':"""
                <xpathexpr="."position="inside">
                    <scripttype="text/javascript">document.body.dataset.hello='world';</script>
                </xpath>
            """,
        })
        self.start_tour("/website/force/%s"%website_default.id,"generic_website_editor",login='admin')
        self.start_tour("/website/force/%s"%new_website.id,"specific_website_editor",login='admin')

    deftest_06_public_user_editor(self):
        website_default=self.env['website'].search([],limit=1)
        website_default.homepage_id.arch="""
            <tname="Homepage"t-name="website.homepage">
                <tt-call="website.layout">
                    <textareaclass="o_public_user_editor_test_textareao_wysiwyg_loader"/>
                </t>
            </t>
        """
        self.start_tour("/","public_user_editor",login=None)

    deftest_07_snippet_version(self):
        website_snippets=self.env.ref('website.snippets')
        self.env['ir.ui.view'].create([{
            'name':'Testsnip',
            'type':'qweb',
            'key':'website.s_test_snip',
            'arch':"""
                <sectionclass="s_test_snip">
                    <tt-snippet-call="website.s_share"/>
                </section>
            """,
        },{
            'type':'qweb',
            'inherit_id':website_snippets.id,
            'arch':"""
                <xpathexpr="//t[@t-snippet='website.s_parallax']"position="after">
                    <tt-snippet="website.s_test_snip"t-thumbnail="/website/static/src/img/snippets_thumbs/s_website_form.svg"/>
                </xpath>
            """,
        }])
        self.start_tour("/",'snippet_version',login='admin')

    deftest_08_website_style_custo(self):
        self.start_tour("/","website_style_edition",login="admin")

    deftest_09_carousel_snippet_content_removal(self):
        self.start_tour("/","carousel_content_removal",login='admin')

    deftest_10_editor_focus_blur_unit_test(self):
        #TODOthisshoulddefinitelynotbeawebsitepythontourtestbut
        #whilewaitingforaproperweb_editorqunitJStestsuiteforthe
        #editor,itisbetterthannotestatallasthiswasbrokenmultiple
        #timesalready.
        self.env["ir.ui.view"].create([{
            'name':'s_focusblur',
            'key':'website.s_focusblur',
            'type':'qweb',
            'arch':"""
                <sectionclass="s_focusblurbg-successpy-5">
                    <divclass="container">
                        <divclass="row">
                            <divclass="col-lg-6s_focusblur_child1bg-warningpy-5"></div>
                            <divclass="col-lg-6s_focusblur_child2bg-dangerpy-5"></div>
                        </div>
                    </div>
                </section>
            """,
        },{
            'name':'s_focusblur_snippets',
            'mode':'extension',
            'inherit_id':self.env.ref('website.snippets').id,
            'key':'website.s_focusblur_snippets',
            'type':'qweb',
            'arch':"""
                <data>
                    <xpathexpr="//*[@id='snippet_structure']//t[@t-snippet]"position="before">
                        <tt-snippet="website.s_focusblur"/>
                    </xpath>
                </data>
            """,
        },{
            'name':'s_focusblur_options',
            'mode':'extension',
            'inherit_id':self.env.ref('web_editor.snippet_options').id,
            'key':'website.s_focusblur_options',
            'type':'qweb',
            'arch':"""
                <data>
                    <xpathexpr=".">
                        <divdata-js="FocusBlurParent"data-selector=".s_focusblur"/>
                        <divdata-js="FocusBlurChild1"data-selector=".s_focusblur_child1"/>
                        <divdata-js="FocusBlurChild2"data-selector=".s_focusblur_child2"/>
                    </xpath>
                </data>
            """,
        }])

        self.start_tour("/?enable_editor=1","focus_blur_snippets",login="admin")
