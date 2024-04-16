flectra.define('website_sale_slides.course.join.widget',function(require){
"usestrict";

varCourseJoinWidget=require('website_slides.course.join.widget').courseJoinWidget;
constwUtils=require('website.utils');

CourseJoinWidget.include({
    xmlDependencies:(CourseJoinWidget.prototype.xmlDependencies||[]).concat(
        ["/website_sale_slides/static/src/xml/slide_course_join.xml"]
    ),
    init:function(parent,options){
        this._super.apply(this,arguments);
        this.productId=options.channel.productId||false;
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *Whentheuserjoinsthecourse,ifit'ssetas"onpayment"andtheuserisloggedin,
     *weredirecttotheshoppageforthiscourse.
     *
     *@param{MouseEvent}ev
     *@override
     *@private
     */
    _onClickJoin:function(ev){
        ev.preventDefault();

        if(this.channel.channelEnroll==='payment'&&!this.publicUser){
            constself=this;
            this.beforeJoin().then(function(){
                wUtils.sendRequest('/shop/cart/update',{
                    product_id:self.productId,
                    express:1,
                });
            });
        }else{
            this._super.apply(this,arguments);
        }
    },
});

returnCourseJoinWidget;

});
