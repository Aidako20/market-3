flectra.define('point_of_sale.SyncNotification',function(require){
    'usestrict';

    const{useState}=owl;
    constPosComponent=require('point_of_sale.PosComponent');
    constRegistries=require('point_of_sale.Registries');

    //PreviouslySynchNotificationWidget
    classSyncNotificationextendsPosComponent{
        constructor(){
            super(...arguments);
            constsynch=this.env.pos.get('synch');
            this.state=useState({status:synch.status,msg:synch.pending});
        }
        mounted(){
            this.env.pos.on(
                'change:synch',
                (pos,synch)=>{
                    this.state.status=synch.status;
                    this.state.msg=synch.pending;
                },
                this
            );
        }
        willUnmount(){
            this.env.pos.on('change:synch',null,this);
        }
        onClick(){
            this.env.pos.push_orders(null,{show_error:true});
        }
    }
    SyncNotification.template='SyncNotification';

    Registries.Component.add(SyncNotification);

    returnSyncNotification;
});
