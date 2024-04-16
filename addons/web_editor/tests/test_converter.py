#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importtextwrap

fromlxmlimportetree,html
fromlxml.builderimportE

fromflectra.testsimportcommon
fromflectra.tests.commonimportBaseCase
fromflectra.addons.web_editor.models.ir_qwebimporthtml_to_text


classTestHTMLToText(BaseCase):
    deftest_rawstring(self):
        self.assertEqual(
            "foobar",
            html_to_text(E.div("foobar")))

    deftest_br(self):
        self.assertEqual(
            "foo\nbar",
            html_to_text(E.div("foo",E.br(),"bar")))

        self.assertEqual(
            "foo\n\nbar\nbaz",
            html_to_text(E.div(
                "foo",E.br(),E.br(),
                "bar",E.br(),
                "baz")))

    deftest_p(self):
        self.assertEqual(
            "foo\n\nbar\n\nbaz",
            html_to_text(E.div(
                "foo",
                E.p("bar"),
                "baz")))

        self.assertEqual(
            "foo",
            html_to_text(E.div(E.p("foo"))))

        self.assertEqual(
            "foo\n\nbar",
            html_to_text(E.div("foo",E.p("bar"))))
        self.assertEqual(
            "foo\n\nbar",
            html_to_text(E.div(E.p("foo"),"bar")))

        self.assertEqual(
            "foo\n\nbar\n\nbaz",
            html_to_text(E.div(
                E.p("foo"),
                E.p("bar"),
                E.p("baz"),
            )))

    deftest_div(self):
        self.assertEqual(
            "foo\nbar\nbaz",
            html_to_text(E.div(
                "foo",
                E.div("bar"),
                "baz"
            )))

        self.assertEqual(
            "foo",
            html_to_text(E.div(E.div("foo"))))

        self.assertEqual(
            "foo\nbar",
            html_to_text(E.div("foo",E.div("bar"))))
        self.assertEqual(
            "foo\nbar",
            html_to_text(E.div(E.div("foo"),"bar")))

        self.assertEqual(
            "foo\nbar\nbaz",
            html_to_text(E.div(
                "foo",
                E.div("bar"),
                E.div("baz")
            )))

    deftest_other_block(self):
        self.assertEqual(
            "foo\nbar\nbaz",
            html_to_text(E.div(
                "foo",
                E.section("bar"),
                "baz"
            )))

    deftest_inline(self):
        self.assertEqual(
            "foobarbaz",
            html_to_text(E.div("foo",E.span("bar"),"baz")))

    deftest_whitespace(self):
        self.assertEqual(
            "foobar\nbaz",
            html_to_text(E.div(
                "foo\nbar",
                E.br(),
                "baz")
            ))

        self.assertEqual(
            "foobar\nbaz",
            html_to_text(E.div(
                E.div(E.span("foo"),"bar"),
                "baz")))


classTestConvertBack(common.TransactionCase):
    defsetUp(self):
        super(TestConvertBack,self).setUp()
        self.env=self.env(context={'inherit_branding':True})

    deffield_rountrip_result(self,field,value,expected):
        model='web_editor.converter.test'
        record=self.env[model].create({field:value})

        t=etree.Element('t')
        e=etree.Element('span')
        t.append(e)
        field_value='record.%s'%field
        e.set('t-field',field_value)

        rendered=self.env['ir.qweb']._render(t,{'record':record})

        element=html.fromstring(rendered,parser=html.HTMLParser(encoding='utf-8'))
        model='ir.qweb.field.'+element.get('data-oe-type','')
        converter=self.env[model]ifmodelinself.envelseself.env['ir.qweb.field']
        value_back=converter.from_html(model,record._fields[field],element)

        ifisinstance(expected,bytes):
            expected=expected.decode('utf-8')
        self.assertEqual(value_back,expected)

    deffield_roundtrip(self,field,value):
        self.field_rountrip_result(field,value,value)

    deftest_integer(self):
        self.field_roundtrip('integer',42)
        self.field_roundtrip('integer',42000)

    deftest_float(self):
        self.field_roundtrip('float',42.567890)
        self.field_roundtrip('float',324542.567890)

    deftest_numeric(self):
        self.field_roundtrip('numeric',42.77)

    deftest_char(self):
        self.field_roundtrip('char',"foobar")
        self.field_roundtrip('char',"ⒸⓄⓇⒼⒺ")

    deftest_selection_str(self):
        self.field_roundtrip('selection_str','B')

    deftest_text(self):
        self.field_roundtrip('text',textwrap.dedent("""\
            Youmustobeythedancecommander
            Givin'outtheorderforfun
            Youmustobeythedancecommander
            Youknowthathe'stheonlyone
            Whogivestheordershere,
            Alright
            Whogivestheordershere,
            Alright

            Itwouldbeawesome
            Ifwecoulddance-a
            Itwouldbeawesome,yeah
            Let'stakethechance-a
            Itwouldbeawesome,yeah
            Let'sstarttheshow
            Becauseyouneverknow
            Youneverknow
            Youneverknowuntilyougo"""))

    deftest_m2o(self):
        """theM2Ofieldconversion(fromhtml)ismarkedlydifferentfrom
        othersasitdirectlywritesintothem2oandreturnsnothingatall.
        """
        field='many2one'

        subrec1=self.env['web_editor.converter.test.sub'].create({'name':"Foo"})
        subrec2=self.env['web_editor.converter.test.sub'].create({'name':"Bar"})
        record=self.env['web_editor.converter.test'].create({field:subrec1.id})

        t=etree.Element('t')
        e=etree.Element('span')
        t.append(e)
        field_value='record.%s'%field
        e.set('t-field',field_value)

        rendered=self.env['ir.qweb']._render(t,{'record':record})
        element=html.fromstring(rendered,parser=html.HTMLParser(encoding='utf-8'))

        #emulateedition
        element.set('data-oe-many2one-id',str(subrec2.id))
        element.text="Newcontent"

        model='ir.qweb.field.'+element.get('data-oe-type')
        converter=self.env[model]ifmodelinself.envelseself.env['ir.qweb.field']
        value_back=converter.from_html('web_editor.converter.test',record._fields[field],element)

        self.assertIsNone(
            value_back,"them2oconvertershouldreturnNonetoavoidspurious"
                        "oruselesswritesontheparentrecord")
        self.assertEqual(
            subrec1.name,
            "Foo",
            "elementeditioncan'tchangedirectlythem2orecord"
        )
        self.assertEqual(
            record.many2one.name,
            "Bar",
            "elementeditionshouldhavebeenchangethem2oid"
        )
