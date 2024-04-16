flectra.define('web.special_fields',function(require){
"usestrict";

varcore=require('web.core');
varfield_utils=require('web.field_utils');
varrelational_fields=require('web.relational_fields');
varAbstractField=require('web.AbstractField');

varFieldSelection=relational_fields.FieldSelection;
var_t=core._t;
var_lt=core._lt;


/**
 *Thiswidgetisintendedtodisplayawarningnearalabelofa'timezone'field
 *indicatingifthebrowsertimezoneisidentical(ornot)totheselectedtimezone.
 *Thiswidgetdependsonafieldgivenwiththeparam'tz_offset_field',whichcontains
 *thetimedifferencebetweenUTCtimeandlocaltime,inminutes.
 */
varFieldTimezoneMismatch=FieldSelection.extend({
    /**
     *@override
     */
    start:function(){
        varinterval=navigator.platform.toUpperCase().indexOf('MAC')>=0?60000:1000;
        this._datetime=setInterval(this._renderDateTimeTimezone.bind(this),interval);
        returnthis._super.apply(this,arguments);
    },
    /**
     *@override
     */
    destroy:function(){
        clearInterval(this._datetime);
        returnthis._super();
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _render:function(){
        this._super.apply(this,arguments);
        this._renderTimezoneMismatch();
    },
    /**
     *Displaythetimeintheusertimezone(reloadeachsecond)
     *
     *@private
     */
    _renderDateTimeTimezone:function(){
        if(!this.mismatch||!this.$option.html()){
            return;
        }
        varoffset=this.recordData.tz_offset.match(/([+-])([0-9]{2})([0-9]{2})/);
        offset=(offset[1]==='-'?-1:1)*(parseInt(offset[2])*60+parseInt(offset[3]));
        vardatetime=field_utils.format.datetime(moment.utc().add(offset,'minutes'),this.field,{timezone:false});
        varcontent=this.$option.html().split('')[0];
        content+='   ('+datetime+')';
        this.$option.html(content);
    },
    /**
     *Displaythetimezonealert
     *
     *Note:timezonealertisaspanthatisaddedafter$el,and$elisnowa
     *setoftwoelements
     *
     *@private
     */
    _renderTimezoneMismatch:function(){
        //weneedtocleanthewarningtohavemaximumonealert
        this.$el.last().filter('.o_tz_warning').remove();
        this.$el=this.$el.first();
        varvalue=this.$el.val();
        var$span=$('<spanclass="fafa-exclamation-triangleo_tz_warning"/>');

        if(this.$option&&this.$option.html()){
            this.$option.html(this.$option.html().split('')[0]);
        }

        varuserOffset=this.recordData.tz_offset;
        this.mismatch=false;
        if(userOffset&&value!==""&&value!=="false"){
            varoffset=-(newDate().getTimezoneOffset());
            varbrowserOffset=(offset<0)?"-":"+";
            browserOffset+=_.str.sprintf("%02d",Math.abs(offset/60));
            browserOffset+=_.str.sprintf("%02d",Math.abs(offset%60));
            this.mismatch=(browserOffset!==userOffset);
        }

        if(this.mismatch){
            $span.insertAfter(this.$el);
            $span.attr('title',_t("TimezoneMismatch:Thistimezoneisdifferentfromthatofyourbrowser.\nPlease,setthesametimezoneasyourbrowser'stoavoidtimediscrepanciesinyoursystem."));
            this.$el=this.$el.add($span);

            this.$option=this.$('option').filter(function(){
                return$(this).attr('value')===value;
            });
            this._renderDateTimeTimezone();
        }elseif(value=="false"){
            $span.insertAfter(this.$el);
            $span.attr('title',_t("Setatimezoneonyouruser"));
            this.$el=this.$el.add($span);
        }
    },
    /**
     *@override
     *@private
     *this.$elcanhaveotherelementsthanselect
     *thatshouldnotbetouched
     */
    _renderEdit:function(){
        //FIXME:hacktohandlemultiplerootelements
        //inthis.$el,whichisabadidea
        //Inmasterweshouldmakethis.$elawrapper
        //aroundmultiplesubelements
        var$otherEl=this.$el.not('select');
        this.$el=this.$el.first();

        this._super.apply(this,arguments);

        $otherEl.insertAfter(this.$el);
        this.$el=this.$el.add($otherEl);
    },
});

varFieldReportLayout=relational_fields.FieldMany2One.extend({
    //thiswidgetisnotgeneric,sowedisableitsstudiouse
    //supportedFieldTypes:['many2one','selection'],
    events:_.extend({},relational_fields.FieldMany2One.prototype.events,{
        'clickimg':'_onImgClicked',
    }),

    willStart:function(){
        varself=this;
        this.previews={};
        returnthis._super()
            .then(function(){
                returnself._rpc({
                    model:'report.layout',
                    method:"search_read"
                }).then(function(values){
                    self.previews=values;
                });
            });
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     */
    _render:function(){
        varself=this;
        this.$el.empty();
        varvalue=_.isObject(this.value)?this.value.data.id:this.value;
        _.each(this.previews,function(val){
            var$container=$('<div>').addClass('col-3text-center');
            var$img=$('<img>')
                .addClass('imgimg-fluidimg-thumbnailml16')
                .toggleClass('btn-info',val.view_id[0]===value)
                .attr('src',val.image)
                .data('key',val.view_id[0]);
            $container.append($img);
            if(val.pdf){
                var$previewLink=$('<a>')
                    .text('Example')
                    .attr('href',val.pdf)
                    .attr('target','_blank');
                $container.append($previewLink);
            }
            self.$el.append($container);
        });
    },

    //--------------------------------------------------------------------------
    //Handlers
    //--------------------------------------------------------------------------

    /**
     *@override
     *@private
     *@param{MouseEvent}event
     */
    _onImgClicked:function(event){
        this._setValue($(event.currentTarget).data('key'));
    },
});


constIframeWrapper=AbstractField.extend({
    description:_lt("Wraprawhtmlwithinaniframe"),

    //IfHTML,don'tforgettoadjustthesanitizeoptionstoavoidstrippingmostofthemetadata
    supportedFieldTypes:['text','html'],

    template:"web.IframeWrapper",

    _render(){

        constspinner=this.el.querySelector('.o_iframe_wrapper_spinner');
        constiframe=this.el.querySelector('.o_preview_iframe');

        iframe.style.display='none';
        spinner.style.display='block';

        //Promisefortests
        letresolver;
        $(iframe).data('ready',newPromise((resolve)=>{
            resolver=resolve;
        }));

        /**
         *Certainbrowserdon'ttriggeronloadeventsofiframeforparticularcases.
         *Inourcase,chromeandsafaricouldbeproblematicdependingonversionandenvironment.
         *Thisratherunorthodoxsolutionreplacetheonloadeventhandler.(jqueryon('load')doesn'tfixit)
         */
        constonloadReplacement=setInterval(()=>{
            constiframeDoc=iframe.contentDocument;
            if(iframeDoc&&(iframeDoc.readyState==='complete'||iframeDoc.readyState==='interactive')){

                /**
                 *Thedocument.writeisnotrecommended.ItisbettertomanipulatetheDOMthrough$.appendChildand
                 *others.Inourcasethough,wedealwithaniframewithoutsrcattributeandwithmetadatatoputin
                 *headtag.Ifweusetheusualdommethods,theiframeisautomaticallycreatedwithitsdocument
                 *componentcontaininghtml>head&body.Therefore,ifwewanttomakeitworkthatway,wewould
                 *needtoreceiveeachpieceatatimeto appendittothisdocument(withthis.record.dataandextra
                 *modelfieldsorwithanrpc).Italsocauseotherdifficultiesgettingattributeonthemostparent
                 *nodes,parsingtoHTMLcomplexelements,etc.
                 *Therefore,document.writemakesitmuchmoretrivialinoursituation.
                 */
                iframeDoc.open();
                iframeDoc.write(this.value);
                iframeDoc.close();

                iframe.style.display='block';
                spinner.style.display='none';

                resolver();

                clearInterval(onloadReplacement);
            }
        },100);

    }

});


return{
    FieldTimezoneMismatch:FieldTimezoneMismatch,
    FieldReportLayout:FieldReportLayout,
    IframeWrapper,
};

});
