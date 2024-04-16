flectra.define('hr_timesheet.timesheet_factor',function(require){
'usestrict';

consttimesheetUomFields=require('hr_timesheet.timesheet_uom');
constfieldUtils=require('web.field_utils');
constfieldRegistry=require('web.field_registry');

fieldRegistry.add('timesheet_factor',timesheetUomFields.FieldTimesheetFactor);

fieldUtils.format.timesheet_factor=function(value,field,options){
    constformatter=fieldUtils.format[timesheetUomFields.FieldTimesheetFactor.prototype.formatType];
    returnformatter(value,field,options);
};

fieldUtils.parse.timesheet_factor=function(value,field,options){
    constparser=fieldUtils.parse[timesheetUomFields.FieldTimesheetFactor.prototype.formatType];
    returnparser(value,field,options);
};

});
