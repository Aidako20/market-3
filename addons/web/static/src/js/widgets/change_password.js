flectra.define('web.ChangePassword',function(require){
"usestrict";

/**
 *Thisfiledefinesaclientactionthatopensinadialog(target='new')and
 *allowstheusertochangehispassword.
 */

varAbstractAction=require('web.AbstractAction');
varcore=require('web.core');
varDialog=require('web.Dialog');
varweb_client=require('web.web_client');

var_t=core._t;

varChangePassword=AbstractAction.extend({
    template:"ChangePassword",

    /**
     *@fixme:weirdinteractionwiththeparentforthe$buttonshandling
     *
     *@override
     *@returns{Promise}
     */
    start:function(){
        varself=this;
        web_client.set_title(_t("ChangePassword"));
        var$button=self.$('.oe_form_button');
        $button.appendTo(this.getParent().$footer);
        $button.eq(1).click(function(){
            self.$el.parents('.modal').modal('hide');
        });
        $button.eq(0).click(function(){
            self._rpc({
                    route:'/web/session/change_password',
                    params:{
                        fields:$('form[name=change_password_form]').serializeArray()
                    }
                })
                .then(function(result){
                    if(result.error){
                        self._display_error(result);
                    }else{
                    self.do_action('logout');
                    }
                });
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Displaystheerrorinadialog
     *
     *@private
     *@param{Object}error
     *@param{string}error.error
     *@param{string}error.title
     */
    _display_error:function(error){
        returnnewDialog(this,{
            size:'medium',
            title:error.title,
            $content:$('<div>').html(error.error)
        }).open();
    },
});

core.action_registry.add("change_password",ChangePassword);

returnChangePassword;

});
