flectra.define('website_event_track_quiz.event_leaderboard',function(require){

'usestrict';

varpublicWidget=require('web.public.widget');

publicWidget.registry.EventLeaderboard=publicWidget.Widget.extend({
    selector:'.o_wevent_quiz_leaderboard',

    /**
     *Basicoverridetoscrolltocurrentvisitor'sposition.
     */
    start:function(){
        varself=this;
        returnthis._super(...arguments).then(function(){
            var$scrollTo=self.$('.o_wevent_quiz_scroll_to');
            if($scrollTo.length!==0){
                varoffset=$('.o_header_standard').height();
                var$appMenu=$('.o_main_navbar');
                if($appMenu.length!==0){
                    offset+=$appMenu.height();
                }
                window.scrollTo({
                    top:$scrollTo.offset().top-offset,
                    behavior:'smooth'
                });
            }
        });
    }
});

returnpublicWidget.registry.EventLeaderboard;

});
