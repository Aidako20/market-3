flectra.define('mail.ActivityView',function(require){
"usestrict";

constActivityController=require('mail.ActivityController');
constActivityModel=require('mail.ActivityModel');
constActivityRenderer=require('mail.ActivityRenderer');
constBasicView=require('web.BasicView');
constcore=require('web.core');
constRendererWrapper=require('web.RendererWrapper');
constview_registry=require('web.view_registry');

const_lt=core._lt;

constActivityView=BasicView.extend({
    accesskey:"a",
    display_name:_lt('Activity'),
    icon:'fa-clock-o',
    config:_.extend({},BasicView.prototype.config,{
        Controller:ActivityController,
        Model:ActivityModel,
        Renderer:ActivityRenderer,
    }),
    viewType:'activity',
    searchMenuTypes:['filter','favorite'],

    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);

        this.loadParams.type='list';
        //limitmakesnosenseinthisviewaswedisplayallrecordshavingactivities
        this.loadParams.limit=false;

        this.rendererParams.templates=_.findWhere(this.arch.children,{'tag':'templates'});
        this.controllerParams.title=this.arch.attrs.string;
    },
    /**
     *
     *@override
     */
    getRenderer(parent,state){
        state=Object.assign({},state,this.rendererParams);
        returnnewRendererWrapper(null,this.config.Renderer,state);
    },
});

view_registry.add('activity',ActivityView);

returnActivityView;

});
