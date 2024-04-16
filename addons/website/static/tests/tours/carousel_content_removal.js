flectra.define('website.tour.carousel_content_removal',function(require){
'usestrict';

consttour=require('web_tour.tour');

tour.register("carousel_content_removal",{
    test:true,
    url:"/",
},[{
    trigger:"a[data-action=edit]",
    content:"ClicktheEditbutton.",
    extra_trigger:".homepage",
},{
    trigger:"#snippet_structure.oe_snippet:has(span:contains('Carousel')).oe_snippet_thumbnail",
    content:"DragtheCarouselblockanddropitinyourpage.",
    run:"drag_and_drop#wrap",
},
{
    trigger:".carousel.carousel-item.active.carousel-content",
    content:"Selecttheactivecarouselitem.",
},{
    trigger:".oe_overlay.oe_active.oe_snippet_remove",
    content:"Removetheactivecarouselitem.",
},
{
    trigger:".carousel.carousel-item.active.container:not(:has(*))",
    content:"Checkforacarouselslidewithanemptycontainertag",
    run:function(){},
}]);

});
