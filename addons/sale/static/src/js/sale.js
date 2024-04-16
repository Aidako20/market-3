flectra.define('sale.sales_team_dashboard',function(require){
"usestrict";

varcore=require('web.core');
varKanbanRecord=require('web.KanbanRecord');
var_t=core._t;

KanbanRecord.include({
    events:_.defaults({
        'click.sales_team_target_definition':'_onSalesTeamTargetClick',
    },KanbanRecord.prototype.events),

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@param{MouseEvent}ev
     */
    _onSalesTeamTargetClick:function(ev){
        ev.preventDefault();
        varself=this;

        this.$target_input=$('<input>');
        this.$('.o_kanban_primary_bottom:last').html(this.$target_input);
        this.$('.o_kanban_primary_bottom:last').prepend(_t("Setaninvoicingtarget:"));
        this.$target_input.focus();

        this.$target_input.on({
            blur:this._onSalesTeamTargetSet.bind(this),
            keydown:function(ev){
                if(ev.keyCode===$.ui.keyCode.ENTER){
                    self._onSalesTeamTargetSet();
                }
            },
        });
    },
    /**
     *Mostlyahandlerforwhathappenstotheinput"this.$target_input"
     *
     *@private
     *
     */
    _onSalesTeamTargetSet:function(){
        varself=this;
        varvalue=Number(this.$target_input.val());
        if(isNaN(value)){
            this.do_warn(false,_t("Pleaseenteranintegervalue"));
        }else{
            this.trigger_up('kanban_record_update',{
                invoiced_target:value,
                onSuccess:function(){
                    self.trigger_up('reload');
                },
            });
        }
    },
});

});
