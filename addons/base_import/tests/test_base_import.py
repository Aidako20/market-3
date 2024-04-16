#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.
importbase64
importdifflib
importio
importpprint
importunittest

fromflectra.tests.commonimportTransactionCase,can_import
fromflectra.modules.moduleimportget_module_resource
fromflectra.toolsimportmute_logger,pycompat

ID_FIELD={
    'id':'id',
    'name':'id',
    'string':"ExternalID",

    'required':False,
    'fields':[],
    'type':'id',
}


defmake_field(name='value',string='Value',required=False,fields=[],field_type='id'):
    return[
        ID_FIELD,
        {'id':name,'name':name,'string':string,'required':required,'fields':fields,'type':field_type},
    ]


defsorted_fields(fields):
    """recursivelysortfieldliststoeasecomparison"""
    recursed=[dict(field,fields=sorted_fields(field['fields']))forfieldinfields]
    returnsorted(recursed,key=lambdafield:field['id'])


classBaseImportCase(TransactionCase):

    defassertEqualFields(self,fields1,fields2):
        f1=sorted_fields(fields1)
        f2=sorted_fields(fields2)
        assertf1==f2,'\n'.join(difflib.unified_diff(
            pprint.pformat(f1).splitlines(),
            pprint.pformat(f2).splitlines()
        ))

classTestBasicFields(BaseImportCase):

    defget_fields(self,field):
        returnself.env['base_import.import'].get_fields('base_import.tests.models.'+field)

    deftest_base(self):
        """Abasicfieldisnotrequired"""
        self.assertEqualFields(self.get_fields('char'),make_field(field_type='char'))

    deftest_required(self):
        """Requiredfieldsshouldbeflagged(sotheycanbefill-required)"""
        self.assertEqualFields(self.get_fields('char.required'),make_field(required=True,field_type='char'))

    deftest_readonly(self):
        """Readonlyfieldsshouldbefilteredout"""
        self.assertEqualFields(self.get_fields('char.readonly'),[ID_FIELD])

    deftest_readonly_states(self):
        """Readonlyfieldswithstatesshouldnotbefilteredout"""
        self.assertEqualFields(self.get_fields('char.states'),make_field(field_type='char'))

    deftest_readonly_states_noreadonly(self):
        """Readonlyfieldswithstateshavingnothingtodowith
        readonlyshouldstillbefilteredout"""
        self.assertEqualFields(self.get_fields('char.noreadonly'),[ID_FIELD])

    deftest_readonly_states_stillreadonly(self):
        """Readonlyfieldswithreadonlystatesleavingthemreadonly
        always...filteredout"""
        self.assertEqualFields(self.get_fields('char.stillreadonly'),[ID_FIELD])

    deftest_m2o(self):
        """M2Ofieldsshouldallowimportofthemselves(name_get),
        theiridandtheirxid"""
        self.assertEqualFields(self.get_fields('m2o'),make_field(field_type='many2one',fields=[
            {'id':'value','name':'id','string':'ExternalID','required':False,'fields':[],'type':'id'},
            {'id':'value','name':'.id','string':'DatabaseID','required':False,'fields':[],'type':'id'},
        ]))

    deftest_m2o_required(self):
        """Ifanm2ofieldisrequired,itsthreesub-fieldsare
        requiredaswell(theclienthastohandlethat:requiredness
        isid-based)
        """
        self.assertEqualFields(self.get_fields('m2o.required'),make_field(field_type='many2one',required=True,fields=[
            {'id':'value','name':'id','string':'ExternalID','required':True,'fields':[],'type':'id'},
            {'id':'value','name':'.id','string':'DatabaseID','required':True,'fields':[],'type':'id'},
        ]))


