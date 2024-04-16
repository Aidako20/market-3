#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importunittest
fromitertoolsimportzip_longest
fromlxmlimportetreeasET,html
fromlxml.htmlimportbuilderash

fromflectra.testsimportcommon,HttpCase,tagged


defattrs(**kwargs):
    return{'data-oe-%s'%key:str(value)forkey,valueinkwargs.items()}


classTestViewSavingCommon(common.TransactionCase):
    def_create_imd(self,view):
        xml_id=view.key.split('.')
        returnself.env['ir.model.data'].create({
            'module':xml_id[0],
            'name':xml_id[1],
            'model':view._name,
            'res_id':view.id,
        })


classTestViewSaving(TestViewSavingCommon):

    defeq(self,a,b):
        self.assertEqual(a.tag,b.tag)
        self.assertEqual(a.attrib,b.attrib)
        self.assertEqual((a.textor'').strip(),(b.textor'').strip())
        self.assertEqual((a.tailor'').strip(),(b.tailor'').strip())
        forca,cbinzip_longest(a,b):
            self.eq(ca,cb)

    defsetUp(self):
        super(TestViewSaving,self).setUp()
        self.arch=h.DIV(
            h.DIV(
                h.H3("Column1"),
                h.UL(
                    h.LI("Item1"),
                    h.LI("Item2"),
                    h.LI("Item3"))),
            h.DIV(
                h.H3("Column2"),
                h.UL(
                    h.LI("Item1"),
                    h.LI(h.SPAN("MyCompany",attrs(model='res.company',id=1,field='name',type='char'))),
                    h.LI(h.SPAN("+0000000000000",attrs(model='res.company',id=1,field='phone',type='char')))
                ))
        )
        self.view_id=self.env['ir.ui.view'].create({
            'name':"TestView",
            'type':'qweb',
            'key':'website.test_view',
            'arch':ET.tostring(self.arch,encoding='unicode')
        })

    deftest_embedded_extraction(self):
        fields=self.env['ir.ui.view'].extract_embedded_fields(self.arch)

        expect=[
            h.SPAN("MyCompany",attrs(model='res.company',id=1,field='name',type='char')),
            h.SPAN("+0000000000000",attrs(model='res.company',id=1,field='phone',type='char')),
        ]
        foractual,expectedinzip_longest(fields,expect):
            self.eq(actual,expected)

    deftest_embedded_save(self):
        embedded=h.SPAN("+0000000000000",attrs(
            model='res.company',id=1,field='phone',type='char'))

        self.env['ir.ui.view'].save_embedded_field(embedded)

        company=self.env['res.company'].browse(1)
        self.assertEqual(company.phone,"+0000000000000")

    @unittest.skip("saveconflictforembedded(savedbythirdpartyorpreviousversioninpage)notimplemented")
    deftest_embedded_conflict(self):
        e1=h.SPAN("MyCompany",attrs(model='res.company',id=1,field='name'))
        e2=h.SPAN("LeeroyJenkins",attrs(model='res.company',id=1,field='name'))

        View=self.env['ir.ui.view']

        View.save_embedded_field(e1)
        #FIXME:morepreciseexception
        withself.assertRaises(Exception):
            View.save_embedded_field(e2)

    deftest_embedded_to_field_ref(self):
        View=self.env['ir.ui.view']
        embedded=h.SPAN("MyCompany",attrs(expression="bob"))
        self.eq(
            View.to_field_ref(embedded),
            h.SPAN({'t-field':'bob'})
        )

    deftest_to_field_ref_keep_attributes(self):
        View=self.env['ir.ui.view']

        att=attrs(expression="bob",model="res.company",id=1,field="name")
        att['id']="whop"
        att['class']="foobar"
        embedded=h.SPAN("MyCompany",att)

        self.eq(View.to_field_ref(embedded),h.SPAN({'t-field':'bob','class':'foobar','id':'whop'}))

    deftest_replace_arch(self):
        replacement=h.P("Wheee")

        result=self.view_id.replace_arch_section(None,replacement)

        self.eq(result,h.DIV("Wheee"))

    deftest_replace_arch_2(self):
        replacement=h.DIV(h.P("Wheee"))

        result=self.view_id.replace_arch_section(None,replacement)

        self.eq(result,replacement)

    deftest_fixup_arch(self):
        replacement=h.H1("Iamthegreatesttitlealive!")

        result=self.view_id.replace_arch_section('/div/div[1]/h3',replacement)

        self.eq(result,h.DIV(
            h.DIV(
                h.H3("Iamthegreatesttitlealive!"),
                h.UL(
                    h.LI("Item1"),
                    h.LI("Item2"),
                    h.LI("Item3"))),
            h.DIV(
                h.H3("Column2"),
                h.UL(
                    h.LI("Item1"),
                    h.LI(h.SPAN("MyCompany",attrs(model='res.company',id=1,field='name',type='char'))),
                    h.LI(h.SPAN("+0000000000000",attrs(model='res.company',id=1,field='phone',type='char')))
                ))
        ))

    deftest_multiple_xpath_matches(self):
        withself.assertRaises(ValueError):
            self.view_id.replace_arch_section('/div/div/h3',h.H6("Lolnope"))

    deftest_save(self):
        Company=self.env['res.company']

        #createanxmlidfortheview
        imd=self._create_imd(self.view_id)
        self.assertEqual(self.view_id.model_data_id,imd)
        self.assertFalse(imd.noupdate)

        replacement=ET.tostring(h.DIV(
            h.H3("Column2"),
            h.UL(
                h.LI("wobwobwob"),
                h.LI(h.SPAN("AcmeCorporation",attrs(model='res.company',id=1,field='name',expression="bob",type='char'))),
                h.LI(h.SPAN("+123456789",attrs(model='res.company',id=1,field='phone',expression="edmund",type='char'))),
            )
        ),encoding='unicode')

        self.view_id.with_context(website_id=1).save(value=replacement,xpath='/div/div[2]')
        self.assertFalse(imd.noupdate,"view'sxml_idshouldn'tbesetto'noupdate'inawebsitecontextas`save`methodwillCOW")
        #removenewlycreatedCOWviewsonext`save()``wontberedirectedtoCOWview
        self.env['website'].with_context(website_id=1).viewref(self.view_id.key).unlink()

        self.view_id.save(value=replacement,xpath='/div/div[2]')

        #thexml_idoftheviewshouldbeflaggedas'noupdate'
        self.assertTrue(imd.noupdate)

        company=Company.browse(1)
        self.assertEqual(company.name,"AcmeCorporation")
        self.assertEqual(company.phone,"+123456789")
        self.eq(
            ET.fromstring(self.view_id.arch),
            h.DIV(
                h.DIV(
                    h.H3("Column1"),
                    h.UL(
                        h.LI("Item1"),
                        h.LI("Item2"),
                        h.LI("Item3"))),
                h.DIV(
                    h.H3("Column2"),
                    h.UL(
                        h.LI("wobwobwob"),
                        h.LI(h.SPAN({'t-field':"bob"})),
                        h.LI(h.SPAN({'t-field':"edmund"}))
                    ))
            )
        )

    deftest_save_escaped_text(self):
        """Testsavinghtmlspecialcharsintextnodes"""
        view=self.env['ir.ui.view'].create({
            'arch':u'<tt-name="dummy"><p><h1>helloworld</h1></p></t>',
            'type':'qweb'
        })
        #scriptandstyletextnodesshouldnotescapedclientside
        replacement=u'<script>1&&"hello&world"</script>'
        view.save(replacement,xpath='/t/p/h1')
        self.assertIn(
            replacement.replace(u'&',u'&amp;'),
            view.arch,
            'inlinescriptshouldbeescapedserverside'
        )
        self.assertIn(
            replacement,
            view._render().decode('utf-8'),
            'inlinescriptshouldnotbeescapedwhenrendering'
        )
        #commontextnodesshouldbebeescapedclientside
        replacement=u'world&amp;amp;&amp;lt;b&amp;gt;cie'
        view.save(replacement,xpath='/t/p')
        self.assertIn(replacement,view.arch,'commontextnodeshouldnotbeescapedserverside')
        self.assertIn(
            replacement,
            view._render().decode('utf-8').replace(u'&',u'&amp;'),
            'textnodecharacterswronglyunescapedwhenrendering'
        )

    deftest_save_oe_structure_with_attr(self):
        """Testsavingoe_structurewithattributes"""
        view=self.env['ir.ui.view'].create({
            'arch':u'<tt-name="dummy"><divclass="oe_structure"t-att-test="1"data-test="1"id="oe_structure_test"/></t>',
            'type':'qweb'
        }).with_context(website_id=1,load_all_views=True)
        replacement=u'<divclass="oe_structure"data-test="1"id="oe_structure_test"data-oe-id="55"test="2">hello</div>'
        view.save(replacement,xpath='/t/div')
        #brandingdata-oe-*shouldbestripped
        self.assertIn(
            '<divclass="oe_structure"data-test="1"id="oe_structure_test"test="2">hello</div>',
            view.read_combined(['arch'])['arch'],
            'savedelementattributesaresavedexcludingbrandingones'
        )

    deftest_save_only_embedded(self):
        Company=self.env['res.company']
        company_id=1
        company=Company.browse(company_id)
        company.write({'name':"FooCorporation"})

        node=html.tostring(h.SPAN(
            "AcmeCorporation",
            attrs(model='res.company',id=company_id,field="name",expression='bob',type='char')),
            encoding='unicode')
        View=self.env['ir.ui.view']
        View.browse(company_id).save(value=node)
        self.assertEqual(company.name,"AcmeCorporation")

    deftest_field_tail(self):
        replacement=ET.tostring(
            h.LI(h.SPAN("+123456789",attrs(
                        model='res.company',id=1,type='char',
                        field='phone',expression="edmund")),
                 "whopwhop"
                 ),encoding="utf-8")
        self.view_id.save(value=replacement,xpath='/div/div[2]/ul/li[3]')

        self.eq(
            ET.fromstring(self.view_id.arch.encode('utf-8')),
            h.DIV(
                h.DIV(
                    h.H3("Column1"),
                    h.UL(
                        h.LI("Item1"),
                        h.LI("Item2"),
                        h.LI("Item3"))),
                h.DIV(
                    h.H3("Column2"),
                    h.UL(
                        h.LI("Item1"),
                        h.LI(h.SPAN("MyCompany",attrs(model='res.company',id=1,field='name',type='char'))),
                        h.LI(h.SPAN({'t-field':"edmund"}),"whopwhop"),
                    ))
            )
        )


