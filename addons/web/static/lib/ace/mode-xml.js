define("ace/mode/xml_highlight_rules",["require","exports","module","ace/lib/oop","ace/mode/text_highlight_rules"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varTextHighlightRules=require("./text_highlight_rules").TextHighlightRules;

varXmlHighlightRules=function(normalize){
    vartagRegex="[_:a-zA-Z\xc0-\uffff][-_:.a-zA-Z0-9\xc0-\uffff]*";

    this.$rules={
        start:[
            {token:"string.cdata.xml",regex:"<\\!\\[CDATA\\[",next:"cdata"},
            {
                token:["punctuation.instruction.xml","keyword.instruction.xml"],
                regex:"(<\\?)("+tagRegex+")",next:"processing_instruction"
            },
            {token:"comment.start.xml",regex:"<\\!--",next:"comment"},
            {
                token:["xml-pe.doctype.xml","xml-pe.doctype.xml"],
                regex:"(<\\!)(DOCTYPE)(?=[\\s])",next:"doctype",caseInsensitive:true
            },
            {include:"tag"},
            {token:"text.end-tag-open.xml",regex:"</"},
            {token:"text.tag-open.xml",regex:"<"},
            {include:"reference"},
            {defaultToken:"text.xml"}
        ],

        processing_instruction:[{
            token:"entity.other.attribute-name.decl-attribute-name.xml",
            regex:tagRegex
        },{
            token:"keyword.operator.decl-attribute-equals.xml",
            regex:"="
        },{
            include:"whitespace"
        },{
            include:"string"
        },{
            token:"punctuation.xml-decl.xml",
            regex:"\\?>",
            next:"start"
        }],

        doctype:[
            {include:"whitespace"},
            {include:"string"},
            {token:"xml-pe.doctype.xml",regex:">",next:"start"},
            {token:"xml-pe.xml",regex:"[-_a-zA-Z0-9:]+"},
            {token:"punctuation.int-subset",regex:"\\[",push:"int_subset"}
        ],

        int_subset:[{
            token:"text.xml",
            regex:"\\s+"
        },{
            token:"punctuation.int-subset.xml",
            regex:"]",
            next:"pop"
        },{
            token:["punctuation.markup-decl.xml","keyword.markup-decl.xml"],
            regex:"(<\\!)("+tagRegex+")",
            push:[{
                token:"text",
                regex:"\\s+"
            },
            {
                token:"punctuation.markup-decl.xml",
                regex:">",
                next:"pop"
            },
            {include:"string"}]
        }],

        cdata:[
            {token:"string.cdata.xml",regex:"\\]\\]>",next:"start"},
            {token:"text.xml",regex:"\\s+"},
            {token:"text.xml",regex:"(?:[^\\]]|\\](?!\\]>))+"}
        ],

        comment:[
            {token:"comment.end.xml",regex:"-->",next:"start"},
            {defaultToken:"comment.xml"}
        ],

        reference:[{
            token:"constant.language.escape.reference.xml",
            regex:"(?:&#[0-9]+;)|(?:&#x[0-9a-fA-F]+;)|(?:&[a-zA-Z0-9_:\\.-]+;)"
        }],

        attr_reference:[{
            token:"constant.language.escape.reference.attribute-value.xml",
            regex:"(?:&#[0-9]+;)|(?:&#x[0-9a-fA-F]+;)|(?:&[a-zA-Z0-9_:\\.-]+;)"
        }],

        tag:[{
            token:["meta.tag.punctuation.tag-open.xml","meta.tag.punctuation.end-tag-open.xml","meta.tag.tag-name.xml"],
            regex:"(?:(<)|(</))((?:"+tagRegex+":)?"+tagRegex+")",
            next:[
                {include:"attributes"},
                {token:"meta.tag.punctuation.tag-close.xml",regex:"/?>",next:"start"}
            ]
        }],

        tag_whitespace:[
            {token:"text.tag-whitespace.xml",regex:"\\s+"}
        ],
        whitespace:[
            {token:"text.whitespace.xml",regex:"\\s+"}
        ],
        string:[{
            token:"string.xml",
            regex:"'",
            push:[
                {token:"string.xml",regex:"'",next:"pop"},
                {defaultToken:"string.xml"}
            ]
        },{
            token:"string.xml",
            regex:'"',
            push:[
                {token:"string.xml",regex:'"',next:"pop"},
                {defaultToken:"string.xml"}
            ]
        }],

        attributes:[{
            token:"entity.other.attribute-name.xml",
            regex:tagRegex
        },{
            token:"keyword.operator.attribute-equals.xml",
            regex:"="
        },{
            include:"tag_whitespace"
        },{
            include:"attribute_value"
        }],

        attribute_value:[{
            token:"string.attribute-value.xml",
            regex:"'",
            push:[
                {token:"string.attribute-value.xml",regex:"'",next:"pop"},
                {include:"attr_reference"},
                {defaultToken:"string.attribute-value.xml"}
            ]
        },{
            token:"string.attribute-value.xml",
            regex:'"',
            push:[
                {token:"string.attribute-value.xml",regex:'"',next:"pop"},
                {include:"attr_reference"},
                {defaultToken:"string.attribute-value.xml"}
            ]
        }]
    };

    if(this.constructor===XmlHighlightRules)
        this.normalizeRules();
};


(function(){

    this.embedTagRules=function(HighlightRules,prefix,tag){
        this.$rules.tag.unshift({
            token:["meta.tag.punctuation.tag-open.xml","meta.tag."+tag+".tag-name.xml"],
            regex:"(<)("+tag+"(?=\\s|>|$))",
            next:[
                {include:"attributes"},
                {token:"meta.tag.punctuation.tag-close.xml",regex:"/?>",next:prefix+"start"}
            ]
        });

        this.$rules[tag+"-end"]=[
            {include:"attributes"},
            {token:"meta.tag.punctuation.tag-close.xml",regex:"/?>", next:"start",
                onMatch:function(value,currentState,stack){
                    stack.splice(0);
                    returnthis.token;
            }}
        ];

        this.embedRules(HighlightRules,prefix,[{
            token:["meta.tag.punctuation.end-tag-open.xml","meta.tag."+tag+".tag-name.xml"],
            regex:"(</)("+tag+"(?=\\s|>|$))",
            next:tag+"-end"
        },{
            token:"string.cdata.xml",
            regex:"<\\!\\[CDATA\\["
        },{
            token:"string.cdata.xml",
            regex:"\\]\\]>"
        }]);
    };

}).call(TextHighlightRules.prototype);

oop.inherits(XmlHighlightRules,TextHighlightRules);

exports.XmlHighlightRules=XmlHighlightRules;
});