classTestO2M(BaseImportCase):

    defget_fields(self,field):
        returnself.env['base_import.import'].get_fields('base_import.tests.models.'+field)

    deftest_shallow(self):
        self.assertEqualFields(
            self.get_fields('o2m'),[
                ID_FIELD,
                {'id':'name','name':'name','string':"Name",'required':False,'fields':[],'type':'char',},
                {
                    'id':'value','name':'value','string':'Value',
                    'required':False,'type':'one2many',
                    'fields':[
                        ID_FIELD,
                        {
                            'id':'parent_id','name':'parent_id',
                            'string':'Parent','type':'many2one',
                            'required':False,'fields':[
                                {'id':'parent_id','name':'id',
                                 'string':'ExternalID','required':False,
                                 'fields':[],'type':'id'},
                                {'id':'parent_id','name':'.id',
                                 'string':'DatabaseID','required':False,
                                 'fields':[],'type':'id'},
                            ]
                        },
                        {'id':'value','name':'value','string':'Value',
                         'required':False,'fields':[],'type':'integer'
                        },
                    ]
                }
            ]
        )


classTestMatchHeadersSingle(TransactionCase):

    deftest_match_by_name(self):
        match=self.env['base_import.import']._match_header('f0',[{'name':'f0'}],{})
        self.assertEqual(match,[{'name':'f0'}])

    deftest_match_by_string(self):
        match=self.env['base_import.import']._match_header('somefield',[{'name':'bob','string':"SomeField"}],{})
        self.assertEqual(match,[{'name':'bob','string':"SomeField"}])

    deftest_nomatch(self):
        match=self.env['base_import.import']._match_header('shouldnotbe',[{'name':'bob','string':"wheee"}],{})
        self.assertEqual(match,[])

    deftest_recursive_match(self):
        f={
            'name':'f0',
            'string':"MyField",
            'fields':[
                {'name':'f0','string':"Subfield0",'fields':[]},
                {'name':'f1','string':"Subfield2",'fields':[]},
            ]
        }
        match=self.env['base_import.import']._match_header('f0/f1',[f],{})
        self.assertEqual(match,[f,f['fields'][1]])

    deftest_recursive_nomatch(self):
        """Matchfirstlevel,failtomatchsecondlevel
        """
        f={
            'name':'f0',
            'string':"MyField",
            'fields':[
                {'name':'f0','string':"Subfield0",'fields':[]},
                {'name':'f1','string':"Subfield2",'fields':[]},
            ]
        }
        match=self.env['base_import.import']._match_header('f0/f2',[f],{})
        self.assertEqual(match,[])


classTestMatchHeadersMultiple(TransactionCase):

    deftest_noheaders(self):
        self.assertEqual(
            self.env['base_import.import']._match_headers([],[],{}),([],{})
        )

    deftest_nomatch(self):
        self.assertEqual(
            self.env['base_import.import']._match_headers(
                iter([
                    ['foo','bar','baz','qux'],
                    ['v1','v2','v3','v4'],
                ]),
                [],
                {'headers':True}),
            (
                ['foo','bar','baz','qux'],
                dict.fromkeys(range(4))
            )
        )

    deftest_mixed(self):
        self.assertEqual(
            self.env['base_import.import']._match_headers(
                iter(['foobarbazqux/corge'.split()]),
                [
                    {'name':'bar','string':'Bar'},
                    {'name':'bob','string':'Baz'},
                    {'name':'qux','string':'Qux','fields':[
                        {'name':'corge','fields':[]},
                     ]}
                ],
                {'headers':True}),
            (['foo','bar','baz','qux/corge'],{
                0:None,
                1:['bar'],
                2:['bob'],
                3:['qux','corge'],
            })
        )


classTestColumnMapping(TransactionCase):

    deftest_column_mapping(self):
        import_record=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':u"Name,SomeValue,value\n"
                    u"chhagan,10,1\n"
                    u"magan,20,2\n".encode('utf-8'),
            'file_type':'text/csv',
            'file_name':'data.csv',
        })
        import_record.do(
            ['name','somevalue','othervalue'],
            ['Name','SomeValue','value'],
            {'quoting':'"','separator':',','headers':True},
            True
        )
        fields=self.env['base_import.mapping'].search_read(
            [('res_model','=','base_import.tests.models.preview')],
            ['column_name','field_name']
        )
        self.assertItemsEqual([f['column_name']forfinfields],['Name','SomeValue','value'])
        self.assertItemsEqual([f['field_name']forfinfields],['somevalue','name','othervalue'])


