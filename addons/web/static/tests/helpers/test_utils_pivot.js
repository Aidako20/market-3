flectra.define('web.test_utils_pivot',function(require){
"usestrict";

vartestUtilsDom=require('web.test_utils_dom');

/**
 *PivotTestUtils
 *
 *Thismoduledefinesvariousutilityfunctionstohelptestpivotviews.
 *
 *Notethatallmethodsdefinedinthismoduleareexportedinthemain
 *testUtilsfile.
 */


/**
 *Selectameasurebyclickingonthecorrespondingdropdownitem(inthe
 *controlpanel'Measure'submenu).
 *
 *Notethatthismethodassumesthatthedropdownmenuisopen.
 *@seetoggleMeasuresDropdown
 *
 *@param{PivotController}pivot
 *@param{string}measure
 */
functionclickMeasure(pivot,measure){
    returntestUtilsDom.click(pivot.$buttons.find(`.dropdown-item[data-field=${measure}]`));
}

/**
 *Openthe'Measure'dropdownmenu(inthecontrolpanel)
 *
 *@seeclickMeasure
 *
 *@param{PivotController}pivot
 */
functiontoggleMeasuresDropdown(pivot){
    returntestUtilsDom.click(pivot.$buttons.filter('.btn-group:first').find('>button'));
}

/**
 *Reloadsagraphview.
 *
 *@param{PivotController}pivot
 *@param{[Object]}paramsgiventothecontrollerreloadmethod
 */
functionreload(pivot,params){
    returnpivot.reload(params);
}

return{
    clickMeasure:clickMeasure,
    reload:reload,
    toggleMeasuresDropdown:toggleMeasuresDropdown,
};

});
