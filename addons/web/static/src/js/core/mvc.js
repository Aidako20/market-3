flectra.define('web.mvc',function(require){
"usestrict";

/**
 *Thisfilecontainsa'formalization'ofaMVCpattern,appliedtoFlectra
 *idioms.
 *
 *Forasimplewidget/component,thisisdefinitelyoverkill. However,when
 *workingoncomplexsystems,suchasFlectraviews(orthecontrolpanel,orsome
 *clientactions),itisusefultoclearlyseparatethecodeinconcerns.
 *
 *Wedefinehere4classes:Factory,Model,Renderer,Controller. Notethat
 *forvarioushistoricalreasons,weusethetermRendererinsteadofView.The
 *mainissueisthattheterm'View'isusedwaytoomuchinFlectraland,and
 *addingitwouldincreasetheconfusion.
 *
 *Inshort,herearetheresponsabilitiesofthefourclasses:
 *-Model:thisiswherethemainstateofthesystemlives. Thisisthepart
 *    thatwilltalktotheserver,processtheresultsandistheownerofthe
 *    state
 *-Renderer:thisistheUIcode:itshouldonlybeconcernedwiththelook
 *    andfeelofthesystem:rendering,bindinghandlers,...
 *-Controller:coordinatesthemodelwiththerendererandtheparentswidgets.
 *    Thisismorea'plumbing'widget.
 *-Factory:settinguptheMRCcomponentsisacomplextask,becauseeachof
 *    themneedstheproperarguments/options,itneedstobeextensible,they
 *    needstobecreatedintheproperorder,... Thejobofthefactoryis
 *    toprocessallthevariousarguments,andmakesureeachcomponentisas
 *    simpleaspossible.
 */

varajax=require('web.ajax');
varClass=require('web.Class');
varmixins=require('web.mixins');
varServicesMixin=require('web.ServicesMixin');
varWidget=require('web.Widget');


/**
 *Ownerofthestate,thiscomponentistaskedwithfetchingdata,processing
 *it,updatingit,...
 *
 *Notethatthisisnotawidget:itisaclasswhichhasnotUIrepresentation.
 *
 *@classModel
 */
varModel=Class.extend(mixins.EventDispatcherMixin,ServicesMixin,{
    /**
     *@param{Widget}parent
     *@param{Object}params
     */
    init:function(parent,params){
        mixins.EventDispatcherMixin.init.call(this);
        this.setParent(parent);
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *Thismethodshouldreturnthecompletestatenecessaryfortherenderer
     *todisplaythecurrentdata.
     *
     *@returns{*}
     */
    get:function(){
    },
    /**
     *Theloadmethodiscalledonceinamodel,whenweloadthedataforthe
     *firsttime. Themethodreturns(apromisethatresolvesto)somekind
     *oftoken/handle. Thehandlecanthenbeusedwiththegetmethodto
     *accessarepresentationofthedata.
     *
     *@param{Object}params
     *@returns{Promise}Thepromiseresolvestosomekindofhandle
     */
    load:function(){
        returnPromise.resolve();
    },
});

/**
 *Onlyresponsibilityofthiscomponentistodisplaytheuserinterface,and
 *reacttouserchanges.
 *
 *@classRenderer
 */
varRenderer=Widget.extend({
    /**
     *@override
     *@param{any}state
     *@param{Object}params
     */
    init:function(parent,state,params){
        this._super(parent);
        this.state=state;
    },
});

/**
 *Thecontrollerhastocoordinatebetweenparent,rendererandmodel.
 *
 *@classController
 */
varController=Widget.extend({
    /**
     *@override
     *@param{Model}model
     *@param{Renderer}renderer
     *@param{Object}params
     *@param{any}[params.handle=null]
     */
    init:function(parent,model,renderer,params){
        this._super.apply(this,arguments);
        this.handle=params.handle||null;
        this.model=model;
        this.renderer=renderer;
    },
    /**
     *@returns{Promise}
     */
    start:function(){
        returnPromise.all(
            [this._super.apply(this,arguments),
            this._startRenderer()]
        );
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Appendstherendererinthe$el.Tooverridetoinsertitelsewhere.
     *
     *@private
     */
    _startRenderer:function(){
        returnthis.renderer.appendTo(this.$el);
    },
});

varFactory=Class.extend({
    config:{
        Model:Model,
        Renderer:Renderer,
        Controller:Controller,
    },
    /**
     *@override
     */
    init:function(){
        this.rendererParams={};
        this.controllerParams={};
        this.modelParams={};
        this.loadParams={};
    },

    //--------------------------------------------------------------------------
    //Public
    //--------------------------------------------------------------------------

    /**
     *MainmethodoftheFactoryclass.Createacontroller,andmakesurethat
     *dataandlibrariesareloaded.
     *
     *Thereisaunusualthinggoinginthismethodwithparents:wecreate
     *renderer/modelwithparentasparent,thenwehavetoreassignthemat
     *theendtomakesurethatwehavetheproperrelationships. Thisis
     *necessarytosolvetheproblemthatthecontrollerneedsthemodeland
     *therenderertobeinstantiated,butthemodelneedaparenttobeable
     *toloaditself,andtherendererneedsthedatainitsconstructor.
     *
     *@param{Widget}parenttheparentoftheresultingController(most
     *     likelyanactionmanager)
     *@returns{Promise<Controller>}
     */
    getController:function(parent){
        varself=this;
        varmodel=this.getModel(parent);
        returnPromise.all([this._loadData(model),ajax.loadLibs(this)]).then(function(result){
            const{state,handle}=result[0];
            varrenderer=self.getRenderer(parent,state);
            varController=self.Controller||self.config.Controller;
            constinitialState=model.get(handle);
            varcontrollerParams=_.extend({
                initialState,
                handle,
            },self.controllerParams);
            varcontroller=newController(parent,model,renderer,controllerParams);
            model.setParent(controller);
            renderer.setParent(controller);
            returncontroller;
        });
    },
    /**
     *Returnsanewmodelinstance
     *
     *@param{Widget}parenttheparentofthemodel
     *@returns{Model}instanceofthemodel
     */
    getModel:function(parent){
        varModel=this.config.Model;
        returnnewModel(parent,this.modelParams);
    },
    /**
     *Returnsanewrendererinstance
     *
     *@param{Widget}parenttheparentoftherenderer
     *@param{Object}statetheinformationrelatedtotherendereddata
     *@returns{Renderer}instanceoftherenderer
     */
    getRenderer:function(parent,state){
        varRenderer=this.config.Renderer;
        returnnewRenderer(parent,state,this.rendererParams);
    },

    //--------------------------------------------------------------------------
    //Private
    //--------------------------------------------------------------------------

    /**
     *Loadsinitialdatafromthemodel
     *
     *@private
     *@param{Model}modelaModelinstance
     *@param{Object}[options={}]
     *@param{boolean}[options.withSampleData=true]
     *@returns{Promise<*>}apromisethatresolvestothevaluereturnedby
     *  thegetmethodfromthemodel
     *@todo:getridofloadParams(usemodelParamsinstead)
     */
    _loadData:function(model,options={}){
        options.withSampleData='withSampleData'inoptions?options.withSampleData:true;
        returnmodel.load(this.loadParams).then(function(handle){
            return{state:model.get(handle,options),handle};
        });
    },
});


return{
    Factory:Factory,
    Model:Model,
    Renderer:Renderer,
    Controller:Controller,
};

});
