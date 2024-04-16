flectra.define('mail.ActivityRenderer',function(require){
"usestrict";

constAbstractRendererOwl=require('web.AbstractRendererOwl');
constActivityCell=require('mail.ActivityCell');
constActivityRecord=require('mail.ActivityRecord');
const{ComponentAdapter}=require('web.OwlCompatibility');
constcore=require('web.core');
constKanbanColumnProgressBar=require('web.KanbanColumnProgressBar');
constpatchMixin=require('web.patchMixin');
constQWeb=require('web.QWeb');
constsession=require('web.session');
constutils=require('web.utils');

const_t=core._t;

const{useState}=owl.hooks;

/**
 *OwlComponentAdapterforActivityRecordwhichisKanbanRecord(FlectraWidget)
 *TODO:RemovethisadapterwhenActivityRecordisaComponent
 */
classActivityRecordAdapterextendsComponentAdapter{
    renderWidget(){
        _.invoke(_.pluck(this.widget.subWidgets,'$el'),'detach');
        this.widget._render();
    }

    updateWidget(nextProps){
        conststate=nextProps.widgetArgs[0];
        this.widget._setState(state);
    }
}

/**
 *OwlComponentAdapterforActivityCellwhichisBasicActivity(AbstractField)
 *TODO:RemovethisadapterwhenActivityCellisaComponent
 */
classActivityCellAdapterextendsComponentAdapter{
    renderWidget(){
        this.widget._render();
    }

    updateWidget(nextProps){
        constrecord=nextProps.widgetArgs[1];
        this.widget._reset(record);
    }
}

/**
 *OwlComponentAdapterforKanbanColumnProgressBar(FlectraWidget)
 *TODO:RemovethisadapterwhenKanbanColumnProgressBarisaComponent
 */
classKanbanColumnProgressBarAdapterextendsComponentAdapter{
    renderWidget(){
        this.widget._render();
    }

    updateWidget(nextProps){
        constoptions=nextProps.widgetArgs[0];
        constcolumnState=nextProps.widgetArgs[1];
        
        constcolumnId=options.columnID;
        constnextActiveFilter=options.progressBarStates[columnId].activeFilter;
        this.widget.activeFilter=nextActiveFilter?this.widget.activeFilter:false;
        this.widget.columnState=columnState;
        this.widget.computeCounters();
    }

    _trigger_up(ev){
        //KanbanColumnProgressBartriggers3eventsbeforebeingmounted
        //butwedon'tneedtolistentotheminourcase.
        if(this.el){
            super._trigger_up(ev);
        }
    }
}

classActivityRendererextendsAbstractRendererOwl{
    constructor(parent,props){
        super(...arguments);
        this.qweb=newQWeb(this.env.isDebug(),{_s:session.origin});
        this.qweb.add_template(utils.json_node_to_xml(props.templates));
        this.activeFilter=useState({
            state:null,
            activityTypeId:null,
            resIds:[]
        });
        this.widgetComponents={
            ActivityRecord,
            ActivityCell,
            KanbanColumnProgressBar,
        };
    }

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *GetsallactivityresIdsintheview.
     *
     *@returnsfilteredresIdsfirstthentherest.
     */
    getactivityResIds(){
        constcopiedActivityResIds=Array.from(this.props.activity_res_ids)
        returncopiedActivityResIds.sort((a,b)=>this.activeFilter.resIds.includes(a)?-1:0);
    }

    /**
     *Getsallexistingactivitytypeids.
     */
    getactivityTypeIds(){
        constactivities=Object.values(this.props.grouped_activities);
        constactivityIds=activities.flatMap(Object.keys);
        constuniqueIds=Array.from(newSet(activityIds));
        returnuniqueIds.map(Number);
    }

    getProgressBarOptions(typeId){
        return{
            columnID:typeId,
            progressBarStates:{
                [typeId]:{
                    activeFilter:this.activeFilter.activityTypeId===typeId,
                },
            },
        };
    }

    getProgressBarColumnState(typeId){
        constcounts={planned:0,today:0,overdue:0};
        for(letactivitiesofObject.values(this.props.grouped_activities)){
            if(typeIdinactivities){
                counts[activities[typeId].state]+=1;
            }
        }
        return{
            count:Object.values(counts).reduce((x,y)=>x+y),
            fields:{
                activity_state:{
                    type:'selection',
                    selection:[
                        ['planned',_t('Planned')],
                        ['today',_t('Today')],
                        ['overdue',_t('Overdue')],
                    ],
                },
            },
            progressBarValues:{
                field:'activity_state',
                colors:{planned:'success',today:'warning',overdue:'danger'},
                counts:counts,
            },
        };
    }

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------
    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onEmptyCellClicked(ev){
        this.trigger('empty_cell_clicked',{
            resId:parseInt(ev.currentTarget.dataset.resId,10),
            activityTypeId:parseInt(ev.currentTarget.dataset.activityTypeId,10),
        });
    }
    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onSendMailTemplateClicked(ev){
        this.trigger('send_mail_template',{
            activityTypeID:parseInt(ev.currentTarget.dataset.activityTypeId,10),
            templateID:parseInt(ev.currentTarget.dataset.templateId,10),
        });
    }
    /**
     *@private
     *@param{CustomEvent}ev
     */
    _onSetProgressBarState(ev){
        if(ev.detail.values.activeFilter){
            this.activeFilter.state=ev.detail.values.activeFilter;
            this.activeFilter.activityTypeId=ev.detail.columnID;
            this.activeFilter.resIds=Object.entries(this.props.grouped_activities)
                .filter(([,resIds])=>ev.detail.columnIDinresIds&&
                    resIds[ev.detail.columnID].state===ev.detail.values.activeFilter)
                .map(([key])=>parseInt(key));
        }else{
            this.activeFilter.state=null;
            this.activeFilter.activityTypeId=null;
            this.activeFilter.resIds=[];
        }
    }
}

ActivityRenderer.components={
    ActivityRecordAdapter,
    ActivityCellAdapter,
    KanbanColumnProgressBarAdapter,
};
ActivityRenderer.template='mail.ActivityRenderer';

returnpatchMixin(ActivityRenderer);

});
