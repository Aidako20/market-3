flectra.define('survey.tour_test_survey_prefill',function(require){
'usestrict';

vartour=require('web_tour.tour');

tour.register('test_survey_prefill',{
    test:true,
    url:'/survey/start/b137640d-14d4-4748-9ef6-344caaaaaae'
},
[{     //Page-1
        trigger:'button.btn.btn-primary.btn-lg:contains("StartSurvey")',
    },{//Question:Wheredoyoulive?
        trigger:'div.js_question-wrapper:contains("Wheredoyoulive?")input',
        run:'textGrand-Rosiere',
    },{//Question:Whenisyourdateofbirth?
        trigger:'div.js_question-wrapper:contains("Whenisyourdateofbirth?")input',
        run:'text05/05/1980',
    },{//Question:Howfrequentlydoyoubuyproductsonline?
        trigger:'div.js_question-wrapper:contains("Howfrequentlydoyoubuyproductsonline?")label:contains("Onceaweek")',
    },{//Question:Howmanytimesdidyouorderproductsonourwebsite?
        trigger:'div.js_question-wrapper:contains("Howmanytimesdidyouorderproductsonourwebsite?")input',
        run:'text42',
    },{
        content:'ClickonNextPage',
        trigger:'button[value="next"]',
    },
    //Page-2
    {//Question:Whichofthefollowingwordswouldyouusetodescribeourproducts?
        content:'AnswerWhichofthefollowingwordswouldyouusetodescribeourproducts(HighQuality)',
        trigger:'div.js_question-wrapper:contains("Whichofthefollowingwordswouldyouusetodescribeourproducts")label:contains("Highquality")',
    },{
        content:'AnswerWhichofthefollowingwordswouldyouusetodescribeourproducts(Goodvalueformoney)',
        trigger:'div.js_question-wrapper:contains("Whichofthefollowingwordswouldyouusetodescribeourproducts")label:contains("Goodvalueformoney")',
    },{
        content:'AnswerWhatdoyourthinkaboutourneweCommerce(Thenewlayoutanddesignisfreshandup-to-date)',
        trigger:'div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Thenewlayoutanddesignisfreshandup-to-date")td:first',
    },{
        content:'AnswerWhatdoyourthinkaboutourneweCommerce(ItiseasytofindtheproductthatIwant)',
        trigger:'div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("ItiseasytofindtheproductthatIwant")td:eq(2)',
    },{
        content:'AnswerWhatdoyourthinkaboutourneweCommerce(Thetooltocomparetheproductsisusefultomakeachoice)',
        trigger:'div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Thetooltocomparetheproductsisusefultomakeachoice")td:eq(3)',
    },{
        content:'AnswerWhatdoyourthinkaboutourneweCommerce(Thecheckoutprocessisclearandsecure)',
        trigger:'div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Thecheckoutprocessisclearandsecure")td:eq(2)',
    },{
        content:'AnswerWhatdoyourthinkaboutourneweCommerce(Ihaveaddedproductstomywishlist)',
        trigger:'div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Ihaveaddedproductstomywishlist")td:last',
    },{
        content:'AnswerDoyouhaveanyothercomments,questions,orconcerns',
        trigger:'div.js_question-wrapper:contains("Doyouhaveanyothercomments,questions,orconcerns")textarea',
        run:'textIstheprefillworking?',
    },{
        //Gobacktopreviouspage
        content:'Clickonthepreviouspagenameinthebreadcrumb',
        trigger:'ol.breadcrumba:first',
    },{
        trigger:'div.js_question-wrapper:contains("Howmanytimesdidyouorderproductsonourwebsite?")input',
        run:function(){
            var$inputQ3=$('div.js_question-wrapper:contains("Howmanytimesdidyouorderproductsonourwebsite?")input');
            if($inputQ3.val()==='42.0'){
                $('.o_survey_title').addClass('prefilled');
            }
        }
    },{
        trigger:'.o_survey_title.prefilled',
        run:function(){
            //checkthatalltheanswersareprefilledinPage1
            var$inputQ1=$('div.js_question-wrapper:contains("Wheredoyoulive?")input');
            if($inputQ1.val()!=='Grand-Rosiere'){
                return;
            }

            var$inputQ2=$('div.js_question-wrapper:contains("Whenisyourdateofbirth?")input');
            if($inputQ2.val()!=='05/05/1980'){
                return;
            }

            var$inputQ3=$('div.js_question-wrapper:contains("Howfrequentlydoyoubuyproductsonline?")label:contains("Onceaweek")input');
            if(!$inputQ3.is(':checked')){
                return;
            }

            var$inputQ4=$('div.js_question-wrapper:contains("Howmanytimesdidyouorderproductsonourwebsite?")input');
            if($inputQ4.val()!=='42.0'){
                return;
            }

            $('.o_survey_title').addClass('tour_success');
        }
    },{
        trigger:'.o_survey_title.tour_success'
    },{
        content:'ClickonNextPage',
        trigger:'button[value="next"]',
    },{
        trigger:'div.js_question-wrapper:contains("Doyouhaveanyothercomments,questions,orconcerns")textarea',
        run:function(){
            var$inputQ3=$('div.js_question-wrapper:contains("Doyouhaveanyothercomments,questions,orconcerns")textarea');
            if($inputQ3.val()==="Istheprefillworking?"){
                $('.o_survey_title').addClass('prefilled2');
            }
        }
    },{
        trigger:'.o_survey_title.prefilled2',
        run:function(){
            //checkthatalltheanswersareprefilledinPage2
            var$input1Q1=$('div.js_question-wrapper:contains("Whichofthefollowingwordswouldyouusetodescribeourproducts")label:contains("Highquality")input');
            if(!$input1Q1.is(':checked')){
                return;
            }

            var$input2Q1=$('div.js_question-wrapper:contains("Whichofthefollowingwordswouldyouusetodescribeourproducts")label:contains("Goodvalueformoney")input');
            if(!$input2Q1.is(':checked')){
                return;
            }

            var$input1Q2=$('div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Thenewlayoutanddesignisfreshandup-to-date")input:first');
            if(!$input1Q2.is(':checked')){
                return;
            }

            var$input2Q2=$('div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("ItiseasytofindtheproductthatIwant")input:eq(2)');
            if(!$input2Q2.is(':checked')){
                return;
            }

            var$input3Q2=$('div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Thetooltocomparetheproductsisusefultomakeachoice")input:eq(3)');
            if(!$input3Q2.is(':checked')){
                return;
            }

            var$input4Q2=$('div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Thecheckoutprocessisclearandsecure")input:eq(2)');
            if(!$input4Q2.is(':checked')){
                return;
            }

            var$input5Q2=$('div.js_question-wrapper:contains("WhatdoyourthinkaboutourneweCommerce")tr:contains("Ihaveaddedproductstomywishlist")input:last');
            if(!$input5Q2.is(':checked')){
                return;
            }

            var$inputQ3=$('div.js_question-wrapper:contains("Doyouhaveanyothercomments,questions,orconcerns")textarea');
            if($inputQ3.val()!=="Istheprefillworking?"){
                return;
            }

            $('.o_survey_title').addClass('tour_success_2');
        }
    },{
        trigger:'.o_survey_title.tour_success_2'
    }
]);

});
