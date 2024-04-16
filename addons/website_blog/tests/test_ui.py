#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importflectra.tests


@flectra.tests.tagged('post_install','-at_install')
classTestUi(flectra.tests.HttpCase):
    deftest_admin(self):
        #Ensureatleasttwoblogsexistforthestepaskingtoselectablog
        self.env['blog.blog'].create({'name':'Travel'})

        #Ensureatleastoneimageexistsforthestepthatchoosesone
        self.env['ir.attachment'].create({
            'public':True,
            'type':'url',
            'url':'/web/image/123/transparent.png',
            'name':'transparent.png',
            'mimetype':'image/png',
        })

        self.start_tour("/",'blog',login='admin')