@tagged('-at_install','post_install')
classTestCowViewSaving(TestViewSavingCommon):
    defsetUp(self):
        super(TestCowViewSaving,self).setUp()
        View=self.env['ir.ui.view']

        self.base_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'<div>basecontent</div>',
            'key':'website.base_view',
        }).with_context(load_all_views=True)

        self.inherit_view=View.create({
            'name':'Extension',
            'mode':'extension',
            'inherit_id':self.base_view.id,
            'arch':'<divposition="inside">,extendedcontent</div>',
            'key':'website.extension_view',
        })

    deftest_cow_on_base_after_extension(self):
        View=self.env['ir.ui.view']
        self.inherit_view.with_context(website_id=1).write({'name':'ExtensionSpecific'})
        v1=self.base_view
        v2=self.inherit_view
        v3=View.search([('website_id','=',1),('name','=','ExtensionSpecific')])
        v4=self.inherit_view.copy({'name':'SecondExtension'})
        v5=self.inherit_view.copy({'name':'ThirdExtension(Specific)'})
        v5.write({'website_id':1})

        #id|name                       |website_id|inherit |key
        #------------------------------------------------------------------------
        #1 |Base                       |    /     |    /   | website.base_view
        #2 |Extension                  |    /     |    1   | website.extension_view
        #3 |ExtensionSpecific         |    1     |    1   | website.extension_view
        #4 |SecondExtension           |    /     |    1   | website.extension_view_a5f579d5(generatedhash)
        #5 |ThirdExtension(Specific) |    1     |    1   | website.extension_view_5gr87e6c(anothergeneratedhash)

        self.assertEqual(v2.key==v3.key,True,"Makingspecificagenericinheritedviewshouldcopyit'skey(justchangethewebsite_id)")
        self.assertEqual(v3.key!=v4.key!=v5.key,True,"Copyingaviewshouldgenerateanewkeyforthenewview(notthecasewhentriggeringCOW)")
        self.assertEqual('website.extension_view'inv3.keyand'website.extension_view'inv4.keyand'website.extension_view'inv5.key,True,"Thecopiedviewsshouldhavethekeyfromtheviewitwascopiedfrombutwithanuniquesuffix")

        total_views=View.search_count([])
        v1.with_context(website_id=1).write({'name':'BaseSpecific'})

        #id|name                       |website_id|inherit |key
        #------------------------------------------------------------------------
        #1 |Base                       |    /     |    /   | website.base_view
        #2 |Extension                  |    /     |    1   | website.extension_view
        #3-DELETED
        #4 |SecondExtension           |    /     |    1   | website.extension_view_a5f579d5
        #5-DELETED
        #6 |BaseSpecific              |    1     |    /   | website.base_view
        #7 |ExtensionSpecific         |    1     |    6   | website.extension_view
        #8 |SecondExtension           |    1     |    6   | website.extension_view_a5f579d5
        #9 |ThirdExtension(Specific) |    1     |    6   | website.extension_view_5gr87e6c

        v6=View.search([('website_id','=',1),('name','=','BaseSpecific')])
        v7=View.search([('website_id','=',1),('name','=','ExtensionSpecific')])
        v8=View.search([('website_id','=',1),('name','=','SecondExtension')])
        v9=View.search([('website_id','=',1),('name','=','ThirdExtension(Specific)')])

        self.assertEqual(total_views+4-2,View.search_count([]),"Itshouldhaveduplicatedtheviewtreewithawebsite_id,takingonlymostspecific(onlyspecific`b`key),andremovingwebsite_specificfromgenerictree")
        self.assertEqual(len((v3+v5).exists()),0,"v3andv5shouldhavebeendeletedastheywerealreadyspecificandcopiedtothenewspecificbase")
        #Checkgenerictree
        self.assertEqual((v1+v2+v4).mapped('website_id').ids,[])
        self.assertEqual((v2+v4).mapped('inherit_id'),v1)
        #Checkspecifictree
        self.assertEqual((v6+v7+v8+v9).mapped('website_id').ids,[1])
        self.assertEqual((v7+v8+v9).mapped('inherit_id'),v6)
        #Checkkey
        self.assertEqual(v6.key==v1.key,True)
        self.assertEqual(v7.key==v2.key,True)
        self.assertEqual(v4.key==v8.key,True)
        self.assertEqual(View.search_count([('key','=',v9.key)]),1)

    deftest_cow_leaf(self):
        View=self.env['ir.ui.view']

        #editonbackend,regularwrite
        self.inherit_view.write({'arch':'<divposition="replace"><div>modifiedcontent</div></div>'})
        self.assertEqual(View.search_count([('key','=','website.base_view')]),1)
        self.assertEqual(View.search_count([('key','=','website.extension_view')]),1)

        arch=self.base_view.read_combined(['arch'])['arch']
        self.assertEqual(arch,'<div>modifiedcontent</div>')

        #editonfrontend,copyjusttheleaf
        self.inherit_view.with_context(website_id=1).write({'arch':'<divposition="replace"><div>website1content</div></div>'})
        inherit_views=View.search([('key','=','website.extension_view')])
        self.assertEqual(View.search_count([('key','=','website.base_view')]),1)
        self.assertEqual(len(inherit_views),2)
        self.assertEqual(len(inherit_views.filtered(lambdav:v.website_id.id==1)),1)

        #readinbackendshouldbeunaffected
        arch=self.base_view.read_combined(['arch'])['arch']
        self.assertEqual(arch,'<div>modifiedcontent</div>')
        #readonwebsiteshouldreflectchange
        arch=self.base_view.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual(arch,'<div>website1content</div>')

        #website-specificinactiveviewshouldtakepreferenceoveractivegenericonewhenviewingthewebsite
        #thisisnecessarytomakecustomize_show=Truetemplatesworkcorrectly
        inherit_views.filtered(lambdav:v.website_id.id==1).write({'active':False})
        arch=self.base_view.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual(arch,'<div>basecontent</div>')

    deftest_cow_root(self):
        View=self.env['ir.ui.view']

        #editonbackend,regularwrite
        self.base_view.write({'arch':'<div>modifiedbasecontent</div>'})
        self.assertEqual(View.search_count([('key','=','website.base_view')]),1)
        self.assertEqual(View.search_count([('key','=','website.extension_view')]),1)

        #editonfrontend,copytheentiretree
        self.base_view.with_context(website_id=1).write({'arch':'<div>website1content</div>'})

        generic_base_view=View.search([('key','=','website.base_view'),('website_id','=',False)])
        website_specific_base_view=View.search([('key','=','website.base_view'),('website_id','=',1)])
        self.assertEqual(len(generic_base_view),1)
        self.assertEqual(len(website_specific_base_view),1)

        inherit_views=View.search([('key','=','website.extension_view')])
        self.assertEqual(len(inherit_views),2)
        self.assertEqual(len(inherit_views.filtered(lambdav:v.website_id.id==1)),1)

        arch=generic_base_view.with_context(load_all_views=True).read_combined(['arch'])['arch']
        self.assertEqual(arch,'<div>modifiedbasecontent,extendedcontent</div>')

        arch=website_specific_base_view.with_context(load_all_views=True,website_id=1).read_combined(['arch'])['arch']
        self.assertEqual(arch,'<div>website1content,extendedcontent</div>')

    ##AsthereisanewSQLconstraintthatpreventQWebviewstohaveanempty`key`,thistestwon'twork
    #deftest_cow_view_without_key(self):
    #    #Removekeyforthistest
    #    self.base_view.key=False
    #
    #    View=self.env['ir.ui.view']
    #
    #    #editonbackend,regularwrite
    #    self.base_view.write({'arch':'<div>modifiedbasecontent</div>'})
    #    self.assertEqual(self.base_view.key,False,"Writingonakeylessviewshouldnotsetakeyonitifthereisnowebsiteincontext")
    #
    #    #editonfrontend,copyjusttheleaf
    #    self.base_view.with_context(website_id=1).write({'arch':'<divposition="replace"><div>website1content</div></div>'})
    #    self.assertEqual('website.key_'inself.base_view.key,True,"Writingonakeylessviewshouldsetakeyonitifthereisawebsiteincontext")
    #    total_views_with_key=View.search_count([('key','=',self.base_view.key)])
    #    self.assertEqual(total_views_with_key,2,"Itshouldhavesetthekeyongenericviewthencopytospecificview(withtheykey)")

    deftest_cow_generic_view_with_already_existing_specific(self):
        """Writingonagenericviewshouldcheckifawebsitespecificviewalreadyexists
            (Theflowofthistestwillhappenwheneditingagenericviewinthefrontendandchangingmorethanoneelement)
        """
        #1.Testwithcallingwritedirectly
        View=self.env['ir.ui.view']

        base_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'<div>content</div>',
        })

        total_views=View.with_context(active_test=False).search_count([])
        base_view.with_context(website_id=1).write({'name':'NewName'}) #Thiswillnotwriteon`base_view`butwillcopyittoaspecificviewonwhichthe`name`changewillbeapplied
        specific_view=View.search([['name','=','NewName'],['website_id','=',1]])
        base_view.with_context(website_id=1).write({'name':'AnotherNewName'})
        specific_view.active=False
        base_view.with_context(website_id=1).write({'name':'YetAnotherNewName'})
        self.assertEqual(total_views+1,View.with_context(active_test=False).search_count([]),"Subsequentwritesshouldhavewrittenontheviewcopiedduringfirstwrite")

        #2.Testwithcallingsave()fromir.ui.view
        view_arch='''<tname="SecondView"t-name="website.second_view">
                          <tt-call="website.layout">
                            <divid="wrap">
                              <divclass="editable_part"/>
                              <divclass="container">
                                  <h1>SecondView</h1>
                              </div>
                              <divclass="editable_part"/>
                            </div>
                          </t>
                       </t>'''
        second_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':view_arch,
        })

        total_views=View.with_context(active_test=False).search_count([])
        second_view.with_context(website_id=1).save('<divclass="editable_part"data-oe-id="%s"data-oe-xpath="/t[1]/t[1]/div[1]/div[1]"data-oe-field="arch"data-oe-model="ir.ui.view">Firsteditable_part</div>'%second_view.id,"/t[1]/t[1]/div[1]/div[1]")
        second_view.with_context(website_id=1).save('<divclass="editable_part"data-oe-id="%s"data-oe-xpath="/t[1]/t[1]/div[1]/div[3]"data-oe-field="arch"data-oe-model="ir.ui.view">Secondeditable_part</div>'%second_view.id,"/t[1]/t[1]/div[1]/div[3]")
        self.assertEqual(total_views+1,View.with_context(active_test=False).search_count([]),"Secondsaveshouldhavewrittenontheviewcopiedduringfirstsave")

        total_specific_view=View.with_context(active_test=False).search_count([('arch_db','like','Firsteditable_part'),('arch_db','like','Secondeditable_part')])
        self.assertEqual(total_specific_view,1,"botheditable_partshouldhavebeenreplacedonacreatedspecificview")

    deftest_cow_complete_flow(self):
        View=self.env['ir.ui.view']
        total_views=View.search_count([])

        self.base_view.write({'arch':'<div>Hi</div>'})
        self.inherit_view.write({'arch':'<divposition="inside">World</div>'})

        #id|name     |content|website_id|inherit |key
        #-------------------------------------------------------
        #1 |Base     | Hi    |    /     |    /   | website.base_view
        #2 |Extension| World |    /     |    1   | website.extension_view

        arch=self.base_view.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual('HiWorld'inarch,True)

        self.base_view.write({'arch':'<div>Hello</div>'})

        #id|name     |content|website_id|inherit |key
        #-------------------------------------------------------
        #1 |Base     | Hello |    /     |    /   | website.base_view
        #2 |Extension| World |    /     |    1   | website.extension_view

        arch=self.base_view.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual('HelloWorld'inarch,True)

        self.base_view.with_context(website_id=1).write({'arch':'<div>Bye</div>'})

        #id|name     |content|website_id|inherit |key
        #-------------------------------------------------------
        #1 |Base     | Hello |    /     |    /   | website.base_view
        #3 |Base     | Bye   |    1     |    /   | website.base_view
        #2 |Extension| World |    /     |    1   | website.extension_view
        #4 |Extension| World |    1     |    3   | website.extension_view

        base_specific=View.search([('key','=',self.base_view.key),('website_id','=',1)]).with_context(load_all_views=True)
        extend_specific=View.search([('key','=',self.inherit_view.key),('website_id','=',1)])
        self.assertEqual(total_views+2,View.search_count([]),"ShouldhavecopiedBase&Extensionwithawebsite_id")
        self.assertEqual(self.base_view.key,base_specific.key)
        self.assertEqual(self.inherit_view.key,extend_specific.key)

        extend_specific.write({'arch':'<divposition="inside">All</div>'})

        #id|name     |content|website_id|inherit |key
        #-------------------------------------------------------
        #1 |Base     | Hello |    /     |    /   | website.base_view
        #3 |Base     | Bye   |    1     |    /   | website.base_view
        #2 |Extension| World |    /     |    1   | website.extension_view
        #4 |Extension| All   |    1     |    3   | website.extension_view

        arch=base_specific.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual('ByeAll'inarch,True)

        self.inherit_view.with_context(website_id=1).write({'arch':'<divposition="inside">Nobody</div>'})

        #id|name     |content|website_id|inherit |key
        #-------------------------------------------------------
        #1 |Base     | Hello |    /     |    /   | website.base_view
        #3 |Base     | Bye   |    1     |    /   | website.base_view
        #2 |Extension| World |    /     |    1   | website.extension_view
        #4 |Extension| Nobody|    1     |    3   | website.extension_view

        arch=base_specific.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual('ByeNobody'inarch,True,"Writeongeneric`inherit_view`shouldhavebeendivertedtoalreadyexistingspecificview")

        base_arch=self.base_view.read_combined(['arch'])['arch']
        base_arch_w1=self.base_view.with_context(website_id=1).read_combined(['arch'])['arch']
        self.assertEqual('HelloWorld'inbase_arch,True)
        self.assertEqual(base_arch,base_arch_w1,"Readingatoplevelviewwithorwithoutawebsite_idinthecontextshouldrenderthatexactview..") #..evenifthereisaspecificviewforthatone,asread_combinedissupposedtorenderspecificinheritedviewovergenericbutnotspecifictoplevelinsteadofgenerictoplevel

    deftest_cow_cross_inherit(self):
        View=self.env['ir.ui.view']
        total_views=View.search_count([])

        main_view=View.create({
            'name':'MainView',
            'type':'qweb',
            'arch':'<body>GENERIC<div>A</div></body>',
            'key':'website.main_view',
        }).with_context(load_all_views=True)

        View.create({
            'name':'ChildView',
            'mode':'extension',
            'inherit_id':main_view.id,
            'arch':'<xpathexpr="//div"position="replace"><div>VIEW<p>B</p></div></xpath>',
            'key':'website.child_view',
        })

        child_view_2=View.with_context(load_all_views=True).create({
            'name':'ChildView2',
            'mode':'extension',
            'inherit_id':main_view.id,
            'arch':'<xpathexpr="//p"position="replace"><span>C</span></xpath>',
            'key':'website.child_view_2',
        })

        #Theselinedoing`write()`aretherealtests,itshouldnotbechangedandshouldnotcrashonxpath.
        child_view_2.with_context(website_id=1).write({'arch':'<xpathexpr="//p"position="replace"><span>D</span></xpath>'})
        self.assertEqual(total_views+3+1,View.search_count([]),"Itshouldhavecreatedthe3initialgenericviewsandcreatedachild_view_2specificview")
        main_view.with_context(website_id=1).write({'arch':'<body>SPECIFIC<div>Z</div></body>'})
        self.assertEqual(total_views+3+3,View.search_count([]),"ItshouldhaveduplicatedtheMainViewtreeasaspecifictreeandthenremovedthespecificviewfromthegenerictreeasnomoreneeded")

        generic_view=View.with_context(website_id=None).get_view_id('website.main_view')
        specific_view=View.with_context(website_id=1).get_view_id('website.main_view')
        generic_view_arch=View.browse(generic_view).with_context(load_all_views=True).read_combined(['arch'])['arch']
        specific_view_arch=View.browse(specific_view).with_context(load_all_views=True,website_id=1).read_combined(['arch'])['arch']
        self.assertEqual(generic_view_arch,'<body>GENERIC<div>VIEW<span>C</span></div></body>')
        self.assertEqual(specific_view_arch,'<body>SPECIFIC<div>VIEW<span>D</span></div></body>',"Writingontoplevelviewhierarchywithawebsiteincontextshouldwriteontheviewandcloneit'sinheritedviews")

    deftest_multi_website_view_obj_active(self):
        '''Withthefollowingstructure:
            *Agenericactiveparentview
            *Agenericactivechildview,thatisinactiveonwebsite1
            Themethodstoretrieveviewsshouldreturnthespecificinactive
            childoverthegenericactiveone.
        '''
        View=self.env['ir.ui.view']
        self.inherit_view.with_context(website_id=1).write({'active':False})

        #Test_view_obj()returntheinactivespecificoveractivegeneric
        inherit_view=View._view_obj(self.inherit_view.key)
        self.assertEqual(inherit_view.active,True,"_view_objshouldreturnthegenericone")
        inherit_view=View.with_context(website_id=1)._view_obj(self.inherit_view.key)
        self.assertEqual(inherit_view.active,False,"_view_objshouldreturnthespecificone")

        #Testget_related_views()returntheinactivespecificoveractivegeneric
        #Notethatwecannottestget_related_viewswithoutawebsiteincontextasitwillfallbackonawebsitewithget_current_website()
        views=View.with_context(website_id=1).get_related_views(self.base_view.key)
        self.assertEqual(views.mapped('active'),[True,False],"get_related_viewsshouldreturnthespecificchild")

        #Testfilter_duplicate()returntheinactivespecificoveractivegeneric
        view=View.with_context(active_test=False).search([('key','=',self.inherit_view.key)]).filter_duplicate()
        self.assertEqual(view.active,True,"filter_duplicateshouldreturnthegenericone")
        view=View.with_context(active_test=False,website_id=1).search([('key','=',self.inherit_view.key)]).filter_duplicate()
        self.assertEqual(view.active,False,"filter_duplicateshouldreturnthespecificone")

    deftest_get_related_views_tree(self):
        View=self.env['ir.ui.view']

        self.base_view.write({'name':'B','key':'B'})
        self.inherit_view.write({'name':'I','key':'I'})
        View.create({
            'name':'II',
            'mode':'extension',
            'inherit_id':self.inherit_view.id,
            'arch':'<divposition="inside">,subext</div>',
            'key':'II',
        })

        # B
        # |
        # I
        # |
        # II

        #First,testthatchildrenofinactivechildrenarenotreturned(notmultiwebsiterelated)
        self.inherit_view.active=False
        views=View.get_related_views('B')
        self.assertEqual(views.mapped('key'),['B','I'],"As'I'isinactive,'II'(itsownchild)shouldnotbereturned.")
        self.inherit_view.active=True

        #Second,testmulti-website
        self.inherit_view.with_context(website_id=1).write({'name':'Extension'}) #Triggercowonhierarchy
        View.create({
            'name':'II2',
            'mode':'extension',
            'inherit_id':self.inherit_view.id,
            'arch':'<divposition="inside">,subsiblingspecific</div>',
            'key':'II2',
        })

        #      B
        #     /\
        #    /  \
        #   I    I'
        #  /\    |
        #II II2  II'

        views=View.with_context(website_id=1).get_related_views('B')
        self.assertEqual(views.mapped('key'),['B','I','II'],"Shouldonlyreturnthespecifictree")

    deftest_get_related_views_tree_recursive_t_call_and_inherit_inactive(self):
        """IfaviewAwasdoingat-callonaviewBandviewBhadviewCaschild.
            AndviewAhadviewDaschild.
            AndviewDalsot-callviewB(thatasmentionnedabovehasviewCaschild).
            AndviewDwasinactive(`d`inbellowschema).

            ThenCOWingCtosetitasinactivewouldmake`get_related_views()`onAtoreturn
            bothgenericactiveCandCOWinactiveC.
            (TypicallythecaseforCustomizeshowon/shopforWishlist,compare..)
            Seecommitmessagefordetailedexplanation.
        """
        #A->B
        #|   ^\
        #|   | C
        #d___|

        View=self.env['ir.ui.view']
        Website=self.env['website']

        products=View.create({
            'name':'Products',
            'type':'qweb',
            'key':'_website_sale.products',
            'arch':'''
                <divid="products_grid">
                    <tt-call="_website_sale.products_item"/>
                </div>
        ''',
        })

        products_item=View.create({
            'name':'Productsitem',
            'type':'qweb',
            'key':'_website_sale.products_item',
            'arch':'''
                <divclass="product_price"/>
            ''',
        })

        add_to_wishlist=View.create({
            'name':'Wishlist',
            'active':True,
            'customize_show':True,
            'inherit_id':products_item.id,
            'key':'_website_sale_wishlist.add_to_wishlist',
            'arch':'''
                <xpathexpr="//div[hasclass('product_price')]"position="inside"></xpath>
            ''',
        })

        products_list_view=View.create({
            'name':'ListView',
            'active':False, #<-That'sthereasonofwhythisbehaviorneededafix
            'customize_show':True,
            'inherit_id':products.id,
            'key':'_website_sale.products_list_view',
            'arch':'''
                <divid="products_grid"position="replace">
                    <tt-call="_website_sale.products_item"/>
                </div>
            ''',
        })

        views=View.with_context(website_id=1).get_related_views('_website_sale.products')
        self.assertEqual(views,products+products_item+add_to_wishlist+products_list_view,"Thefourviewsshouldbereturned.")
        add_to_wishlist.with_context(website_id=1).write({'active':False}) #Triggercowonhierarchy
        add_to_wishlist_cow=Website.with_context(website_id=1).viewref(add_to_wishlist.key)
        views=View.with_context(website_id=1).get_related_views('_website_sale.products')
        self.assertEqual(views,products+products_item+add_to_wishlist_cow+products_list_view,"ThegenericwishlistviewshouldhavebeenreplacedbytheCOWone.")

    deftest_cow_inherit_children_order(self):
        """COWmethodshouldlooponinherit_children_idsincorrectorder
            whencopyingthemonthenewspecifictree.
            Correctorderisthesameastheonewhenapplyingviewarch:
            PRIORITY,ID
            Andnotthedefaultonefromir.ui.view(NAME,PRIORITY,ID).
        """
        self.inherit_view.copy({
            'name':'alphabeticallybefore"Extension"',
            'key':'_test.alphabetically_first',
            'arch':'<divposition="replace"><p>COMPARE</p></div>',
        })
        #Nextlineshouldnotcrash,COWlooponinherit_children_idsshouldbesortedcorrectly
        self.base_view.with_context(website_id=1).write({'name':'Product(W1)'})

    deftest_write_order_vs_cow_inherit_children_order(self):
        """Whenbothaspecificinheritingviewandanon-specificbaseview
            arewrittensimultaneously,thespecificinheritingbaseview
            mustbeupdatedeventhoughitsidwillchangeduringtheCOWof
            thebaseview.
        """
        View=self.env['ir.ui.view']
        self.inherit_view.with_context(website_id=1).write({'name':'SpecificInheritedViewChangedFirst'})
        specific_view=View.search([('name','=','SpecificInheritedViewChangedFirst')])
        views=View.browse([self.base_view.id,specific_view.id])
        views.with_context(website_id=1).write({'active':False})
        new_specific_view=View.search([('name','=','SpecificInheritedViewChangedFirst')])
        self.assertTrue(specific_view.id!=new_specific_view.id,"Shouldhaveanewid")
        self.assertFalse(new_specific_view.active,"Shouldhavebeendeactivated")

    deftest_write_order_vs_cow_inherit_children_order_alt(self):
        """Sameastheprevioustest,butrequestingtheupdateinthe
            oppositeorder.
        """
        View=self.env['ir.ui.view']
        self.inherit_view.with_context(website_id=1).write({'name':'SpecificInheritedViewChangedFirst'})
        specific_view=View.search([('name','=','SpecificInheritedViewChangedFirst')])
        views=View.browse([specific_view.id,self.base_view.id])
        views.with_context(website_id=1).write({'active':False})
        new_specific_view=View.search([('name','=','SpecificInheritedViewChangedFirst')])
        self.assertTrue(specific_view.id!=new_specific_view.id,"Shouldhaveanewid")
        self.assertFalse(new_specific_view.active,"Shouldhavebeendeactivated")

    deftest_module_new_inherit_view_on_parent_already_forked(self):
        """Ifagenericparentviewiscopied(COW)andthatanothermodule
            createsachildviewforthatgenericparent,alltheCOWviews
            shouldalsogetacopyofthatnewchildview.

            Typically,aparentview(website_sale.product)iscopied(COW)
            andthenwishlistmoduleisinstalled.
            Wishlistviewsinheringfromwebsite_sale.productareaddedtothe
            generic`website_sale.product`.Butitshouldalsobeaddedtothe
            COW`website_sale.product`toactivatethemoduleviewsforthat
            website.
        """
        Website=self.env['website']
        View=self.env['ir.ui.view']

        #Simulatewebsite_saleproductview
        self.base_view.write({'name':'Product','key':'_website_sale.product'})
        #Triggercowonwebsite_salehierarchyforwebsite1
        self.base_view.with_context(website_id=1).write({'name':'Product(W1)'})

        #Simulatewebsite_sale_comparisoninstall
        View._load_records([dict(xml_id='_website_sale_comparison.product_add_to_compare',values={
            'name':'Addtocomparisoninproductpage',
            'mode':'extension',
            'inherit_id':self.base_view.id,
            'arch':'<divposition="replace"><p>COMPARE</p></div>',
            'key':'_website_sale_comparison.product_add_to_compare',
        })])
        Website.with_context(load_all_views=True).viewref('_website_sale_comparison.product_add_to_compare').invalidate_cache()

        #Simulateendofinstallation/update
        View._create_all_specific_views(['_website_sale_comparison'])

        specific_view=Website.with_context(load_all_views=True,website_id=1).viewref('_website_sale.product')
        self.assertEqual(self.base_view.key,specific_view.key,"Ensureitisequalasitshouldbefortherestofthetestsowetesttheexpectedbehaviors")
        specific_view_arch=specific_view.read_combined(['arch'])['arch']
        self.assertEqual(specific_view.website_id.id,1,"Ensurewegotspecificviewtoperformthechecksagainst")
        self.assertEqual(specific_view_arch,'<p>COMPARE</p>',"Whenamodulecreatesaninheritedview(onagenerictree),itshouldalsocreatethatviewinthespecificCOW'dtree.")

        #Simulatewebsite_sale_comparisonupdate
        View._load_records([dict(xml_id='_website_sale_comparison.product_add_to_compare',values={
            'arch':'<divposition="replace"><p>COMPAREEDITED</p></div>',
        })])
        specific_view_arch=Website.with_context(load_all_views=True,website_id=1).viewref('_website_sale.product').read_combined(['arch'])['arch']
        self.assertEqual(specific_view_arch,'<p>COMPAREEDITED</p>',"Whenamoduleupdatesaninheritedview(onagenerictree),itshouldalsoupdatethecopiesofthatview(COW).")

        #TestfieldsthatshouldnotbeCOW'd
        random_views=View.search([('key','!=',None)],limit=2)
        View._load_records([dict(xml_id='_website_sale_comparison.product_add_to_compare',values={
            'website_id':None,
            'inherit_id':random_views[0].id,
        })])

        w1_specific_child_view=Website.with_context(load_all_views=True,website_id=1).viewref('_website_sale_comparison.product_add_to_compare')
        generic_child_view=Website.with_context(load_all_views=True).viewref('_website_sale_comparison.product_add_to_compare')
        self.assertEqual(w1_specific_child_view.website_id.id,1,"website_idisaprohibitedfieldwhenCOWingviewsduring_load_records")
        self.assertEqual(generic_child_view.inherit_id,random_views[0],"prohibitedfieldsonlyconcernedwriteonCOW'dview.Genericshouldstillconsiderethesefields")
        self.assertEqual(w1_specific_child_view.inherit_id,random_views[0],"inherit_idupdateshouldberepliacatedoncowviewsduring_load_records")

        #Setbackthegenericviewasparentfortherestofthetest
        generic_child_view.inherit_id=self.base_view
        w1_specific_child_view.inherit_id=specific_view

        #Don'tupdateinherit_idifitwasanuallyupdated
        w1_specific_child_view.inherit_id=random_views[1].id
        View._load_records([dict(xml_id='_website_sale_comparison.product_add_to_compare',values={
            'inherit_id':random_views[0].id,
        })])
        self.assertEqual(w1_specific_child_view.inherit_id,random_views[1],
                         "inherit_idupdateshouldnotberepliacatedoncowviewsduring_load_recordsifitwasmanuallyupdatedbefore")

        #Setbackthegenericviewasparentfortherestofthetest
        generic_child_view.inherit_id=self.base_view
        w1_specific_child_view.inherit_id=specific_view

        #Don'tupdatefieldsfromCOW'dviewifthesefieldshavebeenmodifiedfromoriginalview
        new_website=Website.create({'name':'NewWebsite'})
        self.base_view.with_context(website_id=new_website.id).write({'name':'Product(new_website)'})
        new_website_specific_child_view=Website.with_context(load_all_views=True,website_id=new_website.id).viewref('_website_sale_comparison.product_add_to_compare')
        new_website_specific_child_view.priority=6
        View._load_records([dict(xml_id='_website_sale_comparison.product_add_to_compare',values={
            'priority':3,
        })])
        self.assertEqual(generic_child_view.priority,3,"XMLupdateshouldbewrittenontheGenericView")
        self.assertEqual(w1_specific_child_view.priority,3,"XMLupdateshouldbewrittenonthespecificviewifthefieldshavenotbeenmodifiedonthatspecificview")
        self.assertEqual(new_website_specific_child_view.priority,6,"XMLupdateshouldNOTbewrittenonthespecificviewifthefieldshavebeenmodifiedonthatspecificview")

        #Simulatewebsite_saleupdateontoplevelview
        self._create_imd(self.base_view)
        self.base_view.invalidate_cache()
        View._load_records([dict(xml_id='_website_sale.product',values={
            'website_meta_title':'Abuggotfixedbyupdatingthisfield',
        })])
        all_title_updated=specific_view.website_meta_title==self.base_view.website_meta_title=="Abuggotfixedbyupdatingthisfield"
        self.assertEqual(all_title_updated,True,"Updateontoplevelgenericviewsshouldalsobeappliedonspecificviews")

    deftest_module_new_inherit_view_on_parent_already_forked_xpath_replace(self):
        """Deeper,morespecifictestofabovebehavior.
            Amoduleinstallshouldadd/updatetheCOWview(ifallowedfields,
            egnotmodifiedorprohibited(website_id,inherit_id..)).
            Thistestensureitdoesnotcrashifthechildviewisaprimaryview.
        """
        View=self.env['ir.ui.view']

        #Simulatelayoutviews
        base_view=View.create({
            'name':'MainFrontendLayout',
            'type':'qweb',
            'arch':'<tt-call="web.layout"><tt-set="head_website"/></t>',
            'key':'_portal.frontend_layout',
        }).with_context(load_all_views=True)

        inherit_view=View.create({
            'name':'Mainlayout',
            'mode':'extension',
            'inherit_id':base_view.id,
            'arch':'<xpathexpr="//t[@t-set=\'head_website\']"position="replace"><tt-call-assets="web_editor.assets_summernote"t-js="false"groups="website.group_website_publisher"/></xpath>',
            'key':'_website.layout',
        })

        #Triggercowonwebsite_salehierarchyforwebsite1
        base_view.with_context(website_id=1).write({'name':'MainFrontendLayout(W1)'})

        #Simulatewebsite_sale_comparisoninstall,that'stherealtest,it
        #shouldnotcrash.
        View._load_records([dict(xml_id='_website_forum.layout',values={
            'name':'ForumLayout',
            'mode':'primary',
            'inherit_id':inherit_view.id,
            'arch':'<xpathexpr="//t[@t-call-assets=\'web_editor.assets_summernote\'][@t-js=\'false\']"position="attributes"><attributename="groups"/></xpath>',
            'key':'_website_forum.layout',
        })])

    deftest_multiple_inherit_level(self):
        """Testmulti-levelinheritance:
            Base
            |
            --->Extension(Website-specific)
                |
                --->Extension2(Website-specific)
        """
        View=self.env['ir.ui.view']

        self.inherit_view.website_id=1
        inherit_view_2=View.create({
            'name':'Extension2',
            'mode':'extension',
            'inherit_id':self.inherit_view.id,
            'arch':'<divposition="inside">,extendedcontent2</div>',
            'key':'website.extension_view_2',
            'website_id':1,
        })

        total_views=View.search_count([])

        #id|name       |content              |website_id|inherit |key
        #--------------------------------------------------------------------------------------------
        #1 |Base       | basecontent        |    /     |    /   | website.base_view
        #2 |Extension  | ,extendedcontent  |    1     |    1   | website.extension_view
        #3 |Extension2| ,extendedcontent2|    1     |    2   | website.extension_view_2

        self.base_view.with_context(website_id=1).write({'arch':'<div>modifiedcontent</div>'})

        #2viewsarecreated,oneisdeleted
        self.assertEqual(View.search_count([]),total_views+1)
        self.assertFalse(self.inherit_view.exists())
        self.assertTrue(inherit_view_2.exists())

        #Verifytheinheritance
        base_specific=View.search([('key','=',self.base_view.key),('website_id','=',1)]).with_context(load_all_views=True)
        extend_specific=View.search([('key','=','website.extension_view'),('website_id','=',1)])
        self.assertEqual(extend_specific.inherit_id,base_specific)
        self.assertEqual(inherit_view_2.inherit_id,extend_specific)

        #id|name       |content              |website_id|inherit |key
        #--------------------------------------------------------------------------------------------
        #1 |Base       | basecontent        |    /     |    /   | website.base_view
        #4 |Base       | modifiedcontent    |    1     |    /   | website.base_view
        #5 |Extension  | ,extendedcontent  |    1     |    4   | website.extension_view
        #3 |Extension2| ,extendedcontent2|    1     |    5   | website.extension_view_2

    deftest_cow_extension_with_install(self):
        View=self.env['ir.ui.view']
        #Base
        v1=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'<div>basecontent</div>',
            'key':'website.base_view_v1',
        }).with_context(load_all_views=True)
        self._create_imd(v1)

        #Extension
        v2=View.create({
            'name':'Extension',
            'mode':'extension',
            'inherit_id':v1.id,
            'arch':'<divposition="inside"><ooo>extendedcontent</ooo></div>',
            'key':'website.extension_view_v2',
        })
        self._create_imd(v2)

        #multiwebsitespecific
        v1.with_context(website_id=1).write({'name':'ExtensionSpecific'})

        original_pool_init=View.pool._init
        View.pool._init=True

        try:
            #Simulatemoduleinstall
            View._load_records([dict(xml_id='website.extension2_view',values={
                'name':'---',
                'mode':'extension',
                'inherit_id':v1.id,
                'arch':'<oooposition="replace"><p>EXTENSION</p></ooo>',
                'key':'website.extension2_view',
            })])
        finally:
            View.pool._init=original_pool_init

    deftest_specific_view_translation(self):
        Translation=self.env['ir.translation']

        Translation.insert_missing(self.base_view._fields['arch_db'], self.base_view)
        translation=Translation.search([
            ('res_id','=',self.base_view.id),('name','=','ir.ui.view,arch_db')
        ])
        translation.value='hello'
        translation.module='website'

        self.base_view.with_context(website_id=1).write({'active':True})
        specific_view=self.base_view._get_specific_views()-self.base_view

        self.assertEqual(specific_view.with_context(lang='en_US').arch,'<div>hello</div>',
            "copyonwrite(COW)alsocopyexistingtranslations")

        translation.value='hi'
        self.assertEqual(specific_view.with_context(lang='en_US').arch,'<div>hello</div>',
            "updatingtranslationofbaseviewdoesn'tupdatespecificview")

        Translation._load_module_terms(['website'],['en_US'],overwrite=True)

        specific_view.invalidate_cache(['arch_db','arch'])
        self.assertEqual(specific_view.with_context(lang='en_US').arch,'<div>hi</div>',
            "loadingmoduletranslationcopytranslationfrombasetospecificview")

    deftest_specific_view_module_update_inherit_change(self):
        """Duringamoduleupdate,ifinherit_idischanged,weneedto
        replicatethechangeforcowviews."""
        #IfD.inherit_idbecomesBinsteadofA,aftermoduleupdate,weexpect:
        #CASE1
        #  A   A'  B                     A   A'  B
        #  |   |                =>                /\
        #  D   D'                                 D  D'
        #
        #CASE2
        #  A   A'  B   B'              A   A'  B  B'
        #  |   |                =>                |  |
        #  D   D'                                  D  D'
        #
        #CASE3
        #    A   B                       A   B
        #   /\                  =>          /\
        #  D  D'                            D  D'
        #
        #CASE4
        #    A   B   B'                 A   B  B'
        #   /\                  =>           |  |
        #  D  D'                              D  D'

        #1.Setupfollowingviewtrees
        #  A   A'  B
        #  |   |
        #  D   D'
        View=self.env['ir.ui.view']
        Website=self.env['website']
        self._create_imd(self.inherit_view)
        #invalidatecachetorecomputexml_id,oritwillstillbeempty
        self.inherit_view.invalidate_cache()
        base_view_2=self.base_view.copy({'key':'website.base_view2','arch':'<div>base2content</div>'})
        self.base_view.with_context(website_id=1).write({'arch':'<div>website1content</div>'})
        specific_view=Website.with_context(load_all_views=True,website_id=1).viewref(self.base_view.key)
        specific_view.inherit_children_ids.with_context(website_id=1).write({'arch':'<divposition="inside">,extendedcontentwebsite1</div>'})
        specific_child_view=Website.with_context(load_all_views=True,website_id=1).viewref(self.inherit_view.key)
        #2.Ensureviewtreesareasexpected
        self.assertEqual(self.base_view.inherit_children_ids,self.inherit_view,"DshouldbeunderA")
        self.assertEqual(specific_view.inherit_children_ids,specific_child_view,"D'shouldbeunderA'")
        self.assertFalse(base_view_2.inherit_children_ids,"Bshouldhavenochild")

        #3.Simulatemoduleupdate,D.inherit_idisnowBinsteadofA
        View._load_records([dict(xml_id=self.inherit_view.key,values={
            'inherit_id':base_view_2.id,
        })])

        #4.Ensureviewtreesisnow
        #  A   A'  B
        #           /\
        #          D  D'
        self.assertTrue(len(self.base_view.inherit_children_ids)==len(specific_view.inherit_children_ids)==0,
                        "ChildviewsshouldnowbeunderviewB")
        self.assertEqual(len(base_view_2.inherit_children_ids),2,"DandD'shouldbeunderB")
        self.assertTrue(self.inherit_viewinbase_view_2.inherit_children_ids,"DshouldbeunderB")
        self.assertTrue(specific_child_viewinbase_view_2.inherit_children_ids,"D'shouldbeunderB")


