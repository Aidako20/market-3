flectra.define('survey.print',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
vardom=require('web.dom');

publicWidget.registry.SurveyPrintWidget=publicWidget.Widget.extend({
    selector:'.o_survey_print',

    //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
    *@override
    */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            //Willallowthetextareatoresizeifanycarriagereturninsteadofshowingscrollbar.
            self.$('textarea').each(function(){
                dom.autoresize($(this));
            });
        });
    },

});

returnpublicWidget.registry.SurveyPrintWidget;

});
