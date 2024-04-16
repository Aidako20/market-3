flectra.define('web.Context',function(require){
"usestrict";

varClass=require('web.Class');
varpyUtils=require('web.py_utils');

varContext=Class.extend({
    init:function(){
        this.__ref="compound_context";
        this.__contexts=[];
        this.__eval_context=null;
        varself=this;
        _.each(arguments,function(x){
            self.add(x);
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    add:function(context){
        this.__contexts.push(context);
        returnthis;
    },
    eval:function(){
        returnpyUtils.eval('context',this);
    },
    /**
     *Settheevaluationcontexttobeusedwhenweactuallyeval.
     *
     *@param{Object}evalContext
     *@returns{Context}
     */
    set_eval_context:function(evalContext){
        //aspecialcaseneedstobedoneformomentobjects. Datesare
        //internallyrepresentedbyamomentobject,buttheyneedtobe
        //convertedtotheserverformatbeforebeingsent.WecallthetoJSON
        //method,becauseitreturnsthedatewiththeformatrequiredbythe
        //server
        for(varkeyinevalContext){
            if(evalContext[key]instanceofmoment){
                evalContext[key]=evalContext[key].toJSON();
            }
        }
        this.__eval_context=evalContext;
        returnthis;
    },
});

returnContext;

});
