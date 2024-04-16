flectra.define('website_slides.tour.slide.course.member.youtube',function(require){
'usestrict';

vartour=require('web_tour.tour');
varFullScreen=require('website_slides.fullscreen');

/**
 *Alterthismethodfortestpurposes.
 *Thiswillmakethevideostartat10minutes.
 *Asitlasts10min24s,itwillmarkitascompletedimmediately.
 */
FullScreen.include({
    _renderSlide:function(){

        varslide=this.get('slide');
        slide.embedUrl+='&start=260';
        this.set('slide',slide);

        returnthis._super.call(this,arguments);
    }
});

/**
 *Globalusecase:
 *anuser(eitheremployee,websitepublisherorportal)joinsapublic
    course;
 *hehasaccesstothefullcoursecontentwhenhe'samemberofthe
    course;
 *heusesfullscreenplayertocompletethecourse;
 *heratesthecourse;
 */
tour.register('course_member_youtube',{
    url:'/slides',
    test:true
},[
//eLearning:goon/all,findfreecourseandjoinit
{
    trigger:'a.o_wslides_home_all_slides'
},{
    trigger:'a:contains("Chooseyourwood")'
},{
    trigger:'a:contains("JoinCourse")'
},{
    trigger:'.o_wslides_js_course_join:contains("You\'reenrolled")',
    run:function(){}//checkmembership
},{
    trigger:'a:contains("ComparingHardnessofWoodSpecies")',
}, {
    trigger:'.o_wslides_progress_percentage:contains("50")',
    run:function(){}//checkprogression
},{
    trigger:'a:contains("WoodBendingWithSteamBox")',
},{
    trigger:'.player',
    run:function(){}//checkplayerloading
},{
    trigger:'.o_wslides_fs_sidebar_section_slidesli:contains("WoodBendingWithSteamBox").o_wslides_slide_completed',
    run:function(){}//checkthatvideoslideismarkedas'done'
},{
    trigger:'.o_wslides_progress_percentage:contains("100")',
    run:function(){}//checkprogression
},{
    trigger:'a:contains("Backtocourse")'
}
]);

});
