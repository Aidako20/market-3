flectra.define('web.PivotModel',function(require){
"usestrict";

/**
 *PivotModel
 *
 *Thepivotmodelkeepsanin-memoryrepresentationofthepivottablethatis
 *displayedonthescreen. Theexactlayoutofthisrepresentationisnotso
 *simple,becauseapivottableisatitscorea2-dimensionalobject,but
 *witha'tree'component:somerows/colscanbeexpandedsowezoomintothe
 *structure.
 *
 *However,weneedtobeabletomanipulatethedatainasomewhatefficient
 *way,andtotransformitintoalistoflinestobedisplayedbytherenderer.
 *
 *Basicalythepivottablepresentsaggregatedvaluesforvariousgroupsofrecords
 *inonedomain.Ifacomparisonisaskedfor,twodomainsareconsidered.
 *
 *Letusconsiderasimpleexampleandletusfixthevocabulary(letussupposeweareinJune2020):
 *___________________________________________________________________________________________________________________________________________
 *|                   |  Total                                                                                                            |
 *|                   |_____________________________________________________________________________________________________________________|
 *|                   |  SaleTeam1                        | SaleTeam2                        |                                     |
 *|                   |_______________________________________|______________________________________|______________________________________|
 *|                   |  Salestotal                        | Salestotal                        | Salestotal                        |
 *|                   |_______________________________________|______________________________________|______________________________________|
 *|                   |  May2020  |June2020 |Variation| May2020  |June2020 |Variation| May2020  |June2020 |Variation|
 *|____________________|______________|____________|___________|_____________|____________|___________|_____________|____________|___________|
 *|Total             |    85      |    110   | 29.4%   |    40     |   30     |  -25%   |   125     |   140    |    12%  |
 *|   Europe         |    25      |    35    |   40%   |    40     |   30     |  -25%   |    65     |    65    |     0%  |
 *|       Brussels   |     0      |    15    |  100%   |    30     |   30     |    0%   |    30     |    45    |    50%  |
 *|       Paris      |    25      |    20    |  -20%   |    10     |    0     | -100%   |    35     |    20    | -42.8%  |
 *|   NorthAmerica  |    60      |    75    |   25%   |            |           |          |    60     |    75    |    25%  |
 *|       Washington |    60      |    75    |   25%   |            |           |          |    60     |    75    |    25%  |
 *|____________________|______________|____________|___________|_____________|____________|___________|_____________|____________|___________|
 *
 *
 *METADATA:
 *
 *Intheabovepivottable,therecordshavebeengroupedusingthefields
 *
 *     continent_id,city_id
 *
 *forrowsand
 *
 *     sale_team_id
 *
 *forcolumns.
 *
 *Themeasureisthefield'sales_total'.
 *
 *Twodomainsareconsidered:'May2020'and'June2020'.
 *
 *Inthemodel,
 *
 *     -rowGroupBysisthelist[continent_id,city_id]
 *     -colGroupBysisthelist[sale_team_id]
 *     -measuresisthelist[sales_total]
 *     -domainsisthelist[d1,d2]withd1andd2domainexpressions
 *         forsaysale_dateinMay2020andJune2020,forinstance
 *         d1=[['sale_date',>=,2020-05-01],['sale_date','<=',2020-05-31]]
 *     -originsisthelist['May2020','June2020']
 *
 *DATA:
 *
 *Recallthatagroupisconstitutedbyrecords(inagivendomain)
 *thathavethesame(raw)valuesforalistoffields.
 *Thusthegroupitselfisidentifiedbythislistandthedomain.
 *Incomparisonmode,thesamegroup(forgettingthedomainpartor'originIndex')
 *canbeeventuallyfoundinthetwodomains.
 *Thisdefinesthewayinwhichthegroupsareidentifiedornot.
 *
 *Intheabovetable,(forgettingthedomain)thefollowinggroupsarefound:
 *
 *     the'rowgroups'
 *     -Total
 *     -Europe
 *     -America
 *     -Europe,Brussels
 *     -Europe,Paris
 *     -America,Washington
 *
 *     the'colgroups'
 *
 *     -Total
 *     -SaleTeam1
 *     -SaleTeam2
 *
 *     andallnontrivialcombinationsofrowgroupsandcolgroups
 *
 *     -Europe,SaleTeam1
 *     -Europe,Brussels,SaleTeam2
 *     -America,Washington,SaleTeam1
 *     -...
 *
 *Thelistoffieldsiscreatedfromtheconcatenationoftwolistsoffields,thefirstin
 *
 *[],[f1],[f1,f2],...[f1,f2,...,fn] for[f1,f2,...,fn]thefulllistofgroupbys
 *(calledrowGroupBys)usedtocreaterowgroups
 *
 *Intheexample:[],[continent_id],[continent_id,city_id].
 *
 *andthesecondin
 *[],[g1],[g1,g2],...[g1,g2,...,gm] for[g1,g2,...,gm]thefulllistofgroupbys
 *(calledcolGroupBys)usedtocreatecolgroups.
 *
 *Intheexample:[],[sale_team_id].
 *
 *Thusthereare(n+1)*(m+1)listsoffieldspossible.
 *
 *Intheexample:6listspossible,namely[],
 *                                         [continent_id],[sale_team_id],
 *                                         [continent_id,sale_team_id],[continent_id,city_id],
 *                                         [continent_id,city_id,sale_team_id]
 *
 *Agivenlististhusoftheform[f1,...,fi,g1,...,gj]orbetter[[f1,...,fi],[g1,...,gj]]
 *
 *Foreachlistoffieldspossibleandeachdomainconsidered,oneread_groupisdone
 *andgivesresultsoftheform(anexceptionforlist[])
 *
 *g={
 * f1:v1,...,fi:vi,
 * g1:w1,...,gj:wj,
 * m1:x1,...,mk:xk,
 * __count:c,
 * __domain:d
 *}
 *
 *wherev1,...,vi,w1,...,Wjare'values'forthecorrespondingfieldsand
 *m1,...,mkarethefieldsselectedasmeasures.
 *
 *Forexample,g={
 *     continent_id:[1,'Europe']
 *     sale_team_id:[1,'SaleTeam1']
 *     sales_count:25,
 *     __count:4
 *     __domain:[
 *                 ['sale_date',>=,2020-05-01],['sale_date','<=',2020-05-31],
 *                 ['continent_id','=',1],
 *                 ['sale_team_id','=',1]
 *               ]
 *}
 *
 *Thustheabovegroupgisfullydeterminedby[[v1,...,vi],[w1,...,wj]]andthebasedomain
 *orthecorresponding'originIndex'.
 *
 *Whenj=0,gcorrespondstoarowgroup(oralsorowheader)andisoftheform[[v1,...,vi],[]]ormoresimply[v1,...vi]
 *(notforgettingthelist[v1,...vi]comesfromleft).
 *Wheni=0,gcorrespondstoacolgroup(orcolheader)andisoftheform[[],[w1,...,wj]]ormoresimply[w1,...,wj].
 *
 *Agenericgroupgasabove[[v1,...,vi],[w1,...,wj]]correspondstothetwoheaders[[v1,...,vi],[]]
 *and[[],[w1,...,wj]].
 *
 *Hereisadescriptionofthedatastructuremanipulatedbythepivotmodel.
 *
 *Fiveobjectscontainallthedatafromtheread_groups
 *
 *     -rowGroupTree:containsinformationonrowheaders
 *            thenodescorrespondtothegroupsoftheform[[v1,...,vi],[]]
 *            Therootis[[],[]].
 *            Anode[[v1,...,vl],[]]hasasdirectchildrenthenodesoftheform[[v1,...,vl,v],[]],
 *            thismeansthatadirectchildisobtainedbygroupingrecordsusingthesinglefieldfi+1
 *
 *            Thestructureateachlevelisoftheform
 *
 *            {
 *                 root:{
 *                     values:[v1,...,vl],
 *                     labels:[la1,...,lal]
 *                 },
 *                 directSubTrees:{
 *                     v=>{
 *                             root:{
 *                                 values:[v1,...,vl,v]
 *                                 labels:[label1,...,labell,label]
 *                             },
 *                             directSubTrees:{...}
 *                         },
 *                     v'=>{...},
 *                     ...
 *                 }
 *            }
 *
 *            (directSubTreesisaMapinstance)
 *
 *            Intheexample,therowGroupTreeis:
 *
 *            {
 *                 root:{
 *                     values:[],
 *                     labels:[]
 *                 },
 *                 directSubTrees:{
 *                     1=>{
 *                             root:{
 *                                 values:[1],
 *                                 labels:['Europe'],
 *                             },
 *                             directSubTrees:{
 *                                 1=>{
 *                                         root:{
 *                                             values:[1,1],
 *                                             labels:['Europe','Brussels'],
 *                                         },
 *                                         directSubTrees:newMap(),
 *                                 },
 *                                 2=>{
 *                                         root:{
 *                                             values:[1,2],
 *                                             labels:['Europe','Paris'],
 *                                         },
 *                                         directSubTrees:newMap(),
 *                                 },
 *                             },
 *                         },
 *                     2=>{
 *                             root:{
 *                                 values:[2],
 *                                 labels:['America'],
 *                             },
 *                             directSubTrees:{
 *                                 3=>{
 *                                         root:{
 *                                             values:[2,3],
 *                                             labels:['America','Washington'],
 *                                         }
 *                                         directSubTrees:newMap(),
 *                                 },
 *                             },
 *                     },
 *                 },
 *            }
 *
 *     -colGroupTree:containsinformationoncolheaders
 *             Thesameasabovewithrightinsteadofleft
 *
 *     -measurements:containsinformationonmeasurevaluesforallthegroups
 *
 *             theobjectkeysareoftheformJSON.stringify([[v1,...,vi],[w1,...,wj]])
 *             andvaluesarearraysoflengthequaltonumberoforiginscontainingobjectsoftheform
 *                 {m1:x1,...,mk:xk}
 *             Thestructurelookslike
 *
 *             {
 *                 JSON.stringify([[],[]]):[{m1:x1,...,mk:xk},{m1:x1',...,mk:xk'},...]
 *                 ....
 *                 JSON.stringify([[v1,...,vi],[w1,...,wj]]):[{m1:y1',...,mk:yk'},{m1:y1',...,mk:yk'},...],
 *                 ....
 *                 JSON.stringify([[v1,...,vn],[w1,...,wm]]):[{m1:z1',...,mk:zk'},{m1:z1',...,mk:zk'},...],
 *             }
 *             Thusthestructurecontainsallinformationforallgroupsandalloriginsonmeasurevalues.
 *
 *
 *             this.measurments["[[],[]]"][0]['foo']givesthevalueofthemeasure'foo'forthegroup'Total'andthe
 *             firstdomain(origin).
 *
 *             Intheexample:
 *                 {
 *                     "[[],[]]":[{'sales_total':125},{'sales_total':140}]                     (total/total)
 *                     ...
 *                     "[[1,2],[2]]":[{'sales_total':10},{'sales_total':0}]                  (Europe/Paris/SaleTeam2)
 *                     ...
 *                 }
 *
 *     -counts:containsinformationonthenumberofrecordsineachgroups
 *             Thestructureissimilartotheabovebutthearrayscontainsnumbers(counts)
 *     -groupDomains:
 *             Thestructureissimilartotheabovebutthearrayscontainsdomains
 *
 *     Withthislightdatastructures,allmanipulationdonebythemodelareeasedandredundanciesarelimited.
 *     Eachtimearenderingoranexportofthedatahastobedone,thepivottableisgeneratedbythe_getTablefunction.
 */

varAbstractModel=require('web.AbstractModel');
varconcurrency=require('web.concurrency');
varcore=require('web.core');
vardataComparisonUtils=require('web.dataComparisonUtils');
constDomain=require('web.Domain');
varmathUtils=require('web.mathUtils');
varsession=require('web.session');


var_t=core._t;
varcartesian=mathUtils.cartesian;
varcomputeVariation=dataComparisonUtils.computeVariation;
varsections=mathUtils.sections;

varPivotModel=AbstractModel.extend({
    /**
     *@override
     *@param{Object}params
     */
    init:function(){
        this._super.apply(this,arguments);
        this.numbering={};
        this.data=null;
        this._loadDataDropPrevious=newconcurrency.DropPrevious();
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *AddagroupBytorowGroupBysorcolGroupBysaccordingtoprovidedtype.
     *
     *@param{string}groupBy
     *@param{'row'|'col'}type
     */
    addGroupBy:function(groupBy,type){
        if(type==='row'){
            this.data.expandedRowGroupBys.push(groupBy);
        }else{
            this.data.expandedColGroupBys.push(groupBy);
        }
    },
    /**
     *ClosethegroupwithidgivenbygroupId.Atypemustbespecified
     *incasegroupIdis[[],[]](theidofthegroup'Total')becausethis
     *groupispresentinbothcolGroupTreeandrowGroupTree.
     *
     *@param{Array[]}groupId
     *@param{'row'|'col'}type
     */
    closeGroup:function(groupId,type){
        vargroupBys;
        varexpandedGroupBys;
        letkeyPart;
        vargroup;
        vartree;
        if(type==='row'){
            groupBys=this.data.rowGroupBys;
            expandedGroupBys=this.data.expandedRowGroupBys;
            tree=this.rowGroupTree;
            group=this._findGroup(this.rowGroupTree,groupId[0]);
            keyPart=0;
        }else{
            groupBys=this.data.colGroupBys;
            expandedGroupBys=this.data.expandedColGroupBys;
            tree=this.colGroupTree;
            group=this._findGroup(this.colGroupTree,groupId[1]);
            keyPart=1;
        }

        constgroupIdPart=groupId[keyPart];
        constrange=groupIdPart.map((_,index)=>index);
        functionkeep(key){
            constidPart=JSON.parse(key)[keyPart];
            returnrange.some(index=>groupIdPart[index]!==idPart[index])||
                    idPart.length=== groupIdPart.length;
        }
        functionomitKeys(object){
            constnewObject={};
            for(constkeyinobject){
                if(keep(key)){
                    newObject[key]=object[key];
                }
            }
            returnnewObject;
        }
        this.measurements=omitKeys(this.measurements);
        this.counts=omitKeys(this.counts);
        this.groupDomains=omitKeys(this.groupDomains);

        group.directSubTrees.clear();
        deletegroup.sortedKeys;
        varnewGroupBysLength=this._getTreeHeight(tree)-1;
        if(newGroupBysLength<=groupBys.length){
            expandedGroupBys.splice(0);
            groupBys.splice(newGroupBysLength);
        }else{
            expandedGroupBys.splice(newGroupBysLength-groupBys.length);
        }
    },
    /**
     *ReloadtheviewwiththecurrentrowGroupBysandcolGroupBys
     *Thisistheeasiestwaytoexpandallthegroupsthatarenotexpanded
     *
     *@returns{Promise}
     */
    expandAll:function(){
        returnthis._loadData();
    },
    /**
     *ExpandagroupbyusinggroupBytosplitit.
     *
     *@param{Object}group
     *@param{string}groupBy
     *@returns{Promise}
     */
    expandGroup:asyncfunction(group,groupBy){
        varleftDivisors;
        varrightDivisors;

        if(group.type==='row'){
            leftDivisors=[[groupBy]];
            rightDivisors=sections(this._getGroupBys().colGroupBys);
        }else{
            leftDivisors=sections(this._getGroupBys().rowGroupBys);
            rightDivisors=[[groupBy]];
        }
        vardivisors=cartesian(leftDivisors,rightDivisors);

        deletegroup.type;
        returnthis._subdivideGroup(group,divisors);
    },
    /**
     *Exportmodeldatainaformsuitableforaneasyencodingofthepivot
     *tableinexcell.
     *
     *@returns{Object}
     */
    exportData:function(){
        varmeasureCount=this.data.measures.length;
        varoriginCount=this.data.origins.length;

        vartable=this._getTable();

        //processheaders
        varheaders=table.headers;
        varcolGroupHeaderRows;
        varmeasureRow=[];
        varoriginRow=[];

        functionprocessHeader(header){
            varinTotalColumn=header.groupId[1].length===0;
            return{
                title:header.title,
                width:header.width,
                height:header.height,
                is_bold:!!header.measure&&inTotalColumn
            };
        }

        if(originCount>1){
            colGroupHeaderRows=headers.slice(0,headers.length-2);
            measureRow=headers[headers.length-2].map(processHeader);
            originRow=headers[headers.length-1].map(processHeader);
        }else{
            colGroupHeaderRows=headers.slice(0,headers.length-1);
            measureRow=headers[headers.length-1].map(processHeader);
        }

        //removetheemptyheadersonleftside
        colGroupHeaderRows[0].splice(0,1);

        colGroupHeaderRows=colGroupHeaderRows.map(function(headerRow){
            returnheaderRow.map(processHeader);
        });

        //processrows
        vartableRows=table.rows.map(function(row){
            return{
                title:row.title,
                indent:row.indent,
                values:row.subGroupMeasurements.map(function(measurement){
                    varvalue=measurement.value;
                    if(value===undefined){
                        value="";
                    }elseif(measurement.originIndexes.length>1){
                        //inthatcasethevalueisavariationanda
                        //numberbetween0and1
                        value=value*100;
                    }
                    return{
                        is_bold:measurement.isBold,
                        value:value,
                    };
                }),
            };
        });

        return{
            col_group_headers:colGroupHeaderRows,
            measure_headers:measureRow,
            origin_headers:originRow,
            rows:tableRows,
            measure_count:measureCount,
            origin_count:originCount,
        };
    },
    /**
     *Swapthepivotcolumnsandtherows.Itisasynchronousoperation.
     */
    flip:function(){
        //swapthedata:themaincolumnandthemainrow
        vartemp=this.rowGroupTree;
        this.rowGroupTree=this.colGroupTree;
        this.colGroupTree=temp;

        //weneedtoupdatetherecordmetadata:(expanded)rowandcolgroupBys
        temp=this.data.rowGroupBys;
        this.data.groupedBy=this.data.colGroupBys;
        this.data.rowGroupBys=this.data.colGroupBys;
        this.data.colGroupBys=temp;
        temp=this.data.expandedColGroupBys;
        this.data.expandedColGroupBys=this.data.expandedRowGroupBys;
        this.data.expandedRowGroupBys=temp;

        functiontwistKey(key){
            returnJSON.stringify(JSON.parse(key).reverse());
        }

        functiontwist(object){
            varnewObject={};
            Object.keys(object).forEach(function(key){
                varvalue=object[key];
                newObject[twistKey(key)]=value;
            });
            returnnewObject;
        }

        this.measurements=twist(this.measurements);
        this.counts=twist(this.counts);
        this.groupDomains=twist(this.groupDomains);
    },
    /**
     *@override
     *
     *@param{Object}[options]
     *@param{boolean}[options.raw=false]
     *@returns{Object}
     */
    __get:function(options){
        options=options||{};
        varraw=options.raw||false;
        vargroupBys=this._getGroupBys();
        varstate={
            colGroupBys:groupBys.colGroupBys,
            context:this.data.context,
            domain:this.data.domain,
            fields:this.fields,
            hasData:this._hasData(),
            isSample:this.isSampleModel,
            measures:this.data.measures,
            origins:this.data.origins,
            rowGroupBys:groupBys.rowGroupBys,
            selectionGroupBys:this._getSelectionGroupBy(groupBys),
            modelName:this.modelName
        };
        if(!raw&&state.hasData){
            state.table=this._getTable();
            state.tree=this.rowGroupTree;
        }
        returnstate;
    },
    /**
     *Returnsthetotalnumberofcolumnsofthepivottable.
     *
     *@returns{integer}
     */
    getTableWidth:function(){
        varleafCounts=this._getLeafCounts(this.colGroupTree);
        returnleafCounts[JSON.stringify(this.colGroupTree.root.values)]+2;
    },
    /**
     *@override
     *
     *@param{Object}params
     *@param{boolean}[params.compare=false]
     *@param{Object}params.context
     *@param{Object}params.fields
     *@param{string[]}[params.groupedBy]
     *@param{string[]}params.colGroupBys
     *@param{Array[]}params.domain
     *@param{string[]}params.measures
     *@param{string[]}params.rowGroupBys
     *@param{string}[params.default_order]
     *@param{string}params.modelName
     *@param{Object[]}params.groupableFields
     *@param{Object}params.timeRanges
     *@returns{Promise}
     */
    __load:function(params){
        this.initialDomain=params.domain;
        this.initialRowGroupBys=params.context.pivot_row_groupby||params.rowGroupBys;
        this.defaultGroupedBy=params.groupedBy;

        this.fields=params.fields;
        this.modelName=params.modelName;
        this.groupableFields=params.groupableFields;
        constmeasures=this._processMeasures(params.context.pivot_measures)||
                            params.measures.map(m=>m);
        this.data={
            expandedRowGroupBys:[],
            expandedColGroupBys:[],
            domain:this.initialDomain,
            context:_.extend({},session.user_context,params.context),
            groupedBy:params.context.pivot_row_groupby||params.groupedBy,
            colGroupBys:params.context.pivot_column_groupby||params.colGroupBys,
            measures,
            timeRanges:params.timeRanges,
        };
        this._computeDerivedParams();

        this.data.groupedBy=this.data.groupedBy.slice();
        this.data.rowGroupBys=!_.isEmpty(this.data.groupedBy)?this.data.groupedBy:this.initialRowGroupBys.slice();

        vardefaultOrder=params.default_order&&params.default_order.split('');
        if(defaultOrder){
            this.data.sortedColumn={
                groupId:[[],[]],
                measure:defaultOrder[0],
                order:defaultOrder[1]?defaultOrder[1]:'asc',
            };
        }
        returnthis._loadData();
    },
    /**
     *@override
     *
     *@param{any}handlethisparameterisignored
     *@param{Object}params
     *@param{boolean}[params.compare=false]
     *@param{Object}params.context
     *@param{string[]}[params.groupedBy]
     *@param{Array[]}params.domain
     *@param{string[]}params.groupBy
     *@param{string[]}params.measures
     *@param{Object}[params.timeRanges]
     *@returns{Promise}
     */
    __reload:function(handle,params){
        varself=this;
        varoldColGroupBys=this.data.colGroupBys;
        varoldRowGroupBys=this.data.rowGroupBys;
        if('context'inparams){
            this.data.context=params.context;
            this.data.colGroupBys=params.context.pivot_column_groupby||this.data.colGroupBys;
            this.data.groupedBy=params.context.pivot_row_groupby||this.data.groupedBy;
            this.data.measures=this._processMeasures(params.context.pivot_measures)||this.data.measures;
            this.defaultGroupedBy=this.data.groupedBy.length?this.data.groupedBy:this.defaultGroupedBy;
        }
        if('domain'inparams){
            this.data.domain=params.domain;
            this.initialDomain=params.domain;
        }else{
            this.data.domain=this.initialDomain;
        }
        if('groupBy'inparams){
            this.data.groupedBy=params.groupBy.length?params.groupBy:this.defaultGroupedBy;
        }
        if('timeRanges'inparams){
            this.data.timeRanges=params.timeRanges;
        }
        this._computeDerivedParams();

        this.data.groupedBy=this.data.groupedBy.slice();
        this.data.rowGroupBys=!_.isEmpty(this.data.groupedBy)?this.data.groupedBy:this.initialRowGroupBys.slice();

        if(!_.isEqual(oldRowGroupBys,self.data.rowGroupBys)){
            this.data.expandedRowGroupBys=[];
        }
        if(!_.isEqual(oldColGroupBys,self.data.colGroupBys)){
            this.data.expandedColGroupBys=[];
        }

        if('measure'inparams){
            returnthis._toggleMeasure(params.measure);
        }

        if(!this._hasData()){
            returnthis._loadData();
        }

        varoldRowGroupTree=this.rowGroupTree;
        varoldColGroupTree=this.colGroupTree;
        returnthis._loadData().then(function(){
            if(_.isEqual(oldRowGroupBys,self.data.rowGroupBys)){
                self._pruneTree(self.rowGroupTree,oldRowGroupTree);
            }
            if(_.isEqual(oldColGroupBys,self.data.colGroupBys)){
                self._pruneTree(self.colGroupTree,oldColGroupTree);
            }
        });
    },
    /**
     *Sorttherows,dependingonthevaluesofagivencolumn. Thisisan
     *in-memorysort.
     *
     *@param{Object}sortedColumn
     *@param{number[]}sortedColumn.groupId
     */
    sortRows:function(sortedColumn){
        varself=this;
        varcolGroupValues=sortedColumn.groupId[1];
        sortedColumn.originIndexes=sortedColumn.originIndexes||[0];
        this.data.sortedColumn=sortedColumn;

        varsortFunction=function(tree){
            returnfunction(subTreeKey){
                varsubTree=tree.directSubTrees.get(subTreeKey);
                vargroupIntersectionId=[subTree.root.values,colGroupValues];
                varvalue=self._getCellValue(
                    groupIntersectionId,
                    sortedColumn.measure,
                    sortedColumn.originIndexes
                )||0;
                returnsortedColumn.order==='asc'?value:-value;
            };
        };

        this._sortTree(sortFunction,this.rowGroupTree);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Addlabels/valuesintheprovidedgroupTree.Anewleafiscreatedin
     *thegroupTreewitharootobjectcorrespondingtothegroupwithgiven
     *labels/values.
     *
     *@private
     *@param{Object}groupTree,eitherthis.rowGroupTreeorthis.colGroupTree
     *@param{string[]}labels
     *@param{Array}values
     */
    _addGroup:function(groupTree,labels,values){
        vartree=groupTree;
        //weassumeherethatthegroupwithvaluevalue.slice(value.length-2)hasalreadybeenadded.
        values.slice(0,values.length-1).forEach(function(value){
            tree=tree.directSubTrees.get(value);
        });
        constvalue=values[values.length-1];
        if(tree.directSubTrees.has(value)){
            return;
        }
        tree.directSubTrees.set(value,{
            root:{
                labels:labels,
                values:values,
            },
            directSubTrees:newMap(),
        });
    },
    /**
     *ComputewhatshouldbeusedasrowGroupBysbythepivotview
     *
     *@private
     *@returns{string[]}
     */
    _computeRowGroupBys:function(){
        return!_.isEmpty(this.data.groupedBy)?this.data.groupedBy:this.initialRowGroupBys;
    },
    /**
     *FindagroupwithgivenvaluesintheprovidedgroupTree,either
     *this.rowGrouptreeorthis.colGroupTree.
     *
     *@private
     *@param {Object}groupTree
     *@param {Array}values
     *@returns{Object}
     */
    _findGroup:function(groupTree,values){
        vartree=groupTree;
        values.slice(0,values.length).forEach(function(value){
            tree=tree.directSubTrees.get(value);
        });
        returntree;
    },
    /**
     *IncaseoriginIndexisanarrayoflength1,thusasingleorigin
     *index,returnsthegivenmeasureforagroupdeterminedbytheid
     *groupIdandtheoriginindex.
     *IforiginIndexesisanarrayoflength2,wecomputethevariation
     *otthemeasurevaluesforthegroupsdeterminedbygroupIdandthe
     *differentoriginindexes.
     *
     *@private
     *@param {Array[]}groupId
     *@param {string}measure
     *@param {number[]}originIndexes
     *@returns{number}
     */
    _getCellValue:function(groupId,measure,originIndexes){
        varself=this;
        varkey=JSON.stringify(groupId);
        if(!self.measurements[key]){
            return;
        }
        varvalues=originIndexes.map(function(originIndex){
            returnself.measurements[key][originIndex][measure];
        });
        if(originIndexes.length>1){
            returncomputeVariation(values[1],values[0]);
        }else{
            returnvalues[0];
        }
    },
    /**
     *ReturnstherowGroupBysandcolGroupBysarraysthat
     *areactuallyusedbythepivotviewinternally
     *(forread_grouporotherpurpose)
     *
     *@private
     *@returns{Object}withkeyscolGroupBysandrowGroupBys
     */
    _getGroupBys:function(){
        return{
            colGroupBys:this.data.colGroupBys.concat(this.data.expandedColGroupBys),
            rowGroupBys:this.data.rowGroupBys.concat(this.data.expandedRowGroupBys),
        };
    },
    /**
     *Returnsadomainrepresentationofagroup
     *
     *@private
     *@param {Object}group
     *@param {Array}group.colValues
     *@param {Array}group.rowValues
     *@param {number}group.originIndex
     *@returns{Array[]}
     */
    _getGroupDomain:function(group){
        varkey=JSON.stringify([group.rowValues,group.colValues]);
        returnthis.groupDomains[key][group.originIndex];
    },
    /**
     *Returnsthegroupsanitizedlabels.
     *
     *@private
     *@param {Object}group
     *@param {string[]}groupBys
     *@returns{string[]}
     */
    _getGroupLabels:function(group,groupBys){
        varself=this;
        returngroupBys.map(function(groupBy){
            returnself._sanitizeLabel(group[groupBy],groupBy);
        });
    },
    /**
     *Returnsapromisethatreturnstheannotatedread_groupresults
     *correspondingtoapartitionofthegivengroupobtainedusingthegiven
     *rowGroupByandcolGroupBy.
     *
     *@private
     *@param {Object}group
     *@param {string[]}rowGroupBy
     *@param {string[]}colGroupBy
     *@returns{Promise}
     */
    _getGroupSubdivision:function(group,rowGroupBy,colGroupBy){
        vargroupDomain=this._getGroupDomain(group);
        varmeasureSpecs=this._getMeasureSpecs();
        vargroupBy=rowGroupBy.concat(colGroupBy);
        returnthis._rpc({
            model:this.modelName,
            method:'read_group',
            context:this.data.context,
            domain:groupDomain,
            fields:measureSpecs,
            groupBy:groupBy,
            lazy:false,
        }).then(function(subGroups){
            return{
                group:group,
                subGroups:subGroups,
                rowGroupBy:rowGroupBy,
                colGroupBy:colGroupBy
            };
        });
    },
    /**
     *Returnsthegroupsanitizedvalues.
     *
     *@private
     *@param {Object}group
     *@param {string[]}groupBys
     *@returns{Array}
     */
    _getGroupValues:function(group,groupBys){
        varself=this;
        returngroupBys.map(function(groupBy){
            returnself._sanitizeValue(group[groupBy]);
        });
    },
    /**
     *Returnstheleafcountsofeachgroupinsidethegiventree.
     *
     *@private
     *@param{Object}tree
     *@returns{Object}keysaregroupids
     */
    _getLeafCounts:function(tree){
        varself=this;
        varleafCounts={};
        varleafCount;
        if(!tree.directSubTrees.size){
            leafCount=1;
        }else{
            leafCount=[...tree.directSubTrees.values()].reduce(
                function(acc,subTree){
                    varsubLeafCounts=self._getLeafCounts(subTree);
                    _.extend(leafCounts,subLeafCounts);
                    returnacc+leafCounts[JSON.stringify(subTree.root.values)];
                },
                0
            );
        }

        leafCounts[JSON.stringify(tree.root.values)]=leafCount;
        returnleafCounts;
    },
    /**
     *Returnsthegroupsanitizedmeasurevaluesforthemeasuresin
     *this.data.measures(thatmigthcontain'__count',notreallyafieldName).
     *
     *@private
     *@param {Object}group
     *@returns{Array}
     */
    _getMeasurements:function(group){
        varself=this;
        returnthis.data.measures.reduce(
            function(measurements,fieldName){
                varmeasurement=group[fieldName];
                if(measurementinstanceofArray){
                    //casefieldismany2oneandusedasmeasureandgroupBysimultaneously
                    measurement=1;
                }
                if(self.fields[fieldName].type==='boolean'&&measurementinstanceofBoolean){
                    measurement=measurement?1:0;
                }
                if(self.data.origins.length>1&&!measurement){
                    measurement=0;
                }
                measurements[fieldName]=measurement;
                returnmeasurements;
            },
            {}
        );
    },
    /**
     *Returnsadescriptionofthemeasuresrowofthepivottable
     *
     *@private
     *@param{Object[]}columnsforwhichmeasurecellsmustbegenerated
     *@returns{Object[]}
     */
    _getMeasuresRow:function(columns){
        varself=this;
        varsortedColumn=this.data.sortedColumn||{};
        varmeasureRow=[];

        columns.forEach(function(column){
            self.data.measures.forEach(function(measure){
                varmeasureCell={
                    groupId:column.groupId,
                    height:1,
                    measure:measure,
                    title:self.fields[measure].string,
                    width:2*self.data.origins.length-1,
                };
                if(sortedColumn.measure===measure&&
                    _.isEqual(sortedColumn.groupId,column.groupId)){
                    measureCell.order=sortedColumn.order;
                }
                measureRow.push(measureCell);
            });
        });

        returnmeasureRow;
    },
    /**
     *Returnsthelistofmeasurespecsassociatedwithdata.measures,i.e.
     *ameasure'fieldName'becomes'fieldName:groupOperator'where
     *groupOperatoristhevaluespecifiedonthefield'fieldName'for
     *thekeygroup_operator.
     *
     *@private
     *@return{string[]}
     */
    _getMeasureSpecs:function(){
        varself=this;
        returnthis.data.measures.reduce(
            function(acc,measure){
                if(measure==='__count'){
                    acc.push(measure);
                    returnacc;
                }
                vartype=self.fields[measure].type;
                vargroupOperator=self.fields[measure].group_operator;
                if(type==='many2one'){
                    groupOperator='count_distinct';
                }
                if(groupOperator===undefined){
                    thrownewError("Noaggregatefunctionhasbeenprovidedforthemeasure'"+measure+"'");
                }
                acc.push(measure+':'+groupOperator);
                returnacc;
            },
            []
        );
    },
    /**
     *Makesurethatthelabelsofdifferentmany2onevaluesaredistinguished
     *bynumberingthemifnecessary.
     *
     *@private
     *@param{Array}label
     *@param{string}fieldName
     *@returns{string}
     */
    _getNumberedLabel:function(label,fieldName){
        varid=label[0];
        varname=label[1];
        this.numbering[fieldName]=this.numbering[fieldName]||{};
        this.numbering[fieldName][name]=this.numbering[fieldName][name]||{};
        varnumbers=this.numbering[fieldName][name];
        numbers[id]=numbers[id]||_.size(numbers)+1;
        returnname+(numbers[id]>1?" ("+numbers[id]+")":"");
    },
    /**
     *Returnsadescriptionoftheoriginsrowofthepivottable
     *
     *@private
     *@param{Object[]}columnsforwhichorigincellsmustbegenerated
     *@returns{Object[]}
     */
    _getOriginsRow:function(columns){
        varself=this;
        varsortedColumn=this.data.sortedColumn||{};
        varoriginRow=[];

        columns.forEach(function(column){
            vargroupId=column.groupId;
            varmeasure=column.measure;
            varisSorted=sortedColumn.measure===measure&&
                _.isEqual(sortedColumn.groupId,groupId);
            varisSortedByOrigin=isSorted&&!sortedColumn.originIndexes[1];
            varisSortedByVariation=isSorted&&sortedColumn.originIndexes[1];

            self.data.origins.forEach(function(origin,originIndex){
                varoriginCell={
                    groupId:groupId,
                    height:1,
                    measure:measure,
                    originIndexes:[originIndex],
                    title:origin,
                    width:1,
                };
                if(isSortedByOrigin&&sortedColumn.originIndexes[0]===originIndex){
                    originCell.order=sortedColumn.order;
                }
                originRow.push(originCell);

                if(originIndex>0){
                    varvariationCell={
                        groupId:groupId,
                        height:1,
                        measure:measure,
                        originIndexes:[originIndex-1,originIndex],
                        title:_t('Variation'),
                        width:1,
                    };
                    if(isSortedByVariation&&sortedColumn.originIndexes[1]===originIndex){
                        variationCell.order=sortedColumn.order;
                    }
                    originRow.push(variationCell);
                }

            });
        });

        returnoriginRow;
    },

    /**
     *Gettheselectionneededtodisplaythegroupbydropdown
     *@returns{Object[]}
     *@private
     */
    _getSelectionGroupBy:function(groupBys){
        letgroupedFieldNames=groupBys.rowGroupBys
            .concat(groupBys.colGroupBys)
            .map(function(g){
                returng.split(':')[0];
            });

        varfields=Object.keys(this.groupableFields)
            .map((fieldName,index)=>{
                return{
                    name:fieldName,
                    field:this.groupableFields[fieldName],
                    active:groupedFieldNames.includes(fieldName)
                }
            })
            .sort((left,right)=>left.field.string<right.field.string?-1:1);
        returnfields;
    },

    /**
     *Returnsadescriptionofthepivottable.
     *
     *@private
     *@returns{Object}
     */
    _getTable:function(){
        varheaders=this._getTableHeaders();
        return{
            headers:headers,
            rows:this._getTableRows(this.rowGroupTree,headers[headers.length-1]),
        };
    },
    /**
     *Returnsthelistofheaderrowsofthepivottable:thecolgrouprows
     *(dependingonthecolgroupbys),themeasuresrowandoptionnalythe
     *originsrow(iftherearemorethanoneorigins).
     *
     *@private
     *@returns{Object[]}
     */
    _getTableHeaders:function(){
        varcolGroupBys=this._getGroupBys().colGroupBys;
        varheight=colGroupBys.length+1;
        varmeasureCount=this.data.measures.length;
        varoriginCount=this.data.origins.length;
        varleafCounts=this._getLeafCounts(this.colGroupTree);
        varheaders=[];
        varmeasureColumns=[];//usedtogeneratethemeasurecells

        //1)generatecolgrouprows(totalrow+onerowforeachcolgroupby)
        varcolGroupRows=(newArray(height)).fill(0).map(function(){
            return[];
        });
        //blanktopleftcell
        colGroupRows[0].push({
            height:height+1+(originCount>1?1:0),//+measuresrows[+originsrow]
            title:"",
            width:1,
        });

        //colgroupbycellswithgroupvalues
        /**
         *Recursivefunctionthatgeneratestheheadercellscorrespondingto
         *thegroupsofagiventree.
         *
         *@param{Object}tree
         */
        functiongenerateTreeHeaders(tree,fields){
            vargroup=tree.root;
            varrowIndex=group.values.length;
            varrow=colGroupRows[rowIndex];
            vargroupId=[[],group.values];
            varisLeaf=!tree.directSubTrees.size;
            varleafCount=leafCounts[JSON.stringify(tree.root.values)];
            varcell={
                groupId:groupId,
                height:isLeaf?(colGroupBys.length+1-rowIndex):1,
                isLeaf:isLeaf,
                label:rowIndex===0?undefined:fields[colGroupBys[rowIndex-1].split(':')[0]].string,
                title:group.labels[group.labels.length-1]||_t('Total'),
                width:leafCount*measureCount*(2*originCount-1),
            };
            row.push(cell);
            if(isLeaf){
                measureColumns.push(cell);
            }

            [...tree.directSubTrees.values()].forEach(function(subTree){
                generateTreeHeaders(subTree,fields);
            });
        }

        generateTreeHeaders(this.colGroupTree,this.fields);
        //blanktoprightcellfor'Total'group(ifthereismorethatoneleaf)
        if(leafCounts[JSON.stringify(this.colGroupTree.root.values)]>1){
            vargroupId=[[],[]];
            vartotalTopRightCell={
                groupId:groupId,
                height:height,
                title:"",
                width:measureCount*(2*originCount-1),
            };
            colGroupRows[0].push(totalTopRightCell);
            measureColumns.push(totalTopRightCell);
        }
        headers=headers.concat(colGroupRows);

        //2)generatemeasuresrow
        varmeasuresRow=this._getMeasuresRow(measureColumns);
        headers.push(measuresRow);

        //3)generateoriginsrowifmorethanoneorigin
        if(originCount>1){
            headers.push(this._getOriginsRow(measuresRow));
        }

        returnheaders;
    },
    /**
     *Returnsthelistofbodyrowsofthepivottableforagiventree.
     *
     *@private
     *@param{Object}tree
     *@param{Object[]}columns
     *@returns{Object[]}
     */
    _getTableRows:function(tree,columns){
        varself=this;

        varrows=[];
        vargroup=tree.root;
        varrowGroupId=[group.values,[]];
        vartitle=group.labels[group.labels.length-1]||_t('Total');
        varindent=group.labels.length;
        varisLeaf=!tree.directSubTrees.size;
        varrowGroupBys=this._getGroupBys().rowGroupBys;

        varsubGroupMeasurements=columns.map(function(column){
            varcolGroupId=column.groupId;
            vargroupIntersectionId=[rowGroupId[0],colGroupId[1]];
            varmeasure=column.measure;
            varoriginIndexes=column.originIndexes||[0];

            varvalue=self._getCellValue(groupIntersectionId,measure,originIndexes);

            varmeasurement={
                groupId:groupIntersectionId,
                originIndexes:originIndexes,
                measure:measure,
                value:value,
                isBold:!groupIntersectionId[0].length||!groupIntersectionId[1].length,
            };
            returnmeasurement;
        });

        rows.push({
            title:title,
            label:indent===0?undefined:this.fields[rowGroupBys[indent-1].split(':')[0]].string,
            groupId:rowGroupId,
            indent:indent,
            isLeaf:isLeaf,
            subGroupMeasurements:subGroupMeasurements
        });

        varsubTreeKeys=tree.sortedKeys||[...tree.directSubTrees.keys()];
        subTreeKeys.forEach(function(subTreeKey){
            varsubTree=tree.directSubTrees.get(subTreeKey);
            rows=rows.concat(self._getTableRows(subTree,columns));
        });

        returnrows;
    },
    /**
     *returnstheheightofagivengroupTree
     *
     *@private
     *@param {Object}tree,agroupTree
     *@returns{number}
     */
    _getTreeHeight:function(tree){
        varsubTreeHeights=[...tree.directSubTrees.values()].map(this._getTreeHeight.bind(this));
        returnMath.max(0,Math.max.apply(null,subTreeHeights))+1;
    },
    /**
     *@private
     *@returns{boolean}
     */
    _hasData:function(){
        return(this.counts[JSON.stringify([[],[]])]||[]).some(function(count){
            returncount>0;
        });
    },
    /**
     *@override
     */
    _isEmpty(){
        return!this._hasData();
    },
    /**
     *Initilize/Reinitializethis.rowGroupTree,colGroupTree,measurements,
     *countsandsubdividethegroup'Total'asmanytimesitisnecessary.
     *AfirstsubdivisionwithnogroupBy(divisors.slice(0,1))ismadein
     *ordertoseeifthereisdataintheintersectionofthegroup'Total'
     *andthevariousorigins.Incasethereisnone,nonsupplementaryrpc
     *willbedone(seethecodeofsubdivideGroup).
     *Oncethepromiseresolves,this.rowGroupTree,colGroupTree,
     *measurements,countsarecorrectlyset.
     *
     *@private
     *@return{Promise}
     */
    _loadData:function(){
        varself=this;

        this.rowGroupTree={root:{labels:[],values:[]},directSubTrees:newMap()};
        this.colGroupTree={root:{labels:[],values:[]},directSubTrees:newMap()};
        this.measurements={};
        this.counts={};

        varkey=JSON.stringify([[],[]]);
        this.groupDomains={};
        this.groupDomains[key]=this.data.domains.slice(0);


        vargroup={rowValues:[],colValues:[]};
        vargroupBys=this._getGroupBys();
        varleftDivisors=sections(groupBys.rowGroupBys);
        varrightDivisors=sections(groupBys.colGroupBys);
        vardivisors=cartesian(leftDivisors,rightDivisors);

        returnthis._subdivideGroup(group,divisors.slice(0,1)).then(function(){
            returnself._subdivideGroup(group,divisors.slice(1));
        });
    },
    /**
     *Extracttheinformationintheread_groupresults(groupSubdivisions)
     *anddevelopthis.rowGroupTree,colGroupTree,measurements,counts,and
     *groupDomains.
     *Ifacolumnneedstobesorted,therowGroupTreecorrespondingtothe
     *groupissorted.
     *
     *@private
     *@param {Object}group
     *@param {Object[]}groupSubdivisions
     */
    _prepareData:function(group,groupSubdivisions){
        varself=this;

        vargroupRowValues=group.rowValues;
        vargroupRowLabels=[];
        varrowSubTree=this.rowGroupTree;
        varroot;
        if(groupRowValues.length){
            //weshouldhavelabelsinformationonhand!regretful!
            rowSubTree=this._findGroup(this.rowGroupTree,groupRowValues);
            root=rowSubTree.root;
            groupRowLabels=root.labels;
        }

        vargroupColValues=group.colValues;
        vargroupColLabels=[];
        if(groupColValues.length){
            root=this._findGroup(this.colGroupTree,groupColValues).root;
            groupColLabels=root.labels;
        }

        groupSubdivisions.forEach(function(groupSubdivision){
            groupSubdivision.subGroups.forEach(function(subGroup){

                varrowValues=groupRowValues.concat(self._getGroupValues(subGroup,groupSubdivision.rowGroupBy));
                varrowLabels=groupRowLabels.concat(self._getGroupLabels(subGroup,groupSubdivision.rowGroupBy));

                varcolValues=groupColValues.concat(self._getGroupValues(subGroup,groupSubdivision.colGroupBy));
                varcolLabels=groupColLabels.concat(self._getGroupLabels(subGroup,groupSubdivision.colGroupBy));

                if(!colValues.length&&rowValues.length){
                    self._addGroup(self.rowGroupTree,rowLabels,rowValues);
                }
                if(colValues.length&&!rowValues.length){
                    self._addGroup(self.colGroupTree,colLabels,colValues);
                }

                varkey=JSON.stringify([rowValues,colValues]);
                varoriginIndex=groupSubdivision.group.originIndex;

                if(!(keyinself.measurements)){
                    self.measurements[key]=self.data.origins.map(function(){
                        returnself._getMeasurements({});
                    });
                }
                self.measurements[key][originIndex]=self._getMeasurements(subGroup);

                if(!(keyinself.counts)){
                    self.counts[key]=self.data.origins.map(function(){
                        return0;
                    });
                }
                self.counts[key][originIndex]=subGroup.__count;

                if(!(keyinself.groupDomains)){
                    self.groupDomains[key]=self.data.origins.map(function(){
                        returnDomain.FALSE_DOMAIN;
                    });
                }
                //if__domainisnotdefinedthismeansthatweareinthe
                //casewhere
                //groupSubdivision.rowGroupBy=groupSubdivision.rowGroupBy=[]
                if(subGroup.__domain){
                    self.groupDomains[key][originIndex]=subGroup.__domain;
                }
            });
        });

        if(this.data.sortedColumn){
            this.sortRows(this.data.sortedColumn,rowSubTree);
        }
    },
    /**
     *Inthepreviewimplementationofthepivotview(a.k.a.version2),
     *thevirtualfieldusedtodisplaythenumberofrecordswasnamed
     *__count__,whereas__countisactuallytheoneusedinxml.So
     *basically,activatingafilterspecifying__countasmeasurescrashed.
     *Unfortunately,as__count__wasusedintheJS,allfilterssavedas
     *favoriteatthattimeweresavedwith__count__,andnot__count.
     *Soinorderthemakethemstillworkwiththenewimplementation,we
     *handleboth__count__and__count.
     *
     *Thisfunctionreplacesinthegivenarrayofmeasuresoccurencesof
     *'__count__'by'__count'.
     *
     *@private
     *@param{Array[string]||undefined}measures
     *@returns{Array[string]||undefined}
     */
    _processMeasures:function(measures){
        if(measures){
            return_.map(measures,function(measure){
                returnmeasure==='__count__'?'__count':measure;
            });
        }
    },
    /**
     *Determinethis.data.domainsandthis.data.originsfrom
     *this.data.domainandthis.data.timeRanges;
     *
     *@private
     */
    _computeDerivedParams:function(){
        const{range,rangeDescription,comparisonRange,comparisonRangeDescription}=this.data.timeRanges;
        if(range){
            this.data.domains=[this.data.domain.concat(comparisonRange),this.data.domain.concat(range)];
            this.data.origins=[comparisonRangeDescription,rangeDescription];
        }else{
            this.data.domains=[this.data.domain];
            this.data.origins=[""];
        }
    },
    /**
     *MakeanygroupintreealeafifitwasaleafinoldTree.
     *
     *@private
     *@param{Object}tree
     *@param{Object}oldTree
     */
    _pruneTree:function(tree,oldTree){
        if(!oldTree.directSubTrees.size){
            tree.directSubTrees.clear();
            deletetree.sortedKeys;
            return;
        }
        varself=this;
        [...tree.directSubTrees.keys()].forEach(function(subTreeKey){
            varsubTree=tree.directSubTrees.get(subTreeKey);
            if(!oldTree.directSubTrees.has(subTreeKey)){
                subTree.directSubTrees.clear();
                deletesubTreeKey.sortedKeys;
            }else{
                varoldSubTree=oldTree.directSubTrees.get(subTreeKey);
                self._pruneTree(subTree,oldSubTree);
            }
        });
    },
    /**
     *Toggletheactivestateforagivenmeasure,thenreloadthedata
     *ifthisturnsouttobenecessary.
     *
     *@param{string}fieldName
     *@returns{Promise}
     */
    _toggleMeasure:function(fieldName){
        varindex=this.data.measures.indexOf(fieldName);
        if(index!==-1){
            this.data.measures.splice(index,1);
            //inthiscase,wealreadyhavealldatainmemory,noneedto
            //actuallyreloadalesseramountofinformation
            returnPromise.resolve();
        }else{
            this.data.measures.push(fieldName);
        }
        returnthis._loadData();
    },
    /**
     *ExtractfromagroupByvaluealabel.
     *
     *@private
     *@param {any}value
     *@param {string}groupBy
     *@returns{string}
     */
    _sanitizeLabel:function(value,groupBy){
        varfieldName=groupBy.split(':')[0];
        if(value===false){
            return_t("Undefined");
        }
        if(valueinstanceofArray){
            returnthis._getNumberedLabel(value,fieldName);
        }
        if(fieldName&&this.fields[fieldName]&&(this.fields[fieldName].type==='selection')){
            varselected=_.where(this.fields[fieldName].selection,{0:value})[0];
            returnselected?selected[1]:value;
        }
        returnvalue;
    },
    /**
     *ExtractfromagroupByvaluetherawvalueofthatgroupBy(discarding
     *alabelifany)
     *
     *@private
     *@param{any}value
     *@returns{any}
     */
    _sanitizeValue:function(value){
        if(valueinstanceofArray){
            returnvalue[0];
        }
        returnvalue;
    },
    /**
     *Getallpartitionsofagivengroupusingtheprovidedlistofdivisors
     *andenrichtheobjectsofthis.rowGroupTree,colGroupTree,
     *measurements,counts.
     *
     *@private
     *@param{Object}group
     *@param{Array[]}divisors
     *@returns
     */
    _subdivideGroup:function(group,divisors){
        varself=this;

        varkey=JSON.stringify([group.rowValues,group.colValues]);

        varproms=this.data.origins.reduce(
            function(acc,origin,originIndex){
                //ifnoinformationongroupcontentisavailable,wefetchdata.
                //ifgroupisknowntobeemptyforthegivenorigin,
                //wedon'tneedtofetchdatafotthatorigin.
                if(!self.counts[key]||self.counts[key][originIndex]>0){
                    varsubGroup={
                        rowValues:group.rowValues,
                        colValues:group.colValues,
                        originIndex:originIndex
                    };
                    divisors.forEach(function(divisor){
                        acc.push(self._getGroupSubdivision(subGroup,divisor[0],divisor[1]));
                    });
                }
                returnacc;
            },
            []
        );
        returnthis._loadDataDropPrevious.add(Promise.all(proms)).then(function(groupSubdivisions){
            if(groupSubdivisions.length){
                self._prepareData(group,groupSubdivisions);
            }
        });
    },
    /**
     *SortrecursivelythesubTreesoftreeusingsortFunction.
     *Intheendeachnodeofthetreehasitsdirectchildrensorted
     *accordingtothecriterionreprensentedbysortFunction.
     *
     *@private
     *@param {Function}sortFunction
     *@param {Object}tree
     */
    _sortTree:function(sortFunction,tree){
        varself=this;
        tree.sortedKeys=_.sortBy([...tree.directSubTrees.keys()],sortFunction(tree));
        [...tree.directSubTrees.values()].forEach(function(subTree){
            self._sortTree(sortFunction,subTree);
        });
    },
});

returnPivotModel;

});
