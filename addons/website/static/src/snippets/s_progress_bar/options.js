flectra.define('website.s_progress_bar_options',function(require){
'usestrict';

constcore=require('web.core');
constutils=require('web.utils');
constoptions=require('web_editor.snippets.options');

const_t=core._t;

options.registry.progress=options.Class.extend({

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Changesthepositionoftheprogressbartext.
     *
     *@seethis.selectClassforparameters
     */
    display:function(previewMode,widgetValue,params){
        //retro-compatibility
        if(this.$target.hasClass('progress')){
            this.$target.removeClass('progress');
            this.$target.find('.progress-bar').wrap($('<div/>',{
                class:'progress',
            }));
            this.$target.find('.progress-barspan').addClass('s_progress_bar_text');
        }

        let$text=this.$target.find('.s_progress_bar_text');
        if(!$text.length){
            $text=$('<span/>').addClass('s_progress_bar_text').html(_t('80%Development'));
        }

        if(widgetValue==='inline'){
            $text.appendTo(this.$target.find('.progress-bar'));
        }else{
            $text.insertBefore(this.$target.find('.progress'));
        }
    },
    /**
     *Setstheprogressbarvalue.
     *
     *@seethis.selectClassforparameters
     */
    progressBarValue:function(previewMode,widgetValue,params){
        letvalue=parseInt(widgetValue);
        value=utils.confine(value,0,100);
        const$progressBar=this.$target.find('.progress-bar');
        const$progressBarText=this.$target.find('.s_progress_bar_text');
        //TargetpreciselytheXX%notonlyXXtonotreplacewrongelement
        //eg'Since1978wehavecompleted45%'<-don'treplace1978
        $progressBarText.text($progressBarText.text().replace(/[0-9]+%/,value+'%'));
        $progressBar.attr("aria-valuenow",value);
        $progressBar.css("width",value+"%");
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _computeWidgetState:function(methodName,params){
        switch(methodName){
            case'display':{
                constisInline=this.$target.find('.s_progress_bar_text')
                                        .parent('.progress-bar').length;
                returnisInline?'inline':'below';
            }
            case'progressBarValue':{
                returnthis.$target.find('.progress-bar').attr('aria-valuenow')+'%';
            }
        }
        returnthis._super(...arguments);
    },
});
});
