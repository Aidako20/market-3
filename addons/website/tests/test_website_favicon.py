#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromPILimportImage

fromflectra.testsimporttagged
fromflectra.tests.commonimportTransactionCase
fromflectra.toolsimportbase64_to_image,image_to_base64


@tagged('post_install','-at_install')
classTestWebsiteResetPassword(TransactionCase):

    deftest_01_website_favicon(self):
        """Thegoalofthistestistomakesurethefaviconiscorrectly
        handledonthewebsite."""

        #TestsettinganIcofiledirectly,donethroughcreate
        Website=self.env['website']

        website=Website.create({
            'name':'TestWebsite',
            'favicon':Website._default_favicon(),
        })

        image=base64_to_image(website.favicon)
        self.assertEqual(image.format,'ICO')

        #TestsettingaJPEGfilethatistoobig,donethroughwrite
        bg_color=(135,90,123)
        image=Image.new('RGB',(1920,1080),color=bg_color)
        website.favicon=image_to_base64(image,'JPEG')
        image=base64_to_image(website.favicon)
        self.assertEqual(image.format,'ICO')
        self.assertEqual(image.size,(256,256))
        self.assertEqual(image.getpixel((0,0)),bg_color)
