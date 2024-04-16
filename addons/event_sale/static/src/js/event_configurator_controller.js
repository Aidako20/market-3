flectra.define('event.EventConfiguratorFormController',function(require){
"usestrict";

varFormController=require('web.FormController');

/**
 *Thiscontrollerisoverriddentoallowconfiguringsale_order_linesthroughapopup
 *windowwhenaproductwith'event_ok'isselected.
 *
 *Thisallowskeepinganeditablelistviewforsalesorderandremovethenoiseof
 *those2fields('event_id'+'event_ticket_id')
 */
varEventConfiguratorFormController=FormController.extend({
    /**
     *Welettheregularprocesstakeplacetoallowthevalidationoftherequiredfields
     *tohappen.
     *
     *Thenwecanmanuallyclosethewindow,providingeventinformationtothecaller.
     *
     *@override
     */
    saveRecord:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            varstate=self.renderer.state.data;
            self.do_action({type:'ir.actions.act_window_close',infos:{
                eventConfiguration:{
                    event_id:{id:state.event_id.data.id},
                    event_ticket_id:{id:state.event_ticket_id.data.id}
                }
            }});
        });
    }
});

returnEventConfiguratorFormController;

});
