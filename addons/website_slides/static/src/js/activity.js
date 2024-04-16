flectra.define('website_slides.Activity',function(require){
"usestrict";

varfield_registry=require('web.field_registry');

require('mail.Activity');

varKanbanActivity=field_registry.get('kanban_activity');

functionapplyInclude(Activity){
    Activity.include({
        events:_.extend({},Activity.prototype.events,{
            'click.o_activity_action_grant_access':'_onGrantAccess',
            'click.o_activity_action_refuse_access':'_onRefuseAccess',
        }),

        _onGrantAccess:function(event){
            varself=this;
            varpartnerId=$(event.currentTarget).data('partner-id');
            this._rpc({
                model:'slide.channel',
                method:'action_grant_access',
                args:[this.res_id,partnerId],
            }).then(function(result){
                self.trigger_up('reload');
            });
        },

        _onRefuseAccess:function(event){
            varself=this;
            varpartnerId=$(event.currentTarget).data('partner-id');
            this._rpc({
                model:'slide.channel',
                method:'action_refuse_access',
                args:[this.res_id,partnerId],
            }).then(function(){
                self.trigger_up('reload');
            });
        },
    });
}

applyInclude(KanbanActivity);

});

flectra.define('website_slides/static/src/components/activity/activity.js',function(require){
'usestrict';

constcomponents={
    Activity:require('mail/static/src/components/activity/activity.js'),
};
const{patch}=require('web.utils');

patch(components.Activity,'website_slides/static/src/components/activity/activity.js',{

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    async_onGrantAccess(ev){
        awaitthis.env.services.rpc({
            model:'slide.channel',
            method:'action_grant_access',
            args:[[this.activity.thread.id]],
            kwargs:{partner_id:this.activity.requestingPartner.id},
        });
        this.trigger('reload');
    },
    /**
     *@private
     */
    async_onRefuseAccess(ev){
        awaitthis.env.services.rpc({
            model:'slide.channel',
            method:'action_refuse_access',
            args:[[this.activity.thread.id]],
            kwargs:{partner_id:this.activity.requestingPartner.id},
        });
        this.trigger('reload');
    },
});

});
