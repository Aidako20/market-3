flectra.define('hr_timesheet.task_with_hours',function(require){
"usestrict";

varfield_registry=require('web.field_registry');
varrelational_fields=require('web.relational_fields');
varFieldMany2One=relational_fields.FieldMany2One;

varTaskWithHours=FieldMany2One.extend({
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        this.additionalContext.hr_timesheet_display_remaining_hours=true;
    },
    /**
     *@override
     */
    _getDisplayNameWithoutHours:function(value){
        returnvalue.split('‒')[0];
    },
    /**
     *@override
     *@private
     */
    _renderEdit:function(){
        this.m2o_value=this._getDisplayNameWithoutHours(this.m2o_value);
        this._super.apply(this,arguments);
    },
});

field_registry.add('task_with_hours',TaskWithHours);

returnTaskWithHours;

});