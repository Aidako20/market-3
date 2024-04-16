flectra.define('mail.utils',function(require){
"usestrict";

varcore=require('web.core');

var_t=core._t;

/**
 *WARNING:thisisnotenoughtounescapepotentialXSScontainedinhtmlString,transformFunction
 *shouldhandleitoritshouldbehandledafter/beforecallingparseAndTransform.Soiftheresult
 *ofthisfunctionisusedinat-raw,beverycareful.
 *
 *@param{string}htmlString
 *@param{function}transformFunction
 *@returns{string}
 */
functionparseAndTransform(htmlString,transformFunction){
    varopenToken="OPEN"+Date.now();
    varstring=htmlString.replace(/&lt;/g,openToken);
    varchildren;
    try{
        children=$('<div>').html(string).contents();
    }catch(e){
        children=$('<div>').html('<pre>'+string+'</pre>').contents();
    }
    return_parseAndTransform(children,transformFunction)
                .replace(newRegExp(openToken,"g"),"&lt;");
}

/**
 *@param{Node[]}nodes
 *@param{function}transformFunctionwith:
 *  paramnode
 *  paramfunction
 *  returnstring
 *@return{string}
 */
function_parseAndTransform(nodes,transformFunction){
    return_.map(nodes,function(node){
        returntransformFunction(node,function(){
            return_parseAndTransform(node.childNodes,transformFunction);
        });
    }).join("");
}

/**
 *Escape<>&ashtmlentities(copyfrom_.escapewithlessescapedcharacters)
 *
 *@param{string}
 *@return{string}
 */
var_escapeEntities=(function(){
    varmap={"&":"&amp;","<":"&lt;",">":"&gt;"};
    varescaper=function(match){
        returnmap[match];
    };
    vartestRegexp=RegExp('(?:&|<|>)');
    varreplaceRegexp=RegExp('(?:&|<|>)','g');
    returnfunction(string){
        string=string==null?'':''+string;
        returntestRegexp.test(string)?string.replace(replaceRegexp,escaper):string;
    };
})();

//SuggestedURLJavascriptregexofhttp://stackoverflow.com/questions/3809401/what-is-a-good-regular-expression-to-match-a-url
//Adaptedtomakehttp(s)://notrequiredif(andonlyif)www.isgiven.So`should.notmatch`doesnotmatch.
//AndfurtherextendedtoincludeLatin-1Supplement,LatinExtended-A,LatinExtended-BandLatinExtendedAdditional.
varurlRegexp=/\b(?:https?:\/\/\d{1,3}(?:\.\d{1,3}){3}|(?:https?:\/\/|(?:www\.))[-a-z0-9@:%._+~#=\u00C0-\u024F\u1E00-\u1EFF]{2,256}\.[a-z]{2,13})\b(?:[-a-z0-9@:%_+.~#?&'$//=;\u00C0-\u024F\u1E00-\u1EFF]*)/gi;
/**
 *@param{string}text
 *@param{Object}[attrs={}]
 *@return{string}linkifiedtext
 */
functionlinkify(text,attrs){
    attrs=attrs||{};
    if(attrs.target===undefined){
        attrs.target='_blank';
    }
    if(attrs.target==='_blank'){
      attrs.rel='noreferrernoopener';
    }
    attrs=_.map(attrs,function(value,key){
        returnkey+'="'+_.escape(value)+'"';
    }).join('');
    varcurIndex=0;
    varresult="";
    varmatch;
    while((match=urlRegexp.exec(text))!==null){
        result+=_escapeEntities(text.slice(curIndex,match.index));
        varurl=match[0];
        varhref=(!/^https?:\/\//i.test(url))?"http://"+_.escape(url):_.escape(url);
        result+='<a'+attrs+'href="'+href+'">'+_escapeEntities(url)+'</a>';
        curIndex=match.index+match[0].length;
    }
    returnresult+_escapeEntities(text.slice(curIndex));
}

functionaddLink(node,transformChildren){
    if(node.nodeType===3){ //textnode
        constlinkified=linkify(node.data);
        if(linkified!==node.data){
            constdiv=document.createElement('div');
            div.innerHTML=linkified;
            for(constchildNodeof[...div.childNodes]){
                node.parentNode.insertBefore(childNode,node);
            }
            node.parentNode.removeChild(node);
            returnlinkified;
        }
        returnnode.textContent;
    }
    if(node.tagName==="A")returnnode.outerHTML;
    transformChildren();
    returnnode.outerHTML;
}

/**
 *@param{string}htmlString
 *@return{string}
 */
functionhtmlToTextContentInline(htmlString){
    constfragment=document.createDocumentFragment();
    constdiv=document.createElement('div');
    fragment.appendChild(div);
    htmlString=htmlString.replace(/<br\s*\/?>/gi,'');
    try{
        div.innerHTML=htmlString;
    }catch(e){
        div.innerHTML=`<pre>${htmlString}</pre>`;
    }
    returndiv
        .textContent
        .trim()
        .replace(/[\n\r]/g,'')
        .replace(/\s\s+/g,'');
}

functionstripHTML(node,transformChildren){
    if(node.nodeType===3)returnnode.data; //textnode
    if(node.tagName==="BR")return"\n";
    returntransformChildren();
}

functioninline(node,transform_children){
    if(node.nodeType===3)returnnode.data;
    if(node.nodeType===8)return"";
    if(node.tagName==="BR")return"";
    if(node.tagName.match(/^(A|P|DIV|PRE|BLOCKQUOTE)$/))returntransform_children();
    node.innerHTML=transform_children();
    returnnode.outerHTML;
}

//Parsestexttofindemail:Tagada<address@mail.fr>->[Tagada,address@mail.fr]orFalse
functionparseEmail(text){
    if(text){
        varresult=text.match(/(.*)<(.*@.*)>/);
        if(result){
            name=_.str.trim(result[1]).replace(/(^"|"$)/g,'')
            return[name,_.str.trim(result[2])];
        }
        result=text.match(/(.*@.*)/);
        if(result){
            return[_.str.trim(result[1]),_.str.trim(result[1])];
        }
        return[text,false];
    }
}

/**
 *Returnsanescapedconversionofacontent.
 *
 *@param{string}content
 *@returns{string}
 */
functionescapeAndCompactTextContent(content){
    //Removingunwantedextraspacesfrommessage
    letvalue=owl.utils.escape(content).trim();
    value=value.replace(/(\r|\n){2,}/g,'<br/><br/>');
    value=value.replace(/(\r|\n)/g,'<br/>');

    //preventhtmlspacecollapsing
    value=value.replace(//g,'&nbsp;').replace(/([^>])&nbsp;([^<])/g,'$1$2');
    returnvalue;
}

//Replacestextareatextintohtmltext(add<p>,<a>)
//TDEnote:shouldbedoneserver-side,inPython->usemail.compose.message?
functiongetTextToHTML(text){
    returntext
        .replace(/((?:https?|ftp):\/\/[\S]+)/g,'<ahref="$1">$1</a>')
        .replace(/[\n\r]/g,'<br/>');
}

functiontimeFromNow(date){
    if(moment().diff(date,'seconds')<45){
        return_t("now");
    }
    returndate.fromNow();
}

return{
    addLink:addLink,
    getTextToHTML:getTextToHTML,
    htmlToTextContentInline,
    inline:inline,
    linkify:linkify,
    parseAndTransform:parseAndTransform,
    parseEmail:parseEmail,
    stripHTML:stripHTML,
    timeFromNow:timeFromNow,
    escapeAndCompactTextContent,
};

});
