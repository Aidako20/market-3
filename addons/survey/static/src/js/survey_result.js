flectra.define('survey.result',function(require){
'usestrict';

var_t=require('web.core')._t;
varajax=require('web.ajax');
varpublicWidget=require('web.public.widget');

//ThegivencolorsarethesameasthoseusedbyD3
varD3_COLORS=["#1f77b4","#ff7f0e","#aec7e8","#ffbb78","#2ca02c","#98df8a","#d62728",
                    "#ff9896","#9467bd","#c5b0d5","#8c564b","#c49c94","#e377c2","#f7b6d2",
                    "#7f7f7f","#c7c7c7","#bcbd22","#dbdb8d","#17becf","#9edae5"];

//TODOawa:thiswidgetloadsallrecordsandonlyhidessomebasedonpage
//->thisisugly/notefficient,needstoberefactored
publicWidget.registry.SurveyResultPagination=publicWidget.Widget.extend({
    events:{
        'clickli.o_survey_js_results_paginationa':'_onPageClick',
    },

    //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
     *@override
     *@param{$.Element}params.questionsElTheelementcontainingtheactualquestions
     *  tobeabletohide/showthembasedonthepagenumber
     */
    init:function(parent,params){
        this._super.apply(this,arguments);
        this.$questionsEl=params.questionsEl;
    },

    /**
     *@override
     */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self.limit=self.$el.data("record_limit");
        });
    },

    //-------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onPageClick:function(ev){
        ev.preventDefault();
        this.$('li.o_survey_js_results_pagination').removeClass('active');

        var$target=$(ev.currentTarget);
        $target.closest('li').addClass('active');
        this.$questionsEl.find('tbodytr').addClass('d-none');

        varnum=$target.text();
        varmin=(this.limit*(num-1))-1;
        if(min===-1){
            this.$questionsEl.find('tbodytr:lt('+this.limit*num+')')
                .removeClass('d-none');
        }else{
            this.$questionsEl.find('tbodytr:lt('+this.limit*num+'):gt('+min+')')
                .removeClass('d-none');
        }

    },
});

/**
 *Widgetresponsiblefortheinitializationandthedrawingofthevariouscharts.
 *
 */
publicWidget.registry.SurveyResultChart=publicWidget.Widget.extend({
    jsLibs:[
        '/web/static/lib/Chart/Chart.js',
    ],

    //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
     *Initializesthewidgetbasedonitsdefinedgraph_typeandloadsthechart.
     *
     *@override
     */
    start:function(){
        varself=this;

        returnthis._super.apply(this,arguments).then(function(){
            self.graphData=self.$el.data("graphData");

            if(self.graphData&&self.graphData.length!==0){
                switch(self.$el.data("graphType")){
                    case'multi_bar':
                        self.chartConfig=self._getMultibarChartConfig();
                        break;
                    case'bar':
                        self.chartConfig=self._getBarChartConfig();
                        break;
                    case'pie':
                        self.chartConfig=self._getPieChartConfig();
                        break;
                    case'doughnut':
                        self.chartConfig=self._getDoughnutChartConfig();
                        break;
                }

                self._loadChart();
            }
        });
    },

    //-------------------------------------------------------------------------
    //Private
    //-------------------------------------------------------------------------

    /**
     *Returnsastandardmultibarchartconfiguration.
     *
     *@private
     */
    _getMultibarChartConfig:function(){
        return{
            type:'bar',
            data:{
                labels:this.graphData[0].values.map(function(value){
                    returnvalue.text;
                }),
                datasets:this.graphData.map(function(group,index){
                    vardata=group.values.map(function(value){
                        returnvalue.count;
                    });
                    return{
                        label:group.key,
                        data:data,
                        backgroundColor:D3_COLORS[index%20],
                    };
                })
            },
            options:{
                scales:{
                    xAxes:[{
                        ticks:{
                            callback:this._customTick(25),
                        },
                    }],
                    yAxes:[{
                        ticks:{
                            precision:0,
                        },
                    }],
                },
                tooltips:{
                    callbacks:{
                        title:function(tooltipItem,data){
                            returndata.labels[tooltipItem[0].index];
                        }
                    }
                },
            },
        };
    },

    /**
     *Returnsastandardbarchartconfiguration.
     *
     *@private
     */
    _getBarChartConfig:function(){
        return{
            type:'bar',
            data:{
                labels:this.graphData[0].values.map(function(value){
                    returnvalue.text;
                }),
                datasets:this.graphData.map(function(group){
                    vardata=group.values.map(function(value){
                        returnvalue.count;
                    });
                    return{
                        label:group.key,
                        data:data,
                        backgroundColor:data.map(function(val,index){
                            returnD3_COLORS[index%20];
                        }),
                    };
                })
            },
            options:{
                legend:{
                    display:false,
                },
                scales:{
                    xAxes:[{
                        ticks:{
                            callback:this._customTick(35),
                        },
                    }],
                    yAxes:[{
                        ticks:{
                                precision:0,
                        },
                    }],
                },
                tooltips:{
                    enabled:false,
                }
            },
        };
    },

    /**
     *Returnsastandardpiechartconfiguration.
     *
     *@private
     */
    _getPieChartConfig:function(){
        varcounts=this.graphData.map(function(point){
            returnpoint.count;
        });

        return{
            type:'pie',
            data:{
                labels:this.graphData.map(function(point){
                    returnpoint.text;
                }),
                datasets:[{
                    label:'',
                    data:counts,
                    backgroundColor:counts.map(function(val,index){
                        returnD3_COLORS[index%20];
                    }),
                }]
            }
        };
    },

    _getDoughnutChartConfig:function(){
        varscoring_percentage=this.$el.data("scoring_percentage")||0.0;
        varcounts=this.graphData.map(function(point){
            returnpoint.count;
        });

        return{
            type:'doughnut',
            data:{
                labels:this.graphData.map(function(point){
                    returnpoint.text;
                }),
                datasets:[{
                    label:'',
                    data:counts,
                    backgroundColor:counts.map(function(val,index){
                        returnD3_COLORS[index%20];
                    }),
                }]
            },
            options:{
                title:{
                    display:true,
                    text:_.str.sprintf(_t("OverallPerformance%.2f%s"),parseFloat(scoring_percentage),'%'),
                },
            }
        };
    },

    /**
     *CustomTickfunctiontoreplaceoverflowingtextwith'...'
     *
     *@private
     *@param{Integer}tickLimit
     */
    _customTick:function(tickLimit){
        returnfunction(label){
            if(label.length<=tickLimit){
                returnlabel;
            }else{
                returnlabel.slice(0,tickLimit)+'...';
            }
        };
    },

    /**
     *LoadsthechartusingtheprovidedChartlibrary.
     *
     *@private
     */
    _loadChart:function(){
        this.$el.css({position:'relative'});
        var$canvas=this.$('canvas');
        varctx=$canvas.get(0).getContext('2d');
        returnnewChart(ctx,this.chartConfig);
    }
});

