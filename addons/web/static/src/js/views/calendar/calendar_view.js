flectra.define('web.CalendarView',function(require){
"usestrict";

varAbstractView=require('web.AbstractView');
varCalendarModel=require('web.CalendarModel');
varCalendarController=require('web.CalendarController');
varCalendarRenderer=require('web.CalendarRenderer');
varcore=require('web.core');
varpyUtils=require('web.py_utils');
varutils=require('web.utils');

var_lt=core._lt;

//gatherthefieldstoget
varfieldsToGather=[
    "date_start",
    "date_delay",
    "date_stop",
    "all_day",
    "recurrence_update"
];

constscalesInfo={
    day:'timeGridDay',
    week:'timeGridWeek',
    month:'dayGridMonth',
    year:'dayGridYear',
};

varCalendarView=AbstractView.extend({
    display_name:_lt('Calendar'),
    icon:'fa-calendar',
    jsLibs:[
        '/web/static/lib/fullcalendar/core/main.js',
        '/web/static/lib/fullcalendar/interaction/main.js',
        '/web/static/lib/fullcalendar/moment/main.js',
        '/web/static/lib/fullcalendar/daygrid/main.js',
        '/web/static/lib/fullcalendar/timegrid/main.js',
        '/web/static/lib/fullcalendar/list/main.js'
    ],
    cssLibs:[
        '/web/static/lib/fullcalendar/core/main.css',
        '/web/static/lib/fullcalendar/daygrid/main.css',
        '/web/static/lib/fullcalendar/timegrid/main.css',
        '/web/static/lib/fullcalendar/list/main.css'
    ],
    config:_.extend({},AbstractView.prototype.config,{
        Model:CalendarModel,
        Controller:CalendarController,
        Renderer:CalendarRenderer,
    }),
    viewType:'calendar',
    searchMenuTypes:['filter','favorite'],

    /**
     *@override
     */
    init:function(viewInfo,params){
        this._super.apply(this,arguments);
        vararch=this.arch;
        varfields=this.fields;
        varattrs=arch.attrs;

        if(!attrs.date_start){
            thrownewError(_lt("Calendarviewhasnotdefined'date_start'attribute."));
        }

        varmapping={};
        varfieldNames=fields.display_name?['display_name']:[];
        vardisplayFields={};

        _.each(fieldsToGather,function(field){
            if(arch.attrs[field]){
                varfieldName=attrs[field];
                mapping[field]=fieldName;
                fieldNames.push(fieldName);
            }
        });

        varfilters={};

        vareventLimit=attrs.event_limit!==null&&(isNaN(+attrs.event_limit)?_.str.toBool(attrs.event_limit):+attrs.event_limit);

        varmodelFilters=[];
        _.each(arch.children,function(child){
            if(child.tag!=='field')return;
            varfieldName=child.attrs.name;
            fieldNames.push(fieldName);
            if(!child.attrs.invisible||child.attrs.filters){
                child.attrs.options=child.attrs.options?pyUtils.py_eval(child.attrs.options):{};
                if(!child.attrs.invisible){
                    displayFields[fieldName]={attrs:child.attrs};
                }

                if(params.sidebar===false)return;//ifwehavenotsidebar,(eg:Dashboard),wedon'tusethefilter"coworkers"

                if(child.attrs.avatar_field){
                    filters[fieldName]=filters[fieldName]||{
                        'title':fields[fieldName].string,
                        'fieldName':fieldName,
                        'filters':[],
                    };
                    filters[fieldName].avatar_field=child.attrs.avatar_field;
                    filters[fieldName].avatar_model=fields[fieldName].relation;
                }
                if(child.attrs.write_model){
                    filters[fieldName]=filters[fieldName]||{
                        'title':fields[fieldName].string,
                        'fieldName':fieldName,
                        'filters':[],
                    };
                    filters[fieldName].write_model=child.attrs.write_model;
                    filters[fieldName].write_field=child.attrs.write_field;//can'tuseax2manyfields

                    modelFilters.push(fields[fieldName].relation);
                }
                if(child.attrs.filters){
                    filters[fieldName]=filters[fieldName]||{
                        'title':fields[fieldName].string,
                        'fieldName':fieldName,
                        'filters':[],
                    };
                    if(child.attrs.color){
                        filters[fieldName].field_color=child.attrs.color;
                        filters[fieldName].color_model=fields[fieldName].relation;
                    }
                    if(!child.attrs.avatar_field&&fields[fieldName].relation){
                        if(fields[fieldName].relation.includes(['res.users','res.partner','hr.employee'])){
                            filters[fieldName].avatar_field='image_128';
                        }
                        filters[fieldName].avatar_model=fields[fieldName].relation;
                    }
                }
            }
        });

        if(attrs.color){
            varfieldName=attrs.color;
            fieldNames.push(fieldName);
        }

        //ifquick_add=False,wedon'tallowquick_add
        //ifquick_add=notspecifiedinview,weusethedefaultwidgets.QuickCreate
        //ifquick_add=isNOTFalseandISspecifiedinview,wethisoneforwidgets.QuickCreate'
        this.controllerParams.quickAddPop=(!('quick_add'inattrs)||utils.toBoolElse(attrs.quick_add+'',true));
        this.controllerParams.disableQuickCreate= params.disable_quick_create||!this.controllerParams.quickAddPop;

        //Ifform_view_idisset,thenthecalendarviewwillopenaformview
        //withthisid,whenitneedstoeditorcreateanevent.
        this.controllerParams.formViewId=
            attrs.form_view_id?parseInt(attrs.form_view_id,10):false;
        if(!this.controllerParams.formViewId&&params.action){
            varformViewDescr=_.find(params.action.views,function(v){
                returnv.type=== 'form';
            });
            if(formViewDescr){
                this.controllerParams.formViewId=formViewDescr.viewID;
            }
        }

        letscales;
        constallowedScales=Object.keys(scalesInfo);
        if(arch.attrs.scales){
            scales=arch.attrs.scales.split(',')
                .filter(x=>allowedScales.includes(x));
        }else{
            scales=allowedScales;
        }

        this.controllerParams.eventOpenPopup=utils.toBoolElse(attrs.event_open_popup||'',false);
        this.controllerParams.showUnusualDays=utils.toBoolElse(attrs.show_unusual_days||'',false);
        this.controllerParams.mapping=mapping;
        this.controllerParams.context=params.context||{};
        this.controllerParams.displayName=params.action&&params.action.name;
        this.controllerParams.scales=scales;

        this.rendererParams.displayFields=displayFields;
        this.rendererParams.model=viewInfo.model;
        this.rendererParams.hideDate=utils.toBoolElse(attrs.hide_date||'',false);
        this.rendererParams.hideTime=utils.toBoolElse(attrs.hide_time||'',false);
        this.rendererParams.canDelete=this.controllerParams.activeActions.delete;
        this.rendererParams.canCreate=this.controllerParams.activeActions.create;
        this.rendererParams.scalesInfo=scalesInfo;

        this.loadParams.fieldNames=_.uniq(fieldNames);
        this.loadParams.mapping=mapping;
        this.loadParams.fields=fields;
        this.loadParams.fieldsInfo=viewInfo.fieldsInfo;
        this.loadParams.editable=!fields[mapping.date_start].readonly;
        this.loadParams.creatable=this.controllerParams.activeActions.create;
        this.loadParams.eventLimit=eventLimit;
        this.loadParams.fieldColor=attrs.color;

        this.loadParams.filters=filters;
        this.loadParams.mode=(params.context&&params.context.default_mode)||attrs.mode;
        this.loadParams.scales=scales;
        this.loadParams.initialDate=moment(params.initialDate||newDate());
        this.loadParams.scalesInfo=scalesInfo;
    },
});

returnCalendarView;

});
