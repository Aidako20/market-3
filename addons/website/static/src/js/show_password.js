//
//Thisfileismeanttoallowtoswitchthetypeofaninput#password
//frompasswordtotextonmousedownonaninputgroup.
//Onmousedown,weseethepasswordincleartext
//Onmouseup,wehideitagain.
//
flectra.define('website.show_password',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.ShowPassword=publicWidget.Widget.extend({
    selector:'#showPass',
    events:{
        'mousedown':'_onShowText',
        'touchstart':'_onShowText',
    },

    /**
     *@override
     */
    destroy:function(){
        this._super(...arguments);
        $('body').off(".ShowPassword");
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onShowPassword:function(){
        this.$el.closest('.input-group').find('#password').attr('type','password');
    },
    /**
     *@private
     */
    _onShowText:function(){
        $('body').one('mouseup.ShowPasswordtouchend.ShowPassword',this._onShowPassword.bind(this));
        this.$el.closest('.input-group').find('#password').attr('type','text');
    },
});

returnpublicWidget.registry.ShowPassword;

});
