flectra.define('website_rating_project.rating',function(require){
'usestrict';

vartime=require('web.time');
varpublicWidget=require('web.public.widget');

publicWidget.registry.ProjectRatingImage=publicWidget.Widget.extend({
    selector:'.o_portal_project_rating.o_rating_image',

    /**
     *@override
     */
    start:function(){
        this.$el.popover({
            placement:'bottom',
            trigger:'hover',
            html:true,
            content:function(){
                var$elem=$(this);
                varid=$elem.data('id');
                varratingDate=$elem.data('rating-date');
                varbaseDate=time.auto_str_to_date(ratingDate);
                varduration=moment(baseDate).fromNow();
                var$rating=$('#rating_'+id);
                $rating.find('.rating_timeduration').text(duration);
                return$rating.html();
            },
        });
        returnthis._super.apply(this,arguments);
    },
});
});
