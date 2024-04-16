flectra.define('web.ListView',function(require){
"usestrict";

/**
 *Thelistviewisoneofthecoreandmostbasicview:itisusedtolookat
 *alistofrecordsinatable.
 *
 *Notethatalistviewisnotinstantiatedtodisplayaone2manyfieldina
 *formview.OnlyaListRendererisusedinthatcase.
 */

varBasicView=require('web.BasicView');
varcore=require('web.core');
varListModel=require('web.ListModel');
varListRenderer=require('web.ListRenderer');
varListController=require('web.ListController');
varpyUtils=require('web.py_utils');

var_lt=core._lt;

varListView=BasicView.extend({
    accesskey:"l",
    display_name:_lt('List'),
    icon:'fa-list-ul',
    config:_.extend({},BasicView.prototype.config,{
        Model:ListModel,
        Renderer:ListRenderer,
        Controller:ListController,
    }),
    viewType:'list',
    /**
     *@override
     *
     *@param{Object}viewInfo
     *@param{Object}params
     *@param{boolean}params.hasActionMenus
     *@param{boolean}[params.hasSelectors=true]
     */
    init:function(viewInfo,params){
        varself=this;
        this._super.apply(this,arguments);
        varselectedRecords=[];//thereisnoselectedrecordsbydefault

        varpyevalContext=py.dict.fromJSON(_.pick(params.context,function(value,key,object){return!_.isUndefined(value)})||{});
        varexpandGroups=!!JSON.parse(pyUtils.py_eval(this.arch.attrs.expand||"0",{'context':pyevalContext}));

        this.groupbys={};
        this.headerButtons=[];
        this.arch.children.forEach(function(child){
            if(child.tag==='groupby'){
                self._extractGroup(child);
            }
            if(child.tag==='header'){
                self._extractHeaderButtons(child);
            }
        });

        leteditable=false;
        if((!this.arch.attrs.edit||!!JSON.parse(this.arch.attrs.edit))&&!params.readonly){
            editable=this.arch.attrs.editable;
        }

        this.controllerParams.activeActions.export_xlsx=this.arch.attrs.export_xlsx?!!JSON.parse(this.arch.attrs.export_xlsx):true;
        this.controllerParams.editable=editable;
        this.controllerParams.hasActionMenus=params.hasActionMenus;
        this.controllerParams.headerButtons=this.headerButtons;
        this.controllerParams.toolbarActions=viewInfo.toolbar;
        this.controllerParams.mode='readonly';
        this.controllerParams.selectedRecords=selectedRecords;

        this.rendererParams.arch=this.arch;
        this.rendererParams.groupbys=this.groupbys;
        this.rendererParams.hasSelectors=
                'hasSelectors'inparams?params.hasSelectors:true;
        this.rendererParams.editable=editable;
        this.rendererParams.selectedRecords=selectedRecords;
        this.rendererParams.addCreateLine=false;
        this.rendererParams.addCreateLineInGroups=editable&&this.controllerParams.activeActions.create;
        this.rendererParams.isMultiEditable=this.arch.attrs.multi_edit&&!!JSON.parse(this.arch.attrs.multi_edit);

        this.modelParams.groupbys=this.groupbys;

        this.loadParams.limit=this.loadParams.limit||80;
        this.loadParams.openGroupByDefault=expandGroups;
        this.loadParams.type='list';
        vargroupsLimit=parseInt(this.arch.attrs.groups_limit,10);
        this.loadParams.groupsLimit=groupsLimit||(expandGroups?10:80);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}node
     */
    _extractGroup:function(node){
        varinnerView=this.fields[node.attrs.name].views.groupby;
        this.groupbys[node.attrs.name]=this._processFieldsView(innerView,'groupby');
    },
    /**
     *Extractsactionbuttonsdefinitionsfromthe<header>nodeofthelist
     *viewdefinition
     *
     *@private
     *@param{Object}node
     */
    _extractHeaderButtons(node){
        node.children.forEach(child=>{
            if(child.tag==='button'&&!child.attrs.modifiers.invisible){
                this.headerButtons.push(child);
            }
        });
    },
    /**
     *@override
     */
    _extractParamsFromAction:function(action){
        varparams=this._super.apply(this,arguments);
        varinDialog=action.target==='new';
        varinline=action.target==='inline';
        params.hasActionMenus=!inDialog&&!inline;
        returnparams;
    },
    /**
     *@override
     */
    _updateMVCParams:function(){
        this._super.apply(this,arguments);
        this.controllerParams.noLeaf=!!this.loadParams.context.group_by_no_leaf;
    },
});

returnListView;

});
