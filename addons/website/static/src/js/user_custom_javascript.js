//
//Thisfileismeanttoregroupyourjavascriptcode.Youcaneithercopy/past
//anycodethatshouldbeexecutedoneachpageloadingorwriteyourown
//takingadvantageoftheFlectraframeworktocreatenewbehaviorsormodify
//existingones.Forexample,doingthiswillgreetanyvisitorwitha'Hello,
//world!'messageinapopup:
//
/*
flectra.define('website.user_custom_code',function(require){
'usestrict';

varDialog=require('web.Dialog');
varpublicWidget=require('web.public.widget');

publicWidget.registry.HelloWorldPopup=publicWidget.Widget.extend({
    selector:'#wrapwrap',

    start:function(){
        Dialog.alert(this,"Hello,world!");
        returnthis._super.apply(this,arguments);
    },
})
});
*/
