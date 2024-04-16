#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importrandom
importre
fromunittest.mockimportpatch
importtextwrap
fromdatetimeimportdatetime,timedelta
fromlxmlimportetree
importlogging

fromflectra.tests.commonimportBaseCase,tagged
fromflectra.toolsimporttopological_sort
fromflectra.addons.web.controllers.mainimportHomeStaticTemplateHelpers

_logger=logging.getLogger(__name__)

defsample(population):
    returnrandom.sample(
        population,
            random.randint(0,min(len(population),5)))


classTestModulesLoading(BaseCase):
    defsetUp(self):
        self.mods=[str(i)foriinrange(1000)]

    deftest_topological_sort(self):
        random.shuffle(self.mods)
        modules=[
            (k,sample(self.mods[:i]))
            fori,kinenumerate(self.mods)]
        random.shuffle(modules)
        ms=dict(modules)

        seen=set()
        sorted_modules=topological_sort(ms)
        formoduleinsorted_modules:
            deps=ms[module]
            self.assertGreaterEqual(
                seen,set(deps),
                        'Module%s(index%d),'\
                        'missingdependencies%sfromloadedmodules%s'%(
                    module,sorted_modules.index(module),deps,seen
                ))
            seen.add(module)


classTestStaticInheritanceCommon(BaseCase):

    defsetUp(self):
        super(TestStaticInheritanceCommon,self).setUp()
        #outputis"manifest_glob"return
        self.modules=[
            ('module_1_file_1',None,'module_1'),
            ('module_2_file_1',None,'module_2'),
        ]

        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                        <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    </form>
                    <tt-name="template_1_2">
                        <div>AndIgrewstrong</div>
                    </t>
                </templates>
                """,

            'module_2_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_2_1"t-inherit="module_1.template_1_1"t-inherit-mode="primary">
                        <xpathexpr="//div[1]"position="after">
                            <div>Iwaspetrified</div>
                        </xpath>
                        <xpathexpr="//div[2]"position="after">
                            <div>ButthenIspentsomanynightsthinkinghowyoudidmewrong</div>
                        </xpath>
                    </form>
                    <divt-name="template_2_2">
                        <div>AndIlearnedhowtogetalong</div>
                    </div>
                    <formt-inherit="module_1.template_1_2"t-inherit-mode="extension">
                        <xpathexpr="//div[1]"position="after">
                            <div>AndIlearnedhowtogetalong</div>
                        </xpath>
                    </form>
                </templates>
                """,
        }
        self._set_patchers()
        self._toggle_patchers('start')
        self._reg_replace_ws=r"\s|\t"

    deftearDown(self):
        super(TestStaticInheritanceCommon,self).tearDown()
        self._toggle_patchers('stop')

    #CustomAssert
    defassertXMLEqual(self,output,expected):
        self.assertTrue(output)
        self.assertTrue(expected)
        output=textwrap.dedent(output.decode('UTF-8')).strip()
        output=re.sub(self._reg_replace_ws,'',output)

        expected=textwrap.dedent(expected.decode('UTF-8')).strip()
        expected=re.sub(self._reg_replace_ws,'',expected)
        self.assertEqual(output,expected)

    #Privatemethods
    def_get_module_names(self):
        return','.join([glob[2]forglobinself.modules])

    def_set_patchers(self):
        def_patched_for_manifest_glob(*args,**kwargs):
            #Orderedbymodule
            returnself.modules

        def_patch_for_read_addon_file(*args,**kwargs):
            returnself.template_files[args[1]]

        self.patchers=[
            patch.object(HomeStaticTemplateHelpers,'_manifest_glob',_patched_for_manifest_glob),
            patch.object(HomeStaticTemplateHelpers,'_read_addon_file',_patch_for_read_addon_file),
        ]

    def_toggle_patchers(self,mode):
        self.assertTrue(modein('start','stop'))
        forpinself.patchers:
            getattr(p,mode)()


