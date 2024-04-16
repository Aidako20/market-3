flectra.define('web.test_utils_modal',function(require){
    "usestrict";

    /**
     *ModalTestUtils
     *
     *Thismoduledefinesvariousutilityfunctionstohelptestpivotviews.
     *
     *Notethatallmethodsdefinedinthismoduleareexportedinthemain
     *testUtilsfile.
     */

    const{_t}=require('web.core');
    consttestUtilsDom=require('web.test_utils_dom');

    /**
     *Clickonabuttoninthefooterofamodal(whichcontainsagivenstring).
     *
     *@param{string}text(inenglish:thismethodwillperformthetranslation)
     */
    functionclickButton(text){
        returntestUtilsDom.click($(`.modal-footerbutton:contains(${_t(text)})`));
    }

    return{clickButton};
});
