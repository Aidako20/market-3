flectra.define('web.test_utils_kanban',function(require){
"usestrict";

/**
 *KanbanTestUtils
 *
 *Thismoduledefinesvariousutilityfunctionstohelptestingkanbanviews.
 *
 *Notethatallmethodsdefinedinthismoduleareexportedinthemain
 *testUtilsfile.
 */

vartestUtilsDom=require('web.test_utils_dom');
vartestUtilsFields=require('web.test_utils_fields');

/**
 *ClicksontheCreatebuttoninakanbanview.Notethatthismethodchecksthat
 *theCreatebuttonisvisible.
 *
 *@param{KanbanController}kanban
 *@returns{Promise}
 */
functionclickCreate(kanban){
    returntestUtilsDom.click(kanban.$buttons.find('.o-kanban-button-new'));
}

/**
 *Openthesettingsmenuforacolumn(inagroupedkanbanview)
 *
 *@param{jQuery}$column
 *@returns{Promise}
 */
functiontoggleGroupSettings($column){
    var$dropdownToggler=$column.find('.o_kanban_config>a.dropdown-toggle');
    if(!$dropdownToggler.is(':visible')){
        $dropdownToggler.css('display','block');
    }
    returntestUtilsDom.click($dropdownToggler);
}

/**
 *Editavalueinaquickcreateformview(thismethodassumesthatthequick
 *createfeatureisactive,andasubformviewisopen)
 *
 *@param{kanbanController}kanban
 *@param{string|number}value
 *@param{[string]}fieldName
 *@returns{Promise}
 */
functionquickCreate(kanban,value,fieldName){
    varadditionalSelector=fieldName?('[name='+fieldName+']'):'';
    varenterEvent=$.Event(
        'keydown',
        {
            which:$.ui.keyCode.ENTER,
            keyCode:$.ui.keyCode.ENTER,
        }
    );
    returntestUtilsFields.editAndTrigger(
        kanban.$('.o_kanban_quick_createinput'+additionalSelector),
        value,
        ['input',enterEvent]
    );
}

/**
 *Reloadsakanbanview.
 *
 *@param{KanbanController}kanban
 *@param{[Object]}paramsgiventothecontrollerreloadmethod
 *@returns{Promise}
 */
functionreload(kanban,params){
    returnkanban.reload(params);
}

/**
 *Openthesettingdropdownofakanbanrecord. Notethatthetemplateofa
 *kanbanrecordisnotstandardized,sothismethodwillfailifthetemplate
 *doesnotcomplywiththeusualdomstructure.
 *
 *@param{jQuery}$record
 *@returns{Promise}
 */
functiontoggleRecordDropdown($record){
    var$dropdownToggler=$record.find('.o_dropdown_kanban>a.dropdown-toggle');
    if(!$dropdownToggler.is(':visible')){
        $dropdownToggler.css('display','block');
    }
    returntestUtilsDom.click($dropdownToggler);
}


return{
    clickCreate:clickCreate,
    quickCreate:quickCreate,
    reload:reload,
    toggleGroupSettings:toggleGroupSettings,
    toggleRecordDropdown:toggleRecordDropdown,
};

});
