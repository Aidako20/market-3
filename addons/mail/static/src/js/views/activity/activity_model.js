flectra.define('mail.ActivityModel',function(require){
'usestrict';

constBasicModel=require('web.BasicModel');
constsession=require('web.session');

constActivityModel=BasicModel.extend({

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------
    /**
     *Addthefollowing(activityspecific)keyswhenperforminga`get`onthe
     *mainlistdatapoint:
     *-activity_types
     *-activity_res_ids
     *-grouped_activities
     *
     *@override
     */
    __get:function(){
        varresult=this._super.apply(this,arguments);
        if(result&&result.model===this.modelName&&result.type==='list'){
            _.extend(result,this.additionalData,{getKanbanActivityData:this.getKanbanActivityData});
        }
        returnresult;
    },
    /**
     *@param{Object}activityGroup
     *@param{integer}resId
     *@returns{Object}
     */
    getKanbanActivityData(activityGroup,resId){
        return{
            data:{
                activity_ids:{
                    model:'mail.activity',
                    res_ids:activityGroup.ids,
                },
                activity_state:activityGroup.state,
                closest_deadline:activityGroup.o_closest_deadline,
            },
            fields:{
                activity_ids:{},
                activity_state:{
                    selection:[
                        ['overdue',"Overdue"],
                        ['today',"Today"],
                        ['planned',"Planned"],
                    ],
                },
            },
            fieldsInfo:{},
            model:this.model,
            type:'record',
            res_id:resId,
            getContext:function(){
                return{};
            },
        };
    },
    /**
     *@override
     *@param{Array[]}params.domain
     */
    __load:function(params){
        this.originalDomain=_.extend([],params.domain);
        params.domain.push(['activity_ids','!=',false]);
        this.domain=params.domain;
        this.modelName=params.modelName;
        params.groupedBy=[];
        vardef=this._super.apply(this,arguments);
        returnPromise.all([def,this._fetchData()]).then(function(result){
            returnresult[0];
        });
    },
    /**
     *@override
     *@param{Array[]}[params.domain]
     */
    __reload:function(handle,params){
        if(params&&'domain'inparams){
            this.originalDomain=_.extend([],params.domain);
            params.domain.push(['activity_ids','!=',false]);
            this.domain=params.domain;
        }
        if(params&&'groupBy'inparams){
            params.groupBy=[];
        }
        vardef=this._super.apply(this,arguments);
        returnPromise.all([def,this._fetchData()]).then(function(result){
            returnresult[0];
        });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Fetchactivitydata.
     *
     *@private
     *@returns{Promise}
     */
    _fetchData:function(){
        varself=this;
        returnthis._rpc({
            model:"mail.activity",
            method:'get_activity_data',
            kwargs:{
                res_model:this.modelName,
                domain:this.domain,
                context:session.user_context,
            }
        }).then(function(result){
            self.additionalData=result;
        });
    },
});

returnActivityModel;

});
