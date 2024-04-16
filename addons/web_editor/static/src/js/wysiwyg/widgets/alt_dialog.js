flectra.define('wysiwyg.widgets.AltDialog',function(require){
'usestrict';

varcore=require('web.core');
varDialog=require('wysiwyg.widgets.Dialog');

var_t=core._t;

/**
 *Letuserschangethealt&titleofamedia.
 */
varAltDialog=Dialog.extend({
    template:'wysiwyg.widgets.alt',
    xmlDependencies:Dialog.prototype.xmlDependencies.concat(
        ['/web_editor/static/src/xml/wysiwyg.xml']
    ),

    /**
     *@constructor
     */
    init:function(parent,options,media){
        options=options||{};
        this._super(parent,_.extend({},{
            title:_t("Changemediadescriptionandtooltip")
        },options));

        this.trigger_up('getRecordInfo',{
            recordInfo:options,
            callback:function(recordInfo){
                _.defaults(options,recordInfo);
            },
        });

        this.media=media;
        varallEscQuots=/&quot;/g;
        this.alt=($(this.media).attr('alt')||"").replace(allEscQuots,'"');
        vartitle=$(this.media).attr('title')||$(this.media).data('original-title')||"";
        this.tag_title=(title).replace(allEscQuots,'"');
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *@override
     */
    save:function(){
        varalt=this.$('#alt').val();
        vartitle=this.$('#title').val();
        varallNonEscQuots=/"/g;
        $(this.media).attr('alt',alt?alt.replace(allNonEscQuots,"&quot;"):null)
            .attr('title',title?title.replace(allNonEscQuots,"&quot;"):null);
        $(this.media).trigger('content_changed');
        this.final_data=this.media;
        returnthis._super.apply(this,arguments);
    },
});


returnAltDialog;
});
