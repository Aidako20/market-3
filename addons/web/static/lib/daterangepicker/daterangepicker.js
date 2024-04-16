/**
*@version:3.0.5
*@author:DanGrossmanhttp://www.dangrossman.info/
*@copyright:Copyright(c)2012-2019DanGrossman.Allrightsreserved.
*@license:LicensedundertheMITlicense.Seehttp://www.opensource.org/licenses/mit-license.php
*@website:http://www.daterangepicker.com/
*/
//FollowingtheUMDtemplatehttps://github.com/umdjs/umd/blob/master/templates/returnExportsGlobal.js
(function(root,factory){
    if(typeofdefine==='function'&&define.amd){
        //AMD.Makegloballyavailableaswell
        define(['moment','jquery'],function(moment,jquery){
            if(!jquery.fn)jquery.fn={};//webpackserverrendering
            if(typeofmoment!=='function'&&moment.default)moment=moment.default
            returnfactory(moment,jquery);
        });
    }elseif(typeofmodule==='object'&&module.exports){
        //Node/Browserify
        //isomorphicissue
        varjQuery=(typeofwindow!='undefined')?window.jQuery:undefined;
        if(!jQuery){
            jQuery=require('jquery');
            if(!jQuery.fn)jQuery.fn={};
        }
        varmoment=(typeofwindow!='undefined'&&typeofwindow.moment!='undefined')?window.moment:require('moment');
        module.exports=factory(moment,jQuery);
    }else{
        //Browserglobals
        root.daterangepicker=factory(root.moment,root.jQuery);
    }
}(this,function(moment,$){
    varDateRangePicker=function(element,options,cb){

        //defaultsettingsforoptions
        this.parentEl='body';
        this.element=$(element);
        this.startDate=moment().startOf('day');
        this.endDate=moment().endOf('day');
        this.minDate=false;
        this.maxDate=false;
        this.maxSpan=false;
        this.autoApply=false;
        this.singleDatePicker=false;
        this.showDropdowns=false;
        this.minYear=moment().subtract(100,'year').format('YYYY');
        this.maxYear=moment().add(100,'year').format('YYYY');
        this.showWeekNumbers=false;
        this.showISOWeekNumbers=false;
        this.showCustomRangeLabel=true;
        this.timePicker=false;
        this.timePicker24Hour=false;
        this.timePickerIncrement=1;
        this.timePickerSeconds=false;
        this.linkedCalendars=true;
        this.autoUpdateInput=true;
        this.alwaysShowCalendars=false;
        this.ranges={};

        this.opens='right';
        if(this.element.hasClass('pull-right'))
            this.opens='left';

        this.drops='down';
        if(this.element.hasClass('dropup'))
            this.drops='up';

        this.buttonClasses='btnbtn-sm';
        this.applyButtonClasses='btn-primary';
        this.cancelButtonClasses='btn-default';

        this.locale={
            direction:'ltr',
            format:moment.localeData().longDateFormat('L'),
            separator:'-',
            applyLabel:'Apply',
            cancelLabel:'Cancel',
            weekLabel:'W',
            customRangeLabel:'CustomRange',
            daysOfWeek:moment.weekdaysMin(),
            monthNames:moment.monthsShort(),
            firstDay:moment.localeData().firstDayOfWeek()
        };

        this.callback=function(){};

        //somestateinformation
        this.isShowing=false;
        this.leftCalendar={};
        this.rightCalendar={};

        //customoptionsfromuser
        if(typeofoptions!=='object'||options===null)
            options={};

        //allowsettingoptionswithdataattributes
        //data-apioptionswillbeoverwrittenwithcustomjavascriptoptions
        options=$.extend(this.element.data(),options);

        //htmltemplateforthepickerUI
        if(typeofoptions.template!=='string'&&!(options.templateinstanceof$))
            options.template=
            '<divclass="daterangepicker">'+
                '<divclass="ranges"></div>'+
                '<divclass="drp-calendarleft">'+
                    '<divclass="calendar-table"></div>'+
                    '<divclass="calendar-time"></div>'+
                '</div>'+
                '<divclass="drp-calendarright">'+
                    '<divclass="calendar-table"></div>'+
                    '<divclass="calendar-time"></div>'+
                '</div>'+
                '<divclass="drp-buttons">'+
                    '<spanclass="drp-selected"></span>'+
                    '<buttonclass="cancelBtn"type="button"></button>'+
                    '<buttonclass="applyBtn"disabled="disabled"type="button"></button>'+
                '</div>'+
            '</div>';

        this.parentEl=(options.parentEl&&$(options.parentEl).length)?$(options.parentEl):$(this.parentEl);
        this.container=$(options.template).appendTo(this.parentEl);

        //
        //handleallthepossibleoptionsoverridingdefaults
        //

        if(typeofoptions.locale==='object'){

            if(typeofoptions.locale.direction==='string')
                this.locale.direction=options.locale.direction;

            if(typeofoptions.locale.format==='string')
                this.locale.format=options.locale.format;

            if(typeofoptions.locale.separator==='string')
                this.locale.separator=options.locale.separator;

            if(typeofoptions.locale.daysOfWeek==='object')
                this.locale.daysOfWeek=options.locale.daysOfWeek.slice();

            if(typeofoptions.locale.monthNames==='object')
              this.locale.monthNames=options.locale.monthNames.slice();

            if(typeofoptions.locale.firstDay==='number')
              this.locale.firstDay=options.locale.firstDay;

            if(typeofoptions.locale.applyLabel==='string')
              this.locale.applyLabel=options.locale.applyLabel;

            if(typeofoptions.locale.cancelLabel==='string')
              this.locale.cancelLabel=options.locale.cancelLabel;

            if(typeofoptions.locale.weekLabel==='string')
              this.locale.weekLabel=options.locale.weekLabel;

            if(typeofoptions.locale.customRangeLabel==='string'){
                //Supportunicodecharsinthecustomrangename.
                varelem=document.createElement('textarea');
                elem.innerHTML=options.locale.customRangeLabel;
                varrangeHtml=elem.value;
                this.locale.customRangeLabel=rangeHtml;
            }
        }
        this.container.addClass(this.locale.direction);

        if(typeofoptions.startDate==='string')
            this.startDate=moment(options.startDate,this.locale.format);

        if(typeofoptions.endDate==='string')
            this.endDate=moment(options.endDate,this.locale.format);

        if(typeofoptions.minDate==='string')
            this.minDate=moment(options.minDate,this.locale.format);

        if(typeofoptions.maxDate==='string')
            this.maxDate=moment(options.maxDate,this.locale.format);

        if(typeofoptions.startDate==='object')
            this.startDate=moment(options.startDate);

        if(typeofoptions.endDate==='object')
            this.endDate=moment(options.endDate);

        if(typeofoptions.minDate==='object')
            this.minDate=moment(options.minDate);

        if(typeofoptions.maxDate==='object')
            this.maxDate=moment(options.maxDate);

        //sanitycheckforbadoptions
        if(this.minDate&&this.startDate.isBefore(this.minDate))
            this.startDate=this.minDate.clone();

        //sanitycheckforbadoptions
        if(this.maxDate&&this.endDate.isAfter(this.maxDate))
            this.endDate=this.maxDate.clone();

        if(typeofoptions.applyButtonClasses==='string')
            this.applyButtonClasses=options.applyButtonClasses;

        if(typeofoptions.applyClass==='string')//backwardscompat
            this.applyButtonClasses=options.applyClass;

        if(typeofoptions.cancelButtonClasses==='string')
            this.cancelButtonClasses=options.cancelButtonClasses;

        if(typeofoptions.cancelClass==='string')//backwardscompat
            this.cancelButtonClasses=options.cancelClass;

        if(typeofoptions.maxSpan==='object')
            this.maxSpan=options.maxSpan;

        if(typeofoptions.dateLimit==='object')//backwardscompat
            this.maxSpan=options.dateLimit;

        if(typeofoptions.opens==='string')
            this.opens=options.opens;

        if(typeofoptions.drops==='string')
            this.drops=options.drops;

        if(typeofoptions.showWeekNumbers==='boolean')
            this.showWeekNumbers=options.showWeekNumbers;

        if(typeofoptions.showISOWeekNumbers==='boolean')
            this.showISOWeekNumbers=options.showISOWeekNumbers;

        if(typeofoptions.buttonClasses==='string')
            this.buttonClasses=options.buttonClasses;

        if(typeofoptions.buttonClasses==='object')
            this.buttonClasses=options.buttonClasses.join('');

        if(typeofoptions.showDropdowns==='boolean')
            this.showDropdowns=options.showDropdowns;

        if(typeofoptions.minYear==='number')
            this.minYear=options.minYear;

        if(typeofoptions.maxYear==='number')
            this.maxYear=options.maxYear;

        if(typeofoptions.showCustomRangeLabel==='boolean')
            this.showCustomRangeLabel=options.showCustomRangeLabel;

        if(typeofoptions.singleDatePicker==='boolean'){
            this.singleDatePicker=options.singleDatePicker;
            if(this.singleDatePicker)
                this.endDate=this.startDate.clone();
        }

        if(typeofoptions.timePicker==='boolean')
            this.timePicker=options.timePicker;

        if(typeofoptions.timePickerSeconds==='boolean')
            this.timePickerSeconds=options.timePickerSeconds;

        if(typeofoptions.timePickerIncrement==='number')
            this.timePickerIncrement=options.timePickerIncrement;

        if(typeofoptions.timePicker24Hour==='boolean')
            this.timePicker24Hour=options.timePicker24Hour;

        if(typeofoptions.autoApply==='boolean')
            this.autoApply=options.autoApply;

        if(typeofoptions.autoUpdateInput==='boolean')
            this.autoUpdateInput=options.autoUpdateInput;

        if(typeofoptions.linkedCalendars==='boolean')
            this.linkedCalendars=options.linkedCalendars;

        if(typeofoptions.isInvalidDate==='function')
            this.isInvalidDate=options.isInvalidDate;

        if(typeofoptions.isCustomDate==='function')
            this.isCustomDate=options.isCustomDate;

        if(typeofoptions.alwaysShowCalendars==='boolean')
            this.alwaysShowCalendars=options.alwaysShowCalendars;

        //updatedaynamesordertofirstDay
        if(this.locale.firstDay!=0){
            variterator=this.locale.firstDay;
            while(iterator>0){
                this.locale.daysOfWeek.push(this.locale.daysOfWeek.shift());
                iterator--;
            }
        }

        varstart,end,range;

        //ifnostart/enddatesset,checkifaninputelementcontainsinitialvalues
        if(typeofoptions.startDate==='undefined'&&typeofoptions.endDate==='undefined'){
            if($(this.element).is(':text')){
                varval=$(this.element).val(),
                    split=val.split(this.locale.separator);

                start=end=null;

                if(split.length==2){
                    start=moment(split[0],this.locale.format);
                    end=moment(split[1],this.locale.format);
                }elseif(this.singleDatePicker&&val!==""){
                    start=moment(val,this.locale.format);
                    end=moment(val,this.locale.format);
                }
                if(start!==null&&end!==null){
                    this.setStartDate(start);
                    this.setEndDate(end);
                }
            }
        }

        if(typeofoptions.ranges==='object'){
            for(rangeinoptions.ranges){

                if(typeofoptions.ranges[range][0]==='string')
                    start=moment(options.ranges[range][0],this.locale.format);
                else
                    start=moment(options.ranges[range][0]);

                if(typeofoptions.ranges[range][1]==='string')
                    end=moment(options.ranges[range][1],this.locale.format);
                else
                    end=moment(options.ranges[range][1]);

                //IfthestartorenddateexceedthoseallowedbytheminDateormaxSpan
                //options,shortentherangetotheallowableperiod.
                if(this.minDate&&start.isBefore(this.minDate))
                    start=this.minDate.clone();

                varmaxDate=this.maxDate;
                if(this.maxSpan&&maxDate&&start.clone().add(this.maxSpan).isAfter(maxDate))
                    maxDate=start.clone().add(this.maxSpan);
                if(maxDate&&end.isAfter(maxDate))
                    end=maxDate.clone();

                //Iftheendoftherangeisbeforetheminimumorthestartoftherangeis
                //afterthemaximum,don'tdisplaythisrangeoptionatall.
                if((this.minDate&&end.isBefore(this.minDate,this.timepicker?'minute':'day'))
                  ||(maxDate&&start.isAfter(maxDate,this.timepicker?'minute':'day')))
                    continue;

                //Supportunicodecharsintherangenames.
                varelem=document.createElement('textarea');
                elem.innerHTML=range;
                varrangeHtml=elem.value;

                this.ranges[rangeHtml]=[start,end];
            }

            varlist='<ul>';
            for(rangeinthis.ranges){
                list+='<lidata-range-key="'+range+'">'+range+'</li>';
            }
            if(this.showCustomRangeLabel){
                list+='<lidata-range-key="'+this.locale.customRangeLabel+'">'+this.locale.customRangeLabel+'</li>';
            }
            list+='</ul>';
            this.container.find('.ranges').prepend(list);
        }

        if(typeofcb==='function'){
            this.callback=cb;
        }

        if(!this.timePicker){
            this.startDate=this.startDate.startOf('day');
            this.endDate=this.endDate.endOf('day');
            this.container.find('.calendar-time').hide();
        }

        //can'tbeusedtogetherfornow
        if(this.timePicker&&this.autoApply)
            this.autoApply=false;

        if(this.autoApply){
            this.container.addClass('auto-apply');
        }

        if(typeofoptions.ranges==='object')
            this.container.addClass('show-ranges');

        if(this.singleDatePicker){
            this.container.addClass('single');
            this.container.find('.drp-calendar.left').addClass('single');
            this.container.find('.drp-calendar.left').show();
            this.container.find('.drp-calendar.right').hide();
            if(!this.timePicker){
                this.container.addClass('auto-apply');
            }
        }

        if((typeofoptions.ranges==='undefined'&&!this.singleDatePicker)||this.alwaysShowCalendars){
            this.container.addClass('show-calendar');
        }

        this.container.addClass('opens'+this.opens);

        //applyCSSclassesandlabelstobuttons
        this.container.find('.applyBtn,.cancelBtn').addClass(this.buttonClasses);
        if(this.applyButtonClasses.length)
            this.container.find('.applyBtn').addClass(this.applyButtonClasses);
        if(this.cancelButtonClasses.length)
            this.container.find('.cancelBtn').addClass(this.cancelButtonClasses);
        this.container.find('.applyBtn').html(this.locale.applyLabel);
        this.container.find('.cancelBtn').html(this.locale.cancelLabel);

        //
        //eventlisteners
        //

        this.container.find('.drp-calendar')
            .on('click.daterangepicker','.prev',$.proxy(this.clickPrev,this))
            .on('click.daterangepicker','.next',$.proxy(this.clickNext,this))
            .on('mousedown.daterangepicker','td.available',$.proxy(this.clickDate,this))
            .on('mouseenter.daterangepicker','td.available',$.proxy(this.hoverDate,this))
            .on('change.daterangepicker','select.yearselect',$.proxy(this.monthOrYearChanged,this))
            .on('change.daterangepicker','select.monthselect',$.proxy(this.monthOrYearChanged,this))
            .on('change.daterangepicker','select.hourselect,select.minuteselect,select.secondselect,select.ampmselect',$.proxy(this.timeChanged,this))

        this.container.find('.ranges')
            .on('click.daterangepicker','li',$.proxy(this.clickRange,this))

        this.container.find('.drp-buttons')
            .on('click.daterangepicker','button.applyBtn',$.proxy(this.clickApply,this))
            .on('click.daterangepicker','button.cancelBtn',$.proxy(this.clickCancel,this))

        if(this.element.is('input')||this.element.is('button')){
            this.element.on({
                'click.daterangepicker':$.proxy(this.show,this),
                'focus.daterangepicker':$.proxy(this.show,this),
                'keyup.daterangepicker':$.proxy(this.elementChanged,this),
                'keydown.daterangepicker':$.proxy(this.keydown,this)//IE11compatibility
            });
        }else{
            this.element.on('click.daterangepicker',$.proxy(this.toggle,this));
            this.element.on('keydown.daterangepicker',$.proxy(this.toggle,this));
        }

        //
        //ifattachedtoatextinput,settheinitialvalue
        //

        this.updateElement();

    };

    DateRangePicker.prototype={

        constructor:DateRangePicker,

        setStartDate:function(startDate){
            if(typeofstartDate==='string')
                this.startDate=moment(startDate,this.locale.format);

            if(typeofstartDate==='object')
                this.startDate=moment(startDate);

            if(!this.timePicker)
                this.startDate=this.startDate.startOf('day');

            if(this.timePicker&&this.timePickerIncrement)
                this.startDate.minute(Math.round(this.startDate.minute()/this.timePickerIncrement)*this.timePickerIncrement);

            if(this.minDate&&this.startDate.isBefore(this.minDate)){
                this.startDate=this.minDate.clone();
                if(this.timePicker&&this.timePickerIncrement)
                    this.startDate.minute(Math.round(this.startDate.minute()/this.timePickerIncrement)*this.timePickerIncrement);
            }

            if(this.maxDate&&this.startDate.isAfter(this.maxDate)){
                this.startDate=this.maxDate.clone();
                if(this.timePicker&&this.timePickerIncrement)
                    this.startDate.minute(Math.floor(this.startDate.minute()/this.timePickerIncrement)*this.timePickerIncrement);
            }

            if(!this.isShowing)
                this.updateElement();

            this.updateMonthsInView();
        },

        setEndDate:function(endDate){
            if(typeofendDate==='string')
                this.endDate=moment(endDate,this.locale.format);

            if(typeofendDate==='object')
                this.endDate=moment(endDate);

            if(!this.timePicker)
                this.endDate=this.endDate.endOf('day');

            if(this.timePicker&&this.timePickerIncrement)
                this.endDate.minute(Math.round(this.endDate.minute()/this.timePickerIncrement)*this.timePickerIncrement);

            if(this.endDate.isBefore(this.startDate))
                this.endDate=this.startDate.clone();

            if(this.maxDate&&this.endDate.isAfter(this.maxDate))
                this.endDate=this.maxDate.clone();

            if(this.maxSpan&&this.startDate.clone().add(this.maxSpan).isBefore(this.endDate))
                this.endDate=this.startDate.clone().add(this.maxSpan);

            this.previousRightTime=this.endDate.clone();

            this.container.find('.drp-selected').html(this.startDate.format(this.locale.format)+this.locale.separator+this.endDate.format(this.locale.format));

            if(!this.isShowing)
                this.updateElement();

            this.updateMonthsInView();
        },

        isInvalidDate:function(){
            returnfalse;
        },

        isCustomDate:function(){
            returnfalse;
        },

        updateView:function(){
            if(this.timePicker){
                this.renderTimePicker('left');
                this.renderTimePicker('right');
                if(!this.endDate){
                    this.container.find('.right.calendar-timeselect').attr('disabled','disabled').addClass('disabled');
                }else{
                    this.container.find('.right.calendar-timeselect').removeAttr('disabled').removeClass('disabled');
                }
            }
            if(this.endDate)
                this.container.find('.drp-selected').html(this.startDate.format(this.locale.format)+this.locale.separator+this.endDate.format(this.locale.format));
            this.updateMonthsInView();
            this.updateCalendars();
            this.updateFormInputs();
        },

        updateMonthsInView:function(){
            if(this.endDate){

                //ifbothdatesarevisiblealready,donothing
                if(!this.singleDatePicker&&this.leftCalendar.month&&this.rightCalendar.month&&
                    (this.startDate.format('YYYY-MM')==this.leftCalendar.month.format('YYYY-MM')||this.startDate.format('YYYY-MM')==this.rightCalendar.month.format('YYYY-MM'))
                    &&
                    (this.endDate.format('YYYY-MM')==this.leftCalendar.month.format('YYYY-MM')||this.endDate.format('YYYY-MM')==this.rightCalendar.month.format('YYYY-MM'))
                    ){
                    return;
                }

                this.leftCalendar.month=this.startDate.clone().date(2);
                if(!this.linkedCalendars&&(this.endDate.month()!=this.startDate.month()||this.endDate.year()!=this.startDate.year())){
                    this.rightCalendar.month=this.endDate.clone().date(2);
                }else{
                    this.rightCalendar.month=this.startDate.clone().date(2).add(1,'month');
                }

            }else{
                if(this.leftCalendar.month.format('YYYY-MM')!=this.startDate.format('YYYY-MM')&&this.rightCalendar.month.format('YYYY-MM')!=this.startDate.format('YYYY-MM')){
                    this.leftCalendar.month=this.startDate.clone().date(2);
                    this.rightCalendar.month=this.startDate.clone().date(2).add(1,'month');
                }
            }
            if(this.maxDate&&this.linkedCalendars&&!this.singleDatePicker&&this.rightCalendar.month>this.maxDate){
              this.rightCalendar.month=this.maxDate.clone().date(2);
              this.leftCalendar.month=this.maxDate.clone().date(2).subtract(1,'month');
            }
        },

        updateCalendars:function(){

            if(this.timePicker){
                varhour,minute,second;
                if(this.endDate){
                    hour=parseInt(this.container.find('.left.hourselect').val(),10);
                    minute=parseInt(this.container.find('.left.minuteselect').val(),10);
                    if(isNaN(minute)){
                        minute=parseInt(this.container.find('.left.minuteselectoption:last').val(),10);
                    }
                    second=this.timePickerSeconds?parseInt(this.container.find('.left.secondselect').val(),10):0;
                    if(!this.timePicker24Hour){
                        varampm=this.container.find('.left.ampmselect').val();
                        if(ampm==='PM'&&hour<12)
                            hour+=12;
                        if(ampm==='AM'&&hour===12)
                            hour=0;
                    }
                }else{
                    hour=parseInt(this.container.find('.right.hourselect').val(),10);
                    minute=parseInt(this.container.find('.right.minuteselect').val(),10);
                    if(isNaN(minute)){
                        minute=parseInt(this.container.find('.right.minuteselectoption:last').val(),10);
                    }
                    second=this.timePickerSeconds?parseInt(this.container.find('.right.secondselect').val(),10):0;
                    if(!this.timePicker24Hour){
                        varampm=this.container.find('.right.ampmselect').val();
                        if(ampm==='PM'&&hour<12)
                            hour+=12;
                        if(ampm==='AM'&&hour===12)
                            hour=0;
                    }
                }
                this.leftCalendar.month.hour(hour).minute(minute).second(second);
                this.rightCalendar.month.hour(hour).minute(minute).second(second);
            }

            this.renderCalendar('left');
            this.renderCalendar('right');

            //highlightanypredefinedrangematchingthecurrentstartandenddates
            this.container.find('.rangesli').removeClass('active');
            if(this.endDate==null)return;

            this.calculateChosenLabel();
        },

        renderCalendar:function(side){

            //
            //Buildthematrixofdatesthatwillpopulatethecalendar
            //

            varcalendar=side=='left'?this.leftCalendar:this.rightCalendar;
            varmonth=calendar.month.month();
            varyear=calendar.month.year();
            varhour=calendar.month.hour();
            varminute=calendar.month.minute();
            varsecond=calendar.month.second();
            vardaysInMonth=moment([year,month]).daysInMonth();
            varfirstDay=moment([year,month,1]);
            varlastDay=moment([year,month,daysInMonth]);
            varlastMonth=moment(firstDay).subtract(1,'month').month();
            varlastYear=moment(firstDay).subtract(1,'month').year();
            vardaysInLastMonth=moment([lastYear,lastMonth]).daysInMonth();
            vardayOfWeek=firstDay.day();

            //initializea6rowsx7columnsarrayforthecalendar
            varcalendar=[];
            calendar.firstDay=firstDay;
            calendar.lastDay=lastDay;

            for(vari=0;i<6;i++){
                calendar[i]=[];
            }

            //populatethecalendarwithdateobjects
            varstartDay=daysInLastMonth-dayOfWeek+this.locale.firstDay+1;
            if(startDay>daysInLastMonth)
                startDay-=7;

            if(dayOfWeek==this.locale.firstDay)
                startDay=daysInLastMonth-6;

            varcurDate=moment([lastYear,lastMonth,startDay,12,minute,second]);

            varcol,row;
            for(vari=0,col=0,row=0;i<42;i++,col++,curDate=moment(curDate).add(24,'hour')){
                if(i>0&&col%7===0){
                    col=0;
                    row++;
                }
                calendar[row][col]=curDate.clone().hour(hour).minute(minute).second(second);
                curDate.hour(12);

                if(this.minDate&&calendar[row][col].format('YYYY-MM-DD')==this.minDate.format('YYYY-MM-DD')&&calendar[row][col].isBefore(this.minDate)&&side=='left'){
                    calendar[row][col]=this.minDate.clone();
                }

                if(this.maxDate&&calendar[row][col].format('YYYY-MM-DD')==this.maxDate.format('YYYY-MM-DD')&&calendar[row][col].isAfter(this.maxDate)&&side=='right'){
                    calendar[row][col]=this.maxDate.clone();
                }

            }

            //makethecalendarobjectavailabletohoverDate/clickDate
            if(side=='left'){
                this.leftCalendar.calendar=calendar;
            }else{
                this.rightCalendar.calendar=calendar;
            }

            //
            //Displaythecalendar
            //

            varminDate=side=='left'?this.minDate:this.startDate;
            varmaxDate=this.maxDate;
            varselected=side=='left'?this.startDate:this.endDate;
            vararrow=this.locale.direction=='ltr'?{left:'chevron-left',right:'chevron-right'}:{left:'chevron-right',right:'chevron-left'};

            varhtml='<tableclass="table-condensed">';
            html+='<thead>';
            html+='<tr>';

            //addemptycellforweeknumber
            if(this.showWeekNumbers||this.showISOWeekNumbers)
                html+='<th></th>';

            if((!minDate||minDate.isBefore(calendar.firstDay))&&(!this.linkedCalendars||side=='left')){
                html+='<thclass="prevavailable"><span></span></th>';
            }else{
                html+='<th></th>';
            }

            vardateHtml=this.locale.monthNames[calendar[1][1].month()]+calendar[1][1].format("YYYY");

            if(this.showDropdowns){
                varcurrentMonth=calendar[1][1].month();
                varcurrentYear=calendar[1][1].year();
                varmaxYear=(maxDate&&maxDate.year())||(this.maxYear);
                varminYear=(minDate&&minDate.year())||(this.minYear);
                varinMinYear=currentYear==minYear;
                varinMaxYear=currentYear==maxYear;

                varmonthHtml='<selectclass="monthselect">';
                for(varm=0;m<12;m++){
                    if((!inMinYear||(minDate&&m>=minDate.month()))&&(!inMaxYear||(maxDate&&m<=maxDate.month()))){
                        monthHtml+="<optionvalue='"+m+"'"+
                            (m===currentMonth?"selected='selected'":"")+
                            ">"+this.locale.monthNames[m]+"</option>";
                    }else{
                        monthHtml+="<optionvalue='"+m+"'"+
                            (m===currentMonth?"selected='selected'":"")+
                            "disabled='disabled'>"+this.locale.monthNames[m]+"</option>";
                    }
                }
                monthHtml+="</select>";

                varyearHtml='<selectclass="yearselect">';
                for(vary=minYear;y<=maxYear;y++){
                    yearHtml+='<optionvalue="'+y+'"'+
                        (y===currentYear?'selected="selected"':'')+
                        '>'+y+'</option>';
                }
                yearHtml+='</select>';

                dateHtml=monthHtml+yearHtml;
            }

            html+='<thcolspan="5"class="month">'+dateHtml+'</th>';
            if((!maxDate||maxDate.isAfter(calendar.lastDay))&&(!this.linkedCalendars||side=='right'||this.singleDatePicker)){
                html+='<thclass="nextavailable"><span></span></th>';
            }else{
                html+='<th></th>';
            }

            html+='</tr>';
            html+='<tr>';

            //addweeknumberlabel
            if(this.showWeekNumbers||this.showISOWeekNumbers)
                html+='<thclass="week">'+this.locale.weekLabel+'</th>';

            $.each(this.locale.daysOfWeek,function(index,dayOfWeek){
                html+='<th>'+dayOfWeek+'</th>';
            });

            html+='</tr>';
            html+='</thead>';
            html+='<tbody>';

            //adjustmaxDatetoreflectthemaxSpansettinginorderto
            //greyoutenddatesbeyondthemaxSpan
            if(this.endDate==null&&this.maxSpan){
                varmaxLimit=this.startDate.clone().add(this.maxSpan).endOf('day');
                if(!maxDate||maxLimit.isBefore(maxDate)){
                    maxDate=maxLimit;
                }
            }

            for(varrow=0;row<6;row++){
                html+='<tr>';

                //addweeknumber
                if(this.showWeekNumbers)
                    html+='<tdclass="week">'+calendar[row][0].week()+'</td>';
                elseif(this.showISOWeekNumbers)
                    html+='<tdclass="week">'+calendar[row][0].isoWeek()+'</td>';

                for(varcol=0;col<7;col++){

                    varclasses=[];

                    //highlighttoday'sdate
                    if(calendar[row][col].isSame(newDate(),"day"))
                        classes.push('today');

                    //highlightweekends
                    if(calendar[row][col].isoWeekday()>5)
                        classes.push('weekend');

                    //greyoutthedatesinothermonthsdisplayedatbeginningandendofthiscalendar
                    if(calendar[row][col].month()!=calendar[1][1].month())
                        classes.push('off','ends');

                    //don'tallowselectionofdatesbeforetheminimumdate
                    if(this.minDate&&calendar[row][col].isBefore(this.minDate,'day'))
                        classes.push('off','disabled');

                    //don'tallowselectionofdatesafterthemaximumdate
                    if(maxDate&&calendar[row][col].isAfter(maxDate,'day'))
                        classes.push('off','disabled');

                    //don'tallowselectionofdateifacustomfunctiondecidesit'sinvalid
                    if(this.isInvalidDate(calendar[row][col]))
                        classes.push('off','disabled');

                    //highlightthecurrentlyselectedstartdate
                    if(calendar[row][col].format('YYYY-MM-DD')==this.startDate.format('YYYY-MM-DD'))
                        classes.push('active','start-date');

                    //highlightthecurrentlyselectedenddate
                    if(this.endDate!=null&&calendar[row][col].format('YYYY-MM-DD')==this.endDate.format('YYYY-MM-DD'))
                        classes.push('active','end-date');

                    //highlightdatesin-betweentheselecteddates
                    if(this.endDate!=null&&calendar[row][col]>this.startDate&&calendar[row][col]<this.endDate)
                        classes.push('in-range');

                    //applycustomclassesforthisdate
                    varisCustom=this.isCustomDate(calendar[row][col]);
                    if(isCustom!==false){
                        if(typeofisCustom==='string')
                            classes.push(isCustom);
                        else
                            Array.prototype.push.apply(classes,isCustom);
                    }

                    varcname='',disabled=false;
                    for(vari=0;i<classes.length;i++){
                        cname+=classes[i]+'';
                        if(classes[i]=='disabled')
                            disabled=true;
                    }
                    if(!disabled)
                        cname+='available';

                    html+='<tdclass="'+cname.replace(/^\s+|\s+$/g,'')+'"data-title="'+'r'+row+'c'+col+'">'+calendar[row][col].date()+'</td>';

                }
                html+='</tr>';
            }

            html+='</tbody>';
            html+='</table>';

            this.container.find('.drp-calendar.'+side+'.calendar-table').html(html);

        },

        renderTimePicker:function(side){

            //Don'tbotherupdatingthetimepickerifit'scurrentlydisabled
            //becauseanenddatehasn'tbeenclickedyet
            if(side=='right'&&!this.endDate)return;

            varhtml,selected,minDate,maxDate=this.maxDate;

            if(this.maxSpan&&(!this.maxDate||this.startDate.clone().add(this.maxSpan).isBefore(this.maxDate)))
                maxDate=this.startDate.clone().add(this.maxSpan);

            if(side=='left'){
                selected=this.startDate.clone();
                minDate=this.minDate;
            }elseif(side=='right'){
                selected=this.endDate.clone();
                minDate=this.startDate;

                //Preservethetimealreadyselected
                vartimeSelector=this.container.find('.drp-calendar.right.calendar-time');
                if(timeSelector.html()!=''){

                    selected.hour(!isNaN(selected.hour())?selected.hour():timeSelector.find('.hourselectoption:selected').val());
                    selected.minute(!isNaN(selected.minute())?selected.minute():timeSelector.find('.minuteselectoption:selected').val());
                    selected.second(!isNaN(selected.second())?selected.second():timeSelector.find('.secondselectoption:selected').val());

                    if(!this.timePicker24Hour){
                        varampm=timeSelector.find('.ampmselectoption:selected').val();
                        if(ampm==='PM'&&selected.hour()<12)
                            selected.hour(selected.hour()+12);
                        if(ampm==='AM'&&selected.hour()===12)
                            selected.hour(0);
                    }

                }

                if(selected.isBefore(this.startDate))
                    selected=this.startDate.clone();

                if(maxDate&&selected.isAfter(maxDate))
                    selected=maxDate.clone();

            }

            //
            //hours
            //

            html='<selectclass="hourselect">';

            varstart=this.timePicker24Hour?0:1;
            varend=this.timePicker24Hour?23:12;

            for(vari=start;i<=end;i++){
                vari_in_24=i;
                if(!this.timePicker24Hour)
                    i_in_24=selected.hour()>=12?(i==12?12:i+12):(i==12?0:i);

                vartime=selected.clone().hour(i_in_24);
                vardisabled=false;
                if(minDate&&time.minute(59).isBefore(minDate))
                    disabled=true;
                if(maxDate&&time.minute(0).isAfter(maxDate))
                    disabled=true;

                if(i_in_24==selected.hour()&&!disabled){
                    html+='<optionvalue="'+i+'"selected="selected">'+i+'</option>';
                }elseif(disabled){
                    html+='<optionvalue="'+i+'"disabled="disabled"class="disabled">'+i+'</option>';
                }else{
                    html+='<optionvalue="'+i+'">'+i+'</option>';
                }
            }

            html+='</select>';

            //
            //minutes
            //

            html+=':<selectclass="minuteselect">';

            for(vari=0;i<60;i+=this.timePickerIncrement){
                varpadded=i<10?'0'+i:i;
                vartime=selected.clone().minute(i);

                vardisabled=false;
                if(minDate&&time.second(59).isBefore(minDate))
                    disabled=true;
                if(maxDate&&time.second(0).isAfter(maxDate))
                    disabled=true;

                if(selected.minute()==i&&!disabled){
                    html+='<optionvalue="'+i+'"selected="selected">'+padded+'</option>';
                }elseif(disabled){
                    html+='<optionvalue="'+i+'"disabled="disabled"class="disabled">'+padded+'</option>';
                }else{
                    html+='<optionvalue="'+i+'">'+padded+'</option>';
                }
            }

            html+='</select>';

            //
            //seconds
            //

            if(this.timePickerSeconds){
                html+=':<selectclass="secondselect">';

                for(vari=0;i<60;i++){
                    varpadded=i<10?'0'+i:i;
                    vartime=selected.clone().second(i);

                    vardisabled=false;
                    if(minDate&&time.isBefore(minDate))
                        disabled=true;
                    if(maxDate&&time.isAfter(maxDate))
                        disabled=true;

                    if(selected.second()==i&&!disabled){
                        html+='<optionvalue="'+i+'"selected="selected">'+padded+'</option>';
                    }elseif(disabled){
                        html+='<optionvalue="'+i+'"disabled="disabled"class="disabled">'+padded+'</option>';
                    }else{
                        html+='<optionvalue="'+i+'">'+padded+'</option>';
                    }
                }

                html+='</select>';
            }

            //
            //AM/PM
            //

            if(!this.timePicker24Hour){
                html+='<selectclass="ampmselect">';

                varam_html='';
                varpm_html='';

                if(minDate&&selected.clone().hour(12).minute(0).second(0).isBefore(minDate))
                    am_html='disabled="disabled"class="disabled"';

                if(maxDate&&selected.clone().hour(0).minute(0).second(0).isAfter(maxDate))
                    pm_html='disabled="disabled"class="disabled"';

                if(selected.hour()>=12){
                    html+='<optionvalue="AM"'+am_html+'>AM</option><optionvalue="PM"selected="selected"'+pm_html+'>PM</option>';
                }else{
                    html+='<optionvalue="AM"selected="selected"'+am_html+'>AM</option><optionvalue="PM"'+pm_html+'>PM</option>';
                }

                html+='</select>';
            }

            this.container.find('.drp-calendar.'+side+'.calendar-time').html(html);

        },

        updateFormInputs:function(){

            if(this.singleDatePicker||(this.endDate&&(this.startDate.isBefore(this.endDate)||this.startDate.isSame(this.endDate)))){
                this.container.find('button.applyBtn').removeAttr('disabled');
            }else{
                this.container.find('button.applyBtn').attr('disabled','disabled');
            }

        },

        move:function(){
            varparentOffset={top:0,left:0},
                containerTop;
            varparentRightEdge=$(window).width();
            if(!this.parentEl.is('body')){
                parentOffset={
                    top:this.parentEl.offset().top-this.parentEl.scrollTop(),
                    left:this.parentEl.offset().left-this.parentEl.scrollLeft()
                };
                parentRightEdge=this.parentEl[0].clientWidth+this.parentEl.offset().left;
            }

            if(this.drops=='up')
                containerTop=this.element.offset().top-this.container.outerHeight()-parentOffset.top;
            else
                containerTop=this.element.offset().top+this.element.outerHeight()-parentOffset.top;

            //Forcethecontainertoit'sactualwidth
            this.container.css({
              top:0,
              left:0,
              right:'auto'
            });
            varcontainerWidth=this.container.outerWidth();

            this.container[this.drops=='up'?'addClass':'removeClass']('drop-up');

            if(this.opens=='left'){
                varcontainerRight=parentRightEdge-this.element.offset().left-this.element.outerWidth();
                if(containerWidth+containerRight>$(window).width()){
                    this.container.css({
                        top:containerTop,
                        right:'auto',
                        left:9
                    });
                }else{
                    this.container.css({
                        top:containerTop,
                        right:containerRight,
                        left:'auto'
                    });
                }
            }elseif(this.opens=='center'){
                varcontainerLeft=this.element.offset().left-parentOffset.left+this.element.outerWidth()/2
                                        -containerWidth/2;
                if(containerLeft<0){
                    this.container.css({
                        top:containerTop,
                        right:'auto',
                        left:9
                    });
                }elseif(containerLeft+containerWidth>$(window).width()){
                    this.container.css({
                        top:containerTop,
                        left:'auto',
                        right:0
                    });
                }else{
                    this.container.css({
                        top:containerTop,
                        left:containerLeft,
                        right:'auto'
                    });
                }
            }else{
                varcontainerLeft=this.element.offset().left-parentOffset.left;
                if(containerLeft+containerWidth>$(window).width()){
                    this.container.css({
                        top:containerTop,
                        left:'auto',
                        right:0
                    });
                }else{
                    this.container.css({
                        top:containerTop,
                        left:containerLeft,
                        right:'auto'
                    });
                }
            }
        },

        show:function(e){
            if(this.isShowing)return;

            //Createaclickproxythatisprivatetothisinstanceofdatepicker,forunbinding
            this._outsideClickProxy=$.proxy(function(e){this.outsideClick(e);},this);

            //Bindglobaldatepickermousedownforhidingand
            $(document)
              .on('mousedown.daterangepicker',this._outsideClickProxy)
              //alsosupportmobiledevices
              .on('touchend.daterangepicker',this._outsideClickProxy)
              //alsoexplicitlyplaynicewithBootstrapdropdowns,whichstopPropagationwhenclickingthem
              .on('click.daterangepicker','[data-toggle=dropdown]',this._outsideClickProxy)
              //andalsoclosewhenfocuschangestooutsidethepicker(eg.tabbingbetweencontrols)
              .on('focusin.daterangepicker',this._outsideClickProxy);

            //Repositionthepickerifthewindowisresizedwhileit'sopen
            $(window).on('resize.daterangepicker',$.proxy(function(e){this.move(e);},this));

            this.oldStartDate=this.startDate.clone();
            this.oldEndDate=this.endDate.clone();
            this.previousRightTime=this.endDate.clone();

            this.updateView();
            this.container.show();
            this.move();
            this.element.trigger('show.daterangepicker',this);
            this.isShowing=true;
        },

        hide:function(e){
            if(!this.isShowing)return;

            //incompletedateselection,reverttolastvalues
            if(!this.endDate){
                this.startDate=this.oldStartDate.clone();
                this.endDate=this.oldEndDate.clone();
            }

            //ifanewdaterangewasselected,invoketheusercallbackfunction
            if(!this.startDate.isSame(this.oldStartDate)||!this.endDate.isSame(this.oldEndDate))
                this.callback(this.startDate.clone(),this.endDate.clone(),this.chosenLabel);

            //ifpickerisattachedtoatextinput,updateit
            this.updateElement();

            $(document).off('.daterangepicker');
            $(window).off('.daterangepicker');
            this.container.hide();
            this.element.trigger('hide.daterangepicker',this);
            this.isShowing=false;
        },

        toggle:function(e){
            if(this.isShowing){
                this.hide();
            }else{
                this.show();
            }
        },

        outsideClick:function(e){
            vartarget=$(e.target);
            //ifthepageisclickedanywhereexceptwithinthedaterangerpicker/button
            //itselfthencallthis.hide()
            if(
                //iemodaldialogfix
                e.type=="focusin"||
                target.closest(this.element).length||
                target.closest(this.container).length||
                target.closest('.calendar-table').length
                )return;
            this.hide();
            this.element.trigger('outsideClick.daterangepicker',this);
        },

        showCalendars:function(){
            this.container.addClass('show-calendar');
            this.move();
            this.element.trigger('showCalendar.daterangepicker',this);
        },

        hideCalendars:function(){
            this.container.removeClass('show-calendar');
            this.element.trigger('hideCalendar.daterangepicker',this);
        },

        clickRange:function(e){
            varlabel=e.target.getAttribute('data-range-key');
            this.chosenLabel=label;
            if(label==this.locale.customRangeLabel){
                this.showCalendars();
            }else{
                vardates=this.ranges[label];
                this.startDate=dates[0];
                this.endDate=dates[1];

                if(!this.timePicker){
                    this.startDate.startOf('day');
                    this.endDate.endOf('day');
                }

                if(!this.alwaysShowCalendars)
                    this.hideCalendars();
                this.clickApply();
            }
        },

        clickPrev:function(e){
            varcal=$(e.target).parents('.drp-calendar');
            if(cal.hasClass('left')){
                this.leftCalendar.month.subtract(1,'month');
                if(this.linkedCalendars)
                    this.rightCalendar.month.subtract(1,'month');
            }else{
                this.rightCalendar.month.subtract(1,'month');
            }
            this.updateCalendars();
        },

        clickNext:function(e){
            varcal=$(e.target).parents('.drp-calendar');
            if(cal.hasClass('left')){
                this.leftCalendar.month.add(1,'month');
            }else{
                this.rightCalendar.month.add(1,'month');
                if(this.linkedCalendars)
                    this.leftCalendar.month.add(1,'month');
            }
            this.updateCalendars();
        },

        hoverDate:function(e){

            //ignoredatesthatcan'tbeselected
            if(!$(e.target).hasClass('available'))return;

            vartitle=$(e.target).attr('data-title');
            varrow=title.substr(1,1);
            varcol=title.substr(3,1);
            varcal=$(e.target).parents('.drp-calendar');
            vardate=cal.hasClass('left')?this.leftCalendar.calendar[row][col]:this.rightCalendar.calendar[row][col];

            //highlightthedatesbetweenthestartdateandthedatebeinghoveredasapotentialenddate
            varleftCalendar=this.leftCalendar;
            varrightCalendar=this.rightCalendar;
            varstartDate=this.startDate;
            if(!this.endDate){
                this.container.find('.drp-calendartbodytd').each(function(index,el){

                    //skipweeknumbers,onlylookatdates
                    if($(el).hasClass('week'))return;

                    vartitle=$(el).attr('data-title');
                    varrow=title.substr(1,1);
                    varcol=title.substr(3,1);
                    varcal=$(el).parents('.drp-calendar');
                    vardt=cal.hasClass('left')?leftCalendar.calendar[row][col]:rightCalendar.calendar[row][col];

                    if((dt.isAfter(startDate)&&dt.isBefore(date))||dt.isSame(date,'day')){
                        $(el).addClass('in-range');
                    }else{
                        $(el).removeClass('in-range');
                    }

                });
            }

        },

        clickDate:function(e){

            if(!$(e.target).hasClass('available'))return;

            vartitle=$(e.target).attr('data-title');
            varrow=title.substr(1,1);
            varcol=title.substr(3,1);
            varcal=$(e.target).parents('.drp-calendar');
            vardate=cal.hasClass('left')?this.leftCalendar.calendar[row][col]:this.rightCalendar.calendar[row][col];

            //
            //thisfunctionneedstodoafewthings:
            //*alternatebetweenselectingastartandenddatefortherange,
            //*ifthetimepickerisenabled,applythehour/minute/secondfromtheselectboxestotheclickeddate
            //*ifautoapplyisenabled,andanenddatewaschosen,applytheselection
            //*ifsingledatepickermode,andtimepickerisn'tenabled,applytheselectionimmediately
            //*ifoneoftheinputsabovethecalendarswasfocused,cancelthatmanualinput
            //

            if(this.endDate||date.isBefore(this.startDate,'day')){//pickingstart
                if(this.timePicker){
                    varhour=parseInt(this.container.find('.left.hourselect').val(),10);
                    if(!this.timePicker24Hour){
                        varampm=this.container.find('.left.ampmselect').val();
                        if(ampm==='PM'&&hour<12)
                            hour+=12;
                        if(ampm==='AM'&&hour===12)
                            hour=0;
                    }
                    varminute=parseInt(this.container.find('.left.minuteselect').val(),10);
                    if(isNaN(minute)){
                        minute=parseInt(this.container.find('.left.minuteselectoption:last').val(),10);
                    }
                    varsecond=this.timePickerSeconds?parseInt(this.container.find('.left.secondselect').val(),10):0;
                    date=date.clone().hour(hour).minute(minute).second(second);
                }
                this.endDate=null;
                this.setStartDate(date.clone());
            }elseif(!this.endDate&&date.isBefore(this.startDate)){
                //specialcase:clickingthesamedateforstart/end,
                //butthetimeoftheenddateisbeforethestartdate
                this.setEndDate(this.startDate.clone());
            }else{//pickingend
                if(this.timePicker){
                    varhour=parseInt(this.container.find('.right.hourselect').val(),10);
                    if(!this.timePicker24Hour){
                        varampm=this.container.find('.right.ampmselect').val();
                        if(ampm==='PM'&&hour<12)
                            hour+=12;
                        if(ampm==='AM'&&hour===12)
                            hour=0;
                    }
                    varminute=parseInt(this.container.find('.right.minuteselect').val(),10);
                    if(isNaN(minute)){
                        minute=parseInt(this.container.find('.right.minuteselectoption:last').val(),10);
                    }
                    varsecond=this.timePickerSeconds?parseInt(this.container.find('.right.secondselect').val(),10):0;
                    date=date.clone().hour(hour).minute(minute).second(second);
                }
                this.setEndDate(date.clone());
                if(this.autoApply){
                  this.calculateChosenLabel();
                  this.clickApply();
                }
            }

            if(this.singleDatePicker){
                this.setEndDate(this.startDate);
                if(!this.timePicker)
                    this.clickApply();
            }

            this.updateView();

            //Thisistocanceltheblureventhandlerifthemousewasinoneoftheinputs
            e.stopPropagation();

        },

        calculateChosenLabel:function(){
            varcustomRange=true;
            vari=0;
            for(varrangeinthis.ranges){
              if(this.timePicker){
                    varformat=this.timePickerSeconds?"YYYY-MM-DDHH:mm:ss":"YYYY-MM-DDHH:mm";
                    //ignoretimeswhencomparingdatesiftimepickersecondsisnotenabled
                    if(this.startDate.format(format)==this.ranges[range][0].format(format)&&this.endDate.format(format)==this.ranges[range][1].format(format)){
                        customRange=false;
                        this.chosenLabel=this.container.find('.rangesli:eq('+i+')').addClass('active').attr('data-range-key');
                        break;
                    }
                }else{
                    //ignoretimeswhencomparingdatesiftimepickerisnotenabled
                    if(this.startDate.format('YYYY-MM-DD')==this.ranges[range][0].format('YYYY-MM-DD')&&this.endDate.format('YYYY-MM-DD')==this.ranges[range][1].format('YYYY-MM-DD')){
                        customRange=false;
                        this.chosenLabel=this.container.find('.rangesli:eq('+i+')').addClass('active').attr('data-range-key');
                        break;
                    }
                }
                i++;
            }
            if(customRange){
                if(this.showCustomRangeLabel){
                    this.chosenLabel=this.container.find('.rangesli:last').addClass('active').attr('data-range-key');
                }else{
                    this.chosenLabel=null;
                }
                this.showCalendars();
            }
        },

        clickApply:function(e){
            this.hide();
            this.element.trigger('apply.daterangepicker',this);
        },

        clickCancel:function(e){
            this.startDate=this.oldStartDate;
            this.endDate=this.oldEndDate;
            this.hide();
            this.element.trigger('cancel.daterangepicker',this);
        },

        monthOrYearChanged:function(e){
            varisLeft=$(e.target).closest('.drp-calendar').hasClass('left'),
                leftOrRight=isLeft?'left':'right',
                cal=this.container.find('.drp-calendar.'+leftOrRight);

            //MonthmustbeNumberfornewmomentversions
            varmonth=parseInt(cal.find('.monthselect').val(),10);
            varyear=cal.find('.yearselect').val();

            if(!isLeft){
                if(year<this.startDate.year()||(year==this.startDate.year()&&month<this.startDate.month())){
                    month=this.startDate.month();
                    year=this.startDate.year();
                }
            }

            if(this.minDate){
                if(year<this.minDate.year()||(year==this.minDate.year()&&month<this.minDate.month())){
                    month=this.minDate.month();
                    year=this.minDate.year();
                }
            }

            if(this.maxDate){
                if(year>this.maxDate.year()||(year==this.maxDate.year()&&month>this.maxDate.month())){
                    month=this.maxDate.month();
                    year=this.maxDate.year();
                }
            }

            if(isLeft){
                this.leftCalendar.month.month(month).year(year);
                if(this.linkedCalendars)
                    this.rightCalendar.month=this.leftCalendar.month.clone().add(1,'month');
            }else{
                this.rightCalendar.month.month(month).year(year);
                if(this.linkedCalendars)
                    this.leftCalendar.month=this.rightCalendar.month.clone().subtract(1,'month');
            }
            this.updateCalendars();
        },

        timeChanged:function(e){

            varcal=$(e.target).closest('.drp-calendar'),
                isLeft=cal.hasClass('left');

            varhour=parseInt(cal.find('.hourselect').val(),10);
            varminute=parseInt(cal.find('.minuteselect').val(),10);
            if(isNaN(minute)){
                minute=parseInt(cal.find('.minuteselectoption:last').val(),10);
            }
            varsecond=this.timePickerSeconds?parseInt(cal.find('.secondselect').val(),10):0;

            if(!this.timePicker24Hour){
                varampm=cal.find('.ampmselect').val();
                if(ampm==='PM'&&hour<12)
                    hour+=12;
                if(ampm==='AM'&&hour===12)
                    hour=0;
            }

            if(isLeft){
                varstart=this.startDate.clone();
                start.hour(hour);
                start.minute(minute);
                start.second(second);
                this.setStartDate(start);
                if(this.singleDatePicker){
                    this.endDate=this.startDate.clone();
                }elseif(this.endDate&&this.endDate.format('YYYY-MM-DD')==start.format('YYYY-MM-DD')&&this.endDate.isBefore(start)){
                    this.setEndDate(start.clone());
                }
            }elseif(this.endDate){
                varend=this.endDate.clone();
                end.hour(hour);
                end.minute(minute);
                end.second(second);
                this.setEndDate(end);
            }

            //updatethecalendarssoallclickabledatesreflectthenewtimecomponent
            this.updateCalendars();

            //updatetheforminputsabovethecalendarswiththenewtime
            this.updateFormInputs();

            //re-renderthetimepickersbecausechangingoneselectioncanaffectwhat'senabledinanother
            this.renderTimePicker('left');
            this.renderTimePicker('right');

        },

        elementChanged:function(){
            if(!this.element.is('input'))return;
            if(!this.element.val().length)return;

            vardateString=this.element.val().split(this.locale.separator),
                start=null,
                end=null;

            if(dateString.length===2){
                start=moment(dateString[0],this.locale.format);
                end=moment(dateString[1],this.locale.format);
            }

            if(this.singleDatePicker||start===null||end===null){
                start=moment(this.element.val(),this.locale.format);
                end=start;
            }

            if(!start.isValid()||!end.isValid())return;

            this.setStartDate(start);
            this.setEndDate(end);
            this.updateView();
        },

        keydown:function(e){
            //hideontaborenter
            if((e.keyCode===9)||(e.keyCode===13)){
                this.hide();
            }

            //hideonescandpreventpropagation
            if(e.keyCode===27){
                e.preventDefault();
                e.stopPropagation();

                this.hide();
            }
        },

        updateElement:function(){
            if(this.element.is('input')&&this.autoUpdateInput){
                varnewValue=this.startDate.format(this.locale.format);
                if(!this.singleDatePicker){
                    newValue+=this.locale.separator+this.endDate.format(this.locale.format);
                }
                if(newValue!==this.element.val()){
                    this.element.val(newValue).trigger('change');
                }
            }
        },

        remove:function(){
            this.container.remove();
            this.element.off('.daterangepicker');
            this.element.removeData();
        }

    };

    $.fn.daterangepicker=function(options,callback){
        varimplementOptions=$.extend(true,{},$.fn.daterangepicker.defaultOptions,options);
        this.each(function(){
            varel=$(this);
            if(el.data('daterangepicker'))
                el.data('daterangepicker').remove();
            el.data('daterangepicker',newDateRangePicker(el,implementOptions,callback));
        });
        returnthis;
    };

    returnDateRangePicker;

}));
