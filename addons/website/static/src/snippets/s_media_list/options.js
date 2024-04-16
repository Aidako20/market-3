flectra.define('website.s_media_list_options',function(require){
'usestrict';

constoptions=require('web_editor.snippets.options');

options.registry.MediaItemLayout=options.Class.extend({

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Changethemediaitemlayout.
     *
     *@seethis.selectClassforparameters
     */
    layout:function(previewMode,widgetValue,params){
        const$image=this.$target.find('.s_media_list_img_wrapper');
        const$content=this.$target.find('.s_media_list_body');

        for(constpossibleValueofparams.possibleValues){
            $image.removeClass(`col-lg-${possibleValue}`);
            $content.removeClass(`col-lg-${12-possibleValue}`);
        }
        $image.addClass(`col-lg-${widgetValue}`);
        $content.addClass(`col-lg-${12-widgetValue}`);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _computeWidgetState(methodName,params){
        switch(methodName){
            case'layout':{
                const$image=this.$target.find('.s_media_list_img_wrapper');
                for(constpossibleValueofparams.possibleValues){
                    if($image.hasClass(`col-lg-${possibleValue}`)){
                        returnpossibleValue;
                    }
                }
            }
        }
        returnthis._super(...arguments);
    },
});
});
