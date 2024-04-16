flectra.define('crm.systray.ActivityMenu',function(require){
"usestrict";

varActivityMenu=require('mail.systray.ActivityMenu');

ActivityMenu.include({

    //--------------------------------------------------
    //Private
    //--------------------------------------------------

    /**
     *@override
     */
    _getViewsList(model){
        if(model==="crm.lead"){
                return[[false,'list'],[false,'kanban'],
                        [false,'form'],[false,'calendar'],
                        [false,'pivot'],[false,'graph'],
                        [false,'activity']
                    ];
        }
        returnthis._super(...arguments);
    },

    //-----------------------------------------
    //Handlers
    //-----------------------------------------

    /**
     *@private
     *@override
     */
    _onActivityFilterClick:function(event){
        //fetchthedatafromthebuttonotherwisefetchtheonesfromtheparent(.o_mail_preview).
        vardata=_.extend({},$(event.currentTarget).data(),$(event.target).data());
        varcontext={};
        if(data.res_model==="crm.lead"){
            if(data.filter==='my'){
                context['search_default_activities_overdue']=1;
                context['search_default_activities_today']=1;
            }else{
                context['search_default_activities_'+data.filter]=1;
            }
            //Necessarybecauseactivity_idsofmail.activity.mixinhasauto_join
            //So,duplicatesarefakingthecountand"Loadmore"doesn'tshowup
            context['force_search_count']=1;
            this.do_action('crm.crm_lead_action_my_activities',{
                additional_context:context,
                clear_breadcrumbs:true,
            });
        }else{
            this._super.apply(this,arguments);
        }
    },
});
});
