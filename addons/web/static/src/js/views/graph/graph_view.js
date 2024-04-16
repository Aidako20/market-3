flectra.define('web.GraphView',function(require){
"usestrict";

/**
 *TheGraphViewisresponsibletodisplayagraphical(meaning:chart)
 *representationofthecurrentdataset. Asofnow,itiscurrentlyableto
 *displaydatainthreetypesofchart:barchart,linechartandpiechart.
 */

varAbstractView=require('web.AbstractView');
varcore=require('web.core');
varGraphModel=require('web.GraphModel');
varController=require('web.GraphController');
varGraphRenderer=require('web.GraphRenderer');

var_t=core._t;
var_lt=core._lt;

varsearchUtils=require('web.searchUtils');
varGROUPABLE_TYPES=searchUtils.GROUPABLE_TYPES;

varGraphView=AbstractView.extend({
    display_name:_lt('Graph'),
    icon:'fa-bar-chart',
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],
    config:_.extend({},AbstractView.prototype.config,{
        Model:GraphModel,
        Controller:Controller,
        Renderer:GraphRenderer,
    }),
    viewType:'graph',
    searchMenuTypes:['filter','groupBy','comparison','favorite'],

    /**
     *@override
     */
    init:function(viewInfo,params){
        this._super.apply(this,arguments);

        constadditionalMeasures=params.additionalMeasures||[];
        letmeasure;
        constmeasures={};
        constmeasureStrings={};
        letgroupBys=[];
        constgroupableFields={};
        this.fields.__count__={string:_t("Count"),type:'integer'};

        this.arch.children.forEach(field=>{
            letfieldName=field.attrs.name;
            if(fieldName==="id"){
                return;
            }
            constinterval=field.attrs.interval;
            if(interval){
                fieldName=fieldName+':'+interval;
            }
            if(field.attrs.type==='measure'){
                const{string}=this.fields[fieldName];
                measure=fieldName;
                measures[fieldName]={
                    description:string,
                    fieldName,
                    groupNumber:0,
                    isActive:false,
                    itemType:'measure',
                };
            }else{
                groupBys.push(fieldName);
            }
            if(field.attrs.string){
                measureStrings[fieldName]=field.attrs.string;
            }
        });

        for(constnameinthis.fields){
            constfield=this.fields[name];
            if(name!=='id'&&field.store===true){
                if(
                    ['integer','float','monetary'].includes(field.type)||
                    additionalMeasures.includes(name)
                ){
                    measures[name]={
                        description:field.string,
                        fieldName:name,
                        groupNumber:0,
                        isActive:false,
                        itemType:'measure',
                    };
                }
                if(GROUPABLE_TYPES.includes(field.type)){
                    groupableFields[name]=field;
                }
            }
        }
        for(constnameinmeasureStrings){
            if(measures[name]){
                measures[name].description=measureStrings[name];
            }
        }

        //Removeinvisiblefieldsfromthemeasures
        this.arch.children.forEach(field=>{
            letfieldName=field.attrs.name;
            if(field.attrs.invisible&&py.eval(field.attrs.invisible)){
                groupBys=groupBys.filter(groupBy=>groupBy!==fieldName);
                if(fieldNameingroupableFields){
                    deletegroupableFields[fieldName];
                }
                if(!additionalMeasures.includes(fieldName)){
                    deletemeasures[fieldName];
                }
            }
        });

        constsortedMeasures=Object.values(measures).sort((a,b)=>{
                constdescA=a.description.toLowerCase();
                constdescB=b.description.toLowerCase();
                returndescA>descB?1:descA<descB?-1:0;
            });
        constcountMeasure={
            description:_t("Count"),
            fieldName:'__count__',
            groupNumber:1,
            isActive:false,
            itemType:'measure',
        };
        this.controllerParams.withButtons=params.withButtons!==false;
        this.controllerParams.measures=[...sortedMeasures,countMeasure];
        this.controllerParams.groupableFields=groupableFields;
        this.controllerParams.title=params.title||this.arch.attrs.string||_t("Untitled");
        //retrieveformandlistviewidsfromtheactiontoopenthoseviews
        //whenthegraphisclicked
        function_findView(views,viewType){
            constview=views.find(view=>{
                returnview.type===viewType;
            });
            return[view?view.viewID:false,viewType];
        }
        this.controllerParams.views=[
            _findView(params.actionViews,'list'),
            _findView(params.actionViews,'form'),
        ];

        this.rendererParams.fields=this.fields;
        this.rendererParams.title=this.arch.attrs.title;//TODO:useattrs.stringinstead
        this.rendererParams.disableLinking=!!JSON.parse(this.arch.attrs.disable_linking||'0');

        this.loadParams.mode=this.arch.attrs.type||'bar';
        this.loadParams.orderBy=this.arch.attrs.order;
        this.loadParams.measure=measure||'__count__';
        this.loadParams.groupBys=groupBys;
        this.loadParams.fields=this.fields;
        this.loadParams.comparisonDomain=params.comparisonDomain;
        this.loadParams.stacked=this.arch.attrs.stacked!=="False";
    },
});

returnGraphView;

});
