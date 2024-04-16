flectra.define('website_event.event_steps',function(require){
"usestrict";

varcore=require('web.core');
var_t=core._t;

varEventAdditionalTourSteps=require('event.event_steps');

EventAdditionalTourSteps.include({

    init:function(){
        this._super.apply(this,arguments);
    },

    _get_website_event_steps:function(){
        this._super.apply(this,arguments);
        return[{
                trigger:'.o_event_form_viewbutton[name="is_published"]',
                content:_t("Usethis<b>shortcut</b>toeasilyaccessyoureventwebpage."),
                position:'bottom',
            },{
                trigger:'li#edit-page-menua',
                extra_trigger:'.o_wevent_event',
                content:_t("WiththeEditbutton,youcan<b>customize</b>thewebpagevisitorswillseewhenregistering."),
                position:'bottom',
            },{
                trigger:'div[name="Image-Text"].oe_snippet_thumbnail',
                extra_trigger:'.o_wevent_event',
                content:_t("<b>DragandDrop</b>thissnippetbelowtheeventtitle."),
                position:'bottom',
                run:'drag_and_drop#o_wevent_event_main_col',
            },{
                trigger:'button[data-action="save"]',
                extra_trigger:'.o_wevent_event',
                content:_t("Don'tforgettoclick<b>save</b>whenyou'redone."),
                position:'bottom',
            },{
                trigger:'label.js_publish_btn',
                extra_trigger:'.o_wevent_event',
                content:_t("Lookinggreat!Let'snow<b>publish</b>thispagesothatitbecomes<b>visible</b>onyourwebsite!"),
                position:'bottom',
            },{
                trigger:'a.css_edit_dynamic',
                extra_trigger:'.js_publish_management[data-object="event.event"].js_publish_btn.css_unpublish:visible',
                content:_t("Wanttochangeyoureventconfiguration?Let'sgobacktotheeventform."),
                position:'bottom',
                run:function(actions){
                    actions.click('div.dropdown-menua#edit-in-backend');
                },
            },{
                trigger:'a#edit-in-backend',
                extra_trigger:'.o_wevent_event',
                content:_t("Thisshortcutwillbringyourightbacktotheeventform."),
                position:'bottom'
            }];
    }
});

returnEventAdditionalTourSteps;

});