@tagged('-at_install','post_install')
classCrawler(HttpCase):
    defsetUp(self):
        super(Crawler,self).setUp()
        View=self.env['ir.ui.view']

        self.base_view=View.create({
            'name':'Base',
            'type':'qweb',
            'arch':'<div>basecontent</div>',
            'key':'website.base_view',
        }).with_context(load_all_views=True)

        self.inherit_view=View.create({
            'name':'Extension',
            'mode':'extension',
            'inherit_id':self.base_view.id,
            'arch':'<divposition="inside">,extendedcontent</div>',
            'key':'website.extension_view',
        })

    deftest_get_switchable_related_views(self):
        View=self.env['ir.ui.view']
        Website=self.env['website']

        #Setup
        website_1=Website.create({'name':'Website1'}) #willhavespecificviews
        website_2=Website.create({'name':'Website2'}) #willusegenericviews

        self.base_view.write({'name':'MainFrontendLayout','key':'_portal.frontend_layout'})
        event_main_view=self.base_view.copy({
            'name':'Events',
            'key':'_website_event.index',
            'arch':'<tt-call="_website.layout"><div>Archisnotimportantinthistest</div></t>',
        })
        self.inherit_view.write({'name':'Mainlayout','key':'_website.layout'})

        self.inherit_view.copy({'name':'SignIn','customize_show':True,'key':'_portal.user_sign_in'})
        view_logo=self.inherit_view.copy({
            'name':'ShowLogo',
            'inherit_id':self.inherit_view.id,
            'customize_show':True,
            'key':'_website.layout_logo_show',
        })
        view_logo.copy({'name':'AffixTopMenu','key':'_website.affix_top_menu'})

        event_child_view=self.inherit_view.copy({
            'name':'Filters',
            'customize_show':True,
            'inherit_id':event_main_view.id,
            'key':'_website_event.event_left_column',
            'priority':30,
        })
        view_photos=event_child_view.copy({'name':'Photos','key':'_website_event.event_right_photos'})
        event_child_view.copy({'name':'Quotes','key':'_website_event.event_right_quotes','priority':30})

        event_child_view.copy({'name':'FilterbyCategory','inherit_id':event_child_view.id,'key':'_website_event.event_category'})
        event_child_view.copy({'name':'FilterbyCountry','inherit_id':event_child_view.id,'key':'_website_event.event_location'})

        View.flush()

        #Customize
        #  |MainFrontendLayout
        #      |ShowSignIn
        #  |MainLayout
        #      |AffixTopMenu
        #      |ShowLogo
        #  |Events
        #      |Filters
        #      |Photos
        #      |Quotes
        #  |Filters
        #      |FilterByCategory
        #      |FilterByCountry

        self.authenticate("admin","admin")
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        #Simulatewebsite2(thatuseonlygenericviews)
        self.url_open(base_url+'/website/force/%s'%website_2.id)

        #Testcontroller
        url=base_url+'/website/get_switchable_related_views'
        json={'params':{'key':'_website_event.index'}}
        response=self.opener.post(url=url,json=json)
        res=response.json()['result']

        self.assertEqual(
            [v['name']forvinres],
            ['SignIn','AffixTopMenu','ShowLogo','Filters','Photos','Quotes','FilterbyCategory','FilterbyCountry'],
            "Sequenceshouldnotbetakenintoaccountforcustomizemenu",
        )
        self.assertEqual(
            [v['inherit_id'][1]forvinres],
            ['MainFrontendLayout','Mainlayout','Mainlayout','Events','Events','Events','Filters','Filters'],
            "Sequenceshouldnotbetakenintoaccountforcustomizemenu(CheckingCustomizeheaders)",
        )

        #TriggerCOW
        view_logo.with_context(website_id=website_1.id).write({'arch':'<divposition="inside">,triggerCOW,archisnotrelevantinthistest</div>'})
        #Thiswouldwronglybecome:

        #Customize
        #  |MainFrontendLayout
        #      |ShowSignIn
        #  |MainLayout
        #      |AffixTopMenu
        #      |ShowLogo<====Wasabove"AffixTopMenu"
        #  |Events
        #      |Filters
        #      |Photos
        #      |Quotes
        #  |Filters
        #      |FilterByCategory
        #      |FilterByCountry

        #Simulatewebsite1(thathasspecificviews)
        self.url_open(base_url+'/website/force/%s'%website_1.id)

        #Testcontroller
        url=base_url+'/website/get_switchable_related_views'
        json={'params':{'key':'_website_event.index'}}
        response=self.opener.post(url=url,json=json)
        res=response.json()['result']
        self.assertEqual(
            [v['name']forvinres],
            ['SignIn','AffixTopMenu','ShowLogo','Filters','Photos','Quotes','FilterbyCategory','FilterbyCountry'],
            "multi-websiteCOWshouldnotimpactcustomizeviewsorder(COWviewwillhaveabiggerIDandshouldnotbelast)",
        )
        self.assertEqual(
            [v['inherit_id'][1]forvinres],
            ['MainFrontendLayout','Mainlayout','Mainlayout','Events','Events','Events','Filters','Filters'],
            "multi-websiteCOWshouldnotimpactcustomizeviewsmenuheaderpositionorsplit(COWviewwillhaveabiggerIDandshouldnotbelast)",
        )

        #TriggerCOW
        view_photos.with_context(website_id=website_1.id).write({'arch':'<divposition="inside">,triggerCOW,archisnotrelevantinthistest</div>'})
        #Thiswouldwronglybecome:

        #Customize
        #  |MainFrontendLayout
        #      |ShowSignIn
        #  |MainLayout
        #      |AffixTopMenu
        #      |ShowLogo
        #  |Events
        #      |Filters
        #      |Quotes
        #  |Filters
        #      |FilterByCategory
        #      |FilterByCountry
        #  |Events    <====JScodecreatesanewEventsheaderastheEvent'schildrenviewsarenotoneaftertheotheranymore..
        #      |Photos<====..sincePhotosgotduplicatedandnowhaveabiggerIDthatothers

        #Testcontroller
        url=base_url+'/website/get_switchable_related_views'
        json={'params':{'key':'_website_event.index'}}
        response=self.opener.post(url=url,json=json)
        res=response.json()['result']
        self.assertEqual(
            [v['name']forvinres],
            ['SignIn','AffixTopMenu','ShowLogo','Filters','Photos','Quotes','FilterbyCategory','FilterbyCountry'],
            "multi-websiteCOWshouldnotimpactcustomizeviewsorder(COWviewwillhaveabiggerIDandshouldnotbelast)(2)",
        )
        self.assertEqual(
            [v['inherit_id'][1]forvinres],
            ['MainFrontendLayout','Mainlayout','Mainlayout','Events','Events','Events','Filters','Filters'],
            "multi-websiteCOWshouldnotimpactcustomizeviewsmenuheaderpositionorsplit(COWviewwillhaveabiggerIDandshouldnotbelast)(2)",
        )

    deftest_multi_website_views_retrieving(self):
        View=self.env['ir.ui.view']
        Website=self.env['website']

        website_1=Website.create({'name':'Website1'})
        website_2=Website.create({'name':'Website2'})

        main_view=View.create({
            'name':'Products',
            'type':'qweb',
            'arch':'<body>Archisnotrelevantforthistest</body>',
            'key':'_website_sale.products',
        }).with_context(load_all_views=True)

        View.with_context(load_all_views=True).create({
            'name':'ChildViewW1',
            'mode':'extension',
            'inherit_id':main_view.id,
            'arch':'<xpathexpr="//body"position="replace">Itisreallynotrelevant!</xpath>',
            'key':'_website_sale.child_view_w1',
            'website_id':website_1.id,
            'active':False,
            'customize_show':True,
        })

        #Simulatethemeviewinstal+loadonwebsite
        theme_view=self.env['theme.ir.ui.view'].with_context(install_filename='/testviews').create({
            'name':'ProductsThemeKea',
            'mode':'extension',
            'inherit_id':main_view,
            'arch':'<xpathexpr="//p"position="replace"><span>C</span></xpath>',
            'key':'_theme_kea_sale.products',
        })
        view_from_theme_view_on_w2=View.with_context(load_all_views=True).create({
            'name':'ProductsThemeKea',
            'mode':'extension',
            'inherit_id':main_view.id,
            'arch':'<xpathexpr="//body"position="replace">Reallyreallynotimportantforthistest</xpath>',
            'key':'_theme_kea_sale.products',
            'website_id':website_2.id,
            'customize_show':True,
        })
        self.env['ir.model.data'].create({
            'module':'_theme_kea_sale',
            'name':'products',
            'model':'theme.ir.ui.view',
            'res_id':theme_view.id,
        })

        ######################################################ir.ui.view###############################################
        #id|       name       |website_id|inherit|            key              |         xml_id              |
        #----------------------------------------------------------------------------------------------------------------
        # 1|Products          |     /    |   /   |_website_sale.products       |           /                 |
        # 2|ChildViewW1     |     1    |   1   |_website_sale.child_view_w1  |           /                 |
        # 3|ProductsThemeKea|     2    |   1   |_theme_kea_sale.products     |           /                 |

        ##################################################theme.ir.ui.view#############################################
        #id|              name             |inherit|            key              |        xml_id               |
        #----------------------------------------------------------------------------------------------------------------
        # 1|ProductsThemeKea             |   1   |_theme_kea_sale.products     |_theme_kea_sale.products     |

        withself.assertRaises(ValueError):
            #Itshouldcrashasitshouldnotfindaviewonwebsite1for'_theme_kea_sale.products',!!andcertainlynotatheme.ir.ui.view!!.
            view=View.with_context(website_id=website_1.id)._view_obj('_theme_kea_sale.products')
        view=View.with_context(website_id=website_2.id)._view_obj('_theme_kea_sale.products')
        self.assertEqual(len(view),1,"Itshouldfindtheir.ui.viewwithkey'_theme_kea_sale.products'onwebsite2..")
        self.assertEqual(view._name,'ir.ui.view',"..andnotatheme.ir.ui.view")

        views=View.with_context(website_id=website_1.id).get_related_views('_website_sale.products')
        self.assertEqual(len(views),2,"Itshouldnotmixapplesandoranges,onlyir.ui.view['_website_sale.products','_website_sale.child_view_w1']shouldbereturned")
        views=View.with_context(website_id=website_2.id).get_related_views('_website_sale.products')
        self.assertEqual(len(views),2,"Itshouldnotmixapplesandoranges,onlyir.ui.view['_website_sale.products','_theme_kea_sale.products']shouldbereturned")

        #Part2ofthetest,ittestthesamestuffbutfromahigherlevel(get_related_viewsendsupcalling_view_obj)
        called_theme_view=self.env['theme.ir.ui.view'].with_context(install_filename='/testviews').create({
            'name':'CalledViewKea',
            'arch':'<div></div>',
            'key':'_theme_kea_sale.t_called_view',
        })
        View.create({
            'name':'CalledViewKea',
            'type':'qweb',
            'arch':'<div></div>',
            'key':'_theme_kea_sale.t_called_view',
            'website_id':website_2.id,
        }).with_context(load_all_views=True)
        self.env['ir.model.data'].create({
            'module':'_theme_kea_sale',
            'name':'t_called_view',
            'model':'theme.ir.ui.view',
            'res_id':called_theme_view.id,
        })
        view_from_theme_view_on_w2.write({'arch':'<tt-call="_theme_kea_sale.t_called_view"/>'})

        ######################################################ir.ui.view###############################################
        #id|       name       |website_id|inherit|            key              |         xml_id              |
        #----------------------------------------------------------------------------------------------------------------
        # 1|Products          |     /    |   /   |_website_sale.products       |           /                 |
        # 2|ChildViewW1     |     1    |   1   |_website_sale.child_view_w1  |           /                 |
        # 3|ProductsThemeKea|     2    |   1   |_theme_kea_sale.products     |           /                 |
        # 4|CalledViewKea   |     2    |   /   |_theme_kea_sale.t_called_view|           /                 |

        ##################################################theme.ir.ui.view#############################################
        #id|              name             |inherit|            key              |        xml_id               |
        #----------------------------------------------------------------------------------------------------------------
        # 1|ProductsThemeKea             |   1   |_theme_kea_sale.products     |_theme_kea_sale.products     |
        # 1|CalledViewKea                |   /   |_theme_kea_sale.t_called_view|_theme_kea_sale.t_called_view|

        #Nextlineshouldnotcrash(wasmixingapplesandoranges-ir.ui.viewandtheme.ir.ui.view)
        views=View.with_context(website_id=website_1.id).get_related_views('_website_sale.products')
        self.assertEqual(len(views),2,"Itshouldnotmixapplesandoranges,onlyir.ui.view['_website_sale.products','_website_sale.child_view_w1']shouldbereturned(2)")
        views=View.with_context(website_id=website_2.id).get_related_views('_website_sale.products')
        self.assertEqual(len(views),3,"Itshouldnotmixapplesandoranges,onlyir.ui.view['_website_sale.products','_theme_kea_sale.products','_theme_kea_sale.t_called_view']shouldbereturned")

        #########################################################
        #Testthecontroller(whichiscallingget_related_views)
        self.authenticate("admin","admin")
        base_url=self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        #Simulatewebsite2
        self.url_open(base_url+'/website/force/%s'%website_2.id)

        #Testcontroller
        url=base_url+'/website/get_switchable_related_views'
        json={'params':{'key':'_website_sale.products'}}
        response=self.opener.post(url=url,json=json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()['result']),1,"Only'_theme_kea_sale.products'shouldbereturnedasitistheonlycustomize_showrelatedviewinwebsite2context")
        self.assertEqual(response.json()['result'][0]['key'],'_theme_kea_sale.products',"Only'_theme_kea_sale.products'shouldbereturned")

        #Simulatewebsite1
        self.url_open(base_url+'/website/force/%s'%website_1.id)

        #Testcontroller
        url=base_url+'/website/get_switchable_related_views'
        json={'params':{'key':'_website_sale.products'}}
        response=self.opener.post(url=url,json=json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json()['result']),1,"Only'_website_sale.child_view_w1'shouldbereturnedasitistheonlycustomize_showrelatedviewinwebsite1context")
        self.assertEqual(response.json()['result'][0]['key'],'_website_sale.child_view_w1',"Only'_website_sale.child_view_w1'shouldbereturned")


