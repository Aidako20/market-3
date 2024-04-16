flectra.define('web.IFrameWidget',function(require){
"usestrict";

varWidget=require('web.Widget');

/**
 *Genericwidgettocreateaniframethatlistensforclicks
 *
 *Itshouldbeextendedbyoverwritingthemethods::
 *
 *     init:function(parent){
 *         this._super(parent,<url_of_iframe>);
 *     },
 *     _onIFrameClicked:function(e){
 *         filtertheclicksyouwanttouseandapply
 *         anactiononit
 *     }
 */
varIFrameWidget=Widget.extend({
    tagName:'iframe',
    /**
     *@constructor
     *@param{Widget}parent
     *@param{string}url
     */
    init:function(parent,url){
        this._super(parent);
        this.url=url;
    },
    /**
     *@override
     *@returns{Promise}
     */
    start:function(){
        this.$el.css({height:'100%',width:'100%',border:0});
        this.$el.attr({src:this.url});
        this.$el.on("load",this._bindEvents.bind(this));
        returnthis._super();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Calledwhentheiframeisready
     */
    _bindEvents:function(){
        this.$el.contents().click(this._onIFrameClicked.bind(this));
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@param{MouseEvent}event
     */
    _onIFrameClicked:function(event){
    }
});

returnIFrameWidget;

});
