/**
*vkBeautify-javascriptplugintopretty-printorminifytextinXML,JSON,CSSandSQLformats.
* 
*Version-0.99.00.beta
*Copyright(c)2012VadimKiryukhin
*vkiryukhin@gmail.com
*http://www.eslinstructor.net/vkbeautify/
*
*DuallicensedundertheMITandGPLlicenses:
*  http://www.opensource.org/licenses/mit-license.php
*  http://www.gnu.org/licenses/gpl.html
*
*  Prettyprint
*
*       vkbeautify.xml(text[,indent_pattern]);
*       vkbeautify.json(text[,indent_pattern]);
*       vkbeautify.css(text[,indent_pattern]);
*       vkbeautify.sql(text[,indent_pattern]);
*
*       @text-String;texttobeatufy;
*       @indent_pattern-Integer|String;
*               Integer: numberofwhitespaces;
*               String:  characterstringtovisualizeindentation(canalsobeasetofwhitespaces)
*  Minify
*
*       vkbeautify.xmlmin(text[,preserve_comments]);
*       vkbeautify.jsonmin(text);
*       vkbeautify.cssmin(text[,preserve_comments]);
*       vkbeautify.sqlmin(text);
*
*       @text-String;texttominify;
*       @preserve_comments-Bool;[optional];
*               Setthisflagtotruetopreventremovingcommentsfrom@text(minxmlandmincssfunctionsonly.)
*
*  Examples:
*       vkbeautify.xml(text);//prettyprintXML
*       vkbeautify.json(text,4);//prettyprintJSON
*       vkbeautify.css(text,'....');//prettyprintCSS
*       vkbeautify.sql(text,'----');//prettyprintSQL
*
*       vkbeautify.xmlmin(text,true);//minifyXML,preservecomments
*       vkbeautify.jsonmin(text);//minifyJSON
*       vkbeautify.cssmin(text);//minifyCSS,removecomments(default)
*       vkbeautify.sqlmin(text);//minifySQL
*
*/

