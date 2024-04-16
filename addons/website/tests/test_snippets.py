#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra
importflectra.tests
fromflectra.tests.commonimportHOST
fromflectra.toolsimportconfig


@flectra.tests.common.tagged('post_install','-at_install','website_snippets')
classTestSnippets(flectra.tests.HttpCase):

    deftest_01_empty_parents_autoremove(self):
        self.start_tour("/?enable_editor=1","snippet_empty_parent_autoremove",login='admin')

    deftest_02_countdown_preview(self):
        self.start_tour("/?enable_editor=1","snippet_countdown",login='admin')

    deftest_03_snippet_image_gallery(self):
        IrAttachment=self.env['ir.attachment']
        base="http://%s:%s"%(HOST,config['http_port'])
        IrAttachment.create({
            'public':True,
            'name':'s_default_image.jpg',
            'type':'url',
            'url':base+'/web/image/website.s_banner_default_image.jpg',
        })
        IrAttachment.create({
            'public':True,
            'name':'s_default_image2.jpg',
            'type':'url',
            'url':base+'/web/image/website.s_banner_default_image.jpg',
        })
        self.start_tour("/","snippet_image_gallery",login='admin')

    deftest_04_parallax(self):
        self.start_tour('/','test_parallax',login='admin')
