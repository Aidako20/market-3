define("ace/mode/scss_highlight_rules",["require","exports","module","ace/lib/oop","ace/lib/lang","ace/mode/text_highlight_rules"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varlang=require("../lib/lang");
varTextHighlightRules=require("./text_highlight_rules").TextHighlightRules;

varScssHighlightRules=function(){

    varproperties=lang.arrayToMap((function(){

        varbrowserPrefix=("-webkit-|-moz-|-o-|-ms-|-svg-|-pie-|-khtml-").split("|");

        varprefixProperties=("appearance|background-clip|background-inline-policy|background-origin|"+
             "background-size|binding|border-bottom-colors|border-left-colors|"+
             "border-right-colors|border-top-colors|border-end|border-end-color|"+
             "border-end-style|border-end-width|border-image|border-start|"+
             "border-start-color|border-start-style|border-start-width|box-align|"+
             "box-direction|box-flex|box-flexgroup|box-ordinal-group|box-orient|"+
             "box-pack|box-sizing|column-count|column-gap|column-width|column-rule|"+
             "column-rule-width|column-rule-style|column-rule-color|float-edge|"+
             "font-feature-settings|font-language-override|force-broken-image-icon|"+
             "image-region|margin-end|margin-start|opacity|outline|outline-color|"+
             "outline-offset|outline-radius|outline-radius-bottomleft|"+
             "outline-radius-bottomright|outline-radius-topleft|outline-radius-topright|"+
             "outline-style|outline-width|padding-end|padding-start|stack-sizing|"+
             "tab-size|text-blink|text-decoration-color|text-decoration-line|"+
             "text-decoration-style|transform|transform-origin|transition|"+
             "transition-delay|transition-duration|transition-property|"+
             "transition-timing-function|user-focus|user-input|user-modify|user-select|"+
             "window-shadow|border-radius").split("|");

        varproperties=("azimuth|background-attachment|background-color|background-image|"+
            "background-position|background-repeat|background|border-bottom-color|"+
            "border-bottom-style|border-bottom-width|border-bottom|border-collapse|"+
            "border-color|border-left-color|border-left-style|border-left-width|"+
            "border-left|border-right-color|border-right-style|border-right-width|"+
            "border-right|border-spacing|border-style|border-top-color|"+
            "border-top-style|border-top-width|border-top|border-width|border|bottom|"+
            "box-shadow|box-sizing|caption-side|clear|clip|color|content|counter-increment|"+
            "counter-reset|cue-after|cue-before|cue|cursor|direction|display|"+
            "elevation|empty-cells|float|font-family|font-size-adjust|font-size|"+
            "font-stretch|font-style|font-variant|font-weight|font|height|left|"+
            "letter-spacing|line-height|list-style-image|list-style-position|"+
            "list-style-type|list-style|margin-bottom|margin-left|margin-right|"+
            "margin-top|marker-offset|margin|marks|max-height|max-width|min-height|"+
            "min-width|opacity|orphans|outline-color|"+
            "outline-style|outline-width|outline|overflow|overflow-x|overflow-y|padding-bottom|"+
            "padding-left|padding-right|padding-top|padding|page-break-after|"+
            "page-break-before|page-break-inside|page|pause-after|pause-before|"+
            "pause|pitch-range|pitch|play-during|position|quotes|richness|right|"+
            "size|speak-header|speak-numeral|speak-punctuation|speech-rate|speak|"+
            "stress|table-layout|text-align|text-decoration|text-indent|"+
            "text-shadow|text-transform|top|unicode-bidi|vertical-align|"+
            "visibility|voice-family|volume|white-space|widows|width|word-spacing|"+
            "z-index").split("|");
        varret=[];
        for(vari=0,ln=browserPrefix.length;i<ln;i++){
            Array.prototype.push.apply(
                ret,
                ((browserPrefix[i]+prefixProperties.join("|"+browserPrefix[i])).split("|"))
            );
        }
        Array.prototype.push.apply(ret,prefixProperties);
        Array.prototype.push.apply(ret,properties);

        returnret;

    })());



    varfunctions=lang.arrayToMap(
        ("hsl|hsla|rgb|rgba|url|attr|counter|counters|abs|adjust_color|adjust_hue|"+
         "alpha|join|blue|ceil|change_color|comparable|complement|darken|desaturate|"+
         "floor|grayscale|green|hue|if|invert|join|length|lighten|lightness|mix|"+
         "nth|opacify|opacity|percentage|quote|red|round|saturate|saturation|"+
         "scale_color|transparentize|type_of|unit|unitless|unquote").split("|")
    );

    varconstants=lang.arrayToMap(
        ("absolute|all-scroll|always|armenian|auto|baseline|below|bidi-override|"+
        "block|bold|bolder|border-box|both|bottom|break-all|break-word|capitalize|center|"+
        "char|circle|cjk-ideographic|col-resize|collapse|content-box|crosshair|dashed|"+
        "decimal-leading-zero|decimal|default|disabled|disc|"+
        "distribute-all-lines|distribute-letter|distribute-space|"+
        "distribute|dotted|double|e-resize|ellipsis|fixed|georgian|groove|"+
        "hand|hebrew|help|hidden|hiragana-iroha|hiragana|horizontal|"+
        "ideograph-alpha|ideograph-numeric|ideograph-parenthesis|"+
        "ideograph-space|inactive|inherit|inline-block|inline|inset|inside|"+
        "inter-ideograph|inter-word|italic|justify|katakana-iroha|katakana|"+
        "keep-all|left|lighter|line-edge|line-through|line|list-item|loose|"+
        "lower-alpha|lower-greek|lower-latin|lower-roman|lowercase|lr-tb|ltr|"+
        "medium|middle|move|n-resize|ne-resize|newspaper|no-drop|no-repeat|"+
        "nw-resize|none|normal|not-allowed|nowrap|oblique|outset|outside|"+
        "overline|pointer|progress|relative|repeat-x|repeat-y|repeat|right|"+
        "ridge|row-resize|rtl|s-resize|scroll|se-resize|separate|small-caps|"+
        "solid|square|static|strict|super|sw-resize|table-footer-group|"+
        "table-header-group|tb-rl|text-bottom|text-top|text|thick|thin|top|"+
        "transparent|underline|upper-alpha|upper-latin|upper-roman|uppercase|"+
        "vertical-ideographic|vertical-text|visible|w-resize|wait|whitespace|"+
        "zero").split("|")
    );

    varcolors=lang.arrayToMap(
        ("aliceblue|antiquewhite|aqua|aquamarine|azure|beige|bisque|black|"+
        "blanchedalmond|blue|blueviolet|brown|burlywood|cadetblue|"+
        "chartreuse|chocolate|coral|cornflowerblue|cornsilk|crimson|cyan|"+
        "darkblue|darkcyan|darkgoldenrod|darkgray|darkgreen|darkgrey|"+
        "darkkhaki|darkmagenta|darkolivegreen|darkorange|darkorchid|darkred|"+
        "darksalmon|darkseagreen|darkslateblue|darkslategray|darkslategrey|"+
        "darkturquoise|darkviolet|deeppink|deepskyblue|dimgray|dimgrey|"+
        "dodgerblue|firebrick|floralwhite|forestgreen|fuchsia|gainsboro|"+
        "ghostwhite|gold|goldenrod|gray|green|greenyellow|grey|honeydew|"+
        "hotpink|indianred|indigo|ivory|khaki|lavender|lavenderblush|"+
        "lawngreen|lemonchiffon|lightblue|lightcoral|lightcyan|"+
        "lightgoldenrodyellow|lightgray|lightgreen|lightgrey|lightpink|"+
        "lightsalmon|lightseagreen|lightskyblue|lightslategray|"+
        "lightslategrey|lightsteelblue|lightyellow|lime|limegreen|linen|"+
        "magenta|maroon|mediumaquamarine|mediumblue|mediumorchid|"+
        "mediumpurple|mediumseagreen|mediumslateblue|mediumspringgreen|"+
        "mediumturquoise|mediumvioletred|midnightblue|mintcream|mistyrose|"+
        "moccasin|navajowhite|navy|oldlace|olive|olivedrab|orange|orangered|"+
        "orchid|palegoldenrod|palegreen|paleturquoise|palevioletred|"+
        "papayawhip|peachpuff|peru|pink|plum|powderblue|purple|rebeccapurple|"+
        "red|rosybrown|royalblue|saddlebrown|salmon|sandybrown|seagreen|"+
        "seashell|sienna|silver|skyblue|slateblue|slategray|slategrey|snow|"+
        "springgreen|steelblue|tan|teal|thistle|tomato|turquoise|violet|"+
        "wheat|white|whitesmoke|yellow|yellowgreen").split("|")
    );

    varkeywords=lang.arrayToMap(
        ("@mixin|@extend|@include|@import|@media|@debug|@warn|@if|@for|@each|@while|@else|@font-face|@-webkit-keyframes|if|and|!default|module|def|end|declare").split("|")
    );

    vartags=lang.arrayToMap(
        ("a|abbr|acronym|address|applet|area|article|aside|audio|b|base|basefont|bdo|"+
         "big|blockquote|body|br|button|canvas|caption|center|cite|code|col|colgroup|"+
         "command|datalist|dd|del|details|dfn|dir|div|dl|dt|em|embed|fieldset|"+
         "figcaption|figure|font|footer|form|frame|frameset|h1|h2|h3|h4|h5|h6|head|"+
         "header|hgroup|hr|html|i|iframe|img|input|ins|keygen|kbd|label|legend|li|"+
         "link|map|mark|menu|meta|meter|nav|noframes|noscript|object|ol|optgroup|"+
         "option|output|p|param|pre|progress|q|rp|rt|ruby|s|samp|script|section|select|"+
         "small|source|span|strike|strong|style|sub|summary|sup|table|tbody|td|"+
         "textarea|tfoot|th|thead|time|title|tr|tt|u|ul|var|video|wbr|xmp").split("|")
    );

    varnumRe="\\-?(?:(?:[0-9]+)|(?:[0-9]*\\.[0-9]+))";

    this.$rules={
        "start":[
            {
                token:"comment",
                regex:"\\/\\/.*$"
            },
            {
                token:"comment",//multilinecomment
                regex:"\\/\\*",
                next:"comment"
            },{
                token:"string",//singleline
                regex:'["](?:(?:\\\\.)|(?:[^"\\\\]))*?["]'
            },{
                token:"string",//multilinestringstart
                regex:'["].*\\\\$',
                next:"qqstring"
            },{
                token:"string",//singleline
                regex:"['](?:(?:\\\\.)|(?:[^'\\\\]))*?[']"
            },{
                token:"string",//multilinestringstart
                regex:"['].*\\\\$",
                next:"qstring"
            },{
                token:"constant.numeric",
                regex:numRe+"(?:em|ex|px|cm|mm|in|pt|pc|deg|rad|grad|ms|s|hz|khz|%)"
            },{
                token:"constant.numeric",//hex6color
                regex:"#[a-f0-9]{6}"
            },{
                token:"constant.numeric",//hex3color
                regex:"#[a-f0-9]{3}"
            },{
                token:"constant.numeric",
                regex:numRe
            },{
                token:["support.function","string","support.function"],
                regex:"(url\\()(.*)(\\))"
            },{
                token:function(value){
                    if(properties.hasOwnProperty(value.toLowerCase()))
                        return"support.type";
                    if(keywords.hasOwnProperty(value))
                        return"keyword";
                    elseif(constants.hasOwnProperty(value))
                        return"constant.language";
                    elseif(functions.hasOwnProperty(value))
                        return"support.function";
                    elseif(colors.hasOwnProperty(value.toLowerCase()))
                        return"support.constant.color";
                    elseif(tags.hasOwnProperty(value.toLowerCase()))
                        return"variable.language";
                    else
                        return"text";
                },
                regex:"\\-?[@a-z_][@a-z0-9_\\-]*"
            },{
                token:"variable",
                regex:"[a-z_\\-$][a-z0-9_\\-$]*\\b"
            },{
                token:"variable.language",
                regex:"#[a-z0-9-_]+"
            },{
                token:"variable.language",
                regex:"\\.[a-z0-9-_]+"
            },{
                token:"variable.language",
                regex:":[a-z0-9-_]+"
            },{
                token:"constant",
                regex:"[a-z0-9-_]+"
            },{
                token:"keyword.operator",
                regex:"<|>|<=|>=|==|!=|-|%|#|\\+|\\$|\\+|\\*"
            },{
                token:"paren.lparen",
                regex:"[[({]"
            },{
                token:"paren.rparen",
                regex:"[\\])}]"
            },{
                token:"text",
                regex:"\\s+"
            },{
                caseInsensitive:true
            }
        ],
        "comment":[
            {
                token:"comment",//closingcomment
                regex:"\\*\\/",
                next:"start"
            },{
                defaultToken:"comment"
            }
        ],
        "qqstring":[
            {
                token:"string",
                regex:'(?:(?:\\\\.)|(?:[^"\\\\]))*?"',
                next:"start"
            },{
                token:"string",
                regex:'.+'
            }
        ],
        "qstring":[
            {
                token:"string",
                regex:"(?:(?:\\\\.)|(?:[^'\\\\]))*?'",
                next:"start"
            },{
                token:"string",
                regex:'.+'
            }
        ]
    };
};

oop.inherits(ScssHighlightRules,TextHighlightRules);

exports.ScssHighlightRules=ScssHighlightRules;

});

