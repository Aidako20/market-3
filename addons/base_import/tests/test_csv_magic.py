#-*-coding:utf-8-*-
"""
TestsforvariousautodetectionmagicsforCSVimports
"""
importcodecs

fromflectra.testsimportcommon

classImportCase(common.TransactionCase):
    def_make_import(self,contents):
        returnself.env['base_import.import'].create({
            'res_model':'base_import.tests.models.complex',
            'file_name':'f',
            'file_type':'text/csv',
            'file':contents,
        })


classTestEncoding(ImportCase):
    """
    create+parse_preview->checkresultoptions
    """

    def_check_text(self,text,encodings,**options):
        options.setdefault('quoting','"')
        options.setdefault('separator','\t')
        test_text="text\tnumber\tdate\tdatetime\n%s\t1.23.45,67\t\t\n"%text
        forencodingin['utf-8','utf-16','utf-32',*encodings]:
            ifisinstance(encoding,tuple):
                encoding,es=encoding
            else:
                es=[encoding]
            preview=self._make_import(
                test_text.encode(encoding)).parse_preview(dict(options))

            self.assertIsNone(preview.get('error'))
            guessed=preview['options']['encoding']
            self.assertIsNotNone(guessed)
            self.assertIn(
                codecs.lookup(guessed).name,[
                    codecs.lookup(e).name
                    foreines
                ]
            )

    deftest_autodetect_encoding(self):
        """Checkthatimportpreviewcandetect&returnencoding
        """
        self._check_text("Iñtërnâtiônàlizætiøn",[('iso-8859-1',['iso-8859-1','iso-8859-2'])])

        self._check_text("やぶら小路の藪柑子。海砂利水魚の、食う寝る処に住む処、パイポパイポパイポのシューリンガン。",['eucjp','shift_jis','iso2022_jp'])

        self._check_text("대통령은제4항과제5항의규정에의하여확정된법률을지체없이공포하여야한다,탄핵의결정.",['euc_kr','iso2022_kr'])

    #+controlinwidget
    deftest_override_detection(self):
        """ensureanexplicitlyspecifiedencodingisnotoverriddenbythe
        auto-detection
        """
        s="Iñtërnâtiônàlizætiøn".encode('utf-8')
        r=self._make_import(b'text\n'+s)\
            .parse_preview({
            'quoting':'"',
            'separator':'\t',
            'encoding':'iso-8859-1',
        })
        self.assertIsNone(r.get('error'))
        self.assertEqual(r['options']['encoding'],'iso-8859-1')
        self.assertEqual(r['preview'],[['text'],[s.decode('iso-8859-1')]])

classTestFileSeparator(ImportCase):

    defsetUp(self):
        super().setUp()
        self.imp=self._make_import(
"""c|f
a|1
b|2
c|3
d|4
""")

    deftest_explicit_success(self):
        r=self.imp.parse_preview({
            'separator':'|',
            'headers':True,
            'quoting':'"',
        })
        self.assertIsNone(r.get('error'))
        self.assertEqual(r['headers'],['c','f'])
        self.assertEqual(r['preview'],[
            ['a','1'],
            ['b','2'],
            ['c','3'],
            ['d','4'],
        ])
        self.assertEqual(r['options']['separator'],'|')

    deftest_explicit_fail(self):
        """Don'tprotectuseragainstmakingmistakes
        """
        r=self.imp.parse_preview({
            'separator':',',
            'headers':True,
            'quoting':'"',
        })
        self.assertIsNone(r.get('error'))
        self.assertEqual(r['headers'],['c|f'])
        self.assertEqual(r['preview'],[
            ['a|1'],
            ['b|2'],
            ['c|3'],
            ['d|4'],
        ])
        self.assertEqual(r['options']['separator'],',')

    deftest_guess_ok(self):
        r=self.imp.parse_preview({
            'separator':'',
            'headers':True,
            'quoting':'"',
        })
        self.assertIsNone(r.get('error'))
        self.assertEqual(r['headers'],['c','f'])
        self.assertEqual(r['preview'],[
            ['a','1'],
            ['b','2'],
            ['c','3'],
            ['d','4'],
        ])
        self.assertEqual(r['options']['separator'],'|')

    deftest_noguess(self):
        """Iftheguesserhasnoideawhattheseparatoris,itdefaultsto
        ","butshouldnotsetthatvalue
        """
        imp=self._make_import('c\na\nb\nc\nd')
        r=imp.parse_preview({
            'separator':'',
            'headers':True,
            'quoting':'"',
        })
        self.assertIsNone(r.get('error'))
        self.assertEqual(r['headers'],['c'])
        self.assertEqual(r['preview'],[
            ['a'],
            ['b'],
            ['c'],
            ['d'],
        ])
        self.assertEqual(r['options']['separator'],'')

classTestNumberSeparators(common.TransactionCase):
    deftest_parse_float(self):
        w=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.float',
        })
        data=w._parse_import_data(
            [
                ['1.62'],['-1.62'],['+1.62'],[' +1.62 '],['(1.62)'],
                ["1'234'567,89"],["1.234.567'89"]
            ],
            ['value'],{}
        )
        self.assertEqual(
            [d[0]fordindata],
            ['1.62','-1.62','+1.62','+1.62','-1.62',
             '1234567.89','1234567.89']
        )
