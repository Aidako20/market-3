flectra.define('iap/static/tests/helpers/mock_server.js',function(require){
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
        if(args.model==='iap.account'&&args.method==='get_credits_url'){
            constservice_name=args.args[0]||args.kwargs.service_name;
            constbase_url=args.args[1]||args.kwargs.base_url;
            constcredit=args.args[2]!==undefined?args.args[2]:args.kwargs.credit;
            consttrial=args.args[3]!==undefined?args.args[3]:args.kwargs.trial;
            returnthis._mockIapAccountGetCreditsUrl(service_name,base_url,credit,trial);
        }
        returnthis._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //PrivateMockedRoutes
    //--------------------------------------------------------------------------

    /**
     *Simulates`get_credits_url`on`iap.account`.
     *
     *@private
     *@param{string}service_name
     *@param{string}[base_url='']
     *@param{number}[credit=0]
     *@param{boolean}[trial=false]
     *@returns{string}
     */
    _mockIapAccountGetCreditsUrl(service_name,base_url='',credit=0,trial=false){
        //Thismockcouldbeimproved,inparticularbyreturninganURLthat
        //isactuallymockedhereandincludingallparams,butitisnotdone
        //duetoURLnotbeingusedinanytestatthetimeofthiscomment.
        returnbase_url+'/random/url?service_name='+service_name;
    },
});

});
