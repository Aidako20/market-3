define("ace/mode/python_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varTextHighlightRules=require("./text_highlight_rules").TextHighlightRules;

varPythonHighlightRules=function(){

    varkeywords=(
        "and|as|assert|break|class|continue|def|del|elif|else|except|exec|"+
        "finally|for|from|global|if|import|in|is|lambda|not|or|pass|print|"+
        "raise|return|try|while|with|yield|async|await"
    );

    varbuiltinConstants=(
        "True|False|None|NotImplemented|Ellipsis|__debug__"
    );

    varbuiltinFunctions=(
        "abs|divmod|input|open|staticmethod|all|enumerate|int|ord|str|any|"+
        "eval|isinstance|pow|sum|basestring|execfile|issubclass|print|super|"+
        "binfile|iter|property|tuple|bool|filter|len|range|type|bytearray|"+
        "float|list|raw_input|unichr|callable|format|locals|reduce|unicode|"+
        "chr|frozenset|long|reload|vars|classmethod|getattr|map|repr|xrange|"+
        "cmp|globals|max|reversed|zip|compile|hasattr|memoryview|round|"+
        "__import__|complex|hash|min|set|apply|delattr|help|next|setattr|"+
        "buffer|dict|hex|object|slice|coerce|dir|id|oct|sorted|intern"
    );
    varkeywordMapper=this.createKeywordMapper({
        "invalid.deprecated":"debugger",
        "support.function":builtinFunctions,
        "constant.language":builtinConstants,
        "keyword":keywords
    },"identifier");

    varstrPre="(?:r|u|ur|R|U|UR|Ur|uR)?";

    vardecimalInteger="(?:(?:[1-9]\\d*)|(?:0))";
    varoctInteger="(?:0[oO]?[0-7]+)";
    varhexInteger="(?:0[xX][\\dA-Fa-f]+)";
    varbinInteger="(?:0[bB][01]+)";
    varinteger="(?:"+decimalInteger+"|"+octInteger+"|"+hexInteger+"|"+binInteger+")";

    varexponent="(?:[eE][+-]?\\d+)";
    varfraction="(?:\\.\\d+)";
    varintPart="(?:\\d+)";
    varpointFloat="(?:(?:"+intPart+"?"+fraction+")|(?:"+intPart+"\\.))";
    varexponentFloat="(?:(?:"+pointFloat+"|"+ intPart+")"+exponent+")";
    varfloatNumber="(?:"+exponentFloat+"|"+pointFloat+")";

    varstringEscape= "\\\\(x[0-9A-Fa-f]{2}|[0-7]{3}|[\\\\abfnrtv'\"]|U[0-9A-Fa-f]{8}|u[0-9A-Fa-f]{4})";

    this.$rules={
        "start":[{
            token:"comment",
            regex:"#.*$"
        },{
            token:"string",          //multiline"""stringstart
            regex:strPre+'"{3}',
            next:"qqstring3"
        },{
            token:"string",          //"string
            regex:strPre+'"(?=.)',
            next:"qqstring"
        },{
            token:"string",          //multiline'''stringstart
            regex:strPre+"'{3}",
            next:"qstring3"
        },{
            token:"string",          //'string
            regex:strPre+"'(?=.)",
            next:"qstring"
        },{
            token:"constant.numeric",//imaginary
            regex:"(?:"+floatNumber+"|\\d+)[jJ]\\b"
        },{
            token:"constant.numeric",//float
            regex:floatNumber
        },{
            token:"constant.numeric",//longinteger
            regex:integer+"[lL]\\b"
        },{
            token:"constant.numeric",//integer
            regex:integer+"\\b"
        },{
            token:keywordMapper,
            regex:"[a-zA-Z_$][a-zA-Z0-9_$]*\\b"
        },{
            token:"keyword.operator",
            regex:"\\+|\\-|\\*|\\*\\*|\\/|\\/\\/|%|<<|>>|&|\\||\\^|~|<|>|<=|=>|==|!=|<>|="
        },{
            token:"paren.lparen",
            regex:"[\\[\\(\\{]"
        },{
            token:"paren.rparen",
            regex:"[\\]\\)\\}]"
        },{
            token:"text",
            regex:"\\s+"
        }],
        "qqstring3":[{
            token:"constant.language.escape",
            regex:stringEscape
        },{
            token:"string",//multiline"""stringend
            regex:'"{3}',
            next:"start"
        },{
            defaultToken:"string"
        }],
        "qstring3":[{
            token:"constant.language.escape",
            regex:stringEscape
        },{
            token:"string", //multiline'''stringend
            regex:"'{3}",
            next:"start"
        },{
            defaultToken:"string"
        }],
        "qqstring":[{
            token:"constant.language.escape",
            regex:stringEscape
        },{
            token:"string",
            regex:"\\\\$",
            next :"qqstring"
        },{
            token:"string",
            regex:'"|$',
            next :"start"
        },{
            defaultToken:"string"
        }],
        "qstring":[{
            token:"constant.language.escape",
            regex:stringEscape
        },{
            token:"string",
            regex:"\\\\$",
            next :"qstring"
        },{
            token:"string",
            regex:"'|$",
            next :"start"
        },{
            defaultToken:"string"
        }]
    };
};

oop.inherits(PythonHighlightRules,TextHighlightRules);

exports.PythonHighlightRules=PythonHighlightRules;
});

