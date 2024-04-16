flectra.define('website.s_timeline_options',function(require){
'usestrict';

constoptions=require('web_editor.snippets.options');

options.registry.Timeline=options.Class.extend({
    /**
     *@override
     */
    start:function(){
        var$buttons=this.$el.find('we-button');
        var$overlayArea=this.$overlay.find('.o_overlay_options_wrap');
        $overlayArea.append($('<div/>').append($buttons));

        returnthis._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Movesthecardtotheright/left.
     *
     *@seethis.selectClassforparameters
     */
    timelineCard:function(previewMode,widgetValue,params){
        const$timelineRow=this.$target.closest('.s_timeline_row');
        $timelineRow.toggleClass('flex-row-reverseflex-row');
    },
});
});
