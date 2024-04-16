#-*-coding:utf-8-*-
importbabel.dates
importpytz
fromlxmlimportetree
importbase64
importjson

fromflectraimport_,_lt,api,fields,models
fromflectra.osv.expressionimportAND,TRUE_DOMAIN,normalize_domain
fromflectra.toolsimportdate_utils,lazy
fromflectra.tools.miscimportget_lang
fromflectra.exceptionsimportUserError
fromcollectionsimportdefaultdict

SEARCH_PANEL_ERROR_MESSAGE=_lt("Toomanyitemstodisplay.")

defis_true_domain(domain):
    returnnormalize_domain(domain)==TRUE_DOMAIN


classlazymapping(defaultdict):
    def__missing__(self,key):
        value=self.default_factory(key)
        self[key]=value
        returnvalue

DISPLAY_DATE_FORMATS={
    'day':'ddMMMyyyy',
    'week':"'W'wYYYY",
    'month':'MMMMyyyy',
    'quarter':'QQQyyyy',
    'year':'yyyy',
}


classIrActionsActWindowView(models.Model):
    _inherit='ir.actions.act_window.view'

    view_mode=fields.Selection(selection_add=[
        ('qweb','QWeb')
    ],ondelete={'qweb':'cascade'})


classBase(models.AbstractModel):
    _inherit='base'

    @api.model
    defweb_search_read(self,domain=None,fields=None,offset=0,limit=None,order=None):
        """
        Performsasearch_readandasearch_count.

        :paramdomain:searchdomain
        :paramfields:listoffieldstoread
        :paramlimit:maximumnumberofrecordstoread
        :paramoffset:numberofrecordstoskip
        :paramorder:columnstosortresults
        :return:{
            'records':arrayofreadrecords(resultofacallto'search_read')
            'length':numberofrecordsmatchingthedomain(resultofacallto'search_count')
        }
        """
        records=self.search_read(domain,fields,offset=offset,limit=limit,order=order)
        ifnotrecords:
            return{
                'length':0,
                'records':[]
            }
        iflimitand(len(records)==limitorself.env.context.get('force_search_count')):
            length=self.search_count(domain)
        else:
            length=len(records)+offset
        return{
            'length':length,
            'records':records
        }

    @api.model
    defweb_read_group(self,domain,fields,groupby,limit=None,offset=0,orderby=False,
                       lazy=True,expand=False,expand_limit=None,expand_orderby=False):
        """
        Returnstheresultofaread_group(andoptionallysearchforandreadrecordsinsideeach
        group),andthetotalnumberofgroupsmatchingthesearchdomain.

        :paramdomain:searchdomain
        :paramfields:listoffieldstoread(see``fields```paramof``read_group``)
        :paramgroupby:listoffieldstogroupon(see``groupby```paramof``read_group``)
        :paramlimit:see``limit``paramof``read_group``
        :paramoffset:see``offset``paramof``read_group``
        :paramorderby:see``orderby``paramof``read_group``
        :paramlazy:see``lazy``paramof``read_group``
        :paramexpand:iftrue,andgroupbyonlycontainsonefield,readrecordsinsideeachgroup
        :paramexpand_limit:maximumnumberofrecordstoreadineachgroup
        :paramexpand_orderby:ordertoapplywhenreadingrecordsineachgroup
        :return:{
            'groups':arrayofreadgroups
            'length':totalnumberofgroups
        }
        """
        groups=self._web_read_group(domain,fields,groupby,limit,offset,orderby,lazy,expand,
                                      expand_limit,expand_orderby)

        ifnotgroups:
            length=0
        eliflimitandlen(groups)==limit:
            #Weneedtofetchallgroupstoknowthetotalnumber
            #thiscannotbedoneallatoncetoavoidMemoryError
            length=limit
            chunk_size=100000
            whileTrue:
                more=len(self.read_group(domain,['display_name'],groupby,offset=length,limit=chunk_size,lazy=True))
                length+=more
                ifmore<chunk_size:
                    break
        else:
            length=len(groups)+offset
        return{
            'groups':groups,
            'length':length
        }

    @api.model
    def_web_read_group(self,domain,fields,groupby,limit=None,offset=0,orderby=False,
                        lazy=True,expand=False,expand_limit=None,expand_orderby=False):
        """
        Performsaread_groupandoptionallyaweb_search_readforeachgroup.
        See``web_read_group``forparamsdescription.

        :returns:arrayofgroups
        """
        groups=self.read_group(domain,fields,groupby,offset=offset,limit=limit,
                                 orderby=orderby,lazy=lazy)

        ifexpandandlen(groupby)==1:
            forgroupingroups:
                group['__data']=self.web_search_read(domain=group['__domain'],fields=fields,
                                                       offset=0,limit=expand_limit,
                                                       order=expand_orderby)

        returngroups

    @api.model
    defread_progress_bar(self,domain,group_by,progress_bar):
        """
        Getsthedataneededforallthekanbancolumnprogressbars.
        Thesearefetchedalongsideread_groupoperation.

        :paramdomain-thedomainusedinthekanbanviewtofilterrecords
        :paramgroup_by-thenameofthefieldusedtogrouprecordsinto
                        kanbancolumns
        :paramprogress_bar-the<progressbar/>declarationattributes
                            (field,colors,sum)
        :returnadictionnarymappinggroup_byvaluestodictionnariesmapping
                progressbarfieldvaluestotherelatednumberofrecords
        """
        group_by_fname=group_by.partition(':')[0]
        field_type=self._fields[group_by_fname].type
        iffield_type=='selection':
            selection_labels=dict(self.fields_get()[group_by]['selection'])

        defadapt(value):
            iffield_type=='selection':
                value=selection_labels.get(value,False)
            ifisinstance(value,tuple):
                value=value[1] #FIXMEshouldusetechnicalvalue(0)
            returnvalue

        result={}
        forgroupinself._read_progress_bar(domain,group_by,progress_bar):
            group_by_value=str(adapt(group[group_by]))
            field_value=group[progress_bar['field']]
            ifgroup_by_valuenotinresult:
                result[group_by_value]=dict.fromkeys(progress_bar['colors'],0)
            iffield_valueinresult[group_by_value]:
                result[group_by_value][field_value]+=group['__count']
        returnresult

    def_read_progress_bar(self,domain,group_by,progress_bar):
        """Implementationofread_progress_bar()thatreturnsresultsinthe
            formatofread_group().
        """
        try:
            fname=progress_bar['field']
            returnself.read_group(domain,[fname],[group_by,fname],lazy=False)
        exceptUserError:
            #possiblyfailedbecauseofgroupingonoraggregatingnon-stored
            #field;fallbackonalternativeimplementation
            pass

        #Workaroundtomatchread_group'sinfrastructure
        #TODOinmaster:harmonizethisfunctionandreadgrouptoallowfactorization
        group_by_name=group_by.partition(':')[0]
        group_by_modifier=group_by.partition(':')[2]or'month'

        records_values=self.search_read(domainor[],[progress_bar['field'],group_by_name])
        field_type=self._fields[group_by_name].type

        forrecord_valuesinrecords_values:
            group_by_value=record_values.pop(group_by_name)

            #Again,imitatingwhat_read_group_format_resultand_read_group_prepare_datado
            ifgroup_by_valueandfield_typein['date','datetime']:
                locale=get_lang(self.env).code
                group_by_value=date_utils.start_of(fields.Datetime.to_datetime(group_by_value),group_by_modifier)
                group_by_value=pytz.timezone('UTC').localize(group_by_value)
                tz_info=None
                iffield_type=='datetime'andself._context.get('tz')inpytz.all_timezones:
                    tz_info=self._context.get('tz')
                    group_by_value=babel.dates.format_datetime(
                        group_by_value,format=DISPLAY_DATE_FORMATS[group_by_modifier],
                        tzinfo=tz_info,locale=locale)
                else:
                    group_by_value=babel.dates.format_date(
                        group_by_value,format=DISPLAY_DATE_FORMATS[group_by_modifier],
                        locale=locale)

            record_values[group_by]=group_by_value
            record_values['__count']=1

        returnrecords_values

    #####qwebviewhooks#####
    @api.model
    defqweb_render_view(self,view_id,domain):
        assertview_id
        returnself.env['ir.qweb']._render(
            view_id,{
            **self.env['ir.ui.view']._prepare_qcontext(),
            **self._qweb_prepare_qcontext(view_id,domain),
        })

    def_qweb_prepare_qcontext(self,view_id,domain):
        """
        Baseqcontextforrenderingqwebviewsboundtothismodel
        """
        return{
            'model':self,
            'domain':domain,
            #notnecessarilynecessaryasenvisalreadypartofthe
            #non-minimalqcontext
            'context':self.env.context,
            'records':lazy(self.search,domain),
        }

    @api.model
    deffields_view_get(self,view_id=None,view_type='form',toolbar=False,submenu=False):
        r=super().fields_view_get(view_id,view_type,toolbar,submenu)
        #avoidleakingtheraw(un-rendered)template,alsoavoidsbloating
        #theresponsepayloadfornoreason.Onlysendtherootnode,
        #tosendattributessuchas`js_class`.
        ifr['type']=='qweb':
            root=etree.fromstring(r['arch'])
            r['arch']=etree.tostring(etree.Element('qweb',root.attrib))
        returnr

    @api.model
    def_search_panel_field_image(self,field_name,**kwargs):
        """
        Returnthevaluesintheimageoftheprovideddomainbyfield_name.

        :parammodel_domain:domainwhoseimageisreturned
        :paramextra_domain:extradomaintousewhencountingrecordsassociatedwithfieldvalues
        :paramfield_name:thenameofafield(typemany2oneorselection)
        :paramenable_counters:whethertosetthekey'__count'inimagevalues
        :paramonly_counters:whethertoretrieveinformationonthemodel_domainimageoronly
                                countsbasedonmodel_domainandextra_domain.Inthelatercase,
                                thecountsaresetwhateverisenable_counters.
        :paramlimit:integer,maximalnumberofvaluestofetch
        :paramset_limit:boolean,whethertousetheprovidedlimit(ifany)
        :return:adictoftheform
                    {
                        id:{'id':id,'display_name':display_name,('__count':c,)},
                        ...
                    }
        """

        enable_counters=kwargs.get('enable_counters')
        only_counters=kwargs.get('only_counters')
        extra_domain=kwargs.get('extra_domain',[])
        no_extra=is_true_domain(extra_domain)
        model_domain=kwargs.get('model_domain',[])
        count_domain=AND([model_domain,extra_domain])

        limit=kwargs.get('limit')
        set_limit=kwargs.get('set_limit')

        ifonly_counters:
            returnself._search_panel_domain_image(field_name,count_domain,True)

        model_domain_image=self._search_panel_domain_image(field_name,model_domain,
                            enable_countersandno_extra,
                            set_limitandlimit,
                        )
        ifenable_countersandnotno_extra:
            count_domain_image=self._search_panel_domain_image(field_name,count_domain,True)
            forid,valuesinmodel_domain_image.items():
                element=count_domain_image.get(id)
                values['__count']=element['__count']ifelementelse0

        returnmodel_domain_image

    @api.model
    def_search_panel_domain_image(self,field_name,domain,set_count=False,limit=False):
        """
        Returnthevaluesintheimageoftheprovideddomainbyfield_name.

        :paramdomain:domainwhoseimageisreturned
        :paramfield_name:thenameofafield(typemany2oneorselection)
        :paramset_count:whethertosetthekey'__count'inimagevalues.DefaultisFalse.
        :paramlimit:integer,maximalnumberofvaluestofetch.DefaultisFalse.
        :return:adictoftheform
                    {
                        id:{'id':id,'display_name':display_name,('__count':c,)},
                        ...
                    }
        """
        field=self._fields[field_name]
        iffield.type=='many2one':
            defgroup_id_name(value):
                returnvalue

        else:
            #fieldtypeisselection:seedocabove
            desc=self.fields_get([field_name])[field_name]
            field_name_selection=dict(desc['selection'])

            defgroup_id_name(value):
                returnvalue,field_name_selection[value]

        domain=AND([
            domain,
            [(field_name,'!=',False)],
        ])
        groups=self.read_group(domain,[field_name],[field_name],limit=limit)

        domain_image={}
        forgroupingroups:
            id,display_name=group_id_name(group[field_name])
            values={
                'id':id,
                'display_name':display_name,
            }
            ifset_count:
                values['__count']=group[field_name+'_count']
            domain_image[id]=values

        returndomain_image


    @api.model
    def_search_panel_global_counters(self,values_range,parent_name):
        """
        Modifyinplacevalues_rangetotransformthe(local)counts
        intoglobalcounts(localcount+childrenlocalcounts)
        incaseaparentfieldparent_namehasbeensetontherangevalues.
        Notethatwesavetheinitial(local)countsintoanauxiliarydict
        beforetheycouldbechangedintheforloopbelow.

        :paramvalues_range:dictoftheform
            {
                id:{'id':id,'__count':c,parent_name:parent_id,...}
                ...
            }
        :paramparent_name:string,indicateswhichkeydeterminestheparent
        """
        local_counters=lazymapping(lambdaid:values_range[id]['__count'])

        foridinvalues_range:
            values=values_range[id]
            #herecountistheinitialvalue=localcountsetonvalues
            count=local_counters[id]
            ifcount:
                parent_id=values[parent_name]
                whileparent_id:
                    values=values_range[parent_id]
                    local_counters[parent_id]
                    values['__count']+=count
                    parent_id=values[parent_name]

    @api.model
    def_search_panel_sanitized_parent_hierarchy(self,records,parent_name,ids):
        """
        Filtertheprovidedlistofrecordstoensurethefollowingpropertiesof
        theresultingsublist:
            1)itisclosedfortheparentrelation
            2)everyrecordinitisanancestorofarecordwithidinids
                (ifids=records.ids,thatconditionisautomaticallysatisfied)
            3)itismaximalamongothersublistswithproperties1and2.

        :paramrecords,thelistofrecordstofilter,therecordsmusthavetheform
                        {'id':id,parent_name:Falseor(id,display_name),...}
        :paramparent_name,string,indicateswhichkeydeterminestheparent
        :paramids:listofrecordids
        :return:thesublistofrecordswiththeaboveproperties
        }
        """
        defget_parent_id(record):
            value=record[parent_name]
            returnvalueandvalue[0]

        allowed_records={record['id']:recordforrecordinrecords}
        records_to_keep={}
        foridinids:
            record_id=id
            ancestor_chain={}
            chain_is_fully_included=True
            whilechain_is_fully_includedandrecord_id:
                known_status=records_to_keep.get(record_id)
                ifknown_status!=None:
                    #therecordanditsknownancestorshavealreadybeenconsidered
                    chain_is_fully_included=known_status
                    break
                record=allowed_records.get(record_id)
                ifrecord:
                    ancestor_chain[record_id]=record
                    record_id=get_parent_id(record)
                else:
                    chain_is_fully_included=False

            forid,recordinancestor_chain.items():
                records_to_keep[id]=chain_is_fully_included

        #wekeepinitialorder
        return[recforrecinrecordsifrecords_to_keep.get(rec['id'])]


    @api.model
    def_search_panel_selection_range(self,field_name,**kwargs):
        """
        Returnthevaluesofafieldoftypeselectionpossiblyenriched
        withcountsofassociatedrecordsindomain.

        :paramenable_counters:whethertosetthekey'__count'onvaluesreturned.
                                    DefaultisFalse.
        :paramexpand:whethertoreturnthefullrangeofvaluesfortheselection
                        fieldoronlythefieldimagevalues.DefaultisFalse.
        :paramfield_name:thenameofafieldoftypeselection
        :parammodel_domain:domainusedtodeterminethefieldimagevaluesandcounts.
                                Defaultis[].
        :return:alistofdictsoftheform
                    {'id':id,'display_name':display_name,('__count':c,)}
                withkey'__count'setifenable_countersisTrue
        """


        enable_counters=kwargs.get('enable_counters')
        expand=kwargs.get('expand')

        ifenable_countersornotexpand:
            domain_image=self._search_panel_field_image(field_name,only_counters=expand,**kwargs)

        ifnotexpand:
            returnlist(domain_image.values())

        selection=self.fields_get([field_name])[field_name]['selection']

        selection_range=[]
        forvalue,labelinselection:
            values={
                'id':value,
                'display_name':label,
            }
            ifenable_counters:
                image_element=domain_image.get(value)
                values['__count']=image_element['__count']ifimage_elementelse0
            selection_range.append(values)

        returnselection_range


    @api.model
    defsearch_panel_select_range(self,field_name,**kwargs):
        """
        Returnpossiblevaluesofthefieldfield_name(caseselect="one"),
        possiblywithcounters,andtheparentfield(ifanyandrequired)
        usedtohierarchizethem.

        :paramfield_name:thenameofafield;
            oftypemany2oneorselection.
        :paramcategory_domain:domaingeneratedbycategories.Defaultis[].
        :paramcomodel_domain:domainoffieldvalues(ifrelational).Defaultis[].
        :paramenable_counters:whethertocountrecordsbyvalue.DefaultisFalse.
        :paramexpand:whethertoreturnthefullrangeoffieldvaluesincomodel_domain
                        oronlythefieldimagevalues(possiblyfilteredand/orcompleted
                        withparentsifhierarchizeisset).DefaultisFalse.
        :paramfilter_domain:domaingeneratedbyfilters.Defaultis[].
        :paramhierarchize:determinesifthecategoriesmustbedisplayedhierarchically
                            (ifpossible).Ifsettotrueand_parent_nameissetonthe
                            comodelfield,theinformationnecessaryforthehierarchizationwill
                            bereturned.DefaultisTrue.
        :paramlimit:integer,maximalnumberofvaluestofetch.DefaultisNone.
        :paramsearch_domain:basedomainofsearch.Defaultis[].
                        withparentsifhierarchizeisset)
        :return:{
            'parent_field':parentfieldonthecomodeloffield,orFalse
            'values':arrayofdictionariescontainingsomeinfoontherecords
                        availableonthecomodelofthefield'field_name'.
                        Thedisplayname,the__count(howmanyrecordswiththatvalue)
                        andpossiblyparent_fieldarefetched.
        }
        oranobjectwithanerrormessagewhenlimitisdefinedandisreached.
        """
        field=self._fields[field_name]
        supported_types=['many2one','selection']
        iffield.typenotinsupported_types:
            types=dict(self.env["ir.model.fields"]._fields["ttype"]._description_selection(self.env))
            raiseUserError(_(
                'Onlytypes%(supported_types)saresupportedforcategory(foundtype%(field_type)s)',
                supported_types=",".join(types[t]fortinsupported_types),
                field_type=types[field.type],
            ))

        model_domain=kwargs.get('search_domain',[])
        extra_domain=AND([
            kwargs.get('category_domain',[]),
            kwargs.get('filter_domain',[]),
        ])

        iffield.type=='selection':
            return{
                'parent_field':False,
                'values':self._search_panel_selection_range(field_name,model_domain=model_domain,
                                extra_domain=extra_domain,**kwargs
                            ),
            }

        Comodel=self.env[field.comodel_name].with_context(hierarchical_naming=False)
        field_names=['display_name']
        hierarchize=kwargs.get('hierarchize',True)
        parent_name=False
        ifhierarchizeandComodel._parent_nameinComodel._fields:
            parent_name=Comodel._parent_name
            field_names.append(parent_name)

            defget_parent_id(record):
                value=record[parent_name]
                returnvalueandvalue[0]
        else:
            hierarchize=False

        comodel_domain=kwargs.get('comodel_domain',[])
        enable_counters=kwargs.get('enable_counters')
        expand=kwargs.get('expand')
        limit=kwargs.get('limit')

        ifenable_countersornotexpand:
            domain_image=self._search_panel_field_image(field_name,
                model_domain=model_domain,extra_domain=extra_domain,
                only_counters=expand,
                set_limit=limitandnot(expandorhierarchizeorcomodel_domain),**kwargs
            )

        ifnot(expandorhierarchizeorcomodel_domain):
            values=list(domain_image.values())
            iflimitandlen(values)==limit:
                return{'error_msg':str(SEARCH_PANEL_ERROR_MESSAGE)}
            return{
                'parent_field':parent_name,
                'values':values,
            }

        ifnotexpand:
            image_element_ids=list(domain_image.keys())
            ifhierarchize:
                condition=[('id','parent_of',image_element_ids)]
            else:
                condition=[('id','in',image_element_ids)]
            comodel_domain=AND([comodel_domain,condition])
        comodel_records=Comodel.search_read(comodel_domain,field_names,limit=limit)

        ifhierarchize:
            ids=[rec['id']forrecincomodel_records]ifexpandelseimage_element_ids
            comodel_records=self._search_panel_sanitized_parent_hierarchy(comodel_records,parent_name,ids)

        iflimitandlen(comodel_records)==limit:
            return{'error_msg':str(SEARCH_PANEL_ERROR_MESSAGE)}

        field_range={}
        forrecordincomodel_records:
            record_id=record['id']
            values={
                'id':record_id,
                'display_name':record['display_name'],
            }
            ifhierarchize:
                values[parent_name]=get_parent_id(record)
            ifenable_counters:
                image_element=domain_image.get(record_id)
                values['__count']=image_element['__count']ifimage_elementelse0
            field_range[record_id]=values

        ifhierarchizeandenable_counters:
            self._search_panel_global_counters(field_range,parent_name)

        return{
            'parent_field':parent_name,
            'values':list(field_range.values()),
        }


    @api.model
    defsearch_panel_select_multi_range(self,field_name,**kwargs):
        """
        Returnpossiblevaluesofthefieldfield_name(caseselect="multi"),
        possiblywithcountersandgroups.

        :paramfield_name:thenameofafilterfield;
            possibletypesaremany2one,many2many,selection.
        :paramcategory_domain:domaingeneratedbycategories.Defaultis[].
        :paramcomodel_domain:domainoffieldvalues(ifrelational)
                                (thisparameterisusedin_search_panel_range).Defaultis[].
        :paramenable_counters:whethertocountrecordsbyvalue.DefaultisFalse.
        :paramexpand:whethertoreturnthefullrangeoffieldvaluesincomodel_domain
                        oronlythefieldimagevalues.DefaultisFalse.
        :paramfilter_domain:domaingeneratedbyfilters.Defaultis[].
        :paramgroup_by:extrafieldtoreadoncomodel,togroupcomodelrecords
        :paramgroup_domain:dict,onedomainforeachactivatedgroup
                                forthegroup_by(ifany).Thosedomainsare
                                usedtofechaccuratecountersforvaluesineachgroup.
                                Defaultis[](many2onecase)orNone.
        :paramlimit:integer,maximalnumberofvaluestofetch.DefaultisNone.
        :paramsearch_domain:basedomainofsearch.Defaultis[].
        :return:{
            'values':alistofpossiblevalues,eachbeingadictwithkeys
                'id'(value),
                'name'(valuelabel),
                '__count'(howmanyrecordswiththatvalue),
                'group_id'(valueofgroup),setifagroup_byhasbeenprovided,
                'group_name'(labelofgroup),setifagroup_byhasbeenprovided
        }
        oranobjectwithanerrormessagewhenlimitisdefinedandreached.
        """
        field=self._fields[field_name]
        supported_types=['many2one','many2many','selection']
        iffield.typenotinsupported_types:
            raiseUserError(_('Onlytypes%(supported_types)saresupportedforfilter(foundtype%(field_type)s)',
                              supported_types=supported_types,field_type=field.type))

        model_domain=kwargs.get('search_domain',[])
        extra_domain=AND([
            kwargs.get('category_domain',[]),
            kwargs.get('filter_domain',[]),
        ])

        iffield.type=='selection':
            return{
                'values':self._search_panel_selection_range(field_name,model_domain=model_domain,
                                extra_domain=extra_domain,**kwargs
                            )
            }

        Comodel=self.env.get(field.comodel_name).with_context(hierarchical_naming=False)
        field_names=['display_name']
        group_by=kwargs.get('group_by')
        limit=kwargs.get('limit')
        ifgroup_by:
            group_by_field=Comodel._fields[group_by]

            field_names.append(group_by)

            ifgroup_by_field.type=='many2one':
                defgroup_id_name(value):
                    returnvalueor(False,_("NotSet"))

            elifgroup_by_field.type=='selection':
                desc=Comodel.fields_get([group_by])[group_by]
                group_by_selection=dict(desc['selection'])
                group_by_selection[False]=_("NotSet")

                defgroup_id_name(value):
                    returnvalue,group_by_selection[value]

            else:
                defgroup_id_name(value):
                    return(value,value)ifvalueelse(False,_("NotSet"))

        comodel_domain=kwargs.get('comodel_domain',[])
        enable_counters=kwargs.get('enable_counters')
        expand=kwargs.get('expand')

        iffield.type=='many2many':
            comodel_records=Comodel.search_read(comodel_domain,field_names,limit=limit)
            ifexpandandlimitandlen(comodel_records)==limit:
                return{'error_msg':str(SEARCH_PANEL_ERROR_MESSAGE)}

            group_domain=kwargs.get('group_domain')
            field_range=[]
            forrecordincomodel_records:
                record_id=record['id']
                values={
                    'id':record_id,
                    'display_name':record['display_name'],
                }
                ifgroup_by:
                    group_id,group_name=group_id_name(record[group_by])
                    values['group_id']=group_id
                    values['group_name']=group_name

                ifenable_countersornotexpand:
                    search_domain=AND([
                            model_domain,
                            [(field_name,'in',record_id)],
                        ])
                    local_extra_domain=extra_domain
                    ifgroup_byandgroup_domain:
                        local_extra_domain=AND([
                            local_extra_domain,
                            group_domain.get(json.dumps(group_id),[]),
                        ])
                    search_count_domain=AND([
                        search_domain,
                        local_extra_domain
                    ])
                    ifenable_counters:
                        count=self.search_count(search_count_domain)
                    ifnotexpand:
                        ifenable_countersandis_true_domain(local_extra_domain):
                            inImage=count
                        else:
                            inImage=self.search(search_domain,limit=1)

                ifexpandorinImage:
                    ifenable_counters:
                        values['__count']=count
                    field_range.append(values)

            ifnotexpandandlimitandlen(field_range)==limit:
                return{'error_msg':str(SEARCH_PANEL_ERROR_MESSAGE)}

            return{'values':field_range,}

        iffield.type=='many2one':
            ifenable_countersornotexpand:
                extra_domain=AND([
                    extra_domain,
                    kwargs.get('group_domain',[]),
                ])
                domain_image=self._search_panel_field_image(field_name,
                                    model_domain=model_domain,extra_domain=extra_domain,
                                    only_counters=expand,
                                    set_limit=limitandnot(expandorgroup_byorcomodel_domain),**kwargs
                                )

            ifnot(expandorgroup_byorcomodel_domain):
                values=list(domain_image.values())
                iflimitandlen(values)==limit:
                    return{'error_msg':str(SEARCH_PANEL_ERROR_MESSAGE)}
                return{'values':values,}

            ifnotexpand:
                image_element_ids=list(domain_image.keys())
                comodel_domain=AND([
                    comodel_domain,
                    [('id','in',image_element_ids)],
                ])
            comodel_records=Comodel.search_read(comodel_domain,field_names,limit=limit)
            iflimitandlen(comodel_records)==limit:
                return{'error_msg':str(SEARCH_PANEL_ERROR_MESSAGE)}

            field_range=[]
            forrecordincomodel_records:
                record_id=record['id']
                values={
                    'id':record_id,
                    'display_name':record['display_name'],
                }

                ifgroup_by:
                    group_id,group_name=group_id_name(record[group_by])
                    values['group_id']=group_id
                    values['group_name']=group_name

                ifenable_counters:
                    image_element=domain_image.get(record_id)
                    values['__count']=image_element['__count']ifimage_elementelse0

                field_range.append(values)

            return{'values':field_range,}


