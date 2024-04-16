flectra.define('website_slides_survey.fullscreen',function(require){
"usestrict";

varcore=require('web.core');
varQWeb=core.qweb;
varFullscreen=require('website_slides.fullscreen');

Fullscreen.include({
    xmlDependencies:(Fullscreen.prototype.xmlDependencies||[]).concat(
        ["/website_slides_survey/static/src/xml/website_slides_fullscreen.xml"]
    ),

    /**
     *Extendthe_renderSlidemethodsothatslidesoftype"certification"
     *arealsotakenintoaccountandrenderedcorrectly
     *
     *@private
     *@override
     */
    _renderSlide:function(){
        vardef=this._super.apply(this,arguments);
        var$content=this.$('.o_wslides_fs_content');
        if(this.get('slide').type==="certification"){
            $content.html(QWeb.render('website.slides.fullscreen.certification',{widget:this}));
        }
        returnPromise.all([def]);
    },
});
});


