flectra.define('website.theme_preview_kanban',function(require){
"usestrict";

varKanbanController=require('web.KanbanController');
varKanbanView=require('web.KanbanView');
varViewRegistry=require('web.view_registry');
constThemePreviewControllerCommon=require('website.theme_preview_form').ThemePreviewControllerCommon;
varcore=require('web.core');
var_lt=core._lt;

varThemePreviewKanbanController=KanbanController.extend(ThemePreviewControllerCommon,{
    /**
     *@override
     */
    start:asyncfunction(){
        awaitthis._super(...arguments);

        //hidepager
        this.el.classList.add('o_view_kanban_theme_preview_controller');

        //updatebreacrumb
        constwebsiteLink=Object.assign(document.createElement('a'),{
            className:'btnbtn-secondaryml-3text-black-75',
            href:'/',
            innerHTML:'<iclass="fafa-close"></i>',
        });
        constsmallBreadcumb=Object.assign(document.createElement('small'),{
            className:'mx-2text-muted',
            innerHTML:_lt("Don'tworry,youcanswitchlater."),
        });
        this._controlPanelWrapper.el.querySelector('.o_cp_top.breadcrumbli.active').classList.add('text-black-75');
        this._controlPanelWrapper.el.querySelector('.o_cp_top').appendChild(websiteLink);
        this._controlPanelWrapper.el.querySelector('.o_cp_topli').appendChild(smallBreadcumb);
    },
    /**
     *Calledwhenuserclickonanybuttoninkanbanview.
     *Targetedbuttonsareselectedusingnameattributevalue.
     *
     *@override
     */
    _onButtonClicked:function(ev){
        constattrName=ev.data.attrs.name;
        if(attrName==='button_choose_theme'||attrName==='button_refresh_theme'){
            this._handleThemeAction(ev.data.record.res_id,attrName);
        }else{
            this._super(...arguments);
        }
    },
});

varThemePreviewKanbanView=KanbanView.extend({
    withSearchBar:false, //hidesearchBar

    config:_.extend({},KanbanView.prototype.config,{
        Controller:ThemePreviewKanbanController,
    }),
});

ViewRegistry.add('theme_preview_kanban',ThemePreviewKanbanView);

});
