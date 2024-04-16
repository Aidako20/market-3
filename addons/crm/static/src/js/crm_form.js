flectra.define("crm.crm_form",function(require){
    "usestrict";

    /**
     *ThisFromControllermakessurewedisplayarainbowmanmessage
     *whenthestageiswon,evenwhenweclickonthestatusbar.
     *Whenthestageofaleadischangedanddataaresaved,wecheck
     *iftheleadiswonandifamessageshouldbedisplayedtotheuser
     *witharainbowmanlikewhentheuserclickonthebutton"MarkWon".
     */

    varFormController=require('web.FormController');
    varFormView=require('web.FormView');
    varviewRegistry=require('web.view_registry');

    varCrmFormController=FormController.extend({
        /**
         *Mainmethodusedwhensavingtherecordhittingthe"Save"button.
         *Wecheckifthestage_idfieldwasalteredandifweneedtodisplayarainbowman
         *message.
         *
         *Thismethodwillalsosimulateareal"force_save"ontheemailandphone
         *whenneeded.The"force_save"attributeonlyworksonreadonlyfield.Forour
         *usecase,weneedtowritetheemailandthephoneeveniftheuserdidn't
         *changethem,tosynchronizethosevalueswiththepartner(sotheemail/phone
         *inversemethodcanbecalled).
         *
         *Webasethissynchronizationonthevalueof"ribbon_message",whichisa
         *computedfieldthatholdavaluewheneverweneedtosynch.
         *
         *@override
         */
        saveRecord:function(recordID,options){
            recordID=recordID||this.handle;
            constlocalData=this.model.localData[recordID];
            constchanges=localData._changes||{};

            constneedsSynchronization=changes.ribbon_message===undefined
                ?localData.data.ribbon_message//originalvalue
                :changes.ribbon_message;//newvalue

            if(needsSynchronization&&changes.email_from===undefined&&localData.data.email_from){
                changes.email_from=localData.data.email_from;
            }
            if(needsSynchronization&&changes.phone===undefined&&localData.data.phone){
                changes.phone=localData.data.phone;
            }
            if(!localData._changes&&Object.keys(changes).length){
                localData._changes=changes;
            }

            returnthis._super(...arguments).then((modifiedFields)=>{
                if(modifiedFields.indexOf('stage_id')!==-1){
                    this._checkRainbowmanMessage(this.renderer.state.res_id)
                }
            });
        },

        //--------------------------------------------------------------------------
        //Private
        //--------------------------------------------------------------------------

        /**
         *Applychangemaybecalledwith'event.data.force_save'settoTrue.
         *Thistypicallyhappenswhendirectlyclickinginthestatusbarwidgetonanewstage.
         *Ifit'sthecase,wecheckforamodifiedstage_idfieldandifweneedtodisplaya
         *rainbowmanmessage.
         *
         *@param{string}dataPointID
         *@param{Object}changes
         *@param{FlectraEvent}event
         *@override
         *@private
         */
        _applyChanges:function(dataPointID,changes,event){
            returnthis._super(...arguments).then(()=>{
                if(event.data.force_save&&'stage_id'inchanges){
                    this._checkRainbowmanMessage(parseInt(event.target.res_id));
                }
            });
        },

        /**
         *Whenupdatingacrm.lead,throughdirectuseofthestatusbarorwhensavingthe
         *record,wecheckforarainbowmanmessagetodisplay.
         *
         *(seeWidgetdocstringformoreinformation).
         *
         *@param{integer}recordId
         */
        _checkRainbowmanMessage:asyncfunction(recordId){
            constmessage=awaitthis._rpc({
                model:'crm.lead',
                method:'get_rainbowman_message',
                args:[[recordId]],
            });
            if(message){
                this.trigger_up('show_effect',{
                    message:message,
                    type:'rainbow_man',
                });
            }
        }
    });

    varCrmFormView=FormView.extend({
        config:_.extend({},FormView.prototype.config,{
            Controller:CrmFormController,
        }),
    });

    viewRegistry.add('crm_form',CrmFormView);

    return{
        CrmFormController:CrmFormController,
        CrmFormView:CrmFormView,
    };
});
