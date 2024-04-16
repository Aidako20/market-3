flectra.define('website_slides.slides_tour',function(require){
"usestrict";

varcore=require('web.core');
var_t=core._t;

vartour=require('web_tour.tour');

tour.register('slides_tour',{
    url:'/slides',
},[{
    trigger:"body:has(#o_new_content_menu_choices.o_hidden)#new-content-menu>a",
    content:_t("Welcomeonyourcourse'shomepage.It'sstillemptyfornow.Clickon\"<b>New</b>\"towriteyourfirstcourse."),
    consumeVisibleOnly:true,
    position:'bottom',
},{
    trigger:'a[data-action="new_slide_channel"]',
    content:_t("Select<b>Course</b>tocreateitandmanageit."),
    position:'bottom',
    width:210,
},{
    trigger:'input[name="name"]',
    content:_t("Giveyourcourseanengaging<b>Title</b>."),
    position:'bottom',
    width:280,
    run:'textMyNewCourse',
},{
    trigger:'textarea[name="description"]',
    content:_t("Giveyourcourseahelpful<b>Description</b>."),
    position:'bottom',
    width:300,
    run:'textThiscourseisforadvancedusers.',
},{
    trigger:'button.btn-primary',
    content:_t("Clickonthe<b>Create</b>buttontocreateyourfirstcourse."),
},{
    trigger:'.o_wslides_js_slide_section_add',
    content:_t("Congratulations,yourcoursehasbeencreated,butthereisn'tanycontentyet.First,let'sadda<b>Section</b>togiveyourcourseastructure."),
    position:'bottom',
},{
    trigger:'button.btn-primary',
    content:_t("Agoodcoursehasastructure.Pickanameforyourfirstsectionandclick<b>Save</b>tocreateit."),
    position:'bottom',
    width:260,
},{
    trigger:'a.btn-primary.o_wslides_js_slide_upload',
    content:_t("Yourfirstsectioniscreated,nowit'stimetoaddlessonstoyourcourse.Clickon<b>AddContent</b>touploadadocument,createawebpageorlinkavideo."),
    position:'bottom',
},{
    trigger:'a[data-slide-type="presentation"]',
    content:_t("First,let'sadda<b>Presentation</b>.Itcanbea.pdforanimage."),
    position:'bottom',
},{
    trigger:'input#upload',
    content:_t("Choosea<b>File</b>onyourcomputer."),
},{
    trigger:'input#name',
    content:_t("The<b>Title</b>ofyourlessonisautocompletedbutyoucanchangeitifyouwant.</br>A<b>Preview</b>ofyourfileisavailableontherightsideofthescreen."),
},{
    trigger:'input#duration',
    content:_t("The<b>Duration</b>ofthelessonisbasedonthenumberofpagesofyourdocument.Youcanchangethisnumberifyourattendeeswillneedmoretimetoassimilatethecontent."),
},{
    trigger:'button.o_w_slide_upload_published',
    content:_t("<b>Save&Publish</b>yourlessontomakeitavailabletoyourattendees."),
    position:'bottom',
    width:285,
},{
    trigger:'span.badge-info:contains("New")',
    content:_t("Congratulations!Yourfirstlessonisavailable.Let'sseetheoptionsavailablehere.Thetag\"<b>New</b>\"indicatesthatthislessonwascreatedlessthan7daysago."),
    position:'bottom',
},{
    trigger:'a[name="o_wslides_list_slide_add_quizz"]',
    extra_trigger:'.o_wslides_slides_list_slide:hover',
    content:_t("Ifyouwanttobesurethatattendeeshaveunderstoodandmemorizedthecontent,youcanaddaQuizonthelesson.Clickon<b>AddQuiz</b>."),
},{
    trigger:'input[name="question-name"]',
    content:_t("Enteryour<b>Question</b>.Beclearandconcise."),
    position:'left',
    width:330,
},{
    trigger:'input.o_wslides_js_quiz_answer_value',
    content:_t("Enteratleasttwopossible<b>Answers</b>."),
    position:'left',
    width:290,
},{
    trigger:'a.o_wslides_js_quiz_is_correct',
    content:_t("Markthecorrectanswerbycheckingthe<b>correct</b>mark."),
    position:'right',
    width:230,
},{
    trigger:'i.o_wslides_js_quiz_comment_answer:last',
    content:_t("Youcanadd<b>comments</b>onanswers.Thiswillbevisiblewiththeresultsiftheuserselectthisanswer."),
    position:'right',

},{
    trigger:'a.o_wslides_js_quiz_validate_question',
    content:_t("<b>Save</b>yourquestion."),
    position:'left',
    width:170,
},{
    trigger:'li.breadcrumb-item:nth-child(2)',
    content:_t("Clickonyour<b>Course</b>togobacktothetableofcontent."),
    position:'top',
},{
    trigger:'label.js_publish_btn',
    content:_t("Onceyou'redone,don'tforgetto<b>Publish</b>yourcourse."),
    position:'bottom',
},{
    trigger:'a.o_wslides_js_slides_list_slide_link',
    content:_t("Congratulations,you'vecreatedyourfirstcourse.<br/>Clickonthetitleofthiscontenttoseeitinfullscreenmode."),
    position:'bottom',
}]);

});
