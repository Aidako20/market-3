flectra.define("website.tour.restricted_editor",function(require){
"usestrict";

vartour=require("web_tour.tour");

tour.register("restricted_editor",{
    test:true,
    url:"/",
},[{
    trigger:'a[data-action=edit]',
    content:"Click\"EDIT\"buttonofwebsiteasRestrictedEditor",
    extra_trigger:".homepage",
},{
    trigger:'#oe_snippets.o_loaded',
    content:"Checkthatthesnippetsloadedproperly",
}]);
});
