flectra.define('survey.tour_test_survey_chained_conditional_questions',function(require){
'usestrict';

consttour=require('web_tour.tour');

tour.register('test_survey_chained_conditional_questions',{
    test:true,
    url:'/survey/start/3cfadce3-3f7e-41da-920d-10fa0eb19527',
},[
    {
        content:'ClickonStart',
        trigger:'button.btn:contains("Start")',
    },{
        content:'AnswerQ1withAnswer1',
        trigger:'div.js_question-wrapper:contains("Q1")label:contains("Answer1")',
    },{
        content:'AnswerQ2withAnswer1',
        trigger:'div.js_question-wrapper:contains("Q2")label:contains("Answer1")',
    },{
        content:'AnswerQ3withAnswer1',
        trigger:'div.js_question-wrapper:contains("Q3")label:contains("Answer1")',
    },{
        content:'AnswerQ1withAnswer2', //Thisshouldhideallremainingquestions.
        trigger:'div.js_question-wrapper:contains("Q1")label:contains("Answer2")',
    },{
        content:'Checkthatonlyquestion1isnowvisible',
        trigger:'div.js_question-wrapper:contains("Q1")',
        run:()=>{
            constselector='div.js_question-wrapper.d-none';
            if(document.querySelectorAll(selector).length!==2){
                thrownewError('Q2andQ3shouldhavebeenhidden.');
            }
        }
    },{
        content:'ClickSubmitandfinishthesurvey',
        trigger:'button[value="finish"]',
    },
    //Finalpage
    {
        content:'Thankyou',
        trigger:'h1:contains("Thankyou!")',
    }

]);

});
