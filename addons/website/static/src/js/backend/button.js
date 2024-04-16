flectra.define('website.backend.button',function(require){
'usestrict';

varAbstractField=require('web.AbstractField');
varcore=require('web.core');
varfield_registry=require('web.field_registry');

var_t=core._t;

varWebsitePublishButton=AbstractField.extend({
    className:'o_stat_info',
    supportedFieldTypes:['boolean'],

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Abooleanfieldisalwayssetsincefalseisavalidvalue.
     *
     *@override
     */
    isSet:function(){
        returntrue;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Thiswidgetissupposedtobeusedinsideastatbuttonand,assuch,is
     *renderedthesamewayineditandreadonlymode.
     *
     *@override
     *@private
     */
    _render:function(){
        this.$el.empty();
        vartext=this.value?_t("Published"):_t("Unpublished");
        varhover=this.value?_t("Unpublish"):_t("Publish");
        varvalColor=this.value?'text-success':'text-danger';
        varhoverColor=this.value?'text-danger':'text-success';
        var$val=$('<span>').addClass('o_stat_texto_not_hover'+valColor).text(text);
        var$hover=$('<span>').addClass('o_stat_texto_hover'+hoverColor).text(hover);
        this.$el.append($val).append($hover);
    },
});

varWidgetWebsiteButtonIcon=AbstractField.extend({
    template:'WidgetWebsiteButtonIcon',
    events:{
        'click':'_onClick',
    },

    /**
    *@override
    */
    start:function(){
        this.$icon=this.$('.o_button_icon');
        returnthis._super.apply(this,arguments);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    isSet:function(){
        returntrue;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    _render:function(){
        this._super.apply(this,arguments);

        varpublished=this.value;
        varinfo=published?_t("Published"):_t("Unpublished");
        this.$el.attr('aria-label',info)
                .prop('title',info);
        this.$icon.toggleClass('text-danger',!published)
                .toggleClass('text-success',published);
    },

    //--------------------------------------------------------------------------
    //Handler
    //--------------------------------------------------------------------------

    /**
     *Redirectstothewebsitepageoftherecord.
     *
     *@private
     */
    _onClick:function(){
        this.trigger_up('button_clicked',{
            attrs:{
                type:'object',
                name:'open_website_url',
            },
            record:this.record,
        });
    },
});

field_registry
    .add('website_redirect_button',WidgetWebsiteButtonIcon)
    .add('website_publish_button',WebsitePublishButton);
});
