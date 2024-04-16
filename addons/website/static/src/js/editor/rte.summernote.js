flectra.define('website.rte.summernote',function(require){
'usestrict';

varcore=require('web.core');
constrte=require('web_editor.rte');
require('web_editor.rte.summernote');

vareventHandler=$.summernote.eventHandler;
varrenderer=$.summernote.renderer;
vartplIconButton=renderer.getTemplate().iconButton;
var_t=core._t;

varfn_tplPopovers=renderer.tplPopovers;
renderer.tplPopovers=function(lang,options){
    var$popover=$(fn_tplPopovers.call(this,lang,options));
    $popover.find('.note-image-popover.btn-group:has([data-value="img-thumbnail"])').append(
        tplIconButton('fafa-object-ungroup',{
            title:_t('Transformthepicture(clicktwicetoresettransformation)'),
            event:'transform',
        }));
    return$popover;
};

$.summernote.pluginEvents.transform=function(event,editor,layoutInfo,sorted){
    var$selection=layoutInfo.handle().find('.note-control-selection');
    var$image=$($selection.data('target'));

    if($image.data('transfo-destroy')){
        $image.removeData('transfo-destroy');
        return;
    }

    $image.transfo();

    varmouseup=function(event){
        $('.note-popoverbutton[data-event="transform"]').toggleClass('active',$image.is('[style*="transform"]'));
    };
    $(document).on('mouseup',mouseup);

    varmousedown=function(event){
        if(!$(event.target).closest('.transfo-container').length){
            $image.transfo('destroy');
            $(document).off('mousedown',mousedown).off('mouseup',mouseup);
        }
        if($(event.target).closest('.note-popover').length){
            $image.data('transfo-destroy',true).attr('style',($image.attr('style')||'').replace(/[^;]*transform[\w:]*;?/g,''));
        }
        $image.trigger('content_changed');
    };
    $(document).on('mousedown',mousedown);
};

varfn_boutton_update=eventHandler.modules.popover.button.update;
eventHandler.modules.popover.button.update=function($container,oStyle){
    fn_boutton_update.call(this,$container,oStyle);
    $container.find('button[data-event="transform"]')
        .toggleClass('active',$(oStyle.image).is('[style*="transform"]'))
        .toggleClass('d-none',!$(oStyle.image).is('img'));
};

rte.Class.include({
    /**
     *@override
     */
    asyncstart(){
        constres=awaitthis._super(...arguments);

        //TODOreviewinmaster.Thisstablefixrestoresthepossibilityto
        //editthecompanyteamsnippetimagesonsubsequenteditions.Indeed
        //thisbadlyreliesonthecontenteditable="true"attributebeingon
        //thoseimagesbutitisrightfullylostafterthefirstsave.
        //grep:COMPANY_TEAM_CONTENTEDITABLE
        this.__$editable.find('.s_company_team.o_not_editableimg').prop('contenteditable',true);

        returnres;
    },
});
});
