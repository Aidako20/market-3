flectra.define('survey.test_survey_session_manage_tour',function(require){
"usestrict";

vartour=require('web_tour.tour');
varsurveySessionTools=require('survey.session_tour_tools');

/**
 *SincethechartisrenderedusingSVG,wecan'tusejQuerytriggerstocheckifeverything
 *iscorrectlyrendered.
 *Thishelpermethodreturnsthechartdata(Chartjsframeworkspecific)inthefollowingstructure:
 *[{value,backgroundColor,labelColor}]
 */
vargetChartData=function(){
    varchartData=[];
    varrootWidget=flectra.__DEBUG__.services['root.widget'];
    varsurveyManagePublicWidget=rootWidget.publicWidgets.find(function(widget){
        returnwidget.$el.hasClass('o_survey_session_manage');
    });

    if(!surveyManagePublicWidget){
        returnchartData;
    }

    surveyManagePublicWidget.resultsChart.chart.data.datasets[0].data.forEach(function(value,index){
        chartData.push({
            value:value,
            backgroundColor:surveyManagePublicWidget.resultsChart._getBackgroundColor({dataIndex:index}),
            labelColor:surveyManagePublicWidget.resultsChart._getLabelColor({dataIndex:index}),
        });
    });

    returnchartData;
};

varnextScreen=function(){
    vare=$.Event('keydown');
    e.keyCode=39;//arrow-right
    $(document).trigger(e);
};

varpreviousScreen=function(){
    vare=$.Event('keydown');
    e.keyCode=37;//arrow-left
    $(document).trigger(e);
};

varREGULAR_ANSWER_COLOR='#212529';
varCORRECT_ANSWER_COLOR='#2CBB70';
varWRONG_ANSWER_COLOR='#D9534F';

/**
 *A'regular'answerisananswerthatisnorcorrect,norincorrect.
 *Thecheckisbasedonthespecificopacity(0.8)andcolorofthoseanswers.
 */
varisRegularAnswer=function(answer){
    returnanswer.backgroundColor.includes('0.8')&&
        answer.labelColor===REGULAR_ANSWER_COLOR;
};

/**
 *Thecheckisbasedonthespecificopacity(0.8)andcolorofcorrectanswers.
 */
varisCorrectAnswer=function(answer){
    returnanswer.backgroundColor.includes('0.8')&&
        answer.labelColor===CORRECT_ANSWER_COLOR;
};

/**
 *Thecheckisbasedonthespecificopacity(0.2)andcolorofincorrectanswers.
 */
varisIncorrectAnswer=function(answer){
    returnanswer.backgroundColor.includes('0.2')&&
        answer.labelColor===WRONG_ANSWER_COLOR;
};

/**
 *Tourthatwilltestthewholesurveysessionfromthehostpointofview.
 *
 *Breakdownofthemainpoints:
 *-Openthe'sessionmanager'(thesessionwasalreadycreatedbyaprevioustour)
 *-Displaythenicknamequestion,andmovetothenextone(asanswersarenotdisplayed)
 *-Checkanswersarecorrectlydisplayedforthe3'simple'questiontypes(text,date,datetime)
 *-Movetothechoicequestionandcheckthatanswersaredisplayed
 *  (Thecheckisrathercomplex,see'getChartData'fordetails)
 *-Ifeverythingiscorrectlydisplayed,movetothenextquestion
 *-Onthescoredchoicequestion,checkthatthescreensarecorrectlychained:
 *  noresultsdisplayed->resultsdisplayed->correct/incorrectanswers->leaderboard
 *-Onthescored+timedmultiplechoicequestion,checkthesamethanpreviousquestion,
 *  exceptthattheresultsaresupposedtobedisplayedautomaticallywhenthequestiontimerrunsout
 *-Testthe'back'behaviorandcheckthatscreensarereversedcorrectly
 *-Checkthatourfinalleaderboardiscorrectbasedonattendeesanswers
 *-Closethesurveysession
 */
tour.register('test_survey_session_manage_tour',{
    url:"/web",
    test:true,
},[].concat(surveySessionTools.accessSurveySteps,[{
    trigger:'button[name="action_open_session_manager"]',
},{
    trigger:'h1:contains("Nickname")',
    run:function(){}//checknicknamequestionisdisplayed
},{
    trigger:'h1',
    run:nextScreen
},{
    trigger:'h1:contains("TextQuestion")',
    run:function(){}//checktextquestionisdisplayed
},{
    trigger:'.o_survey_session_progress_small:contains("3/3")',
    run:function(){}//checkwehave3answers
},{
    trigger:'.o_survey_session_text_answer_container:contains("Attendee1isthebest")',
    run:function(){}//checkattendee1answerisdisplayed
},{
    trigger:'.o_survey_session_text_answer_container:contains("Attendee2rulez")',
    run:function(){}//checkattendee2answerisdisplayed
},{
    trigger:'.o_survey_session_text_answer_container:contains("Attendee3willcrushyou")',
    run:function(){}//checkattendee3answerisdisplayed
},{
    trigger:'h1',
    run:nextScreen
},{
    trigger:'.o_survey_session_progress_small:contains("2/3")',
    run:function(){}//checkwehave2answers
},{
    trigger:'.o_survey_session_text_answer_container:contains("10/10/2010")',
    run:function(){}//checkattendee1answerisdisplayed
},{
    trigger:'.o_survey_session_text_answer_container:contains("11/11/2011")',
    run:function(){}//checkattendee2answerisdisplayed
},{
    trigger:'h1',
    run:nextScreen
},{
    trigger:'.o_survey_session_progress_small:contains("2/3")',
    run:function(){}//checkwehave2answers
},{
    trigger:'.o_survey_session_text_answer_container:contains("10/10/201010:00:00")',
    run:function(){}//checkattendee2answerisdisplayed
},{
    trigger:'.o_survey_session_text_answer_container:contains("11/11/201115:55:55")',
    run:function(){}//checkattendee3answerisdisplayed
},{
    trigger:'h1',
    run:nextScreen
},{
    trigger:'h1:contains("RegularSimpleChoice")',
    run:function(){
        varchartData=getChartData();
        if(chartData.length!==3){
            console.error('Chartdatashouldcontain3records!');
            return;
        }

        varfirstAnswerData=chartData[0];
        if(firstAnswerData.value!==2||!isRegularAnswer(firstAnswerData)){
            console.error('Firstanswershouldbepickedby2users!');
            return;
        }

        varsecondAnswerData=chartData[1];
        if(secondAnswerData.value!==1||!isRegularAnswer(secondAnswerData)){
            console.error('Secondanswershouldbepickedby1user!');
            return;
        }

        varthirdAnswerData=chartData[2];
        if(thirdAnswerData.value!==0||!isRegularAnswer(thirdAnswerData)){
            console.error('Thirdanswershouldbepickedbynousers!');
            return;
        }

        nextScreen();
    }
},{
    trigger:'h1:contains("ScoredSimpleChoice")',
    run:function(){
        varchartData=getChartData();
        if(chartData.length!==4){
            console.error('Chartdatashouldcontain4records!');
            return;
        }

        for(vari=0;i<chartData.length;i++){
            if(chartData[i].value!==0){
                console.error(
                    'Chartdatashouldallbe0because"nextscreen"thatshows'+
                    'answersvaluesisnottriggeredyet!');
                return;
            }
        }

        nextScreen();
        chartData=getChartData();

        varfirstAnswerData=chartData[0];
        if(firstAnswerData.value!==1||!isRegularAnswer(firstAnswerData)){
            console.error(
                'Firstanswershouldbepickedby1useranditscorrectnessshouldnotbeshownyet!'
            );
            return;
        }

        varsecondAnswerData=chartData[1];
        if(secondAnswerData.value!==1||!isRegularAnswer(secondAnswerData)){
            console.error(
                'Secondanswershouldbepickedby1useranditscorrectnessshouldnotbeshownyet!'
            );
            return;
        }

        varthirdAnswerData=chartData[2];
        if(thirdAnswerData.value!==1||!isRegularAnswer(thirdAnswerData)){
            console.error(
                'Thirdanswershouldbepickedby1useranditscorrectnessshouldnotbeshownyet!'
            );
            return;
        }

        varfourthAnswerData=chartData[3];
        if(fourthAnswerData.value!==0||!isRegularAnswer(fourthAnswerData)){
            console.error(
                'Fourthanswershouldbepickedbynousersanditscorrectnessshouldnotbeshownyet!'
            );
            return;
        }

        nextScreen();
        chartData=getChartData();

        firstAnswerData=chartData[0];
        if(firstAnswerData.value!==1||!isCorrectAnswer(firstAnswerData)){
            console.error(
                'Firstanswershouldbepickedby1useranditshouldbecorrect!'
            );
            return;
        }

        secondAnswerData=chartData[1];
        if(secondAnswerData.value!==1||!isIncorrectAnswer(secondAnswerData)){
            console.error(
                'Secondanswershouldbepickedby1useranditshouldbeincorrect!'
            );
            return;
        }

        thirdAnswerData=chartData[2];
        if(thirdAnswerData.value!==1||!isIncorrectAnswer(thirdAnswerData)){
            console.error(
                'Thirdanswershouldbepickedby1useranditshouldbeincorrect!'
            );
            return;
        }

        fourthAnswerData=chartData[3];
        if(fourthAnswerData.value!==0||!isIncorrectAnswer(fourthAnswerData)){
            console.error(
                'Fourthanswershouldbepickedbynousersanditshouldbeincorrect!'
            );
            return;
        }

        nextScreen();
        nextScreen();
    }
},{
    trigger:'h1:contains("TimedScoredMultipleChoice")',
    run:function(){
        varchartData=getChartData();
        if(chartData.length!==3){
            console.error('Chartdatashouldcontain4records!');
            return;
        }

        for(vari=0;i<chartData.length;i++){
            if(chartData[i].value!==0){
                console.error(
                    'Chartdatashouldallbe0because"nextscreen"thatshows'+
                    'answersvaluesisnottriggeredyet!');
                return;
            }
        }

        //after1second,resultsaredisplayedautomaticallybecausequestiontimerrunsout
        //weadd1extrasecondbecauseofthewaythetimerworks:
        //itonlytriggersthetime_upevent1secondAFTERthedelayispassed
        setTimeout(function(){
            chartData=getChartData();
            varfirstAnswerData=chartData[0];
            if(firstAnswerData.value!==2||!isRegularAnswer(firstAnswerData)){
                console.error(
                    'Firstanswershouldbepickedby2usersanditscorrectnessshouldnotbeshownyet!'
                );
                return;
            }

            varsecondAnswerData=chartData[1];
            if(secondAnswerData.value!==2||!isRegularAnswer(secondAnswerData)){
                console.error(
                    'Secondanswershouldbepickedby2usersanditscorrectnessshouldnotbeshownyet!'
                );
                return;
            }

            varthirdAnswerData=chartData[2];
            if(thirdAnswerData.value!==1||!isRegularAnswer(thirdAnswerData)){
                console.error(
                    'Thirdanswershouldbepickedby1useranditscorrectnessshouldnotbeshownyet!'
                );
                return;
            }

            nextScreen();
            chartData=getChartData();

            firstAnswerData=chartData[0];
            if(firstAnswerData.value!==2||!isCorrectAnswer(firstAnswerData)){
                console.error(
                    'Firstanswershouldbepickedby2usersanditshouldbecorrect!'
                );
                return;
            }

            secondAnswerData=chartData[1];
            if(secondAnswerData.value!==2||!isCorrectAnswer(secondAnswerData)){
                console.error(
                    'Secondanswershouldbepickedby2usersanditshouldbecorrect!'
                );
                return;
            }

            thirdAnswerData=chartData[2];
            if(thirdAnswerData.value!==1||!isIncorrectAnswer(thirdAnswerData)){
                console.error(
                    'Thirdanswershouldbepickedby1useranditshouldbeincorrect!'
                );
                return;
            }

            nextScreen();
        },2100);
    }
},{
    trigger:'h1:contains("FinalLeaderboard")',
    run:function(){}//FinalLeaderboardisdisplayed
},{
    trigger:'h1',
    run:function(){
        //previousscreentesting
        previousScreen();
        varchartData=getChartData();

        varfirstAnswerData=chartData[0];
        if(firstAnswerData.value!==2||!isCorrectAnswer(firstAnswerData)){
            console.error(
                'Firstanswershouldbepickedby2usersanditshouldbecorrect!'
            );
            return;
        }

        varsecondAnswerData=chartData[1];
        if(secondAnswerData.value!==2||!isCorrectAnswer(secondAnswerData)){
            console.error(
                'Secondanswershouldbepickedby2usersanditshouldbecorrect!'
            );
            return;
        }

        varthirdAnswerData=chartData[2];
        if(thirdAnswerData.value!==1||!isIncorrectAnswer(thirdAnswerData)){
            console.error(
                'Thirdanswershouldbepickedby1useranditshouldbeincorrect!'
            );
            return;
        }

        previousScreen();
        chartData=getChartData();

        firstAnswerData=chartData[0];
        if(firstAnswerData.value!==2||!isRegularAnswer(firstAnswerData)){
            console.error(
                'Firstanswershouldbepickedby2usersanditscorrectnessshouldnotbeshown!'
            );
            return;
        }

        secondAnswerData=chartData[1];
        if(secondAnswerData.value!==2||!isRegularAnswer(secondAnswerData)){
            console.error(
                'Secondanswershouldbepickedby2usersanditscorrectnessshouldnotbeshown!'
            );
            return;
        }

        thirdAnswerData=chartData[2];
        if(thirdAnswerData.value!==1||!isRegularAnswer(thirdAnswerData)){
            console.error(
                'Thirdanswershouldbepickedby1useranditscorrectnessshouldnotbeshown!'
            );
            return;
        }

        previousScreen();
        chartData=getChartData();

        for(vari=0;i<chartData.length;i++){
            if(chartData[i].value!==0){
                console.error(
                    'Chartdatashouldallbe0because"nextscreen"thatshows'+
                    'answersvaluesisnottriggeredyet!');
                return;
            }
        }

        //Nowwegoforwardtothe"FinalLeaderboard"again(3times)
        for(i=0;i<3;i++){
            nextScreen();
        }
    }
},{
    trigger:'h1:contains("FinalLeaderboard")',
    run:function(){}//FinalLeaderboardisdisplayed
},{
    trigger:'.o_survey_session_close:has("i.fa-close")'
},{
    trigger:'button[name="action_start_session"]',
    run:function(){}//checkthatwecanstartanothersession
}]));

});