@tagged('post_install','-at_install')
classTestThemeViews(common.TransactionCase):
    deftest_inherit_specific(self):
        View=self.env['ir.ui.view']
        Website=self.env['website']

        website_1=Website.create({'name':'Website1'})

        #1.SimulateCOWstructure
        main_view=View.create({
            'name':'TestMainView',
            'type':'qweb',
            'arch':'<body>Archisnotrelevantforthistest</body>',
            'key':'_test.main_view',
        }).with_context(load_all_views=True)
        #TriggerCOW
        main_view.with_context(website_id=website_1.id).arch='<body>specific</body>'

        #2.Simulateathemeinstallwithachildviewof`main_view`
        test_theme_module=self.env['ir.module.module'].create({'name':'test_theme'})
        self.env['ir.model.data'].create({
            'module':'base',
            'name':'module_test_theme_module',
            'model':'ir.module.module',
            'res_id':test_theme_module.id,
        })
        theme_view=self.env['theme.ir.ui.view'].with_context(install_filename='/testviews').create({
            'name':'TestChildView',
            'mode':'extension',
            'inherit_id':'ir.ui.view,%s'%main_view.id,
            'arch':'<xpathexpr="//body"position="replace"><span>C</span></xpath>',
            'key':'test_theme.test_child_view',
        })
        self.env['ir.model.data'].create({
            'module':'test_theme',
            'name':'products',
            'model':'theme.ir.ui.view',
            'res_id':theme_view.id,
        })
        test_theme_module.with_context(load_all_views=True)._theme_load(website_1)

        #3.Ensureeverythingwentcorrectly
        main_views=View.search([('key','=','_test.main_view')])
        self.assertEqual(len(main_views),2,"ViewshouldhavebeenCOWdwhenwritingonitsarchinawebsitecontext")
        specific_main_view=main_views.filtered(lambdav:v.website_id==website_1)
        specific_main_view_children=specific_main_view.inherit_children_ids
        self.assertEqual(specific_main_view_children.name,'TestChildView',"Ensuretheme.ir.ui.viewhasbeenloadedasanir.ui.viewintothewebsite..")
        self.assertEqual(specific_main_view_children.website_id,website_1,"..andthewebsiteisthecorrectone.")

        #4.Simulatethemeupdate.Doit2timetomakesureitwasnotinterpretedasauserchangethefirsttime.
        new_arch='<xpathexpr="//body"position="replace"><span>FlectraChange01</span></xpath>'
        theme_view.arch=new_arch
        test_theme_module.with_context(load_all_views=True)._theme_load(website_1)
        self.assertEqual(specific_main_view_children.arch,new_arch,"Firsttime:Viewarchshouldreceivethemeupdates.")
        self.assertFalse(specific_main_view_children.arch_updated)
        new_arch='<xpathexpr="//body"position="replace"><span>FlectraChange02</span></xpath>'
        theme_view.arch=new_arch
        test_theme_module.with_context(load_all_views=True)._theme_load(website_1)
        self.assertEqual(specific_main_view_children.arch,new_arch,"Secondtime:Viewarchshouldstillreceivethemeupdates.")

        #5.KeepUserarchchanges
        new_arch='<xpathexpr="//body"position="replace"><span>Flectra</span></xpath>'
        specific_main_view_children.arch=new_arch
        theme_view.name='TestChildViewmodified'
        test_theme_module.with_context(load_all_views=True)._theme_load(website_1)
        self.assertEqual(specific_main_view_children.arch,new_arch,"Viewarchshouldn'thavebeenoverridedonthemeupdateasitwasmodifiedbyuser.")
        self.assertEqual(specific_main_view_children.name,'TestChildViewmodified',"Viewshouldreceivemodificationonthemeupdate.")
