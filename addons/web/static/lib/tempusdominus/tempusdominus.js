/*@preserve
 *TempusDominusBootstrap4v5.0.1(https://tempusdominus.github.io/bootstrap-4/)
 *Copyright2016-2018JonathanPeterson
 *LicensedunderMIT(https://github.com/tempusdominus/bootstrap-3/blob/master/LICENSE)
 */

if(typeofjQuery==='undefined'){
  thrownewError('TempusDominusBootstrap4\'srequiresjQuery.jQuerymustbeincludedbeforeTempusDominusBootstrap4\'sJavaScript.');
}

+function($){
  varversion=$.fn.jquery.split('')[0].split('.');
  if((version[0]<2&&version[1]<9)||(version[0]===1&&version[1]===9&&version[2]<1)||(version[0]>=4)){
    thrownewError('TempusDominusBootstrap4\'srequiresatleastjQueryv3.0.0butlessthanv4.0.0');
  }
}(jQuery);


if(typeofmoment==='undefined'){
  thrownewError('TempusDominusBootstrap4\'srequiresmoment.js.Moment.jsmustbeincludedbeforeTempusDominusBootstrap4\'sJavaScript.');
}

varversion=moment.version.split('.')
if((version[0]<=2&&version[1]<17)||(version[0]>=3)){
  thrownewError('TempusDominusBootstrap4\'srequiresatleastmoment.jsv2.17.0butlessthanv3.0.0');
}

+function(){

var_typeof=typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"?function(obj){returntypeofobj;}:function(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};

var_createClass=function(){functiondefineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}returnfunction(Constructor,protoProps,staticProps){if(protoProps)defineProperties(Constructor.prototype,protoProps);if(staticProps)defineProperties(Constructor,staticProps);returnConstructor;};}();

