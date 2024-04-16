flectra.define('website_event.register_toaster_widget',function(require){
'usestrict';

letcore=require('web.core');
let_t=core._t;
letpublicWidget=require('web.public.widget');

publicWidget.registry.RegisterToasterWidget=publicWidget.Widget.extend({
    selector:'.o_wevent_register_toaster',

    /**
     *Thiswidgetallowstodisplayatoastmessageonthepage.
     *
     *@override
     */
    start:function(){
        constmessage=this.$el.data('message');
        if(message&&message.length){
            this.displayNotification({
                title:_t("Register"),
                message:message,
                type:'info'
            });
        }
        returnthis._super.apply(this,arguments);
    },
});

returnpublicWidget.registry.RegisterToasterWidget;

});
