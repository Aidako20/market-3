#-*-coding:utf-8-*-
#PartofFlectra.SeeLICENSEfileforfullcopyrightandlicensingdetails.

importbase64
importbinascii
importcodecs
importcollections
importunicodedata

importchardet
importdatetime
importio
importitertools
importlogging
importpsycopg2
importoperator
importos
importre
importrequests

fromPILimportImage

fromflectraimportapi,fields,models
fromflectra.exceptionsimportAccessError
fromflectra.tools.translateimport_
fromflectra.tools.mimetypesimportguess_mimetype
fromflectra.toolsimportconfig,DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT,pycompat

FIELDS_RECURSION_LIMIT=3
ERROR_PREVIEW_BYTES=200
DEFAULT_IMAGE_TIMEOUT=3
DEFAULT_IMAGE_MAXBYTES=10*1024*1024
DEFAULT_IMAGE_REGEX=r"^(?:http|https)://"
DEFAULT_IMAGE_CHUNK_SIZE=32768
IMAGE_FIELDS=["icon","image","logo","picture"]
_logger=logging.getLogger(__name__)
BOM_MAP={
    'utf-16le':codecs.BOM_UTF16_LE,
    'utf-16be':codecs.BOM_UTF16_BE,
    'utf-32le':codecs.BOM_UTF32_LE,
    'utf-32be':codecs.BOM_UTF32_BE,
}

try:
    importxlrd
    try:
        fromxlrdimportxlsx
    exceptImportError:
        xlsx=None
exceptImportError:
    xlrd=xlsx=None

try:
    from.importodf_ods_reader
exceptImportError:
    odf_ods_reader=None

FILE_TYPE_DICT={
    'text/csv':('csv',True,None),
    'application/vnd.ms-excel':('xls',xlrd,'xlrd'),
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':('xlsx',xlsx,'xlrd>=1.0.0'),
    'application/vnd.oasis.opendocument.spreadsheet':('ods',odf_ods_reader,'odfpy')
}
EXTENSIONS={
    '.'+ext:handler
    formime,(ext,handler,req)inFILE_TYPE_DICT.items()
}

classBase(models.AbstractModel):
    _inherit='base'

    @api.model
    defget_import_templates(self):
        """
        Gettheimporttemplateslabelandpath.

        :return:alist(dict)containinglabelandtemplatepath
                 like``[{'label':'foo','template':'path'}]``
        """
        return[]

classImportMapping(models.Model):
    """mappingofpreviouscolumn:fieldselections

    Thisisusefulwhenrepeatedlyimportingfromathird-party
    system:columnnamesgeneratedbytheexternalsystemmay
    notmatchFlectra'sfieldnamesorlabels.Thismodelisused
    tosavethemappingbetweencolumnnamesandfieldssothat
    nexttimeauserimportsfromthesamethird-partysystems
    wecanautomaticallymatchthecolumnstothecorrectfield
    withoutthemhavingtore-enterthemappingeverysingle
    time.
    """
    _name='base_import.mapping'
    _description='BaseImportMapping'

    res_model=fields.Char(index=True)
    column_name=fields.Char()
    field_name=fields.Char()


classResUsers(models.Model):
    _inherit='res.users'

    def_can_import_remote_urls(self):
        """Hooktodecidewhetherthecurrentuserisallowedtoimport
        imagesviaURL(assuchanimportcanDOSaworker).Bydefault,
        allowstheadministratorgroup.

        :rtype:bool
        """
        self.ensure_one()
        returnself._is_admin()