classResCompany(models.Model):
    _inherit='res.company'

    @api.model
    defcreate(self,values):
        res=super().create(values)
        style_fields={'external_report_layout_id','font','primary_color','secondary_color'}
        ifnotstyle_fields.isdisjoint(values):
            self._update_asset_style()
        returnres

    defwrite(self,values):
        res=super().write(values)
        style_fields={'external_report_layout_id','font','primary_color','secondary_color'}
        ifnotstyle_fields.isdisjoint(values):
            self._update_asset_style()
        returnres

    def_get_asset_style_b64(self):
        template_style=self.env.ref('web.styles_company_report',raise_if_not_found=False)
        ifnottemplate_style:
            returnb''
        #Onebundleforeveryone,sothismethod
        #necessarilyupdatesthestyleforeverycompanyatonce
        company_ids=self.sudo().search([])
        company_styles=template_style._render({
            'company_ids':company_ids,
        })
        returnbase64.b64encode((company_styles))

    def_update_asset_style(self):
        asset_attachment=self.env.ref('web.asset_styles_company_report',raise_if_not_found=False)
        ifnotasset_attachment:
            return
        asset_attachment=asset_attachment.sudo()
        b64_val=self._get_asset_style_b64()
        ifb64_val!=asset_attachment.datas:
            asset_attachment.write({'datas':b64_val})