define("ace/mode/folding/pythonic",["require","exports","module","ace/lib/oop","ace/mode/folding/fold_mode"],function(require,exports,module){
"usestrict";

varoop=require("../../lib/oop");
varBaseFoldMode=require("./fold_mode").FoldMode;

varFoldMode=exports.FoldMode=function(markers){
    this.foldingStartMarker=newRegExp("([\\[{])(?:\\s*)$|("+markers+")(?:\\s*)(?:#.*)?$");
};
oop.inherits(FoldMode,BaseFoldMode);

(function(){

    this.getFoldWidgetRange=function(session,foldStyle,row){
        varline=session.getLine(row);
        varmatch=line.match(this.foldingStartMarker);
        if(match){
            if(match[1])
                returnthis.openingBracketBlock(session,match[1],row,match.index);
            if(match[2])
                returnthis.indentationBlock(session,row,match.index+match[2].length);
            returnthis.indentationBlock(session,row);
        }
    };

}).call(FoldMode.prototype);

});

define("ace/mode/python",["require","exports","module","ace/lib/oop","ace/mode/text","ace/mode/python_highlight_rules","ace/mode/folding/pythonic","ace/range"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varTextMode=require("./text").Mode;
varPythonHighlightRules=require("./python_highlight_rules").PythonHighlightRules;
varPythonFoldMode=require("./folding/pythonic").FoldMode;
varRange=require("../range").Range;

varMode=function(){
    this.HighlightRules=PythonHighlightRules;
    this.foldingRules=newPythonFoldMode("\\:");
    this.$behaviour=this.$defaultBehaviour;
};
oop.inherits(Mode,TextMode);

(function(){

    this.lineCommentStart="#";

    this.getNextLineIndent=function(state,line,tab){
        varindent=this.$getIndent(line);

        vartokenizedLine=this.getTokenizer().getLineTokens(line,state);
        vartokens=tokenizedLine.tokens;

        if(tokens.length&&tokens[tokens.length-1].type=="comment"){
            returnindent;
        }

        if(state=="start"){
            varmatch=line.match(/^.*[\{\(\[:]\s*$/);
            if(match){
                indent+=tab;
            }
        }

        returnindent;
    };

    varoutdents={
        "pass":1,
        "return":1,
        "raise":1,
        "break":1,
        "continue":1
    };
    
    this.checkOutdent=function(state,line,input){
        if(input!=="\r\n"&&input!=="\r"&&input!=="\n")
            returnfalse;

        vartokens=this.getTokenizer().getLineTokens(line.trim(),state).tokens;
        
        if(!tokens)
            returnfalse;
        do{
            varlast=tokens.pop();
        }while(last&&(last.type=="comment"||(last.type=="text"&&last.value.match(/^\s+$/))));
        
        if(!last)
            returnfalse;
        
        return(last.type=="keyword"&&outdents[last.value]);
    };

    this.autoOutdent=function(state,doc,row){
        
        row+=1;
        varindent=this.$getIndent(doc.getLine(row));
        vartab=doc.getTabString();
        if(indent.slice(-tab.length)==tab)
            doc.remove(newRange(row,indent.length-tab.length,row,indent.length));
    };

    this.$id="ace/mode/python";
}).call(Mode.prototype);

exports.Mode=Mode;
});
