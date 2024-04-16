flectra.define('stock.PopoverStockPicking',function(require){
"usestrict";

varcore=require('web.core');

varPopoverWidgetField=require('stock.popover_widget');
varregistry=require('web.field_registry');
var_lt=core._lt;

varPopoverStockPicking=PopoverWidgetField.extend({
    title:_lt('PlanningIssue'),
    trigger:'focus',
    color:'text-danger',
    icon:'fa-exclamation-triangle',

    _render:function(){
        this._super();
        if(this.$popover){
            varself=this;
            this.$popover.find('a').on('click',function(ev){
                ev.preventDefault();
                ev.stopPropagation();
                self.do_action({
                    type:'ir.actions.act_window',
                    res_model:ev.currentTarget.getAttribute('element-model'),
                    res_id:parseInt(ev.currentTarget.getAttribute('element-id'),10),
                    views:[[false,'form']],
                    target:'current'
                });
            });
        }
    },

});

registry.add('stock_rescheduling_popover',PopoverStockPicking);

returnPopoverStockPicking;
});