classImport(models.TransientModel):

    _name='base_import.import'
    _description='BaseImport'

    #allowimportstosurvivefor12hincaseuserisslow
    _transient_max_hours=12.0

    res_model=fields.Char('Model')
    file=fields.Binary('File',help="Filetocheckand/orimport,rawbinary(notbase64)",attachment=False)
    file_name=fields.Char('FileName')
    file_type=fields.Char('FileType')

    @api.model
    defget_fields(self,model,depth=FIELDS_RECURSION_LIMIT):
        """Recursivelygetfieldsfortheprovidedmodel(through
        fields_get)andfilterthemaccordingtoimportability

        Theoutputformatisalistof``Field``,with``Field``
        definedas:

        ..class::Field

            ..attribute::id(str)

                Anon-uniqueidentifierforthefield,usedtocompute
                thespanofthe``required``attribute:ifmultiple
                ``required``fieldshavethesameid,onlyoneofthem
                isnecessary.

            ..attribute::name(str)

                Thefield'slogical(Flectra)namewithinthescopeof
                itsparent.

            ..attribute::string(str)

                Thefield'shuman-readablename(``@string``)

            ..attribute::required(bool)

                Whetherthefieldismarkedasrequiredinthe
                model.Clientsmustprovidenon-emptyimportvalues
                forallrequiredfieldsortheimportwillerrorout.

            ..attribute::fields(list(Field))

                Thecurrentfield'ssubfields.Thedatabaseand
                externalidentifiersform2oandm2mfields;a
                filteredandtransformedfields_getforo2mfields(to
                avariabledepthdefinedby``depth``).

                Fieldswithnosub-fieldswillhaveanemptylistof
                sub-fields.

        :paramstrmodel:nameofthemodeltogetfieldsform
        :paramintdepth:depthofrecursionintoo2mfields
        """
        Model=self.env[model]
        importable_fields=[{
            'id':'id',
            'name':'id',
            'string':_("ExternalID"),
            'required':False,
            'fields':[],
            'type':'id',
        }]
        ifnotdepth:
            returnimportable_fields

        model_fields=Model.fields_get()
        blacklist=models.MAGIC_COLUMNS+[Model.CONCURRENCY_CHECK_FIELD]
        forname,fieldinmodel_fields.items():
            ifnameinblacklist:
                continue
            #anemptystringmeansthefieldisdeprecated,@deprecatedmust
            #beabsentorFalsetomeannot-deprecated
            iffield.get('deprecated',False)isnotFalse:
                continue
            iffield.get('readonly'):
                states=field.get('states')
                ifnotstates:
                    continue
                #states={state:[(attr,value),(attr2,value2)],state2:...}
                ifnotany(attr=='readonly'andvalueisFalse
                           forattr,valueinitertools.chain.from_iterable(states.values())):
                    continue
            field_value={
                'id':name,
                'name':name,
                'string':field['string'],
                #YUNOALWAYSHASREQUIRED
                'required':bool(field.get('required')),
                'fields':[],
                'type':field['type'],
            }

            iffield['type']in('many2many','many2one'):
                field_value['fields']=[
                    dict(field_value,name='id',string=_("ExternalID"),type='id'),
                    dict(field_value,name='.id',string=_("DatabaseID"),type='id'),
                ]
            eliffield['type']=='one2many':
                field_value['fields']=self.get_fields(field['relation'],depth=depth-1)
                ifself.user_has_groups('base.group_no_one'):
                    field_value['fields'].append({'id':'.id','name':'.id','string':_("DatabaseID"),'required':False,'fields':[],'type':'id'})

            importable_fields.append(field_value)

        #TODO:cacheonmodel?
        returnimportable_fields

    def_read_file(self,options):
        """Dispatchtospecificmethodtoreadfilecontent,accordingtoitsmimetypeorfiletype
            :paramoptions:dictofreadingoptions(quoting,separator,...)
        """
        self.ensure_one()
        #guessmimetypefromfilecontent
        mimetype=guess_mimetype(self.fileorb'')
        (file_extension,handler,req)=FILE_TYPE_DICT.get(mimetype,(None,None,None))
        ifhandler:
            try:
                returngetattr(self,'_read_'+file_extension)(options)
            exceptException:
                _logger.warning("Failedtoreadfile'%s'(transientid%d)usingguessedmimetype%s",self.file_nameor'<unknown>',self.id,mimetype)

        #tryreadingwithuser-providedmimetype
        (file_extension,handler,req)=FILE_TYPE_DICT.get(self.file_type,(None,None,None))
        ifhandler:
            try:
                returngetattr(self,'_read_'+file_extension)(options)
            exceptException:
                _logger.warning("Failedtoreadfile'%s'(transientid%d)usinguser-providedmimetype%s",self.file_nameor'<unknown>',self.id,self.file_type)

        #fallbackonfileextensionsasmimetypescanbeunreliable(e.g.
        #softwaresettingincorrectmimetypes,ornon-installedsoftware
        #leadingtobrowsernotsendingmimetypes)
        ifself.file_name:
            p,ext=os.path.splitext(self.file_name)
            ifextinEXTENSIONS:
                try:
                    returngetattr(self,'_read_'+ext[1:])(options)
                exceptException:
                    _logger.warning("Failedtoreadfile'%s'(transientid%s)usingfileextension",self.file_name,self.id)

        ifreq:
            raiseImportError(_("Unabletoload\"{extension}\"file:requiresPythonmodule\"{modname}\"").format(extension=file_extension,modname=req))
        raiseValueError(_("Unsupportedfileformat\"{}\",importonlysupportsCSV,ODS,XLSandXLSX").format(self.file_type))

    def_read_xls(self,options):
        """Readfilecontent,usingxlrdlib"""
        book=xlrd.open_workbook(file_contents=self.fileorb'')
        sheets=options['sheets']=book.sheet_names()
        sheet=options['sheet']=options.get('sheet')orsheets[0]
        returnself._read_xls_book(book,sheet)

    def_read_xls_book(self,book,sheet_name):
        sheet=book.sheet_by_name(sheet_name)
        #emulateSheet.get_rowsforpre-0.9.4
        forrowx,rowinenumerate(map(sheet.row,range(sheet.nrows)),1):
            values=[]
            forcolx,cellinenumerate(row,1):
                ifcell.ctypeisxlrd.XL_CELL_NUMBER:
                    is_float=cell.value%1!=0.0
                    values.append(
                        str(cell.value)
                        ifis_float
                        elsestr(int(cell.value))
                    )
                elifcell.ctypeisxlrd.XL_CELL_DATE:
                    is_datetime=cell.value%1!=0.0
                    #emulatexldate_as_datetimeforpre-0.9.3
                    dt=datetime.datetime(*xlrd.xldate.xldate_as_tuple(cell.value,book.datemode))
                    values.append(
                        dt.strftime(DEFAULT_SERVER_DATETIME_FORMAT)
                        ifis_datetime
                        elsedt.strftime(DEFAULT_SERVER_DATE_FORMAT)
                    )
                elifcell.ctypeisxlrd.XL_CELL_BOOLEAN:
                    values.append(u'True'ifcell.valueelseu'False')
                elifcell.ctypeisxlrd.XL_CELL_ERROR:
                    raiseValueError(
                        _("Invalidcellvalueatrow%(row)s,column%(col)s:%(cell_value)s")%{
                            'row':rowx,
                            'col':colx,
                            'cell_value':xlrd.error_text_from_code.get(cell.value,_("unknownerrorcode%s",cell.value))
                        }
                    )
                else:
                    values.append(cell.value)
            ifany(xforxinvaluesifx.strip()):
                yieldvalues

    #usethesamemethodforxlsxandxlsfiles
    _read_xlsx=_read_xls

    def_read_ods(self,options):
        """ReadfilecontentusingODSReadercustomlib"""
        doc=odf_ods_reader.ODSReader(file=io.BytesIO(self.fileorb''))
        sheets=options['sheets']=list(doc.SHEETS.keys())
        sheet=options['sheet']=options.get('sheet')orsheets[0]

        return(
            row
            forrowindoc.getSheet(sheet)
            ifany(xforxinrowifx.strip())
        )

    def_read_csv(self,options):
        """ReturnsaCSV-parsediteratorofallnon-emptylinesinthefile
            :throwscsv.Error:ifanerrorisdetectedduringCSVparsing
        """
        csv_data=self.fileorb''
        ifnotcsv_data:
            returniter([])

        encoding=options.get('encoding')
        ifnotencoding:
            encoding=options['encoding']=chardet.detect(csv_data)['encoding'].lower()
            #someversionsofchardet(e.g.2.3.0butnot3.x)willreturn
            #utf-(16|32)(le|be),whichforpythonmeans"ignore/don'tstrip
            #BOM".Wedon'twantthat,sorectifytheencodingtonon-marked
            #IFFtheguessedencodingisLE/BEandcsv_datastartswithaBOM
            bom=BOM_MAP.get(encoding)
            ifbomandcsv_data.startswith(bom):
                encoding=options['encoding']=encoding[:-2]

        ifencoding!='utf-8':
            csv_data=csv_data.decode(encoding).encode('utf-8')

        separator=options.get('separator')
        ifnotseparator:
            #defaultforunspecifiedseparatorsousergetsamessageabout
            #havingtospecifyit
            separator=','
            forcandidatein(',',';','\t','','|',unicodedata.lookup('unitseparator')):
                #passthroughtheCSVandcheckifallrowsarethesame
                #length&atleast2-wideassumeit'sthecorrectone
                it=pycompat.csv_reader(io.BytesIO(csv_data),quotechar=options['quoting'],delimiter=candidate)
                w=None
                forrowinit:
                    width=len(row)
                    ifwisNone:
                        w=width
                    ifwidth==1orwidth!=w:
                        break#nextcandidate
                else:#nobreak
                    separator=options['separator']=candidate
                    break

        csv_iterator=pycompat.csv_reader(
            io.BytesIO(csv_data),
            quotechar=options['quoting'],
            delimiter=separator)

        return(
            rowforrowincsv_iterator
            ifany(xforxinrowifx.strip())
        )

    @api.model
    def_try_match_column(self,preview_values,options):
        """Returnsthepotentialfieldtypes,basedonthepreviewvalues,usingheuristics
            :parampreview_values:listofvalueforthecolumntodetermine
            :paramoptions:parsingoptions
        """
        values=set(preview_values)
        #Ifallvaluesareemptyinpreviewthancanbeanyfield
        ifvalues=={''}:
            return['all']

        #Ifallvaluesstartswith__export__thisisprobablyanid
        ifall(v.startswith('__export__')forvinvalues):
            return['id','many2many','many2one','one2many']

        #Ifallvaluescanbecasttointtypeiseitherid,floatormonetary
        #Exception:ifweonlyhave1and0,itcanalsobeaboolean
        ifall(v.isdigit()forvinvaluesifv):
            field_type=['id','integer','char','float','monetary','many2one','many2many','one2many']
            if{'0','1',''}.issuperset(values):
                field_type.append('boolean')
            returnfield_type

        #IfallvaluesareeitherTrueorFalse,typeisboolean
        ifall(val.lower()in('true','false','t','f','')forvalinpreview_values):
            return['boolean']

        #Ifallvaluescanbecasttofloat,typeiseitherfloatormonetary
        results=[]
        try:
            thousand_separator=decimal_separator=False
            forvalinpreview_values:
                val=val.strip()
                ifnotval:
                    continue
                #valuemighthavethecurrencysymbolleftorrightfromthevalue
                val=self._remove_currency_symbol(val)
                ifval:
                    ifoptions.get('float_thousand_separator')andoptions.get('float_decimal_separator'):
                        val=val.replace(options['float_thousand_separator'],'').replace(options['float_decimal_separator'],'.')
                    #Wearenowsurethatthisisafloat,butwestillneedtofindthe
                    #thousandanddecimalseparator
                    else:
                        ifval.count('.')>1:
                            options['float_thousand_separator']='.'
                            options['float_decimal_separator']=','
                        elifval.count(',')>1:
                            options['float_thousand_separator']=','
                            options['float_decimal_separator']='.'
                        elifval.find('.')>val.find(','):
                            thousand_separator=','
                            decimal_separator='.'
                        elifval.find(',')>val.find('.'):
                            thousand_separator='.'
                            decimal_separator=','
                else:
                    #Thisisnotafloatsoexitthistry
                    float('a')
            ifthousand_separatorandnotoptions.get('float_decimal_separator'):
                options['float_thousand_separator']=thousand_separator
                options['float_decimal_separator']=decimal_separator
            results=['float','monetary']
        exceptValueError:
            pass

        results+=self._try_match_date_time(preview_values,options)
        ifresults:
            returnresults

        return['id','text','boolean','char','datetime','selection','many2one','one2many','many2many','html']


    def_try_match_date_time(self,preview_values,options):
        #Oradate/datetimeifitmatchesthepattern
        date_patterns=[options['date_format']]ifoptions.get(
            'date_format')else[]
        user_date_format=self.env['res.lang']._lang_get(self.env.user.lang).date_format
        ifuser_date_format:
            try:
                to_re(user_date_format)
                date_patterns.append(user_date_format)
            exceptKeyError:
                pass
        date_patterns.extend(DATE_PATTERNS)
        match=check_patterns(date_patterns,preview_values)
        ifmatch:
            options['date_format']=match
            return['date','datetime']

        datetime_patterns=[options['datetime_format']]ifoptions.get(
            'datetime_format')else[]
        datetime_patterns.extend(
            "%s%s"%(d,t)
            fordindate_patterns
            fortinTIME_PATTERNS
        )
        match=check_patterns(datetime_patterns,preview_values)
        ifmatch:
            options['datetime_format']=match
            return['datetime']

        return[]

    @api.model
    def_find_type_from_preview(self,options,preview):
        type_fields=[]
        ifpreview:
            forcolumninrange(0,len(preview[0])):
                preview_values=[value[column].strip()forvalueinpreview]
                type_field=self._try_match_column(preview_values,options)
                type_fields.append(type_field)
        returntype_fields

    def_match_header(self,header,fields,options):
        """Attemptstomatchagivenheadertoafieldofthe
            importedmodel.

            :paramstrheader:headernamefromtheCSVfile
            :paramfields:
            :paramdictoptions:
            :returns:anemptylistiftheheadercouldn'tbematched,or
                      allthefieldstotraverse
            :rtype:list(Field)
        """
        string_match=None
        IrTranslation=self.env['ir.translation']
        forfieldinfields:
            #FIXME:shouldmatchalltranslations&original
            #TODO:usestringdistance(levenshtein?hamming?)
            ifheader.lower()==field['name'].lower():
                return[field]
            ifheader.lower()==field['string'].lower():
                #matchingstringarenotreliablewaybecause
                #stringshavenouniqueconstraint
                string_match=field
            translated_header=IrTranslation._get_source('ir.model.fields,field_description','model',self.env.lang,header).lower()
            iftranslated_header==field['string'].lower():
                string_match=field
        ifstring_match:
            #thisbehaviorisonlyappliedifthereisnomatchingfield['name']
            return[string_match]

        if'/'notinheader:
            return[]

        #relationalfieldpath
        traversal=[]
        subfields=fields
        #Iterativelydiveintofieldstree
        forsectioninheader.split('/'):
            #Stripsectionincasespacesareaddedaround'/'for
            #readabilityofpaths
            match=self._match_header(section.strip(),subfields,options)
            #Anymatchfailure,exit
            ifnotmatch:
                return[]
            #prepsubfieldsfornextiterationwithinmatch[0]
            field=match[0]
            subfields=field['fields']
            traversal.append(field)
        returntraversal

    def_match_headers(self,rows,fields,options):
        """Attemptstomatchtheimportedmodel'sfieldstothe
            titlesoftheparsedCSVfile,ifthefileissupposedtohave
            headers.

            Willconsumethefirstlineofthe``rows``iterator.

            Returnsthelistofheadersandadictmappingcellindices
            tokeypathsinthe``fields``tree.Ifheaderswerenot
            requested,bothcollectionsareempty.

            :paramIteratorrows:
            :paramdictfields:
            :paramdictoptions:
            :rtype:(list(str),dict(int:list(str)))
        """
        ifnotoptions.get('headers'):
            return[],{}

        headers=next(rows,None)
        ifnotheaders:
            return[],{}

        matches={}
        mapping_records=self.env['base_import.mapping'].search_read([('res_model','=',self.res_model)],['column_name','field_name'])
        mapping_fields={rec['column_name']:rec['field_name']forrecinmapping_records}
        forindex,headerinenumerate(headers):
            match_field=[]
            mapping_field_name=mapping_fields.get(header.lower())
            ifmapping_field_name:
                match_field=mapping_field_name.split('/')
            ifnotmatch_field:
                match_field=[field['name']forfieldinself._match_header(header,fields,options)]
            matches[index]=match_fieldorNone
        returnheaders,matches

    defparse_preview(self,options,count=10):
        """Generatesapreviewoftheuploadedfiles,andperforms
            fields-matchingbetweentheimport'sfiledataandthemodel's
            columns.

            Iftheheadersarenotrequested(notoptions.headers),
            ``matches``and``headers``areboth``False``.

            :paramintcount:numberofpreviewlinestogenerate
            :paramoptions:format-specificoptions.
                            CSV:{quoting,separator,headers}
            :typeoptions:{str,str,str,bool}
            :returns:{fields,matches,headers,preview}|{error,preview}
            :rtype:{dict(str:dict(...)),dict(int,list(str)),list(str),list(list(str))}|{str,str}
        """
        self.ensure_one()
        fields=self.get_fields(self.res_model)
        try:
            rows=self._read_file(options)
            headers,matches=self._match_headers(rows,fields,options)
            #Matchshouldhaveconsumedthefirstrow(iifheaders),get
            #the``count``nextrowsforpreview
            preview=list(itertools.islice(rows,count))
            assertpreview,"fileseemstohavenocontent"
            header_types=self._find_type_from_preview(options,preview)
            ifoptions.get('keep_matches')andlen(options.get('fields',[])):
                matches={}
                forindex,matchinenumerate(options.get('fields')):
                    ifmatch:
                        matches[index]=match.split('/')

            ifoptions.get('keep_matches'):
                advanced_mode=options.get('advanced')
            else:
                #Checkislabelcontainrelationalfield
                has_relational_header=any(len(models.fix_import_export_id_paths(col))>1forcolinheaders)
                #Checkismatchesfieldshaverelationalfield
                has_relational_match=any(len(match)>1forfield,matchinmatches.items()ifmatch)
                advanced_mode=has_relational_headerorhas_relational_match

            batch=False
            batch_cutoff=options.get('limit')
            ifbatch_cutoff:
                ifcount>batch_cutoff:
                    batch=len(preview)>batch_cutoff
                else:
                    batch=bool(next(
                        itertools.islice(rows,batch_cutoff-count,None),
                        None
                    ))

            return{
                'fields':fields,
                'matches':matchesorFalse,
                'headers':headersorFalse,
                'headers_type':header_typesorFalse,
                'preview':preview,
                'options':options,
                'advanced_mode':advanced_mode,
                'debug':self.user_has_groups('base.group_no_one'),
                'batch':batch,
            }
        exceptExceptionaserror:
            #Duetolazygenerators,UnicodeDecodeError(for
            #instance)mayonlyberaisedwhenserializingthe
            #previewtoalistinthereturn.
            _logger.debug("Errorduringparsingpreview",exc_info=True)
            preview=None
            ifself.file_type=='text/csv'andself.file:
                preview=self.file[:ERROR_PREVIEW_BYTES].decode('iso-8859-1')
            return{
                'error':str(error),
                #iso-8859-1ensuresdecodingwillalwayssucceed,
                #evenifityieldsnon-printablecharacters.Thisis
                #incaseofUnicodeDecodeError(orcsv.Error
                #compoundedwithUnicodeDecodeError)
                'preview':preview,
            }

    @api.model
    def_convert_import_data(self,fields,options):
        """ExtractstheinputBaseModelandfieldslist(with
            ``False``-yplaceholdersforfieldsto*not*import)intoa
            formatModel.import_datacanuse:afieldslistwithoutholes
            andthepreciselymatchingdatamatrix

            :paramlist(str|bool):fields
            :returns:(data,fields)
            :rtype:(list(list(str)),list(str))
            :raisesValueError:incasetheimportdatacouldnotbeconverted
        """
        #Getindicesfornon-emptyfields
        indices=[indexforindex,fieldinenumerate(fields)iffield]
        ifnotindices:
            raiseValueError(_("Youmustconfigureatleastonefieldtoimport"))
        #Ifonlyoneindex,itemgetterwillreturnanatomrather
        #thana1-tuple
        iflen(indices)==1:
            mapper=lambdarow:[row[indices[0]]]
        else:
            mapper=operator.itemgetter(*indices)
        #Getonlylistofactuallyimportedfields
        import_fields=[fforfinfieldsiff]

        rows_to_import=self._read_file(options)
        ifoptions.get('headers'):
            rows_to_import=itertools.islice(rows_to_import,1,None)
        data=[
            list(row)forrowinmap(mapper,rows_to_import)
            #don'ttryinsertingcompletelyemptyrows(e.g.from
            #filteringouto2mfields)
            ifany(row)
        ]

        #slicingneedstohappenafterfilteringoutemptyrowsasthe
        #dataoffsetsfromloadarepost-filtering
        returndata[options.get('skip'):],import_fields

    @api.model
    def_remove_currency_symbol(self,value):
        value=value.strip()
        negative=False
        #Carefulthatsomecountriesuse()fornegativesoreplaceitby-sign
        ifvalue.startswith('(')andvalue.endswith(')'):
            value=value[1:-1]
            negative=True
        float_regex=re.compile(r'([+-]?[0-9.,]+)')
        split_value=[gforginfloat_regex.split(value)ifg]
        iflen(split_value)>2:
            #Thisisprobablynotafloat
            returnFalse
        iflen(split_value)==1:
            iffloat_regex.search(split_value[0])isnotNone:
                returnsplit_value[0]ifnotnegativeelse'-'+split_value[0]
            returnFalse
        else:
            #Stringhasbeensplitin2,locatewhichindexcontainsthefloatandwhichdoesnot
            currency_index=0
            iffloat_regex.search(split_value[0])isnotNone:
                currency_index=1
            #Checkthatcurrencyexists
            currency=self.env['res.currency'].search([('symbol','=',split_value[currency_index].strip())])
            iflen(currency):
                returnsplit_value[(currency_index+1)%2]ifnotnegativeelse'-'+split_value[(currency_index+1)%2]
            #Otherwiseitisnotafloatwithacurrencysymbol
            returnFalse

    @api.model
    def_parse_float_from_data(self,data,index,name,options):
        forlineindata:
            line[index]=line[index].strip()
            ifnotline[index]:
                continue
            thousand_separator,decimal_separator=self._infer_separators(line[index],options)

            if'E'inline[index]or'e'inline[index]:
                tmp_value=line[index].replace(thousand_separator,'.')
                try:
                    tmp_value='{:f}'.format(float(tmp_value))
                    line[index]=tmp_value
                    thousand_separator=''
                exceptException:
                    pass

            line[index]=line[index].replace(thousand_separator,'').replace(decimal_separator,'.')
            old_value=line[index]
            line[index]=self._remove_currency_symbol(line[index])
            ifline[index]isFalse:
                raiseValueError(_("Column%scontainsincorrectvalues(value:%s)",name,old_value))

    def_infer_separators(self,value,options):
        """Trytoinfertheshapeoftheseparators:iftherearetwo
        different"non-numberic"charactersinthenumber,the
        former/duplicatedonewouldbegrouping("thousands"separator)and
        thelatterwouldbethedecimalseparator.Thedecimalseparator
        shouldfurthermorebeunique.
        """
        #can'tuse\p{Sc}usingresohandrollit
        non_number=[
            #anycharacter
            cforcinvalue
            #whichisnotanumericdecoration(()isusedfornegative
            #byaccountants)
            ifcnotin'()-+'
            #whichisnotadigitoracurrencysymbol
            ifunicodedata.category(c)notin('Nd','Sc')
        ]

        counts=collections.Counter(non_number)
        #ifwehavetwonon-numbers*and*thelastonehasacountof1,
        #weprobablyhavegrouping&decimalseparators
        iflen(counts)==2andcounts[non_number[-1]]==1:
            return[characterforcharacter,_countincounts.most_common()]

        #otherwisegetwhatever'sintheoptions,orfallbacktoadefault
        thousand_separator=options.get('float_thousand_separator','')
        decimal_separator=options.get('float_decimal_separator','.')
        returnthousand_separator,decimal_separator

    def_parse_import_data(self,data,import_fields,options):
        """Lauchfirstcallto_parse_import_data_recursivewithan
        emptyprefix._parse_import_data_recursivewillberun
        recursivelyforeachrelationalfield.
        """
        returnself._parse_import_data_recursive(self.res_model,'',data,import_fields,options)

    def_parse_import_data_recursive(self,model,prefix,data,import_fields,options):
        #Getfieldsoftypedate/datetime
        all_fields=self.env[model].fields_get()
        forname,fieldinall_fields.items():
            name=prefix+name
            iffield['type']in('date','datetime')andnameinimport_fields:
                index=import_fields.index(name)
                self._parse_date_from_data(data,index,name,field['type'],options)
            #Checkifthefieldisinimport_fieldandisarelational(followedby/)
            #Alsoverifythatthefieldnameexactlymatchtheimport_fieldatthecorrectlevel.
            elifany(name+'/'inimport_fieldandname==import_field.split('/')[prefix.count('/')]forimport_fieldinimport_fields):
                #Recursivecallwiththerelationalasnewmodelandaddthefieldnametotheprefix
                self._parse_import_data_recursive(field['relation'],name+'/',data,import_fields,options)
            eliffield['type']in('float','monetary')andnameinimport_fields:
                #Parsefloat,sometimesfloatvaluesfromfilehavecurrencysymbolor()todenoteanegativevalue
                #Weshouldbeabletomanagebothcase
                index=import_fields.index(name)
                self._parse_float_from_data(data,index,name,options)
            eliffield['type']=='binary'andfield.get('attachment')andany(finnameforfinIMAGE_FIELDS)andnameinimport_fields:
                index=import_fields.index(name)

                withrequests.Session()assession:
                    session.stream=True

                    fornum,lineinenumerate(data):
                        ifre.match(config.get("import_image_regex",DEFAULT_IMAGE_REGEX),line[index]):
                            ifnotself.env.user._can_import_remote_urls():
                                raiseAccessError(_("YoucannotimportimagesviaURL,checkwithyouradministratororsupportforthereason."))

                            line[index]=self._import_image_by_url(line[index],session,name,num)
                        else:
                            try:
                                base64.b64decode(line[index],validate=True)
                            exceptbinascii.Error:
                                raiseValueError(_("Foundinvalidimagedata,imagesshouldbeimportedaseitherURLsorbase64-encodeddata."))

        returndata

    def_parse_date_from_data(self,data,index,name,field_type,options):
        dt=datetime.datetime
        fmt=fields.Date.to_stringiffield_type=='date'elsefields.Datetime.to_string
        d_fmt=options.get('date_format')
        dt_fmt=options.get('datetime_format')
        fornum,lineinenumerate(data):
            ifnotline[index]:
                continue

            v=line[index].strip()
            try:
                #firsttryparsingasadatetimeifit'sone
                ifdt_fmtandfield_type=='datetime':
                    try:
                        line[index]=fmt(dt.strptime(v,dt_fmt))
                        continue
                    exceptValueError:
                        pass
                #otherwisetryparsingasadatewhetherit'sadate
                #ordatetime
                line[index]=fmt(dt.strptime(v,d_fmt))
            exceptValueErrorase:
                raiseValueError(_("Column%scontainsincorrectvalues.Errorinline%d:%s")%(name,num+1,e))
            exceptExceptionase:
                raiseValueError(_("ErrorParsingDate[%s:L%d]:%s")%(name,num+1,e))

    def_import_image_by_url(self,url,session,field,line_number):
        """ImportsanimagebyURL

        :paramstrurl:theoriginalfieldvalue
        :paramrequests.Sessionsession:
        :paramstrfield:nameofthefield(forlogging/debugging)
        :paramintline_number:0-indexedlinenumberwithintheimportedfile(forlogging/debugging)
        :return:thereplacementvalue
        :rtype:bytes
        """
        maxsize=int(config.get("import_image_maxbytes",DEFAULT_IMAGE_MAXBYTES))
        _logger.debug("TryingtoimportimagefromURL:%sintofield%s,atline%s"%(url,field,line_number))
        try:
            response=session.get(url,timeout=int(config.get("import_image_timeout",DEFAULT_IMAGE_TIMEOUT)))
            response.raise_for_status()

            ifresponse.headers.get('Content-Length')andint(response.headers['Content-Length'])>maxsize:
                raiseValueError(_("Filesizeexceedsconfiguredmaximum(%sbytes)",maxsize))

            content=bytearray()
            forchunkinresponse.iter_content(DEFAULT_IMAGE_CHUNK_SIZE):
                content+=chunk
                iflen(content)>maxsize:
                    raiseValueError(_("Filesizeexceedsconfiguredmaximum(%sbytes)",maxsize))

            image=Image.open(io.BytesIO(content))
            w,h=image.size
            ifw*h>42e6: #NokiaLumia1020photoresolution
                raiseValueError(
                    u"Imagesizeexcessive,importedimagesmustbesmaller"
                    u"than42millionpixel")

            returnbase64.b64encode(content)
        exceptExceptionase:
            _logger.warning(e,exc_info=True)
            raiseValueError(_("CouldnotretrieveURL:%(url)s[%(field_name)s:L%(line_number)d]:%(error)s")%{
                'url':url,
                'field_name':field,
                'line_number':line_number+1,
                'error':e
            })

    defdo(self,fields,columns,options,dryrun=False):
        """Actualexecutionoftheimport

        :paramfields:importmapping:mapseachcolumntoafield,
                       ``False``forthecolumnstoignore
        :typefields:list(str|bool)
        :paramcolumns:columnslabel
        :typecolumns:list(str|bool)
        :paramdictoptions:
        :parambooldryrun:performsallimportoperations(and
                            validations)butrollbackswrites,allows
                            gettingasmucherrorsaspossiblewithout
                            theriskofclobberingthedatabase.
        :returns:Alistoferrors.Ifthelistisemptytheimport
                  executedfullyandcorrectly.Ifthelistis
                  non-emptyitcontainsdictswith3keys``type``the
                  typeoferror(``error|warning``);``message``the
                  errormessageassociatedwiththeerror(astring)
                  and``record``thedatawhichfailedtoimport(or
                  ``false``ifthatdataisn'tavailableorprovided)
        :rtype:dict(ids:list(int),messages:list({type,message,record}))
        """
        self.ensure_one()
        self._cr.execute('SAVEPOINTimport')

        try:
            data,import_fields=self._convert_import_data(fields,options)
            #Parsedateandfloatfield
            data=self._parse_import_data(data,import_fields,options)
        exceptValueErroraserror:
            return{
                'messages':[{
                    'type':'error',
                    'message':str(error),
                    'record':False,
                }]
            }

        _logger.info('importing%drows...',len(data))

        name_create_enabled_fields=options.pop('name_create_enabled_fields',{})
        import_limit=options.pop('limit',None)
        model=self.env[self.res_model].with_context(import_file=True,name_create_enabled_fields=name_create_enabled_fields,_import_limit=import_limit)
        import_result=model.load(import_fields,data)
        _logger.info('done')

        #Iftransactionaborted,RELEASESAVEPOINTisgoingtoraise
        #anInternalError(ROLLBACKshouldwork,maybe).Ignorethat.
        #TODO:tohandlemultipleerrors,createsavepointaround
        #      writeandreleaseitincaseofwriteerror(after
        #      addingerrortoerrorsarray)=>cankeepontryingto
        #      importstuff,androllbackattheendifthereisany
        #      errorintheresults.
        try:
            ifdryrun:
                self._cr.execute('ROLLBACKTOSAVEPOINTimport')
                #cancelallchangesdonetotheregistry/ormcache
                self.pool.clear_caches()
                self.pool.reset_changes()
            else:
                self._cr.execute('RELEASESAVEPOINTimport')
        exceptpsycopg2.InternalError:
            pass

        #Insert/Updatemappingcolumnswhenimportcompletesuccessfully
        ifimport_result['ids']andoptions.get('headers'):
            BaseImportMapping=self.env['base_import.mapping']
            forindex,column_nameinenumerate(columns):
                ifcolumn_name:
                    #Updatetolatestselectedfield
                    mapping_domain=[('res_model','=',self.res_model),('column_name','=',column_name)]
                    column_mapping=BaseImportMapping.search(mapping_domain,limit=1)
                    ifcolumn_mapping:
                        ifcolumn_mapping.field_name!=fields[index]:
                            column_mapping.field_name=fields[index]
                    else:
                        BaseImportMapping.create({
                            'res_model':self.res_model,
                            'column_name':column_name,
                            'field_name':fields[index]
                        })
        if'name'inimport_fields:
            index_of_name=import_fields.index('name')
            skipped=options.get('skip',0)
            #padfrontasdatadoesn'tcontainanythigforskippedlines
            r=import_result['name']=['']*skipped
            #onlyaddnamesforthewindowbeingimported
            r.extend(x[index_of_name]forxindata[:import_limit])
            #padback(thoughthat'sprobablynotuseful)
            r.extend(['']*(len(data)-(import_limitor0)))
        else:
            import_result['name']=[]

        skip=options.get('skip',0)
        #convertload'sinternalnextrowtotheimportedfile's
        ifimport_result['nextrow']:#don'tupdateifnextrow=0(=nonextrow)
            import_result['nextrow']+=skip

        returnimport_result

