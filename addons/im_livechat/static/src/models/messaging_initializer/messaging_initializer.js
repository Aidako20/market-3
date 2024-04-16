flectra.define('im_livechat/static/src/models/messaging_initializer/messaging_initializer.js',function(require){
'usestrict';

const{registerInstancePatchModel}=require('mail/static/src/model/model_core.js');
const{executeGracefully}=require('mail/static/src/utils/utils.js');

registerInstancePatchModel('mail.messaging_initializer','im_livechat/static/src/models/messaging_initializer/messaging_initializer.js',{

    //----------------------------------------------------------------------
    //Private
    //----------------------------------------------------------------------

    /**
     *@override
     *@param{Object[]}[param0.channel_livechat=[]]
     */
    async_initChannels(initMessagingData){
        awaitthis.async(()=>this._super(initMessagingData));
        const{channel_livechat=[]}=initMessagingData;
        returnexecuteGracefully(channel_livechat.map(data=>()=>{
            constchannel=this.env.models['mail.thread'].insert(
                this.env.models['mail.thread'].convertData(data),
            );
            //fluxspecific:channelsreceivedatinithavetobe
            //consideredpinned.task-2284357
            if(!channel.isPinned){
                channel.pin();
            }
        }));
    },
});

});
