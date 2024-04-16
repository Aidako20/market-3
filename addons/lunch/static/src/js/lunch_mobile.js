flectra.define('lunch.LunchMobile',function(require){
"usestrict";

varconfig=require('web.config');
varLunchWidget=require('lunch.LunchWidget');
varLunchKanbanController=require('lunch.LunchKanbanController');
varLunchListController=require('lunch.LunchListController');

if(!config.device.isMobile){
    return;
}

LunchWidget.include({
    template:"LunchWidgetMobile",

    /**
     *Overridetosetthetogglestateallowinginitiallyopenit.
     *
     *@override
     */
    init:function(parent,params){
        this._super.apply(this,arguments);
        this.keepOpen=params.keepOpen||undefined;
    },
});

varmobileFunctions={
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.openWidget=false;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Overridetoaddthewidget'stogglestatetoitsdata.
     *
     *@override
     *@private
     */
    _renderLunchWidget:function(){
        this.widgetData.keepOpen=this.openWidget;
        this.openWidget=false;
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _onAddProduct:function(){
        this.openWidget=true;
        this._super.apply(this,arguments);
    },

    /**
     *@override
     *@private
     */
    _onRemoveProduct:function(){
        this.openWidget=true;
        this._super.apply(this,arguments);
    },
};

LunchKanbanController.include(mobileFunctions);
LunchListController.include(mobileFunctions);

});
