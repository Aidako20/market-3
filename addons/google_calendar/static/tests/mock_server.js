flectra.define('google_calendar.MockServer',function(require){
    'usestrict';

    varMockServer=require('web.MockServer');

    MockServer.include({
        /**
         *@override
         *@private
         *@returns{Promise}
         */
        _performRpc(route,args){
            if(route==='/google_calendar/sync_data'){
                returnPromise.resolve({status:'no_new_event_from_google'});
            }else{
                returnthis._super(...arguments);
            }
        },
    });
});
