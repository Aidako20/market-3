flectra.define('web.RainbowMan',function(require){
"usestrict";

/**
 *TheRainbowManwidgetisthewidgetdisplayedbydefaultasa'fun/rewarding'
 *effectinsomecases. Forexample,whentheusermarkedalargedealaswon,
 *orwhenhecleareditsinbox.
 *
 *Thiswidgetismostlyapictureandamessagewitharainbowanimationaround
 *IfyouwanttodisplayaRainbowMan,youprobablydonotwanttodoitby
 *importingthisfile. Theusualwaytodothatwouldbetousetheeffect
 *service(bytriggeringthe'show_effect'event)
 */

varWidget=require('web.Widget');
varcore=require('web.core');

var_t=core._t;

varRainbowMan=Widget.extend({
    template:'rainbow_man.notification',
    xmlDependencies:['/web/static/src/xml/rainbow_man.xml'],
    /**
     *@override
     *@constructor
     *@param{Object}[options]
     *@param{string}[options.message]Messagetobedisplayedonrainbowmancard
     *@param{string}[options.fadeout='medium']Delayforrainbowmantodisappear.'fast'willmakerainbowmandissapearquickly,'medium'and'slow'willwaitlittlelongerbeforedisappearing(canbeusedwhenoptions.messageislonger),'no'willkeeprainbowmanonscreenuntiluserclicksanywhereoutsiderainbowman
     *@param{string}[options.img_url]URLoftheimagetobedisplayed
     */
    init:function(options){
        this._super.apply(this,arguments);
        varrainbowDelay={slow:4500,medium:3500,fast:2000,no:false};
        this.options=_.defaults(options||{},{
            fadeout:'medium',
            img_url:'/web/static/src/img/smile.svg',
            message:_t('WellDone!'),
        });
        this.delay=rainbowDelay[this.options.fadeout];
    },
    /**
     *@override
     */
    start:function(){
        varself=this;
        //destroyrainbowmanwhentheuserclicksoutside
        //thisisdoneinasetTimeouttopreventtheclickthattriggeredthe
        //rainbowmantocloseitdirectly
        setTimeout(function(){
            core.bus.on('click',self,function(ev){
                if(ev.originalEvent&&ev.target.className.indexOf('o_reward')===-1){
                    this.destroy();
                }
            });
        });
        if(this.delay){
            setTimeout(function(){
                self.$el.addClass('o_reward_fading');
                setTimeout(function(){
                    self.destroy();
                },600);//destroyonlyafterfadeoutanimationiscompleted
            },this.delay);
        }
        this.$('.o_reward_msg_content').append(this.options.message);
        returnthis._super.apply(this,arguments);
    }
});

returnRainbowMan;

});
