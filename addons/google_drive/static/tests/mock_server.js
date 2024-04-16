flectra.define('google_drive.MockServer',function(require){
    'usestrict';

    varMockServer=require('web.MockServer');

    MockServer.include({
        //--------------------------------------------------------------------------
        //Private
        //--------------------------------------------------------------------------

        /**
         *@override
         *@private
         */
        async_performRpc(route,args){
            if(args.method==='get_google_drive_config'){
                return[];
            }
            returnthis._super(...arguments);
        },
    });
});
