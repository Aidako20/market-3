flectra.define('portal.rating.composer',function(require){
'usestrict';

varpublicWidget=require('web.public.widget');
varsession=require('web.session');
varportalComposer=require('portal.composer');

varPortalComposer=portalComposer.PortalComposer;

/**
 *RatingPopupComposer
 *
 *Displaytheratingaveragewithastaticstarwidget,andopen
 *apopupwiththeportalcomposerwhenclickingonit.
 **/
varRatingPopupComposer=publicWidget.Widget.extend({
    template:'portal_rating.PopupComposer',
    xmlDependencies:[
        '/portal/static/src/xml/portal_chatter.xml',
        '/portal_rating/static/src/xml/portal_tools.xml',
        '/portal_rating/static/src/xml/portal_rating_composer.xml',
    ],

    init:function(parent,options){
        this._super.apply(this,arguments);
        this.rating_avg=Math.round(options['ratingAvg']*100)/100||0.0;
        this.rating_total=options['ratingTotal']||0.0;

        this.options=_.defaults({},options,{
            'token':false,
            'res_model':false,
            'res_id':false,
            'pid':0,
            'display_composer':options['disable_composer']?false:!session.is_website_user,
            'display_rating':true,
            'csrf_token':flectra.csrf_token,
            'user_id':session.user_id,
        });
    },
    /**
     *@override
     */
    start:function(){
        vardefs=[];
        defs.push(this._super.apply(this,arguments));

        //instanciateandinsertcomposerwidget
        this._composer=newPortalComposer(this,this.options);
        defs.push(this._composer.replace(this.$('.o_portal_chatter_composer')));

        returnPromise.all(defs);
    },
});

publicWidget.registry.RatingPopupComposer=publicWidget.Widget.extend({
    selector:'.o_rating_popup_composer',

    /**
     *@override
     */
    start:function(){
        varratingPopupData=this.$el.data();
        varratingPopup=newRatingPopupComposer(this,ratingPopupData);
        returnPromise.all([
            this._super.apply(this,arguments),
            ratingPopup.appendTo(this.$el)
        ]);
    },
});

returnRatingPopupComposer;

});
