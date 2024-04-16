flectra.define('hr_attendance.my_attendances',function(require){
"usestrict";

varAbstractAction=require('web.AbstractAction');
varcore=require('web.core');
varfield_utils=require('web.field_utils');


varMyAttendances=AbstractAction.extend({
    contentTemplate:'HrAttendanceMyMainMenu',
    events:{
        "click.o_hr_attendance_sign_in_out_icon":_.debounce(function(){
            this.update_attendance();
        },200,true),
    },

    willStart:function(){
        varself=this;

        vardef=this._rpc({
                model:'hr.employee',
                method:'search_read',
                args:[[['user_id','=',this.getSession().uid]],['attendance_state','name','hours_today']],
            })
            .then(function(res){
                self.employee=res.length&&res[0];
                if(res.length){
                    self.hours_today=field_utils.format.float_time(self.employee.hours_today);
                }
            });

        returnPromise.all([def,this._super.apply(this,arguments)]);
    },

    update_attendance:function(){
        varself=this;
        this._rpc({
                model:'hr.employee',
                method:'attendance_manual',
                args:[[self.employee.id],'hr_attendance.hr_attendance_action_my_attendances'],
            })
            .then(function(result){
                if(result.action){
                    self.do_action(result.action);
                }elseif(result.warning){
                    self.do_warn(result.warning);
                }
            });
    },
});

core.action_registry.add('hr_attendance_my_attendances',MyAttendances);

returnMyAttendances;

});
