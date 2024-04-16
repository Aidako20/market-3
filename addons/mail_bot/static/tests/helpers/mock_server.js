flectra.define('mail_bot/static/tests/helpers/mock_server.js',function(require){
"usestrict";

constMockServer=require('web.MockServer');

MockServer.include({
    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    async_performRpc(route,args){
        if(args.model==='mail.channel'&&args.method==='init_flectrabot'){
            returnthis._mockMailChannelInitFlectraBot();
        }
        returnthis._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //PrivateMockedMethods
    //--------------------------------------------------------------------------

    /**
     *Simulates`init_flectrabot`on`mail.channel`.
     *
     *@private
     */
    _mockMailChannelInitFlectraBot(){
        //TODOimplementthismocktask-2300480
        //andimprovetest"FlectraBotinitializedafter2minutes"
    },
});

});
