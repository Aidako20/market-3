flectra.define('website_livechat.chat_request_tour',function(require){
'usestrict';

varcommonSteps=require("website_livechat.tour_common");
vartour=require("web_tour.tour");


varstepWithChatRequestStep=[{
    content:"Answerthechatrequest!",
    trigger:"input.o_composer_text_field",
    run:"textHi!Whatacoincidence!Ineedyourhelpindeed."
},{
    content:"Sendthemessage",
    trigger:"input.o_composer_text_field",
    run:function(){
        $('input.o_composer_text_field').trigger($.Event('keydown',{which:$.ui.keyCode.ENTER}));
    }
},{
    content:"Verifyyourmessagehasbeentyped",
    trigger:"div.o_thread_message_content>p:contains('Hi!Whatacoincidence!Ineedyourhelpindeed.')"
},{
    content:"Verifythereisnoduplicates",
    trigger:"body",
    run:function(){
        if($("div.o_thread_message_contentp:contains('Hi!Whatacoincidence!Ineedyourhelpindeed.')").length===1){
            $('body').addClass('no_duplicated_message');
        }
    }
},{
    content:"Isyourmessagecorrectlysent?",
    trigger:'body.no_duplicated_message'
}];


tour.register('website_livechat_chat_request_part_1_no_close_tour',{
    test:true,
    url:'/',
},[].concat(stepWithChatRequestStep));

tour.register('website_livechat_chat_request_part_2_end_session_tour',{
    test:true,
    url:'/',
},[].concat(commonSteps.endDiscussionStep,commonSteps.okRatingStep,commonSteps.feedbackStep,commonSteps.transcriptStep,commonSteps.closeStep));

return{};
});
