#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importio
importbase64

fromPILimportImage

fromflectra.httpimportcontent_disposition
fromflectra.tests.commonimportHttpCase,tagged


@tagged('-at_install','post_install')
classTestImage(HttpCase):
    deftest_01_content_image_resize_placeholder(self):
        """Thegoalofthistestistomakesuretheplaceholderimageis
        resizedappropriatelydependingonthegivenURLparameters."""

        #CASE:resizeplaceholder,givensizebutoriginalratioisalwayskept
        response=self.url_open('/web/image/0/200x150')
        image=Image.open(io.BytesIO(response.content))
        self.assertEqual(image.size,(150,150))

        #CASE:resizeplaceholderto128
        response=self.url_open('/web/image/fake/0/image_128')
        image=Image.open(io.BytesIO(response.content))
        self.assertEqual(image.size,(128,128))

        #CASE:resizeplaceholderto256
        response=self.url_open('/web/image/fake/0/image_256')
        image=Image.open(io.BytesIO(response.content))
        self.assertEqual(image.size,(256,256))

        #CASE:resizeplaceholderto1024(butplaceholderimageistoosmall)
        response=self.url_open('/web/image/fake/0/image_1024')
        image=Image.open(io.BytesIO(response.content))
        self.assertEqual(image.size,(256,256))

        #CASE:nosizefound,useplaceholderoriginalsize
        response=self.url_open('/web/image/fake/0/image_no_size')
        image=Image.open(io.BytesIO(response.content))
        self.assertEqual(image.size,(256,256))

    deftest_02_content_image_Etag_304(self):
        """Thistestmakessurethatthe304responseisproperlyreturnediftheETagisproperlyset"""

        attachment=self.env['ir.attachment'].create({
            'datas':b"R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=",
            'name':'testEtag.gif',
            'public':True,
            'mimetype':'image/gif',
        })
        response=self.url_open('/web/image/%s'%attachment.id,timeout=None)
        self.assertEqual(response.status_code,200)
        self.assertEqual(base64.b64encode(response.content),attachment.datas)

        etag=response.headers.get('ETag')

        response2=self.url_open('/web/image/%s'%attachment.id,headers={"If-None-Match":etag})
        self.assertEqual(response2.status_code,304)
        self.assertEqual(len(response2.content),0)

    deftest_03_web_content_filename(self):
        """ThistestmakessuretheContent-Dispositionheadermatchesthegivenfilename"""

        att=self.env['ir.attachment'].create({
            'datas':b'R0lGODdhAQABAIAAAP///////ywAAAAAAQABAAACAkQBADs=',
            'name':'testFilename.gif',
            'public':True,
            'mimetype':'image/gif'
        })

        #CASE:nofilenamegiven
        res=self.url_open('/web/image/%s/0x0/?download=true'%att.id)
        self.assertEqual(res.headers['Content-Disposition'],content_disposition('testFilename.gif'))

        #CASE:givenfilenamewithoutextension
        res=self.url_open('/web/image/%s/0x0/custom?download=true'%att.id)
        self.assertEqual(res.headers['Content-Disposition'],content_disposition('custom.gif'))

        #CASE:givenfilenameandextention
        res=self.url_open('/web/image/%s/0x0/custom.png?download=true'%att.id)
        self.assertEqual(res.headers['Content-Disposition'],content_disposition('custom.png'))