define("ace/mode/matching_brace_outdent",["require","exports","module","ace/range"],function(require,exports,module){
"usestrict";

varRange=require("../range").Range;

varMatchingBraceOutdent=function(){};

(function(){

    this.checkOutdent=function(line,input){
        if(!/^\s+$/.test(line))
            returnfalse;

        return/^\s*\}/.test(input);
    };

    this.autoOutdent=function(doc,row){
        varline=doc.getLine(row);
        varmatch=line.match(/^(\s*\})/);

        if(!match)return0;

        varcolumn=match[1].length;
        varopenBracePos=doc.findMatchingBracket({row:row,column:column});

        if(!openBracePos||openBracePos.row==row)return0;

        varindent=this.$getIndent(doc.getLine(openBracePos.row));
        doc.replace(newRange(row,0,row,column-1),indent);
    };

    this.$getIndent=function(line){
        returnline.match(/^\s*/)[0];
    };

}).call(MatchingBraceOutdent.prototype);

exports.MatchingBraceOutdent=MatchingBraceOutdent;
});

define("ace/mode/behaviour/css",["require","exports","module","ace/lib/oop","ace/mode/behaviour","ace/mode/behaviour/cstyle","ace/token_iterator"],function(require,exports,module){
"usestrict";

varoop=require("../../lib/oop");
varBehaviour=require("../behaviour").Behaviour;
varCstyleBehaviour=require("./cstyle").CstyleBehaviour;
varTokenIterator=require("../../token_iterator").TokenIterator;

varCssBehaviour=function(){

    this.inherit(CstyleBehaviour);

    this.add("colon","insertion",function(state,action,editor,session,text){
        if(text===':'){
            varcursor=editor.getCursorPosition();
            variterator=newTokenIterator(session,cursor.row,cursor.column);
            vartoken=iterator.getCurrentToken();
            if(token&&token.value.match(/\s+/)){
                token=iterator.stepBackward();
            }
            if(token&&token.type==='support.type'){
                varline=session.doc.getLine(cursor.row);
                varrightChar=line.substring(cursor.column,cursor.column+1);
                if(rightChar===':'){
                    return{
                       text:'',
                       selection:[1,1]
                    };
                }
                if(!line.substring(cursor.column).match(/^\s*;/)){
                    return{
                       text:':;',
                       selection:[1,1]
                    };
                }
            }
        }
    });

    this.add("colon","deletion",function(state,action,editor,session,range){
        varselected=session.doc.getTextRange(range);
        if(!range.isMultiLine()&&selected===':'){
            varcursor=editor.getCursorPosition();
            variterator=newTokenIterator(session,cursor.row,cursor.column);
            vartoken=iterator.getCurrentToken();
            if(token&&token.value.match(/\s+/)){
                token=iterator.stepBackward();
            }
            if(token&&token.type==='support.type'){
                varline=session.doc.getLine(range.start.row);
                varrightChar=line.substring(range.end.column,range.end.column+1);
                if(rightChar===';'){
                    range.end.column++;
                    returnrange;
                }
            }
        }
    });

    this.add("semicolon","insertion",function(state,action,editor,session,text){
        if(text===';'){
            varcursor=editor.getCursorPosition();
            varline=session.doc.getLine(cursor.row);
            varrightChar=line.substring(cursor.column,cursor.column+1);
            if(rightChar===';'){
                return{
                   text:'',
                   selection:[1,1]
                };
            }
        }
    });

};
oop.inherits(CssBehaviour,CstyleBehaviour);

exports.CssBehaviour=CssBehaviour;
});

