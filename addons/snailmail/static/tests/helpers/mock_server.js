flectra.define('snailmail/static/tests/helpers/mock_server.js',function(require){
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
        if(args.model==='mail.message'&&args.method==='cancel_letter'){
            constids=args.args[0];
            returnthis._mockMailMessageCancelLetter(ids);
        }
        if(args.model==='mail.message'&&args.method==='send_letter'){
            constids=args.args[0];
            returnthis._mockMailMessageSendLetter(ids);
        }
        returnthis._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //PrivateMockedMethods
    //--------------------------------------------------------------------------

    /**
     *Simulates`cancel_letter`on`mail.message`.
     *
     *@private
     *@param{integer[]}ids
     */
    _mockMailMessageCancelLetter(ids){
        //TODOimplementthismockandimproverelatedtests(task-2300496)
    },
    /**
     *Simulates`send_letter`on`mail.message`.
     *
     *@private
     *@param{integer[]}ids
     */
    _mockMailMessageSendLetter(ids){
        //TODOimplementthismockandimproverelatedtests(task-2300496)
    },
});

});