@tagged('static_templates')
classTestStaticInheritance(TestStaticInheritanceCommon):
    #Actualtestcases
    deftest_static_inheritance_01(self):
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <tt-name="template_1_2">
                    <div>AndIgrewstrong</div>
                    <!--Modifiedbyanonymous_template_2frommodule_2-->
                    <div>AndIlearnedhowtogetalong</div>
                </t>
                <formt-name="template_2_1"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                    <div>Iwaspetrified</div>
                    <div>ButthenIspentsomanynightsthinkinghowyoudidmewrong</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <divt-name="template_2_2">
                    <div>AndIlearnedhowtogetalong</div>
                </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_static_inheritance_02(self):
        self.template_files={
            'module_1_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                        <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    </form>
                    <formt-name="template_1_2"t-inherit="template_1_1"added="true">
                        <xpathexpr="//div[1]"position="after">
                            <div>Iwaspetrified</div>
                        </xpath>
                    </form>
                </templates>
            '''
        }
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <formt-name="template_1_2"random-attr="gloria"added="true">
                    <div>AtfirstIwasafraid</div>
                    <div>Iwaspetrified</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_static_inheritance_03(self):
        self.maxDiff=None
        self.template_files={
            'module_1_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1">
                        <div>AtfirstIwasafraid</div>
                        <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    </form>
                    <formt-name="template_1_2"t-inherit="template_1_1"added="true">
                        <xpathexpr="//div[1]"position="after">
                            <div>Iwaspetrified</div>
                        </xpath>
                    </form>
                    <formt-name="template_1_3"t-inherit="template_1_2"added="false"other="here">
                        <xpathexpr="//div[2]"position="replace"/>
                    </form>
                </templates>
            '''
        }
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1">
                    <div>AtfirstIwasafraid</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <formt-name="template_1_2"added="true">
                    <div>AtfirstIwasafraid</div>
                    <div>Iwaspetrified</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <formt-name="template_1_3"added="false"other="here">
                    <div>AtfirstIwasafraid</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_static_inheritance_in_same_module(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
            ('module_1_file_2',None,'module_1'),
        ]

        self.template_files={
            'module_1_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1">
                        <div>AtfirstIwasafraid</div>
                        <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    </form>
                </templates>
            ''',

            'module_1_file_2':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="primary">
                        <xpathexpr="//div[1]"position="after">
                            <div>Iwaspetrified</div>
                        </xpath>
                    </form>
                </templates>
            '''
        }
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1">
                    <div>AtfirstIwasafraid</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <formt-name="template_1_2">
                    <div>AtfirstIwasafraid</div>
                    <div>Iwaspetrified</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_static_inheritance_in_same_file(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]

        self.template_files={
            'module_1_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1">
                        <div>AtfirstIwasafraid</div>
                        <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    </form>
                    <formt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="primary">
                        <xpathexpr="//div[1]"position="after">
                            <div>Iwaspetrified</div>
                        </xpath>
                    </form>
                </templates>
            ''',
        }
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1">
                    <div>AtfirstIwasafraid</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <formt-name="template_1_2">
                    <div>AtfirstIwasafraid</div>
                    <div>Iwaspetrified</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_static_inherit_extended_template(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1">
                        <div>AtfirstIwasafraid</div>
                        <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    </form>
                    <formt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="extension">
                        <xpathexpr="//div[1]"position="after">
                            <div>Iwaspetrified</div>
                        </xpath>
                    </form>
                    <formt-name="template_1_3"t-inherit="template_1_1"t-inherit-mode="primary">
                        <xpathexpr="//div[3]"position="after">
                            <div>ButthenIspentsomanynightsthinkinghowyoudidmewrong</div>
                        </xpath>
                    </form>
                </templates>
            ''',
        }
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1">
                    <div>AtfirstIwasafraid</div>
                    <!--Modifiedbytemplate_1_2frommodule_1-->
                    <div>Iwaspetrified</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                </form>
                <formt-name="template_1_3">
                    <div>AtfirstIwasafraid</div>
                    <div>Iwaspetrified</div>
                    <div>KeptthinkingIcouldneverlivewithoutyoubymyside</div>
                    <div>ButthenIspentsomanynightsthinkinghowyoudidmewrong</div>
                </form>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_sibling_extension(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
            ('module_2_file_1',None,'module_2'),
            ('module_3_file_1',None,'module_3'),
        ]
        self.template_files={
            'module_1_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1">
                        <div>Iamamanofconstantsorrow</div>
                        <div>I'veseentroubleallmydays</div>
                    </form>
                </templates>
            ''',

            'module_2_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_2_1"t-inherit="module_1.template_1_1"t-inherit-mode="extension">
                        <xpathexpr="//div[1]"position="after">
                            <div>Inconstantsorrowallthroughhisdays</div>
                        </xpath>
                    </form>
                </templates>
            ''',

            'module_3_file_1':b'''
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_3_1"t-inherit="module_1.template_1_1"t-inherit-mode="extension">
                        <xpathexpr="//div[2]"position="after">
                            <div>OhBrother!</div>
                        </xpath>
                    </form>
                </templates>
            '''
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1">
                    <div>Iamamanofconstantsorrow</div>
                    <!--Modifiedbytemplate_2_1frommodule_2-->
                    <div>Inconstantsorrowallthroughhisdays</div>
                    <!--Modifiedbytemplate_3_1frommodule_3-->
                    <div>OhBrother!</div>
                    <div>I'veseentroubleallmydays</div>
                </form>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_static_misordered_modules(self):
        self.modules.reverse()
        withself.assertRaises(ValueError)asve:
            HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)

        self.assertEqual(
            str(ve.exception),
            'Modulemodule_1notloadedorinexistent,ortemplatesofaddonbeingloaded(module_2)aremisordered'
        )

    deftest_static_misordered_templates(self):
        self.template_files['module_2_file_1']=b"""
            <templatesid="template"xml:space="preserve">
                <formt-name="template_2_1"t-inherit="module_2.template_2_2"t-inherit-mode="primary">
                    <xpathexpr="//div[1]"position="after">
                        <div>Iwaspetrified</div>
                    </xpath>
                </form>
                <divt-name="template_2_2">
                    <div>AndIlearnedhowtogetalong</div>
                </div>
            </templates>
        """
        withself.assertRaises(ValueError)asve:
            HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)

        self.assertEqual(
            str(ve.exception),
            'Notemplatefoundtoinheritfrom.Modulemodule_2andtemplatenametemplate_2_2'
        )

    deftest_replace_in_debug_mode(self):
        """
        Replacingatemplate'smetadefinitioninplacedoesn'tkeeptheoriginalattrsofthetemplate
        """
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="extension">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">AndIgrewstrong</div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <divoverriden-attr="overriden"t-name="template_1_1">
                    <!--Modifiedbytemplate_1_2frommodule_1-->AndIgrewstrong
                </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_replace_in_debug_mode2(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="extension">
                        <xpathexpr="."position="replace">
                            <div>
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                                Andsoyou'reback
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <divt-name="template_1_1">
                    <!--Modifiedbytemplate_1_2frommodule_1-->
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                    Andsoyou'reback
                </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_replace_in_debug_mode3(self):
        """Textoutsideofadivwhichwillreplaceawholetemplate
        becomesoutsideofthetemplate
        Thisdoesn'tmeananythingintermsofthebusinessoftemplateinheritance
        ButitisintheXPATHspecs"""
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="extension">
                        <xpathexpr="."position="replace">
                            <div>
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                            Andsoyou'reback
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <divt-name="template_1_1">
                    <!--Modifiedbytemplate_1_2frommodule_1-->
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                </div>
                Andsoyou'reback
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_replace_root_node_tag(self):
        """
        RootnodeIStargetedby//NODE_TAGinxpath
        """
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                        <form>InnerForm</form>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="extension">
                        <xpathexpr="//form"position="replace">
                            <div>
                                Formreplacer
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <divt-name="template_1_1">
                    <!--Modifiedbytemplate_1_2frommodule_1-->
                    Formreplacer
                </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_replace_root_node_tag_in_primary(self):
        """
        RootnodeIStargetedby//NODE_TAGinxpath
        """
        self.maxDiff=None
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                        <form>InnerForm</form>
                    </form>
                    <formt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="primary">
                        <xpathexpr="//form"position="replace">
                            <div>Formreplacer</div>
                        </xpath>
                    </form>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                    <form>InnerForm</form>
                </form>
                <divt-name="template_1_2">
                    Formreplacer
                </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_inherit_primary_replace_debug(self):
        """
        Theinheritingtemplatehasgotbothitsowndefiningattrs
        andnewonesifoneistoreplaceitsdefiningrootnode
        """
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="primary">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                 </form>
                 <divoverriden-attr="overriden"t-name="template_1_2">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                 </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_replace_in_nodebug_mode1(self):
        """Commentsalreadyinthearchareignored"""
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1"t-inherit-mode="extension">
                        <xpathexpr="."position="replace">
                            <div>
                                <!--RandomComment-->
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                                Andsoyou'reback
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=False)
        expected=b"""
            <templates>
                <divt-name="template_1_1">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                    Andsoyou'reback
                </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_inherit_from_dotted_tname_1(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="module_1.template_1_1.dot"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1.dot"t-inherit-mode="primary">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="module_1.template_1_1.dot"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                 </form>
                 <divoverriden-attr="overriden"t-name="template_1_2">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                 </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_inherit_from_dotted_tname_2(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1.dot"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="template_1_1.dot"t-inherit-mode="primary">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1.dot"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                 </form>
                 <divoverriden-attr="overriden"t-name="template_1_2">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                 </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_inherit_from_dotted_tname_2bis(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="template_1_1.dot"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="module_1.template_1_1.dot"t-inherit-mode="primary">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="template_1_1.dot"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                 </form>
                 <divoverriden-attr="overriden"t-name="template_1_2">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                 </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_inherit_from_dotted_tname_2ter(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="module_1"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                    <tt-name="template_1_2"t-inherit="module_1"t-inherit-mode="primary">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                        </xpath>
                    </t>
                </templates>
                """,
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="module_1"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                 </form>
                 <divoverriden-attr="overriden"t-name="template_1_2">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                 </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)

    deftest_inherit_from_dotted_tname_3(self):
        self.modules=[
            ('module_1_file_1',None,'module_1'),
            ('module_2_file_1',None,'module_2'),
        ]
        self.template_files={
            'module_1_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <formt-name="module_1.template_1_1.dot"random-attr="gloria">
                        <div>AtfirstIwasafraid</div>
                    </form>
                </templates>
                """,

            'module_2_file_1':b"""
                <templatesid="template"xml:space="preserve">
                    <tt-name="template_2_1"t-inherit="module_1.template_1_1.dot"t-inherit-mode="primary">
                        <xpathexpr="."position="replace">
                            <divoverriden-attr="overriden">
                                AndIgrewstrong
                                <p>AndIlearnedhowtogetalong</p>
                            </div>
                        </xpath>
                    </t>
                </templates>
            """
        }

        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        expected=b"""
            <templates>
                <formt-name="module_1.template_1_1.dot"random-attr="gloria">
                    <div>AtfirstIwasafraid</div>
                 </form>
                 <divoverriden-attr="overriden"t-name="template_2_1">
                    AndIgrewstrong
                    <p>AndIlearnedhowtogetalong</p>
                 </div>
            </templates>
        """

        self.assertXMLEqual(contents,expected)


@tagged('-standard','static_templates_performance')
classTestStaticInheritancePerformance(TestStaticInheritanceCommon):
    def_sick_script(self,nMod,nFilePerMod,nTemplatePerFile,stepInheritInModule=2,stepInheritPreviousModule=3):
        """
        Makeasickamountoftemplatestotestperf
        nModmodules
        eachmodule:hasnFilesPerModulefiles,eachofwhichcontainsnTemplatePerFiletemplates
        """
        self.modules=[]
        self.template_files={}
        number_templates=0
        forminrange(nMod):
            forfinrange(nFilePerMod):
                mname='mod_%s'%m
                fname='mod_%s_file_%s'%(m,f)
                self.modules.append((fname,None,mname))

                _file='<templatesid="template"xml:space="preserve">'

                fortinrange(nTemplatePerFile):
                    _template=''
                    ift%stepInheritInModuleort%stepInheritPreviousModuleort==0:
                        _template+="""
                            <divt-name="template_%(t_number)s_mod_%(m_number)s">
                                <div>Parent</div>
                            </div>
                        """

                    elifnott%stepInheritInModuleandt>=1:
                        _template+="""
                            <divt-name="template_%(t_number)s_mod_%(m_number)s"
                                t-inherit="template_%(t_inherit)s_mod_%(m_number)s"
                                t-inherit-mode="primary">
                                <xpathexpr="/div/div[1]"position="before">
                                    <div>SickXPath</div>
                                </xpath>
                            </div>
                        """

                    elifnott%stepInheritPreviousModuleandm>=1:
                        _template+="""
                            <divt-name="template_%(t_number)s_mod_%(m_number)s"
                                t-inherit="mod_%(m_module_inherit)s.template_%(t_module_inherit)s_mod_%(m_module_inherit)s"
                                t-inherit-mode="primary">
                                <xpathexpr="/div/div[1]"position="inside">
                                    <div>MentalXPath</div>
                                </xpath>
                            </div>
                        """
                    if_template:
                        number_templates+=1

                    _template_number=1000*f+t
                    _file+=_template%{
                        't_number':_template_number,
                        'm_number':m,
                        't_inherit':_template_number-1,
                        't_module_inherit':_template_number,
                        'm_module_inherit':m-1,
                    }
                _file+='</templates>'

                self.template_files[fname]=_file.encode()
        self.assertEqual(number_templates,nMod*nFilePerMod*nTemplatePerFile)

    deftest_static_templates_treatment_linearity(self):
        #With2500templatesforstarters
        nMod,nFilePerMod,nTemplatePerFile=50,5,10
        self._sick_script(nMod,nFilePerMod,nTemplatePerFile)

        before=datetime.now()
        contents=HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        after=datetime.now()
        delta2500=after-before
        _logger.runbot('StaticTemplatesInheritance:2500templatestreatedin%sseconds'%delta2500.total_seconds())

        whole_tree=etree.fromstring(contents)
        self.assertEqual(len(whole_tree),nMod*nFilePerMod*nTemplatePerFile)

        #With25000templatesnext
        nMod,nFilePerMod,nTemplatePerFile=50,5,100
        self._sick_script(nMod,nFilePerMod,nTemplatePerFile)

        before=datetime.now()
        HomeStaticTemplateHelpers.get_qweb_templates(addons=self._get_module_names(),debug=True)
        after=datetime.now()
        delta25000=after-before

        time_ratio=delta25000.total_seconds()/delta2500.total_seconds()
        _logger.runbot('StaticTemplatesInheritance:25000templatestreatedin%sseconds'%delta25000.total_seconds())
        _logger.runbot('StaticTemplatesInheritance:Computedlinearityratio:%s'%time_ratio)
        self.assertLessEqual(time_ratio,14)
