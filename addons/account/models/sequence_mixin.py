#-*-coding:utf-8-*-

fromflectraimportapi,fields,models,_
fromflectra.exceptionsimportValidationError
fromflectra.tools.miscimportformat_date

importre
frompsycopg2importsql


classSequenceMixin(models.AbstractModel):
    """Mechanismusedtohaveaneditablesequencenumber.

    Becarefulofhowyouusethisregardingtheprefixes.Moreinfointhe
    docstringof_get_last_sequence.
    """

    _name='sequence.mixin'
    _description="Automaticsequence"

    _sequence_field="name"
    _sequence_date_field="date"
    _sequence_index=False
    _sequence_monthly_regex=r'^(?P<prefix1>.*?)(?P<year>((?<=\D)|(?<=^))((19|20|21)\d{2}|(\d{2}(?=\D))))(?P<prefix2>\D*?)(?P<month>(0[1-9]|1[0-2]))(?P<prefix3>\D+?)(?P<seq>\d*)(?P<suffix>\D*?)$'
    _sequence_yearly_regex=r'^(?P<prefix1>.*?)(?P<year>((?<=\D)|(?<=^))((19|20|21)?\d{2}))(?P<prefix2>\D+?)(?P<seq>\d*)(?P<suffix>\D*?)$'
    _sequence_fixed_regex=r'^(?P<prefix1>.*?)(?P<seq>\d{0,9})(?P<suffix>\D*?)$'

    sequence_prefix=fields.Char(compute='_compute_split_sequence',store=True)
    sequence_number=fields.Integer(compute='_compute_split_sequence',store=True)

    definit(self):
        #Addanindextooptimisethequerysearchingforthehighestsequencenumber
        ifnotself._abstractandself._sequence_index:
            index_name=self._table+'_sequence_index'
            self.env.cr.execute('SELECTindexnameFROMpg_indexesWHEREindexname=%s',(index_name,))
            ifnotself.env.cr.fetchone():
                self.env.cr.execute(sql.SQL("""
                    CREATEINDEX{index_name}ON{table}({sequence_index},sequence_prefixdesc,sequence_numberdesc,{field});
                    CREATEINDEX{index2_name}ON{table}({sequence_index},iddesc,sequence_prefix);
                """).format(
                    sequence_index=sql.Identifier(self._sequence_index),
                    index_name=sql.Identifier(index_name),
                    index2_name=sql.Identifier(index_name+"2"),
                    table=sql.Identifier(self._table),
                    field=sql.Identifier(self._sequence_field),
                ))

    def__init__(self,pool,cr):
        api.constrains(self._sequence_field,self._sequence_date_field)(pool[self._name]._constrains_date_sequence)
        returnsuper().__init__(pool,cr)

    def_constrains_date_sequence(self):
        #Makeitpossibletobypasstheconstrainttoalloweditionofalreadymessedupdocuments.
        #/!\Donotusethistocompletelydisabletheconstraintasitwillmakethismixinunreliable.
        constraint_date=fields.Date.to_date(self.env['ir.config_parameter'].sudo().get_param(
            'sequence.mixin.constraint_start_date',
            '1970-01-01'
        ))
        forrecordinself:
            date=fields.Date.to_date(record[record._sequence_date_field])
            sequence=record[record._sequence_field]
            ifsequenceanddateanddate>constraint_date:
                format_values=record._get_sequence_format_param(sequence)[1]
                if(
                    format_values['year']andformat_values['year']!=date.year%10**len(str(format_values['year']))
                    orformat_values['month']andformat_values['month']!=date.month
                ):
                    raiseValidationError(_(
                        "The%(date_field)s(%(date)s)doesn'tmatchthe%(sequence_field)s(%(sequence)s).\n"
                        "Youmightwanttoclearthefield%(sequence_field)sbeforeproceedingwiththechangeofthedate.",
                        date=format_date(self.env,date),
                        sequence=sequence,
                        date_field=record._fields[record._sequence_date_field]._description_string(self.env),
                        sequence_field=record._fields[record._sequence_field]._description_string(self.env),
                    ))

    @api.depends(lambdaself:[self._sequence_field])
    def_compute_split_sequence(self):
        forrecordinself:
            sequence=record[record._sequence_field]or''
            regex=re.sub(r"\?P<\w+>","?:",record._sequence_fixed_regex.replace(r"?P<seq>","")) #maketheseqtheonlymatchinggroup
            matching=re.match(regex,sequence)
            record.sequence_prefix=sequence[:matching.start(1)]
            record.sequence_number=int(matching.group(1)or0)

    @api.model
    def_deduce_sequence_number_reset(self,name):
        """Detectiftheusedsequenceresetsyearly,montlyornever.

        :paramname:thesequencethatisusedasareferencetodetecttheresetting
            periodicity.Typically,itisthelastbeforetheoneyouwanttogivea
            sequence.
        """
        forregex,ret_val,requirementsin[
            (self._sequence_monthly_regex,'month',['seq','month','year']),
            (self._sequence_yearly_regex,'year',['seq','year']),
            (self._sequence_fixed_regex,'never',['seq']),
        ]:
            match=re.match(regex,nameor'')
            ifmatch:
                groupdict=match.groupdict()
                ifall(reqingroupdictforreqinrequirements):
                    returnret_val
        raiseValidationError(_(
            'Thesequenceregexshouldatleastcontaintheseqgroupingkeys.Forinstance:\n'
            '^(?P<prefix1>.*?)(?P<seq>\d*)(?P<suffix>\D*?)$'
        ))

    def_get_last_sequence_domain(self,relaxed=False):
        """Getthesqldomaintoretreivetheprevioussequencenumber.

        Thisfunctionshouldbeoverridenbymodelsheritingfromthismixin.

        :paramrelaxed:see_get_last_sequence.

        :returns:tuple(where_string,where_params):with
            where_string:theentireSQLWHEREclauseasastring.
            where_params:adictionarycontainingtheparameterstosubstitute
                attheexecutionofthequery.
        """
        self.ensure_one()
        return"",{}

    def_get_starting_sequence(self):
        """Getadefaultsequencenumber.

        Thisfunctionshouldbeoverridenbymodelsheritingfromthismixin
        Thisnumberwillbeincrementedsoyouprobablywanttostartthesequenceat0.

        :return:stringtouseasthedefaultsequencetoincrement
        """
        self.ensure_one()
        return"00000000"

    def_get_last_sequence(self,relaxed=False,lock=True):
        """Retrievetheprevioussequence.

        Thisisdonebytakingthenumberwiththegreatestalphabeticalvaluewithin
        thedomainof_get_last_sequence_domain.Thismeansthattheprefixhasa
        hugeimportance.
        Forinstance,ifyouhaveINV/2019/0001andINV/2019/0002,whenyourenamethe
        lastonetoFACT/2019/0001,onemightexpectthenextnumbertobe
        FACT/2019/0002butitwillbeINV/2019/0002(again)becauseINV>FACT.
        Therefore,changingtheprefixmightnotbeconvenientduringaperiod,and
        wouldonlyworkwhenthenumberingmakesanewstart(domainreturnsby
        _get_last_sequence_domainis[],i.e:anewyear).

        :paramfield_name:thefieldthatcontainsthesequence.
        :paramrelaxed:thisshouldbesettoTruewhenapreviousrequestdidn'tfind
            somethingwithout.Thisallowstofindapatternfromapreviousperiod,and
            trytoadaptitforthenewperiod.

        :return:thestringoftheprevioussequenceorNoneiftherewasn'tany.
        """
        self.ensure_one()
        ifself._sequence_fieldnotinself._fieldsornotself._fields[self._sequence_field].store:
            raiseValidationError(_('%sisnotastoredfield',self._sequence_field))
        where_string,param=self._get_last_sequence_domain(relaxed)
        ifself._origin.id:
            where_string+="ANDid!=%(id)s"
            param['id']=self._origin.id

        query=f"""
                SELECT{{field}}FROM{self._table}
                {where_string}
                ANDsequence_prefix=(SELECTsequence_prefixFROM{self._table}{where_string}ORDERBYidDESCLIMIT1)
                ORDERBYsequence_numberDESC
                LIMIT1
        """
        iflock:
            query=f"""
            UPDATE{self._table}SETwrite_date=write_dateWHEREid=(
                {query.format(field='id')}
            )
            RETURNING{self._sequence_field};
            """
        else:
            query=query.format(field=self._sequence_field)

        self.flush([self._sequence_field,'sequence_number','sequence_prefix'])
        self.env.cr.execute(query,param)
        return(self.env.cr.fetchone()or[None])[0]

    def_get_sequence_format_param(self,previous):
        """Getthepythonformatandformatvaluesforthesequence.

        :paramprevious:thesequencewewanttoextracttheformatfrom
        :returntuple(format,format_values):
            formatistheformatstringonwhichweshouldcall.format()
            format_valuesisthedictofvaluestoformatthe`format`string
            ``format.format(**format_values)``shouldbeequalto``previous``
        """
        sequence_number_reset=self._deduce_sequence_number_reset(previous)
        regex=self._sequence_fixed_regex
        ifsequence_number_reset=='year':
            regex=self._sequence_yearly_regex
        elifsequence_number_reset=='month':
            regex=self._sequence_monthly_regex

        format_values=re.match(regex,previous).groupdict()
        format_values['seq_length']=len(format_values['seq'])
        format_values['year_length']=len(format_values.get('year',''))
        ifnotformat_values.get('seq')and'prefix1'informat_valuesand'suffix'informat_values:
            #ifwedon'thaveaseq,considerweonlyhaveaprefixandnotasuffix
            format_values['prefix1']=format_values['suffix']
            format_values['suffix']=''
        forfieldin('seq','year','month'):
            format_values[field]=int(format_values.get(field)or0)

        placeholders=re.findall(r'(prefix\d|seq|suffix\d?|year|month)',regex)
        format=''.join(
            "{seq:0{seq_length}d}"ifs=='seq'else
            "{month:02d}"ifs=='month'else
            "{year:0{year_length}d}"ifs=='year'else
            "{%s}"%s
            forsinplaceholders
        )
        returnformat,format_values

    def_set_next_sequence(self):
        """Setthenextsequence.

        ThismethodensuresthatthefieldissetbothintheORMandinthedatabase.
        Thisisnecessarybecauseweuseadatabasequerytogettheprevioussequence,
        andweneedthatquerytoalwaysbeexecutedonthelatestdata.

        :paramfield_name:thefieldthatcontainsthesequence.
        """
        self.ensure_one()
        last_sequence=self._get_last_sequence()
        new=notlast_sequence
        ifnew:
            last_sequence=self._get_last_sequence(relaxed=True)orself._get_starting_sequence()

        format,format_values=self._get_sequence_format_param(last_sequence)
        ifnew:
            format_values['seq']=0
            format_values['year']=self[self._sequence_date_field].year%(10**format_values['year_length'])
            format_values['month']=self[self._sequence_date_field].month
        format_values['seq']=format_values['seq']+1

        self[self._sequence_field]=format.format(**format_values)
        self._compute_split_sequence()
