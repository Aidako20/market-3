flectra.define('website.s_showcase_options',function(require){
'usestrict';

constoptions=require('web_editor.snippets.options');

options.registry.Showcase=options.Class.extend({
    /**
     *@override
     */
    onMove:function(){
        const$showcaseCol=this.$target.parent().closest('.row>div');
        constisLeftCol=$showcaseCol.index()<=0;
        const$title=this.$target.children('.s_showcase_title');
        $title.toggleClass('flex-lg-row-reverse',isLeftCol);
        $showcaseCol.find('.s_showcase_icon.ml-3').removeClass('ml-3').addClass('ml-lg-3');//Forcompatibilitywitholdversion
        $title.find('.s_showcase_icon').toggleClass('mr-lg-0ml-lg-3',isLeftCol);
    },
});
});
