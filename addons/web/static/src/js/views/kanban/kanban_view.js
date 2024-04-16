flectra.define('web.KanbanView',function(require){
"usestrict";

varBasicView=require('web.BasicView');
varcore=require('web.core');
varKanbanController=require('web.KanbanController');
varkanbanExamplesRegistry=require('web.kanban_examples_registry');
varKanbanModel=require('web.KanbanModel');
varKanbanRenderer=require('web.KanbanRenderer');
varutils=require('web.utils');

var_lt=core._lt;

varKanbanView=BasicView.extend({
    accesskey:"k",
    display_name:_lt("Kanban"),
    icon:'fa-th-large',
    mobile_friendly:true,
    config:_.extend({},BasicView.prototype.config,{
        Model:KanbanModel,
        Controller:KanbanController,
        Renderer:KanbanRenderer,
    }),
    jsLibs:[],
    viewType:'kanban',

    /**
     *@constructor
     */
    init:function(viewInfo,params){
        this._super.apply(this,arguments);

        this.loadParams.limit=this.loadParams.limit||40;
        this.loadParams.openGroupByDefault=true;
        this.loadParams.type='list';
        this.noDefaultGroupby=params.noDefaultGroupby;
        varprogressBar;
        utils.traverse(this.arch,function(n){
            varisProgressBar=(n.tag==='progressbar');
            if(isProgressBar){
                progressBar=_.clone(n.attrs);
                progressBar.colors=JSON.parse(progressBar.colors);
                progressBar.sum_field=progressBar.sum_field||false;
            }
            return!isProgressBar;
        });
        if(progressBar){
            this.loadParams.progressBar=progressBar;
        }

        varactiveActions=this.controllerParams.activeActions;
        vararchAttrs=this.arch.attrs;
        activeActions=_.extend(activeActions,{
            group_create:this.arch.attrs.group_create?!!JSON.parse(archAttrs.group_create):true,
            group_edit:archAttrs.group_edit?!!JSON.parse(archAttrs.group_edit):true,
            group_delete:archAttrs.group_delete?!!JSON.parse(archAttrs.group_delete):true,
        });

        this.rendererParams.column_options={
            editable:activeActions.group_edit,
            deletable:activeActions.group_delete,
            archivable:archAttrs.archivable?!!JSON.parse(archAttrs.archivable):true,
            group_creatable:activeActions.group_create,
            quickCreateView:archAttrs.quick_create_view||null,
            recordsDraggable:archAttrs.records_draggable?!!JSON.parse(archAttrs.records_draggable):true,
            hasProgressBar:!!progressBar,
        };
        this.rendererParams.record_options={
            editable:activeActions.edit,
            deletable:activeActions.delete,
            read_only_mode:params.readOnlyMode,
            selectionMode:params.selectionMode,
        };
        this.rendererParams.quickCreateEnabled=this._isQuickCreateEnabled();
        this.rendererParams.readOnlyMode=params.readOnlyMode;
        varexamples=archAttrs.examples;
        if(examples){
            this.rendererParams.examples=kanbanExamplesRegistry.get(examples);
        }

        this.controllerParams.on_create=archAttrs.on_create;
        this.controllerParams.hasButtons=!params.selectionMode?true:false;
        this.controllerParams.quickCreateEnabled=this.rendererParams.quickCreateEnabled;
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{Object}viewInfo
     *@returns{boolean}trueiffthequickcreatefeatureisnotexplicitely
     *  disabled(withcreate="False"orquick_create="False"inthearch)
     */
    _isQuickCreateEnabled:function(){
        if(!this.controllerParams.activeActions.create){
            returnfalse;
        }
        if(this.arch.attrs.quick_create!==undefined){
            return!!JSON.parse(this.arch.attrs.quick_create);
        }
        returntrue;
    },
    /**
     *@override
     *@private
     */
    _updateMVCParams:function(){
        this._super.apply(this,arguments);
        if(this.searchMenuTypes.includes('groupBy')&&!this.noDefaultGroupby&&this.arch.attrs.default_group_by){
            this.loadParams.groupBy=[this.arch.attrs.default_group_by];
        }
    },
});

returnKanbanView;

});
