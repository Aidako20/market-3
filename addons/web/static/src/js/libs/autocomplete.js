flectra.define('web.autocomplete.extensions',function(){
'usestrict';

/**
 *Thejqueryautocompletelibraryextensionsandfixesshouldbedonehereto
 *avoidpatchinginplace.
 */

//jqueryautocompletetweaktoallowhtmlandclassnames
varproto=$.ui.autocomplete.prototype;
varinitSource=proto._initSource;

functionfilter(array,term){
    varmatcher=newRegExp($.ui.autocomplete.escapeRegex(term),"i");
    return$.grep(array,function(value_){
        returnmatcher.test($("<div>").html(value_.label||value_.value||value_).text());
    });
}

$.extend(proto,{
    _initSource:function(){
        if(this.options.html&&$.isArray(this.options.source)){
            this.source=function(request,response){
                response(filter(this.options.source,request.term));
            };
        }else{
            initSource.call(this);
        }
    },
    _renderItem:function(ul,item){
        return$("<li></li>")
            .data("item.autocomplete",item)
            .append($("<a></a>")[this.options.html?"html":"text"](item.label))
            .appendTo(ul)
            .addClass(item.classname);
    },
});
});
