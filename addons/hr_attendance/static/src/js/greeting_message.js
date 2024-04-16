flectra.define('hr_attendance.greeting_message',function(require){
"usestrict";

varAbstractAction=require('web.AbstractAction');
varcore=require('web.core');
vartime=require('web.time');

var_t=core._t;


varGreetingMessage=AbstractAction.extend({
    contentTemplate:'HrAttendanceGreetingMessage',

    events:{
        "click.o_hr_attendance_button_dismiss":function(){this.do_action(this.next_action,{clear_breadcrumbs:true});},
    },

    init:function(parent,action){
        varself=this;
        this._super.apply(this,arguments);
        this.activeBarcode=true;

        //ifnocorrectactiongiven(duetoanerroneousbackorrefreshfromthebrowser),wesetthedismissbuttontoreturn
        //tothe(likely)appropriatemenu,accordingtotheuseraccessrights
        if(!action.attendance){
            this.activeBarcode=false;
            this.getSession().user_has_group('hr_attendance.group_hr_attendance_user').then(function(has_group){
                if(has_group){
                    self.next_action='hr_attendance.hr_attendance_action_kiosk_mode';
                }else{
                    self.next_action='hr_attendance.hr_attendance_action_my_attendances';
                }
            });
            return;
        }

        this.next_action=action.next_action||'hr_attendance.hr_attendance_action_my_attendances';
        //nolisteningtobarcodescansifwearen'tcomingfromthekioskmode(andthusnotgoingbacktoitwithnext_action)
        if(this.next_action!='hr_attendance.hr_attendance_action_kiosk_mode'&&this.next_action.tag!='hr_attendance_kiosk_mode'){
            this.activeBarcode=false;
        }

        this.attendance=action.attendance;
        //Wereceivethecheckin/outtimesinUTC
        //Thiswidgetonlydealswithdisplay,whichshouldbeinbrowser'sTimeZone
        this.attendance.check_in=this.attendance.check_in&&moment.utc(this.attendance.check_in).local();
        this.attendance.check_out=this.attendance.check_out&&moment.utc(this.attendance.check_out).local();
        this.previous_attendance_change_date=action.previous_attendance_change_date&&moment.utc(action.previous_attendance_change_date).local();

        //checkin/outtimesdisplayedinthegreetingmessagetemplate.
        this.format_time=time.getLangTimeFormat();
        this.attendance.check_in_time=this.attendance.check_in&&this.attendance.check_in.format(this.format_time);
        this.attendance.check_out_time=this.attendance.check_out&&this.attendance.check_out.format(this.format_time);

        if(action.hours_today){
            varduration=moment.duration(action.hours_today,"hours");
            this.hours_today=duration.hours()+'hours,'+duration.minutes()+'minutes';
        }

        this.employee_name=action.employee_name;
        this.attendanceBarcode=action.barcode;
    },

    start:function(){
        if(this.attendance){
            this.attendance.check_out?this.farewell_message():this.welcome_message();
        }
        if(this.activeBarcode){
            core.bus.on('barcode_scanned',this,this._onBarcodeScanned);
        }
        returnthis._super.apply(this,arguments);
    },

    welcome_message:function(){
        varself=this;
        varnow=this.attendance.check_in.clone();
        this.return_to_main_menu=setTimeout(function(){self.do_action(self.next_action,{clear_breadcrumbs:true});},5000);

        if(now.hours()<5){
            this.$('.o_hr_attendance_message_message').append(_t("Goodnight"));
        }elseif(now.hours()<12){
            if(now.hours()<8&&Math.random()<0.3){
                if(Math.random()<0.75){
                    this.$('.o_hr_attendance_message_message').append(_t("Theearlybirdcatchestheworm"));
                }else{
                    this.$('.o_hr_attendance_message_message').append(_t("Firstcome,firstserved"));
                }
            }else{
                this.$('.o_hr_attendance_message_message').append(_t("Goodmorning"));
            }
        }elseif(now.hours()<17){
            this.$('.o_hr_attendance_message_message').append(_t("Goodafternoon"));
        }elseif(now.hours()<23){
            this.$('.o_hr_attendance_message_message').append(_t("Goodevening"));
        }else{
            this.$('.o_hr_attendance_message_message').append(_t("Goodnight"));
        }
        if(this.previous_attendance_change_date){
            varlast_check_out_date=this.previous_attendance_change_date.clone();
            if(now-last_check_out_date>24*7*60*60*1000){
                this.$('.o_hr_attendance_random_message').html(_t("Gladtohaveyouback,it'sbeenawhile!"));
            }else{
                if(Math.random()<0.02){
                    this.$('.o_hr_attendance_random_message').html(_t("Ifajobisworthdoing,itisworthdoingwell!"));
                }
            }
        }
    },

    farewell_message:function(){
        varself=this;
        varnow=this.attendance.check_out.clone();
        this.return_to_main_menu=setTimeout(function(){self.do_action(self.next_action,{clear_breadcrumbs:true});},5000);

        if(this.previous_attendance_change_date){
            varlast_check_in_date=this.previous_attendance_change_date.clone();
            if(now-last_check_in_date>1000*60*60*12){
                this.$('.o_hr_attendance_warning_message').show().append(_t("<b>Warning!Lastcheckinwasover12hoursago.</b><br/>Ifthisisn'tright,pleasecontactHumanResourcestaff"));
                clearTimeout(this.return_to_main_menu);
                this.activeBarcode=false;
            }elseif(now-last_check_in_date>1000*60*60*8){
                this.$('.o_hr_attendance_random_message').html(_t("Anothergoodday'swork!Seeyousoon!"));
            }
        }

        if(now.hours()<12){
            this.$('.o_hr_attendance_message_message').append(_t("Haveagoodday!"));
        }elseif(now.hours()<14){
            this.$('.o_hr_attendance_message_message').append(_t("Haveanicelunch!"));
            if(Math.random()<0.05){
                this.$('.o_hr_attendance_random_message').html(_t("Eatbreakfastasaking,lunchasamerchantandsupperasabeggar"));
            }elseif(Math.random()<0.06){
                this.$('.o_hr_attendance_random_message').html(_t("Anappleadaykeepsthedoctoraway"));
            }
        }elseif(now.hours()<17){
            this.$('.o_hr_attendance_message_message').append(_t("Haveagoodafternoon"));
        }else{
            if(now.hours()<18&&Math.random()<0.2){
                this.$('.o_hr_attendance_message_message').append(_t("Earlytobedandearlytorise,makesamanhealthy,wealthyandwise"));
            }else{
                this.$('.o_hr_attendance_message_message').append(_t("Haveagoodevening"));
            }
        }
    },

    _onBarcodeScanned:function(barcode){
        varself=this;
        if(this.attendanceBarcode!==barcode){
            if(this.return_to_main_menu){ //incaseofmultiplescansinthegreetingmessageview,deletethetimer,anewonewillbecreated.
                clearTimeout(this.return_to_main_menu);
            }
            core.bus.off('barcode_scanned',this,this._onBarcodeScanned);
            this._rpc({
                    model:'hr.employee',
                    method:'attendance_scan',
                    args:[barcode,],
                })
                .then(function(result){
                    if(result.action){
                        self.do_action(result.action);
                    }elseif(result.warning){
                        self.do_warn(result.warning);
                        setTimeout(function(){self.do_action(self.next_action,{clear_breadcrumbs:true});},5000);
                    }
                },function(){
                    setTimeout(function(){self.do_action(self.next_action,{clear_breadcrumbs:true});},5000);
                });
        }
    },

    destroy:function(){
        core.bus.off('barcode_scanned',this,this._onBarcodeScanned);
        clearTimeout(this.return_to_main_menu);
        this._super.apply(this,arguments);
    },
});

core.action_registry.add('hr_attendance_greeting_message',GreetingMessage);

returnGreetingMessage;

});
