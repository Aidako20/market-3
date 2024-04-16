#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
#-*-coding:utf-8-*-

fromflectra.testsimporttagged
fromflectra.tests.commonimportTransactionCase
fromflectraimporttools
fromioimportBytesIO
fromPILimportImage
importbase64

@tagged('post_install','-at_install')
classTestWebsite(TransactionCase):

    deftest_event_app_name(self):
        website0=self.env['website'].create({'name':'Foo'})
        self.assertEqual(website0.events_app_name,'FooEvents')

        website1=self.env['website'].create({'name':'Foo','events_app_name':'BarEvents'})
        self.assertEqual(website1.events_app_name,'BarEvents')

        website2=self.env['website'].create({'name':'Foo'})
        self.assertEqual(website2.events_app_name,'FooEvents')
        website2.write({'name':'Bar'})
        self.assertEqual(website2.events_app_name,'FooEvents')

    deftest_compute_app_icon(self):

        #GenerateimagedataforJPEG
        jpeg_image=Image.new('RGB',(60,30),color=(73,109,137))
        jpeg_io=BytesIO()
        jpeg_image.save(jpeg_io,format='JPEG')
        jpeg_image_data=jpeg_io.getvalue()

        #GenerateimagedataforJPG
        jpg_image=Image.new('RGB',(60,30),color=(73,109,137))
        jpg_io=BytesIO()
        jpg_image.save(jpg_io,format='JPEG')
        jpg_image_data=jpg_io.getvalue()

        #GenerateimagedataforPNG
        png_image=Image.new('RGB',(60,30),color=(73,109,137))
        png_io=BytesIO()
        png_image.save(png_io,format='PNG')
        png_image_data=png_io.getvalue()

        #GenerateimagedataforSVG
        svg_image_data=b"""<svgxmlns="http://www.w3.org/2000/svg"width="60"height="30"version="1.1">
                            <rectwidth="100%"height="100%"fill="rgb(73,109,137)"/>
                            </svg>
                        """
        #Imagedataandtheirrespectiveexpectedtypes
        image_data={
            'png':png_image_data,
            'jpg':jpg_image_data,
            'jpeg':jpeg_image_data,
            'svg':svg_image_data
        }

        forexpected_type,image_datainimage_data.items():
            #Createawebsiterecord
            website=self.env['website'].create({
                'name':'TestWebsite',
                'favicon':base64.b64encode(image_data)
            })

            #Callthemethodtocomputeapp_icon
            website._compute_app_icon()

            ifexpected_typein['jpeg','png','jpg']:
                #Checkifapp_iconisset
                self.assertTrue(website.app_icon)

                #Checkifapp_iconisavalidimage
                image=tools.base64_to_image(website.app_icon)
                self.assertEqual(image.format.lower(),'png')
            else:
                #ForSVGimages,ensurethattheapp_iconisnotset
                self.assertFalse(website.app_icon)
