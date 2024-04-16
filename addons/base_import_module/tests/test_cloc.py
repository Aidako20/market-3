#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

fromflectra.toolsimportcloc
fromflectra.addons.base.testsimporttest_cloc

classTestClocFields(test_cloc.TestClocCustomization):

    deftest_fields_from_import_module(self):
        """
            Checkthatcustomcomputedfieldsinstalledwithanimportedmodule
            iscountedascustomization
        """
        self.env['ir.module.module'].create({
            'name':'imported_module',
            'state':'installed',
            'imported':True,
        })
        f1=self.create_field('x_imported_field')
        self.create_xml_id('imported_module','import_field',f1)
        cl=cloc.Cloc()
        cl.count_customization(self.env)
        self.assertEqual(cl.code.get('imported_module',0),1,'Countfieldswithxml_idofimportedmodule')

    deftest_fields_from_studio(self):
        #Studiomoduledoesnotexistatthisstage,sowesimulateit
        #Checkforexistingmoduleincasethetestrunonanexistingdatabase
        ifnotself.env['ir.module.module'].search([('name','=','studio_customization')]):
            self.env['ir.module.module'].create({
                'author':'Flectra',
                'imported':True,
                'latest_version':'13.0.1.0.0',
                'name':'studio_customization',
                'state':'installed',
                'summary':'StudioCustomization',
            })

        f1=self.create_field('x_field_count')
        self.create_xml_id('studio_customization','field_count',f1)
        cl=cloc.Cloc()
        cl.count_customization(self.env)
        self.assertEqual(cl.code.get('studio_customization',0),0,"Don'tcountfieldgeneratedbystudio")
        f2=self.create_field('x_studio_manual_field')
        self.create_xml_id('studio_customization','manual_field',f2)
        cl=cloc.Cloc()
        cl.count_customization(self.env)
        self.assertEqual(cl.code.get('studio_customization',0),1,"Countmanualfieldcreatedviastudio")

    deftest_fields_module_name(self):
        """
            Checkthatcustomcomputedfieldsinstalledwithanimportedmodule
            iscountedascustomization
        """
        self.env['ir.module.module'].create({
            'name':'imported_module',
            'state':'installed',
            'imported':True,
        })
        f1=self.create_field('x_imported_field')
        self.create_xml_id('imported_module','import_field',f1)
        self.create_xml_id('__export__','import_field',f1)

        sa=self.create_server_action("Testimporteddoublexml_id")
        self.create_xml_id("imported_module","first",sa)
        self.create_xml_id("__export__","second",sa)
        cl=cloc.Cloc()
        cl.count_customization(self.env)
        self.assertEqual(cl.code.get('imported_module',0),3)
