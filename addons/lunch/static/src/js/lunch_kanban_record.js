flectra.define('lunch.LunchKanbanRecord',function(require){
    "usestrict";

    /**
     *ThisfiledefinestheKanbanRecordfortheLunchKanbanview.
     */

    varKanbanRecord=require('web.KanbanRecord');

    varLunchKanbanRecord=KanbanRecord.extend({
        events:_.extend({},KanbanRecord.prototype.events,{
            'click':'_onSelectRecord',
        }),

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *Opentheaddproductwizard
         *
         *@private
         *@param{MouseEvent}evClickevent
         */
        _onSelectRecord:function(ev){
            ev.preventDefault();
            //ignoreclicksonoe_kanban_actionelements
            if(!$(ev.target).hasClass('oe_kanban_action')){
                this.trigger_up('open_wizard',{productId:this.recordData.product_id?this.recordData.product_id.res_id:this.recordData.id});
            }
        },
    });

    returnLunchKanbanRecord;

    });
