/**
 *ThisfileallowsintroducingnewJSmoduleswithoutcontaminatingotherfiles.
 *ThisisusefulwhenbugfixingrequiresaddingsuchJSmodulesinstable
 *versionsofFlectra.Anymodulethatisdefinedinthisfileshouldbeisolated
 *initsownfileinmaster.
 */
flectra.define('website_livechat/static/src/bugfix/bugfix.js',function(require){
'usestrict';

const{LivechatButton}=require('im_livechat.legacy.im_livechat.im_livechat');

LivechatButton.include({
    className:`${LivechatButton.prototype.className}o_bottom_fixed_element`,

    /**
     *@override
     */
    start(){
        //Wetriggeraresizetolaunchtheeventthatchecksifthiselementhides
        //abuttonwhenthepageisloaded.
        $(window).trigger('resize');
        returnthis._super(...arguments);
    },
});
});
