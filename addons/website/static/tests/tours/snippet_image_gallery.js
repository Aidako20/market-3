flectra.define("website.tour.snippet_image_gallery",function(require){
"usestrict";

consttour=require("web_tour.tour");
constwTourUtils=require("website.tour_utils");

tour.register("snippet_image_gallery",{
    test:true,
    url:"/",
},[
    ...wTourUtils.clickOnEditAndWaitEditMode(),
    wTourUtils.dragNDrop({
        id:"s_image_gallery",
        name:"ImageGallery",
}),{
    content:"Clickonthefirstnewimage",
    trigger:".o_select_media_dialogimg[title='s_default_image.jpg']",
},{
    content:"Clickonthesecondnewimage",
    trigger:".o_select_media_dialogimg[title='s_default_image2.jpg']",
},{
    content:"ClickonAdd",
    trigger:"button:has(span:contains('Add'))",
},{
    content:"ClickontheimageoftheImageGallerysnippet",
    trigger:".s_image_gallery.carousel-item.active img",
},{
    content:"ClickonRemoveBlock",
    trigger:".o_we_customize_panelwe-title:has(span:contains('ImageGallery'))we-button[title='RemoveBlock']",
},{
    content:"CheckthattheImageGallerysnippethasbeenremoved",
    trigger:"#wrap:not(:has(.s_image_gallery))",
    run:()=>null,
}]);
});
