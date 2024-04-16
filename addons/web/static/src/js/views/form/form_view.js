flectra.define('web.FormView',function(require){
"usestrict";

varBasicView=require('web.BasicView');
varContext=require('web.Context');
varcore=require('web.core');
varFormController=require('web.FormController');
varFormRenderer=require('web.FormRenderer');
const{generateID}=require('web.utils');

var_lt=core._lt;

varFormView=BasicView.extend({
    config:_.extend({},BasicView.prototype.config,{
        Renderer:FormRenderer,
        Controller:FormController,
    }),
    display_name:_lt('Form'),
    icon:'fa-edit',
    multi_record:false,
    withSearchBar:false,
    searchMenuTypes:[],
    viewType:'form',
    /**
     *@override
     */
    init:function(viewInfo,params){
        varhasActionMenus=params.hasActionMenus;
        this._super.apply(this,arguments);

        varmode=params.mode||(params.currentId?'readonly':'edit');
        this.loadParams.type='record';

        //thisiskindofstrange,buttheparamobjectismodifiedby
        //AbstractView,soweonlyneedtouseitshasActionMenusvalueifitwas
        //notalreadypresentinthebeginningofthismethod
        if(hasActionMenus===undefined){
            hasActionMenus=params.hasActionMenus;
        }
        this.controllerParams.hasActionMenus=hasActionMenus;
        this.controllerParams.disableAutofocus=params.disable_autofocus||this.arch.attrs.disable_autofocus;
        this.controllerParams.toolbarActions=viewInfo.toolbar;
        this.controllerParams.footerToButtons=params.footerToButtons;

        vardefaultButtons='default_buttons'inparams?params.default_buttons:true;
        this.controllerParams.defaultButtons=defaultButtons;
        this.controllerParams.mode=mode;

        this.rendererParams.mode=mode;
        this.rendererParams.isFromFormViewDialog=params.isFromFormViewDialog;
        this.rendererParams.fieldIdsToNames=this.fieldsView.fieldIdsToNames;
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    getController:function(parent){
        returnthis._loadSubviews(parent).then(this._super.bind(this,parent));
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _extractParamsFromAction:function(action){
        varparams=this._super.apply(this,arguments);
        varinDialog=action.target==='new';
        varinline=action.target==='inline';
        varfullscreen=action.target==='fullscreen';
        params.withControlPanel=!(inDialog||inline);
        params.footerToButtons=inDialog;
        params.hasSearchView=inDialog?false:params.hasSearchView;
        params.hasActionMenus=!inDialog&&!inline;
        params.searchMenuTypes=inDialog?[]:params.searchMenuTypes;
        if(inDialog||inline||fullscreen){
            params.mode='edit';
        }elseif(action.context&&action.context.form_view_initial_mode){
            params.mode=action.context.form_view_initial_mode;
        }
        returnparams;
    },
    /**
     *Loadsthesubviewsforx2manyfieldswhentheyarenotinline
     *
     *@private
     *@param{Widget}parenttheparentofthemodel,ifithastobecreated
     *@returns{Promise}
     */
    _loadSubviews:function(parent){
        varself=this;
        vardefs=[];
        if(this.loadParams&&this.loadParams.fieldsInfo){
            varfields=this.loadParams.fields;

            _.each(this.loadParams.fieldsInfo.form,function(attrs,fieldName){
                varfield=fields[fieldName];
                if(!field){
                    //whenaone2manyrecordisopenedinaformview,thefields
                    //ofthemainone2manyview(listorkanban)areaddedtothe
                    //fieldsInfoofitsformview,butthosefieldsaren'tinthe
                    //loadParams.fields,astheyarenotdisplayedintheview,so
                    //wecanignorethem.
                    return;
                }
                if(field.type!=='one2many'&&field.type!=='many2many'){
                    return;
                }

                if(attrs.Widget.prototype.useSubview&&!attrs.__no_fetch&&!attrs.views[attrs.mode]){
                    varcontext={};
                    varregex=/'([a-z]*_view_ref)'*:*'(.*?)'/g;
                    varmatches;
                    while(matches=regex.exec(attrs.context)){
                        context[matches[1]]=matches[2];
                    }

                    //Remove*_view_refcomingfromparentview
                    varrefinedContext=_.pick(self.loadParams.context,function(value,key){
                        returnkey.indexOf('_view_ref')===-1;
                    });
                    //Specifythemainmodeltopreventaccessrightsdefinedinthecontext
                    //(e.g.create:0)toapplytosubviews.Weuseherethesamelogicas
                    //theoneappliedbytheserverforinlineviews.
                    refinedContext.base_model_name=self.controllerParams.modelName;
                    defs.push(parent.loadViews(
                            field.relation,
                            newContext(context,self.userContext,refinedContext).eval(),
                            [[null,attrs.mode==='tree'?'list':attrs.mode]])
                        .then(function(views){
                            for(varviewNameinviews){
                                //clonetomakerunbotgreen?
                                attrs.views[viewName]=self._processFieldsView(views[viewName],viewName);
                                attrs.views[viewName].fields=attrs.views[viewName].viewFields;
                                self._processSubViewAttrs(attrs.views[viewName],attrs);
                            }
                            self._setSubViewLimit(attrs);
                        }));
                }else{
                    self._setSubViewLimit(attrs);
                }
            });
        }
        returnPromise.all(defs);
    },
    /**
     *@override
     */
    _processArch(arch,fv){
        fv.fieldIdsToNames={};//mapsfieldids(identifying<field>nodes)tofieldnames
        returnthis._super(...arguments);
    },
    /**
     *Overridetopopulatethe'fieldIdsToNames'dictmapping<field>nodeids
     *tofieldnames.Thoseidsarecomputedasfollows:
     *  -ifsetonthenode,weusethe'id'attribute
     *  -otherwise
     *      -ifthisisthefirstoccurrenceofthefieldinthearch,weuse
     *        itsnameasid('name'attribute)
     *      -otherwisewegenerateanidbyconcatenatingthefieldnamewith
     *        auniqueid
     *      -inbothcases,wesettheidwegeneratedintheattrs,asit
     *        willbeusedbytherenderer.
     *
     *@override
     */
    _processNode(node,fv){
        if(node.tag==='field'){
            constname=node.attrs.name;
            letuid=node.attrs.id;
            if(!uid){
                uid=nameinfv.fieldIdsToNames?`${name}__${generateID()}__`:name;
                node.attrs.id=uid;
            }
            fv.fieldIdsToNames[uid]=name;
        }
        returnthis._super(...arguments);
    },
    /**
     *Wesetherethelimitforthenumberofrecordsfetched(inonepage).
     *Thismethodisonlycalledforsubviews,notformainviews.
     *
     *@private
     *@param{Object}attrs
     */
    _setSubViewLimit:function(attrs){
        varview=attrs.views&&attrs.views[attrs.mode];
        varlimit=view&&view.arch.attrs.limit&&parseInt(view.arch.attrs.limit,10);
        attrs.limit=limit||attrs.Widget.prototype.limit||40;
    },
});

returnFormView;

});
