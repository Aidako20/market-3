/**
 *@licstartThefollowingistheentirelicensenoticeforthe
 *Javascriptcodeinthispage
 *
 *Copyright2019MozillaFoundation
 *
 *LicensedundertheApacheLicense,Version2.0(the"License");
 *youmaynotusethisfileexceptincompliancewiththeLicense.
 *YoumayobtainacopyoftheLicenseat
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 *Unlessrequiredbyapplicablelaworagreedtoinwriting,software
 *distributedundertheLicenseisdistributedonan"ASIS"BASIS,
 *WITHOUTWARRANTIESORCONDITIONSOFANYKIND,eitherexpressorimplied.
 *SeetheLicenseforthespecificlanguagegoverningpermissionsand
 *limitationsundertheLicense.
 *
 *@licendTheaboveistheentirelicensenoticeforthe
 *Javascriptcodeinthispage
 */

(functionwebpackUniversalModuleDefinition(root,factory){
	if(typeofexports==='object'&&typeofmodule==='object')
		module.exports=factory();
	elseif(typeofdefine==='function'&&define.amd)
		define("pdfjs-dist/build/pdf",[],factory);
	elseif(typeofexports==='object')
		exports["pdfjs-dist/build/pdf"]=factory();
	else
		root["pdfjs-dist/build/pdf"]=root.pdfjsLib=factory();
})(this,function(){
return/******/(function(modules){//webpackBootstrap
/******/	//Themodulecache
/******/	varinstalledModules={};
/******/
/******/	//Therequirefunction
/******/	function__w_pdfjs_require__(moduleId){
/******/
/******/		//Checkifmoduleisincache
/******/		if(installedModules[moduleId]){
/******/			returninstalledModules[moduleId].exports;
/******/		}
/******/		//Createanewmodule(andputitintothecache)
/******/		varmodule=installedModules[moduleId]={
/******/			i:moduleId,
/******/			l:false,
/******/			exports:{}
/******/		};
/******/
/******/		//Executethemodulefunction
/******/		modules[moduleId].call(module.exports,module,module.exports,__w_pdfjs_require__);
/******/
/******/		//Flagthemoduleasloaded
/******/		module.l=true;
/******/
/******/		//Returntheexportsofthemodule
/******/		returnmodule.exports;
/******/	}
/******/
/******/
/******/	//exposethemodulesobject(__webpack_modules__)
/******/	__w_pdfjs_require__.m=modules;
/******/
/******/	//exposethemodulecache
/******/	__w_pdfjs_require__.c=installedModules;
/******/
/******/	//definegetterfunctionforharmonyexports
/******/	__w_pdfjs_require__.d=function(exports,name,getter){
/******/		if(!__w_pdfjs_require__.o(exports,name)){
/******/			Object.defineProperty(exports,name,{enumerable:true,get:getter});
/******/		}
/******/	};
/******/
/******/	//define__esModuleonexports
/******/	__w_pdfjs_require__.r=function(exports){
/******/		if(typeofSymbol!=='undefined'&&Symbol.toStringTag){
/******/			Object.defineProperty(exports,Symbol.toStringTag,{value:'Module'});
/******/		}
/******/		Object.defineProperty(exports,'__esModule',{value:true});
/******/	};
/******/
/******/	//createafakenamespaceobject
/******/	//mode&1:valueisamoduleid,requireit
/******/	//mode&2:mergeallpropertiesofvalueintothens
/******/	//mode&4:returnvaluewhenalreadynsobject
/******/	//mode&8|1:behavelikerequire
/******/	__w_pdfjs_require__.t=function(value,mode){
/******/		if(mode&1)value=__w_pdfjs_require__(value);
/******/		if(mode&8)returnvalue;
/******/		if((mode&4)&&typeofvalue==='object'&&value&&value.__esModule)returnvalue;
/******/		varns=Object.create(null);
/******/		__w_pdfjs_require__.r(ns);
/******/		Object.defineProperty(ns,'default',{enumerable:true,value:value});
/******/		if(mode&2&&typeofvalue!='string')for(varkeyinvalue)__w_pdfjs_require__.d(ns,key,function(key){returnvalue[key];}.bind(null,key));
/******/		returnns;
/******/	};
/******/
/******/	//getDefaultExportfunctionforcompatibilitywithnon-harmonymodules
/******/	__w_pdfjs_require__.n=function(module){
/******/		vargetter=module&&module.__esModule?
/******/			functiongetDefault(){returnmodule['default'];}:
/******/			functiongetModuleExports(){returnmodule;};
/******/		__w_pdfjs_require__.d(getter,'a',getter);
/******/		returngetter;
/******/	};
/******/
/******/	//Object.prototype.hasOwnProperty.call
/******/	__w_pdfjs_require__.o=function(object,property){returnObject.prototype.hasOwnProperty.call(object,property);};
/******/
/******/	//__webpack_public_path__
/******/	__w_pdfjs_require__.p="";
/******/
/******/
/******/	//Loadentrymoduleandreturnexports
/******/	return__w_pdfjs_require__(__w_pdfjs_require__.s=0);
/******/})
/************************************************************************/
/******/([
/*0*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varpdfjsVersion='2.2.228';
varpdfjsBuild='d7afb74a';

varpdfjsSharedUtil=__w_pdfjs_require__(1);

varpdfjsDisplayAPI=__w_pdfjs_require__(147);

varpdfjsDisplayTextLayer=__w_pdfjs_require__(162);

varpdfjsDisplayAnnotationLayer=__w_pdfjs_require__(163);

varpdfjsDisplayDisplayUtils=__w_pdfjs_require__(151);

varpdfjsDisplaySVG=__w_pdfjs_require__(164);

varpdfjsDisplayWorkerOptions=__w_pdfjs_require__(156);

varpdfjsDisplayAPICompatibility=__w_pdfjs_require__(153);

{
  varisNodeJS=__w_pdfjs_require__(4);

  if(isNodeJS()){
    varPDFNodeStream=__w_pdfjs_require__(165).PDFNodeStream;

    pdfjsDisplayAPI.setPDFNetworkStreamFactory(function(params){
      returnnewPDFNodeStream(params);
    });
  }else{
    varPDFNetworkStream=__w_pdfjs_require__(168).PDFNetworkStream;

    varPDFFetchStream;

    if(pdfjsDisplayDisplayUtils.isFetchSupported()){
      PDFFetchStream=__w_pdfjs_require__(169).PDFFetchStream;
    }

    pdfjsDisplayAPI.setPDFNetworkStreamFactory(function(params){
      if(PDFFetchStream&&pdfjsDisplayDisplayUtils.isValidFetchUrl(params.url)){
        returnnewPDFFetchStream(params);
      }

      returnnewPDFNetworkStream(params);
    });
  }
}
exports.build=pdfjsDisplayAPI.build;
exports.version=pdfjsDisplayAPI.version;
exports.getDocument=pdfjsDisplayAPI.getDocument;
exports.LoopbackPort=pdfjsDisplayAPI.LoopbackPort;
exports.PDFDataRangeTransport=pdfjsDisplayAPI.PDFDataRangeTransport;
exports.PDFWorker=pdfjsDisplayAPI.PDFWorker;
exports.renderTextLayer=pdfjsDisplayTextLayer.renderTextLayer;
exports.AnnotationLayer=pdfjsDisplayAnnotationLayer.AnnotationLayer;
exports.createPromiseCapability=pdfjsSharedUtil.createPromiseCapability;
exports.PasswordResponses=pdfjsSharedUtil.PasswordResponses;
exports.InvalidPDFException=pdfjsSharedUtil.InvalidPDFException;
exports.MissingPDFException=pdfjsSharedUtil.MissingPDFException;
exports.SVGGraphics=pdfjsDisplaySVG.SVGGraphics;
exports.NativeImageDecoding=pdfjsSharedUtil.NativeImageDecoding;
exports.CMapCompressionType=pdfjsSharedUtil.CMapCompressionType;
exports.PermissionFlag=pdfjsSharedUtil.PermissionFlag;
exports.UnexpectedResponseException=pdfjsSharedUtil.UnexpectedResponseException;
exports.OPS=pdfjsSharedUtil.OPS;
exports.VerbosityLevel=pdfjsSharedUtil.VerbosityLevel;
exports.UNSUPPORTED_FEATURES=pdfjsSharedUtil.UNSUPPORTED_FEATURES;
exports.createValidAbsoluteUrl=pdfjsSharedUtil.createValidAbsoluteUrl;
exports.createObjectURL=pdfjsSharedUtil.createObjectURL;
exports.removeNullCharacters=pdfjsSharedUtil.removeNullCharacters;
exports.shadow=pdfjsSharedUtil.shadow;
exports.Util=pdfjsSharedUtil.Util;
exports.ReadableStream=pdfjsSharedUtil.ReadableStream;
exports.URL=pdfjsSharedUtil.URL;
exports.RenderingCancelledException=pdfjsDisplayDisplayUtils.RenderingCancelledException;
exports.getFilenameFromUrl=pdfjsDisplayDisplayUtils.getFilenameFromUrl;
exports.LinkTarget=pdfjsDisplayDisplayUtils.LinkTarget;
exports.addLinkAttributes=pdfjsDisplayDisplayUtils.addLinkAttributes;
exports.loadScript=pdfjsDisplayDisplayUtils.loadScript;
exports.PDFDateString=pdfjsDisplayDisplayUtils.PDFDateString;
exports.GlobalWorkerOptions=pdfjsDisplayWorkerOptions.GlobalWorkerOptions;
exports.apiCompatibilityParams=pdfjsDisplayAPICompatibility.apiCompatibilityParams;

/***/}),
/*1*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.arrayByteLength=arrayByteLength;
exports.arraysToBytes=arraysToBytes;
exports.assert=assert;
exports.bytesToString=bytesToString;
exports.createPromiseCapability=createPromiseCapability;
exports.getVerbosityLevel=getVerbosityLevel;
exports.info=info;
exports.isArrayBuffer=isArrayBuffer;
exports.isArrayEqual=isArrayEqual;
exports.isBool=isBool;
exports.isEmptyObj=isEmptyObj;
exports.isNum=isNum;
exports.isString=isString;
exports.isSpace=isSpace;
exports.isSameOrigin=isSameOrigin;
exports.createValidAbsoluteUrl=createValidAbsoluteUrl;
exports.isLittleEndian=isLittleEndian;
exports.isEvalSupported=isEvalSupported;
exports.log2=log2;
exports.readInt8=readInt8;
exports.readUint16=readUint16;
exports.readUint32=readUint32;
exports.removeNullCharacters=removeNullCharacters;
exports.setVerbosityLevel=setVerbosityLevel;
exports.shadow=shadow;
exports.string32=string32;
exports.stringToBytes=stringToBytes;
exports.stringToPDFString=stringToPDFString;
exports.stringToUTF8String=stringToUTF8String;
exports.utf8StringToString=utf8StringToString;
exports.warn=warn;
exports.unreachable=unreachable;
Object.defineProperty(exports,"ReadableStream",{
  enumerable:true,
  get:functionget(){
    return_streams_polyfill.ReadableStream;
  }
});
Object.defineProperty(exports,"URL",{
  enumerable:true,
  get:functionget(){
    return_url_polyfill.URL;
  }
});
exports.createObjectURL=exports.FormatError=exports.Util=exports.UnknownErrorException=exports.UnexpectedResponseException=exports.TextRenderingMode=exports.StreamType=exports.PermissionFlag=exports.PasswordResponses=exports.PasswordException=exports.NativeImageDecoding=exports.MissingPDFException=exports.InvalidPDFException=exports.AbortException=exports.CMapCompressionType=exports.ImageKind=exports.FontType=exports.AnnotationType=exports.AnnotationFlag=exports.AnnotationFieldFlag=exports.AnnotationBorderStyleType=exports.UNSUPPORTED_FEATURES=exports.VerbosityLevel=exports.OPS=exports.IDENTITY_MATRIX=exports.FONT_IDENTITY_MATRIX=void0;

__w_pdfjs_require__(2);

var_streams_polyfill=__w_pdfjs_require__(143);

var_url_polyfill=__w_pdfjs_require__(145);

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

varIDENTITY_MATRIX=[1,0,0,1,0,0];
exports.IDENTITY_MATRIX=IDENTITY_MATRIX;
varFONT_IDENTITY_MATRIX=[0.001,0,0,0.001,0,0];
exports.FONT_IDENTITY_MATRIX=FONT_IDENTITY_MATRIX;
varNativeImageDecoding={
  NONE:'none',
  DECODE:'decode',
  DISPLAY:'display'
};
exports.NativeImageDecoding=NativeImageDecoding;
varPermissionFlag={
  PRINT:0x04,
  MODIFY_CONTENTS:0x08,
  COPY:0x10,
  MODIFY_ANNOTATIONS:0x20,
  FILL_INTERACTIVE_FORMS:0x100,
  COPY_FOR_ACCESSIBILITY:0x200,
  ASSEMBLE:0x400,
  PRINT_HIGH_QUALITY:0x800
};
exports.PermissionFlag=PermissionFlag;
varTextRenderingMode={
  FILL:0,
  STROKE:1,
  FILL_STROKE:2,
  INVISIBLE:3,
  FILL_ADD_TO_PATH:4,
  STROKE_ADD_TO_PATH:5,
  FILL_STROKE_ADD_TO_PATH:6,
  ADD_TO_PATH:7,
  FILL_STROKE_MASK:3,
  ADD_TO_PATH_FLAG:4
};
exports.TextRenderingMode=TextRenderingMode;
varImageKind={
  GRAYSCALE_1BPP:1,
  RGB_24BPP:2,
  RGBA_32BPP:3
};
exports.ImageKind=ImageKind;
varAnnotationType={
  TEXT:1,
  LINK:2,
  FREETEXT:3,
  LINE:4,
  SQUARE:5,
  CIRCLE:6,
  POLYGON:7,
  POLYLINE:8,
  HIGHLIGHT:9,
  UNDERLINE:10,
  SQUIGGLY:11,
  STRIKEOUT:12,
  STAMP:13,
  CARET:14,
  INK:15,
  POPUP:16,
  FILEATTACHMENT:17,
  SOUND:18,
  MOVIE:19,
  WIDGET:20,
  SCREEN:21,
  PRINTERMARK:22,
  TRAPNET:23,
  WATERMARK:24,
  THREED:25,
  REDACT:26
};
exports.AnnotationType=AnnotationType;
varAnnotationFlag={
  INVISIBLE:0x01,
  HIDDEN:0x02,
  PRINT:0x04,
  NOZOOM:0x08,
  NOROTATE:0x10,
  NOVIEW:0x20,
  READONLY:0x40,
  LOCKED:0x80,
  TOGGLENOVIEW:0x100,
  LOCKEDCONTENTS:0x200
};
exports.AnnotationFlag=AnnotationFlag;
varAnnotationFieldFlag={
  READONLY:0x0000001,
  REQUIRED:0x0000002,
  NOEXPORT:0x0000004,
  MULTILINE:0x0001000,
  PASSWORD:0x0002000,
  NOTOGGLETOOFF:0x0004000,
  RADIO:0x0008000,
  PUSHBUTTON:0x0010000,
  COMBO:0x0020000,
  EDIT:0x0040000,
  SORT:0x0080000,
  FILESELECT:0x0100000,
  MULTISELECT:0x0200000,
  DONOTSPELLCHECK:0x0400000,
  DONOTSCROLL:0x0800000,
  COMB:0x1000000,
  RICHTEXT:0x2000000,
  RADIOSINUNISON:0x2000000,
  COMMITONSELCHANGE:0x4000000
};
exports.AnnotationFieldFlag=AnnotationFieldFlag;
varAnnotationBorderStyleType={
  SOLID:1,
  DASHED:2,
  BEVELED:3,
  INSET:4,
  UNDERLINE:5
};
exports.AnnotationBorderStyleType=AnnotationBorderStyleType;
varStreamType={
  UNKNOWN:0,
  FLATE:1,
  LZW:2,
  DCT:3,
  JPX:4,
  JBIG:5,
  A85:6,
  AHX:7,
  CCF:8,
  RL:9
};
exports.StreamType=StreamType;
varFontType={
  UNKNOWN:0,
  TYPE1:1,
  TYPE1C:2,
  CIDFONTTYPE0:3,
  CIDFONTTYPE0C:4,
  TRUETYPE:5,
  CIDFONTTYPE2:6,
  TYPE3:7,
  OPENTYPE:8,
  TYPE0:9,
  MMTYPE1:10
};
exports.FontType=FontType;
varVerbosityLevel={
  ERRORS:0,
  WARNINGS:1,
  INFOS:5
};
exports.VerbosityLevel=VerbosityLevel;
varCMapCompressionType={
  NONE:0,
  BINARY:1,
  STREAM:2
};
exports.CMapCompressionType=CMapCompressionType;
varOPS={
  dependency:1,
  setLineWidth:2,
  setLineCap:3,
  setLineJoin:4,
  setMiterLimit:5,
  setDash:6,
  setRenderingIntent:7,
  setFlatness:8,
  setGState:9,
  save:10,
  restore:11,
  transform:12,
  moveTo:13,
  lineTo:14,
  curveTo:15,
  curveTo2:16,
  curveTo3:17,
  closePath:18,
  rectangle:19,
  stroke:20,
  closeStroke:21,
  fill:22,
  eoFill:23,
  fillStroke:24,
  eoFillStroke:25,
  closeFillStroke:26,
  closeEOFillStroke:27,
  endPath:28,
  clip:29,
  eoClip:30,
  beginText:31,
  endText:32,
  setCharSpacing:33,
  setWordSpacing:34,
  setHScale:35,
  setLeading:36,
  setFont:37,
  setTextRenderingMode:38,
  setTextRise:39,
  moveText:40,
  setLeadingMoveText:41,
  setTextMatrix:42,
  nextLine:43,
  showText:44,
  showSpacedText:45,
  nextLineShowText:46,
  nextLineSetSpacingShowText:47,
  setCharWidth:48,
  setCharWidthAndBounds:49,
  setStrokeColorSpace:50,
  setFillColorSpace:51,
  setStrokeColor:52,
  setStrokeColorN:53,
  setFillColor:54,
  setFillColorN:55,
  setStrokeGray:56,
  setFillGray:57,
  setStrokeRGBColor:58,
  setFillRGBColor:59,
  setStrokeCMYKColor:60,
  setFillCMYKColor:61,
  shadingFill:62,
  beginInlineImage:63,
  beginImageData:64,
  endInlineImage:65,
  paintXObject:66,
  markPoint:67,
  markPointProps:68,
  beginMarkedContent:69,
  beginMarkedContentProps:70,
  endMarkedContent:71,
  beginCompat:72,
  endCompat:73,
  paintFormXObjectBegin:74,
  paintFormXObjectEnd:75,
  beginGroup:76,
  endGroup:77,
  beginAnnotations:78,
  endAnnotations:79,
  beginAnnotation:80,
  endAnnotation:81,
  paintJpegXObject:82,
  paintImageMaskXObject:83,
  paintImageMaskXObjectGroup:84,
  paintImageXObject:85,
  paintInlineImageXObject:86,
  paintInlineImageXObjectGroup:87,
  paintImageXObjectRepeat:88,
  paintImageMaskXObjectRepeat:89,
  paintSolidColorImageMask:90,
  constructPath:91
};
exports.OPS=OPS;
varUNSUPPORTED_FEATURES={
  unknown:'unknown',
  forms:'forms',
  javaScript:'javaScript',
  smask:'smask',
  shadingPattern:'shadingPattern',
  font:'font'
};
exports.UNSUPPORTED_FEATURES=UNSUPPORTED_FEATURES;
varPasswordResponses={
  NEED_PASSWORD:1,
  INCORRECT_PASSWORD:2
};
exports.PasswordResponses=PasswordResponses;
varverbosity=VerbosityLevel.WARNINGS;

functionsetVerbosityLevel(level){
  if(Number.isInteger(level)){
    verbosity=level;
  }
}

functiongetVerbosityLevel(){
  returnverbosity;
}

functioninfo(msg){
  if(verbosity>=VerbosityLevel.INFOS){
    console.log('Info:'+msg);
  }
}

functionwarn(msg){
  if(verbosity>=VerbosityLevel.WARNINGS){
    console.log('Warning:'+msg);
  }
}

functionunreachable(msg){
  thrownewError(msg);
}

functionassert(cond,msg){
  if(!cond){
    unreachable(msg);
  }
}

functionisSameOrigin(baseUrl,otherUrl){
  try{
    varbase=new_url_polyfill.URL(baseUrl);

    if(!base.origin||base.origin==='null'){
      returnfalse;
    }
  }catch(e){
    returnfalse;
  }

  varother=new_url_polyfill.URL(otherUrl,base);
  returnbase.origin===other.origin;
}

function_isValidProtocol(url){
  if(!url){
    returnfalse;
  }

  switch(url.protocol){
    case'http:':
    case'https:':
    case'ftp:':
    case'mailto:':
    case'tel:':
      returntrue;

    default:
      returnfalse;
  }
}

functioncreateValidAbsoluteUrl(url,baseUrl){
  if(!url){
    returnnull;
  }

  try{
    varabsoluteUrl=baseUrl?new_url_polyfill.URL(url,baseUrl):new_url_polyfill.URL(url);

    if(_isValidProtocol(absoluteUrl)){
      returnabsoluteUrl;
    }
  }catch(ex){}

  returnnull;
}

functionshadow(obj,prop,value){
  Object.defineProperty(obj,prop,{
    value:value,
    enumerable:true,
    configurable:true,
    writable:false
  });
  returnvalue;
}

varPasswordException=functionPasswordExceptionClosure(){
  functionPasswordException(msg,code){
    this.name='PasswordException';
    this.message=msg;
    this.code=code;
  }

  PasswordException.prototype=newError();
  PasswordException.constructor=PasswordException;
  returnPasswordException;
}();

exports.PasswordException=PasswordException;

varUnknownErrorException=functionUnknownErrorExceptionClosure(){
  functionUnknownErrorException(msg,details){
    this.name='UnknownErrorException';
    this.message=msg;
    this.details=details;
  }

  UnknownErrorException.prototype=newError();
  UnknownErrorException.constructor=UnknownErrorException;
  returnUnknownErrorException;
}();

exports.UnknownErrorException=UnknownErrorException;

varInvalidPDFException=functionInvalidPDFExceptionClosure(){
  functionInvalidPDFException(msg){
    this.name='InvalidPDFException';
    this.message=msg;
  }

  InvalidPDFException.prototype=newError();
  InvalidPDFException.constructor=InvalidPDFException;
  returnInvalidPDFException;
}();

exports.InvalidPDFException=InvalidPDFException;

varMissingPDFException=functionMissingPDFExceptionClosure(){
  functionMissingPDFException(msg){
    this.name='MissingPDFException';
    this.message=msg;
  }

  MissingPDFException.prototype=newError();
  MissingPDFException.constructor=MissingPDFException;
  returnMissingPDFException;
}();

exports.MissingPDFException=MissingPDFException;

varUnexpectedResponseException=functionUnexpectedResponseExceptionClosure(){
  functionUnexpectedResponseException(msg,status){
    this.name='UnexpectedResponseException';
    this.message=msg;
    this.status=status;
  }

  UnexpectedResponseException.prototype=newError();
  UnexpectedResponseException.constructor=UnexpectedResponseException;
  returnUnexpectedResponseException;
}();

exports.UnexpectedResponseException=UnexpectedResponseException;

varFormatError=functionFormatErrorClosure(){
  functionFormatError(msg){
    this.message=msg;
  }

  FormatError.prototype=newError();
  FormatError.prototype.name='FormatError';
  FormatError.constructor=FormatError;
  returnFormatError;
}();

exports.FormatError=FormatError;

varAbortException=functionAbortExceptionClosure(){
  functionAbortException(msg){
    this.name='AbortException';
    this.message=msg;
  }

  AbortException.prototype=newError();
  AbortException.constructor=AbortException;
  returnAbortException;
}();

exports.AbortException=AbortException;
varNullCharactersRegExp=/\x00/g;

functionremoveNullCharacters(str){
  if(typeofstr!=='string'){
    warn('TheargumentforremoveNullCharactersmustbeastring.');
    returnstr;
  }

  returnstr.replace(NullCharactersRegExp,'');
}

functionbytesToString(bytes){
  assert(bytes!==null&&_typeof(bytes)==='object'&&bytes.length!==undefined,'InvalidargumentforbytesToString');
  varlength=bytes.length;
  varMAX_ARGUMENT_COUNT=8192;

  if(length<MAX_ARGUMENT_COUNT){
    returnString.fromCharCode.apply(null,bytes);
  }

  varstrBuf=[];

  for(vari=0;i<length;i+=MAX_ARGUMENT_COUNT){
    varchunkEnd=Math.min(i+MAX_ARGUMENT_COUNT,length);
    varchunk=bytes.subarray(i,chunkEnd);
    strBuf.push(String.fromCharCode.apply(null,chunk));
  }

  returnstrBuf.join('');
}

functionstringToBytes(str){
  assert(typeofstr==='string','InvalidargumentforstringToBytes');
  varlength=str.length;
  varbytes=newUint8Array(length);

  for(vari=0;i<length;++i){
    bytes[i]=str.charCodeAt(i)&0xFF;
  }

  returnbytes;
}

functionarrayByteLength(arr){
  if(arr.length!==undefined){
    returnarr.length;
  }

  assert(arr.byteLength!==undefined);
  returnarr.byteLength;
}

functionarraysToBytes(arr){
  if(arr.length===1&&arr[0]instanceofUint8Array){
    returnarr[0];
  }

  varresultLength=0;
  vari,
      ii=arr.length;
  varitem,itemLength;

  for(i=0;i<ii;i++){
    item=arr[i];
    itemLength=arrayByteLength(item);
    resultLength+=itemLength;
  }

  varpos=0;
  vardata=newUint8Array(resultLength);

  for(i=0;i<ii;i++){
    item=arr[i];

    if(!(iteminstanceofUint8Array)){
      if(typeofitem==='string'){
        item=stringToBytes(item);
      }else{
        item=newUint8Array(item);
      }
    }

    itemLength=item.byteLength;
    data.set(item,pos);
    pos+=itemLength;
  }

  returndata;
}

functionstring32(value){
  returnString.fromCharCode(value>>24&0xff,value>>16&0xff,value>>8&0xff,value&0xff);
}

functionlog2(x){
  if(x<=0){
    return0;
  }

  returnMath.ceil(Math.log2(x));
}

functionreadInt8(data,start){
  returndata[start]<<24>>24;
}

functionreadUint16(data,offset){
  returndata[offset]<<8|data[offset+1];
}

functionreadUint32(data,offset){
  return(data[offset]<<24|data[offset+1]<<16|data[offset+2]<<8|data[offset+3])>>>0;
}

functionisLittleEndian(){
  varbuffer8=newUint8Array(4);
  buffer8[0]=1;
  varview32=newUint32Array(buffer8.buffer,0,1);
  returnview32[0]===1;
}

functionisEvalSupported(){
  try{
    newFunction('');
    returntrue;
  }catch(e){
    returnfalse;
  }
}

varUtil=functionUtilClosure(){
  functionUtil(){}

  varrgbBuf=['rgb(',0,',',0,',',0,')'];

  Util.makeCssRgb=functionUtil_makeCssRgb(r,g,b){
    rgbBuf[1]=r;
    rgbBuf[3]=g;
    rgbBuf[5]=b;
    returnrgbBuf.join('');
  };

  Util.transform=functionUtil_transform(m1,m2){
    return[m1[0]*m2[0]+m1[2]*m2[1],m1[1]*m2[0]+m1[3]*m2[1],m1[0]*m2[2]+m1[2]*m2[3],m1[1]*m2[2]+m1[3]*m2[3],m1[0]*m2[4]+m1[2]*m2[5]+m1[4],m1[1]*m2[4]+m1[3]*m2[5]+m1[5]];
  };

  Util.applyTransform=functionUtil_applyTransform(p,m){
    varxt=p[0]*m[0]+p[1]*m[2]+m[4];
    varyt=p[0]*m[1]+p[1]*m[3]+m[5];
    return[xt,yt];
  };

  Util.applyInverseTransform=functionUtil_applyInverseTransform(p,m){
    vard=m[0]*m[3]-m[1]*m[2];
    varxt=(p[0]*m[3]-p[1]*m[2]+m[2]*m[5]-m[4]*m[3])/d;
    varyt=(-p[0]*m[1]+p[1]*m[0]+m[4]*m[1]-m[5]*m[0])/d;
    return[xt,yt];
  };

  Util.getAxialAlignedBoundingBox=functionUtil_getAxialAlignedBoundingBox(r,m){
    varp1=Util.applyTransform(r,m);
    varp2=Util.applyTransform(r.slice(2,4),m);
    varp3=Util.applyTransform([r[0],r[3]],m);
    varp4=Util.applyTransform([r[2],r[1]],m);
    return[Math.min(p1[0],p2[0],p3[0],p4[0]),Math.min(p1[1],p2[1],p3[1],p4[1]),Math.max(p1[0],p2[0],p3[0],p4[0]),Math.max(p1[1],p2[1],p3[1],p4[1])];
  };

  Util.inverseTransform=functionUtil_inverseTransform(m){
    vard=m[0]*m[3]-m[1]*m[2];
    return[m[3]/d,-m[1]/d,-m[2]/d,m[0]/d,(m[2]*m[5]-m[4]*m[3])/d,(m[4]*m[1]-m[5]*m[0])/d];
  };

  Util.apply3dTransform=functionUtil_apply3dTransform(m,v){
    return[m[0]*v[0]+m[1]*v[1]+m[2]*v[2],m[3]*v[0]+m[4]*v[1]+m[5]*v[2],m[6]*v[0]+m[7]*v[1]+m[8]*v[2]];
  };

  Util.singularValueDecompose2dScale=functionUtil_singularValueDecompose2dScale(m){
    vartranspose=[m[0],m[2],m[1],m[3]];
    vara=m[0]*transpose[0]+m[1]*transpose[2];
    varb=m[0]*transpose[1]+m[1]*transpose[3];
    varc=m[2]*transpose[0]+m[3]*transpose[2];
    vard=m[2]*transpose[1]+m[3]*transpose[3];
    varfirst=(a+d)/2;
    varsecond=Math.sqrt((a+d)*(a+d)-4*(a*d-c*b))/2;
    varsx=first+second||1;
    varsy=first-second||1;
    return[Math.sqrt(sx),Math.sqrt(sy)];
  };

  Util.normalizeRect=functionUtil_normalizeRect(rect){
    varr=rect.slice(0);

    if(rect[0]>rect[2]){
      r[0]=rect[2];
      r[2]=rect[0];
    }

    if(rect[1]>rect[3]){
      r[1]=rect[3];
      r[3]=rect[1];
    }

    returnr;
  };

  Util.intersect=functionUtil_intersect(rect1,rect2){
    functioncompare(a,b){
      returna-b;
    }

    varorderedX=[rect1[0],rect1[2],rect2[0],rect2[2]].sort(compare),
        orderedY=[rect1[1],rect1[3],rect2[1],rect2[3]].sort(compare),
        result=[];
    rect1=Util.normalizeRect(rect1);
    rect2=Util.normalizeRect(rect2);

    if(orderedX[0]===rect1[0]&&orderedX[1]===rect2[0]||orderedX[0]===rect2[0]&&orderedX[1]===rect1[0]){
      result[0]=orderedX[1];
      result[2]=orderedX[2];
    }else{
      returnfalse;
    }

    if(orderedY[0]===rect1[1]&&orderedY[1]===rect2[1]||orderedY[0]===rect2[1]&&orderedY[1]===rect1[1]){
      result[1]=orderedY[1];
      result[3]=orderedY[2];
    }else{
      returnfalse;
    }

    returnresult;
  };

  returnUtil;
}();

exports.Util=Util;
varPDFStringTranslateTable=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x2D8,0x2C7,0x2C6,0x2D9,0x2DD,0x2DB,0x2DA,0x2DC,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0x2022,0x2020,0x2021,0x2026,0x2014,0x2013,0x192,0x2044,0x2039,0x203A,0x2212,0x2030,0x201E,0x201C,0x201D,0x2018,0x2019,0x201A,0x2122,0xFB01,0xFB02,0x141,0x152,0x160,0x178,0x17D,0x131,0x142,0x153,0x161,0x17E,0,0x20AC];

functionstringToPDFString(str){
  vari,
      n=str.length,
      strBuf=[];

  if(str[0]==='\xFE'&&str[1]==='\xFF'){
    for(i=2;i<n;i+=2){
      strBuf.push(String.fromCharCode(str.charCodeAt(i)<<8|str.charCodeAt(i+1)));
    }
  }else{
    for(i=0;i<n;++i){
      varcode=PDFStringTranslateTable[str.charCodeAt(i)];
      strBuf.push(code?String.fromCharCode(code):str.charAt(i));
    }
  }

  returnstrBuf.join('');
}

functionstringToUTF8String(str){
  returndecodeURIComponent(escape(str));
}

functionutf8StringToString(str){
  returnunescape(encodeURIComponent(str));
}

functionisEmptyObj(obj){
  for(varkeyinobj){
    returnfalse;
  }

  returntrue;
}

functionisBool(v){
  returntypeofv==='boolean';
}

functionisNum(v){
  returntypeofv==='number';
}

functionisString(v){
  returntypeofv==='string';
}

functionisArrayBuffer(v){
  return_typeof(v)==='object'&&v!==null&&v.byteLength!==undefined;
}

functionisArrayEqual(arr1,arr2){
  if(arr1.length!==arr2.length){
    returnfalse;
  }

  returnarr1.every(function(element,index){
    returnelement===arr2[index];
  });
}

functionisSpace(ch){
  returnch===0x20||ch===0x09||ch===0x0D||ch===0x0A;
}

functioncreatePromiseCapability(){
  varcapability=Object.create(null);
  varisSettled=false;
  Object.defineProperty(capability,'settled',{
    get:functionget(){
      returnisSettled;
    }
  });
  capability.promise=newPromise(function(resolve,reject){
    capability.resolve=function(data){
      isSettled=true;
      resolve(data);
    };

    capability.reject=function(reason){
      isSettled=true;
      reject(reason);
    };
  });
  returncapability;
}

varcreateObjectURL=functioncreateObjectURLClosure(){
  vardigits='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=';
  returnfunctioncreateObjectURL(data,contentType){
    varforceDataSchema=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

    if(!forceDataSchema&&_url_polyfill.URL.createObjectURL){
      varblob=newBlob([data],{
        type:contentType
      });
      return_url_polyfill.URL.createObjectURL(blob);
    }

    varbuffer='data:'+contentType+';base64,';

    for(vari=0,ii=data.length;i<ii;i+=3){
      varb1=data[i]&0xFF;
      varb2=data[i+1]&0xFF;
      varb3=data[i+2]&0xFF;
      vard1=b1>>2,
          d2=(b1&3)<<4|b2>>4;
      vard3=i+1<ii?(b2&0xF)<<2|b3>>6:64;
      vard4=i+2<ii?b3&0x3F:64;
      buffer+=digits[d1]+digits[d2]+digits[d3]+digits[d4];
    }

    returnbuffer;
  };
}();

exports.createObjectURL=createObjectURL;

/***/}),
/*2*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

varglobalScope=__w_pdfjs_require__(3);

if(!globalScope._pdfjsCompatibilityChecked){
  globalScope._pdfjsCompatibilityChecked=true;

  varisNodeJS=__w_pdfjs_require__(4);

  varhasDOM=(typeofwindow==="undefined"?"undefined":_typeof(window))==='object'&&(typeofdocument==="undefined"?"undefined":_typeof(document))==='object';

  (functioncheckNodeBtoa(){
    if(globalScope.btoa||!isNodeJS()){
      return;
    }

    globalScope.btoa=function(chars){
      returnBuffer.from(chars,'binary').toString('base64');
    };
  })();

  (functioncheckNodeAtob(){
    if(globalScope.atob||!isNodeJS()){
      return;
    }

    globalScope.atob=function(input){
      returnBuffer.from(input,'base64').toString('binary');
    };
  })();

  (functioncheckChildNodeRemove(){
    if(!hasDOM){
      return;
    }

    if(typeofElement.prototype.remove!=='undefined'){
      return;
    }

    Element.prototype.remove=function(){
      if(this.parentNode){
        this.parentNode.removeChild(this);
      }
    };
  })();

  (functioncheckDOMTokenListAddRemove(){
    if(!hasDOM||isNodeJS()){
      return;
    }

    vardiv=document.createElement('div');
    div.classList.add('testOne','testTwo');

    if(div.classList.contains('testOne')===true&&div.classList.contains('testTwo')===true){
      return;
    }

    varOriginalDOMTokenListAdd=DOMTokenList.prototype.add;
    varOriginalDOMTokenListRemove=DOMTokenList.prototype.remove;

    DOMTokenList.prototype.add=function(){
      for(var_len=arguments.length,tokens=newArray(_len),_key=0;_key<_len;_key++){
        tokens[_key]=arguments[_key];
      }

      for(var_i=0,_tokens=tokens;_i<_tokens.length;_i++){
        vartoken=_tokens[_i];
        OriginalDOMTokenListAdd.call(this,token);
      }
    };

    DOMTokenList.prototype.remove=function(){
      for(var_len2=arguments.length,tokens=newArray(_len2),_key2=0;_key2<_len2;_key2++){
        tokens[_key2]=arguments[_key2];
      }

      for(var_i2=0,_tokens2=tokens;_i2<_tokens2.length;_i2++){
        vartoken=_tokens2[_i2];
        OriginalDOMTokenListRemove.call(this,token);
      }
    };
  })();

  (functioncheckDOMTokenListToggle(){
    if(!hasDOM||isNodeJS()){
      return;
    }

    vardiv=document.createElement('div');

    if(div.classList.toggle('test',0)===false){
      return;
    }

    DOMTokenList.prototype.toggle=function(token){
      varforce=arguments.length>1?!!arguments[1]:!this.contains(token);
      returnthis[force?'add':'remove'](token),force;
    };
  })();

  (functioncheckStringStartsWith(){
    if(String.prototype.startsWith){
      return;
    }

    __w_pdfjs_require__(5);
  })();

  (functioncheckStringEndsWith(){
    if(String.prototype.endsWith){
      return;
    }

    __w_pdfjs_require__(36);
  })();

  (functioncheckStringIncludes(){
    if(String.prototype.includes){
      return;
    }

    __w_pdfjs_require__(38);
  })();

  (functioncheckArrayIncludes(){
    if(Array.prototype.includes){
      return;
    }

    __w_pdfjs_require__(40);
  })();

  (functioncheckArrayFrom(){
    if(Array.from){
      return;
    }

    __w_pdfjs_require__(47);
  })();

  (functioncheckObjectAssign(){
    if(Object.assign){
      return;
    }

    __w_pdfjs_require__(70);
  })();

  (functioncheckMathLog2(){
    if(Math.log2){
      return;
    }

    Math.log2=__w_pdfjs_require__(75);
  })();

  (functioncheckNumberIsNaN(){
    if(Number.isNaN){
      return;
    }

    Number.isNaN=__w_pdfjs_require__(77);
  })();

  (functioncheckNumberIsInteger(){
    if(Number.isInteger){
      return;
    }

    Number.isInteger=__w_pdfjs_require__(79);
  })();

  (functioncheckPromise(){
    if(globalScope.Promise&&globalScope.Promise.prototype&&globalScope.Promise.prototype["finally"]){
      return;
    }

    globalScope.Promise=__w_pdfjs_require__(82);
  })();

  (functioncheckWeakMap(){
    if(globalScope.WeakMap){
      return;
    }

    globalScope.WeakMap=__w_pdfjs_require__(102);
  })();

  (functioncheckWeakSet(){
    if(globalScope.WeakSet){
      return;
    }

    globalScope.WeakSet=__w_pdfjs_require__(119);
  })();

  (functioncheckStringCodePointAt(){
    if(String.codePointAt){
      return;
    }

    String.codePointAt=__w_pdfjs_require__(123);
  })();

  (functioncheckStringFromCodePoint(){
    if(String.fromCodePoint){
      return;
    }

    String.fromCodePoint=__w_pdfjs_require__(125);
  })();

  (functioncheckSymbol(){
    if(globalScope.Symbol){
      return;
    }

    __w_pdfjs_require__(127);
  })();

  (functioncheckStringPadStart(){
    if(String.prototype.padStart){
      return;
    }

    __w_pdfjs_require__(134);
  })();

  (functioncheckStringPadEnd(){
    if(String.prototype.padEnd){
      return;
    }

    __w_pdfjs_require__(138);
  })();

  (functioncheckObjectValues(){
    if(Object.values){
      return;
    }

    Object.values=__w_pdfjs_require__(140);
  })();
}

/***/}),
/*3*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=typeofwindow!=='undefined'&&window.Math===Math?window:typeofglobal!=='undefined'&&global.Math===Math?global:typeofself!=='undefined'&&self.Math===Math?self:{};

/***/}),
/*4*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

module.exports=functionisNodeJS(){
  return(typeofprocess==="undefined"?"undefined":_typeof(process))==='object'&&process+''==='[objectprocess]'&&!process.versions['nw']&&!process.versions['electron'];
};

/***/}),
/*5*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(6);

module.exports=__w_pdfjs_require__(9).String.startsWith;

/***/}),
/*6*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

vartoLength=__w_pdfjs_require__(28);

varcontext=__w_pdfjs_require__(30);

varSTARTS_WITH='startsWith';
var$startsWith=''[STARTS_WITH];
$export($export.P+$export.F*__w_pdfjs_require__(35)(STARTS_WITH),'String',{
  startsWith:functionstartsWith(searchString){
    varthat=context(this,searchString,STARTS_WITH);
    varindex=toLength(Math.min(arguments.length>1?arguments[1]:undefined,that.length));
    varsearch=String(searchString);
    return$startsWith?$startsWith.call(that,search,index):that.slice(index,index+search.length)===search;
  }
});

/***/}),
/*7*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

varcore=__w_pdfjs_require__(9);

varhide=__w_pdfjs_require__(10);

varredefine=__w_pdfjs_require__(20);

varctx=__w_pdfjs_require__(26);

varPROTOTYPE='prototype';

var$export=function$export(type,name,source){
  varIS_FORCED=type&$export.F;
  varIS_GLOBAL=type&$export.G;
  varIS_STATIC=type&$export.S;
  varIS_PROTO=type&$export.P;
  varIS_BIND=type&$export.B;
  vartarget=IS_GLOBAL?global:IS_STATIC?global[name]||(global[name]={}):(global[name]||{})[PROTOTYPE];
  varexports=IS_GLOBAL?core:core[name]||(core[name]={});
  varexpProto=exports[PROTOTYPE]||(exports[PROTOTYPE]={});
  varkey,own,out,exp;
  if(IS_GLOBAL)source=name;

  for(keyinsource){
    own=!IS_FORCED&&target&&target[key]!==undefined;
    out=(own?target:source)[key];
    exp=IS_BIND&&own?ctx(out,global):IS_PROTO&&typeofout=='function'?ctx(Function.call,out):out;
    if(target)redefine(target,key,out,type&$export.U);
    if(exports[key]!=out)hide(exports,key,exp);
    if(IS_PROTO&&expProto[key]!=out)expProto[key]=out;
  }
};

global.core=core;
$export.F=1;
$export.G=2;
$export.S=4;
$export.P=8;
$export.B=16;
$export.W=32;
$export.U=64;
$export.R=128;
module.exports=$export;

/***/}),
/*8*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=module.exports=typeofwindow!='undefined'&&window.Math==Math?window:typeofself!='undefined'&&self.Math==Math?self:Function('returnthis')();
if(typeof__g=='number')__g=global;

/***/}),
/*9*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcore=module.exports={
  version:'2.6.9'
};
if(typeof__e=='number')__e=core;

/***/}),
/*10*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vardP=__w_pdfjs_require__(11);

varcreateDesc=__w_pdfjs_require__(19);

module.exports=__w_pdfjs_require__(15)?function(object,key,value){
  returndP.f(object,key,createDesc(1,value));
}:function(object,key,value){
  object[key]=value;
  returnobject;
};

/***/}),
/*11*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varanObject=__w_pdfjs_require__(12);

varIE8_DOM_DEFINE=__w_pdfjs_require__(14);

vartoPrimitive=__w_pdfjs_require__(18);

vardP=Object.defineProperty;
exports.f=__w_pdfjs_require__(15)?Object.defineProperty:functiondefineProperty(O,P,Attributes){
  anObject(O);
  P=toPrimitive(P,true);
  anObject(Attributes);
  if(IE8_DOM_DEFINE)try{
    returndP(O,P,Attributes);
  }catch(e){}
  if('get'inAttributes||'set'inAttributes)throwTypeError('Accessorsnotsupported!');
  if('value'inAttributes)O[P]=Attributes.value;
  returnO;
};

/***/}),
/*12*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

module.exports=function(it){
  if(!isObject(it))throwTypeError(it+'isnotanobject!');
  returnit;
};

/***/}),
/*13*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

module.exports=function(it){
  return_typeof(it)==='object'?it!==null:typeofit==='function';
};

/***/}),
/*14*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=!__w_pdfjs_require__(15)&&!__w_pdfjs_require__(16)(function(){
  returnObject.defineProperty(__w_pdfjs_require__(17)('div'),'a',{
    get:functionget(){
      return7;
    }
  }).a!=7;
});

/***/}),
/*15*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=!__w_pdfjs_require__(16)(function(){
  returnObject.defineProperty({},'a',{
    get:functionget(){
      return7;
    }
  }).a!=7;
});

/***/}),
/*16*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(exec){
  try{
    return!!exec();
  }catch(e){
    returntrue;
  }
};

/***/}),
/*17*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

vardocument=__w_pdfjs_require__(8).document;

varis=isObject(document)&&isObject(document.createElement);

module.exports=function(it){
  returnis?document.createElement(it):{};
};

/***/}),
/*18*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

module.exports=function(it,S){
  if(!isObject(it))returnit;
  varfn,val;
  if(S&&typeof(fn=it.toString)=='function'&&!isObject(val=fn.call(it)))returnval;
  if(typeof(fn=it.valueOf)=='function'&&!isObject(val=fn.call(it)))returnval;
  if(!S&&typeof(fn=it.toString)=='function'&&!isObject(val=fn.call(it)))returnval;
  throwTypeError("Can'tconvertobjecttoprimitivevalue");
};

/***/}),
/*19*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(bitmap,value){
  return{
    enumerable:!(bitmap&1),
    configurable:!(bitmap&2),
    writable:!(bitmap&4),
    value:value
  };
};

/***/}),
/*20*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

varhide=__w_pdfjs_require__(10);

varhas=__w_pdfjs_require__(21);

varSRC=__w_pdfjs_require__(22)('src');

var$toString=__w_pdfjs_require__(23);

varTO_STRING='toString';
varTPL=(''+$toString).split(TO_STRING);

__w_pdfjs_require__(9).inspectSource=function(it){
  return$toString.call(it);
};

(module.exports=function(O,key,val,safe){
  varisFunction=typeofval=='function';
  if(isFunction)has(val,'name')||hide(val,'name',key);
  if(O[key]===val)return;
  if(isFunction)has(val,SRC)||hide(val,SRC,O[key]?''+O[key]:TPL.join(String(key)));

  if(O===global){
    O[key]=val;
  }elseif(!safe){
    deleteO[key];
    hide(O,key,val);
  }elseif(O[key]){
    O[key]=val;
  }else{
    hide(O,key,val);
  }
})(Function.prototype,TO_STRING,functiontoString(){
  returntypeofthis=='function'&&this[SRC]||$toString.call(this);
});

/***/}),
/*21*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varhasOwnProperty={}.hasOwnProperty;

module.exports=function(it,key){
  returnhasOwnProperty.call(it,key);
};

/***/}),
/*22*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varid=0;
varpx=Math.random();

module.exports=function(key){
  return'Symbol('.concat(key===undefined?'':key,')_',(++id+px).toString(36));
};

/***/}),
/*23*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=__w_pdfjs_require__(24)('native-function-to-string',Function.toString);

/***/}),
/*24*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcore=__w_pdfjs_require__(9);

varglobal=__w_pdfjs_require__(8);

varSHARED='__core-js_shared__';
varstore=global[SHARED]||(global[SHARED]={});
(module.exports=function(key,value){
  returnstore[key]||(store[key]=value!==undefined?value:{});
})('versions',[]).push({
  version:core.version,
  mode:__w_pdfjs_require__(25)?'pure':'global',
  copyright:'©2019DenisPushkarev(zloirock.ru)'
});

/***/}),
/*25*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=false;

/***/}),
/*26*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varaFunction=__w_pdfjs_require__(27);

module.exports=function(fn,that,length){
  aFunction(fn);
  if(that===undefined)returnfn;

  switch(length){
    case1:
      returnfunction(a){
        returnfn.call(that,a);
      };

    case2:
      returnfunction(a,b){
        returnfn.call(that,a,b);
      };

    case3:
      returnfunction(a,b,c){
        returnfn.call(that,a,b,c);
      };
  }

  returnfunction(){
    returnfn.apply(that,arguments);
  };
};

/***/}),
/*27*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(it){
  if(typeofit!='function')throwTypeError(it+'isnotafunction!');
  returnit;
};

/***/}),
/*28*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoInteger=__w_pdfjs_require__(29);

varmin=Math.min;

module.exports=function(it){
  returnit>0?min(toInteger(it),0x1fffffffffffff):0;
};

/***/}),
/*29*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varceil=Math.ceil;
varfloor=Math.floor;

module.exports=function(it){
  returnisNaN(it=+it)?0:(it>0?floor:ceil)(it);
};

/***/}),
/*30*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisRegExp=__w_pdfjs_require__(31);

vardefined=__w_pdfjs_require__(34);

module.exports=function(that,searchString,NAME){
  if(isRegExp(searchString))throwTypeError('String#'+NAME+"doesn'tacceptregex!");
  returnString(defined(that));
};

/***/}),
/*31*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

varcof=__w_pdfjs_require__(32);

varMATCH=__w_pdfjs_require__(33)('match');

module.exports=function(it){
  varisRegExp;
  returnisObject(it)&&((isRegExp=it[MATCH])!==undefined?!!isRegExp:cof(it)=='RegExp');
};

/***/}),
/*32*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoString={}.toString;

module.exports=function(it){
  returntoString.call(it).slice(8,-1);
};

/***/}),
/*33*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varstore=__w_pdfjs_require__(24)('wks');

varuid=__w_pdfjs_require__(22);

var_Symbol=__w_pdfjs_require__(8).Symbol;

varUSE_SYMBOL=typeof_Symbol=='function';

var$exports=module.exports=function(name){
  returnstore[name]||(store[name]=USE_SYMBOL&&_Symbol[name]||(USE_SYMBOL?_Symbol:uid)('Symbol.'+name));
};

$exports.store=store;

/***/}),
/*34*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(it){
  if(it==undefined)throwTypeError("Can'tcallmethodon "+it);
  returnit;
};

/***/}),
/*35*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varMATCH=__w_pdfjs_require__(33)('match');

module.exports=function(KEY){
  varre=/./;

  try{
    '/./'[KEY](re);
  }catch(e){
    try{
      re[MATCH]=false;
      return!'/./'[KEY](re);
    }catch(f){}
  }

  returntrue;
};

/***/}),
/*36*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(37);

module.exports=__w_pdfjs_require__(9).String.endsWith;

/***/}),
/*37*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

vartoLength=__w_pdfjs_require__(28);

varcontext=__w_pdfjs_require__(30);

varENDS_WITH='endsWith';
var$endsWith=''[ENDS_WITH];
$export($export.P+$export.F*__w_pdfjs_require__(35)(ENDS_WITH),'String',{
  endsWith:functionendsWith(searchString){
    varthat=context(this,searchString,ENDS_WITH);
    varendPosition=arguments.length>1?arguments[1]:undefined;
    varlen=toLength(that.length);
    varend=endPosition===undefined?len:Math.min(toLength(endPosition),len);
    varsearch=String(searchString);
    return$endsWith?$endsWith.call(that,search,end):that.slice(end-search.length,end)===search;
  }
});

/***/}),
/*38*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(39);

module.exports=__w_pdfjs_require__(9).String.includes;

/***/}),
/*39*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

varcontext=__w_pdfjs_require__(30);

varINCLUDES='includes';
$export($export.P+$export.F*__w_pdfjs_require__(35)(INCLUDES),'String',{
  includes:functionincludes(searchString){
    return!!~context(this,searchString,INCLUDES).indexOf(searchString,arguments.length>1?arguments[1]:undefined);
  }
});

/***/}),
/*40*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(41);

module.exports=__w_pdfjs_require__(9).Array.includes;

/***/}),
/*41*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

var$includes=__w_pdfjs_require__(42)(true);

$export($export.P,'Array',{
  includes:functionincludes(el){
    return$includes(this,el,arguments.length>1?arguments[1]:undefined);
  }
});

__w_pdfjs_require__(46)('includes');

/***/}),
/*42*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoIObject=__w_pdfjs_require__(43);

vartoLength=__w_pdfjs_require__(28);

vartoAbsoluteIndex=__w_pdfjs_require__(45);

module.exports=function(IS_INCLUDES){
  returnfunction($this,el,fromIndex){
    varO=toIObject($this);
    varlength=toLength(O.length);
    varindex=toAbsoluteIndex(fromIndex,length);
    varvalue;
    if(IS_INCLUDES&&el!=el)while(length>index){
      value=O[index++];
      if(value!=value)returntrue;
    }elsefor(;length>index;index++){
      if(IS_INCLUDES||indexinO){
        if(O[index]===el)returnIS_INCLUDES||index||0;
      }
    }
    return!IS_INCLUDES&&-1;
  };
};

/***/}),
/*43*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varIObject=__w_pdfjs_require__(44);

vardefined=__w_pdfjs_require__(34);

module.exports=function(it){
  returnIObject(defined(it));
};

/***/}),
/*44*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcof=__w_pdfjs_require__(32);

module.exports=Object('z').propertyIsEnumerable(0)?Object:function(it){
  returncof(it)=='String'?it.split(''):Object(it);
};

/***/}),
/*45*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoInteger=__w_pdfjs_require__(29);

varmax=Math.max;
varmin=Math.min;

module.exports=function(index,length){
  index=toInteger(index);
  returnindex<0?max(index+length,0):min(index,length);
};

/***/}),
/*46*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varUNSCOPABLES=__w_pdfjs_require__(33)('unscopables');

varArrayProto=Array.prototype;
if(ArrayProto[UNSCOPABLES]==undefined)__w_pdfjs_require__(10)(ArrayProto,UNSCOPABLES,{});

module.exports=function(key){
  ArrayProto[UNSCOPABLES][key]=true;
};

/***/}),
/*47*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(48);

__w_pdfjs_require__(63);

module.exports=__w_pdfjs_require__(9).Array.from;

/***/}),
/*48*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$at=__w_pdfjs_require__(49)(true);

__w_pdfjs_require__(50)(String,'String',function(iterated){
  this._t=String(iterated);
  this._i=0;
},function(){
  varO=this._t;
  varindex=this._i;
  varpoint;
  if(index>=O.length)return{
    value:undefined,
    done:true
  };
  point=$at(O,index);
  this._i+=point.length;
  return{
    value:point,
    done:false
  };
});

/***/}),
/*49*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoInteger=__w_pdfjs_require__(29);

vardefined=__w_pdfjs_require__(34);

module.exports=function(TO_STRING){
  returnfunction(that,pos){
    vars=String(defined(that));
    vari=toInteger(pos);
    varl=s.length;
    vara,b;
    if(i<0||i>=l)returnTO_STRING?'':undefined;
    a=s.charCodeAt(i);
    returna<0xd800||a>0xdbff||i+1===l||(b=s.charCodeAt(i+1))<0xdc00||b>0xdfff?TO_STRING?s.charAt(i):a:TO_STRING?s.slice(i,i+2):(a-0xd800<<10)+(b-0xdc00)+0x10000;
  };
};

/***/}),
/*50*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varLIBRARY=__w_pdfjs_require__(25);

var$export=__w_pdfjs_require__(7);

varredefine=__w_pdfjs_require__(20);

varhide=__w_pdfjs_require__(10);

varIterators=__w_pdfjs_require__(51);

var$iterCreate=__w_pdfjs_require__(52);

varsetToStringTag=__w_pdfjs_require__(60);

vargetPrototypeOf=__w_pdfjs_require__(61);

varITERATOR=__w_pdfjs_require__(33)('iterator');

varBUGGY=!([].keys&&'next'in[].keys());
varFF_ITERATOR='@@iterator';
varKEYS='keys';
varVALUES='values';

varreturnThis=functionreturnThis(){
  returnthis;
};

module.exports=function(Base,NAME,Constructor,next,DEFAULT,IS_SET,FORCED){
  $iterCreate(Constructor,NAME,next);

  vargetMethod=functiongetMethod(kind){
    if(!BUGGY&&kindinproto)returnproto[kind];

    switch(kind){
      caseKEYS:
        returnfunctionkeys(){
          returnnewConstructor(this,kind);
        };

      caseVALUES:
        returnfunctionvalues(){
          returnnewConstructor(this,kind);
        };
    }

    returnfunctionentries(){
      returnnewConstructor(this,kind);
    };
  };

  varTAG=NAME+'Iterator';
  varDEF_VALUES=DEFAULT==VALUES;
  varVALUES_BUG=false;
  varproto=Base.prototype;
  var$native=proto[ITERATOR]||proto[FF_ITERATOR]||DEFAULT&&proto[DEFAULT];
  var$default=$native||getMethod(DEFAULT);
  var$entries=DEFAULT?!DEF_VALUES?$default:getMethod('entries'):undefined;
  var$anyNative=NAME=='Array'?proto.entries||$native:$native;
  varmethods,key,IteratorPrototype;

  if($anyNative){
    IteratorPrototype=getPrototypeOf($anyNative.call(newBase()));

    if(IteratorPrototype!==Object.prototype&&IteratorPrototype.next){
      setToStringTag(IteratorPrototype,TAG,true);
      if(!LIBRARY&&typeofIteratorPrototype[ITERATOR]!='function')hide(IteratorPrototype,ITERATOR,returnThis);
    }
  }

  if(DEF_VALUES&&$native&&$native.name!==VALUES){
    VALUES_BUG=true;

    $default=functionvalues(){
      return$native.call(this);
    };
  }

  if((!LIBRARY||FORCED)&&(BUGGY||VALUES_BUG||!proto[ITERATOR])){
    hide(proto,ITERATOR,$default);
  }

  Iterators[NAME]=$default;
  Iterators[TAG]=returnThis;

  if(DEFAULT){
    methods={
      values:DEF_VALUES?$default:getMethod(VALUES),
      keys:IS_SET?$default:getMethod(KEYS),
      entries:$entries
    };
    if(FORCED)for(keyinmethods){
      if(!(keyinproto))redefine(proto,key,methods[key]);
    }else$export($export.P+$export.F*(BUGGY||VALUES_BUG),NAME,methods);
  }

  returnmethods;
};

/***/}),
/*51*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports={};

/***/}),
/*52*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcreate=__w_pdfjs_require__(53);

vardescriptor=__w_pdfjs_require__(19);

varsetToStringTag=__w_pdfjs_require__(60);

varIteratorPrototype={};

__w_pdfjs_require__(10)(IteratorPrototype,__w_pdfjs_require__(33)('iterator'),function(){
  returnthis;
});

module.exports=function(Constructor,NAME,next){
  Constructor.prototype=create(IteratorPrototype,{
    next:descriptor(1,next)
  });
  setToStringTag(Constructor,NAME+'Iterator');
};

/***/}),
/*53*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varanObject=__w_pdfjs_require__(12);

vardPs=__w_pdfjs_require__(54);

varenumBugKeys=__w_pdfjs_require__(58);

varIE_PROTO=__w_pdfjs_require__(57)('IE_PROTO');

varEmpty=functionEmpty(){};

varPROTOTYPE='prototype';

var_createDict=functioncreateDict(){
  variframe=__w_pdfjs_require__(17)('iframe');

  vari=enumBugKeys.length;
  varlt='<';
  vargt='>';
  variframeDocument;
  iframe.style.display='none';

  __w_pdfjs_require__(59).appendChild(iframe);

  iframe.src='javascript:';
  iframeDocument=iframe.contentWindow.document;
  iframeDocument.open();
  iframeDocument.write(lt+'script'+gt+'document.F=Object'+lt+'/script'+gt);
  iframeDocument.close();
  _createDict=iframeDocument.F;

  while(i--){
    delete_createDict[PROTOTYPE][enumBugKeys[i]];
  }

  return_createDict();
};

module.exports=Object.create||functioncreate(O,Properties){
  varresult;

  if(O!==null){
    Empty[PROTOTYPE]=anObject(O);
    result=newEmpty();
    Empty[PROTOTYPE]=null;
    result[IE_PROTO]=O;
  }elseresult=_createDict();

  returnProperties===undefined?result:dPs(result,Properties);
};

/***/}),
/*54*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vardP=__w_pdfjs_require__(11);

varanObject=__w_pdfjs_require__(12);

vargetKeys=__w_pdfjs_require__(55);

module.exports=__w_pdfjs_require__(15)?Object.defineProperties:functiondefineProperties(O,Properties){
  anObject(O);
  varkeys=getKeys(Properties);
  varlength=keys.length;
  vari=0;
  varP;

  while(length>i){
    dP.f(O,P=keys[i++],Properties[P]);
  }

  returnO;
};

/***/}),
/*55*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$keys=__w_pdfjs_require__(56);

varenumBugKeys=__w_pdfjs_require__(58);

module.exports=Object.keys||functionkeys(O){
  return$keys(O,enumBugKeys);
};

/***/}),
/*56*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varhas=__w_pdfjs_require__(21);

vartoIObject=__w_pdfjs_require__(43);

vararrayIndexOf=__w_pdfjs_require__(42)(false);

varIE_PROTO=__w_pdfjs_require__(57)('IE_PROTO');

module.exports=function(object,names){
  varO=toIObject(object);
  vari=0;
  varresult=[];
  varkey;

  for(keyinO){
    if(key!=IE_PROTO)has(O,key)&&result.push(key);
  }

  while(names.length>i){
    if(has(O,key=names[i++])){
      ~arrayIndexOf(result,key)||result.push(key);
    }
  }

  returnresult;
};

/***/}),
/*57*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varshared=__w_pdfjs_require__(24)('keys');

varuid=__w_pdfjs_require__(22);

module.exports=function(key){
  returnshared[key]||(shared[key]=uid(key));
};

/***/}),
/*58*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports='constructor,hasOwnProperty,isPrototypeOf,propertyIsEnumerable,toLocaleString,toString,valueOf'.split(',');

/***/}),
/*59*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vardocument=__w_pdfjs_require__(8).document;

module.exports=document&&document.documentElement;

/***/}),
/*60*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vardef=__w_pdfjs_require__(11).f;

varhas=__w_pdfjs_require__(21);

varTAG=__w_pdfjs_require__(33)('toStringTag');

module.exports=function(it,tag,stat){
  if(it&&!has(it=stat?it:it.prototype,TAG))def(it,TAG,{
    configurable:true,
    value:tag
  });
};

/***/}),
/*61*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varhas=__w_pdfjs_require__(21);

vartoObject=__w_pdfjs_require__(62);

varIE_PROTO=__w_pdfjs_require__(57)('IE_PROTO');

varObjectProto=Object.prototype;

module.exports=Object.getPrototypeOf||function(O){
  O=toObject(O);
  if(has(O,IE_PROTO))returnO[IE_PROTO];

  if(typeofO.constructor=='function'&&OinstanceofO.constructor){
    returnO.constructor.prototype;
  }

  returnOinstanceofObject?ObjectProto:null;
};

/***/}),
/*62*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vardefined=__w_pdfjs_require__(34);

module.exports=function(it){
  returnObject(defined(it));
};

/***/}),
/*63*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varctx=__w_pdfjs_require__(26);

var$export=__w_pdfjs_require__(7);

vartoObject=__w_pdfjs_require__(62);

varcall=__w_pdfjs_require__(64);

varisArrayIter=__w_pdfjs_require__(65);

vartoLength=__w_pdfjs_require__(28);

varcreateProperty=__w_pdfjs_require__(66);

vargetIterFn=__w_pdfjs_require__(67);

$export($export.S+$export.F*!__w_pdfjs_require__(69)(function(iter){
  Array.from(iter);
}),'Array',{
  from:functionfrom(arrayLike){
    varO=toObject(arrayLike);
    varC=typeofthis=='function'?this:Array;
    varaLen=arguments.length;
    varmapfn=aLen>1?arguments[1]:undefined;
    varmapping=mapfn!==undefined;
    varindex=0;
    variterFn=getIterFn(O);
    varlength,result,step,iterator;
    if(mapping)mapfn=ctx(mapfn,aLen>2?arguments[2]:undefined,2);

    if(iterFn!=undefined&&!(C==Array&&isArrayIter(iterFn))){
      for(iterator=iterFn.call(O),result=newC();!(step=iterator.next()).done;index++){
        createProperty(result,index,mapping?call(iterator,mapfn,[step.value,index],true):step.value);
      }
    }else{
      length=toLength(O.length);

      for(result=newC(length);length>index;index++){
        createProperty(result,index,mapping?mapfn(O[index],index):O[index]);
      }
    }

    result.length=index;
    returnresult;
  }
});

/***/}),
/*64*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varanObject=__w_pdfjs_require__(12);

module.exports=function(iterator,fn,value,entries){
  try{
    returnentries?fn(anObject(value)[0],value[1]):fn(value);
  }catch(e){
    varret=iterator['return'];
    if(ret!==undefined)anObject(ret.call(iterator));
    throwe;
  }
};

/***/}),
/*65*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varIterators=__w_pdfjs_require__(51);

varITERATOR=__w_pdfjs_require__(33)('iterator');

varArrayProto=Array.prototype;

module.exports=function(it){
  returnit!==undefined&&(Iterators.Array===it||ArrayProto[ITERATOR]===it);
};

/***/}),
/*66*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$defineProperty=__w_pdfjs_require__(11);

varcreateDesc=__w_pdfjs_require__(19);

module.exports=function(object,index,value){
  if(indexinobject)$defineProperty.f(object,index,createDesc(0,value));elseobject[index]=value;
};

/***/}),
/*67*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varclassof=__w_pdfjs_require__(68);

varITERATOR=__w_pdfjs_require__(33)('iterator');

varIterators=__w_pdfjs_require__(51);

module.exports=__w_pdfjs_require__(9).getIteratorMethod=function(it){
  if(it!=undefined)returnit[ITERATOR]||it['@@iterator']||Iterators[classof(it)];
};

/***/}),
/*68*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcof=__w_pdfjs_require__(32);

varTAG=__w_pdfjs_require__(33)('toStringTag');

varARG=cof(function(){
  returnarguments;
}())=='Arguments';

vartryGet=functiontryGet(it,key){
  try{
    returnit[key];
  }catch(e){}
};

module.exports=function(it){
  varO,T,B;
  returnit===undefined?'Undefined':it===null?'Null':typeof(T=tryGet(O=Object(it),TAG))=='string'?T:ARG?cof(O):(B=cof(O))=='Object'&&typeofO.callee=='function'?'Arguments':B;
};

/***/}),
/*69*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varITERATOR=__w_pdfjs_require__(33)('iterator');

varSAFE_CLOSING=false;

try{
  varriter=[7][ITERATOR]();

  riter['return']=function(){
    SAFE_CLOSING=true;
  };

  Array.from(riter,function(){
    throw2;
  });
}catch(e){}

module.exports=function(exec,skipClosing){
  if(!skipClosing&&!SAFE_CLOSING)returnfalse;
  varsafe=false;

  try{
    vararr=[7];
    variter=arr[ITERATOR]();

    iter.next=function(){
      return{
        done:safe=true
      };
    };

    arr[ITERATOR]=function(){
      returniter;
    };

    exec(arr);
  }catch(e){}

  returnsafe;
};

/***/}),
/*70*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(71);

module.exports=__w_pdfjs_require__(9).Object.assign;

/***/}),
/*71*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

$export($export.S+$export.F,'Object',{
  assign:__w_pdfjs_require__(72)
});

/***/}),
/*72*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varDESCRIPTORS=__w_pdfjs_require__(15);

vargetKeys=__w_pdfjs_require__(55);

vargOPS=__w_pdfjs_require__(73);

varpIE=__w_pdfjs_require__(74);

vartoObject=__w_pdfjs_require__(62);

varIObject=__w_pdfjs_require__(44);

var$assign=Object.assign;
module.exports=!$assign||__w_pdfjs_require__(16)(function(){
  varA={};
  varB={};
  varS=Symbol();
  varK='abcdefghijklmnopqrst';
  A[S]=7;
  K.split('').forEach(function(k){
    B[k]=k;
  });
  return$assign({},A)[S]!=7||Object.keys($assign({},B)).join('')!=K;
})?functionassign(target,source){
  varT=toObject(target);
  varaLen=arguments.length;
  varindex=1;
  vargetSymbols=gOPS.f;
  varisEnum=pIE.f;

  while(aLen>index){
    varS=IObject(arguments[index++]);
    varkeys=getSymbols?getKeys(S).concat(getSymbols(S)):getKeys(S);
    varlength=keys.length;
    varj=0;
    varkey;

    while(length>j){
      key=keys[j++];
      if(!DESCRIPTORS||isEnum.call(S,key))T[key]=S[key];
    }
  }

  returnT;
}:$assign;

/***/}),
/*73*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


exports.f=Object.getOwnPropertySymbols;

/***/}),
/*74*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


exports.f={}.propertyIsEnumerable;

/***/}),
/*75*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(76);

module.exports=__w_pdfjs_require__(9).Math.log2;

/***/}),
/*76*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

$export($export.S,'Math',{
  log2:functionlog2(x){
    returnMath.log(x)/Math.LN2;
  }
});

/***/}),
/*77*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(78);

module.exports=__w_pdfjs_require__(9).Number.isNaN;

/***/}),
/*78*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

$export($export.S,'Number',{
  isNaN:functionisNaN(number){
    returnnumber!=number;
  }
});

/***/}),
/*79*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(80);

module.exports=__w_pdfjs_require__(9).Number.isInteger;

/***/}),
/*80*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

$export($export.S,'Number',{
  isInteger:__w_pdfjs_require__(81)
});

/***/}),
/*81*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

varfloor=Math.floor;

module.exports=functionisInteger(it){
  return!isObject(it)&&isFinite(it)&&floor(it)===it;
};

/***/}),
/*82*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(83);

__w_pdfjs_require__(48);

__w_pdfjs_require__(84);

__w_pdfjs_require__(87);

__w_pdfjs_require__(100);

__w_pdfjs_require__(101);

module.exports=__w_pdfjs_require__(9).Promise;

/***/}),
/*83*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varclassof=__w_pdfjs_require__(68);

vartest={};
test[__w_pdfjs_require__(33)('toStringTag')]='z';

if(test+''!='[objectz]'){
  __w_pdfjs_require__(20)(Object.prototype,'toString',functiontoString(){
    return'[object'+classof(this)+']';
  },true);
}

/***/}),
/*84*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$iterators=__w_pdfjs_require__(85);

vargetKeys=__w_pdfjs_require__(55);

varredefine=__w_pdfjs_require__(20);

varglobal=__w_pdfjs_require__(8);

varhide=__w_pdfjs_require__(10);

varIterators=__w_pdfjs_require__(51);

varwks=__w_pdfjs_require__(33);

varITERATOR=wks('iterator');
varTO_STRING_TAG=wks('toStringTag');
varArrayValues=Iterators.Array;
varDOMIterables={
  CSSRuleList:true,
  CSSStyleDeclaration:false,
  CSSValueList:false,
  ClientRectList:false,
  DOMRectList:false,
  DOMStringList:false,
  DOMTokenList:true,
  DataTransferItemList:false,
  FileList:false,
  HTMLAllCollection:false,
  HTMLCollection:false,
  HTMLFormElement:false,
  HTMLSelectElement:false,
  MediaList:true,
  MimeTypeArray:false,
  NamedNodeMap:false,
  NodeList:true,
  PaintRequestList:false,
  Plugin:false,
  PluginArray:false,
  SVGLengthList:false,
  SVGNumberList:false,
  SVGPathSegList:false,
  SVGPointList:false,
  SVGStringList:false,
  SVGTransformList:false,
  SourceBufferList:false,
  StyleSheetList:true,
  TextTrackCueList:false,
  TextTrackList:false,
  TouchList:false
};

for(varcollections=getKeys(DOMIterables),i=0;i<collections.length;i++){
  varNAME=collections[i];
  varexplicit=DOMIterables[NAME];
  varCollection=global[NAME];
  varproto=Collection&&Collection.prototype;
  varkey;

  if(proto){
    if(!proto[ITERATOR])hide(proto,ITERATOR,ArrayValues);
    if(!proto[TO_STRING_TAG])hide(proto,TO_STRING_TAG,NAME);
    Iterators[NAME]=ArrayValues;
    if(explicit)for(keyin$iterators){
      if(!proto[key])redefine(proto,key,$iterators[key],true);
    }
  }
}

/***/}),
/*85*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varaddToUnscopables=__w_pdfjs_require__(46);

varstep=__w_pdfjs_require__(86);

varIterators=__w_pdfjs_require__(51);

vartoIObject=__w_pdfjs_require__(43);

module.exports=__w_pdfjs_require__(50)(Array,'Array',function(iterated,kind){
  this._t=toIObject(iterated);
  this._i=0;
  this._k=kind;
},function(){
  varO=this._t;
  varkind=this._k;
  varindex=this._i++;

  if(!O||index>=O.length){
    this._t=undefined;
    returnstep(1);
  }

  if(kind=='keys')returnstep(0,index);
  if(kind=='values')returnstep(0,O[index]);
  returnstep(0,[index,O[index]]);
},'values');
Iterators.Arguments=Iterators.Array;
addToUnscopables('keys');
addToUnscopables('values');
addToUnscopables('entries');

/***/}),
/*86*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(done,value){
  return{
    value:value,
    done:!!done
  };
};

/***/}),
/*87*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varLIBRARY=__w_pdfjs_require__(25);

varglobal=__w_pdfjs_require__(8);

varctx=__w_pdfjs_require__(26);

varclassof=__w_pdfjs_require__(68);

var$export=__w_pdfjs_require__(7);

varisObject=__w_pdfjs_require__(13);

varaFunction=__w_pdfjs_require__(27);

varanInstance=__w_pdfjs_require__(88);

varforOf=__w_pdfjs_require__(89);

varspeciesConstructor=__w_pdfjs_require__(90);

vartask=__w_pdfjs_require__(91).set;

varmicrotask=__w_pdfjs_require__(93)();

varnewPromiseCapabilityModule=__w_pdfjs_require__(94);

varperform=__w_pdfjs_require__(95);

varuserAgent=__w_pdfjs_require__(96);

varpromiseResolve=__w_pdfjs_require__(97);

varPROMISE='Promise';
varTypeError=global.TypeError;
varprocess=global.process;
varversions=process&&process.versions;
varv8=versions&&versions.v8||'';
var$Promise=global[PROMISE];
varisNode=classof(process)=='process';

varempty=functionempty(){};

varInternal,newGenericPromiseCapability,OwnPromiseCapability,Wrapper;
varnewPromiseCapability=newGenericPromiseCapability=newPromiseCapabilityModule.f;
varUSE_NATIVE=!!function(){
  try{
    varpromise=$Promise.resolve(1);

    varFakePromise=(promise.constructor={})[__w_pdfjs_require__(33)('species')]=function(exec){
      exec(empty,empty);
    };

    return(isNode||typeofPromiseRejectionEvent=='function')&&promise.then(empty)instanceofFakePromise&&v8.indexOf('6.6')!==0&&userAgent.indexOf('Chrome/66')===-1;
  }catch(e){}
}();

varisThenable=functionisThenable(it){
  varthen;
  returnisObject(it)&&typeof(then=it.then)=='function'?then:false;
};

varnotify=functionnotify(promise,isReject){
  if(promise._n)return;
  promise._n=true;
  varchain=promise._c;
  microtask(function(){
    varvalue=promise._v;
    varok=promise._s==1;
    vari=0;

    varrun=functionrun(reaction){
      varhandler=ok?reaction.ok:reaction.fail;
      varresolve=reaction.resolve;
      varreject=reaction.reject;
      vardomain=reaction.domain;
      varresult,then,exited;

      try{
        if(handler){
          if(!ok){
            if(promise._h==2)onHandleUnhandled(promise);
            promise._h=1;
          }

          if(handler===true)result=value;else{
            if(domain)domain.enter();
            result=handler(value);

            if(domain){
              domain.exit();
              exited=true;
            }
          }

          if(result===reaction.promise){
            reject(TypeError('Promise-chaincycle'));
          }elseif(then=isThenable(result)){
            then.call(result,resolve,reject);
          }elseresolve(result);
        }elsereject(value);
      }catch(e){
        if(domain&&!exited)domain.exit();
        reject(e);
      }
    };

    while(chain.length>i){
      run(chain[i++]);
    }

    promise._c=[];
    promise._n=false;
    if(isReject&&!promise._h)onUnhandled(promise);
  });
};

varonUnhandled=functiononUnhandled(promise){
  task.call(global,function(){
    varvalue=promise._v;
    varunhandled=isUnhandled(promise);
    varresult,handler,console;

    if(unhandled){
      result=perform(function(){
        if(isNode){
          process.emit('unhandledRejection',value,promise);
        }elseif(handler=global.onunhandledrejection){
          handler({
            promise:promise,
            reason:value
          });
        }elseif((console=global.console)&&console.error){
          console.error('Unhandledpromiserejection',value);
        }
      });
      promise._h=isNode||isUnhandled(promise)?2:1;
    }

    promise._a=undefined;
    if(unhandled&&result.e)throwresult.v;
  });
};

varisUnhandled=functionisUnhandled(promise){
  returnpromise._h!==1&&(promise._a||promise._c).length===0;
};

varonHandleUnhandled=functiononHandleUnhandled(promise){
  task.call(global,function(){
    varhandler;

    if(isNode){
      process.emit('rejectionHandled',promise);
    }elseif(handler=global.onrejectionhandled){
      handler({
        promise:promise,
        reason:promise._v
      });
    }
  });
};

var$reject=function$reject(value){
  varpromise=this;
  if(promise._d)return;
  promise._d=true;
  promise=promise._w||promise;
  promise._v=value;
  promise._s=2;
  if(!promise._a)promise._a=promise._c.slice();
  notify(promise,true);
};

var$resolve=function$resolve(value){
  varpromise=this;
  varthen;
  if(promise._d)return;
  promise._d=true;
  promise=promise._w||promise;

  try{
    if(promise===value)throwTypeError("Promisecan'tberesolveditself");

    if(then=isThenable(value)){
      microtask(function(){
        varwrapper={
          _w:promise,
          _d:false
        };

        try{
          then.call(value,ctx($resolve,wrapper,1),ctx($reject,wrapper,1));
        }catch(e){
          $reject.call(wrapper,e);
        }
      });
    }else{
      promise._v=value;
      promise._s=1;
      notify(promise,false);
    }
  }catch(e){
    $reject.call({
      _w:promise,
      _d:false
    },e);
  }
};

if(!USE_NATIVE){
  $Promise=functionPromise(executor){
    anInstance(this,$Promise,PROMISE,'_h');
    aFunction(executor);
    Internal.call(this);

    try{
      executor(ctx($resolve,this,1),ctx($reject,this,1));
    }catch(err){
      $reject.call(this,err);
    }
  };

  Internal=functionPromise(executor){
    this._c=[];
    this._a=undefined;
    this._s=0;
    this._d=false;
    this._v=undefined;
    this._h=0;
    this._n=false;
  };

  Internal.prototype=__w_pdfjs_require__(98)($Promise.prototype,{
    then:functionthen(onFulfilled,onRejected){
      varreaction=newPromiseCapability(speciesConstructor(this,$Promise));
      reaction.ok=typeofonFulfilled=='function'?onFulfilled:true;
      reaction.fail=typeofonRejected=='function'&&onRejected;
      reaction.domain=isNode?process.domain:undefined;

      this._c.push(reaction);

      if(this._a)this._a.push(reaction);
      if(this._s)notify(this,false);
      returnreaction.promise;
    },
    'catch':function_catch(onRejected){
      returnthis.then(undefined,onRejected);
    }
  });

  OwnPromiseCapability=functionOwnPromiseCapability(){
    varpromise=newInternal();
    this.promise=promise;
    this.resolve=ctx($resolve,promise,1);
    this.reject=ctx($reject,promise,1);
  };

  newPromiseCapabilityModule.f=newPromiseCapability=functionnewPromiseCapability(C){
    returnC===$Promise||C===Wrapper?newOwnPromiseCapability(C):newGenericPromiseCapability(C);
  };
}

$export($export.G+$export.W+$export.F*!USE_NATIVE,{
  Promise:$Promise
});

__w_pdfjs_require__(60)($Promise,PROMISE);

__w_pdfjs_require__(99)(PROMISE);

Wrapper=__w_pdfjs_require__(9)[PROMISE];
$export($export.S+$export.F*!USE_NATIVE,PROMISE,{
  reject:functionreject(r){
    varcapability=newPromiseCapability(this);
    var$$reject=capability.reject;
    $$reject(r);
    returncapability.promise;
  }
});
$export($export.S+$export.F*(LIBRARY||!USE_NATIVE),PROMISE,{
  resolve:functionresolve(x){
    returnpromiseResolve(LIBRARY&&this===Wrapper?$Promise:this,x);
  }
});
$export($export.S+$export.F*!(USE_NATIVE&&__w_pdfjs_require__(69)(function(iter){
  $Promise.all(iter)['catch'](empty);
})),PROMISE,{
  all:functionall(iterable){
    varC=this;
    varcapability=newPromiseCapability(C);
    varresolve=capability.resolve;
    varreject=capability.reject;
    varresult=perform(function(){
      varvalues=[];
      varindex=0;
      varremaining=1;
      forOf(iterable,false,function(promise){
        var$index=index++;
        varalreadyCalled=false;
        values.push(undefined);
        remaining++;
        C.resolve(promise).then(function(value){
          if(alreadyCalled)return;
          alreadyCalled=true;
          values[$index]=value;
          --remaining||resolve(values);
        },reject);
      });
      --remaining||resolve(values);
    });
    if(result.e)reject(result.v);
    returncapability.promise;
  },
  race:functionrace(iterable){
    varC=this;
    varcapability=newPromiseCapability(C);
    varreject=capability.reject;
    varresult=perform(function(){
      forOf(iterable,false,function(promise){
        C.resolve(promise).then(capability.resolve,reject);
      });
    });
    if(result.e)reject(result.v);
    returncapability.promise;
  }
});

/***/}),
/*88*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(it,Constructor,name,forbiddenField){
  if(!(itinstanceofConstructor)||forbiddenField!==undefined&&forbiddenFieldinit){
    throwTypeError(name+':incorrectinvocation!');
  }

  returnit;
};

/***/}),
/*89*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varctx=__w_pdfjs_require__(26);

varcall=__w_pdfjs_require__(64);

varisArrayIter=__w_pdfjs_require__(65);

varanObject=__w_pdfjs_require__(12);

vartoLength=__w_pdfjs_require__(28);

vargetIterFn=__w_pdfjs_require__(67);

varBREAK={};
varRETURN={};

var_exports=module.exports=function(iterable,entries,fn,that,ITERATOR){
  variterFn=ITERATOR?function(){
    returniterable;
  }:getIterFn(iterable);
  varf=ctx(fn,that,entries?2:1);
  varindex=0;
  varlength,step,iterator,result;
  if(typeofiterFn!='function')throwTypeError(iterable+'isnotiterable!');
  if(isArrayIter(iterFn))for(length=toLength(iterable.length);length>index;index++){
    result=entries?f(anObject(step=iterable[index])[0],step[1]):f(iterable[index]);
    if(result===BREAK||result===RETURN)returnresult;
  }elsefor(iterator=iterFn.call(iterable);!(step=iterator.next()).done;){
    result=call(iterator,f,step.value,entries);
    if(result===BREAK||result===RETURN)returnresult;
  }
};

_exports.BREAK=BREAK;
_exports.RETURN=RETURN;

/***/}),
/*90*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varanObject=__w_pdfjs_require__(12);

varaFunction=__w_pdfjs_require__(27);

varSPECIES=__w_pdfjs_require__(33)('species');

module.exports=function(O,D){
  varC=anObject(O).constructor;
  varS;
  returnC===undefined||(S=anObject(C)[SPECIES])==undefined?D:aFunction(S);
};

/***/}),
/*91*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varctx=__w_pdfjs_require__(26);

varinvoke=__w_pdfjs_require__(92);

varhtml=__w_pdfjs_require__(59);

varcel=__w_pdfjs_require__(17);

varglobal=__w_pdfjs_require__(8);

varprocess=global.process;
varsetTask=global.setImmediate;
varclearTask=global.clearImmediate;
varMessageChannel=global.MessageChannel;
varDispatch=global.Dispatch;
varcounter=0;
varqueue={};
varONREADYSTATECHANGE='onreadystatechange';
vardefer,channel,port;

varrun=functionrun(){
  varid=+this;

  if(queue.hasOwnProperty(id)){
    varfn=queue[id];
    deletequeue[id];
    fn();
  }
};

varlistener=functionlistener(event){
  run.call(event.data);
};

if(!setTask||!clearTask){
  setTask=functionsetImmediate(fn){
    varargs=[];
    vari=1;

    while(arguments.length>i){
      args.push(arguments[i++]);
    }

    queue[++counter]=function(){
      invoke(typeoffn=='function'?fn:Function(fn),args);
    };

    defer(counter);
    returncounter;
  };

  clearTask=functionclearImmediate(id){
    deletequeue[id];
  };

  if(__w_pdfjs_require__(32)(process)=='process'){
    defer=functiondefer(id){
      process.nextTick(ctx(run,id,1));
    };
  }elseif(Dispatch&&Dispatch.now){
    defer=functiondefer(id){
      Dispatch.now(ctx(run,id,1));
    };
  }elseif(MessageChannel){
    channel=newMessageChannel();
    port=channel.port2;
    channel.port1.onmessage=listener;
    defer=ctx(port.postMessage,port,1);
  }elseif(global.addEventListener&&typeofpostMessage=='function'&&!global.importScripts){
    defer=functiondefer(id){
      global.postMessage(id+'','*');
    };

    global.addEventListener('message',listener,false);
  }elseif(ONREADYSTATECHANGEincel('script')){
    defer=functiondefer(id){
      html.appendChild(cel('script'))[ONREADYSTATECHANGE]=function(){
        html.removeChild(this);
        run.call(id);
      };
    };
  }else{
    defer=functiondefer(id){
      setTimeout(ctx(run,id,1),0);
    };
  }
}

module.exports={
  set:setTask,
  clear:clearTask
};

/***/}),
/*92*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(fn,args,that){
  varun=that===undefined;

  switch(args.length){
    case0:
      returnun?fn():fn.call(that);

    case1:
      returnun?fn(args[0]):fn.call(that,args[0]);

    case2:
      returnun?fn(args[0],args[1]):fn.call(that,args[0],args[1]);

    case3:
      returnun?fn(args[0],args[1],args[2]):fn.call(that,args[0],args[1],args[2]);

    case4:
      returnun?fn(args[0],args[1],args[2],args[3]):fn.call(that,args[0],args[1],args[2],args[3]);
  }

  returnfn.apply(that,args);
};

/***/}),
/*93*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

varmacrotask=__w_pdfjs_require__(91).set;

varObserver=global.MutationObserver||global.WebKitMutationObserver;
varprocess=global.process;
varPromise=global.Promise;
varisNode=__w_pdfjs_require__(32)(process)=='process';

module.exports=function(){
  varhead,last,notify;

  varflush=functionflush(){
    varparent,fn;
    if(isNode&&(parent=process.domain))parent.exit();

    while(head){
      fn=head.fn;
      head=head.next;

      try{
        fn();
      }catch(e){
        if(head)notify();elselast=undefined;
        throwe;
      }
    }

    last=undefined;
    if(parent)parent.enter();
  };

  if(isNode){
    notify=functionnotify(){
      process.nextTick(flush);
    };
  }elseif(Observer&&!(global.navigator&&global.navigator.standalone)){
    vartoggle=true;
    varnode=document.createTextNode('');
    newObserver(flush).observe(node,{
      characterData:true
    });

    notify=functionnotify(){
      node.data=toggle=!toggle;
    };
  }elseif(Promise&&Promise.resolve){
    varpromise=Promise.resolve(undefined);

    notify=functionnotify(){
      promise.then(flush);
    };
  }else{
    notify=functionnotify(){
      macrotask.call(global,flush);
    };
  }

  returnfunction(fn){
    vartask={
      fn:fn,
      next:undefined
    };
    if(last)last.next=task;

    if(!head){
      head=task;
      notify();
    }

    last=task;
  };
};

/***/}),
/*94*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varaFunction=__w_pdfjs_require__(27);

functionPromiseCapability(C){
  varresolve,reject;
  this.promise=newC(function($$resolve,$$reject){
    if(resolve!==undefined||reject!==undefined)throwTypeError('BadPromiseconstructor');
    resolve=$$resolve;
    reject=$$reject;
  });
  this.resolve=aFunction(resolve);
  this.reject=aFunction(reject);
}

module.exports.f=function(C){
  returnnewPromiseCapability(C);
};

/***/}),
/*95*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(exec){
  try{
    return{
      e:false,
      v:exec()
    };
  }catch(e){
    return{
      e:true,
      v:e
    };
  }
};

/***/}),
/*96*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

varnavigator=global.navigator;
module.exports=navigator&&navigator.userAgent||'';

/***/}),
/*97*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varanObject=__w_pdfjs_require__(12);

varisObject=__w_pdfjs_require__(13);

varnewPromiseCapability=__w_pdfjs_require__(94);

module.exports=function(C,x){
  anObject(C);
  if(isObject(x)&&x.constructor===C)returnx;
  varpromiseCapability=newPromiseCapability.f(C);
  varresolve=promiseCapability.resolve;
  resolve(x);
  returnpromiseCapability.promise;
};

/***/}),
/*98*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varredefine=__w_pdfjs_require__(20);

module.exports=function(target,src,safe){
  for(varkeyinsrc){
    redefine(target,key,src[key],safe);
  }

  returntarget;
};

/***/}),
/*99*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

vardP=__w_pdfjs_require__(11);

varDESCRIPTORS=__w_pdfjs_require__(15);

varSPECIES=__w_pdfjs_require__(33)('species');

module.exports=function(KEY){
  varC=global[KEY];
  if(DESCRIPTORS&&C&&!C[SPECIES])dP.f(C,SPECIES,{
    configurable:true,
    get:functionget(){
      returnthis;
    }
  });
};

/***/}),
/*100*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

varcore=__w_pdfjs_require__(9);

varglobal=__w_pdfjs_require__(8);

varspeciesConstructor=__w_pdfjs_require__(90);

varpromiseResolve=__w_pdfjs_require__(97);

$export($export.P+$export.R,'Promise',{
  'finally':function_finally(onFinally){
    varC=speciesConstructor(this,core.Promise||global.Promise);
    varisFunction=typeofonFinally=='function';
    returnthis.then(isFunction?function(x){
      returnpromiseResolve(C,onFinally()).then(function(){
        returnx;
      });
    }:onFinally,isFunction?function(e){
      returnpromiseResolve(C,onFinally()).then(function(){
        throwe;
      });
    }:onFinally);
  }
});

/***/}),
/*101*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

varnewPromiseCapability=__w_pdfjs_require__(94);

varperform=__w_pdfjs_require__(95);

$export($export.S,'Promise',{
  'try':function_try(callbackfn){
    varpromiseCapability=newPromiseCapability.f(this);
    varresult=perform(callbackfn);
    (result.e?promiseCapability.reject:promiseCapability.resolve)(result.v);
    returnpromiseCapability.promise;
  }
});

/***/}),
/*102*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(83);

__w_pdfjs_require__(84);

__w_pdfjs_require__(103);

__w_pdfjs_require__(115);

__w_pdfjs_require__(117);

module.exports=__w_pdfjs_require__(9).WeakMap;

/***/}),
/*103*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

vareach=__w_pdfjs_require__(104)(0);

varredefine=__w_pdfjs_require__(20);

varmeta=__w_pdfjs_require__(108);

varassign=__w_pdfjs_require__(72);

varweak=__w_pdfjs_require__(109);

varisObject=__w_pdfjs_require__(13);

varvalidate=__w_pdfjs_require__(110);

varNATIVE_WEAK_MAP=__w_pdfjs_require__(110);

varIS_IE11=!global.ActiveXObject&&'ActiveXObject'inglobal;
varWEAK_MAP='WeakMap';
vargetWeak=meta.getWeak;
varisExtensible=Object.isExtensible;
varuncaughtFrozenStore=weak.ufstore;
varInternalMap;

varwrapper=functionwrapper(get){
  returnfunctionWeakMap(){
    returnget(this,arguments.length>0?arguments[0]:undefined);
  };
};

varmethods={
  get:functionget(key){
    if(isObject(key)){
      vardata=getWeak(key);
      if(data===true)returnuncaughtFrozenStore(validate(this,WEAK_MAP)).get(key);
      returndata?data[this._i]:undefined;
    }
  },
  set:functionset(key,value){
    returnweak.def(validate(this,WEAK_MAP),key,value);
  }
};

var$WeakMap=module.exports=__w_pdfjs_require__(111)(WEAK_MAP,wrapper,methods,weak,true,true);

if(NATIVE_WEAK_MAP&&IS_IE11){
  InternalMap=weak.getConstructor(wrapper,WEAK_MAP);
  assign(InternalMap.prototype,methods);
  meta.NEED=true;
  each(['delete','has','get','set'],function(key){
    varproto=$WeakMap.prototype;
    varmethod=proto[key];
    redefine(proto,key,function(a,b){
      if(isObject(a)&&!isExtensible(a)){
        if(!this._f)this._f=newInternalMap();

        varresult=this._f[key](a,b);

        returnkey=='set'?this:result;
      }

      returnmethod.call(this,a,b);
    });
  });
}

/***/}),
/*104*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varctx=__w_pdfjs_require__(26);

varIObject=__w_pdfjs_require__(44);

vartoObject=__w_pdfjs_require__(62);

vartoLength=__w_pdfjs_require__(28);

varasc=__w_pdfjs_require__(105);

module.exports=function(TYPE,$create){
  varIS_MAP=TYPE==1;
  varIS_FILTER=TYPE==2;
  varIS_SOME=TYPE==3;
  varIS_EVERY=TYPE==4;
  varIS_FIND_INDEX=TYPE==6;
  varNO_HOLES=TYPE==5||IS_FIND_INDEX;
  varcreate=$create||asc;
  returnfunction($this,callbackfn,that){
    varO=toObject($this);
    varself=IObject(O);
    varf=ctx(callbackfn,that,3);
    varlength=toLength(self.length);
    varindex=0;
    varresult=IS_MAP?create($this,length):IS_FILTER?create($this,0):undefined;
    varval,res;

    for(;length>index;index++){
      if(NO_HOLES||indexinself){
        val=self[index];
        res=f(val,index,O);

        if(TYPE){
          if(IS_MAP)result[index]=res;elseif(res)switch(TYPE){
            case3:
              returntrue;

            case5:
              returnval;

            case6:
              returnindex;

            case2:
              result.push(val);
          }elseif(IS_EVERY)returnfalse;
        }
      }
    }

    returnIS_FIND_INDEX?-1:IS_SOME||IS_EVERY?IS_EVERY:result;
  };
};

/***/}),
/*105*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varspeciesConstructor=__w_pdfjs_require__(106);

module.exports=function(original,length){
  returnnew(speciesConstructor(original))(length);
};

/***/}),
/*106*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

varisArray=__w_pdfjs_require__(107);

varSPECIES=__w_pdfjs_require__(33)('species');

module.exports=function(original){
  varC;

  if(isArray(original)){
    C=original.constructor;
    if(typeofC=='function'&&(C===Array||isArray(C.prototype)))C=undefined;

    if(isObject(C)){
      C=C[SPECIES];
      if(C===null)C=undefined;
    }
  }

  returnC===undefined?Array:C;
};

/***/}),
/*107*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcof=__w_pdfjs_require__(32);

module.exports=Array.isArray||functionisArray(arg){
  returncof(arg)=='Array';
};

/***/}),
/*108*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

varMETA=__w_pdfjs_require__(22)('meta');

varisObject=__w_pdfjs_require__(13);

varhas=__w_pdfjs_require__(21);

varsetDesc=__w_pdfjs_require__(11).f;

varid=0;

varisExtensible=Object.isExtensible||function(){
  returntrue;
};

varFREEZE=!__w_pdfjs_require__(16)(function(){
  returnisExtensible(Object.preventExtensions({}));
});

varsetMeta=functionsetMeta(it){
  setDesc(it,META,{
    value:{
      i:'O'+++id,
      w:{}
    }
  });
};

varfastKey=functionfastKey(it,create){
  if(!isObject(it))return_typeof(it)=='symbol'?it:(typeofit=='string'?'S':'P')+it;

  if(!has(it,META)){
    if(!isExtensible(it))return'F';
    if(!create)return'E';
    setMeta(it);
  }

  returnit[META].i;
};

vargetWeak=functiongetWeak(it,create){
  if(!has(it,META)){
    if(!isExtensible(it))returntrue;
    if(!create)returnfalse;
    setMeta(it);
  }

  returnit[META].w;
};

varonFreeze=functiononFreeze(it){
  if(FREEZE&&meta.NEED&&isExtensible(it)&&!has(it,META))setMeta(it);
  returnit;
};

varmeta=module.exports={
  KEY:META,
  NEED:false,
  fastKey:fastKey,
  getWeak:getWeak,
  onFreeze:onFreeze
};

/***/}),
/*109*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varredefineAll=__w_pdfjs_require__(98);

vargetWeak=__w_pdfjs_require__(108).getWeak;

varanObject=__w_pdfjs_require__(12);

varisObject=__w_pdfjs_require__(13);

varanInstance=__w_pdfjs_require__(88);

varforOf=__w_pdfjs_require__(89);

varcreateArrayMethod=__w_pdfjs_require__(104);

var$has=__w_pdfjs_require__(21);

varvalidate=__w_pdfjs_require__(110);

vararrayFind=createArrayMethod(5);
vararrayFindIndex=createArrayMethod(6);
varid=0;

varuncaughtFrozenStore=functionuncaughtFrozenStore(that){
  returnthat._l||(that._l=newUncaughtFrozenStore());
};

varUncaughtFrozenStore=functionUncaughtFrozenStore(){
  this.a=[];
};

varfindUncaughtFrozen=functionfindUncaughtFrozen(store,key){
  returnarrayFind(store.a,function(it){
    returnit[0]===key;
  });
};

UncaughtFrozenStore.prototype={
  get:functionget(key){
    varentry=findUncaughtFrozen(this,key);
    if(entry)returnentry[1];
  },
  has:functionhas(key){
    return!!findUncaughtFrozen(this,key);
  },
  set:functionset(key,value){
    varentry=findUncaughtFrozen(this,key);
    if(entry)entry[1]=value;elsethis.a.push([key,value]);
  },
  'delete':function_delete(key){
    varindex=arrayFindIndex(this.a,function(it){
      returnit[0]===key;
    });
    if(~index)this.a.splice(index,1);
    return!!~index;
  }
};
module.exports={
  getConstructor:functiongetConstructor(wrapper,NAME,IS_MAP,ADDER){
    varC=wrapper(function(that,iterable){
      anInstance(that,C,NAME,'_i');
      that._t=NAME;
      that._i=id++;
      that._l=undefined;
      if(iterable!=undefined)forOf(iterable,IS_MAP,that[ADDER],that);
    });
    redefineAll(C.prototype,{
      'delete':function_delete(key){
        if(!isObject(key))returnfalse;
        vardata=getWeak(key);
        if(data===true)returnuncaughtFrozenStore(validate(this,NAME))['delete'](key);
        returndata&&$has(data,this._i)&&deletedata[this._i];
      },
      has:functionhas(key){
        if(!isObject(key))returnfalse;
        vardata=getWeak(key);
        if(data===true)returnuncaughtFrozenStore(validate(this,NAME)).has(key);
        returndata&&$has(data,this._i);
      }
    });
    returnC;
  },
  def:functiondef(that,key,value){
    vardata=getWeak(anObject(key),true);
    if(data===true)uncaughtFrozenStore(that).set(key,value);elsedata[that._i]=value;
    returnthat;
  },
  ufstore:uncaughtFrozenStore
};

/***/}),
/*110*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

module.exports=function(it,TYPE){
  if(!isObject(it)||it._t!==TYPE)throwTypeError('Incompatiblereceiver,'+TYPE+'required!');
  returnit;
};

/***/}),
/*111*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

var$export=__w_pdfjs_require__(7);

varredefine=__w_pdfjs_require__(20);

varredefineAll=__w_pdfjs_require__(98);

varmeta=__w_pdfjs_require__(108);

varforOf=__w_pdfjs_require__(89);

varanInstance=__w_pdfjs_require__(88);

varisObject=__w_pdfjs_require__(13);

varfails=__w_pdfjs_require__(16);

var$iterDetect=__w_pdfjs_require__(69);

varsetToStringTag=__w_pdfjs_require__(60);

varinheritIfRequired=__w_pdfjs_require__(112);

module.exports=function(NAME,wrapper,methods,common,IS_MAP,IS_WEAK){
  varBase=global[NAME];
  varC=Base;
  varADDER=IS_MAP?'set':'add';
  varproto=C&&C.prototype;
  varO={};

  varfixMethod=functionfixMethod(KEY){
    varfn=proto[KEY];
    redefine(proto,KEY,KEY=='delete'?function(a){
      returnIS_WEAK&&!isObject(a)?false:fn.call(this,a===0?0:a);
    }:KEY=='has'?functionhas(a){
      returnIS_WEAK&&!isObject(a)?false:fn.call(this,a===0?0:a);
    }:KEY=='get'?functionget(a){
      returnIS_WEAK&&!isObject(a)?undefined:fn.call(this,a===0?0:a);
    }:KEY=='add'?functionadd(a){
      fn.call(this,a===0?0:a);
      returnthis;
    }:functionset(a,b){
      fn.call(this,a===0?0:a,b);
      returnthis;
    });
  };

  if(typeofC!='function'||!(IS_WEAK||proto.forEach&&!fails(function(){
    newC().entries().next();
  }))){
    C=common.getConstructor(wrapper,NAME,IS_MAP,ADDER);
    redefineAll(C.prototype,methods);
    meta.NEED=true;
  }else{
    varinstance=newC();
    varHASNT_CHAINING=instance[ADDER](IS_WEAK?{}:-0,1)!=instance;
    varTHROWS_ON_PRIMITIVES=fails(function(){
      instance.has(1);
    });
    varACCEPT_ITERABLES=$iterDetect(function(iter){
      newC(iter);
    });
    varBUGGY_ZERO=!IS_WEAK&&fails(function(){
      var$instance=newC();
      varindex=5;

      while(index--){
        $instance[ADDER](index,index);
      }

      return!$instance.has(-0);
    });

    if(!ACCEPT_ITERABLES){
      C=wrapper(function(target,iterable){
        anInstance(target,C,NAME);
        varthat=inheritIfRequired(newBase(),target,C);
        if(iterable!=undefined)forOf(iterable,IS_MAP,that[ADDER],that);
        returnthat;
      });
      C.prototype=proto;
      proto.constructor=C;
    }

    if(THROWS_ON_PRIMITIVES||BUGGY_ZERO){
      fixMethod('delete');
      fixMethod('has');
      IS_MAP&&fixMethod('get');
    }

    if(BUGGY_ZERO||HASNT_CHAINING)fixMethod(ADDER);
    if(IS_WEAK&&proto.clear)deleteproto.clear;
  }

  setToStringTag(C,NAME);
  O[NAME]=C;
  $export($export.G+$export.W+$export.F*(C!=Base),O);
  if(!IS_WEAK)common.setStrong(C,NAME,IS_MAP);
  returnC;
};

/***/}),
/*112*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

varsetPrototypeOf=__w_pdfjs_require__(113).set;

module.exports=function(that,target,C){
  varS=target.constructor;
  varP;

  if(S!==C&&typeofS=='function'&&(P=S.prototype)!==C.prototype&&isObject(P)&&setPrototypeOf){
    setPrototypeOf(that,P);
  }

  returnthat;
};

/***/}),
/*113*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varisObject=__w_pdfjs_require__(13);

varanObject=__w_pdfjs_require__(12);

varcheck=functioncheck(O,proto){
  anObject(O);
  if(!isObject(proto)&&proto!==null)throwTypeError(proto+":can'tsetasprototype!");
};

module.exports={
  set:Object.setPrototypeOf||('__proto__'in{}?function(test,buggy,set){
    try{
      set=__w_pdfjs_require__(26)(Function.call,__w_pdfjs_require__(114).f(Object.prototype,'__proto__').set,2);
      set(test,[]);
      buggy=!(testinstanceofArray);
    }catch(e){
      buggy=true;
    }

    returnfunctionsetPrototypeOf(O,proto){
      check(O,proto);
      if(buggy)O.__proto__=proto;elseset(O,proto);
      returnO;
    };
  }({},false):undefined),
  check:check
};

/***/}),
/*114*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varpIE=__w_pdfjs_require__(74);

varcreateDesc=__w_pdfjs_require__(19);

vartoIObject=__w_pdfjs_require__(43);

vartoPrimitive=__w_pdfjs_require__(18);

varhas=__w_pdfjs_require__(21);

varIE8_DOM_DEFINE=__w_pdfjs_require__(14);

vargOPD=Object.getOwnPropertyDescriptor;
exports.f=__w_pdfjs_require__(15)?gOPD:functiongetOwnPropertyDescriptor(O,P){
  O=toIObject(O);
  P=toPrimitive(P,true);
  if(IE8_DOM_DEFINE)try{
    returngOPD(O,P);
  }catch(e){}
  if(has(O,P))returncreateDesc(!pIE.f.call(O,P),O[P]);
};

/***/}),
/*115*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(116)('WeakMap');

/***/}),
/*116*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

module.exports=function(COLLECTION){
  $export($export.S,COLLECTION,{
    of:functionof(){
      varlength=arguments.length;
      varA=newArray(length);

      while(length--){
        A[length]=arguments[length];
      }

      returnnewthis(A);
    }
  });
};

/***/}),
/*117*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(118)('WeakMap');

/***/}),
/*118*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

varaFunction=__w_pdfjs_require__(27);

varctx=__w_pdfjs_require__(26);

varforOf=__w_pdfjs_require__(89);

module.exports=function(COLLECTION){
  $export($export.S,COLLECTION,{
    from:functionfrom(source){
      varmapFn=arguments[1];
      varmapping,A,n,cb;
      aFunction(this);
      mapping=mapFn!==undefined;
      if(mapping)aFunction(mapFn);
      if(source==undefined)returnnewthis();
      A=[];

      if(mapping){
        n=0;
        cb=ctx(mapFn,arguments[2],2);
        forOf(source,false,function(nextItem){
          A.push(cb(nextItem,n++));
        });
      }else{
        forOf(source,false,A.push,A);
      }

      returnnewthis(A);
    }
  });
};

/***/}),
/*119*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(83);

__w_pdfjs_require__(84);

__w_pdfjs_require__(120);

__w_pdfjs_require__(121);

__w_pdfjs_require__(122);

module.exports=__w_pdfjs_require__(9).WeakSet;

/***/}),
/*120*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varweak=__w_pdfjs_require__(109);

varvalidate=__w_pdfjs_require__(110);

varWEAK_SET='WeakSet';

__w_pdfjs_require__(111)(WEAK_SET,function(get){
  returnfunctionWeakSet(){
    returnget(this,arguments.length>0?arguments[0]:undefined);
  };
},{
  add:functionadd(value){
    returnweak.def(validate(this,WEAK_SET),value,true);
  }
},weak,false,true);

/***/}),
/*121*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(116)('WeakSet');

/***/}),
/*122*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(118)('WeakSet');

/***/}),
/*123*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(124);

module.exports=__w_pdfjs_require__(9).String.codePointAt;

/***/}),
/*124*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

var$at=__w_pdfjs_require__(49)(false);

$export($export.P,'String',{
  codePointAt:functioncodePointAt(pos){
    return$at(this,pos);
  }
});

/***/}),
/*125*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(126);

module.exports=__w_pdfjs_require__(9).String.fromCodePoint;

/***/}),
/*126*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

vartoAbsoluteIndex=__w_pdfjs_require__(45);

varfromCharCode=String.fromCharCode;
var$fromCodePoint=String.fromCodePoint;
$export($export.S+$export.F*(!!$fromCodePoint&&$fromCodePoint.length!=1),'String',{
  fromCodePoint:functionfromCodePoint(x){
    varres=[];
    varaLen=arguments.length;
    vari=0;
    varcode;

    while(aLen>i){
      code=+arguments[i++];
      if(toAbsoluteIndex(code,0x10ffff)!==code)throwRangeError(code+'isnotavalidcodepoint');
      res.push(code<0x10000?fromCharCode(code):fromCharCode(((code-=0x10000)>>10)+0xd800,code%0x400+0xdc00));
    }

    returnres.join('');
  }
});

/***/}),
/*127*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(128);

__w_pdfjs_require__(83);

module.exports=__w_pdfjs_require__(9).Symbol;

/***/}),
/*128*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

varglobal=__w_pdfjs_require__(8);

varhas=__w_pdfjs_require__(21);

varDESCRIPTORS=__w_pdfjs_require__(15);

var$export=__w_pdfjs_require__(7);

varredefine=__w_pdfjs_require__(20);

varMETA=__w_pdfjs_require__(108).KEY;

var$fails=__w_pdfjs_require__(16);

varshared=__w_pdfjs_require__(24);

varsetToStringTag=__w_pdfjs_require__(60);

varuid=__w_pdfjs_require__(22);

varwks=__w_pdfjs_require__(33);

varwksExt=__w_pdfjs_require__(129);

varwksDefine=__w_pdfjs_require__(130);

varenumKeys=__w_pdfjs_require__(131);

varisArray=__w_pdfjs_require__(107);

varanObject=__w_pdfjs_require__(12);

varisObject=__w_pdfjs_require__(13);

vartoObject=__w_pdfjs_require__(62);

vartoIObject=__w_pdfjs_require__(43);

vartoPrimitive=__w_pdfjs_require__(18);

varcreateDesc=__w_pdfjs_require__(19);

var_create=__w_pdfjs_require__(53);

vargOPNExt=__w_pdfjs_require__(132);

var$GOPD=__w_pdfjs_require__(114);

var$GOPS=__w_pdfjs_require__(73);

var$DP=__w_pdfjs_require__(11);

var$keys=__w_pdfjs_require__(55);

vargOPD=$GOPD.f;
vardP=$DP.f;
vargOPN=gOPNExt.f;
var$Symbol=global.Symbol;
var$JSON=global.JSON;

var_stringify=$JSON&&$JSON.stringify;

varPROTOTYPE='prototype';
varHIDDEN=wks('_hidden');
varTO_PRIMITIVE=wks('toPrimitive');
varisEnum={}.propertyIsEnumerable;
varSymbolRegistry=shared('symbol-registry');
varAllSymbols=shared('symbols');
varOPSymbols=shared('op-symbols');
varObjectProto=Object[PROTOTYPE];
varUSE_NATIVE=typeof$Symbol=='function'&&!!$GOPS.f;
varQObject=global.QObject;
varsetter=!QObject||!QObject[PROTOTYPE]||!QObject[PROTOTYPE].findChild;
varsetSymbolDesc=DESCRIPTORS&&$fails(function(){
  return_create(dP({},'a',{
    get:functionget(){
      returndP(this,'a',{
        value:7
      }).a;
    }
  })).a!=7;
})?function(it,key,D){
  varprotoDesc=gOPD(ObjectProto,key);
  if(protoDesc)deleteObjectProto[key];
  dP(it,key,D);
  if(protoDesc&&it!==ObjectProto)dP(ObjectProto,key,protoDesc);
}:dP;

varwrap=functionwrap(tag){
  varsym=AllSymbols[tag]=_create($Symbol[PROTOTYPE]);

  sym._k=tag;
  returnsym;
};

varisSymbol=USE_NATIVE&&_typeof($Symbol.iterator)=='symbol'?function(it){
  return_typeof(it)=='symbol';
}:function(it){
  returnitinstanceof$Symbol;
};

var$defineProperty=functiondefineProperty(it,key,D){
  if(it===ObjectProto)$defineProperty(OPSymbols,key,D);
  anObject(it);
  key=toPrimitive(key,true);
  anObject(D);

  if(has(AllSymbols,key)){
    if(!D.enumerable){
      if(!has(it,HIDDEN))dP(it,HIDDEN,createDesc(1,{}));
      it[HIDDEN][key]=true;
    }else{
      if(has(it,HIDDEN)&&it[HIDDEN][key])it[HIDDEN][key]=false;
      D=_create(D,{
        enumerable:createDesc(0,false)
      });
    }

    returnsetSymbolDesc(it,key,D);
  }

  returndP(it,key,D);
};

var$defineProperties=functiondefineProperties(it,P){
  anObject(it);
  varkeys=enumKeys(P=toIObject(P));
  vari=0;
  varl=keys.length;
  varkey;

  while(l>i){
    $defineProperty(it,key=keys[i++],P[key]);
  }

  returnit;
};

var$create=functioncreate(it,P){
  returnP===undefined?_create(it):$defineProperties(_create(it),P);
};

var$propertyIsEnumerable=functionpropertyIsEnumerable(key){
  varE=isEnum.call(this,key=toPrimitive(key,true));
  if(this===ObjectProto&&has(AllSymbols,key)&&!has(OPSymbols,key))returnfalse;
  returnE||!has(this,key)||!has(AllSymbols,key)||has(this,HIDDEN)&&this[HIDDEN][key]?E:true;
};

var$getOwnPropertyDescriptor=functiongetOwnPropertyDescriptor(it,key){
  it=toIObject(it);
  key=toPrimitive(key,true);
  if(it===ObjectProto&&has(AllSymbols,key)&&!has(OPSymbols,key))return;
  varD=gOPD(it,key);
  if(D&&has(AllSymbols,key)&&!(has(it,HIDDEN)&&it[HIDDEN][key]))D.enumerable=true;
  returnD;
};

var$getOwnPropertyNames=functiongetOwnPropertyNames(it){
  varnames=gOPN(toIObject(it));
  varresult=[];
  vari=0;
  varkey;

  while(names.length>i){
    if(!has(AllSymbols,key=names[i++])&&key!=HIDDEN&&key!=META)result.push(key);
  }

  returnresult;
};

var$getOwnPropertySymbols=functiongetOwnPropertySymbols(it){
  varIS_OP=it===ObjectProto;
  varnames=gOPN(IS_OP?OPSymbols:toIObject(it));
  varresult=[];
  vari=0;
  varkey;

  while(names.length>i){
    if(has(AllSymbols,key=names[i++])&&(IS_OP?has(ObjectProto,key):true))result.push(AllSymbols[key]);
  }

  returnresult;
};

if(!USE_NATIVE){
  $Symbol=function_Symbol(){
    if(thisinstanceof$Symbol)throwTypeError('Symbolisnotaconstructor!');
    vartag=uid(arguments.length>0?arguments[0]:undefined);

    var$set=function$set(value){
      if(this===ObjectProto)$set.call(OPSymbols,value);
      if(has(this,HIDDEN)&&has(this[HIDDEN],tag))this[HIDDEN][tag]=false;
      setSymbolDesc(this,tag,createDesc(1,value));
    };

    if(DESCRIPTORS&&setter)setSymbolDesc(ObjectProto,tag,{
      configurable:true,
      set:$set
    });
    returnwrap(tag);
  };

  redefine($Symbol[PROTOTYPE],'toString',functiontoString(){
    returnthis._k;
  });
  $GOPD.f=$getOwnPropertyDescriptor;
  $DP.f=$defineProperty;
  __w_pdfjs_require__(133).f=gOPNExt.f=$getOwnPropertyNames;
  __w_pdfjs_require__(74).f=$propertyIsEnumerable;
  $GOPS.f=$getOwnPropertySymbols;

  if(DESCRIPTORS&&!__w_pdfjs_require__(25)){
    redefine(ObjectProto,'propertyIsEnumerable',$propertyIsEnumerable,true);
  }

  wksExt.f=function(name){
    returnwrap(wks(name));
  };
}

$export($export.G+$export.W+$export.F*!USE_NATIVE,{
  Symbol:$Symbol
});

for(vares6Symbols='hasInstance,isConcatSpreadable,iterator,match,replace,search,species,split,toPrimitive,toStringTag,unscopables'.split(','),j=0;es6Symbols.length>j;){
  wks(es6Symbols[j++]);
}

for(varwellKnownSymbols=$keys(wks.store),k=0;wellKnownSymbols.length>k;){
  wksDefine(wellKnownSymbols[k++]);
}

$export($export.S+$export.F*!USE_NATIVE,'Symbol',{
  'for':function_for(key){
    returnhas(SymbolRegistry,key+='')?SymbolRegistry[key]:SymbolRegistry[key]=$Symbol(key);
  },
  keyFor:functionkeyFor(sym){
    if(!isSymbol(sym))throwTypeError(sym+'isnotasymbol!');

    for(varkeyinSymbolRegistry){
      if(SymbolRegistry[key]===sym)returnkey;
    }
  },
  useSetter:functionuseSetter(){
    setter=true;
  },
  useSimple:functionuseSimple(){
    setter=false;
  }
});
$export($export.S+$export.F*!USE_NATIVE,'Object',{
  create:$create,
  defineProperty:$defineProperty,
  defineProperties:$defineProperties,
  getOwnPropertyDescriptor:$getOwnPropertyDescriptor,
  getOwnPropertyNames:$getOwnPropertyNames,
  getOwnPropertySymbols:$getOwnPropertySymbols
});
varFAILS_ON_PRIMITIVES=$fails(function(){
  $GOPS.f(1);
});
$export($export.S+$export.F*FAILS_ON_PRIMITIVES,'Object',{
  getOwnPropertySymbols:functiongetOwnPropertySymbols(it){
    return$GOPS.f(toObject(it));
  }
});
$JSON&&$export($export.S+$export.F*(!USE_NATIVE||$fails(function(){
  varS=$Symbol();
  return_stringify([S])!='[null]'||_stringify({
    a:S
  })!='{}'||_stringify(Object(S))!='{}';
})),'JSON',{
  stringify:functionstringify(it){
    varargs=[it];
    vari=1;
    varreplacer,$replacer;

    while(arguments.length>i){
      args.push(arguments[i++]);
    }

    $replacer=replacer=args[1];
    if(!isObject(replacer)&&it===undefined||isSymbol(it))return;
    if(!isArray(replacer))replacer=functionreplacer(key,value){
      if(typeof$replacer=='function')value=$replacer.call(this,key,value);
      if(!isSymbol(value))returnvalue;
    };
    args[1]=replacer;
    return_stringify.apply($JSON,args);
  }
});
$Symbol[PROTOTYPE][TO_PRIMITIVE]||__w_pdfjs_require__(10)($Symbol[PROTOTYPE],TO_PRIMITIVE,$Symbol[PROTOTYPE].valueOf);
setToStringTag($Symbol,'Symbol');
setToStringTag(Math,'Math',true);
setToStringTag(global.JSON,'JSON',true);

/***/}),
/*129*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


exports.f=__w_pdfjs_require__(33);

/***/}),
/*130*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varglobal=__w_pdfjs_require__(8);

varcore=__w_pdfjs_require__(9);

varLIBRARY=__w_pdfjs_require__(25);

varwksExt=__w_pdfjs_require__(129);

vardefineProperty=__w_pdfjs_require__(11).f;

module.exports=function(name){
  var$Symbol=core.Symbol||(core.Symbol=LIBRARY?{}:global.Symbol||{});
  if(name.charAt(0)!='_'&&!(namein$Symbol))defineProperty($Symbol,name,{
    value:wksExt.f(name)
  });
};

/***/}),
/*131*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vargetKeys=__w_pdfjs_require__(55);

vargOPS=__w_pdfjs_require__(73);

varpIE=__w_pdfjs_require__(74);

module.exports=function(it){
  varresult=getKeys(it);
  vargetSymbols=gOPS.f;

  if(getSymbols){
    varsymbols=getSymbols(it);
    varisEnum=pIE.f;
    vari=0;
    varkey;

    while(symbols.length>i){
      if(isEnum.call(it,key=symbols[i++]))result.push(key);
    }
  }

  returnresult;
};

/***/}),
/*132*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

vartoIObject=__w_pdfjs_require__(43);

vargOPN=__w_pdfjs_require__(133).f;

vartoString={}.toString;
varwindowNames=(typeofwindow==="undefined"?"undefined":_typeof(window))=='object'&&window&&Object.getOwnPropertyNames?Object.getOwnPropertyNames(window):[];

vargetWindowNames=functiongetWindowNames(it){
  try{
    returngOPN(it);
  }catch(e){
    returnwindowNames.slice();
  }
};

module.exports.f=functiongetOwnPropertyNames(it){
  returnwindowNames&&toString.call(it)=='[objectWindow]'?getWindowNames(it):gOPN(toIObject(it));
};

/***/}),
/*133*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$keys=__w_pdfjs_require__(56);

varhiddenKeys=__w_pdfjs_require__(58).concat('length','prototype');

exports.f=Object.getOwnPropertyNames||functiongetOwnPropertyNames(O){
  return$keys(O,hiddenKeys);
};

/***/}),
/*134*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(135);

module.exports=__w_pdfjs_require__(9).String.padStart;

/***/}),
/*135*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

var$pad=__w_pdfjs_require__(136);

varuserAgent=__w_pdfjs_require__(96);

varWEBKIT_BUG=/Version\/10\.\d+(\.\d+)?(Mobile\/\w+)?Safari\//.test(userAgent);
$export($export.P+$export.F*WEBKIT_BUG,'String',{
  padStart:functionpadStart(maxLength){
    return$pad(this,maxLength,arguments.length>1?arguments[1]:undefined,true);
  }
});

/***/}),
/*136*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoLength=__w_pdfjs_require__(28);

varrepeat=__w_pdfjs_require__(137);

vardefined=__w_pdfjs_require__(34);

module.exports=function(that,maxLength,fillString,left){
  varS=String(defined(that));
  varstringLength=S.length;
  varfillStr=fillString===undefined?'':String(fillString);
  varintMaxLength=toLength(maxLength);
  if(intMaxLength<=stringLength||fillStr=='')returnS;
  varfillLen=intMaxLength-stringLength;
  varstringFiller=repeat.call(fillStr,Math.ceil(fillLen/fillStr.length));
  if(stringFiller.length>fillLen)stringFiller=stringFiller.slice(0,fillLen);
  returnleft?stringFiller+S:S+stringFiller;
};

/***/}),
/*137*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


vartoInteger=__w_pdfjs_require__(29);

vardefined=__w_pdfjs_require__(34);

module.exports=functionrepeat(count){
  varstr=String(defined(this));
  varres='';
  varn=toInteger(count);
  if(n<0||n==Infinity)throwRangeError("Countcan'tbenegative");

  for(;n>0;(n>>>=1)&&(str+=str)){
    if(n&1)res+=str;
  }

  returnres;
};

/***/}),
/*138*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(139);

module.exports=__w_pdfjs_require__(9).String.padEnd;

/***/}),
/*139*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

var$pad=__w_pdfjs_require__(136);

varuserAgent=__w_pdfjs_require__(96);

varWEBKIT_BUG=/Version\/10\.\d+(\.\d+)?(Mobile\/\w+)?Safari\//.test(userAgent);
$export($export.P+$export.F*WEBKIT_BUG,'String',{
  padEnd:functionpadEnd(maxLength){
    return$pad(this,maxLength,arguments.length>1?arguments[1]:undefined,false);
  }
});

/***/}),
/*140*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


__w_pdfjs_require__(141);

module.exports=__w_pdfjs_require__(9).Object.values;

/***/}),
/*141*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


var$export=__w_pdfjs_require__(7);

var$values=__w_pdfjs_require__(142)(false);

$export($export.S,'Object',{
  values:functionvalues(it){
    return$values(it);
  }
});

/***/}),
/*142*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varDESCRIPTORS=__w_pdfjs_require__(15);

vargetKeys=__w_pdfjs_require__(55);

vartoIObject=__w_pdfjs_require__(43);

varisEnum=__w_pdfjs_require__(74).f;

module.exports=function(isEntries){
  returnfunction(it){
    varO=toIObject(it);
    varkeys=getKeys(O);
    varlength=keys.length;
    vari=0;
    varresult=[];
    varkey;

    while(length>i){
      key=keys[i++];

      if(!DESCRIPTORS||isEnum.call(O,key)){
        result.push(isEntries?[key,O[key]]:O[key]);
      }
    }

    returnresult;
  };
};

/***/}),
/*143*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


{
  varisReadableStreamSupported=false;

  if(typeofReadableStream!=='undefined'){
    try{
      newReadableStream({
        start:functionstart(controller){
          controller.close();
        }
      });
      isReadableStreamSupported=true;
    }catch(e){}
  }

  if(isReadableStreamSupported){
    exports.ReadableStream=ReadableStream;
  }else{
    exports.ReadableStream=__w_pdfjs_require__(144).ReadableStream;
  }
}

/***/}),
/*144*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof2(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof2=function_typeof2(obj){returntypeofobj;};}else{_typeof2=function_typeof2(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof2(obj);}

(function(e,a){
  for(variina){
    e[i]=a[i];
  }
})(exports,function(modules){
  varinstalledModules={};

  function__w_pdfjs_require__(moduleId){
    if(installedModules[moduleId])returninstalledModules[moduleId].exports;
    varmodule=installedModules[moduleId]={
      i:moduleId,
      l:false,
      exports:{}
    };
    modules[moduleId].call(module.exports,module,module.exports,__w_pdfjs_require__);
    module.l=true;
    returnmodule.exports;
  }

  __w_pdfjs_require__.m=modules;
  __w_pdfjs_require__.c=installedModules;

  __w_pdfjs_require__.i=function(value){
    returnvalue;
  };

  __w_pdfjs_require__.d=function(exports,name,getter){
    if(!__w_pdfjs_require__.o(exports,name)){
      Object.defineProperty(exports,name,{
        configurable:false,
        enumerable:true,
        get:getter
      });
    }
  };

  __w_pdfjs_require__.n=function(module){
    vargetter=module&&module.__esModule?functiongetDefault(){
      returnmodule['default'];
    }:functiongetModuleExports(){
      returnmodule;
    };

    __w_pdfjs_require__.d(getter,'a',getter);

    returngetter;
  };

  __w_pdfjs_require__.o=function(object,property){
    returnObject.prototype.hasOwnProperty.call(object,property);
  };

  __w_pdfjs_require__.p="";
  return__w_pdfjs_require__(__w_pdfjs_require__.s=7);
}([function(module,exports,__w_pdfjs_require__){
  "usestrict";

  var_typeof=typeofSymbol==="function"&&_typeof2(Symbol.iterator)==="symbol"?function(obj){
    return_typeof2(obj);
  }:function(obj){
    returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":_typeof2(obj);
  };

  var_require=__w_pdfjs_require__(1),
      assert=_require.assert;

  functionIsPropertyKey(argument){
    returntypeofargument==='string'||(typeofargument==='undefined'?'undefined':_typeof(argument))==='symbol';
  }

  exports.typeIsObject=function(x){
    return(typeofx==='undefined'?'undefined':_typeof(x))==='object'&&x!==null||typeofx==='function';
  };

  exports.createDataProperty=function(o,p,v){
    assert(exports.typeIsObject(o));
    Object.defineProperty(o,p,{
      value:v,
      writable:true,
      enumerable:true,
      configurable:true
    });
  };

  exports.createArrayFromList=function(elements){
    returnelements.slice();
  };

  exports.ArrayBufferCopy=function(dest,destOffset,src,srcOffset,n){
    newUint8Array(dest).set(newUint8Array(src,srcOffset,n),destOffset);
  };

  exports.CreateIterResultObject=function(value,done){
    assert(typeofdone==='boolean');
    varobj={};
    Object.defineProperty(obj,'value',{
      value:value,
      enumerable:true,
      writable:true,
      configurable:true
    });
    Object.defineProperty(obj,'done',{
      value:done,
      enumerable:true,
      writable:true,
      configurable:true
    });
    returnobj;
  };

  exports.IsFiniteNonNegativeNumber=function(v){
    if(Number.isNaN(v)){
      returnfalse;
    }

    if(v===Infinity){
      returnfalse;
    }

    if(v<0){
      returnfalse;
    }

    returntrue;
  };

  functionCall(F,V,args){
    if(typeofF!=='function'){
      thrownewTypeError('Argumentisnotafunction');
    }

    returnFunction.prototype.apply.call(F,V,args);
  }

  exports.InvokeOrNoop=function(O,P,args){
    assert(O!==undefined);
    assert(IsPropertyKey(P));
    assert(Array.isArray(args));
    varmethod=O[P];

    if(method===undefined){
      returnundefined;
    }

    returnCall(method,O,args);
  };

  exports.PromiseInvokeOrNoop=function(O,P,args){
    assert(O!==undefined);
    assert(IsPropertyKey(P));
    assert(Array.isArray(args));

    try{
      returnPromise.resolve(exports.InvokeOrNoop(O,P,args));
    }catch(returnValueE){
      returnPromise.reject(returnValueE);
    }
  };

  exports.PromiseInvokeOrPerformFallback=function(O,P,args,F,argsF){
    assert(O!==undefined);
    assert(IsPropertyKey(P));
    assert(Array.isArray(args));
    assert(Array.isArray(argsF));
    varmethod=void0;

    try{
      method=O[P];
    }catch(methodE){
      returnPromise.reject(methodE);
    }

    if(method===undefined){
      returnF.apply(null,argsF);
    }

    try{
      returnPromise.resolve(Call(method,O,args));
    }catch(e){
      returnPromise.reject(e);
    }
  };

  exports.TransferArrayBuffer=function(O){
    returnO.slice();
  };

  exports.ValidateAndNormalizeHighWaterMark=function(highWaterMark){
    highWaterMark=Number(highWaterMark);

    if(Number.isNaN(highWaterMark)||highWaterMark<0){
      thrownewRangeError('highWaterMarkpropertyofaqueuingstrategymustbenon-negativeandnon-NaN');
    }

    returnhighWaterMark;
  };

  exports.ValidateAndNormalizeQueuingStrategy=function(size,highWaterMark){
    if(size!==undefined&&typeofsize!=='function'){
      thrownewTypeError('sizepropertyofaqueuingstrategymustbeafunction');
    }

    highWaterMark=exports.ValidateAndNormalizeHighWaterMark(highWaterMark);
    return{
      size:size,
      highWaterMark:highWaterMark
    };
  };
},function(module,exports,__w_pdfjs_require__){
  "usestrict";

  functionrethrowAssertionErrorRejection(e){
    if(e&&e.constructor===AssertionError){
      setTimeout(function(){
        throwe;
      },0);
    }
  }

  functionAssertionError(message){
    this.name='AssertionError';
    this.message=message||'';
    this.stack=newError().stack;
  }

  AssertionError.prototype=Object.create(Error.prototype);
  AssertionError.prototype.constructor=AssertionError;

  functionassert(value,message){
    if(!value){
      thrownewAssertionError(message);
    }
  }

  module.exports={
    rethrowAssertionErrorRejection:rethrowAssertionErrorRejection,
    AssertionError:AssertionError,
    assert:assert
  };
},function(module,exports,__w_pdfjs_require__){
  "usestrict";

  var_createClass=function(){
    functiondefineProperties(target,props){
      for(vari=0;i<props.length;i++){
        vardescriptor=props[i];
        descriptor.enumerable=descriptor.enumerable||false;
        descriptor.configurable=true;
        if("value"indescriptor)descriptor.writable=true;
        Object.defineProperty(target,descriptor.key,descriptor);
      }
    }

    returnfunction(Constructor,protoProps,staticProps){
      if(protoProps)defineProperties(Constructor.prototype,protoProps);
      if(staticProps)defineProperties(Constructor,staticProps);
      returnConstructor;
    };
  }();

  function_classCallCheck(instance,Constructor){
    if(!(instanceinstanceofConstructor)){
      thrownewTypeError("Cannotcallaclassasafunction");
    }
  }

  var_require=__w_pdfjs_require__(0),
      InvokeOrNoop=_require.InvokeOrNoop,
      PromiseInvokeOrNoop=_require.PromiseInvokeOrNoop,
      ValidateAndNormalizeQueuingStrategy=_require.ValidateAndNormalizeQueuingStrategy,
      typeIsObject=_require.typeIsObject;

  var_require2=__w_pdfjs_require__(1),
      assert=_require2.assert,
      rethrowAssertionErrorRejection=_require2.rethrowAssertionErrorRejection;

  var_require3=__w_pdfjs_require__(3),
      DequeueValue=_require3.DequeueValue,
      EnqueueValueWithSize=_require3.EnqueueValueWithSize,
      PeekQueueValue=_require3.PeekQueueValue,
      ResetQueue=_require3.ResetQueue;

  varWritableStream=function(){
    functionWritableStream(){
      varunderlyingSink=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};

      var_ref=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{},
          size=_ref.size,
          _ref$highWaterMark=_ref.highWaterMark,
          highWaterMark=_ref$highWaterMark===undefined?1:_ref$highWaterMark;

      _classCallCheck(this,WritableStream);

      this._state='writable';
      this._storedError=undefined;
      this._writer=undefined;
      this._writableStreamController=undefined;
      this._writeRequests=[];
      this._inFlightWriteRequest=undefined;
      this._closeRequest=undefined;
      this._inFlightCloseRequest=undefined;
      this._pendingAbortRequest=undefined;
      this._backpressure=false;
      vartype=underlyingSink.type;

      if(type!==undefined){
        thrownewRangeError('Invalidtypeisspecified');
      }

      this._writableStreamController=newWritableStreamDefaultController(this,underlyingSink,size,highWaterMark);

      this._writableStreamController.__startSteps();
    }

    _createClass(WritableStream,[{
      key:'abort',
      value:functionabort(reason){
        if(IsWritableStream(this)===false){
          returnPromise.reject(streamBrandCheckException('abort'));
        }

        if(IsWritableStreamLocked(this)===true){
          returnPromise.reject(newTypeError('Cannotabortastreamthatalreadyhasawriter'));
        }

        returnWritableStreamAbort(this,reason);
      }
    },{
      key:'getWriter',
      value:functiongetWriter(){
        if(IsWritableStream(this)===false){
          throwstreamBrandCheckException('getWriter');
        }

        returnAcquireWritableStreamDefaultWriter(this);
      }
    },{
      key:'locked',
      get:functionget(){
        if(IsWritableStream(this)===false){
          throwstreamBrandCheckException('locked');
        }

        returnIsWritableStreamLocked(this);
      }
    }]);

    returnWritableStream;
  }();

  module.exports={
    AcquireWritableStreamDefaultWriter:AcquireWritableStreamDefaultWriter,
    IsWritableStream:IsWritableStream,
    IsWritableStreamLocked:IsWritableStreamLocked,
    WritableStream:WritableStream,
    WritableStreamAbort:WritableStreamAbort,
    WritableStreamDefaultControllerError:WritableStreamDefaultControllerError,
    WritableStreamDefaultWriterCloseWithErrorPropagation:WritableStreamDefaultWriterCloseWithErrorPropagation,
    WritableStreamDefaultWriterRelease:WritableStreamDefaultWriterRelease,
    WritableStreamDefaultWriterWrite:WritableStreamDefaultWriterWrite,
    WritableStreamCloseQueuedOrInFlight:WritableStreamCloseQueuedOrInFlight
  };

  functionAcquireWritableStreamDefaultWriter(stream){
    returnnewWritableStreamDefaultWriter(stream);
  }

  functionIsWritableStream(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_writableStreamController')){
      returnfalse;
    }

    returntrue;
  }

  functionIsWritableStreamLocked(stream){
    assert(IsWritableStream(stream)===true,'IsWritableStreamLockedshouldonlybeusedonknownwritablestreams');

    if(stream._writer===undefined){
      returnfalse;
    }

    returntrue;
  }

  functionWritableStreamAbort(stream,reason){
    varstate=stream._state;

    if(state==='closed'){
      returnPromise.resolve(undefined);
    }

    if(state==='errored'){
      returnPromise.reject(stream._storedError);
    }

    varerror=newTypeError('Requestedtoabort');

    if(stream._pendingAbortRequest!==undefined){
      returnPromise.reject(error);
    }

    assert(state==='writable'||state==='erroring','statemustbewritableorerroring');
    varwasAlreadyErroring=false;

    if(state==='erroring'){
      wasAlreadyErroring=true;
      reason=undefined;
    }

    varpromise=newPromise(function(resolve,reject){
      stream._pendingAbortRequest={
        _resolve:resolve,
        _reject:reject,
        _reason:reason,
        _wasAlreadyErroring:wasAlreadyErroring
      };
    });

    if(wasAlreadyErroring===false){
      WritableStreamStartErroring(stream,error);
    }

    returnpromise;
  }

  functionWritableStreamAddWriteRequest(stream){
    assert(IsWritableStreamLocked(stream)===true);
    assert(stream._state==='writable');
    varpromise=newPromise(function(resolve,reject){
      varwriteRequest={
        _resolve:resolve,
        _reject:reject
      };

      stream._writeRequests.push(writeRequest);
    });
    returnpromise;
  }

  functionWritableStreamDealWithRejection(stream,error){
    varstate=stream._state;

    if(state==='writable'){
      WritableStreamStartErroring(stream,error);
      return;
    }

    assert(state==='erroring');
    WritableStreamFinishErroring(stream);
  }

  functionWritableStreamStartErroring(stream,reason){
    assert(stream._storedError===undefined,'stream._storedError===undefined');
    assert(stream._state==='writable','statemustbewritable');
    varcontroller=stream._writableStreamController;
    assert(controller!==undefined,'controllermustnotbeundefined');
    stream._state='erroring';
    stream._storedError=reason;
    varwriter=stream._writer;

    if(writer!==undefined){
      WritableStreamDefaultWriterEnsureReadyPromiseRejected(writer,reason);
    }

    if(WritableStreamHasOperationMarkedInFlight(stream)===false&&controller._started===true){
      WritableStreamFinishErroring(stream);
    }
  }

  functionWritableStreamFinishErroring(stream){
    assert(stream._state==='erroring','stream._state===erroring');
    assert(WritableStreamHasOperationMarkedInFlight(stream)===false,'WritableStreamHasOperationMarkedInFlight(stream)===false');
    stream._state='errored';

    stream._writableStreamController.__errorSteps();

    varstoredError=stream._storedError;

    for(vari=0;i<stream._writeRequests.length;i++){
      varwriteRequest=stream._writeRequests[i];

      writeRequest._reject(storedError);
    }

    stream._writeRequests=[];

    if(stream._pendingAbortRequest===undefined){
      WritableStreamRejectCloseAndClosedPromiseIfNeeded(stream);
      return;
    }

    varabortRequest=stream._pendingAbortRequest;
    stream._pendingAbortRequest=undefined;

    if(abortRequest._wasAlreadyErroring===true){
      abortRequest._reject(storedError);

      WritableStreamRejectCloseAndClosedPromiseIfNeeded(stream);
      return;
    }

    varpromise=stream._writableStreamController.__abortSteps(abortRequest._reason);

    promise.then(function(){
      abortRequest._resolve();

      WritableStreamRejectCloseAndClosedPromiseIfNeeded(stream);
    },function(reason){
      abortRequest._reject(reason);

      WritableStreamRejectCloseAndClosedPromiseIfNeeded(stream);
    });
  }

  functionWritableStreamFinishInFlightWrite(stream){
    assert(stream._inFlightWriteRequest!==undefined);

    stream._inFlightWriteRequest._resolve(undefined);

    stream._inFlightWriteRequest=undefined;
  }

  functionWritableStreamFinishInFlightWriteWithError(stream,error){
    assert(stream._inFlightWriteRequest!==undefined);

    stream._inFlightWriteRequest._reject(error);

    stream._inFlightWriteRequest=undefined;
    assert(stream._state==='writable'||stream._state==='erroring');
    WritableStreamDealWithRejection(stream,error);
  }

  functionWritableStreamFinishInFlightClose(stream){
    assert(stream._inFlightCloseRequest!==undefined);

    stream._inFlightCloseRequest._resolve(undefined);

    stream._inFlightCloseRequest=undefined;
    varstate=stream._state;
    assert(state==='writable'||state==='erroring');

    if(state==='erroring'){
      stream._storedError=undefined;

      if(stream._pendingAbortRequest!==undefined){
        stream._pendingAbortRequest._resolve();

        stream._pendingAbortRequest=undefined;
      }
    }

    stream._state='closed';
    varwriter=stream._writer;

    if(writer!==undefined){
      defaultWriterClosedPromiseResolve(writer);
    }

    assert(stream._pendingAbortRequest===undefined,'stream._pendingAbortRequest===undefined');
    assert(stream._storedError===undefined,'stream._storedError===undefined');
  }

  functionWritableStreamFinishInFlightCloseWithError(stream,error){
    assert(stream._inFlightCloseRequest!==undefined);

    stream._inFlightCloseRequest._reject(error);

    stream._inFlightCloseRequest=undefined;
    assert(stream._state==='writable'||stream._state==='erroring');

    if(stream._pendingAbortRequest!==undefined){
      stream._pendingAbortRequest._reject(error);

      stream._pendingAbortRequest=undefined;
    }

    WritableStreamDealWithRejection(stream,error);
  }

  functionWritableStreamCloseQueuedOrInFlight(stream){
    if(stream._closeRequest===undefined&&stream._inFlightCloseRequest===undefined){
      returnfalse;
    }

    returntrue;
  }

  functionWritableStreamHasOperationMarkedInFlight(stream){
    if(stream._inFlightWriteRequest===undefined&&stream._inFlightCloseRequest===undefined){
      returnfalse;
    }

    returntrue;
  }

  functionWritableStreamMarkCloseRequestInFlight(stream){
    assert(stream._inFlightCloseRequest===undefined);
    assert(stream._closeRequest!==undefined);
    stream._inFlightCloseRequest=stream._closeRequest;
    stream._closeRequest=undefined;
  }

  functionWritableStreamMarkFirstWriteRequestInFlight(stream){
    assert(stream._inFlightWriteRequest===undefined,'theremustbenopendingwriterequest');
    assert(stream._writeRequests.length!==0,'writeRequestsmustnotbeempty');
    stream._inFlightWriteRequest=stream._writeRequests.shift();
  }

  functionWritableStreamRejectCloseAndClosedPromiseIfNeeded(stream){
    assert(stream._state==='errored','_stream_.[[state]]is`"errored"`');

    if(stream._closeRequest!==undefined){
      assert(stream._inFlightCloseRequest===undefined);

      stream._closeRequest._reject(stream._storedError);

      stream._closeRequest=undefined;
    }

    varwriter=stream._writer;

    if(writer!==undefined){
      defaultWriterClosedPromiseReject(writer,stream._storedError);

      writer._closedPromise["catch"](function(){});
    }
  }

  functionWritableStreamUpdateBackpressure(stream,backpressure){
    assert(stream._state==='writable');
    assert(WritableStreamCloseQueuedOrInFlight(stream)===false);
    varwriter=stream._writer;

    if(writer!==undefined&&backpressure!==stream._backpressure){
      if(backpressure===true){
        defaultWriterReadyPromiseReset(writer);
      }else{
        assert(backpressure===false);
        defaultWriterReadyPromiseResolve(writer);
      }
    }

    stream._backpressure=backpressure;
  }

  varWritableStreamDefaultWriter=function(){
    functionWritableStreamDefaultWriter(stream){
      _classCallCheck(this,WritableStreamDefaultWriter);

      if(IsWritableStream(stream)===false){
        thrownewTypeError('WritableStreamDefaultWritercanonlybeconstructedwithaWritableStreaminstance');
      }

      if(IsWritableStreamLocked(stream)===true){
        thrownewTypeError('Thisstreamhasalreadybeenlockedforexclusivewritingbyanotherwriter');
      }

      this._ownerWritableStream=stream;
      stream._writer=this;
      varstate=stream._state;

      if(state==='writable'){
        if(WritableStreamCloseQueuedOrInFlight(stream)===false&&stream._backpressure===true){
          defaultWriterReadyPromiseInitialize(this);
        }else{
          defaultWriterReadyPromiseInitializeAsResolved(this);
        }

        defaultWriterClosedPromiseInitialize(this);
      }elseif(state==='erroring'){
        defaultWriterReadyPromiseInitializeAsRejected(this,stream._storedError);

        this._readyPromise["catch"](function(){});

        defaultWriterClosedPromiseInitialize(this);
      }elseif(state==='closed'){
        defaultWriterReadyPromiseInitializeAsResolved(this);
        defaultWriterClosedPromiseInitializeAsResolved(this);
      }else{
        assert(state==='errored','statemustbeerrored');
        varstoredError=stream._storedError;
        defaultWriterReadyPromiseInitializeAsRejected(this,storedError);

        this._readyPromise["catch"](function(){});

        defaultWriterClosedPromiseInitializeAsRejected(this,storedError);

        this._closedPromise["catch"](function(){});
      }
    }

    _createClass(WritableStreamDefaultWriter,[{
      key:'abort',
      value:functionabort(reason){
        if(IsWritableStreamDefaultWriter(this)===false){
          returnPromise.reject(defaultWriterBrandCheckException('abort'));
        }

        if(this._ownerWritableStream===undefined){
          returnPromise.reject(defaultWriterLockException('abort'));
        }

        returnWritableStreamDefaultWriterAbort(this,reason);
      }
    },{
      key:'close',
      value:functionclose(){
        if(IsWritableStreamDefaultWriter(this)===false){
          returnPromise.reject(defaultWriterBrandCheckException('close'));
        }

        varstream=this._ownerWritableStream;

        if(stream===undefined){
          returnPromise.reject(defaultWriterLockException('close'));
        }

        if(WritableStreamCloseQueuedOrInFlight(stream)===true){
          returnPromise.reject(newTypeError('cannotcloseanalready-closingstream'));
        }

        returnWritableStreamDefaultWriterClose(this);
      }
    },{
      key:'releaseLock',
      value:functionreleaseLock(){
        if(IsWritableStreamDefaultWriter(this)===false){
          throwdefaultWriterBrandCheckException('releaseLock');
        }

        varstream=this._ownerWritableStream;

        if(stream===undefined){
          return;
        }

        assert(stream._writer!==undefined);
        WritableStreamDefaultWriterRelease(this);
      }
    },{
      key:'write',
      value:functionwrite(chunk){
        if(IsWritableStreamDefaultWriter(this)===false){
          returnPromise.reject(defaultWriterBrandCheckException('write'));
        }

        if(this._ownerWritableStream===undefined){
          returnPromise.reject(defaultWriterLockException('writeto'));
        }

        returnWritableStreamDefaultWriterWrite(this,chunk);
      }
    },{
      key:'closed',
      get:functionget(){
        if(IsWritableStreamDefaultWriter(this)===false){
          returnPromise.reject(defaultWriterBrandCheckException('closed'));
        }

        returnthis._closedPromise;
      }
    },{
      key:'desiredSize',
      get:functionget(){
        if(IsWritableStreamDefaultWriter(this)===false){
          throwdefaultWriterBrandCheckException('desiredSize');
        }

        if(this._ownerWritableStream===undefined){
          throwdefaultWriterLockException('desiredSize');
        }

        returnWritableStreamDefaultWriterGetDesiredSize(this);
      }
    },{
      key:'ready',
      get:functionget(){
        if(IsWritableStreamDefaultWriter(this)===false){
          returnPromise.reject(defaultWriterBrandCheckException('ready'));
        }

        returnthis._readyPromise;
      }
    }]);

    returnWritableStreamDefaultWriter;
  }();

  functionIsWritableStreamDefaultWriter(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_ownerWritableStream')){
      returnfalse;
    }

    returntrue;
  }

  functionWritableStreamDefaultWriterAbort(writer,reason){
    varstream=writer._ownerWritableStream;
    assert(stream!==undefined);
    returnWritableStreamAbort(stream,reason);
  }

  functionWritableStreamDefaultWriterClose(writer){
    varstream=writer._ownerWritableStream;
    assert(stream!==undefined);
    varstate=stream._state;

    if(state==='closed'||state==='errored'){
      returnPromise.reject(newTypeError('Thestream(in'+state+'state)isnotinthewritablestateandcannotbeclosed'));
    }

    assert(state==='writable'||state==='erroring');
    assert(WritableStreamCloseQueuedOrInFlight(stream)===false);
    varpromise=newPromise(function(resolve,reject){
      varcloseRequest={
        _resolve:resolve,
        _reject:reject
      };
      stream._closeRequest=closeRequest;
    });

    if(stream._backpressure===true&&state==='writable'){
      defaultWriterReadyPromiseResolve(writer);
    }

    WritableStreamDefaultControllerClose(stream._writableStreamController);
    returnpromise;
  }

  functionWritableStreamDefaultWriterCloseWithErrorPropagation(writer){
    varstream=writer._ownerWritableStream;
    assert(stream!==undefined);
    varstate=stream._state;

    if(WritableStreamCloseQueuedOrInFlight(stream)===true||state==='closed'){
      returnPromise.resolve();
    }

    if(state==='errored'){
      returnPromise.reject(stream._storedError);
    }

    assert(state==='writable'||state==='erroring');
    returnWritableStreamDefaultWriterClose(writer);
  }

  functionWritableStreamDefaultWriterEnsureClosedPromiseRejected(writer,error){
    if(writer._closedPromiseState==='pending'){
      defaultWriterClosedPromiseReject(writer,error);
    }else{
      defaultWriterClosedPromiseResetToRejected(writer,error);
    }

    writer._closedPromise["catch"](function(){});
  }

  functionWritableStreamDefaultWriterEnsureReadyPromiseRejected(writer,error){
    if(writer._readyPromiseState==='pending'){
      defaultWriterReadyPromiseReject(writer,error);
    }else{
      defaultWriterReadyPromiseResetToRejected(writer,error);
    }

    writer._readyPromise["catch"](function(){});
  }

  functionWritableStreamDefaultWriterGetDesiredSize(writer){
    varstream=writer._ownerWritableStream;
    varstate=stream._state;

    if(state==='errored'||state==='erroring'){
      returnnull;
    }

    if(state==='closed'){
      return0;
    }

    returnWritableStreamDefaultControllerGetDesiredSize(stream._writableStreamController);
  }

  functionWritableStreamDefaultWriterRelease(writer){
    varstream=writer._ownerWritableStream;
    assert(stream!==undefined);
    assert(stream._writer===writer);
    varreleasedError=newTypeError('Writerwasreleasedandcannolongerbeusedtomonitorthestream\'sclosedness');
    WritableStreamDefaultWriterEnsureReadyPromiseRejected(writer,releasedError);
    WritableStreamDefaultWriterEnsureClosedPromiseRejected(writer,releasedError);
    stream._writer=undefined;
    writer._ownerWritableStream=undefined;
  }

  functionWritableStreamDefaultWriterWrite(writer,chunk){
    varstream=writer._ownerWritableStream;
    assert(stream!==undefined);
    varcontroller=stream._writableStreamController;
    varchunkSize=WritableStreamDefaultControllerGetChunkSize(controller,chunk);

    if(stream!==writer._ownerWritableStream){
      returnPromise.reject(defaultWriterLockException('writeto'));
    }

    varstate=stream._state;

    if(state==='errored'){
      returnPromise.reject(stream._storedError);
    }

    if(WritableStreamCloseQueuedOrInFlight(stream)===true||state==='closed'){
      returnPromise.reject(newTypeError('Thestreamisclosingorclosedandcannotbewrittento'));
    }

    if(state==='erroring'){
      returnPromise.reject(stream._storedError);
    }

    assert(state==='writable');
    varpromise=WritableStreamAddWriteRequest(stream);
    WritableStreamDefaultControllerWrite(controller,chunk,chunkSize);
    returnpromise;
  }

  varWritableStreamDefaultController=function(){
    functionWritableStreamDefaultController(stream,underlyingSink,size,highWaterMark){
      _classCallCheck(this,WritableStreamDefaultController);

      if(IsWritableStream(stream)===false){
        thrownewTypeError('WritableStreamDefaultControllercanonlybeconstructedwithaWritableStreaminstance');
      }

      if(stream._writableStreamController!==undefined){
        thrownewTypeError('WritableStreamDefaultControllerinstancescanonlybecreatedbytheWritableStreamconstructor');
      }

      this._controlledWritableStream=stream;
      this._underlyingSink=underlyingSink;
      this._queue=undefined;
      this._queueTotalSize=undefined;
      ResetQueue(this);
      this._started=false;
      varnormalizedStrategy=ValidateAndNormalizeQueuingStrategy(size,highWaterMark);
      this._strategySize=normalizedStrategy.size;
      this._strategyHWM=normalizedStrategy.highWaterMark;
      varbackpressure=WritableStreamDefaultControllerGetBackpressure(this);
      WritableStreamUpdateBackpressure(stream,backpressure);
    }

    _createClass(WritableStreamDefaultController,[{
      key:'error',
      value:functionerror(e){
        if(IsWritableStreamDefaultController(this)===false){
          thrownewTypeError('WritableStreamDefaultController.prototype.errorcanonlybeusedonaWritableStreamDefaultController');
        }

        varstate=this._controlledWritableStream._state;

        if(state!=='writable'){
          return;
        }

        WritableStreamDefaultControllerError(this,e);
      }
    },{
      key:'__abortSteps',
      value:function__abortSteps(reason){
        returnPromiseInvokeOrNoop(this._underlyingSink,'abort',[reason]);
      }
    },{
      key:'__errorSteps',
      value:function__errorSteps(){
        ResetQueue(this);
      }
    },{
      key:'__startSteps',
      value:function__startSteps(){
        var_this=this;

        varstartResult=InvokeOrNoop(this._underlyingSink,'start',[this]);
        varstream=this._controlledWritableStream;
        Promise.resolve(startResult).then(function(){
          assert(stream._state==='writable'||stream._state==='erroring');
          _this._started=true;
          WritableStreamDefaultControllerAdvanceQueueIfNeeded(_this);
        },function(r){
          assert(stream._state==='writable'||stream._state==='erroring');
          _this._started=true;
          WritableStreamDealWithRejection(stream,r);
        })["catch"](rethrowAssertionErrorRejection);
      }
    }]);

    returnWritableStreamDefaultController;
  }();

  functionWritableStreamDefaultControllerClose(controller){
    EnqueueValueWithSize(controller,'close',0);
    WritableStreamDefaultControllerAdvanceQueueIfNeeded(controller);
  }

  functionWritableStreamDefaultControllerGetChunkSize(controller,chunk){
    varstrategySize=controller._strategySize;

    if(strategySize===undefined){
      return1;
    }

    try{
      returnstrategySize(chunk);
    }catch(chunkSizeE){
      WritableStreamDefaultControllerErrorIfNeeded(controller,chunkSizeE);
      return1;
    }
  }

  functionWritableStreamDefaultControllerGetDesiredSize(controller){
    returncontroller._strategyHWM-controller._queueTotalSize;
  }

  functionWritableStreamDefaultControllerWrite(controller,chunk,chunkSize){
    varwriteRecord={
      chunk:chunk
    };

    try{
      EnqueueValueWithSize(controller,writeRecord,chunkSize);
    }catch(enqueueE){
      WritableStreamDefaultControllerErrorIfNeeded(controller,enqueueE);
      return;
    }

    varstream=controller._controlledWritableStream;

    if(WritableStreamCloseQueuedOrInFlight(stream)===false&&stream._state==='writable'){
      varbackpressure=WritableStreamDefaultControllerGetBackpressure(controller);
      WritableStreamUpdateBackpressure(stream,backpressure);
    }

    WritableStreamDefaultControllerAdvanceQueueIfNeeded(controller);
  }

  functionIsWritableStreamDefaultController(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_underlyingSink')){
      returnfalse;
    }

    returntrue;
  }

  functionWritableStreamDefaultControllerAdvanceQueueIfNeeded(controller){
    varstream=controller._controlledWritableStream;

    if(controller._started===false){
      return;
    }

    if(stream._inFlightWriteRequest!==undefined){
      return;
    }

    varstate=stream._state;

    if(state==='closed'||state==='errored'){
      return;
    }

    if(state==='erroring'){
      WritableStreamFinishErroring(stream);
      return;
    }

    if(controller._queue.length===0){
      return;
    }

    varwriteRecord=PeekQueueValue(controller);

    if(writeRecord==='close'){
      WritableStreamDefaultControllerProcessClose(controller);
    }else{
      WritableStreamDefaultControllerProcessWrite(controller,writeRecord.chunk);
    }
  }

  functionWritableStreamDefaultControllerErrorIfNeeded(controller,error){
    if(controller._controlledWritableStream._state==='writable'){
      WritableStreamDefaultControllerError(controller,error);
    }
  }

  functionWritableStreamDefaultControllerProcessClose(controller){
    varstream=controller._controlledWritableStream;
    WritableStreamMarkCloseRequestInFlight(stream);
    DequeueValue(controller);
    assert(controller._queue.length===0,'queuemustbeemptyoncethefinalwriterecordisdequeued');
    varsinkClosePromise=PromiseInvokeOrNoop(controller._underlyingSink,'close',[]);
    sinkClosePromise.then(function(){
      WritableStreamFinishInFlightClose(stream);
    },function(reason){
      WritableStreamFinishInFlightCloseWithError(stream,reason);
    })["catch"](rethrowAssertionErrorRejection);
  }

  functionWritableStreamDefaultControllerProcessWrite(controller,chunk){
    varstream=controller._controlledWritableStream;
    WritableStreamMarkFirstWriteRequestInFlight(stream);
    varsinkWritePromise=PromiseInvokeOrNoop(controller._underlyingSink,'write',[chunk,controller]);
    sinkWritePromise.then(function(){
      WritableStreamFinishInFlightWrite(stream);
      varstate=stream._state;
      assert(state==='writable'||state==='erroring');
      DequeueValue(controller);

      if(WritableStreamCloseQueuedOrInFlight(stream)===false&&state==='writable'){
        varbackpressure=WritableStreamDefaultControllerGetBackpressure(controller);
        WritableStreamUpdateBackpressure(stream,backpressure);
      }

      WritableStreamDefaultControllerAdvanceQueueIfNeeded(controller);
    },function(reason){
      WritableStreamFinishInFlightWriteWithError(stream,reason);
    })["catch"](rethrowAssertionErrorRejection);
  }

  functionWritableStreamDefaultControllerGetBackpressure(controller){
    vardesiredSize=WritableStreamDefaultControllerGetDesiredSize(controller);
    returndesiredSize<=0;
  }

  functionWritableStreamDefaultControllerError(controller,error){
    varstream=controller._controlledWritableStream;
    assert(stream._state==='writable');
    WritableStreamStartErroring(stream,error);
  }

  functionstreamBrandCheckException(name){
    returnnewTypeError('WritableStream.prototype.'+name+'canonlybeusedonaWritableStream');
  }

  functiondefaultWriterBrandCheckException(name){
    returnnewTypeError('WritableStreamDefaultWriter.prototype.'+name+'canonlybeusedonaWritableStreamDefaultWriter');
  }

  functiondefaultWriterLockException(name){
    returnnewTypeError('Cannot'+name+'astreamusingareleasedwriter');
  }

  functiondefaultWriterClosedPromiseInitialize(writer){
    writer._closedPromise=newPromise(function(resolve,reject){
      writer._closedPromise_resolve=resolve;
      writer._closedPromise_reject=reject;
      writer._closedPromiseState='pending';
    });
  }

  functiondefaultWriterClosedPromiseInitializeAsRejected(writer,reason){
    writer._closedPromise=Promise.reject(reason);
    writer._closedPromise_resolve=undefined;
    writer._closedPromise_reject=undefined;
    writer._closedPromiseState='rejected';
  }

  functiondefaultWriterClosedPromiseInitializeAsResolved(writer){
    writer._closedPromise=Promise.resolve(undefined);
    writer._closedPromise_resolve=undefined;
    writer._closedPromise_reject=undefined;
    writer._closedPromiseState='resolved';
  }

  functiondefaultWriterClosedPromiseReject(writer,reason){
    assert(writer._closedPromise_resolve!==undefined,'writer._closedPromise_resolve!==undefined');
    assert(writer._closedPromise_reject!==undefined,'writer._closedPromise_reject!==undefined');
    assert(writer._closedPromiseState==='pending','writer._closedPromiseStateispending');

    writer._closedPromise_reject(reason);

    writer._closedPromise_resolve=undefined;
    writer._closedPromise_reject=undefined;
    writer._closedPromiseState='rejected';
  }

  functiondefaultWriterClosedPromiseResetToRejected(writer,reason){
    assert(writer._closedPromise_resolve===undefined,'writer._closedPromise_resolve===undefined');
    assert(writer._closedPromise_reject===undefined,'writer._closedPromise_reject===undefined');
    assert(writer._closedPromiseState!=='pending','writer._closedPromiseStateisnotpending');
    writer._closedPromise=Promise.reject(reason);
    writer._closedPromiseState='rejected';
  }

  functiondefaultWriterClosedPromiseResolve(writer){
    assert(writer._closedPromise_resolve!==undefined,'writer._closedPromise_resolve!==undefined');
    assert(writer._closedPromise_reject!==undefined,'writer._closedPromise_reject!==undefined');
    assert(writer._closedPromiseState==='pending','writer._closedPromiseStateispending');

    writer._closedPromise_resolve(undefined);

    writer._closedPromise_resolve=undefined;
    writer._closedPromise_reject=undefined;
    writer._closedPromiseState='resolved';
  }

  functiondefaultWriterReadyPromiseInitialize(writer){
    writer._readyPromise=newPromise(function(resolve,reject){
      writer._readyPromise_resolve=resolve;
      writer._readyPromise_reject=reject;
    });
    writer._readyPromiseState='pending';
  }

  functiondefaultWriterReadyPromiseInitializeAsRejected(writer,reason){
    writer._readyPromise=Promise.reject(reason);
    writer._readyPromise_resolve=undefined;
    writer._readyPromise_reject=undefined;
    writer._readyPromiseState='rejected';
  }

  functiondefaultWriterReadyPromiseInitializeAsResolved(writer){
    writer._readyPromise=Promise.resolve(undefined);
    writer._readyPromise_resolve=undefined;
    writer._readyPromise_reject=undefined;
    writer._readyPromiseState='fulfilled';
  }

  functiondefaultWriterReadyPromiseReject(writer,reason){
    assert(writer._readyPromise_resolve!==undefined,'writer._readyPromise_resolve!==undefined');
    assert(writer._readyPromise_reject!==undefined,'writer._readyPromise_reject!==undefined');

    writer._readyPromise_reject(reason);

    writer._readyPromise_resolve=undefined;
    writer._readyPromise_reject=undefined;
    writer._readyPromiseState='rejected';
  }

  functiondefaultWriterReadyPromiseReset(writer){
    assert(writer._readyPromise_resolve===undefined,'writer._readyPromise_resolve===undefined');
    assert(writer._readyPromise_reject===undefined,'writer._readyPromise_reject===undefined');
    writer._readyPromise=newPromise(function(resolve,reject){
      writer._readyPromise_resolve=resolve;
      writer._readyPromise_reject=reject;
    });
    writer._readyPromiseState='pending';
  }

  functiondefaultWriterReadyPromiseResetToRejected(writer,reason){
    assert(writer._readyPromise_resolve===undefined,'writer._readyPromise_resolve===undefined');
    assert(writer._readyPromise_reject===undefined,'writer._readyPromise_reject===undefined');
    writer._readyPromise=Promise.reject(reason);
    writer._readyPromiseState='rejected';
  }

  functiondefaultWriterReadyPromiseResolve(writer){
    assert(writer._readyPromise_resolve!==undefined,'writer._readyPromise_resolve!==undefined');
    assert(writer._readyPromise_reject!==undefined,'writer._readyPromise_reject!==undefined');

    writer._readyPromise_resolve(undefined);

    writer._readyPromise_resolve=undefined;
    writer._readyPromise_reject=undefined;
    writer._readyPromiseState='fulfilled';
  }
},function(module,exports,__w_pdfjs_require__){
  "usestrict";

  var_require=__w_pdfjs_require__(0),
      IsFiniteNonNegativeNumber=_require.IsFiniteNonNegativeNumber;

  var_require2=__w_pdfjs_require__(1),
      assert=_require2.assert;

  exports.DequeueValue=function(container){
    assert('_queue'incontainer&&'_queueTotalSize'incontainer,'Spec-levelfailure:DequeueValueshouldonlybeusedoncontainerswith[[queue]]and[[queueTotalSize]].');
    assert(container._queue.length>0,'Spec-levelfailure:shouldneverdequeuefromanemptyqueue.');

    varpair=container._queue.shift();

    container._queueTotalSize-=pair.size;

    if(container._queueTotalSize<0){
      container._queueTotalSize=0;
    }

    returnpair.value;
  };

  exports.EnqueueValueWithSize=function(container,value,size){
    assert('_queue'incontainer&&'_queueTotalSize'incontainer,'Spec-levelfailure:EnqueueValueWithSizeshouldonlybeusedoncontainerswith[[queue]]and'+'[[queueTotalSize]].');
    size=Number(size);

    if(!IsFiniteNonNegativeNumber(size)){
      thrownewRangeError('Sizemustbeafinite,non-NaN,non-negativenumber.');
    }

    container._queue.push({
      value:value,
      size:size
    });

    container._queueTotalSize+=size;
  };

  exports.PeekQueueValue=function(container){
    assert('_queue'incontainer&&'_queueTotalSize'incontainer,'Spec-levelfailure:PeekQueueValueshouldonlybeusedoncontainerswith[[queue]]and[[queueTotalSize]].');
    assert(container._queue.length>0,'Spec-levelfailure:shouldneverpeekatanemptyqueue.');
    varpair=container._queue[0];
    returnpair.value;
  };

  exports.ResetQueue=function(container){
    assert('_queue'incontainer&&'_queueTotalSize'incontainer,'Spec-levelfailure:ResetQueueshouldonlybeusedoncontainerswith[[queue]]and[[queueTotalSize]].');
    container._queue=[];
    container._queueTotalSize=0;
  };
},function(module,exports,__w_pdfjs_require__){
  "usestrict";

  var_createClass=function(){
    functiondefineProperties(target,props){
      for(vari=0;i<props.length;i++){
        vardescriptor=props[i];
        descriptor.enumerable=descriptor.enumerable||false;
        descriptor.configurable=true;
        if("value"indescriptor)descriptor.writable=true;
        Object.defineProperty(target,descriptor.key,descriptor);
      }
    }

    returnfunction(Constructor,protoProps,staticProps){
      if(protoProps)defineProperties(Constructor.prototype,protoProps);
      if(staticProps)defineProperties(Constructor,staticProps);
      returnConstructor;
    };
  }();

  function_classCallCheck(instance,Constructor){
    if(!(instanceinstanceofConstructor)){
      thrownewTypeError("Cannotcallaclassasafunction");
    }
  }

  var_require=__w_pdfjs_require__(0),
      ArrayBufferCopy=_require.ArrayBufferCopy,
      CreateIterResultObject=_require.CreateIterResultObject,
      IsFiniteNonNegativeNumber=_require.IsFiniteNonNegativeNumber,
      InvokeOrNoop=_require.InvokeOrNoop,
      PromiseInvokeOrNoop=_require.PromiseInvokeOrNoop,
      TransferArrayBuffer=_require.TransferArrayBuffer,
      ValidateAndNormalizeQueuingStrategy=_require.ValidateAndNormalizeQueuingStrategy,
      ValidateAndNormalizeHighWaterMark=_require.ValidateAndNormalizeHighWaterMark;

  var_require2=__w_pdfjs_require__(0),
      createArrayFromList=_require2.createArrayFromList,
      createDataProperty=_require2.createDataProperty,
      typeIsObject=_require2.typeIsObject;

  var_require3=__w_pdfjs_require__(1),
      assert=_require3.assert,
      rethrowAssertionErrorRejection=_require3.rethrowAssertionErrorRejection;

  var_require4=__w_pdfjs_require__(3),
      DequeueValue=_require4.DequeueValue,
      EnqueueValueWithSize=_require4.EnqueueValueWithSize,
      ResetQueue=_require4.ResetQueue;

  var_require5=__w_pdfjs_require__(2),
      AcquireWritableStreamDefaultWriter=_require5.AcquireWritableStreamDefaultWriter,
      IsWritableStream=_require5.IsWritableStream,
      IsWritableStreamLocked=_require5.IsWritableStreamLocked,
      WritableStreamAbort=_require5.WritableStreamAbort,
      WritableStreamDefaultWriterCloseWithErrorPropagation=_require5.WritableStreamDefaultWriterCloseWithErrorPropagation,
      WritableStreamDefaultWriterRelease=_require5.WritableStreamDefaultWriterRelease,
      WritableStreamDefaultWriterWrite=_require5.WritableStreamDefaultWriterWrite,
      WritableStreamCloseQueuedOrInFlight=_require5.WritableStreamCloseQueuedOrInFlight;

  varReadableStream=function(){
    functionReadableStream(){
      varunderlyingSource=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};

      var_ref=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{},
          size=_ref.size,
          highWaterMark=_ref.highWaterMark;

      _classCallCheck(this,ReadableStream);

      this._state='readable';
      this._reader=undefined;
      this._storedError=undefined;
      this._disturbed=false;
      this._readableStreamController=undefined;
      vartype=underlyingSource.type;
      vartypeString=String(type);

      if(typeString==='bytes'){
        if(highWaterMark===undefined){
          highWaterMark=0;
        }

        this._readableStreamController=newReadableByteStreamController(this,underlyingSource,highWaterMark);
      }elseif(type===undefined){
        if(highWaterMark===undefined){
          highWaterMark=1;
        }

        this._readableStreamController=newReadableStreamDefaultController(this,underlyingSource,size,highWaterMark);
      }else{
        thrownewRangeError('Invalidtypeisspecified');
      }
    }

    _createClass(ReadableStream,[{
      key:'cancel',
      value:functioncancel(reason){
        if(IsReadableStream(this)===false){
          returnPromise.reject(streamBrandCheckException('cancel'));
        }

        if(IsReadableStreamLocked(this)===true){
          returnPromise.reject(newTypeError('Cannotcancelastreamthatalreadyhasareader'));
        }

        returnReadableStreamCancel(this,reason);
      }
    },{
      key:'getReader',
      value:functiongetReader(){
        var_ref2=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
            mode=_ref2.mode;

        if(IsReadableStream(this)===false){
          throwstreamBrandCheckException('getReader');
        }

        if(mode===undefined){
          returnAcquireReadableStreamDefaultReader(this);
        }

        mode=String(mode);

        if(mode==='byob'){
          returnAcquireReadableStreamBYOBReader(this);
        }

        thrownewRangeError('Invalidmodeisspecified');
      }
    },{
      key:'pipeThrough',
      value:functionpipeThrough(_ref3,options){
        varwritable=_ref3.writable,
            readable=_ref3.readable;
        varpromise=this.pipeTo(writable,options);
        ifIsObjectAndHasAPromiseIsHandledInternalSlotSetPromiseIsHandledToTrue(promise);
        returnreadable;
      }
    },{
      key:'pipeTo',
      value:functionpipeTo(dest){
        var_this=this;

        var_ref4=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{},
            preventClose=_ref4.preventClose,
            preventAbort=_ref4.preventAbort,
            preventCancel=_ref4.preventCancel;

        if(IsReadableStream(this)===false){
          returnPromise.reject(streamBrandCheckException('pipeTo'));
        }

        if(IsWritableStream(dest)===false){
          returnPromise.reject(newTypeError('ReadableStream.prototype.pipeTo\'sfirstargumentmustbeaWritableStream'));
        }

        preventClose=Boolean(preventClose);
        preventAbort=Boolean(preventAbort);
        preventCancel=Boolean(preventCancel);

        if(IsReadableStreamLocked(this)===true){
          returnPromise.reject(newTypeError('ReadableStream.prototype.pipeTocannotbeusedonalockedReadableStream'));
        }

        if(IsWritableStreamLocked(dest)===true){
          returnPromise.reject(newTypeError('ReadableStream.prototype.pipeTocannotbeusedonalockedWritableStream'));
        }

        varreader=AcquireReadableStreamDefaultReader(this);
        varwriter=AcquireWritableStreamDefaultWriter(dest);
        varshuttingDown=false;
        varcurrentWrite=Promise.resolve();
        returnnewPromise(function(resolve,reject){
          functionpipeLoop(){
            currentWrite=Promise.resolve();

            if(shuttingDown===true){
              returnPromise.resolve();
            }

            returnwriter._readyPromise.then(function(){
              returnReadableStreamDefaultReaderRead(reader).then(function(_ref5){
                varvalue=_ref5.value,
                    done=_ref5.done;

                if(done===true){
                  return;
                }

                currentWrite=WritableStreamDefaultWriterWrite(writer,value)["catch"](function(){});
              });
            }).then(pipeLoop);
          }

          isOrBecomesErrored(_this,reader._closedPromise,function(storedError){
            if(preventAbort===false){
              shutdownWithAction(function(){
                returnWritableStreamAbort(dest,storedError);
              },true,storedError);
            }else{
              shutdown(true,storedError);
            }
          });
          isOrBecomesErrored(dest,writer._closedPromise,function(storedError){
            if(preventCancel===false){
              shutdownWithAction(function(){
                returnReadableStreamCancel(_this,storedError);
              },true,storedError);
            }else{
              shutdown(true,storedError);
            }
          });
          isOrBecomesClosed(_this,reader._closedPromise,function(){
            if(preventClose===false){
              shutdownWithAction(function(){
                returnWritableStreamDefaultWriterCloseWithErrorPropagation(writer);
              });
            }else{
              shutdown();
            }
          });

          if(WritableStreamCloseQueuedOrInFlight(dest)===true||dest._state==='closed'){
            vardestClosed=newTypeError('thedestinationwritablestreamclosedbeforealldatacouldbepipedtoit');

            if(preventCancel===false){
              shutdownWithAction(function(){
                returnReadableStreamCancel(_this,destClosed);
              },true,destClosed);
            }else{
              shutdown(true,destClosed);
            }
          }

          pipeLoop()["catch"](function(err){
            currentWrite=Promise.resolve();
            rethrowAssertionErrorRejection(err);
          });

          functionwaitForWritesToFinish(){
            varoldCurrentWrite=currentWrite;
            returncurrentWrite.then(function(){
              returnoldCurrentWrite!==currentWrite?waitForWritesToFinish():undefined;
            });
          }

          functionisOrBecomesErrored(stream,promise,action){
            if(stream._state==='errored'){
              action(stream._storedError);
            }else{
              promise["catch"](action)["catch"](rethrowAssertionErrorRejection);
            }
          }

          functionisOrBecomesClosed(stream,promise,action){
            if(stream._state==='closed'){
              action();
            }else{
              promise.then(action)["catch"](rethrowAssertionErrorRejection);
            }
          }

          functionshutdownWithAction(action,originalIsError,originalError){
            if(shuttingDown===true){
              return;
            }

            shuttingDown=true;

            if(dest._state==='writable'&&WritableStreamCloseQueuedOrInFlight(dest)===false){
              waitForWritesToFinish().then(doTheRest);
            }else{
              doTheRest();
            }

            functiondoTheRest(){
              action().then(function(){
                returnfinalize(originalIsError,originalError);
              },function(newError){
                returnfinalize(true,newError);
              })["catch"](rethrowAssertionErrorRejection);
            }
          }

          functionshutdown(isError,error){
            if(shuttingDown===true){
              return;
            }

            shuttingDown=true;

            if(dest._state==='writable'&&WritableStreamCloseQueuedOrInFlight(dest)===false){
              waitForWritesToFinish().then(function(){
                returnfinalize(isError,error);
              })["catch"](rethrowAssertionErrorRejection);
            }else{
              finalize(isError,error);
            }
          }

          functionfinalize(isError,error){
            WritableStreamDefaultWriterRelease(writer);
            ReadableStreamReaderGenericRelease(reader);

            if(isError){
              reject(error);
            }else{
              resolve(undefined);
            }
          }
        });
      }
    },{
      key:'tee',
      value:functiontee(){
        if(IsReadableStream(this)===false){
          throwstreamBrandCheckException('tee');
        }

        varbranches=ReadableStreamTee(this,false);
        returncreateArrayFromList(branches);
      }
    },{
      key:'locked',
      get:functionget(){
        if(IsReadableStream(this)===false){
          throwstreamBrandCheckException('locked');
        }

        returnIsReadableStreamLocked(this);
      }
    }]);

    returnReadableStream;
  }();

  module.exports={
    ReadableStream:ReadableStream,
    IsReadableStreamDisturbed:IsReadableStreamDisturbed,
    ReadableStreamDefaultControllerClose:ReadableStreamDefaultControllerClose,
    ReadableStreamDefaultControllerEnqueue:ReadableStreamDefaultControllerEnqueue,
    ReadableStreamDefaultControllerError:ReadableStreamDefaultControllerError,
    ReadableStreamDefaultControllerGetDesiredSize:ReadableStreamDefaultControllerGetDesiredSize
  };

  functionAcquireReadableStreamBYOBReader(stream){
    returnnewReadableStreamBYOBReader(stream);
  }

  functionAcquireReadableStreamDefaultReader(stream){
    returnnewReadableStreamDefaultReader(stream);
  }

  functionIsReadableStream(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_readableStreamController')){
      returnfalse;
    }

    returntrue;
  }

  functionIsReadableStreamDisturbed(stream){
    assert(IsReadableStream(stream)===true,'IsReadableStreamDisturbedshouldonlybeusedonknownreadablestreams');
    returnstream._disturbed;
  }

  functionIsReadableStreamLocked(stream){
    assert(IsReadableStream(stream)===true,'IsReadableStreamLockedshouldonlybeusedonknownreadablestreams');

    if(stream._reader===undefined){
      returnfalse;
    }

    returntrue;
  }

  functionReadableStreamTee(stream,cloneForBranch2){
    assert(IsReadableStream(stream)===true);
    assert(typeofcloneForBranch2==='boolean');
    varreader=AcquireReadableStreamDefaultReader(stream);
    varteeState={
      closedOrErrored:false,
      canceled1:false,
      canceled2:false,
      reason1:undefined,
      reason2:undefined
    };
    teeState.promise=newPromise(function(resolve){
      teeState._resolve=resolve;
    });
    varpull=create_ReadableStreamTeePullFunction();
    pull._reader=reader;
    pull._teeState=teeState;
    pull._cloneForBranch2=cloneForBranch2;
    varcancel1=create_ReadableStreamTeeBranch1CancelFunction();
    cancel1._stream=stream;
    cancel1._teeState=teeState;
    varcancel2=create_ReadableStreamTeeBranch2CancelFunction();
    cancel2._stream=stream;
    cancel2._teeState=teeState;
    varunderlyingSource1=Object.create(Object.prototype);
    createDataProperty(underlyingSource1,'pull',pull);
    createDataProperty(underlyingSource1,'cancel',cancel1);
    varbranch1Stream=newReadableStream(underlyingSource1);
    varunderlyingSource2=Object.create(Object.prototype);
    createDataProperty(underlyingSource2,'pull',pull);
    createDataProperty(underlyingSource2,'cancel',cancel2);
    varbranch2Stream=newReadableStream(underlyingSource2);
    pull._branch1=branch1Stream._readableStreamController;
    pull._branch2=branch2Stream._readableStreamController;

    reader._closedPromise["catch"](function(r){
      if(teeState.closedOrErrored===true){
        return;
      }

      ReadableStreamDefaultControllerError(pull._branch1,r);
      ReadableStreamDefaultControllerError(pull._branch2,r);
      teeState.closedOrErrored=true;
    });

    return[branch1Stream,branch2Stream];
  }

  functioncreate_ReadableStreamTeePullFunction(){
    functionf(){
      varreader=f._reader,
          branch1=f._branch1,
          branch2=f._branch2,
          teeState=f._teeState;
      returnReadableStreamDefaultReaderRead(reader).then(function(result){
        assert(typeIsObject(result));
        varvalue=result.value;
        vardone=result.done;
        assert(typeofdone==='boolean');

        if(done===true&&teeState.closedOrErrored===false){
          if(teeState.canceled1===false){
            ReadableStreamDefaultControllerClose(branch1);
          }

          if(teeState.canceled2===false){
            ReadableStreamDefaultControllerClose(branch2);
          }

          teeState.closedOrErrored=true;
        }

        if(teeState.closedOrErrored===true){
          return;
        }

        varvalue1=value;
        varvalue2=value;

        if(teeState.canceled1===false){
          ReadableStreamDefaultControllerEnqueue(branch1,value1);
        }

        if(teeState.canceled2===false){
          ReadableStreamDefaultControllerEnqueue(branch2,value2);
        }
      });
    }

    returnf;
  }

  functioncreate_ReadableStreamTeeBranch1CancelFunction(){
    functionf(reason){
      varstream=f._stream,
          teeState=f._teeState;
      teeState.canceled1=true;
      teeState.reason1=reason;

      if(teeState.canceled2===true){
        varcompositeReason=createArrayFromList([teeState.reason1,teeState.reason2]);
        varcancelResult=ReadableStreamCancel(stream,compositeReason);

        teeState._resolve(cancelResult);
      }

      returnteeState.promise;
    }

    returnf;
  }

  functioncreate_ReadableStreamTeeBranch2CancelFunction(){
    functionf(reason){
      varstream=f._stream,
          teeState=f._teeState;
      teeState.canceled2=true;
      teeState.reason2=reason;

      if(teeState.canceled1===true){
        varcompositeReason=createArrayFromList([teeState.reason1,teeState.reason2]);
        varcancelResult=ReadableStreamCancel(stream,compositeReason);

        teeState._resolve(cancelResult);
      }

      returnteeState.promise;
    }

    returnf;
  }

  functionReadableStreamAddReadIntoRequest(stream){
    assert(IsReadableStreamBYOBReader(stream._reader)===true);
    assert(stream._state==='readable'||stream._state==='closed');
    varpromise=newPromise(function(resolve,reject){
      varreadIntoRequest={
        _resolve:resolve,
        _reject:reject
      };

      stream._reader._readIntoRequests.push(readIntoRequest);
    });
    returnpromise;
  }

  functionReadableStreamAddReadRequest(stream){
    assert(IsReadableStreamDefaultReader(stream._reader)===true);
    assert(stream._state==='readable');
    varpromise=newPromise(function(resolve,reject){
      varreadRequest={
        _resolve:resolve,
        _reject:reject
      };

      stream._reader._readRequests.push(readRequest);
    });
    returnpromise;
  }

  functionReadableStreamCancel(stream,reason){
    stream._disturbed=true;

    if(stream._state==='closed'){
      returnPromise.resolve(undefined);
    }

    if(stream._state==='errored'){
      returnPromise.reject(stream._storedError);
    }

    ReadableStreamClose(stream);

    varsourceCancelPromise=stream._readableStreamController.__cancelSteps(reason);

    returnsourceCancelPromise.then(function(){
      returnundefined;
    });
  }

  functionReadableStreamClose(stream){
    assert(stream._state==='readable');
    stream._state='closed';
    varreader=stream._reader;

    if(reader===undefined){
      returnundefined;
    }

    if(IsReadableStreamDefaultReader(reader)===true){
      for(vari=0;i<reader._readRequests.length;i++){
        var_resolve=reader._readRequests[i]._resolve;

        _resolve(CreateIterResultObject(undefined,true));
      }

      reader._readRequests=[];
    }

    defaultReaderClosedPromiseResolve(reader);
    returnundefined;
  }

  functionReadableStreamError(stream,e){
    assert(IsReadableStream(stream)===true,'streammustbeReadableStream');
    assert(stream._state==='readable','statemustbereadable');
    stream._state='errored';
    stream._storedError=e;
    varreader=stream._reader;

    if(reader===undefined){
      returnundefined;
    }

    if(IsReadableStreamDefaultReader(reader)===true){
      for(vari=0;i<reader._readRequests.length;i++){
        varreadRequest=reader._readRequests[i];

        readRequest._reject(e);
      }

      reader._readRequests=[];
    }else{
      assert(IsReadableStreamBYOBReader(reader),'readermustbeReadableStreamBYOBReader');

      for(var_i=0;_i<reader._readIntoRequests.length;_i++){
        varreadIntoRequest=reader._readIntoRequests[_i];

        readIntoRequest._reject(e);
      }

      reader._readIntoRequests=[];
    }

    defaultReaderClosedPromiseReject(reader,e);

    reader._closedPromise["catch"](function(){});
  }

  functionReadableStreamFulfillReadIntoRequest(stream,chunk,done){
    varreader=stream._reader;
    assert(reader._readIntoRequests.length>0);

    varreadIntoRequest=reader._readIntoRequests.shift();

    readIntoRequest._resolve(CreateIterResultObject(chunk,done));
  }

  functionReadableStreamFulfillReadRequest(stream,chunk,done){
    varreader=stream._reader;
    assert(reader._readRequests.length>0);

    varreadRequest=reader._readRequests.shift();

    readRequest._resolve(CreateIterResultObject(chunk,done));
  }

  functionReadableStreamGetNumReadIntoRequests(stream){
    returnstream._reader._readIntoRequests.length;
  }

  functionReadableStreamGetNumReadRequests(stream){
    returnstream._reader._readRequests.length;
  }

  functionReadableStreamHasBYOBReader(stream){
    varreader=stream._reader;

    if(reader===undefined){
      returnfalse;
    }

    if(IsReadableStreamBYOBReader(reader)===false){
      returnfalse;
    }

    returntrue;
  }

  functionReadableStreamHasDefaultReader(stream){
    varreader=stream._reader;

    if(reader===undefined){
      returnfalse;
    }

    if(IsReadableStreamDefaultReader(reader)===false){
      returnfalse;
    }

    returntrue;
  }

  varReadableStreamDefaultReader=function(){
    functionReadableStreamDefaultReader(stream){
      _classCallCheck(this,ReadableStreamDefaultReader);

      if(IsReadableStream(stream)===false){
        thrownewTypeError('ReadableStreamDefaultReadercanonlybeconstructedwithaReadableStreaminstance');
      }

      if(IsReadableStreamLocked(stream)===true){
        thrownewTypeError('Thisstreamhasalreadybeenlockedforexclusivereadingbyanotherreader');
      }

      ReadableStreamReaderGenericInitialize(this,stream);
      this._readRequests=[];
    }

    _createClass(ReadableStreamDefaultReader,[{
      key:'cancel',
      value:functioncancel(reason){
        if(IsReadableStreamDefaultReader(this)===false){
          returnPromise.reject(defaultReaderBrandCheckException('cancel'));
        }

        if(this._ownerReadableStream===undefined){
          returnPromise.reject(readerLockException('cancel'));
        }

        returnReadableStreamReaderGenericCancel(this,reason);
      }
    },{
      key:'read',
      value:functionread(){
        if(IsReadableStreamDefaultReader(this)===false){
          returnPromise.reject(defaultReaderBrandCheckException('read'));
        }

        if(this._ownerReadableStream===undefined){
          returnPromise.reject(readerLockException('readfrom'));
        }

        returnReadableStreamDefaultReaderRead(this);
      }
    },{
      key:'releaseLock',
      value:functionreleaseLock(){
        if(IsReadableStreamDefaultReader(this)===false){
          throwdefaultReaderBrandCheckException('releaseLock');
        }

        if(this._ownerReadableStream===undefined){
          return;
        }

        if(this._readRequests.length>0){
          thrownewTypeError('Triedtoreleaseareaderlockwhenthatreaderhaspendingread()callsun-settled');
        }

        ReadableStreamReaderGenericRelease(this);
      }
    },{
      key:'closed',
      get:functionget(){
        if(IsReadableStreamDefaultReader(this)===false){
          returnPromise.reject(defaultReaderBrandCheckException('closed'));
        }

        returnthis._closedPromise;
      }
    }]);

    returnReadableStreamDefaultReader;
  }();

  varReadableStreamBYOBReader=function(){
    functionReadableStreamBYOBReader(stream){
      _classCallCheck(this,ReadableStreamBYOBReader);

      if(!IsReadableStream(stream)){
        thrownewTypeError('ReadableStreamBYOBReadercanonlybeconstructedwithaReadableStreaminstancegivena'+'bytesource');
      }

      if(IsReadableByteStreamController(stream._readableStreamController)===false){
        thrownewTypeError('CannotconstructaReadableStreamBYOBReaderforastreamnotconstructedwithabyte'+'source');
      }

      if(IsReadableStreamLocked(stream)){
        thrownewTypeError('Thisstreamhasalreadybeenlockedforexclusivereadingbyanotherreader');
      }

      ReadableStreamReaderGenericInitialize(this,stream);
      this._readIntoRequests=[];
    }

    _createClass(ReadableStreamBYOBReader,[{
      key:'cancel',
      value:functioncancel(reason){
        if(!IsReadableStreamBYOBReader(this)){
          returnPromise.reject(byobReaderBrandCheckException('cancel'));
        }

        if(this._ownerReadableStream===undefined){
          returnPromise.reject(readerLockException('cancel'));
        }

        returnReadableStreamReaderGenericCancel(this,reason);
      }
    },{
      key:'read',
      value:functionread(view){
        if(!IsReadableStreamBYOBReader(this)){
          returnPromise.reject(byobReaderBrandCheckException('read'));
        }

        if(this._ownerReadableStream===undefined){
          returnPromise.reject(readerLockException('readfrom'));
        }

        if(!ArrayBuffer.isView(view)){
          returnPromise.reject(newTypeError('viewmustbeanarraybufferview'));
        }

        if(view.byteLength===0){
          returnPromise.reject(newTypeError('viewmusthavenon-zerobyteLength'));
        }

        returnReadableStreamBYOBReaderRead(this,view);
      }
    },{
      key:'releaseLock',
      value:functionreleaseLock(){
        if(!IsReadableStreamBYOBReader(this)){
          throwbyobReaderBrandCheckException('releaseLock');
        }

        if(this._ownerReadableStream===undefined){
          return;
        }

        if(this._readIntoRequests.length>0){
          thrownewTypeError('Triedtoreleaseareaderlockwhenthatreaderhaspendingread()callsun-settled');
        }

        ReadableStreamReaderGenericRelease(this);
      }
    },{
      key:'closed',
      get:functionget(){
        if(!IsReadableStreamBYOBReader(this)){
          returnPromise.reject(byobReaderBrandCheckException('closed'));
        }

        returnthis._closedPromise;
      }
    }]);

    returnReadableStreamBYOBReader;
  }();

  functionIsReadableStreamBYOBReader(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_readIntoRequests')){
      returnfalse;
    }

    returntrue;
  }

  functionIsReadableStreamDefaultReader(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_readRequests')){
      returnfalse;
    }

    returntrue;
  }

  functionReadableStreamReaderGenericInitialize(reader,stream){
    reader._ownerReadableStream=stream;
    stream._reader=reader;

    if(stream._state==='readable'){
      defaultReaderClosedPromiseInitialize(reader);
    }elseif(stream._state==='closed'){
      defaultReaderClosedPromiseInitializeAsResolved(reader);
    }else{
      assert(stream._state==='errored','statemustbeerrored');
      defaultReaderClosedPromiseInitializeAsRejected(reader,stream._storedError);

      reader._closedPromise["catch"](function(){});
    }
  }

  functionReadableStreamReaderGenericCancel(reader,reason){
    varstream=reader._ownerReadableStream;
    assert(stream!==undefined);
    returnReadableStreamCancel(stream,reason);
  }

  functionReadableStreamReaderGenericRelease(reader){
    assert(reader._ownerReadableStream!==undefined);
    assert(reader._ownerReadableStream._reader===reader);

    if(reader._ownerReadableStream._state==='readable'){
      defaultReaderClosedPromiseReject(reader,newTypeError('Readerwasreleasedandcannolongerbeusedtomonitorthestream\'sclosedness'));
    }else{
      defaultReaderClosedPromiseResetToRejected(reader,newTypeError('Readerwasreleasedandcannolongerbeusedtomonitorthestream\'sclosedness'));
    }

    reader._closedPromise["catch"](function(){});

    reader._ownerReadableStream._reader=undefined;
    reader._ownerReadableStream=undefined;
  }

  functionReadableStreamBYOBReaderRead(reader,view){
    varstream=reader._ownerReadableStream;
    assert(stream!==undefined);
    stream._disturbed=true;

    if(stream._state==='errored'){
      returnPromise.reject(stream._storedError);
    }

    returnReadableByteStreamControllerPullInto(stream._readableStreamController,view);
  }

  functionReadableStreamDefaultReaderRead(reader){
    varstream=reader._ownerReadableStream;
    assert(stream!==undefined);
    stream._disturbed=true;

    if(stream._state==='closed'){
      returnPromise.resolve(CreateIterResultObject(undefined,true));
    }

    if(stream._state==='errored'){
      returnPromise.reject(stream._storedError);
    }

    assert(stream._state==='readable');
    returnstream._readableStreamController.__pullSteps();
  }

  varReadableStreamDefaultController=function(){
    functionReadableStreamDefaultController(stream,underlyingSource,size,highWaterMark){
      _classCallCheck(this,ReadableStreamDefaultController);

      if(IsReadableStream(stream)===false){
        thrownewTypeError('ReadableStreamDefaultControllercanonlybeconstructedwithaReadableStreaminstance');
      }

      if(stream._readableStreamController!==undefined){
        thrownewTypeError('ReadableStreamDefaultControllerinstancescanonlybecreatedbytheReadableStreamconstructor');
      }

      this._controlledReadableStream=stream;
      this._underlyingSource=underlyingSource;
      this._queue=undefined;
      this._queueTotalSize=undefined;
      ResetQueue(this);
      this._started=false;
      this._closeRequested=false;
      this._pullAgain=false;
      this._pulling=false;
      varnormalizedStrategy=ValidateAndNormalizeQueuingStrategy(size,highWaterMark);
      this._strategySize=normalizedStrategy.size;
      this._strategyHWM=normalizedStrategy.highWaterMark;
      varcontroller=this;
      varstartResult=InvokeOrNoop(underlyingSource,'start',[this]);
      Promise.resolve(startResult).then(function(){
        controller._started=true;
        assert(controller._pulling===false);
        assert(controller._pullAgain===false);
        ReadableStreamDefaultControllerCallPullIfNeeded(controller);
      },function(r){
        ReadableStreamDefaultControllerErrorIfNeeded(controller,r);
      })["catch"](rethrowAssertionErrorRejection);
    }

    _createClass(ReadableStreamDefaultController,[{
      key:'close',
      value:functionclose(){
        if(IsReadableStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('close');
        }

        if(this._closeRequested===true){
          thrownewTypeError('Thestreamhasalreadybeenclosed;donotcloseitagain!');
        }

        varstate=this._controlledReadableStream._state;

        if(state!=='readable'){
          thrownewTypeError('Thestream(in'+state+'state)isnotinthereadablestateandcannotbeclosed');
        }

        ReadableStreamDefaultControllerClose(this);
      }
    },{
      key:'enqueue',
      value:functionenqueue(chunk){
        if(IsReadableStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('enqueue');
        }

        if(this._closeRequested===true){
          thrownewTypeError('streamisclosedordraining');
        }

        varstate=this._controlledReadableStream._state;

        if(state!=='readable'){
          thrownewTypeError('Thestream(in'+state+'state)isnotinthereadablestateandcannotbeenqueuedto');
        }

        returnReadableStreamDefaultControllerEnqueue(this,chunk);
      }
    },{
      key:'error',
      value:functionerror(e){
        if(IsReadableStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('error');
        }

        varstream=this._controlledReadableStream;

        if(stream._state!=='readable'){
          thrownewTypeError('Thestreamis'+stream._state+'andsocannotbeerrored');
        }

        ReadableStreamDefaultControllerError(this,e);
      }
    },{
      key:'__cancelSteps',
      value:function__cancelSteps(reason){
        ResetQueue(this);
        returnPromiseInvokeOrNoop(this._underlyingSource,'cancel',[reason]);
      }
    },{
      key:'__pullSteps',
      value:function__pullSteps(){
        varstream=this._controlledReadableStream;

        if(this._queue.length>0){
          varchunk=DequeueValue(this);

          if(this._closeRequested===true&&this._queue.length===0){
            ReadableStreamClose(stream);
          }else{
            ReadableStreamDefaultControllerCallPullIfNeeded(this);
          }

          returnPromise.resolve(CreateIterResultObject(chunk,false));
        }

        varpendingPromise=ReadableStreamAddReadRequest(stream);
        ReadableStreamDefaultControllerCallPullIfNeeded(this);
        returnpendingPromise;
      }
    },{
      key:'desiredSize',
      get:functionget(){
        if(IsReadableStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('desiredSize');
        }

        returnReadableStreamDefaultControllerGetDesiredSize(this);
      }
    }]);

    returnReadableStreamDefaultController;
  }();

  functionIsReadableStreamDefaultController(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_underlyingSource')){
      returnfalse;
    }

    returntrue;
  }

  functionReadableStreamDefaultControllerCallPullIfNeeded(controller){
    varshouldPull=ReadableStreamDefaultControllerShouldCallPull(controller);

    if(shouldPull===false){
      returnundefined;
    }

    if(controller._pulling===true){
      controller._pullAgain=true;
      returnundefined;
    }

    assert(controller._pullAgain===false);
    controller._pulling=true;
    varpullPromise=PromiseInvokeOrNoop(controller._underlyingSource,'pull',[controller]);
    pullPromise.then(function(){
      controller._pulling=false;

      if(controller._pullAgain===true){
        controller._pullAgain=false;
        returnReadableStreamDefaultControllerCallPullIfNeeded(controller);
      }

      returnundefined;
    },function(e){
      ReadableStreamDefaultControllerErrorIfNeeded(controller,e);
    })["catch"](rethrowAssertionErrorRejection);
    returnundefined;
  }

  functionReadableStreamDefaultControllerShouldCallPull(controller){
    varstream=controller._controlledReadableStream;

    if(stream._state==='closed'||stream._state==='errored'){
      returnfalse;
    }

    if(controller._closeRequested===true){
      returnfalse;
    }

    if(controller._started===false){
      returnfalse;
    }

    if(IsReadableStreamLocked(stream)===true&&ReadableStreamGetNumReadRequests(stream)>0){
      returntrue;
    }

    vardesiredSize=ReadableStreamDefaultControllerGetDesiredSize(controller);

    if(desiredSize>0){
      returntrue;
    }

    returnfalse;
  }

  functionReadableStreamDefaultControllerClose(controller){
    varstream=controller._controlledReadableStream;
    assert(controller._closeRequested===false);
    assert(stream._state==='readable');
    controller._closeRequested=true;

    if(controller._queue.length===0){
      ReadableStreamClose(stream);
    }
  }

  functionReadableStreamDefaultControllerEnqueue(controller,chunk){
    varstream=controller._controlledReadableStream;
    assert(controller._closeRequested===false);
    assert(stream._state==='readable');

    if(IsReadableStreamLocked(stream)===true&&ReadableStreamGetNumReadRequests(stream)>0){
      ReadableStreamFulfillReadRequest(stream,chunk,false);
    }else{
      varchunkSize=1;

      if(controller._strategySize!==undefined){
        varstrategySize=controller._strategySize;

        try{
          chunkSize=strategySize(chunk);
        }catch(chunkSizeE){
          ReadableStreamDefaultControllerErrorIfNeeded(controller,chunkSizeE);
          throwchunkSizeE;
        }
      }

      try{
        EnqueueValueWithSize(controller,chunk,chunkSize);
      }catch(enqueueE){
        ReadableStreamDefaultControllerErrorIfNeeded(controller,enqueueE);
        throwenqueueE;
      }
    }

    ReadableStreamDefaultControllerCallPullIfNeeded(controller);
    returnundefined;
  }

  functionReadableStreamDefaultControllerError(controller,e){
    varstream=controller._controlledReadableStream;
    assert(stream._state==='readable');
    ResetQueue(controller);
    ReadableStreamError(stream,e);
  }

  functionReadableStreamDefaultControllerErrorIfNeeded(controller,e){
    if(controller._controlledReadableStream._state==='readable'){
      ReadableStreamDefaultControllerError(controller,e);
    }
  }

  functionReadableStreamDefaultControllerGetDesiredSize(controller){
    varstream=controller._controlledReadableStream;
    varstate=stream._state;

    if(state==='errored'){
      returnnull;
    }

    if(state==='closed'){
      return0;
    }

    returncontroller._strategyHWM-controller._queueTotalSize;
  }

  varReadableStreamBYOBRequest=function(){
    functionReadableStreamBYOBRequest(controller,view){
      _classCallCheck(this,ReadableStreamBYOBRequest);

      this._associatedReadableByteStreamController=controller;
      this._view=view;
    }

    _createClass(ReadableStreamBYOBRequest,[{
      key:'respond',
      value:functionrespond(bytesWritten){
        if(IsReadableStreamBYOBRequest(this)===false){
          throwbyobRequestBrandCheckException('respond');
        }

        if(this._associatedReadableByteStreamController===undefined){
          thrownewTypeError('ThisBYOBrequesthasbeeninvalidated');
        }

        ReadableByteStreamControllerRespond(this._associatedReadableByteStreamController,bytesWritten);
      }
    },{
      key:'respondWithNewView',
      value:functionrespondWithNewView(view){
        if(IsReadableStreamBYOBRequest(this)===false){
          throwbyobRequestBrandCheckException('respond');
        }

        if(this._associatedReadableByteStreamController===undefined){
          thrownewTypeError('ThisBYOBrequesthasbeeninvalidated');
        }

        if(!ArrayBuffer.isView(view)){
          thrownewTypeError('Youcanonlyrespondwitharraybufferviews');
        }

        ReadableByteStreamControllerRespondWithNewView(this._associatedReadableByteStreamController,view);
      }
    },{
      key:'view',
      get:functionget(){
        returnthis._view;
      }
    }]);

    returnReadableStreamBYOBRequest;
  }();

  varReadableByteStreamController=function(){
    functionReadableByteStreamController(stream,underlyingByteSource,highWaterMark){
      _classCallCheck(this,ReadableByteStreamController);

      if(IsReadableStream(stream)===false){
        thrownewTypeError('ReadableByteStreamControllercanonlybeconstructedwithaReadableStreaminstancegiven'+'abytesource');
      }

      if(stream._readableStreamController!==undefined){
        thrownewTypeError('ReadableByteStreamControllerinstancescanonlybecreatedbytheReadableStreamconstructorgivenabyte'+'source');
      }

      this._controlledReadableStream=stream;
      this._underlyingByteSource=underlyingByteSource;
      this._pullAgain=false;
      this._pulling=false;
      ReadableByteStreamControllerClearPendingPullIntos(this);
      this._queue=this._queueTotalSize=undefined;
      ResetQueue(this);
      this._closeRequested=false;
      this._started=false;
      this._strategyHWM=ValidateAndNormalizeHighWaterMark(highWaterMark);
      varautoAllocateChunkSize=underlyingByteSource.autoAllocateChunkSize;

      if(autoAllocateChunkSize!==undefined){
        if(Number.isInteger(autoAllocateChunkSize)===false||autoAllocateChunkSize<=0){
          thrownewRangeError('autoAllocateChunkSizemustbeapositiveinteger');
        }
      }

      this._autoAllocateChunkSize=autoAllocateChunkSize;
      this._pendingPullIntos=[];
      varcontroller=this;
      varstartResult=InvokeOrNoop(underlyingByteSource,'start',[this]);
      Promise.resolve(startResult).then(function(){
        controller._started=true;
        assert(controller._pulling===false);
        assert(controller._pullAgain===false);
        ReadableByteStreamControllerCallPullIfNeeded(controller);
      },function(r){
        if(stream._state==='readable'){
          ReadableByteStreamControllerError(controller,r);
        }
      })["catch"](rethrowAssertionErrorRejection);
    }

    _createClass(ReadableByteStreamController,[{
      key:'close',
      value:functionclose(){
        if(IsReadableByteStreamController(this)===false){
          throwbyteStreamControllerBrandCheckException('close');
        }

        if(this._closeRequested===true){
          thrownewTypeError('Thestreamhasalreadybeenclosed;donotcloseitagain!');
        }

        varstate=this._controlledReadableStream._state;

        if(state!=='readable'){
          thrownewTypeError('Thestream(in'+state+'state)isnotinthereadablestateandcannotbeclosed');
        }

        ReadableByteStreamControllerClose(this);
      }
    },{
      key:'enqueue',
      value:functionenqueue(chunk){
        if(IsReadableByteStreamController(this)===false){
          throwbyteStreamControllerBrandCheckException('enqueue');
        }

        if(this._closeRequested===true){
          thrownewTypeError('streamisclosedordraining');
        }

        varstate=this._controlledReadableStream._state;

        if(state!=='readable'){
          thrownewTypeError('Thestream(in'+state+'state)isnotinthereadablestateandcannotbeenqueuedto');
        }

        if(!ArrayBuffer.isView(chunk)){
          thrownewTypeError('YoucanonlyenqueuearraybufferviewswhenusingaReadableByteStreamController');
        }

        ReadableByteStreamControllerEnqueue(this,chunk);
      }
    },{
      key:'error',
      value:functionerror(e){
        if(IsReadableByteStreamController(this)===false){
          throwbyteStreamControllerBrandCheckException('error');
        }

        varstream=this._controlledReadableStream;

        if(stream._state!=='readable'){
          thrownewTypeError('Thestreamis'+stream._state+'andsocannotbeerrored');
        }

        ReadableByteStreamControllerError(this,e);
      }
    },{
      key:'__cancelSteps',
      value:function__cancelSteps(reason){
        if(this._pendingPullIntos.length>0){
          varfirstDescriptor=this._pendingPullIntos[0];
          firstDescriptor.bytesFilled=0;
        }

        ResetQueue(this);
        returnPromiseInvokeOrNoop(this._underlyingByteSource,'cancel',[reason]);
      }
    },{
      key:'__pullSteps',
      value:function__pullSteps(){
        varstream=this._controlledReadableStream;
        assert(ReadableStreamHasDefaultReader(stream)===true);

        if(this._queueTotalSize>0){
          assert(ReadableStreamGetNumReadRequests(stream)===0);

          varentry=this._queue.shift();

          this._queueTotalSize-=entry.byteLength;
          ReadableByteStreamControllerHandleQueueDrain(this);
          varview=void0;

          try{
            view=newUint8Array(entry.buffer,entry.byteOffset,entry.byteLength);
          }catch(viewE){
            returnPromise.reject(viewE);
          }

          returnPromise.resolve(CreateIterResultObject(view,false));
        }

        varautoAllocateChunkSize=this._autoAllocateChunkSize;

        if(autoAllocateChunkSize!==undefined){
          varbuffer=void0;

          try{
            buffer=newArrayBuffer(autoAllocateChunkSize);
          }catch(bufferE){
            returnPromise.reject(bufferE);
          }

          varpullIntoDescriptor={
            buffer:buffer,
            byteOffset:0,
            byteLength:autoAllocateChunkSize,
            bytesFilled:0,
            elementSize:1,
            ctor:Uint8Array,
            readerType:'default'
          };

          this._pendingPullIntos.push(pullIntoDescriptor);
        }

        varpromise=ReadableStreamAddReadRequest(stream);
        ReadableByteStreamControllerCallPullIfNeeded(this);
        returnpromise;
      }
    },{
      key:'byobRequest',
      get:functionget(){
        if(IsReadableByteStreamController(this)===false){
          throwbyteStreamControllerBrandCheckException('byobRequest');
        }

        if(this._byobRequest===undefined&&this._pendingPullIntos.length>0){
          varfirstDescriptor=this._pendingPullIntos[0];
          varview=newUint8Array(firstDescriptor.buffer,firstDescriptor.byteOffset+firstDescriptor.bytesFilled,firstDescriptor.byteLength-firstDescriptor.bytesFilled);
          this._byobRequest=newReadableStreamBYOBRequest(this,view);
        }

        returnthis._byobRequest;
      }
    },{
      key:'desiredSize',
      get:functionget(){
        if(IsReadableByteStreamController(this)===false){
          throwbyteStreamControllerBrandCheckException('desiredSize');
        }

        returnReadableByteStreamControllerGetDesiredSize(this);
      }
    }]);

    returnReadableByteStreamController;
  }();

  functionIsReadableByteStreamController(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_underlyingByteSource')){
      returnfalse;
    }

    returntrue;
  }

  functionIsReadableStreamBYOBRequest(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_associatedReadableByteStreamController')){
      returnfalse;
    }

    returntrue;
  }

  functionReadableByteStreamControllerCallPullIfNeeded(controller){
    varshouldPull=ReadableByteStreamControllerShouldCallPull(controller);

    if(shouldPull===false){
      returnundefined;
    }

    if(controller._pulling===true){
      controller._pullAgain=true;
      returnundefined;
    }

    assert(controller._pullAgain===false);
    controller._pulling=true;
    varpullPromise=PromiseInvokeOrNoop(controller._underlyingByteSource,'pull',[controller]);
    pullPromise.then(function(){
      controller._pulling=false;

      if(controller._pullAgain===true){
        controller._pullAgain=false;
        ReadableByteStreamControllerCallPullIfNeeded(controller);
      }
    },function(e){
      if(controller._controlledReadableStream._state==='readable'){
        ReadableByteStreamControllerError(controller,e);
      }
    })["catch"](rethrowAssertionErrorRejection);
    returnundefined;
  }

  functionReadableByteStreamControllerClearPendingPullIntos(controller){
    ReadableByteStreamControllerInvalidateBYOBRequest(controller);
    controller._pendingPullIntos=[];
  }

  functionReadableByteStreamControllerCommitPullIntoDescriptor(stream,pullIntoDescriptor){
    assert(stream._state!=='errored','statemustnotbeerrored');
    vardone=false;

    if(stream._state==='closed'){
      assert(pullIntoDescriptor.bytesFilled===0);
      done=true;
    }

    varfilledView=ReadableByteStreamControllerConvertPullIntoDescriptor(pullIntoDescriptor);

    if(pullIntoDescriptor.readerType==='default'){
      ReadableStreamFulfillReadRequest(stream,filledView,done);
    }else{
      assert(pullIntoDescriptor.readerType==='byob');
      ReadableStreamFulfillReadIntoRequest(stream,filledView,done);
    }
  }

  functionReadableByteStreamControllerConvertPullIntoDescriptor(pullIntoDescriptor){
    varbytesFilled=pullIntoDescriptor.bytesFilled;
    varelementSize=pullIntoDescriptor.elementSize;
    assert(bytesFilled<=pullIntoDescriptor.byteLength);
    assert(bytesFilled%elementSize===0);
    returnnewpullIntoDescriptor.ctor(pullIntoDescriptor.buffer,pullIntoDescriptor.byteOffset,bytesFilled/elementSize);
  }

  functionReadableByteStreamControllerEnqueueChunkToQueue(controller,buffer,byteOffset,byteLength){
    controller._queue.push({
      buffer:buffer,
      byteOffset:byteOffset,
      byteLength:byteLength
    });

    controller._queueTotalSize+=byteLength;
  }

  functionReadableByteStreamControllerFillPullIntoDescriptorFromQueue(controller,pullIntoDescriptor){
    varelementSize=pullIntoDescriptor.elementSize;
    varcurrentAlignedBytes=pullIntoDescriptor.bytesFilled-pullIntoDescriptor.bytesFilled%elementSize;
    varmaxBytesToCopy=Math.min(controller._queueTotalSize,pullIntoDescriptor.byteLength-pullIntoDescriptor.bytesFilled);
    varmaxBytesFilled=pullIntoDescriptor.bytesFilled+maxBytesToCopy;
    varmaxAlignedBytes=maxBytesFilled-maxBytesFilled%elementSize;
    vartotalBytesToCopyRemaining=maxBytesToCopy;
    varready=false;

    if(maxAlignedBytes>currentAlignedBytes){
      totalBytesToCopyRemaining=maxAlignedBytes-pullIntoDescriptor.bytesFilled;
      ready=true;
    }

    varqueue=controller._queue;

    while(totalBytesToCopyRemaining>0){
      varheadOfQueue=queue[0];
      varbytesToCopy=Math.min(totalBytesToCopyRemaining,headOfQueue.byteLength);
      vardestStart=pullIntoDescriptor.byteOffset+pullIntoDescriptor.bytesFilled;
      ArrayBufferCopy(pullIntoDescriptor.buffer,destStart,headOfQueue.buffer,headOfQueue.byteOffset,bytesToCopy);

      if(headOfQueue.byteLength===bytesToCopy){
        queue.shift();
      }else{
        headOfQueue.byteOffset+=bytesToCopy;
        headOfQueue.byteLength-=bytesToCopy;
      }

      controller._queueTotalSize-=bytesToCopy;
      ReadableByteStreamControllerFillHeadPullIntoDescriptor(controller,bytesToCopy,pullIntoDescriptor);
      totalBytesToCopyRemaining-=bytesToCopy;
    }

    if(ready===false){
      assert(controller._queueTotalSize===0,'queuemustbeempty');
      assert(pullIntoDescriptor.bytesFilled>0);
      assert(pullIntoDescriptor.bytesFilled<pullIntoDescriptor.elementSize);
    }

    returnready;
  }

  functionReadableByteStreamControllerFillHeadPullIntoDescriptor(controller,size,pullIntoDescriptor){
    assert(controller._pendingPullIntos.length===0||controller._pendingPullIntos[0]===pullIntoDescriptor);
    ReadableByteStreamControllerInvalidateBYOBRequest(controller);
    pullIntoDescriptor.bytesFilled+=size;
  }

  functionReadableByteStreamControllerHandleQueueDrain(controller){
    assert(controller._controlledReadableStream._state==='readable');

    if(controller._queueTotalSize===0&&controller._closeRequested===true){
      ReadableStreamClose(controller._controlledReadableStream);
    }else{
      ReadableByteStreamControllerCallPullIfNeeded(controller);
    }
  }

  functionReadableByteStreamControllerInvalidateBYOBRequest(controller){
    if(controller._byobRequest===undefined){
      return;
    }

    controller._byobRequest._associatedReadableByteStreamController=undefined;
    controller._byobRequest._view=undefined;
    controller._byobRequest=undefined;
  }

  functionReadableByteStreamControllerProcessPullIntoDescriptorsUsingQueue(controller){
    assert(controller._closeRequested===false);

    while(controller._pendingPullIntos.length>0){
      if(controller._queueTotalSize===0){
        return;
      }

      varpullIntoDescriptor=controller._pendingPullIntos[0];

      if(ReadableByteStreamControllerFillPullIntoDescriptorFromQueue(controller,pullIntoDescriptor)===true){
        ReadableByteStreamControllerShiftPendingPullInto(controller);
        ReadableByteStreamControllerCommitPullIntoDescriptor(controller._controlledReadableStream,pullIntoDescriptor);
      }
    }
  }

  functionReadableByteStreamControllerPullInto(controller,view){
    varstream=controller._controlledReadableStream;
    varelementSize=1;

    if(view.constructor!==DataView){
      elementSize=view.constructor.BYTES_PER_ELEMENT;
    }

    varctor=view.constructor;
    varpullIntoDescriptor={
      buffer:view.buffer,
      byteOffset:view.byteOffset,
      byteLength:view.byteLength,
      bytesFilled:0,
      elementSize:elementSize,
      ctor:ctor,
      readerType:'byob'
    };

    if(controller._pendingPullIntos.length>0){
      pullIntoDescriptor.buffer=TransferArrayBuffer(pullIntoDescriptor.buffer);

      controller._pendingPullIntos.push(pullIntoDescriptor);

      returnReadableStreamAddReadIntoRequest(stream);
    }

    if(stream._state==='closed'){
      varemptyView=newview.constructor(pullIntoDescriptor.buffer,pullIntoDescriptor.byteOffset,0);
      returnPromise.resolve(CreateIterResultObject(emptyView,true));
    }

    if(controller._queueTotalSize>0){
      if(ReadableByteStreamControllerFillPullIntoDescriptorFromQueue(controller,pullIntoDescriptor)===true){
        varfilledView=ReadableByteStreamControllerConvertPullIntoDescriptor(pullIntoDescriptor);
        ReadableByteStreamControllerHandleQueueDrain(controller);
        returnPromise.resolve(CreateIterResultObject(filledView,false));
      }

      if(controller._closeRequested===true){
        vare=newTypeError('Insufficientbytestofillelementsinthegivenbuffer');
        ReadableByteStreamControllerError(controller,e);
        returnPromise.reject(e);
      }
    }

    pullIntoDescriptor.buffer=TransferArrayBuffer(pullIntoDescriptor.buffer);

    controller._pendingPullIntos.push(pullIntoDescriptor);

    varpromise=ReadableStreamAddReadIntoRequest(stream);
    ReadableByteStreamControllerCallPullIfNeeded(controller);
    returnpromise;
  }

  functionReadableByteStreamControllerRespondInClosedState(controller,firstDescriptor){
    firstDescriptor.buffer=TransferArrayBuffer(firstDescriptor.buffer);
    assert(firstDescriptor.bytesFilled===0,'bytesFilledmustbe0');
    varstream=controller._controlledReadableStream;

    if(ReadableStreamHasBYOBReader(stream)===true){
      while(ReadableStreamGetNumReadIntoRequests(stream)>0){
        varpullIntoDescriptor=ReadableByteStreamControllerShiftPendingPullInto(controller);
        ReadableByteStreamControllerCommitPullIntoDescriptor(stream,pullIntoDescriptor);
      }
    }
  }

  functionReadableByteStreamControllerRespondInReadableState(controller,bytesWritten,pullIntoDescriptor){
    if(pullIntoDescriptor.bytesFilled+bytesWritten>pullIntoDescriptor.byteLength){
      thrownewRangeError('bytesWrittenoutofrange');
    }

    ReadableByteStreamControllerFillHeadPullIntoDescriptor(controller,bytesWritten,pullIntoDescriptor);

    if(pullIntoDescriptor.bytesFilled<pullIntoDescriptor.elementSize){
      return;
    }

    ReadableByteStreamControllerShiftPendingPullInto(controller);
    varremainderSize=pullIntoDescriptor.bytesFilled%pullIntoDescriptor.elementSize;

    if(remainderSize>0){
      varend=pullIntoDescriptor.byteOffset+pullIntoDescriptor.bytesFilled;
      varremainder=pullIntoDescriptor.buffer.slice(end-remainderSize,end);
      ReadableByteStreamControllerEnqueueChunkToQueue(controller,remainder,0,remainder.byteLength);
    }

    pullIntoDescriptor.buffer=TransferArrayBuffer(pullIntoDescriptor.buffer);
    pullIntoDescriptor.bytesFilled-=remainderSize;
    ReadableByteStreamControllerCommitPullIntoDescriptor(controller._controlledReadableStream,pullIntoDescriptor);
    ReadableByteStreamControllerProcessPullIntoDescriptorsUsingQueue(controller);
  }

  functionReadableByteStreamControllerRespondInternal(controller,bytesWritten){
    varfirstDescriptor=controller._pendingPullIntos[0];
    varstream=controller._controlledReadableStream;

    if(stream._state==='closed'){
      if(bytesWritten!==0){
        thrownewTypeError('bytesWrittenmustbe0whencallingrespond()onaclosedstream');
      }

      ReadableByteStreamControllerRespondInClosedState(controller,firstDescriptor);
    }else{
      assert(stream._state==='readable');
      ReadableByteStreamControllerRespondInReadableState(controller,bytesWritten,firstDescriptor);
    }
  }

  functionReadableByteStreamControllerShiftPendingPullInto(controller){
    vardescriptor=controller._pendingPullIntos.shift();

    ReadableByteStreamControllerInvalidateBYOBRequest(controller);
    returndescriptor;
  }

  functionReadableByteStreamControllerShouldCallPull(controller){
    varstream=controller._controlledReadableStream;

    if(stream._state!=='readable'){
      returnfalse;
    }

    if(controller._closeRequested===true){
      returnfalse;
    }

    if(controller._started===false){
      returnfalse;
    }

    if(ReadableStreamHasDefaultReader(stream)===true&&ReadableStreamGetNumReadRequests(stream)>0){
      returntrue;
    }

    if(ReadableStreamHasBYOBReader(stream)===true&&ReadableStreamGetNumReadIntoRequests(stream)>0){
      returntrue;
    }

    if(ReadableByteStreamControllerGetDesiredSize(controller)>0){
      returntrue;
    }

    returnfalse;
  }

  functionReadableByteStreamControllerClose(controller){
    varstream=controller._controlledReadableStream;
    assert(controller._closeRequested===false);
    assert(stream._state==='readable');

    if(controller._queueTotalSize>0){
      controller._closeRequested=true;
      return;
    }

    if(controller._pendingPullIntos.length>0){
      varfirstPendingPullInto=controller._pendingPullIntos[0];

      if(firstPendingPullInto.bytesFilled>0){
        vare=newTypeError('Insufficientbytestofillelementsinthegivenbuffer');
        ReadableByteStreamControllerError(controller,e);
        throwe;
      }
    }

    ReadableStreamClose(stream);
  }

  functionReadableByteStreamControllerEnqueue(controller,chunk){
    varstream=controller._controlledReadableStream;
    assert(controller._closeRequested===false);
    assert(stream._state==='readable');
    varbuffer=chunk.buffer;
    varbyteOffset=chunk.byteOffset;
    varbyteLength=chunk.byteLength;
    vartransferredBuffer=TransferArrayBuffer(buffer);

    if(ReadableStreamHasDefaultReader(stream)===true){
      if(ReadableStreamGetNumReadRequests(stream)===0){
        ReadableByteStreamControllerEnqueueChunkToQueue(controller,transferredBuffer,byteOffset,byteLength);
      }else{
        assert(controller._queue.length===0);
        vartransferredView=newUint8Array(transferredBuffer,byteOffset,byteLength);
        ReadableStreamFulfillReadRequest(stream,transferredView,false);
      }
    }elseif(ReadableStreamHasBYOBReader(stream)===true){
      ReadableByteStreamControllerEnqueueChunkToQueue(controller,transferredBuffer,byteOffset,byteLength);
      ReadableByteStreamControllerProcessPullIntoDescriptorsUsingQueue(controller);
    }else{
      assert(IsReadableStreamLocked(stream)===false,'streammustnotbelocked');
      ReadableByteStreamControllerEnqueueChunkToQueue(controller,transferredBuffer,byteOffset,byteLength);
    }
  }

  functionReadableByteStreamControllerError(controller,e){
    varstream=controller._controlledReadableStream;
    assert(stream._state==='readable');
    ReadableByteStreamControllerClearPendingPullIntos(controller);
    ResetQueue(controller);
    ReadableStreamError(stream,e);
  }

  functionReadableByteStreamControllerGetDesiredSize(controller){
    varstream=controller._controlledReadableStream;
    varstate=stream._state;

    if(state==='errored'){
      returnnull;
    }

    if(state==='closed'){
      return0;
    }

    returncontroller._strategyHWM-controller._queueTotalSize;
  }

  functionReadableByteStreamControllerRespond(controller,bytesWritten){
    bytesWritten=Number(bytesWritten);

    if(IsFiniteNonNegativeNumber(bytesWritten)===false){
      thrownewRangeError('bytesWrittenmustbeafinite');
    }

    assert(controller._pendingPullIntos.length>0);
    ReadableByteStreamControllerRespondInternal(controller,bytesWritten);
  }

  functionReadableByteStreamControllerRespondWithNewView(controller,view){
    assert(controller._pendingPullIntos.length>0);
    varfirstDescriptor=controller._pendingPullIntos[0];

    if(firstDescriptor.byteOffset+firstDescriptor.bytesFilled!==view.byteOffset){
      thrownewRangeError('TheregionspecifiedbyviewdoesnotmatchbyobRequest');
    }

    if(firstDescriptor.byteLength!==view.byteLength){
      thrownewRangeError('ThebufferofviewhasdifferentcapacitythanbyobRequest');
    }

    firstDescriptor.buffer=view.buffer;
    ReadableByteStreamControllerRespondInternal(controller,view.byteLength);
  }

  functionstreamBrandCheckException(name){
    returnnewTypeError('ReadableStream.prototype.'+name+'canonlybeusedonaReadableStream');
  }

  functionreaderLockException(name){
    returnnewTypeError('Cannot'+name+'astreamusingareleasedreader');
  }

  functiondefaultReaderBrandCheckException(name){
    returnnewTypeError('ReadableStreamDefaultReader.prototype.'+name+'canonlybeusedonaReadableStreamDefaultReader');
  }

  functiondefaultReaderClosedPromiseInitialize(reader){
    reader._closedPromise=newPromise(function(resolve,reject){
      reader._closedPromise_resolve=resolve;
      reader._closedPromise_reject=reject;
    });
  }

  functiondefaultReaderClosedPromiseInitializeAsRejected(reader,reason){
    reader._closedPromise=Promise.reject(reason);
    reader._closedPromise_resolve=undefined;
    reader._closedPromise_reject=undefined;
  }

  functiondefaultReaderClosedPromiseInitializeAsResolved(reader){
    reader._closedPromise=Promise.resolve(undefined);
    reader._closedPromise_resolve=undefined;
    reader._closedPromise_reject=undefined;
  }

  functiondefaultReaderClosedPromiseReject(reader,reason){
    assert(reader._closedPromise_resolve!==undefined);
    assert(reader._closedPromise_reject!==undefined);

    reader._closedPromise_reject(reason);

    reader._closedPromise_resolve=undefined;
    reader._closedPromise_reject=undefined;
  }

  functiondefaultReaderClosedPromiseResetToRejected(reader,reason){
    assert(reader._closedPromise_resolve===undefined);
    assert(reader._closedPromise_reject===undefined);
    reader._closedPromise=Promise.reject(reason);
  }

  functiondefaultReaderClosedPromiseResolve(reader){
    assert(reader._closedPromise_resolve!==undefined);
    assert(reader._closedPromise_reject!==undefined);

    reader._closedPromise_resolve(undefined);

    reader._closedPromise_resolve=undefined;
    reader._closedPromise_reject=undefined;
  }

  functionbyobReaderBrandCheckException(name){
    returnnewTypeError('ReadableStreamBYOBReader.prototype.'+name+'canonlybeusedonaReadableStreamBYOBReader');
  }

  functiondefaultControllerBrandCheckException(name){
    returnnewTypeError('ReadableStreamDefaultController.prototype.'+name+'canonlybeusedonaReadableStreamDefaultController');
  }

  functionbyobRequestBrandCheckException(name){
    returnnewTypeError('ReadableStreamBYOBRequest.prototype.'+name+'canonlybeusedonaReadableStreamBYOBRequest');
  }

  functionbyteStreamControllerBrandCheckException(name){
    returnnewTypeError('ReadableByteStreamController.prototype.'+name+'canonlybeusedonaReadableByteStreamController');
  }

  functionifIsObjectAndHasAPromiseIsHandledInternalSlotSetPromiseIsHandledToTrue(promise){
    try{
      Promise.prototype.then.call(promise,undefined,function(){});
    }catch(e){}
  }
},function(module,exports,__w_pdfjs_require__){
  "usestrict";

  vartransformStream=__w_pdfjs_require__(6);

  varreadableStream=__w_pdfjs_require__(4);

  varwritableStream=__w_pdfjs_require__(2);

  exports.TransformStream=transformStream.TransformStream;
  exports.ReadableStream=readableStream.ReadableStream;
  exports.IsReadableStreamDisturbed=readableStream.IsReadableStreamDisturbed;
  exports.ReadableStreamDefaultControllerClose=readableStream.ReadableStreamDefaultControllerClose;
  exports.ReadableStreamDefaultControllerEnqueue=readableStream.ReadableStreamDefaultControllerEnqueue;
  exports.ReadableStreamDefaultControllerError=readableStream.ReadableStreamDefaultControllerError;
  exports.ReadableStreamDefaultControllerGetDesiredSize=readableStream.ReadableStreamDefaultControllerGetDesiredSize;
  exports.AcquireWritableStreamDefaultWriter=writableStream.AcquireWritableStreamDefaultWriter;
  exports.IsWritableStream=writableStream.IsWritableStream;
  exports.IsWritableStreamLocked=writableStream.IsWritableStreamLocked;
  exports.WritableStream=writableStream.WritableStream;
  exports.WritableStreamAbort=writableStream.WritableStreamAbort;
  exports.WritableStreamDefaultControllerError=writableStream.WritableStreamDefaultControllerError;
  exports.WritableStreamDefaultWriterCloseWithErrorPropagation=writableStream.WritableStreamDefaultWriterCloseWithErrorPropagation;
  exports.WritableStreamDefaultWriterRelease=writableStream.WritableStreamDefaultWriterRelease;
  exports.WritableStreamDefaultWriterWrite=writableStream.WritableStreamDefaultWriterWrite;
},function(module,exports,__w_pdfjs_require__){
  "usestrict";

  var_createClass=function(){
    functiondefineProperties(target,props){
      for(vari=0;i<props.length;i++){
        vardescriptor=props[i];
        descriptor.enumerable=descriptor.enumerable||false;
        descriptor.configurable=true;
        if("value"indescriptor)descriptor.writable=true;
        Object.defineProperty(target,descriptor.key,descriptor);
      }
    }

    returnfunction(Constructor,protoProps,staticProps){
      if(protoProps)defineProperties(Constructor.prototype,protoProps);
      if(staticProps)defineProperties(Constructor,staticProps);
      returnConstructor;
    };
  }();

  function_classCallCheck(instance,Constructor){
    if(!(instanceinstanceofConstructor)){
      thrownewTypeError("Cannotcallaclassasafunction");
    }
  }

  var_require=__w_pdfjs_require__(1),
      assert=_require.assert;

  var_require2=__w_pdfjs_require__(0),
      InvokeOrNoop=_require2.InvokeOrNoop,
      PromiseInvokeOrPerformFallback=_require2.PromiseInvokeOrPerformFallback,
      PromiseInvokeOrNoop=_require2.PromiseInvokeOrNoop,
      typeIsObject=_require2.typeIsObject;

  var_require3=__w_pdfjs_require__(4),
      ReadableStream=_require3.ReadableStream,
      ReadableStreamDefaultControllerClose=_require3.ReadableStreamDefaultControllerClose,
      ReadableStreamDefaultControllerEnqueue=_require3.ReadableStreamDefaultControllerEnqueue,
      ReadableStreamDefaultControllerError=_require3.ReadableStreamDefaultControllerError,
      ReadableStreamDefaultControllerGetDesiredSize=_require3.ReadableStreamDefaultControllerGetDesiredSize;

  var_require4=__w_pdfjs_require__(2),
      WritableStream=_require4.WritableStream,
      WritableStreamDefaultControllerError=_require4.WritableStreamDefaultControllerError;

  functionTransformStreamCloseReadable(transformStream){
    if(transformStream._errored===true){
      thrownewTypeError('TransformStreamisalreadyerrored');
    }

    if(transformStream._readableClosed===true){
      thrownewTypeError('Readablesideisalreadyclosed');
    }

    TransformStreamCloseReadableInternal(transformStream);
  }

  functionTransformStreamEnqueueToReadable(transformStream,chunk){
    if(transformStream._errored===true){
      thrownewTypeError('TransformStreamisalreadyerrored');
    }

    if(transformStream._readableClosed===true){
      thrownewTypeError('Readablesideisalreadyclosed');
    }

    varcontroller=transformStream._readableController;

    try{
      ReadableStreamDefaultControllerEnqueue(controller,chunk);
    }catch(e){
      transformStream._readableClosed=true;
      TransformStreamErrorIfNeeded(transformStream,e);
      throwtransformStream._storedError;
    }

    vardesiredSize=ReadableStreamDefaultControllerGetDesiredSize(controller);
    varmaybeBackpressure=desiredSize<=0;

    if(maybeBackpressure===true&&transformStream._backpressure===false){
      TransformStreamSetBackpressure(transformStream,true);
    }
  }

  functionTransformStreamError(transformStream,e){
    if(transformStream._errored===true){
      thrownewTypeError('TransformStreamisalreadyerrored');
    }

    TransformStreamErrorInternal(transformStream,e);
  }

  functionTransformStreamCloseReadableInternal(transformStream){
    assert(transformStream._errored===false);
    assert(transformStream._readableClosed===false);

    try{
      ReadableStreamDefaultControllerClose(transformStream._readableController);
    }catch(e){
      assert(false);
    }

    transformStream._readableClosed=true;
  }

  functionTransformStreamErrorIfNeeded(transformStream,e){
    if(transformStream._errored===false){
      TransformStreamErrorInternal(transformStream,e);
    }
  }

  functionTransformStreamErrorInternal(transformStream,e){
    assert(transformStream._errored===false);
    transformStream._errored=true;
    transformStream._storedError=e;

    if(transformStream._writableDone===false){
      WritableStreamDefaultControllerError(transformStream._writableController,e);
    }

    if(transformStream._readableClosed===false){
      ReadableStreamDefaultControllerError(transformStream._readableController,e);
    }
  }

  functionTransformStreamReadableReadyPromise(transformStream){
    assert(transformStream._backpressureChangePromise!==undefined,'_backpressureChangePromiseshouldhavebeeninitialized');

    if(transformStream._backpressure===false){
      returnPromise.resolve();
    }

    assert(transformStream._backpressure===true,'_backpressureshouldhavebeeninitialized');
    returntransformStream._backpressureChangePromise;
  }

  functionTransformStreamSetBackpressure(transformStream,backpressure){
    assert(transformStream._backpressure!==backpressure,'TransformStreamSetBackpressure()shouldbecalledonlywhenbackpressureischanged');

    if(transformStream._backpressureChangePromise!==undefined){
      transformStream._backpressureChangePromise_resolve(backpressure);
    }

    transformStream._backpressureChangePromise=newPromise(function(resolve){
      transformStream._backpressureChangePromise_resolve=resolve;
    });

    transformStream._backpressureChangePromise.then(function(resolution){
      assert(resolution!==backpressure,'_backpressureChangePromiseshouldbefulfilledonlywhenbackpressureischanged');
    });

    transformStream._backpressure=backpressure;
  }

  functionTransformStreamDefaultTransform(chunk,transformStreamController){
    vartransformStream=transformStreamController._controlledTransformStream;
    TransformStreamEnqueueToReadable(transformStream,chunk);
    returnPromise.resolve();
  }

  functionTransformStreamTransform(transformStream,chunk){
    assert(transformStream._errored===false);
    assert(transformStream._transforming===false);
    assert(transformStream._backpressure===false);
    transformStream._transforming=true;
    vartransformer=transformStream._transformer;
    varcontroller=transformStream._transformStreamController;
    vartransformPromise=PromiseInvokeOrPerformFallback(transformer,'transform',[chunk,controller],TransformStreamDefaultTransform,[chunk,controller]);
    returntransformPromise.then(function(){
      transformStream._transforming=false;
      returnTransformStreamReadableReadyPromise(transformStream);
    },function(e){
      TransformStreamErrorIfNeeded(transformStream,e);
      returnPromise.reject(e);
    });
  }

  functionIsTransformStreamDefaultController(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_controlledTransformStream')){
      returnfalse;
    }

    returntrue;
  }

  functionIsTransformStream(x){
    if(!typeIsObject(x)){
      returnfalse;
    }

    if(!Object.prototype.hasOwnProperty.call(x,'_transformStreamController')){
      returnfalse;
    }

    returntrue;
  }

  varTransformStreamSink=function(){
    functionTransformStreamSink(transformStream,startPromise){
      _classCallCheck(this,TransformStreamSink);

      this._transformStream=transformStream;
      this._startPromise=startPromise;
    }

    _createClass(TransformStreamSink,[{
      key:'start',
      value:functionstart(c){
        vartransformStream=this._transformStream;
        transformStream._writableController=c;
        returnthis._startPromise.then(function(){
          returnTransformStreamReadableReadyPromise(transformStream);
        });
      }
    },{
      key:'write',
      value:functionwrite(chunk){
        vartransformStream=this._transformStream;
        returnTransformStreamTransform(transformStream,chunk);
      }
    },{
      key:'abort',
      value:functionabort(){
        vartransformStream=this._transformStream;
        transformStream._writableDone=true;
        TransformStreamErrorInternal(transformStream,newTypeError('Writablesideaborted'));
      }
    },{
      key:'close',
      value:functionclose(){
        vartransformStream=this._transformStream;
        assert(transformStream._transforming===false);
        transformStream._writableDone=true;
        varflushPromise=PromiseInvokeOrNoop(transformStream._transformer,'flush',[transformStream._transformStreamController]);
        returnflushPromise.then(function(){
          if(transformStream._errored===true){
            returnPromise.reject(transformStream._storedError);
          }

          if(transformStream._readableClosed===false){
            TransformStreamCloseReadableInternal(transformStream);
          }

          returnPromise.resolve();
        })["catch"](function(r){
          TransformStreamErrorIfNeeded(transformStream,r);
          returnPromise.reject(transformStream._storedError);
        });
      }
    }]);

    returnTransformStreamSink;
  }();

  varTransformStreamSource=function(){
    functionTransformStreamSource(transformStream,startPromise){
      _classCallCheck(this,TransformStreamSource);

      this._transformStream=transformStream;
      this._startPromise=startPromise;
    }

    _createClass(TransformStreamSource,[{
      key:'start',
      value:functionstart(c){
        vartransformStream=this._transformStream;
        transformStream._readableController=c;
        returnthis._startPromise.then(function(){
          assert(transformStream._backpressureChangePromise!==undefined,'_backpressureChangePromiseshouldhavebeeninitialized');

          if(transformStream._backpressure===true){
            returnPromise.resolve();
          }

          assert(transformStream._backpressure===false,'_backpressureshouldhavebeeninitialized');
          returntransformStream._backpressureChangePromise;
        });
      }
    },{
      key:'pull',
      value:functionpull(){
        vartransformStream=this._transformStream;
        assert(transformStream._backpressure===true,'pull()shouldbenevercalledwhile_backpressureisfalse');
        assert(transformStream._backpressureChangePromise!==undefined,'_backpressureChangePromiseshouldhavebeeninitialized');
        TransformStreamSetBackpressure(transformStream,false);
        returntransformStream._backpressureChangePromise;
      }
    },{
      key:'cancel',
      value:functioncancel(){
        vartransformStream=this._transformStream;
        transformStream._readableClosed=true;
        TransformStreamErrorInternal(transformStream,newTypeError('Readablesidecanceled'));
      }
    }]);

    returnTransformStreamSource;
  }();

  varTransformStreamDefaultController=function(){
    functionTransformStreamDefaultController(transformStream){
      _classCallCheck(this,TransformStreamDefaultController);

      if(IsTransformStream(transformStream)===false){
        thrownewTypeError('TransformStreamDefaultControllercanonlybe'+'constructedwithaTransformStreaminstance');
      }

      if(transformStream._transformStreamController!==undefined){
        thrownewTypeError('TransformStreamDefaultControllerinstancescan'+'onlybecreatedbytheTransformStreamconstructor');
      }

      this._controlledTransformStream=transformStream;
    }

    _createClass(TransformStreamDefaultController,[{
      key:'enqueue',
      value:functionenqueue(chunk){
        if(IsTransformStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('enqueue');
        }

        TransformStreamEnqueueToReadable(this._controlledTransformStream,chunk);
      }
    },{
      key:'close',
      value:functionclose(){
        if(IsTransformStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('close');
        }

        TransformStreamCloseReadable(this._controlledTransformStream);
      }
    },{
      key:'error',
      value:functionerror(reason){
        if(IsTransformStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('error');
        }

        TransformStreamError(this._controlledTransformStream,reason);
      }
    },{
      key:'desiredSize',
      get:functionget(){
        if(IsTransformStreamDefaultController(this)===false){
          throwdefaultControllerBrandCheckException('desiredSize');
        }

        vartransformStream=this._controlledTransformStream;
        varreadableController=transformStream._readableController;
        returnReadableStreamDefaultControllerGetDesiredSize(readableController);
      }
    }]);

    returnTransformStreamDefaultController;
  }();

  varTransformStream=function(){
    functionTransformStream(){
      vartransformer=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};

      _classCallCheck(this,TransformStream);

      this._transformer=transformer;
      varreadableStrategy=transformer.readableStrategy,
          writableStrategy=transformer.writableStrategy;
      this._transforming=false;
      this._errored=false;
      this._storedError=undefined;
      this._writableController=undefined;
      this._readableController=undefined;
      this._transformStreamController=undefined;
      this._writableDone=false;
      this._readableClosed=false;
      this._backpressure=undefined;
      this._backpressureChangePromise=undefined;
      this._backpressureChangePromise_resolve=undefined;
      this._transformStreamController=newTransformStreamDefaultController(this);
      varstartPromise_resolve=void0;
      varstartPromise=newPromise(function(resolve){
        startPromise_resolve=resolve;
      });
      varsource=newTransformStreamSource(this,startPromise);
      this._readable=newReadableStream(source,readableStrategy);
      varsink=newTransformStreamSink(this,startPromise);
      this._writable=newWritableStream(sink,writableStrategy);
      assert(this._writableController!==undefined);
      assert(this._readableController!==undefined);
      vardesiredSize=ReadableStreamDefaultControllerGetDesiredSize(this._readableController);
      TransformStreamSetBackpressure(this,desiredSize<=0);
      vartransformStream=this;
      varstartResult=InvokeOrNoop(transformer,'start',[transformStream._transformStreamController]);
      startPromise_resolve(startResult);
      startPromise["catch"](function(e){
        if(transformStream._errored===false){
          transformStream._errored=true;
          transformStream._storedError=e;
        }
      });
    }

    _createClass(TransformStream,[{
      key:'readable',
      get:functionget(){
        if(IsTransformStream(this)===false){
          throwstreamBrandCheckException('readable');
        }

        returnthis._readable;
      }
    },{
      key:'writable',
      get:functionget(){
        if(IsTransformStream(this)===false){
          throwstreamBrandCheckException('writable');
        }

        returnthis._writable;
      }
    }]);

    returnTransformStream;
  }();

  module.exports={
    TransformStream:TransformStream
  };

  functiondefaultControllerBrandCheckException(name){
    returnnewTypeError('TransformStreamDefaultController.prototype.'+name+'canonlybeusedonaTransformStreamDefaultController');
  }

  functionstreamBrandCheckException(name){
    returnnewTypeError('TransformStream.prototype.'+name+'canonlybeusedonaTransformStream');
  }
},function(module,exports,__w_pdfjs_require__){
  module.exports=__w_pdfjs_require__(5);
}]));

/***/}),
/*145*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

{
  varisURLSupported=false;

  try{
    if(typeofURL==='function'&&_typeof(URL.prototype)==='object'&&'origin'inURL.prototype){
      varu=newURL('b','http://a');
      u.pathname='c%20d';
      isURLSupported=u.href==='http://a/c%20d';
    }
  }catch(ex){}

  if(isURLSupported){
    exports.URL=URL;
  }else{
    varPolyfillURL=__w_pdfjs_require__(146).URL;

    varOriginalURL=__w_pdfjs_require__(3).URL;

    if(OriginalURL){
      PolyfillURL.createObjectURL=function(blob){
        returnOriginalURL.createObjectURL.apply(OriginalURL,arguments);
      };

      PolyfillURL.revokeObjectURL=function(url){
        OriginalURL.revokeObjectURL(url);
      };
    }

    exports.URL=PolyfillURL;
  }
}

/***/}),
/*146*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


(functionURLConstructorClosure(){
  'usestrict';

  varrelative=Object.create(null);
  relative['ftp']=21;
  relative['file']=0;
  relative['gopher']=70;
  relative['http']=80;
  relative['https']=443;
  relative['ws']=80;
  relative['wss']=443;
  varrelativePathDotMapping=Object.create(null);
  relativePathDotMapping['%2e']='.';
  relativePathDotMapping['.%2e']='..';
  relativePathDotMapping['%2e.']='..';
  relativePathDotMapping['%2e%2e']='..';

  functionisRelativeScheme(scheme){
    returnrelative[scheme]!==undefined;
  }

  functioninvalid(){
    clear.call(this);
    this._isInvalid=true;
  }

  functionIDNAToASCII(h){
    if(h===''){
      invalid.call(this);
    }

    returnh.toLowerCase();
  }

  functionpercentEscape(c){
    varunicode=c.charCodeAt(0);

    if(unicode>0x20&&unicode<0x7F&&[0x22,0x23,0x3C,0x3E,0x3F,0x60].indexOf(unicode)===-1){
      returnc;
    }

    returnencodeURIComponent(c);
  }

  functionpercentEscapeQuery(c){
    varunicode=c.charCodeAt(0);

    if(unicode>0x20&&unicode<0x7F&&[0x22,0x23,0x3C,0x3E,0x60].indexOf(unicode)===-1){
      returnc;
    }

    returnencodeURIComponent(c);
  }

  varEOF,
      ALPHA=/[a-zA-Z]/,
      ALPHANUMERIC=/[a-zA-Z0-9\+\-\.]/;

  functionparse(input,stateOverride,base){
    functionerr(message){
      errors.push(message);
    }

    varstate=stateOverride||'schemestart',
        cursor=0,
        buffer='',
        seenAt=false,
        seenBracket=false,
        errors=[];

    loop:while((input[cursor-1]!==EOF||cursor===0)&&!this._isInvalid){
      varc=input[cursor];

      switch(state){
        case'schemestart':
          if(c&&ALPHA.test(c)){
            buffer+=c.toLowerCase();
            state='scheme';
          }elseif(!stateOverride){
            buffer='';
            state='noscheme';
            continue;
          }else{
            err('Invalidscheme.');
            breakloop;
          }

          break;

        case'scheme':
          if(c&&ALPHANUMERIC.test(c)){
            buffer+=c.toLowerCase();
          }elseif(c===':'){
            this._scheme=buffer;
            buffer='';

            if(stateOverride){
              breakloop;
            }

            if(isRelativeScheme(this._scheme)){
              this._isRelative=true;
            }

            if(this._scheme==='file'){
              state='relative';
            }elseif(this._isRelative&&base&&base._scheme===this._scheme){
              state='relativeorauthority';
            }elseif(this._isRelative){
              state='authorityfirstslash';
            }else{
              state='schemedata';
            }
          }elseif(!stateOverride){
            buffer='';
            cursor=0;
            state='noscheme';
            continue;
          }elseif(c===EOF){
            breakloop;
          }else{
            err('Codepointnotallowedinscheme:'+c);
            breakloop;
          }

          break;

        case'schemedata':
          if(c==='?'){
            this._query='?';
            state='query';
          }elseif(c==='#'){
            this._fragment='#';
            state='fragment';
          }else{
            if(c!==EOF&&c!=='\t'&&c!=='\n'&&c!=='\r'){
              this._schemeData+=percentEscape(c);
            }
          }

          break;

        case'noscheme':
          if(!base||!isRelativeScheme(base._scheme)){
            err('Missingscheme.');
            invalid.call(this);
          }else{
            state='relative';
            continue;
          }

          break;

        case'relativeorauthority':
          if(c==='/'&&input[cursor+1]==='/'){
            state='authorityignoreslashes';
          }else{
            err('Expected/,got:'+c);
            state='relative';
            continue;
          }

          break;

        case'relative':
          this._isRelative=true;

          if(this._scheme!=='file'){
            this._scheme=base._scheme;
          }

          if(c===EOF){
            this._host=base._host;
            this._port=base._port;
            this._path=base._path.slice();
            this._query=base._query;
            this._username=base._username;
            this._password=base._password;
            breakloop;
          }elseif(c==='/'||c==='\\'){
            if(c==='\\'){
              err('\\isaninvalidcodepoint.');
            }

            state='relativeslash';
          }elseif(c==='?'){
            this._host=base._host;
            this._port=base._port;
            this._path=base._path.slice();
            this._query='?';
            this._username=base._username;
            this._password=base._password;
            state='query';
          }elseif(c==='#'){
            this._host=base._host;
            this._port=base._port;
            this._path=base._path.slice();
            this._query=base._query;
            this._fragment='#';
            this._username=base._username;
            this._password=base._password;
            state='fragment';
          }else{
            varnextC=input[cursor+1];
            varnextNextC=input[cursor+2];

            if(this._scheme!=='file'||!ALPHA.test(c)||nextC!==':'&&nextC!=='|'||nextNextC!==EOF&&nextNextC!=='/'&&nextNextC!=='\\'&&nextNextC!=='?'&&nextNextC!=='#'){
              this._host=base._host;
              this._port=base._port;
              this._username=base._username;
              this._password=base._password;
              this._path=base._path.slice();

              this._path.pop();
            }

            state='relativepath';
            continue;
          }

          break;

        case'relativeslash':
          if(c==='/'||c==='\\'){
            if(c==='\\'){
              err('\\isaninvalidcodepoint.');
            }

            if(this._scheme==='file'){
              state='filehost';
            }else{
              state='authorityignoreslashes';
            }
          }else{
            if(this._scheme!=='file'){
              this._host=base._host;
              this._port=base._port;
              this._username=base._username;
              this._password=base._password;
            }

            state='relativepath';
            continue;
          }

          break;

        case'authorityfirstslash':
          if(c==='/'){
            state='authoritysecondslash';
          }else{
            err('Expected\'/\',got:'+c);
            state='authorityignoreslashes';
            continue;
          }

          break;

        case'authoritysecondslash':
          state='authorityignoreslashes';

          if(c!=='/'){
            err('Expected\'/\',got:'+c);
            continue;
          }

          break;

        case'authorityignoreslashes':
          if(c!=='/'&&c!=='\\'){
            state='authority';
            continue;
          }else{
            err('Expectedauthority,got:'+c);
          }

          break;

        case'authority':
          if(c==='@'){
            if(seenAt){
              err('@alreadyseen.');
              buffer+='%40';
            }

            seenAt=true;

            for(vari=0;i<buffer.length;i++){
              varcp=buffer[i];

              if(cp==='\t'||cp==='\n'||cp==='\r'){
                err('Invalidwhitespaceinauthority.');
                continue;
              }

              if(cp===':'&&this._password===null){
                this._password='';
                continue;
              }

              vartempC=percentEscape(cp);

              if(this._password!==null){
                this._password+=tempC;
              }else{
                this._username+=tempC;
              }
            }

            buffer='';
          }elseif(c===EOF||c==='/'||c==='\\'||c==='?'||c==='#'){
            cursor-=buffer.length;
            buffer='';
            state='host';
            continue;
          }else{
            buffer+=c;
          }

          break;

        case'filehost':
          if(c===EOF||c==='/'||c==='\\'||c==='?'||c==='#'){
            if(buffer.length===2&&ALPHA.test(buffer[0])&&(buffer[1]===':'||buffer[1]==='|')){
              state='relativepath';
            }elseif(buffer.length===0){
              state='relativepathstart';
            }else{
              this._host=IDNAToASCII.call(this,buffer);
              buffer='';
              state='relativepathstart';
            }

            continue;
          }elseif(c==='\t'||c==='\n'||c==='\r'){
            err('Invalidwhitespaceinfilehost.');
          }else{
            buffer+=c;
          }

          break;

        case'host':
        case'hostname':
          if(c===':'&&!seenBracket){
            this._host=IDNAToASCII.call(this,buffer);
            buffer='';
            state='port';

            if(stateOverride==='hostname'){
              breakloop;
            }
          }elseif(c===EOF||c==='/'||c==='\\'||c==='?'||c==='#'){
            this._host=IDNAToASCII.call(this,buffer);
            buffer='';
            state='relativepathstart';

            if(stateOverride){
              breakloop;
            }

            continue;
          }elseif(c!=='\t'&&c!=='\n'&&c!=='\r'){
            if(c==='['){
              seenBracket=true;
            }elseif(c===']'){
              seenBracket=false;
            }

            buffer+=c;
          }else{
            err('Invalidcodepointinhost/hostname:'+c);
          }

          break;

        case'port':
          if(/[0-9]/.test(c)){
            buffer+=c;
          }elseif(c===EOF||c==='/'||c==='\\'||c==='?'||c==='#'||stateOverride){
            if(buffer!==''){
              vartemp=parseInt(buffer,10);

              if(temp!==relative[this._scheme]){
                this._port=temp+'';
              }

              buffer='';
            }

            if(stateOverride){
              breakloop;
            }

            state='relativepathstart';
            continue;
          }elseif(c==='\t'||c==='\n'||c==='\r'){
            err('Invalidcodepointinport:'+c);
          }else{
            invalid.call(this);
          }

          break;

        case'relativepathstart':
          if(c==='\\'){
            err('\'\\\'notallowedinpath.');
          }

          state='relativepath';

          if(c!=='/'&&c!=='\\'){
            continue;
          }

          break;

        case'relativepath':
          if(c===EOF||c==='/'||c==='\\'||!stateOverride&&(c==='?'||c==='#')){
            if(c==='\\'){
              err('\\notallowedinrelativepath.');
            }

            vartmp;

            if(tmp=relativePathDotMapping[buffer.toLowerCase()]){
              buffer=tmp;
            }

            if(buffer==='..'){
              this._path.pop();

              if(c!=='/'&&c!=='\\'){
                this._path.push('');
              }
            }elseif(buffer==='.'&&c!=='/'&&c!=='\\'){
              this._path.push('');
            }elseif(buffer!=='.'){
              if(this._scheme==='file'&&this._path.length===0&&buffer.length===2&&ALPHA.test(buffer[0])&&buffer[1]==='|'){
                buffer=buffer[0]+':';
              }

              this._path.push(buffer);
            }

            buffer='';

            if(c==='?'){
              this._query='?';
              state='query';
            }elseif(c==='#'){
              this._fragment='#';
              state='fragment';
            }
          }elseif(c!=='\t'&&c!=='\n'&&c!=='\r'){
            buffer+=percentEscape(c);
          }

          break;

        case'query':
          if(!stateOverride&&c==='#'){
            this._fragment='#';
            state='fragment';
          }elseif(c!==EOF&&c!=='\t'&&c!=='\n'&&c!=='\r'){
            this._query+=percentEscapeQuery(c);
          }

          break;

        case'fragment':
          if(c!==EOF&&c!=='\t'&&c!=='\n'&&c!=='\r'){
            this._fragment+=c;
          }

          break;
      }

      cursor++;
    }
  }

  functionclear(){
    this._scheme='';
    this._schemeData='';
    this._username='';
    this._password=null;
    this._host='';
    this._port='';
    this._path=[];
    this._query='';
    this._fragment='';
    this._isInvalid=false;
    this._isRelative=false;
  }

  functionJURL(url,base){
    if(base!==undefined&&!(baseinstanceofJURL)){
      base=newJURL(String(base));
    }

    this._url=url;
    clear.call(this);
    varinput=url.replace(/^[\t\r\n\f]+|[\t\r\n\f]+$/g,'');
    parse.call(this,input,null,base);
  }

  JURL.prototype={
    toString:functiontoString(){
      returnthis.href;
    },

    gethref(){
      if(this._isInvalid){
        returnthis._url;
      }

      varauthority='';

      if(this._username!==''||this._password!==null){
        authority=this._username+(this._password!==null?':'+this._password:'')+'@';
      }

      returnthis.protocol+(this._isRelative?'//'+authority+this.host:'')+this.pathname+this._query+this._fragment;
    },

    sethref(value){
      clear.call(this);
      parse.call(this,value);
    },

    getprotocol(){
      returnthis._scheme+':';
    },

    setprotocol(value){
      if(this._isInvalid){
        return;
      }

      parse.call(this,value+':','schemestart');
    },

    gethost(){
      returnthis._isInvalid?'':this._port?this._host+':'+this._port:this._host;
    },

    sethost(value){
      if(this._isInvalid||!this._isRelative){
        return;
      }

      parse.call(this,value,'host');
    },

    gethostname(){
      returnthis._host;
    },

    sethostname(value){
      if(this._isInvalid||!this._isRelative){
        return;
      }

      parse.call(this,value,'hostname');
    },

    getport(){
      returnthis._port;
    },

    setport(value){
      if(this._isInvalid||!this._isRelative){
        return;
      }

      parse.call(this,value,'port');
    },

    getpathname(){
      returnthis._isInvalid?'':this._isRelative?'/'+this._path.join('/'):this._schemeData;
    },

    setpathname(value){
      if(this._isInvalid||!this._isRelative){
        return;
      }

      this._path=[];
      parse.call(this,value,'relativepathstart');
    },

    getsearch(){
      returnthis._isInvalid||!this._query||this._query==='?'?'':this._query;
    },

    setsearch(value){
      if(this._isInvalid||!this._isRelative){
        return;
      }

      this._query='?';

      if(value[0]==='?'){
        value=value.slice(1);
      }

      parse.call(this,value,'query');
    },

    gethash(){
      returnthis._isInvalid||!this._fragment||this._fragment==='#'?'':this._fragment;
    },

    sethash(value){
      if(this._isInvalid){
        return;
      }

      this._fragment='#';

      if(value[0]==='#'){
        value=value.slice(1);
      }

      parse.call(this,value,'fragment');
    },

    getorigin(){
      varhost;

      if(this._isInvalid||!this._scheme){
        return'';
      }

      switch(this._scheme){
        case'data':
        case'file':
        case'javascript':
        case'mailto':
          return'null';

        case'blob':
          try{
            returnnewJURL(this._schemeData).origin||'null';
          }catch(_){}

          return'null';
      }

      host=this.host;

      if(!host){
        return'';
      }

      returnthis._scheme+'://'+host;
    }

  };
  exports.URL=JURL;
})();

/***/}),
/*147*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.getDocument=getDocument;
exports.setPDFNetworkStreamFactory=setPDFNetworkStreamFactory;
exports.build=exports.version=exports.PDFPageProxy=exports.PDFDocumentProxy=exports.PDFWorker=exports.PDFDataRangeTransport=exports.LoopbackPort=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

var_display_utils=__w_pdfjs_require__(151);

var_font_loader=__w_pdfjs_require__(152);

var_api_compatibility=__w_pdfjs_require__(153);

var_canvas=__w_pdfjs_require__(154);

var_global_scope=_interopRequireDefault(__w_pdfjs_require__(3));

var_worker_options=__w_pdfjs_require__(156);

var_message_handler=__w_pdfjs_require__(157);

var_metadata=__w_pdfjs_require__(158);

var_transport_stream=__w_pdfjs_require__(160);

var_webgl=__w_pdfjs_require__(161);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{default:obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

function_toConsumableArray(arr){return_arrayWithoutHoles(arr)||_iterableToArray(arr)||_nonIterableSpread();}

function_nonIterableSpread(){thrownewTypeError("Invalidattempttospreadnon-iterableinstance");}

function_iterableToArray(iter){if(Symbol.iteratorinObject(iter)||Object.prototype.toString.call(iter)==="[objectArguments]")returnArray.from(iter);}

function_arrayWithoutHoles(arr){if(Array.isArray(arr)){for(vari=0,arr2=newArray(arr.length);i<arr.length;i++){arr2[i]=arr[i];}returnarr2;}}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

varDEFAULT_RANGE_CHUNK_SIZE=65536;
varisWorkerDisabled=false;
varfallbackWorkerSrc;
varfakeWorkerFilesLoader=null;
{
  varuseRequireEnsure=false;

  if(typeofwindow==='undefined'){
    isWorkerDisabled=true;

    if(typeofrequire.ensure==='undefined'){
      require.ensure=require('node-ensure');
    }

    useRequireEnsure=true;
  }elseif(typeofrequire!=='undefined'&&typeofrequire.ensure==='function'){
    useRequireEnsure=true;
  }

  if(typeofrequirejs!=='undefined'&&requirejs.toUrl){
    fallbackWorkerSrc=requirejs.toUrl('pdfjs-dist/build/pdf.worker.js');
  }

  vardynamicLoaderSupported=typeofrequirejs!=='undefined'&&requirejs.load;
  fakeWorkerFilesLoader=useRequireEnsure?function(){
    returnnewPromise(function(resolve,reject){
      require.ensure([],function(){
        try{
          varworker;
          worker=require('./pdf.worker.js');
          resolve(worker.WorkerMessageHandler);
        }catch(ex){
          reject(ex);
        }
      },reject,'pdfjsWorker');
    });
  }:dynamicLoaderSupported?function(){
    returnnewPromise(function(resolve,reject){
      requirejs(['pdfjs-dist/build/pdf.worker'],function(worker){
        try{
          resolve(worker.WorkerMessageHandler);
        }catch(ex){
          reject(ex);
        }
      },reject);
    });
  }:null;

  if(!fallbackWorkerSrc&&(typeofdocument==="undefined"?"undefined":_typeof(document))==='object'&&'currentScript'indocument){
    varpdfjsFilePath=document.currentScript&&document.currentScript.src;

    if(pdfjsFilePath){
      fallbackWorkerSrc=pdfjsFilePath.replace(/(\.(?:min\.)?js)(\?.*)?$/i,'.worker$1$2');
    }
  }
}
varcreatePDFNetworkStream;

functionsetPDFNetworkStreamFactory(pdfNetworkStreamFactory){
  createPDFNetworkStream=pdfNetworkStreamFactory;
}

functiongetDocument(src){
  vartask=newPDFDocumentLoadingTask();
  varsource;

  if(typeofsrc==='string'){
    source={
      url:src
    };
  }elseif((0,_util.isArrayBuffer)(src)){
    source={
      data:src
    };
  }elseif(srcinstanceofPDFDataRangeTransport){
    source={
      range:src
    };
  }else{
    if(_typeof(src)!=='object'){
      thrownewError('InvalidparameteringetDocument,'+'needeitherUint8Array,stringoraparameterobject');
    }

    if(!src.url&&!src.data&&!src.range){
      thrownewError('Invalidparameterobject:needeither.data,.rangeor.url');
    }

    source=src;
  }

  varparams=Object.create(null);
  varrangeTransport=null,
      worker=null;

  for(varkeyinsource){
    if(key==='url'&&typeofwindow!=='undefined'){
      params[key]=new_util.URL(source[key],window.location).href;
      continue;
    }elseif(key==='range'){
      rangeTransport=source[key];
      continue;
    }elseif(key==='worker'){
      worker=source[key];
      continue;
    }elseif(key==='data'&&!(source[key]instanceofUint8Array)){
      varpdfBytes=source[key];

      if(typeofpdfBytes==='string'){
        params[key]=(0,_util.stringToBytes)(pdfBytes);
      }elseif(_typeof(pdfBytes)==='object'&&pdfBytes!==null&&!isNaN(pdfBytes.length)){
        params[key]=newUint8Array(pdfBytes);
      }elseif((0,_util.isArrayBuffer)(pdfBytes)){
        params[key]=newUint8Array(pdfBytes);
      }else{
        thrownewError('InvalidPDFbinarydata:eithertypedarray,'+'stringorarray-likeobjectisexpectedinthe'+'dataproperty.');
      }

      continue;
    }

    params[key]=source[key];
  }

  params.rangeChunkSize=params.rangeChunkSize||DEFAULT_RANGE_CHUNK_SIZE;
  params.CMapReaderFactory=params.CMapReaderFactory||_display_utils.DOMCMapReaderFactory;
  params.ignoreErrors=params.stopAtErrors!==true;
  params.pdfBug=params.pdfBug===true;
  varNativeImageDecoderValues=Object.values(_util.NativeImageDecoding);

  if(params.nativeImageDecoderSupport===undefined||!NativeImageDecoderValues.includes(params.nativeImageDecoderSupport)){
    params.nativeImageDecoderSupport=_api_compatibility.apiCompatibilityParams.nativeImageDecoderSupport||_util.NativeImageDecoding.DECODE;
  }

  if(!Number.isInteger(params.maxImageSize)){
    params.maxImageSize=-1;
  }

  if(typeofparams.isEvalSupported!=='boolean'){
    params.isEvalSupported=true;
  }

  if(typeofparams.disableFontFace!=='boolean'){
    params.disableFontFace=_api_compatibility.apiCompatibilityParams.disableFontFace||false;
  }

  if(typeofparams.disableRange!=='boolean'){
    params.disableRange=false;
  }

  if(typeofparams.disableStream!=='boolean'){
    params.disableStream=false;
  }

  if(typeofparams.disableAutoFetch!=='boolean'){
    params.disableAutoFetch=false;
  }

  if(typeofparams.disableCreateObjectURL!=='boolean'){
    params.disableCreateObjectURL=_api_compatibility.apiCompatibilityParams.disableCreateObjectURL||false;
  }

  (0,_util.setVerbosityLevel)(params.verbosity);

  if(!worker){
    varworkerParams={
      postMessageTransfers:params.postMessageTransfers,
      verbosity:params.verbosity,
      port:_worker_options.GlobalWorkerOptions.workerPort
    };
    worker=workerParams.port?PDFWorker.fromPort(workerParams):newPDFWorker(workerParams);
    task._worker=worker;
  }

  vardocId=task.docId;
  worker.promise.then(function(){
    if(task.destroyed){
      thrownewError('Loadingaborted');
    }

    return_fetchDocument(worker,params,rangeTransport,docId).then(function(workerId){
      if(task.destroyed){
        thrownewError('Loadingaborted');
      }

      varnetworkStream;

      if(rangeTransport){
        networkStream=new_transport_stream.PDFDataTransportStream({
          length:params.length,
          initialData:params.initialData,
          progressiveDone:params.progressiveDone,
          disableRange:params.disableRange,
          disableStream:params.disableStream
        },rangeTransport);
      }elseif(!params.data){
        networkStream=createPDFNetworkStream({
          url:params.url,
          length:params.length,
          httpHeaders:params.httpHeaders,
          withCredentials:params.withCredentials,
          rangeChunkSize:params.rangeChunkSize,
          disableRange:params.disableRange,
          disableStream:params.disableStream
        });
      }

      varmessageHandler=new_message_handler.MessageHandler(docId,workerId,worker.port);
      messageHandler.postMessageTransfers=worker.postMessageTransfers;
      vartransport=newWorkerTransport(messageHandler,task,networkStream,params);
      task._transport=transport;
      messageHandler.send('Ready',null);
    });
  })["catch"](task._capability.reject);
  returntask;
}

function_fetchDocument(worker,source,pdfDataRangeTransport,docId){
  if(worker.destroyed){
    returnPromise.reject(newError('Workerwasdestroyed'));
  }

  if(pdfDataRangeTransport){
    source.length=pdfDataRangeTransport.length;
    source.initialData=pdfDataRangeTransport.initialData;
    source.progressiveDone=pdfDataRangeTransport.progressiveDone;
  }

  returnworker.messageHandler.sendWithPromise('GetDocRequest',{
    docId:docId,
    apiVersion:'2.2.228',
    source:{
      data:source.data,
      url:source.url,
      password:source.password,
      disableAutoFetch:source.disableAutoFetch,
      rangeChunkSize:source.rangeChunkSize,
      length:source.length
    },
    maxImageSize:source.maxImageSize,
    disableFontFace:source.disableFontFace,
    disableCreateObjectURL:source.disableCreateObjectURL,
    postMessageTransfers:worker.postMessageTransfers,
    docBaseUrl:source.docBaseUrl,
    nativeImageDecoderSupport:source.nativeImageDecoderSupport,
    ignoreErrors:source.ignoreErrors,
    isEvalSupported:source.isEvalSupported
  }).then(function(workerId){
    if(worker.destroyed){
      thrownewError('Workerwasdestroyed');
    }

    returnworkerId;
  });
}

varPDFDocumentLoadingTask=functionPDFDocumentLoadingTaskClosure(){
  varnextDocumentId=0;

  varPDFDocumentLoadingTask=
  /*#__PURE__*/
  function(){
    functionPDFDocumentLoadingTask(){
      _classCallCheck(this,PDFDocumentLoadingTask);

      this._capability=(0,_util.createPromiseCapability)();
      this._transport=null;
      this._worker=null;
      this.docId='d'+nextDocumentId++;
      this.destroyed=false;
      this.onPassword=null;
      this.onProgress=null;
      this.onUnsupportedFeature=null;
    }

    _createClass(PDFDocumentLoadingTask,[{
      key:"destroy",
      value:functiondestroy(){
        var_this=this;

        this.destroyed=true;
        vartransportDestroyed=!this._transport?Promise.resolve():this._transport.destroy();
        returntransportDestroyed.then(function(){
          _this._transport=null;

          if(_this._worker){
            _this._worker.destroy();

            _this._worker=null;
          }
        });
      }
    },{
      key:"then",
      value:functionthen(onFulfilled,onRejected){
        (0,_display_utils.deprecated)('PDFDocumentLoadingTask.thenmethod,'+'usethe`promise`getterinstead.');
        returnthis.promise.then.apply(this.promise,arguments);
      }
    },{
      key:"promise",
      get:functionget(){
        returnthis._capability.promise;
      }
    }]);

    returnPDFDocumentLoadingTask;
  }();

  returnPDFDocumentLoadingTask;
}();

varPDFDataRangeTransport=
/*#__PURE__*/
function(){
  functionPDFDataRangeTransport(length,initialData){
    varprogressiveDone=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

    _classCallCheck(this,PDFDataRangeTransport);

    this.length=length;
    this.initialData=initialData;
    this.progressiveDone=progressiveDone;
    this._rangeListeners=[];
    this._progressListeners=[];
    this._progressiveReadListeners=[];
    this._progressiveDoneListeners=[];
    this._readyCapability=(0,_util.createPromiseCapability)();
  }

  _createClass(PDFDataRangeTransport,[{
    key:"addRangeListener",
    value:functionaddRangeListener(listener){
      this._rangeListeners.push(listener);
    }
  },{
    key:"addProgressListener",
    value:functionaddProgressListener(listener){
      this._progressListeners.push(listener);
    }
  },{
    key:"addProgressiveReadListener",
    value:functionaddProgressiveReadListener(listener){
      this._progressiveReadListeners.push(listener);
    }
  },{
    key:"addProgressiveDoneListener",
    value:functionaddProgressiveDoneListener(listener){
      this._progressiveDoneListeners.push(listener);
    }
  },{
    key:"onDataRange",
    value:functiononDataRange(begin,chunk){
      var_iteratorNormalCompletion=true;
      var_didIteratorError=false;
      var_iteratorError=undefined;

      try{
        for(var_iterator=this._rangeListeners[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
          varlistener=_step.value;
          listener(begin,chunk);
        }
      }catch(err){
        _didIteratorError=true;
        _iteratorError=err;
      }finally{
        try{
          if(!_iteratorNormalCompletion&&_iterator["return"]!=null){
            _iterator["return"]();
          }
        }finally{
          if(_didIteratorError){
            throw_iteratorError;
          }
        }
      }
    }
  },{
    key:"onDataProgress",
    value:functiononDataProgress(loaded,total){
      var_this2=this;

      this._readyCapability.promise.then(function(){
        var_iteratorNormalCompletion2=true;
        var_didIteratorError2=false;
        var_iteratorError2=undefined;

        try{
          for(var_iterator2=_this2._progressListeners[Symbol.iterator](),_step2;!(_iteratorNormalCompletion2=(_step2=_iterator2.next()).done);_iteratorNormalCompletion2=true){
            varlistener=_step2.value;
            listener(loaded,total);
          }
        }catch(err){
          _didIteratorError2=true;
          _iteratorError2=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion2&&_iterator2["return"]!=null){
              _iterator2["return"]();
            }
          }finally{
            if(_didIteratorError2){
              throw_iteratorError2;
            }
          }
        }
      });
    }
  },{
    key:"onDataProgressiveRead",
    value:functiononDataProgressiveRead(chunk){
      var_this3=this;

      this._readyCapability.promise.then(function(){
        var_iteratorNormalCompletion3=true;
        var_didIteratorError3=false;
        var_iteratorError3=undefined;

        try{
          for(var_iterator3=_this3._progressiveReadListeners[Symbol.iterator](),_step3;!(_iteratorNormalCompletion3=(_step3=_iterator3.next()).done);_iteratorNormalCompletion3=true){
            varlistener=_step3.value;
            listener(chunk);
          }
        }catch(err){
          _didIteratorError3=true;
          _iteratorError3=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion3&&_iterator3["return"]!=null){
              _iterator3["return"]();
            }
          }finally{
            if(_didIteratorError3){
              throw_iteratorError3;
            }
          }
        }
      });
    }
  },{
    key:"onDataProgressiveDone",
    value:functiononDataProgressiveDone(){
      var_this4=this;

      this._readyCapability.promise.then(function(){
        var_iteratorNormalCompletion4=true;
        var_didIteratorError4=false;
        var_iteratorError4=undefined;

        try{
          for(var_iterator4=_this4._progressiveDoneListeners[Symbol.iterator](),_step4;!(_iteratorNormalCompletion4=(_step4=_iterator4.next()).done);_iteratorNormalCompletion4=true){
            varlistener=_step4.value;
            listener();
          }
        }catch(err){
          _didIteratorError4=true;
          _iteratorError4=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion4&&_iterator4["return"]!=null){
              _iterator4["return"]();
            }
          }finally{
            if(_didIteratorError4){
              throw_iteratorError4;
            }
          }
        }
      });
    }
  },{
    key:"transportReady",
    value:functiontransportReady(){
      this._readyCapability.resolve();
    }
  },{
    key:"requestDataRange",
    value:functionrequestDataRange(begin,end){
      (0,_util.unreachable)('AbstractmethodPDFDataRangeTransport.requestDataRange');
    }
  },{
    key:"abort",
    value:functionabort(){}
  }]);

  returnPDFDataRangeTransport;
}();

exports.PDFDataRangeTransport=PDFDataRangeTransport;

varPDFDocumentProxy=
/*#__PURE__*/
function(){
  functionPDFDocumentProxy(pdfInfo,transport){
    _classCallCheck(this,PDFDocumentProxy);

    this._pdfInfo=pdfInfo;
    this._transport=transport;
  }

  _createClass(PDFDocumentProxy,[{
    key:"getPage",
    value:functiongetPage(pageNumber){
      returnthis._transport.getPage(pageNumber);
    }
  },{
    key:"getPageIndex",
    value:functiongetPageIndex(ref){
      returnthis._transport.getPageIndex(ref);
    }
  },{
    key:"getDestinations",
    value:functiongetDestinations(){
      returnthis._transport.getDestinations();
    }
  },{
    key:"getDestination",
    value:functiongetDestination(id){
      returnthis._transport.getDestination(id);
    }
  },{
    key:"getPageLabels",
    value:functiongetPageLabels(){
      returnthis._transport.getPageLabels();
    }
  },{
    key:"getPageLayout",
    value:functiongetPageLayout(){
      returnthis._transport.getPageLayout();
    }
  },{
    key:"getPageMode",
    value:functiongetPageMode(){
      returnthis._transport.getPageMode();
    }
  },{
    key:"getViewerPreferences",
    value:functiongetViewerPreferences(){
      returnthis._transport.getViewerPreferences();
    }
  },{
    key:"getOpenActionDestination",
    value:functiongetOpenActionDestination(){
      returnthis._transport.getOpenActionDestination();
    }
  },{
    key:"getAttachments",
    value:functiongetAttachments(){
      returnthis._transport.getAttachments();
    }
  },{
    key:"getJavaScript",
    value:functiongetJavaScript(){
      returnthis._transport.getJavaScript();
    }
  },{
    key:"getOutline",
    value:functiongetOutline(){
      returnthis._transport.getOutline();
    }
  },{
    key:"getPermissions",
    value:functiongetPermissions(){
      returnthis._transport.getPermissions();
    }
  },{
    key:"getMetadata",
    value:functiongetMetadata(){
      returnthis._transport.getMetadata();
    }
  },{
    key:"getData",
    value:functiongetData(){
      returnthis._transport.getData();
    }
  },{
    key:"getDownloadInfo",
    value:functiongetDownloadInfo(){
      returnthis._transport.downloadInfoCapability.promise;
    }
  },{
    key:"getStats",
    value:functiongetStats(){
      returnthis._transport.getStats();
    }
  },{
    key:"cleanup",
    value:functioncleanup(){
      this._transport.startCleanup();
    }
  },{
    key:"destroy",
    value:functiondestroy(){
      returnthis.loadingTask.destroy();
    }
  },{
    key:"numPages",
    get:functionget(){
      returnthis._pdfInfo.numPages;
    }
  },{
    key:"fingerprint",
    get:functionget(){
      returnthis._pdfInfo.fingerprint;
    }
  },{
    key:"loadingParams",
    get:functionget(){
      returnthis._transport.loadingParams;
    }
  },{
    key:"loadingTask",
    get:functionget(){
      returnthis._transport.loadingTask;
    }
  }]);

  returnPDFDocumentProxy;
}();

exports.PDFDocumentProxy=PDFDocumentProxy;

varPDFPageProxy=
/*#__PURE__*/
function(){
  functionPDFPageProxy(pageIndex,pageInfo,transport){
    varpdfBug=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;

    _classCallCheck(this,PDFPageProxy);

    this.pageIndex=pageIndex;
    this._pageInfo=pageInfo;
    this._transport=transport;
    this._stats=pdfBug?new_display_utils.StatTimer():_display_utils.DummyStatTimer;
    this._pdfBug=pdfBug;
    this.commonObjs=transport.commonObjs;
    this.objs=newPDFObjects();
    this.cleanupAfterRender=false;
    this.pendingCleanup=false;
    this.intentStates=Object.create(null);
    this.destroyed=false;
  }

  _createClass(PDFPageProxy,[{
    key:"getViewport",
    value:functiongetViewport(){
      var_ref=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
          scale=_ref.scale,
          _ref$rotation=_ref.rotation,
          rotation=_ref$rotation===void0?this.rotate:_ref$rotation,
          _ref$dontFlip=_ref.dontFlip,
          dontFlip=_ref$dontFlip===void0?false:_ref$dontFlip;

      if(arguments.length>1||typeofarguments[0]==='number'){
        (0,_display_utils.deprecated)('getViewportiscalledwithobsoletearguments.');
        scale=arguments[0];
        rotation=typeofarguments[1]==='number'?arguments[1]:this.rotate;
        dontFlip=typeofarguments[2]==='boolean'?arguments[2]:false;
      }

      returnnew_display_utils.PageViewport({
        viewBox:this.view,
        scale:scale,
        rotation:rotation,
        dontFlip:dontFlip
      });
    }
  },{
    key:"getAnnotations",
    value:functiongetAnnotations(){
      var_ref2=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
          _ref2$intent=_ref2.intent,
          intent=_ref2$intent===void0?null:_ref2$intent;

      if(!this.annotationsPromise||this.annotationsIntent!==intent){
        this.annotationsPromise=this._transport.getAnnotations(this.pageIndex,intent);
        this.annotationsIntent=intent;
      }

      returnthis.annotationsPromise;
    }
  },{
    key:"render",
    value:functionrender(_ref3){
      var_this5=this;

      varcanvasContext=_ref3.canvasContext,
          viewport=_ref3.viewport,
          _ref3$intent=_ref3.intent,
          intent=_ref3$intent===void0?'display':_ref3$intent,
          _ref3$enableWebGL=_ref3.enableWebGL,
          enableWebGL=_ref3$enableWebGL===void0?false:_ref3$enableWebGL,
          _ref3$renderInteracti=_ref3.renderInteractiveForms,
          renderInteractiveForms=_ref3$renderInteracti===void0?false:_ref3$renderInteracti,
          _ref3$transform=_ref3.transform,
          transform=_ref3$transform===void0?null:_ref3$transform,
          _ref3$imageLayer=_ref3.imageLayer,
          imageLayer=_ref3$imageLayer===void0?null:_ref3$imageLayer,
          _ref3$canvasFactory=_ref3.canvasFactory,
          canvasFactory=_ref3$canvasFactory===void0?null:_ref3$canvasFactory,
          _ref3$background=_ref3.background,
          background=_ref3$background===void0?null:_ref3$background;
      varstats=this._stats;
      stats.time('Overall');
      this.pendingCleanup=false;
      varrenderingIntent=intent==='print'?'print':'display';
      varcanvasFactoryInstance=canvasFactory||new_display_utils.DOMCanvasFactory();
      varwebGLContext=new_webgl.WebGLContext({
        enable:enableWebGL
      });

      if(!this.intentStates[renderingIntent]){
        this.intentStates[renderingIntent]=Object.create(null);
      }

      varintentState=this.intentStates[renderingIntent];

      if(!intentState.displayReadyCapability){
        intentState.receivingOperatorList=true;
        intentState.displayReadyCapability=(0,_util.createPromiseCapability)();
        intentState.operatorList={
          fnArray:[],
          argsArray:[],
          lastChunk:false
        };
        stats.time('PageRequest');

        this._transport.messageHandler.send('RenderPageRequest',{
          pageIndex:this.pageNumber-1,
          intent:renderingIntent,
          renderInteractiveForms:renderInteractiveForms===true
        });
      }

      varcomplete=functioncomplete(error){
        vari=intentState.renderTasks.indexOf(internalRenderTask);

        if(i>=0){
          intentState.renderTasks.splice(i,1);
        }

        if(_this5.cleanupAfterRender||renderingIntent==='print'){
          _this5.pendingCleanup=true;
        }

        _this5._tryCleanup();

        if(error){
          internalRenderTask.capability.reject(error);
        }else{
          internalRenderTask.capability.resolve();
        }

        stats.timeEnd('Rendering');
        stats.timeEnd('Overall');
      };

      varinternalRenderTask=newInternalRenderTask({
        callback:complete,
        params:{
          canvasContext:canvasContext,
          viewport:viewport,
          transform:transform,
          imageLayer:imageLayer,
          background:background
        },
        objs:this.objs,
        commonObjs:this.commonObjs,
        operatorList:intentState.operatorList,
        pageNumber:this.pageNumber,
        canvasFactory:canvasFactoryInstance,
        webGLContext:webGLContext,
        useRequestAnimationFrame:renderingIntent!=='print',
        pdfBug:this._pdfBug
      });

      if(!intentState.renderTasks){
        intentState.renderTasks=[];
      }

      intentState.renderTasks.push(internalRenderTask);
      varrenderTask=internalRenderTask.task;
      intentState.displayReadyCapability.promise.then(function(transparency){
        if(_this5.pendingCleanup){
          complete();
          return;
        }

        stats.time('Rendering');
        internalRenderTask.initializeGraphics(transparency);
        internalRenderTask.operatorListChanged();
      })["catch"](complete);
      returnrenderTask;
    }
  },{
    key:"getOperatorList",
    value:functiongetOperatorList(){
      functionoperatorListChanged(){
        if(intentState.operatorList.lastChunk){
          intentState.opListReadCapability.resolve(intentState.operatorList);
          vari=intentState.renderTasks.indexOf(opListTask);

          if(i>=0){
            intentState.renderTasks.splice(i,1);
          }
        }
      }

      varrenderingIntent='oplist';

      if(!this.intentStates[renderingIntent]){
        this.intentStates[renderingIntent]=Object.create(null);
      }

      varintentState=this.intentStates[renderingIntent];
      varopListTask;

      if(!intentState.opListReadCapability){
        opListTask={};
        opListTask.operatorListChanged=operatorListChanged;
        intentState.receivingOperatorList=true;
        intentState.opListReadCapability=(0,_util.createPromiseCapability)();
        intentState.renderTasks=[];
        intentState.renderTasks.push(opListTask);
        intentState.operatorList={
          fnArray:[],
          argsArray:[],
          lastChunk:false
        };

        this._stats.time('PageRequest');

        this._transport.messageHandler.send('RenderPageRequest',{
          pageIndex:this.pageIndex,
          intent:renderingIntent
        });
      }

      returnintentState.opListReadCapability.promise;
    }
  },{
    key:"streamTextContent",
    value:functionstreamTextContent(){
      var_ref4=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
          _ref4$normalizeWhites=_ref4.normalizeWhitespace,
          normalizeWhitespace=_ref4$normalizeWhites===void0?false:_ref4$normalizeWhites,
          _ref4$disableCombineT=_ref4.disableCombineTextItems,
          disableCombineTextItems=_ref4$disableCombineT===void0?false:_ref4$disableCombineT;

      varTEXT_CONTENT_CHUNK_SIZE=100;
      returnthis._transport.messageHandler.sendWithStream('GetTextContent',{
        pageIndex:this.pageNumber-1,
        normalizeWhitespace:normalizeWhitespace===true,
        combineTextItems:disableCombineTextItems!==true
      },{
        highWaterMark:TEXT_CONTENT_CHUNK_SIZE,
        size:functionsize(textContent){
          returntextContent.items.length;
        }
      });
    }
  },{
    key:"getTextContent",
    value:functiongetTextContent(){
      varparams=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{};
      varreadableStream=this.streamTextContent(params);
      returnnewPromise(function(resolve,reject){
        functionpump(){
          reader.read().then(function(_ref5){
            var_textContent$items;

            varvalue=_ref5.value,
                done=_ref5.done;

            if(done){
              resolve(textContent);
              return;
            }

            Object.assign(textContent.styles,value.styles);

            (_textContent$items=textContent.items).push.apply(_textContent$items,_toConsumableArray(value.items));

            pump();
          },reject);
        }

        varreader=readableStream.getReader();
        vartextContent={
          items:[],
          styles:Object.create(null)
        };
        pump();
      });
    }
  },{
    key:"_destroy",
    value:function_destroy(){
      this.destroyed=true;
      this._transport.pageCache[this.pageIndex]=null;
      varwaitOn=[];
      Object.keys(this.intentStates).forEach(function(intent){
        if(intent==='oplist'){
          return;
        }

        varintentState=this.intentStates[intent];
        intentState.renderTasks.forEach(function(renderTask){
          varrenderCompleted=renderTask.capability.promise["catch"](function(){});
          waitOn.push(renderCompleted);
          renderTask.cancel();
        });
      },this);
      this.objs.clear();
      this.annotationsPromise=null;
      this.pendingCleanup=false;
      returnPromise.all(waitOn);
    }
  },{
    key:"cleanup",
    value:functioncleanup(){
      varresetStats=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      this.pendingCleanup=true;

      this._tryCleanup(resetStats);
    }
  },{
    key:"_tryCleanup",
    value:function_tryCleanup(){
      varresetStats=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(!this.pendingCleanup||Object.keys(this.intentStates).some(function(intent){
        varintentState=this.intentStates[intent];
        returnintentState.renderTasks.length!==0||intentState.receivingOperatorList;
      },this)){
        return;
      }

      Object.keys(this.intentStates).forEach(function(intent){
        deletethis.intentStates[intent];
      },this);
      this.objs.clear();
      this.annotationsPromise=null;

      if(resetStats&&this._statsinstanceof_display_utils.StatTimer){
        this._stats=new_display_utils.StatTimer();
      }

      this.pendingCleanup=false;
    }
  },{
    key:"_startRenderPage",
    value:function_startRenderPage(transparency,intent){
      varintentState=this.intentStates[intent];

      if(intentState.displayReadyCapability){
        intentState.displayReadyCapability.resolve(transparency);
      }
    }
  },{
    key:"_renderPageChunk",
    value:function_renderPageChunk(operatorListChunk,intent){
      varintentState=this.intentStates[intent];

      for(vari=0,ii=operatorListChunk.length;i<ii;i++){
        intentState.operatorList.fnArray.push(operatorListChunk.fnArray[i]);
        intentState.operatorList.argsArray.push(operatorListChunk.argsArray[i]);
      }

      intentState.operatorList.lastChunk=operatorListChunk.lastChunk;

      for(var_i=0;_i<intentState.renderTasks.length;_i++){
        intentState.renderTasks[_i].operatorListChanged();
      }

      if(operatorListChunk.lastChunk){
        intentState.receivingOperatorList=false;

        this._tryCleanup();
      }
    }
  },{
    key:"pageNumber",
    get:functionget(){
      returnthis.pageIndex+1;
    }
  },{
    key:"rotate",
    get:functionget(){
      returnthis._pageInfo.rotate;
    }
  },{
    key:"ref",
    get:functionget(){
      returnthis._pageInfo.ref;
    }
  },{
    key:"userUnit",
    get:functionget(){
      returnthis._pageInfo.userUnit;
    }
  },{
    key:"view",
    get:functionget(){
      returnthis._pageInfo.view;
    }
  },{
    key:"stats",
    get:functionget(){
      returnthis._statsinstanceof_display_utils.StatTimer?this._stats:null;
    }
  }]);

  returnPDFPageProxy;
}();

exports.PDFPageProxy=PDFPageProxy;

varLoopbackPort=
/*#__PURE__*/
function(){
  functionLoopbackPort(){
    vardefer=arguments.length>0&&arguments[0]!==undefined?arguments[0]:true;

    _classCallCheck(this,LoopbackPort);

    this._listeners=[];
    this._defer=defer;
    this._deferred=Promise.resolve(undefined);
  }

  _createClass(LoopbackPort,[{
    key:"postMessage",
    value:functionpostMessage(obj,transfers){
      var_this6=this;

      functioncloneValue(value){
        if(_typeof(value)!=='object'||value===null){
          returnvalue;
        }

        if(cloned.has(value)){
          returncloned.get(value);
        }

        varbuffer,result;

        if((buffer=value.buffer)&&(0,_util.isArrayBuffer)(buffer)){
          vartransferable=transfers&&transfers.includes(buffer);

          if(value===buffer){
            result=value;
          }elseif(transferable){
            result=newvalue.constructor(buffer,value.byteOffset,value.byteLength);
          }else{
            result=newvalue.constructor(value);
          }

          cloned.set(value,result);
          returnresult;
        }

        result=Array.isArray(value)?[]:{};
        cloned.set(value,result);

        for(variinvalue){
          vardesc=void0,
              p=value;

          while(!(desc=Object.getOwnPropertyDescriptor(p,i))){
            p=Object.getPrototypeOf(p);
          }

          if(typeofdesc.value==='undefined'||typeofdesc.value==='function'){
            continue;
          }

          result[i]=cloneValue(desc.value);
        }

        returnresult;
      }

      if(!this._defer){
        this._listeners.forEach(function(listener){
          listener.call(this,{
            data:obj
          });
        },this);

        return;
      }

      varcloned=newWeakMap();
      vare={
        data:cloneValue(obj)
      };

      this._deferred.then(function(){
        _this6._listeners.forEach(function(listener){
          listener.call(this,e);
        },_this6);
      });
    }
  },{
    key:"addEventListener",
    value:functionaddEventListener(name,listener){
      this._listeners.push(listener);
    }
  },{
    key:"removeEventListener",
    value:functionremoveEventListener(name,listener){
      vari=this._listeners.indexOf(listener);

      this._listeners.splice(i,1);
    }
  },{
    key:"terminate",
    value:functionterminate(){
      this._listeners.length=0;
    }
  }]);

  returnLoopbackPort;
}();

exports.LoopbackPort=LoopbackPort;

varPDFWorker=functionPDFWorkerClosure(){
  varpdfWorkerPorts=newWeakMap();
  varnextFakeWorkerId=0;
  varfakeWorkerFilesLoadedCapability;

  function_getWorkerSrc(){
    if(_worker_options.GlobalWorkerOptions.workerSrc){
      return_worker_options.GlobalWorkerOptions.workerSrc;
    }

    if(typeoffallbackWorkerSrc!=='undefined'){
      returnfallbackWorkerSrc;
    }

    thrownewError('No"GlobalWorkerOptions.workerSrc"specified.');
  }

  functiongetMainThreadWorkerMessageHandler(){
    try{
      if(typeofwindow!=='undefined'){
        returnwindow.pdfjsWorker&&window.pdfjsWorker.WorkerMessageHandler;
      }
    }catch(ex){}

    returnnull;
  }

  functionsetupFakeWorkerGlobal(){
    if(fakeWorkerFilesLoadedCapability){
      returnfakeWorkerFilesLoadedCapability.promise;
    }

    fakeWorkerFilesLoadedCapability=(0,_util.createPromiseCapability)();
    varmainWorkerMessageHandler=getMainThreadWorkerMessageHandler();

    if(mainWorkerMessageHandler){
      fakeWorkerFilesLoadedCapability.resolve(mainWorkerMessageHandler);
      returnfakeWorkerFilesLoadedCapability.promise;
    }

    varloader=fakeWorkerFilesLoader||function(){
      return(0,_display_utils.loadScript)(_getWorkerSrc()).then(function(){
        returnwindow.pdfjsWorker.WorkerMessageHandler;
      });
    };

    loader().then(fakeWorkerFilesLoadedCapability.resolve,fakeWorkerFilesLoadedCapability.reject);
    returnfakeWorkerFilesLoadedCapability.promise;
  }

  functioncreateCDNWrapper(url){
    varwrapper='importScripts(\''+url+'\');';
    return_util.URL.createObjectURL(newBlob([wrapper]));
  }

  varPDFWorker=
  /*#__PURE__*/
  function(){
    functionPDFWorker(){
      var_ref6=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
          _ref6$name=_ref6.name,
          name=_ref6$name===void0?null:_ref6$name,
          _ref6$port=_ref6.port,
          port=_ref6$port===void0?null:_ref6$port,
          _ref6$postMessageTran=_ref6.postMessageTransfers,
          postMessageTransfers=_ref6$postMessageTran===void0?true:_ref6$postMessageTran,
          _ref6$verbosity=_ref6.verbosity,
          verbosity=_ref6$verbosity===void0?(0,_util.getVerbosityLevel)():_ref6$verbosity;

      _classCallCheck(this,PDFWorker);

      if(port&&pdfWorkerPorts.has(port)){
        thrownewError('CannotusemorethanonePDFWorkerperport');
      }

      this.name=name;
      this.destroyed=false;
      this.postMessageTransfers=postMessageTransfers!==false;
      this.verbosity=verbosity;
      this._readyCapability=(0,_util.createPromiseCapability)();
      this._port=null;
      this._webWorker=null;
      this._messageHandler=null;

      if(port){
        pdfWorkerPorts.set(port,this);

        this._initializeFromPort(port);

        return;
      }

      this._initialize();
    }

    _createClass(PDFWorker,[{
      key:"_initializeFromPort",
      value:function_initializeFromPort(port){
        this._port=port;
        this._messageHandler=new_message_handler.MessageHandler('main','worker',port);

        this._messageHandler.on('ready',function(){});

        this._readyCapability.resolve();
      }
    },{
      key:"_initialize",
      value:function_initialize(){
        var_this7=this;

        if(typeofWorker!=='undefined'&&!isWorkerDisabled&&!getMainThreadWorkerMessageHandler()){
          varworkerSrc=_getWorkerSrc();

          try{
            if(!(0,_util.isSameOrigin)(window.location.href,workerSrc)){
              workerSrc=createCDNWrapper(new_util.URL(workerSrc,window.location).href);
            }

            varworker=newWorker(workerSrc);
            varmessageHandler=new_message_handler.MessageHandler('main','worker',worker);

            varterminateEarly=functionterminateEarly(){
              worker.removeEventListener('error',onWorkerError);
              messageHandler.destroy();
              worker.terminate();

              if(_this7.destroyed){
                _this7._readyCapability.reject(newError('Workerwasdestroyed'));
              }else{
                _this7._setupFakeWorker();
              }
            };

            varonWorkerError=functiononWorkerError(){
              if(!_this7._webWorker){
                terminateEarly();
              }
            };

            worker.addEventListener('error',onWorkerError);
            messageHandler.on('test',function(data){
              worker.removeEventListener('error',onWorkerError);

              if(_this7.destroyed){
                terminateEarly();
                return;
              }

              if(data&&data.supportTypedArray){
                _this7._messageHandler=messageHandler;
                _this7._port=worker;
                _this7._webWorker=worker;

                if(!data.supportTransfers){
                  _this7.postMessageTransfers=false;
                }

                _this7._readyCapability.resolve();

                messageHandler.send('configure',{
                  verbosity:_this7.verbosity
                });
              }else{
                _this7._setupFakeWorker();

                messageHandler.destroy();
                worker.terminate();
              }
            });
            messageHandler.on('ready',function(data){
              worker.removeEventListener('error',onWorkerError);

              if(_this7.destroyed){
                terminateEarly();
                return;
              }

              try{
                sendTest();
              }catch(e){
                _this7._setupFakeWorker();
              }
            });

            varsendTest=functionsendTest(){
              vartestObj=newUint8Array([_this7.postMessageTransfers?255:0]);

              try{
                messageHandler.send('test',testObj,[testObj.buffer]);
              }catch(ex){
                (0,_util.info)('CannotusepostMessagetransfers');
                testObj[0]=0;
                messageHandler.send('test',testObj);
              }
            };

            sendTest();
            return;
          }catch(e){
            (0,_util.info)('Theworkerhasbeendisabled.');
          }
        }

        this._setupFakeWorker();
      }
    },{
      key:"_setupFakeWorker",
      value:function_setupFakeWorker(){
        var_this8=this;

        if(!isWorkerDisabled){
          (0,_util.warn)('Settingupfakeworker.');
          isWorkerDisabled=true;
        }

        setupFakeWorkerGlobal().then(function(WorkerMessageHandler){
          if(_this8.destroyed){
            _this8._readyCapability.reject(newError('Workerwasdestroyed'));

            return;
          }

          varport=newLoopbackPort();
          _this8._port=port;
          varid='fake'+nextFakeWorkerId++;
          varworkerHandler=new_message_handler.MessageHandler(id+'_worker',id,port);
          WorkerMessageHandler.setup(workerHandler,port);
          varmessageHandler=new_message_handler.MessageHandler(id,id+'_worker',port);
          _this8._messageHandler=messageHandler;

          _this8._readyCapability.resolve();
        })["catch"](function(reason){
          _this8._readyCapability.reject(newError("Settingupfakeworkerfailed:\"".concat(reason.message,"\".")));
        });
      }
    },{
      key:"destroy",
      value:functiondestroy(){
        this.destroyed=true;

        if(this._webWorker){
          this._webWorker.terminate();

          this._webWorker=null;
        }

        pdfWorkerPorts["delete"](this._port);
        this._port=null;

        if(this._messageHandler){
          this._messageHandler.destroy();

          this._messageHandler=null;
        }
      }
    },{
      key:"promise",
      get:functionget(){
        returnthis._readyCapability.promise;
      }
    },{
      key:"port",
      get:functionget(){
        returnthis._port;
      }
    },{
      key:"messageHandler",
      get:functionget(){
        returnthis._messageHandler;
      }
    }],[{
      key:"fromPort",
      value:functionfromPort(params){
        if(!params||!params.port){
          thrownewError('PDFWorker.fromPort-invalidmethodsignature.');
        }

        if(pdfWorkerPorts.has(params.port)){
          returnpdfWorkerPorts.get(params.port);
        }

        returnnewPDFWorker(params);
      }
    },{
      key:"getWorkerSrc",
      value:functiongetWorkerSrc(){
        return_getWorkerSrc();
      }
    }]);

    returnPDFWorker;
  }();

  returnPDFWorker;
}();

exports.PDFWorker=PDFWorker;

varWorkerTransport=
/*#__PURE__*/
function(){
  functionWorkerTransport(messageHandler,loadingTask,networkStream,params){
    _classCallCheck(this,WorkerTransport);

    this.messageHandler=messageHandler;
    this.loadingTask=loadingTask;
    this.commonObjs=newPDFObjects();
    this.fontLoader=new_font_loader.FontLoader({
      docId:loadingTask.docId,
      onUnsupportedFeature:this._onUnsupportedFeature.bind(this)
    });
    this._params=params;
    this.CMapReaderFactory=newparams.CMapReaderFactory({
      baseUrl:params.cMapUrl,
      isCompressed:params.cMapPacked
    });
    this.destroyed=false;
    this.destroyCapability=null;
    this._passwordCapability=null;
    this._networkStream=networkStream;
    this._fullReader=null;
    this._lastProgress=null;
    this.pageCache=[];
    this.pagePromises=[];
    this.downloadInfoCapability=(0,_util.createPromiseCapability)();
    this.setupMessageHandler();
  }

  _createClass(WorkerTransport,[{
    key:"destroy",
    value:functiondestroy(){
      var_this9=this;

      if(this.destroyCapability){
        returnthis.destroyCapability.promise;
      }

      this.destroyed=true;
      this.destroyCapability=(0,_util.createPromiseCapability)();

      if(this._passwordCapability){
        this._passwordCapability.reject(newError('WorkerwasdestroyedduringonPasswordcallback'));
      }

      varwaitOn=[];
      this.pageCache.forEach(function(page){
        if(page){
          waitOn.push(page._destroy());
        }
      });
      this.pageCache.length=0;
      this.pagePromises.length=0;
      varterminated=this.messageHandler.sendWithPromise('Terminate',null);
      waitOn.push(terminated);
      Promise.all(waitOn).then(function(){
        _this9.fontLoader.clear();

        if(_this9._networkStream){
          _this9._networkStream.cancelAllRequests();
        }

        if(_this9.messageHandler){
          _this9.messageHandler.destroy();

          _this9.messageHandler=null;
        }

        _this9.destroyCapability.resolve();
      },this.destroyCapability.reject);
      returnthis.destroyCapability.promise;
    }
  },{
    key:"setupMessageHandler",
    value:functionsetupMessageHandler(){
      varmessageHandler=this.messageHandler,
          loadingTask=this.loadingTask;
      messageHandler.on('GetReader',function(data,sink){
        var_this10=this;

        (0,_util.assert)(this._networkStream);
        this._fullReader=this._networkStream.getFullReader();

        this._fullReader.onProgress=function(evt){
          _this10._lastProgress={
            loaded:evt.loaded,
            total:evt.total
          };
        };

        sink.onPull=function(){
          _this10._fullReader.read().then(function(_ref7){
            varvalue=_ref7.value,
                done=_ref7.done;

            if(done){
              sink.close();
              return;
            }

            (0,_util.assert)((0,_util.isArrayBuffer)(value));
            sink.enqueue(newUint8Array(value),1,[value]);
          })["catch"](function(reason){
            sink.error(reason);
          });
        };

        sink.onCancel=function(reason){
          _this10._fullReader.cancel(reason);
        };
      },this);
      messageHandler.on('ReaderHeadersReady',function(data){
        var_this11=this;

        varheadersCapability=(0,_util.createPromiseCapability)();
        varfullReader=this._fullReader;
        fullReader.headersReady.then(function(){
          if(!fullReader.isStreamingSupported||!fullReader.isRangeSupported){
            if(_this11._lastProgress&&loadingTask.onProgress){
              loadingTask.onProgress(_this11._lastProgress);
            }

            fullReader.onProgress=function(evt){
              if(loadingTask.onProgress){
                loadingTask.onProgress({
                  loaded:evt.loaded,
                  total:evt.total
                });
              }
            };
          }

          headersCapability.resolve({
            isStreamingSupported:fullReader.isStreamingSupported,
            isRangeSupported:fullReader.isRangeSupported,
            contentLength:fullReader.contentLength
          });
        },headersCapability.reject);
        returnheadersCapability.promise;
      },this);
      messageHandler.on('GetRangeReader',function(data,sink){
        (0,_util.assert)(this._networkStream);

        varrangeReader=this._networkStream.getRangeReader(data.begin,data.end);

        if(!rangeReader){
          sink.close();
          return;
        }

        sink.onPull=function(){
          rangeReader.read().then(function(_ref8){
            varvalue=_ref8.value,
                done=_ref8.done;

            if(done){
              sink.close();
              return;
            }

            (0,_util.assert)((0,_util.isArrayBuffer)(value));
            sink.enqueue(newUint8Array(value),1,[value]);
          })["catch"](function(reason){
            sink.error(reason);
          });
        };

        sink.onCancel=function(reason){
          rangeReader.cancel(reason);
        };
      },this);
      messageHandler.on('GetDoc',function(_ref9){
        varpdfInfo=_ref9.pdfInfo;
        this._numPages=pdfInfo.numPages;

        loadingTask._capability.resolve(newPDFDocumentProxy(pdfInfo,this));
      },this);
      messageHandler.on('PasswordRequest',function(exception){
        var_this12=this;

        this._passwordCapability=(0,_util.createPromiseCapability)();

        if(loadingTask.onPassword){
          varupdatePassword=functionupdatePassword(password){
            _this12._passwordCapability.resolve({
              password:password
            });
          };

          try{
            loadingTask.onPassword(updatePassword,exception.code);
          }catch(ex){
            this._passwordCapability.reject(ex);
          }
        }else{
          this._passwordCapability.reject(new_util.PasswordException(exception.message,exception.code));
        }

        returnthis._passwordCapability.promise;
      },this);
      messageHandler.on('PasswordException',function(exception){
        loadingTask._capability.reject(new_util.PasswordException(exception.message,exception.code));
      },this);
      messageHandler.on('InvalidPDF',function(exception){
        loadingTask._capability.reject(new_util.InvalidPDFException(exception.message));
      },this);
      messageHandler.on('MissingPDF',function(exception){
        loadingTask._capability.reject(new_util.MissingPDFException(exception.message));
      },this);
      messageHandler.on('UnexpectedResponse',function(exception){
        loadingTask._capability.reject(new_util.UnexpectedResponseException(exception.message,exception.status));
      },this);
      messageHandler.on('UnknownError',function(exception){
        loadingTask._capability.reject(new_util.UnknownErrorException(exception.message,exception.details));
      },this);
      messageHandler.on('DataLoaded',function(data){
        if(loadingTask.onProgress){
          loadingTask.onProgress({
            loaded:data.length,
            total:data.length
          });
        }

        this.downloadInfoCapability.resolve(data);
      },this);
      messageHandler.on('StartRenderPage',function(data){
        if(this.destroyed){
          return;
        }

        varpage=this.pageCache[data.pageIndex];

        page._stats.timeEnd('PageRequest');

        page._startRenderPage(data.transparency,data.intent);
      },this);
      messageHandler.on('RenderPageChunk',function(data){
        if(this.destroyed){
          return;
        }

        varpage=this.pageCache[data.pageIndex];

        page._renderPageChunk(data.operatorList,data.intent);
      },this);
      messageHandler.on('commonobj',function(data){
        var_this13=this;

        if(this.destroyed){
          return;
        }

        var_data=_slicedToArray(data,3),
            id=_data[0],
            type=_data[1],
            exportedData=_data[2];

        if(this.commonObjs.has(id)){
          return;
        }

        switch(type){
          case'Font':
            varparams=this._params;

            if('error'inexportedData){
              varexportedError=exportedData.error;
              (0,_util.warn)("Errorduringfontloading:".concat(exportedError));
              this.commonObjs.resolve(id,exportedError);
              break;
            }

            varfontRegistry=null;

            if(params.pdfBug&&_global_scope["default"].FontInspector&&_global_scope["default"].FontInspector.enabled){
              fontRegistry={
                registerFont:functionregisterFont(font,url){
                  _global_scope["default"]['FontInspector'].fontAdded(font,url);
                }
              };
            }

            varfont=new_font_loader.FontFaceObject(exportedData,{
              isEvalSupported:params.isEvalSupported,
              disableFontFace:params.disableFontFace,
              ignoreErrors:params.ignoreErrors,
              onUnsupportedFeature:this._onUnsupportedFeature.bind(this),
              fontRegistry:fontRegistry
            });
            this.fontLoader.bind(font).then(function(){
              _this13.commonObjs.resolve(id,font);
            },function(reason){
              messageHandler.sendWithPromise('FontFallback',{
                id:id
              })["finally"](function(){
                _this13.commonObjs.resolve(id,font);
              });
            });
            break;

          case'FontPath':
          case'FontType3Res':
            this.commonObjs.resolve(id,exportedData);
            break;

          default:
            thrownewError("Gotunknowncommonobjecttype".concat(type));
        }
      },this);
      messageHandler.on('obj',function(data){
        if(this.destroyed){
          returnundefined;
        }

        var_data2=_slicedToArray(data,4),
            id=_data2[0],
            pageIndex=_data2[1],
            type=_data2[2],
            imageData=_data2[3];

        varpageProxy=this.pageCache[pageIndex];

        if(pageProxy.objs.has(id)){
          returnundefined;
        }

        switch(type){
          case'JpegStream':
            returnnewPromise(function(resolve,reject){
              varimg=newImage();

              img.onload=function(){
                resolve(img);
              };

              img.onerror=function(){
                reject(newError('ErrorduringJPEGimageloading'));
                (0,_display_utils.releaseImageResources)(img);
              };

              img.src=imageData;
            }).then(function(img){
              pageProxy.objs.resolve(id,img);
            });

          case'Image':
            pageProxy.objs.resolve(id,imageData);
            varMAX_IMAGE_SIZE_TO_STORE=8000000;

            if(imageData&&'data'inimageData&&imageData.data.length>MAX_IMAGE_SIZE_TO_STORE){
              pageProxy.cleanupAfterRender=true;
            }

            break;

          default:
            thrownewError("Gotunknownobjecttype".concat(type));
        }

        returnundefined;
      },this);
      messageHandler.on('DocProgress',function(data){
        if(this.destroyed){
          return;
        }

        if(loadingTask.onProgress){
          loadingTask.onProgress({
            loaded:data.loaded,
            total:data.total
          });
        }
      },this);
      messageHandler.on('PageError',function(data){
        if(this.destroyed){
          return;
        }

        varpage=this.pageCache[data.pageIndex];
        varintentState=page.intentStates[data.intent];

        if(intentState.displayReadyCapability){
          intentState.displayReadyCapability.reject(newError(data.error));
        }else{
          thrownewError(data.error);
        }

        if(intentState.operatorList){
          intentState.operatorList.lastChunk=true;

          for(vari=0;i<intentState.renderTasks.length;i++){
            intentState.renderTasks[i].operatorListChanged();
          }
        }
      },this);
      messageHandler.on('UnsupportedFeature',this._onUnsupportedFeature,this);
      messageHandler.on('JpegDecode',function(data){
        if(this.destroyed){
          returnPromise.reject(newError('Workerwasdestroyed'));
        }

        if(typeofdocument==='undefined'){
          returnPromise.reject(newError('"document"isnotdefined.'));
        }

        var_data3=_slicedToArray(data,2),
            imageUrl=_data3[0],
            components=_data3[1];

        if(components!==3&&components!==1){
          returnPromise.reject(newError('Only3componentsor1componentcanbereturned'));
        }

        returnnewPromise(function(resolve,reject){
          varimg=newImage();

          img.onload=function(){
            varwidth=img.width,
                height=img.height;
            varsize=width*height;
            varrgbaLength=size*4;
            varbuf=newUint8ClampedArray(size*components);
            vartmpCanvas=document.createElement('canvas');
            tmpCanvas.width=width;
            tmpCanvas.height=height;
            vartmpCtx=tmpCanvas.getContext('2d');
            tmpCtx.drawImage(img,0,0);
            vardata=tmpCtx.getImageData(0,0,width,height).data;

            if(components===3){
              for(vari=0,j=0;i<rgbaLength;i+=4,j+=3){
                buf[j]=data[i];
                buf[j+1]=data[i+1];
                buf[j+2]=data[i+2];
              }
            }elseif(components===1){
              for(var_i2=0,_j=0;_i2<rgbaLength;_i2+=4,_j++){
                buf[_j]=data[_i2];
              }
            }

            resolve({
              data:buf,
              width:width,
              height:height
            });
            (0,_display_utils.releaseImageResources)(img);
            tmpCanvas.width=0;
            tmpCanvas.height=0;
            tmpCanvas=null;
            tmpCtx=null;
          };

          img.onerror=function(){
            reject(newError('JpegDecodefailedtoloadimage'));
            (0,_display_utils.releaseImageResources)(img);
          };

          img.src=imageUrl;
        });
      },this);
      messageHandler.on('FetchBuiltInCMap',function(data){
        if(this.destroyed){
          returnPromise.reject(newError('Workerwasdestroyed'));
        }

        returnthis.CMapReaderFactory.fetch({
          name:data.name
        });
      },this);
    }
  },{
    key:"_onUnsupportedFeature",
    value:function_onUnsupportedFeature(_ref10){
      varfeatureId=_ref10.featureId;

      if(this.destroyed){
        return;
      }

      if(this.loadingTask.onUnsupportedFeature){
        this.loadingTask.onUnsupportedFeature(featureId);
      }
    }
  },{
    key:"getData",
    value:functiongetData(){
      returnthis.messageHandler.sendWithPromise('GetData',null);
    }
  },{
    key:"getPage",
    value:functiongetPage(pageNumber){
      var_this14=this;

      if(!Number.isInteger(pageNumber)||pageNumber<=0||pageNumber>this._numPages){
        returnPromise.reject(newError('Invalidpagerequest'));
      }

      varpageIndex=pageNumber-1;

      if(pageIndexinthis.pagePromises){
        returnthis.pagePromises[pageIndex];
      }

      varpromise=this.messageHandler.sendWithPromise('GetPage',{
        pageIndex:pageIndex
      }).then(function(pageInfo){
        if(_this14.destroyed){
          thrownewError('Transportdestroyed');
        }

        varpage=newPDFPageProxy(pageIndex,pageInfo,_this14,_this14._params.pdfBug);
        _this14.pageCache[pageIndex]=page;
        returnpage;
      });
      this.pagePromises[pageIndex]=promise;
      returnpromise;
    }
  },{
    key:"getPageIndex",
    value:functiongetPageIndex(ref){
      returnthis.messageHandler.sendWithPromise('GetPageIndex',{
        ref:ref
      })["catch"](function(reason){
        returnPromise.reject(newError(reason));
      });
    }
  },{
    key:"getAnnotations",
    value:functiongetAnnotations(pageIndex,intent){
      returnthis.messageHandler.sendWithPromise('GetAnnotations',{
        pageIndex:pageIndex,
        intent:intent
      });
    }
  },{
    key:"getDestinations",
    value:functiongetDestinations(){
      returnthis.messageHandler.sendWithPromise('GetDestinations',null);
    }
  },{
    key:"getDestination",
    value:functiongetDestination(id){
      if(typeofid!=='string'){
        returnPromise.reject(newError('Invaliddestinationrequest.'));
      }

      returnthis.messageHandler.sendWithPromise('GetDestination',{
        id:id
      });
    }
  },{
    key:"getPageLabels",
    value:functiongetPageLabels(){
      returnthis.messageHandler.sendWithPromise('GetPageLabels',null);
    }
  },{
    key:"getPageLayout",
    value:functiongetPageLayout(){
      returnthis.messageHandler.sendWithPromise('GetPageLayout',null);
    }
  },{
    key:"getPageMode",
    value:functiongetPageMode(){
      returnthis.messageHandler.sendWithPromise('GetPageMode',null);
    }
  },{
    key:"getViewerPreferences",
    value:functiongetViewerPreferences(){
      returnthis.messageHandler.sendWithPromise('GetViewerPreferences',null);
    }
  },{
    key:"getOpenActionDestination",
    value:functiongetOpenActionDestination(){
      returnthis.messageHandler.sendWithPromise('GetOpenActionDestination',null);
    }
  },{
    key:"getAttachments",
    value:functiongetAttachments(){
      returnthis.messageHandler.sendWithPromise('GetAttachments',null);
    }
  },{
    key:"getJavaScript",
    value:functiongetJavaScript(){
      returnthis.messageHandler.sendWithPromise('GetJavaScript',null);
    }
  },{
    key:"getOutline",
    value:functiongetOutline(){
      returnthis.messageHandler.sendWithPromise('GetOutline',null);
    }
  },{
    key:"getPermissions",
    value:functiongetPermissions(){
      returnthis.messageHandler.sendWithPromise('GetPermissions',null);
    }
  },{
    key:"getMetadata",
    value:functiongetMetadata(){
      var_this15=this;

      returnthis.messageHandler.sendWithPromise('GetMetadata',null).then(function(results){
        return{
          info:results[0],
          metadata:results[1]?new_metadata.Metadata(results[1]):null,
          contentDispositionFilename:_this15._fullReader?_this15._fullReader.filename:null
        };
      });
    }
  },{
    key:"getStats",
    value:functiongetStats(){
      returnthis.messageHandler.sendWithPromise('GetStats',null);
    }
  },{
    key:"startCleanup",
    value:functionstartCleanup(){
      var_this16=this;

      this.messageHandler.sendWithPromise('Cleanup',null).then(function(){
        for(vari=0,ii=_this16.pageCache.length;i<ii;i++){
          varpage=_this16.pageCache[i];

          if(page){
            page.cleanup();
          }
        }

        _this16.commonObjs.clear();

        _this16.fontLoader.clear();
      });
    }
  },{
    key:"loadingParams",
    get:functionget(){
      varparams=this._params;
      return(0,_util.shadow)(this,'loadingParams',{
        disableAutoFetch:params.disableAutoFetch,
        disableCreateObjectURL:params.disableCreateObjectURL,
        disableFontFace:params.disableFontFace,
        nativeImageDecoderSupport:params.nativeImageDecoderSupport
      });
    }
  }]);

  returnWorkerTransport;
}();

varPDFObjects=
/*#__PURE__*/
function(){
  functionPDFObjects(){
    _classCallCheck(this,PDFObjects);

    this._objs=Object.create(null);
  }

  _createClass(PDFObjects,[{
    key:"_ensureObj",
    value:function_ensureObj(objId){
      if(this._objs[objId]){
        returnthis._objs[objId];
      }

      returnthis._objs[objId]={
        capability:(0,_util.createPromiseCapability)(),
        data:null,
        resolved:false
      };
    }
  },{
    key:"get",
    value:functionget(objId){
      varcallback=arguments.length>1&&arguments[1]!==undefined?arguments[1]:null;

      if(callback){
        this._ensureObj(objId).capability.promise.then(callback);

        returnnull;
      }

      varobj=this._objs[objId];

      if(!obj||!obj.resolved){
        thrownewError("Requestingobjectthatisn'tresolvedyet".concat(objId,"."));
      }

      returnobj.data;
    }
  },{
    key:"has",
    value:functionhas(objId){
      varobj=this._objs[objId];
      returnobj?obj.resolved:false;
    }
  },{
    key:"resolve",
    value:functionresolve(objId,data){
      varobj=this._ensureObj(objId);

      obj.resolved=true;
      obj.data=data;
      obj.capability.resolve(data);
    }
  },{
    key:"clear",
    value:functionclear(){
      for(varobjIdinthis._objs){
        vardata=this._objs[objId].data;

        if(typeofImage!=='undefined'&&datainstanceofImage){
          (0,_display_utils.releaseImageResources)(data);
        }
      }

      this._objs=Object.create(null);
    }
  }]);

  returnPDFObjects;
}();

varRenderTask=
/*#__PURE__*/
function(){
  functionRenderTask(internalRenderTask){
    _classCallCheck(this,RenderTask);

    this._internalRenderTask=internalRenderTask;
    this.onContinue=null;
  }

  _createClass(RenderTask,[{
    key:"cancel",
    value:functioncancel(){
      this._internalRenderTask.cancel();
    }
  },{
    key:"then",
    value:functionthen(onFulfilled,onRejected){
      (0,_display_utils.deprecated)('RenderTask.thenmethod,usethe`promise`getterinstead.');
      returnthis.promise.then.apply(this.promise,arguments);
    }
  },{
    key:"promise",
    get:functionget(){
      returnthis._internalRenderTask.capability.promise;
    }
  }]);

  returnRenderTask;
}();

varInternalRenderTask=functionInternalRenderTaskClosure(){
  varcanvasInRendering=newWeakSet();

  varInternalRenderTask=
  /*#__PURE__*/
  function(){
    functionInternalRenderTask(_ref11){
      varcallback=_ref11.callback,
          params=_ref11.params,
          objs=_ref11.objs,
          commonObjs=_ref11.commonObjs,
          operatorList=_ref11.operatorList,
          pageNumber=_ref11.pageNumber,
          canvasFactory=_ref11.canvasFactory,
          webGLContext=_ref11.webGLContext,
          _ref11$useRequestAnim=_ref11.useRequestAnimationFrame,
          useRequestAnimationFrame=_ref11$useRequestAnim===void0?false:_ref11$useRequestAnim,
          _ref11$pdfBug=_ref11.pdfBug,
          pdfBug=_ref11$pdfBug===void0?false:_ref11$pdfBug;

      _classCallCheck(this,InternalRenderTask);

      this.callback=callback;
      this.params=params;
      this.objs=objs;
      this.commonObjs=commonObjs;
      this.operatorListIdx=null;
      this.operatorList=operatorList;
      this.pageNumber=pageNumber;
      this.canvasFactory=canvasFactory;
      this.webGLContext=webGLContext;
      this._pdfBug=pdfBug;
      this.running=false;
      this.graphicsReadyCallback=null;
      this.graphicsReady=false;
      this._useRequestAnimationFrame=useRequestAnimationFrame===true&&typeofwindow!=='undefined';
      this.cancelled=false;
      this.capability=(0,_util.createPromiseCapability)();
      this.task=newRenderTask(this);
      this._continueBound=this._continue.bind(this);
      this._scheduleNextBound=this._scheduleNext.bind(this);
      this._nextBound=this._next.bind(this);
      this._canvas=params.canvasContext.canvas;
    }

    _createClass(InternalRenderTask,[{
      key:"initializeGraphics",
      value:functioninitializeGraphics(){
        vartransparency=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

        if(this.cancelled){
          return;
        }

        if(this._canvas){
          if(canvasInRendering.has(this._canvas)){
            thrownewError('Cannotusethesamecanvasduringmultiplerender()operations.'+'Usedifferentcanvasorensurepreviousoperationswere'+'cancelledorcompleted.');
          }

          canvasInRendering.add(this._canvas);
        }

        if(this._pdfBug&&_global_scope["default"].StepperManager&&_global_scope["default"].StepperManager.enabled){
          this.stepper=_global_scope["default"].StepperManager.create(this.pageNumber-1);
          this.stepper.init(this.operatorList);
          this.stepper.nextBreakPoint=this.stepper.getNextBreakPoint();
        }

        var_this$params=this.params,
            canvasContext=_this$params.canvasContext,
            viewport=_this$params.viewport,
            transform=_this$params.transform,
            imageLayer=_this$params.imageLayer,
            background=_this$params.background;
        this.gfx=new_canvas.CanvasGraphics(canvasContext,this.commonObjs,this.objs,this.canvasFactory,this.webGLContext,imageLayer);
        this.gfx.beginDrawing({
          transform:transform,
          viewport:viewport,
          transparency:transparency,
          background:background
        });
        this.operatorListIdx=0;
        this.graphicsReady=true;

        if(this.graphicsReadyCallback){
          this.graphicsReadyCallback();
        }
      }
    },{
      key:"cancel",
      value:functioncancel(){
        varerror=arguments.length>0&&arguments[0]!==undefined?arguments[0]:null;
        this.running=false;
        this.cancelled=true;

        if(this.gfx){
          this.gfx.endDrawing();
        }

        if(this._canvas){
          canvasInRendering["delete"](this._canvas);
        }

        this.callback(error||new_display_utils.RenderingCancelledException("Renderingcancelled,page".concat(this.pageNumber),'canvas'));
      }
    },{
      key:"operatorListChanged",
      value:functionoperatorListChanged(){
        if(!this.graphicsReady){
          if(!this.graphicsReadyCallback){
            this.graphicsReadyCallback=this._continueBound;
          }

          return;
        }

        if(this.stepper){
          this.stepper.updateOperatorList(this.operatorList);
        }

        if(this.running){
          return;
        }

        this._continue();
      }
    },{
      key:"_continue",
      value:function_continue(){
        this.running=true;

        if(this.cancelled){
          return;
        }

        if(this.task.onContinue){
          this.task.onContinue(this._scheduleNextBound);
        }else{
          this._scheduleNext();
        }
      }
    },{
      key:"_scheduleNext",
      value:function_scheduleNext(){
        var_this17=this;

        if(this._useRequestAnimationFrame){
          window.requestAnimationFrame(function(){
            _this17._nextBound()["catch"](_this17.cancel.bind(_this17));
          });
        }else{
          Promise.resolve().then(this._nextBound)["catch"](this.cancel.bind(this));
        }
      }
    },{
      key:"_next",
      value:function(){
        var_next2=_asyncToGenerator(
        /*#__PURE__*/
        _regenerator["default"].mark(function_callee(){
          return_regenerator["default"].wrap(function_callee$(_context){
            while(1){
              switch(_context.prev=_context.next){
                case0:
                  if(!this.cancelled){
                    _context.next=2;
                    break;
                  }

                  return_context.abrupt("return");

                case2:
                  this.operatorListIdx=this.gfx.executeOperatorList(this.operatorList,this.operatorListIdx,this._continueBound,this.stepper);

                  if(this.operatorListIdx===this.operatorList.argsArray.length){
                    this.running=false;

                    if(this.operatorList.lastChunk){
                      this.gfx.endDrawing();

                      if(this._canvas){
                        canvasInRendering["delete"](this._canvas);
                      }

                      this.callback();
                    }
                  }

                case4:
                case"end":
                  return_context.stop();
              }
            }
          },_callee,this);
        }));

        function_next(){
          return_next2.apply(this,arguments);
        }

        return_next;
      }()
    }]);

    returnInternalRenderTask;
  }();

  returnInternalRenderTask;
}();

varversion='2.2.228';
exports.version=version;
varbuild='d7afb74a';
exports.build=build;

/***/}),
/*148*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=__w_pdfjs_require__(149);

/***/}),
/*149*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";
/*WEBPACKVARINJECTION*/(function(module){

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

varruntime=function(exports){
  "usestrict";

  varOp=Object.prototype;
  varhasOwn=Op.hasOwnProperty;
  varundefined;
  var$Symbol=typeofSymbol==="function"?Symbol:{};
  variteratorSymbol=$Symbol.iterator||"@@iterator";
  varasyncIteratorSymbol=$Symbol.asyncIterator||"@@asyncIterator";
  vartoStringTagSymbol=$Symbol.toStringTag||"@@toStringTag";

  functionwrap(innerFn,outerFn,self,tryLocsList){
    varprotoGenerator=outerFn&&outerFn.prototypeinstanceofGenerator?outerFn:Generator;
    vargenerator=Object.create(protoGenerator.prototype);
    varcontext=newContext(tryLocsList||[]);
    generator._invoke=makeInvokeMethod(innerFn,self,context);
    returngenerator;
  }

  exports.wrap=wrap;

  functiontryCatch(fn,obj,arg){
    try{
      return{
        type:"normal",
        arg:fn.call(obj,arg)
      };
    }catch(err){
      return{
        type:"throw",
        arg:err
      };
    }
  }

  varGenStateSuspendedStart="suspendedStart";
  varGenStateSuspendedYield="suspendedYield";
  varGenStateExecuting="executing";
  varGenStateCompleted="completed";
  varContinueSentinel={};

  functionGenerator(){}

  functionGeneratorFunction(){}

  functionGeneratorFunctionPrototype(){}

  varIteratorPrototype={};

  IteratorPrototype[iteratorSymbol]=function(){
    returnthis;
  };

  vargetProto=Object.getPrototypeOf;
  varNativeIteratorPrototype=getProto&&getProto(getProto(values([])));

  if(NativeIteratorPrototype&&NativeIteratorPrototype!==Op&&hasOwn.call(NativeIteratorPrototype,iteratorSymbol)){
    IteratorPrototype=NativeIteratorPrototype;
  }

  varGp=GeneratorFunctionPrototype.prototype=Generator.prototype=Object.create(IteratorPrototype);
  GeneratorFunction.prototype=Gp.constructor=GeneratorFunctionPrototype;
  GeneratorFunctionPrototype.constructor=GeneratorFunction;
  GeneratorFunctionPrototype[toStringTagSymbol]=GeneratorFunction.displayName="GeneratorFunction";

  functiondefineIteratorMethods(prototype){
    ["next","throw","return"].forEach(function(method){
      prototype[method]=function(arg){
        returnthis._invoke(method,arg);
      };
    });
  }

  exports.isGeneratorFunction=function(genFun){
    varctor=typeofgenFun==="function"&&genFun.constructor;
    returnctor?ctor===GeneratorFunction||(ctor.displayName||ctor.name)==="GeneratorFunction":false;
  };

  exports.mark=function(genFun){
    if(Object.setPrototypeOf){
      Object.setPrototypeOf(genFun,GeneratorFunctionPrototype);
    }else{
      genFun.__proto__=GeneratorFunctionPrototype;

      if(!(toStringTagSymbolingenFun)){
        genFun[toStringTagSymbol]="GeneratorFunction";
      }
    }

    genFun.prototype=Object.create(Gp);
    returngenFun;
  };

  exports.awrap=function(arg){
    return{
      __await:arg
    };
  };

  functionAsyncIterator(generator){
    functioninvoke(method,arg,resolve,reject){
      varrecord=tryCatch(generator[method],generator,arg);

      if(record.type==="throw"){
        reject(record.arg);
      }else{
        varresult=record.arg;
        varvalue=result.value;

        if(value&&_typeof(value)==="object"&&hasOwn.call(value,"__await")){
          returnPromise.resolve(value.__await).then(function(value){
            invoke("next",value,resolve,reject);
          },function(err){
            invoke("throw",err,resolve,reject);
          });
        }

        returnPromise.resolve(value).then(function(unwrapped){
          result.value=unwrapped;
          resolve(result);
        },function(error){
          returninvoke("throw",error,resolve,reject);
        });
      }
    }

    varpreviousPromise;

    functionenqueue(method,arg){
      functioncallInvokeWithMethodAndArg(){
        returnnewPromise(function(resolve,reject){
          invoke(method,arg,resolve,reject);
        });
      }

      returnpreviousPromise=previousPromise?previousPromise.then(callInvokeWithMethodAndArg,callInvokeWithMethodAndArg):callInvokeWithMethodAndArg();
    }

    this._invoke=enqueue;
  }

  defineIteratorMethods(AsyncIterator.prototype);

  AsyncIterator.prototype[asyncIteratorSymbol]=function(){
    returnthis;
  };

  exports.AsyncIterator=AsyncIterator;

  exports.async=function(innerFn,outerFn,self,tryLocsList){
    variter=newAsyncIterator(wrap(innerFn,outerFn,self,tryLocsList));
    returnexports.isGeneratorFunction(outerFn)?iter:iter.next().then(function(result){
      returnresult.done?result.value:iter.next();
    });
  };

  functionmakeInvokeMethod(innerFn,self,context){
    varstate=GenStateSuspendedStart;
    returnfunctioninvoke(method,arg){
      if(state===GenStateExecuting){
        thrownewError("Generatorisalreadyrunning");
      }

      if(state===GenStateCompleted){
        if(method==="throw"){
          throwarg;
        }

        returndoneResult();
      }

      context.method=method;
      context.arg=arg;

      while(true){
        vardelegate=context.delegate;

        if(delegate){
          vardelegateResult=maybeInvokeDelegate(delegate,context);

          if(delegateResult){
            if(delegateResult===ContinueSentinel)continue;
            returndelegateResult;
          }
        }

        if(context.method==="next"){
          context.sent=context._sent=context.arg;
        }elseif(context.method==="throw"){
          if(state===GenStateSuspendedStart){
            state=GenStateCompleted;
            throwcontext.arg;
          }

          context.dispatchException(context.arg);
        }elseif(context.method==="return"){
          context.abrupt("return",context.arg);
        }

        state=GenStateExecuting;
        varrecord=tryCatch(innerFn,self,context);

        if(record.type==="normal"){
          state=context.done?GenStateCompleted:GenStateSuspendedYield;

          if(record.arg===ContinueSentinel){
            continue;
          }

          return{
            value:record.arg,
            done:context.done
          };
        }elseif(record.type==="throw"){
          state=GenStateCompleted;
          context.method="throw";
          context.arg=record.arg;
        }
      }
    };
  }

  functionmaybeInvokeDelegate(delegate,context){
    varmethod=delegate.iterator[context.method];

    if(method===undefined){
      context.delegate=null;

      if(context.method==="throw"){
        if(delegate.iterator["return"]){
          context.method="return";
          context.arg=undefined;
          maybeInvokeDelegate(delegate,context);

          if(context.method==="throw"){
            returnContinueSentinel;
          }
        }

        context.method="throw";
        context.arg=newTypeError("Theiteratordoesnotprovidea'throw'method");
      }

      returnContinueSentinel;
    }

    varrecord=tryCatch(method,delegate.iterator,context.arg);

    if(record.type==="throw"){
      context.method="throw";
      context.arg=record.arg;
      context.delegate=null;
      returnContinueSentinel;
    }

    varinfo=record.arg;

    if(!info){
      context.method="throw";
      context.arg=newTypeError("iteratorresultisnotanobject");
      context.delegate=null;
      returnContinueSentinel;
    }

    if(info.done){
      context[delegate.resultName]=info.value;
      context.next=delegate.nextLoc;

      if(context.method!=="return"){
        context.method="next";
        context.arg=undefined;
      }
    }else{
      returninfo;
    }

    context.delegate=null;
    returnContinueSentinel;
  }

  defineIteratorMethods(Gp);
  Gp[toStringTagSymbol]="Generator";

  Gp[iteratorSymbol]=function(){
    returnthis;
  };

  Gp.toString=function(){
    return"[objectGenerator]";
  };

  functionpushTryEntry(locs){
    varentry={
      tryLoc:locs[0]
    };

    if(1inlocs){
      entry.catchLoc=locs[1];
    }

    if(2inlocs){
      entry.finallyLoc=locs[2];
      entry.afterLoc=locs[3];
    }

    this.tryEntries.push(entry);
  }

  functionresetTryEntry(entry){
    varrecord=entry.completion||{};
    record.type="normal";
    deleterecord.arg;
    entry.completion=record;
  }

  functionContext(tryLocsList){
    this.tryEntries=[{
      tryLoc:"root"
    }];
    tryLocsList.forEach(pushTryEntry,this);
    this.reset(true);
  }

  exports.keys=function(object){
    varkeys=[];

    for(varkeyinobject){
      keys.push(key);
    }

    keys.reverse();
    returnfunctionnext(){
      while(keys.length){
        varkey=keys.pop();

        if(keyinobject){
          next.value=key;
          next.done=false;
          returnnext;
        }
      }

      next.done=true;
      returnnext;
    };
  };

  functionvalues(iterable){
    if(iterable){
      variteratorMethod=iterable[iteratorSymbol];

      if(iteratorMethod){
        returniteratorMethod.call(iterable);
      }

      if(typeofiterable.next==="function"){
        returniterable;
      }

      if(!isNaN(iterable.length)){
        vari=-1,
            next=functionnext(){
          while(++i<iterable.length){
            if(hasOwn.call(iterable,i)){
              next.value=iterable[i];
              next.done=false;
              returnnext;
            }
          }

          next.value=undefined;
          next.done=true;
          returnnext;
        };

        returnnext.next=next;
      }
    }

    return{
      next:doneResult
    };
  }

  exports.values=values;

  functiondoneResult(){
    return{
      value:undefined,
      done:true
    };
  }

  Context.prototype={
    constructor:Context,
    reset:functionreset(skipTempReset){
      this.prev=0;
      this.next=0;
      this.sent=this._sent=undefined;
      this.done=false;
      this.delegate=null;
      this.method="next";
      this.arg=undefined;
      this.tryEntries.forEach(resetTryEntry);

      if(!skipTempReset){
        for(varnameinthis){
          if(name.charAt(0)==="t"&&hasOwn.call(this,name)&&!isNaN(+name.slice(1))){
            this[name]=undefined;
          }
        }
      }
    },
    stop:functionstop(){
      this.done=true;
      varrootEntry=this.tryEntries[0];
      varrootRecord=rootEntry.completion;

      if(rootRecord.type==="throw"){
        throwrootRecord.arg;
      }

      returnthis.rval;
    },
    dispatchException:functiondispatchException(exception){
      if(this.done){
        throwexception;
      }

      varcontext=this;

      functionhandle(loc,caught){
        record.type="throw";
        record.arg=exception;
        context.next=loc;

        if(caught){
          context.method="next";
          context.arg=undefined;
        }

        return!!caught;
      }

      for(vari=this.tryEntries.length-1;i>=0;--i){
        varentry=this.tryEntries[i];
        varrecord=entry.completion;

        if(entry.tryLoc==="root"){
          returnhandle("end");
        }

        if(entry.tryLoc<=this.prev){
          varhasCatch=hasOwn.call(entry,"catchLoc");
          varhasFinally=hasOwn.call(entry,"finallyLoc");

          if(hasCatch&&hasFinally){
            if(this.prev<entry.catchLoc){
              returnhandle(entry.catchLoc,true);
            }elseif(this.prev<entry.finallyLoc){
              returnhandle(entry.finallyLoc);
            }
          }elseif(hasCatch){
            if(this.prev<entry.catchLoc){
              returnhandle(entry.catchLoc,true);
            }
          }elseif(hasFinally){
            if(this.prev<entry.finallyLoc){
              returnhandle(entry.finallyLoc);
            }
          }else{
            thrownewError("trystatementwithoutcatchorfinally");
          }
        }
      }
    },
    abrupt:functionabrupt(type,arg){
      for(vari=this.tryEntries.length-1;i>=0;--i){
        varentry=this.tryEntries[i];

        if(entry.tryLoc<=this.prev&&hasOwn.call(entry,"finallyLoc")&&this.prev<entry.finallyLoc){
          varfinallyEntry=entry;
          break;
        }
      }

      if(finallyEntry&&(type==="break"||type==="continue")&&finallyEntry.tryLoc<=arg&&arg<=finallyEntry.finallyLoc){
        finallyEntry=null;
      }

      varrecord=finallyEntry?finallyEntry.completion:{};
      record.type=type;
      record.arg=arg;

      if(finallyEntry){
        this.method="next";
        this.next=finallyEntry.finallyLoc;
        returnContinueSentinel;
      }

      returnthis.complete(record);
    },
    complete:functioncomplete(record,afterLoc){
      if(record.type==="throw"){
        throwrecord.arg;
      }

      if(record.type==="break"||record.type==="continue"){
        this.next=record.arg;
      }elseif(record.type==="return"){
        this.rval=this.arg=record.arg;
        this.method="return";
        this.next="end";
      }elseif(record.type==="normal"&&afterLoc){
        this.next=afterLoc;
      }

      returnContinueSentinel;
    },
    finish:functionfinish(finallyLoc){
      for(vari=this.tryEntries.length-1;i>=0;--i){
        varentry=this.tryEntries[i];

        if(entry.finallyLoc===finallyLoc){
          this.complete(entry.completion,entry.afterLoc);
          resetTryEntry(entry);
          returnContinueSentinel;
        }
      }
    },
    "catch":function_catch(tryLoc){
      for(vari=this.tryEntries.length-1;i>=0;--i){
        varentry=this.tryEntries[i];

        if(entry.tryLoc===tryLoc){
          varrecord=entry.completion;

          if(record.type==="throw"){
            varthrown=record.arg;
            resetTryEntry(entry);
          }

          returnthrown;
        }
      }

      thrownewError("illegalcatchattempt");
    },
    delegateYield:functiondelegateYield(iterable,resultName,nextLoc){
      this.delegate={
        iterator:values(iterable),
        resultName:resultName,
        nextLoc:nextLoc
      };

      if(this.method==="next"){
        this.arg=undefined;
      }

      returnContinueSentinel;
    }
  };
  returnexports;
}((false?undefined:_typeof(module))==="object"?module.exports:{});

try{
  regeneratorRuntime=runtime;
}catch(accidentalStrictMode){
  Function("r","regeneratorRuntime=r")(runtime);
}
/*WEBPACKVARINJECTION*/}.call(this,__w_pdfjs_require__(150)(module)))

/***/}),
/*150*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


module.exports=function(module){
  if(!module.webpackPolyfill){
    module.deprecate=function(){};

    module.paths=[];
    if(!module.children)module.children=[];
    Object.defineProperty(module,"loaded",{
      enumerable:true,
      get:functionget(){
        returnmodule.l;
      }
    });
    Object.defineProperty(module,"id",{
      enumerable:true,
      get:functionget(){
        returnmodule.i;
      }
    });
    module.webpackPolyfill=1;
  }

  returnmodule;
};

/***/}),
/*151*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.addLinkAttributes=addLinkAttributes;
exports.getFilenameFromUrl=getFilenameFromUrl;
exports.isFetchSupported=isFetchSupported;
exports.isValidFetchUrl=isValidFetchUrl;
exports.loadScript=loadScript;
exports.deprecated=deprecated;
exports.releaseImageResources=releaseImageResources;
exports.PDFDateString=exports.DummyStatTimer=exports.StatTimer=exports.DOMSVGFactory=exports.DOMCMapReaderFactory=exports.DOMCanvasFactory=exports.DEFAULT_LINK_REL=exports.LinkTarget=exports.RenderingCancelledException=exports.PageViewport=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{default:obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varDEFAULT_LINK_REL='noopenernoreferrernofollow';
exports.DEFAULT_LINK_REL=DEFAULT_LINK_REL;
varSVG_NS='http://www.w3.org/2000/svg';

varDOMCanvasFactory=
/*#__PURE__*/
function(){
  functionDOMCanvasFactory(){
    _classCallCheck(this,DOMCanvasFactory);
  }

  _createClass(DOMCanvasFactory,[{
    key:"create",
    value:functioncreate(width,height){
      if(width<=0||height<=0){
        thrownewError('Invalidcanvassize');
      }

      varcanvas=document.createElement('canvas');
      varcontext=canvas.getContext('2d');
      canvas.width=width;
      canvas.height=height;
      return{
        canvas:canvas,
        context:context
      };
    }
  },{
    key:"reset",
    value:functionreset(canvasAndContext,width,height){
      if(!canvasAndContext.canvas){
        thrownewError('Canvasisnotspecified');
      }

      if(width<=0||height<=0){
        thrownewError('Invalidcanvassize');
      }

      canvasAndContext.canvas.width=width;
      canvasAndContext.canvas.height=height;
    }
  },{
    key:"destroy",
    value:functiondestroy(canvasAndContext){
      if(!canvasAndContext.canvas){
        thrownewError('Canvasisnotspecified');
      }

      canvasAndContext.canvas.width=0;
      canvasAndContext.canvas.height=0;
      canvasAndContext.canvas=null;
      canvasAndContext.context=null;
    }
  }]);

  returnDOMCanvasFactory;
}();

exports.DOMCanvasFactory=DOMCanvasFactory;

varDOMCMapReaderFactory=
/*#__PURE__*/
function(){
  functionDOMCMapReaderFactory(_ref){
    var_ref$baseUrl=_ref.baseUrl,
        baseUrl=_ref$baseUrl===void0?null:_ref$baseUrl,
        _ref$isCompressed=_ref.isCompressed,
        isCompressed=_ref$isCompressed===void0?false:_ref$isCompressed;

    _classCallCheck(this,DOMCMapReaderFactory);

    this.baseUrl=baseUrl;
    this.isCompressed=isCompressed;
  }

  _createClass(DOMCMapReaderFactory,[{
    key:"fetch",
    value:function(_fetch){
      functionfetch(_x){
        return_fetch.apply(this,arguments);
      }

      fetch.toString=function(){
        return_fetch.toString();
      };

      returnfetch;
    }(
    /*#__PURE__*/
    function(){
      var_ref3=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(_ref2){
        var_this=this;

        varname,url,compressionType;
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                name=_ref2.name;

                if(this.baseUrl){
                  _context2.next=3;
                  break;
                }

                thrownewError('TheCMap"baseUrl"parametermustbespecified,ensurethat'+'the"cMapUrl"and"cMapPacked"APIparametersareprovided.');

              case3:
                if(name){
                  _context2.next=5;
                  break;
                }

                thrownewError('CMapnamemustbespecified.');

              case5:
                url=this.baseUrl+name+(this.isCompressed?'.bcmap':'');
                compressionType=this.isCompressed?_util.CMapCompressionType.BINARY:_util.CMapCompressionType.NONE;

                if(!(isFetchSupported()&&isValidFetchUrl(url,document.baseURI))){
                  _context2.next=9;
                  break;
                }

                return_context2.abrupt("return",fetch(url).then(
                /*#__PURE__*/
                function(){
                  var_ref4=_asyncToGenerator(
                  /*#__PURE__*/
                  _regenerator["default"].mark(function_callee(response){
                    varcMapData;
                    return_regenerator["default"].wrap(function_callee$(_context){
                      while(1){
                        switch(_context.prev=_context.next){
                          case0:
                            if(response.ok){
                              _context.next=2;
                              break;
                            }

                            thrownewError(response.statusText);

                          case2:
                            if(!_this.isCompressed){
                              _context.next=10;
                              break;
                            }

                            _context.t0=Uint8Array;
                            _context.next=6;
                            returnresponse.arrayBuffer();

                          case6:
                            _context.t1=_context.sent;
                            cMapData=new_context.t0(_context.t1);
                            _context.next=15;
                            break;

                          case10:
                            _context.t2=_util.stringToBytes;
                            _context.next=13;
                            returnresponse.text();

                          case13:
                            _context.t3=_context.sent;
                            cMapData=(0,_context.t2)(_context.t3);

                          case15:
                            return_context.abrupt("return",{
                              cMapData:cMapData,
                              compressionType:compressionType
                            });

                          case16:
                          case"end":
                            return_context.stop();
                        }
                      }
                    },_callee);
                  }));

                  returnfunction(_x3){
                    return_ref4.apply(this,arguments);
                  };
                }())["catch"](function(reason){
                  thrownewError("Unabletoload".concat(_this.isCompressed?'binary':'')+"CMapat:".concat(url));
                }));

              case9:
                return_context2.abrupt("return",newPromise(function(resolve,reject){
                  varrequest=newXMLHttpRequest();
                  request.open('GET',url,true);

                  if(_this.isCompressed){
                    request.responseType='arraybuffer';
                  }

                  request.onreadystatechange=function(){
                    if(request.readyState!==XMLHttpRequest.DONE){
                      return;
                    }

                    if(request.status===200||request.status===0){
                      varcMapData;

                      if(_this.isCompressed&&request.response){
                        cMapData=newUint8Array(request.response);
                      }elseif(!_this.isCompressed&&request.responseText){
                        cMapData=(0,_util.stringToBytes)(request.responseText);
                      }

                      if(cMapData){
                        resolve({
                          cMapData:cMapData,
                          compressionType:compressionType
                        });
                        return;
                      }
                    }

                    reject(newError(request.statusText));
                  };

                  request.send(null);
                })["catch"](function(reason){
                  thrownewError("Unabletoload".concat(_this.isCompressed?'binary':'')+"CMapat:".concat(url));
                }));

              case10:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      returnfunction(_x2){
        return_ref3.apply(this,arguments);
      };
    }())
  }]);

  returnDOMCMapReaderFactory;
}();

exports.DOMCMapReaderFactory=DOMCMapReaderFactory;

varDOMSVGFactory=
/*#__PURE__*/
function(){
  functionDOMSVGFactory(){
    _classCallCheck(this,DOMSVGFactory);
  }

  _createClass(DOMSVGFactory,[{
    key:"create",
    value:functioncreate(width,height){
      (0,_util.assert)(width>0&&height>0,'InvalidSVGdimensions');
      varsvg=document.createElementNS(SVG_NS,'svg:svg');
      svg.setAttribute('version','1.1');
      svg.setAttribute('width',width+'px');
      svg.setAttribute('height',height+'px');
      svg.setAttribute('preserveAspectRatio','none');
      svg.setAttribute('viewBox','00'+width+''+height);
      returnsvg;
    }
  },{
    key:"createElement",
    value:functioncreateElement(type){
      (0,_util.assert)(typeoftype==='string','InvalidSVGelementtype');
      returndocument.createElementNS(SVG_NS,type);
    }
  }]);

  returnDOMSVGFactory;
}();

exports.DOMSVGFactory=DOMSVGFactory;

varPageViewport=
/*#__PURE__*/
function(){
  functionPageViewport(_ref5){
    varviewBox=_ref5.viewBox,
        scale=_ref5.scale,
        rotation=_ref5.rotation,
        _ref5$offsetX=_ref5.offsetX,
        offsetX=_ref5$offsetX===void0?0:_ref5$offsetX,
        _ref5$offsetY=_ref5.offsetY,
        offsetY=_ref5$offsetY===void0?0:_ref5$offsetY,
        _ref5$dontFlip=_ref5.dontFlip,
        dontFlip=_ref5$dontFlip===void0?false:_ref5$dontFlip;

    _classCallCheck(this,PageViewport);

    this.viewBox=viewBox;
    this.scale=scale;
    this.rotation=rotation;
    this.offsetX=offsetX;
    this.offsetY=offsetY;
    varcenterX=(viewBox[2]+viewBox[0])/2;
    varcenterY=(viewBox[3]+viewBox[1])/2;
    varrotateA,rotateB,rotateC,rotateD;
    rotation=rotation%360;
    rotation=rotation<0?rotation+360:rotation;

    switch(rotation){
      case180:
        rotateA=-1;
        rotateB=0;
        rotateC=0;
        rotateD=1;
        break;

      case90:
        rotateA=0;
        rotateB=1;
        rotateC=1;
        rotateD=0;
        break;

      case270:
        rotateA=0;
        rotateB=-1;
        rotateC=-1;
        rotateD=0;
        break;

      default:
        rotateA=1;
        rotateB=0;
        rotateC=0;
        rotateD=-1;
        break;
    }

    if(dontFlip){
      rotateC=-rotateC;
      rotateD=-rotateD;
    }

    varoffsetCanvasX,offsetCanvasY;
    varwidth,height;

    if(rotateA===0){
      offsetCanvasX=Math.abs(centerY-viewBox[1])*scale+offsetX;
      offsetCanvasY=Math.abs(centerX-viewBox[0])*scale+offsetY;
      width=Math.abs(viewBox[3]-viewBox[1])*scale;
      height=Math.abs(viewBox[2]-viewBox[0])*scale;
    }else{
      offsetCanvasX=Math.abs(centerX-viewBox[0])*scale+offsetX;
      offsetCanvasY=Math.abs(centerY-viewBox[1])*scale+offsetY;
      width=Math.abs(viewBox[2]-viewBox[0])*scale;
      height=Math.abs(viewBox[3]-viewBox[1])*scale;
    }

    this.transform=[rotateA*scale,rotateB*scale,rotateC*scale,rotateD*scale,offsetCanvasX-rotateA*scale*centerX-rotateC*scale*centerY,offsetCanvasY-rotateB*scale*centerX-rotateD*scale*centerY];
    this.width=width;
    this.height=height;
  }

  _createClass(PageViewport,[{
    key:"clone",
    value:functionclone(){
      var_ref6=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
          _ref6$scale=_ref6.scale,
          scale=_ref6$scale===void0?this.scale:_ref6$scale,
          _ref6$rotation=_ref6.rotation,
          rotation=_ref6$rotation===void0?this.rotation:_ref6$rotation,
          _ref6$dontFlip=_ref6.dontFlip,
          dontFlip=_ref6$dontFlip===void0?false:_ref6$dontFlip;

      returnnewPageViewport({
        viewBox:this.viewBox.slice(),
        scale:scale,
        rotation:rotation,
        offsetX:this.offsetX,
        offsetY:this.offsetY,
        dontFlip:dontFlip
      });
    }
  },{
    key:"convertToViewportPoint",
    value:functionconvertToViewportPoint(x,y){
      return_util.Util.applyTransform([x,y],this.transform);
    }
  },{
    key:"convertToViewportRectangle",
    value:functionconvertToViewportRectangle(rect){
      vartopLeft=_util.Util.applyTransform([rect[0],rect[1]],this.transform);

      varbottomRight=_util.Util.applyTransform([rect[2],rect[3]],this.transform);

      return[topLeft[0],topLeft[1],bottomRight[0],bottomRight[1]];
    }
  },{
    key:"convertToPdfPoint",
    value:functionconvertToPdfPoint(x,y){
      return_util.Util.applyInverseTransform([x,y],this.transform);
    }
  }]);

  returnPageViewport;
}();

exports.PageViewport=PageViewport;

varRenderingCancelledException=functionRenderingCancelledException(){
  functionRenderingCancelledException(msg,type){
    this.message=msg;
    this.type=type;
  }

  RenderingCancelledException.prototype=newError();
  RenderingCancelledException.prototype.name='RenderingCancelledException';
  RenderingCancelledException.constructor=RenderingCancelledException;
  returnRenderingCancelledException;
}();

exports.RenderingCancelledException=RenderingCancelledException;
varLinkTarget={
  NONE:0,
  SELF:1,
  BLANK:2,
  PARENT:3,
  TOP:4
};
exports.LinkTarget=LinkTarget;
varLinkTargetStringMap=['','_self','_blank','_parent','_top'];

functionaddLinkAttributes(link){
  var_ref7=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{},
      url=_ref7.url,
      target=_ref7.target,
      rel=_ref7.rel;

  link.href=link.title=url?(0,_util.removeNullCharacters)(url):'';

  if(url){
    varLinkTargetValues=Object.values(LinkTarget);
    vartargetIndex=LinkTargetValues.includes(target)?target:LinkTarget.NONE;
    link.target=LinkTargetStringMap[targetIndex];
    link.rel=typeofrel==='string'?rel:DEFAULT_LINK_REL;
  }
}

functiongetFilenameFromUrl(url){
  varanchor=url.indexOf('#');
  varquery=url.indexOf('?');
  varend=Math.min(anchor>0?anchor:url.length,query>0?query:url.length);
  returnurl.substring(url.lastIndexOf('/',end)+1,end);
}

varStatTimer=
/*#__PURE__*/
function(){
  functionStatTimer(){
    varenable=arguments.length>0&&arguments[0]!==undefined?arguments[0]:true;

    _classCallCheck(this,StatTimer);

    this.enabled=!!enable;
    this.started=Object.create(null);
    this.times=[];
  }

  _createClass(StatTimer,[{
    key:"time",
    value:functiontime(name){
      if(!this.enabled){
        return;
      }

      if(nameinthis.started){
        (0,_util.warn)('Timerisalreadyrunningfor'+name);
      }

      this.started[name]=Date.now();
    }
  },{
    key:"timeEnd",
    value:functiontimeEnd(name){
      if(!this.enabled){
        return;
      }

      if(!(nameinthis.started)){
        (0,_util.warn)('Timerhasnotbeenstartedfor'+name);
      }

      this.times.push({
        'name':name,
        'start':this.started[name],
        'end':Date.now()
      });
      deletethis.started[name];
    }
  },{
    key:"toString",
    value:functiontoString(){
      varout='',
          longest=0;
      var_iteratorNormalCompletion=true;
      var_didIteratorError=false;
      var_iteratorError=undefined;

      try{
        for(var_iterator=this.times[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
          vartime=_step.value;
          varname=time.name;

          if(name.length>longest){
            longest=name.length;
          }
        }
      }catch(err){
        _didIteratorError=true;
        _iteratorError=err;
      }finally{
        try{
          if(!_iteratorNormalCompletion&&_iterator["return"]!=null){
            _iterator["return"]();
          }
        }finally{
          if(_didIteratorError){
            throw_iteratorError;
          }
        }
      }

      var_iteratorNormalCompletion2=true;
      var_didIteratorError2=false;
      var_iteratorError2=undefined;

      try{
        for(var_iterator2=this.times[Symbol.iterator](),_step2;!(_iteratorNormalCompletion2=(_step2=_iterator2.next()).done);_iteratorNormalCompletion2=true){
          var_time=_step2.value;
          varduration=_time.end-_time.start;
          out+="".concat(_time.name.padEnd(longest),"").concat(duration,"ms\n");
        }
      }catch(err){
        _didIteratorError2=true;
        _iteratorError2=err;
      }finally{
        try{
          if(!_iteratorNormalCompletion2&&_iterator2["return"]!=null){
            _iterator2["return"]();
          }
        }finally{
          if(_didIteratorError2){
            throw_iteratorError2;
          }
        }
      }

      returnout;
    }
  }]);

  returnStatTimer;
}();

exports.StatTimer=StatTimer;

varDummyStatTimer=
/*#__PURE__*/
function(){
  functionDummyStatTimer(){
    _classCallCheck(this,DummyStatTimer);

    (0,_util.unreachable)('CannotinitializeDummyStatTimer.');
  }

  _createClass(DummyStatTimer,null,[{
    key:"time",
    value:functiontime(name){}
  },{
    key:"timeEnd",
    value:functiontimeEnd(name){}
  },{
    key:"toString",
    value:functiontoString(){
      return'';
    }
  }]);

  returnDummyStatTimer;
}();

exports.DummyStatTimer=DummyStatTimer;

functionisFetchSupported(){
  returntypeoffetch!=='undefined'&&typeofResponse!=='undefined'&&'body'inResponse.prototype&&typeofReadableStream!=='undefined';
}

functionisValidFetchUrl(url,baseUrl){
  try{
    var_ref8=baseUrl?new_util.URL(url,baseUrl):new_util.URL(url),
        protocol=_ref8.protocol;

    returnprotocol==='http:'||protocol==='https:';
  }catch(ex){
    returnfalse;
  }
}

functionloadScript(src){
  returnnewPromise(function(resolve,reject){
    varscript=document.createElement('script');
    script.src=src;
    script.onload=resolve;

    script.onerror=function(){
      reject(newError("Cannotloadscriptat:".concat(script.src)));
    };

    (document.head||document.documentElement).appendChild(script);
  });
}

functiondeprecated(details){
  console.log('DeprecatedAPIusage:'+details);
}

functionreleaseImageResources(img){
  (0,_util.assert)(imginstanceofImage,'Invalid`img`parameter.');
  varurl=img.src;

  if(typeofurl==='string'&&url.startsWith('blob:')&&_util.URL.revokeObjectURL){
    _util.URL.revokeObjectURL(url);
  }

  img.removeAttribute('src');
}

varpdfDateStringRegex;

varPDFDateString=
/*#__PURE__*/
function(){
  functionPDFDateString(){
    _classCallCheck(this,PDFDateString);
  }

  _createClass(PDFDateString,null,[{
    key:"toDateObject",
    value:functiontoDateObject(input){
      if(!input||!(0,_util.isString)(input)){
        returnnull;
      }

      if(!pdfDateStringRegex){
        pdfDateStringRegex=newRegExp('^D:'+'(\\d{4})'+'(\\d{2})?'+'(\\d{2})?'+'(\\d{2})?'+'(\\d{2})?'+'(\\d{2})?'+'([Z|+|-])?'+'(\\d{2})?'+'\'?'+'(\\d{2})?'+'\'?');
      }

      varmatches=pdfDateStringRegex.exec(input);

      if(!matches){
        returnnull;
      }

      varyear=parseInt(matches[1],10);
      varmonth=parseInt(matches[2],10);
      month=month>=1&&month<=12?month-1:0;
      varday=parseInt(matches[3],10);
      day=day>=1&&day<=31?day:1;
      varhour=parseInt(matches[4],10);
      hour=hour>=0&&hour<=23?hour:0;
      varminute=parseInt(matches[5],10);
      minute=minute>=0&&minute<=59?minute:0;
      varsecond=parseInt(matches[6],10);
      second=second>=0&&second<=59?second:0;
      varuniversalTimeRelation=matches[7]||'Z';
      varoffsetHour=parseInt(matches[8],10);
      offsetHour=offsetHour>=0&&offsetHour<=23?offsetHour:0;
      varoffsetMinute=parseInt(matches[9],10)||0;
      offsetMinute=offsetMinute>=0&&offsetMinute<=59?offsetMinute:0;

      if(universalTimeRelation==='-'){
        hour+=offsetHour;
        minute+=offsetMinute;
      }elseif(universalTimeRelation==='+'){
        hour-=offsetHour;
        minute-=offsetMinute;
      }

      returnnewDate(Date.UTC(year,month,day,hour,minute,second));
    }
  }]);

  returnPDFDateString;
}();

exports.PDFDateString=PDFDateString;

/***/}),
/*152*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.FontLoader=exports.FontFaceObject=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varBaseFontLoader=
/*#__PURE__*/
function(){
  functionBaseFontLoader(_ref){
    vardocId=_ref.docId,
        onUnsupportedFeature=_ref.onUnsupportedFeature;

    _classCallCheck(this,BaseFontLoader);

    if(this.constructor===BaseFontLoader){
      (0,_util.unreachable)('CannotinitializeBaseFontLoader.');
    }

    this.docId=docId;
    this._onUnsupportedFeature=onUnsupportedFeature;
    this.nativeFontFaces=[];
    this.styleElement=null;
  }

  _createClass(BaseFontLoader,[{
    key:"addNativeFontFace",
    value:functionaddNativeFontFace(nativeFontFace){
      this.nativeFontFaces.push(nativeFontFace);
      document.fonts.add(nativeFontFace);
    }
  },{
    key:"insertRule",
    value:functioninsertRule(rule){
      varstyleElement=this.styleElement;

      if(!styleElement){
        styleElement=this.styleElement=document.createElement('style');
        styleElement.id="PDFJS_FONT_STYLE_TAG_".concat(this.docId);
        document.documentElement.getElementsByTagName('head')[0].appendChild(styleElement);
      }

      varstyleSheet=styleElement.sheet;
      styleSheet.insertRule(rule,styleSheet.cssRules.length);
    }
  },{
    key:"clear",
    value:functionclear(){
      this.nativeFontFaces.forEach(function(nativeFontFace){
        document.fonts["delete"](nativeFontFace);
      });
      this.nativeFontFaces.length=0;

      if(this.styleElement){
        this.styleElement.remove();
        this.styleElement=null;
      }
    }
  },{
    key:"bind",
    value:function(){
      var_bind=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(font){
        var_this=this;

        varnativeFontFace,rule;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                if(!(font.attached||font.missingFile)){
                  _context.next=2;
                  break;
                }

                return_context.abrupt("return",undefined);

              case2:
                font.attached=true;

                if(!this.isFontLoadingAPISupported){
                  _context.next=19;
                  break;
                }

                nativeFontFace=font.createNativeFontFace();

                if(!nativeFontFace){
                  _context.next=18;
                  break;
                }

                this.addNativeFontFace(nativeFontFace);
                _context.prev=7;
                _context.next=10;
                returnnativeFontFace.loaded;

              case10:
                _context.next=18;
                break;

              case12:
                _context.prev=12;
                _context.t0=_context["catch"](7);

                this._onUnsupportedFeature({
                  featureId:_util.UNSUPPORTED_FEATURES.font
                });

                (0,_util.warn)("Failedtoloadfont'".concat(nativeFontFace.family,"':'").concat(_context.t0,"'."));
                font.disableFontFace=true;
                throw_context.t0;

              case18:
                return_context.abrupt("return",undefined);

              case19:
                rule=font.createFontFaceRule();

                if(!rule){
                  _context.next=25;
                  break;
                }

                this.insertRule(rule);

                if(!this.isSyncFontLoadingSupported){
                  _context.next=24;
                  break;
                }

                return_context.abrupt("return",undefined);

              case24:
                return_context.abrupt("return",newPromise(function(resolve){
                  varrequest=_this._queueLoadingCallback(resolve);

                  _this._prepareFontLoadEvent([rule],[font],request);
                }));

              case25:
                return_context.abrupt("return",undefined);

              case26:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this,[[7,12]]);
      }));

      functionbind(_x){
        return_bind.apply(this,arguments);
      }

      returnbind;
    }()
  },{
    key:"_queueLoadingCallback",
    value:function_queueLoadingCallback(callback){
      (0,_util.unreachable)('Abstractmethod`_queueLoadingCallback`.');
    }
  },{
    key:"_prepareFontLoadEvent",
    value:function_prepareFontLoadEvent(rules,fontsToLoad,request){
      (0,_util.unreachable)('Abstractmethod`_prepareFontLoadEvent`.');
    }
  },{
    key:"isFontLoadingAPISupported",
    get:functionget(){
      (0,_util.unreachable)('Abstractmethod`isFontLoadingAPISupported`.');
    }
  },{
    key:"isSyncFontLoadingSupported",
    get:functionget(){
      (0,_util.unreachable)('Abstractmethod`isSyncFontLoadingSupported`.');
    }
  },{
    key:"_loadTestFont",
    get:functionget(){
      (0,_util.unreachable)('Abstractmethod`_loadTestFont`.');
    }
  }]);

  returnBaseFontLoader;
}();

varFontLoader;
exports.FontLoader=FontLoader;
{
  exports.FontLoader=FontLoader=
  /*#__PURE__*/
  function(_BaseFontLoader){
    _inherits(GenericFontLoader,_BaseFontLoader);

    functionGenericFontLoader(docId){
      var_this2;

      _classCallCheck(this,GenericFontLoader);

      _this2=_possibleConstructorReturn(this,_getPrototypeOf(GenericFontLoader).call(this,docId));
      _this2.loadingContext={
        requests:[],
        nextRequestId:0
      };
      _this2.loadTestFontId=0;
      return_this2;
    }

    _createClass(GenericFontLoader,[{
      key:"_queueLoadingCallback",
      value:function_queueLoadingCallback(callback){
        functioncompleteRequest(){
          (0,_util.assert)(!request.done,'completeRequest()cannotbecalledtwice.');
          request.done=true;

          while(context.requests.length>0&&context.requests[0].done){
            varotherRequest=context.requests.shift();
            setTimeout(otherRequest.callback,0);
          }
        }

        varcontext=this.loadingContext;
        varrequest={
          id:"pdfjs-font-loading-".concat(context.nextRequestId++),
          done:false,
          complete:completeRequest,
          callback:callback
        };
        context.requests.push(request);
        returnrequest;
      }
    },{
      key:"_prepareFontLoadEvent",
      value:function_prepareFontLoadEvent(rules,fonts,request){
        functionint32(data,offset){
          returndata.charCodeAt(offset)<<24|data.charCodeAt(offset+1)<<16|data.charCodeAt(offset+2)<<8|data.charCodeAt(offset+3)&0xff;
        }

        functionspliceString(s,offset,remove,insert){
          varchunk1=s.substring(0,offset);
          varchunk2=s.substring(offset+remove);
          returnchunk1+insert+chunk2;
        }

        vari,ii;
        varcanvas=document.createElement('canvas');
        canvas.width=1;
        canvas.height=1;
        varctx=canvas.getContext('2d');
        varcalled=0;

        functionisFontReady(name,callback){
          called++;

          if(called>30){
            (0,_util.warn)('Loadtestfontneverloaded.');
            callback();
            return;
          }

          ctx.font='30px'+name;
          ctx.fillText('.',0,20);
          varimageData=ctx.getImageData(0,0,1,1);

          if(imageData.data[3]>0){
            callback();
            return;
          }

          setTimeout(isFontReady.bind(null,name,callback));
        }

        varloadTestFontId="lt".concat(Date.now()).concat(this.loadTestFontId++);
        vardata=this._loadTestFont;
        varCOMMENT_OFFSET=976;
        data=spliceString(data,COMMENT_OFFSET,loadTestFontId.length,loadTestFontId);
        varCFF_CHECKSUM_OFFSET=16;
        varXXXX_VALUE=0x58585858;
        varchecksum=int32(data,CFF_CHECKSUM_OFFSET);

        for(i=0,ii=loadTestFontId.length-3;i<ii;i+=4){
          checksum=checksum-XXXX_VALUE+int32(loadTestFontId,i)|0;
        }

        if(i<loadTestFontId.length){
          checksum=checksum-XXXX_VALUE+int32(loadTestFontId+'XXX',i)|0;
        }

        data=spliceString(data,CFF_CHECKSUM_OFFSET,4,(0,_util.string32)(checksum));
        varurl="url(data:font/opentype;base64,".concat(btoa(data),");");
        varrule="@font-face{font-family:\"".concat(loadTestFontId,"\";src:").concat(url,"}");
        this.insertRule(rule);
        varnames=[];

        for(i=0,ii=fonts.length;i<ii;i++){
          names.push(fonts[i].loadedName);
        }

        names.push(loadTestFontId);
        vardiv=document.createElement('div');
        div.setAttribute('style','visibility:hidden;'+'width:10px;height:10px;'+'position:absolute;top:0px;left:0px;');

        for(i=0,ii=names.length;i<ii;++i){
          varspan=document.createElement('span');
          span.textContent='Hi';
          span.style.fontFamily=names[i];
          div.appendChild(span);
        }

        document.body.appendChild(div);
        isFontReady(loadTestFontId,function(){
          document.body.removeChild(div);
          request.complete();
        });
      }
    },{
      key:"isFontLoadingAPISupported",
      get:functionget(){
        varsupported=typeofdocument!=='undefined'&&!!document.fonts;

        if(supported&&typeofnavigator!=='undefined'){
          varm=/Mozilla\/5.0.*?rv:(\d+).*?Gecko/.exec(navigator.userAgent);

          if(m&&m[1]<63){
            supported=false;
          }
        }

        return(0,_util.shadow)(this,'isFontLoadingAPISupported',supported);
      }
    },{
      key:"isSyncFontLoadingSupported",
      get:functionget(){
        varsupported=false;

        if(typeofnavigator==='undefined'){
          supported=true;
        }else{
          varm=/Mozilla\/5.0.*?rv:(\d+).*?Gecko/.exec(navigator.userAgent);

          if(m&&m[1]>=14){
            supported=true;
          }
        }

        return(0,_util.shadow)(this,'isSyncFontLoadingSupported',supported);
      }
    },{
      key:"_loadTestFont",
      get:functionget(){
        vargetLoadTestFont=functiongetLoadTestFont(){
          returnatob('T1RUTwALAIAAAwAwQ0ZGIDHtZg4AAAOYAAAAgUZGVE1lkzZwAAAEHAAAABxHREVGABQA'+'FQAABDgAAAAeT1MvMlYNYwkAAAEgAAAAYGNtYXABDQLUAAACNAAAAUJoZWFk/xVFDQAA'+'ALwAAAA2aGhlYQdkA+oAAAD0AAAAJGhtdHgD6AAAAAAEWAAAAAZtYXhwAAJQAAAAARgA'+'AAAGbmFtZVjmdH4AAAGAAAAAsXBvc3T/hgAzAAADeAAAACAAAQAAAAEAALZRFsRfDzz1'+'AAsD6AAAAADOBOTLAAAAAM4KHDwAAAAAA+gDIQAAAAgAAgAAAAAAAAABAAADIQAAAFoD'+'6AAAAAAD6AABAAAAAAAAAAAAAAAAAAAAAQAAUAAAAgAAAAQD6AH0AAUAAAKKArwAAACM'+'AooCvAAAAeAAMQECAAACAAYJAAAAAAAAAAAAAQAAAAAAAAAAAAAAAFBmRWQAwAAuAC4D'+'IP84AFoDIQAAAAAAAQAAAAAAAAAAACAAIAABAAAADgCuAAEAAAAAAAAAAQAAAAEAAAAA'+'AAEAAQAAAAEAAAAAAAIAAQAAAAEAAAAAAAMAAQAAAAEAAAAAAAQAAQAAAAEAAAAAAAUA'+'AQAAAAEAAAAAAAYAAQAAAAMAAQQJAAAAAgABAAMAAQQJAAEAAgABAAMAAQQJAAIAAgAB'+'AAMAAQQJAAMAAgABAAMAAQQJAAQAAgABAAMAAQQJAAUAAgABAAMAAQQJAAYAAgABWABY'+'AAAAAAAAAwAAAAMAAAAcAAEAAAAAADwAAwABAAAAHAAEACAAAAAEAAQAAQAAAC7//wAA'+'AC7////TAAEAAAAAAAABBgAAAQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+'AAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'+'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAMAAAAAAAD/gwAyAAAAAQAAAAAAAAAAAAAAAAAA'+'AAABAAQEAAEBAQJYAAEBASH4DwD4GwHEAvgcA/gXBIwMAYuL+nz5tQXkD5j3CBLnEQAC'+'AQEBIVhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYAAABAQAADwACAQEEE/t3'+'Dov6fAH6fAT+fPp8+nwHDosMCvm1Cvm1DAz6fBQAAAAAAAABAAAAAMmJbzEAAAAAzgTj'+'FQAAAADOBOQpAAEAAAAAAAAADAAUAAQAAAABAAAAAgABAAAAAAAAAAAD6AAAAAAAAA==');
        };

        return(0,_util.shadow)(this,'_loadTestFont',getLoadTestFont());
      }
    }]);

    returnGenericFontLoader;
  }(BaseFontLoader);
}
varIsEvalSupportedCached={
  getvalue(){
    return(0,_util.shadow)(this,'value',(0,_util.isEvalSupported)());
  }

};

varFontFaceObject=
/*#__PURE__*/
function(){
  functionFontFaceObject(translatedData,_ref2){
    var_ref2$isEvalSupported=_ref2.isEvalSupported,
        isEvalSupported=_ref2$isEvalSupported===void0?true:_ref2$isEvalSupported,
        _ref2$disableFontFace=_ref2.disableFontFace,
        disableFontFace=_ref2$disableFontFace===void0?false:_ref2$disableFontFace,
        _ref2$ignoreErrors=_ref2.ignoreErrors,
        ignoreErrors=_ref2$ignoreErrors===void0?false:_ref2$ignoreErrors,
        _ref2$onUnsupportedFe=_ref2.onUnsupportedFeature,
        onUnsupportedFeature=_ref2$onUnsupportedFe===void0?null:_ref2$onUnsupportedFe,
        _ref2$fontRegistry=_ref2.fontRegistry,
        fontRegistry=_ref2$fontRegistry===void0?null:_ref2$fontRegistry;

    _classCallCheck(this,FontFaceObject);

    this.compiledGlyphs=Object.create(null);

    for(variintranslatedData){
      this[i]=translatedData[i];
    }

    this.isEvalSupported=isEvalSupported!==false;
    this.disableFontFace=disableFontFace===true;
    this.ignoreErrors=ignoreErrors===true;
    this._onUnsupportedFeature=onUnsupportedFeature;
    this.fontRegistry=fontRegistry;
  }

  _createClass(FontFaceObject,[{
    key:"createNativeFontFace",
    value:functioncreateNativeFontFace(){
      if(!this.data||this.disableFontFace){
        returnnull;
      }

      varnativeFontFace=newFontFace(this.loadedName,this.data,{});

      if(this.fontRegistry){
        this.fontRegistry.registerFont(this);
      }

      returnnativeFontFace;
    }
  },{
    key:"createFontFaceRule",
    value:functioncreateFontFaceRule(){
      if(!this.data||this.disableFontFace){
        returnnull;
      }

      vardata=(0,_util.bytesToString)(newUint8Array(this.data));
      varurl="url(data:".concat(this.mimetype,";base64,").concat(btoa(data),");");
      varrule="@font-face{font-family:\"".concat(this.loadedName,"\";src:").concat(url,"}");

      if(this.fontRegistry){
        this.fontRegistry.registerFont(this,url);
      }

      returnrule;
    }
  },{
    key:"getPathGenerator",
    value:functiongetPathGenerator(objs,character){
      if(this.compiledGlyphs[character]!==undefined){
        returnthis.compiledGlyphs[character];
      }

      varcmds,current;

      try{
        cmds=objs.get(this.loadedName+'_path_'+character);
      }catch(ex){
        if(!this.ignoreErrors){
          throwex;
        }

        if(this._onUnsupportedFeature){
          this._onUnsupportedFeature({
            featureId:_util.UNSUPPORTED_FEATURES.font
          });
        }

        (0,_util.warn)("getPathGenerator-ignoringcharacter:\"".concat(ex,"\"."));
        returnthis.compiledGlyphs[character]=function(c,size){};
      }

      if(this.isEvalSupported&&IsEvalSupportedCached.value){
        varargs,
            js='';

        for(vari=0,ii=cmds.length;i<ii;i++){
          current=cmds[i];

          if(current.args!==undefined){
            args=current.args.join(',');
          }else{
            args='';
          }

          js+='c.'+current.cmd+'('+args+');\n';
        }

        returnthis.compiledGlyphs[character]=newFunction('c','size',js);
      }

      returnthis.compiledGlyphs[character]=function(c,size){
        for(var_i=0,_ii=cmds.length;_i<_ii;_i++){
          current=cmds[_i];

          if(current.cmd==='scale'){
            current.args=[size,-size];
          }

          c[current.cmd].apply(c,current.args);
        }
      };
    }
  }]);

  returnFontFaceObject;
}();

exports.FontFaceObject=FontFaceObject;

/***/}),
/*153*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


varcompatibilityParams=Object.create(null);
{
  varisNodeJS=__w_pdfjs_require__(4);

  varuserAgent=typeofnavigator!=='undefined'&&navigator.userAgent||'';
  varisIE=/Trident/.test(userAgent);
  varisIOSChrome=/CriOS/.test(userAgent);

  (functioncheckOnBlobSupport(){
    if(isIE||isIOSChrome){
      compatibilityParams.disableCreateObjectURL=true;
    }
  })();

  (functioncheckFontFaceAndImage(){
    if(isNodeJS()){
      compatibilityParams.disableFontFace=true;
      compatibilityParams.nativeImageDecoderSupport='none';
    }
  })();
}
exports.apiCompatibilityParams=Object.freeze(compatibilityParams);

/***/}),
/*154*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.CanvasGraphics=void0;

var_util=__w_pdfjs_require__(1);

var_pattern_helper=__w_pdfjs_require__(155);

varMIN_FONT_SIZE=16;
varMAX_FONT_SIZE=100;
varMAX_GROUP_SIZE=4096;
varMIN_WIDTH_FACTOR=0.65;
varCOMPILE_TYPE3_GLYPHS=true;
varMAX_SIZE_TO_COMPILE=1000;
varFULL_CHUNK_HEIGHT=16;
varIsLittleEndianCached={
  getvalue(){
    return(0,_util.shadow)(IsLittleEndianCached,'value',(0,_util.isLittleEndian)());
  }

};

functionaddContextCurrentTransform(ctx){
  if(!ctx.mozCurrentTransform){
    ctx._originalSave=ctx.save;
    ctx._originalRestore=ctx.restore;
    ctx._originalRotate=ctx.rotate;
    ctx._originalScale=ctx.scale;
    ctx._originalTranslate=ctx.translate;
    ctx._originalTransform=ctx.transform;
    ctx._originalSetTransform=ctx.setTransform;
    ctx._transformMatrix=ctx._transformMatrix||[1,0,0,1,0,0];
    ctx._transformStack=[];
    Object.defineProperty(ctx,'mozCurrentTransform',{
      get:functiongetCurrentTransform(){
        returnthis._transformMatrix;
      }
    });
    Object.defineProperty(ctx,'mozCurrentTransformInverse',{
      get:functiongetCurrentTransformInverse(){
        varm=this._transformMatrix;
        vara=m[0],
            b=m[1],
            c=m[2],
            d=m[3],
            e=m[4],
            f=m[5];
        varad_bc=a*d-b*c;
        varbc_ad=b*c-a*d;
        return[d/ad_bc,b/bc_ad,c/bc_ad,a/ad_bc,(d*e-c*f)/bc_ad,(b*e-a*f)/ad_bc];
      }
    });

    ctx.save=functionctxSave(){
      varold=this._transformMatrix;

      this._transformStack.push(old);

      this._transformMatrix=old.slice(0,6);

      this._originalSave();
    };

    ctx.restore=functionctxRestore(){
      varprev=this._transformStack.pop();

      if(prev){
        this._transformMatrix=prev;

        this._originalRestore();
      }
    };

    ctx.translate=functionctxTranslate(x,y){
      varm=this._transformMatrix;
      m[4]=m[0]*x+m[2]*y+m[4];
      m[5]=m[1]*x+m[3]*y+m[5];

      this._originalTranslate(x,y);
    };

    ctx.scale=functionctxScale(x,y){
      varm=this._transformMatrix;
      m[0]=m[0]*x;
      m[1]=m[1]*x;
      m[2]=m[2]*y;
      m[3]=m[3]*y;

      this._originalScale(x,y);
    };

    ctx.transform=functionctxTransform(a,b,c,d,e,f){
      varm=this._transformMatrix;
      this._transformMatrix=[m[0]*a+m[2]*b,m[1]*a+m[3]*b,m[0]*c+m[2]*d,m[1]*c+m[3]*d,m[0]*e+m[2]*f+m[4],m[1]*e+m[3]*f+m[5]];

      ctx._originalTransform(a,b,c,d,e,f);
    };

    ctx.setTransform=functionctxSetTransform(a,b,c,d,e,f){
      this._transformMatrix=[a,b,c,d,e,f];

      ctx._originalSetTransform(a,b,c,d,e,f);
    };

    ctx.rotate=functionctxRotate(angle){
      varcosValue=Math.cos(angle);
      varsinValue=Math.sin(angle);
      varm=this._transformMatrix;
      this._transformMatrix=[m[0]*cosValue+m[2]*sinValue,m[1]*cosValue+m[3]*sinValue,m[0]*-sinValue+m[2]*cosValue,m[1]*-sinValue+m[3]*cosValue,m[4],m[5]];

      this._originalRotate(angle);
    };
  }
}

varCachedCanvases=functionCachedCanvasesClosure(){
  functionCachedCanvases(canvasFactory){
    this.canvasFactory=canvasFactory;
    this.cache=Object.create(null);
  }

  CachedCanvases.prototype={
    getCanvas:functionCachedCanvases_getCanvas(id,width,height,trackTransform){
      varcanvasEntry;

      if(this.cache[id]!==undefined){
        canvasEntry=this.cache[id];
        this.canvasFactory.reset(canvasEntry,width,height);
        canvasEntry.context.setTransform(1,0,0,1,0,0);
      }else{
        canvasEntry=this.canvasFactory.create(width,height);
        this.cache[id]=canvasEntry;
      }

      if(trackTransform){
        addContextCurrentTransform(canvasEntry.context);
      }

      returncanvasEntry;
    },
    clear:functionclear(){
      for(varidinthis.cache){
        varcanvasEntry=this.cache[id];
        this.canvasFactory.destroy(canvasEntry);
        deletethis.cache[id];
      }
    }
  };
  returnCachedCanvases;
}();

functioncompileType3Glyph(imgData){
  varPOINT_TO_PROCESS_LIMIT=1000;
  varwidth=imgData.width,
      height=imgData.height;
  vari,
      j,
      j0,
      width1=width+1;
  varpoints=newUint8Array(width1*(height+1));
  varPOINT_TYPES=newUint8Array([0,2,4,0,1,0,5,4,8,10,0,8,0,2,1,0]);
  varlineSize=width+7&~7,
      data0=imgData.data;
  vardata=newUint8Array(lineSize*height),
      pos=0,
      ii;

  for(i=0,ii=data0.length;i<ii;i++){
    varmask=128,
        elem=data0[i];

    while(mask>0){
      data[pos++]=elem&mask?0:255;
      mask>>=1;
    }
  }

  varcount=0;
  pos=0;

  if(data[pos]!==0){
    points[0]=1;
    ++count;
  }

  for(j=1;j<width;j++){
    if(data[pos]!==data[pos+1]){
      points[j]=data[pos]?2:1;
      ++count;
    }

    pos++;
  }

  if(data[pos]!==0){
    points[j]=2;
    ++count;
  }

  for(i=1;i<height;i++){
    pos=i*lineSize;
    j0=i*width1;

    if(data[pos-lineSize]!==data[pos]){
      points[j0]=data[pos]?1:8;
      ++count;
    }

    varsum=(data[pos]?4:0)+(data[pos-lineSize]?8:0);

    for(j=1;j<width;j++){
      sum=(sum>>2)+(data[pos+1]?4:0)+(data[pos-lineSize+1]?8:0);

      if(POINT_TYPES[sum]){
        points[j0+j]=POINT_TYPES[sum];
        ++count;
      }

      pos++;
    }

    if(data[pos-lineSize]!==data[pos]){
      points[j0+j]=data[pos]?2:4;
      ++count;
    }

    if(count>POINT_TO_PROCESS_LIMIT){
      returnnull;
    }
  }

  pos=lineSize*(height-1);
  j0=i*width1;

  if(data[pos]!==0){
    points[j0]=8;
    ++count;
  }

  for(j=1;j<width;j++){
    if(data[pos]!==data[pos+1]){
      points[j0+j]=data[pos]?4:8;
      ++count;
    }

    pos++;
  }

  if(data[pos]!==0){
    points[j0+j]=4;
    ++count;
  }

  if(count>POINT_TO_PROCESS_LIMIT){
    returnnull;
  }

  varsteps=newInt32Array([0,width1,-1,0,-width1,0,0,0,1]);
  varoutlines=[];

  for(i=0;count&&i<=height;i++){
    varp=i*width1;
    varend=p+width;

    while(p<end&&!points[p]){
      p++;
    }

    if(p===end){
      continue;
    }

    varcoords=[p%width1,i];
    vartype=points[p],
        p0=p,
        pp;

    do{
      varstep=steps[type];

      do{
        p+=step;
      }while(!points[p]);

      pp=points[p];

      if(pp!==5&&pp!==10){
        type=pp;
        points[p]=0;
      }else{
        type=pp&0x33*type>>4;
        points[p]&=type>>2|type<<2;
      }

      coords.push(p%width1);
      coords.push(p/width1|0);

      if(!points[p]){
        --count;
      }
    }while(p0!==p);

    outlines.push(coords);
    --i;
  }

  vardrawOutline=functiondrawOutline(c){
    c.save();
    c.scale(1/width,-1/height);
    c.translate(0,-height);
    c.beginPath();

    for(vari=0,ii=outlines.length;i<ii;i++){
      varo=outlines[i];
      c.moveTo(o[0],o[1]);

      for(varj=2,jj=o.length;j<jj;j+=2){
        c.lineTo(o[j],o[j+1]);
      }
    }

    c.fill();
    c.beginPath();
    c.restore();
  };

  returndrawOutline;
}

varCanvasExtraState=functionCanvasExtraStateClosure(){
  functionCanvasExtraState(){
    this.alphaIsShape=false;
    this.fontSize=0;
    this.fontSizeScale=1;
    this.textMatrix=_util.IDENTITY_MATRIX;
    this.textMatrixScale=1;
    this.fontMatrix=_util.FONT_IDENTITY_MATRIX;
    this.leading=0;
    this.x=0;
    this.y=0;
    this.lineX=0;
    this.lineY=0;
    this.charSpacing=0;
    this.wordSpacing=0;
    this.textHScale=1;
    this.textRenderingMode=_util.TextRenderingMode.FILL;
    this.textRise=0;
    this.fillColor='#000000';
    this.strokeColor='#000000';
    this.patternFill=false;
    this.fillAlpha=1;
    this.strokeAlpha=1;
    this.lineWidth=1;
    this.activeSMask=null;
    this.resumeSMaskCtx=null;
  }

  CanvasExtraState.prototype={
    clone:functionCanvasExtraState_clone(){
      returnObject.create(this);
    },
    setCurrentPoint:functionCanvasExtraState_setCurrentPoint(x,y){
      this.x=x;
      this.y=y;
    }
  };
  returnCanvasExtraState;
}();

varCanvasGraphics=functionCanvasGraphicsClosure(){
  varEXECUTION_TIME=15;
  varEXECUTION_STEPS=10;

  functionCanvasGraphics(canvasCtx,commonObjs,objs,canvasFactory,webGLContext,imageLayer){
    this.ctx=canvasCtx;
    this.current=newCanvasExtraState();
    this.stateStack=[];
    this.pendingClip=null;
    this.pendingEOFill=false;
    this.res=null;
    this.xobjs=null;
    this.commonObjs=commonObjs;
    this.objs=objs;
    this.canvasFactory=canvasFactory;
    this.webGLContext=webGLContext;
    this.imageLayer=imageLayer;
    this.groupStack=[];
    this.processingType3=null;
    this.baseTransform=null;
    this.baseTransformStack=[];
    this.groupLevel=0;
    this.smaskStack=[];
    this.smaskCounter=0;
    this.tempSMask=null;
    this.cachedCanvases=newCachedCanvases(this.canvasFactory);

    if(canvasCtx){
      addContextCurrentTransform(canvasCtx);
    }

    this._cachedGetSinglePixelWidth=null;
  }

  functionputBinaryImageData(ctx,imgData){
    if(typeofImageData!=='undefined'&&imgDatainstanceofImageData){
      ctx.putImageData(imgData,0,0);
      return;
    }

    varheight=imgData.height,
        width=imgData.width;
    varpartialChunkHeight=height%FULL_CHUNK_HEIGHT;
    varfullChunks=(height-partialChunkHeight)/FULL_CHUNK_HEIGHT;
    vartotalChunks=partialChunkHeight===0?fullChunks:fullChunks+1;
    varchunkImgData=ctx.createImageData(width,FULL_CHUNK_HEIGHT);
    varsrcPos=0,
        destPos;
    varsrc=imgData.data;
    vardest=chunkImgData.data;
    vari,j,thisChunkHeight,elemsInThisChunk;

    if(imgData.kind===_util.ImageKind.GRAYSCALE_1BPP){
      varsrcLength=src.byteLength;
      vardest32=newUint32Array(dest.buffer,0,dest.byteLength>>2);
      vardest32DataLength=dest32.length;
      varfullSrcDiff=width+7>>3;
      varwhite=0xFFFFFFFF;
      varblack=IsLittleEndianCached.value?0xFF000000:0x000000FF;

      for(i=0;i<totalChunks;i++){
        thisChunkHeight=i<fullChunks?FULL_CHUNK_HEIGHT:partialChunkHeight;
        destPos=0;

        for(j=0;j<thisChunkHeight;j++){
          varsrcDiff=srcLength-srcPos;
          vark=0;
          varkEnd=srcDiff>fullSrcDiff?width:srcDiff*8-7;
          varkEndUnrolled=kEnd&~7;
          varmask=0;
          varsrcByte=0;

          for(;k<kEndUnrolled;k+=8){
            srcByte=src[srcPos++];
            dest32[destPos++]=srcByte&128?white:black;
            dest32[destPos++]=srcByte&64?white:black;
            dest32[destPos++]=srcByte&32?white:black;
            dest32[destPos++]=srcByte&16?white:black;
            dest32[destPos++]=srcByte&8?white:black;
            dest32[destPos++]=srcByte&4?white:black;
            dest32[destPos++]=srcByte&2?white:black;
            dest32[destPos++]=srcByte&1?white:black;
          }

          for(;k<kEnd;k++){
            if(mask===0){
              srcByte=src[srcPos++];
              mask=128;
            }

            dest32[destPos++]=srcByte&mask?white:black;
            mask>>=1;
          }
        }

        while(destPos<dest32DataLength){
          dest32[destPos++]=0;
        }

        ctx.putImageData(chunkImgData,0,i*FULL_CHUNK_HEIGHT);
      }
    }elseif(imgData.kind===_util.ImageKind.RGBA_32BPP){
      j=0;
      elemsInThisChunk=width*FULL_CHUNK_HEIGHT*4;

      for(i=0;i<fullChunks;i++){
        dest.set(src.subarray(srcPos,srcPos+elemsInThisChunk));
        srcPos+=elemsInThisChunk;
        ctx.putImageData(chunkImgData,0,j);
        j+=FULL_CHUNK_HEIGHT;
      }

      if(i<totalChunks){
        elemsInThisChunk=width*partialChunkHeight*4;
        dest.set(src.subarray(srcPos,srcPos+elemsInThisChunk));
        ctx.putImageData(chunkImgData,0,j);
      }
    }elseif(imgData.kind===_util.ImageKind.RGB_24BPP){
      thisChunkHeight=FULL_CHUNK_HEIGHT;
      elemsInThisChunk=width*thisChunkHeight;

      for(i=0;i<totalChunks;i++){
        if(i>=fullChunks){
          thisChunkHeight=partialChunkHeight;
          elemsInThisChunk=width*thisChunkHeight;
        }

        destPos=0;

        for(j=elemsInThisChunk;j--;){
          dest[destPos++]=src[srcPos++];
          dest[destPos++]=src[srcPos++];
          dest[destPos++]=src[srcPos++];
          dest[destPos++]=255;
        }

        ctx.putImageData(chunkImgData,0,i*FULL_CHUNK_HEIGHT);
      }
    }else{
      thrownewError("badimagekind:".concat(imgData.kind));
    }
  }

  functionputBinaryImageMask(ctx,imgData){
    varheight=imgData.height,
        width=imgData.width;
    varpartialChunkHeight=height%FULL_CHUNK_HEIGHT;
    varfullChunks=(height-partialChunkHeight)/FULL_CHUNK_HEIGHT;
    vartotalChunks=partialChunkHeight===0?fullChunks:fullChunks+1;
    varchunkImgData=ctx.createImageData(width,FULL_CHUNK_HEIGHT);
    varsrcPos=0;
    varsrc=imgData.data;
    vardest=chunkImgData.data;

    for(vari=0;i<totalChunks;i++){
      varthisChunkHeight=i<fullChunks?FULL_CHUNK_HEIGHT:partialChunkHeight;
      vardestPos=3;

      for(varj=0;j<thisChunkHeight;j++){
        varmask=0;

        for(vark=0;k<width;k++){
          if(!mask){
            varelem=src[srcPos++];
            mask=128;
          }

          dest[destPos]=elem&mask?0:255;
          destPos+=4;
          mask>>=1;
        }
      }

      ctx.putImageData(chunkImgData,0,i*FULL_CHUNK_HEIGHT);
    }
  }

  functioncopyCtxState(sourceCtx,destCtx){
    varproperties=['strokeStyle','fillStyle','fillRule','globalAlpha','lineWidth','lineCap','lineJoin','miterLimit','globalCompositeOperation','font'];

    for(vari=0,ii=properties.length;i<ii;i++){
      varproperty=properties[i];

      if(sourceCtx[property]!==undefined){
        destCtx[property]=sourceCtx[property];
      }
    }

    if(sourceCtx.setLineDash!==undefined){
      destCtx.setLineDash(sourceCtx.getLineDash());
      destCtx.lineDashOffset=sourceCtx.lineDashOffset;
    }
  }

  functionresetCtxToDefault(ctx){
    ctx.strokeStyle='#000000';
    ctx.fillStyle='#000000';
    ctx.fillRule='nonzero';
    ctx.globalAlpha=1;
    ctx.lineWidth=1;
    ctx.lineCap='butt';
    ctx.lineJoin='miter';
    ctx.miterLimit=10;
    ctx.globalCompositeOperation='source-over';
    ctx.font='10pxsans-serif';

    if(ctx.setLineDash!==undefined){
      ctx.setLineDash([]);
      ctx.lineDashOffset=0;
    }
  }

  functioncomposeSMaskBackdrop(bytes,r0,g0,b0){
    varlength=bytes.length;

    for(vari=3;i<length;i+=4){
      varalpha=bytes[i];

      if(alpha===0){
        bytes[i-3]=r0;
        bytes[i-2]=g0;
        bytes[i-1]=b0;
      }elseif(alpha<255){
        varalpha_=255-alpha;
        bytes[i-3]=bytes[i-3]*alpha+r0*alpha_>>8;
        bytes[i-2]=bytes[i-2]*alpha+g0*alpha_>>8;
        bytes[i-1]=bytes[i-1]*alpha+b0*alpha_>>8;
      }
    }
  }

  functioncomposeSMaskAlpha(maskData,layerData,transferMap){
    varlength=maskData.length;
    varscale=1/255;

    for(vari=3;i<length;i+=4){
      varalpha=transferMap?transferMap[maskData[i]]:maskData[i];
      layerData[i]=layerData[i]*alpha*scale|0;
    }
  }

  functioncomposeSMaskLuminosity(maskData,layerData,transferMap){
    varlength=maskData.length;

    for(vari=3;i<length;i+=4){
      vary=maskData[i-3]*77+maskData[i-2]*152+maskData[i-1]*28;
      layerData[i]=transferMap?layerData[i]*transferMap[y>>8]>>8:layerData[i]*y>>16;
    }
  }

  functiongenericComposeSMask(maskCtx,layerCtx,width,height,subtype,backdrop,transferMap){
    varhasBackdrop=!!backdrop;
    varr0=hasBackdrop?backdrop[0]:0;
    varg0=hasBackdrop?backdrop[1]:0;
    varb0=hasBackdrop?backdrop[2]:0;
    varcomposeFn;

    if(subtype==='Luminosity'){
      composeFn=composeSMaskLuminosity;
    }else{
      composeFn=composeSMaskAlpha;
    }

    varPIXELS_TO_PROCESS=1048576;
    varchunkSize=Math.min(height,Math.ceil(PIXELS_TO_PROCESS/width));

    for(varrow=0;row<height;row+=chunkSize){
      varchunkHeight=Math.min(chunkSize,height-row);
      varmaskData=maskCtx.getImageData(0,row,width,chunkHeight);
      varlayerData=layerCtx.getImageData(0,row,width,chunkHeight);

      if(hasBackdrop){
        composeSMaskBackdrop(maskData.data,r0,g0,b0);
      }

      composeFn(maskData.data,layerData.data,transferMap);
      maskCtx.putImageData(layerData,0,row);
    }
  }

  functioncomposeSMask(ctx,smask,layerCtx,webGLContext){
    varmask=smask.canvas;
    varmaskCtx=smask.context;
    ctx.setTransform(smask.scaleX,0,0,smask.scaleY,smask.offsetX,smask.offsetY);
    varbackdrop=smask.backdrop||null;

    if(!smask.transferMap&&webGLContext.isEnabled){
      varcomposed=webGLContext.composeSMask({
        layer:layerCtx.canvas,
        mask:mask,
        properties:{
          subtype:smask.subtype,
          backdrop:backdrop
        }
      });
      ctx.setTransform(1,0,0,1,0,0);
      ctx.drawImage(composed,smask.offsetX,smask.offsetY);
      return;
    }

    genericComposeSMask(maskCtx,layerCtx,mask.width,mask.height,smask.subtype,backdrop,smask.transferMap);
    ctx.drawImage(mask,0,0);
  }

  varLINE_CAP_STYLES=['butt','round','square'];
  varLINE_JOIN_STYLES=['miter','round','bevel'];
  varNORMAL_CLIP={};
  varEO_CLIP={};
  CanvasGraphics.prototype={
    beginDrawing:functionbeginDrawing(_ref){
      vartransform=_ref.transform,
          viewport=_ref.viewport,
          _ref$transparency=_ref.transparency,
          transparency=_ref$transparency===void0?false:_ref$transparency,
          _ref$background=_ref.background,
          background=_ref$background===void0?null:_ref$background;
      varwidth=this.ctx.canvas.width;
      varheight=this.ctx.canvas.height;
      this.ctx.save();
      this.ctx.fillStyle=background||'rgb(255,255,255)';
      this.ctx.fillRect(0,0,width,height);
      this.ctx.restore();

      if(transparency){
        vartransparentCanvas=this.cachedCanvases.getCanvas('transparent',width,height,true);
        this.compositeCtx=this.ctx;
        this.transparentCanvas=transparentCanvas.canvas;
        this.ctx=transparentCanvas.context;
        this.ctx.save();
        this.ctx.transform.apply(this.ctx,this.compositeCtx.mozCurrentTransform);
      }

      this.ctx.save();
      resetCtxToDefault(this.ctx);

      if(transform){
        this.ctx.transform.apply(this.ctx,transform);
      }

      this.ctx.transform.apply(this.ctx,viewport.transform);
      this.baseTransform=this.ctx.mozCurrentTransform.slice();

      if(this.imageLayer){
        this.imageLayer.beginLayout();
      }
    },
    executeOperatorList:functionCanvasGraphics_executeOperatorList(operatorList,executionStartIdx,continueCallback,stepper){
      varargsArray=operatorList.argsArray;
      varfnArray=operatorList.fnArray;
      vari=executionStartIdx||0;
      varargsArrayLen=argsArray.length;

      if(argsArrayLen===i){
        returni;
      }

      varchunkOperations=argsArrayLen-i>EXECUTION_STEPS&&typeofcontinueCallback==='function';
      varendTime=chunkOperations?Date.now()+EXECUTION_TIME:0;
      varsteps=0;
      varcommonObjs=this.commonObjs;
      varobjs=this.objs;
      varfnId;

      while(true){
        if(stepper!==undefined&&i===stepper.nextBreakPoint){
          stepper.breakIt(i,continueCallback);
          returni;
        }

        fnId=fnArray[i];

        if(fnId!==_util.OPS.dependency){
          this[fnId].apply(this,argsArray[i]);
        }else{
          var_iteratorNormalCompletion=true;
          var_didIteratorError=false;
          var_iteratorError=undefined;

          try{
            for(var_iterator=argsArray[i][Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
              vardepObjId=_step.value;
              varobjsPool=depObjId.startsWith('g_')?commonObjs:objs;

              if(!objsPool.has(depObjId)){
                objsPool.get(depObjId,continueCallback);
                returni;
              }
            }
          }catch(err){
            _didIteratorError=true;
            _iteratorError=err;
          }finally{
            try{
              if(!_iteratorNormalCompletion&&_iterator["return"]!=null){
                _iterator["return"]();
              }
            }finally{
              if(_didIteratorError){
                throw_iteratorError;
              }
            }
          }
        }

        i++;

        if(i===argsArrayLen){
          returni;
        }

        if(chunkOperations&&++steps>EXECUTION_STEPS){
          if(Date.now()>endTime){
            continueCallback();
            returni;
          }

          steps=0;
        }
      }
    },
    endDrawing:functionCanvasGraphics_endDrawing(){
      if(this.current.activeSMask!==null){
        this.endSMaskGroup();
      }

      this.ctx.restore();

      if(this.transparentCanvas){
        this.ctx=this.compositeCtx;
        this.ctx.save();
        this.ctx.setTransform(1,0,0,1,0,0);
        this.ctx.drawImage(this.transparentCanvas,0,0);
        this.ctx.restore();
        this.transparentCanvas=null;
      }

      this.cachedCanvases.clear();
      this.webGLContext.clear();

      if(this.imageLayer){
        this.imageLayer.endLayout();
      }
    },
    setLineWidth:functionCanvasGraphics_setLineWidth(width){
      this.current.lineWidth=width;
      this.ctx.lineWidth=width;
    },
    setLineCap:functionCanvasGraphics_setLineCap(style){
      this.ctx.lineCap=LINE_CAP_STYLES[style];
    },
    setLineJoin:functionCanvasGraphics_setLineJoin(style){
      this.ctx.lineJoin=LINE_JOIN_STYLES[style];
    },
    setMiterLimit:functionCanvasGraphics_setMiterLimit(limit){
      this.ctx.miterLimit=limit;
    },
    setDash:functionCanvasGraphics_setDash(dashArray,dashPhase){
      varctx=this.ctx;

      if(ctx.setLineDash!==undefined){
        ctx.setLineDash(dashArray);
        ctx.lineDashOffset=dashPhase;
      }
    },
    setRenderingIntent:functionsetRenderingIntent(intent){},
    setFlatness:functionsetFlatness(flatness){},
    setGState:functionCanvasGraphics_setGState(states){
      for(vari=0,ii=states.length;i<ii;i++){
        varstate=states[i];
        varkey=state[0];
        varvalue=state[1];

        switch(key){
          case'LW':
            this.setLineWidth(value);
            break;

          case'LC':
            this.setLineCap(value);
            break;

          case'LJ':
            this.setLineJoin(value);
            break;

          case'ML':
            this.setMiterLimit(value);
            break;

          case'D':
            this.setDash(value[0],value[1]);
            break;

          case'RI':
            this.setRenderingIntent(value);
            break;

          case'FL':
            this.setFlatness(value);
            break;

          case'Font':
            this.setFont(value[0],value[1]);
            break;

          case'CA':
            this.current.strokeAlpha=state[1];
            break;

          case'ca':
            this.current.fillAlpha=state[1];
            this.ctx.globalAlpha=state[1];
            break;

          case'BM':
            this.ctx.globalCompositeOperation=value;
            break;

          case'SMask':
            if(this.current.activeSMask){
              if(this.stateStack.length>0&&this.stateStack[this.stateStack.length-1].activeSMask===this.current.activeSMask){
                this.suspendSMaskGroup();
              }else{
                this.endSMaskGroup();
              }
            }

            this.current.activeSMask=value?this.tempSMask:null;

            if(this.current.activeSMask){
              this.beginSMaskGroup();
            }

            this.tempSMask=null;
            break;
        }
      }
    },
    beginSMaskGroup:functionCanvasGraphics_beginSMaskGroup(){
      varactiveSMask=this.current.activeSMask;
      vardrawnWidth=activeSMask.canvas.width;
      vardrawnHeight=activeSMask.canvas.height;
      varcacheId='smaskGroupAt'+this.groupLevel;
      varscratchCanvas=this.cachedCanvases.getCanvas(cacheId,drawnWidth,drawnHeight,true);
      varcurrentCtx=this.ctx;
      varcurrentTransform=currentCtx.mozCurrentTransform;
      this.ctx.save();
      vargroupCtx=scratchCanvas.context;
      groupCtx.scale(1/activeSMask.scaleX,1/activeSMask.scaleY);
      groupCtx.translate(-activeSMask.offsetX,-activeSMask.offsetY);
      groupCtx.transform.apply(groupCtx,currentTransform);
      activeSMask.startTransformInverse=groupCtx.mozCurrentTransformInverse;
      copyCtxState(currentCtx,groupCtx);
      this.ctx=groupCtx;
      this.setGState([['BM','source-over'],['ca',1],['CA',1]]);
      this.groupStack.push(currentCtx);
      this.groupLevel++;
    },
    suspendSMaskGroup:functionCanvasGraphics_endSMaskGroup(){
      vargroupCtx=this.ctx;
      this.groupLevel--;
      this.ctx=this.groupStack.pop();
      composeSMask(this.ctx,this.current.activeSMask,groupCtx,this.webGLContext);
      this.ctx.restore();
      this.ctx.save();
      copyCtxState(groupCtx,this.ctx);
      this.current.resumeSMaskCtx=groupCtx;

      vardeltaTransform=_util.Util.transform(this.current.activeSMask.startTransformInverse,groupCtx.mozCurrentTransform);

      this.ctx.transform.apply(this.ctx,deltaTransform);
      groupCtx.save();
      groupCtx.setTransform(1,0,0,1,0,0);
      groupCtx.clearRect(0,0,groupCtx.canvas.width,groupCtx.canvas.height);
      groupCtx.restore();
    },
    resumeSMaskGroup:functionCanvasGraphics_endSMaskGroup(){
      vargroupCtx=this.current.resumeSMaskCtx;
      varcurrentCtx=this.ctx;
      this.ctx=groupCtx;
      this.groupStack.push(currentCtx);
      this.groupLevel++;
    },
    endSMaskGroup:functionCanvasGraphics_endSMaskGroup(){
      vargroupCtx=this.ctx;
      this.groupLevel--;
      this.ctx=this.groupStack.pop();
      composeSMask(this.ctx,this.current.activeSMask,groupCtx,this.webGLContext);
      this.ctx.restore();
      copyCtxState(groupCtx,this.ctx);

      vardeltaTransform=_util.Util.transform(this.current.activeSMask.startTransformInverse,groupCtx.mozCurrentTransform);

      this.ctx.transform.apply(this.ctx,deltaTransform);
    },
    save:functionCanvasGraphics_save(){
      this.ctx.save();
      varold=this.current;
      this.stateStack.push(old);
      this.current=old.clone();
      this.current.resumeSMaskCtx=null;
    },
    restore:functionCanvasGraphics_restore(){
      if(this.current.resumeSMaskCtx){
        this.resumeSMaskGroup();
      }

      if(this.current.activeSMask!==null&&(this.stateStack.length===0||this.stateStack[this.stateStack.length-1].activeSMask!==this.current.activeSMask)){
        this.endSMaskGroup();
      }

      if(this.stateStack.length!==0){
        this.current=this.stateStack.pop();
        this.ctx.restore();
        this.pendingClip=null;
        this._cachedGetSinglePixelWidth=null;
      }
    },
    transform:functionCanvasGraphics_transform(a,b,c,d,e,f){
      this.ctx.transform(a,b,c,d,e,f);
      this._cachedGetSinglePixelWidth=null;
    },
    constructPath:functionCanvasGraphics_constructPath(ops,args){
      varctx=this.ctx;
      varcurrent=this.current;
      varx=current.x,
          y=current.y;

      for(vari=0,j=0,ii=ops.length;i<ii;i++){
        switch(ops[i]|0){
          case_util.OPS.rectangle:
            x=args[j++];
            y=args[j++];
            varwidth=args[j++];
            varheight=args[j++];

            if(width===0){
              width=this.getSinglePixelWidth();
            }

            if(height===0){
              height=this.getSinglePixelWidth();
            }

            varxw=x+width;
            varyh=y+height;
            this.ctx.moveTo(x,y);
            this.ctx.lineTo(xw,y);
            this.ctx.lineTo(xw,yh);
            this.ctx.lineTo(x,yh);
            this.ctx.lineTo(x,y);
            this.ctx.closePath();
            break;

          case_util.OPS.moveTo:
            x=args[j++];
            y=args[j++];
            ctx.moveTo(x,y);
            break;

          case_util.OPS.lineTo:
            x=args[j++];
            y=args[j++];
            ctx.lineTo(x,y);
            break;

          case_util.OPS.curveTo:
            x=args[j+4];
            y=args[j+5];
            ctx.bezierCurveTo(args[j],args[j+1],args[j+2],args[j+3],x,y);
            j+=6;
            break;

          case_util.OPS.curveTo2:
            ctx.bezierCurveTo(x,y,args[j],args[j+1],args[j+2],args[j+3]);
            x=args[j+2];
            y=args[j+3];
            j+=4;
            break;

          case_util.OPS.curveTo3:
            x=args[j+2];
            y=args[j+3];
            ctx.bezierCurveTo(args[j],args[j+1],x,y,x,y);
            j+=4;
            break;

          case_util.OPS.closePath:
            ctx.closePath();
            break;
        }
      }

      current.setCurrentPoint(x,y);
    },
    closePath:functionCanvasGraphics_closePath(){
      this.ctx.closePath();
    },
    stroke:functionCanvasGraphics_stroke(consumePath){
      consumePath=typeofconsumePath!=='undefined'?consumePath:true;
      varctx=this.ctx;
      varstrokeColor=this.current.strokeColor;
      ctx.lineWidth=Math.max(this.getSinglePixelWidth()*MIN_WIDTH_FACTOR,this.current.lineWidth);
      ctx.globalAlpha=this.current.strokeAlpha;

      if(strokeColor&&strokeColor.hasOwnProperty('type')&&strokeColor.type==='Pattern'){
        ctx.save();
        ctx.strokeStyle=strokeColor.getPattern(ctx,this);
        ctx.stroke();
        ctx.restore();
      }else{
        ctx.stroke();
      }

      if(consumePath){
        this.consumePath();
      }

      ctx.globalAlpha=this.current.fillAlpha;
    },
    closeStroke:functionCanvasGraphics_closeStroke(){
      this.closePath();
      this.stroke();
    },
    fill:functionCanvasGraphics_fill(consumePath){
      consumePath=typeofconsumePath!=='undefined'?consumePath:true;
      varctx=this.ctx;
      varfillColor=this.current.fillColor;
      varisPatternFill=this.current.patternFill;
      varneedRestore=false;

      if(isPatternFill){
        ctx.save();

        if(this.baseTransform){
          ctx.setTransform.apply(ctx,this.baseTransform);
        }

        ctx.fillStyle=fillColor.getPattern(ctx,this);
        needRestore=true;
      }

      if(this.pendingEOFill){
        ctx.fill('evenodd');
        this.pendingEOFill=false;
      }else{
        ctx.fill();
      }

      if(needRestore){
        ctx.restore();
      }

      if(consumePath){
        this.consumePath();
      }
    },
    eoFill:functionCanvasGraphics_eoFill(){
      this.pendingEOFill=true;
      this.fill();
    },
    fillStroke:functionCanvasGraphics_fillStroke(){
      this.fill(false);
      this.stroke(false);
      this.consumePath();
    },
    eoFillStroke:functionCanvasGraphics_eoFillStroke(){
      this.pendingEOFill=true;
      this.fillStroke();
    },
    closeFillStroke:functionCanvasGraphics_closeFillStroke(){
      this.closePath();
      this.fillStroke();
    },
    closeEOFillStroke:functionCanvasGraphics_closeEOFillStroke(){
      this.pendingEOFill=true;
      this.closePath();
      this.fillStroke();
    },
    endPath:functionCanvasGraphics_endPath(){
      this.consumePath();
    },
    clip:functionCanvasGraphics_clip(){
      this.pendingClip=NORMAL_CLIP;
    },
    eoClip:functionCanvasGraphics_eoClip(){
      this.pendingClip=EO_CLIP;
    },
    beginText:functionCanvasGraphics_beginText(){
      this.current.textMatrix=_util.IDENTITY_MATRIX;
      this.current.textMatrixScale=1;
      this.current.x=this.current.lineX=0;
      this.current.y=this.current.lineY=0;
    },
    endText:functionCanvasGraphics_endText(){
      varpaths=this.pendingTextPaths;
      varctx=this.ctx;

      if(paths===undefined){
        ctx.beginPath();
        return;
      }

      ctx.save();
      ctx.beginPath();

      for(vari=0;i<paths.length;i++){
        varpath=paths[i];
        ctx.setTransform.apply(ctx,path.transform);
        ctx.translate(path.x,path.y);
        path.addToPath(ctx,path.fontSize);
      }

      ctx.restore();
      ctx.clip();
      ctx.beginPath();
      deletethis.pendingTextPaths;
    },
    setCharSpacing:functionCanvasGraphics_setCharSpacing(spacing){
      this.current.charSpacing=spacing;
    },
    setWordSpacing:functionCanvasGraphics_setWordSpacing(spacing){
      this.current.wordSpacing=spacing;
    },
    setHScale:functionCanvasGraphics_setHScale(scale){
      this.current.textHScale=scale/100;
    },
    setLeading:functionCanvasGraphics_setLeading(leading){
      this.current.leading=-leading;
    },
    setFont:functionCanvasGraphics_setFont(fontRefName,size){
      varfontObj=this.commonObjs.get(fontRefName);
      varcurrent=this.current;

      if(!fontObj){
        thrownewError("Can'tfindfontfor".concat(fontRefName));
      }

      current.fontMatrix=fontObj.fontMatrix?fontObj.fontMatrix:_util.FONT_IDENTITY_MATRIX;

      if(current.fontMatrix[0]===0||current.fontMatrix[3]===0){
        (0,_util.warn)('Invalidfontmatrixforfont'+fontRefName);
      }

      if(size<0){
        size=-size;
        current.fontDirection=-1;
      }else{
        current.fontDirection=1;
      }

      this.current.font=fontObj;
      this.current.fontSize=size;

      if(fontObj.isType3Font){
        return;
      }

      varname=fontObj.loadedName||'sans-serif';
      varbold=fontObj.black?'900':fontObj.bold?'bold':'normal';
      varitalic=fontObj.italic?'italic':'normal';
      vartypeface="\"".concat(name,"\",").concat(fontObj.fallbackName);
      varbrowserFontSize=size<MIN_FONT_SIZE?MIN_FONT_SIZE:size>MAX_FONT_SIZE?MAX_FONT_SIZE:size;
      this.current.fontSizeScale=size/browserFontSize;
      this.ctx.font="".concat(italic,"").concat(bold,"").concat(browserFontSize,"px").concat(typeface);
    },
    setTextRenderingMode:functionCanvasGraphics_setTextRenderingMode(mode){
      this.current.textRenderingMode=mode;
    },
    setTextRise:functionCanvasGraphics_setTextRise(rise){
      this.current.textRise=rise;
    },
    moveText:functionCanvasGraphics_moveText(x,y){
      this.current.x=this.current.lineX+=x;
      this.current.y=this.current.lineY+=y;
    },
    setLeadingMoveText:functionCanvasGraphics_setLeadingMoveText(x,y){
      this.setLeading(-y);
      this.moveText(x,y);
    },
    setTextMatrix:functionCanvasGraphics_setTextMatrix(a,b,c,d,e,f){
      this.current.textMatrix=[a,b,c,d,e,f];
      this.current.textMatrixScale=Math.sqrt(a*a+b*b);
      this.current.x=this.current.lineX=0;
      this.current.y=this.current.lineY=0;
    },
    nextLine:functionCanvasGraphics_nextLine(){
      this.moveText(0,this.current.leading);
    },
    paintChar:functionpaintChar(character,x,y,patternTransform){
      varctx=this.ctx;
      varcurrent=this.current;
      varfont=current.font;
      vartextRenderingMode=current.textRenderingMode;
      varfontSize=current.fontSize/current.fontSizeScale;
      varfillStrokeMode=textRenderingMode&_util.TextRenderingMode.FILL_STROKE_MASK;
      varisAddToPathSet=!!(textRenderingMode&_util.TextRenderingMode.ADD_TO_PATH_FLAG);
      varpatternFill=current.patternFill&&font.data;
      varaddToPath;

      if(font.disableFontFace||isAddToPathSet||patternFill){
        addToPath=font.getPathGenerator(this.commonObjs,character);
      }

      if(font.disableFontFace||patternFill){
        ctx.save();
        ctx.translate(x,y);
        ctx.beginPath();
        addToPath(ctx,fontSize);

        if(patternTransform){
          ctx.setTransform.apply(ctx,patternTransform);
        }

        if(fillStrokeMode===_util.TextRenderingMode.FILL||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          ctx.fill();
        }

        if(fillStrokeMode===_util.TextRenderingMode.STROKE||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          ctx.stroke();
        }

        ctx.restore();
      }else{
        if(fillStrokeMode===_util.TextRenderingMode.FILL||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          ctx.fillText(character,x,y);
        }

        if(fillStrokeMode===_util.TextRenderingMode.STROKE||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          ctx.strokeText(character,x,y);
        }
      }

      if(isAddToPathSet){
        varpaths=this.pendingTextPaths||(this.pendingTextPaths=[]);
        paths.push({
          transform:ctx.mozCurrentTransform,
          x:x,
          y:y,
          fontSize:fontSize,
          addToPath:addToPath
        });
      }
    },

    getisFontSubpixelAAEnabled(){
      var_this$cachedCanvases$=this.cachedCanvases.getCanvas('isFontSubpixelAAEnabled',10,10),
          ctx=_this$cachedCanvases$.context;

      ctx.scale(1.5,1);
      ctx.fillText('I',0,10);
      vardata=ctx.getImageData(0,0,10,10).data;
      varenabled=false;

      for(vari=3;i<data.length;i+=4){
        if(data[i]>0&&data[i]<255){
          enabled=true;
          break;
        }
      }

      return(0,_util.shadow)(this,'isFontSubpixelAAEnabled',enabled);
    },

    showText:functionCanvasGraphics_showText(glyphs){
      varcurrent=this.current;
      varfont=current.font;

      if(font.isType3Font){
        returnthis.showType3Text(glyphs);
      }

      varfontSize=current.fontSize;

      if(fontSize===0){
        returnundefined;
      }

      varctx=this.ctx;
      varfontSizeScale=current.fontSizeScale;
      varcharSpacing=current.charSpacing;
      varwordSpacing=current.wordSpacing;
      varfontDirection=current.fontDirection;
      vartextHScale=current.textHScale*fontDirection;
      varglyphsLength=glyphs.length;
      varvertical=font.vertical;
      varspacingDir=vertical?1:-1;
      vardefaultVMetrics=font.defaultVMetrics;
      varwidthAdvanceScale=fontSize*current.fontMatrix[0];
      varsimpleFillText=current.textRenderingMode===_util.TextRenderingMode.FILL&&!font.disableFontFace&&!current.patternFill;
      ctx.save();
      varpatternTransform;

      if(current.patternFill){
        ctx.save();
        varpattern=current.fillColor.getPattern(ctx,this);
        patternTransform=ctx.mozCurrentTransform;
        ctx.restore();
        ctx.fillStyle=pattern;
      }

      ctx.transform.apply(ctx,current.textMatrix);
      ctx.translate(current.x,current.y+current.textRise);

      if(fontDirection>0){
        ctx.scale(textHScale,-1);
      }else{
        ctx.scale(textHScale,1);
      }

      varlineWidth=current.lineWidth;
      varscale=current.textMatrixScale;

      if(scale===0||lineWidth===0){
        varfillStrokeMode=current.textRenderingMode&_util.TextRenderingMode.FILL_STROKE_MASK;

        if(fillStrokeMode===_util.TextRenderingMode.STROKE||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          this._cachedGetSinglePixelWidth=null;
          lineWidth=this.getSinglePixelWidth()*MIN_WIDTH_FACTOR;
        }
      }else{
        lineWidth/=scale;
      }

      if(fontSizeScale!==1.0){
        ctx.scale(fontSizeScale,fontSizeScale);
        lineWidth/=fontSizeScale;
      }

      ctx.lineWidth=lineWidth;
      varx=0,
          i;

      for(i=0;i<glyphsLength;++i){
        varglyph=glyphs[i];

        if((0,_util.isNum)(glyph)){
          x+=spacingDir*glyph*fontSize/1000;
          continue;
        }

        varrestoreNeeded=false;
        varspacing=(glyph.isSpace?wordSpacing:0)+charSpacing;
        varcharacter=glyph.fontChar;
        varaccent=glyph.accent;
        varscaledX,scaledY,scaledAccentX,scaledAccentY;
        varwidth=glyph.width;

        if(vertical){
          varvmetric,vx,vy;
          vmetric=glyph.vmetric||defaultVMetrics;
          vx=glyph.vmetric?vmetric[1]:width*0.5;
          vx=-vx*widthAdvanceScale;
          vy=vmetric[2]*widthAdvanceScale;
          width=vmetric?-vmetric[0]:width;
          scaledX=vx/fontSizeScale;
          scaledY=(x+vy)/fontSizeScale;
        }else{
          scaledX=x/fontSizeScale;
          scaledY=0;
        }

        if(font.remeasure&&width>0){
          varmeasuredWidth=ctx.measureText(character).width*1000/fontSize*fontSizeScale;

          if(width<measuredWidth&&this.isFontSubpixelAAEnabled){
            varcharacterScaleX=width/measuredWidth;
            restoreNeeded=true;
            ctx.save();
            ctx.scale(characterScaleX,1);
            scaledX/=characterScaleX;
          }elseif(width!==measuredWidth){
            scaledX+=(width-measuredWidth)/2000*fontSize/fontSizeScale;
          }
        }

        if(glyph.isInFont||font.missingFile){
          if(simpleFillText&&!accent){
            ctx.fillText(character,scaledX,scaledY);
          }else{
            this.paintChar(character,scaledX,scaledY,patternTransform);

            if(accent){
              scaledAccentX=scaledX+accent.offset.x/fontSizeScale;
              scaledAccentY=scaledY-accent.offset.y/fontSizeScale;
              this.paintChar(accent.fontChar,scaledAccentX,scaledAccentY,patternTransform);
            }
          }
        }

        varcharWidth=width*widthAdvanceScale+spacing*fontDirection;
        x+=charWidth;

        if(restoreNeeded){
          ctx.restore();
        }
      }

      if(vertical){
        current.y-=x*textHScale;
      }else{
        current.x+=x*textHScale;
      }

      ctx.restore();
    },
    showType3Text:functionCanvasGraphics_showType3Text(glyphs){
      varctx=this.ctx;
      varcurrent=this.current;
      varfont=current.font;
      varfontSize=current.fontSize;
      varfontDirection=current.fontDirection;
      varspacingDir=font.vertical?1:-1;
      varcharSpacing=current.charSpacing;
      varwordSpacing=current.wordSpacing;
      vartextHScale=current.textHScale*fontDirection;
      varfontMatrix=current.fontMatrix||_util.FONT_IDENTITY_MATRIX;
      varglyphsLength=glyphs.length;
      varisTextInvisible=current.textRenderingMode===_util.TextRenderingMode.INVISIBLE;
      vari,glyph,width,spacingLength;

      if(isTextInvisible||fontSize===0){
        return;
      }

      this._cachedGetSinglePixelWidth=null;
      ctx.save();
      ctx.transform.apply(ctx,current.textMatrix);
      ctx.translate(current.x,current.y);
      ctx.scale(textHScale,fontDirection);

      for(i=0;i<glyphsLength;++i){
        glyph=glyphs[i];

        if((0,_util.isNum)(glyph)){
          spacingLength=spacingDir*glyph*fontSize/1000;
          this.ctx.translate(spacingLength,0);
          current.x+=spacingLength*textHScale;
          continue;
        }

        varspacing=(glyph.isSpace?wordSpacing:0)+charSpacing;
        varoperatorList=font.charProcOperatorList[glyph.operatorListId];

        if(!operatorList){
          (0,_util.warn)("Type3character\"".concat(glyph.operatorListId,"\"isnotavailable."));
          continue;
        }

        this.processingType3=glyph;
        this.save();
        ctx.scale(fontSize,fontSize);
        ctx.transform.apply(ctx,fontMatrix);
        this.executeOperatorList(operatorList);
        this.restore();

        vartransformed=_util.Util.applyTransform([glyph.width,0],fontMatrix);

        width=transformed[0]*fontSize+spacing;
        ctx.translate(width,0);
        current.x+=width*textHScale;
      }

      ctx.restore();
      this.processingType3=null;
    },
    setCharWidth:functionCanvasGraphics_setCharWidth(xWidth,yWidth){},
    setCharWidthAndBounds:functionCanvasGraphics_setCharWidthAndBounds(xWidth,yWidth,llx,lly,urx,ury){
      this.ctx.rect(llx,lly,urx-llx,ury-lly);
      this.clip();
      this.endPath();
    },
    getColorN_Pattern:functionCanvasGraphics_getColorN_Pattern(IR){
      var_this=this;

      varpattern;

      if(IR[0]==='TilingPattern'){
        varcolor=IR[1];
        varbaseTransform=this.baseTransform||this.ctx.mozCurrentTransform.slice();
        varcanvasGraphicsFactory={
          createCanvasGraphics:functioncreateCanvasGraphics(ctx){
            returnnewCanvasGraphics(ctx,_this.commonObjs,_this.objs,_this.canvasFactory,_this.webGLContext);
          }
        };
        pattern=new_pattern_helper.TilingPattern(IR,color,this.ctx,canvasGraphicsFactory,baseTransform);
      }else{
        pattern=(0,_pattern_helper.getShadingPatternFromIR)(IR);
      }

      returnpattern;
    },
    setStrokeColorN:functionCanvasGraphics_setStrokeColorN(){
      this.current.strokeColor=this.getColorN_Pattern(arguments);
    },
    setFillColorN:functionCanvasGraphics_setFillColorN(){
      this.current.fillColor=this.getColorN_Pattern(arguments);
      this.current.patternFill=true;
    },
    setStrokeRGBColor:functionCanvasGraphics_setStrokeRGBColor(r,g,b){
      varcolor=_util.Util.makeCssRgb(r,g,b);

      this.ctx.strokeStyle=color;
      this.current.strokeColor=color;
    },
    setFillRGBColor:functionCanvasGraphics_setFillRGBColor(r,g,b){
      varcolor=_util.Util.makeCssRgb(r,g,b);

      this.ctx.fillStyle=color;
      this.current.fillColor=color;
      this.current.patternFill=false;
    },
    shadingFill:functionCanvasGraphics_shadingFill(patternIR){
      varctx=this.ctx;
      this.save();
      varpattern=(0,_pattern_helper.getShadingPatternFromIR)(patternIR);
      ctx.fillStyle=pattern.getPattern(ctx,this,true);
      varinv=ctx.mozCurrentTransformInverse;

      if(inv){
        varcanvas=ctx.canvas;
        varwidth=canvas.width;
        varheight=canvas.height;

        varbl=_util.Util.applyTransform([0,0],inv);

        varbr=_util.Util.applyTransform([0,height],inv);

        varul=_util.Util.applyTransform([width,0],inv);

        varur=_util.Util.applyTransform([width,height],inv);

        varx0=Math.min(bl[0],br[0],ul[0],ur[0]);
        vary0=Math.min(bl[1],br[1],ul[1],ur[1]);
        varx1=Math.max(bl[0],br[0],ul[0],ur[0]);
        vary1=Math.max(bl[1],br[1],ul[1],ur[1]);
        this.ctx.fillRect(x0,y0,x1-x0,y1-y0);
      }else{
        this.ctx.fillRect(-1e10,-1e10,2e10,2e10);
      }

      this.restore();
    },
    beginInlineImage:functionCanvasGraphics_beginInlineImage(){
      (0,_util.unreachable)('ShouldnotcallbeginInlineImage');
    },
    beginImageData:functionCanvasGraphics_beginImageData(){
      (0,_util.unreachable)('ShouldnotcallbeginImageData');
    },
    paintFormXObjectBegin:functionCanvasGraphics_paintFormXObjectBegin(matrix,bbox){
      this.save();
      this.baseTransformStack.push(this.baseTransform);

      if(Array.isArray(matrix)&&matrix.length===6){
        this.transform.apply(this,matrix);
      }

      this.baseTransform=this.ctx.mozCurrentTransform;

      if(bbox){
        varwidth=bbox[2]-bbox[0];
        varheight=bbox[3]-bbox[1];
        this.ctx.rect(bbox[0],bbox[1],width,height);
        this.clip();
        this.endPath();
      }
    },
    paintFormXObjectEnd:functionCanvasGraphics_paintFormXObjectEnd(){
      this.restore();
      this.baseTransform=this.baseTransformStack.pop();
    },
    beginGroup:functionCanvasGraphics_beginGroup(group){
      this.save();
      varcurrentCtx=this.ctx;

      if(!group.isolated){
        (0,_util.info)('TODO:Supportnon-isolatedgroups.');
      }

      if(group.knockout){
        (0,_util.warn)('Knockoutgroupsnotsupported.');
      }

      varcurrentTransform=currentCtx.mozCurrentTransform;

      if(group.matrix){
        currentCtx.transform.apply(currentCtx,group.matrix);
      }

      if(!group.bbox){
        thrownewError('Boundingboxisrequired.');
      }

      varbounds=_util.Util.getAxialAlignedBoundingBox(group.bbox,currentCtx.mozCurrentTransform);

      varcanvasBounds=[0,0,currentCtx.canvas.width,currentCtx.canvas.height];
      bounds=_util.Util.intersect(bounds,canvasBounds)||[0,0,0,0];
      varoffsetX=Math.floor(bounds[0]);
      varoffsetY=Math.floor(bounds[1]);
      vardrawnWidth=Math.max(Math.ceil(bounds[2])-offsetX,1);
      vardrawnHeight=Math.max(Math.ceil(bounds[3])-offsetY,1);
      varscaleX=1,
          scaleY=1;

      if(drawnWidth>MAX_GROUP_SIZE){
        scaleX=drawnWidth/MAX_GROUP_SIZE;
        drawnWidth=MAX_GROUP_SIZE;
      }

      if(drawnHeight>MAX_GROUP_SIZE){
        scaleY=drawnHeight/MAX_GROUP_SIZE;
        drawnHeight=MAX_GROUP_SIZE;
      }

      varcacheId='groupAt'+this.groupLevel;

      if(group.smask){
        cacheId+='_smask_'+this.smaskCounter++%2;
      }

      varscratchCanvas=this.cachedCanvases.getCanvas(cacheId,drawnWidth,drawnHeight,true);
      vargroupCtx=scratchCanvas.context;
      groupCtx.scale(1/scaleX,1/scaleY);
      groupCtx.translate(-offsetX,-offsetY);
      groupCtx.transform.apply(groupCtx,currentTransform);

      if(group.smask){
        this.smaskStack.push({
          canvas:scratchCanvas.canvas,
          context:groupCtx,
          offsetX:offsetX,
          offsetY:offsetY,
          scaleX:scaleX,
          scaleY:scaleY,
          subtype:group.smask.subtype,
          backdrop:group.smask.backdrop,
          transferMap:group.smask.transferMap||null,
          startTransformInverse:null
        });
      }else{
        currentCtx.setTransform(1,0,0,1,0,0);
        currentCtx.translate(offsetX,offsetY);
        currentCtx.scale(scaleX,scaleY);
      }

      copyCtxState(currentCtx,groupCtx);
      this.ctx=groupCtx;
      this.setGState([['BM','source-over'],['ca',1],['CA',1]]);
      this.groupStack.push(currentCtx);
      this.groupLevel++;
      this.current.activeSMask=null;
    },
    endGroup:functionCanvasGraphics_endGroup(group){
      this.groupLevel--;
      vargroupCtx=this.ctx;
      this.ctx=this.groupStack.pop();

      if(this.ctx.imageSmoothingEnabled!==undefined){
        this.ctx.imageSmoothingEnabled=false;
      }else{
        this.ctx.mozImageSmoothingEnabled=false;
      }

      if(group.smask){
        this.tempSMask=this.smaskStack.pop();
      }else{
        this.ctx.drawImage(groupCtx.canvas,0,0);
      }

      this.restore();
    },
    beginAnnotations:functionCanvasGraphics_beginAnnotations(){
      this.save();

      if(this.baseTransform){
        this.ctx.setTransform.apply(this.ctx,this.baseTransform);
      }
    },
    endAnnotations:functionCanvasGraphics_endAnnotations(){
      this.restore();
    },
    beginAnnotation:functionCanvasGraphics_beginAnnotation(rect,transform,matrix){
      this.save();
      resetCtxToDefault(this.ctx);
      this.current=newCanvasExtraState();

      if(Array.isArray(rect)&&rect.length===4){
        varwidth=rect[2]-rect[0];
        varheight=rect[3]-rect[1];
        this.ctx.rect(rect[0],rect[1],width,height);
        this.clip();
        this.endPath();
      }

      this.transform.apply(this,transform);
      this.transform.apply(this,matrix);
    },
    endAnnotation:functionCanvasGraphics_endAnnotation(){
      this.restore();
    },
    paintJpegXObject:functionCanvasGraphics_paintJpegXObject(objId,w,h){
      vardomImage=this.processingType3?this.commonObjs.get(objId):this.objs.get(objId);

      if(!domImage){
        (0,_util.warn)('Dependentimageisn\'treadyyet');
        return;
      }

      this.save();
      varctx=this.ctx;
      ctx.scale(1/w,-1/h);
      ctx.drawImage(domImage,0,0,domImage.width,domImage.height,0,-h,w,h);

      if(this.imageLayer){
        varcurrentTransform=ctx.mozCurrentTransformInverse;
        varposition=this.getCanvasPosition(0,0);
        this.imageLayer.appendImage({
          objId:objId,
          left:position[0],
          top:position[1],
          width:w/currentTransform[0],
          height:h/currentTransform[3]
        });
      }

      this.restore();
    },
    paintImageMaskXObject:functionCanvasGraphics_paintImageMaskXObject(img){
      varctx=this.ctx;
      varwidth=img.width,
          height=img.height;
      varfillColor=this.current.fillColor;
      varisPatternFill=this.current.patternFill;
      varglyph=this.processingType3;

      if(COMPILE_TYPE3_GLYPHS&&glyph&&glyph.compiled===undefined){
        if(width<=MAX_SIZE_TO_COMPILE&&height<=MAX_SIZE_TO_COMPILE){
          glyph.compiled=compileType3Glyph({
            data:img.data,
            width:width,
            height:height
          });
        }else{
          glyph.compiled=null;
        }
      }

      if(glyph&&glyph.compiled){
        glyph.compiled(ctx);
        return;
      }

      varmaskCanvas=this.cachedCanvases.getCanvas('maskCanvas',width,height);
      varmaskCtx=maskCanvas.context;
      maskCtx.save();
      putBinaryImageMask(maskCtx,img);
      maskCtx.globalCompositeOperation='source-in';
      maskCtx.fillStyle=isPatternFill?fillColor.getPattern(maskCtx,this):fillColor;
      maskCtx.fillRect(0,0,width,height);
      maskCtx.restore();
      this.paintInlineImageXObject(maskCanvas.canvas);
    },
    paintImageMaskXObjectRepeat:functionCanvasGraphics_paintImageMaskXObjectRepeat(imgData,scaleX,scaleY,positions){
      varwidth=imgData.width;
      varheight=imgData.height;
      varfillColor=this.current.fillColor;
      varisPatternFill=this.current.patternFill;
      varmaskCanvas=this.cachedCanvases.getCanvas('maskCanvas',width,height);
      varmaskCtx=maskCanvas.context;
      maskCtx.save();
      putBinaryImageMask(maskCtx,imgData);
      maskCtx.globalCompositeOperation='source-in';
      maskCtx.fillStyle=isPatternFill?fillColor.getPattern(maskCtx,this):fillColor;
      maskCtx.fillRect(0,0,width,height);
      maskCtx.restore();
      varctx=this.ctx;

      for(vari=0,ii=positions.length;i<ii;i+=2){
        ctx.save();
        ctx.transform(scaleX,0,0,scaleY,positions[i],positions[i+1]);
        ctx.scale(1,-1);
        ctx.drawImage(maskCanvas.canvas,0,0,width,height,0,-1,1,1);
        ctx.restore();
      }
    },
    paintImageMaskXObjectGroup:functionCanvasGraphics_paintImageMaskXObjectGroup(images){
      varctx=this.ctx;
      varfillColor=this.current.fillColor;
      varisPatternFill=this.current.patternFill;

      for(vari=0,ii=images.length;i<ii;i++){
        varimage=images[i];
        varwidth=image.width,
            height=image.height;
        varmaskCanvas=this.cachedCanvases.getCanvas('maskCanvas',width,height);
        varmaskCtx=maskCanvas.context;
        maskCtx.save();
        putBinaryImageMask(maskCtx,image);
        maskCtx.globalCompositeOperation='source-in';
        maskCtx.fillStyle=isPatternFill?fillColor.getPattern(maskCtx,this):fillColor;
        maskCtx.fillRect(0,0,width,height);
        maskCtx.restore();
        ctx.save();
        ctx.transform.apply(ctx,image.transform);
        ctx.scale(1,-1);
        ctx.drawImage(maskCanvas.canvas,0,0,width,height,0,-1,1,1);
        ctx.restore();
      }
    },
    paintImageXObject:functionCanvasGraphics_paintImageXObject(objId){
      varimgData=this.processingType3?this.commonObjs.get(objId):this.objs.get(objId);

      if(!imgData){
        (0,_util.warn)('Dependentimageisn\'treadyyet');
        return;
      }

      this.paintInlineImageXObject(imgData);
    },
    paintImageXObjectRepeat:functionCanvasGraphics_paintImageXObjectRepeat(objId,scaleX,scaleY,positions){
      varimgData=this.processingType3?this.commonObjs.get(objId):this.objs.get(objId);

      if(!imgData){
        (0,_util.warn)('Dependentimageisn\'treadyyet');
        return;
      }

      varwidth=imgData.width;
      varheight=imgData.height;
      varmap=[];

      for(vari=0,ii=positions.length;i<ii;i+=2){
        map.push({
          transform:[scaleX,0,0,scaleY,positions[i],positions[i+1]],
          x:0,
          y:0,
          w:width,
          h:height
        });
      }

      this.paintInlineImageXObjectGroup(imgData,map);
    },
    paintInlineImageXObject:functionCanvasGraphics_paintInlineImageXObject(imgData){
      varwidth=imgData.width;
      varheight=imgData.height;
      varctx=this.ctx;
      this.save();
      ctx.scale(1/width,-1/height);
      varcurrentTransform=ctx.mozCurrentTransformInverse;
      vara=currentTransform[0],
          b=currentTransform[1];
      varwidthScale=Math.max(Math.sqrt(a*a+b*b),1);
      varc=currentTransform[2],
          d=currentTransform[3];
      varheightScale=Math.max(Math.sqrt(c*c+d*d),1);
      varimgToPaint,tmpCanvas;

      if(typeofHTMLElement==='function'&&imgDatainstanceofHTMLElement||!imgData.data){
        imgToPaint=imgData;
      }else{
        tmpCanvas=this.cachedCanvases.getCanvas('inlineImage',width,height);
        vartmpCtx=tmpCanvas.context;
        putBinaryImageData(tmpCtx,imgData);
        imgToPaint=tmpCanvas.canvas;
      }

      varpaintWidth=width,
          paintHeight=height;
      vartmpCanvasId='prescale1';

      while(widthScale>2&&paintWidth>1||heightScale>2&&paintHeight>1){
        varnewWidth=paintWidth,
            newHeight=paintHeight;

        if(widthScale>2&&paintWidth>1){
          newWidth=Math.ceil(paintWidth/2);
          widthScale/=paintWidth/newWidth;
        }

        if(heightScale>2&&paintHeight>1){
          newHeight=Math.ceil(paintHeight/2);
          heightScale/=paintHeight/newHeight;
        }

        tmpCanvas=this.cachedCanvases.getCanvas(tmpCanvasId,newWidth,newHeight);
        tmpCtx=tmpCanvas.context;
        tmpCtx.clearRect(0,0,newWidth,newHeight);
        tmpCtx.drawImage(imgToPaint,0,0,paintWidth,paintHeight,0,0,newWidth,newHeight);
        imgToPaint=tmpCanvas.canvas;
        paintWidth=newWidth;
        paintHeight=newHeight;
        tmpCanvasId=tmpCanvasId==='prescale1'?'prescale2':'prescale1';
      }

      ctx.drawImage(imgToPaint,0,0,paintWidth,paintHeight,0,-height,width,height);

      if(this.imageLayer){
        varposition=this.getCanvasPosition(0,-height);
        this.imageLayer.appendImage({
          imgData:imgData,
          left:position[0],
          top:position[1],
          width:width/currentTransform[0],
          height:height/currentTransform[3]
        });
      }

      this.restore();
    },
    paintInlineImageXObjectGroup:functionCanvasGraphics_paintInlineImageXObjectGroup(imgData,map){
      varctx=this.ctx;
      varw=imgData.width;
      varh=imgData.height;
      vartmpCanvas=this.cachedCanvases.getCanvas('inlineImage',w,h);
      vartmpCtx=tmpCanvas.context;
      putBinaryImageData(tmpCtx,imgData);

      for(vari=0,ii=map.length;i<ii;i++){
        varentry=map[i];
        ctx.save();
        ctx.transform.apply(ctx,entry.transform);
        ctx.scale(1,-1);
        ctx.drawImage(tmpCanvas.canvas,entry.x,entry.y,entry.w,entry.h,0,-1,1,1);

        if(this.imageLayer){
          varposition=this.getCanvasPosition(entry.x,entry.y);
          this.imageLayer.appendImage({
            imgData:imgData,
            left:position[0],
            top:position[1],
            width:w,
            height:h
          });
        }

        ctx.restore();
      }
    },
    paintSolidColorImageMask:functionCanvasGraphics_paintSolidColorImageMask(){
      this.ctx.fillRect(0,0,1,1);
    },
    paintXObject:functionCanvasGraphics_paintXObject(){
      (0,_util.warn)('Unsupported\'paintXObject\'command.');
    },
    markPoint:functionCanvasGraphics_markPoint(tag){},
    markPointProps:functionCanvasGraphics_markPointProps(tag,properties){},
    beginMarkedContent:functionCanvasGraphics_beginMarkedContent(tag){},
    beginMarkedContentProps:functionCanvasGraphics_beginMarkedContentProps(tag,properties){},
    endMarkedContent:functionCanvasGraphics_endMarkedContent(){},
    beginCompat:functionCanvasGraphics_beginCompat(){},
    endCompat:functionCanvasGraphics_endCompat(){},
    consumePath:functionCanvasGraphics_consumePath(){
      varctx=this.ctx;

      if(this.pendingClip){
        if(this.pendingClip===EO_CLIP){
          ctx.clip('evenodd');
        }else{
          ctx.clip();
        }

        this.pendingClip=null;
      }

      ctx.beginPath();
    },
    getSinglePixelWidth:functiongetSinglePixelWidth(scale){
      if(this._cachedGetSinglePixelWidth===null){
        varinverse=this.ctx.mozCurrentTransformInverse;
        this._cachedGetSinglePixelWidth=Math.sqrt(Math.max(inverse[0]*inverse[0]+inverse[1]*inverse[1],inverse[2]*inverse[2]+inverse[3]*inverse[3]));
      }

      returnthis._cachedGetSinglePixelWidth;
    },
    getCanvasPosition:functionCanvasGraphics_getCanvasPosition(x,y){
      vartransform=this.ctx.mozCurrentTransform;
      return[transform[0]*x+transform[2]*y+transform[4],transform[1]*x+transform[3]*y+transform[5]];
    }
  };

  for(varopin_util.OPS){
    CanvasGraphics.prototype[_util.OPS[op]]=CanvasGraphics.prototype[op];
  }

  returnCanvasGraphics;
}();

exports.CanvasGraphics=CanvasGraphics;

/***/}),
/*155*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.getShadingPatternFromIR=getShadingPatternFromIR;
exports.TilingPattern=void0;

var_util=__w_pdfjs_require__(1);

varShadingIRs={};
ShadingIRs.RadialAxial={
  fromIR:functionRadialAxial_fromIR(raw){
    vartype=raw[1];
    varcolorStops=raw[2];
    varp0=raw[3];
    varp1=raw[4];
    varr0=raw[5];
    varr1=raw[6];
    return{
      type:'Pattern',
      getPattern:functionRadialAxial_getPattern(ctx){
        vargrad;

        if(type==='axial'){
          grad=ctx.createLinearGradient(p0[0],p0[1],p1[0],p1[1]);
        }elseif(type==='radial'){
          grad=ctx.createRadialGradient(p0[0],p0[1],r0,p1[0],p1[1],r1);
        }

        for(vari=0,ii=colorStops.length;i<ii;++i){
          varc=colorStops[i];
          grad.addColorStop(c[0],c[1]);
        }

        returngrad;
      }
    };
  }
};

varcreateMeshCanvas=functioncreateMeshCanvasClosure(){
  functiondrawTriangle(data,context,p1,p2,p3,c1,c2,c3){
    varcoords=context.coords,
        colors=context.colors;
    varbytes=data.data,
        rowSize=data.width*4;
    vartmp;

    if(coords[p1+1]>coords[p2+1]){
      tmp=p1;
      p1=p2;
      p2=tmp;
      tmp=c1;
      c1=c2;
      c2=tmp;
    }

    if(coords[p2+1]>coords[p3+1]){
      tmp=p2;
      p2=p3;
      p3=tmp;
      tmp=c2;
      c2=c3;
      c3=tmp;
    }

    if(coords[p1+1]>coords[p2+1]){
      tmp=p1;
      p1=p2;
      p2=tmp;
      tmp=c1;
      c1=c2;
      c2=tmp;
    }

    varx1=(coords[p1]+context.offsetX)*context.scaleX;
    vary1=(coords[p1+1]+context.offsetY)*context.scaleY;
    varx2=(coords[p2]+context.offsetX)*context.scaleX;
    vary2=(coords[p2+1]+context.offsetY)*context.scaleY;
    varx3=(coords[p3]+context.offsetX)*context.scaleX;
    vary3=(coords[p3+1]+context.offsetY)*context.scaleY;

    if(y1>=y3){
      return;
    }

    varc1r=colors[c1],
        c1g=colors[c1+1],
        c1b=colors[c1+2];
    varc2r=colors[c2],
        c2g=colors[c2+1],
        c2b=colors[c2+2];
    varc3r=colors[c3],
        c3g=colors[c3+1],
        c3b=colors[c3+2];
    varminY=Math.round(y1),
        maxY=Math.round(y3);
    varxa,car,cag,cab;
    varxb,cbr,cbg,cbb;
    vark;

    for(vary=minY;y<=maxY;y++){
      if(y<y2){
        k=y<y1?0:y1===y2?1:(y1-y)/(y1-y2);
        xa=x1-(x1-x2)*k;
        car=c1r-(c1r-c2r)*k;
        cag=c1g-(c1g-c2g)*k;
        cab=c1b-(c1b-c2b)*k;
      }else{
        k=y>y3?1:y2===y3?0:(y2-y)/(y2-y3);
        xa=x2-(x2-x3)*k;
        car=c2r-(c2r-c3r)*k;
        cag=c2g-(c2g-c3g)*k;
        cab=c2b-(c2b-c3b)*k;
      }

      k=y<y1?0:y>y3?1:(y1-y)/(y1-y3);
      xb=x1-(x1-x3)*k;
      cbr=c1r-(c1r-c3r)*k;
      cbg=c1g-(c1g-c3g)*k;
      cbb=c1b-(c1b-c3b)*k;
      varx1_=Math.round(Math.min(xa,xb));
      varx2_=Math.round(Math.max(xa,xb));
      varj=rowSize*y+x1_*4;

      for(varx=x1_;x<=x2_;x++){
        k=(xa-x)/(xa-xb);
        k=k<0?0:k>1?1:k;
        bytes[j++]=car-(car-cbr)*k|0;
        bytes[j++]=cag-(cag-cbg)*k|0;
        bytes[j++]=cab-(cab-cbb)*k|0;
        bytes[j++]=255;
      }
    }
  }

  functiondrawFigure(data,figure,context){
    varps=figure.coords;
    varcs=figure.colors;
    vari,ii;

    switch(figure.type){
      case'lattice':
        varverticesPerRow=figure.verticesPerRow;
        varrows=Math.floor(ps.length/verticesPerRow)-1;
        varcols=verticesPerRow-1;

        for(i=0;i<rows;i++){
          varq=i*verticesPerRow;

          for(varj=0;j<cols;j++,q++){
            drawTriangle(data,context,ps[q],ps[q+1],ps[q+verticesPerRow],cs[q],cs[q+1],cs[q+verticesPerRow]);
            drawTriangle(data,context,ps[q+verticesPerRow+1],ps[q+1],ps[q+verticesPerRow],cs[q+verticesPerRow+1],cs[q+1],cs[q+verticesPerRow]);
          }
        }

        break;

      case'triangles':
        for(i=0,ii=ps.length;i<ii;i+=3){
          drawTriangle(data,context,ps[i],ps[i+1],ps[i+2],cs[i],cs[i+1],cs[i+2]);
        }

        break;

      default:
        thrownewError('illegalfigure');
    }
  }

  functioncreateMeshCanvas(bounds,combinesScale,coords,colors,figures,backgroundColor,cachedCanvases,webGLContext){
    varEXPECTED_SCALE=1.1;
    varMAX_PATTERN_SIZE=3000;
    varBORDER_SIZE=2;
    varoffsetX=Math.floor(bounds[0]);
    varoffsetY=Math.floor(bounds[1]);
    varboundsWidth=Math.ceil(bounds[2])-offsetX;
    varboundsHeight=Math.ceil(bounds[3])-offsetY;
    varwidth=Math.min(Math.ceil(Math.abs(boundsWidth*combinesScale[0]*EXPECTED_SCALE)),MAX_PATTERN_SIZE);
    varheight=Math.min(Math.ceil(Math.abs(boundsHeight*combinesScale[1]*EXPECTED_SCALE)),MAX_PATTERN_SIZE);
    varscaleX=boundsWidth/width;
    varscaleY=boundsHeight/height;
    varcontext={
      coords:coords,
      colors:colors,
      offsetX:-offsetX,
      offsetY:-offsetY,
      scaleX:1/scaleX,
      scaleY:1/scaleY
    };
    varpaddedWidth=width+BORDER_SIZE*2;
    varpaddedHeight=height+BORDER_SIZE*2;
    varcanvas,tmpCanvas,i,ii;

    if(webGLContext.isEnabled){
      canvas=webGLContext.drawFigures({
        width:width,
        height:height,
        backgroundColor:backgroundColor,
        figures:figures,
        context:context
      });
      tmpCanvas=cachedCanvases.getCanvas('mesh',paddedWidth,paddedHeight,false);
      tmpCanvas.context.drawImage(canvas,BORDER_SIZE,BORDER_SIZE);
      canvas=tmpCanvas.canvas;
    }else{
      tmpCanvas=cachedCanvases.getCanvas('mesh',paddedWidth,paddedHeight,false);
      vartmpCtx=tmpCanvas.context;
      vardata=tmpCtx.createImageData(width,height);

      if(backgroundColor){
        varbytes=data.data;

        for(i=0,ii=bytes.length;i<ii;i+=4){
          bytes[i]=backgroundColor[0];
          bytes[i+1]=backgroundColor[1];
          bytes[i+2]=backgroundColor[2];
          bytes[i+3]=255;
        }
      }

      for(i=0;i<figures.length;i++){
        drawFigure(data,figures[i],context);
      }

      tmpCtx.putImageData(data,BORDER_SIZE,BORDER_SIZE);
      canvas=tmpCanvas.canvas;
    }

    return{
      canvas:canvas,
      offsetX:offsetX-BORDER_SIZE*scaleX,
      offsetY:offsetY-BORDER_SIZE*scaleY,
      scaleX:scaleX,
      scaleY:scaleY
    };
  }

  returncreateMeshCanvas;
}();

ShadingIRs.Mesh={
  fromIR:functionMesh_fromIR(raw){
    varcoords=raw[2];
    varcolors=raw[3];
    varfigures=raw[4];
    varbounds=raw[5];
    varmatrix=raw[6];
    varbackground=raw[8];
    return{
      type:'Pattern',
      getPattern:functionMesh_getPattern(ctx,owner,shadingFill){
        varscale;

        if(shadingFill){
          scale=_util.Util.singularValueDecompose2dScale(ctx.mozCurrentTransform);
        }else{
          scale=_util.Util.singularValueDecompose2dScale(owner.baseTransform);

          if(matrix){
            varmatrixScale=_util.Util.singularValueDecompose2dScale(matrix);

            scale=[scale[0]*matrixScale[0],scale[1]*matrixScale[1]];
          }
        }

        vartemporaryPatternCanvas=createMeshCanvas(bounds,scale,coords,colors,figures,shadingFill?null:background,owner.cachedCanvases,owner.webGLContext);

        if(!shadingFill){
          ctx.setTransform.apply(ctx,owner.baseTransform);

          if(matrix){
            ctx.transform.apply(ctx,matrix);
          }
        }

        ctx.translate(temporaryPatternCanvas.offsetX,temporaryPatternCanvas.offsetY);
        ctx.scale(temporaryPatternCanvas.scaleX,temporaryPatternCanvas.scaleY);
        returnctx.createPattern(temporaryPatternCanvas.canvas,'no-repeat');
      }
    };
  }
};
ShadingIRs.Dummy={
  fromIR:functionDummy_fromIR(){
    return{
      type:'Pattern',
      getPattern:functionDummy_fromIR_getPattern(){
        return'hotpink';
      }
    };
  }
};

functiongetShadingPatternFromIR(raw){
  varshadingIR=ShadingIRs[raw[0]];

  if(!shadingIR){
    thrownewError("UnknownIRtype:".concat(raw[0]));
  }

  returnshadingIR.fromIR(raw);
}

varTilingPattern=functionTilingPatternClosure(){
  varPaintType={
    COLORED:1,
    UNCOLORED:2
  };
  varMAX_PATTERN_SIZE=3000;

  functionTilingPattern(IR,color,ctx,canvasGraphicsFactory,baseTransform){
    this.operatorList=IR[2];
    this.matrix=IR[3]||[1,0,0,1,0,0];
    this.bbox=IR[4];
    this.xstep=IR[5];
    this.ystep=IR[6];
    this.paintType=IR[7];
    this.tilingType=IR[8];
    this.color=color;
    this.canvasGraphicsFactory=canvasGraphicsFactory;
    this.baseTransform=baseTransform;
    this.type='Pattern';
    this.ctx=ctx;
  }

  TilingPattern.prototype={
    createPatternCanvas:functionTilinPattern_createPatternCanvas(owner){
      varoperatorList=this.operatorList;
      varbbox=this.bbox;
      varxstep=this.xstep;
      varystep=this.ystep;
      varpaintType=this.paintType;
      vartilingType=this.tilingType;
      varcolor=this.color;
      varcanvasGraphicsFactory=this.canvasGraphicsFactory;
      (0,_util.info)('TilingType:'+tilingType);
      varx0=bbox[0],
          y0=bbox[1],
          x1=bbox[2],
          y1=bbox[3];

      varmatrixScale=_util.Util.singularValueDecompose2dScale(this.matrix);

      varcurMatrixScale=_util.Util.singularValueDecompose2dScale(this.baseTransform);

      varcombinedScale=[matrixScale[0]*curMatrixScale[0],matrixScale[1]*curMatrixScale[1]];
      vardimx=this.getSizeAndScale(xstep,this.ctx.canvas.width,combinedScale[0]);
      vardimy=this.getSizeAndScale(ystep,this.ctx.canvas.height,combinedScale[1]);
      vartmpCanvas=owner.cachedCanvases.getCanvas('pattern',dimx.size,dimy.size,true);
      vartmpCtx=tmpCanvas.context;
      vargraphics=canvasGraphicsFactory.createCanvasGraphics(tmpCtx);
      graphics.groupLevel=owner.groupLevel;
      this.setFillAndStrokeStyleToContext(graphics,paintType,color);
      graphics.transform(dimx.scale,0,0,dimy.scale,0,0);
      graphics.transform(1,0,0,1,-x0,-y0);
      this.clipBbox(graphics,bbox,x0,y0,x1,y1);
      graphics.executeOperatorList(operatorList);
      this.ctx.transform(1,0,0,1,x0,y0);
      this.ctx.scale(1/dimx.scale,1/dimy.scale);
      returntmpCanvas.canvas;
    },
    getSizeAndScale:functionTilingPattern_getSizeAndScale(step,realOutputSize,scale){
      step=Math.abs(step);
      varmaxSize=Math.max(MAX_PATTERN_SIZE,realOutputSize);
      varsize=Math.ceil(step*scale);

      if(size>=maxSize){
        size=maxSize;
      }else{
        scale=size/step;
      }

      return{
        scale:scale,
        size:size
      };
    },
    clipBbox:functionclipBbox(graphics,bbox,x0,y0,x1,y1){
      if(Array.isArray(bbox)&&bbox.length===4){
        varbboxWidth=x1-x0;
        varbboxHeight=y1-y0;
        graphics.ctx.rect(x0,y0,bboxWidth,bboxHeight);
        graphics.clip();
        graphics.endPath();
      }
    },
    setFillAndStrokeStyleToContext:functionsetFillAndStrokeStyleToContext(graphics,paintType,color){
      varcontext=graphics.ctx,
          current=graphics.current;

      switch(paintType){
        casePaintType.COLORED:
          varctx=this.ctx;
          context.fillStyle=ctx.fillStyle;
          context.strokeStyle=ctx.strokeStyle;
          current.fillColor=ctx.fillStyle;
          current.strokeColor=ctx.strokeStyle;
          break;

        casePaintType.UNCOLORED:
          varcssColor=_util.Util.makeCssRgb(color[0],color[1],color[2]);

          context.fillStyle=cssColor;
          context.strokeStyle=cssColor;
          current.fillColor=cssColor;
          current.strokeColor=cssColor;
          break;

        default:
          thrownew_util.FormatError("Unsupportedpainttype:".concat(paintType));
      }
    },
    getPattern:functionTilingPattern_getPattern(ctx,owner){
      ctx=this.ctx;
      ctx.setTransform.apply(ctx,this.baseTransform);
      ctx.transform.apply(ctx,this.matrix);
      vartemporaryPatternCanvas=this.createPatternCanvas(owner);
      returnctx.createPattern(temporaryPatternCanvas,'repeat');
    }
  };
  returnTilingPattern;
}();

exports.TilingPattern=TilingPattern;

/***/}),
/*156*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.GlobalWorkerOptions=void0;
varGlobalWorkerOptions=Object.create(null);
exports.GlobalWorkerOptions=GlobalWorkerOptions;
GlobalWorkerOptions.workerPort=GlobalWorkerOptions.workerPort===undefined?null:GlobalWorkerOptions.workerPort;
GlobalWorkerOptions.workerSrc=GlobalWorkerOptions.workerSrc===undefined?'':GlobalWorkerOptions.workerSrc;

/***/}),
/*157*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.MessageHandler=MessageHandler;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

functionresolveCall(_x,_x2){
  return_resolveCall.apply(this,arguments);
}

function_resolveCall(){
  _resolveCall=_asyncToGenerator(
  /*#__PURE__*/
  _regenerator["default"].mark(function_callee(fn,args){
    varthisArg,
        _args=arguments;
    return_regenerator["default"].wrap(function_callee$(_context){
      while(1){
        switch(_context.prev=_context.next){
          case0:
            thisArg=_args.length>2&&_args[2]!==undefined?_args[2]:null;

            if(fn){
              _context.next=3;
              break;
            }

            return_context.abrupt("return",undefined);

          case3:
            return_context.abrupt("return",fn.apply(thisArg,args));

          case4:
          case"end":
            return_context.stop();
        }
      }
    },_callee);
  }));
  return_resolveCall.apply(this,arguments);
}

functionwrapReason(reason){
  if(_typeof(reason)!=='object'){
    returnreason;
  }

  switch(reason.name){
    case'AbortException':
      returnnew_util.AbortException(reason.message);

    case'MissingPDFException':
      returnnew_util.MissingPDFException(reason.message);

    case'UnexpectedResponseException':
      returnnew_util.UnexpectedResponseException(reason.message,reason.status);

    default:
      returnnew_util.UnknownErrorException(reason.message,reason.details);
  }
}

functionmakeReasonSerializable(reason){
  if(!(reasoninstanceofError)||reasoninstanceof_util.AbortException||reasoninstanceof_util.MissingPDFException||reasoninstanceof_util.UnexpectedResponseException||reasoninstanceof_util.UnknownErrorException){
    returnreason;
  }

  returnnew_util.UnknownErrorException(reason.message,reason.toString());
}

functionresolveOrReject(capability,success,reason){
  if(success){
    capability.resolve();
  }else{
    capability.reject(reason);
  }
}

functionfinalize(promise){
  returnPromise.resolve(promise)["catch"](function(){});
}

functionMessageHandler(sourceName,targetName,comObj){
  var_this=this;

  this.sourceName=sourceName;
  this.targetName=targetName;
  this.comObj=comObj;
  this.callbackId=1;
  this.streamId=1;
  this.postMessageTransfers=true;
  this.streamSinks=Object.create(null);
  this.streamControllers=Object.create(null);
  varcallbacksCapabilities=this.callbacksCapabilities=Object.create(null);
  varah=this.actionHandler=Object.create(null);

  this._onComObjOnMessage=function(event){
    vardata=event.data;

    if(data.targetName!==_this.sourceName){
      return;
    }

    if(data.stream){
      _this._processStreamMessage(data);
    }elseif(data.isReply){
      varcallbackId=data.callbackId;

      if(data.callbackIdincallbacksCapabilities){
        varcallback=callbacksCapabilities[callbackId];
        deletecallbacksCapabilities[callbackId];

        if('error'indata){
          callback.reject(wrapReason(data.error));
        }else{
          callback.resolve(data.data);
        }
      }else{
        thrownewError("Cannotresolvecallback".concat(callbackId));
      }
    }elseif(data.actioninah){
      varaction=ah[data.action];

      if(data.callbackId){
        var_sourceName=_this.sourceName;
        var_targetName=data.sourceName;
        Promise.resolve().then(function(){
          returnaction[0].call(action[1],data.data);
        }).then(function(result){
          comObj.postMessage({
            sourceName:_sourceName,
            targetName:_targetName,
            isReply:true,
            callbackId:data.callbackId,
            data:result
          });
        },function(reason){
          comObj.postMessage({
            sourceName:_sourceName,
            targetName:_targetName,
            isReply:true,
            callbackId:data.callbackId,
            error:makeReasonSerializable(reason)
          });
        });
      }elseif(data.streamId){
        _this._createStreamSink(data);
      }else{
        action[0].call(action[1],data.data);
      }
    }else{
      thrownewError("Unknownactionfromworker:".concat(data.action));
    }
  };

  comObj.addEventListener('message',this._onComObjOnMessage);
}

MessageHandler.prototype={
  on:functionon(actionName,handler,scope){
    varah=this.actionHandler;

    if(ah[actionName]){
      thrownewError("ThereisalreadyanactionNamecalled\"".concat(actionName,"\""));
    }

    ah[actionName]=[handler,scope];
  },
  send:functionsend(actionName,data,transfers){
    varmessage={
      sourceName:this.sourceName,
      targetName:this.targetName,
      action:actionName,
      data:data
    };
    this.postMessage(message,transfers);
  },
  sendWithPromise:functionsendWithPromise(actionName,data,transfers){
    varcallbackId=this.callbackId++;
    varmessage={
      sourceName:this.sourceName,
      targetName:this.targetName,
      action:actionName,
      data:data,
      callbackId:callbackId
    };
    varcapability=(0,_util.createPromiseCapability)();
    this.callbacksCapabilities[callbackId]=capability;

    try{
      this.postMessage(message,transfers);
    }catch(e){
      capability.reject(e);
    }

    returncapability.promise;
  },
  sendWithStream:functionsendWithStream(actionName,data,queueingStrategy,transfers){
    var_this2=this;

    varstreamId=this.streamId++;
    varsourceName=this.sourceName;
    vartargetName=this.targetName;
    returnnew_util.ReadableStream({
      start:functionstart(controller){
        varstartCapability=(0,_util.createPromiseCapability)();
        _this2.streamControllers[streamId]={
          controller:controller,
          startCall:startCapability,
          isClosed:false
        };

        _this2.postMessage({
          sourceName:sourceName,
          targetName:targetName,
          action:actionName,
          streamId:streamId,
          data:data,
          desiredSize:controller.desiredSize
        });

        returnstartCapability.promise;
      },
      pull:functionpull(controller){
        varpullCapability=(0,_util.createPromiseCapability)();
        _this2.streamControllers[streamId].pullCall=pullCapability;

        _this2.postMessage({
          sourceName:sourceName,
          targetName:targetName,
          stream:'pull',
          streamId:streamId,
          desiredSize:controller.desiredSize
        });

        returnpullCapability.promise;
      },
      cancel:functioncancel(reason){
        varcancelCapability=(0,_util.createPromiseCapability)();
        _this2.streamControllers[streamId].cancelCall=cancelCapability;
        _this2.streamControllers[streamId].isClosed=true;

        _this2.postMessage({
          sourceName:sourceName,
          targetName:targetName,
          stream:'cancel',
          reason:reason,
          streamId:streamId
        });

        returncancelCapability.promise;
      }
    },queueingStrategy);
  },
  _createStreamSink:function_createStreamSink(data){
    var_this3=this;

    varself=this;
    varaction=this.actionHandler[data.action];
    varstreamId=data.streamId;
    vardesiredSize=data.desiredSize;
    varsourceName=this.sourceName;
    vartargetName=data.sourceName;
    varcapability=(0,_util.createPromiseCapability)();

    varsendStreamRequest=functionsendStreamRequest(_ref){
      varstream=_ref.stream,
          chunk=_ref.chunk,
          transfers=_ref.transfers,
          success=_ref.success,
          reason=_ref.reason;

      _this3.postMessage({
        sourceName:sourceName,
        targetName:targetName,
        stream:stream,
        streamId:streamId,
        chunk:chunk,
        success:success,
        reason:reason
      },transfers);
    };

    varstreamSink={
      enqueue:functionenqueue(chunk){
        varsize=arguments.length>1&&arguments[1]!==undefined?arguments[1]:1;
        vartransfers=arguments.length>2?arguments[2]:undefined;

        if(this.isCancelled){
          return;
        }

        varlastDesiredSize=this.desiredSize;
        this.desiredSize-=size;

        if(lastDesiredSize>0&&this.desiredSize<=0){
          this.sinkCapability=(0,_util.createPromiseCapability)();
          this.ready=this.sinkCapability.promise;
        }

        sendStreamRequest({
          stream:'enqueue',
          chunk:chunk,
          transfers:transfers
        });
      },
      close:functionclose(){
        if(this.isCancelled){
          return;
        }

        this.isCancelled=true;
        sendStreamRequest({
          stream:'close'
        });
        deleteself.streamSinks[streamId];
      },
      error:functionerror(reason){
        if(this.isCancelled){
          return;
        }

        this.isCancelled=true;
        sendStreamRequest({
          stream:'error',
          reason:reason
        });
      },
      sinkCapability:capability,
      onPull:null,
      onCancel:null,
      isCancelled:false,
      desiredSize:desiredSize,
      ready:null
    };
    streamSink.sinkCapability.resolve();
    streamSink.ready=streamSink.sinkCapability.promise;
    this.streamSinks[streamId]=streamSink;
    resolveCall(action[0],[data.data,streamSink],action[1]).then(function(){
      sendStreamRequest({
        stream:'start_complete',
        success:true
      });
    },function(reason){
      sendStreamRequest({
        stream:'start_complete',
        success:false,
        reason:reason
      });
    });
  },
  _processStreamMessage:function_processStreamMessage(data){
    var_this4=this;

    varsourceName=this.sourceName;
    vartargetName=data.sourceName;
    varstreamId=data.streamId;

    varsendStreamResponse=functionsendStreamResponse(_ref2){
      varstream=_ref2.stream,
          success=_ref2.success,
          reason=_ref2.reason;

      _this4.comObj.postMessage({
        sourceName:sourceName,
        targetName:targetName,
        stream:stream,
        success:success,
        streamId:streamId,
        reason:reason
      });
    };

    vardeleteStreamController=functiondeleteStreamController(){
      Promise.all([_this4.streamControllers[data.streamId].startCall,_this4.streamControllers[data.streamId].pullCall,_this4.streamControllers[data.streamId].cancelCall].map(function(capability){
        returncapability&&finalize(capability.promise);
      })).then(function(){
        delete_this4.streamControllers[data.streamId];
      });
    };

    switch(data.stream){
      case'start_complete':
        resolveOrReject(this.streamControllers[data.streamId].startCall,data.success,wrapReason(data.reason));
        break;

      case'pull_complete':
        resolveOrReject(this.streamControllers[data.streamId].pullCall,data.success,wrapReason(data.reason));
        break;

      case'pull':
        if(!this.streamSinks[data.streamId]){
          sendStreamResponse({
            stream:'pull_complete',
            success:true
          });
          break;
        }

        if(this.streamSinks[data.streamId].desiredSize<=0&&data.desiredSize>0){
          this.streamSinks[data.streamId].sinkCapability.resolve();
        }

        this.streamSinks[data.streamId].desiredSize=data.desiredSize;
        resolveCall(this.streamSinks[data.streamId].onPull).then(function(){
          sendStreamResponse({
            stream:'pull_complete',
            success:true
          });
        },function(reason){
          sendStreamResponse({
            stream:'pull_complete',
            success:false,
            reason:reason
          });
        });
        break;

      case'enqueue':
        (0,_util.assert)(this.streamControllers[data.streamId],'enqueueshouldhavestreamcontroller');

        if(!this.streamControllers[data.streamId].isClosed){
          this.streamControllers[data.streamId].controller.enqueue(data.chunk);
        }

        break;

      case'close':
        (0,_util.assert)(this.streamControllers[data.streamId],'closeshouldhavestreamcontroller');

        if(this.streamControllers[data.streamId].isClosed){
          break;
        }

        this.streamControllers[data.streamId].isClosed=true;
        this.streamControllers[data.streamId].controller.close();
        deleteStreamController();
        break;

      case'error':
        (0,_util.assert)(this.streamControllers[data.streamId],'errorshouldhavestreamcontroller');
        this.streamControllers[data.streamId].controller.error(wrapReason(data.reason));
        deleteStreamController();
        break;

      case'cancel_complete':
        resolveOrReject(this.streamControllers[data.streamId].cancelCall,data.success,wrapReason(data.reason));
        deleteStreamController();
        break;

      case'cancel':
        if(!this.streamSinks[data.streamId]){
          break;
        }

        resolveCall(this.streamSinks[data.streamId].onCancel,[wrapReason(data.reason)]).then(function(){
          sendStreamResponse({
            stream:'cancel_complete',
            success:true
          });
        },function(reason){
          sendStreamResponse({
            stream:'cancel_complete',
            success:false,
            reason:reason
          });
        });
        this.streamSinks[data.streamId].sinkCapability.reject(wrapReason(data.reason));
        this.streamSinks[data.streamId].isCancelled=true;
        deletethis.streamSinks[data.streamId];
        break;

      default:
        thrownewError('Unexpectedstreamcase');
    }
  },
  postMessage:functionpostMessage(message,transfers){
    if(transfers&&this.postMessageTransfers){
      this.comObj.postMessage(message,transfers);
    }else{
      this.comObj.postMessage(message);
    }
  },
  destroy:functiondestroy(){
    this.comObj.removeEventListener('message',this._onComObjOnMessage);
  }
};

/***/}),
/*158*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.Metadata=void0;

var_util=__w_pdfjs_require__(1);

var_xml_parser=__w_pdfjs_require__(159);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varMetadata=
/*#__PURE__*/
function(){
  functionMetadata(data){
    _classCallCheck(this,Metadata);

    (0,_util.assert)(typeofdata==='string','Metadata:inputisnotastring');
    data=this._repair(data);
    varparser=new_xml_parser.SimpleXMLParser();
    varxmlDocument=parser.parseFromString(data);
    this._metadata=Object.create(null);

    if(xmlDocument){
      this._parse(xmlDocument);
    }
  }

  _createClass(Metadata,[{
    key:"_repair",
    value:function_repair(data){
      returndata.replace(/^([^<]+)/,'').replace(/>\\376\\377([^<]+)/g,function(all,codes){
        varbytes=codes.replace(/\\([0-3])([0-7])([0-7])/g,function(code,d1,d2,d3){
          returnString.fromCharCode(d1*64+d2*8+d3*1);
        }).replace(/&(amp|apos|gt|lt|quot);/g,function(str,name){
          switch(name){
            case'amp':
              return'&';

            case'apos':
              return'\'';

            case'gt':
              return'>';

            case'lt':
              return'<';

            case'quot':
              return'\"';
          }

          thrownewError("_repair:".concat(name,"isn'tdefined."));
        });
        varchars='';

        for(vari=0,ii=bytes.length;i<ii;i+=2){
          varcode=bytes.charCodeAt(i)*256+bytes.charCodeAt(i+1);

          if(code>=32&&code<127&&code!==60&&code!==62&&code!==38){
            chars+=String.fromCharCode(code);
          }else{
            chars+='&#x'+(0x10000+code).toString(16).substring(1)+';';
          }
        }

        return'>'+chars;
      });
    }
  },{
    key:"_parse",
    value:function_parse(xmlDocument){
      varrdf=xmlDocument.documentElement;

      if(rdf.nodeName.toLowerCase()!=='rdf:rdf'){
        rdf=rdf.firstChild;

        while(rdf&&rdf.nodeName.toLowerCase()!=='rdf:rdf'){
          rdf=rdf.nextSibling;
        }
      }

      varnodeName=rdf?rdf.nodeName.toLowerCase():null;

      if(!rdf||nodeName!=='rdf:rdf'||!rdf.hasChildNodes()){
        return;
      }

      varchildren=rdf.childNodes;

      for(vari=0,ii=children.length;i<ii;i++){
        vardesc=children[i];

        if(desc.nodeName.toLowerCase()!=='rdf:description'){
          continue;
        }

        for(varj=0,jj=desc.childNodes.length;j<jj;j++){
          if(desc.childNodes[j].nodeName.toLowerCase()!=='#text'){
            varentry=desc.childNodes[j];
            varname=entry.nodeName.toLowerCase();
            this._metadata[name]=entry.textContent.trim();
          }
        }
      }
    }
  },{
    key:"get",
    value:functionget(name){
      vardata=this._metadata[name];
      returntypeofdata!=='undefined'?data:null;
    }
  },{
    key:"getAll",
    value:functiongetAll(){
      returnthis._metadata;
    }
  },{
    key:"has",
    value:functionhas(name){
      returntypeofthis._metadata[name]!=='undefined';
    }
  }]);

  returnMetadata;
}();

exports.Metadata=Metadata;

/***/}),
/*159*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.SimpleXMLParser=void0;

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_get(target,property,receiver){if(typeofReflect!=="undefined"&&Reflect.get){_get=Reflect.get;}else{_get=function_get(target,property,receiver){varbase=_superPropBase(target,property);if(!base)return;vardesc=Object.getOwnPropertyDescriptor(base,property);if(desc.get){returndesc.get.call(receiver);}returndesc.value;};}return_get(target,property,receiver||target);}

function_superPropBase(object,property){while(!Object.prototype.hasOwnProperty.call(object,property)){object=_getPrototypeOf(object);if(object===null)break;}returnobject;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varXMLParserErrorCode={
  NoError:0,
  EndOfDocument:-1,
  UnterminatedCdat:-2,
  UnterminatedXmlDeclaration:-3,
  UnterminatedDoctypeDeclaration:-4,
  UnterminatedComment:-5,
  MalformedElement:-6,
  OutOfMemory:-7,
  UnterminatedAttributeValue:-8,
  UnterminatedElement:-9,
  ElementNeverBegun:-10
};

functionisWhitespace(s,index){
  varch=s[index];
  returnch===''||ch==='\n'||ch==='\r'||ch==='\t';
}

functionisWhitespaceString(s){
  for(vari=0,ii=s.length;i<ii;i++){
    if(!isWhitespace(s,i)){
      returnfalse;
    }
  }

  returntrue;
}

varXMLParserBase=
/*#__PURE__*/
function(){
  functionXMLParserBase(){
    _classCallCheck(this,XMLParserBase);
  }

  _createClass(XMLParserBase,[{
    key:"_resolveEntities",
    value:function_resolveEntities(s){
      var_this=this;

      returns.replace(/&([^;]+);/g,function(all,entity){
        if(entity.substring(0,2)==='#x'){
          returnString.fromCharCode(parseInt(entity.substring(2),16));
        }elseif(entity.substring(0,1)==='#'){
          returnString.fromCharCode(parseInt(entity.substring(1),10));
        }

        switch(entity){
          case'lt':
            return'<';

          case'gt':
            return'>';

          case'amp':
            return'&';

          case'quot':
            return'\"';
        }

        return_this.onResolveEntity(entity);
      });
    }
  },{
    key:"_parseContent",
    value:function_parseContent(s,start){
      varpos=start,
          name,
          attributes=[];

      functionskipWs(){
        while(pos<s.length&&isWhitespace(s,pos)){
          ++pos;
        }
      }

      while(pos<s.length&&!isWhitespace(s,pos)&&s[pos]!=='>'&&s[pos]!=='/'){
        ++pos;
      }

      name=s.substring(start,pos);
      skipWs();

      while(pos<s.length&&s[pos]!=='>'&&s[pos]!=='/'&&s[pos]!=='?'){
        skipWs();
        varattrName='',
            attrValue='';

        while(pos<s.length&&!isWhitespace(s,pos)&&s[pos]!=='='){
          attrName+=s[pos];
          ++pos;
        }

        skipWs();

        if(s[pos]!=='='){
          returnnull;
        }

        ++pos;
        skipWs();
        varattrEndChar=s[pos];

        if(attrEndChar!=='\"'&&attrEndChar!=='\''){
          returnnull;
        }

        varattrEndIndex=s.indexOf(attrEndChar,++pos);

        if(attrEndIndex<0){
          returnnull;
        }

        attrValue=s.substring(pos,attrEndIndex);
        attributes.push({
          name:attrName,
          value:this._resolveEntities(attrValue)
        });
        pos=attrEndIndex+1;
        skipWs();
      }

      return{
        name:name,
        attributes:attributes,
        parsed:pos-start
      };
    }
  },{
    key:"_parseProcessingInstruction",
    value:function_parseProcessingInstruction(s,start){
      varpos=start,
          name,
          value;

      functionskipWs(){
        while(pos<s.length&&isWhitespace(s,pos)){
          ++pos;
        }
      }

      while(pos<s.length&&!isWhitespace(s,pos)&&s[pos]!=='>'&&s[pos]!=='/'){
        ++pos;
      }

      name=s.substring(start,pos);
      skipWs();
      varattrStart=pos;

      while(pos<s.length&&(s[pos]!=='?'||s[pos+1]!=='>')){
        ++pos;
      }

      value=s.substring(attrStart,pos);
      return{
        name:name,
        value:value,
        parsed:pos-start
      };
    }
  },{
    key:"parseXml",
    value:functionparseXml(s){
      vari=0;

      while(i<s.length){
        varch=s[i];
        varj=i;

        if(ch==='<'){
          ++j;
          varch2=s[j];
          varq=void0;

          switch(ch2){
            case'/':
              ++j;
              q=s.indexOf('>',j);

              if(q<0){
                this.onError(XMLParserErrorCode.UnterminatedElement);
                return;
              }

              this.onEndElement(s.substring(j,q));
              j=q+1;
              break;

            case'?':
              ++j;

              varpi=this._parseProcessingInstruction(s,j);

              if(s.substring(j+pi.parsed,j+pi.parsed+2)!=='?>'){
                this.onError(XMLParserErrorCode.UnterminatedXmlDeclaration);
                return;
              }

              this.onPi(pi.name,pi.value);
              j+=pi.parsed+2;
              break;

            case'!':
              if(s.substring(j+1,j+3)==='--'){
                q=s.indexOf('-->',j+3);

                if(q<0){
                  this.onError(XMLParserErrorCode.UnterminatedComment);
                  return;
                }

                this.onComment(s.substring(j+3,q));
                j=q+3;
              }elseif(s.substring(j+1,j+8)==='[CDATA['){
                q=s.indexOf(']]>',j+8);

                if(q<0){
                  this.onError(XMLParserErrorCode.UnterminatedCdat);
                  return;
                }

                this.onCdata(s.substring(j+8,q));
                j=q+3;
              }elseif(s.substring(j+1,j+8)==='DOCTYPE'){
                varq2=s.indexOf('[',j+8);
                varcomplexDoctype=false;
                q=s.indexOf('>',j+8);

                if(q<0){
                  this.onError(XMLParserErrorCode.UnterminatedDoctypeDeclaration);
                  return;
                }

                if(q2>0&&q>q2){
                  q=s.indexOf(']>',j+8);

                  if(q<0){
                    this.onError(XMLParserErrorCode.UnterminatedDoctypeDeclaration);
                    return;
                  }

                  complexDoctype=true;
                }

                vardoctypeContent=s.substring(j+8,q+(complexDoctype?1:0));
                this.onDoctype(doctypeContent);
                j=q+(complexDoctype?2:1);
              }else{
                this.onError(XMLParserErrorCode.MalformedElement);
                return;
              }

              break;

            default:
              varcontent=this._parseContent(s,j);

              if(content===null){
                this.onError(XMLParserErrorCode.MalformedElement);
                return;
              }

              varisClosed=false;

              if(s.substring(j+content.parsed,j+content.parsed+2)==='/>'){
                isClosed=true;
              }elseif(s.substring(j+content.parsed,j+content.parsed+1)!=='>'){
                this.onError(XMLParserErrorCode.UnterminatedElement);
                return;
              }

              this.onBeginElement(content.name,content.attributes,isClosed);
              j+=content.parsed+(isClosed?2:1);
              break;
          }
        }else{
          while(j<s.length&&s[j]!=='<'){
            j++;
          }

          vartext=s.substring(i,j);
          this.onText(this._resolveEntities(text));
        }

        i=j;
      }
    }
  },{
    key:"onResolveEntity",
    value:functiononResolveEntity(name){
      return"&".concat(name,";");
    }
  },{
    key:"onPi",
    value:functiononPi(name,value){}
  },{
    key:"onComment",
    value:functiononComment(text){}
  },{
    key:"onCdata",
    value:functiononCdata(text){}
  },{
    key:"onDoctype",
    value:functiononDoctype(doctypeContent){}
  },{
    key:"onText",
    value:functiononText(text){}
  },{
    key:"onBeginElement",
    value:functiononBeginElement(name,attributes,isEmpty){}
  },{
    key:"onEndElement",
    value:functiononEndElement(name){}
  },{
    key:"onError",
    value:functiononError(code){}
  }]);

  returnXMLParserBase;
}();

varSimpleDOMNode=
/*#__PURE__*/
function(){
  functionSimpleDOMNode(nodeName,nodeValue){
    _classCallCheck(this,SimpleDOMNode);

    this.nodeName=nodeName;
    this.nodeValue=nodeValue;
    Object.defineProperty(this,'parentNode',{
      value:null,
      writable:true
    });
  }

  _createClass(SimpleDOMNode,[{
    key:"hasChildNodes",
    value:functionhasChildNodes(){
      returnthis.childNodes&&this.childNodes.length>0;
    }
  },{
    key:"firstChild",
    get:functionget(){
      returnthis.childNodes&&this.childNodes[0];
    }
  },{
    key:"nextSibling",
    get:functionget(){
      varchildNodes=this.parentNode.childNodes;

      if(!childNodes){
        returnundefined;
      }

      varindex=childNodes.indexOf(this);

      if(index===-1){
        returnundefined;
      }

      returnchildNodes[index+1];
    }
  },{
    key:"textContent",
    get:functionget(){
      if(!this.childNodes){
        returnthis.nodeValue||'';
      }

      returnthis.childNodes.map(function(child){
        returnchild.textContent;
      }).join('');
    }
  }]);

  returnSimpleDOMNode;
}();

varSimpleXMLParser=
/*#__PURE__*/
function(_XMLParserBase){
  _inherits(SimpleXMLParser,_XMLParserBase);

  functionSimpleXMLParser(){
    var_this2;

    _classCallCheck(this,SimpleXMLParser);

    _this2=_possibleConstructorReturn(this,_getPrototypeOf(SimpleXMLParser).call(this));
    _this2._currentFragment=null;
    _this2._stack=null;
    _this2._errorCode=XMLParserErrorCode.NoError;
    return_this2;
  }

  _createClass(SimpleXMLParser,[{
    key:"parseFromString",
    value:functionparseFromString(data){
      this._currentFragment=[];
      this._stack=[];
      this._errorCode=XMLParserErrorCode.NoError;
      this.parseXml(data);

      if(this._errorCode!==XMLParserErrorCode.NoError){
        returnundefined;
      }

      var_this$_currentFragmen=_slicedToArray(this._currentFragment,1),
          documentElement=_this$_currentFragmen[0];

      if(!documentElement){
        returnundefined;
      }

      return{
        documentElement:documentElement
      };
    }
  },{
    key:"onResolveEntity",
    value:functiononResolveEntity(name){
      switch(name){
        case'apos':
          return'\'';
      }

      return_get(_getPrototypeOf(SimpleXMLParser.prototype),"onResolveEntity",this).call(this,name);
    }
  },{
    key:"onText",
    value:functiononText(text){
      if(isWhitespaceString(text)){
        return;
      }

      varnode=newSimpleDOMNode('#text',text);

      this._currentFragment.push(node);
    }
  },{
    key:"onCdata",
    value:functiononCdata(text){
      varnode=newSimpleDOMNode('#text',text);

      this._currentFragment.push(node);
    }
  },{
    key:"onBeginElement",
    value:functiononBeginElement(name,attributes,isEmpty){
      varnode=newSimpleDOMNode(name);
      node.childNodes=[];

      this._currentFragment.push(node);

      if(isEmpty){
        return;
      }

      this._stack.push(this._currentFragment);

      this._currentFragment=node.childNodes;
    }
  },{
    key:"onEndElement",
    value:functiononEndElement(name){
      this._currentFragment=this._stack.pop()||[];
      varlastElement=this._currentFragment[this._currentFragment.length-1];

      if(!lastElement){
        return;
      }

      for(vari=0,ii=lastElement.childNodes.length;i<ii;i++){
        lastElement.childNodes[i].parentNode=lastElement;
      }
    }
  },{
    key:"onError",
    value:functiononError(code){
      this._errorCode=code;
    }
  }]);

  returnSimpleXMLParser;
}(XMLParserBase);

exports.SimpleXMLParser=SimpleXMLParser;

/***/}),
/*160*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFDataTransportStream=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{default:obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varPDFDataTransportStream=
/*#__PURE__*/
function(){
  functionPDFDataTransportStream(params,pdfDataRangeTransport){
    var_this=this;

    _classCallCheck(this,PDFDataTransportStream);

    (0,_util.assert)(pdfDataRangeTransport);
    this._queuedChunks=[];
    this._progressiveDone=params.progressiveDone||false;
    varinitialData=params.initialData;

    if(initialData&&initialData.length>0){
      varbuffer=newUint8Array(initialData).buffer;

      this._queuedChunks.push(buffer);
    }

    this._pdfDataRangeTransport=pdfDataRangeTransport;
    this._isStreamingSupported=!params.disableStream;
    this._isRangeSupported=!params.disableRange;
    this._contentLength=params.length;
    this._fullRequestReader=null;
    this._rangeReaders=[];

    this._pdfDataRangeTransport.addRangeListener(function(begin,chunk){
      _this._onReceiveData({
        begin:begin,
        chunk:chunk
      });
    });

    this._pdfDataRangeTransport.addProgressListener(function(loaded,total){
      _this._onProgress({
        loaded:loaded,
        total:total
      });
    });

    this._pdfDataRangeTransport.addProgressiveReadListener(function(chunk){
      _this._onReceiveData({
        chunk:chunk
      });
    });

    this._pdfDataRangeTransport.addProgressiveDoneListener(function(){
      _this._onProgressiveDone();
    });

    this._pdfDataRangeTransport.transportReady();
  }

  _createClass(PDFDataTransportStream,[{
    key:"_onReceiveData",
    value:function_onReceiveData(args){
      varbuffer=newUint8Array(args.chunk).buffer;

      if(args.begin===undefined){
        if(this._fullRequestReader){
          this._fullRequestReader._enqueue(buffer);
        }else{
          this._queuedChunks.push(buffer);
        }
      }else{
        varfound=this._rangeReaders.some(function(rangeReader){
          if(rangeReader._begin!==args.begin){
            returnfalse;
          }

          rangeReader._enqueue(buffer);

          returntrue;
        });

        (0,_util.assert)(found);
      }
    }
  },{
    key:"_onProgress",
    value:function_onProgress(evt){
      if(evt.total===undefined){
        varfirstReader=this._rangeReaders[0];

        if(firstReader&&firstReader.onProgress){
          firstReader.onProgress({
            loaded:evt.loaded
          });
        }
      }else{
        varfullReader=this._fullRequestReader;

        if(fullReader&&fullReader.onProgress){
          fullReader.onProgress({
            loaded:evt.loaded,
            total:evt.total
          });
        }
      }
    }
  },{
    key:"_onProgressiveDone",
    value:function_onProgressiveDone(){
      if(this._fullRequestReader){
        this._fullRequestReader.progressiveDone();
      }

      this._progressiveDone=true;
    }
  },{
    key:"_removeRangeReader",
    value:function_removeRangeReader(reader){
      vari=this._rangeReaders.indexOf(reader);

      if(i>=0){
        this._rangeReaders.splice(i,1);
      }
    }
  },{
    key:"getFullReader",
    value:functiongetFullReader(){
      (0,_util.assert)(!this._fullRequestReader);
      varqueuedChunks=this._queuedChunks;
      this._queuedChunks=null;
      returnnewPDFDataTransportStreamReader(this,queuedChunks,this._progressiveDone);
    }
  },{
    key:"getRangeReader",
    value:functiongetRangeReader(begin,end){
      if(end<=this._progressiveDataLength){
        returnnull;
      }

      varreader=newPDFDataTransportStreamRangeReader(this,begin,end);

      this._pdfDataRangeTransport.requestDataRange(begin,end);

      this._rangeReaders.push(reader);

      returnreader;
    }
  },{
    key:"cancelAllRequests",
    value:functioncancelAllRequests(reason){
      if(this._fullRequestReader){
        this._fullRequestReader.cancel(reason);
      }

      varreaders=this._rangeReaders.slice(0);

      readers.forEach(function(rangeReader){
        rangeReader.cancel(reason);
      });

      this._pdfDataRangeTransport.abort();
    }
  },{
    key:"_progressiveDataLength",
    get:functionget(){
      returnthis._fullRequestReader?this._fullRequestReader._loaded:0;
    }
  }]);

  returnPDFDataTransportStream;
}();

exports.PDFDataTransportStream=PDFDataTransportStream;

varPDFDataTransportStreamReader=
/*#__PURE__*/
function(){
  functionPDFDataTransportStreamReader(stream,queuedChunks){
    varprogressiveDone=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

    _classCallCheck(this,PDFDataTransportStreamReader);

    this._stream=stream;
    this._done=progressiveDone||false;
    this._filename=null;
    this._queuedChunks=queuedChunks||[];
    this._loaded=0;
    var_iteratorNormalCompletion=true;
    var_didIteratorError=false;
    var_iteratorError=undefined;

    try{
      for(var_iterator=this._queuedChunks[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
        varchunk=_step.value;
        this._loaded+=chunk.byteLength;
      }
    }catch(err){
      _didIteratorError=true;
      _iteratorError=err;
    }finally{
      try{
        if(!_iteratorNormalCompletion&&_iterator["return"]!=null){
          _iterator["return"]();
        }
      }finally{
        if(_didIteratorError){
          throw_iteratorError;
        }
      }
    }

    this._requests=[];
    this._headersReady=Promise.resolve();
    stream._fullRequestReader=this;
    this.onProgress=null;
  }

  _createClass(PDFDataTransportStreamReader,[{
    key:"_enqueue",
    value:function_enqueue(chunk){
      if(this._done){
        return;
      }

      if(this._requests.length>0){
        varrequestCapability=this._requests.shift();

        requestCapability.resolve({
          value:chunk,
          done:false
        });
      }else{
        this._queuedChunks.push(chunk);
      }

      this._loaded+=chunk.byteLength;
    }
  },{
    key:"read",
    value:function(){
      var_read=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        varchunk,requestCapability;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                if(!(this._queuedChunks.length>0)){
                  _context.next=3;
                  break;
                }

                chunk=this._queuedChunks.shift();
                return_context.abrupt("return",{
                  value:chunk,
                  done:false
                });

              case3:
                if(!this._done){
                  _context.next=5;
                  break;
                }

                return_context.abrupt("return",{
                  value:undefined,
                  done:true
                });

              case5:
                requestCapability=(0,_util.createPromiseCapability)();

                this._requests.push(requestCapability);

                return_context.abrupt("return",requestCapability.promise);

              case8:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      functionread(){
        return_read.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      this._done=true;

      this._requests.forEach(function(requestCapability){
        requestCapability.resolve({
          value:undefined,
          done:true
        });
      });

      this._requests=[];
    }
  },{
    key:"progressiveDone",
    value:functionprogressiveDone(){
      if(this._done){
        return;
      }

      this._done=true;
    }
  },{
    key:"headersReady",
    get:functionget(){
      returnthis._headersReady;
    }
  },{
    key:"filename",
    get:functionget(){
      returnthis._filename;
    }
  },{
    key:"isRangeSupported",
    get:functionget(){
      returnthis._stream._isRangeSupported;
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnthis._stream._isStreamingSupported;
    }
  },{
    key:"contentLength",
    get:functionget(){
      returnthis._stream._contentLength;
    }
  }]);

  returnPDFDataTransportStreamReader;
}();

varPDFDataTransportStreamRangeReader=
/*#__PURE__*/
function(){
  functionPDFDataTransportStreamRangeReader(stream,begin,end){
    _classCallCheck(this,PDFDataTransportStreamRangeReader);

    this._stream=stream;
    this._begin=begin;
    this._end=end;
    this._queuedChunk=null;
    this._requests=[];
    this._done=false;
    this.onProgress=null;
  }

  _createClass(PDFDataTransportStreamRangeReader,[{
    key:"_enqueue",
    value:function_enqueue(chunk){
      if(this._done){
        return;
      }

      if(this._requests.length===0){
        this._queuedChunk=chunk;
      }else{
        varrequestsCapability=this._requests.shift();

        requestsCapability.resolve({
          value:chunk,
          done:false
        });

        this._requests.forEach(function(requestCapability){
          requestCapability.resolve({
            value:undefined,
            done:true
          });
        });

        this._requests=[];
      }

      this._done=true;

      this._stream._removeRangeReader(this);
    }
  },{
    key:"read",
    value:function(){
      var_read2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(){
        varchunk,requestCapability;
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                if(!this._queuedChunk){
                  _context2.next=4;
                  break;
                }

                chunk=this._queuedChunk;
                this._queuedChunk=null;
                return_context2.abrupt("return",{
                  value:chunk,
                  done:false
                });

              case4:
                if(!this._done){
                  _context2.next=6;
                  break;
                }

                return_context2.abrupt("return",{
                  value:undefined,
                  done:true
                });

              case6:
                requestCapability=(0,_util.createPromiseCapability)();

                this._requests.push(requestCapability);

                return_context2.abrupt("return",requestCapability.promise);

              case9:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      functionread(){
        return_read2.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      this._done=true;

      this._requests.forEach(function(requestCapability){
        requestCapability.resolve({
          value:undefined,
          done:true
        });
      });

      this._requests=[];

      this._stream._removeRangeReader(this);
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnfalse;
    }
  }]);

  returnPDFDataTransportStreamRangeReader;
}();

/***/}),
/*161*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.WebGLContext=void0;

var_util=__w_pdfjs_require__(1);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varWebGLContext=
/*#__PURE__*/
function(){
  functionWebGLContext(_ref){
    var_ref$enable=_ref.enable,
        enable=_ref$enable===void0?false:_ref$enable;

    _classCallCheck(this,WebGLContext);

    this._enabled=enable===true;
  }

  _createClass(WebGLContext,[{
    key:"composeSMask",
    value:functioncomposeSMask(_ref2){
      varlayer=_ref2.layer,
          mask=_ref2.mask,
          properties=_ref2.properties;
      returnWebGLUtils.composeSMask(layer,mask,properties);
    }
  },{
    key:"drawFigures",
    value:functiondrawFigures(_ref3){
      varwidth=_ref3.width,
          height=_ref3.height,
          backgroundColor=_ref3.backgroundColor,
          figures=_ref3.figures,
          context=_ref3.context;
      returnWebGLUtils.drawFigures(width,height,backgroundColor,figures,context);
    }
  },{
    key:"clear",
    value:functionclear(){
      WebGLUtils.cleanup();
    }
  },{
    key:"isEnabled",
    get:functionget(){
      varenabled=this._enabled;

      if(enabled){
        enabled=WebGLUtils.tryInitGL();
      }

      return(0,_util.shadow)(this,'isEnabled',enabled);
    }
  }]);

  returnWebGLContext;
}();

exports.WebGLContext=WebGLContext;

varWebGLUtils=functionWebGLUtilsClosure(){
  functionloadShader(gl,code,shaderType){
    varshader=gl.createShader(shaderType);
    gl.shaderSource(shader,code);
    gl.compileShader(shader);
    varcompiled=gl.getShaderParameter(shader,gl.COMPILE_STATUS);

    if(!compiled){
      varerrorMsg=gl.getShaderInfoLog(shader);
      thrownewError('Errorduringshadercompilation:'+errorMsg);
    }

    returnshader;
  }

  functioncreateVertexShader(gl,code){
    returnloadShader(gl,code,gl.VERTEX_SHADER);
  }

  functioncreateFragmentShader(gl,code){
    returnloadShader(gl,code,gl.FRAGMENT_SHADER);
  }

  functioncreateProgram(gl,shaders){
    varprogram=gl.createProgram();

    for(vari=0,ii=shaders.length;i<ii;++i){
      gl.attachShader(program,shaders[i]);
    }

    gl.linkProgram(program);
    varlinked=gl.getProgramParameter(program,gl.LINK_STATUS);

    if(!linked){
      varerrorMsg=gl.getProgramInfoLog(program);
      thrownewError('Errorduringprogramlinking:'+errorMsg);
    }

    returnprogram;
  }

  functioncreateTexture(gl,image,textureId){
    gl.activeTexture(textureId);
    vartexture=gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D,texture);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_S,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_WRAP_T,gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MIN_FILTER,gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D,gl.TEXTURE_MAG_FILTER,gl.NEAREST);
    gl.texImage2D(gl.TEXTURE_2D,0,gl.RGBA,gl.RGBA,gl.UNSIGNED_BYTE,image);
    returntexture;
  }

  varcurrentGL,currentCanvas;

  functiongenerateGL(){
    if(currentGL){
      return;
    }

    currentCanvas=document.createElement('canvas');
    currentGL=currentCanvas.getContext('webgl',{
      premultipliedalpha:false
    });
  }

  varsmaskVertexShaderCode='\
  attributevec2a_position;                                   \
  attributevec2a_texCoord;                                   \
                                                                \
  uniformvec2u_resolution;                                   \
                                                                \
  varyingvec2v_texCoord;                                     \
                                                                \
  voidmain(){                                                \
    vec2clipSpace=(a_position/u_resolution)*2.0-1.0;  \
    gl_Position=vec4(clipSpace*vec2(1,-1),0,1);         \
                                                                \
    v_texCoord=a_texCoord;                                   \
  }                                                            ';
  varsmaskFragmentShaderCode='\
  precisionmediumpfloat;                                     \
                                                                \
  uniformvec4u_backdrop;                                     \
  uniformintu_subtype;                                       \
  uniformsampler2Du_image;                                   \
  uniformsampler2Du_mask;                                    \
                                                                \
  varyingvec2v_texCoord;                                     \
                                                                \
  voidmain(){                                                \
    vec4imageColor=texture2D(u_image,v_texCoord);          \
    vec4maskColor=texture2D(u_mask,v_texCoord);            \
    if(u_backdrop.a>0.0){                                  \
      maskColor.rgb=maskColor.rgb*maskColor.a+            \
                      u_backdrop.rgb*(1.0-maskColor.a);    \
    }                                                          \
    floatlum;                                                 \
    if(u_subtype==0){                                      \
      lum=maskColor.a;                                       \
    }else{                                                   \
      lum=maskColor.r*0.3+maskColor.g*0.59+           \
            maskColor.b*0.11;                                \
    }                                                          \
    imageColor.a*=lum;                                       \
    imageColor.rgb*=imageColor.a;                            \
    gl_FragColor=imageColor;                                 \
  }                                                            ';
  varsmaskCache=null;

  functioninitSmaskGL(){
    varcanvas,gl;
    generateGL();
    canvas=currentCanvas;
    currentCanvas=null;
    gl=currentGL;
    currentGL=null;
    varvertexShader=createVertexShader(gl,smaskVertexShaderCode);
    varfragmentShader=createFragmentShader(gl,smaskFragmentShaderCode);
    varprogram=createProgram(gl,[vertexShader,fragmentShader]);
    gl.useProgram(program);
    varcache={};
    cache.gl=gl;
    cache.canvas=canvas;
    cache.resolutionLocation=gl.getUniformLocation(program,'u_resolution');
    cache.positionLocation=gl.getAttribLocation(program,'a_position');
    cache.backdropLocation=gl.getUniformLocation(program,'u_backdrop');
    cache.subtypeLocation=gl.getUniformLocation(program,'u_subtype');
    vartexCoordLocation=gl.getAttribLocation(program,'a_texCoord');
    vartexLayerLocation=gl.getUniformLocation(program,'u_image');
    vartexMaskLocation=gl.getUniformLocation(program,'u_mask');
    vartexCoordBuffer=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,texCoordBuffer);
    gl.bufferData(gl.ARRAY_BUFFER,newFloat32Array([0.0,0.0,1.0,0.0,0.0,1.0,0.0,1.0,1.0,0.0,1.0,1.0]),gl.STATIC_DRAW);
    gl.enableVertexAttribArray(texCoordLocation);
    gl.vertexAttribPointer(texCoordLocation,2,gl.FLOAT,false,0,0);
    gl.uniform1i(texLayerLocation,0);
    gl.uniform1i(texMaskLocation,1);
    smaskCache=cache;
  }

  functioncomposeSMask(layer,mask,properties){
    varwidth=layer.width,
        height=layer.height;

    if(!smaskCache){
      initSmaskGL();
    }

    varcache=smaskCache,
        canvas=cache.canvas,
        gl=cache.gl;
    canvas.width=width;
    canvas.height=height;
    gl.viewport(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight);
    gl.uniform2f(cache.resolutionLocation,width,height);

    if(properties.backdrop){
      gl.uniform4f(cache.resolutionLocation,properties.backdrop[0],properties.backdrop[1],properties.backdrop[2],1);
    }else{
      gl.uniform4f(cache.resolutionLocation,0,0,0,0);
    }

    gl.uniform1i(cache.subtypeLocation,properties.subtype==='Luminosity'?1:0);
    vartexture=createTexture(gl,layer,gl.TEXTURE0);
    varmaskTexture=createTexture(gl,mask,gl.TEXTURE1);
    varbuffer=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,buffer);
    gl.bufferData(gl.ARRAY_BUFFER,newFloat32Array([0,0,width,0,0,height,0,height,width,0,width,height]),gl.STATIC_DRAW);
    gl.enableVertexAttribArray(cache.positionLocation);
    gl.vertexAttribPointer(cache.positionLocation,2,gl.FLOAT,false,0,0);
    gl.clearColor(0,0,0,0);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.ONE,gl.ONE_MINUS_SRC_ALPHA);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.TRIANGLES,0,6);
    gl.flush();
    gl.deleteTexture(texture);
    gl.deleteTexture(maskTexture);
    gl.deleteBuffer(buffer);
    returncanvas;
  }

  varfiguresVertexShaderCode='\
  attributevec2a_position;                                   \
  attributevec3a_color;                                      \
                                                                \
  uniformvec2u_resolution;                                   \
  uniformvec2u_scale;                                        \
  uniformvec2u_offset;                                       \
                                                                \
  varyingvec4v_color;                                        \
                                                                \
  voidmain(){                                                \
    vec2position=(a_position+u_offset)*u_scale;         \
    vec2clipSpace=(position/u_resolution)*2.0-1.0;    \
    gl_Position=vec4(clipSpace*vec2(1,-1),0,1);         \
                                                                \
    v_color=vec4(a_color/255.0,1.0);                      \
  }                                                            ';
  varfiguresFragmentShaderCode='\
  precisionmediumpfloat;                                     \
                                                                \
  varyingvec4v_color;                                        \
                                                                \
  voidmain(){                                                \
    gl_FragColor=v_color;                                    \
  }                                                            ';
  varfiguresCache=null;

  functioninitFiguresGL(){
    varcanvas,gl;
    generateGL();
    canvas=currentCanvas;
    currentCanvas=null;
    gl=currentGL;
    currentGL=null;
    varvertexShader=createVertexShader(gl,figuresVertexShaderCode);
    varfragmentShader=createFragmentShader(gl,figuresFragmentShaderCode);
    varprogram=createProgram(gl,[vertexShader,fragmentShader]);
    gl.useProgram(program);
    varcache={};
    cache.gl=gl;
    cache.canvas=canvas;
    cache.resolutionLocation=gl.getUniformLocation(program,'u_resolution');
    cache.scaleLocation=gl.getUniformLocation(program,'u_scale');
    cache.offsetLocation=gl.getUniformLocation(program,'u_offset');
    cache.positionLocation=gl.getAttribLocation(program,'a_position');
    cache.colorLocation=gl.getAttribLocation(program,'a_color');
    figuresCache=cache;
  }

  functiondrawFigures(width,height,backgroundColor,figures,context){
    if(!figuresCache){
      initFiguresGL();
    }

    varcache=figuresCache,
        canvas=cache.canvas,
        gl=cache.gl;
    canvas.width=width;
    canvas.height=height;
    gl.viewport(0,0,gl.drawingBufferWidth,gl.drawingBufferHeight);
    gl.uniform2f(cache.resolutionLocation,width,height);
    varcount=0;
    vari,ii,rows;

    for(i=0,ii=figures.length;i<ii;i++){
      switch(figures[i].type){
        case'lattice':
          rows=figures[i].coords.length/figures[i].verticesPerRow|0;
          count+=(rows-1)*(figures[i].verticesPerRow-1)*6;
          break;

        case'triangles':
          count+=figures[i].coords.length;
          break;
      }
    }

    varcoords=newFloat32Array(count*2);
    varcolors=newUint8Array(count*3);
    varcoordsMap=context.coords,
        colorsMap=context.colors;
    varpIndex=0,
        cIndex=0;

    for(i=0,ii=figures.length;i<ii;i++){
      varfigure=figures[i],
          ps=figure.coords,
          cs=figure.colors;

      switch(figure.type){
        case'lattice':
          varcols=figure.verticesPerRow;
          rows=ps.length/cols|0;

          for(varrow=1;row<rows;row++){
            varoffset=row*cols+1;

            for(varcol=1;col<cols;col++,offset++){
              coords[pIndex]=coordsMap[ps[offset-cols-1]];
              coords[pIndex+1]=coordsMap[ps[offset-cols-1]+1];
              coords[pIndex+2]=coordsMap[ps[offset-cols]];
              coords[pIndex+3]=coordsMap[ps[offset-cols]+1];
              coords[pIndex+4]=coordsMap[ps[offset-1]];
              coords[pIndex+5]=coordsMap[ps[offset-1]+1];
              colors[cIndex]=colorsMap[cs[offset-cols-1]];
              colors[cIndex+1]=colorsMap[cs[offset-cols-1]+1];
              colors[cIndex+2]=colorsMap[cs[offset-cols-1]+2];
              colors[cIndex+3]=colorsMap[cs[offset-cols]];
              colors[cIndex+4]=colorsMap[cs[offset-cols]+1];
              colors[cIndex+5]=colorsMap[cs[offset-cols]+2];
              colors[cIndex+6]=colorsMap[cs[offset-1]];
              colors[cIndex+7]=colorsMap[cs[offset-1]+1];
              colors[cIndex+8]=colorsMap[cs[offset-1]+2];
              coords[pIndex+6]=coords[pIndex+2];
              coords[pIndex+7]=coords[pIndex+3];
              coords[pIndex+8]=coords[pIndex+4];
              coords[pIndex+9]=coords[pIndex+5];
              coords[pIndex+10]=coordsMap[ps[offset]];
              coords[pIndex+11]=coordsMap[ps[offset]+1];
              colors[cIndex+9]=colors[cIndex+3];
              colors[cIndex+10]=colors[cIndex+4];
              colors[cIndex+11]=colors[cIndex+5];
              colors[cIndex+12]=colors[cIndex+6];
              colors[cIndex+13]=colors[cIndex+7];
              colors[cIndex+14]=colors[cIndex+8];
              colors[cIndex+15]=colorsMap[cs[offset]];
              colors[cIndex+16]=colorsMap[cs[offset]+1];
              colors[cIndex+17]=colorsMap[cs[offset]+2];
              pIndex+=12;
              cIndex+=18;
            }
          }

          break;

        case'triangles':
          for(varj=0,jj=ps.length;j<jj;j++){
            coords[pIndex]=coordsMap[ps[j]];
            coords[pIndex+1]=coordsMap[ps[j]+1];
            colors[cIndex]=colorsMap[cs[j]];
            colors[cIndex+1]=colorsMap[cs[j]+1];
            colors[cIndex+2]=colorsMap[cs[j]+2];
            pIndex+=2;
            cIndex+=3;
          }

          break;
      }
    }

    if(backgroundColor){
      gl.clearColor(backgroundColor[0]/255,backgroundColor[1]/255,backgroundColor[2]/255,1.0);
    }else{
      gl.clearColor(0,0,0,0);
    }

    gl.clear(gl.COLOR_BUFFER_BIT);
    varcoordsBuffer=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,coordsBuffer);
    gl.bufferData(gl.ARRAY_BUFFER,coords,gl.STATIC_DRAW);
    gl.enableVertexAttribArray(cache.positionLocation);
    gl.vertexAttribPointer(cache.positionLocation,2,gl.FLOAT,false,0,0);
    varcolorsBuffer=gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER,colorsBuffer);
    gl.bufferData(gl.ARRAY_BUFFER,colors,gl.STATIC_DRAW);
    gl.enableVertexAttribArray(cache.colorLocation);
    gl.vertexAttribPointer(cache.colorLocation,3,gl.UNSIGNED_BYTE,false,0,0);
    gl.uniform2f(cache.scaleLocation,context.scaleX,context.scaleY);
    gl.uniform2f(cache.offsetLocation,context.offsetX,context.offsetY);
    gl.drawArrays(gl.TRIANGLES,0,count);
    gl.flush();
    gl.deleteBuffer(coordsBuffer);
    gl.deleteBuffer(colorsBuffer);
    returncanvas;
  }

  return{
    tryInitGL:functiontryInitGL(){
      try{
        generateGL();
        return!!currentGL;
      }catch(ex){}

      returnfalse;
    },
    composeSMask:composeSMask,
    drawFigures:drawFigures,
    cleanup:functioncleanup(){
      if(smaskCache&&smaskCache.canvas){
        smaskCache.canvas.width=0;
        smaskCache.canvas.height=0;
      }

      if(figuresCache&&figuresCache.canvas){
        figuresCache.canvas.width=0;
        figuresCache.canvas.height=0;
      }

      smaskCache=null;
      figuresCache=null;
    }
  };
}();

/***/}),
/*162*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.renderTextLayer=void0;

var_util=__w_pdfjs_require__(1);

var_global_scope=_interopRequireDefault(__w_pdfjs_require__(3));

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

varrenderTextLayer=functionrenderTextLayerClosure(){
  varMAX_TEXT_DIVS_TO_RENDER=100000;
  varNonWhitespaceRegexp=/\S/;

  functionisAllWhitespace(str){
    return!NonWhitespaceRegexp.test(str);
  }

  varstyleBuf=['left:',0,'px;top:',0,'px;font-size:',0,'px;font-family:','',';'];

  functionappendText(task,geom,styles){
    vartextDiv=document.createElement('span');
    vartextDivProperties={
      style:null,
      angle:0,
      canvasWidth:0,
      isWhitespace:false,
      originalTransform:null,
      paddingBottom:0,
      paddingLeft:0,
      paddingRight:0,
      paddingTop:0,
      scale:1
    };

    task._textDivs.push(textDiv);

    if(isAllWhitespace(geom.str)){
      textDivProperties.isWhitespace=true;

      task._textDivProperties.set(textDiv,textDivProperties);

      return;
    }

    vartx=_util.Util.transform(task._viewport.transform,geom.transform);

    varangle=Math.atan2(tx[1],tx[0]);
    varstyle=styles[geom.fontName];

    if(style.vertical){
      angle+=Math.PI/2;
    }

    varfontHeight=Math.sqrt(tx[2]*tx[2]+tx[3]*tx[3]);
    varfontAscent=fontHeight;

    if(style.ascent){
      fontAscent=style.ascent*fontAscent;
    }elseif(style.descent){
      fontAscent=(1+style.descent)*fontAscent;
    }

    varleft;
    vartop;

    if(angle===0){
      left=tx[4];
      top=tx[5]-fontAscent;
    }else{
      left=tx[4]+fontAscent*Math.sin(angle);
      top=tx[5]-fontAscent*Math.cos(angle);
    }

    styleBuf[1]=left;
    styleBuf[3]=top;
    styleBuf[5]=fontHeight;
    styleBuf[7]=style.fontFamily;
    textDivProperties.style=styleBuf.join('');
    textDiv.setAttribute('style',textDivProperties.style);
    textDiv.textContent=geom.str;

    if(task._fontInspectorEnabled){
      textDiv.dataset.fontName=geom.fontName;
    }

    if(angle!==0){
      textDivProperties.angle=angle*(180/Math.PI);
    }

    if(geom.str.length>1){
      if(style.vertical){
        textDivProperties.canvasWidth=geom.height*task._viewport.scale;
      }else{
        textDivProperties.canvasWidth=geom.width*task._viewport.scale;
      }
    }

    task._textDivProperties.set(textDiv,textDivProperties);

    if(task._textContentStream){
      task._layoutText(textDiv);
    }

    if(task._enhanceTextSelection){
      varangleCos=1,
          angleSin=0;

      if(angle!==0){
        angleCos=Math.cos(angle);
        angleSin=Math.sin(angle);
      }

      vardivWidth=(style.vertical?geom.height:geom.width)*task._viewport.scale;
      vardivHeight=fontHeight;
      varm,b;

      if(angle!==0){
        m=[angleCos,angleSin,-angleSin,angleCos,left,top];
        b=_util.Util.getAxialAlignedBoundingBox([0,0,divWidth,divHeight],m);
      }else{
        b=[left,top,left+divWidth,top+divHeight];
      }

      task._bounds.push({
        left:b[0],
        top:b[1],
        right:b[2],
        bottom:b[3],
        div:textDiv,
        size:[divWidth,divHeight],
        m:m
      });
    }
  }

  functionrender(task){
    if(task._canceled){
      return;
    }

    vartextDivs=task._textDivs;
    varcapability=task._capability;
    vartextDivsLength=textDivs.length;

    if(textDivsLength>MAX_TEXT_DIVS_TO_RENDER){
      task._renderingDone=true;
      capability.resolve();
      return;
    }

    if(!task._textContentStream){
      for(vari=0;i<textDivsLength;i++){
        task._layoutText(textDivs[i]);
      }
    }

    task._renderingDone=true;
    capability.resolve();
  }

  functionexpand(task){
    varbounds=task._bounds;
    varviewport=task._viewport;
    varexpanded=expandBounds(viewport.width,viewport.height,bounds);

    for(vari=0;i<expanded.length;i++){
      vardiv=bounds[i].div;

      vardivProperties=task._textDivProperties.get(div);

      if(divProperties.angle===0){
        divProperties.paddingLeft=bounds[i].left-expanded[i].left;
        divProperties.paddingTop=bounds[i].top-expanded[i].top;
        divProperties.paddingRight=expanded[i].right-bounds[i].right;
        divProperties.paddingBottom=expanded[i].bottom-bounds[i].bottom;

        task._textDivProperties.set(div,divProperties);

        continue;
      }

      vare=expanded[i],
          b=bounds[i];
      varm=b.m,
          c=m[0],
          s=m[1];
      varpoints=[[0,0],[0,b.size[1]],[b.size[0],0],b.size];
      varts=newFloat64Array(64);
      points.forEach(function(p,i){
        vart=_util.Util.applyTransform(p,m);

        ts[i+0]=c&&(e.left-t[0])/c;
        ts[i+4]=s&&(e.top-t[1])/s;
        ts[i+8]=c&&(e.right-t[0])/c;
        ts[i+12]=s&&(e.bottom-t[1])/s;
        ts[i+16]=s&&(e.left-t[0])/-s;
        ts[i+20]=c&&(e.top-t[1])/c;
        ts[i+24]=s&&(e.right-t[0])/-s;
        ts[i+28]=c&&(e.bottom-t[1])/c;
        ts[i+32]=c&&(e.left-t[0])/-c;
        ts[i+36]=s&&(e.top-t[1])/-s;
        ts[i+40]=c&&(e.right-t[0])/-c;
        ts[i+44]=s&&(e.bottom-t[1])/-s;
        ts[i+48]=s&&(e.left-t[0])/s;
        ts[i+52]=c&&(e.top-t[1])/-c;
        ts[i+56]=s&&(e.right-t[0])/s;
        ts[i+60]=c&&(e.bottom-t[1])/-c;
      });

      varfindPositiveMin=functionfindPositiveMin(ts,offset,count){
        varresult=0;

        for(vari=0;i<count;i++){
          vart=ts[offset++];

          if(t>0){
            result=result?Math.min(t,result):t;
          }
        }

        returnresult;
      };

      varboxScale=1+Math.min(Math.abs(c),Math.abs(s));
      divProperties.paddingLeft=findPositiveMin(ts,32,16)/boxScale;
      divProperties.paddingTop=findPositiveMin(ts,48,16)/boxScale;
      divProperties.paddingRight=findPositiveMin(ts,0,16)/boxScale;
      divProperties.paddingBottom=findPositiveMin(ts,16,16)/boxScale;

      task._textDivProperties.set(div,divProperties);
    }
  }

  functionexpandBounds(width,height,boxes){
    varbounds=boxes.map(function(box,i){
      return{
        x1:box.left,
        y1:box.top,
        x2:box.right,
        y2:box.bottom,
        index:i,
        x1New:undefined,
        x2New:undefined
      };
    });
    expandBoundsLTR(width,bounds);
    varexpanded=newArray(boxes.length);
    bounds.forEach(function(b){
      vari=b.index;
      expanded[i]={
        left:b.x1New,
        top:0,
        right:b.x2New,
        bottom:0
      };
    });
    boxes.map(function(box,i){
      vare=expanded[i],
          b=bounds[i];
      b.x1=box.top;
      b.y1=width-e.right;
      b.x2=box.bottom;
      b.y2=width-e.left;
      b.index=i;
      b.x1New=undefined;
      b.x2New=undefined;
    });
    expandBoundsLTR(height,bounds);
    bounds.forEach(function(b){
      vari=b.index;
      expanded[i].top=b.x1New;
      expanded[i].bottom=b.x2New;
    });
    returnexpanded;
  }

  functionexpandBoundsLTR(width,bounds){
    bounds.sort(function(a,b){
      returna.x1-b.x1||a.index-b.index;
    });
    varfakeBoundary={
      x1:-Infinity,
      y1:-Infinity,
      x2:0,
      y2:Infinity,
      index:-1,
      x1New:0,
      x2New:0
    };
    varhorizon=[{
      start:-Infinity,
      end:Infinity,
      boundary:fakeBoundary
    }];
    bounds.forEach(function(boundary){
      vari=0;

      while(i<horizon.length&&horizon[i].end<=boundary.y1){
        i++;
      }

      varj=horizon.length-1;

      while(j>=0&&horizon[j].start>=boundary.y2){
        j--;
      }

      varhorizonPart,affectedBoundary;
      varq,
          k,
          maxXNew=-Infinity;

      for(q=i;q<=j;q++){
        horizonPart=horizon[q];
        affectedBoundary=horizonPart.boundary;
        varxNew;

        if(affectedBoundary.x2>boundary.x1){
          xNew=affectedBoundary.index>boundary.index?affectedBoundary.x1New:boundary.x1;
        }elseif(affectedBoundary.x2New===undefined){
          xNew=(affectedBoundary.x2+boundary.x1)/2;
        }else{
          xNew=affectedBoundary.x2New;
        }

        if(xNew>maxXNew){
          maxXNew=xNew;
        }
      }

      boundary.x1New=maxXNew;

      for(q=i;q<=j;q++){
        horizonPart=horizon[q];
        affectedBoundary=horizonPart.boundary;

        if(affectedBoundary.x2New===undefined){
          if(affectedBoundary.x2>boundary.x1){
            if(affectedBoundary.index>boundary.index){
              affectedBoundary.x2New=affectedBoundary.x2;
            }
          }else{
            affectedBoundary.x2New=maxXNew;
          }
        }elseif(affectedBoundary.x2New>maxXNew){
          affectedBoundary.x2New=Math.max(maxXNew,affectedBoundary.x2);
        }
      }

      varchangedHorizon=[],
          lastBoundary=null;

      for(q=i;q<=j;q++){
        horizonPart=horizon[q];
        affectedBoundary=horizonPart.boundary;
        varuseBoundary=affectedBoundary.x2>boundary.x2?affectedBoundary:boundary;

        if(lastBoundary===useBoundary){
          changedHorizon[changedHorizon.length-1].end=horizonPart.end;
        }else{
          changedHorizon.push({
            start:horizonPart.start,
            end:horizonPart.end,
            boundary:useBoundary
          });
          lastBoundary=useBoundary;
        }
      }

      if(horizon[i].start<boundary.y1){
        changedHorizon[0].start=boundary.y1;
        changedHorizon.unshift({
          start:horizon[i].start,
          end:boundary.y1,
          boundary:horizon[i].boundary
        });
      }

      if(boundary.y2<horizon[j].end){
        changedHorizon[changedHorizon.length-1].end=boundary.y2;
        changedHorizon.push({
          start:boundary.y2,
          end:horizon[j].end,
          boundary:horizon[j].boundary
        });
      }

      for(q=i;q<=j;q++){
        horizonPart=horizon[q];
        affectedBoundary=horizonPart.boundary;

        if(affectedBoundary.x2New!==undefined){
          continue;
        }

        varused=false;

        for(k=i-1;!used&&k>=0&&horizon[k].start>=affectedBoundary.y1;k--){
          used=horizon[k].boundary===affectedBoundary;
        }

        for(k=j+1;!used&&k<horizon.length&&horizon[k].end<=affectedBoundary.y2;k++){
          used=horizon[k].boundary===affectedBoundary;
        }

        for(k=0;!used&&k<changedHorizon.length;k++){
          used=changedHorizon[k].boundary===affectedBoundary;
        }

        if(!used){
          affectedBoundary.x2New=maxXNew;
        }
      }

      Array.prototype.splice.apply(horizon,[i,j-i+1].concat(changedHorizon));
    });
    horizon.forEach(function(horizonPart){
      varaffectedBoundary=horizonPart.boundary;

      if(affectedBoundary.x2New===undefined){
        affectedBoundary.x2New=Math.max(width,affectedBoundary.x2);
      }
    });
  }

  functionTextLayerRenderTask(_ref){
    var_this=this;

    vartextContent=_ref.textContent,
        textContentStream=_ref.textContentStream,
        container=_ref.container,
        viewport=_ref.viewport,
        textDivs=_ref.textDivs,
        textContentItemsStr=_ref.textContentItemsStr,
        enhanceTextSelection=_ref.enhanceTextSelection;
    this._textContent=textContent;
    this._textContentStream=textContentStream;
    this._container=container;
    this._viewport=viewport;
    this._textDivs=textDivs||[];
    this._textContentItemsStr=textContentItemsStr||[];
    this._enhanceTextSelection=!!enhanceTextSelection;
    this._fontInspectorEnabled=!!(_global_scope["default"].FontInspector&&_global_scope["default"].FontInspector.enabled);
    this._reader=null;
    this._layoutTextLastFontSize=null;
    this._layoutTextLastFontFamily=null;
    this._layoutTextCtx=null;
    this._textDivProperties=newWeakMap();
    this._renderingDone=false;
    this._canceled=false;
    this._capability=(0,_util.createPromiseCapability)();
    this._renderTimer=null;
    this._bounds=[];

    this._capability.promise["finally"](function(){
      if(_this._layoutTextCtx){
        _this._layoutTextCtx.canvas.width=0;
        _this._layoutTextCtx.canvas.height=0;
        _this._layoutTextCtx=null;
      }
    });
  }

  TextLayerRenderTask.prototype={
    getpromise(){
      returnthis._capability.promise;
    },

    cancel:functionTextLayer_cancel(){
      this._canceled=true;

      if(this._reader){
        this._reader.cancel(new_util.AbortException('TextLayertaskcancelled.'));

        this._reader=null;
      }

      if(this._renderTimer!==null){
        clearTimeout(this._renderTimer);
        this._renderTimer=null;
      }

      this._capability.reject(newError('TextLayertaskcancelled.'));
    },
    _processItems:function_processItems(items,styleCache){
      for(vari=0,len=items.length;i<len;i++){
        this._textContentItemsStr.push(items[i].str);

        appendText(this,items[i],styleCache);
      }
    },
    _layoutText:function_layoutText(textDiv){
      vartextLayerFrag=this._container;

      vartextDivProperties=this._textDivProperties.get(textDiv);

      if(textDivProperties.isWhitespace){
        return;
      }

      varfontSize=textDiv.style.fontSize;
      varfontFamily=textDiv.style.fontFamily;

      if(fontSize!==this._layoutTextLastFontSize||fontFamily!==this._layoutTextLastFontFamily){
        this._layoutTextCtx.font=fontSize+''+fontFamily;
        this._layoutTextLastFontSize=fontSize;
        this._layoutTextLastFontFamily=fontFamily;
      }

      varwidth=this._layoutTextCtx.measureText(textDiv.textContent).width;

      vartransform='';

      if(textDivProperties.canvasWidth!==0&&width>0){
        textDivProperties.scale=textDivProperties.canvasWidth/width;
        transform="scaleX(".concat(textDivProperties.scale,")");
      }

      if(textDivProperties.angle!==0){
        transform="rotate(".concat(textDivProperties.angle,"deg)").concat(transform);
      }

      if(transform.length>0){
        textDivProperties.originalTransform=transform;
        textDiv.style.transform=transform;
      }

      this._textDivProperties.set(textDiv,textDivProperties);

      textLayerFrag.appendChild(textDiv);
    },
    _render:functionTextLayer_render(timeout){
      var_this2=this;

      varcapability=(0,_util.createPromiseCapability)();
      varstyleCache=Object.create(null);
      varcanvas=document.createElement('canvas');
      canvas.mozOpaque=true;
      this._layoutTextCtx=canvas.getContext('2d',{
        alpha:false
      });

      if(this._textContent){
        vartextItems=this._textContent.items;
        vartextStyles=this._textContent.styles;

        this._processItems(textItems,textStyles);

        capability.resolve();
      }elseif(this._textContentStream){
        varpump=functionpump(){
          _this2._reader.read().then(function(_ref2){
            varvalue=_ref2.value,
                done=_ref2.done;

            if(done){
              capability.resolve();
              return;
            }

            Object.assign(styleCache,value.styles);

            _this2._processItems(value.items,styleCache);

            pump();
          },capability.reject);
        };

        this._reader=this._textContentStream.getReader();
        pump();
      }else{
        thrownewError('Neither"textContent"nor"textContentStream"'+'parametersspecified.');
      }

      capability.promise.then(function(){
        styleCache=null;

        if(!timeout){
          render(_this2);
        }else{
          _this2._renderTimer=setTimeout(function(){
            render(_this2);
            _this2._renderTimer=null;
          },timeout);
        }
      },this._capability.reject);
    },
    expandTextDivs:functionTextLayer_expandTextDivs(expandDivs){
      if(!this._enhanceTextSelection||!this._renderingDone){
        return;
      }

      if(this._bounds!==null){
        expand(this);
        this._bounds=null;
      }

      for(vari=0,ii=this._textDivs.length;i<ii;i++){
        vardiv=this._textDivs[i];

        vardivProperties=this._textDivProperties.get(div);

        if(divProperties.isWhitespace){
          continue;
        }

        if(expandDivs){
          vartransform='',
              padding='';

          if(divProperties.scale!==1){
            transform='scaleX('+divProperties.scale+')';
          }

          if(divProperties.angle!==0){
            transform='rotate('+divProperties.angle+'deg)'+transform;
          }

          if(divProperties.paddingLeft!==0){
            padding+='padding-left:'+divProperties.paddingLeft/divProperties.scale+'px;';
            transform+='translateX('+-divProperties.paddingLeft/divProperties.scale+'px)';
          }

          if(divProperties.paddingTop!==0){
            padding+='padding-top:'+divProperties.paddingTop+'px;';
            transform+='translateY('+-divProperties.paddingTop+'px)';
          }

          if(divProperties.paddingRight!==0){
            padding+='padding-right:'+divProperties.paddingRight/divProperties.scale+'px;';
          }

          if(divProperties.paddingBottom!==0){
            padding+='padding-bottom:'+divProperties.paddingBottom+'px;';
          }

          if(padding!==''){
            div.setAttribute('style',divProperties.style+padding);
          }

          if(transform!==''){
            div.style.transform=transform;
          }
        }else{
          div.style.padding=0;
          div.style.transform=divProperties.originalTransform||'';
        }
      }
    }
  };

  functionrenderTextLayer(renderParameters){
    vartask=newTextLayerRenderTask({
      textContent:renderParameters.textContent,
      textContentStream:renderParameters.textContentStream,
      container:renderParameters.container,
      viewport:renderParameters.viewport,
      textDivs:renderParameters.textDivs,
      textContentItemsStr:renderParameters.textContentItemsStr,
      enhanceTextSelection:renderParameters.enhanceTextSelection
    });

    task._render(renderParameters.timeout);

    returntask;
  }

  returnrenderTextLayer;
}();

exports.renderTextLayer=renderTextLayer;

/***/}),
/*163*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.AnnotationLayer=void0;

var_display_utils=__w_pdfjs_require__(151);

var_util=__w_pdfjs_require__(1);

function_get(target,property,receiver){if(typeofReflect!=="undefined"&&Reflect.get){_get=Reflect.get;}else{_get=function_get(target,property,receiver){varbase=_superPropBase(target,property);if(!base)return;vardesc=Object.getOwnPropertyDescriptor(base,property);if(desc.get){returndesc.get.call(receiver);}returndesc.value;};}return_get(target,property,receiver||target);}

function_superPropBase(object,property){while(!Object.prototype.hasOwnProperty.call(object,property)){object=_getPrototypeOf(object);if(object===null)break;}returnobject;}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varAnnotationElementFactory=
/*#__PURE__*/
function(){
  functionAnnotationElementFactory(){
    _classCallCheck(this,AnnotationElementFactory);
  }

  _createClass(AnnotationElementFactory,null,[{
    key:"create",
    value:functioncreate(parameters){
      varsubtype=parameters.data.annotationType;

      switch(subtype){
        case_util.AnnotationType.LINK:
          returnnewLinkAnnotationElement(parameters);

        case_util.AnnotationType.TEXT:
          returnnewTextAnnotationElement(parameters);

        case_util.AnnotationType.WIDGET:
          varfieldType=parameters.data.fieldType;

          switch(fieldType){
            case'Tx':
              returnnewTextWidgetAnnotationElement(parameters);

            case'Btn':
              if(parameters.data.radioButton){
                returnnewRadioButtonWidgetAnnotationElement(parameters);
              }elseif(parameters.data.checkBox){
                returnnewCheckboxWidgetAnnotationElement(parameters);
              }

              returnnewPushButtonWidgetAnnotationElement(parameters);

            case'Ch':
              returnnewChoiceWidgetAnnotationElement(parameters);
          }

          returnnewWidgetAnnotationElement(parameters);

        case_util.AnnotationType.POPUP:
          returnnewPopupAnnotationElement(parameters);

        case_util.AnnotationType.FREETEXT:
          returnnewFreeTextAnnotationElement(parameters);

        case_util.AnnotationType.LINE:
          returnnewLineAnnotationElement(parameters);

        case_util.AnnotationType.SQUARE:
          returnnewSquareAnnotationElement(parameters);

        case_util.AnnotationType.CIRCLE:
          returnnewCircleAnnotationElement(parameters);

        case_util.AnnotationType.POLYLINE:
          returnnewPolylineAnnotationElement(parameters);

        case_util.AnnotationType.CARET:
          returnnewCaretAnnotationElement(parameters);

        case_util.AnnotationType.INK:
          returnnewInkAnnotationElement(parameters);

        case_util.AnnotationType.POLYGON:
          returnnewPolygonAnnotationElement(parameters);

        case_util.AnnotationType.HIGHLIGHT:
          returnnewHighlightAnnotationElement(parameters);

        case_util.AnnotationType.UNDERLINE:
          returnnewUnderlineAnnotationElement(parameters);

        case_util.AnnotationType.SQUIGGLY:
          returnnewSquigglyAnnotationElement(parameters);

        case_util.AnnotationType.STRIKEOUT:
          returnnewStrikeOutAnnotationElement(parameters);

        case_util.AnnotationType.STAMP:
          returnnewStampAnnotationElement(parameters);

        case_util.AnnotationType.FILEATTACHMENT:
          returnnewFileAttachmentAnnotationElement(parameters);

        default:
          returnnewAnnotationElement(parameters);
      }
    }
  }]);

  returnAnnotationElementFactory;
}();

varAnnotationElement=
/*#__PURE__*/
function(){
  functionAnnotationElement(parameters){
    varisRenderable=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
    varignoreBorder=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

    _classCallCheck(this,AnnotationElement);

    this.isRenderable=isRenderable;
    this.data=parameters.data;
    this.layer=parameters.layer;
    this.page=parameters.page;
    this.viewport=parameters.viewport;
    this.linkService=parameters.linkService;
    this.downloadManager=parameters.downloadManager;
    this.imageResourcesPath=parameters.imageResourcesPath;
    this.renderInteractiveForms=parameters.renderInteractiveForms;
    this.svgFactory=parameters.svgFactory;

    if(isRenderable){
      this.container=this._createContainer(ignoreBorder);
    }
  }

  _createClass(AnnotationElement,[{
    key:"_createContainer",
    value:function_createContainer(){
      varignoreBorder=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      vardata=this.data,
          page=this.page,
          viewport=this.viewport;
      varcontainer=document.createElement('section');
      varwidth=data.rect[2]-data.rect[0];
      varheight=data.rect[3]-data.rect[1];
      container.setAttribute('data-annotation-id',data.id);

      varrect=_util.Util.normalizeRect([data.rect[0],page.view[3]-data.rect[1]+page.view[1],data.rect[2],page.view[3]-data.rect[3]+page.view[1]]);

      container.style.transform='matrix('+viewport.transform.join(',')+')';
      container.style.transformOrigin=-rect[0]+'px'+-rect[1]+'px';

      if(!ignoreBorder&&data.borderStyle.width>0){
        container.style.borderWidth=data.borderStyle.width+'px';

        if(data.borderStyle.style!==_util.AnnotationBorderStyleType.UNDERLINE){
          width=width-2*data.borderStyle.width;
          height=height-2*data.borderStyle.width;
        }

        varhorizontalRadius=data.borderStyle.horizontalCornerRadius;
        varverticalRadius=data.borderStyle.verticalCornerRadius;

        if(horizontalRadius>0||verticalRadius>0){
          varradius=horizontalRadius+'px/'+verticalRadius+'px';
          container.style.borderRadius=radius;
        }

        switch(data.borderStyle.style){
          case_util.AnnotationBorderStyleType.SOLID:
            container.style.borderStyle='solid';
            break;

          case_util.AnnotationBorderStyleType.DASHED:
            container.style.borderStyle='dashed';
            break;

          case_util.AnnotationBorderStyleType.BEVELED:
            (0,_util.warn)('Unimplementedborderstyle:beveled');
            break;

          case_util.AnnotationBorderStyleType.INSET:
            (0,_util.warn)('Unimplementedborderstyle:inset');
            break;

          case_util.AnnotationBorderStyleType.UNDERLINE:
            container.style.borderBottomStyle='solid';
            break;

          default:
            break;
        }

        if(data.color){
          container.style.borderColor=_util.Util.makeCssRgb(data.color[0]|0,data.color[1]|0,data.color[2]|0);
        }else{
          container.style.borderWidth=0;
        }
      }

      container.style.left=rect[0]+'px';
      container.style.top=rect[1]+'px';
      container.style.width=width+'px';
      container.style.height=height+'px';
      returncontainer;
    }
  },{
    key:"_createPopup",
    value:function_createPopup(container,trigger,data){
      if(!trigger){
        trigger=document.createElement('div');
        trigger.style.height=container.style.height;
        trigger.style.width=container.style.width;
        container.appendChild(trigger);
      }

      varpopupElement=newPopupElement({
        container:container,
        trigger:trigger,
        color:data.color,
        title:data.title,
        modificationDate:data.modificationDate,
        contents:data.contents,
        hideWrapper:true
      });
      varpopup=popupElement.render();
      popup.style.left=container.style.width;
      container.appendChild(popup);
    }
  },{
    key:"render",
    value:functionrender(){
      (0,_util.unreachable)('Abstractmethod`AnnotationElement.render`called');
    }
  }]);

  returnAnnotationElement;
}();

varLinkAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement){
  _inherits(LinkAnnotationElement,_AnnotationElement);

  functionLinkAnnotationElement(parameters){
    _classCallCheck(this,LinkAnnotationElement);

    varisRenderable=!!(parameters.data.url||parameters.data.dest||parameters.data.action);
    return_possibleConstructorReturn(this,_getPrototypeOf(LinkAnnotationElement).call(this,parameters,isRenderable));
  }

  _createClass(LinkAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='linkAnnotation';
      vardata=this.data,
          linkService=this.linkService;
      varlink=document.createElement('a');
      (0,_display_utils.addLinkAttributes)(link,{
        url:data.url,
        target:data.newWindow?_display_utils.LinkTarget.BLANK:linkService.externalLinkTarget,
        rel:linkService.externalLinkRel
      });

      if(!data.url){
        if(data.action){
          this._bindNamedAction(link,data.action);
        }else{
          this._bindLink(link,data.dest);
        }
      }

      this.container.appendChild(link);
      returnthis.container;
    }
  },{
    key:"_bindLink",
    value:function_bindLink(link,destination){
      var_this=this;

      link.href=this.linkService.getDestinationHash(destination);

      link.onclick=function(){
        if(destination){
          _this.linkService.navigateTo(destination);
        }

        returnfalse;
      };

      if(destination){
        link.className='internalLink';
      }
    }
  },{
    key:"_bindNamedAction",
    value:function_bindNamedAction(link,action){
      var_this2=this;

      link.href=this.linkService.getAnchorUrl('');

      link.onclick=function(){
        _this2.linkService.executeNamedAction(action);

        returnfalse;
      };

      link.className='internalLink';
    }
  }]);

  returnLinkAnnotationElement;
}(AnnotationElement);

varTextAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement2){
  _inherits(TextAnnotationElement,_AnnotationElement2);

  functionTextAnnotationElement(parameters){
    _classCallCheck(this,TextAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(TextAnnotationElement).call(this,parameters,isRenderable));
  }

  _createClass(TextAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='textAnnotation';
      varimage=document.createElement('img');
      image.style.height=this.container.style.height;
      image.style.width=this.container.style.width;
      image.src=this.imageResourcesPath+'annotation-'+this.data.name.toLowerCase()+'.svg';
      image.alt='[{{type}}Annotation]';
      image.dataset.l10nId='text_annotation_type';
      image.dataset.l10nArgs=JSON.stringify({
        type:this.data.name
      });

      if(!this.data.hasPopup){
        this._createPopup(this.container,image,this.data);
      }

      this.container.appendChild(image);
      returnthis.container;
    }
  }]);

  returnTextAnnotationElement;
}(AnnotationElement);

varWidgetAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement3){
  _inherits(WidgetAnnotationElement,_AnnotationElement3);

  functionWidgetAnnotationElement(){
    _classCallCheck(this,WidgetAnnotationElement);

    return_possibleConstructorReturn(this,_getPrototypeOf(WidgetAnnotationElement).apply(this,arguments));
  }

  _createClass(WidgetAnnotationElement,[{
    key:"render",
    value:functionrender(){
      returnthis.container;
    }
  }]);

  returnWidgetAnnotationElement;
}(AnnotationElement);

varTextWidgetAnnotationElement=
/*#__PURE__*/
function(_WidgetAnnotationElem){
  _inherits(TextWidgetAnnotationElement,_WidgetAnnotationElem);

  functionTextWidgetAnnotationElement(parameters){
    _classCallCheck(this,TextWidgetAnnotationElement);

    varisRenderable=parameters.renderInteractiveForms||!parameters.data.hasAppearance&&!!parameters.data.fieldValue;
    return_possibleConstructorReturn(this,_getPrototypeOf(TextWidgetAnnotationElement).call(this,parameters,isRenderable));
  }

  _createClass(TextWidgetAnnotationElement,[{
    key:"render",
    value:functionrender(){
      varTEXT_ALIGNMENT=['left','center','right'];
      this.container.className='textWidgetAnnotation';
      varelement=null;

      if(this.renderInteractiveForms){
        if(this.data.multiLine){
          element=document.createElement('textarea');
          element.textContent=this.data.fieldValue;
        }else{
          element=document.createElement('input');
          element.type='text';
          element.setAttribute('value',this.data.fieldValue);
        }

        element.disabled=this.data.readOnly;

        if(this.data.maxLen!==null){
          element.maxLength=this.data.maxLen;
        }

        if(this.data.comb){
          varfieldWidth=this.data.rect[2]-this.data.rect[0];
          varcombWidth=fieldWidth/this.data.maxLen;
          element.classList.add('comb');
          element.style.letterSpacing='calc('+combWidth+'px-1ch)';
        }
      }else{
        element=document.createElement('div');
        element.textContent=this.data.fieldValue;
        element.style.verticalAlign='middle';
        element.style.display='table-cell';
        varfont=null;

        if(this.data.fontRefName&&this.page.commonObjs.has(this.data.fontRefName)){
          font=this.page.commonObjs.get(this.data.fontRefName);
        }

        this._setTextStyle(element,font);
      }

      if(this.data.textAlignment!==null){
        element.style.textAlign=TEXT_ALIGNMENT[this.data.textAlignment];
      }

      this.container.appendChild(element);
      returnthis.container;
    }
  },{
    key:"_setTextStyle",
    value:function_setTextStyle(element,font){
      varstyle=element.style;
      style.fontSize=this.data.fontSize+'px';
      style.direction=this.data.fontDirection<0?'rtl':'ltr';

      if(!font){
        return;
      }

      style.fontWeight=font.black?font.bold?'900':'bold':font.bold?'bold':'normal';
      style.fontStyle=font.italic?'italic':'normal';
      varfontFamily=font.loadedName?'"'+font.loadedName+'",':'';
      varfallbackName=font.fallbackName||'Helvetica,sans-serif';
      style.fontFamily=fontFamily+fallbackName;
    }
  }]);

  returnTextWidgetAnnotationElement;
}(WidgetAnnotationElement);

varCheckboxWidgetAnnotationElement=
/*#__PURE__*/
function(_WidgetAnnotationElem2){
  _inherits(CheckboxWidgetAnnotationElement,_WidgetAnnotationElem2);

  functionCheckboxWidgetAnnotationElement(parameters){
    _classCallCheck(this,CheckboxWidgetAnnotationElement);

    return_possibleConstructorReturn(this,_getPrototypeOf(CheckboxWidgetAnnotationElement).call(this,parameters,parameters.renderInteractiveForms));
  }

  _createClass(CheckboxWidgetAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='buttonWidgetAnnotationcheckBox';
      varelement=document.createElement('input');
      element.disabled=this.data.readOnly;
      element.type='checkbox';

      if(this.data.fieldValue&&this.data.fieldValue!=='Off'){
        element.setAttribute('checked',true);
      }

      this.container.appendChild(element);
      returnthis.container;
    }
  }]);

  returnCheckboxWidgetAnnotationElement;
}(WidgetAnnotationElement);

varRadioButtonWidgetAnnotationElement=
/*#__PURE__*/
function(_WidgetAnnotationElem3){
  _inherits(RadioButtonWidgetAnnotationElement,_WidgetAnnotationElem3);

  functionRadioButtonWidgetAnnotationElement(parameters){
    _classCallCheck(this,RadioButtonWidgetAnnotationElement);

    return_possibleConstructorReturn(this,_getPrototypeOf(RadioButtonWidgetAnnotationElement).call(this,parameters,parameters.renderInteractiveForms));
  }

  _createClass(RadioButtonWidgetAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='buttonWidgetAnnotationradioButton';
      varelement=document.createElement('input');
      element.disabled=this.data.readOnly;
      element.type='radio';
      element.name=this.data.fieldName;

      if(this.data.fieldValue===this.data.buttonValue){
        element.setAttribute('checked',true);
      }

      this.container.appendChild(element);
      returnthis.container;
    }
  }]);

  returnRadioButtonWidgetAnnotationElement;
}(WidgetAnnotationElement);

varPushButtonWidgetAnnotationElement=
/*#__PURE__*/
function(_LinkAnnotationElemen){
  _inherits(PushButtonWidgetAnnotationElement,_LinkAnnotationElemen);

  functionPushButtonWidgetAnnotationElement(){
    _classCallCheck(this,PushButtonWidgetAnnotationElement);

    return_possibleConstructorReturn(this,_getPrototypeOf(PushButtonWidgetAnnotationElement).apply(this,arguments));
  }

  _createClass(PushButtonWidgetAnnotationElement,[{
    key:"render",
    value:functionrender(){
      varcontainer=_get(_getPrototypeOf(PushButtonWidgetAnnotationElement.prototype),"render",this).call(this);

      container.className='buttonWidgetAnnotationpushButton';
      returncontainer;
    }
  }]);

  returnPushButtonWidgetAnnotationElement;
}(LinkAnnotationElement);

varChoiceWidgetAnnotationElement=
/*#__PURE__*/
function(_WidgetAnnotationElem4){
  _inherits(ChoiceWidgetAnnotationElement,_WidgetAnnotationElem4);

  functionChoiceWidgetAnnotationElement(parameters){
    _classCallCheck(this,ChoiceWidgetAnnotationElement);

    return_possibleConstructorReturn(this,_getPrototypeOf(ChoiceWidgetAnnotationElement).call(this,parameters,parameters.renderInteractiveForms));
  }

  _createClass(ChoiceWidgetAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='choiceWidgetAnnotation';
      varselectElement=document.createElement('select');
      selectElement.disabled=this.data.readOnly;

      if(!this.data.combo){
        selectElement.size=this.data.options.length;

        if(this.data.multiSelect){
          selectElement.multiple=true;
        }
      }

      for(vari=0,ii=this.data.options.length;i<ii;i++){
        varoption=this.data.options[i];
        varoptionElement=document.createElement('option');
        optionElement.textContent=option.displayValue;
        optionElement.value=option.exportValue;

        if(this.data.fieldValue.includes(option.displayValue)){
          optionElement.setAttribute('selected',true);
        }

        selectElement.appendChild(optionElement);
      }

      this.container.appendChild(selectElement);
      returnthis.container;
    }
  }]);

  returnChoiceWidgetAnnotationElement;
}(WidgetAnnotationElement);

varPopupAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement4){
  _inherits(PopupAnnotationElement,_AnnotationElement4);

  functionPopupAnnotationElement(parameters){
    _classCallCheck(this,PopupAnnotationElement);

    varisRenderable=!!(parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(PopupAnnotationElement).call(this,parameters,isRenderable));
  }

  _createClass(PopupAnnotationElement,[{
    key:"render",
    value:functionrender(){
      varIGNORE_TYPES=['Line','Square','Circle','PolyLine','Polygon','Ink'];
      this.container.className='popupAnnotation';

      if(IGNORE_TYPES.includes(this.data.parentType)){
        returnthis.container;
      }

      varselector='[data-annotation-id="'+this.data.parentId+'"]';
      varparentElement=this.layer.querySelector(selector);

      if(!parentElement){
        returnthis.container;
      }

      varpopup=newPopupElement({
        container:this.container,
        trigger:parentElement,
        color:this.data.color,
        title:this.data.title,
        modificationDate:this.data.modificationDate,
        contents:this.data.contents
      });
      varparentLeft=parseFloat(parentElement.style.left);
      varparentWidth=parseFloat(parentElement.style.width);
      this.container.style.transformOrigin=-(parentLeft+parentWidth)+'px-'+parentElement.style.top;
      this.container.style.left=parentLeft+parentWidth+'px';
      this.container.appendChild(popup.render());
      returnthis.container;
    }
  }]);

  returnPopupAnnotationElement;
}(AnnotationElement);

varPopupElement=
/*#__PURE__*/
function(){
  functionPopupElement(parameters){
    _classCallCheck(this,PopupElement);

    this.container=parameters.container;
    this.trigger=parameters.trigger;
    this.color=parameters.color;
    this.title=parameters.title;
    this.modificationDate=parameters.modificationDate;
    this.contents=parameters.contents;
    this.hideWrapper=parameters.hideWrapper||false;
    this.pinned=false;
  }

  _createClass(PopupElement,[{
    key:"render",
    value:functionrender(){
      varBACKGROUND_ENLIGHT=0.7;
      varwrapper=document.createElement('div');
      wrapper.className='popupWrapper';
      this.hideElement=this.hideWrapper?wrapper:this.container;
      this.hideElement.setAttribute('hidden',true);
      varpopup=document.createElement('div');
      popup.className='popup';
      varcolor=this.color;

      if(color){
        varr=BACKGROUND_ENLIGHT*(255-color[0])+color[0];
        varg=BACKGROUND_ENLIGHT*(255-color[1])+color[1];
        varb=BACKGROUND_ENLIGHT*(255-color[2])+color[2];
        popup.style.backgroundColor=_util.Util.makeCssRgb(r|0,g|0,b|0);
      }

      vartitle=document.createElement('h1');
      title.textContent=this.title;
      popup.appendChild(title);

      vardateObject=_display_utils.PDFDateString.toDateObject(this.modificationDate);

      if(dateObject){
        varmodificationDate=document.createElement('span');
        modificationDate.textContent='{{date}},{{time}}';
        modificationDate.dataset.l10nId='annotation_date_string';
        modificationDate.dataset.l10nArgs=JSON.stringify({
          date:dateObject.toLocaleDateString(),
          time:dateObject.toLocaleTimeString()
        });
        popup.appendChild(modificationDate);
      }

      varcontents=this._formatContents(this.contents);

      popup.appendChild(contents);
      this.trigger.addEventListener('click',this._toggle.bind(this));
      this.trigger.addEventListener('mouseover',this._show.bind(this,false));
      this.trigger.addEventListener('mouseout',this._hide.bind(this,false));
      popup.addEventListener('click',this._hide.bind(this,true));
      wrapper.appendChild(popup);
      returnwrapper;
    }
  },{
    key:"_formatContents",
    value:function_formatContents(contents){
      varp=document.createElement('p');
      varlines=contents.split(/(?:\r\n?|\n)/);

      for(vari=0,ii=lines.length;i<ii;++i){
        varline=lines[i];
        p.appendChild(document.createTextNode(line));

        if(i<ii-1){
          p.appendChild(document.createElement('br'));
        }
      }

      returnp;
    }
  },{
    key:"_toggle",
    value:function_toggle(){
      if(this.pinned){
        this._hide(true);
      }else{
        this._show(true);
      }
    }
  },{
    key:"_show",
    value:function_show(){
      varpin=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(pin){
        this.pinned=true;
      }

      if(this.hideElement.hasAttribute('hidden')){
        this.hideElement.removeAttribute('hidden');
        this.container.style.zIndex+=1;
      }
    }
  },{
    key:"_hide",
    value:function_hide(){
      varunpin=arguments.length>0&&arguments[0]!==undefined?arguments[0]:true;

      if(unpin){
        this.pinned=false;
      }

      if(!this.hideElement.hasAttribute('hidden')&&!this.pinned){
        this.hideElement.setAttribute('hidden',true);
        this.container.style.zIndex-=1;
      }
    }
  }]);

  returnPopupElement;
}();

varFreeTextAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement5){
  _inherits(FreeTextAnnotationElement,_AnnotationElement5);

  functionFreeTextAnnotationElement(parameters){
    _classCallCheck(this,FreeTextAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(FreeTextAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(FreeTextAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='freeTextAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnFreeTextAnnotationElement;
}(AnnotationElement);

varLineAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement6){
  _inherits(LineAnnotationElement,_AnnotationElement6);

  functionLineAnnotationElement(parameters){
    _classCallCheck(this,LineAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(LineAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(LineAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='lineAnnotation';
      vardata=this.data;
      varwidth=data.rect[2]-data.rect[0];
      varheight=data.rect[3]-data.rect[1];
      varsvg=this.svgFactory.create(width,height);
      varline=this.svgFactory.createElement('svg:line');
      line.setAttribute('x1',data.rect[2]-data.lineCoordinates[0]);
      line.setAttribute('y1',data.rect[3]-data.lineCoordinates[1]);
      line.setAttribute('x2',data.rect[2]-data.lineCoordinates[2]);
      line.setAttribute('y2',data.rect[3]-data.lineCoordinates[3]);
      line.setAttribute('stroke-width',data.borderStyle.width);
      line.setAttribute('stroke','transparent');
      svg.appendChild(line);
      this.container.append(svg);

      this._createPopup(this.container,line,data);

      returnthis.container;
    }
  }]);

  returnLineAnnotationElement;
}(AnnotationElement);

varSquareAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement7){
  _inherits(SquareAnnotationElement,_AnnotationElement7);

  functionSquareAnnotationElement(parameters){
    _classCallCheck(this,SquareAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(SquareAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(SquareAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='squareAnnotation';
      vardata=this.data;
      varwidth=data.rect[2]-data.rect[0];
      varheight=data.rect[3]-data.rect[1];
      varsvg=this.svgFactory.create(width,height);
      varborderWidth=data.borderStyle.width;
      varsquare=this.svgFactory.createElement('svg:rect');
      square.setAttribute('x',borderWidth/2);
      square.setAttribute('y',borderWidth/2);
      square.setAttribute('width',width-borderWidth);
      square.setAttribute('height',height-borderWidth);
      square.setAttribute('stroke-width',borderWidth);
      square.setAttribute('stroke','transparent');
      square.setAttribute('fill','none');
      svg.appendChild(square);
      this.container.append(svg);

      this._createPopup(this.container,square,data);

      returnthis.container;
    }
  }]);

  returnSquareAnnotationElement;
}(AnnotationElement);

varCircleAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement8){
  _inherits(CircleAnnotationElement,_AnnotationElement8);

  functionCircleAnnotationElement(parameters){
    _classCallCheck(this,CircleAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(CircleAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(CircleAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='circleAnnotation';
      vardata=this.data;
      varwidth=data.rect[2]-data.rect[0];
      varheight=data.rect[3]-data.rect[1];
      varsvg=this.svgFactory.create(width,height);
      varborderWidth=data.borderStyle.width;
      varcircle=this.svgFactory.createElement('svg:ellipse');
      circle.setAttribute('cx',width/2);
      circle.setAttribute('cy',height/2);
      circle.setAttribute('rx',width/2-borderWidth/2);
      circle.setAttribute('ry',height/2-borderWidth/2);
      circle.setAttribute('stroke-width',borderWidth);
      circle.setAttribute('stroke','transparent');
      circle.setAttribute('fill','none');
      svg.appendChild(circle);
      this.container.append(svg);

      this._createPopup(this.container,circle,data);

      returnthis.container;
    }
  }]);

  returnCircleAnnotationElement;
}(AnnotationElement);

varPolylineAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement9){
  _inherits(PolylineAnnotationElement,_AnnotationElement9);

  functionPolylineAnnotationElement(parameters){
    var_this3;

    _classCallCheck(this,PolylineAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    _this3=_possibleConstructorReturn(this,_getPrototypeOf(PolylineAnnotationElement).call(this,parameters,isRenderable,true));
    _this3.containerClassName='polylineAnnotation';
    _this3.svgElementName='svg:polyline';
    return_this3;
  }

  _createClass(PolylineAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className=this.containerClassName;
      vardata=this.data;
      varwidth=data.rect[2]-data.rect[0];
      varheight=data.rect[3]-data.rect[1];
      varsvg=this.svgFactory.create(width,height);
      varvertices=data.vertices;
      varpoints=[];

      for(vari=0,ii=vertices.length;i<ii;i++){
        varx=vertices[i].x-data.rect[0];
        vary=data.rect[3]-vertices[i].y;
        points.push(x+','+y);
      }

      points=points.join('');
      varborderWidth=data.borderStyle.width;
      varpolyline=this.svgFactory.createElement(this.svgElementName);
      polyline.setAttribute('points',points);
      polyline.setAttribute('stroke-width',borderWidth);
      polyline.setAttribute('stroke','transparent');
      polyline.setAttribute('fill','none');
      svg.appendChild(polyline);
      this.container.append(svg);

      this._createPopup(this.container,polyline,data);

      returnthis.container;
    }
  }]);

  returnPolylineAnnotationElement;
}(AnnotationElement);

varPolygonAnnotationElement=
/*#__PURE__*/
function(_PolylineAnnotationEl){
  _inherits(PolygonAnnotationElement,_PolylineAnnotationEl);

  functionPolygonAnnotationElement(parameters){
    var_this4;

    _classCallCheck(this,PolygonAnnotationElement);

    _this4=_possibleConstructorReturn(this,_getPrototypeOf(PolygonAnnotationElement).call(this,parameters));
    _this4.containerClassName='polygonAnnotation';
    _this4.svgElementName='svg:polygon';
    return_this4;
  }

  returnPolygonAnnotationElement;
}(PolylineAnnotationElement);

varCaretAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement10){
  _inherits(CaretAnnotationElement,_AnnotationElement10);

  functionCaretAnnotationElement(parameters){
    _classCallCheck(this,CaretAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(CaretAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(CaretAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='caretAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnCaretAnnotationElement;
}(AnnotationElement);

varInkAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement11){
  _inherits(InkAnnotationElement,_AnnotationElement11);

  functionInkAnnotationElement(parameters){
    var_this5;

    _classCallCheck(this,InkAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    _this5=_possibleConstructorReturn(this,_getPrototypeOf(InkAnnotationElement).call(this,parameters,isRenderable,true));
    _this5.containerClassName='inkAnnotation';
    _this5.svgElementName='svg:polyline';
    return_this5;
  }

  _createClass(InkAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className=this.containerClassName;
      vardata=this.data;
      varwidth=data.rect[2]-data.rect[0];
      varheight=data.rect[3]-data.rect[1];
      varsvg=this.svgFactory.create(width,height);
      varinkLists=data.inkLists;

      for(vari=0,ii=inkLists.length;i<ii;i++){
        varinkList=inkLists[i];
        varpoints=[];

        for(varj=0,jj=inkList.length;j<jj;j++){
          varx=inkList[j].x-data.rect[0];
          vary=data.rect[3]-inkList[j].y;
          points.push(x+','+y);
        }

        points=points.join('');
        varborderWidth=data.borderStyle.width;
        varpolyline=this.svgFactory.createElement(this.svgElementName);
        polyline.setAttribute('points',points);
        polyline.setAttribute('stroke-width',borderWidth);
        polyline.setAttribute('stroke','transparent');
        polyline.setAttribute('fill','none');

        this._createPopup(this.container,polyline,data);

        svg.appendChild(polyline);
      }

      this.container.append(svg);
      returnthis.container;
    }
  }]);

  returnInkAnnotationElement;
}(AnnotationElement);

varHighlightAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement12){
  _inherits(HighlightAnnotationElement,_AnnotationElement12);

  functionHighlightAnnotationElement(parameters){
    _classCallCheck(this,HighlightAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(HighlightAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(HighlightAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='highlightAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnHighlightAnnotationElement;
}(AnnotationElement);

varUnderlineAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement13){
  _inherits(UnderlineAnnotationElement,_AnnotationElement13);

  functionUnderlineAnnotationElement(parameters){
    _classCallCheck(this,UnderlineAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(UnderlineAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(UnderlineAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='underlineAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnUnderlineAnnotationElement;
}(AnnotationElement);

varSquigglyAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement14){
  _inherits(SquigglyAnnotationElement,_AnnotationElement14);

  functionSquigglyAnnotationElement(parameters){
    _classCallCheck(this,SquigglyAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(SquigglyAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(SquigglyAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='squigglyAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnSquigglyAnnotationElement;
}(AnnotationElement);

varStrikeOutAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement15){
  _inherits(StrikeOutAnnotationElement,_AnnotationElement15);

  functionStrikeOutAnnotationElement(parameters){
    _classCallCheck(this,StrikeOutAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(StrikeOutAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(StrikeOutAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='strikeoutAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnStrikeOutAnnotationElement;
}(AnnotationElement);

varStampAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement16){
  _inherits(StampAnnotationElement,_AnnotationElement16);

  functionStampAnnotationElement(parameters){
    _classCallCheck(this,StampAnnotationElement);

    varisRenderable=!!(parameters.data.hasPopup||parameters.data.title||parameters.data.contents);
    return_possibleConstructorReturn(this,_getPrototypeOf(StampAnnotationElement).call(this,parameters,isRenderable,true));
  }

  _createClass(StampAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='stampAnnotation';

      if(!this.data.hasPopup){
        this._createPopup(this.container,null,this.data);
      }

      returnthis.container;
    }
  }]);

  returnStampAnnotationElement;
}(AnnotationElement);

varFileAttachmentAnnotationElement=
/*#__PURE__*/
function(_AnnotationElement17){
  _inherits(FileAttachmentAnnotationElement,_AnnotationElement17);

  functionFileAttachmentAnnotationElement(parameters){
    var_this6;

    _classCallCheck(this,FileAttachmentAnnotationElement);

    _this6=_possibleConstructorReturn(this,_getPrototypeOf(FileAttachmentAnnotationElement).call(this,parameters,true));
    var_this6$data$file=_this6.data.file,
        filename=_this6$data$file.filename,
        content=_this6$data$file.content;
    _this6.filename=(0,_display_utils.getFilenameFromUrl)(filename);
    _this6.content=content;

    if(_this6.linkService.eventBus){
      _this6.linkService.eventBus.dispatch('fileattachmentannotation',{
        source:_assertThisInitialized(_this6),
        id:(0,_util.stringToPDFString)(filename),
        filename:filename,
        content:content
      });
    }

    return_this6;
  }

  _createClass(FileAttachmentAnnotationElement,[{
    key:"render",
    value:functionrender(){
      this.container.className='fileAttachmentAnnotation';
      vartrigger=document.createElement('div');
      trigger.style.height=this.container.style.height;
      trigger.style.width=this.container.style.width;
      trigger.addEventListener('dblclick',this._download.bind(this));

      if(!this.data.hasPopup&&(this.data.title||this.data.contents)){
        this._createPopup(this.container,trigger,this.data);
      }

      this.container.appendChild(trigger);
      returnthis.container;
    }
  },{
    key:"_download",
    value:function_download(){
      if(!this.downloadManager){
        (0,_util.warn)('Downloadcannotbestartedduetounavailabledownloadmanager');
        return;
      }

      this.downloadManager.downloadData(this.content,this.filename,'');
    }
  }]);

  returnFileAttachmentAnnotationElement;
}(AnnotationElement);

varAnnotationLayer=
/*#__PURE__*/
function(){
  functionAnnotationLayer(){
    _classCallCheck(this,AnnotationLayer);
  }

  _createClass(AnnotationLayer,null,[{
    key:"render",
    value:functionrender(parameters){
      for(vari=0,ii=parameters.annotations.length;i<ii;i++){
        vardata=parameters.annotations[i];

        if(!data){
          continue;
        }

        varelement=AnnotationElementFactory.create({
          data:data,
          layer:parameters.div,
          page:parameters.page,
          viewport:parameters.viewport,
          linkService:parameters.linkService,
          downloadManager:parameters.downloadManager,
          imageResourcesPath:parameters.imageResourcesPath||'',
          renderInteractiveForms:parameters.renderInteractiveForms||false,
          svgFactory:new_display_utils.DOMSVGFactory()
        });

        if(element.isRenderable){
          parameters.div.appendChild(element.render());
        }
      }
    }
  },{
    key:"update",
    value:functionupdate(parameters){
      for(vari=0,ii=parameters.annotations.length;i<ii;i++){
        vardata=parameters.annotations[i];
        varelement=parameters.div.querySelector('[data-annotation-id="'+data.id+'"]');

        if(element){
          element.style.transform='matrix('+parameters.viewport.transform.join(',')+')';
        }
      }

      parameters.div.removeAttribute('hidden');
    }
  }]);

  returnAnnotationLayer;
}();

exports.AnnotationLayer=AnnotationLayer;

/***/}),
/*164*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.SVGGraphics=void0;

var_util=__w_pdfjs_require__(1);

var_display_utils=__w_pdfjs_require__(151);

var_is_node=_interopRequireDefault(__w_pdfjs_require__(4));

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_toConsumableArray(arr){return_arrayWithoutHoles(arr)||_iterableToArray(arr)||_nonIterableSpread();}

function_nonIterableSpread(){thrownewTypeError("Invalidattempttospreadnon-iterableinstance");}

function_iterableToArray(iter){if(Symbol.iteratorinObject(iter)||Object.prototype.toString.call(iter)==="[objectArguments]")returnArray.from(iter);}

function_arrayWithoutHoles(arr){if(Array.isArray(arr)){for(vari=0,arr2=newArray(arr.length);i<arr.length;i++){arr2[i]=arr[i];}returnarr2;}}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varSVGGraphics=functionSVGGraphics(){
  thrownewError('Notimplemented:SVGGraphics');
};

exports.SVGGraphics=SVGGraphics;
{
  varopListToTree=functionopListToTree(opList){
    varopTree=[];
    vartmp=[];
    var_iteratorNormalCompletion=true;
    var_didIteratorError=false;
    var_iteratorError=undefined;

    try{
      for(var_iterator=opList[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
        varopListElement=_step.value;

        if(opListElement.fn==='save'){
          opTree.push({
            'fnId':92,
            'fn':'group',
            'items':[]
          });
          tmp.push(opTree);
          opTree=opTree[opTree.length-1].items;
          continue;
        }

        if(opListElement.fn==='restore'){
          opTree=tmp.pop();
        }else{
          opTree.push(opListElement);
        }
      }
    }catch(err){
      _didIteratorError=true;
      _iteratorError=err;
    }finally{
      try{
        if(!_iteratorNormalCompletion&&_iterator["return"]!=null){
          _iterator["return"]();
        }
      }finally{
        if(_didIteratorError){
          throw_iteratorError;
        }
      }
    }

    returnopTree;
  };

  varpf=functionpf(value){
    if(Number.isInteger(value)){
      returnvalue.toString();
    }

    vars=value.toFixed(10);
    vari=s.length-1;

    if(s[i]!=='0'){
      returns;
    }

    do{
      i--;
    }while(s[i]==='0');

    returns.substring(0,s[i]==='.'?i:i+1);
  };

  varpm=functionpm(m){
    if(m[4]===0&&m[5]===0){
      if(m[1]===0&&m[2]===0){
        if(m[0]===1&&m[3]===1){
          return'';
        }

        return"scale(".concat(pf(m[0]),"").concat(pf(m[3]),")");
      }

      if(m[0]===m[3]&&m[1]===-m[2]){
        vara=Math.acos(m[0])*180/Math.PI;
        return"rotate(".concat(pf(a),")");
      }
    }else{
      if(m[0]===1&&m[1]===0&&m[2]===0&&m[3]===1){
        return"translate(".concat(pf(m[4]),"").concat(pf(m[5]),")");
      }
    }

    return"matrix(".concat(pf(m[0]),"").concat(pf(m[1]),"").concat(pf(m[2]),"").concat(pf(m[3]),"").concat(pf(m[4]),"")+"".concat(pf(m[5]),")");
  };

  varSVG_DEFAULTS={
    fontStyle:'normal',
    fontWeight:'normal',
    fillColor:'#000000'
  };
  varXML_NS='http://www.w3.org/XML/1998/namespace';
  varXLINK_NS='http://www.w3.org/1999/xlink';
  varLINE_CAP_STYLES=['butt','round','square'];
  varLINE_JOIN_STYLES=['miter','round','bevel'];

  varconvertImgDataToPng=function(){
    varPNG_HEADER=newUint8Array([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]);
    varCHUNK_WRAPPER_SIZE=12;
    varcrcTable=newInt32Array(256);

    for(vari=0;i<256;i++){
      varc=i;

      for(varh=0;h<8;h++){
        if(c&1){
          c=0xedB88320^c>>1&0x7fffffff;
        }else{
          c=c>>1&0x7fffffff;
        }
      }

      crcTable[i]=c;
    }

    functioncrc32(data,start,end){
      varcrc=-1;

      for(var_i=start;_i<end;_i++){
        vara=(crc^data[_i])&0xff;
        varb=crcTable[a];
        crc=crc>>>8^b;
      }

      returncrc^-1;
    }

    functionwritePngChunk(type,body,data,offset){
      varp=offset;
      varlen=body.length;
      data[p]=len>>24&0xff;
      data[p+1]=len>>16&0xff;
      data[p+2]=len>>8&0xff;
      data[p+3]=len&0xff;
      p+=4;
      data[p]=type.charCodeAt(0)&0xff;
      data[p+1]=type.charCodeAt(1)&0xff;
      data[p+2]=type.charCodeAt(2)&0xff;
      data[p+3]=type.charCodeAt(3)&0xff;
      p+=4;
      data.set(body,p);
      p+=body.length;
      varcrc=crc32(data,offset+4,p);
      data[p]=crc>>24&0xff;
      data[p+1]=crc>>16&0xff;
      data[p+2]=crc>>8&0xff;
      data[p+3]=crc&0xff;
    }

    functionadler32(data,start,end){
      vara=1;
      varb=0;

      for(var_i2=start;_i2<end;++_i2){
        a=(a+(data[_i2]&0xff))%65521;
        b=(b+a)%65521;
      }

      returnb<<16|a;
    }

    functiondeflateSync(literals){
      if(!(0,_is_node["default"])()){
        returndeflateSyncUncompressed(literals);
      }

      try{
        varinput;

        if(parseInt(process.versions.node)>=8){
          input=literals;
        }else{
          input=newBuffer(literals);
        }

        varoutput=require('zlib').deflateSync(input,{
          level:9
        });

        returnoutputinstanceofUint8Array?output:newUint8Array(output);
      }catch(e){
        (0,_util.warn)('NotcompressingPNGbecausezlib.deflateSyncisunavailable:'+e);
      }

      returndeflateSyncUncompressed(literals);
    }

    functiondeflateSyncUncompressed(literals){
      varlen=literals.length;
      varmaxBlockLength=0xFFFF;
      vardeflateBlocks=Math.ceil(len/maxBlockLength);
      varidat=newUint8Array(2+len+deflateBlocks*5+4);
      varpi=0;
      idat[pi++]=0x78;
      idat[pi++]=0x9c;
      varpos=0;

      while(len>maxBlockLength){
        idat[pi++]=0x00;
        idat[pi++]=0xff;
        idat[pi++]=0xff;
        idat[pi++]=0x00;
        idat[pi++]=0x00;
        idat.set(literals.subarray(pos,pos+maxBlockLength),pi);
        pi+=maxBlockLength;
        pos+=maxBlockLength;
        len-=maxBlockLength;
      }

      idat[pi++]=0x01;
      idat[pi++]=len&0xff;
      idat[pi++]=len>>8&0xff;
      idat[pi++]=~len&0xffff&0xff;
      idat[pi++]=(~len&0xffff)>>8&0xff;
      idat.set(literals.subarray(pos),pi);
      pi+=literals.length-pos;
      varadler=adler32(literals,0,literals.length);
      idat[pi++]=adler>>24&0xff;
      idat[pi++]=adler>>16&0xff;
      idat[pi++]=adler>>8&0xff;
      idat[pi++]=adler&0xff;
      returnidat;
    }

    functionencode(imgData,kind,forceDataSchema,isMask){
      varwidth=imgData.width;
      varheight=imgData.height;
      varbitDepth,colorType,lineSize;
      varbytes=imgData.data;

      switch(kind){
        case_util.ImageKind.GRAYSCALE_1BPP:
          colorType=0;
          bitDepth=1;
          lineSize=width+7>>3;
          break;

        case_util.ImageKind.RGB_24BPP:
          colorType=2;
          bitDepth=8;
          lineSize=width*3;
          break;

        case_util.ImageKind.RGBA_32BPP:
          colorType=6;
          bitDepth=8;
          lineSize=width*4;
          break;

        default:
          thrownewError('invalidformat');
      }

      varliterals=newUint8Array((1+lineSize)*height);
      varoffsetLiterals=0,
          offsetBytes=0;

      for(vary=0;y<height;++y){
        literals[offsetLiterals++]=0;
        literals.set(bytes.subarray(offsetBytes,offsetBytes+lineSize),offsetLiterals);
        offsetBytes+=lineSize;
        offsetLiterals+=lineSize;
      }

      if(kind===_util.ImageKind.GRAYSCALE_1BPP&&isMask){
        offsetLiterals=0;

        for(var_y=0;_y<height;_y++){
          offsetLiterals++;

          for(var_i3=0;_i3<lineSize;_i3++){
            literals[offsetLiterals++]^=0xFF;
          }
        }
      }

      varihdr=newUint8Array([width>>24&0xff,width>>16&0xff,width>>8&0xff,width&0xff,height>>24&0xff,height>>16&0xff,height>>8&0xff,height&0xff,bitDepth,colorType,0x00,0x00,0x00]);
      varidat=deflateSync(literals);
      varpngLength=PNG_HEADER.length+CHUNK_WRAPPER_SIZE*3+ihdr.length+idat.length;
      vardata=newUint8Array(pngLength);
      varoffset=0;
      data.set(PNG_HEADER,offset);
      offset+=PNG_HEADER.length;
      writePngChunk('IHDR',ihdr,data,offset);
      offset+=CHUNK_WRAPPER_SIZE+ihdr.length;
      writePngChunk('IDATA',idat,data,offset);
      offset+=CHUNK_WRAPPER_SIZE+idat.length;
      writePngChunk('IEND',newUint8Array(0),data,offset);
      return(0,_util.createObjectURL)(data,'image/png',forceDataSchema);
    }

    returnfunctionconvertImgDataToPng(imgData,forceDataSchema,isMask){
      varkind=imgData.kind===undefined?_util.ImageKind.GRAYSCALE_1BPP:imgData.kind;
      returnencode(imgData,kind,forceDataSchema,isMask);
    };
  }();

  varSVGExtraState=
  /*#__PURE__*/
  function(){
    functionSVGExtraState(){
      _classCallCheck(this,SVGExtraState);

      this.fontSizeScale=1;
      this.fontWeight=SVG_DEFAULTS.fontWeight;
      this.fontSize=0;
      this.textMatrix=_util.IDENTITY_MATRIX;
      this.fontMatrix=_util.FONT_IDENTITY_MATRIX;
      this.leading=0;
      this.textRenderingMode=_util.TextRenderingMode.FILL;
      this.textMatrixScale=1;
      this.x=0;
      this.y=0;
      this.lineX=0;
      this.lineY=0;
      this.charSpacing=0;
      this.wordSpacing=0;
      this.textHScale=1;
      this.textRise=0;
      this.fillColor=SVG_DEFAULTS.fillColor;
      this.strokeColor='#000000';
      this.fillAlpha=1;
      this.strokeAlpha=1;
      this.lineWidth=1;
      this.lineJoin='';
      this.lineCap='';
      this.miterLimit=0;
      this.dashArray=[];
      this.dashPhase=0;
      this.dependencies=[];
      this.activeClipUrl=null;
      this.clipGroup=null;
      this.maskId='';
    }

    _createClass(SVGExtraState,[{
      key:"clone",
      value:functionclone(){
        returnObject.create(this);
      }
    },{
      key:"setCurrentPoint",
      value:functionsetCurrentPoint(x,y){
        this.x=x;
        this.y=y;
      }
    }]);

    returnSVGExtraState;
  }();

  varclipCount=0;
  varmaskCount=0;
  varshadingCount=0;

  exports.SVGGraphics=SVGGraphics=
  /*#__PURE__*/
  function(){
    functionSVGGraphics(commonObjs,objs,forceDataSchema){
      _classCallCheck(this,SVGGraphics);

      this.svgFactory=new_display_utils.DOMSVGFactory();
      this.current=newSVGExtraState();
      this.transformMatrix=_util.IDENTITY_MATRIX;
      this.transformStack=[];
      this.extraStack=[];
      this.commonObjs=commonObjs;
      this.objs=objs;
      this.pendingClip=null;
      this.pendingEOFill=false;
      this.embedFonts=false;
      this.embeddedFonts=Object.create(null);
      this.cssStyle=null;
      this.forceDataSchema=!!forceDataSchema;
      this._operatorIdMapping=[];

      for(varopin_util.OPS){
        this._operatorIdMapping[_util.OPS[op]]=op;
      }
    }

    _createClass(SVGGraphics,[{
      key:"save",
      value:functionsave(){
        this.transformStack.push(this.transformMatrix);
        varold=this.current;
        this.extraStack.push(old);
        this.current=old.clone();
      }
    },{
      key:"restore",
      value:functionrestore(){
        this.transformMatrix=this.transformStack.pop();
        this.current=this.extraStack.pop();
        this.pendingClip=null;
        this.tgrp=null;
      }
    },{
      key:"group",
      value:functiongroup(items){
        this.save();
        this.executeOpTree(items);
        this.restore();
      }
    },{
      key:"loadDependencies",
      value:functionloadDependencies(operatorList){
        var_this=this;

        varfnArray=operatorList.fnArray;
        varargsArray=operatorList.argsArray;

        for(vari=0,ii=fnArray.length;i<ii;i++){
          if(fnArray[i]!==_util.OPS.dependency){
            continue;
          }

          var_iteratorNormalCompletion2=true;
          var_didIteratorError2=false;
          var_iteratorError2=undefined;

          try{
            var_loop=function_loop(){
              varobj=_step2.value;
              varobjsPool=obj.startsWith('g_')?_this.commonObjs:_this.objs;
              varpromise=newPromise(function(resolve){
                objsPool.get(obj,resolve);
              });

              _this.current.dependencies.push(promise);
            };

            for(var_iterator2=argsArray[i][Symbol.iterator](),_step2;!(_iteratorNormalCompletion2=(_step2=_iterator2.next()).done);_iteratorNormalCompletion2=true){
              _loop();
            }
          }catch(err){
            _didIteratorError2=true;
            _iteratorError2=err;
          }finally{
            try{
              if(!_iteratorNormalCompletion2&&_iterator2["return"]!=null){
                _iterator2["return"]();
              }
            }finally{
              if(_didIteratorError2){
                throw_iteratorError2;
              }
            }
          }
        }

        returnPromise.all(this.current.dependencies);
      }
    },{
      key:"transform",
      value:functiontransform(a,b,c,d,e,f){
        vartransformMatrix=[a,b,c,d,e,f];
        this.transformMatrix=_util.Util.transform(this.transformMatrix,transformMatrix);
        this.tgrp=null;
      }
    },{
      key:"getSVG",
      value:functiongetSVG(operatorList,viewport){
        var_this2=this;

        this.viewport=viewport;

        varsvgElement=this._initialize(viewport);

        returnthis.loadDependencies(operatorList).then(function(){
          _this2.transformMatrix=_util.IDENTITY_MATRIX;

          _this2.executeOpTree(_this2.convertOpList(operatorList));

          returnsvgElement;
        });
      }
    },{
      key:"convertOpList",
      value:functionconvertOpList(operatorList){
        varoperatorIdMapping=this._operatorIdMapping;
        varargsArray=operatorList.argsArray;
        varfnArray=operatorList.fnArray;
        varopList=[];

        for(vari=0,ii=fnArray.length;i<ii;i++){
          varfnId=fnArray[i];
          opList.push({
            'fnId':fnId,
            'fn':operatorIdMapping[fnId],
            'args':argsArray[i]
          });
        }

        returnopListToTree(opList);
      }
    },{
      key:"executeOpTree",
      value:functionexecuteOpTree(opTree){
        var_iteratorNormalCompletion3=true;
        var_didIteratorError3=false;
        var_iteratorError3=undefined;

        try{
          for(var_iterator3=opTree[Symbol.iterator](),_step3;!(_iteratorNormalCompletion3=(_step3=_iterator3.next()).done);_iteratorNormalCompletion3=true){
            varopTreeElement=_step3.value;
            varfn=opTreeElement.fn;
            varfnId=opTreeElement.fnId;
            varargs=opTreeElement.args;

            switch(fnId|0){
              case_util.OPS.beginText:
                this.beginText();
                break;

              case_util.OPS.dependency:
                break;

              case_util.OPS.setLeading:
                this.setLeading(args);
                break;

              case_util.OPS.setLeadingMoveText:
                this.setLeadingMoveText(args[0],args[1]);
                break;

              case_util.OPS.setFont:
                this.setFont(args);
                break;

              case_util.OPS.showText:
                this.showText(args[0]);
                break;

              case_util.OPS.showSpacedText:
                this.showText(args[0]);
                break;

              case_util.OPS.endText:
                this.endText();
                break;

              case_util.OPS.moveText:
                this.moveText(args[0],args[1]);
                break;

              case_util.OPS.setCharSpacing:
                this.setCharSpacing(args[0]);
                break;

              case_util.OPS.setWordSpacing:
                this.setWordSpacing(args[0]);
                break;

              case_util.OPS.setHScale:
                this.setHScale(args[0]);
                break;

              case_util.OPS.setTextMatrix:
                this.setTextMatrix(args[0],args[1],args[2],args[3],args[4],args[5]);
                break;

              case_util.OPS.setTextRise:
                this.setTextRise(args[0]);
                break;

              case_util.OPS.setTextRenderingMode:
                this.setTextRenderingMode(args[0]);
                break;

              case_util.OPS.setLineWidth:
                this.setLineWidth(args[0]);
                break;

              case_util.OPS.setLineJoin:
                this.setLineJoin(args[0]);
                break;

              case_util.OPS.setLineCap:
                this.setLineCap(args[0]);
                break;

              case_util.OPS.setMiterLimit:
                this.setMiterLimit(args[0]);
                break;

              case_util.OPS.setFillRGBColor:
                this.setFillRGBColor(args[0],args[1],args[2]);
                break;

              case_util.OPS.setStrokeRGBColor:
                this.setStrokeRGBColor(args[0],args[1],args[2]);
                break;

              case_util.OPS.setStrokeColorN:
                this.setStrokeColorN(args);
                break;

              case_util.OPS.setFillColorN:
                this.setFillColorN(args);
                break;

              case_util.OPS.shadingFill:
                this.shadingFill(args[0]);
                break;

              case_util.OPS.setDash:
                this.setDash(args[0],args[1]);
                break;

              case_util.OPS.setRenderingIntent:
                this.setRenderingIntent(args[0]);
                break;

              case_util.OPS.setFlatness:
                this.setFlatness(args[0]);
                break;

              case_util.OPS.setGState:
                this.setGState(args[0]);
                break;

              case_util.OPS.fill:
                this.fill();
                break;

              case_util.OPS.eoFill:
                this.eoFill();
                break;

              case_util.OPS.stroke:
                this.stroke();
                break;

              case_util.OPS.fillStroke:
                this.fillStroke();
                break;

              case_util.OPS.eoFillStroke:
                this.eoFillStroke();
                break;

              case_util.OPS.clip:
                this.clip('nonzero');
                break;

              case_util.OPS.eoClip:
                this.clip('evenodd');
                break;

              case_util.OPS.paintSolidColorImageMask:
                this.paintSolidColorImageMask();
                break;

              case_util.OPS.paintJpegXObject:
                this.paintJpegXObject(args[0],args[1],args[2]);
                break;

              case_util.OPS.paintImageXObject:
                this.paintImageXObject(args[0]);
                break;

              case_util.OPS.paintInlineImageXObject:
                this.paintInlineImageXObject(args[0]);
                break;

              case_util.OPS.paintImageMaskXObject:
                this.paintImageMaskXObject(args[0]);
                break;

              case_util.OPS.paintFormXObjectBegin:
                this.paintFormXObjectBegin(args[0],args[1]);
                break;

              case_util.OPS.paintFormXObjectEnd:
                this.paintFormXObjectEnd();
                break;

              case_util.OPS.closePath:
                this.closePath();
                break;

              case_util.OPS.closeStroke:
                this.closeStroke();
                break;

              case_util.OPS.closeFillStroke:
                this.closeFillStroke();
                break;

              case_util.OPS.closeEOFillStroke:
                this.closeEOFillStroke();
                break;

              case_util.OPS.nextLine:
                this.nextLine();
                break;

              case_util.OPS.transform:
                this.transform(args[0],args[1],args[2],args[3],args[4],args[5]);
                break;

              case_util.OPS.constructPath:
                this.constructPath(args[0],args[1]);
                break;

              case_util.OPS.endPath:
                this.endPath();
                break;

              case92:
                this.group(opTreeElement.items);
                break;

              default:
                (0,_util.warn)("Unimplementedoperator".concat(fn));
                break;
            }
          }
        }catch(err){
          _didIteratorError3=true;
          _iteratorError3=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion3&&_iterator3["return"]!=null){
              _iterator3["return"]();
            }
          }finally{
            if(_didIteratorError3){
              throw_iteratorError3;
            }
          }
        }
      }
    },{
      key:"setWordSpacing",
      value:functionsetWordSpacing(wordSpacing){
        this.current.wordSpacing=wordSpacing;
      }
    },{
      key:"setCharSpacing",
      value:functionsetCharSpacing(charSpacing){
        this.current.charSpacing=charSpacing;
      }
    },{
      key:"nextLine",
      value:functionnextLine(){
        this.moveText(0,this.current.leading);
      }
    },{
      key:"setTextMatrix",
      value:functionsetTextMatrix(a,b,c,d,e,f){
        varcurrent=this.current;
        current.textMatrix=current.lineMatrix=[a,b,c,d,e,f];
        current.textMatrixScale=Math.sqrt(a*a+b*b);
        current.x=current.lineX=0;
        current.y=current.lineY=0;
        current.xcoords=[];
        current.tspan=this.svgFactory.createElement('svg:tspan');
        current.tspan.setAttributeNS(null,'font-family',current.fontFamily);
        current.tspan.setAttributeNS(null,'font-size',"".concat(pf(current.fontSize),"px"));
        current.tspan.setAttributeNS(null,'y',pf(-current.y));
        current.txtElement=this.svgFactory.createElement('svg:text');
        current.txtElement.appendChild(current.tspan);
      }
    },{
      key:"beginText",
      value:functionbeginText(){
        varcurrent=this.current;
        current.x=current.lineX=0;
        current.y=current.lineY=0;
        current.textMatrix=_util.IDENTITY_MATRIX;
        current.lineMatrix=_util.IDENTITY_MATRIX;
        current.textMatrixScale=1;
        current.tspan=this.svgFactory.createElement('svg:tspan');
        current.txtElement=this.svgFactory.createElement('svg:text');
        current.txtgrp=this.svgFactory.createElement('svg:g');
        current.xcoords=[];
      }
    },{
      key:"moveText",
      value:functionmoveText(x,y){
        varcurrent=this.current;
        current.x=current.lineX+=x;
        current.y=current.lineY+=y;
        current.xcoords=[];
        current.tspan=this.svgFactory.createElement('svg:tspan');
        current.tspan.setAttributeNS(null,'font-family',current.fontFamily);
        current.tspan.setAttributeNS(null,'font-size',"".concat(pf(current.fontSize),"px"));
        current.tspan.setAttributeNS(null,'y',pf(-current.y));
      }
    },{
      key:"showText",
      value:functionshowText(glyphs){
        varcurrent=this.current;
        varfont=current.font;
        varfontSize=current.fontSize;

        if(fontSize===0){
          return;
        }

        varcharSpacing=current.charSpacing;
        varwordSpacing=current.wordSpacing;
        varfontDirection=current.fontDirection;
        vartextHScale=current.textHScale*fontDirection;
        varvertical=font.vertical;
        varwidthAdvanceScale=fontSize*current.fontMatrix[0];
        varx=0;
        var_iteratorNormalCompletion4=true;
        var_didIteratorError4=false;
        var_iteratorError4=undefined;

        try{
          for(var_iterator4=glyphs[Symbol.iterator](),_step4;!(_iteratorNormalCompletion4=(_step4=_iterator4.next()).done);_iteratorNormalCompletion4=true){
            varglyph=_step4.value;

            if(glyph===null){
              x+=fontDirection*wordSpacing;
              continue;
            }elseif((0,_util.isNum)(glyph)){
              x+=-glyph*fontSize*0.001;
              continue;
            }

            varwidth=glyph.width;
            varcharacter=glyph.fontChar;
            varspacing=(glyph.isSpace?wordSpacing:0)+charSpacing;
            varcharWidth=width*widthAdvanceScale+spacing*fontDirection;

            if(!glyph.isInFont&&!font.missingFile){
              x+=charWidth;
              continue;
            }

            current.xcoords.push(current.x+x*textHScale);
            current.tspan.textContent+=character;
            x+=charWidth;
          }
        }catch(err){
          _didIteratorError4=true;
          _iteratorError4=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion4&&_iterator4["return"]!=null){
              _iterator4["return"]();
            }
          }finally{
            if(_didIteratorError4){
              throw_iteratorError4;
            }
          }
        }

        if(vertical){
          current.y-=x*textHScale;
        }else{
          current.x+=x*textHScale;
        }

        current.tspan.setAttributeNS(null,'x',current.xcoords.map(pf).join(''));
        current.tspan.setAttributeNS(null,'y',pf(-current.y));
        current.tspan.setAttributeNS(null,'font-family',current.fontFamily);
        current.tspan.setAttributeNS(null,'font-size',"".concat(pf(current.fontSize),"px"));

        if(current.fontStyle!==SVG_DEFAULTS.fontStyle){
          current.tspan.setAttributeNS(null,'font-style',current.fontStyle);
        }

        if(current.fontWeight!==SVG_DEFAULTS.fontWeight){
          current.tspan.setAttributeNS(null,'font-weight',current.fontWeight);
        }

        varfillStrokeMode=current.textRenderingMode&_util.TextRenderingMode.FILL_STROKE_MASK;

        if(fillStrokeMode===_util.TextRenderingMode.FILL||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          if(current.fillColor!==SVG_DEFAULTS.fillColor){
            current.tspan.setAttributeNS(null,'fill',current.fillColor);
          }

          if(current.fillAlpha<1){
            current.tspan.setAttributeNS(null,'fill-opacity',current.fillAlpha);
          }
        }elseif(current.textRenderingMode===_util.TextRenderingMode.ADD_TO_PATH){
          current.tspan.setAttributeNS(null,'fill','transparent');
        }else{
          current.tspan.setAttributeNS(null,'fill','none');
        }

        if(fillStrokeMode===_util.TextRenderingMode.STROKE||fillStrokeMode===_util.TextRenderingMode.FILL_STROKE){
          varlineWidthScale=1/(current.textMatrixScale||1);

          this._setStrokeAttributes(current.tspan,lineWidthScale);
        }

        vartextMatrix=current.textMatrix;

        if(current.textRise!==0){
          textMatrix=textMatrix.slice();
          textMatrix[5]+=current.textRise;
        }

        current.txtElement.setAttributeNS(null,'transform',"".concat(pm(textMatrix),"scale(1,-1)"));
        current.txtElement.setAttributeNS(XML_NS,'xml:space','preserve');
        current.txtElement.appendChild(current.tspan);
        current.txtgrp.appendChild(current.txtElement);

        this._ensureTransformGroup().appendChild(current.txtElement);
      }
    },{
      key:"setLeadingMoveText",
      value:functionsetLeadingMoveText(x,y){
        this.setLeading(-y);
        this.moveText(x,y);
      }
    },{
      key:"addFontStyle",
      value:functionaddFontStyle(fontObj){
        if(!this.cssStyle){
          this.cssStyle=this.svgFactory.createElement('svg:style');
          this.cssStyle.setAttributeNS(null,'type','text/css');
          this.defs.appendChild(this.cssStyle);
        }

        varurl=(0,_util.createObjectURL)(fontObj.data,fontObj.mimetype,this.forceDataSchema);
        this.cssStyle.textContent+="@font-face{font-family:\"".concat(fontObj.loadedName,"\";")+"src:url(".concat(url,");}\n");
      }
    },{
      key:"setFont",
      value:functionsetFont(details){
        varcurrent=this.current;
        varfontObj=this.commonObjs.get(details[0]);
        varsize=details[1];
        current.font=fontObj;

        if(this.embedFonts&&fontObj.data&&!this.embeddedFonts[fontObj.loadedName]){
          this.addFontStyle(fontObj);
          this.embeddedFonts[fontObj.loadedName]=fontObj;
        }

        current.fontMatrix=fontObj.fontMatrix?fontObj.fontMatrix:_util.FONT_IDENTITY_MATRIX;
        varbold=fontObj.black?fontObj.bold?'bolder':'bold':fontObj.bold?'bold':'normal';
        varitalic=fontObj.italic?'italic':'normal';

        if(size<0){
          size=-size;
          current.fontDirection=-1;
        }else{
          current.fontDirection=1;
        }

        current.fontSize=size;
        current.fontFamily=fontObj.loadedName;
        current.fontWeight=bold;
        current.fontStyle=italic;
        current.tspan=this.svgFactory.createElement('svg:tspan');
        current.tspan.setAttributeNS(null,'y',pf(-current.y));
        current.xcoords=[];
      }
    },{
      key:"endText",
      value:functionendText(){
        varcurrent=this.current;

        if(current.textRenderingMode&_util.TextRenderingMode.ADD_TO_PATH_FLAG&&current.txtElement&&current.txtElement.hasChildNodes()){
          current.element=current.txtElement;
          this.clip('nonzero');
          this.endPath();
        }
      }
    },{
      key:"setLineWidth",
      value:functionsetLineWidth(width){
        if(width>0){
          this.current.lineWidth=width;
        }
      }
    },{
      key:"setLineCap",
      value:functionsetLineCap(style){
        this.current.lineCap=LINE_CAP_STYLES[style];
      }
    },{
      key:"setLineJoin",
      value:functionsetLineJoin(style){
        this.current.lineJoin=LINE_JOIN_STYLES[style];
      }
    },{
      key:"setMiterLimit",
      value:functionsetMiterLimit(limit){
        this.current.miterLimit=limit;
      }
    },{
      key:"setStrokeAlpha",
      value:functionsetStrokeAlpha(strokeAlpha){
        this.current.strokeAlpha=strokeAlpha;
      }
    },{
      key:"setStrokeRGBColor",
      value:functionsetStrokeRGBColor(r,g,b){
        this.current.strokeColor=_util.Util.makeCssRgb(r,g,b);
      }
    },{
      key:"setFillAlpha",
      value:functionsetFillAlpha(fillAlpha){
        this.current.fillAlpha=fillAlpha;
      }
    },{
      key:"setFillRGBColor",
      value:functionsetFillRGBColor(r,g,b){
        this.current.fillColor=_util.Util.makeCssRgb(r,g,b);
        this.current.tspan=this.svgFactory.createElement('svg:tspan');
        this.current.xcoords=[];
      }
    },{
      key:"setStrokeColorN",
      value:functionsetStrokeColorN(args){
        this.current.strokeColor=this._makeColorN_Pattern(args);
      }
    },{
      key:"setFillColorN",
      value:functionsetFillColorN(args){
        this.current.fillColor=this._makeColorN_Pattern(args);
      }
    },{
      key:"shadingFill",
      value:functionshadingFill(args){
        varwidth=this.viewport.width;
        varheight=this.viewport.height;

        varinv=_util.Util.inverseTransform(this.transformMatrix);

        varbl=_util.Util.applyTransform([0,0],inv);

        varbr=_util.Util.applyTransform([0,height],inv);

        varul=_util.Util.applyTransform([width,0],inv);

        varur=_util.Util.applyTransform([width,height],inv);

        varx0=Math.min(bl[0],br[0],ul[0],ur[0]);
        vary0=Math.min(bl[1],br[1],ul[1],ur[1]);
        varx1=Math.max(bl[0],br[0],ul[0],ur[0]);
        vary1=Math.max(bl[1],br[1],ul[1],ur[1]);
        varrect=this.svgFactory.createElement('svg:rect');
        rect.setAttributeNS(null,'x',x0);
        rect.setAttributeNS(null,'y',y0);
        rect.setAttributeNS(null,'width',x1-x0);
        rect.setAttributeNS(null,'height',y1-y0);
        rect.setAttributeNS(null,'fill',this._makeShadingPattern(args));

        this._ensureTransformGroup().appendChild(rect);
      }
    },{
      key:"_makeColorN_Pattern",
      value:function_makeColorN_Pattern(args){
        if(args[0]==='TilingPattern'){
          returnthis._makeTilingPattern(args);
        }

        returnthis._makeShadingPattern(args);
      }
    },{
      key:"_makeTilingPattern",
      value:function_makeTilingPattern(args){
        varcolor=args[1];
        varoperatorList=args[2];
        varmatrix=args[3]||_util.IDENTITY_MATRIX;

        var_args$=_slicedToArray(args[4],4),
            x0=_args$[0],
            y0=_args$[1],
            x1=_args$[2],
            y1=_args$[3];

        varxstep=args[5];
        varystep=args[6];
        varpaintType=args[7];
        vartilingId="shading".concat(shadingCount++);

        var_Util$applyTransform=_util.Util.applyTransform([x0,y0],matrix),
            _Util$applyTransform2=_slicedToArray(_Util$applyTransform,2),
            tx0=_Util$applyTransform2[0],
            ty0=_Util$applyTransform2[1];

        var_Util$applyTransform3=_util.Util.applyTransform([x1,y1],matrix),
            _Util$applyTransform4=_slicedToArray(_Util$applyTransform3,2),
            tx1=_Util$applyTransform4[0],
            ty1=_Util$applyTransform4[1];

        var_Util$singularValueDe=_util.Util.singularValueDecompose2dScale(matrix),
            _Util$singularValueDe2=_slicedToArray(_Util$singularValueDe,2),
            xscale=_Util$singularValueDe2[0],
            yscale=_Util$singularValueDe2[1];

        vartxstep=xstep*xscale;
        vartystep=ystep*yscale;
        vartiling=this.svgFactory.createElement('svg:pattern');
        tiling.setAttributeNS(null,'id',tilingId);
        tiling.setAttributeNS(null,'patternUnits','userSpaceOnUse');
        tiling.setAttributeNS(null,'width',txstep);
        tiling.setAttributeNS(null,'height',tystep);
        tiling.setAttributeNS(null,'x',"".concat(tx0));
        tiling.setAttributeNS(null,'y',"".concat(ty0));
        varsvg=this.svg;
        vartransformMatrix=this.transformMatrix;
        varfillColor=this.current.fillColor;
        varstrokeColor=this.current.strokeColor;
        varbbox=this.svgFactory.create(tx1-tx0,ty1-ty0);
        this.svg=bbox;
        this.transformMatrix=matrix;

        if(paintType===2){
          varcssColor=_util.Util.makeCssRgb.apply(_util.Util,_toConsumableArray(color));

          this.current.fillColor=cssColor;
          this.current.strokeColor=cssColor;
        }

        this.executeOpTree(this.convertOpList(operatorList));
        this.svg=svg;
        this.transformMatrix=transformMatrix;
        this.current.fillColor=fillColor;
        this.current.strokeColor=strokeColor;
        tiling.appendChild(bbox.childNodes[0]);
        this.defs.appendChild(tiling);
        return"url(#".concat(tilingId,")");
      }
    },{
      key:"_makeShadingPattern",
      value:function_makeShadingPattern(args){
        switch(args[0]){
          case'RadialAxial':
            varshadingId="shading".concat(shadingCount++);
            varcolorStops=args[2];
            vargradient;

            switch(args[1]){
              case'axial':
                varpoint0=args[3];
                varpoint1=args[4];
                gradient=this.svgFactory.createElement('svg:linearGradient');
                gradient.setAttributeNS(null,'id',shadingId);
                gradient.setAttributeNS(null,'gradientUnits','userSpaceOnUse');
                gradient.setAttributeNS(null,'x1',point0[0]);
                gradient.setAttributeNS(null,'y1',point0[1]);
                gradient.setAttributeNS(null,'x2',point1[0]);
                gradient.setAttributeNS(null,'y2',point1[1]);
                break;

              case'radial':
                varfocalPoint=args[3];
                varcirclePoint=args[4];
                varfocalRadius=args[5];
                varcircleRadius=args[6];
                gradient=this.svgFactory.createElement('svg:radialGradient');
                gradient.setAttributeNS(null,'id',shadingId);
                gradient.setAttributeNS(null,'gradientUnits','userSpaceOnUse');
                gradient.setAttributeNS(null,'cx',circlePoint[0]);
                gradient.setAttributeNS(null,'cy',circlePoint[1]);
                gradient.setAttributeNS(null,'r',circleRadius);
                gradient.setAttributeNS(null,'fx',focalPoint[0]);
                gradient.setAttributeNS(null,'fy',focalPoint[1]);
                gradient.setAttributeNS(null,'fr',focalRadius);
                break;

              default:
                thrownewError("UnknownRadialAxialtype:".concat(args[1]));
            }

            var_iteratorNormalCompletion5=true;
            var_didIteratorError5=false;
            var_iteratorError5=undefined;

            try{
              for(var_iterator5=colorStops[Symbol.iterator](),_step5;!(_iteratorNormalCompletion5=(_step5=_iterator5.next()).done);_iteratorNormalCompletion5=true){
                varcolorStop=_step5.value;
                varstop=this.svgFactory.createElement('svg:stop');
                stop.setAttributeNS(null,'offset',colorStop[0]);
                stop.setAttributeNS(null,'stop-color',colorStop[1]);
                gradient.appendChild(stop);
              }
            }catch(err){
              _didIteratorError5=true;
              _iteratorError5=err;
            }finally{
              try{
                if(!_iteratorNormalCompletion5&&_iterator5["return"]!=null){
                  _iterator5["return"]();
                }
              }finally{
                if(_didIteratorError5){
                  throw_iteratorError5;
                }
              }
            }

            this.defs.appendChild(gradient);
            return"url(#".concat(shadingId,")");

          case'Mesh':
            (0,_util.warn)('UnimplementedpatternMesh');
            returnnull;

          case'Dummy':
            return'hotpink';

          default:
            thrownewError("UnknownIRtype:".concat(args[0]));
        }
      }
    },{
      key:"setDash",
      value:functionsetDash(dashArray,dashPhase){
        this.current.dashArray=dashArray;
        this.current.dashPhase=dashPhase;
      }
    },{
      key:"constructPath",
      value:functionconstructPath(ops,args){
        varcurrent=this.current;
        varx=current.x,
            y=current.y;
        vard=[];
        varj=0;
        var_iteratorNormalCompletion6=true;
        var_didIteratorError6=false;
        var_iteratorError6=undefined;

        try{
          for(var_iterator6=ops[Symbol.iterator](),_step6;!(_iteratorNormalCompletion6=(_step6=_iterator6.next()).done);_iteratorNormalCompletion6=true){
            varop=_step6.value;

            switch(op|0){
              case_util.OPS.rectangle:
                x=args[j++];
                y=args[j++];
                varwidth=args[j++];
                varheight=args[j++];
                varxw=x+width;
                varyh=y+height;
                d.push('M',pf(x),pf(y),'L',pf(xw),pf(y),'L',pf(xw),pf(yh),'L',pf(x),pf(yh),'Z');
                break;

              case_util.OPS.moveTo:
                x=args[j++];
                y=args[j++];
                d.push('M',pf(x),pf(y));
                break;

              case_util.OPS.lineTo:
                x=args[j++];
                y=args[j++];
                d.push('L',pf(x),pf(y));
                break;

              case_util.OPS.curveTo:
                x=args[j+4];
                y=args[j+5];
                d.push('C',pf(args[j]),pf(args[j+1]),pf(args[j+2]),pf(args[j+3]),pf(x),pf(y));
                j+=6;
                break;

              case_util.OPS.curveTo2:
                x=args[j+2];
                y=args[j+3];
                d.push('C',pf(x),pf(y),pf(args[j]),pf(args[j+1]),pf(args[j+2]),pf(args[j+3]));
                j+=4;
                break;

              case_util.OPS.curveTo3:
                x=args[j+2];
                y=args[j+3];
                d.push('C',pf(args[j]),pf(args[j+1]),pf(x),pf(y),pf(x),pf(y));
                j+=4;
                break;

              case_util.OPS.closePath:
                d.push('Z');
                break;
            }
          }
        }catch(err){
          _didIteratorError6=true;
          _iteratorError6=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion6&&_iterator6["return"]!=null){
              _iterator6["return"]();
            }
          }finally{
            if(_didIteratorError6){
              throw_iteratorError6;
            }
          }
        }

        d=d.join('');

        if(current.path&&ops.length>0&&ops[0]!==_util.OPS.rectangle&&ops[0]!==_util.OPS.moveTo){
          d=current.path.getAttributeNS(null,'d')+d;
        }else{
          current.path=this.svgFactory.createElement('svg:path');

          this._ensureTransformGroup().appendChild(current.path);
        }

        current.path.setAttributeNS(null,'d',d);
        current.path.setAttributeNS(null,'fill','none');
        current.element=current.path;
        current.setCurrentPoint(x,y);
      }
    },{
      key:"endPath",
      value:functionendPath(){
        varcurrent=this.current;
        current.path=null;

        if(!this.pendingClip){
          return;
        }

        if(!current.element){
          this.pendingClip=null;
          return;
        }

        varclipId="clippath".concat(clipCount++);
        varclipPath=this.svgFactory.createElement('svg:clipPath');
        clipPath.setAttributeNS(null,'id',clipId);
        clipPath.setAttributeNS(null,'transform',pm(this.transformMatrix));
        varclipElement=current.element.cloneNode(true);

        if(this.pendingClip==='evenodd'){
          clipElement.setAttributeNS(null,'clip-rule','evenodd');
        }else{
          clipElement.setAttributeNS(null,'clip-rule','nonzero');
        }

        this.pendingClip=null;
        clipPath.appendChild(clipElement);
        this.defs.appendChild(clipPath);

        if(current.activeClipUrl){
          current.clipGroup=null;
          this.extraStack.forEach(function(prev){
            prev.clipGroup=null;
          });
          clipPath.setAttributeNS(null,'clip-path',current.activeClipUrl);
        }

        current.activeClipUrl="url(#".concat(clipId,")");
        this.tgrp=null;
      }
    },{
      key:"clip",
      value:functionclip(type){
        this.pendingClip=type;
      }
    },{
      key:"closePath",
      value:functionclosePath(){
        varcurrent=this.current;

        if(current.path){
          vard="".concat(current.path.getAttributeNS(null,'d'),"Z");
          current.path.setAttributeNS(null,'d',d);
        }
      }
    },{
      key:"setLeading",
      value:functionsetLeading(leading){
        this.current.leading=-leading;
      }
    },{
      key:"setTextRise",
      value:functionsetTextRise(textRise){
        this.current.textRise=textRise;
      }
    },{
      key:"setTextRenderingMode",
      value:functionsetTextRenderingMode(textRenderingMode){
        this.current.textRenderingMode=textRenderingMode;
      }
    },{
      key:"setHScale",
      value:functionsetHScale(scale){
        this.current.textHScale=scale/100;
      }
    },{
      key:"setRenderingIntent",
      value:functionsetRenderingIntent(intent){}
    },{
      key:"setFlatness",
      value:functionsetFlatness(flatness){}
    },{
      key:"setGState",
      value:functionsetGState(states){
        var_iteratorNormalCompletion7=true;
        var_didIteratorError7=false;
        var_iteratorError7=undefined;

        try{
          for(var_iterator7=states[Symbol.iterator](),_step7;!(_iteratorNormalCompletion7=(_step7=_iterator7.next()).done);_iteratorNormalCompletion7=true){
            var_step7$value=_slicedToArray(_step7.value,2),
                key=_step7$value[0],
                value=_step7$value[1];

            switch(key){
              case'LW':
                this.setLineWidth(value);
                break;

              case'LC':
                this.setLineCap(value);
                break;

              case'LJ':
                this.setLineJoin(value);
                break;

              case'ML':
                this.setMiterLimit(value);
                break;

              case'D':
                this.setDash(value[0],value[1]);
                break;

              case'RI':
                this.setRenderingIntent(value);
                break;

              case'FL':
                this.setFlatness(value);
                break;

              case'Font':
                this.setFont(value);
                break;

              case'CA':
                this.setStrokeAlpha(value);
                break;

              case'ca':
                this.setFillAlpha(value);
                break;

              default:
                (0,_util.warn)("Unimplementedgraphicstateoperator".concat(key));
                break;
            }
          }
        }catch(err){
          _didIteratorError7=true;
          _iteratorError7=err;
        }finally{
          try{
            if(!_iteratorNormalCompletion7&&_iterator7["return"]!=null){
              _iterator7["return"]();
            }
          }finally{
            if(_didIteratorError7){
              throw_iteratorError7;
            }
          }
        }
      }
    },{
      key:"fill",
      value:functionfill(){
        varcurrent=this.current;

        if(current.element){
          current.element.setAttributeNS(null,'fill',current.fillColor);
          current.element.setAttributeNS(null,'fill-opacity',current.fillAlpha);
          this.endPath();
        }
      }
    },{
      key:"stroke",
      value:functionstroke(){
        varcurrent=this.current;

        if(current.element){
          this._setStrokeAttributes(current.element);

          current.element.setAttributeNS(null,'fill','none');
          this.endPath();
        }
      }
    },{
      key:"_setStrokeAttributes",
      value:function_setStrokeAttributes(element){
        varlineWidthScale=arguments.length>1&&arguments[1]!==undefined?arguments[1]:1;
        varcurrent=this.current;
        vardashArray=current.dashArray;

        if(lineWidthScale!==1&&dashArray.length>0){
          dashArray=dashArray.map(function(value){
            returnlineWidthScale*value;
          });
        }

        element.setAttributeNS(null,'stroke',current.strokeColor);
        element.setAttributeNS(null,'stroke-opacity',current.strokeAlpha);
        element.setAttributeNS(null,'stroke-miterlimit',pf(current.miterLimit));
        element.setAttributeNS(null,'stroke-linecap',current.lineCap);
        element.setAttributeNS(null,'stroke-linejoin',current.lineJoin);
        element.setAttributeNS(null,'stroke-width',pf(lineWidthScale*current.lineWidth)+'px');
        element.setAttributeNS(null,'stroke-dasharray',dashArray.map(pf).join(''));
        element.setAttributeNS(null,'stroke-dashoffset',pf(lineWidthScale*current.dashPhase)+'px');
      }
    },{
      key:"eoFill",
      value:functioneoFill(){
        if(this.current.element){
          this.current.element.setAttributeNS(null,'fill-rule','evenodd');
        }

        this.fill();
      }
    },{
      key:"fillStroke",
      value:functionfillStroke(){
        this.stroke();
        this.fill();
      }
    },{
      key:"eoFillStroke",
      value:functioneoFillStroke(){
        if(this.current.element){
          this.current.element.setAttributeNS(null,'fill-rule','evenodd');
        }

        this.fillStroke();
      }
    },{
      key:"closeStroke",
      value:functioncloseStroke(){
        this.closePath();
        this.stroke();
      }
    },{
      key:"closeFillStroke",
      value:functioncloseFillStroke(){
        this.closePath();
        this.fillStroke();
      }
    },{
      key:"closeEOFillStroke",
      value:functioncloseEOFillStroke(){
        this.closePath();
        this.eoFillStroke();
      }
    },{
      key:"paintSolidColorImageMask",
      value:functionpaintSolidColorImageMask(){
        varrect=this.svgFactory.createElement('svg:rect');
        rect.setAttributeNS(null,'x','0');
        rect.setAttributeNS(null,'y','0');
        rect.setAttributeNS(null,'width','1px');
        rect.setAttributeNS(null,'height','1px');
        rect.setAttributeNS(null,'fill',this.current.fillColor);

        this._ensureTransformGroup().appendChild(rect);
      }
    },{
      key:"paintJpegXObject",
      value:functionpaintJpegXObject(objId,w,h){
        varimgObj=this.objs.get(objId);
        varimgEl=this.svgFactory.createElement('svg:image');
        imgEl.setAttributeNS(XLINK_NS,'xlink:href',imgObj.src);
        imgEl.setAttributeNS(null,'width',pf(w));
        imgEl.setAttributeNS(null,'height',pf(h));
        imgEl.setAttributeNS(null,'x','0');
        imgEl.setAttributeNS(null,'y',pf(-h));
        imgEl.setAttributeNS(null,'transform',"scale(".concat(pf(1/w),"").concat(pf(-1/h),")"));

        this._ensureTransformGroup().appendChild(imgEl);
      }
    },{
      key:"paintImageXObject",
      value:functionpaintImageXObject(objId){
        varimgData=this.objs.get(objId);

        if(!imgData){
          (0,_util.warn)("DependentimagewithobjectID".concat(objId,"isnotreadyyet"));
          return;
        }

        this.paintInlineImageXObject(imgData);
      }
    },{
      key:"paintInlineImageXObject",
      value:functionpaintInlineImageXObject(imgData,mask){
        varwidth=imgData.width;
        varheight=imgData.height;
        varimgSrc=convertImgDataToPng(imgData,this.forceDataSchema,!!mask);
        varcliprect=this.svgFactory.createElement('svg:rect');
        cliprect.setAttributeNS(null,'x','0');
        cliprect.setAttributeNS(null,'y','0');
        cliprect.setAttributeNS(null,'width',pf(width));
        cliprect.setAttributeNS(null,'height',pf(height));
        this.current.element=cliprect;
        this.clip('nonzero');
        varimgEl=this.svgFactory.createElement('svg:image');
        imgEl.setAttributeNS(XLINK_NS,'xlink:href',imgSrc);
        imgEl.setAttributeNS(null,'x','0');
        imgEl.setAttributeNS(null,'y',pf(-height));
        imgEl.setAttributeNS(null,'width',pf(width)+'px');
        imgEl.setAttributeNS(null,'height',pf(height)+'px');
        imgEl.setAttributeNS(null,'transform',"scale(".concat(pf(1/width),"").concat(pf(-1/height),")"));

        if(mask){
          mask.appendChild(imgEl);
        }else{
          this._ensureTransformGroup().appendChild(imgEl);
        }
      }
    },{
      key:"paintImageMaskXObject",
      value:functionpaintImageMaskXObject(imgData){
        varcurrent=this.current;
        varwidth=imgData.width;
        varheight=imgData.height;
        varfillColor=current.fillColor;
        current.maskId="mask".concat(maskCount++);
        varmask=this.svgFactory.createElement('svg:mask');
        mask.setAttributeNS(null,'id',current.maskId);
        varrect=this.svgFactory.createElement('svg:rect');
        rect.setAttributeNS(null,'x','0');
        rect.setAttributeNS(null,'y','0');
        rect.setAttributeNS(null,'width',pf(width));
        rect.setAttributeNS(null,'height',pf(height));
        rect.setAttributeNS(null,'fill',fillColor);
        rect.setAttributeNS(null,'mask',"url(#".concat(current.maskId,")"));
        this.defs.appendChild(mask);

        this._ensureTransformGroup().appendChild(rect);

        this.paintInlineImageXObject(imgData,mask);
      }
    },{
      key:"paintFormXObjectBegin",
      value:functionpaintFormXObjectBegin(matrix,bbox){
        if(Array.isArray(matrix)&&matrix.length===6){
          this.transform(matrix[0],matrix[1],matrix[2],matrix[3],matrix[4],matrix[5]);
        }

        if(bbox){
          varwidth=bbox[2]-bbox[0];
          varheight=bbox[3]-bbox[1];
          varcliprect=this.svgFactory.createElement('svg:rect');
          cliprect.setAttributeNS(null,'x',bbox[0]);
          cliprect.setAttributeNS(null,'y',bbox[1]);
          cliprect.setAttributeNS(null,'width',pf(width));
          cliprect.setAttributeNS(null,'height',pf(height));
          this.current.element=cliprect;
          this.clip('nonzero');
          this.endPath();
        }
      }
    },{
      key:"paintFormXObjectEnd",
      value:functionpaintFormXObjectEnd(){}
    },{
      key:"_initialize",
      value:function_initialize(viewport){
        varsvg=this.svgFactory.create(viewport.width,viewport.height);
        vardefinitions=this.svgFactory.createElement('svg:defs');
        svg.appendChild(definitions);
        this.defs=definitions;
        varrootGroup=this.svgFactory.createElement('svg:g');
        rootGroup.setAttributeNS(null,'transform',pm(viewport.transform));
        svg.appendChild(rootGroup);
        this.svg=rootGroup;
        returnsvg;
      }
    },{
      key:"_ensureClipGroup",
      value:function_ensureClipGroup(){
        if(!this.current.clipGroup){
          varclipGroup=this.svgFactory.createElement('svg:g');
          clipGroup.setAttributeNS(null,'clip-path',this.current.activeClipUrl);
          this.svg.appendChild(clipGroup);
          this.current.clipGroup=clipGroup;
        }

        returnthis.current.clipGroup;
      }
    },{
      key:"_ensureTransformGroup",
      value:function_ensureTransformGroup(){
        if(!this.tgrp){
          this.tgrp=this.svgFactory.createElement('svg:g');
          this.tgrp.setAttributeNS(null,'transform',pm(this.transformMatrix));

          if(this.current.activeClipUrl){
            this._ensureClipGroup().appendChild(this.tgrp);
          }else{
            this.svg.appendChild(this.tgrp);
          }
        }

        returnthis.tgrp;
      }
    }]);

    returnSVGGraphics;
  }();
}

/***/}),
/*165*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFNodeStream=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

var_network_utils=__w_pdfjs_require__(166);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varfs=require('fs');

varhttp=require('http');

varhttps=require('https');

varurl=require('url');

varfileUriRegex=/^file:\/\/\/[a-zA-Z]:\//;

functionparseUrl(sourceUrl){
  varparsedUrl=url.parse(sourceUrl);

  if(parsedUrl.protocol==='file:'||parsedUrl.host){
    returnparsedUrl;
  }

  if(/^[a-z]:[/\\]/i.test(sourceUrl)){
    returnurl.parse("file:///".concat(sourceUrl));
  }

  if(!parsedUrl.host){
    parsedUrl.protocol='file:';
  }

  returnparsedUrl;
}

varPDFNodeStream=
/*#__PURE__*/
function(){
  functionPDFNodeStream(source){
    _classCallCheck(this,PDFNodeStream);

    this.source=source;
    this.url=parseUrl(source.url);
    this.isHttp=this.url.protocol==='http:'||this.url.protocol==='https:';
    this.isFsUrl=this.url.protocol==='file:';
    this.httpHeaders=this.isHttp&&source.httpHeaders||{};
    this._fullRequestReader=null;
    this._rangeRequestReaders=[];
  }

  _createClass(PDFNodeStream,[{
    key:"getFullReader",
    value:functiongetFullReader(){
      (0,_util.assert)(!this._fullRequestReader);
      this._fullRequestReader=this.isFsUrl?newPDFNodeStreamFsFullReader(this):newPDFNodeStreamFullReader(this);
      returnthis._fullRequestReader;
    }
  },{
    key:"getRangeReader",
    value:functiongetRangeReader(start,end){
      if(end<=this._progressiveDataLength){
        returnnull;
      }

      varrangeReader=this.isFsUrl?newPDFNodeStreamFsRangeReader(this,start,end):newPDFNodeStreamRangeReader(this,start,end);

      this._rangeRequestReaders.push(rangeReader);

      returnrangeReader;
    }
  },{
    key:"cancelAllRequests",
    value:functioncancelAllRequests(reason){
      if(this._fullRequestReader){
        this._fullRequestReader.cancel(reason);
      }

      varreaders=this._rangeRequestReaders.slice(0);

      readers.forEach(function(reader){
        reader.cancel(reason);
      });
    }
  },{
    key:"_progressiveDataLength",
    get:functionget(){
      returnthis._fullRequestReader?this._fullRequestReader._loaded:0;
    }
  }]);

  returnPDFNodeStream;
}();

exports.PDFNodeStream=PDFNodeStream;

varBaseFullReader=
/*#__PURE__*/
function(){
  functionBaseFullReader(stream){
    _classCallCheck(this,BaseFullReader);

    this._url=stream.url;
    this._done=false;
    this._storedError=null;
    this.onProgress=null;
    varsource=stream.source;
    this._contentLength=source.length;
    this._loaded=0;
    this._filename=null;
    this._disableRange=source.disableRange||false;
    this._rangeChunkSize=source.rangeChunkSize;

    if(!this._rangeChunkSize&&!this._disableRange){
      this._disableRange=true;
    }

    this._isStreamingSupported=!source.disableStream;
    this._isRangeSupported=!source.disableRange;
    this._readableStream=null;
    this._readCapability=(0,_util.createPromiseCapability)();
    this._headersCapability=(0,_util.createPromiseCapability)();
  }

  _createClass(BaseFullReader,[{
    key:"read",
    value:function(){
      var_read=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        varchunk,buffer;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                _context.next=2;
                returnthis._readCapability.promise;

              case2:
                if(!this._done){
                  _context.next=4;
                  break;
                }

                return_context.abrupt("return",{
                  value:undefined,
                  done:true
                });

              case4:
                if(!this._storedError){
                  _context.next=6;
                  break;
                }

                throwthis._storedError;

              case6:
                chunk=this._readableStream.read();

                if(!(chunk===null)){
                  _context.next=10;
                  break;
                }

                this._readCapability=(0,_util.createPromiseCapability)();
                return_context.abrupt("return",this.read());

              case10:
                this._loaded+=chunk.length;

                if(this.onProgress){
                  this.onProgress({
                    loaded:this._loaded,
                    total:this._contentLength
                  });
                }

                buffer=newUint8Array(chunk).buffer;
                return_context.abrupt("return",{
                  value:buffer,
                  done:false
                });

              case14:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      functionread(){
        return_read.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      if(!this._readableStream){
        this._error(reason);

        return;
      }

      this._readableStream.destroy(reason);
    }
  },{
    key:"_error",
    value:function_error(reason){
      this._storedError=reason;

      this._readCapability.resolve();
    }
  },{
    key:"_setReadableStream",
    value:function_setReadableStream(readableStream){
      var_this=this;

      this._readableStream=readableStream;
      readableStream.on('readable',function(){
        _this._readCapability.resolve();
      });
      readableStream.on('end',function(){
        readableStream.destroy();
        _this._done=true;

        _this._readCapability.resolve();
      });
      readableStream.on('error',function(reason){
        _this._error(reason);
      });

      if(!this._isStreamingSupported&&this._isRangeSupported){
        this._error(new_util.AbortException('streamingisdisabled'));
      }

      if(this._storedError){
        this._readableStream.destroy(this._storedError);
      }
    }
  },{
    key:"headersReady",
    get:functionget(){
      returnthis._headersCapability.promise;
    }
  },{
    key:"filename",
    get:functionget(){
      returnthis._filename;
    }
  },{
    key:"contentLength",
    get:functionget(){
      returnthis._contentLength;
    }
  },{
    key:"isRangeSupported",
    get:functionget(){
      returnthis._isRangeSupported;
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnthis._isStreamingSupported;
    }
  }]);

  returnBaseFullReader;
}();

varBaseRangeReader=
/*#__PURE__*/
function(){
  functionBaseRangeReader(stream){
    _classCallCheck(this,BaseRangeReader);

    this._url=stream.url;
    this._done=false;
    this._storedError=null;
    this.onProgress=null;
    this._loaded=0;
    this._readableStream=null;
    this._readCapability=(0,_util.createPromiseCapability)();
    varsource=stream.source;
    this._isStreamingSupported=!source.disableStream;
  }

  _createClass(BaseRangeReader,[{
    key:"read",
    value:function(){
      var_read2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(){
        varchunk,buffer;
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                _context2.next=2;
                returnthis._readCapability.promise;

              case2:
                if(!this._done){
                  _context2.next=4;
                  break;
                }

                return_context2.abrupt("return",{
                  value:undefined,
                  done:true
                });

              case4:
                if(!this._storedError){
                  _context2.next=6;
                  break;
                }

                throwthis._storedError;

              case6:
                chunk=this._readableStream.read();

                if(!(chunk===null)){
                  _context2.next=10;
                  break;
                }

                this._readCapability=(0,_util.createPromiseCapability)();
                return_context2.abrupt("return",this.read());

              case10:
                this._loaded+=chunk.length;

                if(this.onProgress){
                  this.onProgress({
                    loaded:this._loaded
                  });
                }

                buffer=newUint8Array(chunk).buffer;
                return_context2.abrupt("return",{
                  value:buffer,
                  done:false
                });

              case14:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      functionread(){
        return_read2.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      if(!this._readableStream){
        this._error(reason);

        return;
      }

      this._readableStream.destroy(reason);
    }
  },{
    key:"_error",
    value:function_error(reason){
      this._storedError=reason;

      this._readCapability.resolve();
    }
  },{
    key:"_setReadableStream",
    value:function_setReadableStream(readableStream){
      var_this2=this;

      this._readableStream=readableStream;
      readableStream.on('readable',function(){
        _this2._readCapability.resolve();
      });
      readableStream.on('end',function(){
        readableStream.destroy();
        _this2._done=true;

        _this2._readCapability.resolve();
      });
      readableStream.on('error',function(reason){
        _this2._error(reason);
      });

      if(this._storedError){
        this._readableStream.destroy(this._storedError);
      }
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnthis._isStreamingSupported;
    }
  }]);

  returnBaseRangeReader;
}();

functioncreateRequestOptions(url,headers){
  return{
    protocol:url.protocol,
    auth:url.auth,
    host:url.hostname,
    port:url.port,
    path:url.path,
    method:'GET',
    headers:headers
  };
}

varPDFNodeStreamFullReader=
/*#__PURE__*/
function(_BaseFullReader){
  _inherits(PDFNodeStreamFullReader,_BaseFullReader);

  functionPDFNodeStreamFullReader(stream){
    var_this3;

    _classCallCheck(this,PDFNodeStreamFullReader);

    _this3=_possibleConstructorReturn(this,_getPrototypeOf(PDFNodeStreamFullReader).call(this,stream));

    varhandleResponse=functionhandleResponse(response){
      if(response.statusCode===404){
        varerror=new_util.MissingPDFException("MissingPDF\"".concat(_this3._url,"\"."));
        _this3._storedError=error;

        _this3._headersCapability.reject(error);

        return;
      }

      _this3._headersCapability.resolve();

      _this3._setReadableStream(response);

      vargetResponseHeader=functiongetResponseHeader(name){
        return_this3._readableStream.headers[name.toLowerCase()];
      };

      var_validateRangeRequest=(0,_network_utils.validateRangeRequestCapabilities)({
        getResponseHeader:getResponseHeader,
        isHttp:stream.isHttp,
        rangeChunkSize:_this3._rangeChunkSize,
        disableRange:_this3._disableRange
      }),
          allowRangeRequests=_validateRangeRequest.allowRangeRequests,
          suggestedLength=_validateRangeRequest.suggestedLength;

      _this3._isRangeSupported=allowRangeRequests;
      _this3._contentLength=suggestedLength||_this3._contentLength;
      _this3._filename=(0,_network_utils.extractFilenameFromHeader)(getResponseHeader);
    };

    _this3._request=null;

    if(_this3._url.protocol==='http:'){
      _this3._request=http.request(createRequestOptions(_this3._url,stream.httpHeaders),handleResponse);
    }else{
      _this3._request=https.request(createRequestOptions(_this3._url,stream.httpHeaders),handleResponse);
    }

    _this3._request.on('error',function(reason){
      _this3._storedError=reason;

      _this3._headersCapability.reject(reason);
    });

    _this3._request.end();

    return_this3;
  }

  returnPDFNodeStreamFullReader;
}(BaseFullReader);

varPDFNodeStreamRangeReader=
/*#__PURE__*/
function(_BaseRangeReader){
  _inherits(PDFNodeStreamRangeReader,_BaseRangeReader);

  functionPDFNodeStreamRangeReader(stream,start,end){
    var_this4;

    _classCallCheck(this,PDFNodeStreamRangeReader);

    _this4=_possibleConstructorReturn(this,_getPrototypeOf(PDFNodeStreamRangeReader).call(this,stream));
    _this4._httpHeaders={};

    for(varpropertyinstream.httpHeaders){
      varvalue=stream.httpHeaders[property];

      if(typeofvalue==='undefined'){
        continue;
      }

      _this4._httpHeaders[property]=value;
    }

    _this4._httpHeaders['Range']="bytes=".concat(start,"-").concat(end-1);

    varhandleResponse=functionhandleResponse(response){
      if(response.statusCode===404){
        varerror=new_util.MissingPDFException("MissingPDF\"".concat(_this4._url,"\"."));
        _this4._storedError=error;
        return;
      }

      _this4._setReadableStream(response);
    };

    _this4._request=null;

    if(_this4._url.protocol==='http:'){
      _this4._request=http.request(createRequestOptions(_this4._url,_this4._httpHeaders),handleResponse);
    }else{
      _this4._request=https.request(createRequestOptions(_this4._url,_this4._httpHeaders),handleResponse);
    }

    _this4._request.on('error',function(reason){
      _this4._storedError=reason;
    });

    _this4._request.end();

    return_this4;
  }

  returnPDFNodeStreamRangeReader;
}(BaseRangeReader);

varPDFNodeStreamFsFullReader=
/*#__PURE__*/
function(_BaseFullReader2){
  _inherits(PDFNodeStreamFsFullReader,_BaseFullReader2);

  functionPDFNodeStreamFsFullReader(stream){
    var_this5;

    _classCallCheck(this,PDFNodeStreamFsFullReader);

    _this5=_possibleConstructorReturn(this,_getPrototypeOf(PDFNodeStreamFsFullReader).call(this,stream));
    varpath=decodeURIComponent(_this5._url.path);

    if(fileUriRegex.test(_this5._url.href)){
      path=path.replace(/^\//,'');
    }

    fs.lstat(path,function(error,stat){
      if(error){
        if(error.code==='ENOENT'){
          error=new_util.MissingPDFException("MissingPDF\"".concat(path,"\"."));
        }

        _this5._storedError=error;

        _this5._headersCapability.reject(error);

        return;
      }

      _this5._contentLength=stat.size;

      _this5._setReadableStream(fs.createReadStream(path));

      _this5._headersCapability.resolve();
    });
    return_this5;
  }

  returnPDFNodeStreamFsFullReader;
}(BaseFullReader);

varPDFNodeStreamFsRangeReader=
/*#__PURE__*/
function(_BaseRangeReader2){
  _inherits(PDFNodeStreamFsRangeReader,_BaseRangeReader2);

  functionPDFNodeStreamFsRangeReader(stream,start,end){
    var_this6;

    _classCallCheck(this,PDFNodeStreamFsRangeReader);

    _this6=_possibleConstructorReturn(this,_getPrototypeOf(PDFNodeStreamFsRangeReader).call(this,stream));
    varpath=decodeURIComponent(_this6._url.path);

    if(fileUriRegex.test(_this6._url.href)){
      path=path.replace(/^\//,'');
    }

    _this6._setReadableStream(fs.createReadStream(path,{
      start:start,
      end:end-1
    }));

    return_this6;
  }

  returnPDFNodeStreamFsRangeReader;
}(BaseRangeReader);

/***/}),
/*166*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.createResponseStatusError=createResponseStatusError;
exports.extractFilenameFromHeader=extractFilenameFromHeader;
exports.validateRangeRequestCapabilities=validateRangeRequestCapabilities;
exports.validateResponseStatus=validateResponseStatus;

var_util=__w_pdfjs_require__(1);

var_content_disposition=__w_pdfjs_require__(167);

functionvalidateRangeRequestCapabilities(_ref){
  vargetResponseHeader=_ref.getResponseHeader,
      isHttp=_ref.isHttp,
      rangeChunkSize=_ref.rangeChunkSize,
      disableRange=_ref.disableRange;
  (0,_util.assert)(rangeChunkSize>0,'Rangechunksizemustbelargerthanzero');
  varreturnValues={
    allowRangeRequests:false,
    suggestedLength:undefined
  };
  varlength=parseInt(getResponseHeader('Content-Length'),10);

  if(!Number.isInteger(length)){
    returnreturnValues;
  }

  returnValues.suggestedLength=length;

  if(length<=2*rangeChunkSize){
    returnreturnValues;
  }

  if(disableRange||!isHttp){
    returnreturnValues;
  }

  if(getResponseHeader('Accept-Ranges')!=='bytes'){
    returnreturnValues;
  }

  varcontentEncoding=getResponseHeader('Content-Encoding')||'identity';

  if(contentEncoding!=='identity'){
    returnreturnValues;
  }

  returnValues.allowRangeRequests=true;
  returnreturnValues;
}

functionextractFilenameFromHeader(getResponseHeader){
  varcontentDisposition=getResponseHeader('Content-Disposition');

  if(contentDisposition){
    varfilename=(0,_content_disposition.getFilenameFromContentDispositionHeader)(contentDisposition);

    if(/\.pdf$/i.test(filename)){
      returnfilename;
    }
  }

  returnnull;
}

functioncreateResponseStatusError(status,url){
  if(status===404||status===0&&/^file:/.test(url)){
    returnnew_util.MissingPDFException('MissingPDF"'+url+'".');
  }

  returnnew_util.UnexpectedResponseException('Unexpectedserverresponse('+status+')whileretrievingPDF"'+url+'".',status);
}

functionvalidateResponseStatus(status){
  returnstatus===200||status===206;
}

/***/}),
/*167*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.getFilenameFromContentDispositionHeader=getFilenameFromContentDispositionHeader;

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

functiongetFilenameFromContentDispositionHeader(contentDisposition){
  varneedsEncodingFixup=true;
  vartmp=toParamRegExp('filename\\*','i').exec(contentDisposition);

  if(tmp){
    tmp=tmp[1];
    varfilename=rfc2616unquote(tmp);
    filename=unescape(filename);
    filename=rfc5987decode(filename);
    filename=rfc2047decode(filename);
    returnfixupEncoding(filename);
  }

  tmp=rfc2231getparam(contentDisposition);

  if(tmp){
    var_filename=rfc2047decode(tmp);

    returnfixupEncoding(_filename);
  }

  tmp=toParamRegExp('filename','i').exec(contentDisposition);

  if(tmp){
    tmp=tmp[1];

    var_filename2=rfc2616unquote(tmp);

    _filename2=rfc2047decode(_filename2);
    returnfixupEncoding(_filename2);
  }

  functiontoParamRegExp(attributePattern,flags){
    returnnewRegExp('(?:^|;)\\s*'+attributePattern+'\\s*=\\s*'+'('+'[^";\\s][^;\\s]*'+'|'+'"(?:[^"\\\\]|\\\\"?)+"?'+')',flags);
  }

  functiontextdecode(encoding,value){
    if(encoding){
      if(!/^[\x00-\xFF]+$/.test(value)){
        returnvalue;
      }

      try{
        vardecoder=newTextDecoder(encoding,{
          fatal:true
        });
        varbytes=Array.from(value,function(ch){
          returnch.charCodeAt(0)&0xFF;
        });
        value=decoder.decode(newUint8Array(bytes));
        needsEncodingFixup=false;
      }catch(e){
        if(/^utf-?8$/i.test(encoding)){
          try{
            value=decodeURIComponent(escape(value));
            needsEncodingFixup=false;
          }catch(err){}
        }
      }
    }

    returnvalue;
  }

  functionfixupEncoding(value){
    if(needsEncodingFixup&&/[\x80-\xff]/.test(value)){
      value=textdecode('utf-8',value);

      if(needsEncodingFixup){
        value=textdecode('iso-8859-1',value);
      }
    }

    returnvalue;
  }

  functionrfc2231getparam(contentDisposition){
    varmatches=[],
        match;
    variter=toParamRegExp('filename\\*((?!0\\d)\\d+)(\\*?)','ig');

    while((match=iter.exec(contentDisposition))!==null){
      var_match=match,
          _match2=_slicedToArray(_match,4),
          n=_match2[1],
          quot=_match2[2],
          part=_match2[3];

      n=parseInt(n,10);

      if(ninmatches){
        if(n===0){
          break;
        }

        continue;
      }

      matches[n]=[quot,part];
    }

    varparts=[];

    for(varn=0;n<matches.length;++n){
      if(!(ninmatches)){
        break;
      }

      var_matches$n=_slicedToArray(matches[n],2),
          quot=_matches$n[0],
          part=_matches$n[1];

      part=rfc2616unquote(part);

      if(quot){
        part=unescape(part);

        if(n===0){
          part=rfc5987decode(part);
        }
      }

      parts.push(part);
    }

    returnparts.join('');
  }

  functionrfc2616unquote(value){
    if(value.startsWith('"')){
      varparts=value.slice(1).split('\\"');

      for(vari=0;i<parts.length;++i){
        varquotindex=parts[i].indexOf('"');

        if(quotindex!==-1){
          parts[i]=parts[i].slice(0,quotindex);
          parts.length=i+1;
        }

        parts[i]=parts[i].replace(/\\(.)/g,'$1');
      }

      value=parts.join('"');
    }

    returnvalue;
  }

  functionrfc5987decode(extvalue){
    varencodingend=extvalue.indexOf('\'');

    if(encodingend===-1){
      returnextvalue;
    }

    varencoding=extvalue.slice(0,encodingend);
    varlangvalue=extvalue.slice(encodingend+1);
    varvalue=langvalue.replace(/^[^']*'/,'');
    returntextdecode(encoding,value);
  }

  functionrfc2047decode(value){
    if(!value.startsWith('=?')||/[\x00-\x19\x80-\xff]/.test(value)){
      returnvalue;
    }

    returnvalue.replace(/=\?([\w-]*)\?([QqBb])\?((?:[^?]|\?(?!=))*)\?=/g,function(_,charset,encoding,text){
      if(encoding==='q'||encoding==='Q'){
        text=text.replace(/_/g,'');
        text=text.replace(/=([0-9a-fA-F]{2})/g,function(_,hex){
          returnString.fromCharCode(parseInt(hex,16));
        });
        returntextdecode(charset,text);
      }

      try{
        text=atob(text);
      }catch(e){}

      returntextdecode(charset,text);
    });
  }

  return'';
}

/***/}),
/*168*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFNetworkStream=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

var_network_utils=__w_pdfjs_require__(166);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{default:obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

;
varOK_RESPONSE=200;
varPARTIAL_CONTENT_RESPONSE=206;

functiongetArrayBuffer(xhr){
  vardata=xhr.response;

  if(typeofdata!=='string'){
    returndata;
  }

  vararray=(0,_util.stringToBytes)(data);
  returnarray.buffer;
}

varNetworkManager=
/*#__PURE__*/
function(){
  functionNetworkManager(url,args){
    _classCallCheck(this,NetworkManager);

    this.url=url;
    args=args||{};
    this.isHttp=/^https?:/i.test(url);
    this.httpHeaders=this.isHttp&&args.httpHeaders||{};
    this.withCredentials=args.withCredentials||false;

    this.getXhr=args.getXhr||functionNetworkManager_getXhr(){
      returnnewXMLHttpRequest();
    };

    this.currXhrId=0;
    this.pendingRequests=Object.create(null);
  }

  _createClass(NetworkManager,[{
    key:"requestRange",
    value:functionrequestRange(begin,end,listeners){
      varargs={
        begin:begin,
        end:end
      };

      for(varpropinlisteners){
        args[prop]=listeners[prop];
      }

      returnthis.request(args);
    }
  },{
    key:"requestFull",
    value:functionrequestFull(listeners){
      returnthis.request(listeners);
    }
  },{
    key:"request",
    value:functionrequest(args){
      varxhr=this.getXhr();
      varxhrId=this.currXhrId++;
      varpendingRequest=this.pendingRequests[xhrId]={
        xhr:xhr
      };
      xhr.open('GET',this.url);
      xhr.withCredentials=this.withCredentials;

      for(varpropertyinthis.httpHeaders){
        varvalue=this.httpHeaders[property];

        if(typeofvalue==='undefined'){
          continue;
        }

        xhr.setRequestHeader(property,value);
      }

      if(this.isHttp&&'begin'inargs&&'end'inargs){
        xhr.setRequestHeader('Range',"bytes=".concat(args.begin,"-").concat(args.end-1));
        pendingRequest.expectedStatus=PARTIAL_CONTENT_RESPONSE;
      }else{
        pendingRequest.expectedStatus=OK_RESPONSE;
      }

      xhr.responseType='arraybuffer';

      if(args.onError){
        xhr.onerror=function(evt){
          args.onError(xhr.status);
        };
      }

      xhr.onreadystatechange=this.onStateChange.bind(this,xhrId);
      xhr.onprogress=this.onProgress.bind(this,xhrId);
      pendingRequest.onHeadersReceived=args.onHeadersReceived;
      pendingRequest.onDone=args.onDone;
      pendingRequest.onError=args.onError;
      pendingRequest.onProgress=args.onProgress;
      xhr.send(null);
      returnxhrId;
    }
  },{
    key:"onProgress",
    value:functiononProgress(xhrId,evt){
      varpendingRequest=this.pendingRequests[xhrId];

      if(!pendingRequest){
        return;
      }

      if(pendingRequest.onProgress){
        pendingRequest.onProgress(evt);
      }
    }
  },{
    key:"onStateChange",
    value:functiononStateChange(xhrId,evt){
      varpendingRequest=this.pendingRequests[xhrId];

      if(!pendingRequest){
        return;
      }

      varxhr=pendingRequest.xhr;

      if(xhr.readyState>=2&&pendingRequest.onHeadersReceived){
        pendingRequest.onHeadersReceived();
        deletependingRequest.onHeadersReceived;
      }

      if(xhr.readyState!==4){
        return;
      }

      if(!(xhrIdinthis.pendingRequests)){
        return;
      }

      deletethis.pendingRequests[xhrId];

      if(xhr.status===0&&this.isHttp){
        if(pendingRequest.onError){
          pendingRequest.onError(xhr.status);
        }

        return;
      }

      varxhrStatus=xhr.status||OK_RESPONSE;
      varok_response_on_range_request=xhrStatus===OK_RESPONSE&&pendingRequest.expectedStatus===PARTIAL_CONTENT_RESPONSE;

      if(!ok_response_on_range_request&&xhrStatus!==pendingRequest.expectedStatus){
        if(pendingRequest.onError){
          pendingRequest.onError(xhr.status);
        }

        return;
      }

      varchunk=getArrayBuffer(xhr);

      if(xhrStatus===PARTIAL_CONTENT_RESPONSE){
        varrangeHeader=xhr.getResponseHeader('Content-Range');
        varmatches=/bytes(\d+)-(\d+)\/(\d+)/.exec(rangeHeader);
        pendingRequest.onDone({
          begin:parseInt(matches[1],10),
          chunk:chunk
        });
      }elseif(chunk){
        pendingRequest.onDone({
          begin:0,
          chunk:chunk
        });
      }elseif(pendingRequest.onError){
        pendingRequest.onError(xhr.status);
      }
    }
  },{
    key:"hasPendingRequests",
    value:functionhasPendingRequests(){
      for(varxhrIdinthis.pendingRequests){
        returntrue;
      }

      returnfalse;
    }
  },{
    key:"getRequestXhr",
    value:functiongetRequestXhr(xhrId){
      returnthis.pendingRequests[xhrId].xhr;
    }
  },{
    key:"isPendingRequest",
    value:functionisPendingRequest(xhrId){
      returnxhrIdinthis.pendingRequests;
    }
  },{
    key:"abortAllRequests",
    value:functionabortAllRequests(){
      for(varxhrIdinthis.pendingRequests){
        this.abortRequest(xhrId|0);
      }
    }
  },{
    key:"abortRequest",
    value:functionabortRequest(xhrId){
      varxhr=this.pendingRequests[xhrId].xhr;
      deletethis.pendingRequests[xhrId];
      xhr.abort();
    }
  }]);

  returnNetworkManager;
}();

varPDFNetworkStream=
/*#__PURE__*/
function(){
  functionPDFNetworkStream(source){
    _classCallCheck(this,PDFNetworkStream);

    this._source=source;
    this._manager=newNetworkManager(source.url,{
      httpHeaders:source.httpHeaders,
      withCredentials:source.withCredentials
    });
    this._rangeChunkSize=source.rangeChunkSize;
    this._fullRequestReader=null;
    this._rangeRequestReaders=[];
  }

  _createClass(PDFNetworkStream,[{
    key:"_onRangeRequestReaderClosed",
    value:function_onRangeRequestReaderClosed(reader){
      vari=this._rangeRequestReaders.indexOf(reader);

      if(i>=0){
        this._rangeRequestReaders.splice(i,1);
      }
    }
  },{
    key:"getFullReader",
    value:functiongetFullReader(){
      (0,_util.assert)(!this._fullRequestReader);
      this._fullRequestReader=newPDFNetworkStreamFullRequestReader(this._manager,this._source);
      returnthis._fullRequestReader;
    }
  },{
    key:"getRangeReader",
    value:functiongetRangeReader(begin,end){
      varreader=newPDFNetworkStreamRangeRequestReader(this._manager,begin,end);
      reader.onClosed=this._onRangeRequestReaderClosed.bind(this);

      this._rangeRequestReaders.push(reader);

      returnreader;
    }
  },{
    key:"cancelAllRequests",
    value:functioncancelAllRequests(reason){
      if(this._fullRequestReader){
        this._fullRequestReader.cancel(reason);
      }

      varreaders=this._rangeRequestReaders.slice(0);

      readers.forEach(function(reader){
        reader.cancel(reason);
      });
    }
  }]);

  returnPDFNetworkStream;
}();

exports.PDFNetworkStream=PDFNetworkStream;

varPDFNetworkStreamFullRequestReader=
/*#__PURE__*/
function(){
  functionPDFNetworkStreamFullRequestReader(manager,source){
    _classCallCheck(this,PDFNetworkStreamFullRequestReader);

    this._manager=manager;
    varargs={
      onHeadersReceived:this._onHeadersReceived.bind(this),
      onDone:this._onDone.bind(this),
      onError:this._onError.bind(this),
      onProgress:this._onProgress.bind(this)
    };
    this._url=source.url;
    this._fullRequestId=manager.requestFull(args);
    this._headersReceivedCapability=(0,_util.createPromiseCapability)();
    this._disableRange=source.disableRange||false;
    this._contentLength=source.length;
    this._rangeChunkSize=source.rangeChunkSize;

    if(!this._rangeChunkSize&&!this._disableRange){
      this._disableRange=true;
    }

    this._isStreamingSupported=false;
    this._isRangeSupported=false;
    this._cachedChunks=[];
    this._requests=[];
    this._done=false;
    this._storedError=undefined;
    this._filename=null;
    this.onProgress=null;
  }

  _createClass(PDFNetworkStreamFullRequestReader,[{
    key:"_onHeadersReceived",
    value:function_onHeadersReceived(){
      varfullRequestXhrId=this._fullRequestId;

      varfullRequestXhr=this._manager.getRequestXhr(fullRequestXhrId);

      vargetResponseHeader=functiongetResponseHeader(name){
        returnfullRequestXhr.getResponseHeader(name);
      };

      var_validateRangeRequest=(0,_network_utils.validateRangeRequestCapabilities)({
        getResponseHeader:getResponseHeader,
        isHttp:this._manager.isHttp,
        rangeChunkSize:this._rangeChunkSize,
        disableRange:this._disableRange
      }),
          allowRangeRequests=_validateRangeRequest.allowRangeRequests,
          suggestedLength=_validateRangeRequest.suggestedLength;

      if(allowRangeRequests){
        this._isRangeSupported=true;
      }

      this._contentLength=suggestedLength||this._contentLength;
      this._filename=(0,_network_utils.extractFilenameFromHeader)(getResponseHeader);

      if(this._isRangeSupported){
        this._manager.abortRequest(fullRequestXhrId);
      }

      this._headersReceivedCapability.resolve();
    }
  },{
    key:"_onDone",
    value:function_onDone(args){
      if(args){
        if(this._requests.length>0){
          varrequestCapability=this._requests.shift();

          requestCapability.resolve({
            value:args.chunk,
            done:false
          });
        }else{
          this._cachedChunks.push(args.chunk);
        }
      }

      this._done=true;

      if(this._cachedChunks.length>0){
        return;
      }

      this._requests.forEach(function(requestCapability){
        requestCapability.resolve({
          value:undefined,
          done:true
        });
      });

      this._requests=[];
    }
  },{
    key:"_onError",
    value:function_onError(status){
      varurl=this._url;
      varexception=(0,_network_utils.createResponseStatusError)(status,url);
      this._storedError=exception;

      this._headersReceivedCapability.reject(exception);

      this._requests.forEach(function(requestCapability){
        requestCapability.reject(exception);
      });

      this._requests=[];
      this._cachedChunks=[];
    }
  },{
    key:"_onProgress",
    value:function_onProgress(data){
      if(this.onProgress){
        this.onProgress({
          loaded:data.loaded,
          total:data.lengthComputable?data.total:this._contentLength
        });
      }
    }
  },{
    key:"read",
    value:function(){
      var_read=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        varchunk,requestCapability;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                if(!this._storedError){
                  _context.next=2;
                  break;
                }

                throwthis._storedError;

              case2:
                if(!(this._cachedChunks.length>0)){
                  _context.next=5;
                  break;
                }

                chunk=this._cachedChunks.shift();
                return_context.abrupt("return",{
                  value:chunk,
                  done:false
                });

              case5:
                if(!this._done){
                  _context.next=7;
                  break;
                }

                return_context.abrupt("return",{
                  value:undefined,
                  done:true
                });

              case7:
                requestCapability=(0,_util.createPromiseCapability)();

                this._requests.push(requestCapability);

                return_context.abrupt("return",requestCapability.promise);

              case10:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      functionread(){
        return_read.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      this._done=true;

      this._headersReceivedCapability.reject(reason);

      this._requests.forEach(function(requestCapability){
        requestCapability.resolve({
          value:undefined,
          done:true
        });
      });

      this._requests=[];

      if(this._manager.isPendingRequest(this._fullRequestId)){
        this._manager.abortRequest(this._fullRequestId);
      }

      this._fullRequestReader=null;
    }
  },{
    key:"filename",
    get:functionget(){
      returnthis._filename;
    }
  },{
    key:"isRangeSupported",
    get:functionget(){
      returnthis._isRangeSupported;
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnthis._isStreamingSupported;
    }
  },{
    key:"contentLength",
    get:functionget(){
      returnthis._contentLength;
    }
  },{
    key:"headersReady",
    get:functionget(){
      returnthis._headersReceivedCapability.promise;
    }
  }]);

  returnPDFNetworkStreamFullRequestReader;
}();

varPDFNetworkStreamRangeRequestReader=
/*#__PURE__*/
function(){
  functionPDFNetworkStreamRangeRequestReader(manager,begin,end){
    _classCallCheck(this,PDFNetworkStreamRangeRequestReader);

    this._manager=manager;
    varargs={
      onDone:this._onDone.bind(this),
      onProgress:this._onProgress.bind(this)
    };
    this._requestId=manager.requestRange(begin,end,args);
    this._requests=[];
    this._queuedChunk=null;
    this._done=false;
    this.onProgress=null;
    this.onClosed=null;
  }

  _createClass(PDFNetworkStreamRangeRequestReader,[{
    key:"_close",
    value:function_close(){
      if(this.onClosed){
        this.onClosed(this);
      }
    }
  },{
    key:"_onDone",
    value:function_onDone(data){
      varchunk=data.chunk;

      if(this._requests.length>0){
        varrequestCapability=this._requests.shift();

        requestCapability.resolve({
          value:chunk,
          done:false
        });
      }else{
        this._queuedChunk=chunk;
      }

      this._done=true;

      this._requests.forEach(function(requestCapability){
        requestCapability.resolve({
          value:undefined,
          done:true
        });
      });

      this._requests=[];

      this._close();
    }
  },{
    key:"_onProgress",
    value:function_onProgress(evt){
      if(!this.isStreamingSupported&&this.onProgress){
        this.onProgress({
          loaded:evt.loaded
        });
      }
    }
  },{
    key:"read",
    value:function(){
      var_read2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(){
        varchunk,requestCapability;
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                if(!(this._queuedChunk!==null)){
                  _context2.next=4;
                  break;
                }

                chunk=this._queuedChunk;
                this._queuedChunk=null;
                return_context2.abrupt("return",{
                  value:chunk,
                  done:false
                });

              case4:
                if(!this._done){
                  _context2.next=6;
                  break;
                }

                return_context2.abrupt("return",{
                  value:undefined,
                  done:true
                });

              case6:
                requestCapability=(0,_util.createPromiseCapability)();

                this._requests.push(requestCapability);

                return_context2.abrupt("return",requestCapability.promise);

              case9:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      functionread(){
        return_read2.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      this._done=true;

      this._requests.forEach(function(requestCapability){
        requestCapability.resolve({
          value:undefined,
          done:true
        });
      });

      this._requests=[];

      if(this._manager.isPendingRequest(this._requestId)){
        this._manager.abortRequest(this._requestId);
      }

      this._close();
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnfalse;
    }
  }]);

  returnPDFNetworkStreamRangeRequestReader;
}();

/***/}),
/*169*/
/***/(function(module,exports,__w_pdfjs_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFFetchStream=void0;

var_regenerator=_interopRequireDefault(__w_pdfjs_require__(148));

var_util=__w_pdfjs_require__(1);

var_network_utils=__w_pdfjs_require__(166);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{default:obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

functioncreateFetchOptions(headers,withCredentials,abortController){
  return{
    method:'GET',
    headers:headers,
    signal:abortController&&abortController.signal,
    mode:'cors',
    credentials:withCredentials?'include':'same-origin',
    redirect:'follow'
  };
}

varPDFFetchStream=
/*#__PURE__*/
function(){
  functionPDFFetchStream(source){
    _classCallCheck(this,PDFFetchStream);

    this.source=source;
    this.isHttp=/^https?:/i.test(source.url);
    this.httpHeaders=this.isHttp&&source.httpHeaders||{};
    this._fullRequestReader=null;
    this._rangeRequestReaders=[];
  }

  _createClass(PDFFetchStream,[{
    key:"getFullReader",
    value:functiongetFullReader(){
      (0,_util.assert)(!this._fullRequestReader);
      this._fullRequestReader=newPDFFetchStreamReader(this);
      returnthis._fullRequestReader;
    }
  },{
    key:"getRangeReader",
    value:functiongetRangeReader(begin,end){
      if(end<=this._progressiveDataLength){
        returnnull;
      }

      varreader=newPDFFetchStreamRangeReader(this,begin,end);

      this._rangeRequestReaders.push(reader);

      returnreader;
    }
  },{
    key:"cancelAllRequests",
    value:functioncancelAllRequests(reason){
      if(this._fullRequestReader){
        this._fullRequestReader.cancel(reason);
      }

      varreaders=this._rangeRequestReaders.slice(0);

      readers.forEach(function(reader){
        reader.cancel(reason);
      });
    }
  },{
    key:"_progressiveDataLength",
    get:functionget(){
      returnthis._fullRequestReader?this._fullRequestReader._loaded:0;
    }
  }]);

  returnPDFFetchStream;
}();

exports.PDFFetchStream=PDFFetchStream;

varPDFFetchStreamReader=
/*#__PURE__*/
function(){
  functionPDFFetchStreamReader(stream){
    var_this=this;

    _classCallCheck(this,PDFFetchStreamReader);

    this._stream=stream;
    this._reader=null;
    this._loaded=0;
    this._filename=null;
    varsource=stream.source;
    this._withCredentials=source.withCredentials||false;
    this._contentLength=source.length;
    this._headersCapability=(0,_util.createPromiseCapability)();
    this._disableRange=source.disableRange||false;
    this._rangeChunkSize=source.rangeChunkSize;

    if(!this._rangeChunkSize&&!this._disableRange){
      this._disableRange=true;
    }

    if(typeofAbortController!=='undefined'){
      this._abortController=newAbortController();
    }

    this._isStreamingSupported=!source.disableStream;
    this._isRangeSupported=!source.disableRange;
    this._headers=newHeaders();

    for(varpropertyinthis._stream.httpHeaders){
      varvalue=this._stream.httpHeaders[property];

      if(typeofvalue==='undefined'){
        continue;
      }

      this._headers.append(property,value);
    }

    varurl=source.url;
    fetch(url,createFetchOptions(this._headers,this._withCredentials,this._abortController)).then(function(response){
      if(!(0,_network_utils.validateResponseStatus)(response.status)){
        throw(0,_network_utils.createResponseStatusError)(response.status,url);
      }

      _this._reader=response.body.getReader();

      _this._headersCapability.resolve();

      vargetResponseHeader=functiongetResponseHeader(name){
        returnresponse.headers.get(name);
      };

      var_validateRangeRequest=(0,_network_utils.validateRangeRequestCapabilities)({
        getResponseHeader:getResponseHeader,
        isHttp:_this._stream.isHttp,
        rangeChunkSize:_this._rangeChunkSize,
        disableRange:_this._disableRange
      }),
          allowRangeRequests=_validateRangeRequest.allowRangeRequests,
          suggestedLength=_validateRangeRequest.suggestedLength;

      _this._isRangeSupported=allowRangeRequests;
      _this._contentLength=suggestedLength||_this._contentLength;
      _this._filename=(0,_network_utils.extractFilenameFromHeader)(getResponseHeader);

      if(!_this._isStreamingSupported&&_this._isRangeSupported){
        _this.cancel(new_util.AbortException('Streamingisdisabled.'));
      }
    })["catch"](this._headersCapability.reject);
    this.onProgress=null;
  }

  _createClass(PDFFetchStreamReader,[{
    key:"read",
    value:function(){
      var_read=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        var_ref,value,done,buffer;

        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                _context.next=2;
                returnthis._headersCapability.promise;

              case2:
                _context.next=4;
                returnthis._reader.read();

              case4:
                _ref=_context.sent;
                value=_ref.value;
                done=_ref.done;

                if(!done){
                  _context.next=9;
                  break;
                }

                return_context.abrupt("return",{
                  value:value,
                  done:done
                });

              case9:
                this._loaded+=value.byteLength;

                if(this.onProgress){
                  this.onProgress({
                    loaded:this._loaded,
                    total:this._contentLength
                  });
                }

                buffer=newUint8Array(value).buffer;
                return_context.abrupt("return",{
                  value:buffer,
                  done:false
                });

              case13:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      functionread(){
        return_read.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      if(this._reader){
        this._reader.cancel(reason);
      }

      if(this._abortController){
        this._abortController.abort();
      }
    }
  },{
    key:"headersReady",
    get:functionget(){
      returnthis._headersCapability.promise;
    }
  },{
    key:"filename",
    get:functionget(){
      returnthis._filename;
    }
  },{
    key:"contentLength",
    get:functionget(){
      returnthis._contentLength;
    }
  },{
    key:"isRangeSupported",
    get:functionget(){
      returnthis._isRangeSupported;
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnthis._isStreamingSupported;
    }
  }]);

  returnPDFFetchStreamReader;
}();

varPDFFetchStreamRangeReader=
/*#__PURE__*/
function(){
  functionPDFFetchStreamRangeReader(stream,begin,end){
    var_this2=this;

    _classCallCheck(this,PDFFetchStreamRangeReader);

    this._stream=stream;
    this._reader=null;
    this._loaded=0;
    varsource=stream.source;
    this._withCredentials=source.withCredentials||false;
    this._readCapability=(0,_util.createPromiseCapability)();
    this._isStreamingSupported=!source.disableStream;

    if(typeofAbortController!=='undefined'){
      this._abortController=newAbortController();
    }

    this._headers=newHeaders();

    for(varpropertyinthis._stream.httpHeaders){
      varvalue=this._stream.httpHeaders[property];

      if(typeofvalue==='undefined'){
        continue;
      }

      this._headers.append(property,value);
    }

    this._headers.append('Range',"bytes=".concat(begin,"-").concat(end-1));

    varurl=source.url;
    fetch(url,createFetchOptions(this._headers,this._withCredentials,this._abortController)).then(function(response){
      if(!(0,_network_utils.validateResponseStatus)(response.status)){
        throw(0,_network_utils.createResponseStatusError)(response.status,url);
      }

      _this2._readCapability.resolve();

      _this2._reader=response.body.getReader();
    });
    this.onProgress=null;
  }

  _createClass(PDFFetchStreamRangeReader,[{
    key:"read",
    value:function(){
      var_read2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(){
        var_ref2,value,done,buffer;

        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                _context2.next=2;
                returnthis._readCapability.promise;

              case2:
                _context2.next=4;
                returnthis._reader.read();

              case4:
                _ref2=_context2.sent;
                value=_ref2.value;
                done=_ref2.done;

                if(!done){
                  _context2.next=9;
                  break;
                }

                return_context2.abrupt("return",{
                  value:value,
                  done:done
                });

              case9:
                this._loaded+=value.byteLength;

                if(this.onProgress){
                  this.onProgress({
                    loaded:this._loaded
                  });
                }

                buffer=newUint8Array(value).buffer;
                return_context2.abrupt("return",{
                  value:buffer,
                  done:false
                });

              case13:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      functionread(){
        return_read2.apply(this,arguments);
      }

      returnread;
    }()
  },{
    key:"cancel",
    value:functioncancel(reason){
      if(this._reader){
        this._reader.cancel(reason);
      }

      if(this._abortController){
        this._abortController.abort();
      }
    }
  },{
    key:"isStreamingSupported",
    get:functionget(){
      returnthis._isStreamingSupported;
    }
  }]);

  returnPDFFetchStreamRangeReader;
}();

/***/})
/******/]);
});
//#sourceMappingURL=pdf.js.map