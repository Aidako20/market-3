flectra.define('web_editor.wysiwyg.root',function(require){
'usestrict';

varWidget=require('web.Widget');

varassetsLoaded=false;

varWysiwygRoot=Widget.extend({
    assetLibs:['web_editor.compiled_assets_wysiwyg'],
    _loadLibsTplRoute:'/web_editor/public_render_template',

    publicMethods:['isDirty','save','getValue','setValue','getEditable','on','trigger','focus','saveModifiedImages'],

    /**
     *  @see'web_editor.wysiwyg'module
     **/
    init:function(parent,params){
        this._super.apply(this,arguments);
        this._params=params;
        this.$editor=null;
    },
    /**
     *Loadassets
     *
     *@override
     **/
    willStart:function(){
        varself=this;

        var$target=this.$el;
        this.$el=null;

        returnthis._super().then(function(){
            //FIXME:thiscodeworksbypureluck.Iftheweb_editor.wysiwyg
            //JSmodulewasrequiringadelayedmodule,usingithereright
            //awaywouldleadtoacrash.
            if(!assetsLoaded){
                varWysiwyg=flectra.__DEBUG__.services['web_editor.wysiwyg'];
                _.each(['getRange','setRange','setRangeFromNode'],function(methodName){
                    WysiwygRoot[methodName]=Wysiwyg[methodName].bind(Wysiwyg);
                });
                assetsLoaded=true;
            }

            varWysiwyg=self._getWysiwygContructor();
            varinstance=newWysiwyg(self,self._params);
            if(self.__extraAssetsForIframe){
                instance.__extraAssetsForIframe=self.__extraAssetsForIframe;
            }
            self._params=null;

            _.each(self.publicMethods,function(methodName){
                self[methodName]=instance[methodName].bind(instance);
            });

            returninstance.attachTo($target).then(function(){
                self.$editor=instance.$editor||instance.$el;
            });
        });
    },

    _getWysiwygContructor:function(){
        returnflectra.__DEBUG__.services['web_editor.wysiwyg'];
    }
});

returnWysiwygRoot;

});

flectra.define('web_editor.wysiwyg.default_options',function(require){
'usestrict';

/**
 *TODOthisshouldberefactoredtobedoneanotherway,sameasthe'root'
 *modulethatshouldbedoneanotherway.
 *
 *Thisallowstohaveaccesstodefaultoptionsthatareusedinthesummernote
 *editorsothattheycanbetweaked(insteadofentirelyreplaced)whenusing
 *theeditoronaneditablecontent.
 */

varcore=require('web.core');

var_lt=core._lt;

return{
    styleTags:['p','pre','small','h1','h2','h3','h4','h5','h6','blockquote'],
    fontSizes:[_lt('Default'),8,9,10,11,12,14,18,24,36,48,62],
};
});

//TODOshouldbemovedinadedicatedfileinnewerversions
flectra.define('web_editor.browser_extensions',function(require){
'usestrict';

//RedefinethegetRangeAtfunctioninordertoavoidanerrorappearing
//sometimeswhenaninputelementisfocusedonFirefox.
//TheerrorhappensbecausetherangereturnedbygetRangeAtis"restricted".
//Ex:Range{commonAncestorContainer:Restricted,startContainer:Restricted,
//startOffset:0,endContainer:Restricted,endOffset:0,collapsed:true}
//Thesolutionconsistsindetectingwhentherangeisrestrictedandthen
//redefiningitmanuallybasedonthecurrentselection.
constoriginalGetRangeAt=Selection.prototype.getRangeAt;
Selection.prototype.getRangeAt=function(){
    letrange=originalGetRangeAt.apply(this,arguments);
    //Checkiftherangeisrestricted
    if(range.startContainer&&!Object.getPrototypeOf(range.startContainer)){
        //Definetherangemanuallybasedontheselection
        range=document.createRange();
        range.setStart(this.anchorNode,0);
        range.setEnd(this.focusNode,0);
    }
    returnrange;
};
});
