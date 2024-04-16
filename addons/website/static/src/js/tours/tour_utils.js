flectra.define("website.tour_utils",function(require){
"usestrict";

constcore=require("web.core");
const_t=core._t;

vartour=require("web_tour.tour");

/**

constsnippets=[
    {
        id:'s_cover',
        name:'Cover',
    },
    {
        id:'s_text_image',
        name:'Text-Image',
    }
];

tour.register("themename_tour",{
    url:"/",
    saveAs:"homepage",
},[
    wTourUtils.dragNDrop(snippets[0]),
    wTourUtils.clickOnText(snippets[0],'h1'),
    wTourUtils.changeOption('colorFilter','span.o_we_color_preview',_t('colorfilter')),
    wTourUtils.selectHeader(),
    wTourUtils.changeOption('HeaderTemplate','[data-name="header_alignment_opt"]',_t('alignment')),
    wTourUtils.goBackToBlocks(),
    wTourUtils.dragNDrop(snippets[1]),
    wTourUtils.changeImage(snippets[1]),
    wTourUtils.clickOnSave(),
]);
**/



functionaddMedia(position="right"){
    return{
        trigger:`.modal-contentfooter.btn-primary`,
        content:_t("<b>Add</b>theselectedimage."),
        position:position,
        run:"click",
    };
}

functionchangeBackground(snippet,position="bottom"){
    return{
        trigger:".o_we_customize_panel.o_we_edit_image",
        content:_t("<b>Customize</b>anyblockthroughthismenu.Trytochangethebackgroundimageofthisblock."),
        position:position,
        run:"click",
    };
}

functionchangeBackgroundColor(position="bottom"){
    return{
        trigger:".o_we_customize_panel.o_we_color_preview",
        content:_t("<b>Customize</b>anyblockthroughthismenu.Trytochangethebackgroundcolorofthisblock."),
        position:position,
        run:"click",
    };
}

functionselectColorPalette(position="left"){
    return{
        trigger:".o_we_customize_panel.o_we_so_color_palettewe-selection-items",
        alt_trigger:".o_we_customize_panel.o_we_color_preview",
        content:_t(`<b>Select</b>aColorPalette.`),
        position:position,
        run:'click',
        location:position==='left'?'#oe_snippets':undefined,
    };
}

functionchangeColumnSize(position="right"){
    return{
        trigger:`.oe_overlay.ui-draggable.o_we_overlay_sticky.oe_active.o_handle.e`,
        content:_t("<b>Slide</b>thisbuttontochangethecolumnsize."),
        position:position,
    };
}

functionchangeIcon(snippet,index=0,position="bottom"){
    return{
        trigger:`#wrapwrap.${snippet.id}i:eq(${index})`,
        content:_t("<b>Doubleclickonanicon</b>tochangeitwithoneofyourchoice."),
        position:position,
        run:"dblclick",
    };
}

functionchangeImage(snippet,position="bottom"){
    return{
        trigger:`#wrapwrap.${snippet.id}img`,
        content:_t("<b>Doubleclickonanimage</b>tochangeitwithoneofyourchoice."),
        position:position,
        run:"dblclick",
    };
}

/**
    wTourUtils.changeOption('HeaderTemplate','[data-name="header_alignment_opt"]',_t('alignment')),
*/
functionchangeOption(optionName,weName='',optionTooltipLabel='',position="bottom"){
    constoption_block=`we-customizeblock-option[class='snippet-option-${optionName}']`
    return{
        trigger:`${option_block}${weName},${option_block}[title='${weName}']`,
        content:_.str.sprintf(_t("<b>Click</b>onthisoptiontochangethe%softheblock."),optionTooltipLabel),
        position:position,
        run:"click",
    };
}

functionselectNested(trigger,optionName,alt_trigger=null,optionTooltipLabel='',position="top"){
    constoption_block=`we-customizeblock-option[class='snippet-option-${optionName}']`;
    return{
        trigger:trigger,
        content:_.str.sprintf(_t("<b>Select</b>a%s."),optionTooltipLabel),
        alt_trigger:alt_trigger==null?undefined:`${option_block}${alt_trigger}`,
        position:position,
        run:'click',
        location:position==='left'?'#oe_snippets':undefined,
    };
}

functionchangePaddingSize(direction){
    letpaddingDirection="n";
    letposition="top";
    if(direction==="bottom"){
        paddingDirection="s";
        position="bottom";
    }
    return{
        trigger:`.oe_overlay.ui-draggable.o_we_overlay_sticky.oe_active.o_handle.${paddingDirection}`,
        content:_.str.sprintf(_t("<b>Slide</b>thisbuttontochangethe%spadding"),direction),
        consumeEvent:'mousedown',
        position:position,
    };
}

/**
 *Clickonthetoprighteditbutton
 *
 *@deprecateduse`clickOnEditAndWaitEditMode`insteadtoavoidracecondition
 */
functionclickOnEdit(position="bottom"){
    return{
        trigger:"a[data-action=edit]",
        content:_t("<b>ClickEdit</b>tostartdesigningyourhomepage."),
        extra_trigger:".homepage",
        position:position,
    };
}

/**
 *Clickonthetoprighteditbuttonandwaitfortheeditmode
 *
 *@param{string}positionWherethepurplearrowwillshowup
 */
functionclickOnEditAndWaitEditMode(position="bottom"){
    return[{
        content:_t("<b>ClickEdit</b>tostartdesigningyourhomepage."),
        trigger:"a[data-action=edit]",
        position:position,
    },{
        content:"Checkthatweareineditmode",
        trigger:'#oe_snippets.o_loaded',
        run:()=>null,//it'sacheck
    }];
}

/**
 *Simpleclickonasnippetintheeditionarea
 *@param{*}snippet
 *@param{*}position
 */
functionclickOnSnippet(snippet,position="bottom"){
    return{
        trigger:`#wrapwrap.${snippet.id}`,
        content:_t("<b>Clickonasnippet</b>toaccessitsoptionsmenu."),
        position:position,
        run:"click",
    };
}

functionclickOnSave(position="bottom"){
    return{
        trigger:"button[data-action=save]",
        in_modal:false,
        content:_t("Goodjob!It'stimeto<b>Save</b>yourwork."),
        position:position,
    };
}

/**
 *Clickonasnippet'stexttomodifyitscontent
 *@param{*}snippet
 *@param{*}elementTargettheelementwhichshouldberewrite
 *@param{*}position
 */
functionclickOnText(snippet,element,position="bottom"){
    return{
        trigger:`#wrapwrap.${snippet.id}${element}`,
        content:_t("<b>Clickonatext</b>tostarteditingit."),
        position:position,
        run:"text",
        consumeEvent:"input",
    };
}

/**
 *DragasnippetfromtheBlocksareaanddropitintheEditarea
 *@param{*}snippetcontaintheidandthenameofthetargetedsnippet
 *@param{*}positionWherethepurplearrowwillshowup
 */
functiondragNDrop(snippet,position="bottom"){
    return{
        trigger:`#oe_snippets.oe_snippet[name="${snippet.name}"].oe_snippet_thumbnail:not(.o_we_already_dragging)`,
        extra_trigger:"body.editor_enable.editor_has_snippets",
        moveTrigger:'.oe_drop_zone',
        content:_.str.sprintf(_t("Dragthe<b>%s</b>buildingblockanddropitatthebottomofthepage."),snippet.name),
        position:position,
        //Normallynomainsnippetcanbedroppedinthedefaultfooterbut
        //targetingitallowstoforce"droppingattheendofthepage".
        run:"drag_and_drop#wrapwrap>footer",
    };
}

functiongoBackToBlocks(position="bottom"){
    return{
        trigger:'.o_we_add_snippet_btn',
        content:_t("Clickheretogobacktoblocktab."),
        position:position,
        run:"click",
    };
}

functiongoToOptions(position="bottom"){
    return{
        trigger:'.o_we_customize_theme_btn',
        content:_t("GototheOptionstab"),
        position:position,
        run:"click",
    };
}

functionselectHeader(position="bottom"){
    return{
        trigger:`header#top`,
        content:_t(`<b>Click</b>onthisheadertoconfigureit.`),
        position:position,
        run:"click",
    };
}

functionselectSnippetColumn(snippet,index=0,position="bottom"){
     return{
        trigger:`#wrapwrap.${snippet.id}.rowdiv[class*="col-lg-"]:eq(${index})`,
        content:_t("<b>Click</b>onthiscolumntoaccessitsoptions."),
         position:position,
        run:"click",
     };
}

functionprepend_trigger(steps,prepend_text=''){
    for(conststepofsteps){
        if(!step.noPrepend&&prepend_text){
            step.trigger=prepend_text+step.trigger;
        }
    }
    returnsteps;
}

functionregisterThemeHomepageTour(name,steps){
    tour.register(name,{
        url:"/?enable_editor=1",
        sequence:1010,
        saveAs:"homepage",
    },prepend_trigger(
        steps,
        "html[data-view-xmlid='website.homepage']"
    ));
}


return{
    addMedia,
    changeBackground,
    changeBackgroundColor,
    changeColumnSize,
    changeIcon,
    changeImage,
    changeOption,
    changePaddingSize,
    clickOnEdit,
    clickOnEditAndWaitEditMode,
    clickOnSave,
    clickOnSnippet,
    clickOnText,
    dragNDrop,
    goBackToBlocks,
    goToOptions,
    selectColorPalette,
    selectHeader,
    selectNested,
    selectSnippetColumn,

    registerThemeHomepageTour,
};
});
