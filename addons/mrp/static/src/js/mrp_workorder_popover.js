flectra.define('mrp.mrp_workorder_popover',function(require){
'usestrict';

varPopoverWidget=require('stock.popover_widget');
varfieldRegistry=require('web.field_registry');
varcore=require('web.core');
var_t=core._t;


/**
 *LinktoaCharfieldrepresentingaJSON:
 *{
 * 'replan':<REPLAN_BOOL>,//Showthereplanbtn
 * 'color':'<COLOR_CLASS>',//ColorClassoftheicon(d-nonetohide)
 * 'infos':[
 *     {'msg':'<MESSAGE>','color':'<COLOR_CLASS>'},
 *     {'msg':'<MESSAGE>','color':'<COLOR_CLASS>'},
 *     ...]
 *}
 */
varMrpWorkorderPopover=PopoverWidget.extend({
    popoverTemplate:'mrp.workorderPopover',
    title:_t('SchedulingInformation'),

    _render:function(){
        this._super.apply(this,arguments);
        if(!this.$popover){
          return;
        }
        varself=this;
        this.$popover.find('.action_replan_button').click(function(e){
            self._onReplanClick(e);
        });
    },

    _onReplanClick:function(e){
        varself=this;
        this._rpc({
            model:'mrp.workorder',
            method:'action_replan',
            args:[[self.res_id]]
        }).then(function(){
            self.trigger_up('reload');
        });
    },
});

fieldRegistry.add('mrp_workorder_popover',MrpWorkorderPopover);

returnMrpWorkorderPopover;
});
