flectra.define('website_event_track_exhibitor.event_exhibitor_connect',function(require){
'usestrict';

varDialog=require('web.Dialog');
varpublicWidget=require('web.public.widget');

varExhibitorConnectClosedDialog=Dialog.extend({
    events:_.extend({},Dialog.prototype.events,{
        'click.o_wesponsor_js_connect_modal_contry':'_onClickCountryFlag',
    }),
    template:'exhibitor.connect.closed.modal',

    /**
     *@override
     *@param{Object}parent;
     *@param{Object}optionsholdingasponsorDataobjwithrequiredvaluesto
     *  display(see.xmlfordetails);
     */
    init:function(parent,options){
        options=_.defaults(options||{},{
            size:'medium',
            renderHeader:false,
            renderFooter:false,
            backdrop:true,
        });
        this.sponsorId=options.sponsorId;
        this._super(parent,options);
    },

    /**
     *@override
     *Waitforfetchingsponsordata;
     */
    willStart:function(){
        returnPromise.all([
            this._super(...arguments),
            this._fetchSponsor()
        ]);
    },

    //---------------------------------------------------------------------
    //Private
    //---------------------------------------------------------------------

    /**
     *@private
     *@returns{Promise<*>}promiseafterfetchingsponsordata,givenits
     *  sponsorId.Necessarytorendertemplatecontent;
     */
    _fetchSponsor:function(){
        letself=this;
        letrpcPromise=this._rpc({
            route:`/event_sponsor/${this.sponsorId}/read`,
        }).then(function(readData){
            self.sponsorData=readData;
            returnPromise.resolve();
        });
        returnrpcPromise;
    },
});


publicWidget.registry.eventExhibitorConnect=publicWidget.Widget.extend({
    selector:'.o_wesponsor_js_connect',
    xmlDependencies:['/website_event_track_exhibitor/static/src/xml/event_exhibitor_connect.xml'],

    /**
     *@override
     *@public
     */
    init:function(){
        this._super(...arguments);
        this._onConnectClick=_.debounce(this._onConnectClick,500,true);
    },

    /**
     *@override
     *@public
     */
    start:function(){
        varself=this;
        returnthis._super(...arguments).then(function(){
            self.eventIsOngoing=self.$el.data('eventIsOngoing')||false;
            self.sponsorIsOngoing=self.$el.data('sponsorIsOngoing')||false;
            self.isParticipating=self.$el.data('isParticipating')||false;
            self.userEventManager=self.$el.data('userEventManager')||false;
            self.$el.on('click',self._onConnectClick.bind(self));
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //-------------------------------------------------------------------------

    /**
     *@private
     *@param{Event}ev
     *Onclick,ifsponsorisnotwithinopeninghours,displayamodalinstead
     *ofredirectingonthesponsorview;
     */
    _onConnectClick:function(ev){
        ev.stopPropagation();
        ev.preventDefault();

        if(this.userEventManager){
            document.location=this.$el.data('sponsorUrl');
        }elseif(!this.eventIsOngoing&&!this.isParticipating){
            document.location=this.$el.data('registerUrl');
        }elseif(!this.eventIsOngoing||!this.sponsorIsOngoing){
            returnthis._openClosedDialog();
        }else{
            document.location=this.$el.data('sponsorUrl');
        }
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    _openClosedDialog:function($element){
        constsponsorId=this.$el.data('sponsorId');
        returnnewExhibitorConnectClosedDialog(
            this,{
                sponsorId:sponsorId,
            }
        ).open();
    },

});


return{
    ExhibitorConnectClosedDialog:ExhibitorConnectClosedDialog,
    eventExhibitorConnect:publicWidget.registry.eventExhibitorConnect,
};

});
