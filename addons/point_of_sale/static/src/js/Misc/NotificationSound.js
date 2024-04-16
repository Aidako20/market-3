flectra.define('point_of_sale.NotificationSound',function(require){
    'usestrict';

    const{useListener}=require('web.custom_hooks');
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    classNotificationSoundextendsPosComponent{
        constructor(){
            super(...arguments);
            useListener('ended',()=>(this.props.sound.src=null));
        }
    }
    NotificationSound.template='NotificationSound';

    Registries.Component.add(NotificationSound);

    returnNotificationSound;
});
