flectra.define('web_editor.base',function(require){
'usestrict';

//TODOthisshouldbere-removedassoonaspossible.

varajax=require('web.ajax');
varsession=require('web.session');

vardomReady=newPromise(function(resolve){
    $(resolve);
});

return{
    /**
     *RetrievesalltheCSSruleswhichmatchthegivenparser(Regex).
     *
     *@param{Regex}filter
     *@returns{Object[]}ArrayofCSSrulesdescriptions(objects).Aruleis
     *         definedby3values:'selector','css'and'names'.'selector'
     *         isastringwhichcontainsthewholeselector,'css'isastring
     *         whichcontainsthecsspropertiesand'names'isanarrayofthe
     *         firstcapturedgroupsforeachselectorpart.E.g.:ifthe
     *         filterissettomatch.fa-*rulesandcapturetheiconnames,
     *         therule:
     *             '.fa-alias1::before,.fa-alias2::before{hello:world;}'
     *         willberetrievedas
     *             {
     *                 selector:'.fa-alias1::before,.fa-alias2::before',
     *                 css:'hello:world;',
     *                 names:['.fa-alias1','.fa-alias2'],
     *             }
     */
    cacheCssSelectors:{},
    getCssSelectors:function(filter){
        if(this.cacheCssSelectors[filter]){
            returnthis.cacheCssSelectors[filter];
        }
        this.cacheCssSelectors[filter]=[];
        varsheets=document.styleSheets;
        for(vari=0;i<sheets.length;i++){
            varrules;
            try{
                //try...catchbecauseFirefoxnotabletoenumerate
                //document.styleSheets[].cssRules[]forcross-domain
                //stylesheets.
                rules=sheets[i].rules||sheets[i].cssRules;
            }catch(e){
                console.warn("Can'treadthecssrulesof:"+sheets[i].href,e);
                continue;
            }
            if(!rules){
                continue;
            }

            for(varr=0;r<rules.length;r++){
                varselectorText=rules[r].selectorText;
                if(!selectorText){
                    continue;
                }
                varselectors=selectorText.split(/\s*,\s*/);
                vardata=null;
                for(vars=0;s<selectors.length;s++){
                    varmatch=selectors[s].trim().match(filter);
                    if(!match){
                        continue;
                    }
                    if(!data){
                        data={
                            selector:match[0],
                            css:rules[r].cssText.replace(/(^.*\{\s*)|(\s*\}\s*$)/g,''),
                            names:[match[1]]
                        };
                    }else{
                        data.selector+=(','+match[0]);
                        data.names.push(match[1]);
                    }
                }
                if(data){
                    this.cacheCssSelectors[filter].push(data);
                }
            }
        }
        returnthis.cacheCssSelectors[filter];
    },
    /**
     *Listoffonticonstoloadbyeditor.Theiconsaredisplayedinthemedia
     *editorandidentifiedlikefontandimage(canbecolored,spinned,resized
     *withfaclasses).
     *Toaddfont,pushanewobject{base,parser}
     *
     *-base:classwhoappearonallfonts
     *-parser:regularexpressionusedtoselectallfontincssstylesheets
     *
     *@typeArray
     */
    fontIcons:[{base:'fa',parser:/\.(fa-(?:\w|-)+)::?before/i}],
    /**
     *Searchesthefontsdescribedbythe@seefontIconsvariable.
     */
    computeFonts:_.once(function(){
        varself=this;
        _.each(this.fontIcons,function(data){
            data.cssData=self.getCssSelectors(data.parser);
            data.alias=_.flatten(_.map(data.cssData,_.property('names')));
        });
    }),
    /**
     *Ifawidgetneedstobeinstantiatedonpageloading,itneedstowait
     *forappropriateresourcestobeloaded.ThisfunctionreturnsaPromise
     *whichisresolvedwhenthedomisready,thesessionisbound
     *(translationsloaded)andtheXMLisloaded.Thisshouldhowevernotbe
     *necessaryanymoreaswidgetsshouldnotbeparentlessandshouldthenbe
     *instantiated(directlyornot)bythepagemaincomponent(webclient,
     *websiteroot,editorbar,...).TheDOMwillbereadythen,themain
     *componentisinchargeofwaitingforthesessionandtheXMLcanbe
     *lazyloadedthankstothe@seeWidget.xmlDependencieskey.
     *
     *@returns{Promise}
     */
    ready:function(){
        returnPromise.all([domReady,session.is_bound,ajax.loadXML()]);
    },
};
});

//==============================================================================

flectra.define('web_editor.context',function(require){
'usestrict';

//TODOthisshouldbere-removedassoonaspossible.

functiongetContext(context){
    varhtml=document.documentElement;
    return_.extend({
        lang:(html.getAttribute('lang')||'en_US').replace('-','_'),

        //Unfortunatelythisisamentionof'website'in'web_editor'asthere
        //wasnootherwaytodoitasthiswasrestoredinastableversion.
        //Indeed,theeditoriscurrentlyusingthiscontextattherootofJS
        //module,sothereisnowayforwebsitetohookitselfbefore
        //web_editorusesit(withoutariskyrefactoringofweb_editorin
        //stable).Asmentionedabove,theeditorshouldnotusethiscontext
        //anymoreanyway(thiswasrestoredbythesaas-12.2editorrevert).
        'website_id':html.getAttribute('data-website-id')|0,
    },context||{});
}
functiongetExtraContext(context){
    varhtml=document.documentElement;
    return_.extend(getContext(),{
        editable:!!(html.dataset.editable||$('[data-oe-model]').length),//temporaryhack,thisshouldbedoneinpython
        translatable:!!html.dataset.translatable,
        edit_translations:!!html.dataset.edit_translations,
    },context||{});
}

return{
    get:getContext,
    getExtra:getExtraContext,
};
});

//==============================================================================

flectra.define('web_editor.ready',function(require){
'usestrict';

//TODOthisshouldbere-removedassoonaspossible.

varbase=require('web_editor.base');

returnbase.ready();
});