_SEPARATORS=['','/','-','']
_PATTERN_BASELINE=[
    ('%m','%d','%Y'),
    ('%d','%m','%Y'),
    ('%Y','%m','%d'),
    ('%Y','%d','%m'),
]
DATE_FORMATS=[]
#takethebaselineformatandduplicateperformingthefollowing
#substitution:longyear->shortyear,numericalmonth->short
#month,numericalmonth->longmonth.Eachsubstitutionbuildson
#theprevioustwo
forpsin_PATTERN_BASELINE:
    patterns={ps}
    fors,tin[('%Y','%y')]:
        patterns.update([#needlistcomp:withgenexpr"setchangedsizeduringiteration"
            tuple(tifit==selseitforitinf)
            forfinpatterns
        ])
    DATE_FORMATS.extend(patterns)
DATE_PATTERNS=[
    sep.join(fmt)
    forsepin_SEPARATORS
    forfmtinDATE_FORMATS
]
TIME_PATTERNS=[
    '%H:%M:%S','%H:%M','%H',#24h
    '%I:%M:%S%p','%I:%M%p','%I%p',#12h
]

defcheck_patterns(patterns,values):
    forpatterninpatterns:
        p=to_re(pattern)
        forvalinvalues:
            ifvalandnotp.match(val):
                break

        else: #nobreak,allmatch
            returnpattern

    returnNone

defto_re(pattern):
    """cutdownversionofTimeREconvertingstrptimepatternstoregex
    """
    pattern=re.sub(r'\s+',r'\\s+',pattern)
    pattern=re.sub('%([a-z])',_replacer,pattern,flags=re.IGNORECASE)
    pattern='^'+pattern+'$'
    returnre.compile(pattern,re.IGNORECASE)
def_replacer(m):
    return_P_TO_RE[m.group(1)]

_P_TO_RE={
    'd':r"(3[0-1]|[1-2]\d|0[1-9]|[1-9]|[1-9])",
    'H':r"(2[0-3]|[0-1]\d|\d)",
    'I':r"(1[0-2]|0[1-9]|[1-9])",
    'm':r"(1[0-2]|0[1-9]|[1-9])",
    'M':r"([0-5]\d|\d)",
    'S':r"(6[0-1]|[0-5]\d|\d)",
    'y':r"(\d\d)",
    'Y':r"(\d\d\d\d)",

    'p':r"(am|pm)",

    '%':'%',
}
