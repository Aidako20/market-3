flectra.define('survey.quick.access',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.SurveyQuickAccessWidget=publicWidget.Widget.extend({
    selector:'.o_survey_quick_access',
    events:{
        'clickbutton[type="submit"]':'_onSubmit',
    },

        //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
    *@override
    */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            //Initeventlistener
            if(!self.readonly){
                $(document).on('keypress',self._onKeyPress.bind(self));
            }

            self.$('input').focus();
        });
    },

    //-------------------------------------------------------------------------
    //Private
    //-------------------------------------------------------------------------

    //Handlers
    //-------------------------------------------------------------------------

    _onKeyPress:function(event){
        if(event.keyCode===13){ //Enter
            event.preventDefault();
            this._submitCode();
        }
    },

    _onSubmit:function(event){
        event.preventDefault();
        this._submitCode();
    },

    _submitCode:function(){
        varself=this;
        this.$('.o_survey_error').addClass("d-none");
        var$sessionCodeInput=this.$('input#session_code');
        this._rpc({
            route:`/survey/check_session_code/${$sessionCodeInput.val()}`,
        }).then(function(response){
            if(response.survey_url){
                window.location=response.survey_url;
            }else{
                self.$('.o_survey_error').removeClass("d-none");
            }
        });
    },
});

returnpublicWidget.registry.SurveyQuickAccessWidget;

});
