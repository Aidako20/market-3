flectra.define("website.tour.website_style_edition",function(require){
"usestrict";

consttour=require("web_tour.tour");

constTARGET_FONT_SIZE=30;

tour.register("website_style_edition",{
    test:true,
    url:"/",
},[{
    content:"Entereditmode",
    trigger:'a[data-action=edit]',
},{
    content:"Gotothemeoptions",
    trigger:'.o_we_customize_theme_btn',
},{
    content:"Changefontsize",
    trigger:'[data-variable="font-size-base"]input',
    run:`text_blur${TARGET_FONT_SIZE}`,
},{
    content:"Save",
    trigger:'[data-action="save"]',
},{
    content:"Checkthefontsizewasproperlyadapted",
    trigger:'body:not(.editor_enable)#wrapwrap',
    run:function(actions){
        conststyle=window.getComputedStyle(this.$anchor[0]);
        if(style.fontSize!==`${TARGET_FONT_SIZE}px`){
            console.error(`Expectedthefont-sizetobeequalto${TARGET_FONT_SIZE}pxbutfound${style.fontSize}instead`);
        }
    },
}]);
});
