flectra.define('/web/static/src/js/libs/fullcalendar.js',function(){
    "usestrict";

    functioncreateYearCalendarView(FullCalendar){
        const{
            Calendar,
            createElement,
            EventApi,
            memoizeRendering,
            View,
        }=FullCalendar;

        classYearViewextendsView{
            constructor(){
                super(...arguments);
                this.months=null;
                this.renderSubCalendarsMem=memoizeRendering(
                    this.renderSubCalendars,this.unrenderSubCalendars);
                this.events=[];
            }

            //----------------------------------------------------------------------
            //Getters
            //----------------------------------------------------------------------

            getcurrentDate(){
                returnthis.context.calendar.state.currentDate;
            }

            //----------------------------------------------------------------------
            //Public
            //----------------------------------------------------------------------

            /**
             *@override
             */
            destroy(){
                this.renderSubCalendarsMem.unrender();
                super.destroy();
            }
            /**
             *Removestheselectiononsubcalendar.
             *Selectionsonsubcalendarsarenotpropagatedtothisviewso
             *thisviewcannotmanagethem.
             */
            unselect(){
                for(const{calendar}ofthis.months){
                    calendar.unselect();
                }
            }
            /**
             *@override
             */
            render(){
                this.renderSubCalendarsMem(this.context);
                super.render(...arguments);
            }
            /**
             *Rendersthemainlayout(the4x3monthgrid)
             */
            renderSubCalendars(){
                this.el.classList.add('fc-scroller');
                if(!this.context.options.selectable){
                    this.el.classList.add('fc-readonly-year-view');
                }
                this.months=[];
                for(letmonthNumber=0;monthNumber<12;monthNumber++){
                    constmonthDate=newDate(this.currentDate.getFullYear(),monthNumber);
                    constmonthShortName=moment(monthDate).format('MMM').toLowerCase();
                    constcontainer=createElement('div',{class:'fc-month-container'});
                    this.el.appendChild(container);
                    constel=createElement('div',{
                        class:`fc-monthfc-month-${monthShortName}`,
                    });
                    container.appendChild(el);
                    constcalendar=this._createMonthCalendar(el,monthDate);
                    this.months.push({el,calendar});
                    calendar.render();
                }
            }
            /**
             *Removesthemainlayout(the4x3monthgrid).
             *Calledwhenviewisswitched/destroyed.
             */
            unrenderSubCalendars(){
                for(const{el,calendar}ofthis.months){
                    calendar.destroy();
                    el.remove();
                }
            }
            /**
             *Renderseventsinsubcalendars.
             *Calledeverytimeeventsourcechanged(whenchangingthedate,
             *  whenchangingfilters,adding/removingfilters).
             */
            renderEvents(){
                //`renderDates`alsorenderseventssoifit'scalledjustbefore
                //thendonotexecutethisasitwilldoare-render.
                if(this.datesRendered){
                    this.datesRendered=false;
                    return;
                }
                this.events=this._computeEvents();
                for(const{calendar}ofthis.months){
                    calendar.refetchEvents();
                }
                this._setCursorOnEventDates();
            }
            /**
             *Rendersdatesandeventsinsubcalendars.
             *Calledwhentheyearofthedatechangedtorenderanew
             *4*3gridofmonthcalendarbasedonthenewyear.
             */
            renderDates(){
                this.events=this._computeEvents();
                for(const[monthNumber,{calendar}]ofObject.entries(this.months)){
                    constmonthDate=newDate(this.currentDate.getFullYear(),monthNumber);
                    calendar.gotoDate(monthDate);
                }
                this._setCursorOnEventDates();
                this.datesRendered=true;
            }

            //----------------------------------------------------------------------
            //Private
            //----------------------------------------------------------------------

            /**
             *@private
             */
            _computeEvents(){
                constcalendar=this.context.calendar;
                returncalendar.getEvents().map(event=>{
                    constendUTC=calendar.dateEnv.toDate(event._instance.range.end);
                    constend=newDate(event._instance.range.end);
                    if(endUTC.getHours()>0||endUTC.getMinutes()>0||
                        endUTC.getSeconds()>0||endUTC.getMilliseconds()>0){
                        end.setDate(end.getDate()+1);
                    }
                    //cloneeventdatatonottriggerrerenderingandissues
                    constinstance=Object.assign({},event._instance,{
                        range:{start:newDate(event._instance.range.start),end},
                    });
                    constdef=Object.assign({},event._def,{
                        rendering:'background',
                        allDay:true,
                    });
                    returnnewEventApi(this.context.calendar,def,instance);
                });
            }
            /**
             *Createamonthcalendarforthedate`monthDate`andmountitoncontainer.
             *
             *@private
             *@param{HTMLElement}container
             *@param{Date}monthDate
             */
            _createMonthCalendar(container,monthDate){
                returnnewCalendar(container,Object.assign({},this.context.options,{
                    defaultDate:monthDate,
                    defaultView:'dayGridMonth',
                    header:{left:false,center:'title',right:false},
                    titleFormat:{month:'short',year:'numeric'},
                    height:0,
                    contentHeight:0,
                    weekNumbers:false,
                    showNonCurrentDates:false,
                    views:{
                        dayGridMonth:{
                            columnHeaderText:(date)=>moment(date).format("ddd")[0],
                        },
                    },
                    selectMinDistance:5,//neededtonottriggerselectwhenclick
                    dateClick:this._onYearDateClick.bind(this),
                    datesRender:undefined,
                    events:(info,successCB)=>{
                        successCB(this.events);
                    },
                    windowResize:undefined,
                }));
            }
            /**
             *Setsfc-has-eventclassoneverydatesthathaveatleastoneevent.
             *
             *@private
             */
            _setCursorOnEventDates(){
                for(constelofthis.el.querySelectorAll('.fc-has-event')){
                    el.classList.remove('fc-has-event');
                }
                for(consteventofObject.values(this.events)){
                    letcurrentDate=moment(event._instance.range.start);
                    while(currentDate.isBefore(event._instance.range.end,'day')){
                        constformattedDate=currentDate.format('YYYY-MM-DD');
                        constel=this.el.querySelector(`.fc-day-top[data-date="${formattedDate}"]`);
                        if(el){
                            el.classList.add('fc-has-event');
                        }
                        currentDate.add(1,'days');
                    }
                }
            }

            //----------------------------------------------------------------------
            //Handlers
            //----------------------------------------------------------------------

            /**
             *@private
             *@param{*}info
             */
            _onYearDateClick(info){
                constcalendar=this.context.calendar;
                constevents=this.events
                    .filter(event=>{
                        conststart=moment(event.start);
                        constend=moment(event.end);
                        constinclusivity=start.isSame(end,'day')?'[]':'[)';
                        returnmoment(info.date).isBetween(start,end,'day',inclusivity);
                    })
                    .map(event=>{
                        returnObject.assign({},event._def,event._instance.range);
                    });
                constyearDateInfo=Object.assign({},info,{
                    view:this,
                    monthView:info.view,
                    events,
                    selectable:this.context.options.selectable,
                });
                calendar.publiclyTrigger('yearDateClick',[yearDateInfo]);
            }
        }

        returnFullCalendar.createPlugin({
            views:{
                dayGridYear:{
                    class:YearView,
                    duration:{years:1},
                    defaults:{
                        fixedWeekCount:true,
                    },
                },
            },
        });
    }

    return{
        createYearCalendarView,
    };
});
