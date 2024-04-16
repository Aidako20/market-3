flectra.define("website.tour.backend_dashboard",function(require){
"usestrict";

vartour=require("web_tour.tour");

tour.register("backend_dashboard",{
    test:true,
    url:"/web",
},[tour.stepUtils.showAppsMenuItem(),
    {
    trigger:'a[data-menu-xmlid="website.menu_website_configuration"]',
},{
    trigger:'.dropdown-toggle[data-menu-xmlid="website.menu_dashboard"]',
},{
    trigger:'.dropdown-item[data-menu-xmlid="website.menu_website_google_analytics"]',
},{
    //Visitssectionshouldalwaysbepresentevenwhenempty/nothookedtoanything
    trigger:'h2:contains("Visits")',
    content:"Checkifdashboardloads",
    run:function(){}
}]);
});