classTestPreview(TransactionCase):

    defmake_import(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'res.users',
            'file':u"로그인,언어\nbob,1\n".encode('euc_kr'),
            'file_type':'text/csv',
            'file_name':'kr_data.csv',
        })
        returnimport_wizard

    @mute_logger('flectra.addons.base_import.models.base_import')
    deftest_encoding(self):
        import_wizard=self.make_import()
        result=import_wizard.parse_preview({
            'quoting':'"',
            'separator':',',
        })
        self.assertFalse('error'inresult)

    @mute_logger('flectra.addons.base_import.models.base_import')
    deftest_csv_errors(self):
        import_wizard=self.make_import()

        result=import_wizard.parse_preview({
            'quoting':'foo',
            'separator':',',
        })
        self.assertTrue('error'inresult)

        result=import_wizard.parse_preview({
            'quoting':'"',
            'separator':'bob',
        })
        self.assertTrue('error'inresult)

    deftest_csv_success(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue,Counter\n'
                    b'foo,1,2\n'
                    b'bar,3,4\n'
                    b'qux,5,6\n',
            'file_type':'text/csv'
        })

        result=import_wizard.parse_preview({
            'quoting':'"',
            'separator':',',
            'headers':True,
        })
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['matches'],{0:['name'],1:['somevalue'],2:None})
        self.assertEqual(result['headers'],['name','SomeValue','Counter'])
        #Orderdependsoniterationorderoffields_get
        self.assertItemsEqual(result['fields'],[
            ID_FIELD,
            {'id':'name','name':'name','string':'Name','required':False,'fields':[],'type':'char'},
            {'id':'somevalue','name':'somevalue','string':'SomeValue','required':True,'fields':[],'type':'integer'},
            {'id':'othervalue','name':'othervalue','string':'OtherVariable','required':False,'fields':[],'type':'integer'},
        ])
        self.assertEqual(result['preview'],[
            ['foo','1','2'],
            ['bar','3','4'],
            ['qux','5','6'],
        ])

    @unittest.skipUnless(can_import('xlrd'),"XLRDmodulenotavailable")
    deftest_xls_success(self):
        xls_file_path=get_module_resource('base_import','tests','test.xls')
        file_content=open(xls_file_path,'rb').read()
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':file_content,
            'file_type':'application/vnd.ms-excel'
        })

        result=import_wizard.parse_preview({
            'headers':True,
        })
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['matches'],{0:['name'],1:['somevalue'],2:None})
        self.assertEqual(result['headers'],['name','SomeValue','Counter'])
        self.assertItemsEqual(result['fields'],[
            ID_FIELD,
            {'id':'name','name':'name','string':'Name','required':False,'fields':[],'type':'char'},
            {'id':'somevalue','name':'somevalue','string':'SomeValue','required':True,'fields':[],'type':'integer'},
            {'id':'othervalue','name':'othervalue','string':'OtherVariable','required':False,'fields':[],'type':'integer'},
        ])
        self.assertEqual(result['preview'],[
            ['foo','1','2'],
            ['bar','3','4'],
            ['qux','5','6'],
        ])

    @unittest.skipUnless(can_import('xlrd.xlsx'),"XLRD/XLSXnotavailable")
    deftest_xlsx_success(self):
        xlsx_file_path=get_module_resource('base_import','tests','test.xlsx')
        file_content=open(xlsx_file_path,'rb').read()
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':file_content,
            'file_type':'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        })

        result=import_wizard.parse_preview({
            'headers':True,
        })
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['matches'],{0:['name'],1:['somevalue'],2:None})
        self.assertEqual(result['headers'],['name','SomeValue','Counter'])
        self.assertItemsEqual(result['fields'],[
            ID_FIELD,
            {'id':'name','name':'name','string':'Name','required':False,'fields':[],'type':'char'},
            {'id':'somevalue','name':'somevalue','string':'SomeValue','required':True,'fields':[],'type':'integer'},
            {'id':'othervalue','name':'othervalue','string':'OtherVariable','required':False,'fields':[],'type':'integer'},
        ])
        self.assertEqual(result['preview'],[
            ['foo','1','2'],
            ['bar','3','4'],
            ['qux','5','6'],
        ])

    @unittest.skipUnless(can_import('odf'),"ODFPYnotavailable")
    deftest_ods_success(self):
        ods_file_path=get_module_resource('base_import','tests','test.ods')
        file_content=open(ods_file_path,'rb').read()
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':file_content,
            'file_type':'application/vnd.oasis.opendocument.spreadsheet'
        })

        result=import_wizard.parse_preview({
            'headers':True,
        })
        self.assertIsNone(result.get('error'))
        self.assertEqual(result['matches'],{0:['name'],1:['somevalue'],2:None})
        self.assertEqual(result['headers'],['name','SomeValue','Counter'])
        self.assertItemsEqual(result['fields'],[
            ID_FIELD,
            {'id':'name','name':'name','string':'Name','required':False,'fields':[],'type':'char'},
            {'id':'somevalue','name':'somevalue','string':'SomeValue','required':True,'fields':[],'type':'integer'},
            {'id':'othervalue','name':'othervalue','string':'OtherVariable','required':False,'fields':[],'type':'integer'},
        ])
        self.assertEqual(result['preview'],[
            ['foo','1','2'],
            ['bar','3','4'],
            ['aux','5','6'],
        ])

