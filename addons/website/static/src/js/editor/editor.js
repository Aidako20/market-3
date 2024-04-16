flectra.define('website.editor',function(require){
'usestrict';

varweWidgets=require('web_editor.widget');
varwUtils=require('website.utils');

weWidgets.LinkDialog.include({
    /**
     *AllowstheURLinputtoproposeexistingwebsitepages.
     *
     *@override
     */
    start:function(){
        wUtils.autocompleteWithPages(this,this.$('input[name="url"]'));
        returnthis._super.apply(this,arguments);
    },
});
});
