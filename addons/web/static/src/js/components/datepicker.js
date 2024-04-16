flectra.define('web.DatePickerOwl',function(require){
    "usestrict";

    constconfig=require('web.config');
    constfield_utils=require('web.field_utils');
    consttime=require('web.time');
    const{useAutofocus}=require('web.custom_hooks');

    const{Component,hooks}=owl;
    const{useExternalListener,useRef,useState}=hooks;

    letdatePickerId=0;

    /**
     *Datepicker
     *
     *ThiscomponentexposestheAPIofthetempusdominusdatepickerlibrary.
     *Assuch,itstemplateisasimpleinputthatwillopentheTDdatepicker
     *whenclickedon.Thecomponentwillalsosynchronizeanyuser-inputvalue
     *withthelibrarywidgetandvice-vera.
     *
     *Forfurtherdetailsregardingtheimplementationofthepickeritself,please
     *refertotheofficialtempusdominusdocumentation(note:allpropsgiven
     *tothiscomponentwillbepassedasargumentstoinstantiatethepickerwidget).
     *@extendsComponent
     */
    classDatePickerextendsComponent{
        constructor(){
            super(...arguments);

            this.inputRef=useRef('input');
            this.state=useState({warning:false});

            this.datePickerId=`o_datepicker_${datePickerId++}`;
            this.typeOfDate='date';

            useAutofocus();
            useExternalListener(window,'scroll',this._onWindowScroll);
        }

        mounted(){
            $(this.el).on('show.datetimepicker',this._onDateTimePickerShow.bind(this));
            $(this.el).on('hide.datetimepicker',this._onDateTimePickerHide.bind(this));
            $(this.el).on('error.datetimepicker',()=>false);

            constpickerOptions=Object.assign({format:this.defaultFormat},this.props);
            this._datetimepicker(pickerOptions);
            this.inputRef.el.value=this._formatDate(this.props.date);
        }

        willUnmount(){
            this._datetimepicker('destroy');
        }

        willUpdateProps(nextProps){
            for(constpropinnextProps){
                this._datetimepicker(prop,nextProps[prop]);
            }
            if(nextProps.date){
                this.inputRef.el.value=this._formatDate(nextProps.date);
            }
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *@returns{string}
         */
        getdefaultFormat(){
            returntime.getLangDateFormat();
        }

        //---------------------------------------------------------------------
        //Private
        //---------------------------------------------------------------------

        /**
         *Handlebootstrapdatetimepickercalls.
         *@private
         *@param{...any}argsanythingthatwillbepassedtothedatetimepickerfunction.
         */
        _datetimepicker(...args){
            this.ignoreBootstrapEvents=true;
            $(this.el).datetimepicker(...args);
            this.ignoreBootstrapEvents=false;
        }

        /**
         *@private
         *@param{moment}date
         *@returns{string}
         */
        _formatDate(date){
            try{
                returnfield_utils.format[this.typeOfDate](date,null,{timezone:false});
            }catch(err){
                returnfalse;
            }
        }

        /**
         *@private
         *@param{string|false}value
         *@returns{moment}
         */
        _parseInput(inputValue){
            try{
                returnfield_utils.parse[this.typeOfDate](inputValue,null,{timezone:false});
            }catch(err){
                returnfalse;
            }
        }

        //---------------------------------------------------------------------
        //Handlers
        //---------------------------------------------------------------------

        /**
         *Reactstothedatetimepickerbeinghidden
         *Usedtounbindthescrolleventfromthedatetimepicker
         *@private
         */
        _onDateTimePickerHide(){
            if(this.ignoreBootstrapEvents){
                return;
            }
            constdate=this._parseInput(this.inputRef.el.value);
            this.state.warning=date.format('YYYY-MM-DD')>moment().format('YYYY-MM-DD');
            this.trigger('datetime-changed',{date});
        }

        /**
         *Reactstothedatetimepickerbeingshown
         *Couldset/verifyourwidgetvalue
         *Andsubsequentlyupdatethedatetimepicker
         *@private
         */
        _onDateTimePickerShow(){
            if(this.ignoreBootstrapEvents){
                return;
            }
            this.inputRef.el.select();
        }

        /**
         *@private
         */
        _onInputClick(){
            this._datetimepicker('toggle');
        }

        /**
         *@private
         */
        _onInputChange(){
            constdate=this._parseInput(this.inputRef.el.value);
            if(date){
                this.state.warning=date.format('YYYY-MM-DD')>moment().format('YYYY-MM-DD');
                this.trigger('datetime-changed',{date});
            }else{
                this.inputRef.el.value=this._formatDate(this.props.date);
            }
        }

        /**
         *@private
         */
        _onWindowScroll(ev){
            if(!config.device.isIOS&&ev.target!==this.inputRef.el){
                this._datetimepicker('hide');
            }
        }
    }

    DatePicker.defaultProps={
        calendarWeeks:true,
        icons:{
            clear:'fafa-delete',
            close:'fafa-checkprimary',
            date:'fafa-calendar',
            down:'fafa-chevron-down',
            next:'fafa-chevron-right',
            previous:'fafa-chevron-left',
            time:'fafa-clock-o',
            today:'fafa-calendar-check-o',
            up:'fafa-chevron-up',
        },
        getlocale(){returnmoment.locale();},
        maxDate:moment({y:9999,M:11,d:31}),
        minDate:moment({y:1000}),
        useCurrent:false,
        widgetParent:'body',
    };
    DatePicker.props={
        //Actualdatevalue
        date:moment,
        //Otherprops
        buttons:{
            type:Object,
            shape:{
                showClear:Boolean,
                showClose:Boolean,
                showToday:Boolean,
            },
            optional:1,
        },
        calendarWeeks:Boolean,
        format:{type:String,optional:1},
        icons:{
            type:Object,
            shape:{
                clear:String,
                close:String,
                date:String,
                down:String,
                next:String,
                previous:String,
                time:String,
                today:String,
                up:String,
            },
        },
        keyBinds:{validate:kb=>typeofkb==='object'||kb===null,optional:1},
        locale:String,
        maxDate:moment,
        minDate:moment,
        readonly:{type:Boolean,optional:1},
        useCurrent:Boolean,
        widgetParent:String,
    };
    DatePicker.template='web.DatePicker';

    /**
     *Date/timepicker
     *
     *SimilartotheDatePickercomponent,addingthehandlingofmorespecific
     *timevalues:hour-minute-second.
     *
     *Onceagain,refertothetempusdominusdocumentationforimplementation
     *details.
     *@extendsDatePicker
     */
    classDateTimePickerextendsDatePicker{
        constructor(){
            super(...arguments);

            this.typeOfDate='datetime';
        }

        /**
         *@override
         */
        getdefaultFormat(){
            returntime.getLangDatetimeFormat();
        }
    }

    DateTimePicker.defaultProps=Object.assign(Object.create(DatePicker.defaultProps),{
        buttons:{
            showClear:false,
            showClose:true,
            showToday:false,
        },
    });

    return{
        DatePicker,
        DateTimePicker,
    };
});
