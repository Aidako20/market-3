flectra.define('hr_attendance.widget',function(require){
    "usestrict";

    varbasic_fields=require('web.basic_fields');
    varfield_registry=require('web.field_registry');

    varRelativeTime=basic_fields.FieldDateTime.extend({
        _formatValue:function(val){
            if(!(val&&val._isAMomentObject)){
                return;
            }
            returnval.fromNow(true);
        },
    });

    field_registry.add('relative_time',RelativeTime);

    returnRelativeTime;
});