define("ace/mode/behaviour/xml",["require","exports","module","ace/lib/oop","ace/mode/behaviour","ace/token_iterator","ace/lib/lang"],function(require,exports,module){
"usestrict";

varoop=require("../../lib/oop");
varBehaviour=require("../behaviour").Behaviour;
varTokenIterator=require("../../token_iterator").TokenIterator;
varlang=require("../../lib/lang");

functionis(token,type){
    returntoken&&token.type.lastIndexOf(type+".xml")>-1;
}

varXmlBehaviour=function(){

    this.add("string_dquotes","insertion",function(state,action,editor,session,text){
        if(text=='"'||text=="'"){
            varquote=text;
            varselected=session.doc.getTextRange(editor.getSelectionRange());
            if(selected!==""&&selected!=="'"&&selected!='"'&&editor.getWrapBehavioursEnabled()){
                return{
                    text:quote+selected+quote,
                    selection:false
                };
            }

            varcursor=editor.getCursorPosition();
            varline=session.doc.getLine(cursor.row);
            varrightChar=line.substring(cursor.column,cursor.column+1);
            variterator=newTokenIterator(session,cursor.row,cursor.column);
            vartoken=iterator.getCurrentToken();

            if(rightChar==quote&&(is(token,"attribute-value")||is(token,"string"))){
                return{
                    text:"",
                    selection:[1,1]
                };
            }

            if(!token)
                token=iterator.stepBackward();

            if(!token)
                return;

            while(is(token,"tag-whitespace")||is(token,"whitespace")){
                token=iterator.stepBackward();
            }
            varrightSpace=!rightChar||rightChar.match(/\s/);
            if(is(token,"attribute-equals")&&(rightSpace||rightChar=='>')||(is(token,"decl-attribute-equals")&&(rightSpace||rightChar=='?'))){
                return{
                    text:quote+quote,
                    selection:[1,1]
                };
            }
        }
    });

    this.add("string_dquotes","deletion",function(state,action,editor,session,range){
        varselected=session.doc.getTextRange(range);
        if(!range.isMultiLine()&&(selected=='"'||selected=="'")){
            varline=session.doc.getLine(range.start.row);
            varrightChar=line.substring(range.start.column+1,range.start.column+2);
            if(rightChar==selected){
                range.end.column++;
                returnrange;
            }
        }
    });

    this.add("autoclosing","insertion",function(state,action,editor,session,text){
        if(text=='>'){
            varposition=editor.getSelectionRange().start;
            variterator=newTokenIterator(session,position.row,position.column);
            vartoken=iterator.getCurrentToken()||iterator.stepBackward();
            if(!token||!(is(token,"tag-name")||is(token,"tag-whitespace")||is(token,"attribute-name")||is(token,"attribute-equals")||is(token,"attribute-value")))
                return;
            if(is(token,"reference.attribute-value"))
                return;
            if(is(token,"attribute-value")){
                vartokenEndColumn=iterator.getCurrentTokenColumn()+token.value.length;
                if(position.column<tokenEndColumn)
                    return;
                if(position.column==tokenEndColumn){
                    varnextToken=iterator.stepForward();
                    //TODOalsohandlenon-closedstringattheendoftheline
                    if(nextToken&&is(nextToken,"attribute-value"))
                        return;
                    iterator.stepBackward();
                }
            }

            if(/^\s*>/.test(session.getLine(position.row).slice(position.column)))
                return;
            while(!is(token,"tag-name")){
                token=iterator.stepBackward();
                if(token.value=="<"){
                    token=iterator.stepForward();
                    break;
                }
            }

            vartokenRow=iterator.getCurrentTokenRow();
            vartokenColumn=iterator.getCurrentTokenColumn();
            if(is(iterator.stepBackward(),"end-tag-open"))
                return;

            varelement=token.value;
            if(tokenRow==position.row)
                element=element.substring(0,position.column-tokenColumn);

            if(this.voidElements.hasOwnProperty(element.toLowerCase()))
                 return;

            return{
               text:">"+"</"+element+">",
               selection:[1,1]
            };
        }
    });

    this.add("autoindent","insertion",function(state,action,editor,session,text){
        if(text=="\n"){
            varcursor=editor.getCursorPosition();
            varline=session.getLine(cursor.row);
            variterator=newTokenIterator(session,cursor.row,cursor.column);
            vartoken=iterator.getCurrentToken();

            if(token&&token.type.indexOf("tag-close")!==-1){
                if(token.value=="/>")
                    return;
                while(token&&token.type.indexOf("tag-name")===-1){
                    token=iterator.stepBackward();
                }

                if(!token){
                    return;
                }

                vartag=token.value;
                varrow=iterator.getCurrentTokenRow();
                token=iterator.stepBackward();
                if(!token||token.type.indexOf("end-tag")!==-1){
                    return;
                }

                if(this.voidElements&&!this.voidElements[tag]){
                    varnextToken=session.getTokenAt(cursor.row,cursor.column+1);
                    varline=session.getLine(row);
                    varnextIndent=this.$getIndent(line);
                    varindent=nextIndent+session.getTabString();

                    if(nextToken&&nextToken.value==="</"){
                        return{
                            text:"\n"+indent+"\n"+nextIndent,
                            selection:[1,indent.length,1,indent.length]
                        };
                    }else{
                        return{
                            text:"\n"+indent
                        };
                    }
                }
            }
        }
    });

};

oop.inherits(XmlBehaviour,Behaviour);

exports.XmlBehaviour=XmlBehaviour;
});