publicWidget.registry.SurveyResultWidget=publicWidget.Widget.extend({
    selector:'.o_survey_result',
    events:{
        'clicktd.survey_answeri.fa-filter':'_onSurveyAnswerFilterClick',
        'click.clear_survey_filter':'_onClearFilterClick',
        'clickspan.filter-all':'_onFilterAllClick',
        'clickspan.filter-finished':'_onFilterFinishedClick',
    },

    //--------------------------------------------------------------------------
    //Widget
    //--------------------------------------------------------------------------

    /**
    *@override
    */
    willStart:function(){
        varurl='/web/webclient/locale/'+(document.documentElement.getAttribute('lang')||'en_US').replace('-','_');
        varlocaleReady=ajax.loadJS(url);
        returnPromise.all([this._super.apply(this,arguments),localeReady]);
    },

    /**
    *@override
    */
    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            varallPromises=[];

            self.$('.pagination').each(function(){
                varquestionId=$(this).data("question_id");
                allPromises.push(newpublicWidget.registry.SurveyResultPagination(self,{
                    'questionsEl':self.$('#survey_table_question_'+questionId)
                }).attachTo($(this)));
            });

            self.$('.survey_graph').each(function(){
                allPromises.push(newpublicWidget.registry.SurveyResultChart(self)
                    .attachTo($(this)));
            });

            if(allPromises.length!==0){
                returnPromise.all(allPromises);
            }else{
                returnPromise.resolve();
            }
        });
    },

    //-------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     */
    _onSurveyAnswerFilterClick:function(ev){
        varcell=$(ev.target);
        varrow_id=cell.data('row_id')|0;
        varanswer_id=cell.data('answer_id');

        varparams=newURLSearchParams(window.location.search);
        varfilters=params.get('filters')?params.get('filters')+"|"+row_id+','+answer_id:row_id+','+answer_id;
        params.set('filters',filters);

        window.location.href=window.location.pathname+'?'+params.toString();
    },

    /**
     *@private
     *@param{Event}ev
     */
    _onClearFilterClick:function(ev){
        varparams=newURLSearchParams(window.location.search);
        params.delete('filters');
        params.delete('finished');
        window.location.href=window.location.pathname+'?'+params.toString();
    },

    /**
     *@private
     *@param{Event}ev
     */
    _onFilterAllClick:function(ev){
        varparams=newURLSearchParams(window.location.search);
        params.delete('finished');
        window.location.href=window.location.pathname+'?'+params.toString();
    },

    /**
     *@private
     *@param{Event}ev
     */
    _onFilterFinishedClick:function(ev){
        varparams=newURLSearchParams(window.location.search);
        params.set('finished',true);
        window.location.href=window.location.pathname+'?'+params.toString();
    },
});

return{
    resultWidget:publicWidget.registry.SurveyResultWidget,
    chartWidget:publicWidget.registry.SurveyResultChart,
    paginationWidget:publicWidget.registry.SurveyResultPagination
};

});