classtest_convert_import_data(TransactionCase):
    """Testsconversionofbase_import.importinputintodatawhich
    canbefedtoModel.load
    """
    deftest_all(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue,Counter\n'
                    b'foo,1,2\n'
                    b'bar,3,4\n'
                    b'qux,5,6\n',
            'file_type':'text/csv'

        })
        data,fields=import_wizard._convert_import_data(
            ['name','somevalue','othervalue'],
            {'quoting':'"','separator':',','headers':True}
        )

        self.assertItemsEqual(fields,['name','somevalue','othervalue'])
        self.assertItemsEqual(data,[
            ['foo','1','2'],
            ['bar','3','4'],
            ['qux','5','6'],
        ])

    deftest_date_fields(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'res.partner',
            'file':u'name,date,create_date\n'
                    u'"foo","2013年07月18日","2016-10-1206:06"\n'.encode('utf-8'),
            'file_type':'text/csv'

        })

        results=import_wizard.do(
            ['name','date','create_date'],
            [],
            {
                'date_format':'%Y年%m月%d日',
                'datetime_format':'%Y-%m-%d%H:%M',
                'quoting':'"',
                'separator':',',
                'headers':True
            }
        )

        #ifresultsempty,noerrors
        self.assertItemsEqual(results['messages'],[])

    deftest_parse_relational_fields(self):
        """Ensurethatrelationalfieldsfloatanddatearecorrectly
        parsedduringtheimportcall.
        """
        import_wizard=self.env['base_import.import'].create({
            'res_model':'res.partner',
            'file':u'name,parent_id/id,parent_id/date,parent_id/credit_limit\n'
                    u'"foo","__export__.res_partner_1","2017年10月12日","5,69"\n'.encode('utf-8'),
            'file_type':'text/csv'

        })
        options={
            'date_format':'%Y年%m月%d日',
            'quoting':'"',
            'separator':',',
            'float_decimal_separator':',',
            'float_thousand_separator':'.',
            'headers':True
        }
        data,import_fields=import_wizard._convert_import_data(
            ['name','parent_id/.id','parent_id/date','parent_id/credit_limit'],
            options
        )
        result=import_wizard._parse_import_data(data,import_fields,options)
        #Checkifthedata5,69asbeencorrectlyparsed.
        self.assertEqual(float(result[0][-1]),5.69)
        self.assertEqual(str(result[0][-2]),'2017-10-12')

    deftest_parse_scientific_notation(self):
        """Ensurethatscientificnotationiscorrectlyconvertedtodecimal"""
        import_wizard=self.env['base_import.import']

        test_options={}
        test_data=[
            ["1E+05"],
            ["1.20E-05"],
            ["1,9e5"],
            ["9,5e-5"],
        ]
        expected_result=[
            ["100000.000000"],
            ["0.000012"],
            ["190000.000000"],
            ["0.000095"],
        ]

        import_wizard._parse_float_from_data(test_data,0,'test-name',test_options)
        self.assertEqual(test_data,expected_result)

    deftest_filtered(self):
        """If``False``isprovidedasfieldmappingforacolumn,
        thatcolumnshouldberemovedfromimportabledata
        """
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue,Counter\n'
                    b'foo,1,2\n'
                    b'bar,3,4\n'
                    b'qux,5,6\n',
            'file_type':'text/csv'
        })
        data,fields=import_wizard._convert_import_data(
            ['name',False,'othervalue'],
            {'quoting':'"','separator':',','headers':True}
        )

        self.assertItemsEqual(fields,['name','othervalue'])
        self.assertItemsEqual(data,[
            ['foo','2'],
            ['bar','4'],
            ['qux','6'],
        ])

    deftest_norow(self):
        """Ifarowiscomposedonlyofemptyvalues(duetohaving
        filteredoutnon-emptyvaluesfromit),itshouldberemoved
        """
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue,Counter\n'
                    b'foo,1,2\n'
                    b',3,\n'
                    b',5,6\n',
            'file_type':'text/csv'
        })
        data,fields=import_wizard._convert_import_data(
            ['name',False,'othervalue'],
            {'quoting':'"','separator':',','headers':True}
        )

        self.assertItemsEqual(fields,['name','othervalue'])
        self.assertItemsEqual(data,[
            ['foo','2'],
            ['','6'],
        ])

    deftest_empty_rows(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue\n'
                    b'foo,1\n'
                    b'\n'
                    b'bar,2\n'
                    b'    \n'
                    b'\t\n',
            'file_type':'text/csv'
        })
        data,fields=import_wizard._convert_import_data(
            ['name','somevalue'],
            {'quoting':'"','separator':',','headers':True}
        )

        self.assertItemsEqual(fields,['name','somevalue'])
        self.assertItemsEqual(data,[
            ['foo','1'],
            ['bar','2'],
        ])

    deftest_nofield(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue,Counter\n'
                    b'foo,1,2\n',
            'file_type':'text/csv'

        })
        self.assertRaises(ValueError,import_wizard._convert_import_data,[],{'quoting':'"','separator':',','headers':True})

    deftest_falsefields(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':b'name,SomeValue,Counter\n'
                    b'foo,1,2\n',
            'file_type':'text/csv'
        })

        self.assertRaises(
            ValueError,
            import_wizard._convert_import_data,
            [False,False,False],
            {'quoting':'"','separator':',','headers':True})

    deftest_newline_import(self):
        """
        Ensureimportingkeepnewlines
        """
        output=io.BytesIO()
        writer=pycompat.csv_writer(output,quoting=1)

        data_row=[u"\tfoo\n\tbar",u"\"hello\"\n\n'world'"]

        writer.writerow([u"name",u"SomeValue"])
        writer.writerow(data_row)

        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file':output.getvalue(),
            'file_type':'text/csv',
        })
        data,_=import_wizard._convert_import_data(
            ['name','somevalue'],
            {'quoting':'"','separator':',','headers':True}
        )

        self.assertItemsEqual(data,[data_row])

