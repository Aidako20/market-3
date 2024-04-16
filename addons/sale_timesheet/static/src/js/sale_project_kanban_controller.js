flectra.define('sale_timesheet.sale_project_kanban_controller',function(require){
"usestrict";

varcore=require('web.core');
varProjectKanbanController=require('project.project_kanban');
varsession=require('web.session');

varQWeb=core.qweb;

//YTITODO:Masterremovefile

varSaleProjectKanbanController=ProjectKanbanController.include({

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _showCreateSOButton:asyncfunction(){
        varself=this;
        this.activeProjectIds=this.initialState.context.active_ids;

        if(!this.activeProjectIds||this.activeProjectIds.length!==1){
            this.showCreateSaleOrder=false;
            return;
        }
        varcanCreateSO=awaitsession.user_has_group('sales_team.group_sale_salesman');
        if(canCreateSO){
            awaitthis._rpc({
                model:'project.project',
                method:'search_count',
                args:[[
                    ["id","in",this.activeProjectIds],
                    ["bill_type","=","customer_project"],
                    ["sale_order_id","=",false],
                    ["allow_billable","=",true],
                    ["allow_timesheets","=",true],
                ]],
            }).then(function(projectCount){
                self.showCreateSaleOrder=projectCount!==0;
            });
        }else{
            this.showCreateSaleOrder=false;
        }
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onCreateSaleOrder:function(ev){
        ev.preventDefault();
        this.do_action('sale_timesheet.project_project_action_multi_create_sale_order',{
            additional_context:{
                'active_id':this.activeProjectIds&&this.activeProjectIds[0],
                'active_model':"project.project",
            },
            on_close:async()=>awaitthis.reload()
        });
    },
});

returnSaleProjectKanbanController;

});
