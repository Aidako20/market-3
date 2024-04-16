flectra.define('web.test_utils_form',function(require){
"usestrict";

/**
 *FormTestUtils
 *
 *Thismoduledefinesvariousutilityfunctionstohelptestformviews.
 *
 *Notethatallmethodsdefinedinthismoduleareexportedinthemain
 *testUtilsfile.
 */

vartestUtilsDom=require('web.test_utils_dom');

/**
 *ClicksontheEditbuttoninaformview,tosetittoeditmode.Notethat
 *itchecksthatthebuttonisvisible,socallingthismethodineditmode
 *willfail.
 *
 *@param{FormController}form
 */
functionclickEdit(form){
    returntestUtilsDom.click(form.$buttons.find('.o_form_button_edit'));
}

/**
 *ClicksontheSavebuttoninaformview.Notethatthismethodchecksthat
 *theSavebuttonisvisible.
 *
 *@param{FormController}form
 */
functionclickSave(form){
    returntestUtilsDom.click(form.$buttons.find('.o_form_button_save'));
}

/**
 *ClicksontheCreatebuttoninaformview.Notethatthismethodchecksthat
 *theCreatebuttonisvisible.
 *
 *@param{FormController}form
 */
functionclickCreate(form){
    returntestUtilsDom.click(form.$buttons.find('.o_form_button_create'));
}

/**
 *ClicksontheDiscardbuttoninaformview.Notethatthismethodchecksthat
 *theDiscardbuttonisvisible.
 *
 *@param{FormController}form
 */
functionclickDiscard(form){
    returntestUtilsDom.click(form.$buttons.find('.o_form_button_cancel'));
}

/**
 *Reloadsaformview.
 *
 *@param{FormController}form
 *@param{[Object]}paramsgiventothecontrollerreloadmethod
 */
functionreload(form,params){
    returnform.reload(params);
}

return{
    clickEdit:clickEdit,
    clickSave:clickSave,
    clickCreate:clickCreate,
    clickDiscard:clickDiscard,
    reload:reload,
};

});