function_possibleConstructorReturn(self,call){if(!self){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returncall&&(typeofcall==="object"||typeofcall==="function")?call:self;}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction,not"+typeofsuperClass);}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,enumerable:false,writable:true,configurable:true}});if(superClass)Object.setPrototypeOf?Object.setPrototypeOf(subClass,superClass):subClass.__proto__=superClass;}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

//ReSharperdisableonceInconsistentNaming
varDateTimePicker=function($,moment){
    //ReSharperdisableInconsistentNaming
    varNAME='datetimepicker',
        DATA_KEY=''+NAME,
        EVENT_KEY='.'+DATA_KEY,
        DATA_API_KEY='.data-api',
        Selector={
        ///!\FLECTRAPATCH:ensurethedatetimepickerscanbetoggledonlyafter
        //theFlectralazyloaderfinishedloadingalllazyscripts.Another
        //solutioncouldhavebeentotemporarilyremovingthedata-toggle
        //attributesduringlazyloadingbutthatwouldnothavebeenstableas
        //customcodecouldsearchfordata-toggleelementswhilethelazy
        //loadingisbeingperformed.Withoutthis,clickingtoosoonona
        //datetimepickerwouldnotusetherightformatandUIoptions.
        DATA_TOGGLE:'body:not(.o_lazy_js_waiting)[data-toggle="'+DATA_KEY+'"]'
    },
        ClassName={
        INPUT:NAME+'-input'
    },
        Event={
        CHANGE:'change'+EVENT_KEY,
        BLUR:'blur'+EVENT_KEY,
        KEYUP:'keyup'+EVENT_KEY,
        KEYDOWN:'keydown'+EVENT_KEY,
        FOCUS:'focus'+EVENT_KEY,
        CLICK_DATA_API:'click'+EVENT_KEY+DATA_API_KEY,
        //emitted
        UPDATE:'update'+EVENT_KEY,
        ERROR:'error'+EVENT_KEY,
        HIDE:'hide'+EVENT_KEY,
        SHOW:'show'+EVENT_KEY
    },
        DatePickerModes=[{
        CLASS_NAME:'days',
        NAV_FUNCTION:'M',
        NAV_STEP:1
    },{
        CLASS_NAME:'months',
        NAV_FUNCTION:'y',
        NAV_STEP:1
    },{
        CLASS_NAME:'years',
        NAV_FUNCTION:'y',
        NAV_STEP:10
    },{
        CLASS_NAME:'decades',
        NAV_FUNCTION:'y',
        NAV_STEP:100
    }],
        KeyMap={
        'up':38,
        38:'up',
        'down':40,
        40:'down',
        'left':37,
        37:'left',
        'right':39,
        39:'right',
        'tab':9,
        9:'tab',
        'escape':27,
        27:'escape',
        'enter':13,
        13:'enter',
        'pageUp':33,
        33:'pageUp',
        'pageDown':34,
        34:'pageDown',
        'shift':16,
        16:'shift',
        'control':17,
        17:'control',
        'space':32,
        32:'space',
        't':84,
        84:'t',
        'delete':46,
        46:'delete'
    },
        ViewModes=['times','days','months','years','decades'],
        keyState={},
        keyPressHandled={};

    varMinViewModeNumber=0,
        Default={
        timeZone:'',
        format:false,
        dayViewHeaderFormat:'MMMMYYYY',
        extraFormats:false,
        stepping:1,
        minDate:false,
        maxDate:false,
        useCurrent:true,
        collapse:true,
        locale:moment.locale(),
        defaultDate:false,
        disabledDates:false,
        enabledDates:false,
        icons:{
            time:'fafa-clock-o',
            date:'fafa-calendar',
            up:'fafa-arrow-up',
            down:'fafa-arrow-down',
            previous:'fafa-chevron-left',
            next:'fafa-chevron-right',
            today:'fafa-calendar-check-o',
            clear:'fafa-trash',
            close:'fafa-times'
        },
        tooltips:{
            today:'Gototoday',
            clear:'Clearselection',
            close:'Closethepicker',
            selectMonth:'SelectMonth',
            prevMonth:'PreviousMonth',
            nextMonth:'NextMonth',
            selectYear:'SelectYear',
            prevYear:'PreviousYear',
            nextYear:'NextYear',
            selectDecade:'SelectDecade',
            prevDecade:'PreviousDecade',
            nextDecade:'NextDecade',
            prevCentury:'PreviousCentury',
            nextCentury:'NextCentury',
            pickHour:'PickHour',
            incrementHour:'IncrementHour',
            decrementHour:'DecrementHour',
            pickMinute:'PickMinute',
            incrementMinute:'IncrementMinute',
            decrementMinute:'DecrementMinute',
            pickSecond:'PickSecond',
            incrementSecond:'IncrementSecond',
            decrementSecond:'DecrementSecond',
            togglePeriod:'TogglePeriod',
            selectTime:'SelectTime',
            selectDate:'SelectDate'
        },
        useStrict:false,
        sideBySide:false,
        daysOfWeekDisabled:false,
        calendarWeeks:false,
        viewMode:'days',
        toolbarPlacement:'default',
        buttons:{
            showToday:false,
            showClear:false,
            showClose:false
        },
        widgetPositioning:{
            horizontal:'auto',
            vertical:'auto'
        },
        widgetParent:null,
        ignoreReadonly:false,
        keepOpen:false,
        focusOnShow:true,
        inline:false,
        keepInvalid:false,
        keyBinds:{
            up:functionup(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().subtract(7,'d'));
                }else{
                    this.date(d.clone().add(this.stepping(),'m'));
                }
                returntrue;
            },
            down:functiondown(){
                if(!this.widget){
                    this.show();
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().add(7,'d'));
                }else{
                    this.date(d.clone().subtract(this.stepping(),'m'));
                }
                returntrue;
            },
            'controlup':functioncontrolUp(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().subtract(1,'y'));
                }else{
                    this.date(d.clone().add(1,'h'));
                }
                returntrue;
            },
            'controldown':functioncontrolDown(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().add(1,'y'));
                }else{
                    this.date(d.clone().subtract(1,'h'));
                }
                returntrue;
            },
            left:functionleft(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().subtract(1,'d'));
                }
                returntrue;
            },
            right:functionright(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().add(1,'d'));
                }
                returntrue;
            },
            pageUp:functionpageUp(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().subtract(1,'M'));
                }
                returntrue;
            },
            pageDown:functionpageDown(){
                if(!this.widget){
                    returnfalse;
                }
                vard=this._dates[0]||this.getMoment();
                if(this.widget.find('.datepicker').is(':visible')){
                    this.date(d.clone().add(1,'M'));
                }
                returntrue;
            },
            enter:functionenter(){
                if(!this.widget){
                    returnfalse;
                }
                this.hide();
                returntrue;
            },
            escape:functionescape(){
                if(!this.widget){
                    returnfalse;
                }
                this.hide();
                returntrue;
            },
            'controlspace':functioncontrolSpace(){
                if(!this.widget){
                    returnfalse;
                }
                if(this.widget.find('.timepicker').is(':visible')){
                    this.widget.find('.btn[data-action="togglePeriod"]').click();
                }
                returntrue;
            },
            t:functiont(){
                if(!this.widget){
                    returnfalse;
                }
                this.date(this.getMoment());
                returntrue;
            },
            'delete':function_delete(){
                if(!this.widget){
                    returnfalse;
                }
                this.clear();
                returntrue;
            }
        },
        debug:false,
        allowInputToggle:false,
        disabledTimeIntervals:false,
        disabledHours:false,
        enabledHours:false,
        viewDate:false,
        allowMultidate:false,
        multidateSeparator:','
    };

    //ReSharperrestoreInconsistentNaming

    //ReSharperdisableonceDeclarationHides
    //ReSharperdisableonceInconsistentNaming

    varDateTimePicker=function(){
        /**@namespaceeData.dateOptions*/
        /**@namespacemoment.tz*/

        functionDateTimePicker(element,options){
            _classCallCheck(this,DateTimePicker);

            this._options=this._getOptions(options);
            this._element=element;
            this._dates=[];
            this._datesFormatted=[];
            this._viewDate=null;
            this.unset=true;
            this.component=false;
            this.widget=false;
            this.use24Hours=null;
            this.actualFormat=null;
            this.parseFormats=null;
            this.currentViewMode=null;

            this._int();
        }

        /**
         *@return{string}
         */


        //private

        DateTimePicker.prototype._int=function_int(){
            vartargetInput=this._element.data('target-input');
            if(this._element.is('input')){
                this.input=this._element;
            }elseif(targetInput!==undefined){
                if(targetInput==='nearest'){
                    this.input=this._element.find('input');
                }else{
                    this.input=$(targetInput);
                }
            }

            this._dates=[];
            this._dates[0]=this.getMoment();
            this._viewDate=this.getMoment().clone();

            $.extend(true,this._options,this._dataToOptions());

            this.options(this._options);

            this._initFormatting();

            if(this.input!==undefined&&this.input.is('input')&&this.input.val().trim().length!==0){
                this._setValue(this._parseInputDate(this.input.val().trim()),0);
            }elseif(this._options.defaultDate&&this.input!==undefined&&this.input.attr('placeholder')===undefined){
                this._setValue(this._options.defaultDate,0);
            }
            if(this._options.inline){
                this.show();
            }
        };

        DateTimePicker.prototype._update=function_update(){
            if(!this.widget){
                return;
            }
            this._fillDate();
            this._fillTime();
        };

        DateTimePicker.prototype._setValue=function_setValue(targetMoment,index){
            varoldDate=this.unset?null:this._dates[index];
            varoutpValue='';
            //caseofcallingsetValue(nullorfalse)
            if(!targetMoment){
                if(!this._options.allowMultidate||this._dates.length===1){
                    this.unset=true;
                    this._dates=[];
                    this._datesFormatted=[];
                }else{
                    outpValue=this._element.data('date')+',';
                    outpValue=outpValue.replace(oldDate.format(this.actualFormat)+',','').replace(',,','').replace(/,\s*$/,'');
                    this._dates.splice(index,1);
                    this._datesFormatted.splice(index,1);
                }
                if(this.input!==undefined){
                    this.input.val(outpValue);
                    this.input.trigger('input');
                }
                this._element.data('date',outpValue);
                this._notifyEvent({
                    type:DateTimePicker.Event.CHANGE,
                    date:false,
                    oldDate:oldDate
                });
                this._update();
                return;
            }

            targetMoment=targetMoment.clone().locale(this._options.locale);

            if(this._hasTimeZone()){
                targetMoment.tz(this._options.timeZone);
            }

            if(this._options.stepping!==1){
                targetMoment.minutes(Math.round(targetMoment.minutes()/this._options.stepping)*this._options.stepping).seconds(0);
            }

            if(this._isValid(targetMoment)){
                this._dates[index]=targetMoment;
                this._datesFormatted[index]=targetMoment.format('YYYY-MM-DD');
                this._viewDate=targetMoment.clone();
                if(this._options.allowMultidate&&this._dates.length>1){
                    for(vari=0;i<this._dates.length;i++){
                        outpValue+=''+this._dates[i].format(this.actualFormat)+this._options.multidateSeparator;
                    }
                    outpValue=outpValue.replace(/,\s*$/,'');
                }else{
                    outpValue=this._dates[index].format(this.actualFormat);
                }
                if(this.input!==undefined){
                    this.input.val(outpValue);
                    this.input.trigger('input');
                }
                this._element.data('date',outpValue);

                this.unset=false;
                this._update();
                this._notifyEvent({
                    type:DateTimePicker.Event.CHANGE,
                    date:this._dates[index].clone(),
                    oldDate:oldDate
                });
            }else{
                if(!this._options.keepInvalid){
                    if(this.input!==undefined){
                        this.input.val(''+(this.unset?'':this._dates[index].format(this.actualFormat)));
                        this.input.trigger('input');
                    }
                }else{
                    this._notifyEvent({
                        type:DateTimePicker.Event.CHANGE,
                        date:targetMoment,
                        oldDate:oldDate
                    });
                }
                this._notifyEvent({
                    type:DateTimePicker.Event.ERROR,
                    date:targetMoment,
                    oldDate:oldDate
                });
            }
        };

        DateTimePicker.prototype._change=function_change(e){
            varval=$(e.target).val().trim(),
                parsedDate=val?this._parseInputDate(val):null;
            this._setValue(parsedDate,0);//FlectraFIX:ifavaliddateisreplacedbyaninvalidone,libwillcrash,seehttps://github.com/tempusdominus/bootstrap-4/issues/223
            e.stopImmediatePropagation();
            returnfalse;
        };

        //noinspectionJSMethodCanBeStatic


        DateTimePicker.prototype._getOptions=function_getOptions(options){
            options=$.extend(true,{},Default,options);
            returnoptions;
        };

        DateTimePicker.prototype._hasTimeZone=function_hasTimeZone(){
            returnmoment.tz!==undefined&&this._options.timeZone!==undefined&&this._options.timeZone!==null&&this._options.timeZone!=='';
        };

        DateTimePicker.prototype._isEnabled=function_isEnabled(granularity){
            if(typeofgranularity!=='string'||granularity.length>1){
                thrownewTypeError('isEnabledexpectsasinglecharacterstringparameter');
            }
            switch(granularity){
                case'y':
                    returnthis.actualFormat.indexOf('Y')!==-1;
                case'M':
                    returnthis.actualFormat.indexOf('M')!==-1;
                case'd':
                    returnthis.actualFormat.toLowerCase().indexOf('d')!==-1;
                case'h':
                case'H':
                    returnthis.actualFormat.toLowerCase().indexOf('h')!==-1;
                case'm':
                    returnthis.actualFormat.indexOf('m')!==-1;
                case's':
                    returnthis.actualFormat.indexOf('s')!==-1;
                case'a':
                case'A':
                    returnthis.actualFormat.toLowerCase().indexOf('a')!==-1;
                default:
                    returnfalse;
            }
        };

        DateTimePicker.prototype._hasTime=function_hasTime(){
            returnthis._isEnabled('h')||this._isEnabled('m')||this._isEnabled('s');
        };

        DateTimePicker.prototype._hasDate=function_hasDate(){
            returnthis._isEnabled('y')||this._isEnabled('M')||this._isEnabled('d');
        };

        DateTimePicker.prototype._dataToOptions=function_dataToOptions(){
            vareData=this._element.data();
            vardataOptions={};

            if(eData.dateOptions&&eData.dateOptionsinstanceofObject){
                dataOptions=$.extend(true,dataOptions,eData.dateOptions);
            }

            $.each(this._options,function(key){
                varattributeName='date'+key.charAt(0).toUpperCase()+key.slice(1);//tododataapikey
                if(eData[attributeName]!==undefined){
                    dataOptions[key]=eData[attributeName];
                }else{
                    deletedataOptions[key];
                }
            });
            returndataOptions;
        };

        DateTimePicker.prototype._notifyEvent=function_notifyEvent(e){
            ///!\FLECTRAFIX:thesenextconditionshavebeenmodifiedbyflectra
            //FIXMEshouldwriteatestaboutthetrickycasethishandles
            if(e.type===DateTimePicker.Event.CHANGE){
                if(!e.date&&!e.oldDate){
                    return;
                }
                //check_isUTCflagtoensurethatwearenotcomparingapplesandoranges
                varbothUTC=e.date&&e.oldDate&&e.date._isUTC===e.oldDate._isUTC;
                if(bothUTC&&e.date.isSame(e.oldDate)){
                    return;
                }
            }
            this._element.trigger(e);
        };

        DateTimePicker.prototype._viewUpdate=function_viewUpdate(e){
            if(e==='y'){
                e='YYYY';
            }
            this._notifyEvent({
                type:DateTimePicker.Event.UPDATE,
                change:e,
                viewDate:this._viewDate.clone()
            });
        };

        DateTimePicker.prototype._showMode=function_showMode(dir){
            if(!this.widget){
                return;
            }
            if(dir){
                this.currentViewMode=Math.max(MinViewModeNumber,Math.min(3,this.currentViewMode+dir));
            }
            this.widget.find('.datepicker>div').hide().filter('.datepicker-'+DatePickerModes[this.currentViewMode].CLASS_NAME).show();
        };

        DateTimePicker.prototype._isInDisabledDates=function_isInDisabledDates(testDate){
            returnthis._options.disabledDates[testDate.format('YYYY-MM-DD')]===true;
        };

        DateTimePicker.prototype._isInEnabledDates=function_isInEnabledDates(testDate){
            returnthis._options.enabledDates[testDate.format('YYYY-MM-DD')]===true;
        };

        DateTimePicker.prototype._isInDisabledHours=function_isInDisabledHours(testDate){
            returnthis._options.disabledHours[testDate.format('H')]===true;
        };

        DateTimePicker.prototype._isInEnabledHours=function_isInEnabledHours(testDate){
            returnthis._options.enabledHours[testDate.format('H')]===true;
        };

        DateTimePicker.prototype._isValid=function_isValid(targetMoment,granularity){
            if(!targetMoment.isValid()){
                returnfalse;
            }
            if(this._options.disabledDates&&granularity==='d'&&this._isInDisabledDates(targetMoment)){
                returnfalse;
            }
            if(this._options.enabledDates&&granularity==='d'&&!this._isInEnabledDates(targetMoment)){
                returnfalse;
            }
            if(this._options.minDate&&targetMoment.isBefore(this._options.minDate,granularity)){
                returnfalse;
            }
            if(this._options.maxDate&&targetMoment.isAfter(this._options.maxDate,granularity)){
                returnfalse;
            }
            if(this._options.daysOfWeekDisabled&&granularity==='d'&&this._options.daysOfWeekDisabled.indexOf(targetMoment.day())!==-1){
                returnfalse;
            }
            if(this._options.disabledHours&&(granularity==='h'||granularity==='m'||granularity==='s')&&this._isInDisabledHours(targetMoment)){
                returnfalse;
            }
            if(this._options.enabledHours&&(granularity==='h'||granularity==='m'||granularity==='s')&&!this._isInEnabledHours(targetMoment)){
                returnfalse;
            }
            if(this._options.disabledTimeIntervals&&(granularity==='h'||granularity==='m'||granularity==='s')){
                varfound=false;
                $.each(this._options.disabledTimeIntervals,function(){
                    if(targetMoment.isBetween(this[0],this[1])){
                        found=true;
                        returnfalse;
                    }
                });
                if(found){
                    returnfalse;
                }
            }
            returntrue;
        };

        DateTimePicker.prototype._parseInputDate=function_parseInputDate(inputDate){
            if(this._options.parseInputDate===undefined){
                if(!moment.isMoment(inputDate)){
                    inputDate=this.getMoment(inputDate);
                }
            }else{
                inputDate=this._options.parseInputDate(inputDate);
            }
            //inputDate.locale(this.options.locale);
            returninputDate;
        };

        DateTimePicker.prototype._keydown=function_keydown(e){
            varhandler=null,
                index=void0,
                index2=void0,
                keyBindKeys=void0,
                allModifiersPressed=void0;
            varpressedKeys=[],
                pressedModifiers={},
                currentKey=e.which,
                pressed='p';

            keyState[currentKey]=pressed;

            for(indexinkeyState){
                if(keyState.hasOwnProperty(index)&&keyState[index]===pressed){
                    pressedKeys.push(index);
                    if(parseInt(index,10)!==currentKey){
                        pressedModifiers[index]=true;
                    }
                }
            }

            for(indexinthis._options.keyBinds){
                if(this._options.keyBinds.hasOwnProperty(index)&&typeofthis._options.keyBinds[index]==='function'){
                    keyBindKeys=index.split('');
                    if(keyBindKeys.length===pressedKeys.length&&KeyMap[currentKey]===keyBindKeys[keyBindKeys.length-1]){
                        allModifiersPressed=true;
                        for(index2=keyBindKeys.length-2;index2>=0;index2--){
                            if(!(KeyMap[keyBindKeys[index2]]inpressedModifiers)){
                                allModifiersPressed=false;
                                break;
                            }
                        }
                        if(allModifiersPressed){
                            handler=this._options.keyBinds[index];
                            break;
                        }
                    }
                }
            }

            if(handler){
                if(handler.call(this)){
                    e.stopPropagation();
                    e.preventDefault();
                }
            }
        };

        //noinspectionJSMethodCanBeStatic,SpellCheckingInspection


        DateTimePicker.prototype._keyup=function_keyup(e){
            keyState[e.which]='r';
            if(keyPressHandled[e.which]){
                keyPressHandled[e.which]=false;
                e.stopPropagation();
                e.preventDefault();
            }
        };

        DateTimePicker.prototype._indexGivenDates=function_indexGivenDates(givenDatesArray){
            //StoregivenenabledDatesanddisabledDatesaskeys.
            //ThiswaywecanchecktheirexistenceinO(1)timeinsteadofloopingthroughwholearray.
            //(forexample:options.enabledDates['2014-02-27']===true)
            vargivenDatesIndexed={},
                self=this;
            $.each(givenDatesArray,function(){
                vardDate=self._parseInputDate(this);
                if(dDate.isValid()){
                    givenDatesIndexed[dDate.format('YYYY-MM-DD')]=true;
                }
            });
            returnObject.keys(givenDatesIndexed).length?givenDatesIndexed:false;
        };

        DateTimePicker.prototype._indexGivenHours=function_indexGivenHours(givenHoursArray){
            //StoregivenenabledHoursanddisabledHoursaskeys.
            //ThiswaywecanchecktheirexistenceinO(1)timeinsteadofloopingthroughwholearray.
            //(forexample:options.enabledHours['2014-02-27']===true)
            vargivenHoursIndexed={};
            $.each(givenHoursArray,function(){
                givenHoursIndexed[this]=true;
            });
            returnObject.keys(givenHoursIndexed).length?givenHoursIndexed:false;
        };

        DateTimePicker.prototype._initFormatting=function_initFormatting(){
            varformat=this._options.format||'LLT',
                self=this;

            this.actualFormat=format.replace(/(\[[^\[]*])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g,function(formatInput){
                returnself._dates[0].localeData().longDateFormat(formatInput)||formatInput;//todotakingthefirstdateshouldbeok
            });

            this.parseFormats=this._options.extraFormats?this._options.extraFormats.slice():[];
            if(this.parseFormats.indexOf(format)<0&&this.parseFormats.indexOf(this.actualFormat)<0){
                this.parseFormats.push(this.actualFormat);
            }

            this.use24Hours=this.actualFormat.toLowerCase().indexOf('a')<1&&this.actualFormat.replace(/\[.*?]/g,'').indexOf('h')<1;

            if(this._isEnabled('y')){
                MinViewModeNumber=2;
            }
            if(this._isEnabled('M')){
                MinViewModeNumber=1;
            }
            if(this._isEnabled('d')){
                MinViewModeNumber=0;
            }

            this.currentViewMode=Math.max(MinViewModeNumber,this.currentViewMode);

            if(!this.unset){
                this._setValue(this._dates[0],0);
            }
        };

        DateTimePicker.prototype._getLastPickedDate=function_getLastPickedDate(){
            returnthis._dates[this._getLastPickedDateIndex()]||this.getMoment();//FIXMEchangedbyFlectra
        };

        DateTimePicker.prototype._getLastPickedDateIndex=function_getLastPickedDateIndex(){
            returnthis._dates.length-1;
        };

        //public


        DateTimePicker.prototype.getMoment=functiongetMoment(d,f){//FLECTRAFIX:giveoptionalformat
            varreturnMoment=void0;

            //FLECTRAFIX:defaulttooriginal`parseFormats`attribute
            if(!f){
                f=this.parseFormats;
            }

            if(d===undefined||d===null){
                returnMoment=moment();//TODOshouldthisuseformat?andlocale?
            }elseif(this._hasTimeZone()){
                //Thereisastringtoparseandadefaulttimezone
                //parsewiththetzfunctionwhichtakesadefaulttimezoneifitisnotintheformatstring
                returnMoment=moment.tz(d,f,this._options.locale,this._options.useStrict,this._options.timeZone);//FLECTRAFIX:useformatargument
            }else{
                returnMoment=moment(d,f,this._options.locale,this._options.useStrict);//FLECTRAFIX:useformatargument
            }

            if(this._hasTimeZone()){
                returnMoment.tz(this._options.timeZone);
            }

            returnreturnMoment;
        };

        DateTimePicker.prototype.toggle=functiontoggle(){
            returnthis.widget?this.hide():this.show();
        };

        DateTimePicker.prototype.ignoreReadonly=functionignoreReadonly(_ignoreReadonly){
            if(arguments.length===0){
                returnthis._options.ignoreReadonly;
            }
            if(typeof_ignoreReadonly!=='boolean'){
                thrownewTypeError('ignoreReadonly()expectsabooleanparameter');
            }
            this._options.ignoreReadonly=_ignoreReadonly;
        };

        DateTimePicker.prototype.options=functionoptions(newOptions){
            if(arguments.length===0){
                return$.extend(true,{},this._options);
            }

            if(!(newOptionsinstanceofObject)){
                thrownewTypeError('options()this.optionsparametershouldbeanobject');
            }
            $.extend(true,this._options,newOptions);
            varself=this;
            $.each(this._options,function(key,value){
                if(self[key]!==undefined){
                    self[key](value);
                }
            });
        };

        DateTimePicker.prototype.date=functiondate(newDate,index){
            index=index||0;
            if(arguments.length===0){
                if(this.unset){
                    returnnull;
                }
                if(this._options.allowMultidate){
                    returnthis._dates.join(this._options.multidateSeparator);
                }else{
                    returnthis._dates[index].clone();
                }
            }

            if(newDate!==null&&typeofnewDate!=='string'&&!moment.isMoment(newDate)&&!(newDateinstanceofDate)){
                thrownewTypeError('date()parametermustbeoneof[null,string,momentorDate]');
            }

            this._setValue(newDate===null?null:this._parseInputDate(newDate),index);
        };

        DateTimePicker.prototype.format=functionformat(newFormat){
            if(arguments.length===0){
                returnthis._options.format;
            }

            if(typeofnewFormat!=='string'&&(typeofnewFormat!=='boolean'||newFormat!==false)){
                thrownewTypeError('format()expectsastringorboolean:falseparameter'+newFormat);
            }

            this._options.format=newFormat;
            if(this.actualFormat){
                this._initFormatting();//reinitializeformatting
            }
        };

        DateTimePicker.prototype.timeZone=functiontimeZone(newZone){
            if(arguments.length===0){
                returnthis._options.timeZone;
            }

            if(typeofnewZone!=='string'){
                thrownewTypeError('newZone()expectsastringparameter');
            }

            this._options.timeZone=newZone;
        };

        DateTimePicker.prototype.dayViewHeaderFormat=functiondayViewHeaderFormat(newFormat){
            if(arguments.length===0){
                returnthis._options.dayViewHeaderFormat;
            }

            if(typeofnewFormat!=='string'){
                thrownewTypeError('dayViewHeaderFormat()expectsastringparameter');
            }

            this._options.dayViewHeaderFormat=newFormat;
        };

        DateTimePicker.prototype.extraFormats=functionextraFormats(formats){
            if(arguments.length===0){
                returnthis._options.extraFormats;
            }

            if(formats!==false&&!(formatsinstanceofArray)){
                thrownewTypeError('extraFormats()expectsanarrayorfalseparameter');
            }

            this._options.extraFormats=formats;
            if(this.parseFormats){
                this._initFormatting();//reinitformatting
            }
        };

        DateTimePicker.prototype.disabledDates=functiondisabledDates(dates){
            if(arguments.length===0){
                returnthis._options.disabledDates?$.extend({},this._options.disabledDates):this._options.disabledDates;
            }

            if(!dates){
                this._options.disabledDates=false;
                this._update();
                returntrue;
            }
            if(!(datesinstanceofArray)){
                thrownewTypeError('disabledDates()expectsanarrayparameter');
            }
            this._options.disabledDates=this._indexGivenDates(dates);
            this._options.enabledDates=false;
            this._update();
        };

        DateTimePicker.prototype.enabledDates=functionenabledDates(dates){
            if(arguments.length===0){
                returnthis._options.enabledDates?$.extend({},this._options.enabledDates):this._options.enabledDates;
            }

            if(!dates){
                this._options.enabledDates=false;
                this._update();
                returntrue;
            }
            if(!(datesinstanceofArray)){
                thrownewTypeError('enabledDates()expectsanarrayparameter');
            }
            this._options.enabledDates=this._indexGivenDates(dates);
            this._options.disabledDates=false;
            this._update();
        };

        DateTimePicker.prototype.daysOfWeekDisabled=functiondaysOfWeekDisabled(_daysOfWeekDisabled){
            if(arguments.length===0){
                returnthis._options.daysOfWeekDisabled.splice(0);
            }

            if(typeof_daysOfWeekDisabled==='boolean'&&!_daysOfWeekDisabled){
                this._options.daysOfWeekDisabled=false;
                this._update();
                returntrue;
            }

            if(!(_daysOfWeekDisabledinstanceofArray)){
                thrownewTypeError('daysOfWeekDisabled()expectsanarrayparameter');
            }
            this._options.daysOfWeekDisabled=_daysOfWeekDisabled.reduce(function(previousValue,currentValue){
                currentValue=parseInt(currentValue,10);
                if(currentValue>6||currentValue<0||isNaN(currentValue)){
                    returnpreviousValue;
                }
                if(previousValue.indexOf(currentValue)===-1){
                    previousValue.push(currentValue);
                }
                returnpreviousValue;
            },[]).sort();
            if(this._options.useCurrent&&!this._options.keepInvalid){
                for(vari=0;i<this._dates.length;i++){
                    vartries=0;
                    while(!this._isValid(this._dates[i],'d')){
                        this._dates[i].add(1,'d');
                        if(tries===31){
                            throw'Tried31timestofindavaliddate';
                        }
                        tries++;
                    }
                    this._setValue(this._dates[i],i);
                }
            }
            this._update();
        };

        DateTimePicker.prototype.maxDate=functionmaxDate(_maxDate){
            if(arguments.length===0){
                returnthis._options.maxDate?this._options.maxDate.clone():this._options.maxDate;
            }

            if(typeof_maxDate==='boolean'&&_maxDate===false){
                this._options.maxDate=false;
                this._update();
                returntrue;
            }

            if(typeof_maxDate==='string'){
                if(_maxDate==='now'||_maxDate==='moment'){
                    _maxDate=this.getMoment();
                }
            }

            varparsedDate=this._parseInputDate(_maxDate);

            if(!parsedDate.isValid()){
                thrownewTypeError('maxDate()Couldnotparsedateparameter:'+_maxDate);
            }
            if(this._options.minDate&&parsedDate.isBefore(this._options.minDate)){
                thrownewTypeError('maxDate()dateparameterisbeforethis.options.minDate:'+parsedDate.format(this.actualFormat));
            }
            this._options.maxDate=parsedDate;
            for(vari=0;i<this._dates.length;i++){
                if(this._options.useCurrent&&!this._options.keepInvalid&&this._dates[i].isAfter(_maxDate)){
                    this._setValue(this._options.maxDate,i);
                }
            }
            if(this._viewDate.isAfter(parsedDate)){
                this._viewDate=parsedDate.clone().subtract(this._options.stepping,'m');
            }
            this._update();
        };

        DateTimePicker.prototype.minDate=functionminDate(_minDate){
            if(arguments.length===0){
                returnthis._options.minDate?this._options.minDate.clone():this._options.minDate;
            }

            if(typeof_minDate==='boolean'&&_minDate===false){
                this._options.minDate=false;
                this._update();
                returntrue;
            }

            if(typeof_minDate==='string'){
                if(_minDate==='now'||_minDate==='moment'){
                    _minDate=this.getMoment();
                }
            }

            varparsedDate=this._parseInputDate(_minDate);

            if(!parsedDate.isValid()){
                thrownewTypeError('minDate()Couldnotparsedateparameter:'+_minDate);
            }
            if(this._options.maxDate&&parsedDate.isAfter(this._options.maxDate)){
                thrownewTypeError('minDate()dateparameterisafterthis.options.maxDate:'+parsedDate.format(this.actualFormat));
            }
            this._options.minDate=parsedDate;
            for(vari=0;i<this._dates.length;i++){
                if(this._options.useCurrent&&!this._options.keepInvalid&&this._dates[i].isBefore(_minDate)){
                    this._setValue(this._options.minDate,i);
                }
            }
            if(this._viewDate.isBefore(parsedDate)){
                this._viewDate=parsedDate.clone().add(this._options.stepping,'m');
            }
            this._update();
        };

        DateTimePicker.prototype.defaultDate=functiondefaultDate(_defaultDate){
            if(arguments.length===0){
                returnthis._options.defaultDate?this._options.defaultDate.clone():this._options.defaultDate;
            }
            if(!_defaultDate){
                this._options.defaultDate=false;
                returntrue;
            }

            if(typeof_defaultDate==='string'){
                if(_defaultDate==='now'||_defaultDate==='moment'){
                    _defaultDate=this.getMoment();
                }else{
                    _defaultDate=this.getMoment(_defaultDate);
                }
            }

            varparsedDate=this._parseInputDate(_defaultDate);
            if(!parsedDate.isValid()){
                thrownewTypeError('defaultDate()Couldnotparsedateparameter:'+_defaultDate);
            }
            if(!this._isValid(parsedDate)){
                thrownewTypeError('defaultDate()datepassedisinvalidaccordingtocomponentsetupvalidations');
            }

            this._options.defaultDate=parsedDate;

            if(this._options.defaultDate&&this._options.inline||this.input!==undefined&&this.input.val().trim()===''){
                this._setValue(this._options.defaultDate,0);
            }
        };

        DateTimePicker.prototype.locale=functionlocale(_locale){
            if(arguments.length===0){
                returnthis._options.locale;
            }

            if(!moment.localeData(_locale)){
                thrownewTypeError('locale()locale'+_locale+'isnotloadedfrommomentlocales!');
            }

            this._options.locale=_locale;

            for(vari=0;i<this._dates.length;i++){
                this._dates[i].locale(this._options.locale);
            }
            this._viewDate.locale(this._options.locale);

            if(this.actualFormat){
                this._initFormatting();//reinitializeformatting
            }
            if(this.widget){
                this.hide();
                this.show();
            }
        };

        DateTimePicker.prototype.stepping=functionstepping(_stepping){
            if(arguments.length===0){
                returnthis._options.stepping;
            }

            _stepping=parseInt(_stepping,10);
            if(isNaN(_stepping)||_stepping<1){
                _stepping=1;
            }
            this._options.stepping=_stepping;
        };

        DateTimePicker.prototype.useCurrent=functionuseCurrent(_useCurrent){
            varuseCurrentOptions=['year','month','day','hour','minute'];
            if(arguments.length===0){
                returnthis._options.useCurrent;
            }

            if(typeof_useCurrent!=='boolean'&&typeof_useCurrent!=='string'){
                thrownewTypeError('useCurrent()expectsabooleanorstringparameter');
            }
            if(typeof_useCurrent==='string'&&useCurrentOptions.indexOf(_useCurrent.toLowerCase())===-1){
                thrownewTypeError('useCurrent()expectsastringparameterof'+useCurrentOptions.join(','));
            }
            this._options.useCurrent=_useCurrent;
        };

        DateTimePicker.prototype.collapse=functioncollapse(_collapse){
            if(arguments.length===0){
                returnthis._options.collapse;
            }

            if(typeof_collapse!=='boolean'){
                thrownewTypeError('collapse()expectsabooleanparameter');
            }
            if(this._options.collapse===_collapse){
                returntrue;
            }
            this._options.collapse=_collapse;
            if(this.widget){
                this.hide();
                this.show();
            }
        };

        DateTimePicker.prototype.icons=functionicons(_icons){
            if(arguments.length===0){
                return$.extend({},this._options.icons);
            }

            if(!(_iconsinstanceofObject)){
                thrownewTypeError('icons()expectsparametertobeanObject');
            }

            $.extend(this._options.icons,_icons);

            if(this.widget){
                this.hide();
                this.show();
            }
        };

        DateTimePicker.prototype.tooltips=functiontooltips(_tooltips){
            if(arguments.length===0){
                return$.extend({},this._options.tooltips);
            }

            if(!(_tooltipsinstanceofObject)){
                thrownewTypeError('tooltips()expectsparametertobeanObject');
            }
            $.extend(this._options.tooltips,_tooltips);
            if(this.widget){
                this.hide();
                this.show();
            }
        };

        DateTimePicker.prototype.useStrict=functionuseStrict(_useStrict){
            if(arguments.length===0){
                returnthis._options.useStrict;
            }

            if(typeof_useStrict!=='boolean'){
                thrownewTypeError('useStrict()expectsabooleanparameter');
            }
            this._options.useStrict=_useStrict;
        };

        DateTimePicker.prototype.sideBySide=functionsideBySide(_sideBySide){
            if(arguments.length===0){
                returnthis._options.sideBySide;
            }

            if(typeof_sideBySide!=='boolean'){
                thrownewTypeError('sideBySide()expectsabooleanparameter');
            }
            this._options.sideBySide=_sideBySide;
            if(this.widget){
                this.hide();
                this.show();
            }
        };

        DateTimePicker.prototype.viewMode=functionviewMode(_viewMode){
            if(arguments.length===0){
                returnthis._options.viewMode;
            }

            if(typeof_viewMode!=='string'){
                thrownewTypeError('viewMode()expectsastringparameter');
            }

            if(DateTimePicker.ViewModes.indexOf(_viewMode)===-1){
                thrownewTypeError('viewMode()parametermustbeoneof('+DateTimePicker.ViewModes.join(',')+')value');
            }

            this._options.viewMode=_viewMode;
            this.currentViewMode=Math.max(DateTimePicker.ViewModes.indexOf(_viewMode)-1,DateTimePicker.MinViewModeNumber);

            this._showMode();
        };

        DateTimePicker.prototype.calendarWeeks=functioncalendarWeeks(_calendarWeeks){
            if(arguments.length===0){
                returnthis._options.calendarWeeks;
            }

            if(typeof_calendarWeeks!=='boolean'){
                thrownewTypeError('calendarWeeks()expectsparametertobeabooleanvalue');
            }

            this._options.calendarWeeks=_calendarWeeks;
            this._update();
        };

        DateTimePicker.prototype.buttons=functionbuttons(_buttons){
            if(arguments.length===0){
                return$.extend({},this._options.buttons);
            }

            if(!(_buttonsinstanceofObject)){
                thrownewTypeError('buttons()expectsparametertobeanObject');
            }

            $.extend(this._options.buttons,_buttons);

            if(typeofthis._options.buttons.showToday!=='boolean'){
                thrownewTypeError('buttons.showTodayexpectsabooleanparameter');
            }
            if(typeofthis._options.buttons.showClear!=='boolean'){
                thrownewTypeError('buttons.showClearexpectsabooleanparameter');
            }
            if(typeofthis._options.buttons.showClose!=='boolean'){
                thrownewTypeError('buttons.showCloseexpectsabooleanparameter');
            }

            if(this.widget){
                this.hide();
                this.show();
            }
        };

        DateTimePicker.prototype.keepOpen=functionkeepOpen(_keepOpen){
            if(arguments.length===0){
                returnthis._options.keepOpen;
            }

            if(typeof_keepOpen!=='boolean'){
                thrownewTypeError('keepOpen()expectsabooleanparameter');
            }

            this._options.keepOpen=_keepOpen;
        };

        DateTimePicker.prototype.focusOnShow=functionfocusOnShow(_focusOnShow){
            if(arguments.length===0){
                returnthis._options.focusOnShow;
            }

            if(typeof_focusOnShow!=='boolean'){
                thrownewTypeError('focusOnShow()expectsabooleanparameter');
            }

            this._options.focusOnShow=_focusOnShow;
        };

        DateTimePicker.prototype.inline=functioninline(_inline){
            if(arguments.length===0){
                returnthis._options.inline;
            }

            if(typeof_inline!=='boolean'){
                thrownewTypeError('inline()expectsabooleanparameter');
            }

            this._options.inline=_inline;
        };

        DateTimePicker.prototype.clear=functionclear(){
            this._setValue(null);//todo
        };

        DateTimePicker.prototype.keyBinds=functionkeyBinds(_keyBinds){
            if(arguments.length===0){
                returnthis._options.keyBinds;
            }

            this._options.keyBinds=_keyBinds;
        };

        DateTimePicker.prototype.debug=functiondebug(_debug){
            if(typeof_debug!=='boolean'){
                thrownewTypeError('debug()expectsabooleanparameter');
            }

            this._options.debug=_debug;
        };

        DateTimePicker.prototype.allowInputToggle=functionallowInputToggle(_allowInputToggle){
            if(arguments.length===0){
                returnthis._options.allowInputToggle;
            }

            if(typeof_allowInputToggle!=='boolean'){
                thrownewTypeError('allowInputToggle()expectsabooleanparameter');
            }

            this._options.allowInputToggle=_allowInputToggle;
        };

        DateTimePicker.prototype.keepInvalid=functionkeepInvalid(_keepInvalid){
            if(arguments.length===0){
                returnthis._options.keepInvalid;
            }

            if(typeof_keepInvalid!=='boolean'){
                thrownewTypeError('keepInvalid()expectsabooleanparameter');
            }
            this._options.keepInvalid=_keepInvalid;
        };

        DateTimePicker.prototype.datepickerInput=functiondatepickerInput(_datepickerInput){
            if(arguments.length===0){
                returnthis._options.datepickerInput;
            }

            if(typeof_datepickerInput!=='string'){
                thrownewTypeError('datepickerInput()expectsastringparameter');
            }

            this._options.datepickerInput=_datepickerInput;
        };

        DateTimePicker.prototype.parseInputDate=functionparseInputDate(_parseInputDate2){
            if(arguments.length===0){
                returnthis._options.parseInputDate;
            }

            if(typeof_parseInputDate2!=='function'){
                thrownewTypeError('parseInputDate()shouldbeasfunction');
            }

            this._options.parseInputDate=_parseInputDate2;
        };

        DateTimePicker.prototype.disabledTimeIntervals=functiondisabledTimeIntervals(_disabledTimeIntervals){
            if(arguments.length===0){
                returnthis._options.disabledTimeIntervals?$.extend({},this._options.disabledTimeIntervals):this._options.disabledTimeIntervals;
            }

            if(!_disabledTimeIntervals){
                this._options.disabledTimeIntervals=false;
                this._update();
                returntrue;
            }
            if(!(_disabledTimeIntervalsinstanceofArray)){
                thrownewTypeError('disabledTimeIntervals()expectsanarrayparameter');
            }
            this._options.disabledTimeIntervals=_disabledTimeIntervals;
            this._update();
        };

        DateTimePicker.prototype.disabledHours=functiondisabledHours(hours){
            if(arguments.length===0){
                returnthis._options.disabledHours?$.extend({},this._options.disabledHours):this._options.disabledHours;
            }

            if(!hours){
                this._options.disabledHours=false;
                this._update();
                returntrue;
            }
            if(!(hoursinstanceofArray)){
                thrownewTypeError('disabledHours()expectsanarrayparameter');
            }
            this._options.disabledHours=this._indexGivenHours(hours);
            this._options.enabledHours=false;
            if(this._options.useCurrent&&!this._options.keepInvalid){
                for(vari=0;i<this._dates.length;i++){
                    vartries=0;
                    while(!this._isValid(this._dates[i],'h')){
                        this._dates[i].add(1,'h');
                        if(tries===24){
                            throw'Tried24timestofindavaliddate';
                        }
                        tries++;
                    }
                    this._setValue(this._dates[i],i);
                }
            }
            this._update();
        };

        DateTimePicker.prototype.enabledHours=functionenabledHours(hours){
            if(arguments.length===0){
                returnthis._options.enabledHours?$.extend({},this._options.enabledHours):this._options.enabledHours;
            }

            if(!hours){
                this._options.enabledHours=false;
                this._update();
                returntrue;
            }
            if(!(hoursinstanceofArray)){
                thrownewTypeError('enabledHours()expectsanarrayparameter');
            }
            this._options.enabledHours=this._indexGivenHours(hours);
            this._options.disabledHours=false;
            if(this._options.useCurrent&&!this._options.keepInvalid){
                for(vari=0;i<this._dates.length;i++){
                    vartries=0;
                    while(!this._isValid(this._dates[i],'h')){
                        this._dates[i].add(1,'h');
                        if(tries===24){
                            throw'Tried24timestofindavaliddate';
                        }
                        tries++;
                    }
                    this._setValue(this._dates[i],i);
                }
            }
            this._update();
        };

        DateTimePicker.prototype.viewDate=functionviewDate(newDate){
            if(arguments.length===0){
                returnthis._viewDate.clone();
            }

            if(!newDate){
                this._viewDate=(this._dates[0]||this.getMoment()).clone();
                returntrue;
            }

            if(typeofnewDate!=='string'&&!moment.isMoment(newDate)&&!(newDateinstanceofDate)){
                thrownewTypeError('viewDate()parametermustbeoneof[string,momentorDate]');
            }

            this._viewDate=this._parseInputDate(newDate);
            this._viewUpdate();
        };

        DateTimePicker.prototype.allowMultidate=functionallowMultidate(_allowMultidate){
            if(typeof_allowMultidate!=='boolean'){
                thrownewTypeError('allowMultidate()expectsabooleanparameter');
            }

            this._options.allowMultidate=_allowMultidate;
        };

        DateTimePicker.prototype.multidateSeparator=functionmultidateSeparator(_multidateSeparator){
            if(arguments.length===0){
                returnthis._options.multidateSeparator;
            }

            if(typeof_multidateSeparator!=='string'||_multidateSeparator.length>1){
                thrownewTypeError('multidateSeparatorexpectsasinglecharacterstringparameter');
            }

            this._options.multidateSeparator=_multidateSeparator;
        };

        _createClass(DateTimePicker,null,[{
            key:'NAME',
            get:functionget(){
                returnNAME;
            }

            /**
             *@return{string}
             */

        },{
            key:'DATA_KEY',
            get:functionget(){
                returnDATA_KEY;
            }

            /**
             *@return{string}
             */

        },{
            key:'EVENT_KEY',
            get:functionget(){
                returnEVENT_KEY;
            }

            /**
             *@return{string}
             */

        },{
            key:'DATA_API_KEY',
            get:functionget(){
                returnDATA_API_KEY;
            }
        },{
            key:'DatePickerModes',
            get:functionget(){
                returnDatePickerModes;
            }
        },{
            key:'ViewModes',
            get:functionget(){
                returnViewModes;
            }

            /**
             *@return{number}
             */

        },{
            key:'MinViewModeNumber',
            get:functionget(){
                returnMinViewModeNumber;
            }
        },{
            key:'Event',
            get:functionget(){
                returnEvent;
            }
        },{
            key:'Selector',
            get:functionget(){
                returnSelector;
            }
        },{
            key:'Default',
            get:functionget(){
                returnDefault;
            },
            set:functionset(value){
                Default=value;
            }
        },{
            key:'ClassName',
            get:functionget(){
                returnClassName;
            }
        }]);

        returnDateTimePicker;
    }();

    returnDateTimePicker;
}(jQuery,moment);

