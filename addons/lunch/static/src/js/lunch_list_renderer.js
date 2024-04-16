flectra.define('lunch.LunchListRenderer',function(require){
"usestrict";

/**
 *ThisfiledefinestheRendererfortheLunchListview,whichisan
 *overrideoftheListRenderer.
 */

varListRenderer=require('web.ListRenderer');

varLunchListRenderer=ListRenderer.extend({
    events:_.extend({},ListRenderer.prototype.events,{
        'click.o_data_row':'_onClickListRow',
    }),

    /**
     *@override
     */
    start:function(){
        this.$el.addClass('o_lunch_viewo_lunch_list_view');
        returnthis._super.apply(this,arguments);
    },
    /**
     *Overridetoaddidofproduct_idindataset.
     *
     *@override
     */
    _renderRow:function(record){
        vartr=this._super.apply(this,arguments);
        tr.attr('data-product-id',record.data.id);
        returntr;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Opentheaddproductwizard
     *
     *@private
     *@param{MouseEvent}evClickevent
     */
    _onClickListRow:function(ev){
        ev.preventDefault();
        varproductId=ev.currentTarget.dataset&&ev.currentTarget.dataset.productId?parseInt(ev.currentTarget.dataset.productId):null;

        if(productId){
            this.trigger_up('open_wizard',{productId:productId});
        }
    },
});

returnLunchListRenderer;

});