define("ace/mode/folding/xml",["require","exports","module","ace/lib/oop","ace/lib/lang","ace/range","ace/mode/folding/fold_mode","ace/token_iterator"],function(require,exports,module){
"usestrict";

varoop=require("../../lib/oop");
varlang=require("../../lib/lang");
varRange=require("../../range").Range;
varBaseFoldMode=require("./fold_mode").FoldMode;
varTokenIterator=require("../../token_iterator").TokenIterator;

varFoldMode=exports.FoldMode=function(voidElements,optionalEndTags){
    BaseFoldMode.call(this);
    this.voidElements=voidElements||{};
    this.optionalEndTags=oop.mixin({},this.voidElements);
    if(optionalEndTags)
        oop.mixin(this.optionalEndTags,optionalEndTags);
    
};
oop.inherits(FoldMode,BaseFoldMode);

varTag=function(){
    this.tagName="";
    this.closing=false;
    this.selfClosing=false;
    this.start={row:0,column:0};
    this.end={row:0,column:0};
};

functionis(token,type){
    returntoken.type.lastIndexOf(type+".xml")>-1;
}

(function(){

    this.getFoldWidget=function(session,foldStyle,row){
        vartag=this._getFirstTagInLine(session,row);

        if(!tag)
            returnthis.getCommentFoldWidget(session,row);

        if(tag.closing||(!tag.tagName&&tag.selfClosing))
            returnfoldStyle=="markbeginend"?"end":"";

        if(!tag.tagName||tag.selfClosing||this.voidElements.hasOwnProperty(tag.tagName.toLowerCase()))
            return"";

        if(this._findEndTagInLine(session,row,tag.tagName,tag.end.column))
            return"";

        return"start";
    };
    
    this.getCommentFoldWidget=function(session,row){
        if(/comment/.test(session.getState(row))&&/<!-/.test(session.getLine(row)))
            return"start";
        return"";
    };
    this._getFirstTagInLine=function(session,row){
        vartokens=session.getTokens(row);
        vartag=newTag();

        for(vari=0;i<tokens.length;i++){
            vartoken=tokens[i];
            if(is(token,"tag-open")){
                tag.end.column=tag.start.column+token.value.length;
                tag.closing=is(token,"end-tag-open");
                token=tokens[++i];
                if(!token)
                    returnnull;
                tag.tagName=token.value;
                tag.end.column+=token.value.length;
                for(i++;i<tokens.length;i++){
                    token=tokens[i];
                    tag.end.column+=token.value.length;
                    if(is(token,"tag-close")){
                        tag.selfClosing=token.value=='/>';
                        break;
                    }
                }
                returntag;
            }elseif(is(token,"tag-close")){
                tag.selfClosing=token.value=='/>';
                returntag;
            }
            tag.start.column+=token.value.length;
        }

        returnnull;
    };

    this._findEndTagInLine=function(session,row,tagName,startColumn){
        vartokens=session.getTokens(row);
        varcolumn=0;
        for(vari=0;i<tokens.length;i++){
            vartoken=tokens[i];
            column+=token.value.length;
            if(column<startColumn)
                continue;
            if(is(token,"end-tag-open")){
                token=tokens[i+1];
                if(token&&token.value==tagName)
                    returntrue;
            }
        }
        returnfalse;
    };
    this._readTagForward=function(iterator){
        vartoken=iterator.getCurrentToken();
        if(!token)
            returnnull;

        vartag=newTag();
        do{
            if(is(token,"tag-open")){
                tag.closing=is(token,"end-tag-open");
                tag.start.row=iterator.getCurrentTokenRow();
                tag.start.column=iterator.getCurrentTokenColumn();
            }elseif(is(token,"tag-name")){
                tag.tagName=token.value;
            }elseif(is(token,"tag-close")){
                tag.selfClosing=token.value=="/>";
                tag.end.row=iterator.getCurrentTokenRow();
                tag.end.column=iterator.getCurrentTokenColumn()+token.value.length;
                iterator.stepForward();
                returntag;
            }
        }while(token=iterator.stepForward());

        returnnull;
    };
    
    this._readTagBackward=function(iterator){
        vartoken=iterator.getCurrentToken();
        if(!token)
            returnnull;

        vartag=newTag();
        do{
            if(is(token,"tag-open")){
                tag.closing=is(token,"end-tag-open");
                tag.start.row=iterator.getCurrentTokenRow();
                tag.start.column=iterator.getCurrentTokenColumn();
                iterator.stepBackward();
                returntag;
            }elseif(is(token,"tag-name")){
                tag.tagName=token.value;
            }elseif(is(token,"tag-close")){
                tag.selfClosing=token.value=="/>";
                tag.end.row=iterator.getCurrentTokenRow();
                tag.end.column=iterator.getCurrentTokenColumn()+token.value.length;
            }
        }while(token=iterator.stepBackward());

        returnnull;
    };
    
    this._pop=function(stack,tag){
        while(stack.length){
            
            vartop=stack[stack.length-1];
            if(!tag||top.tagName==tag.tagName){
                returnstack.pop();
            }
            elseif(this.optionalEndTags.hasOwnProperty(top.tagName)){
                stack.pop();
                continue;
            }else{
                returnnull;
            }
        }
    };
    
    this.getFoldWidgetRange=function(session,foldStyle,row){
        varfirstTag=this._getFirstTagInLine(session,row);
        
        if(!firstTag){
            returnthis.getCommentFoldWidget(session,row)
                &&session.getCommentFoldRange(row,session.getLine(row).length);
        }
        
        varisBackward=firstTag.closing||firstTag.selfClosing;
        varstack=[];
        vartag;
        
        if(!isBackward){
            variterator=newTokenIterator(session,row,firstTag.start.column);
            varstart={
                row:row,
                column:firstTag.start.column+firstTag.tagName.length+2
            };
            if(firstTag.start.row==firstTag.end.row)
                start.column=firstTag.end.column;
            while(tag=this._readTagForward(iterator)){
                if(tag.selfClosing){
                    if(!stack.length){
                        tag.start.column+=tag.tagName.length+2;
                        tag.end.column-=2;
                        returnRange.fromPoints(tag.start,tag.end);
                    }else
                        continue;
                }
                
                if(tag.closing){
                    this._pop(stack,tag);
                    if(stack.length==0)
                        returnRange.fromPoints(start,tag.start);
                }
                else{
                    stack.push(tag);
                }
            }
        }
        else{
            variterator=newTokenIterator(session,row,firstTag.end.column);
            varend={
                row:row,
                column:firstTag.start.column
            };
            
            while(tag=this._readTagBackward(iterator)){
                if(tag.selfClosing){
                    if(!stack.length){
                        tag.start.column+=tag.tagName.length+2;
                        tag.end.column-=2;
                        returnRange.fromPoints(tag.start,tag.end);
                    }else
                        continue;
                }
                
                if(!tag.closing){
                    this._pop(stack,tag);
                    if(stack.length==0){
                        tag.start.column+=tag.tagName.length+2;
                        if(tag.start.row==tag.end.row&&tag.start.column<tag.end.column)
                            tag.start.column=tag.end.column;
                        returnRange.fromPoints(tag.start,end);
                    }
                }
                else{
                    stack.push(tag);
                }
            }
        }
        
    };

}).call(FoldMode.prototype);

});