define("ace/mode/folding/cstyle",["require","exports","module","ace/lib/oop","ace/range","ace/mode/folding/fold_mode"],function(require,exports,module){
"usestrict";

varoop=require("../../lib/oop");
varRange=require("../../range").Range;
varBaseFoldMode=require("./fold_mode").FoldMode;

varFoldMode=exports.FoldMode=function(commentRegex){
    if(commentRegex){
        this.foldingStartMarker=newRegExp(
            this.foldingStartMarker.source.replace(/\|[^|]*?$/,"|"+commentRegex.start)
        );
        this.foldingStopMarker=newRegExp(
            this.foldingStopMarker.source.replace(/\|[^|]*?$/,"|"+commentRegex.end)
        );
    }
};
oop.inherits(FoldMode,BaseFoldMode);

(function(){

    this.foldingStartMarker=/([\{\[\(])[^\}\]\)]*$|^\s*(\/\*)/;
    this.foldingStopMarker=/^[^\[\{\(]*([\}\]\)])|^[\s\*]*(\*\/)/;
    this.singleLineBlockCommentRe=/^\s*(\/\*).*\*\/\s*$/;
    this.tripleStarBlockCommentRe=/^\s*(\/\*\*\*).*\*\/\s*$/;
    this.startRegionRe=/^\s*(\/\*|\/\/)#?region\b/;
    this._getFoldWidgetBase=this.getFoldWidget;
    this.getFoldWidget=function(session,foldStyle,row){
        varline=session.getLine(row);

        if(this.singleLineBlockCommentRe.test(line)){
            if(!this.startRegionRe.test(line)&&!this.tripleStarBlockCommentRe.test(line))
                return"";
        }

        varfw=this._getFoldWidgetBase(session,foldStyle,row);

        if(!fw&&this.startRegionRe.test(line))
            return"start";//lineCommentRegionStart

        returnfw;
    };

    this.getFoldWidgetRange=function(session,foldStyle,row,forceMultiline){
        varline=session.getLine(row);

        if(this.startRegionRe.test(line))
            returnthis.getCommentRegionBlock(session,line,row);

        varmatch=line.match(this.foldingStartMarker);
        if(match){
            vari=match.index;

            if(match[1])
                returnthis.openingBracketBlock(session,match[1],row,i);

            varrange=session.getCommentFoldRange(row,i+match[0].length,1);

            if(range&&!range.isMultiLine()){
                if(forceMultiline){
                    range=this.getSectionRange(session,row);
                }elseif(foldStyle!="all")
                    range=null;
            }

            returnrange;
        }

        if(foldStyle==="markbegin")
            return;

        varmatch=line.match(this.foldingStopMarker);
        if(match){
            vari=match.index+match[0].length;

            if(match[1])
                returnthis.closingBracketBlock(session,match[1],row,i);

            returnsession.getCommentFoldRange(row,i,-1);
        }
    };

    this.getSectionRange=function(session,row){
        varline=session.getLine(row);
        varstartIndent=line.search(/\S/);
        varstartRow=row;
        varstartColumn=line.length;
        row=row+1;
        varendRow=row;
        varmaxRow=session.getLength();
        while(++row<maxRow){
            line=session.getLine(row);
            varindent=line.search(/\S/);
            if(indent===-1)
                continue;
            if (startIndent>indent)
                break;
            varsubRange=this.getFoldWidgetRange(session,"all",row);

            if(subRange){
                if(subRange.start.row<=startRow){
                    break;
                }elseif(subRange.isMultiLine()){
                    row=subRange.end.row;
                }elseif(startIndent==indent){
                    break;
                }
            }
            endRow=row;
        }

        returnnewRange(startRow,startColumn,endRow,session.getLine(endRow).length);
    };
    this.getCommentRegionBlock=function(session,line,row){
        varstartColumn=line.search(/\s*$/);
        varmaxRow=session.getLength();
        varstartRow=row;

        varre=/^\s*(?:\/\*|\/\/|--)#?(end)?region\b/;
        vardepth=1;
        while(++row<maxRow){
            line=session.getLine(row);
            varm=re.exec(line);
            if(!m)continue;
            if(m[1])depth--;
            elsedepth++;

            if(!depth)break;
        }

        varendRow=row;
        if(endRow>startRow){
            returnnewRange(startRow,startColumn,endRow,line.length);
        }
    };

}).call(FoldMode.prototype);

});