//noinspectionJSUnusedGlobalSymbols
/*globalDateTimePicker*/
varTempusDominusBootstrap4=function($){
    //eslint-disable-lineno-unused-vars
    //ReSharperdisableonceInconsistentNaming
    varJQUERY_NO_CONFLICT=$.fn[DateTimePicker.NAME],
        verticalModes=['top','bottom','auto'],
        horizontalModes=['left','right','auto'],
        toolbarPlacements=['default','top','bottom'],
        getSelectorFromElement=functiongetSelectorFromElement($element){
        varselector=$element.data('target'),
            $selector=void0;

        if(!selector){
            selector=$element.attr('href')||'';
            selector=/^#[a-z]/i.test(selector)?selector:null;
        }
        $selector=$(selector);
        if($selector.length===0){
            return$selector;
        }

        if(!$selector.data(DateTimePicker.DATA_KEY)){
            $.extend({},$selector.data(),$(this).data());
        }

        return$selector;
    };

    //ReSharperdisableonceInconsistentNaming

    varTempusDominusBootstrap4=function(_DateTimePicker){
        _inherits(TempusDominusBootstrap4,_DateTimePicker);

        functionTempusDominusBootstrap4(element,options){
            _classCallCheck(this,TempusDominusBootstrap4);

            var_this=_possibleConstructorReturn(this,_DateTimePicker.call(this,element,options));

            _this._init();
            return_this;
        }

        TempusDominusBootstrap4.prototype._init=function_init(){
            if(this._element.hasClass('input-group')){
                vardatepickerButton=this._element.find('.datepickerbutton');
                if(datepickerButton.length===0){
                    this.component=this._element.find('[data-toggle="datetimepicker"]');
                }else{
                    this.component=datepickerButton;
                }
            }
        };

        TempusDominusBootstrap4.prototype._getDatePickerTemplate=function_getDatePickerTemplate(){
            varheadTemplate=$('<thead>').append($('<tr>').append($('<th>').addClass('prev').attr('data-action','previous').append($('<span>').addClass(this._options.icons.previous))).append($('<th>').addClass('picker-switch').attr('data-action','pickerSwitch').attr('colspan',''+(this._options.calendarWeeks?'6':'5'))).append($('<th>').addClass('next').attr('data-action','next').append($('<span>').addClass(this._options.icons.next)))),
                contTemplate=$('<tbody>').append($('<tr>').append($('<td>').attr('colspan',''+(this._options.calendarWeeks?'8':'7'))));

            return[$('<div>').addClass('datepicker-days').append($('<table>').addClass('tabletable-sm').append(headTemplate).append($('<tbody>'))),$('<div>').addClass('datepicker-months').append($('<table>').addClass('table-condensed').append(headTemplate.clone()).append(contTemplate.clone())),$('<div>').addClass('datepicker-years').append($('<table>').addClass('table-condensed').append(headTemplate.clone()).append(contTemplate.clone())),$('<div>').addClass('datepicker-decades').append($('<table>').addClass('table-condensed').append(headTemplate.clone()).append(contTemplate.clone()))];
        };

        TempusDominusBootstrap4.prototype._getTimePickerMainTemplate=function_getTimePickerMainTemplate(){
            vartopRow=$('<tr>'),
                middleRow=$('<tr>'),
                bottomRow=$('<tr>');

            if(this._isEnabled('h')){
                topRow.append($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'title':this._options.tooltips.incrementHour
                }).addClass('btn').attr('data-action','incrementHours').append($('<span>').addClass(this._options.icons.up))));
                middleRow.append($('<td>').append($('<span>').addClass('timepicker-hour').attr({
                    'data-time-component':'hours',
                    'title':this._options.tooltips.pickHour
                }).attr('data-action','showHours')));
                bottomRow.append($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'title':this._options.tooltips.decrementHour
                }).addClass('btn').attr('data-action','decrementHours').append($('<span>').addClass(this._options.icons.down))));
            }
            if(this._isEnabled('m')){
                if(this._isEnabled('h')){
                    topRow.append($('<td>').addClass('separator'));
                    middleRow.append($('<td>').addClass('separator').html(':'));
                    bottomRow.append($('<td>').addClass('separator'));
                }
                topRow.append($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'title':this._options.tooltips.incrementMinute
                }).addClass('btn').attr('data-action','incrementMinutes').append($('<span>').addClass(this._options.icons.up))));
                middleRow.append($('<td>').append($('<span>').addClass('timepicker-minute').attr({
                    'data-time-component':'minutes',
                    'title':this._options.tooltips.pickMinute
                }).attr('data-action','showMinutes')));
                bottomRow.append($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'title':this._options.tooltips.decrementMinute
                }).addClass('btn').attr('data-action','decrementMinutes').append($('<span>').addClass(this._options.icons.down))));
            }
            if(this._isEnabled('s')){
                if(this._isEnabled('m')){
                    topRow.append($('<td>').addClass('separator'));
                    middleRow.append($('<td>').addClass('separator').html(':'));
                    bottomRow.append($('<td>').addClass('separator'));
                }
                topRow.append($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'title':this._options.tooltips.incrementSecond
                }).addClass('btn').attr('data-action','incrementSeconds').append($('<span>').addClass(this._options.icons.up))));
                middleRow.append($('<td>').append($('<span>').addClass('timepicker-second').attr({
                    'data-time-component':'seconds',
                    'title':this._options.tooltips.pickSecond
                }).attr('data-action','showSeconds')));
                bottomRow.append($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'title':this._options.tooltips.decrementSecond
                }).addClass('btn').attr('data-action','decrementSeconds').append($('<span>').addClass(this._options.icons.down))));
            }

            if(!this.use24Hours){
                topRow.append($('<td>').addClass('separator'));
                middleRow.append($('<td>').append($('<button>').addClass('btnbtn-primary').attr({
                    'data-action':'togglePeriod',
                    tabindex:'-1',
                    'title':this._options.tooltips.togglePeriod
                })));
                bottomRow.append($('<td>').addClass('separator'));
            }

            return$('<div>').addClass('timepicker-picker').append($('<table>').addClass('table-condensed').append([topRow,middleRow,bottomRow]));
        };

        TempusDominusBootstrap4.prototype._getTimePickerTemplate=function_getTimePickerTemplate(){
            varhoursView=$('<div>').addClass('timepicker-hours').append($('<table>').addClass('table-condensed')),
                minutesView=$('<div>').addClass('timepicker-minutes').append($('<table>').addClass('table-condensed')),
                secondsView=$('<div>').addClass('timepicker-seconds').append($('<table>').addClass('table-condensed')),
                ret=[this._getTimePickerMainTemplate()];

            if(this._isEnabled('h')){
                ret.push(hoursView);
            }
            if(this._isEnabled('m')){
                ret.push(minutesView);
            }
            if(this._isEnabled('s')){
                ret.push(secondsView);
            }

            returnret;
        };

        TempusDominusBootstrap4.prototype._getToolbar=function_getToolbar(){
            varrow=[];
            if(this._options.buttons.showToday){
                row.push($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'data-action':'today',
                    'title':this._options.tooltips.today
                }).append($('<span>').addClass(this._options.icons.today))));
            }
            if(!this._options.sideBySide&&this._hasDate()&&this._hasTime()){
                vartitle=void0,
                    icon=void0;
                if(this._options.viewMode==='times'){
                    title=this._options.tooltips.selectDate;
                    icon=this._options.icons.date;
                }else{
                    title=this._options.tooltips.selectTime;
                    icon=this._options.icons.time;
                }
                row.push($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'data-action':'togglePicker',
                    'title':title
                }).append($('<span>').addClass(icon))));
            }
            if(this._options.buttons.showClear){
                row.push($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'data-action':'clear',
                    'title':this._options.tooltips.clear
                }).append($('<span>').addClass(this._options.icons.clear))));
            }
            if(this._options.buttons.showClose){
                row.push($('<td>').append($('<a>').attr({
                    href:'#',
                    tabindex:'-1',
                    'data-action':'close',
                    'title':this._options.tooltips.close
                }).append($('<span>').addClass(this._options.icons.close))));
            }
            returnrow.length===0?'':$('<table>').addClass('table-condensed').append($('<tbody>').append($('<tr>').append(row)));
        };

        TempusDominusBootstrap4.prototype._getTemplate=function_getTemplate(){
            vartemplate=$('<div>').addClass('bootstrap-datetimepicker-widgetdropdown-menu'),
                dateView=$('<div>').addClass('datepicker').append(this._getDatePickerTemplate()),
                timeView=$('<div>').addClass('timepicker').append(this._getTimePickerTemplate()),
                content=$('<ul>').addClass('list-unstyled'),
                toolbar=$('<li>').addClass('picker-switch'+(this._options.collapse?'accordion-toggle':'')).append(this._getToolbar());

            if(this._options.inline){
                template.removeClass('dropdown-menu');
            }

            if(this.use24Hours){
                template.addClass('usetwentyfour');
            }
            if(this._isEnabled('s')&&!this.use24Hours){
                template.addClass('wider');
            }

            if(this._options.sideBySide&&this._hasDate()&&this._hasTime()){
                template.addClass('timepicker-sbs');
                if(this._options.toolbarPlacement==='top'){
                    template.append(toolbar);
                }
                template.append($('<div>').addClass('row').append(dateView.addClass('col-md-6')).append(timeView.addClass('col-md-6')));
                if(this._options.toolbarPlacement==='bottom'||this._options.toolbarPlacement==='default'){
                    template.append(toolbar);
                }
                returntemplate;
            }

            if(this._options.toolbarPlacement==='top'){
                content.append(toolbar);
            }
            if(this._hasDate()){
                content.append($('<li>').addClass(this._options.collapse&&this._hasTime()?'collapse':'').addClass(this._options.collapse&&this._hasTime()&&this._options.viewMode==='times'?'':'show').append(dateView));
            }
            if(this._options.toolbarPlacement==='default'){
                content.append(toolbar);
            }
            if(this._hasTime()){
                content.append($('<li>').addClass(this._options.collapse&&this._hasDate()?'collapse':'').addClass(this._options.collapse&&this._hasDate()&&this._options.viewMode==='times'?'show':'').append(timeView));
            }
            if(this._options.toolbarPlacement==='bottom'){
                content.append(toolbar);
            }
            returntemplate.append(content);
        };

        TempusDominusBootstrap4.prototype._place=function_place(e){
            varself=e&&e.data&&e.data.picker||this,
                vertical=self._options.widgetPositioning.vertical,
                horizontal=self._options.widgetPositioning.horizontal,
                parent=void0;
            varposition=(self.component&&self.component.length?self.component:self._element).position(),
                offset=(self.component&&self.component.length?self.component:self._element).offset();
            if(self._options.widgetParent){
                parent=self._options.widgetParent.append(self.widget);
            }elseif(self._element.is('input')){
                parent=self._element.after(self.widget).parent();
            }elseif(self._options.inline){
                parent=self._element.append(self.widget);
                return;
            }else{
                parent=self._element;
                self._element.children().first().after(self.widget);
            }

            ///!\FLECTRAFIX:the3nextlineshavebeen*added*byflectra
            varparentOffset=parent.offset();
            position.top=offset.top-parentOffset.top;
            position.left=offset.left-parentOffset.left;

            //Topandbottomlogic
            if(vertical==='auto'){
                //noinspectionJSValidateTypes
                if(offset.top+self.widget.height()*1.5>=$(window).height()+$(window).scrollTop()&&self.widget.height()+self._element.outerHeight()<offset.top){
                    vertical='top';
                }else{
                    vertical='bottom';
                }
            }

            //Leftandrightlogic
            if(horizontal==='auto'){
                if(parent.width()<offset.left+self.widget.outerWidth()/2&&offset.left+self.widget.outerWidth()>$(window).width()){
                    horizontal='right';
                }else{
                    horizontal='left';
                }
            }

            if(vertical==='top'){
                self.widget.addClass('top').removeClass('bottom');
            }else{
                self.widget.addClass('bottom').removeClass('top');
            }

            if(horizontal==='right'){
                self.widget.addClass('float-right');
            }else{
                self.widget.removeClass('float-right');
            }

            //findthefirstparentelementthathasarelativecsspositioning
            if(parent.css('position')!=='relative'){
                parent=parent.parents().filter(function(){
                    return$(this).css('position')==='relative';
                }).first();
            }

            if(parent.length===0){
                thrownewError('datetimepickercomponentshouldbeplacedwithinarelativepositionedcontainer');
            }

            self.widget.css({
                top:vertical==='top'?'auto':position.top+self._element.outerHeight()+'px',
                bottom:vertical==='top'?parent.outerHeight()-(parent===self._element?0:position.top)+'px':'auto',
                left:horizontal==='left'?(parent===self._element?0:position.left)+'px':'auto',
                right:horizontal==='left'?'auto':parent.outerWidth()-self._element.outerWidth()-(parent===self._element?0:position.left)+'px'
            });
        };

        TempusDominusBootstrap4.prototype._fillDow=function_fillDow(){
            varrow=$('<tr>'),
                currentDate=this._viewDate.clone().startOf('w').startOf('d');

            if(this._options.calendarWeeks===true){
                row.append($('<th>').addClass('cw').text('#'));
            }

            while(currentDate.isBefore(this._viewDate.clone().endOf('w'))){
                row.append($('<th>').addClass('dow').text(currentDate.format('dd')));
                currentDate.add(1,'d');
            }
            this.widget.find('.datepicker-daysthead').append(row);
        };

        TempusDominusBootstrap4.prototype._fillMonths=function_fillMonths(){
            varspans=[],
                monthsShort=this._viewDate.clone().startOf('y').startOf('d');
            while(monthsShort.isSame(this._viewDate,'y')){
                spans.push($('<span>').attr('data-action','selectMonth').addClass('month').text(monthsShort.format('MMM')));
                monthsShort.add(1,'M');
            }
            this.widget.find('.datepicker-monthstd').empty().append(spans);
        };

        TempusDominusBootstrap4.prototype._updateMonths=function_updateMonths(){
            varmonthsView=this.widget.find('.datepicker-months'),
                monthsViewHeader=monthsView.find('th'),
                months=monthsView.find('tbody').find('span'),
                self=this;

            monthsViewHeader.eq(0).find('span').attr('title',this._options.tooltips.prevYear);
            monthsViewHeader.eq(1).attr('title',this._options.tooltips.selectYear);
            monthsViewHeader.eq(2).find('span').attr('title',this._options.tooltips.nextYear);

            monthsView.find('.disabled').removeClass('disabled');

            if(!this._isValid(this._viewDate.clone().subtract(1,'y'),'y')){
                monthsViewHeader.eq(0).addClass('disabled');
            }

            monthsViewHeader.eq(1).text(this._viewDate.year());

            if(!this._isValid(this._viewDate.clone().add(1,'y'),'y')){
                monthsViewHeader.eq(2).addClass('disabled');
            }

            months.removeClass('active');
            if(this._getLastPickedDate().isSame(this._viewDate,'y')&&!this.unset){
                months.eq(this._getLastPickedDate().month()).addClass('active');
            }

            months.each(function(index){
                if(!self._isValid(self._viewDate.clone().month(index),'M')){
                    $(this).addClass('disabled');
                }
            });
        };

        TempusDominusBootstrap4.prototype._getStartEndYear=function_getStartEndYear(factor,year){
            varstep=factor/10,
                startYear=Math.floor(year/factor)*factor,
                endYear=startYear+step*9,
                focusValue=Math.floor(year/step)*step;
            return[startYear,endYear,focusValue];
        };

        TempusDominusBootstrap4.prototype._updateYears=function_updateYears(){
            varyearsView=this.widget.find('.datepicker-years'),
                yearsViewHeader=yearsView.find('th'),
                yearCaps=this._getStartEndYear(10,this._viewDate.year()),
                startYear=this._viewDate.clone().year(yearCaps[0]),
                endYear=this._viewDate.clone().year(yearCaps[1]);
            varhtml='';

            yearsViewHeader.eq(0).find('span').attr('title',this._options.tooltips.prevDecade);
            yearsViewHeader.eq(1).attr('title',this._options.tooltips.selectDecade);
            yearsViewHeader.eq(2).find('span').attr('title',this._options.tooltips.nextDecade);

            yearsView.find('.disabled').removeClass('disabled');

            if(this._options.minDate&&this._options.minDate.isAfter(startYear,'y')){
                yearsViewHeader.eq(0).addClass('disabled');
            }

            yearsViewHeader.eq(1).text(startYear.year()+'-'+endYear.year());

            if(this._options.maxDate&&this._options.maxDate.isBefore(endYear,'y')){
                yearsViewHeader.eq(2).addClass('disabled');
            }

            html+='<spandata-action="selectYear"class="yearold'+(!this._isValid(startYear,'y')?'disabled':'')+'">'+(startYear.year()-1)+'</span>';
            while(!startYear.isAfter(endYear,'y')){
                html+='<spandata-action="selectYear"class="year'+(startYear.isSame(this._getLastPickedDate(),'y')&&!this.unset?'active':'')+(!this._isValid(startYear,'y')?'disabled':'')+'">'+startYear.year()+'</span>';
                startYear.add(1,'y');
            }
            html+='<spandata-action="selectYear"class="yearold'+(!this._isValid(startYear,'y')?'disabled':'')+'">'+startYear.year()+'</span>';

            yearsView.find('td').html(html);
        };

        TempusDominusBootstrap4.prototype._updateDecades=function_updateDecades(){
            vardecadesView=this.widget.find('.datepicker-decades'),
                decadesViewHeader=decadesView.find('th'),
                yearCaps=this._getStartEndYear(100,this._viewDate.year()),
                startDecade=this._viewDate.clone().year(yearCaps[0]),
                endDecade=this._viewDate.clone().year(yearCaps[1]);
            varminDateDecade=false,
                maxDateDecade=false,
                endDecadeYear=void0,
                html='';

            decadesViewHeader.eq(0).find('span').attr('title',this._options.tooltips.prevCentury);
            decadesViewHeader.eq(2).find('span').attr('title',this._options.tooltips.nextCentury);

            decadesView.find('.disabled').removeClass('disabled');

            if(startDecade.year()===0||this._options.minDate&&this._options.minDate.isAfter(startDecade,'y')){
                decadesViewHeader.eq(0).addClass('disabled');
            }

            decadesViewHeader.eq(1).text(startDecade.year()+'-'+endDecade.year());

            if(this._options.maxDate&&this._options.maxDate.isBefore(endDecade,'y')){
                decadesViewHeader.eq(2).addClass('disabled');
            }

            if(startDecade.year()-10<0){
                html+='<span>&nbsp;</span>';
            }else{
                html+='<spandata-action="selectDecade"class="decadeold"data-selection="'+(startDecade.year()+6)+'">'+(startDecade.year()-10)+'</span>';
            }

            while(!startDecade.isAfter(endDecade,'y')){
                endDecadeYear=startDecade.year()+11;
                minDateDecade=this._options.minDate&&this._options.minDate.isAfter(startDecade,'y')&&this._options.minDate.year()<=endDecadeYear;
                maxDateDecade=this._options.maxDate&&this._options.maxDate.isAfter(startDecade,'y')&&this._options.maxDate.year()<=endDecadeYear;
                html+='<spandata-action="selectDecade"class="decade'+(this._getLastPickedDate().isAfter(startDecade)&&this._getLastPickedDate().year()<=endDecadeYear?'active':'')+(!this._isValid(startDecade,'y')&&!minDateDecade&&!maxDateDecade?'disabled':'')+'"data-selection="'+(startDecade.year()+6)+'">'+startDecade.year()+'</span>';
                startDecade.add(10,'y');
            }
            html+='<spandata-action="selectDecade"class="decadeold"data-selection="'+(startDecade.year()+6)+'">'+startDecade.year()+'</span>';

            decadesView.find('td').html(html);
        };

        TempusDominusBootstrap4.prototype._fillDate=function_fillDate(){
            vardaysView=this.widget.find('.datepicker-days'),
                daysViewHeader=daysView.find('th'),
                html=[];
            varcurrentDate=void0,
                row=void0,
                clsName=void0,
                i=void0;

            if(!this._hasDate()){
                return;
            }

            daysViewHeader.eq(0).find('span').attr('title',this._options.tooltips.prevMonth);
            daysViewHeader.eq(1).attr('title',this._options.tooltips.selectMonth);
            daysViewHeader.eq(2).find('span').attr('title',this._options.tooltips.nextMonth);

            daysView.find('.disabled').removeClass('disabled');
            daysViewHeader.eq(1).text(this._viewDate.format(this._options.dayViewHeaderFormat));

            if(!this._isValid(this._viewDate.clone().subtract(1,'M'),'M')){
                daysViewHeader.eq(0).addClass('disabled');
            }
            if(!this._isValid(this._viewDate.clone().add(1,'M'),'M')){
                daysViewHeader.eq(2).addClass('disabled');
            }

            //!!FLECTRAFIXSTART!!
            varnow=this.getMoment();
            //currentDate=this._viewDate.clone().startOf('M').startOf('w').startOf('d');
            //avoidissueofsafari+DSTatmidnight
            currentDate=this._viewDate.clone().startOf('M').startOf('w').add(12,'hours');
            //!!FLECTRAFIXEND!!

            for(i=0;i<42;i++){
                //alwaysdisplay42days(shouldshow6weeks)
                if(currentDate.weekday()===0){
                    row=$('<tr>');
                    if(this._options.calendarWeeks){
                        row.append('<tdclass="cw">'+currentDate.week()+'</td>');
                    }
                    html.push(row);
                }
                clsName='';
                if(currentDate.isBefore(this._viewDate,'M')){
                    clsName+='old';
                }
                if(currentDate.isAfter(this._viewDate,'M')){
                    clsName+='new';
                }
                if(this._options.allowMultidate){
                    varindex=this._datesFormatted.indexOf(currentDate.format('YYYY-MM-DD'));
                    if(index!==-1){
                        if(currentDate.isSame(this._datesFormatted[index],'d')&&!this.unset){
                            clsName+='active';
                        }
                    }
                }else{
                    if(currentDate.isSame(this._getLastPickedDate(),'d')&&!this.unset){
                        clsName+='active';
                    }
                }
                if(!this._isValid(currentDate,'d')){
                    clsName+='disabled';
                }
                //!!FLECTRAFIXSTART!!
                if(currentDate.date()===now.date()&&currentDate.month()===now.month()&&currentDate.year()===now.year()){
                //!!FLECTRAFIXEND!!
                    clsName+='today';
                }
                if(currentDate.day()===0||currentDate.day()===6){
                    clsName+='weekend';
                }
                row.append('<tddata-action="selectDay"data-day="'+currentDate.format('L')+'"class="day'+clsName+'">'+currentDate.date()+'</td>');
                currentDate.add(1,'d');
            }

            daysView.find('tbody').empty().append(html);

            this._updateMonths();

            this._updateYears();

            this._updateDecades();
        };

        TempusDominusBootstrap4.prototype._fillHours=function_fillHours(){
            vartable=this.widget.find('.timepicker-hourstable'),
                currentHour=this._viewDate.clone().startOf('d'),
                html=[];
            varrow=$('<tr>');

            if(this._viewDate.hour()>11&&!this.use24Hours){
                currentHour.hour(12);
            }
            while(currentHour.isSame(this._viewDate,'d')&&(this.use24Hours||this._viewDate.hour()<12&&currentHour.hour()<12||this._viewDate.hour()>11)){
                if(currentHour.hour()%4===0){
                    row=$('<tr>');
                    html.push(row);
                }
                row.append('<tddata-action="selectHour"class="hour'+(!this._isValid(currentHour,'h')?'disabled':'')+'">'+currentHour.format(this.use24Hours?'HH':'hh')+'</td>');
                currentHour.add(1,'h');
            }
            table.empty().append(html);
        };

        TempusDominusBootstrap4.prototype._fillMinutes=function_fillMinutes(){
            vartable=this.widget.find('.timepicker-minutestable'),
                currentMinute=this._viewDate.clone().startOf('h'),
                html=[],
                step=this._options.stepping===1?5:this._options.stepping;
            varrow=$('<tr>');

            while(this._viewDate.isSame(currentMinute,'h')){
                if(currentMinute.minute()%(step*4)===0){
                    row=$('<tr>');
                    html.push(row);
                }
                row.append('<tddata-action="selectMinute"class="minute'+(!this._isValid(currentMinute,'m')?'disabled':'')+'">'+currentMinute.format('mm')+'</td>');
                currentMinute.add(step,'m');
            }
            table.empty().append(html);
        };

        TempusDominusBootstrap4.prototype._fillSeconds=function_fillSeconds(){
            vartable=this.widget.find('.timepicker-secondstable'),
                currentSecond=this._viewDate.clone().startOf('m'),
                html=[];
            varrow=$('<tr>');

            while(this._viewDate.isSame(currentSecond,'m')){
                if(currentSecond.second()%20===0){
                    row=$('<tr>');
                    html.push(row);
                }
                row.append('<tddata-action="selectSecond"class="second'+(!this._isValid(currentSecond,'s')?'disabled':'')+'">'+currentSecond.format('ss')+'</td>');
                currentSecond.add(5,'s');
            }

            table.empty().append(html);
        };

        TempusDominusBootstrap4.prototype._fillTime=function_fillTime(){
            vartoggle=void0,
                newDate=void0;
            vartimeComponents=this.widget.find('.timepickerspan[data-time-component]');

            if(!this.use24Hours){
                toggle=this.widget.find('.timepicker[data-action=togglePeriod]');
                newDate=this._getLastPickedDate().clone().add(this._getLastPickedDate().hours()>=12?-12:12,'h');

                toggle.text(this._getLastPickedDate().format('A'));

                if(this._isValid(newDate,'h')){
                    toggle.removeClass('disabled');
                }else{
                    toggle.addClass('disabled');
                }
            }
            timeComponents.filter('[data-time-component=hours]').text(this._getLastPickedDate().format(''+(this.use24Hours?'HH':'hh')));
            timeComponents.filter('[data-time-component=minutes]').text(this._getLastPickedDate().format('mm'));
            timeComponents.filter('[data-time-component=seconds]').text(this._getLastPickedDate().format('ss'));

            this._fillHours();
            this._fillMinutes();
            this._fillSeconds();
        };

        TempusDominusBootstrap4.prototype._doAction=function_doAction(e,action){
            varlastPicked=this._getLastPickedDate();
            if($(e.currentTarget).is('.disabled')){
                returnfalse;
            }
            action=action||$(e.currentTarget).data('action');
            switch(action){
                case'next':
                    {
                        varnavFnc=DateTimePicker.DatePickerModes[this.currentViewMode].NAV_FUNCTION;
                        this._viewDate.add(DateTimePicker.DatePickerModes[this.currentViewMode].NAV_STEP,navFnc);
                        this._fillDate();
                        this._viewUpdate(navFnc);
                        break;
                    }
                case'previous':
                    {
                        var_navFnc=DateTimePicker.DatePickerModes[this.currentViewMode].NAV_FUNCTION;
                        this._viewDate.subtract(DateTimePicker.DatePickerModes[this.currentViewMode].NAV_STEP,_navFnc);
                        this._fillDate();
                        this._viewUpdate(_navFnc);
                        break;
                    }
                case'pickerSwitch':
                    this._showMode(1);
                    break;
                case'selectMonth':
                    {
                        varmonth=$(e.target).closest('tbody').find('span').index($(e.target));
                        this._viewDate.month(month);
                        if(this.currentViewMode===DateTimePicker.MinViewModeNumber){
                            this._setValue(lastPicked.clone().year(this._viewDate.year()).month(this._viewDate.month()),this._getLastPickedDateIndex());
                            if(!this._options.inline){
                                this.hide();
                            }
                        }else{
                            this._showMode(-1);
                            this._fillDate();
                        }
                        this._viewUpdate('M');
                        break;
                    }
                case'selectYear':
                    {
                        varyear=parseInt($(e.target).text(),10)||0;
                        this._viewDate.year(year);
                        if(this.currentViewMode===DateTimePicker.MinViewModeNumber){
                            this._setValue(lastPicked.clone().year(this._viewDate.year()),this._getLastPickedDateIndex());
                            if(!this._options.inline){
                                this.hide();
                            }
                        }else{
                            this._showMode(-1);
                            this._fillDate();
                        }
                        this._viewUpdate('YYYY');
                        break;
                    }
                case'selectDecade':
                    {
                        var_year=parseInt($(e.target).data('selection'),10)||0;
                        this._viewDate.year(_year);
                        if(this.currentViewMode===DateTimePicker.MinViewModeNumber){
                            this._setValue(lastPicked.clone().year(this._viewDate.year()),this._getLastPickedDateIndex());
                            if(!this._options.inline){
                                this.hide();
                            }
                        }else{
                            this._showMode(-1);
                            this._fillDate();
                        }
                        this._viewUpdate('YYYY');
                        break;
                    }
                case'selectDay':
                    {
                        varday=this._viewDate.clone();
                        if($(e.target).is('.old')){
                            day.subtract(1,'M');
                        }
                        if($(e.target).is('.new')){
                            day.add(1,'M');
                        }
                        this._setValue(day.date(parseInt($(e.target).text(),10)),this._getLastPickedDateIndex());
                        if(!this._hasTime()&&!this._options.keepOpen&&!this._options.inline){
                            this.hide();
                        }
                        break;
                    }
                case'incrementHours':
                    {
                        varnewDate=lastPicked.clone().add(1,'h');
                        if(this._isValid(newDate,'h')){
                            this._setValue(newDate,this._getLastPickedDateIndex());
                        }
                        break;
                    }
                case'incrementMinutes':
                    {
                        var_newDate=lastPicked.clone().add(this._options.stepping,'m');
                        if(this._isValid(_newDate,'m')){
                            this._setValue(_newDate,this._getLastPickedDateIndex());
                        }
                        break;
                    }
                case'incrementSeconds':
                    {
                        var_newDate2=lastPicked.clone().add(1,'s');
                        if(this._isValid(_newDate2,'s')){
                            this._setValue(_newDate2,this._getLastPickedDateIndex());
                        }
                        break;
                    }
                case'decrementHours':
                    {
                        var_newDate3=lastPicked.clone().subtract(1,'h');
                        if(this._isValid(_newDate3,'h')){
                            this._setValue(_newDate3,this._getLastPickedDateIndex());
                        }
                        break;
                    }
                case'decrementMinutes':
                    {
                        var_newDate4=lastPicked.clone().subtract(this._options.stepping,'m');
                        if(this._isValid(_newDate4,'m')){
                            this._setValue(_newDate4,this._getLastPickedDateIndex());
                        }
                        break;
                    }
                case'decrementSeconds':
                    {
                        var_newDate5=lastPicked.clone().subtract(1,'s');
                        if(this._isValid(_newDate5,'s')){
                            this._setValue(_newDate5,this._getLastPickedDateIndex());
                        }
                        break;
                    }
                case'togglePeriod':
                    {
                        this._setValue(lastPicked.clone().add(lastPicked.hours()>=12?-12:12,'h'),this._getLastPickedDateIndex());
                        break;
                    }
                case'togglePicker':
                    {
                        var$this=$(e.target),
                            $link=$this.closest('a'),
                            $parent=$this.closest('ul'),
                            expanded=$parent.find('.show'),
                            closed=$parent.find('.collapse:not(.show)'),
                            $span=$this.is('span')?$this:$this.find('span');
                        varcollapseData=void0;

                        if(expanded&&expanded.length){
                            collapseData=expanded.data('collapse');
                            if(collapseData&&collapseData.transitioning){
                                returntrue;
                            }
                            if(expanded.collapse){
                                //ifcollapsepluginisavailablethroughbootstrap.jsthenuseit
                                expanded.collapse('hide');
                                closed.collapse('show');
                            }else{
                                //otherwisejusttoggleinclassonthetwoviews
                                expanded.removeClass('show');
                                closed.addClass('show');
                            }
                            $span.toggleClass(this._options.icons.time+''+this._options.icons.date);

                            if($span.hasClass(this._options.icons.date)){
                                $link.attr('title',this._options.tooltips.selectDate);
                            }else{
                                $link.attr('title',this._options.tooltips.selectTime);
                            }
                        }
                    }
                    break;
                case'showPicker':
                    this.widget.find('.timepicker>div:not(.timepicker-picker)').hide();
                    this.widget.find('.timepicker.timepicker-picker').show();
                    break;
                case'showHours':
                    this.widget.find('.timepicker.timepicker-picker').hide();
                    this.widget.find('.timepicker.timepicker-hours').show();
                    break;
                case'showMinutes':
                    this.widget.find('.timepicker.timepicker-picker').hide();
                    this.widget.find('.timepicker.timepicker-minutes').show();
                    break;
                case'showSeconds':
                    this.widget.find('.timepicker.timepicker-picker').hide();
                    this.widget.find('.timepicker.timepicker-seconds').show();
                    break;
                case'selectHour':
                    {
                        varhour=this.getMoment($(e.target).text(),this.use24Hours?'HH':'hh').hour();//FLECTRAFIX:usemomentformattogetthepropervalue(notnecessarilylatnnumbers)

                        if(!this.use24Hours){
                            if(lastPicked.hours()>=12){
                                if(hour!==12){
                                    hour+=12;
                                }
                            }else{
                                if(hour===12){
                                    hour=0;
                                }
                            }
                        }
                        this._setValue(lastPicked.clone().hours(hour),this._getLastPickedDateIndex());
                        if(!this._isEnabled('a')&&!this._isEnabled('m')&&!this._options.keepOpen&&!this._options.inline){
                            this.hide();
                        }else{
                            this._doAction(e,'showPicker');
                        }
                        break;
                    }
                case'selectMinute':
                    this._setValue(lastPicked.clone().minutes(this.getMoment($(e.target).text(),'mm').minute()),this._getLastPickedDateIndex());//FLECTRAFIX:usemomentformattogetthepropervalue(notnecessarilylatnnumbers)
                    if(!this._isEnabled('a')&&!this._isEnabled('s')&&!this._options.keepOpen&&!this._options.inline){
                        this.hide();
                    }else{
                        this._doAction(e,'showPicker');
                    }
                    break;
                case'selectSecond':
                    this._setValue(lastPicked.clone().seconds(this.getMoment($(e.target).text(),'ss').second()),this._getLastPickedDateIndex());//FLECTRAFIX:usemomentformattogetthepropervalue(notnecessarilylatnnumbers)
                    if(!this._isEnabled('a')&&!this._options.keepOpen&&!this._options.inline){
                        this.hide();
                    }else{
                        this._doAction(e,'showPicker');
                    }
                    break;
                case'clear':
                    this.clear();
                    break;
                case'close':
                    this.hide();
                    break;
                case'today':
                    {
                        vartodaysDate=this.getMoment();
                        if(this._isValid(todaysDate,'d')){
                            this._setValue(todaysDate,this._getLastPickedDateIndex());
                        }
                        break;
                    }
            }
            returnfalse;
        };

        //public


        TempusDominusBootstrap4.prototype.hide=functionhide(){
            vartransitioning=false;
            if(!this.widget){
                return;
            }
            //Ignoreeventifinthemiddleofapickertransition
            this.widget.find('.collapse').each(function(){
                varcollapseData=$(this).data('collapse');
                if(collapseData&&collapseData.transitioning){
                    transitioning=true;
                    returnfalse;
                }
                returntrue;
            });
            if(transitioning){
                return;
            }
            if(this.component&&this.component.hasClass('btn')){
                this.component.toggleClass('active');
            }
            this.widget.hide();

            $(window).off('resize',this._place());
            this.widget.off('click','[data-action]');
            this.widget.off('mousedown',false);

            this.widget.remove();
            this.widget=false;

            this._notifyEvent({
                type:DateTimePicker.Event.HIDE,
                date:this._getLastPickedDate().clone()
            });

            if(this.input!==undefined){
                this.input.blur();
            }

            this._viewDate=this._getLastPickedDate().clone();
        };

        TempusDominusBootstrap4.prototype.show=functionshow(){
            varcurrentMoment=void0;
            varuseCurrentGranularity={
                'year':functionyear(m){
                    returnm.month(0).date(1).hours(0).seconds(0).minutes(0);
                },
                'month':functionmonth(m){
                    returnm.date(1).hours(0).seconds(0).minutes(0);
                },
                'day':functionday(m){
                    returnm.hours(0).seconds(0).minutes(0);
                },
                'hour':functionhour(m){
                    returnm.seconds(0).minutes(0);
                },
                'minute':functionminute(m){
                    returnm.seconds(0);
                }
            };

            if(this.input!==undefined){
                if(this.input.prop('disabled')||!this._options.ignoreReadonly&&this.input.prop('readonly')||this.widget){
                    return;
                }
                if(this.input.val()!==undefined&&this.input.val().trim().length!==0){
                    this._setValue(this._parseInputDate(this.input.val().trim()),0);
                }elseif(this.unset&&this._options.useCurrent){
                    currentMoment=this.getMoment();
                    if(typeofthis._options.useCurrent==='string'){
                        currentMoment=useCurrentGranularity[this._options.useCurrent](currentMoment);
                    }
                    this._setValue(currentMoment,0);
                }
            }elseif(this.unset&&this._options.useCurrent){
                currentMoment=this.getMoment();
                if(typeofthis._options.useCurrent==='string'){
                    currentMoment=useCurrentGranularity[this._options.useCurrent](currentMoment);
                }
                this._setValue(currentMoment,0);
            }

            this.widget=this._getTemplate();

            this._fillDow();
            this._fillMonths();

            this.widget.find('.timepicker-hours').hide();
            this.widget.find('.timepicker-minutes').hide();
            this.widget.find('.timepicker-seconds').hide();

            this._update();
            this._showMode();

            $(window).on('resize',{picker:this},this._place);
            this.widget.on('click','[data-action]',$.proxy(this._doAction,this));//thishandlesclicksonthewidget
            this.widget.on('mousedown',false);

            if(this.component&&this.component.hasClass('btn')){
                this.component.toggleClass('active');
            }
            this._place();
            this.widget.show();
            if(this.input!==undefined&&this._options.focusOnShow&&!this.input.is(':focus')){
                this.input.focus();
            }

            this._notifyEvent({
                type:DateTimePicker.Event.SHOW
            });
        };

        TempusDominusBootstrap4.prototype.destroy=functiondestroy(){
            this.hide();
            //tododocoff?
            this._element.removeData(DateTimePicker.DATA_KEY);
            this._element.removeData('date');
        };

        TempusDominusBootstrap4.prototype.disable=functiondisable(){
            this.hide();
            if(this.component&&this.component.hasClass('btn')){
                this.component.addClass('disabled');
            }
            if(this.input!==undefined){
                this.input.prop('disabled',true);//tododisablethis/compifinputisnull
            }
        };

        TempusDominusBootstrap4.prototype.enable=functionenable(){
            if(this.component&&this.component.hasClass('btn')){
                this.component.removeClass('disabled');
            }
            if(this.input!==undefined){
                this.input.prop('disabled',false);//todoenablecomp/thisifinputisnull
            }
        };

        TempusDominusBootstrap4.prototype.toolbarPlacement=functiontoolbarPlacement(_toolbarPlacement){
            if(arguments.length===0){
                returnthis._options.toolbarPlacement;
            }

            if(typeof_toolbarPlacement!=='string'){
                thrownewTypeError('toolbarPlacement()expectsastringparameter');
            }
            if(toolbarPlacements.indexOf(_toolbarPlacement)===-1){
                thrownewTypeError('toolbarPlacement()parametermustbeoneof('+toolbarPlacements.join(',')+')value');
            }
            this._options.toolbarPlacement=_toolbarPlacement;

            if(this.widget){
                this.hide();
                this.show();
            }
        };

        TempusDominusBootstrap4.prototype.widgetPositioning=functionwidgetPositioning(_widgetPositioning){
            if(arguments.length===0){
                return$.extend({},this._options.widgetPositioning);
            }

            if({}.toString.call(_widgetPositioning)!=='[objectObject]'){
                thrownewTypeError('widgetPositioning()expectsanobjectvariable');
            }
            if(_widgetPositioning.horizontal){
                if(typeof_widgetPositioning.horizontal!=='string'){
                    thrownewTypeError('widgetPositioning()horizontalvariablemustbeastring');
                }
                _widgetPositioning.horizontal=_widgetPositioning.horizontal.toLowerCase();
                if(horizontalModes.indexOf(_widgetPositioning.horizontal)===-1){
                    thrownewTypeError('widgetPositioning()expectshorizontalparametertobeoneof('+horizontalModes.join(',')+')');
                }
                this._options.widgetPositioning.horizontal=_widgetPositioning.horizontal;
            }
            if(_widgetPositioning.vertical){
                if(typeof_widgetPositioning.vertical!=='string'){
                    thrownewTypeError('widgetPositioning()verticalvariablemustbeastring');
                }
                _widgetPositioning.vertical=_widgetPositioning.vertical.toLowerCase();
                if(verticalModes.indexOf(_widgetPositioning.vertical)===-1){
                    thrownewTypeError('widgetPositioning()expectsverticalparametertobeoneof('+verticalModes.join(',')+')');
                }
                this._options.widgetPositioning.vertical=_widgetPositioning.vertical;
            }
            this._update();
        };

        TempusDominusBootstrap4.prototype.widgetParent=functionwidgetParent(_widgetParent){
            if(arguments.length===0){
                returnthis._options.widgetParent;
            }

            if(typeof_widgetParent==='string'){
                _widgetParent=$(_widgetParent);
            }

            if(_widgetParent!==null&&typeof_widgetParent!=='string'&&!(_widgetParentinstanceof$)){
                thrownewTypeError('widgetParent()expectsastringorajQueryobjectparameter');
            }

            this._options.widgetParent=_widgetParent;
            if(this.widget){
                this.hide();
                this.show();
            }
        };

        //static


        TempusDominusBootstrap4._jQueryHandleThis=function_jQueryHandleThis(me,option,argument){
            vardata=$(me).data(DateTimePicker.DATA_KEY);
            if((typeofoption==='undefined'?'undefined':_typeof(option))==='object'){
                $.extend({},DateTimePicker.Default,option);
            }

            if(!data){
                data=newTempusDominusBootstrap4($(me),option);
                $(me).data(DateTimePicker.DATA_KEY,data);
            }

            if(typeofoption==='string'){
                if(data[option]===undefined){
                    thrownewError('Nomethodnamed"'+option+'"');
                }
                if(argument===undefined){
                    returndata[option]();
                }else{
                    returndata[option](argument);
                }
            }
        };

        TempusDominusBootstrap4._jQueryInterface=function_jQueryInterface(option,argument){
            if(this.length===1){
                returnTempusDominusBootstrap4._jQueryHandleThis(this[0],option,argument);
            }
            returnthis.each(function(){
                TempusDominusBootstrap4._jQueryHandleThis(this,option,argument);
            });
        };

        returnTempusDominusBootstrap4;
    }(DateTimePicker);

    /**
    *------------------------------------------------------------------------
    *jQuery
    *------------------------------------------------------------------------
    */


    $(document).on(DateTimePicker.Event.CLICK_DATA_API,DateTimePicker.Selector.DATA_TOGGLE,function(){
        var$target=getSelectorFromElement($(this));
        if($target.length===0){
            return;
        }
        TempusDominusBootstrap4._jQueryInterface.call($target,'toggle');
    }).on(DateTimePicker.Event.CHANGE,'.'+DateTimePicker.ClassName.INPUT,function(event){
        var$target=getSelectorFromElement($(this));
        if($target.length===0){
            return;
        }
        TempusDominusBootstrap4._jQueryInterface.call($target,'_change',event);
    }).on(DateTimePicker.Event.BLUR,'.'+DateTimePicker.ClassName.INPUT,function(event){
        var$target=getSelectorFromElement($(this)),
            config=$target.data(DateTimePicker.DATA_KEY);
        if($target.length===0){
            return;
        }
        ///!\FLECTRAFIX:checkon'config'existenceaddedbyflectra
        if(config&&config._options.debug||window.debug){
            return;
        }
        TempusDominusBootstrap4._jQueryInterface.call($target,'hide',event);
    }).on(DateTimePicker.Event.KEYDOWN,'.'+DateTimePicker.ClassName.INPUT,function(event){
        var$target=getSelectorFromElement($(this));
        if($target.length===0){
            return;
        }
        TempusDominusBootstrap4._jQueryInterface.call($target,'_keydown',event);
    }).on(DateTimePicker.Event.KEYUP,'.'+DateTimePicker.ClassName.INPUT,function(event){
        var$target=getSelectorFromElement($(this));
        if($target.length===0){
            return;
        }
        TempusDominusBootstrap4._jQueryInterface.call($target,'_keyup',event);
    }).on(DateTimePicker.Event.FOCUS,'.'+DateTimePicker.ClassName.INPUT,function(event){
        var$target=getSelectorFromElement($(this)),
            config=$target.data(DateTimePicker.DATA_KEY);
        if($target.length===0){
            return;
        }
        ///!\FLECTRAFIX:checkon'config'existenceaddedbyflectra
        if(!(config&&config._options.allowInputToggle)){
            return;
        }
        TempusDominusBootstrap4._jQueryInterface.call($target,'show',event);
    });

    $.fn[DateTimePicker.NAME]=TempusDominusBootstrap4._jQueryInterface;
    $.fn[DateTimePicker.NAME].Constructor=TempusDominusBootstrap4;
    $.fn[DateTimePicker.NAME].noConflict=function(){
        $.fn[DateTimePicker.NAME]=JQUERY_NO_CONFLICT;
        returnTempusDominusBootstrap4._jQueryInterface;
    };

    returnTempusDominusBootstrap4;
}(jQuery);

}();
