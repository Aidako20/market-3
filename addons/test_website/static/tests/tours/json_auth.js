flectra.define('test_website.json_auth',function(require){
'usestrict';

vartour=require('web_tour.tour');
varsession=require('web.session')

tour.register('test_json_auth',{
    test:true,
},[{
    trigger:'body',
    run:asyncfunction(){
        awaitsession.rpc('/test_get_dbname').then(function(result){
            returnsession.rpc("/web/session/authenticate",{
                db:result,
                login:'admin',
                password:'admin'
            });
        });
        window.location.href=window.location.origin;
    },
},{
    trigger:'span:contains(MitchellAdmin),span:contains(Administrator)',
    run:function(){},
}
]);
});
