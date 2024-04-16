importos
fromPILimportImage
fromfunctoolsimportpartial

fromflectra.testsimportTransactionCase,tagged,Form
fromflectra.toolsimportfrozendict,image_to_base64,hex_to_rgb


dir_path=os.path.dirname(os.path.realpath(__file__))
_file_cache={}


classTestBaseDocumentLayoutHelpers(TransactionCase):
    #
    #  Public
    #
    defsetUp(self):
        super(TestBaseDocumentLayoutHelpers,self).setUp()
        self.color_fields=['primary_color','secondary_color']
        self.company=self.env.company
        self.css_color_error=0
        self._set_templates_and_layouts()
        self._set_images()

    defassertColors(self,checked_obj,expected):
        _expected_getter=expected.getifisinstance(expected,dict)elsepartial(getattr,expected)
        forfnameinself.color_fields:
            color1=getattr(checked_obj,fname)
            color2=_expected_getter(fname)
            ifself.css_color_error:
                self._compare_colors_rgb(color1,color2)
            else:
                self.assertEqual(color1,color2)

    #
    #  Private
    #
    def_compare_colors_rgb(self,color1,color2):
        self.assertEqual(bool(color1),bool(color2))
        ifnotcolor1:
            return
        color1=hex_to_rgb(color1)
        color2=hex_to_rgb(color2)
        self.assertEqual(len(color1),len(color2))
        foriinrange(len(color1)):
            self.assertAlmostEqual(color1[i],color2[i],delta=self.css_color_error)

    def_get_images_for_test(self):
        return['sweden.png','flectra.png']

    def_set_images(self):
        forfnameinself._get_images_for_test():
            fname_split=fname.split('.')
            ifnotfname_split[0]in_file_cache:
                withImage.open(os.path.join(dir_path,fname),'r')asimg:
                    base64_img=image_to_base64(img,'PNG')
                    primary,secondary=self.env['base.document.layout'].create(
                        {})._parse_logo_colors(base64_img)
                    _img=frozendict({
                        'img':base64_img,
                        'colors':{
                            'primary_color':primary,
                            'secondary_color':secondary,
                        },
                    })
                    _file_cache[fname_split[0]]=_img
        self.company_imgs=frozendict(_file_cache)

    def_set_templates_and_layouts(self):
        self.layout_template1=self.env['ir.ui.view'].create({
            'name':'layout_template1',
            'key':'web.layout_template1',
            'type':'qweb',
            'arch':'''<div></div>''',
        })
        self.env['ir.model.data'].create({
            'name':self.layout_template1.name,
            'model':'ir.ui.view',
            'module':'web',
            'res_id':self.layout_template1.id,
        })
        self.default_colors={
            'primary_color':'#000000',
            'secondary_color':'#000000',
        }
        self.report_layout1=self.env['report.layout'].create({
            'view_id':self.layout_template1.id,
            'name':'report_%s'%self.layout_template1.name,
        })
        self.layout_template2=self.env['ir.ui.view'].create({
            'name':'layout_template2',
            'key':'web.layout_template2',
            'type':'qweb',
            'arch':'''<div></div>''',
        })
        self.env['ir.model.data'].create({
            'name':self.layout_template2.name,
            'model':'ir.ui.view',
            'module':'web',
            'res_id':self.layout_template2.id,
        })
        self.report_layout2=self.env['report.layout'].create({
            'view_id':self.layout_template2.id,
            'name':'report_%s'%self.layout_template2.name,
        })


