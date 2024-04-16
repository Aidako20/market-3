flectra.define('website.s_countdown_options',function(require){
'usestrict';

constcore=require('web.core');
constoptions=require('web_editor.snippets.options');
constCountdownWidget=require('website.s_countdown');

constqweb=core.qweb;

options.registry.countdown=options.Class.extend({
    events:_.extend({},options.Class.prototype.events||{},{
        'click.toggle-edit-message':'_onToggleEndMessageClick',
    }),

    /**
     *Removeanypreviewclasses,ifpresent.
     *
     *@override
     */
    cleanForSave:asyncfunction(){
        this.$target.find('.s_countdown_canvas_wrapper').removeClass("s_countdown_none");
        this.$target.find('.s_countdown_end_message').removeClass("s_countdown_enable_preview");
    },

    //--------------------------------------------------------------------------
    //Options
    //--------------------------------------------------------------------------

    /**
     *Changesthecountdownactionatzero.
     *
     *@seethis.selectClassforparameters
     */
    endAction:function(previewMode,widgetValue,params){
        this.$target[0].dataset.endAction=widgetValue;
        if(widgetValue==='message'){
            if(!this.$target.find('.s_countdown_end_message').length){
                constmessage=this.endMessage||qweb.render('website.s_countdown.end_message');
                this.$target.append(message);
            }
        }else{
            const$message=this.$target.find('.s_countdown_end_message').detach();
            if(this.showEndMessage){
                this._onToggleEndMessageClick();
            }
            if($message.length){
                this.endMessage=$message[0].outerHTML;
            }
        }
    },
    /**
    *Changesthecountdownstyle.
    *
    *@seethis.selectClassforparameters
    */
    layout:function(previewMode,widgetValue,params){
        switch(widgetValue){
            case'circle':
                this.$target[0].dataset.progressBarStyle='disappear';
                this.$target[0].dataset.progressBarWeight='thin';
                this.$target[0].dataset.layoutBackground='none';
                break;
            case'boxes':
                this.$target[0].dataset.progressBarStyle='none';
                this.$target[0].dataset.layoutBackground='plain';
                break;
            case'clean':
                this.$target[0].dataset.progressBarStyle='none';
                this.$target[0].dataset.layoutBackground='none';
                break;
            case'text':
                this.$target[0].dataset.progressBarStyle='none';
                this.$target[0].dataset.layoutBackground='none';
                break;
        }
        this.$target[0].dataset.layout=widgetValue;
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    updateUIVisibility:asyncfunction(){
        awaitthis._super(...arguments);
        constdataset=this.$target[0].dataset;

        //EndActionUI
        this.$el.find('.toggle-edit-message')
            .toggleClass('d-none',dataset.endAction!=='message');

        //EndMessageUI
        this.updateUIEndMessage();
    },
    /**
     *@seethis.updateUI
     */
    updateUIEndMessage:function(){
        this.$target.find('.s_countdown_canvas_wrapper')
            .toggleClass("s_countdown_none",this.showEndMessage===true&&this.$target.hasClass("hide-countdown"));
        this.$target.find('.s_countdown_end_message')
            .toggleClass("s_countdown_enable_preview",this.showEndMessage===true);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _computeWidgetState:function(methodName,params){
        switch(methodName){
            case'endAction':
            case'layout':
                returnthis.$target[0].dataset[methodName];

            case'selectDataAttribute':{
                if(params.colorNames){
                    //Inthiscase,itisacolorpickercontrollingadata
                    //valueonthecountdown:thedefaultvalueisdetermined
                    //bythecountdownpublicwidget.
                    params.attributeDefaultValue=CountdownWidget.prototype.defaultColor;
                }
                break;
            }
        }
        returnthis._super(...arguments);
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _onToggleEndMessageClick:function(){
        this.showEndMessage=!this.showEndMessage;
        this.$el.find(".toggle-edit-message")
            .toggleClass('text-primary',this.showEndMessage);
        this.updateUIEndMessage();
        this.trigger_up('cover_update');
    },
});
});
