flectra.define('hr.employee_chat',function(require){
'usestrict';
    varviewRegistry=require('web.view_registry');

    varFormController=require('web.FormController');
    varFormView=require('web.FormView');
    varFormRenderer=require('web.FormRenderer');

    varKanbanController=require('web.KanbanController');
    varKanbanView=require('web.KanbanView');
    varKanbanRenderer=require('web.KanbanRenderer');
    varKanbanRecord=require('web.KanbanRecord');

    const{Component}=owl;

    //CHATMIXIN
    varChatMixin={
        /**
         *@override
         */
        _render:function(){
            varself=this;
            returnthis._super.apply(this,arguments).then(function(){
                var$chat_button=self.$el.find('.o_employee_chat_btn');
                $chat_button.off('click').on('click',self._onOpenChat.bind(self));
            });
        },

        destroy:function(){
            if(this.$el){
                this.$el.find('.o_employee_chat_btn').off('click');
            }
            returnthis._super();
        },

        _onOpenChat:function(ev){
            ev.preventDefault();
            ev.stopImmediatePropagation();
            constenv=Component.env;
            env.messaging.openChat({employeeId:this.state.data.id});
            returntrue;
        },
    };

    //USAGEOFCHATMIXININFORMVIEWS
    varEmployeeFormRenderer=FormRenderer.extend(ChatMixin);

    varEmployeeFormView=FormView.extend({
        config:_.extend({},FormView.prototype.config,{
            Controller:FormController,
            Renderer:EmployeeFormRenderer
        }),
    });

    viewRegistry.add('hr_employee_form',EmployeeFormView);

    //USAGEOFCHATMIXININKANBANVIEWS
    varEmployeeKanbanRecord=KanbanRecord.extend(ChatMixin);

    varEmployeeKanbanRenderer=KanbanRenderer.extend({
        config:Object.assign({},KanbanRenderer.prototype.config,{
            KanbanRecord:EmployeeKanbanRecord,
        }),
    });

    varEmployeeKanbanView=KanbanView.extend({
        config:_.extend({},KanbanView.prototype.config,{
            Controller:KanbanController,
            Renderer:EmployeeKanbanRenderer
        }),
    });

    viewRegistry.add('hr_employee_kanban',EmployeeKanbanView);
});
