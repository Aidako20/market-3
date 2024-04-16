flectra.define("web/static/src/js/control_panel/control_panel_model_extension.js",function(require){
    "usestrict";

    constActionModel=require("web/static/src/js/views/action_model.js");
    constDomain=require('web.Domain');
    constpyUtils=require('web.py_utils');

    const{DEFAULT_INTERVAL,DEFAULT_PERIOD,
        getComparisonOptions,getIntervalOptions,getPeriodOptions,
        constructDateDomain,rankInterval,yearSelected}=require('web.searchUtils');

    constFAVORITE_PRIVATE_GROUP=1;
    constFAVORITE_SHARED_GROUP=2;
    constDISABLE_FAVORITE="search_disable_custom_filters";

    letfilterId=1;
    letgroupId=1;
    letgroupNumber=0;

    /**
     *Controlpanelmodel
     *
     *Thecontrolpanelmodelstateisanobjectstructuredinthefollowingway:
     *
     * {
     *     filters:Object{},
     *     query:Object[],
     * }
     *
     *-------------------------------------------------------------------------
     *Filters
     *-------------------------------------------------------------------------
     *
     *Thekeysarestringifiednumberscalled'filterids'.
     *Thevaluesareobjectscalled'filters'.
     *
     *Eachfilterhasthefollowingproperties:
     *     @prop{number}iduniqueidentifier,alsothefilter'scorrespondingkey
     *     @prop{number}groupIdtheidofsomegroup,actuallythegroupitself,
     *                    the(active)'groups'arereconstructedin_getGroups.
     *     @prop{string}descriptionthedescriptionofthefilter
     *     @prop{string}type'filter'|'groupBy'|'comparison'|'field'|'favorite'
     *
     *Otherpropertiescanbepresentaccordingtothecorrespondingfiltertype:
     *
     *•type'comparison':
     *     @prop{string}comparisonOptionIdoptionidentifier(@seeCOMPARISON_OPTIONS).
     *     @prop{string}dateFilterIdtheidofadatefilter(filteroftype'filter'
     *                                     withisDateFilter=true)
     *
     *•type'filter':
     *     @prop{number}groupNumberusedtoseparateitemsinthe'Filters'menu
     *     @prop{string}[context]context
     *     @prop{boolean}[invisible]determineifthefilterisaccessibleintheinterface
     *     @prop{boolean}[isDefault]
     *     @ifisDefault=true:
     *         >@prop{number}[defaultRank=-5]usedtodeterminetheorderof
     *         >               activationofdefaultfilters
     *     @prop{boolean}[isDateFilter]trueifthefiltercomesfromanarchnode
     *                     withavalid'date'attribute.
     *     @ifisDateFilter=true
     *         >@prop{boolean}[hasOptions=true]
     *         >@prop{string}defaultOptionIdoptionidentifierdeterminedby
     *         >               default_periodattribute(@seePERIOD_OPTIONS).
     *         >               DefaultsettoDEFAULT_PERIOD.
     *         >@prop{string}fieldNamedeterminedbythevalueof'date'attribute
     *         >@prop{string}fieldType'date'or'datetime',typeofthecorrespondingfield
     *     @else
     *         >@prop{string}domain
     *
     *•type'groupBy':
     *     @prop{string}fieldName
     *     @prop{string}fieldType
     *     @prop{number}groupNumberusedtoseparateitemsinthe'Groupby'menu
     *     @prop{boolean}[isDefault]
     *     @ifisDefault=true:
     *         >@prop{number}defaultRankusedtodeterminetheorderofactivation
     *         >               ofdefaultfilters
     *     @prop{boolean}[invisible]determineifthefilterisaccessibleintheinterface
     *     @prop{boolean}[hasOptions]trueiffieldtypeis'date'or'datetime'
     *     @ifhasOptions=true
     *         >@prop{string}defaultOptionIdoptionidentifier(seeINTERVAL_OPTIONS)
     *                          defaultsettoDEFAULT_INTERVAL.
     *
     *•type'field':
     *     @prop{string}fieldName
     *     @prop{string}fieldType
     *     @prop{string}[context]
     *     @prop{string}[domain]
     *     @prop{string}[filterDomain]
     *     @prop{boolean}[invisible]determineifthefilterisaccessibleintheinterface
     *     @prop{boolean}[isDefault]
     *     @prop{string}[operator]
     *     @ifisDefault=true:
     *         >@prop{number}[defaultRank=-10]usedtodeterminetheorderof
     *         >               activationoffilters
     *         >@prop{Object}defaultAutocompleteValueoftheform{value,label,operator}
     *
     *•type:'favorite':
     *     @prop{Object}[comparison]oftheform{comparisonId,fieldName,fieldDescription,
     *                     range,rangeDescription,comparisonRange,comparisonRangeDescription,}
     *     @prop{Object}context
     *     @prop{string}domain
     *     @prop{string[]}groupBys
     *     @prop{number}groupNumber1|2,2ifthefavoriteisshared
     *     @prop{string[]}orderedBy
     *     @prop{boolean}[removable=true]indicatesthatthefavoritecanbedeleted
     *     @prop{number}serverSideId
     *     @prop{number}userId
     *     @prop{boolean}[isDefault]
     *
     *-------------------------------------------------------------------------
     *Query
     *-------------------------------------------------------------------------
     *
     *Thequeryelementsareobjectscalled'queryelements'.
     *
     *Eachqueryelementhasthefollowingproperties:
     *     @prop{number}filterIdtheidofsomefilter
     *     @prop{number}groupIdtheidofsomegroup(actuallythegroupitself)
     *
     *Otherpropertiesmustbedefinedaccordingtothecorrespondingfiltertype.
     *
     *•type'comparison':
     *     @prop{string}dateFilterIdtheidofadatefilter(filteroftype'filter'
     *                                     withhasOptions=true)
     *     @prop{string}type'comparison',helpwhensearchingifacomparisonisactive
     *
     *•type'filter'withhasOptions=true:
     *     @prop{string}optionIdoptionidentifier(@seePERIOD_OPTIONS)
     *
     *•type'groupBy'withhasOptions=true:
     *     @prop{string}optionIdoptionidentifier(@seeINTERVAL_OPTIONS)
     *
     *•type'field':
     *     @prop{string}labeldescriptionputinthefacet(canbetemporarillymissing)
     *     @prop{(string|number)}valueusedasthevalueofthegenerateddomain
     *     @prop{string}operatorusedastheoperatorofthegenerateddomain
     *
     *Thequeryelementsindicateswhataretheactivefiltersand'how'theyareactive.
     *ThekeygroupIdhasbeenaddedforsimplicity.Itcouldhavebeenremovedfromqueryelements
     *sincetheinformationisavailableonthecorrespondingfilters.
     *@extendsActionModel.Extension
     */
    classControlPanelModelExtensionextendsActionModel.Extension{
        /**
         *@param{Object}config
         *@param{(string|number)}config.actionId
         *@param{Object}config.env
         *@param{string}config.modelName
         *@param{Object}[config.context={}]
         *@param{Object[]}[config.archNodes=[]]
         *@param{Object[]}[config.dynamicFilters=[]]
         *@param{string[]}[config.searchMenuTypes=[]]
         *@param{Object}[config.favoriteFilters={}]
         *@param{Object}[config.fields={}]
         *@param{boolean}[config.withSearchBar=true]
         */
        constructor(){
            super(...arguments);

            this.actionContext=Object.assign({},this.config.context);
            this.searchMenuTypes=this.config.searchMenuTypes||[];
            this.favoriteFilters=this.config.favoriteFilters||[];
            this.fields=this.config.fields||{};
            this.searchDefaults={};
            for(constkeyinthis.actionContext){
                constmatch=/^search_default_(.*)$/.exec(key);
                if(match){
                    constval=this.actionContext[key];
                    if(val){
                        this.searchDefaults[match[1]]=val;
                    }
                    deletethis.actionContext[key];
                }
            }
            this.labelPromises=[];

            this.referenceMoment=moment();
            this.optionGenerators=getPeriodOptions(this.referenceMoment);
            this.intervalOptions=getIntervalOptions();
            this.comparisonOptions=getComparisonOptions();
        }

        //---------------------------------------------------------------------
        //Public
        //---------------------------------------------------------------------

        /**
         *@override
         *@returns{any}
         */
        get(property,...args){
            switch(property){
                case"context":returnthis.getContext();
                case"domain":returnthis.getDomain();
                case"facets":returnthis._getFacets();
                case"filters":returnthis._getFilters(...args);
                case"groupBy":returnthis.getGroupBy();
                case"orderedBy":returnthis.getOrderedBy();
                case"timeRanges":returnthis.getTimeRanges();
            }
        }

        /**
         *@override
         */
        asyncload(){
            awaitPromise.all(this.labelPromises);
        }

        /**
         *@override
         */
        prepareState(){
            Object.assign(this.state,{
                filters:{},
                query:[],
            });
            if(this.config.withSearchBar!==false){
                this._addFilters();
                this._activateDefaultFilters();
            }
        }

        //---------------------------------------------------------------------
        //Actions/Getters
        //---------------------------------------------------------------------

        /**
         *@returns{Object|undefined}
         */
        getactiveComparison(){
            returnthis.state.query.find(queryElem=>queryElem.type==='comparison');
        }

        /**
         *Activateafilteroftype'field'withgivenfilterIdwith
         *'autocompleteValues'value,label,andoperator.
         *@param{Object}
         */
        addAutoCompletionValues({filterId,label,value,operator}){
            constqueryElem=this.state.query.find(queryElem=>
                queryElem.filterId===filterId&&
                queryElem.value===value&&
                queryElem.operator===operator
            );
            if(!queryElem){
                const{groupId}=this.state.filters[filterId];
                this.state.query.push({filterId,groupId,label,value,operator});
            }else{
                queryElem.label=label;
            }
        }

        /**
         *Removeallthequeryelementsfromquery.
         */
        clearQuery(){
            this.state.query=[];
        }

        /**
         *Createanewfilteroftype'favorite'andactivateit.
         *Anewgroupcontainingonlythatfilteriscreated.
         *Thequeryisemptiedbeforeactivatingthenewfavorite.
         *@param{Object}preFilter
         *@returns{Promise}
         */
        asynccreateNewFavorite(preFilter){
            constpreFavorite=awaitthis._saveQuery(preFilter);
            this.clearQuery();
            constfilter=Object.assign(preFavorite,{
                groupId,
                id:filterId,
            });
            this.state.filters[filterId]=filter;
            this.state.query.push({groupId,filterId});
            groupId++;
            filterId++;
        }

        /**
         *Createnewfiltersoftype'filter'andactivatethem.
         *Anewgroupcontainingonlythosefiltersiscreated.
         *@param{Object[]}filters
         *@returns{number[]}
         */
        createNewFilters(prefilters){
            if(!prefilters.length){
                return[];
            }
            constnewFilterIdS=[];
            prefilters.forEach(preFilter=>{
                constfilter=Object.assign(preFilter,{
                    groupId,
                    groupNumber,
                    id:filterId,
                    type:'filter',
                });
                this.state.filters[filterId]=filter;
                this.state.query.push({groupId,filterId});
                newFilterIdS.push(filterId);
                filterId++;
            });
            groupId++;
            groupNumber++;
            returnnewFilterIdS;
        }

        /**
         *Createanewfilteroftype'groupBy'andactivateit.
         *Itisaddedtotheuniquegroupofgroupbys.
         *@param{Object}field
         */
        createNewGroupBy(field){
            constgroupBy=Object.values(this.state.filters).find(f=>f.type==='groupBy');
            constfilter={
                description:field.string||field.name,
                fieldName:field.name,
                fieldType:field.type,
                groupId:groupBy?groupBy.groupId:groupId++,
                groupNumber,
                id:filterId,
                type:'groupBy',
            };
            this.state.filters[filterId]=filter;
            if(['date','datetime'].includes(field.type)){
                filter.hasOptions=true;
                filter.defaultOptionId=DEFAULT_INTERVAL;
                this.toggleFilterWithOptions(filterId);
            }else{
                this.toggleFilter(filterId);
            }
            groupNumber++;
            filterId++;
        }

        /**
         *DeactivateagroupwithprovidedgroupId,i.e.deletethequeryelements
         *withgivengroupId.
         *@param{number}groupId
         */
        deactivateGroup(groupId){
            this.state.query=this.state.query.filter(
                queryElem=>queryElem.groupId!==groupId
            );
            this._checkComparisonStatus();
        }

        /**
         *Deleteafilteroftype'favorite'withgivenfilterIdserversideand
         *incontrolpanelmodel.Ofcoursethefilterisalsoremoved
         *fromthesearchquery.
         *@param{number}filterId
         */
        asyncdeleteFavorite(filterId){
            const{serverSideId}=this.state.filters[filterId];
            awaitthis.env.dataManager.delete_filter(serverSideId);
            constindex=this.state.query.findIndex(
                queryElem=>queryElem.filterId===filterId
            );
            deletethis.state.filters[filterId];
            if(index>=0){
                this.state.query.splice(index,1);
            }
        }

        /**
         *@returns{Object}
         */
        getContext(){
            constgroups=this._getGroups();
            returnthis._getContext(groups);
        }

        /**
         *@returns{Array[]}
         */
        getDomain(){
            constgroups=this._getGroups();
            constuserContext=this.env.session.user_context;
            try{
                returnDomain.prototype.stringToArray(this._getDomain(groups),userContext);
            }catch(err){
                thrownewError(
                    `${this.env._t("Controlpanelmodelextensionfailedtoevaluatedomain")}:/n${JSON.stringify(err)}`
                );
            }
        }

        /**
         *@returns{string[]}
         */
        getGroupBy(){
            constgroups=this._getGroups();
            returnthis._getGroupBy(groups);
        }

        /**
         *@returns{string[]}
         */
        getOrderedBy(){
            constgroups=this._getGroups();
            returnthis._getOrderedBy(groups);
        }

        /**
         *@returns{Object}
         */
        getTimeRanges(){
            constrequireEvaluation=true;
            returnthis._getTimeRanges(requireEvaluation);
        }

        /**
         *Usedtocalldispatchandtriggera'search'.
         */
        search(){
            /*...*/
        }

        /**
         *Activate/Deactivateafilteroftype'comparison'withprovidedid.
         *Atmostonefilteroftype'comparison'canbeactivatedateverytime.
         *@param{string}filterId
         */
        toggleComparison(filterId){
            const{groupId,dateFilterId}=this.state.filters[filterId];
            constqueryElem=this.state.query.find(queryElem=>
                queryElem.type==='comparison'&&
                queryElem.filterId===filterId
            );
            //makesureonlyonecomparisoncanbeactive
            this.state.query=this.state.query.filter(queryElem=>queryElem.type!=='comparison');
            if(!queryElem){
                this.state.query.push({groupId,filterId,dateFilterId,type:'comparison',});
            }
        }

        /**
         *ActivateordeactivatethesimplefilterwithgivenfilterId,i.e.
         *addorremoveacorrespondingqueryelement.
         *@param{string}filterId
         */
        toggleFilter(filterId){
            constindex=this.state.query.findIndex(
                queryElem=>queryElem.filterId===filterId
            );
            if(index>=0){
                this.state.query.splice(index,1);
            }else{
                const{groupId,type}=this.state.filters[filterId];
                if(type==='favorite'){
                    this.state.query=[];
                }
                this.state.query.push({groupId,filterId});
            }
        }

        /**
         *Usedtotoggleaqueryelement{filterId,optionId,(groupId)}.
         *Thiscanimpactthequeryinvariousform,e.g.add/removeotherqueryelements
         *incasethefilterisoftype'filter'.
         *@param{string}filterId
         *@param{string}[optionId]
         */
        toggleFilterWithOptions(filterId,optionId){
            constfilter=this.state.filters[filterId];
            optionId=optionId||filter.defaultOptionId;
            constoption=this.optionGenerators.find(o=>o.id===optionId);

            constindex=this.state.query.findIndex(
                queryElem=>queryElem.filterId===filterId&&queryElem.optionId===optionId
            );

            if(index>=0){
                this.state.query.splice(index,1);
                if(filter.type==='filter'&&!yearSelected(this._getSelectedOptionIds(filterId))){
                    //ThisisthecasewhereoptionIdwasthelastoption
                    //oftype'year'tobetherebeforebeingremovedabove.
                    //Sinceotheroptionsoftype'month'or'quarter'do
                    //notmakesensewithoutayearwedeactivatealloptions.
                    this.state.query=this.state.query.filter(
                        queryElem=>queryElem.filterId!==filterId
                    );
                }
            }else{
                this.state.query.push({groupId:filter.groupId,filterId,optionId});
                if(filter.type==='filter'&&!yearSelected(this._getSelectedOptionIds(filterId))){
                    //Hereweadd'this_year'asoptionsifnooptionoftype
                    //yearisalreadyselected.
                    this.state.query.push({
                        groupId:filter.groupId,
                        filterId,
                        optionId:option.defaultYearId,
                    });
                }
            }
            if(filter.type==='filter'){
                this._checkComparisonStatus();
            }
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Activatethedefaultfavorite(ifany)oralldefaultfilters.
         *@private
         */
        _activateDefaultFilters(){
            if(this.defaultFavoriteId){
                //Activatedefaultfavorite
                this.toggleFilter(this.defaultFavoriteId);
            }else{
                //Activatedefaultfilters
                Object.values(this.state.filters)
                    .filter((f)=>f.isDefault&&f.type!=='favorite')
                    .sort((f1,f2)=>(f1.defaultRank||100)-(f2.defaultRank||100))
                    .forEach(f=>{
                        if(f.hasOptions){
                            this.toggleFilterWithOptions(f.id);
                        }elseif(f.type==='field'){
                            let{operator,label,value}=f.defaultAutocompleteValue;
                            this.addAutoCompletionValues({
                                filterId:f.id,
                                value,
                                operator,
                                label,
                            });
                        }else{
                            this.toggleFilter(f.id);
                        }
                    });
            }
        }

        /**
         *Thisfunctionpopulatesthe'filters'objectatinitialization.
         *Thefilterscomefrom:
         *    -config.archNodes(types'comparison','filter','groupBy','field'),
         *    -config.dynamicFilters(type'filter'),
         *    -config.favoriteFilters(type'favorite'),
         *    -codeitself(type'timeRange')
         *@private
         */
        _addFilters(){
            this._createGroupOfFavorites();
            this._createGroupOfFiltersFromArch();
            this._createGroupOfDynamicFilters();
        }

        /**
         *Ifacomparisonisactive,checkifitshouldbecomeinactive.
         *Thecomparisonshouldbecomeinactiveifthecorrespondingdatefilterhasbecome
         *inactive.
         *@private
         */
        _checkComparisonStatus(){
            constactiveComparison=this.activeComparison;
            if(!activeComparison){
                return;
            }
            const{dateFilterId}=activeComparison;
            constdateFilterIsActive=this.state.query.some(
                queryElem=>queryElem.filterId===dateFilterId
            );
            if(!dateFilterIsActive){
                this.state.query=this.state.query.filter(
                    queryElem=>queryElem.type!=='comparison'
                );
            }
        }

        /**
         *ReturnstheactivecomparisontimeRangesobject.
         *@private
         *@param{Object}comparisonFilter
         *@returns{Object|null}
         */
        _computeTimeRanges(comparisonFilter){
            const{filterId}=this.activeComparison;
            if(filterId!==comparisonFilter.id){
                returnnull;
            }
            const{dateFilterId,comparisonOptionId}=comparisonFilter;
            const{
                fieldName,
                fieldType,
                description:dateFilterDescription,
            }=this.state.filters[dateFilterId];

            constselectedOptionIds=this._getSelectedOptionIds(dateFilterId);

            //computerangeandrangedescription
            const{domain:range,description:rangeDescription}=constructDateDomain(
                this.referenceMoment,fieldName,fieldType,selectedOptionIds,
            );

            //computecomparisonRangeandcomparisonRangedescription
            const{
                domain:comparisonRange,
                description:comparisonRangeDescription,
            }=constructDateDomain(
                this.referenceMoment,fieldName,fieldType,selectedOptionIds,comparisonOptionId
            );

            return{
                comparisonId:comparisonOptionId,
                fieldName,
                fieldDescription:dateFilterDescription,
                range,
                rangeDescription,
                comparisonRange,
                comparisonRangeDescription,
            };
        }

        /**
         *Startingfromthearrayofdatefilters,createthefiltersoftype
         *'comparison'.
         *@private
         *@param{Object[]}dateFilters
         */
        _createGroupOfComparisons(dateFilters){
            constpreFilters=[];
            for(constdateFilterofdateFilters){
                for(constcomparisonOptionofthis.comparisonOptions){
                    const{id:dateFilterId,description}=dateFilter;
                    constpreFilter={
                        type:'comparison',
                        comparisonOptionId:comparisonOption.id,
                        description:`${description}:${comparisonOption.description}`,
                        dateFilterId,
                    };
                    preFilters.push(preFilter);
                }
            }
            this._createGroupOfFilters(preFilters);
        }

        /**
         *Addfiltersoftype'filter'determinedbythekeyarraydynamicFilters.
         *@private
         */
        _createGroupOfDynamicFilters(){
            constdynamicFilters=this.config.dynamicFilters||[];
            constpregroup=dynamicFilters.map(filter=>{
                return{
                    description:filter.description,
                    domain:JSON.stringify(filter.domain),
                    isDefault:true,
                    type:'filter',
                };
            });
            this._createGroupOfFilters(pregroup);
        }

        /**
         *Addfiltersoftype'favorite'determinedbythearraythis.favoriteFilters.
         *@private
         */
        _createGroupOfFavorites(){
            constactivateFavorite=DISABLE_FAVORITEinthis.actionContext?
                !this.actionContext[DISABLE_FAVORITE]:
                true;
            this.favoriteFilters.forEach(irFilter=>{
                constfavorite=this._irFilterToFavorite(irFilter);
                this._createGroupOfFilters([favorite]);
                if(activateFavorite&&favorite.isDefault){
                    this.defaultFavoriteId=favorite.id;
                }
            });
        }

        /**
         *Usingalist(a'pregroup')of'prefilters',createnewfiltersin`state.filters`
         *foreachprefilter.Thenewfiltersbelongtoasamenewgroup.
         *@private
         *@param{Object[]}pregroup,listof'prefilters'
         *@param{string}type
         */
        _createGroupOfFilters(pregroup){
            pregroup.forEach(preFilter=>{
                constfilter=Object.assign(preFilter,{groupId,id:filterId});
                this.state.filters[filterId]=filter;
                if(!this.defaultFavoriteId&&filter.isDefault&&filter.type==='field'){
                    this._prepareDefaultLabel(filter);
                }
                filterId++;
            });
            groupId++;
        }

        /**
         *Parsethearchofa'search'viewandcreatecorrespondingfiltersandgroups.
         *
         *Asearchviewarchmaycontaina'searchpanel'node,butthisisn't
         *theconcernoftheControlPanel(theSearchPanelwillhandleit).
         *Ideally,thiscodeshouldwhitelistthetagstotakeintoaccount
         *insteadofblacklistingtheothers,butwiththecurrent(messy)
         *structureofasearchviewarch,it'swaysimplertodoitthatway.
         *@private
         */
        _createGroupOfFiltersFromArch(){
            constpreFilters=this.config.archNodes.reduce(
                (preFilters,child)=>{
                    if(child.tag==='group'){
                        return[...preFilters,...child.children.map(c=>this._evalArchChild(c))];
                    }else{
                        return[...preFilters,this._evalArchChild(child)];
                    }
                },
                []
            );
            preFilters.push({tag:'separator'});

            //creategroupsandfilters
            letcurrentTag;
            letcurrentGroup=[];
            letpregroupOfGroupBys=[];

            preFilters.forEach(preFilter=>{
                if(
                    preFilter.tag!==currentTag||
                    ['separator','field'].includes(preFilter.tag)
                ){
                    if(currentGroup.length){
                        if(currentTag==='groupBy'){
                            pregroupOfGroupBys=[...pregroupOfGroupBys,...currentGroup];
                        }else{
                            this._createGroupOfFilters(currentGroup);
                        }
                    }
                    currentTag=preFilter.tag;
                    currentGroup=[];
                    groupNumber++;
                }
                if(preFilter.tag!=='separator'){
                    constfilter={
                        type:preFilter.tag,
                        //weneedtocodifyherewhatwewanttokeepfromattrs
                        //andhow,fornowIputeverything.
                        //Insomesence,somefilterareactive(totallydetermined,given)
                        //andothersarepassive(requireinput(s)tobecomedetermined)
                        //Whatistherightplacetoprocesstheattrs?
                    };
                    if(preFilter.attrs&&JSON.parse(preFilter.attrs.modifiers||'{}').invisible){
                        filter.invisible=true;
                        letpreFilterFieldName=null;
                        if(preFilter.tag==='filter'&&preFilter.attrs.date){
                            preFilterFieldName=preFilter.attrs.date;
                        }elseif(preFilter.tag==='groupBy'){
                            preFilterFieldName=preFilter.attrs.fieldName;
                        }
                        if(preFilterFieldName&&!this.fields[preFilterFieldName]){
                            //Insomecasewhenafieldislimitedtospecificgroups
                            //onthemodel,weneedtoensuretodiscardrelatedfilter
                            //asitmaystillbepresentintheview(in'invisible'state)
                            return;
                        }
                    }
                    if(filter.type==='filter'||filter.type==='groupBy'){
                        filter.groupNumber=groupNumber;
                    }
                    this._extractAttributes(filter,preFilter.attrs);
                    currentGroup.push(filter);
                }
            });

            if(pregroupOfGroupBys.length){
                this._createGroupOfFilters(pregroupOfGroupBys);
            }
            constdateFilters=Object.values(this.state.filters).filter(
                (filter)=>filter.isDateFilter
            );
            if(dateFilters.length){
                this._createGroupOfComparisons(dateFilters);
            }
        }

        /**
         *Returnsnulloracopyoftheprovidedfilterwithadditionalinformation
         *usedonlyoutsideofthecontrolpanelmodel,likeinsearchbarorinthe
         *variousmenus.Thevaluenullisreturnedifthefiltershouldnotappear
         *forsomereason.
         *@private
         *@param{Object}filter
         *@param{Object[]}filterQueryElements
         *@returns{Object|null}
         */
        _enrichFilterCopy(filter,filterQueryElements){
            constisActive=Boolean(filterQueryElements.length);
            constf=Object.assign({isActive},filter);

            function_enrichOptions(options){
                returnoptions.map(o=>{
                    const{description,id,groupNumber}=o;
                    constisActive=filterQueryElements.some(a=>a.optionId===id);
                    return{description,id,groupNumber,isActive};
                });
            }

            switch(f.type){
                case'comparison':{
                    const{dateFilterId}=filter;
                    constdateFilterIsActive=this.state.query.some(
                        queryElem=>queryElem.filterId===dateFilterId
                    );
                    if(!dateFilterIsActive){
                        returnnull;
                    }
                    break;
                }
                case'filter':
                    if(f.hasOptions){
                        f.options=_enrichOptions(this.optionGenerators);
                    }
                    break;
                case'groupBy':
                    if(f.hasOptions){
                        f.options=_enrichOptions(this.intervalOptions);
                    }
                    break;
                case'field':
                    f.autoCompleteValues=filterQueryElements.map(
                        ({label,value,operator})=>({label,value,operator})
                    );
                    break;
            }
            returnf;
        }

        /**
         *Processagivenarchnodeandenrichit.
         *@private
         *@param{Object}child
         *@returns{Object}
         */
        _evalArchChild(child){
            if(child.attrs.context){
                try{
                    constcontext=pyUtils.eval('context',child.attrs.context);
                    child.attrs.context=context;
                    if(context.group_by){
                        //letusextractbasicdatasincewejustevaluatedcontext
                        //anduseacorrecttag!
                        child.attrs.fieldName=context.group_by.split(':')[0];
                        child.attrs.defaultInterval=context.group_by.split(':')[1];
                        child.tag='groupBy';
                    }
                }catch(e){}
            }
            if(child.attrs.nameinthis.searchDefaults){
                child.attrs.isDefault=true;
                letvalue=this.searchDefaults[child.attrs.name];
                if(child.tag==='field'){
                    child.attrs.defaultValue=this.fields[child.attrs.name].type==='many2one'&&Array.isArray(value)?value[0]:value;
                }elseif(child.tag==='groupBy'){
                    child.attrs.defaultRank=typeofvalue==='number'?value:100;
                }
            }
            returnchild;
        }

        /**
         *Processtheattributessetonanarchnodeandaddsvariouskeysto
         *thegivenfilter.
         *@private
         *@param{Object}filter
         *@param{Object}attrs
         */
        _extractAttributes(filter,attrs){
            if(attrs.isDefault){
                filter.isDefault=attrs.isDefault;
            }
            filter.description=attrs.string||attrs.help||attrs.name||attrs.domain||'Ω';
            switch(filter.type){
                case'filter':
                    if(attrs.context){
                        filter.context=attrs.context;
                    }
                    if(attrs.date){
                        filter.isDateFilter=true;
                        filter.hasOptions=true;
                        filter.fieldName=attrs.date;
                        filter.fieldType=this.fields[attrs.date].type;
                        filter.defaultOptionId=attrs.default_period||DEFAULT_PERIOD;
                    }else{
                        filter.domain=attrs.domain||'[]';
                    }
                    if(filter.isDefault){
                        filter.defaultRank=-5;
                    }
                    break;
                case'groupBy':
                    filter.fieldName=attrs.fieldName;
                    filter.fieldType=this.fields[attrs.fieldName].type;
                    if(['date','datetime'].includes(filter.fieldType)){
                        filter.hasOptions=true;
                        filter.defaultOptionId=attrs.defaultInterval||DEFAULT_INTERVAL;
                    }
                    if(filter.isDefault){
                        filter.defaultRank=attrs.defaultRank;
                    }
                    break;
                case'field':{
                    constfield=this.fields[attrs.name];
                    filter.fieldName=attrs.name;
                    filter.fieldType=field.type;
                    if(attrs.domain){
                        filter.domain=attrs.domain;
                    }
                    if(attrs.filter_domain){
                        filter.filterDomain=attrs.filter_domain;
                    }elseif(attrs.operator){
                        filter.operator=attrs.operator;
                    }
                    if(attrs.context){
                        filter.context=attrs.context;
                    }
                    if(filter.isDefault){
                        letoperator=filter.operator;
                        if(!operator){
                            consttype=attrs.widget||filter.fieldType;
                            //Note:many2oneasadefaultfilterwillhavea
                            //numericvalueinsteadofastring=>wewant"="
                            //insteadof"ilike".
                            if(["char","html","many2many","one2many","text"].includes(type)){
                                operator="ilike";
                            }else{
                                operator="=";
                            }
                        }
                        filter.defaultRank=-10;
                        filter.defaultAutocompleteValue={
                            operator,
                            value:attrs.defaultValue,
                        };
                    }
                    break;
                }
            }
            if(filter.fieldName&&!attrs.string){
                const{string}=this.fields[filter.fieldName];
                filter.description=string;
            }
        }

        /**
         *ReturnsanobjectirFilterservingtocreateanir_filteindb
         *startingfromafilteroftype'favorite'.
         *@private
         *@param{Object}favorite
         *@returns{Object}
         */
        _favoriteToIrFilter(favorite){
            constirFilter={
                action_id:this.config.actionId,
                model_id:this.config.modelName,
            };

            //ir.filterfields
            if('description'infavorite){
                irFilter.name=favorite.description;
            }
            if('domain'infavorite){
                irFilter.domain=favorite.domain;
            }
            if('isDefault'infavorite){
                irFilter.is_default=favorite.isDefault;
            }
            if('orderedBy'infavorite){
                constsort=favorite.orderedBy.map(
                    ob=>ob.name+(ob.asc===false?"desc":"")
                );
                irFilter.sort=JSON.stringify(sort);
            }
            if('serverSideId'infavorite){
                irFilter.id=favorite.serverSideId;
            }
            if('userId'infavorite){
                irFilter.user_id=favorite.userId;
            }

            //Context
            constcontext=Object.assign({},favorite.context);
            if('groupBys'infavorite){
                context.group_by=favorite.groupBys;
            }
            if('comparison'infavorite){
                context.comparison=favorite.comparison;
            }
            if(Object.keys(context).length){
                irFilter.context=context;
            }

            returnirFilter;
        }

        /**
         *Returnthedomainresultingfromthecombinationoftheauto-completion
         *valuesofafilteroftype'field'.
         *@private
         *@param{Object}filter
         *@param{Object[]}filterQueryElements
         *@returns{string}
         */
        _getAutoCompletionFilterDomain(filter,filterQueryElements){
            constdomains=filterQueryElements.map(({label,value,operator})=>{
                letdomain;
                if(filter.filterDomain){
                    domain=Domain.prototype.stringToArray(
                        filter.filterDomain,
                        {
                            self:label,
                            raw_value:value,
                        }
                    );
                }else{
                    //Createnewdomain
                    domain=[[filter.fieldName,operator,value]];
                }
                returnDomain.prototype.arrayToString(domain);
            });
            returnpyUtils.assembleDomains(domains,'OR');
        }

        /**
         *Constructasinglecontextfromthecontextsof
         *filtersoftype'filter','favorite',and'field'.
         *@private
         *@returns{Object}
         */
        _getContext(groups){
            consttypes=['filter','favorite','field'];
            constcontexts=groups.reduce(
                (contexts,group)=>{
                    if(types.includes(group.type)){
                        contexts.push(...this._getGroupContexts(group));
                    }
                    returncontexts;
                },
                []
            );
            constevaluationContext=this.env.session.user_context;
            try{
                returnpyUtils.eval('contexts',contexts,evaluationContext);
            }catch(err){
                thrownewError(
                    this.env._t("Failedtoevaluatesearchcontext")+":\n"+
                    JSON.stringify(err)
                );
            }
        }

        /**
         *Computethestringrepresentationorthedescriptionofthecurrentdomainassociated
         *withadatefilterstartingfromitscorrespondingqueryelements.
         *@private
         *@param{Object}filter
         *@param{Object[]}filterQueryElements
         *@param{'domain'|'description'}[key='domain']
         *@returns{string}
         */
        _getDateFilterDomain(filter,filterQueryElements,key='domain'){
            const{fieldName,fieldType}=filter;
            constselectedOptionIds=filterQueryElements.map(queryElem=>queryElem.optionId);
            constdateFilterRange=constructDateDomain(
                this.referenceMoment,fieldName,fieldType,selectedOptionIds,
            );
            returndateFilterRange[key];
        }

        /**
         *Returnthestringorarrayrepresentationofadomaincreatedbycombining
         *appropriately(withan'AND')thedomainscomingfromtheactivegroups
         *oftype'filter','favorite',and'field'.
         *@private
         *@param{Object[]}groups
         *@returns{string}
         */
        _getDomain(groups){
            consttypes=['filter','favorite','field'];
            constdomains=[];
            for(constgroupofgroups){
                if(types.includes(group.type)){
                    domains.push(this._getGroupDomain(group));
                }
            }
            returnpyUtils.assembleDomains(domains,'AND');
        }

        /**
         *Getthefilterdescriptiontouseinthesearchbarasafacet.
         *@private
         *@param{Object}activity
         *@param{Object}activity.filter
         *@param{Object[]}activity.filterQueryElements
         *@returns{string}
         */
        _getFacetDescriptions(activities,type){
            constfacetDescriptions=[];
            if(type==='field'){
                for(constqueryElemofactivities[0].filterQueryElements){
                    facetDescriptions.push(queryElem.label);
                }
            }elseif(type==='groupBy'){
                for(const{filter,filterQueryElements}ofactivities){
                    if(filter.hasOptions){
                        for(constqueryElemoffilterQueryElements){
                            constoption=this.intervalOptions.find(
                                o=>o.id===queryElem.optionId
                            );
                            facetDescriptions.push(filter.description+':'+option.description);
                        }
                    }else{
                        facetDescriptions.push(filter.description);
                    }
                }
            }else{
                letfacetDescription;
                for(const{filter,filterQueryElements}ofactivities){
                    //filter,favoriteandcomparison
                    facetDescription=filter.description;
                    if(filter.isDateFilter){
                        constdescription=this._getDateFilterDomain(
                            filter,filterQueryElements,'description'
                        );
                        facetDescription+=`:${description}`;
                    }
                    facetDescriptions.push(facetDescription);
                }
            }
            returnfacetDescriptions;
        }

        /**
         *@returns{Object[]}
         */
        _getFacets(){
            constfacets=this._getGroups().map(({activities,type,id})=>{
                constvalues=this._getFacetDescriptions(activities,type);
                consttitle=activities[0].filter.description;
                return{groupId:id,title,type,values};
            });
            returnfacets;
        }

        /**
         *Returnanarraycontainingenrichedcopiesofthefiltersoftheprovidedtype.
         *@param{Function}predicate
         *@returns{Object[]}
         */
        _getFilters(predicate){
            constfilters=[];
            Object.values(this.state.filters).forEach(filter=>{
                if((!predicate||predicate(filter))&&!filter.invisible){
                    constfilterQueryElements=this.state.query.filter(
                        queryElem=>queryElem.filterId===filter.id
                    );
                    constenrichedFilter=this._enrichFilterCopy(filter,filterQueryElements);
                    if(enrichedFilter){
                        filters.push(enrichedFilter);
                    }
                }
            });
            if(filters.some(f=>f.type==='favorite')){
                filters.sort((f1,f2)=>f1.groupNumber-f2.groupNumber);
            }
            returnfilters;
        }

        /**
        *Returnthecontextoftheprovided(active)filter.
        *@private
        *@param{Object}filter
        *@param{Object[]}filterQueryElements
        *@returns{Object}
        */
        _getFilterContext(filter,filterQueryElements){
            letcontext=filter.context||{};
            //for<field>nodes,adynamiccontext(likecontext="{'field1':self}")
            //shouldset{'field1':[value1,value2]}inthecontext
            if(filter.type==='field'&&filter.context){
                context=pyUtils.eval('context',
                    filter.context,
                    {self:filterQueryElements.map(({value})=>value)},
                );
            }
            //thefollowingcodeaimstoremodelthis:
            //https://github.com/flectra/flectra/blob/12.0/addons/web/static/src/js/views/search/search_inputs.js#L498
            //thisisrequiredforthehelpdesktourtopass
            //thisseemsweirdtoonlydothatform2ofields,butatestfailsif
            //wedoitforotherfields(myguessbeingthatthetestshouldsimply
            //beadapted)
            if(filter.type==='field'&&filter.isDefault&&filter.fieldType==='many2one'){
                context[`default_${filter.fieldName}`]=filter.defaultAutocompleteValue.value;
            }
            returncontext;
        }

        /**
         *Returnthedomainoftheprovidedfilter.
         *@private
         *@param{Object}filter
         *@param{Object[]}filterQueryElements
         *@returns{string}domain,stringrepresentationofadomain
         */
        _getFilterDomain(filter,filterQueryElements){
            if(filter.type==='filter'&&filter.hasOptions){
                const{dateFilterId}=this.activeComparison||{};
                if(this.searchMenuTypes.includes('comparison')&&dateFilterId===filter.id){
                    return"[]";
                }
                returnthis._getDateFilterDomain(filter,filterQueryElements);
            }elseif(filter.type==='field'){
                returnthis._getAutoCompletionFilterDomain(filter,filterQueryElements);
            }
            returnfilter.domain;
        }

        /**
         *ReturnthegroupBysoftheprovidedfilter.
         *@private
         *@param{Object}filter
         *@param{Object[]}filterQueryElements
         *@returns{string[]}groupBys
         */
        _getFilterGroupBys(filter,filterQueryElements){
            if(filter.type==='groupBy'){
                constfieldName=filter.fieldName;
                if(filter.hasOptions){
                    returnfilterQueryElements.map(
                        ({optionId})=>`${fieldName}:${optionId}`
                    );
                }else{
                    return[fieldName];
                }
            }else{
                returnfilter.groupBys;
            }
        }

        /**
         *ReturntheconcatenationofgroupByscommingfromtheactivefiltersof
         *type'favorite'and'groupBy'.
         *Theresultrespectstheappropriatelogic:thegroupBys
         *comingfromanactivefavorite(ifany)comefirst,thencomethe
         *groupByscommingfromtheactivefiltersoftype'groupBy'intheorder
         *definedinthis.state.query.IfnogroupBysarefound,onetriesto
         *findsomegrouBysintheactioncontext.
         *@private
         *@param{Object[]}groups
         *@returns{string[]}
         */
        _getGroupBy(groups){
            constgroupBys=groups.reduce(
                (groupBys,group)=>{
                    if(['groupBy','favorite'].includes(group.type)){
                        groupBys.push(...this._getGroupGroupBys(group));
                    }
                    returngroupBys;
                },
                []
            );
            constgroupBy=groupBys.length?groupBys:(this.actionContext.group_by||[]);
            returntypeofgroupBy==='string'?[groupBy]:groupBy;
        }

        /**
         *Returnthelistofthecontextsofthefiltersactiveinthegiven
         *group.
         *@private
         *@param{Object}group
         *@returns{Object[]}
         */
        _getGroupContexts(group){
            constcontexts=group.activities.reduce(
                (ctx,qe)=>[...ctx,this._getFilterContext(qe.filter,qe.filterQueryElements)],
                []
            );
            returncontexts;
        }

        /**
         *Returnthestringrepresentationofadomaincreatedbycombining
         *appropriately(withan'OR')thedomainscomingfromthefilters
         *activeinthegivengroup.
         *@private
         *@param{Object}group
         *@returns{string}stringrepresentationofadomain
         */
        _getGroupDomain(group){
            constdomains=group.activities.map(({filter,filterQueryElements})=>{
                returnthis._getFilterDomain(filter,filterQueryElements);
            });
            returnpyUtils.assembleDomains(domains,'OR');
        }

        /**
         *ReturnthegroupByscomingformthefiltersactiveinthegivengroup.
         *@private
         *@param{Object}group
         *@returns{string[]}
         */
        _getGroupGroupBys(group){
            constgroupBys=group.activities.reduce(
                (gb,qe)=>[...gb,...this._getFilterGroupBys(qe.filter,qe.filterQueryElements)],
                []
            );
            returngroupBys;
        }

        /**
         *Reconstructthe(active)groupsfromthequeryelements.
         *@private
         *@returns{Object[]}
         */
        _getGroups(){
            constgroups=this.state.query.reduce(
                (groups,queryElem)=>{
                    const{groupId,filterId}=queryElem;
                    letgroup=groups.find(group=>group.id===groupId);
                    constfilter=this.state.filters[filterId];
                    if(!group){
                        const{type}=filter;
                        group={
                            id:groupId,
                            type,
                            activities:[]
                        };
                        groups.push(group);
                    }
                    group.activities.push(queryElem);
                    returngroups;
                },
                []
            );
            groups.forEach(g=>this._mergeActivities(g));
            returngroups;
        }

        /**
         *UsedtogetthekeyorderedByoftheactivefavorite.
         *@private
         *@param{Object[]}groups
         *@returns{string[]}orderedBy
         */
        _getOrderedBy(groups){
            returngroups.reduce(
                (orderedBy,group)=>{
                    if(group.type==='favorite'){
                        constfavoriteOrderedBy=group.activities[0].filter.orderedBy;
                        if(favoriteOrderedBy){
                            //Grouporderisreversedbutinnerorderiskept
                            orderedBy=[...favoriteOrderedBy,...orderedBy];
                        }
                    }
                    returnorderedBy;
                },
                []
            );
        }

        /**
         *Startingfromtheidofadatefilter,returnsthearrayofoptionidscurrentlyselected
         *forthecorrespondingfilter.
         *@private
         *@param{string}dateFilterId
         *@returns{string[]}
         */
        _getSelectedOptionIds(dateFilterId){
            constselectedOptionIds=[];
            for(constqueryElemofthis.state.query){
                if(queryElem.filterId===dateFilterId){
                    selectedOptionIds.push(queryElem.optionId);
                }
            }
            returnselectedOptionIds;
        }

        /**
         *ReturnsthelasttimeRangesobjectfoundinthequery.
         *TimeRangesobjectscanbeassociatedwithfiltersoftype'favorite'
         *or'comparison'.
         *@private
         *@param{boolean}[evaluation=false]
         *@returns{Object|null}
         */
        _getTimeRanges(evaluation){
            lettimeRanges;
            for(constqueryElemofthis.state.query.slice().reverse()){
                constfilter=this.state.filters[queryElem.filterId];
                if(filter.type==='comparison'){
                    timeRanges=this._computeTimeRanges(filter);
                    break;
                }elseif(filter.type==='favorite'&&filter.comparison){
                    timeRanges=filter.comparison;
                    break;
                }
            }
            if(timeRanges){
                if(evaluation){
                    timeRanges.range=Domain.prototype.stringToArray(timeRanges.range);
                    timeRanges.comparisonRange=Domain.prototype.stringToArray(timeRanges.comparisonRange);
                }
                returntimeRanges;
            }
            returnnull;
        }

        /**
         *Returnsafilteroftype'favorite'startingfromanir_filtercommingfromdb.
         *@private
         *@param{Object}irFilter
         *@returns{Object}
         */
        _irFilterToFavorite(irFilter){
            letuserId=irFilter.user_id||false;
            if(Array.isArray(userId)){
                userId=userId[0];
            }
            constgroupNumber=userId?FAVORITE_PRIVATE_GROUP:FAVORITE_SHARED_GROUP;
            constcontext=pyUtils.eval('context',irFilter.context,this.env.session.user_context);
            letgroupBys=[];
            if(context.group_by){
                groupBys=context.group_by;
                deletecontext.group_by;
            }
            letcomparison;
            if(context.comparison){
                comparison=context.comparison;
                deletecontext.comparison;
            }
            letsort;
            try{
                sort=JSON.parse(irFilter.sort);
            }catch(err){
                if(errinstanceofSyntaxError){
                    sort=[];
                }else{
                    throwerr;
                }
            }
            constorderedBy=sort.map(order=>{
                letfieldName;
                letasc;
                constsqlNotation=order.split('');
                if(sqlNotation.length>1){
                    //regex:\fieldName(asc|desc)?\
                    fieldName=sqlNotation[0];
                    asc=sqlNotation[1]==='asc';
                }else{
                    //legacynotation--regex:\-?fieldName\
                    fieldName=order[0]==='-'?order.slice(1):order;
                    asc=order[0]==='-'?false:true;
                }
                return{
                    asc:asc,
                    name:fieldName,
                };
            });
            constfavorite={
                context,
                description:irFilter.name,
                domain:irFilter.domain,
                groupBys,
                groupNumber,
                orderedBy,
                removable:true,
                serverSideId:irFilter.id,
                type:'favorite',
                userId,
            };
            if(irFilter.is_default){
                favorite.isDefault=irFilter.is_default;
            }
            if(comparison){
                favorite.comparison=comparison;
            }
            returnfavorite;
        }

        /**
         *Groupthequeryelementsingroup.activitiesbyqe->qe.filterId
         *andchangestheformofgroup.activitiestomakeitmoresuitableforfurther
         *computations.
         *@private
         *@param{Object}group
         */
        _mergeActivities(group){
            const{activities,type}=group;
            letres=[];
            switch(type){
                case'filter':
                case'groupBy':{
                    for(constactivityofactivities){
                        const{filterId}=activity;
                        leta=res.find(({filter})=>filter.id===filterId);
                        if(!a){
                            a={
                                filter:this.state.filters[filterId],
                                filterQueryElements:[]
                            };
                            res.push(a);
                        }
                        a.filterQueryElements.push(activity);
                    }
                    break;
                }
                case'favorite':
                case'field':
                case'comparison':{
                    //allactivitiesinthegrouphavesamefilterId
                    const{filterId}=group.activities[0];
                    constfilter=this.state.filters[filterId];
                    res.push({
                        filter,
                        filterQueryElements:group.activities
                    });
                    break;
                }
            }
            if(type==='groupBy'){
                res.forEach(activity=>{
                    activity.filterQueryElements.sort(
                        (qe1,qe2)=>rankInterval(qe1.optionId)-rankInterval(qe2.optionId)
                    );
                });
            }
            group.activities=res;
        }

        /**
         *SetthekeylabelindefaultAutocompleteValueusedbydefaultfiltersof
         *type'field'.
         *@private
         *@param{Object}filter
         */
        _prepareDefaultLabel(filter){
            const{id,fieldType,fieldName,defaultAutocompleteValue}=filter;
            const{selection,context,relation}=this.fields[fieldName];
            if(fieldType==='selection'){
                defaultAutocompleteValue.label=selection.find(
                    sel=>sel[0]===defaultAutocompleteValue.value
                )[1];
            }elseif(fieldType==='many2one'){
                constupdateLabel=label=>{
                    constqueryElem=this.state.query.find(({filterId})=>filterId===id);
                    if(queryElem){
                        queryElem.label=label;
                        defaultAutocompleteValue.label=label;
                    }
                };
                constpromise=this.env.services.rpc({
                    args:[defaultAutocompleteValue.value],
                    context:context,
                    method:'name_get',
                    model:relation,
                })
                    .then(results=>updateLabel(results[0][1]))
                    .guardedCatch(()=>updateLabel(defaultAutocompleteValue.value));
                this.labelPromises.push(promise);
            }else{
                defaultAutocompleteValue.label=defaultAutocompleteValue.value;
            }
        }

        /**
         *ComputethesearchQueryandsaveitasanir_filterindb.
         *Noevaluationofdomainsisdoneinordertokeepthemdynamic.
         *Iftheoperationissuccessful,anewfilteroftype'favorite'is
         *createdandactivated.
         *@private
         *@param{Object}preFilter
         *@returns{Promise<Object>}
         */
        async_saveQuery(preFilter){
            constgroups=this._getGroups();

            constuserContext=this.env.session.user_context;
            letcontrollerQueryParams;
            this.config.trigger("get-controller-query-params",params=>{
                controllerQueryParams=params;
            });
            controllerQueryParams=controllerQueryParams||{};
            controllerQueryParams.context=controllerQueryParams.context||{};

            constqueryContext=this._getContext(groups);
            constcontext=pyUtils.eval(
                'contexts',
                [userContext,controllerQueryParams.context,queryContext]
            );
            for(constkeyinuserContext){
                deletecontext[key];
            }

            constrequireEvaluation=false;
            constdomain=this._getDomain(groups);
            constgroupBys=this._getGroupBy(groups);
            consttimeRanges=this._getTimeRanges(requireEvaluation);
            constorderedBy=controllerQueryParams.orderedBy?
                controllerQueryParams.orderedBy:
                (this._getOrderedBy(groups)||[]);

            constuserId=preFilter.isShared?false:this.env.session.uid;
            deletepreFilter.isShared;

            Object.assign(preFilter,{
                context,
                domain,
                groupBys,
                groupNumber:userId?FAVORITE_PRIVATE_GROUP:FAVORITE_SHARED_GROUP,
                orderedBy,
                removable:true,
                userId,
            });
            if(timeRanges){
                preFilter.comparison=timeRanges;
            }
            constirFilter=this._favoriteToIrFilter(preFilter);
            constserverSideId=awaitthis.env.dataManager.create_filter(irFilter);

            preFilter.serverSideId=serverSideId;

            returnpreFilter;
        }

        //---------------------------------------------------------------------
        //Static
        //---------------------------------------------------------------------

        /**
         *@override
         *@returns{{attrs:Object,children:Object[]}}
         */
        staticextractArchInfo(archs){
            const{attrs,children}=archs.search;
            constcontrolPanelInfo={
                attrs,
                children:[],
            };
            for(constchildofchildren){
                if(child.tag!=="searchpanel"){
                    controlPanelInfo.children.push(child);
                }
            }
            returncontrolPanelInfo;
        }
    }

    ActionModel.registry.add("ControlPanel",ControlPanelModelExtension,10);

    returnControlPanelModelExtension;
});
