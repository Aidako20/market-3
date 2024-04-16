flectra.define('project.project_rating_reporting',function(require){
'usestrict';

constcore=require('web.core');
const_t=core._t;

constviewRegistry=require('web.view_registry');

constPivotController=require('web.PivotController');
constPivotView=require('web.PivotView');

constGraphController=require('web.GraphController');
constGraphView=require('web.GraphView');

varProjectPivotController=PivotController.extend({
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        varmeasures=JSON.parse(JSON.stringify(this.measures));
        if('res_id'inmeasures){
            measures.res_id.string=_t('Task');
        }
        if('parent_res_id'inmeasures){
            measures.parent_res_id.string=_t('Project');
        }
        if('rating'inmeasures){
            measures.rating.string=_t('RatingValue(/5)');
        }
        this.measures=measures;
    },
});

varProjectPivotView=PivotView.extend({
    config:_.extend({},PivotView.prototype.config,{
        Controller:ProjectPivotController,
    }),
});

viewRegistry.add('project_rating_pivot',ProjectPivotView);

varProjectGraphController=GraphController.extend({
    /**
     *@override
     */
    init:function(){
        this._super.apply(this,arguments);
        _.each(this.measures,measure=>{
            if(measure.fieldName==='res_id'){
                measure.description=_t('Task');
            }elseif(measure.fieldName==='parent_res_id'){
                measure.description=_t('Project');
            }elseif(measure.fieldName==='rating'){
                measure.description=_t('RatingValue(/5)');
            }
        });
    },
});

varProjectGraphView=GraphView.extend({
    config:_.extend({},GraphView.prototype.config,{
        Controller:ProjectGraphController,
    }),
});

viewRegistry.add('project_rating_graph',ProjectGraphView);

});
