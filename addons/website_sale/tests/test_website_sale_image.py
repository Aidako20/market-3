#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importio

fromflectra.addons.website_sale.tests.commonimportTestWebsiteSaleCommon
fromPILimportImage

importflectra.tests


@flectra.tests.common.tagged('post_install','-at_install')
classTestWebsiteSaleImage(flectra.tests.HttpCase,TestWebsiteSaleCommon):

    #registry_test_mode=False #uncommenttosavetheproducttotestinbrowser

    deftest_01_admin_shop_zoom_tour(self):
        color_red='#CD5C5C'
        name_red='IndianRed'

        color_green='#228B22'
        name_green='ForestGreen'

        color_blue='#4169E1'
        name_blue='RoyalBlue'

        #createthecolorattribute
        product_attribute=self.env['product.attribute'].create({
            'name':'BeautifulColor',
            'display_type':'color',
        })

        #createthecolorattributevalues
        attr_values=self.env['product.attribute.value'].create([{
            'name':name_red,
            'attribute_id':product_attribute.id,
            'html_color':color_red,
            'sequence':1,
        },{
            'name':name_green,
            'attribute_id':product_attribute.id,
            'html_color':color_green,
            'sequence':2,
        },{
            'name':name_blue,
            'attribute_id':product_attribute.id,
            'html_color':color_blue,
            'sequence':3,
        }])

        #firstimage(blue)forthetemplate
        f=io.BytesIO()
        Image.new('RGB',(1920,1080),color_blue).save(f,'JPEG')
        f.seek(0)
        blue_image=base64.b64encode(f.read())

        #secondimage(red)forthevariant1,smallimage(nozoom)
        f=io.BytesIO()
        Image.new('RGB',(800,500),color_red).save(f,'JPEG')
        f.seek(0)
        red_image=base64.b64encode(f.read())

        #secondimage(green)forthevariant2,bigimage(zoom)
        f=io.BytesIO()
        Image.new('RGB',(1920,1080),color_green).save(f,'JPEG')
        f.seek(0)
        green_image=base64.b64encode(f.read())

        #TemplateExtraImage1
        f=io.BytesIO()
        Image.new('RGB',(124,147)).save(f,'GIF')
        f.seek(0)
        image_gif=base64.b64encode(f.read())

        #TemplateExtraImage2
        image_svg=base64.b64encode(b'<svg></svg>')

        #RedVariantExtraImage1
        f=io.BytesIO()
        Image.new('RGB',(767,247)).save(f,'BMP')
        f.seek(0)
        image_bmp=base64.b64encode(f.read())

        #GreenVariantExtraImage1
        f=io.BytesIO()
        Image.new('RGB',(2147,3251)).save(f,'PNG')
        f.seek(0)
        image_png=base64.b64encode(f.read())

        #createthetemplate,withoutcreatingthevariants
        template=self.env['product.template'].with_context(create_product_product=True).create({
            'name':'AColorfulImage',
            'product_template_image_ids':[(0,0,{'name':'image1','image_1920':image_gif}),(0,0,{'name':'image4','image_1920':image_svg})],
        })

        #setthecolorattributeandvaluesonthetemplate
        line=self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute.id,
            'product_tmpl_id':template.id,
            'value_ids':[(6,0,attr_values.ids)]
        }])
        value_red=line.product_template_value_ids[0]
        value_green=line.product_template_value_ids[1]

        #setadifferentpriceonthevariantstodifferentiatethem
        product_template_attribute_values=self.env['product.template.attribute.value'].search([('product_tmpl_id','=',template.id)])

        forvalinproduct_template_attribute_values:
            ifval.name==name_red:
                val.price_extra=10
            else:
                val.price_extra=20

        #GetREDvariant,andsetimagetoblue(willbesetonthetemplate
        #becausethetemplateimageisemptyandthereisonlyonevariant)
        product_red=template._get_variant_for_combination(value_red)
        product_red.write({
            'image_1920':blue_image,
            'product_variant_image_ids':[(0,0,{'name':'image2','image_1920':image_bmp})],
        })

        self.assertEqual(template.image_1920,blue_image)

        #Getthegreenvariant
        product_green=template._get_variant_for_combination(value_green)
        product_green.write({
            'image_1920':green_image,
            'product_variant_image_ids':[(0,0,{'name':'image3','image_1920':image_png})],
        })

        #nowsettheredimageonthefirstvariant,thatworksbecause
        #templateimageisnotemptyanymoreandwehaveasecondvariant
        product_red.image_1920=red_image

        #Verifyimage_1920size>1024canbezoomed
        self.assertTrue(template.can_image_1024_be_zoomed)
        self.assertFalse(template.product_template_image_ids[0].can_image_1024_be_zoomed)
        self.assertFalse(template.product_template_image_ids[1].can_image_1024_be_zoomed)
        self.assertFalse(product_red.can_image_1024_be_zoomed)
        self.assertFalse(product_red.product_variant_image_ids[0].can_image_1024_be_zoomed)
        self.assertTrue(product_green.can_image_1024_be_zoomed)
        self.assertTrue(product_green.product_variant_image_ids[0].can_image_1024_be_zoomed)

        #jpegencodingischangingthecolorabit
        jpeg_blue=(65,105,227)
        jpeg_red=(205,93,92)
        jpeg_green=(34,139,34)

        #Verifyoriginalsize:keeporiginal
        image=Image.open(io.BytesIO(base64.b64decode(template.image_1920)))
        self.assertEqual(image.size,(1920,1080))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_blue,"blue")
        image=Image.open(io.BytesIO(base64.b64decode(product_red.image_1920)))
        self.assertEqual(image.size,(800,500))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_red,"red")
        image=Image.open(io.BytesIO(base64.b64decode(product_green.image_1920)))
        self.assertEqual(image.size,(1920,1080))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_green,"green")

        #Verify1024size:keepaspectratio
        image=Image.open(io.BytesIO(base64.b64decode(template.image_1024)))
        self.assertEqual(image.size,(1024,576))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_blue,"blue")
        image=Image.open(io.BytesIO(base64.b64decode(product_red.image_1024)))
        self.assertEqual(image.size,(800,500))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_red,"red")
        image=Image.open(io.BytesIO(base64.b64decode(product_green.image_1024)))
        self.assertEqual(image.size,(1024,576))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_green,"green")

        #Verify512size:keepaspectratio
        image=Image.open(io.BytesIO(base64.b64decode(template.image_512)))
        self.assertEqual(image.size,(512,288))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_blue,"blue")
        image=Image.open(io.BytesIO(base64.b64decode(product_red.image_512)))
        self.assertEqual(image.size,(512,320))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_red,"red")
        image=Image.open(io.BytesIO(base64.b64decode(product_green.image_512)))
        self.assertEqual(image.size,(512,288))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_green,"green")

        #Verify256size:keepaspectratio
        image=Image.open(io.BytesIO(base64.b64decode(template.image_256)))
        self.assertEqual(image.size,(256,144))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_blue,"blue")
        image=Image.open(io.BytesIO(base64.b64decode(product_red.image_256)))
        self.assertEqual(image.size,(256,160))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_red,"red")
        image=Image.open(io.BytesIO(base64.b64decode(product_green.image_256)))
        self.assertEqual(image.size,(256,144))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_green,"green")

        #Verify128size:keepaspectratio
        image=Image.open(io.BytesIO(base64.b64decode(template.image_128)))
        self.assertEqual(image.size,(128,72))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_blue,"blue")
        image=Image.open(io.BytesIO(base64.b64decode(product_red.image_128)))
        self.assertEqual(image.size,(128,80))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_red,"red")
        image=Image.open(io.BytesIO(base64.b64decode(product_green.image_128)))
        self.assertEqual(image.size,(128,72))
        self.assertEqual(image.getpixel((image.size[0]/2,image.size[1]/2)),jpeg_green,"green")

        #self.env.cr.commit() #uncommenttosavetheproducttotestinbrowser

        self.start_tour("/",'shop_zoom',login="admin")

        #CASE:unlinkmoveimagetofallbackiffallbackimageempty
        template.image_1920=False
        product_red.unlink()
        self.assertEqual(template.image_1920,red_image)

        #CASE:unlinkdoesnothingspecialiffallbackimagealreadyset
        self.env['product.product'].create({
            'product_tmpl_id':template.id,
            'image_1920':green_image,
        }).unlink()
        self.assertEqual(template.image_1920,red_image)

        #CASE:displayvariantimagefirstifset
        self.assertEqual(product_green._get_images()[0].image_1920,green_image)

        #CASE:displayvariantfallbackaftervarianto2m,correctfallback
        #writeonthevariantfield,otherwiseitwillwriteonthefallback
        product_green.image_variant_1920=False
        images=product_green._get_images()
        #imagesonfieldsareresizedtomax1920
        image=Image.open(io.BytesIO(base64.b64decode(images[0].image_1920)))
        self.assertEqual(image.size,(1268,1920))
        self.assertEqual(images[1].image_1920,red_image)
        self.assertEqual(images[2].image_1920,image_gif)
        self.assertEqual(images[3].image_1920,image_svg)

        #CASE:Whenuploadingaproductvariantimage
        #wedon'twantthedefault_product_tmpl_idfromthecontexttobeappliedifwehaveaproduct_variant_idset
        #wewantthedefault_product_tmpl_idfromthecontexttobeappliedifwedon'thaveaproduct_variant_idset

        additionnal_context={'default_product_tmpl_id':template.id}

        product=self.env['product.product'].create({
            'product_tmpl_id':template.id,
        })

        product_image=self.env['product.image'].with_context(**additionnal_context).create([{
            'name':'Templateimage',
            'image_1920':red_image,
        },{
            'name':'Variantimage',
            'image_1920':blue_image,
            'product_variant_id':product.id,
        }])

        template_image=product_image.filtered(lambdai:i.name=='Templateimage')
        variant_image=product_image.filtered(lambdai:i.name=='Variantimage')

        self.assertEqual(template_image.product_tmpl_id.id,template.id)
        self.assertFalse(template_image.product_variant_id.id)
        self.assertFalse(variant_image.product_tmpl_id.id)
        self.assertEqual(variant_image.product_variant_id.id,product.id)

    deftest_02_image_holder(self):
        f=io.BytesIO()
        Image.new('RGB',(800,500),'#FF0000').save(f,'JPEG')
        f.seek(0)
        image=base64.b64encode(f.read())

        #createthecolorattribute
        product_attribute=self.env['product.attribute'].create({
            'name':'BeautifulColor',
            'display_type':'color',
        })

        #createthecolorattributevalues
        attr_values=self.env['product.attribute.value'].create([{
            'name':'Red',
            'attribute_id':product_attribute.id,
            'sequence':1,
        },{
            'name':'Green',
            'attribute_id':product_attribute.id,
            'sequence':2,
        },{
            'name':'Blue',
            'attribute_id':product_attribute.id,
            'sequence':3,
        }])

        #createthetemplate,withoutcreatingthevariants
        template=self.env['product.template'].with_context(create_product_product=True).create({
            'name':'Testsubject',
        })

        #whentherearenovariants,theimagemustbeobtainedfromthetemplate
        self.assertEqual(template,template._get_image_holder())

        #setthecolorattributeandvaluesonthetemplate
        line=self.env['product.template.attribute.line'].create([{
            'attribute_id':product_attribute.id,
            'product_tmpl_id':template.id,
            'value_ids':[(6,0,attr_values.ids)]
        }])
        value_red=line.product_template_value_ids[0]
        product_red=template._get_variant_for_combination(value_red)
        product_red.image_variant_1920=image

        value_green=line.product_template_value_ids[1]
        product_green=template._get_variant_for_combination(value_green)
        product_green.image_variant_1920=image

        #whentherearenotemplateimagebuttherearevariants,theimagemustbeobtainedfromthefirstvariant
        self.assertEqual(product_red,template._get_image_holder())

        product_red.toggle_active()

        #butwhensomevariantsarenotavailable,theimagemustbeobtainedfromthefirstavailablevariant
        self.assertEqual(product_green,template._get_image_holder())

        template.image_1920=image

        #whenthereisatemplateimage,theimagemustbeobtainedfromthetemplate
        self.assertEqual(template,template._get_image_holder())
