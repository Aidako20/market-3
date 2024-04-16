flectra.define('web.QWeb',function(require){
"usestrict";

vartranslation=require('web.translation');

var_t=translation._t;

/**
 *@param{boolean}debug
 *@param{Object}default_dict
 *@param{boolean}[enableTranslation=true]iftrue(thisisthedefault),
 *  therenderingwilltranslateallstringsthatarenotmarkedwith
 *  t-translation=off. Thisisusefulforthekanbanview,whichusesa
 *  templatewhichisalreadytranslatedbytheserver
 */
functionQWeb(debug,default_dict,enableTranslation){
    if(enableTranslation===undefined){
        enableTranslation=true;
    }
    varqweb=newQWeb2.Engine();
    qweb.default_dict=_.extend({},default_dict||{},{
        '_':_,
        'JSON':JSON,
        '_t':translation._t,
        '__debug__':debug,
        'moment':function(date){returnnewmoment(date);},
        'csrf_token':flectra.csrf_token,
    });
    qweb.debug=debug;
    qweb.preprocess_node=enableTranslation?preprocess_node:function(){};
    returnqweb;
}

functionpreprocess_node(){
    //Notethat'this'istheQwebNode
    switch(this.node.nodeType){
        caseNode.TEXT_NODE:
        caseNode.CDATA_SECTION_NODE:
            //TextandCDATAs
            vartranslation=this.node.parentNode.attributes['t-translation'];
            if(translation&&translation.value==='off'){
                return;
            }
            varmatch=/^(\s*)([\s\S]+?)(\s*)$/.exec(this.node.data);
            if(match){
                this.node.data=match[1]+_t(match[2])+match[3];
            }
            break;
        caseNode.ELEMENT_NODE:
            //Element
            varattr,attrs=['label','title','alt','placeholder','aria-label'];
            while((attr=attrs.pop())){
                if(this.attributes[attr]){
                    this.attributes[attr]=_t(this.attributes[attr]);
                }
            }
    }
}

returnQWeb;

});
