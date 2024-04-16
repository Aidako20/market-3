flectra.define('website.tour.specific_website_editor',function(require){
'usestrict';

vartour=require('web_tour.tour');

tour.register('generic_website_editor',{
    test:true,
},[{
    trigger:'a[data-action=edit]',
    content:'Clickeditbutton',
},{
    trigger:'body:not([data-hello="world"])',
    extra_trigger:'#oe_snippets.o_loaded',
    content:'CheckthattheeditorDOMmatchesitswebsite-genericfeatures',
    run:function(){},//Simplecheck
}]);

tour.register('specific_website_editor',{
    test:true,
},[{
    trigger:'a[data-action=edit]',
    content:'Clickeditbutton',
},{
    trigger:'body[data-hello="world"]',
    extra_trigger:'#oe_snippets.o_loaded',
    content:'CheckthattheeditorDOMmatchesitswebsite-specificfeatures',
    run:function(){},//Simplecheck
}]);
});