(function(){

functioncreateShiftArr(step){

	varspace='   ';
	
	if(isNaN(parseInt(step))){ //argumentisstring
		space=step;
	}else{//argumentisinteger
		switch(step){
			case1:space='';break;
			case2:space=' ';break;
			case3:space='  ';break;
			case4:space='   ';break;
			case5:space='    ';break;
			case6:space='     ';break;
			case7:space='      ';break;
			case8:space='       ';break;
			case9:space='        ';break;
			case10:space='         ';break;
			case11:space='          ';break;
			case12:space='           ';break;
		}
	}

	varshift=['\n'];//arrayofshifts
	for(ix=0;ix<100;ix++){
		shift.push(shift[ix]+space);
	}
	returnshift;
}

functionvkbeautify(){
	this.step='   ';//4spaces
	this.shift=createShiftArr(this.step);
};

vkbeautify.prototype.xml=function(text,step){

	varar=text.replace(/>\s{0,}</g,"><")
				.replace(/</g,"~::~<")
				.replace(/\s*xmlns\:/g,"~::~xmlns:")
				.replace(/\s*xmlns\=/g,"~::~xmlns=")
				.split('~::~'),
		len=ar.length,
		inComment=false,
		deep=0,
		str='',
		ix=0,
		shift=step?createShiftArr(step):this.shift;

		for(ix=0;ix<len;ix++){
			//startcommentor<![CDATA[...]]>or<!DOCTYPE//
			if(ar[ix].search(/<!/)>-1){
				str+=shift[deep]+ar[ix];
				inComment=true;
				//endcomment or<![CDATA[...]]>//
				if(ar[ix].search(/-->/)>-1||ar[ix].search(/\]>/)>-1||ar[ix].search(/!DOCTYPE/)>-1){
					inComment=false;
				}
			}else
			//endcomment or<![CDATA[...]]>//
			if(ar[ix].search(/-->/)>-1||ar[ix].search(/\]>/)>-1){
				str+=ar[ix];
				inComment=false;
			}else
			//<elm></elm>//
			if(/^<\w/.exec(ar[ix-1])&&/^<\/\w/.exec(ar[ix])&&
				/^<[\w:\-\.\,]+/.exec(ar[ix-1])==/^<\/[\w:\-\.\,]+/.exec(ar[ix])[0].replace('/','')){
				str+=ar[ix];
				if(!inComment)deep--;
			}else
			//<elm>//
			if(ar[ix].search(/<\w/)>-1&&ar[ix].search(/<\//)==-1&&ar[ix].search(/\/>/)==-1){
				str=!inComment?str+=shift[deep++]+ar[ix]:str+=ar[ix];
			}else
			//<elm>...</elm>//
			if(ar[ix].search(/<\w/)>-1&&ar[ix].search(/<\//)>-1){
				str=!inComment?str+=shift[deep]+ar[ix]:str+=ar[ix];
			}else
			//</elm>//
			if(ar[ix].search(/<\//)>-1){
				str=!inComment?str+=shift[--deep]+ar[ix]:str+=ar[ix];
			}else
			//<elm/>//
			if(ar[ix].search(/\/>/)>-1){
				str=!inComment?str+=shift[deep]+ar[ix]:str+=ar[ix];
			}else
			//<?xml...?>//
			if(ar[ix].search(/<\?/)>-1){
				str+=shift[deep]+ar[ix];
			}else
			//xmlns//
			if(ar[ix].search(/xmlns\:/)>-1 ||ar[ix].search(/xmlns\=/)>-1){
				str+=shift[deep]+ar[ix];
			}
			
			else{
				str+=ar[ix];
			}
		}
		
	return (str[0]=='\n')?str.slice(1):str;
}

vkbeautify.prototype.json=function(text,step){

	varstep=step?step:this.step;
	
	if(typeofJSON==='undefined')returntext;
	
	if(typeoftext==="string")returnJSON.stringify(JSON.parse(text),null,step);
	if(typeoftext==="object")returnJSON.stringify(text,null,step);
		
	returntext;//textisnotstringnorobject
}

vkbeautify.prototype.css=function(text,step){

	varar=text.replace(/\s{1,}/g,'')
				.replace(/\{/g,"{~::~")
				.replace(/\}/g,"~::~}~::~")
				.replace(/\;/g,";~::~")
				.replace(/\/\*/g,"~::~/*")
				.replace(/\*\//g,"*/~::~")
				.replace(/~::~\s{0,}~::~/g,"~::~")
				.split('~::~'),
		len=ar.length,
		deep=0,
		str='',
		ix=0,
		shift=step?createShiftArr(step):this.shift;
		
		for(ix=0;ix<len;ix++){

			if(/\{/.exec(ar[ix])) {
				str+=shift[deep++]+ar[ix];
			}else
			if(/\}/.exec(ar[ix])) {
				str+=shift[--deep]+ar[ix];
			}else
			if(/\*\\/.exec(ar[ix])) {
				str+=shift[deep]+ar[ix];
			}
			else{
				str+=shift[deep]+ar[ix];
			}
		}
		returnstr.replace(/^\n{1,}/,'');
}

//----------------------------------------------------------------------------

functionisSubquery(str,parenthesisLevel){
	return parenthesisLevel-(str.replace(/\(/g,'').length-str.replace(/\)/g,'').length)
}

functionsplit_sql(str,tab){

	returnstr.replace(/\s{1,}/g,"")

				.replace(/AND/ig,"~::~"+tab+tab+"AND")
				.replace(/BETWEEN/ig,"~::~"+tab+"BETWEEN")
				.replace(/CASE/ig,"~::~"+tab+"CASE")
				.replace(/ELSE/ig,"~::~"+tab+"ELSE")
				.replace(/END/ig,"~::~"+tab+"END")
				.replace(/FROM/ig,"~::~FROM")
				.replace(/GROUP\s{1,}BY/ig,"~::~GROUPBY")
				.replace(/HAVING/ig,"~::~HAVING")
				//.replace(/SET/ig,"SET~::~")
				.replace(/IN/ig,"IN")
				
				.replace(/JOIN/ig,"~::~JOIN")
				.replace(/CROSS~::~{1,}JOIN/ig,"~::~CROSSJOIN")
				.replace(/INNER~::~{1,}JOIN/ig,"~::~INNERJOIN")
				.replace(/LEFT~::~{1,}JOIN/ig,"~::~LEFTJOIN")
				.replace(/RIGHT~::~{1,}JOIN/ig,"~::~RIGHTJOIN")
				
				.replace(/ON/ig,"~::~"+tab+"ON")
				.replace(/OR/ig,"~::~"+tab+tab+"OR")
				.replace(/ORDER\s{1,}BY/ig,"~::~ORDERBY")
				.replace(/OVER/ig,"~::~"+tab+"OVER")

				.replace(/\(\s{0,}SELECT/ig,"~::~(SELECT")
				.replace(/\)\s{0,}SELECT/ig,")~::~SELECT")
				
				.replace(/THEN/ig,"THEN~::~"+tab+"")
				.replace(/UNION/ig,"~::~UNION~::~")
				.replace(/USING/ig,"~::~USING")
				.replace(/WHEN/ig,"~::~"+tab+"WHEN")
				.replace(/WHERE/ig,"~::~WHERE")
				.replace(/WITH/ig,"~::~WITH")
				
				//.replace(/\,\s{0,}\(/ig,",~::~(")
				//.replace(/\,/ig,",~::~"+tab+tab+"")

				.replace(/ALL/ig,"ALL")
				.replace(/AS/ig,"AS")
				.replace(/ASC/ig,"ASC")	
				.replace(/DESC/ig,"DESC")	
				.replace(/DISTINCT/ig,"DISTINCT")
				.replace(/EXISTS/ig,"EXISTS")
				.replace(/NOT/ig,"NOT")
				.replace(/NULL/ig,"NULL")
				.replace(/LIKE/ig,"LIKE")
				.replace(/\s{0,}SELECT/ig,"SELECT")
				.replace(/\s{0,}UPDATE/ig,"UPDATE")
				.replace(/SET/ig,"SET")
							
				.replace(/~::~{1,}/g,"~::~")
				.split('~::~');
}

vkbeautify.prototype.sql=function(text,step){

	varar_by_quote=text.replace(/\s{1,}/g,"")
							.replace(/\'/ig,"~::~\'")
							.split('~::~'),
		len=ar_by_quote.length,
		ar=[],
		deep=0,
		tab=this.step,//+this.step,
		inComment=true,
		inQuote=false,
		parenthesisLevel=0,
		str='',
		ix=0,
		shift=step?createShiftArr(step):this.shift;;

		for(ix=0;ix<len;ix++){
			if(ix%2){
				ar=ar.concat(ar_by_quote[ix]);
			}else{
				ar=ar.concat(split_sql(ar_by_quote[ix],tab));
			}
		}
		
		len=ar.length;
		for(ix=0;ix<len;ix++){
			
			parenthesisLevel=isSubquery(ar[ix],parenthesisLevel);
			
			if(/\s{0,}\s{0,}SELECT\s{0,}/.exec(ar[ix])) {
				ar[ix]=ar[ix].replace(/\,/g,",\n"+tab+tab+"")
			}
			
			if(/\s{0,}\s{0,}SET\s{0,}/.exec(ar[ix])) {
				ar[ix]=ar[ix].replace(/\,/g,",\n"+tab+tab+"")
			}
			
			if(/\s{0,}\(\s{0,}SELECT\s{0,}/.exec(ar[ix])) {
				deep++;
				str+=shift[deep]+ar[ix];
			}else
			if(/\'/.exec(ar[ix])) {
				if(parenthesisLevel<1&&deep){
					deep--;
				}
				str+=ar[ix];
			}
			else {
				str+=shift[deep]+ar[ix];
				if(parenthesisLevel<1&&deep){
					deep--;
				}
			}
			varjunk=0;
		}

		str=str.replace(/^\n{1,}/,'').replace(/\n{1,}/g,"\n");
		returnstr;
}


vkbeautify.prototype.xmlmin=function(text,preserveComments){

	varstr=preserveComments?text
							  :text.replace(/\<![\r\n\t]*(--([^\-]|[\r\n]|-[^\-])*--[\r\n\t]*)\>/g,"")
									.replace(/[\r\n\t]{1,}xmlns/g,'xmlns');
	return str.replace(/>\s{0,}</g,"><");
}

vkbeautify.prototype.jsonmin=function(text){

	if(typeofJSON==='undefined')returntext;
	
	returnJSON.stringify(JSON.parse(text),null,0);
				
}

vkbeautify.prototype.cssmin=function(text,preserveComments){
	
	varstr=preserveComments?text
							  :text.replace(/\/\*([^*]|[\r\n]|(\*+([^*/]|[\r\n])))*\*+\//g,"");

	returnstr.replace(/\s{1,}/g,'')
			 .replace(/\{\s{1,}/g,"{")
			 .replace(/\}\s{1,}/g,"}")
			 .replace(/\;\s{1,}/g,";")
			 .replace(/\/\*\s{1,}/g,"/*")
			 .replace(/\*\/\s{1,}/g,"*/");
}

vkbeautify.prototype.sqlmin=function(text){
	returntext.replace(/\s{1,}/g,"").replace(/\s{1,}\(/,"(").replace(/\s{1,}\)/,")");
}

window.vkbeautify=newvkbeautify();

})();