classTestBatching(TransactionCase):
    def_makefile(self,rows):
        f=io.BytesIO()
        writer=pycompat.csv_writer(f,quoting=1)
        writer.writerow(['name','counter'])
        foriinrange(rows):
            writer.writerow(['n_%d'%i,str(i)])
        returnf.getvalue()

    deftest_recognize_batched(self):
        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.preview',
            'file_type':'text/csv',
        })

        import_wizard.file=self._makefile(10)
        result=import_wizard.parse_preview({
            'quoting':'"',
            'separator':',',
            'headers':True,
            'limit':100,
        })
        self.assertIsNone(result.get('error'))
        self.assertIs(result['batch'],False)

        result=import_wizard.parse_preview({
            'quoting':'"',
            'separator':',',
            'headers':True,
            'limit':5,
        })
        self.assertIsNone(result.get('error'))
        self.assertIs(result['batch'],True)

    deftest_limit_on_lines(self):
        """Thelimitoptionshouldbealimitonthenumberof*lines*
        importedatattime,notthenumberof*records*.Thisisrelevant
        whenitcomestoembeddedo2m.

        Abigquestioniswhetherwewanttoroundupordown(ifthelimit
        bringsusinsidearecord).Roundingup(akafinishinguptherecord
        we'recurrentlyparsing)seemslikeabetteridea:

        *ifthefirstrecordhassomanysub-linesithitsthelimitwestill
          wanttoimportit(it'sprobablyextremelyrarebutitcanhappen)
        *ifwehaveonelineperrecord,weprobablywanttoimport<limit>
          recordsnot<limit-1>,butifwestopinthemiddleofthe"current
          record"we'dalwaysignorethelastrecord(Ithink)
        """
        f=io.BytesIO()
        writer=pycompat.csv_writer(f,quoting=1)
        writer.writerow(['name','value/value'])
        forrecordinrange(10):
            writer.writerow(['record_%d'%record,'0'])
            forrowinrange(1,10):
                writer.writerow(['',str(row)])

        import_wizard=self.env['base_import.import'].create({
            'res_model':'base_import.tests.models.o2m',
            'file_type':'text/csv',
            'file_name':'things.csv',
            'file':f.getvalue(),
        })
        opts={'quoting':'"','separator':',','headers':True}
        preview=import_wizard.parse_preview({**opts,'limit':15})
        self.assertIs(preview['batch'],True)

        results=import_wizard.do(
            ['name','value/value'],[],
            {**opts,'limit':5}
        )
        self.assertFalse(results['messages'])
        self.assertEqual(len(results['ids']),1,"shouldhaveimportedthefirstrecordinfull,got%s"%results['ids'])
        self.assertEqual(results['nextrow'],10)

        results=import_wizard.do(
            ['name','value/value'],[],
            {**opts,'limit':15}
        )
        self.assertFalse(results['messages'])
        self.assertEqual(len(results['ids']),2,"shouldhaveimportethefirsttworecords,got%s"%results['ids'])
        self.assertEqual(results['nextrow'],20)


    deftest_batches(self):
        partners_before=self.env['res.partner'].search([])
        opts={'headers':True,'separator':',','quoting':'"'}

        import_wizard=self.env['base_import.import'].create({
            'res_model':'res.partner',
            'file_type':'text/csv',
            'file_name':'clients.csv',
            'file':b"""name,email
a,a@example.com
b,b@example.com
,
c,c@example.com
d,d@example.com
e,e@example.com
f,f@example.com
g,g@example.com
"""
        })

        results=import_wizard.do(['name','email'],[],{**opts,'limit':1})
        self.assertFalse(results['messages'])
        self.assertEqual(len(results['ids']),1)
        #titlerowisignoredbylastrow'scounter
        self.assertEqual(results['nextrow'],1)
        partners_1=self.env['res.partner'].search([])-partners_before
        self.assertEqual(partners_1.name,'a')

        results=import_wizard.do(['name','email'],[],{**opts,'limit':2,'skip':1})
        self.assertFalse(results['messages'])
        self.assertEqual(len(results['ids']),2)
        #emptyrowshouldalsobeignored
        self.assertEqual(results['nextrow'],3)
        partners_2=self.env['res.partner'].search([])-(partners_before|partners_1)
        self.assertEqual(partners_2.mapped('name'),['b','c'])

        results=import_wizard.do(['name','email'],[],{**opts,'limit':10,'skip':3})
        self.assertFalse(results['messages'])
        self.assertEqual(len(results['ids']),4)
        self.assertEqual(results['nextrow'],0)
        partners_3=self.env['res.partner'].search([])-(partners_before|partners_1|partners_2)
        self.assertEqual(partners_3.mapped('name'),['d','e','f','g'])

classtest_failures(TransactionCase):
    deftest_big_attachments(self):
        """
        Ensurebigfields(e.g.b64-encodedimagedata)canbeimportedand
        we'renothittinglimitsofthedefaultCSVparserconfig
        """
        fromPILimportImage

        im=Image.new('RGB',(1920,1080))
        fout=io.BytesIO()

        writer=pycompat.csv_writer(fout,dialect=None)
        writer.writerows([
            [u'name',u'db_datas'],
            [u'foo',base64.b64encode(im.tobytes()).decode('ascii')]
        ])

        import_wizard=self.env['base_import.import'].create({
            'res_model':'ir.attachment',
            'file':fout.getvalue(),
            'file_type':'text/csv'
        })
        results=import_wizard.do(
            ['name','db_datas'],
            [],
            {'headers':True,'separator':',','quoting':'"'})
        self.assertFalse(results['messages'],"resultsshouldbeemptyonsuccessfulimport")
