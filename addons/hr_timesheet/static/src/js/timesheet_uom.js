flectra.define('hr_timesheet.timesheet_uom',function(require){
'usestrict';

constbasicFields=require('web.basic_fields');
constfieldUtils=require('web.field_utils');

constfieldRegistry=require('web.field_registry');

//Weneedthefieldregistrytobepopulated,aswebindthe
//timesheet_uomwidgetonexistingfieldwidgets.
require('web._field_registry');

constsession=require('web.session');

/**
 *Extendthefloatfactorwidgettosetdefaultvaluefortimesheet
 *usecase.The'factor'isforcedtobetheUoMtimesheet
 *conversionfromthesessioninfo.
 **/
constFieldTimesheetFactor=basicFields.FieldFloatFactor.extend({
    formatType:'float_factor',
    /**
     *Overrideinittotweakoptionsdependingonthesession_info
     *
     *@constructor
     *@override
     */
    init:function(parent,name,record,options){
        this._super(parent,name,record,options);

        //forcefactorinformatandparseoptions
        if(session.timesheet_uom_factor){
            this.nodeOptions.factor=session.timesheet_uom_factor;
            this.parseOptions.factor=session.timesheet_uom_factor;
        }
    },
});


/**
 *Extendthefloattogglewidgettosetdefaultvaluefortimesheet
 *usecase.The'range'isdifferentfromthedefaultoneofthe
 *nativewidget,andthe'factor'isforcedtobetheUoMtimesheet
 *conversion.
 **/
constFieldTimesheetToggle=basicFields.FieldFloatToggle.extend({
    formatType:'float_factor',
    /**
     *Overrideinittotweakoptionsdependingonthesession_info
     *
     *@constructor
     *@override
     */
    init:function(parent,name,record,options){
        options=options||{};
        varfieldsInfo=record.fieldsInfo[options.viewType||'default'];
        varattrs=options.attrs||(fieldsInfo&&fieldsInfo[name])||{};

        varhasRange=_.contains(_.keys(attrs.options||{}),'range');

        this._super(parent,name,record,options);

        //Setthetimesheetwidgetoptions:therangecanbecustomized
        //bysettingtheoptiononthefieldintheview.Thefactor
        //isforcedtobetheUoMconversionfactor.
        if(!hasRange){
            this.nodeOptions.range=[0.00,1.00,0.50];
        }
        this.nodeOptions.factor=session.timesheet_uom_factor;
    },
});


/**
 *Extendfloattimewidget
 */
constFieldTimesheetTime=basicFields.FieldFloatTime.extend({
    init:function(){
        this._super.apply(this,arguments);

        if(session.timesheet_uom_factor){
            this.nodeOptions.factor=session.timesheet_uom_factor;
            this.parseOptions.factor=session.timesheet_uom_factor;
        }
    }
});


/**
 *BindingdependingonCompanyPreference
 *
 *determinewichwidgetwillbethetimesheetone.
 *Simplymatchthe'timesheet_uom'widgetkeywiththecorrect
 *implementation(float_time,float_toggle,...).Thedefault
 *valuewillbe'float_factor'.
**/
constwidgetName='timesheet_uom'insession?
         session.timesheet_uom.timesheet_widget:'float_factor';

letFieldTimesheetUom=null;

if(widgetName==='float_toggle'){
    FieldTimesheetUom=FieldTimesheetToggle;
}elseif(widgetName==='float_time'){
    FieldTimesheetUom=FieldTimesheetTime;
}else{
    FieldTimesheetUom=(
            fieldRegistry.get(widgetName)&&
            fieldRegistry.get(widgetName).extend({})
        )||FieldTimesheetFactor;
}
fieldRegistry.add('timesheet_uom',FieldTimesheetUom);

//widgettimesheet_uom_no_toggleisthesameastimesheet_uombutwithouttoggle.
//Wecanmodifyeaslyhugeamountofdays.
letFieldTimesheetUomWithoutToggle=null;
if(widgetName==='float_toggle'){
    FieldTimesheetUomWithoutToggle=FieldTimesheetFactor;
}else{
    FieldTimesheetUomWithoutToggle=FieldTimesheetTime;
}
fieldRegistry.add('timesheet_uom_no_toggle',FieldTimesheetUomWithoutToggle);


//bindtheformatterandparsermethod,andtweaktheoptions
const_tweak_options=function(options){
    if(!_.contains(options,'factor')){
        options.factor=session.timesheet_uom_factor;
    }
    returnoptions;
};

fieldUtils.format.timesheet_uom=function(value,field,options){
    options=_tweak_options(options||{});
    constformatter=fieldUtils.format[FieldTimesheetUom.prototype.formatType];
    returnformatter(value,field,options);
};

fieldUtils.parse.timesheet_uom=function(value,field,options){
    options=_tweak_options(options||{});
    constparser=fieldUtils.parse[FieldTimesheetUom.prototype.formatType];
    returnparser(value,field,options);
};

fieldUtils.format.timesheet_uom_no_toggle=function(value,field,options){
    options=_tweak_options(options||{});
    constformatter=fieldUtils.format[FieldTimesheetUom.prototype.formatType];
    returnformatter(value,field,options);
};

fieldUtils.parse.timesheet_uom_no_toggle=function(value,field,options){
    options=_tweak_options(options||{});
    constparser=fieldUtils.parse[FieldTimesheetUom.prototype.formatType];
    returnparser(value,field,options);
};

return{
    FieldTimesheetUom,
    FieldTimesheetFactor,
    FieldTimesheetTime,
    FieldTimesheetToggle
};

});
