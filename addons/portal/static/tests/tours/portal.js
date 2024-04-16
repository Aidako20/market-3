flectra.define('portal.tour',function(require){
'usestrict';

vartour=require("web_tour.tour");

tour.register('portal_load_homepage',{
    test:true,
    url:'/my',
},
    [
        {
            content:"Checkportalisloaded",
            trigger:'a[href*="/my/account"]:contains("Edit"):first',
        },
        {
            content:"Loadmyaccountdetails",
            trigger:'input[value="JoelWillis"]'
        }
    ]
);

});
