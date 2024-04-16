define("ace/mode/doc_comment_highlight_rules",["require","exports","module"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varTextHighlightRules=require("./text_highlight_rules").TextHighlightRules;

varDocCommentHighlightRules=function(){
    this.$rules={
        "start":[{
            token:"comment.doc.tag",
            regex:"@[\\w\\d_]+"//TODO:fixemailaddresses
        },
        DocCommentHighlightRules.getTagRule(),
        {
            defaultToken:"comment.doc",
            caseInsensitive:true
        }]
    };
};

oop.inherits(DocCommentHighlightRules,TextHighlightRules);

DocCommentHighlightRules.getTagRule=function(start){
    return{
        token:"comment.doc.tag.storage.type",
        regex:"\\b(?:TODO|FIXME|XXX|HACK)\\b"
    };
};

DocCommentHighlightRules.getStartRule=function(start){
    return{
        token:"comment.doc",//doccomment
        regex:"\\/\\*(?=\\*)",
        next :start
    };
};

DocCommentHighlightRules.getEndRule=function(start){
    return{
        token:"comment.doc",//closingcomment
        regex:"\\*\\/",
        next :start
    };
};

exports.DocCommentHighlightRules=DocCommentHighlightRules;

});
