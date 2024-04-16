flectra.define('web.test_utils_fields',function(require){
    "usestrict";

    /**
     *FieldTestUtils
     *
     *Thismoduledefinesvariousutilityfunctionstohelptestingfieldwidgets.
     *
     *Notethatallmethodsdefinedinthismoduleareexportedinthemain
     *testUtilsfile.
     */

    consttestUtilsDom=require('web.test_utils_dom');

    constARROW_KEYS_MAPPING={
        down:'ArrowDown',
        left:'ArrowLeft',
        right:'ArrowRight',
        up:'ArrowUp',
    };

    //-------------------------------------------------------------------------
    //Publicfunctions
    //-------------------------------------------------------------------------

    /**
     *Autofillstheinputofamany2onefieldandclicksonthe"CreateandEdit"option.
     *
     *@param{string}fieldName
     *@param{string}textUsedasdefaultvaluefortherecordname
     *@seeclickM2OItem
     */
    asyncfunctionclickM2OCreateAndEdit(fieldName,text="ABC"){
        awaitclickOpenM2ODropdown(fieldName);
        constmatch=document.querySelector(`.o_field_many2one[name=${fieldName}]input`);
        awaiteditInput(match,text);
        returnclickM2OItem(fieldName,"CreateandEdit");
    }

    /**
     *Clickontheactive(highlighted)selectioninam2odropdown.
     *
     *@param{string}fieldName
     *@param{[string]}selectorifset,thiswillrestrictthesearchforthem2o
     *   input
     *@returns{Promise}
     */
    asyncfunctionclickM2OHighlightedItem(fieldName,selector){
        constm2oSelector=`${selector||''}.o_field_many2one[name=${fieldName}]input`;
        const$dropdown=$(m2oSelector).autocomplete('widget');
        //clickingonanli(nomatterwhichone),willselectthefocussedone
        returntestUtilsDom.click($dropdown[0].querySelector('li'));
    }

    /**
     *Clickonamenuiteminthem2odropdown. Thishelperwilltargetanelement
     *whichcontainssomespecifictext.Notethatitassumesthatthedropdown
     *iscurrentlyopen.
     *
     *Example:
     *   testUtils.fields.many2one.clickM2OItem('partner_id','George');
     *
     *@param{string}fieldName
     *@param{string}searchText
     *@returns{Promise}
     */
    asyncfunctionclickM2OItem(fieldName,searchText){
        constm2oSelector=`.o_field_many2one[name=${fieldName}]input`;
        const$dropdown=$(m2oSelector).autocomplete('widget');
        const$target=$dropdown.find(`li:contains(${searchText})`).first();
        if($target.length!==1||!$target.is(':visible')){
            thrownewError('Menuitemshouldbevisible');
        }
        $target.mouseenter();//ThisisNOTamouseenterevent.Seejquery.js:5516formoreheadaches.
        returntestUtilsDom.click($target);
    }

    /**
     *Clicktoopenthedropdownonamany2one
     *
     *@param{string}fieldName
     *@param{[string]}selectorifset,thiswillrestrictthesearchforthem2o
     *   input
     *@returns{Promise<HTMLInputElement>}themainmany2oneinput
     */
    asyncfunctionclickOpenM2ODropdown(fieldName,selector){
        constm2oSelector=`${selector||''}.o_field_many2one[name=${fieldName}]input`;
        constmatches=document.querySelectorAll(m2oSelector);
        if(matches.length!==1){
            thrownewError(`cannotopenm2o:selector${selector}hasbeenfound${matches.length}insteadof1`);
        }

        awaittestUtilsDom.click(matches[0]);
        returnmatches[0];
    }

    /**
     *Setsthevalueofanelementandthen,triggerallspecifiedevents.
     *Notethatthishelperalsocheckstheunicityofthetarget.
     *
     *Example:
     *    testUtils.fields.editAndTrigger($('selector'),'test',['input','change']);
     *
     *@param{jQuery|EventTarget}elshouldtargetaninput,textareaorselect
     *@param{string|number}value
     *@param{string[]}events
     *@returns{Promise}
     */
    asyncfunctioneditAndTrigger(el,value,events){
        if(elinstanceofjQuery){
            if(el.length!==1){
                thrownewError(`target${el.selector}haslength${el.length}insteadof1`);
            }
            el.val(value);
        }else{
            el.value=value;
        }
        returntestUtilsDom.triggerEvents(el,events);
    }

    /**
     *Setsthevalueofaninput.
     *
     *Notethatthishelperalsocheckstheunicityofthetarget.
     *
     *Example:
     *    testUtils.fields.editInput($('selector'),'somevalue');
     *
     *@param{jQuery|EventTarget}elshouldtargetaninput,textareaorselect
     *@param{string|number}value
     *@returns{Promise}
     */
    asyncfunctioneditInput(el,value){
        returneditAndTrigger(el,value,['input']);
    }

    /**
     *Setsthevalueofaselect.
     *
     *Notethatthishelperalsocheckstheunicityofthetarget.
     *
     *Example:
     *    testUtils.fields.editSelect($('selector'),'somevalue');
     *
     *@param{jQuery|EventTarget}elshouldtargetaninput,textareaorselect
     *@param{string|number}value
     *@returns{Promise}
     */
    functioneditSelect(el,value){
        returneditAndTrigger(el,value,['change']);
    }

    /**
     *Thishelperisusefultotestmany2onefields.Hereiswhatitdoes:
     *-clicktoopenthedropdown
     *-enterasearchstringintheinput
     *-waitfortheselection
     *-clickontherequestedmenuitem,ortheactiveonebydefault
     *
     *Example:
     *   testUtils.fields.many2one.searchAndClickM2OItem('partner_id',{search:'George'});
     *
     *@param{string}fieldName
     *@param{[Object]}[options={}]
     *@param{[string]}[options.selector]
     *@param{[string]}[options.search]
     *@param{[string]}[options.item]
     *@returns{Promise}
     */
    asyncfunctionsearchAndClickM2OItem(fieldName,options={}){
        constinput=awaitclickOpenM2ODropdown(fieldName,options.selector);
        if(options.search){
            awaiteditInput(input,options.search);
        }
        if(options.item){
            returnclickM2OItem(fieldName,options.item);
        }else{
            returnclickM2OHighlightedItem(fieldName,options.selector);
        }
    }

    /**
     *Helpertotriggerakeyeventonanelement.
     *
     *@param{string}typetypeofkeyevent('press','up'or'down')
     *@param{jQuery}$el
     *@param{number|string}keyCodeusedasnumber,butifstring,it'llcheckif
     *  thestringcorrespondstoakey-otherwiseitwillkeeponlythefirst
     *  chartogetaletterkey-andconvertitintoakeyCode.
     *@returns{Promise}
     */
    functiontriggerKey(type,$el,keyCode){
        type='key'+type;
        constparams={};
        if(typeofkeyCode==='string'){
            //Key(newAPI)
            if(keyCodeinARROW_KEYS_MAPPING){
                params.key=ARROW_KEYS_MAPPING[keyCode];
            }else{
                params.key=keyCode[0].toUpperCase()+keyCode.slice(1).toLowerCase();
            }
            //KeyCode/which(jQuery)
            if(keyCode.length>1){
                keyCode=keyCode.toUpperCase();
                keyCode=$.ui.keyCode[keyCode];
            }else{
                keyCode=keyCode.charCodeAt(0);
            }
        }
        params.keyCode=keyCode;
        params.which=keyCode;
        returntestUtilsDom.triggerEvent($el,type,params);
    }

    /**
     *Helpertotriggerakeydowneventonanelement.
     *
     *@param{jQuery}$el
     *@param{number|string}keyCode@seetriggerKey
     *@returns{Promise}
     */
    functiontriggerKeydown($el,keyCode){
        returntriggerKey('down',$el,keyCode);
    }

    /**
     *Helpertotriggerakeyupeventonanelement.
     *
     *@param{jQuery}$el
     *@param{number|string}keyCode@seetriggerKey
     *@returns{Promise}
     */
    functiontriggerKeyup($el,keyCode){
        returntriggerKey('up',$el,keyCode);
    }

    return{
        clickM2OCreateAndEdit,
        clickM2OHighlightedItem,
        clickM2OItem,
        clickOpenM2ODropdown,
        editAndTrigger,
        editInput,
        editSelect,
        searchAndClickM2OItem,
        triggerKey,
        triggerKeydown,
        triggerKeyup,
    };
});
