flectra.define('web.PivotView',function(require){
    "usestrict";

    /**
     *ThePivotViewisaviewthatrepresentsdataina'pivotgrid'form.It
     *aggregatesdataon2dimensionsanddisplaystheresult,allowstheuserto
     *'zoomin'data.
     */

    constAbstractView=require('web.AbstractView');
    constconfig=require('web.config');
    constcore=require('web.core');
    constPivotModel=require('web.PivotModel');
    constPivotController=require('web.PivotController');
    constPivotRenderer=require('web.PivotRenderer');
    constRendererWrapper=require('web.RendererWrapper');

    const_t=core._t;
    const_lt=core._lt;

    constsearchUtils=require('web.searchUtils');
    constGROUPABLE_TYPES=searchUtils.GROUPABLE_TYPES;

    constPivotView=AbstractView.extend({
        display_name:_lt('Pivot'),
        icon:'fa-table',
        config:Object.assign({},AbstractView.prototype.config,{
            Model:PivotModel,
            Controller:PivotController,
            Renderer:PivotRenderer,
        }),
        viewType:'pivot',
        searchMenuTypes:['filter','groupBy','comparison','favorite'],

        /**
         *@override
         *@param{Object}params
         *@param{Array}params.additionalMeasures
         */
        init:function(viewInfo,params){
            this._super.apply(this,arguments);

            constactiveMeasures=[];//Storethedefinedactivemeasures
            constcolGroupBys=[];//Storethedefinedgroup_byusedoncols
            constrowGroupBys=[];//Storethedefinedgroup_byusedonrows
            constmeasures={};//Alltheavailablemeasures
            constgroupableFields={};//Thefieldswhichcanbeusedtogroupdata
            constwidgets={};//Wigdetsdefinedinthearch
            constadditionalMeasures=params.additionalMeasures||[];

            this.fields.__count={string:_t("Count"),type:"integer"};

            //ComputethemeasuresandthegroupableFields
            Object.keys(this.fields).forEach(name=>{
                constfield=this.fields[name];
                if(name!=='id'&&field.store===true){
                    if(['integer','float','monetary'].includes(field.type)||additionalMeasures.includes(name)){
                        measures[name]=field;
                    }
                    if(GROUPABLE_TYPES.includes(field.type)){
                        groupableFields[name]=field;
                    }
                }
            });
            measures.__count={string:_t("Count"),type:"integer"};


            this.arch.children.forEach(field=>{
                letname=field.attrs.name;
                //RemoveinvisiblefieldsfromthemeasuresifnotinadditionalMeasures
                if(field.attrs.invisible&&py.eval(field.attrs.invisible)){
                    if(nameingroupableFields){
                        deletegroupableFields[name];
                    }
                    if(!additionalMeasures.includes(name)){
                        deletemeasures[name];
                        return;
                    }
                }
                if(field.attrs.interval){
                    name+=':'+field.attrs.interval;
                }
                if(field.attrs.widget){
                    widgets[name]=field.attrs.widget;
                }
                //addactivemeasurestothemeasurelist. Thisisveryrarely
                //necessary,butitcanbeusefulifoneisworkingwitha
                //functionalfieldnonstored,butinamodelwithanoverrided
                //read_groupmethod. Inthiscase,thepivotviewcouldwork,and
                //themeasureshouldbeallowed. However,becarefulifyoudefine
                //ameasureinyourpivotview:nonstoredfunctionalfieldswill
                //probablynotwork(theiraggregatewillalwaysbe0).
                if(field.attrs.type==='measure'&&!(nameinmeasures)){
                    measures[name]=this.fields[name];
                }
                if(field.attrs.string&&nameinmeasures){
                    measures[name].string=field.attrs.string;
                }
                if(field.attrs.type==='measure'||'operator'infield.attrs){
                    activeMeasures.push(name);
                    measures[name]=this.fields[name];
                }
                if(field.attrs.type==='col'){
                    colGroupBys.push(name);
                }
                if(field.attrs.type==='row'){
                    rowGroupBys.push(name);
                }
            });
            if((!activeMeasures.length)||this.arch.attrs.display_quantity){
                activeMeasures.splice(0,0,'__count');
            }

            this.loadParams.measures=activeMeasures;
            this.loadParams.colGroupBys=config.device.isMobile?[]:colGroupBys;
            this.loadParams.rowGroupBys=rowGroupBys;
            this.loadParams.fields=this.fields;
            this.loadParams.default_order=params.default_order||this.arch.attrs.default_order;
            this.loadParams.groupableFields=groupableFields;

            constdisableLinking=!!(this.arch.attrs.disable_linking&&
                                        JSON.stringify(this.arch.attrs.disable_linking));

            this.rendererParams.widgets=widgets;
            this.rendererParams.disableLinking=disableLinking;

            this.controllerParams.disableLinking=disableLinking;
            this.controllerParams.title=params.title||this.arch.attrs.string||_t("Untitled");
            this.controllerParams.measures=measures;

            //retrieveformandlistviewidsfromtheactiontoopenthoseviews
            //whenadatacellofthepivotviewisclicked
            this.controllerParams.views=[
                _findView(params.actionViews,'list'),
                _findView(params.actionViews,'form'),
            ];

            function_findView(views,viewType){
                constview=views.find(view=>{
                    returnview.type===viewType;
                });
                return[view?view.viewID:false,viewType];
            }
        },

        /**
         *
         *@override
         */
        getRenderer(parent,state){
            state=Object.assign(state||{},this.rendererParams);
            returnnewRendererWrapper(parent,this.config.Renderer,state);
        },
    });

    returnPivotView;

});
