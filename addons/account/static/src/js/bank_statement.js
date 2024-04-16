flectra.define('account.bank_statement',function(require){
    "usestrict";

    varKanbanController=require("web.KanbanController");
    varListController=require("web.ListController");

    varincludeDict={
        renderButtons:function(){
            this._super.apply(this,arguments);
            if(this.modelName==="account.bank.statement"){
                vardata=this.model.get(this.handle);
                if(data.context.journal_type!=='cash'){
                    this.$buttons.find('button.o_button_import').hide();
                }
            }
        }
    };

    KanbanController.include(includeDict);
    ListController.include(includeDict);
});