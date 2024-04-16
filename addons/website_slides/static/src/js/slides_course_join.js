flectra.define('website_slides.course.join.widget',function(require){
'usestrict';

varcore=require('web.core');
varpublicWidget=require('web.public.widget');

var_t=core._t;

varCourseJoinWidget=publicWidget.Widget.extend({
    template:'slide.course.join',
    xmlDependencies:['/website_slides/static/src/xml/slide_course_join.xml'],
    events:{
        'click.o_wslides_js_course_join_link':'_onClickJoin',
    },

    /**
     *
     *Overriddentoaddoptionsparameters.
     *
     *@param{Object}parent
     *@param{Object}options
     *@param{Object}options.channelslide.channelinformation
     *@param{boolean}options.isMemberwhethercurrentuserismemberornot
     *@param{boolean}options.publicUserwhethercurrentuserispublicornot
     *@param{string}[options.joinMessage]themessagetouseforthesimplejoincase
     *  whenthecourseiffreeandtheuserisloggedin,defaultsto"JoinCourse".
     *@param{Promise}[options.beforeJoin]apromisetoexecutebeforeweredirectto
     *  anotherurlwithinthejoinprocess(login/buycourse/...)
     *@param{function}[options.afterJoin]acallbackfunctioncalledaftertheuserhas
     *  joinedthecourse
     */
    init:function(parent,options){
        this._super.apply(this,arguments);
        this.channel=options.channel;
        this.isMember=options.isMember;
        this.publicUser=options.publicUser;
        this.joinMessage=options.joinMessage||_t('JoinCourse');
        this.beforeJoin=options.beforeJoin||function(){returnPromise.resolve();};
        this.afterJoin=options.afterJoin||function(){document.location.reload();};
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@private
     *@param{MouseEvent}ev
     */
    _onClickJoin:function(ev){
        ev.preventDefault();

        if(this.channel.channelEnroll!=='invite'){
            if(this.publicUser){
                this.beforeJoin().then(this._redirectToLogin.bind(this));
            }elseif(!this.isMember&&this.channel.channelEnroll==='public'){
                this.joinChannel(this.channel.channelId);
            }
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Buildsaloginpagethatthenredirectstothisslidepage,orthechannelifthecourse
     *isnotconfiguredaspublicenrolltype.
     *
     *@private
     */
    _redirectToLogin:function(){
        varurl;
        if(this.channel.channelEnroll==='public'){
            url=window.location.pathname;
            if(document.location.href.indexOf("fullscreen")!==-1){
                url+='?fullscreen=1';
            }
        }else{
            url=`/slides/${this.channel.channelId}`;
        }
        document.location=_.str.sprintf('/web/login?redirect=%s',encodeURIComponent(url));
    },

    /**
     *@private
     *@param{Object}$el
     *@param{String}message
     */
    _popoverAlert:function($el,message){
        $el.popover({
            trigger:'focus',
            placement:'bottom',
            container:'body',
            html:true,
            content:function(){
                returnmessage;
            }
        }).popover('show');
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------
    /**
     *@public
     *@param{integer}channelId
     */
    joinChannel:function(channelId){
        varself=this;
        this._rpc({
            route:'/slides/channel/join',
            params:{
                channel_id:channelId,
            },
        }).then(function(data){
            if(!data.error){
                self.afterJoin();
            }else{
                if(data.error==='public_user'){
                    varmessage=_t('Please<ahref="/web/login?redirect=%s">login</a>tojointhiscourse');
                    varsignupAllowed=data.error_signup_allowed||false;
                    if(signupAllowed){
                        message=_t('Please<ahref="/web/signup?redirect=%s">createanaccount</a>tojointhiscourse');
                    }
                    self._popoverAlert(self.$el,_.str.sprintf(message,encodeURIComponent(document.URL)));
                }elseif(data.error==='join_done'){
                    self._popoverAlert(self.$el,_t('Youhavealreadyjoinedthischannel'));
                }else{
                    self._popoverAlert(self.$el,_t('Unknownerror'));
                }
            }
        });
    },
});

publicWidget.registry.websiteSlidesCourseJoin=publicWidget.Widget.extend({
    selector:'.o_wslides_js_course_join_link',

    /**
     *@override
     *@param{Object}parent
     */
    start:function(){
        varself=this;
        varproms=[this._super.apply(this,arguments)];
        vardata=self.$el.data();
        varoptions={channel:{channelEnroll:data.channelEnroll,channelId:data.channelId}};
        $('.o_wslides_js_course_join').each(function(){
            proms.push(newCourseJoinWidget(self,options).attachTo($(this)));
        });
        returnPromise.all(proms);
    },
});

return{
    courseJoinWidget:CourseJoinWidget,
    websiteSlidesCourseJoin:publicWidget.registry.websiteSlidesCourseJoin
};

});
