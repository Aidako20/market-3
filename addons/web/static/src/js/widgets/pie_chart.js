flectra.define('web.PieChart',function(require){
"usestrict";

/**
 *ThiswidgetrenderaPieChart.Itisusedinthedashboardview.
 */

varcore=require('web.core');
varDomain=require('web.Domain');
varviewRegistry=require('web.view_registry');
varWidget=require('web.Widget');
varwidgetRegistry=require('web.widget_registry');

varqweb=core.qweb;

varPieChart=Widget.extend({
    className:'o_pie_chart',
    xmlDependencies:['/web/static/src/xml/chart.xml'],

    /**
     *@override
     *@param{Widget}parent
     *@param{Object}record
     *@param{Object}nodenodefromarch
     */
    init:function(parent,record,node){
        this._super.apply(this,arguments);

        varmodifiers=node.attrs.modifiers;
        vardomain=record.domain.concat(
            Domain.prototype.stringToArray(modifiers.domain||'[]'));
        vararch=qweb.render('web.PieChart',{
            modifiers:modifiers,
            title:node.attrs.title||modifiers.title||modifiers.measure,
        });

        varpieChartContext=JSON.parse(JSON.stringify(record.context));
        deletepieChartContext.graph_mode;
        deletepieChartContext.graph_measure;
        deletepieChartContext.graph_groupbys;

        this.subViewParams={
            modelName:record.model,
            withButtons:false,
            withControlPanel:false,
            withSearchPanel:false,
            isEmbedded:true,
            useSampleModel:record.isSample,
            mode:'pie',
        };
        this.subViewParams.searchQuery={
            context:pieChartContext,
            domain:domain,
            groupBy:[],
            timeRanges:record.timeRanges||{},
        };

        this.viewInfo={
            arch:arch,
            fields:record.fields,
            viewFields:record.fieldsInfo.dashboard,
        };
    },
    /**
     *Instantiatesthepiechartviewandstartsthegraphcontroller.
     *
     *@override
     */
    willStart:function(){
        varself=this;
        vardef1=this._super.apply(this,arguments);

        varSubView=viewRegistry.get('graph');
        varsubView=newSubView(this.viewInfo,this.subViewParams);
        vardef2=subView.getController(this).then(function(controller){
            self.controller=controller;
            returnself.controller.appendTo(document.createDocumentFragment());
        });
        returnPromise.all([def1,def2]);
    },
    /**
     *@override
     */
    start:function(){
        this.$el.append(this.controller.$el);
        returnthis._super.apply(this,arguments);
    },
    /**
     *Call`on_attach_callback`foreachsubview
     *
     *@override
     */
    on_attach_callback:function(){
        this.controller.on_attach_callback();
    },
});

widgetRegistry.add('pie_chart',PieChart);

returnPieChart;

});
