flectra.define('website_slides.course.slides.list',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varcore=require('web.core');
var_t=core._t;

publicWidget.registry.websiteSlidesCourseSlidesList=publicWidget.Widget.extend({
    selector:'.o_wslides_slides_list',
    xmlDependencies:['/website_slides/static/src/xml/website_slides_upload.xml'],

    start:function(){
        this._super.apply(this,arguments);

        this.channelId=this.$el.data('channelId');

        this._updateHref();
        this._bindSortable();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------,

    /**
     *BindthesortablejQuerywidgettoboth
     *-coursesections
     *-courseslides
     *
     *@private
     */
    _bindSortable:function(){
        this.$('ul.o_wslides_js_slides_list_container').sortable({
            handle:'.o_wslides_slides_list_drag',
            stop:this._reorderSlides.bind(this),
            items:'.o_wslides_slide_list_category',
            placeholder:'o_wslides_slides_list_slide_hilightposition-relativemb-1'
        });

        this.$('.o_wslides_js_slides_list_containerul').sortable({
            handle:'.o_wslides_slides_list_drag',
            connectWith:'.o_wslides_js_slides_list_containerul',
            stop:this._reorderSlides.bind(this),
            items:'.o_wslides_slides_list_slide:not(.o_wslides_js_slides_list_empty)',
            placeholder:'o_wslides_slides_list_slide_hilightposition-relativemb-1'
        });
    },

    /**
     *Thismethodwillcheckthatasectionisempty/notempty
     *whentheslidesarereorderedandshow/hidethe
     *"Emptycategory"placeholder.
     *
     *@private
     */
    _checkForEmptySections:function(){
        this.$('.o_wslides_slide_list_category').each(function(){
            var$categoryHeader=$(this).find('.o_wslides_slide_list_category_header');
            varcategorySlideCount=$(this).find('.o_wslides_slides_list_slide:not(.o_not_editable)').length;
            var$emptyFlagContainer=$categoryHeader.find('.o_wslides_slides_list_drag').first();
            var$emptyFlag=$emptyFlagContainer.find('small');
            if(categorySlideCount===0&&$emptyFlag.length===0){
                $emptyFlagContainer.append($('<small>',{
                    'class':"ml-1text-mutedfont-weight-bold",
                    text:_t("(empty)")
                }));
            }elseif(categorySlideCount>0&&$emptyFlag.length>0){
                $emptyFlag.remove();
            }
        });
    },

    _getSlides:function(){
        varcategories=[];
        this.$('.o_wslides_js_list_item').each(function(){
            categories.push(parseInt($(this).data('slideId')));
        });
        returncategories;
    },
    _reorderSlides:function(){
        varself=this;
        self._rpc({
            route:'/web/dataset/resequence',
            params:{
                model:"slide.slide",
                ids:self._getSlides()
            }
        }).then(function(res){
            self._checkForEmptySections();
        });
    },

    /**
     *ChangelinkshreftofullscreenmodeforSEO.
     *
     *Specificationsdemandthatlinksaregenerated(xml)withoutthe"fullscreen"
     *parameterforSEOpurposes.
     *
     *Thismethodthenaddstheparameterassoonasthepageisloaded.
     *
     *@private
     */
    _updateHref:function(){
        this.$(".o_wslides_js_slides_list_slide_link").each(function(){
            varhref=$(this).attr('href');
            varoperator=href.indexOf('?')!==-1?'&':'?';
            $(this).attr('href',href+operator+"fullscreen=1");
        });
    }
});

returnpublicWidget.registry.websiteSlidesCourseSlidesList;

});
