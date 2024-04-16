flectra.define('web.AbstractAction',function(require){
"usestrict";

/**
 *WedefineheretheAbstractActionwidget,whichimplementstheActionMixin.
 *Allclientactionsmustextendthiswidget.
 *
 *@moduleweb.AbstractAction
 */

varActionMixin=require('web.ActionMixin');
constActionModel=require('web/static/src/js/views/action_model.js');
varControlPanel=require('web.ControlPanel');
varWidget=require('web.Widget');
const{ComponentWrapper}=require('web.OwlCompatibility');

varAbstractAction=Widget.extend(ActionMixin,{
    config:{
        ControlPanel:ControlPanel,
    },

    /**
     *Ifthisflagissettotrue,theclientactionwillcreateacontrol
     *panelwheneveritiscreated.
     *
     *@typeboolean
     */
    hasControlPanel:false,

    /**
     *Iftrue,thisflagindicatesthattheclientactionshouldautomatically
     *fetchthe<arch>ofasearchview(orcontrolpanelview). Notethat
     *todothat,italsoneedsaspecificmodelName.
     *
     *Forexample,theDiscussapplicationaddsthefollowinglineinits
     *constructor::
     *
     *     this.searchModelConfig.modelName='mail.message';
     *
     *@typeboolean
     */
    loadControlPanel:false,

    /**
     *Aclientactionmightwanttouseasearchbarinitscontrolpanel,or
     *itcouldchoosenottouseit.
     *
     *NotethatitonlymakessenseifhasControlPanelissettotrue.
     *
     *@typeboolean
     */
    withSearchBar:false,

    /**
     *Thisparametercanbesettocustomizetheavailablesubmenusinthe
     *controlpanel(Filters/GroupBy/Favorites). Thisisbasicallyalistof
     *thesubmenusthatwewanttouse.
     *
     *NotethatitonlymakessenseifhasControlPanelissettotrue.
     *
     *Forexample,set['filter','favorite']toenabletheFiltersand
     *Favoritesmenus.
     *
     *@typestring[]
     */
    searchMenuTypes:[],

    /**
     *@override
     *
     *@param{Widget}parent
     *@param{Object}action
     *@param{Object}[options]
     */
    init:function(parent,action,options){
        this._super(parent);
        this._title=action.display_name||action.name;

        this.searchModelConfig={
            context:Object.assign({},action.context),
            domain:action.domain||[],
            env:owl.Component.env,
            searchMenuTypes:this.searchMenuTypes,
        };
        this.extensions={};
        if(this.hasControlPanel){
            this.extensions.ControlPanel={
                actionId:action.id,
                withSearchBar:this.withSearchBar,
            };

            this.viewId=action.search_view_id&&action.search_view_id[0];

            this.controlPanelProps={
                action,
                breadcrumbs:options&&options.breadcrumbs,
                withSearchBar:this.withSearchBar,
                searchMenuTypes:this.searchMenuTypes,
            };
        }
    },
    /**
     *ThewillStartmethodisactuallyquitecomplicatediftheclientaction
     *hasacontrolPanel,becauseitneedstoprepareit.
     *
     *@override
     */
    willStart:asyncfunction(){
        constsuperPromise=this._super(...arguments);
        if(this.hasControlPanel){
            if(this.loadControlPanel){
                const{context,modelName}=this.searchModelConfig;
                constoptions={load_filters:this.searchMenuTypes.includes('favorite')};
                const{arch,fields,favoriteFilters}=awaitthis.loadFieldView(
                    modelName,
                    context||{},
                    this.viewId,
                    'search',
                    options
                );
                constarchs={search:arch};
                const{ControlPanel:controlPanelInfo}=ActionModel.extractArchInfo(archs);
                Object.assign(this.extensions.ControlPanel,{
                    archNodes:controlPanelInfo.children,
                    favoriteFilters,
                    fields,
                });
                this.controlPanelProps.fields=fields;
            }
        }
        this.searchModel=newActionModel(this.extensions,this.searchModelConfig);
        if(this.hasControlPanel){
            this.controlPanelProps.searchModel=this.searchModel;
        }
        returnPromise.all([
            superPromise,
            this.searchModel.load(),
        ]);
    },
    /**
     *@override
     */
    start:asyncfunction(){
        awaitthis._super(...arguments);
        if(this.hasControlPanel){
            if('title'inthis.controlPanelProps){
                this._setTitle(this.controlPanelProps.title);
            }
            this.controlPanelProps.title=this.getTitle();
            this._controlPanelWrapper=newComponentWrapper(this,this.config.ControlPanel,this.controlPanelProps);
            awaitthis._controlPanelWrapper.mount(this.el,{position:'first-child'});

        }
    },
    /**
     *@override
     */
    destroy:function(){
        this._super.apply(this,arguments);
        ActionMixin.destroy.call(this);
    },
    /**
     *@override
     */
    on_attach_callback:function(){
        ActionMixin.on_attach_callback.call(this);
        this.searchModel.on('search',this,this._onSearch);
        if(this.hasControlPanel){
            this.searchModel.on('get-controller-query-params',this,this._onGetOwnedQueryParams);
        }
    },
    /**
     *@override
     */
    on_detach_callback:function(){
        ActionMixin.on_detach_callback.call(this);
        this.searchModel.off('search',this);
        if(this.hasControlPanel){
            this.searchModel.off('get-controller-query-params',this);
        }
    },

    /**
     *@private
     *@param{Object}[searchQuery]
     */
    _onSearch:function(){},
});

returnAbstractAction;

});
