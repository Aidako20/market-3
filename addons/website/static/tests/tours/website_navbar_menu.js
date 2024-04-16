flectra.define("website.tour.website_navbar_menu",function(require){
"usestrict";

vartour=require("web_tour.tour");

tour.register("website_navbar_menu",{
    test:true,
    url:"/",
},[
    {
        content:"EnsuremenusareinDOM",
        trigger:'#top_menu.nav-itema:contains("TestTourMenu")',
        run:function(){},//it'sacheck
    },{
        content:"Ensuremenusloadingisdone(sotheyareactuallyvisible)",
        trigger:'body:not(:has(.o_menu_loading))',
        run:function(){},//it'sacheck
    }
]);
});
