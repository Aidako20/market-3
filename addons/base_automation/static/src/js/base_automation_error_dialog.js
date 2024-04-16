flectra.define('base_automation.BaseAutomatioErrorDialog',function(require){
    "usestrict";

    constCrashManager=require('web.CrashManager');
    constErrorDialog=CrashManager.ErrorDialog;
    constErrorDialogRegistry=require('web.ErrorDialogRegistry');
    constsession=require('web.session');

    constBaseAutomationErrorDialog=ErrorDialog.extend({
        xmlDependencies:(ErrorDialog.prototype.xmlDependencies||[]).concat(
            ['/base_automation/static/src/xml/base_automation_error_dialog.xml']
        ),
        template:'CrashManager.BaseAutomationError',
        events:{
            'click.o_disable_action_button':'_onDisableAction',
            'click.o_edit_action_button':'_onEditAction',
        },
        /**
        *Assignthe`base_automation`objectbasedontheerrordata,
        *whichisthenusedbythe`CrashManager.BaseAutomationError`template
        *andtheeventsdefinedabove.
        *@override
        *@param{Object}error
        *@param{string}error.data.context.base_automation.id theIDofthefailingautomatedaction
        *@param{string}error.data.context.base_automation.name thenameofthefailingautomatedaction
        */
        init:function(parent,options,error){
            this._super.apply(this,arguments);
            this.base_automation=error.data.context.base_automation;
            this.is_admin=session.is_admin;
        },

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
        *Thismethodiscalledwhentheuserclicksonthe'Disableaction'button
        *displayedwhenacrashoccursintheevaluationofanautomatedaction.
        *Then,wewrite`active`to`False`ontheautomatedactiontodisableit.
        *
        *@private
        *@param{MouseEvent}ev
        */
        _onDisableAction:function(ev){
            ev.preventDefault();
            this._rpc({
                model:'base.automation',
                method:'write',
                args:[[this.base_automation.id],{
                    active:false,
                }],
            }).then(this.destroy.bind(this));
        },
        /**
        *Thismethodiscalledwhentheuserclicksonthe'Editaction'button
        *displayedwhenacrashoccursintheevaluationofanautomatedaction.
        *Then,weredirecttheusertotheautomatedactionform.
        *
        *@private
        *@param{MouseEvent}ev
        */
        _onEditAction:function(ev){
            ev.preventDefault();
            this.do_action({
                name:'AutomatedActions',
                res_model:'base.automation',
                res_id:this.base_automation.id,
                views:[[false,'form']],
                type:'ir.actions.act_window',
                view_mode:'form',
            });
        },
    });

    ErrorDialogRegistry.add('base_automation',BaseAutomationErrorDialog);

});
