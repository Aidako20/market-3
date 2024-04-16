flectra.define('mail.ActivityRecord',function(require){
"usestrict";

varKanbanRecord=require('web.KanbanRecord');

varActivityRecord=KanbanRecord.extend({
    /**
     *@override
     */
    init:function(parent,state){
        this._super.apply(this,arguments);

        this.fieldsInfo=state.fieldsInfo.activity;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _render:function(){
        this.defs=[];
        this._replaceElement(this.qweb.render('activity-box',this.qweb_context));
        this.$el.on('click',this._onGlobalClick.bind(this));
        this.$el.addClass('o_activity_record');
        this._processFields();
        this._setupColor();
        returnPromise.all(this.defs);
    },
    /**
     *@override
     *@private
     */
    _setFieldDisplay:function($el,fieldName){
        this._super.apply(this,arguments);

        //attributemuted
        if(this.fieldsInfo[fieldName].muted){
            $el.addClass('text-muted');
        }
    },
    /**
     *@override
     *@private
     */
    _setState:function(){
        this._super.apply(this,arguments);

        //activityhasadifferentqwebcontext
        this.qweb_context={
            activity_image:this._getImageURL.bind(this),
            record:this.record,
            user_context:this.getSession().user_context,
            widget:this,
        };
    },
});
returnActivityRecord;
});
