flectra.define('stock.InventoryValidationController',function(require){
"usestrict";

varcore=require('web.core');
varListController=require('web.ListController');

var_t=core._t;
varqweb=core.qweb;

varInventoryValidationController=ListController.extend({
    events:_.extend({
        'click.o_button_validate_inventory':'_onValidateInventory'
    },ListController.prototype.events),
    /**
     *@override
     */
    init:function(parent,model,renderer,params){
        varcontext=renderer.state.getContext();
        this.inventory_id=context.active_id;
        returnthis._super.apply(this,arguments);
    },

    //-------------------------------------------------------------------------
    //Public
    //-------------------------------------------------------------------------

    /**
     *@override
     */
    renderButtons:function(){
        this._super.apply(this,arguments);
        var$validationButton=$(qweb.render('InventoryLines.Buttons'));
        this.$buttons.prepend($validationButton);
    },

    //-------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *Handlercalledwhenuserclickonvalidationbuttonininventorylines
     *view.Makesanrpctotrytovalidatetheinventory,thenwillgobackon
     *theinventoryviewformifitwasvalidated.
     *Thismethodcouldalsoopenawizardincasesomethingwasmissing.
     *
     *@private
     */
    _onValidateInventory:function(){
        varself=this;
        varprom=Promise.resolve();
        varrecordID=this.renderer.getEditableRecordID();
        if(recordID){
            //Ifuser'seditingarecord,wewaittosaveitbeforetotryto
            //validatetheinventory.
            prom=this.saveRecord(recordID);
        }

        prom.then(function(){
            self._rpc({
                model:'stock.inventory',
                method:'action_validate',
                args:[self.inventory_id]
            }).then(function(res){
                varexitCallback=function(infos){
                    //Incasewediscardedawizard,wedonothingtostayon
                    //thesameview...
                    if(infos&&infos.special){
                        return;
                    }
                    //...butinanyothercases,wegobackontheinventoryform.
                    self.do_notify(
                        false,
                        _t("Theinventoryhasbeenvalidated"));
                    self.trigger_up('history_back');
                };

                if(_.isObject(res)){
                    self.do_action(res,{on_close:exitCallback});
                }else{
                    returnexitCallback();
                }
            });
        });
    },
});

returnInventoryValidationController;

});
