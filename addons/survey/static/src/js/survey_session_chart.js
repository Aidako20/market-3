flectra.define('survey.session_chart',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varSESSION_CHART_COLORS=require('survey.session_colors');

publicWidget.registry.SurveySessionChart=publicWidget.Widget.extend({
    init:function(parent,options){
        this._super.apply(this,arguments);

        this.questionType=options.questionType;
        this.answersValidity=options.answersValidity;
        this.hasCorrectAnswers=options.hasCorrectAnswers;
        this.questionStatistics=this._processQuestionStatistics(options.questionStatistics);
        this.showInputs=options.showInputs;
        this.showAnswers=false;
    },

    start:function(){
        varself=this;
        returnthis._super.apply(this,arguments).then(function(){
            self._setupChart();
        });
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Updatesthechartdatausingthelatestreceivedquestionuserinputs.
     *
     *Byupdatingthenumbersinthedataset,wetakeadvantageoftheChartjsAPI
     *thatwillautomaticallyaddanimationstoshowthenewnumber.
     *
     *@param{Object}questionStatisticsobjectcontainingchartdata(counts/labels/...)
     *@param{Integer}newAttendeesCount:maxheightofchart,notusedanymore(deprecated)
     */
    updateChart:function(questionStatistics,newAttendeesCount){
        if(questionStatistics){
            this.questionStatistics=this._processQuestionStatistics(questionStatistics);
        }

        if(this.chart){
            //onlyasingledatasetforourbarcharts
            varchartData=this.chart.data.datasets[0].data;
            for(vari=0;i<chartData.length;i++){
                varvalue=0;
                if(this.showInputs){
                    value=this.questionStatistics[i].count;
                }
                this.chart.data.datasets[0].data[i]=value;
            }

            this.chart.update();
        }
    },

    /**
     *Togglingthisparameterwilldisplayorhidethecorrectandincorrectanswersofthecurrent
     *questiondirectlyonthechart.
     *
     *@param{Boolean}showAnswers
     */
    setShowAnswers:function(showAnswers){
        this.showAnswers=showAnswers;
    },

    /**
     *Togglingthisparameterwilldisplayorhidetheuserinputsofthecurrentquestiondirectly
     *onthechart.
     *
     *@param{Boolean}showInputs
     */
    setShowInputs:function(showInputs){
        this.showInputs=showInputs;
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@private
     */
    _setupChart:function(){
        var$canvas=this.$('canvas');
        varctx=$canvas.get(0).getContext('2d');

        this.chart=newChart(ctx,this._buildChartConfiguration());
    },

    /**
     *Custombarchartconfigurationforoursurveysessionusecase.
     *
     *Quicksummaryofenabledfeatures:
     *-background_colorisoneofthe10customcolorsfromSESSION_CHART_COLORS
     *  (see_getBackgroundColorfordetails)
     *-Theticksarebiggerandboldedtobeabletoseethembetteronabigscreen(projector)
     *-Wedon'tusetooltipstokeepitassimpleaspossible
     *-Wedon'tsetasuggestedMinorMaxsothatChartwilladaptautomaticallyhimselfbasedonthegivendata
     *  The'+1'partisasmalltricktoavoidthedatalabelstobeclippedinheight
     *-Weuseacustom'datalabels'plugintobeabletodisplaythenumbervalueontopofthe
     *  associatedbarofthechart.
     *  Thisallowsthehosttodiscussresultswithattendeesinamoreinteractiveway.
     *
     *@private
     */
    _buildChartConfiguration:function(){
        return{
            type:'bar',
            data:{
                labels:this._extractChartLabels(),
                datasets:[{
                    backgroundColor:this._getBackgroundColor.bind(this),
                    data:this._extractChartData(),
                }]
            },
            options:{
                maintainAspectRatio:false,
                plugins:{
                    datalabels:{
                        color:this._getLabelColor.bind(this),
                        font:{
                            size:'50',
                            weight:'bold',
                        },
                        anchor:'end',
                        align:'top',
                    }
                },
                legend:{
                    display:false,
                },
                scales:{
                    yAxes:[{
                        ticks:{
                            display:false,
                        },
                        gridLines:{
                            display:false
                        }
                    }],
                    xAxes:[{
                        ticks:{
                            maxRotation:0,
                            fontSize:'35',
                            fontStyle:'bold',
                            fontColor:'#212529'
                        },
                        gridLines:{
                            drawOnChartArea:false,
                            color:'rgba(0,0,0,0.2)'
                        }
                    }]
                },
                tooltips:{
                    enabled:false,
                },
                layout:{
                    padding:{
                        left:0,
                        right:0,
                        top:70,
                        bottom:0
                    }
                }
            },
            plugins:[{
                /**
                 *Thewayitworksiseachlabelisanarrayofwords.
                 *eg.:ifwehaveachartlabel:"thisisanexampleofalabel"
                 *Thelibrarywillsplititas:["thisisanexample","ofalabel"]
                 *Eachvalueofthearrayrepresentsalineofthelabel.
                 *Soforthisexampleabove:itwillbedisplayedas:
                 *"thisisanexamble<br/>ofalabel",breakingthelabelin2partsandputon2linesvisually.
                 *
                 *Whatwedohereisreworkthelabelswithourownalgorithmtomakethemfitbetterinscreenspace
                 *basedonbreakpointsbasedonnumberofcolumnstodisplay.
                 *Sothisexamplewillbecome:["thisisan","exampleof","alabel"]ifwehavealotoflabelstoputinthechart.
                 *Whichwillbedisplayedas"thisisan<br/>exampleof<br/>alabel"
                 *Obviously,themorelabelsyouhave,themorecolumns,andlessscreenspaceisavailable.
                 *
                 *Wealsoadaptthefontsizebasedonthewidthavailableinthechart.
                 *
                 *Sowecounterbalancemultipletimes:
                 *-Basedonnumberofcolumns(i.e.numberofsurvey.question.answerofyourcurrentsurvey.question),
                 *  wesplitthewordsofeverylabelstomakethemdisplayonmorerows.
                 *-Basedonthewidthofthechart(whichisequivalenttoscreenwidth),
                 *  wereducethechartfonttobeabletofitmorecharacters.
                 *-Basedonthelongestwordpresentinthelabels,weapplyacertainratiowiththewidthofthechart
                 *  togetamoreaccuratefontsizeforthespaceavailable.
                 *
                 *@param{Object}chart
                 */
                beforeInit:function(chart){
                    constnbrCol=chart.data.labels.length;
                    constminRatio=0.4;
                    //Numbersofmaximumcharactersperlinetoprintbasedonthenumberofcolumnsanddefaultratioforthefontsize
                    //Between1and2->25,3and4->20,5and6->15,...
                    constcharPerLineBreakpoints=[
                        [1,2,25,minRatio],
                        [3,4,20,minRatio],
                        [5,6,15,0.45],
                        [7,8,10,0.65],
                        [9,null,7,0.7],
                    ];

                    letcharPerLine;
                    letfontRatio;
                    charPerLineBreakpoints.forEach(([lowerBound,upperBound,value,ratio])=>{
                        if(nbrCol>=lowerBound&&(upperBound===null||nbrCol<=upperBound)){
                            charPerLine=value;
                            fontRatio=ratio;
                        }
                    });

                    //Adaptfontsizeifthenumberofcharactersperlineisunderthemaximum
                    if(charPerLine<25){
                        constallWords=chart.data.labels.reduce((accumulator,words)=>accumulator.concat(''.concat(words)));
                        constmaxWordLength=Math.max(...allWords.split('').map((word)=>word.length));
                        fontRatio=maxWordLength>charPerLine?minRatio:fontRatio;
                        chart.options.scales.xAxes[0].ticks.fontSize=Math.min(parseInt(chart.options.scales.xAxes[0].ticks.fontSize),chart.width*fontRatio/(nbrCol));
                    }

                    chart.data.labels.forEach(function(label,index,labelsList){
                        //Splitallthewordsofthelabel
                        constwords=label.split("");
                        letresultLines=[];
                        letcurrentLine=[];
                        for(leti=0;i<words.length;i++){
                            //Ifthewordweareaddingexceedalreadythenumberofcharactersfortheline,weadditanywaybeforepassingtoanewline
                            currentLine.push(words[i]);

                            //Continuetoaddwordsinthelineifthereisenoughspaceandifthereisatleastonemorewordtoadd
                            constnextWord=i+1<words.length?words[i+1]:null;
                            if(nextWord){
                                constnextLength=currentLine.join('').length+nextWord.length;
                                if(nextLength<=charPerLine){
                                    continue;
                                }
                            }
                            //Addtheconstructedlineandresetthevariableforthenextline
                            constnewLabelLine=currentLine.join('');
                            resultLines.push(newLabelLine);
                            currentLine=[];
                        }
                        labelsList[index]=resultLines;
                    });
                },
            }],
        };
    },

    /**
     *Returnsthelabeloftheassociatedsurvey.question.answer.
     *
     *@private
     */
    _extractChartLabels:function(){
        returnthis.questionStatistics.map(function(point){
            returnpoint.text;
        });
    },

    /**
     *Wesimplyreturnanarrayofzerosasinitialvalue.
     *Thechartwillupdateafterwardsasattendeesaddtheiruserinputs.
     *
     *@private
     */
    _extractChartData:function(){
        returnthis.questionStatistics.map(function(){
            return0;
        });
    },

    /**
     *CustommethodthatreturnsacolorfromSESSION_CHART_COLORS.
     *Itloopsthroughthetenvaluesandassignthemsequentially.
     *
     *Wehaveaspecialmechanicwhenthehostshowstheanswersofaquestion.
     *Wronganswersare"fadedout"usinga0.3opacity.
     *
     *@param{Object}metaData
     *@param{Integer}metaData.dataIndextheindexofthelabel,matchingtheindexoftheanswer
     *  in'this.answersValidity'
     *@private
     */
    _getBackgroundColor:function(metaData){
        varopacity='0.8';
        if(this.showAnswers&&this.hasCorrectAnswers){
            if(!this._isValidAnswer(metaData.dataIndex)){
                opacity='0.2';
            }
        }
        varrgb=SESSION_CHART_COLORS[metaData.dataIndex];
        return`rgba(${rgb},${opacity})`;
    },

    /**
     *Custommethodthatreturnsthesurvey.question.answerlabelcolor.
     *
     *Break-downofusecases:
     *-Redifthehostisshowinganswer,andtheassociatedanswerisnotcorrect
     *-Greenifthehostisshowinganswer,andtheassociatedansweriscorrect
     *-Blackinallothercases
     *
     *@param{Object}metaData
     *@param{Integer}metaData.dataIndextheindexofthelabel,matchingtheindexoftheanswer
     *  in'this.answersValidity'
     *@private
     */
    _getLabelColor:function(metaData){
        if(this.showAnswers&&this.hasCorrectAnswers){
            if(this._isValidAnswer(metaData.dataIndex)){
                return'#2CBB70';
            }else{
                return'#D9534F';
            }
        }
        return'#212529';
    },

    /**
     *Smallhelpermethodthatreturnsthevalidityoftheanswerbasedonitsindex.
     *
     *WeneedthisspecialhandlingbecauseofChartjsdatastructure.
     *Thelibrarydeterminestheparameters(color/label/...)byonlypassingtheanswer'index'
     *(andnottheidoranythingelsewecanidentify).
     *
     *@param{Integer}answerIndex
     *@private
     */
    _isValidAnswer:function(answerIndex){
        returnthis.answersValidity[answerIndex];
    },

    /**
     *Specialutilitymethodthatwillprocessthestatisticswereceivefromthe
     *survey.question#_prepare_statisticsmethod.
     *
     *Formultiplechoicequestions,thevaluesweneedarestoredinadifferentplace.
     *Wesimplyreturnthevaluestomaketheuseofthestatisticscommonforbothsimpleand
     *multiplechoicequestions.
     *
     *Seesurvey.question#_get_stats_dataformoredetails
     *
     *@param{Object}rawStatistics
     *@private
     */
    _processQuestionStatistics:function(rawStatistics){
        if(this.questionType==='multiple_choice'){
            returnrawStatistics[0].values;
        }

        returnrawStatistics;
    }
});

returnpublicWidget.registry.SurveySessionChart;

});
