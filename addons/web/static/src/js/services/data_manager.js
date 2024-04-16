flectra.define('web.DataManager',function(require){
"usestrict";

varconfig=require('web.config');
varcore=require('web.core');
varrpc=require('web.rpc');
varsession=require('web.session');
varutils=require('web.utils');

returncore.Class.extend({
    init:function(){
        this._init_cache();
        core.bus.on('clear_cache',this,this.invalidate.bind(this));
    },

    _init_cache:function(){
        this._cache={
            actions:{},
            filters:{},
            views:{},
        };
    },

    /**
     *Invalidatesthewholecache
     *Suggestion:couldberefinedtoinvalidatesomepartofthecache
     */
    invalidate:function(){
        session.invalidateCacheKey('load_menus');
        this._init_cache();
    },

    /**
     *Loadsanactionfromitsidorxmlid.
     *
     *@param{int|string}[action_id]theactionidorxmlid
     *@param{Object}[additional_context]usedtoloadtheaction
     *@return{Promise}resolvedwiththeactionwhoseidorxmlidisaction_id
     */
    load_action:function(action_id,additional_context){
        varself=this;
        varkey=this._gen_key(action_id,additional_context||{});

        if(config.isDebug('assets')||!this._cache.actions[key]){
            this._cache.actions[key]=rpc.query({
                route:"/web/action/load",
                params:{
                    action_id:action_id,
                    additional_context:additional_context,
                },
            }).then(function(action){
                self._cache.actions[key]=action.no_cache?null:self._cache.actions[key];
                returnaction;
            }).guardedCatch(()=>this._invalidate('actions',key));
        }

        returnthis._cache.actions[key].then(function(action){
            return$.extend(true,{},action);
        });
    },

    /**
     *Loadsvariousinformationconcerningviews:fields_viewforeachview,
     *thefieldsofthecorrespondingmodel,andoptionallythefilters.
     *
     *@param{Object}params
     *@param{String}params.model
     *@param{Object}params.context
     *@param{Array}params.views_descrarrayof[view_id,view_type]
     *@param{Object}[options={}]dictionaryofvariousoptions:
     *    -options.load_filters:whetherornottoloadthefilters,
     *    -options.action_id:theaction_id(requiredtoloadfilters),
     *    -options.toolbar:whetherornotatoolbarwillbedisplayed,
     *@return{Promise}resolvedwiththerequestedviewsinformation
     */
    load_views:asyncfunction({model,context,views_descr},options={}){
        constviewsKey=this._gen_key(model,views_descr,options,context);
        constfiltersKey=this._gen_key(model,options.action_id);
        constwithFilters=Boolean(options.load_filters);
        constshouldLoadViews=config.isDebug('assets')||!this._cache.views[viewsKey];
        constshouldLoadFilters=config.isDebug('assets')||(
            withFilters&&!this._cache.filters[filtersKey]
        );
        if(shouldLoadViews){
            //Viewsinfoshouldbeloaded
            options.load_filters=shouldLoadFilters;
            this._cache.views[viewsKey]=rpc.query({
                args:[],
                kwargs:{context,options,views:views_descr},
                model,
                method:'load_views',
            }).then(result=>{
                //Freezethefieldsdictasitwillbesharedbetweenviewsand
                //nooneshouldeditit
                utils.deepFreeze(result.fields);
                for(const[viewId,viewType]ofviews_descr){
                    constfvg=result.fields_views[viewType];
                    fvg.viewFields=fvg.fields;
                    fvg.fields=result.fields;
                }

                //Insertfilters,ifany,intothefilterscache
                if(shouldLoadFilters){
                    this._cache.filters[filtersKey]=Promise.resolve(result.filters);
                }
                returnresult.fields_views;
            }).guardedCatch(()=>this._invalidate('views',viewsKey));
        }
        constresult=awaitthis._cache.views[viewsKey];
        if(withFilters&&result.search){
            if(shouldLoadFilters){
                awaitthis.load_filters({
                    actionId:options.action_id,
                    context,
                    forceReload:false,
                    modelName:model,
                });
            }
            result.search.favoriteFilters=awaitthis._cache.filters[filtersKey];
        }
        returnresult;
    },

    /**
     *Loadsthefiltersofagivenmodelandoptionalactionid.
     *
     *@param{Object}params
     *@param{number}params.actionId
     *@param{Object}params.context
     *@param{boolean}[params.forceReload=true]canbesettofalsetopreventforceReload
     *@param{string}params.modelName
     *@return{Promise}resolvedwiththerequestedfilters
     */
    load_filters:function(params){
        constkey=this._gen_key(params.modelName,params.actionId);
        constforceReload=params.forceReload!==false&&config.isDebug('assets');
        if(forceReload||!this._cache.filters[key]){
            this._cache.filters[key]=rpc.query({
                args:[params.modelName,params.actionId],
                kwargs:{
                    context:params.context||{},
                    //get_context()dedataset
                },
                model:'ir.filters',
                method:'get_filters',
            }).guardedCatch(()=>this._invalidate('filters',key));
        }
        returnthis._cache.filters[key];
    },

    /**
     *Calls'create_or_replace'on'ir_filters'.
     *
     *@param{Object}[filter]thefilterdescription
     *@return{Promise}resolvedwiththeidofthecreatedorreplacedfilter
     */
    create_filter:function(filter){
        returnrpc.query({
                args:[filter],
                model:'ir.filters',
                method:'create_or_replace',
            })
            .then(filterId=>{
                constfiltersKey=this._gen_key(filter.model_id,filter.action_id);
                this._invalidate('filters',filtersKey);
                returnfilterId;
            });
    },

    /**
     *Calls'unlink'on'ir_filters'.
     *
     *@param{integer}filterIdIdofthefiltertoremove
     *@return{Promise}
     */
    delete_filter:function(filterId){
        returnrpc.query({
                args:[filterId],
                model:'ir.filters',
                method:'unlink',
            })
            //Invalidatethewholecachesincewehavenoideawherethefiltercamefrom.
            .then(()=>this._invalidate('filters'));
    },

    /**
     *Privatefunctionthatgeneratesacachekeyfromitsarguments
     */
    _gen_key:function(){
        return_.map(Array.prototype.slice.call(arguments),function(arg){
            if(!arg){
                returnfalse;
            }
            return_.isObject(arg)?JSON.stringify(arg):arg;
        }).join(',');
    },

    /**
     *Invalidateacacheentryorawholecachesection.
     *
     *@private
     *@param{string}section
     *@param{string}key
     */
    _invalidate(section,key){
        if(key){
            deletethis._cache[section][key];
        }else{
            this._cache[section]={};
        }
    },
});

});

flectra.define('web.data_manager',function(require){
"usestrict";

varDataManager=require('web.DataManager');

vardata_manager=newDataManager();

returndata_manager;

});
