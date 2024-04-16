flectra.define('hr_holidays.dashboard.view_custo',function(require){
    'usestrict';

    varcore=require('web.core');
    varCalendarModel=require('web.CalendarModel');
    varCalendarPopover=require('web.CalendarPopover');
    varCalendarController=require("web.CalendarController");
    varCalendarRenderer=require("web.CalendarRenderer");
    varCalendarView=require("web.CalendarView");
    varviewRegistry=require('web.view_registry');

    var_t=core._t;
    varQWeb=core.qweb;

    varTimeOffCalendarPopover=CalendarPopover.extend({
        template:'hr_holidays.calendar.popover',

        init:function(parent,eventInfo){
            this._super.apply(this,arguments);
            conststate=this.event.extendedProps.record.state;
            this.canDelete=state&&['validate','refuse'].indexOf(state)===-1;
            this.canEdit=state!==undefined;
            this.displayFields=[];

            if(this.modelName==="hr.leave.report.calendar"){
                constduration=this.event.extendedProps.record.display_name.split(':').slice(-1);
                this.display_name=_.str.sprintf(_t("TimeOff:%s"),duration);
            }else{
                this.display_name=this.event.extendedProps.record.display_name;
            }
        },
    });

    varTimeOffCalendarController=CalendarController.extend({
        events:_.extend({},CalendarController.prototype.events,{
            'click.btn-time-off':'_onNewTimeOff',
            'click.btn-allocation':'_onNewAllocation',
        }),

        /**
         *@override
         */
        start:function(){
            this.$el.addClass('o_timeoff_calendar');
            returnthis._super(...arguments);
        },

        //--------------------------------------------------------------------------
        //Public
        //--------------------------------------------------------------------------

         /**
         *Renderthebuttonsandaddnewbuttonabout
         *timeoffandallocationsrequest
         *
         *@override
         */

        renderButtons:function($node){
            this._super.apply(this,arguments);

            $(QWeb.render('hr_holidays.dashboard.calendar.button',{
                time_off:_t('NewTimeOff'),
                request:_t('NewAllocation'),
            })).appendTo(this.$buttons);

            if($node){
                this.$buttons.appendTo($node);
            }else{
                this.$('.o_calendar_buttons').replaceWith(this.$buttons);
            }
        },

        //--------------------------------------------------------------------------
        //Handlers
        //--------------------------------------------------------------------------

        /**
         *Action:createanewtimeoffrequest
         *
         *@private
         */
        _onNewTimeOff:function(){
            varself=this;

            this.do_action('hr_holidays.hr_leave_action_my_request',{
                on_close:function(){
                    self.reload();
                }
            });
        },

        /**
         *Action:createanewallocationrequest
         *
         *@private
         */
        _onNewAllocation:function(){
            varself=this;
            this.do_action({
                type:'ir.actions.act_window',
                res_model:'hr.leave.allocation',
                name:'NewAllocationRequest',
                views:[[false,'form']],
                context:{'form_view_ref':'hr_holidays.hr_leave_allocation_view_form_dashboard'},
                target:'new',
            },{
                on_close:function(){
                    self.reload();
                }
            });
        },
    });

    varTimeOffPopoverRenderer=CalendarRenderer.extend({
        config:_.extend({},CalendarRenderer.prototype.config,{
            CalendarPopover:TimeOffCalendarPopover,
        }),

        _getPopoverParams:function(eventData){
            letparams=this._super.apply(this,arguments);
            letcalendarIcon;
            letstate=eventData.extendedProps.record.state;

            if(state==='validate'){
                calendarIcon='fa-calendar-check-o';
            }elseif(state==='refuse'){
                calendarIcon='fa-calendar-times-o';
            }elseif(state){
                calendarIcon='fa-calendar-o';
            }

            params['title']=eventData.extendedProps.record.display_name.split(':').slice(0,-1).join(':');
            params['template']=QWeb.render('hr_holidays.calendar.popover.placeholder',{color:this.getColor(eventData.color_index),calendarIcon:calendarIcon});
            returnparams;
        },

        _render:function(){
            varself=this;
            returnthis._super.apply(this,arguments).then(function(){
                self.$el.parent().find('.o_calendar_mini').hide();
            });
        },
    });

    varTimeOffCalendarRenderer=TimeOffPopoverRenderer.extend({
        _render:function(){
            varself=this;
            returnthis._super.apply(this,arguments).then(function(){
                returnself._rpc({
                    model:'hr.leave.type',
                    method:'get_days_all_request',
                    context:self.context,
                });
            }).then(function(result){
                self.$el.parent().find('.o_calendar_mini').hide();
                self.$el.parent().find('.o_timeoff_container').remove();
                varelem=QWeb.render('hr_holidays.dashboard_calendar_header',{
                    timeoffs:result,
                });
                self.$el.before(elem);
            });
        },
    });
    varTimeOffCalendarView=CalendarView.extend({
        config:_.extend({},CalendarView.prototype.config,{
            Controller:TimeOffCalendarController,
            Renderer:TimeOffCalendarRenderer,
        }),
    });

    /**
     *Calendarshowninthe"Everyone"menu
     */
    varTimeOffCalendarAllView=CalendarView.extend({
        config:_.extend({},CalendarView.prototype.config,{
            Renderer:TimeOffPopoverRenderer,
        }),
    });

    viewRegistry.add('time_off_calendar',TimeOffCalendarView);
    viewRegistry.add('time_off_calendar_all',TimeOffCalendarAllView);
});
