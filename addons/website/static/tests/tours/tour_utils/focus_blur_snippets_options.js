flectra.define('website.tour_focus_blur_snippets_options',function(require){
'usestrict';

constoptions=require('web_editor.snippets.options');

constFocusBlur=options.Class.extend({
    onFocus(){
        window.focusBlurSnippetsResult.push(`focus${this.focusBlurName}`);
    },
    onBlur(){
        window.focusBlurSnippetsResult.push(`blur${this.focusBlurName}`);
    },
});

options.registry.FocusBlurParent=FocusBlur.extend({focusBlurName:'parent'});
options.registry.FocusBlurChild1=FocusBlur.extend({focusBlurName:'child1'});
options.registry.FocusBlurChild2=FocusBlur.extend({focusBlurName:'child2'});

});