define("ace/mode/scss",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/scss_highlight_rules","ace/mode/matching_brace_outdent","ace/mode/behaviour/css","ace/mode/folding/cstyle"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varTextMode=require("./text").Mode;
varScssHighlightRules=require("./scss_highlight_rules").ScssHighlightRules;
varMatchingBraceOutdent=require("./matching_brace_outdent").MatchingBraceOutdent;
varCssBehaviour=require("./behaviour/css").CssBehaviour;
varCStyleFoldMode=require("./folding/cstyle").FoldMode;

varMode=function(){
    this.HighlightRules=ScssHighlightRules;
    this.$outdent=newMatchingBraceOutdent();
    this.$behaviour=newCssBehaviour();
    this.foldingRules=newCStyleFoldMode();
};
oop.inherits(Mode,TextMode);

(function(){

    this.lineCommentStart="//";
    this.blockComment={start:"/*",end:"*/"};

    this.getNextLineIndent=function(state,line,tab){
        varindent=this.$getIndent(line);
        vartokens=this.getTokenizer().getLineTokens(line,state).tokens;
        if(tokens.length&&tokens[tokens.length-1].type=="comment"){
            returnindent;
        }

        varmatch=line.match(/^.*\{\s*$/);
        if(match){
            indent+=tab;
        }

        returnindent;
    };

    this.checkOutdent=function(state,line,input){
        returnthis.$outdent.checkOutdent(line,input);
    };

    this.autoOutdent=function(state,doc,row){
        this.$outdent.autoOutdent(doc,row);
    };

    this.$id="ace/mode/scss";
}).call(Mode.prototype);

exports.Mode=Mode;

});