define("ace/mode/xml",["require","exports","module","ace/lib/oop","ace/lib/lang","ace/mode/text","ace/mode/xml_highlight_rules","ace/mode/behaviour/xml","ace/mode/folding/xml","ace/worker/worker_client"],function(require,exports,module){
"usestrict";

varoop=require("../lib/oop");
varlang=require("../lib/lang");
varTextMode=require("./text").Mode;
varXmlHighlightRules=require("./xml_highlight_rules").XmlHighlightRules;
varXmlBehaviour=require("./behaviour/xml").XmlBehaviour;
varXmlFoldMode=require("./folding/xml").FoldMode;
varWorkerClient=require("../worker/worker_client").WorkerClient;

varMode=function(){
   this.HighlightRules=XmlHighlightRules;
   this.$behaviour=newXmlBehaviour();
   this.foldingRules=newXmlFoldMode();
};

oop.inherits(Mode,TextMode);

(function(){

    this.voidElements=lang.arrayToMap([]);

    this.blockComment={start:"<!--",end:"-->"};

    this.createWorker=function(session){
        varworker=newWorkerClient(["ace"],"ace/mode/xml_worker","Worker");
        worker.attachToDocument(session.getDocument());

        worker.on("error",function(e){
            session.setAnnotations(e.data);
        });

        worker.on("terminate",function(){
            session.clearAnnotations();
        });

        returnworker;
    };
    
    this.$id="ace/mode/xml";
}).call(Mode.prototype);

exports.Mode=Mode;
});