@tagged('document_layout')
classTestBaseDocumentLayout(TestBaseDocumentLayoutHelpers):
    #LogochangeTests
    deftest_company_no_color_change_logo(self):
        """Whenneitheralogonorthecolorsareset
        Thewizarddisplaysthecolorsofthereportlayout
        Changinglogomeansthecolorsonthewizardchangetoo
        Emptyingthelogoworksanddoesn'tchangethecolors"""
        self.company.write({
            'primary_color':False,
            'secondary_color':False,
            'logo':False,
            'external_report_layout_id':self.env.ref('web.layout_template1').id,
            'paperformat_id':self.env.ref('base.paperformat_us').id,
        })
        default_colors=self.default_colors
        withForm(self.env['base.document.layout'])asdoc_layout:
            self.assertColors(doc_layout,default_colors)
            self.assertEqual(doc_layout.company_id,self.company)
            doc_layout.logo=self.company_imgs['sweden']['img']

            self.assertColors(doc_layout,self.company_imgs['sweden']['colors'])

            doc_layout.logo=''
            self.assertColors(doc_layout,self.company_imgs['sweden']['colors'])
            self.assertEqual(doc_layout.logo,'')

    deftest_company_no_color_but_logo_change_logo(self):
        """Whencompanycolorsarenotset,butalogois,
        thewizarddisplaysthecomputedcolorsfromthelogo"""
        self.company.write({
            'primary_color':'#ff0080',
            'secondary_color':'#00ff00',
            'logo':self.company_imgs['sweden']['img'],
            'paperformat_id':self.env.ref('base.paperformat_us').id,
        })

        withForm(self.env['base.document.layout'])asdoc_layout:
            self.assertColors(doc_layout,self.company)
            doc_layout.logo=self.company_imgs['flectra']['img']
            self.assertColors(doc_layout,self.company_imgs['flectra']['colors'])

    deftest_company_colors_change_logo(self):
        """changesofthelogoimpliesdisplayingthenewcomputedcolors"""
        self.company.write({
            'primary_color':'#ff0080',
            'secondary_color':'#00ff00',
            'logo':False,
            'paperformat_id':self.env.ref('base.paperformat_us').id,
        })

        withForm(self.env['base.document.layout'])asdoc_layout:
            self.assertColors(doc_layout,self.company)
            doc_layout.logo=self.company_imgs['flectra']['img']
            self.assertColors(doc_layout,self.company_imgs['flectra']['colors'])

    deftest_company_colors_and_logo_change_logo(self):
        """Thecolorsofthecompanymaydifferfromtheonethelogocomputes
        Openingthewizardintheseconditiondisplaysthecompany'scolors
        Whenthelogochanges,colorsmustchangeaccordingtothelogo"""
        self.company.write({
            'primary_color':'#ff0080',
            'secondary_color':'#00ff00',
            'logo':self.company_imgs['sweden']['img'],
            'paperformat_id':self.env.ref('base.paperformat_us').id,
        })

        withForm(self.env['base.document.layout'])asdoc_layout:
            self.assertColors(doc_layout,self.company)
            doc_layout.logo=self.company_imgs['flectra']['img']
            self.assertColors(doc_layout,self.company_imgs['flectra']['colors'])

    #Layoutchangetests
    deftest_company_colors_reset_colors(self):
        """Resetthecolorswhentheydifferfromtheonesoriginally
        computedfromthecompanylogo"""
        self.company.write({
            'primary_color':'#ff0080',
            'secondary_color':'#00ff00',
            'logo':self.company_imgs['sweden']['img'],
            'paperformat_id':self.env.ref('base.paperformat_us').id,
        })

        withForm(self.env['base.document.layout'])asdoc_layout:
            self.assertColors(doc_layout,self.company)
            doc_layout.primary_color=doc_layout.logo_primary_color
            doc_layout.secondary_color=doc_layout.logo_secondary_color
            self.assertColors(doc_layout,self.company_imgs['sweden']['colors'])

    deftest_parse_company_colors_grayscale(self):
        """Grayscaleimageswithtransparency-makesurethecolorextractiondoesnotcrash"""
        self.company.write({
            'primary_color':'#ff0080',
            'secondary_color':'#00ff00',
            'paperformat_id':self.env.ref('base.paperformat_us').id,
        })
        withForm(self.env['base.document.layout'])asdoc_layout:
            withImage.open(os.path.join(dir_path,'logo_ci.png'),'r')asimg:
                base64_img=image_to_base64(img,'PNG')
                doc_layout.logo=base64_img
            self.assertNotEqual(None,doc_layout.primary_color)


    #/!\ThiscaseisNOTsupported,andprobablynotsupportable
    #res.partnerresizesmanu-militaritheimageitisgiven
    #sores.company._get_logodiffersfromres.partner.[defaultimage]
    #deftest_company_no_colors_default_logo_and_layout_change_layout(self):
    #    """WhenthedefaultYourCompanylogoisset,andnocolorsaresetoncompany:
    #    changewizard'scoloraccordingtotemplate"""
    #    self.company.write({
    #        'primary_color':False,
    #        'secondary_color':False,
    #        'external_report_layout_id':self.layout_template1.id,
    #    })
    #    default_colors=self.default_colors
    #    withForm(self.env['base.document.layout'])asdoc_layout:
    #        self.assertColors(doc_layout,default_colors)
    #        doc_layout.report_layout_id=self.report_layout2
    #        self.assertColors(doc_layout,self.report_layout2)
