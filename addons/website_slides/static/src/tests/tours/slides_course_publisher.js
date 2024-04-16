flectra.define('website_slides.tour.slide.course.publisher',function(require){
'usestrict';

vartour=require('web_tour.tour');
varslidesTourTools=require('website_slides.tour.tools');

/**
 *Globalusecase:
 *auser(websitepublisher)createsacourse;
 *heupdatesit;
 *hecreatessomelessonsinit;
 *hepublishesit;
 */
tour.register('course_publisher',{
    url:'/slides',
    test:true
},[{
    content:'eLearning:clickonNew(top-menu)',
    trigger:'li.o_new_content_menua'
},{
    content:'eLearning:clickonNewCourse',
    trigger:'a:contains("Course")'
},{
    content:'eLearning:setname',
    trigger:'input[name="name"]',
    run:'textHowtoDéboulonnate',
},{
    content:'eLearning:clickontags',
    trigger:'ul.select2-choices:first',
},{
    content:'eLearning:selectgardenertag',
    trigger:'div.select2-result-label:contains("Gardener")',
    in_modal:false,
},{
    content:'eLearning:setdescription',
    trigger:'input[name="description"]',
    run:'textDéboulonnateisverycommonatFleurus',
},{
    content:'eLearning:wewantreviews',
    trigger:'input[name="allow_comment"]',
},{
    content:'eLearning:seemscool,createit',
    trigger:'button:contains("Create")',
},{
    content:'eLearning:launchcourseedition',
    trigger:'li[id="edit-page-menu"]a',
},{
    content:'eLearning:doubleclickimagetoeditit',
    trigger:'img.o_wslides_course_pict',
    run:'dblclick',
},{
    content:'eLearning:clickpâtissière',
    trigger:'img[title="s_company_team_image_4.png"]',
},{
    content:'eLearning:isthepâtissièreset?',
    trigger:'img.o_wslides_course_pict',
    run:function(){
        if($('img.o_wslides_course_pict').attr('src').endsWith('s_team_member_4.png')){
            $('img.o_wslides_course_pict').addClass('o_wslides_tour_success');
        }
    },
},{
    content:'eLearning:thepâtissièreisset!',
    trigger:'img.o_wslides_course_pict.o_wslides_tour_success',
},{
    content:'eLearning:savecourseedition',
    trigger:'button[data-action="save"]',
},{
    content:'eLearning:coursecreatewithcurrentmember',
    extra_trigger:'body:not(.editor_enable)', //waitforeditortoclose
    trigger:'.o_wslides_js_course_join:contains("You\'reenrolled")',
    run:function(){}//checkmembership
}
].concat(
    slidesTourTools.addExistingCourseTag(),
    slidesTourTools.addNewCourseTag('TheMostAwesomeCourse'),
    slidesTourTools.addSection('Introduction'),
    slidesTourTools.addVideoToSection('Introduction'),
    [{
    content:'eLearning:publishnewlyaddedcourse',
    trigger:'span:contains("DschinghisKhan-Moskau1979")', //waitforslidetoappear
    //trigger:'span.o_wslides_js_slide_toggle_is_preview:first',
    run:function(){
        $('span.o_wslides_js_slide_toggle_is_preview:first').click();
    }
}]
//    [
//{
//    content:'eLearning:movenewcourseinsideintroduction',
//    trigger:'div.o_wslides_slides_list_drag',
//    //run:'drag_and_dropdiv.o_wslides_slides_list_dragul.ui-sortable:first',
//    run:'drag_and_dropdiv.o_wslides_slides_list_draga.o_wslides_js_slide_section_add',
//}]
));

});
