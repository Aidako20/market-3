flectra.define('website.tour.public_user_editor_dep_widget',function(require){
'usestrict';

constpublicWidget=require('web.public.widget');
constwysiwygLoader=require('web_editor.loader');

publicWidget.registry['public_user_editor_test']=publicWidget.Widget.extend({
    selector:'textarea.o_public_user_editor_test_textarea',

    /**
     *@override
     */
    start:asyncfunction(){
        awaitthis._super(...arguments);
        awaitwysiwygLoader.load(this,this.el,{});
    },
});
});

flectra.define('website.tour.public_user_editor',function(require){
'usestrict';

consttour=require('web_tour.tour');

tour.register('public_user_editor',{
    test:true,
},[{
    trigger:'flectra-wysiwyg-container:has(>.o_public_user_editor_test_textarea:first-child)',
    run:function(){},//Simplecheck
}]);
});
