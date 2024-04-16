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

/******/(function(modules){//webpackBootstrap
/******/	//Themodulecache
/******/	varinstalledModules={};
/******/
/******/	//Therequirefunction
/******/	function__webpack_require__(moduleId){
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
/******/		modules[moduleId].call(module.exports,module,module.exports,__webpack_require__);
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
/******/	__webpack_require__.m=modules;
/******/
/******/	//exposethemodulecache
/******/	__webpack_require__.c=installedModules;
/******/
/******/	//definegetterfunctionforharmonyexports
/******/	__webpack_require__.d=function(exports,name,getter){
/******/		if(!__webpack_require__.o(exports,name)){
/******/			Object.defineProperty(exports,name,{enumerable:true,get:getter});
/******/		}
/******/	};
/******/
/******/	//define__esModuleonexports
/******/	__webpack_require__.r=function(exports){
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
/******/	__webpack_require__.t=function(value,mode){
/******/		if(mode&1)value=__webpack_require__(value);
/******/		if(mode&8)returnvalue;
/******/		if((mode&4)&&typeofvalue==='object'&&value&&value.__esModule)returnvalue;
/******/		varns=Object.create(null);
/******/		__webpack_require__.r(ns);
/******/		Object.defineProperty(ns,'default',{enumerable:true,value:value});
/******/		if(mode&2&&typeofvalue!='string')for(varkeyinvalue)__webpack_require__.d(ns,key,function(key){returnvalue[key];}.bind(null,key));
/******/		returnns;
/******/	};
/******/
/******/	//getDefaultExportfunctionforcompatibilitywithnon-harmonymodules
/******/	__webpack_require__.n=function(module){
/******/		vargetter=module&&module.__esModule?
/******/			functiongetDefault(){returnmodule['default'];}:
/******/			functiongetModuleExports(){returnmodule;};
/******/		__webpack_require__.d(getter,'a',getter);
/******/		returngetter;
/******/	};
/******/
/******/	//Object.prototype.hasOwnProperty.call
/******/	__webpack_require__.o=function(object,property){returnObject.prototype.hasOwnProperty.call(object,property);};
/******/
/******/	//__webpack_public_path__
/******/	__webpack_require__.p="";
/******/
/******/
/******/	//Loadentrymoduleandreturnexports
/******/	return__webpack_require__(__webpack_require__.s=0);
/******/})
/************************************************************************/
/******/([
/*0*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


;
varpdfjsWebApp,pdfjsWebAppOptions;
{
  pdfjsWebApp=__webpack_require__(1);
  pdfjsWebAppOptions=__webpack_require__(6);
}
;
{
  __webpack_require__(36);
}
;
{
  __webpack_require__(41);
}

functiongetViewerConfiguration(){
  return{
    appContainer:document.body,
    mainContainer:document.getElementById('viewerContainer'),
    viewerContainer:document.getElementById('viewer'),
    eventBus:null,
    toolbar:{
      container:document.getElementById('toolbarViewer'),
      numPages:document.getElementById('numPages'),
      pageNumber:document.getElementById('pageNumber'),
      scaleSelectContainer:document.getElementById('scaleSelectContainer'),
      scaleSelect:document.getElementById('scaleSelect'),
      customScaleOption:document.getElementById('customScaleOption'),
      previous:document.getElementById('previous'),
      next:document.getElementById('next'),
      zoomIn:document.getElementById('zoomIn'),
      zoomOut:document.getElementById('zoomOut'),
      viewFind:document.getElementById('viewFind'),
      openFile:document.getElementById('openFile'),
      print:document.getElementById('print'),
      presentationModeButton:document.getElementById('presentationMode'),
      download:document.getElementById('download'),
      viewBookmark:document.getElementById('viewBookmark')
    },
    secondaryToolbar:{
      toolbar:document.getElementById('secondaryToolbar'),
      toggleButton:document.getElementById('secondaryToolbarToggle'),
      toolbarButtonContainer:document.getElementById('secondaryToolbarButtonContainer'),
      presentationModeButton:document.getElementById('secondaryPresentationMode'),
      openFileButton:document.getElementById('secondaryOpenFile'),
      printButton:document.getElementById('secondaryPrint'),
      downloadButton:document.getElementById('secondaryDownload'),
      viewBookmarkButton:document.getElementById('secondaryViewBookmark'),
      firstPageButton:document.getElementById('firstPage'),
      lastPageButton:document.getElementById('lastPage'),
      pageRotateCwButton:document.getElementById('pageRotateCw'),
      pageRotateCcwButton:document.getElementById('pageRotateCcw'),
      cursorSelectToolButton:document.getElementById('cursorSelectTool'),
      cursorHandToolButton:document.getElementById('cursorHandTool'),
      scrollVerticalButton:document.getElementById('scrollVertical'),
      scrollHorizontalButton:document.getElementById('scrollHorizontal'),
      scrollWrappedButton:document.getElementById('scrollWrapped'),
      spreadNoneButton:document.getElementById('spreadNone'),
      spreadOddButton:document.getElementById('spreadOdd'),
      spreadEvenButton:document.getElementById('spreadEven'),
      documentPropertiesButton:document.getElementById('documentProperties')
    },
    fullscreen:{
      contextFirstPage:document.getElementById('contextFirstPage'),
      contextLastPage:document.getElementById('contextLastPage'),
      contextPageRotateCw:document.getElementById('contextPageRotateCw'),
      contextPageRotateCcw:document.getElementById('contextPageRotateCcw')
    },
    sidebar:{
      outerContainer:document.getElementById('outerContainer'),
      viewerContainer:document.getElementById('viewerContainer'),
      toggleButton:document.getElementById('sidebarToggle'),
      thumbnailButton:document.getElementById('viewThumbnail'),
      outlineButton:document.getElementById('viewOutline'),
      attachmentsButton:document.getElementById('viewAttachments'),
      thumbnailView:document.getElementById('thumbnailView'),
      outlineView:document.getElementById('outlineView'),
      attachmentsView:document.getElementById('attachmentsView')
    },
    sidebarResizer:{
      outerContainer:document.getElementById('outerContainer'),
      resizer:document.getElementById('sidebarResizer')
    },
    findBar:{
      bar:document.getElementById('findbar'),
      toggleButton:document.getElementById('viewFind'),
      findField:document.getElementById('findInput'),
      highlightAllCheckbox:document.getElementById('findHighlightAll'),
      caseSensitiveCheckbox:document.getElementById('findMatchCase'),
      entireWordCheckbox:document.getElementById('findEntireWord'),
      findMsg:document.getElementById('findMsg'),
      findResultsCount:document.getElementById('findResultsCount'),
      findPreviousButton:document.getElementById('findPrevious'),
      findNextButton:document.getElementById('findNext')
    },
    passwordOverlay:{
      overlayName:'passwordOverlay',
      container:document.getElementById('passwordOverlay'),
      label:document.getElementById('passwordText'),
      input:document.getElementById('password'),
      submitButton:document.getElementById('passwordSubmit'),
      cancelButton:document.getElementById('passwordCancel')
    },
    documentProperties:{
      overlayName:'documentPropertiesOverlay',
      container:document.getElementById('documentPropertiesOverlay'),
      closeButton:document.getElementById('documentPropertiesClose'),
      fields:{
        'fileName':document.getElementById('fileNameField'),
        'fileSize':document.getElementById('fileSizeField'),
        'title':document.getElementById('titleField'),
        'author':document.getElementById('authorField'),
        'subject':document.getElementById('subjectField'),
        'keywords':document.getElementById('keywordsField'),
        'creationDate':document.getElementById('creationDateField'),
        'modificationDate':document.getElementById('modificationDateField'),
        'creator':document.getElementById('creatorField'),
        'producer':document.getElementById('producerField'),
        'version':document.getElementById('versionField'),
        'pageCount':document.getElementById('pageCountField'),
        'pageSize':document.getElementById('pageSizeField'),
        'linearized':document.getElementById('linearizedField')
      }
    },
    errorWrapper:{
      container:document.getElementById('errorWrapper'),
      errorMessage:document.getElementById('errorMessage'),
      closeButton:document.getElementById('errorClose'),
      errorMoreInfo:document.getElementById('errorMoreInfo'),
      moreInfoButton:document.getElementById('errorShowMore'),
      lessInfoButton:document.getElementById('errorShowLess')
    },
    printContainer:document.getElementById('printContainer'),
    openFileInputName:'fileInput',
    debuggerScriptPath:'./debugger.js'
  };
}

functionwebViewerLoad(){
  varconfig=getViewerConfiguration();
  //StartFlectrapatch
  //Sourcehttps://github.com/mozilla/pdf.js/pull/11246(DetectAndroidandiOS)
  constuserAgent=(typeofnavigator!=='undefined'&&navigator.userAgent)||'';
  constplatform=(typeofnavigator!=='undefined'&&navigator.platform)||'';
  constmaxTouchPoints=(typeofnavigator!=='undefined'&&navigator.maxTouchPoints)||1;
  constisAndroid=/Android/.test(userAgent);
  constisIOS=/\b(iPad|iPhone|iPod)(?=;)/.test(userAgent)||(platform==='MacIntel'&&maxTouchPoints>1);
  //HideOpenButton
  config.toolbar.openFile.setAttribute('hidden','true');
  config.secondaryToolbar.openFileButton.setAttribute('hidden','true');
  if(isAndroid||isIOS){
    //HideDownloadButton
    config.toolbar.download.setAttribute('hidden','true');
    config.secondaryToolbar.downloadButton.setAttribute('hidden','true');
    //HidePrintButton
    config.toolbar.print.setAttribute('hidden','true');
    config.secondaryToolbar.printButton.setAttribute('hidden','true');
  }
  //EndFlectrapatch
  window.PDFViewerApplication=pdfjsWebApp.PDFViewerApplication;
  window.PDFViewerApplicationOptions=pdfjsWebAppOptions.AppOptions;
  varevent=document.createEvent('CustomEvent');
  event.initCustomEvent('webviewerloaded',true,true,{});
  document.dispatchEvent(event);
  pdfjsWebApp.PDFViewerApplication.run(config);
}

if(document.readyState==='interactive'||document.readyState==='complete'){
  webViewerLoad();
}else{
  document.addEventListener('DOMContentLoaded',webViewerLoad,true);
}

/***/}),
/*1*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFPrintServiceFactory=exports.DefaultExternalServices=exports.PDFViewerApplication=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

var_ui_utils=__webpack_require__(5);

var_app_options=__webpack_require__(6);

var_pdfjsLib=__webpack_require__(7);

var_pdf_cursor_tools=__webpack_require__(9);

var_pdf_rendering_queue=__webpack_require__(11);

var_pdf_sidebar=__webpack_require__(12);

var_overlay_manager=__webpack_require__(13);

var_password_prompt=__webpack_require__(14);

var_pdf_attachment_viewer=__webpack_require__(15);

var_pdf_document_properties=__webpack_require__(16);

var_pdf_find_bar=__webpack_require__(17);

var_pdf_find_controller=__webpack_require__(18);

var_pdf_history=__webpack_require__(20);

var_pdf_link_service=__webpack_require__(21);

var_pdf_outline_viewer=__webpack_require__(22);

var_pdf_presentation_mode=__webpack_require__(23);

var_pdf_sidebar_resizer=__webpack_require__(24);

var_pdf_thumbnail_viewer=__webpack_require__(25);

var_pdf_viewer=__webpack_require__(27);

var_secondary_toolbar=__webpack_require__(32);

var_toolbar=__webpack_require__(34);

var_view_history=__webpack_require__(35);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

varDEFAULT_SCALE_DELTA=1.1;
varDISABLE_AUTO_FETCH_LOADING_BAR_TIMEOUT=5000;
varFORCE_PAGES_LOADED_TIMEOUT=10000;
varWHEEL_ZOOM_DISABLED_TIMEOUT=1000;
varViewOnLoad={
  UNKNOWN:-1,
  PREVIOUS:0,
  INITIAL:1
};
varDefaultExternalServices={
  updateFindControlState:functionupdateFindControlState(data){},
  updateFindMatchesCount:functionupdateFindMatchesCount(data){},
  initPassiveLoading:functioninitPassiveLoading(callbacks){},
  fallback:functionfallback(data,callback){},
  reportTelemetry:functionreportTelemetry(data){},
  createDownloadManager:functioncreateDownloadManager(options){
    thrownewError('Notimplemented:createDownloadManager');
  },
  createPreferences:functioncreatePreferences(){
    thrownewError('Notimplemented:createPreferences');
  },
  createL10n:functioncreateL10n(options){
    thrownewError('Notimplemented:createL10n');
  },
  supportsIntegratedFind:false,
  supportsDocumentFonts:true,
  supportsDocumentColors:true,
  supportedMouseWheelZoomModifierKeys:{
    ctrlKey:true,
    metaKey:true
  }
};
exports.DefaultExternalServices=DefaultExternalServices;
varPDFViewerApplication={
  initialBookmark:document.location.hash.substring(1),
  initialized:false,
  fellback:false,
  appConfig:null,
  pdfDocument:null,
  pdfLoadingTask:null,
  printService:null,
  pdfViewer:null,
  pdfThumbnailViewer:null,
  pdfRenderingQueue:null,
  pdfPresentationMode:null,
  pdfDocumentProperties:null,
  pdfLinkService:null,
  pdfHistory:null,
  pdfSidebar:null,
  pdfSidebarResizer:null,
  pdfOutlineViewer:null,
  pdfAttachmentViewer:null,
  pdfCursorTools:null,
  store:null,
  downloadManager:null,
  overlayManager:null,
  preferences:null,
  toolbar:null,
  secondaryToolbar:null,
  eventBus:null,
  l10n:null,
  isInitialViewSet:false,
  downloadComplete:false,
  isViewerEmbedded:window.parent!==window,
  url:'',
  baseUrl:'',
  externalServices:DefaultExternalServices,
  _boundEvents:{},
  contentDispositionFilename:null,
  initialize:function(){
    var_initialize=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee(appConfig){
      var_this=this;

      varappContainer;
      return_regenerator["default"].wrap(function_callee$(_context){
        while(1){
          switch(_context.prev=_context.next){
            case0:
              this.preferences=this.externalServices.createPreferences();
              this.appConfig=appConfig;
              _context.next=4;
              returnthis._readPreferences();

            case4:
              _context.next=6;
              returnthis._parseHashParameters();

            case6:
              _context.next=8;
              returnthis._initializeL10n();

            case8:
              if(this.isViewerEmbedded&&_app_options.AppOptions.get('externalLinkTarget')===_pdfjsLib.LinkTarget.NONE){
                _app_options.AppOptions.set('externalLinkTarget',_pdfjsLib.LinkTarget.TOP);
              }

              _context.next=11;
              returnthis._initializeViewerComponents();

            case11:
              this.bindEvents();
              this.bindWindowEvents();
              appContainer=appConfig.appContainer||document.documentElement;
              this.l10n.translate(appContainer).then(function(){
                _this.eventBus.dispatch('localized',{
                  source:_this
                });
              });
              this.initialized=true;

            case16:
            case"end":
              return_context.stop();
          }
        }
      },_callee,this);
    }));

    functioninitialize(_x){
      return_initialize.apply(this,arguments);
    }

    returninitialize;
  }(),
  _readPreferences:function(){
    var_readPreferences2=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee2(){
      varprefs,name;
      return_regenerator["default"].wrap(function_callee2$(_context2){
        while(1){
          switch(_context2.prev=_context2.next){
            case0:
              if(!(_app_options.AppOptions.get('disablePreferences')===true)){
                _context2.next=2;
                break;
              }

              return_context2.abrupt("return");

            case2:
              _context2.prev=2;
              _context2.next=5;
              returnthis.preferences.getAll();

            case5:
              prefs=_context2.sent;

              for(nameinprefs){
                _app_options.AppOptions.set(name,prefs[name]);
              }

              _context2.next=12;
              break;

            case9:
              _context2.prev=9;
              _context2.t0=_context2["catch"](2);
              console.error("_readPreferences:\"".concat(_context2.t0.message,"\"."));

            case12:
            case"end":
              return_context2.stop();
          }
        }
      },_callee2,this,[[2,9]]);
    }));

    function_readPreferences(){
      return_readPreferences2.apply(this,arguments);
    }

    return_readPreferences;
  }(),
  _parseHashParameters:function(){
    var_parseHashParameters2=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee3(){
      varwaitOn,hash,hashParams,viewer,enabled;
      return_regenerator["default"].wrap(function_callee3$(_context3){
        while(1){
          switch(_context3.prev=_context3.next){
            case0:
              if(_app_options.AppOptions.get('pdfBugEnabled')){
                _context3.next=2;
                break;
              }

              return_context3.abrupt("return",undefined);

            case2:
              waitOn=[];
              hash=document.location.hash.substring(1);
              hashParams=(0,_ui_utils.parseQueryString)(hash);

              if('disableworker'inhashParams&&hashParams['disableworker']==='true'){
                waitOn.push(loadFakeWorker());
              }

              if('disablerange'inhashParams){
                _app_options.AppOptions.set('disableRange',hashParams['disablerange']==='true');
              }

              if('disablestream'inhashParams){
                _app_options.AppOptions.set('disableStream',hashParams['disablestream']==='true');
              }

              if('disableautofetch'inhashParams){
                _app_options.AppOptions.set('disableAutoFetch',hashParams['disableautofetch']==='true');
              }

              if('disablefontface'inhashParams){
                _app_options.AppOptions.set('disableFontFace',hashParams['disablefontface']==='true');
              }

              if('disablehistory'inhashParams){
                _app_options.AppOptions.set('disableHistory',hashParams['disablehistory']==='true');
              }

              if('webgl'inhashParams){
                _app_options.AppOptions.set('enableWebGL',hashParams['webgl']==='true');
              }

              if('useonlycsszoom'inhashParams){
                _app_options.AppOptions.set('useOnlyCssZoom',hashParams['useonlycsszoom']==='true');
              }

              if('verbosity'inhashParams){
                _app_options.AppOptions.set('verbosity',hashParams['verbosity']|0);
              }

              if(!('textlayer'inhashParams)){
                _context3.next=23;
                break;
              }

              _context3.t0=hashParams['textlayer'];
              _context3.next=_context3.t0==='off'?18:_context3.t0==='visible'?20:_context3.t0==='shadow'?20:_context3.t0==='hover'?20:23;
              break;

            case18:
              _app_options.AppOptions.set('textLayerMode',_ui_utils.TextLayerMode.DISABLE);

              return_context3.abrupt("break",23);

            case20:
              viewer=this.appConfig.viewerContainer;
              viewer.classList.add('textLayer-'+hashParams['textlayer']);
              return_context3.abrupt("break",23);

            case23:
              if('pdfbug'inhashParams){
                _app_options.AppOptions.set('pdfBug',true);

                enabled=hashParams['pdfbug'].split(',');
                waitOn.push(loadAndEnablePDFBug(enabled));
              }

              if('locale'inhashParams){
                _app_options.AppOptions.set('locale',hashParams['locale']);
              }

              return_context3.abrupt("return",Promise.all(waitOn)["catch"](function(reason){
                console.error("_parseHashParameters:\"".concat(reason.message,"\"."));
              }));

            case26:
            case"end":
              return_context3.stop();
          }
        }
      },_callee3,this);
    }));

    function_parseHashParameters(){
      return_parseHashParameters2.apply(this,arguments);
    }

    return_parseHashParameters;
  }(),
  _initializeL10n:function(){
    var_initializeL10n2=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee4(){
      vardir;
      return_regenerator["default"].wrap(function_callee4$(_context4){
        while(1){
          switch(_context4.prev=_context4.next){
            case0:
              this.l10n=this.externalServices.createL10n({
                locale:_app_options.AppOptions.get('locale')
              });
              _context4.next=3;
              returnthis.l10n.getDirection();

            case3:
              dir=_context4.sent;
              document.getElementsByTagName('html')[0].dir=dir;

            case5:
            case"end":
              return_context4.stop();
          }
        }
      },_callee4,this);
    }));

    function_initializeL10n(){
      return_initializeL10n2.apply(this,arguments);
    }

    return_initializeL10n;
  }(),
  _initializeViewerComponents:function(){
    var_initializeViewerComponents2=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee5(){
      varappConfig,eventBus,pdfRenderingQueue,pdfLinkService,downloadManager,findController,container,viewer;
      return_regenerator["default"].wrap(function_callee5$(_context5){
        while(1){
          switch(_context5.prev=_context5.next){
            case0:
              appConfig=this.appConfig;
              this.overlayManager=new_overlay_manager.OverlayManager();
              eventBus=appConfig.eventBus||(0,_ui_utils.getGlobalEventBus)(_app_options.AppOptions.get('eventBusDispatchToDOM'));
              this.eventBus=eventBus;
              pdfRenderingQueue=new_pdf_rendering_queue.PDFRenderingQueue();
              pdfRenderingQueue.onIdle=this.cleanup.bind(this);
              this.pdfRenderingQueue=pdfRenderingQueue;
              pdfLinkService=new_pdf_link_service.PDFLinkService({
                eventBus:eventBus,
                externalLinkTarget:_app_options.AppOptions.get('externalLinkTarget'),
                externalLinkRel:_app_options.AppOptions.get('externalLinkRel')
              });
              this.pdfLinkService=pdfLinkService;
              downloadManager=this.externalServices.createDownloadManager({
                disableCreateObjectURL:_app_options.AppOptions.get('disableCreateObjectURL')
              });
              this.downloadManager=downloadManager;
              findController=new_pdf_find_controller.PDFFindController({
                linkService:pdfLinkService,
                eventBus:eventBus
              });
              this.findController=findController;
              container=appConfig.mainContainer;
              viewer=appConfig.viewerContainer;
              this.pdfViewer=new_pdf_viewer.PDFViewer({
                container:container,
                viewer:viewer,
                eventBus:eventBus,
                renderingQueue:pdfRenderingQueue,
                linkService:pdfLinkService,
                downloadManager:downloadManager,
                findController:findController,
                renderer:_app_options.AppOptions.get('renderer'),
                enableWebGL:_app_options.AppOptions.get('enableWebGL'),
                l10n:this.l10n,
                textLayerMode:_app_options.AppOptions.get('textLayerMode'),
                imageResourcesPath:_app_options.AppOptions.get('imageResourcesPath'),
                renderInteractiveForms:_app_options.AppOptions.get('renderInteractiveForms'),
                enablePrintAutoRotate:_app_options.AppOptions.get('enablePrintAutoRotate'),
                useOnlyCssZoom:_app_options.AppOptions.get('useOnlyCssZoom'),
                maxCanvasPixels:_app_options.AppOptions.get('maxCanvasPixels')
              });
              pdfRenderingQueue.setViewer(this.pdfViewer);
              pdfLinkService.setViewer(this.pdfViewer);
              this.pdfThumbnailViewer=new_pdf_thumbnail_viewer.PDFThumbnailViewer({
                container:appConfig.sidebar.thumbnailView,
                renderingQueue:pdfRenderingQueue,
                linkService:pdfLinkService,
                l10n:this.l10n
              });
              pdfRenderingQueue.setThumbnailViewer(this.pdfThumbnailViewer);
              this.pdfHistory=new_pdf_history.PDFHistory({
                linkService:pdfLinkService,
                eventBus:eventBus
              });
              pdfLinkService.setHistory(this.pdfHistory);
              this.findBar=new_pdf_find_bar.PDFFindBar(appConfig.findBar,eventBus,this.l10n);
              this.pdfDocumentProperties=new_pdf_document_properties.PDFDocumentProperties(appConfig.documentProperties,this.overlayManager,eventBus,this.l10n);
              this.pdfCursorTools=new_pdf_cursor_tools.PDFCursorTools({
                container:container,
                eventBus:eventBus,
                cursorToolOnLoad:_app_options.AppOptions.get('cursorToolOnLoad')
              });
              this.toolbar=new_toolbar.Toolbar(appConfig.toolbar,eventBus,this.l10n);
              this.secondaryToolbar=new_secondary_toolbar.SecondaryToolbar(appConfig.secondaryToolbar,container,eventBus);

              if(this.supportsFullscreen){
                this.pdfPresentationMode=new_pdf_presentation_mode.PDFPresentationMode({
                  container:container,
                  viewer:viewer,
                  pdfViewer:this.pdfViewer,
                  eventBus:eventBus,
                  contextMenuItems:appConfig.fullscreen
                });
              }

              this.passwordPrompt=new_password_prompt.PasswordPrompt(appConfig.passwordOverlay,this.overlayManager,this.l10n);
              this.pdfOutlineViewer=new_pdf_outline_viewer.PDFOutlineViewer({
                container:appConfig.sidebar.outlineView,
                eventBus:eventBus,
                linkService:pdfLinkService
              });
              this.pdfAttachmentViewer=new_pdf_attachment_viewer.PDFAttachmentViewer({
                container:appConfig.sidebar.attachmentsView,
                eventBus:eventBus,
                downloadManager:downloadManager
              });
              this.pdfSidebar=new_pdf_sidebar.PDFSidebar({
                elements:appConfig.sidebar,
                pdfViewer:this.pdfViewer,
                pdfThumbnailViewer:this.pdfThumbnailViewer,
                eventBus:eventBus,
                l10n:this.l10n
              });
              this.pdfSidebar.onToggled=this.forceRendering.bind(this);
              this.pdfSidebarResizer=new_pdf_sidebar_resizer.PDFSidebarResizer(appConfig.sidebarResizer,eventBus,this.l10n);

            case34:
            case"end":
              return_context5.stop();
          }
        }
      },_callee5,this);
    }));

    function_initializeViewerComponents(){
      return_initializeViewerComponents2.apply(this,arguments);
    }

    return_initializeViewerComponents;
  }(),
  run:functionrun(config){
    this.initialize(config).then(webViewerInitialized);
  },
  zoomIn:functionzoomIn(ticks){
    varnewScale=this.pdfViewer.currentScale;

    do{
      newScale=(newScale*DEFAULT_SCALE_DELTA).toFixed(2);
      newScale=Math.ceil(newScale*10)/10;
      newScale=Math.min(_ui_utils.MAX_SCALE,newScale);
    }while(--ticks>0&&newScale<_ui_utils.MAX_SCALE);

    this.pdfViewer.currentScaleValue=newScale;
  },
  zoomOut:functionzoomOut(ticks){
    varnewScale=this.pdfViewer.currentScale;

    do{
      newScale=(newScale/DEFAULT_SCALE_DELTA).toFixed(2);
      newScale=Math.floor(newScale*10)/10;
      newScale=Math.max(_ui_utils.MIN_SCALE,newScale);
    }while(--ticks>0&&newScale>_ui_utils.MIN_SCALE);

    this.pdfViewer.currentScaleValue=newScale;
  },
  zoomReset:functionzoomReset(){
    varignoreDuplicate=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

    if(this.pdfViewer.isInPresentationMode){
      return;
    }elseif(ignoreDuplicate&&this.pdfViewer.currentScaleValue===_ui_utils.DEFAULT_SCALE_VALUE){
      return;
    }

    this.pdfViewer.currentScaleValue=_ui_utils.DEFAULT_SCALE_VALUE;
  },

  getpagesCount(){
    returnthis.pdfDocument?this.pdfDocument.numPages:0;
  },

  setpage(val){
    this.pdfViewer.currentPageNumber=val;
  },

  getpage(){
    returnthis.pdfViewer.currentPageNumber;
  },

  getprinting(){
    return!!this.printService;
  },

  getsupportsPrinting(){
    returnPDFPrintServiceFactory.instance.supportsPrinting;
  },

  getsupportsFullscreen(){
    varsupport;
    vardoc=document.documentElement;
    support=!!(doc.requestFullscreen||doc.mozRequestFullScreen||doc.webkitRequestFullScreen||doc.msRequestFullscreen);

    if(document.fullscreenEnabled===false||document.mozFullScreenEnabled===false||document.webkitFullscreenEnabled===false||document.msFullscreenEnabled===false){
      support=false;
    }

    return(0,_pdfjsLib.shadow)(this,'supportsFullscreen',support);
  },

  getsupportsIntegratedFind(){
    returnthis.externalServices.supportsIntegratedFind;
  },

  getsupportsDocumentFonts(){
    returnthis.externalServices.supportsDocumentFonts;
  },

  getsupportsDocumentColors(){
    returnthis.externalServices.supportsDocumentColors;
  },

  getloadingBar(){
    varbar=new_ui_utils.ProgressBar('#loadingBar');
    return(0,_pdfjsLib.shadow)(this,'loadingBar',bar);
  },

  getsupportedMouseWheelZoomModifierKeys(){
    returnthis.externalServices.supportedMouseWheelZoomModifierKeys;
  },

  initPassiveLoading:functioninitPassiveLoading(){
    thrownewError('Notimplemented:initPassiveLoading');
  },
  setTitleUsingUrl:functionsetTitleUsingUrl(){
    varurl=arguments.length>0&&arguments[0]!==undefined?arguments[0]:'';
    this.url=url;
    this.baseUrl=url.split('#')[0];
    vartitle=(0,_ui_utils.getPDFFileNameFromURL)(url,'');

    if(!title){
      try{
        title=decodeURIComponent((0,_pdfjsLib.getFilenameFromUrl)(url))||url;
      }catch(ex){
        title=url;
      }
    }

    this.setTitle(title);
  },
  setTitle:functionsetTitle(title){
    if(this.isViewerEmbedded){
      return;
    }

    document.title=title;
  },
  close:function(){
    var_close=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee6(){
      varerrorWrapper,promise;
      return_regenerator["default"].wrap(function_callee6$(_context6){
        while(1){
          switch(_context6.prev=_context6.next){
            case0:
              errorWrapper=this.appConfig.errorWrapper.container;
              errorWrapper.setAttribute('hidden','true');

              if(this.pdfLoadingTask){
                _context6.next=4;
                break;
              }

              return_context6.abrupt("return",undefined);

            case4:
              promise=this.pdfLoadingTask.destroy();
              this.pdfLoadingTask=null;

              if(this.pdfDocument){
                this.pdfDocument=null;
                this.pdfThumbnailViewer.setDocument(null);
                this.pdfViewer.setDocument(null);
                this.pdfLinkService.setDocument(null);
                this.pdfDocumentProperties.setDocument(null);
              }

              this.store=null;
              this.isInitialViewSet=false;
              this.downloadComplete=false;
              this.url='';
              this.baseUrl='';
              this.contentDispositionFilename=null;
              this.pdfSidebar.reset();
              this.pdfOutlineViewer.reset();
              this.pdfAttachmentViewer.reset();
              this.findBar.reset();
              this.toolbar.reset();
              this.secondaryToolbar.reset();

              if(typeofPDFBug!=='undefined'){
                PDFBug.cleanup();
              }

              return_context6.abrupt("return",promise);

            case21:
            case"end":
              return_context6.stop();
          }
        }
      },_callee6,this);
    }));

    functionclose(){
      return_close.apply(this,arguments);
    }

    returnclose;
  }(),
  open:function(){
    var_open=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee7(file,args){
      var_this2=this;

      varworkerParameters,key,parameters,apiParameters,_key,prop,loadingTask;

      return_regenerator["default"].wrap(function_callee7$(_context7){
        while(1){
          switch(_context7.prev=_context7.next){
            case0:
              if(!this.pdfLoadingTask){
                _context7.next=3;
                break;
              }

              _context7.next=3;
              returnthis.close();

            case3:
              workerParameters=_app_options.AppOptions.getAll(_app_options.OptionKind.WORKER);

              for(keyinworkerParameters){
                _pdfjsLib.GlobalWorkerOptions[key]=workerParameters[key];
              }

              parameters=Object.create(null);

              if(typeoffile==='string'){
                this.setTitleUsingUrl(file);
                parameters.url=file;
              }elseif(file&&'byteLength'infile){
                parameters.data=file;
              }elseif(file.url&&file.originalUrl){
                this.setTitleUsingUrl(file.originalUrl);
                parameters.url=file.url;
              }

              apiParameters=_app_options.AppOptions.getAll(_app_options.OptionKind.API);

              for(_keyinapiParameters){
                parameters[_key]=apiParameters[_key];
              }

              if(args){
                for(propinargs){
                  if(prop==='length'){
                    this.pdfDocumentProperties.setFileSize(args[prop]);
                  }

                  parameters[prop]=args[prop];
                }
              }

              loadingTask=(0,_pdfjsLib.getDocument)(parameters);
              this.pdfLoadingTask=loadingTask;

              loadingTask.onPassword=function(updateCallback,reason){
                _this2.passwordPrompt.setUpdateCallback(updateCallback,reason);

                _this2.passwordPrompt.open();
              };

              loadingTask.onProgress=function(_ref){
                varloaded=_ref.loaded,
                    total=_ref.total;

                _this2.progress(loaded/total);
              };

              loadingTask.onUnsupportedFeature=this.fallback.bind(this);
              return_context7.abrupt("return",loadingTask.promise.then(function(pdfDocument){
                _this2.load(pdfDocument);
              },function(exception){
                if(loadingTask!==_this2.pdfLoadingTask){
                  returnundefined;
                }

                varmessage=exception&&exception.message;
                varloadingErrorMessage;

                if(exceptioninstanceof_pdfjsLib.InvalidPDFException){
                  loadingErrorMessage=_this2.l10n.get('invalid_file_error',null,'InvalidorcorruptedPDFfile.');
                }elseif(exceptioninstanceof_pdfjsLib.MissingPDFException){
                  loadingErrorMessage=_this2.l10n.get('missing_file_error',null,'MissingPDFfile.');
                }elseif(exceptioninstanceof_pdfjsLib.UnexpectedResponseException){
                  loadingErrorMessage=_this2.l10n.get('unexpected_response_error',null,'Unexpectedserverresponse.');
                }else{
                  loadingErrorMessage=_this2.l10n.get('loading_error',null,'AnerroroccurredwhileloadingthePDF.');
                }

                returnloadingErrorMessage.then(function(msg){
                  _this2.error(msg,{
                    message:message
                  });

                  thrownewError(msg);
                });
              }));

            case16:
            case"end":
              return_context7.stop();
          }
        }
      },_callee7,this);
    }));

    functionopen(_x2,_x3){
      return_open.apply(this,arguments);
    }

    returnopen;
  }(),
  download:functiondownload(){
    var_this3=this;

    functiondownloadByUrl(){
      downloadManager.downloadUrl(url,filename);
    }

    varurl=this.baseUrl;
    varfilename=this.contentDispositionFilename||(0,_ui_utils.getPDFFileNameFromURL)(this.url);
    vardownloadManager=this.downloadManager;

    downloadManager.onerror=function(err){
      _this3.error("PDFfailedtodownload:".concat(err));
    };

    if(!this.pdfDocument||!this.downloadComplete){
      downloadByUrl();
      return;
    }

    this.pdfDocument.getData().then(function(data){
      varblob=newBlob([data],{
        type:'application/pdf'
      });
      downloadManager.download(blob,url,filename);
    })["catch"](downloadByUrl);
  },
  fallback:functionfallback(featureId){},
  error:functionerror(message,moreInfo){
    varmoreInfoText=[this.l10n.get('error_version_info',{
      version:_pdfjsLib.version||'?',
      build:_pdfjsLib.build||'?'
    },'PDF.jsv{{version}}(build:{{build}})')];

    if(moreInfo){
      moreInfoText.push(this.l10n.get('error_message',{
        message:moreInfo.message
      },'Message:{{message}}'));

      if(moreInfo.stack){
        moreInfoText.push(this.l10n.get('error_stack',{
          stack:moreInfo.stack
        },'Stack:{{stack}}'));
      }else{
        if(moreInfo.filename){
          moreInfoText.push(this.l10n.get('error_file',{
            file:moreInfo.filename
          },'File:{{file}}'));
        }

        if(moreInfo.lineNumber){
          moreInfoText.push(this.l10n.get('error_line',{
            line:moreInfo.lineNumber
          },'Line:{{line}}'));
        }
      }
    }

    varerrorWrapperConfig=this.appConfig.errorWrapper;
    varerrorWrapper=errorWrapperConfig.container;
    errorWrapper.removeAttribute('hidden');
    varerrorMessage=errorWrapperConfig.errorMessage;
    errorMessage.textContent=message;
    varcloseButton=errorWrapperConfig.closeButton;

    closeButton.onclick=function(){
      errorWrapper.setAttribute('hidden','true');
    };

    varerrorMoreInfo=errorWrapperConfig.errorMoreInfo;
    varmoreInfoButton=errorWrapperConfig.moreInfoButton;
    varlessInfoButton=errorWrapperConfig.lessInfoButton;

    moreInfoButton.onclick=function(){
      errorMoreInfo.removeAttribute('hidden');
      moreInfoButton.setAttribute('hidden','true');
      lessInfoButton.removeAttribute('hidden');
      errorMoreInfo.style.height=errorMoreInfo.scrollHeight+'px';
    };

    lessInfoButton.onclick=function(){
      errorMoreInfo.setAttribute('hidden','true');
      moreInfoButton.removeAttribute('hidden');
      lessInfoButton.setAttribute('hidden','true');
    };

    moreInfoButton.oncontextmenu=_ui_utils.noContextMenuHandler;
    lessInfoButton.oncontextmenu=_ui_utils.noContextMenuHandler;
    closeButton.oncontextmenu=_ui_utils.noContextMenuHandler;
    moreInfoButton.removeAttribute('hidden');
    lessInfoButton.setAttribute('hidden','true');
    Promise.all(moreInfoText).then(function(parts){
      errorMoreInfo.value=parts.join('\n');
    });
  },
  progress:functionprogress(level){
    var_this4=this;

    if(this.downloadComplete){
      return;
    }

    varpercent=Math.round(level*100);

    if(percent>this.loadingBar.percent||isNaN(percent)){
      this.loadingBar.percent=percent;
      vardisableAutoFetch=this.pdfDocument?this.pdfDocument.loadingParams['disableAutoFetch']:_app_options.AppOptions.get('disableAutoFetch');

      if(disableAutoFetch&&percent){
        if(this.disableAutoFetchLoadingBarTimeout){
          clearTimeout(this.disableAutoFetchLoadingBarTimeout);
          this.disableAutoFetchLoadingBarTimeout=null;
        }

        this.loadingBar.show();
        this.disableAutoFetchLoadingBarTimeout=setTimeout(function(){
          _this4.loadingBar.hide();

          _this4.disableAutoFetchLoadingBarTimeout=null;
        },DISABLE_AUTO_FETCH_LOADING_BAR_TIMEOUT);
      }
    }
  },
  load:functionload(pdfDocument){
    var_this5=this;

    this.pdfDocument=pdfDocument;
    pdfDocument.getDownloadInfo().then(function(){
      _this5.downloadComplete=true;

      _this5.loadingBar.hide();

      firstPagePromise.then(function(){
        _this5.eventBus.dispatch('documentloaded',{
          source:_this5
        });
      });
    });
    varpageLayoutPromise=pdfDocument.getPageLayout()["catch"](function(){});
    varpageModePromise=pdfDocument.getPageMode()["catch"](function(){});
    varopenActionDestPromise=pdfDocument.getOpenActionDestination()["catch"](function(){});
    this.toolbar.setPagesCount(pdfDocument.numPages,false);
    this.secondaryToolbar.setPagesCount(pdfDocument.numPages);
    varstore=this.store=new_view_history.ViewHistory(pdfDocument.fingerprint);
    varbaseDocumentUrl;
    baseDocumentUrl=null;
    this.pdfLinkService.setDocument(pdfDocument,baseDocumentUrl);
    this.pdfDocumentProperties.setDocument(pdfDocument,this.url);
    varpdfViewer=this.pdfViewer;
    pdfViewer.setDocument(pdfDocument);
    varfirstPagePromise=pdfViewer.firstPagePromise;
    varpagesPromise=pdfViewer.pagesPromise;
    varonePageRendered=pdfViewer.onePageRendered;
    varpdfThumbnailViewer=this.pdfThumbnailViewer;
    pdfThumbnailViewer.setDocument(pdfDocument);
    firstPagePromise.then(function(pdfPage){
      _this5.loadingBar.setWidth(_this5.appConfig.viewerContainer);

      varstorePromise=store.getMultiple({
        page:null,
        zoom:_ui_utils.DEFAULT_SCALE_VALUE,
        scrollLeft:'0',
        scrollTop:'0',
        rotation:null,
        sidebarView:_pdf_sidebar.SidebarView.UNKNOWN,
        scrollMode:_ui_utils.ScrollMode.UNKNOWN,
        spreadMode:_ui_utils.SpreadMode.UNKNOWN
      })["catch"](function(){});
      Promise.all([storePromise,pageLayoutPromise,pageModePromise,openActionDestPromise]).then(
      /*#__PURE__*/
      function(){
        var_ref3=_asyncToGenerator(
        /*#__PURE__*/
        _regenerator["default"].mark(function_callee8(_ref2){
          var_ref4,_ref4$,values,pageLayout,pageMode,openActionDest,viewOnLoad,initialBookmark,zoom,hash,rotation,sidebarView,scrollMode,spreadMode;

          return_regenerator["default"].wrap(function_callee8$(_context8){
            while(1){
              switch(_context8.prev=_context8.next){
                case0:
                  _ref4=_slicedToArray(_ref2,4),_ref4$=_ref4[0],values=_ref4$===void0?{}:_ref4$,pageLayout=_ref4[1],pageMode=_ref4[2],openActionDest=_ref4[3];
                  viewOnLoad=_app_options.AppOptions.get('viewOnLoad');

                  _this5._initializePdfHistory({
                    fingerprint:pdfDocument.fingerprint,
                    viewOnLoad:viewOnLoad,
                    initialDest:openActionDest
                  });

                  initialBookmark=_this5.initialBookmark;
                  zoom=_app_options.AppOptions.get('defaultZoomValue');
                  hash=zoom?"zoom=".concat(zoom):null;
                  rotation=null;
                  sidebarView=_app_options.AppOptions.get('sidebarViewOnLoad');
                  scrollMode=_app_options.AppOptions.get('scrollModeOnLoad');
                  spreadMode=_app_options.AppOptions.get('spreadModeOnLoad');

                  if(values.page&&viewOnLoad!==ViewOnLoad.INITIAL){
                    hash="page=".concat(values.page,"&zoom=").concat(zoom||values.zoom,",")+"".concat(values.scrollLeft,",").concat(values.scrollTop);
                    rotation=parseInt(values.rotation,10);

                    if(sidebarView===_pdf_sidebar.SidebarView.UNKNOWN){
                      sidebarView=values.sidebarView|0;
                    }

                    if(scrollMode===_ui_utils.ScrollMode.UNKNOWN){
                      scrollMode=values.scrollMode|0;
                    }

                    if(spreadMode===_ui_utils.SpreadMode.UNKNOWN){
                      spreadMode=values.spreadMode|0;
                    }
                  }

                  if(pageMode&&sidebarView===_pdf_sidebar.SidebarView.UNKNOWN){
                    sidebarView=apiPageModeToSidebarView(pageMode);
                  }

                  if(pageLayout&&spreadMode===_ui_utils.SpreadMode.UNKNOWN){
                    spreadMode=apiPageLayoutToSpreadMode(pageLayout);
                  }

                  _this5.setInitialView(hash,{
                    rotation:rotation,
                    sidebarView:sidebarView,
                    scrollMode:scrollMode,
                    spreadMode:spreadMode
                  });

                  _this5.eventBus.dispatch('documentinit',{
                    source:_this5
                  });

                  if(!_this5.isViewerEmbedded){
                    pdfViewer.focus();
                  }

                  _context8.next=18;
                  returnPromise.race([pagesPromise,newPromise(function(resolve){
                    setTimeout(resolve,FORCE_PAGES_LOADED_TIMEOUT);
                  })]);

                case18:
                  if(!(!initialBookmark&&!hash)){
                    _context8.next=20;
                    break;
                  }

                  return_context8.abrupt("return");

                case20:
                  if(!pdfViewer.hasEqualPageSizes){
                    _context8.next=22;
                    break;
                  }

                  return_context8.abrupt("return");

                case22:
                  _this5.initialBookmark=initialBookmark;
                  pdfViewer.currentScaleValue=pdfViewer.currentScaleValue;

                  _this5.setInitialView(hash);

                case25:
                case"end":
                  return_context8.stop();
              }
            }
          },_callee8);
        }));

        returnfunction(_x4){
          return_ref3.apply(this,arguments);
        };
      }())["catch"](function(){
        _this5.setInitialView();
      }).then(function(){
        pdfViewer.update();
      });
    });
    pdfDocument.getPageLabels().then(function(labels){
      if(!labels||_app_options.AppOptions.get('disablePageLabels')){
        return;
      }

      vari=0,
          numLabels=labels.length;

      if(numLabels!==_this5.pagesCount){
        console.error('ThenumberofPageLabelsdoesnotmatch'+'thenumberofpagesinthedocument.');
        return;
      }

      while(i<numLabels&&labels[i]===(i+1).toString()){
        i++;
      }

      if(i===numLabels){
        return;
      }

      pdfViewer.setPageLabels(labels);
      pdfThumbnailViewer.setPageLabels(labels);

      _this5.toolbar.setPagesCount(pdfDocument.numPages,true);

      _this5.toolbar.setPageNumber(pdfViewer.currentPageNumber,pdfViewer.currentPageLabel);
    });
    pagesPromise.then(function(){
      if(!_this5.supportsPrinting){
        return;
      }

      pdfDocument.getJavaScript().then(function(javaScript){
        if(!javaScript){
          return;
        }

        javaScript.some(function(js){
          if(!js){
            returnfalse;
          }

          console.warn('Warning:JavaScriptisnotsupported');

          _this5.fallback(_pdfjsLib.UNSUPPORTED_FEATURES.javaScript);

          returntrue;
        });
        varregex=/\bprint\s*\(/;

        for(vari=0,ii=javaScript.length;i<ii;i++){
          varjs=javaScript[i];

          if(js&&regex.test(js)){
            setTimeout(function(){
              window.print();
            });
            return;
          }
        }
      });
    });
    Promise.all([onePageRendered,_ui_utils.animationStarted]).then(function(){
      pdfDocument.getOutline().then(function(outline){
        _this5.pdfOutlineViewer.render({
          outline:outline
        });
      });
      pdfDocument.getAttachments().then(function(attachments){
        _this5.pdfAttachmentViewer.render({
          attachments:attachments
        });
      });
    });
    pdfDocument.getMetadata().then(function(_ref5){
      varinfo=_ref5.info,
          metadata=_ref5.metadata,
          contentDispositionFilename=_ref5.contentDispositionFilename;
      _this5.documentInfo=info;
      _this5.metadata=metadata;
      _this5.contentDispositionFilename=contentDispositionFilename;
      console.log('PDF'+pdfDocument.fingerprint+'['+info.PDFFormatVersion+''+(info.Producer||'-').trim()+'/'+(info.Creator||'-').trim()+']'+'(PDF.js:'+(_pdfjsLib.version||'-')+(_app_options.AppOptions.get('enableWebGL')?'[WebGL]':'')+')');
      varpdfTitle;

      if(metadata&&metadata.has('dc:title')){
        vartitle=metadata.get('dc:title');

        if(title!=='Untitled'){
          pdfTitle=title;
        }
      }

      if(!pdfTitle&&info&&info['Title']){
        pdfTitle=info['Title'];
      }

      if(pdfTitle){
        _this5.setTitle("".concat(pdfTitle,"-").concat(contentDispositionFilename||document.title));
      }elseif(contentDispositionFilename){
        _this5.setTitle(contentDispositionFilename);
      }

      if(info.IsAcroFormPresent){
        console.warn('Warning:AcroForm/XFAisnotsupported');

        _this5.fallback(_pdfjsLib.UNSUPPORTED_FEATURES.forms);
      }
    });
  },
  _initializePdfHistory:function_initializePdfHistory(_ref6){
    varfingerprint=_ref6.fingerprint,
        viewOnLoad=_ref6.viewOnLoad,
        _ref6$initialDest=_ref6.initialDest,
        initialDest=_ref6$initialDest===void0?null:_ref6$initialDest;

    if(_app_options.AppOptions.get('disableHistory')||this.isViewerEmbedded){
      return;
    }

    this.pdfHistory.initialize({
      fingerprint:fingerprint,
      resetHistory:viewOnLoad===ViewOnLoad.INITIAL,
      updateUrl:_app_options.AppOptions.get('historyUpdateUrl')
    });

    if(this.pdfHistory.initialBookmark){
      this.initialBookmark=this.pdfHistory.initialBookmark;
      this.initialRotation=this.pdfHistory.initialRotation;
    }

    if(initialDest&&!this.initialBookmark&&viewOnLoad===ViewOnLoad.UNKNOWN){
      this.initialBookmark=JSON.stringify(initialDest);
      this.pdfHistory.push({
        explicitDest:initialDest,
        pageNumber:null
      });
    }
  },
  setInitialView:functionsetInitialView(storedHash){
    var_this6=this;

    var_ref7=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{},
        rotation=_ref7.rotation,
        sidebarView=_ref7.sidebarView,
        scrollMode=_ref7.scrollMode,
        spreadMode=_ref7.spreadMode;

    varsetRotation=functionsetRotation(angle){
      if((0,_ui_utils.isValidRotation)(angle)){
        _this6.pdfViewer.pagesRotation=angle;
      }
    };

    varsetViewerModes=functionsetViewerModes(scroll,spread){
      if((0,_ui_utils.isValidScrollMode)(scroll)){
        _this6.pdfViewer.scrollMode=scroll;
      }

      if((0,_ui_utils.isValidSpreadMode)(spread)){
        _this6.pdfViewer.spreadMode=spread;
      }
    };

    this.isInitialViewSet=true;
    this.pdfSidebar.setInitialView(sidebarView);
    setViewerModes(scrollMode,spreadMode);

    if(this.initialBookmark){
      setRotation(this.initialRotation);
      deletethis.initialRotation;
      this.pdfLinkService.setHash(this.initialBookmark);
      this.initialBookmark=null;
    }elseif(storedHash){
      setRotation(rotation);
      this.pdfLinkService.setHash(storedHash);
    }

    this.toolbar.setPageNumber(this.pdfViewer.currentPageNumber,this.pdfViewer.currentPageLabel);
    this.secondaryToolbar.setPageNumber(this.pdfViewer.currentPageNumber);

    if(!this.pdfViewer.currentScaleValue){
      this.pdfViewer.currentScaleValue=_ui_utils.DEFAULT_SCALE_VALUE;
    }
  },
  cleanup:functioncleanup(){
    if(!this.pdfDocument){
      return;
    }

    this.pdfViewer.cleanup();
    this.pdfThumbnailViewer.cleanup();

    if(this.pdfViewer.renderer!==_ui_utils.RendererType.SVG){
      this.pdfDocument.cleanup();
    }
  },
  forceRendering:functionforceRendering(){
    this.pdfRenderingQueue.printing=this.printing;
    this.pdfRenderingQueue.isThumbnailViewEnabled=this.pdfSidebar.isThumbnailViewVisible;
    this.pdfRenderingQueue.renderHighestPriority();
  },
  beforePrint:functionbeforePrint(){
    var_this7=this;

    if(this.printService){
      return;
    }

    if(!this.supportsPrinting){
      this.l10n.get('printing_not_supported',null,'Warning:Printingisnotfullysupportedby'+'thisbrowser.').then(function(printMessage){
        _this7.error(printMessage);
      });
      return;
    }

    if(!this.pdfViewer.pageViewsReady){
      this.l10n.get('printing_not_ready',null,'Warning:ThePDFisnotfullyloadedforprinting.').then(function(notReadyMessage){
        window.alert(notReadyMessage);
      });
      return;
    }

    varpagesOverview=this.pdfViewer.getPagesOverview();
    varprintContainer=this.appConfig.printContainer;
    varprintService=PDFPrintServiceFactory.instance.createPrintService(this.pdfDocument,pagesOverview,printContainer,this.l10n);
    this.printService=printService;
    this.forceRendering();
    printService.layout();
  },
  afterPrint:functionpdfViewSetupAfterPrint(){
    if(this.printService){
      this.printService.destroy();
      this.printService=null;
    }

    this.forceRendering();
  },
  rotatePages:functionrotatePages(delta){
    if(!this.pdfDocument){
      return;
    }

    varnewRotation=(this.pdfViewer.pagesRotation+360+delta)%360;
    this.pdfViewer.pagesRotation=newRotation;
  },
  requestPresentationMode:functionrequestPresentationMode(){
    if(!this.pdfPresentationMode){
      return;
    }

    this.pdfPresentationMode.request();
  },
  bindEvents:functionbindEvents(){
    vareventBus=this.eventBus,
        _boundEvents=this._boundEvents;
    _boundEvents.beforePrint=this.beforePrint.bind(this);
    _boundEvents.afterPrint=this.afterPrint.bind(this);
    eventBus.on('resize',webViewerResize);
    eventBus.on('hashchange',webViewerHashchange);
    eventBus.on('beforeprint',_boundEvents.beforePrint);
    eventBus.on('afterprint',_boundEvents.afterPrint);
    eventBus.on('pagerendered',webViewerPageRendered);
    eventBus.on('textlayerrendered',webViewerTextLayerRendered);
    eventBus.on('updateviewarea',webViewerUpdateViewarea);
    eventBus.on('pagechanging',webViewerPageChanging);
    eventBus.on('scalechanging',webViewerScaleChanging);
    eventBus.on('rotationchanging',webViewerRotationChanging);
    eventBus.on('sidebarviewchanged',webViewerSidebarViewChanged);
    eventBus.on('pagemode',webViewerPageMode);
    eventBus.on('namedaction',webViewerNamedAction);
    eventBus.on('presentationmodechanged',webViewerPresentationModeChanged);
    eventBus.on('presentationmode',webViewerPresentationMode);
    eventBus.on('openfile',webViewerOpenFile);
    eventBus.on('print',webViewerPrint);
    eventBus.on('download',webViewerDownload);
    eventBus.on('firstpage',webViewerFirstPage);
    eventBus.on('lastpage',webViewerLastPage);
    eventBus.on('nextpage',webViewerNextPage);
    eventBus.on('previouspage',webViewerPreviousPage);
    eventBus.on('zoomin',webViewerZoomIn);
    eventBus.on('zoomout',webViewerZoomOut);
    eventBus.on('zoomreset',webViewerZoomReset);
    eventBus.on('pagenumberchanged',webViewerPageNumberChanged);
    eventBus.on('scalechanged',webViewerScaleChanged);
    eventBus.on('rotatecw',webViewerRotateCw);
    eventBus.on('rotateccw',webViewerRotateCcw);
    eventBus.on('switchscrollmode',webViewerSwitchScrollMode);
    eventBus.on('scrollmodechanged',webViewerScrollModeChanged);
    eventBus.on('switchspreadmode',webViewerSwitchSpreadMode);
    eventBus.on('spreadmodechanged',webViewerSpreadModeChanged);
    eventBus.on('documentproperties',webViewerDocumentProperties);
    eventBus.on('find',webViewerFind);
    eventBus.on('findfromurlhash',webViewerFindFromUrlHash);
    eventBus.on('updatefindmatchescount',webViewerUpdateFindMatchesCount);
    eventBus.on('updatefindcontrolstate',webViewerUpdateFindControlState);
    eventBus.on('fileinputchange',webViewerFileInputChange);
  },
  bindWindowEvents:functionbindWindowEvents(){
    vareventBus=this.eventBus,
        _boundEvents=this._boundEvents;

    _boundEvents.windowResize=function(){
      eventBus.dispatch('resize',{
        source:window
      });
    };

    _boundEvents.windowHashChange=function(){
      eventBus.dispatch('hashchange',{
        source:window,
        hash:document.location.hash.substring(1)
      });
    };

    _boundEvents.windowBeforePrint=function(){
      eventBus.dispatch('beforeprint',{
        source:window
      });
    };

    _boundEvents.windowAfterPrint=function(){
      eventBus.dispatch('afterprint',{
        source:window
      });
    };

    window.addEventListener('visibilitychange',webViewerVisibilityChange);
    window.addEventListener('wheel',webViewerWheel,{
      passive:false
    });
    window.addEventListener('click',webViewerClick);
    window.addEventListener('keydown',webViewerKeyDown);
    window.addEventListener('resize',_boundEvents.windowResize);
    window.addEventListener('hashchange',_boundEvents.windowHashChange);
    window.addEventListener('beforeprint',_boundEvents.windowBeforePrint);
    window.addEventListener('afterprint',_boundEvents.windowAfterPrint);
  },
  unbindEvents:functionunbindEvents(){
    vareventBus=this.eventBus,
        _boundEvents=this._boundEvents;
    eventBus.off('resize',webViewerResize);
    eventBus.off('hashchange',webViewerHashchange);
    eventBus.off('beforeprint',_boundEvents.beforePrint);
    eventBus.off('afterprint',_boundEvents.afterPrint);
    eventBus.off('pagerendered',webViewerPageRendered);
    eventBus.off('textlayerrendered',webViewerTextLayerRendered);
    eventBus.off('updateviewarea',webViewerUpdateViewarea);
    eventBus.off('pagechanging',webViewerPageChanging);
    eventBus.off('scalechanging',webViewerScaleChanging);
    eventBus.off('rotationchanging',webViewerRotationChanging);
    eventBus.off('sidebarviewchanged',webViewerSidebarViewChanged);
    eventBus.off('pagemode',webViewerPageMode);
    eventBus.off('namedaction',webViewerNamedAction);
    eventBus.off('presentationmodechanged',webViewerPresentationModeChanged);
    eventBus.off('presentationmode',webViewerPresentationMode);
    eventBus.off('openfile',webViewerOpenFile);
    eventBus.off('print',webViewerPrint);
    eventBus.off('download',webViewerDownload);
    eventBus.off('firstpage',webViewerFirstPage);
    eventBus.off('lastpage',webViewerLastPage);
    eventBus.off('nextpage',webViewerNextPage);
    eventBus.off('previouspage',webViewerPreviousPage);
    eventBus.off('zoomin',webViewerZoomIn);
    eventBus.off('zoomout',webViewerZoomOut);
    eventBus.off('zoomreset',webViewerZoomReset);
    eventBus.off('pagenumberchanged',webViewerPageNumberChanged);
    eventBus.off('scalechanged',webViewerScaleChanged);
    eventBus.off('rotatecw',webViewerRotateCw);
    eventBus.off('rotateccw',webViewerRotateCcw);
    eventBus.off('switchscrollmode',webViewerSwitchScrollMode);
    eventBus.off('scrollmodechanged',webViewerScrollModeChanged);
    eventBus.off('switchspreadmode',webViewerSwitchSpreadMode);
    eventBus.off('spreadmodechanged',webViewerSpreadModeChanged);
    eventBus.off('documentproperties',webViewerDocumentProperties);
    eventBus.off('find',webViewerFind);
    eventBus.off('findfromurlhash',webViewerFindFromUrlHash);
    eventBus.off('updatefindmatchescount',webViewerUpdateFindMatchesCount);
    eventBus.off('updatefindcontrolstate',webViewerUpdateFindControlState);
    eventBus.off('fileinputchange',webViewerFileInputChange);
    _boundEvents.beforePrint=null;
    _boundEvents.afterPrint=null;
  },
  unbindWindowEvents:functionunbindWindowEvents(){
    var_boundEvents=this._boundEvents;
    window.removeEventListener('visibilitychange',webViewerVisibilityChange);
    window.removeEventListener('wheel',webViewerWheel);
    window.removeEventListener('click',webViewerClick);
    window.removeEventListener('keydown',webViewerKeyDown);
    window.removeEventListener('resize',_boundEvents.windowResize);
    window.removeEventListener('hashchange',_boundEvents.windowHashChange);
    window.removeEventListener('beforeprint',_boundEvents.windowBeforePrint);
    window.removeEventListener('afterprint',_boundEvents.windowAfterPrint);
    _boundEvents.windowResize=null;
    _boundEvents.windowHashChange=null;
    _boundEvents.windowBeforePrint=null;
    _boundEvents.windowAfterPrint=null;
  }
};
exports.PDFViewerApplication=PDFViewerApplication;
varvalidateFileURL;
{
  varHOSTED_VIEWER_ORIGINS=['null','http://mozilla.github.io','https://mozilla.github.io'];

  validateFileURL=functionvalidateFileURL(file){
    if(file===undefined){
      return;
    }

    try{
      varviewerOrigin=new_pdfjsLib.URL(window.location.href).origin||'null';

      if(HOSTED_VIEWER_ORIGINS.includes(viewerOrigin)){
        return;
      }

      var_ref8=new_pdfjsLib.URL(file,window.location.href),
          origin=_ref8.origin,
          protocol=_ref8.protocol;

      if(origin!==viewerOrigin&&protocol!=='blob:'){
        thrownewError('fileorigindoesnotmatchviewer\'s');
      }
    }catch(ex){
      varmessage=ex&&ex.message;
      PDFViewerApplication.l10n.get('loading_error',null,'AnerroroccurredwhileloadingthePDF.').then(function(loadingErrorMessage){
        PDFViewerApplication.error(loadingErrorMessage,{
          message:message
        });
      });
      throwex;
    }
  };
}

functionloadFakeWorker(){
  if(!_pdfjsLib.GlobalWorkerOptions.workerSrc){
    _pdfjsLib.GlobalWorkerOptions.workerSrc=_app_options.AppOptions.get('workerSrc');
  }

  return(0,_pdfjsLib.loadScript)(_pdfjsLib.PDFWorker.getWorkerSrc());
}

functionloadAndEnablePDFBug(enabledTabs){
  varappConfig=PDFViewerApplication.appConfig;
  return(0,_pdfjsLib.loadScript)(appConfig.debuggerScriptPath).then(function(){
    PDFBug.enable(enabledTabs);
    PDFBug.init({
      OPS:_pdfjsLib.OPS,
      createObjectURL:_pdfjsLib.createObjectURL
    },appConfig.mainContainer);
  });
}

functionwebViewerInitialized(){
  varappConfig=PDFViewerApplication.appConfig;
  varfile;
  varqueryString=document.location.search.substring(1);
  varparams=(0,_ui_utils.parseQueryString)(queryString);
  file='file'inparams?params.file:_app_options.AppOptions.get('defaultUrl');
  validateFileURL(file);
  varfileInput=document.createElement('input');
  fileInput.id=appConfig.openFileInputName;
  fileInput.className='fileInput';
  fileInput.setAttribute('type','file');
  fileInput.oncontextmenu=_ui_utils.noContextMenuHandler;
  document.body.appendChild(fileInput);

  if(!window.File||!window.FileReader||!window.FileList||!window.Blob){
    appConfig.toolbar.openFile.setAttribute('hidden','true');
    appConfig.secondaryToolbar.openFileButton.setAttribute('hidden','true');
  }else{
    fileInput.value=null;
  }

  fileInput.addEventListener('change',function(evt){
    varfiles=evt.target.files;

    if(!files||files.length===0){
      return;
    }

    PDFViewerApplication.eventBus.dispatch('fileinputchange',{
      source:this,
      fileInput:evt.target
    });
  });
  appConfig.mainContainer.addEventListener('dragover',function(evt){
    evt.preventDefault();
    evt.dataTransfer.dropEffect='move';
  });
  appConfig.mainContainer.addEventListener('drop',function(evt){
    evt.preventDefault();
    varfiles=evt.dataTransfer.files;

    if(!files||files.length===0){
      return;
    }

    PDFViewerApplication.eventBus.dispatch('fileinputchange',{
      source:this,
      fileInput:evt.dataTransfer
    });
  });

  if(!PDFViewerApplication.supportsPrinting){
    appConfig.toolbar.print.classList.add('hidden');
    appConfig.secondaryToolbar.printButton.classList.add('hidden');
  }

  if(!PDFViewerApplication.supportsFullscreen){
    appConfig.toolbar.presentationModeButton.classList.add('hidden');
    appConfig.secondaryToolbar.presentationModeButton.classList.add('hidden');
  }

  if(PDFViewerApplication.supportsIntegratedFind){
    appConfig.toolbar.viewFind.classList.add('hidden');
  }

  appConfig.mainContainer.addEventListener('transitionend',function(evt){
    if(evt.target===this){
      PDFViewerApplication.eventBus.dispatch('resize',{
        source:this
      });
    }
  },true);
  appConfig.sidebar.toggleButton.addEventListener('click',function(){
    PDFViewerApplication.pdfSidebar.toggle();
  });

  try{
    webViewerOpenFileViaURL(file);
  }catch(reason){
    PDFViewerApplication.l10n.get('loading_error',null,'AnerroroccurredwhileloadingthePDF.').then(function(msg){
      PDFViewerApplication.error(msg,reason);
    });
  }
}

varwebViewerOpenFileViaURL;
{
  webViewerOpenFileViaURL=functionwebViewerOpenFileViaURL(file){
    if(file&&file.lastIndexOf('file:',0)===0){
      PDFViewerApplication.setTitleUsingUrl(file);
      varxhr=newXMLHttpRequest();

      xhr.onload=function(){
        PDFViewerApplication.open(newUint8Array(xhr.response));
      };

      xhr.open('GET',file);
      xhr.responseType='arraybuffer';
      xhr.send();
      return;
    }

    if(file){
      PDFViewerApplication.open(file);
    }
  };
}

functionwebViewerPageRendered(evt){
  varpageNumber=evt.pageNumber;
  varpageIndex=pageNumber-1;
  varpageView=PDFViewerApplication.pdfViewer.getPageView(pageIndex);

  if(pageNumber===PDFViewerApplication.page){
    PDFViewerApplication.toolbar.updateLoadingIndicatorState(false);
  }

  if(!pageView){
    return;
  }

  if(PDFViewerApplication.pdfSidebar.isThumbnailViewVisible){
    varthumbnailView=PDFViewerApplication.pdfThumbnailViewer.getThumbnail(pageIndex);
    thumbnailView.setImage(pageView);
  }

  if(typeofStats!=='undefined'&&Stats.enabled&&pageView.stats){
    Stats.add(pageNumber,pageView.stats);
  }

  if(pageView.error){
    PDFViewerApplication.l10n.get('rendering_error',null,'Anerroroccurredwhilerenderingthepage.').then(function(msg){
      PDFViewerApplication.error(msg,pageView.error);
    });
  }
}

functionwebViewerTextLayerRendered(evt){}

functionwebViewerPageMode(evt){
  varmode=evt.mode,
      view;

  switch(mode){
    case'thumbs':
      view=_pdf_sidebar.SidebarView.THUMBS;
      break;

    case'bookmarks':
    case'outline':
      view=_pdf_sidebar.SidebarView.OUTLINE;
      break;

    case'attachments':
      view=_pdf_sidebar.SidebarView.ATTACHMENTS;
      break;

    case'none':
      view=_pdf_sidebar.SidebarView.NONE;
      break;

    default:
      console.error('Invalid"pagemode"hashparameter:'+mode);
      return;
  }

  PDFViewerApplication.pdfSidebar.switchView(view,true);
}

functionwebViewerNamedAction(evt){
  varaction=evt.action;

  switch(action){
    case'GoToPage':
      PDFViewerApplication.appConfig.toolbar.pageNumber.select();
      break;

    case'Find':
      if(!PDFViewerApplication.supportsIntegratedFind){
        PDFViewerApplication.findBar.toggle();
      }

      break;
  }
}

functionwebViewerPresentationModeChanged(evt){
  varactive=evt.active,
      switchInProgress=evt.switchInProgress;
  PDFViewerApplication.pdfViewer.presentationModeState=switchInProgress?_ui_utils.PresentationModeState.CHANGING:active?_ui_utils.PresentationModeState.FULLSCREEN:_ui_utils.PresentationModeState.NORMAL;
}

functionwebViewerSidebarViewChanged(evt){
  PDFViewerApplication.pdfRenderingQueue.isThumbnailViewEnabled=PDFViewerApplication.pdfSidebar.isThumbnailViewVisible;
  varstore=PDFViewerApplication.store;

  if(store&&PDFViewerApplication.isInitialViewSet){
    store.set('sidebarView',evt.view)["catch"](function(){});
  }
}

functionwebViewerUpdateViewarea(evt){
  varlocation=evt.location,
      store=PDFViewerApplication.store;

  if(store&&PDFViewerApplication.isInitialViewSet){
    store.setMultiple({
      'page':location.pageNumber,
      'zoom':location.scale,
      'scrollLeft':location.left,
      'scrollTop':location.top,
      'rotation':location.rotation
    })["catch"](function(){});
  }

  varhref=PDFViewerApplication.pdfLinkService.getAnchorUrl(location.pdfOpenParams);
  PDFViewerApplication.appConfig.toolbar.viewBookmark.href=href;
  PDFViewerApplication.appConfig.secondaryToolbar.viewBookmarkButton.href=href;
  varcurrentPage=PDFViewerApplication.pdfViewer.getPageView(PDFViewerApplication.page-1);
  varloading=currentPage.renderingState!==_pdf_rendering_queue.RenderingStates.FINISHED;
  PDFViewerApplication.toolbar.updateLoadingIndicatorState(loading);
}

functionwebViewerScrollModeChanged(evt){
  varstore=PDFViewerApplication.store;

  if(store&&PDFViewerApplication.isInitialViewSet){
    store.set('scrollMode',evt.mode)["catch"](function(){});
  }
}

functionwebViewerSpreadModeChanged(evt){
  varstore=PDFViewerApplication.store;

  if(store&&PDFViewerApplication.isInitialViewSet){
    store.set('spreadMode',evt.mode)["catch"](function(){});
  }
}

functionwebViewerResize(){
  varpdfDocument=PDFViewerApplication.pdfDocument,
      pdfViewer=PDFViewerApplication.pdfViewer;

  if(!pdfDocument){
    return;
  }

  varcurrentScaleValue=pdfViewer.currentScaleValue;

  if(currentScaleValue==='auto'||currentScaleValue==='page-fit'||currentScaleValue==='page-width'){
    pdfViewer.currentScaleValue=currentScaleValue;
  }

  pdfViewer.update();
}

functionwebViewerHashchange(evt){
  varhash=evt.hash;

  if(!hash){
    return;
  }

  if(!PDFViewerApplication.isInitialViewSet){
    PDFViewerApplication.initialBookmark=hash;
  }elseif(!PDFViewerApplication.pdfHistory.popStateInProgress){
    PDFViewerApplication.pdfLinkService.setHash(hash);
  }
}

varwebViewerFileInputChange;
{
  webViewerFileInputChange=functionwebViewerFileInputChange(evt){
    if(PDFViewerApplication.pdfViewer&&PDFViewerApplication.pdfViewer.isInPresentationMode){
      return;
    }

    varfile=evt.fileInput.files[0];

    if(_pdfjsLib.URL.createObjectURL&&!_app_options.AppOptions.get('disableCreateObjectURL')){
      varurl=_pdfjsLib.URL.createObjectURL(file);

      if(file.name){
        url={
          url:url,
          originalUrl:file.name
        };
      }

      PDFViewerApplication.open(url);
    }else{
      PDFViewerApplication.setTitleUsingUrl(file.name);
      varfileReader=newFileReader();

      fileReader.onload=functionwebViewerChangeFileReaderOnload(evt){
        varbuffer=evt.target.result;
        PDFViewerApplication.open(newUint8Array(buffer));
      };

      fileReader.readAsArrayBuffer(file);
    }

    varappConfig=PDFViewerApplication.appConfig;
    appConfig.toolbar.viewBookmark.setAttribute('hidden','true');
    appConfig.secondaryToolbar.viewBookmarkButton.setAttribute('hidden','true');
    appConfig.toolbar.download.setAttribute('hidden','true');
    appConfig.secondaryToolbar.downloadButton.setAttribute('hidden','true');
  };
}

functionwebViewerPresentationMode(){
  PDFViewerApplication.requestPresentationMode();
}

functionwebViewerOpenFile(){
  varopenFileInputName=PDFViewerApplication.appConfig.openFileInputName;
  document.getElementById(openFileInputName).click();
}

functionwebViewerPrint(){
  window.print();
}

functionwebViewerDownload(){
  PDFViewerApplication.download();
}

functionwebViewerFirstPage(){
  if(PDFViewerApplication.pdfDocument){
    PDFViewerApplication.page=1;
  }
}

functionwebViewerLastPage(){
  if(PDFViewerApplication.pdfDocument){
    PDFViewerApplication.page=PDFViewerApplication.pagesCount;
  }
}

functionwebViewerNextPage(){
  PDFViewerApplication.page++;
}

functionwebViewerPreviousPage(){
  PDFViewerApplication.page--;
}

functionwebViewerZoomIn(){
  PDFViewerApplication.zoomIn();
}

functionwebViewerZoomOut(){
  PDFViewerApplication.zoomOut();
}

functionwebViewerZoomReset(evt){
  PDFViewerApplication.zoomReset(evt&&evt.ignoreDuplicate);
}

functionwebViewerPageNumberChanged(evt){
  varpdfViewer=PDFViewerApplication.pdfViewer;

  if(evt.value!==''){
    pdfViewer.currentPageLabel=evt.value;
  }

  if(evt.value!==pdfViewer.currentPageNumber.toString()&&evt.value!==pdfViewer.currentPageLabel){
    PDFViewerApplication.toolbar.setPageNumber(pdfViewer.currentPageNumber,pdfViewer.currentPageLabel);
  }
}

functionwebViewerScaleChanged(evt){
  PDFViewerApplication.pdfViewer.currentScaleValue=evt.value;
}

functionwebViewerRotateCw(){
  PDFViewerApplication.rotatePages(90);
}

functionwebViewerRotateCcw(){
  PDFViewerApplication.rotatePages(-90);
}

functionwebViewerSwitchScrollMode(evt){
  PDFViewerApplication.pdfViewer.scrollMode=evt.mode;
}

functionwebViewerSwitchSpreadMode(evt){
  PDFViewerApplication.pdfViewer.spreadMode=evt.mode;
}

functionwebViewerDocumentProperties(){
  PDFViewerApplication.pdfDocumentProperties.open();
}

functionwebViewerFind(evt){
  PDFViewerApplication.findController.executeCommand('find'+evt.type,{
    query:evt.query,
    phraseSearch:evt.phraseSearch,
    caseSensitive:evt.caseSensitive,
    entireWord:evt.entireWord,
    highlightAll:evt.highlightAll,
    findPrevious:evt.findPrevious
  });
}

functionwebViewerFindFromUrlHash(evt){
  PDFViewerApplication.findController.executeCommand('find',{
    query:evt.query,
    phraseSearch:evt.phraseSearch,
    caseSensitive:false,
    entireWord:false,
    highlightAll:true,
    findPrevious:false
  });
}

functionwebViewerUpdateFindMatchesCount(_ref9){
  varmatchesCount=_ref9.matchesCount;

  if(PDFViewerApplication.supportsIntegratedFind){
    PDFViewerApplication.externalServices.updateFindMatchesCount(matchesCount);
  }else{
    PDFViewerApplication.findBar.updateResultsCount(matchesCount);
  }
}

functionwebViewerUpdateFindControlState(_ref10){
  varstate=_ref10.state,
      previous=_ref10.previous,
      matchesCount=_ref10.matchesCount;

  if(PDFViewerApplication.supportsIntegratedFind){
    PDFViewerApplication.externalServices.updateFindControlState({
      result:state,
      findPrevious:previous,
      matchesCount:matchesCount
    });
  }else{
    PDFViewerApplication.findBar.updateUIState(state,previous,matchesCount);
  }
}

functionwebViewerScaleChanging(evt){
  PDFViewerApplication.toolbar.setPageScale(evt.presetValue,evt.scale);
  PDFViewerApplication.pdfViewer.update();
}

functionwebViewerRotationChanging(evt){
  PDFViewerApplication.pdfThumbnailViewer.pagesRotation=evt.pagesRotation;
  PDFViewerApplication.forceRendering();
  PDFViewerApplication.pdfViewer.currentPageNumber=evt.pageNumber;
}

functionwebViewerPageChanging(evt){
  varpage=evt.pageNumber;
  PDFViewerApplication.toolbar.setPageNumber(page,evt.pageLabel||null);
  PDFViewerApplication.secondaryToolbar.setPageNumber(page);

  if(PDFViewerApplication.pdfSidebar.isThumbnailViewVisible){
    PDFViewerApplication.pdfThumbnailViewer.scrollThumbnailIntoView(page);
  }

  if(typeofStats!=='undefined'&&Stats.enabled){
    varpageView=PDFViewerApplication.pdfViewer.getPageView(page-1);

    if(pageView&&pageView.stats){
      Stats.add(page,pageView.stats);
    }
  }
}

functionwebViewerVisibilityChange(evt){
  if(document.visibilityState==='visible'){
    setZoomDisabledTimeout();
  }
}

varzoomDisabledTimeout=null;

functionsetZoomDisabledTimeout(){
  if(zoomDisabledTimeout){
    clearTimeout(zoomDisabledTimeout);
  }

  zoomDisabledTimeout=setTimeout(function(){
    zoomDisabledTimeout=null;
  },WHEEL_ZOOM_DISABLED_TIMEOUT);
}

functionwebViewerWheel(evt){
  varpdfViewer=PDFViewerApplication.pdfViewer;

  if(pdfViewer.isInPresentationMode){
    return;
  }

  if(evt.ctrlKey||evt.metaKey){
    varsupport=PDFViewerApplication.supportedMouseWheelZoomModifierKeys;

    if(evt.ctrlKey&&!support.ctrlKey||evt.metaKey&&!support.metaKey){
      return;
    }

    evt.preventDefault();

    if(zoomDisabledTimeout||document.visibilityState==='hidden'){
      return;
    }

    varpreviousScale=pdfViewer.currentScale;
    vardelta=(0,_ui_utils.normalizeWheelEventDelta)(evt);
    varMOUSE_WHEEL_DELTA_PER_PAGE_SCALE=3.0;
    varticks=delta*MOUSE_WHEEL_DELTA_PER_PAGE_SCALE;

    if(ticks<0){
      PDFViewerApplication.zoomOut(-ticks);
    }else{
      PDFViewerApplication.zoomIn(ticks);
    }

    varcurrentScale=pdfViewer.currentScale;

    if(previousScale!==currentScale){
      varscaleCorrectionFactor=currentScale/previousScale-1;
      varrect=pdfViewer.container.getBoundingClientRect();
      vardx=evt.clientX-rect.left;
      vardy=evt.clientY-rect.top;
      pdfViewer.container.scrollLeft+=dx*scaleCorrectionFactor;
      pdfViewer.container.scrollTop+=dy*scaleCorrectionFactor;
    }
  }else{
    setZoomDisabledTimeout();
  }
}

functionwebViewerClick(evt){
  if(!PDFViewerApplication.secondaryToolbar.isOpen){
    return;
  }

  varappConfig=PDFViewerApplication.appConfig;

  if(PDFViewerApplication.pdfViewer.containsElement(evt.target)||appConfig.toolbar.container.contains(evt.target)&&evt.target!==appConfig.secondaryToolbar.toggleButton){
    PDFViewerApplication.secondaryToolbar.close();
  }
}

functionwebViewerKeyDown(evt){
  if(PDFViewerApplication.overlayManager.active){
    return;
  }

  varhandled=false,
      ensureViewerFocused=false;
  varcmd=(evt.ctrlKey?1:0)|(evt.altKey?2:0)|(evt.shiftKey?4:0)|(evt.metaKey?8:0);
  varpdfViewer=PDFViewerApplication.pdfViewer;
  varisViewerInPresentationMode=pdfViewer&&pdfViewer.isInPresentationMode;

  if(cmd===1||cmd===8||cmd===5||cmd===12){
    switch(evt.keyCode){
      case70:
        if(!PDFViewerApplication.supportsIntegratedFind){
          PDFViewerApplication.findBar.open();
          handled=true;
        }

        break;

      case71:
        if(!PDFViewerApplication.supportsIntegratedFind){
          varfindState=PDFViewerApplication.findController.state;

          if(findState){
            PDFViewerApplication.findController.executeCommand('findagain',{
              query:findState.query,
              phraseSearch:findState.phraseSearch,
              caseSensitive:findState.caseSensitive,
              entireWord:findState.entireWord,
              highlightAll:findState.highlightAll,
              findPrevious:cmd===5||cmd===12
            });
          }

          handled=true;
        }

        break;

      case61:
      case107:
      case187:
      case171:
        if(!isViewerInPresentationMode){
          PDFViewerApplication.zoomIn();
        }

        handled=true;
        break;

      case173:
      case109:
      case189:
        if(!isViewerInPresentationMode){
          PDFViewerApplication.zoomOut();
        }

        handled=true;
        break;

      case48:
      case96:
        if(!isViewerInPresentationMode){
          setTimeout(function(){
            PDFViewerApplication.zoomReset();
          });
          handled=false;
        }

        break;

      case38:
        if(isViewerInPresentationMode||PDFViewerApplication.page>1){
          PDFViewerApplication.page=1;
          handled=true;
          ensureViewerFocused=true;
        }

        break;

      case40:
        if(isViewerInPresentationMode||PDFViewerApplication.page<PDFViewerApplication.pagesCount){
          PDFViewerApplication.page=PDFViewerApplication.pagesCount;
          handled=true;
          ensureViewerFocused=true;
        }

        break;
    }
  }

  if(cmd===1||cmd===8){
    switch(evt.keyCode){
      case83:
        PDFViewerApplication.download();
        handled=true;
        break;
    }
  }

  if(cmd===3||cmd===10){
    switch(evt.keyCode){
      case80:
        PDFViewerApplication.requestPresentationMode();
        handled=true;
        break;

      case71:
        PDFViewerApplication.appConfig.toolbar.pageNumber.select();
        handled=true;
        break;
    }
  }

  if(handled){
    if(ensureViewerFocused&&!isViewerInPresentationMode){
      pdfViewer.focus();
    }

    evt.preventDefault();
    return;
  }

  varcurElement=document.activeElement||document.querySelector(':focus');
  varcurElementTagName=curElement&&curElement.tagName.toUpperCase();

  if(curElementTagName==='INPUT'||curElementTagName==='TEXTAREA'||curElementTagName==='SELECT'){
    if(evt.keyCode!==27){
      return;
    }
  }

  if(cmd===0){
    varturnPage=0,
        turnOnlyIfPageFit=false;

    switch(evt.keyCode){
      case38:
      case33:
        if(pdfViewer.isVerticalScrollbarEnabled){
          turnOnlyIfPageFit=true;
        }

        turnPage=-1;
        break;

      case8:
        if(!isViewerInPresentationMode){
          turnOnlyIfPageFit=true;
        }

        turnPage=-1;
        break;

      case37:
        if(pdfViewer.isHorizontalScrollbarEnabled){
          turnOnlyIfPageFit=true;
        }

      case75:
      case80:
        turnPage=-1;
        break;

      case27:
        if(PDFViewerApplication.secondaryToolbar.isOpen){
          PDFViewerApplication.secondaryToolbar.close();
          handled=true;
        }

        if(!PDFViewerApplication.supportsIntegratedFind&&PDFViewerApplication.findBar.opened){
          PDFViewerApplication.findBar.close();
          handled=true;
        }

        break;

      case40:
      case34:
        if(pdfViewer.isVerticalScrollbarEnabled){
          turnOnlyIfPageFit=true;
        }

        turnPage=1;
        break;

      case13:
      case32:
        if(!isViewerInPresentationMode){
          turnOnlyIfPageFit=true;
        }

        turnPage=1;
        break;

      case39:
        if(pdfViewer.isHorizontalScrollbarEnabled){
          turnOnlyIfPageFit=true;
        }

      case74:
      case78:
        turnPage=1;
        break;

      case36:
        if(isViewerInPresentationMode||PDFViewerApplication.page>1){
          PDFViewerApplication.page=1;
          handled=true;
          ensureViewerFocused=true;
        }

        break;

      case35:
        if(isViewerInPresentationMode||PDFViewerApplication.page<PDFViewerApplication.pagesCount){
          PDFViewerApplication.page=PDFViewerApplication.pagesCount;
          handled=true;
          ensureViewerFocused=true;
        }

        break;

      case83:
        PDFViewerApplication.pdfCursorTools.switchTool(_pdf_cursor_tools.CursorTool.SELECT);
        break;

      case72:
        PDFViewerApplication.pdfCursorTools.switchTool(_pdf_cursor_tools.CursorTool.HAND);
        break;

      case82:
        PDFViewerApplication.rotatePages(90);
        break;

      case115:
        PDFViewerApplication.pdfSidebar.toggle();
        break;
    }

    if(turnPage!==0&&(!turnOnlyIfPageFit||pdfViewer.currentScaleValue==='page-fit')){
      if(turnPage>0){
        if(PDFViewerApplication.page<PDFViewerApplication.pagesCount){
          PDFViewerApplication.page++;
        }
      }else{
        if(PDFViewerApplication.page>1){
          PDFViewerApplication.page--;
        }
      }

      handled=true;
    }
  }

  if(cmd===4){
    switch(evt.keyCode){
      case13:
      case32:
        if(!isViewerInPresentationMode&&pdfViewer.currentScaleValue!=='page-fit'){
          break;
        }

        if(PDFViewerApplication.page>1){
          PDFViewerApplication.page--;
        }

        handled=true;
        break;

      case82:
        PDFViewerApplication.rotatePages(-90);
        break;
    }
  }

  if(!handled&&!isViewerInPresentationMode){
    if(evt.keyCode>=33&&evt.keyCode<=40||evt.keyCode===32&&curElementTagName!=='BUTTON'){
      ensureViewerFocused=true;
    }
  }

  if(ensureViewerFocused&&!pdfViewer.containsElement(curElement)){
    pdfViewer.focus();
  }

  if(handled){
    evt.preventDefault();
  }
}

functionapiPageLayoutToSpreadMode(layout){
  switch(layout){
    case'SinglePage':
    case'OneColumn':
      return_ui_utils.SpreadMode.NONE;

    case'TwoColumnLeft':
    case'TwoPageLeft':
      return_ui_utils.SpreadMode.ODD;

    case'TwoColumnRight':
    case'TwoPageRight':
      return_ui_utils.SpreadMode.EVEN;
  }

  return_ui_utils.SpreadMode.NONE;
}

functionapiPageModeToSidebarView(mode){
  switch(mode){
    case'UseNone':
      return_pdf_sidebar.SidebarView.NONE;

    case'UseThumbs':
      return_pdf_sidebar.SidebarView.THUMBS;

    case'UseOutlines':
      return_pdf_sidebar.SidebarView.OUTLINE;

    case'UseAttachments':
      return_pdf_sidebar.SidebarView.ATTACHMENTS;

    case'UseOC':
  }

  return_pdf_sidebar.SidebarView.NONE;
}

varPDFPrintServiceFactory={
  instance:{
    supportsPrinting:false,
    createPrintService:functioncreatePrintService(){
      thrownewError('Notimplemented:createPrintService');
    }
  }
};
exports.PDFPrintServiceFactory=PDFPrintServiceFactory;

/***/}),
/*2*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


module.exports=__webpack_require__(3);

/***/}),
/*3*/
/***/(function(module,exports,__webpack_require__){

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
/*WEBPACKVARINJECTION*/}.call(this,__webpack_require__(4)(module)))

/***/}),
/*4*/
/***/(function(module,exports,__webpack_require__){

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
/*5*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.isValidRotation=isValidRotation;
exports.isValidScrollMode=isValidScrollMode;
exports.isValidSpreadMode=isValidSpreadMode;
exports.isPortraitOrientation=isPortraitOrientation;
exports.getGlobalEventBus=getGlobalEventBus;
exports.getPDFFileNameFromURL=getPDFFileNameFromURL;
exports.noContextMenuHandler=noContextMenuHandler;
exports.parseQueryString=parseQueryString;
exports.backtrackBeforeAllVisibleElements=backtrackBeforeAllVisibleElements;
exports.getVisibleElements=getVisibleElements;
exports.roundToDivide=roundToDivide;
exports.getPageSizeInches=getPageSizeInches;
exports.approximateFraction=approximateFraction;
exports.getOutputScale=getOutputScale;
exports.scrollIntoView=scrollIntoView;
exports.watchScroll=watchScroll;
exports.binarySearchFirstItem=binarySearchFirstItem;
exports.normalizeWheelEventDelta=normalizeWheelEventDelta;
exports.waitOnEventOrTimeout=waitOnEventOrTimeout;
exports.moveToEndOfArray=moveToEndOfArray;
exports.WaitOnType=exports.animationStarted=exports.ProgressBar=exports.EventBus=exports.NullL10n=exports.SpreadMode=exports.ScrollMode=exports.TextLayerMode=exports.RendererType=exports.PresentationModeState=exports.VERTICAL_PADDING=exports.SCROLLBAR_PADDING=exports.MAX_AUTO_SCALE=exports.UNKNOWN_SCALE=exports.MAX_SCALE=exports.MIN_SCALE=exports.DEFAULT_SCALE=exports.DEFAULT_SCALE_VALUE=exports.CSS_UNITS=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

varCSS_UNITS=96.0/72.0;
exports.CSS_UNITS=CSS_UNITS;
varDEFAULT_SCALE_VALUE='auto';
exports.DEFAULT_SCALE_VALUE=DEFAULT_SCALE_VALUE;
varDEFAULT_SCALE=1.0;
exports.DEFAULT_SCALE=DEFAULT_SCALE;
varMIN_SCALE=0.10;
exports.MIN_SCALE=MIN_SCALE;
varMAX_SCALE=10.0;
exports.MAX_SCALE=MAX_SCALE;
varUNKNOWN_SCALE=0;
exports.UNKNOWN_SCALE=UNKNOWN_SCALE;
varMAX_AUTO_SCALE=1.25;
exports.MAX_AUTO_SCALE=MAX_AUTO_SCALE;
varSCROLLBAR_PADDING=40;
exports.SCROLLBAR_PADDING=SCROLLBAR_PADDING;
varVERTICAL_PADDING=5;
exports.VERTICAL_PADDING=VERTICAL_PADDING;
varPresentationModeState={
  UNKNOWN:0,
  NORMAL:1,
  CHANGING:2,
  FULLSCREEN:3
};
exports.PresentationModeState=PresentationModeState;
varRendererType={
  CANVAS:'canvas',
  SVG:'svg'
};
exports.RendererType=RendererType;
varTextLayerMode={
  DISABLE:0,
  ENABLE:1,
  ENABLE_ENHANCE:2
};
exports.TextLayerMode=TextLayerMode;
varScrollMode={
  UNKNOWN:-1,
  VERTICAL:0,
  HORIZONTAL:1,
  WRAPPED:2
};
exports.ScrollMode=ScrollMode;
varSpreadMode={
  UNKNOWN:-1,
  NONE:0,
  ODD:1,
  EVEN:2
};
exports.SpreadMode=SpreadMode;

functionformatL10nValue(text,args){
  if(!args){
    returntext;
  }

  returntext.replace(/\{\{\s*(\w+)\s*\}\}/g,function(all,name){
    returnnameinargs?args[name]:'{{'+name+'}}';
  });
}

varNullL10n={
  getLanguage:function(){
    var_getLanguage=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee(){
      return_regenerator["default"].wrap(function_callee$(_context){
        while(1){
          switch(_context.prev=_context.next){
            case0:
              return_context.abrupt("return",'en-us');

            case1:
            case"end":
              return_context.stop();
          }
        }
      },_callee);
    }));

    functiongetLanguage(){
      return_getLanguage.apply(this,arguments);
    }

    returngetLanguage;
  }(),
  getDirection:function(){
    var_getDirection=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee2(){
      return_regenerator["default"].wrap(function_callee2$(_context2){
        while(1){
          switch(_context2.prev=_context2.next){
            case0:
              return_context2.abrupt("return",'ltr');

            case1:
            case"end":
              return_context2.stop();
          }
        }
      },_callee2);
    }));

    functiongetDirection(){
      return_getDirection.apply(this,arguments);
    }

    returngetDirection;
  }(),
  get:function(){
    var_get=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee3(property,args,fallback){
      return_regenerator["default"].wrap(function_callee3$(_context3){
        while(1){
          switch(_context3.prev=_context3.next){
            case0:
              return_context3.abrupt("return",formatL10nValue(fallback,args));

            case1:
            case"end":
              return_context3.stop();
          }
        }
      },_callee3);
    }));

    functionget(_x,_x2,_x3){
      return_get.apply(this,arguments);
    }

    returnget;
  }(),
  translate:function(){
    var_translate=_asyncToGenerator(
    /*#__PURE__*/
    _regenerator["default"].mark(function_callee4(element){
      return_regenerator["default"].wrap(function_callee4$(_context4){
        while(1){
          switch(_context4.prev=_context4.next){
            case0:
            case"end":
              return_context4.stop();
          }
        }
      },_callee4);
    }));

    functiontranslate(_x4){
      return_translate.apply(this,arguments);
    }

    returntranslate;
  }()
};
exports.NullL10n=NullL10n;

functiongetOutputScale(ctx){
  vardevicePixelRatio=window.devicePixelRatio||1;
  varbackingStoreRatio=ctx.webkitBackingStorePixelRatio||ctx.mozBackingStorePixelRatio||ctx.msBackingStorePixelRatio||ctx.oBackingStorePixelRatio||ctx.backingStorePixelRatio||1;
  varpixelRatio=devicePixelRatio/backingStoreRatio;
  return{
    sx:pixelRatio,
    sy:pixelRatio,
    scaled:pixelRatio!==1
  };
}

functionscrollIntoView(element,spot){
  varskipOverflowHiddenElements=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;
  varparent=element.offsetParent;

  if(!parent){
    console.error('offsetParentisnotset--cannotscroll');
    return;
  }

  varoffsetY=element.offsetTop+element.clientTop;
  varoffsetX=element.offsetLeft+element.clientLeft;

  while(parent.clientHeight===parent.scrollHeight&&parent.clientWidth===parent.scrollWidth||skipOverflowHiddenElements&&getComputedStyle(parent).overflow==='hidden'){
    if(parent.dataset._scaleY){
      offsetY/=parent.dataset._scaleY;
      offsetX/=parent.dataset._scaleX;
    }

    offsetY+=parent.offsetTop;
    offsetX+=parent.offsetLeft;
    parent=parent.offsetParent;

    if(!parent){
      return;
    }
  }

  if(spot){
    if(spot.top!==undefined){
      offsetY+=spot.top;
    }

    if(spot.left!==undefined){
      offsetX+=spot.left;
      parent.scrollLeft=offsetX;
    }
  }

  parent.scrollTop=offsetY;
}

functionwatchScroll(viewAreaElement,callback){
  vardebounceScroll=functiondebounceScroll(evt){
    if(rAF){
      return;
    }

    rAF=window.requestAnimationFrame(functionviewAreaElementScrolled(){
      rAF=null;
      varcurrentX=viewAreaElement.scrollLeft;
      varlastX=state.lastX;

      if(currentX!==lastX){
        state.right=currentX>lastX;
      }

      state.lastX=currentX;
      varcurrentY=viewAreaElement.scrollTop;
      varlastY=state.lastY;

      if(currentY!==lastY){
        state.down=currentY>lastY;
      }

      state.lastY=currentY;
      callback(state);
    });
  };

  varstate={
    right:true,
    down:true,
    lastX:viewAreaElement.scrollLeft,
    lastY:viewAreaElement.scrollTop,
    _eventHandler:debounceScroll
  };
  varrAF=null;
  viewAreaElement.addEventListener('scroll',debounceScroll,true);
  returnstate;
}

functionparseQueryString(query){
  varparts=query.split('&');
  varparams=Object.create(null);

  for(vari=0,ii=parts.length;i<ii;++i){
    varparam=parts[i].split('=');
    varkey=param[0].toLowerCase();
    varvalue=param.length>1?param[1]:null;
    params[decodeURIComponent(key)]=decodeURIComponent(value);
  }

  returnparams;
}

functionbinarySearchFirstItem(items,condition){
  varminIndex=0;
  varmaxIndex=items.length-1;

  if(items.length===0||!condition(items[maxIndex])){
    returnitems.length;
  }

  if(condition(items[minIndex])){
    returnminIndex;
  }

  while(minIndex<maxIndex){
    varcurrentIndex=minIndex+maxIndex>>1;
    varcurrentItem=items[currentIndex];

    if(condition(currentItem)){
      maxIndex=currentIndex;
    }else{
      minIndex=currentIndex+1;
    }
  }

  returnminIndex;
}

functionapproximateFraction(x){
  if(Math.floor(x)===x){
    return[x,1];
  }

  varxinv=1/x;
  varlimit=8;

  if(xinv>limit){
    return[1,limit];
  }elseif(Math.floor(xinv)===xinv){
    return[1,xinv];
  }

  varx_=x>1?xinv:x;
  vara=0,
      b=1,
      c=1,
      d=1;

  while(true){
    varp=a+c,
        q=b+d;

    if(q>limit){
      break;
    }

    if(x_<=p/q){
      c=p;
      d=q;
    }else{
      a=p;
      b=q;
    }
  }

  varresult;

  if(x_-a/b<c/d-x_){
    result=x_===x?[a,b]:[b,a];
  }else{
    result=x_===x?[c,d]:[d,c];
  }

  returnresult;
}

functionroundToDivide(x,div){
  varr=x%div;
  returnr===0?x:Math.round(x-r+div);
}

functiongetPageSizeInches(_ref){
  varview=_ref.view,
      userUnit=_ref.userUnit,
      rotate=_ref.rotate;

  var_view=_slicedToArray(view,4),
      x1=_view[0],
      y1=_view[1],
      x2=_view[2],
      y2=_view[3];

  varchangeOrientation=rotate%180!==0;
  varwidth=(x2-x1)/72*userUnit;
  varheight=(y2-y1)/72*userUnit;
  return{
    width:changeOrientation?height:width,
    height:changeOrientation?width:height
  };
}

functionbacktrackBeforeAllVisibleElements(index,views,top){
  if(index<2){
    returnindex;
  }

  varelt=views[index].div;
  varpageTop=elt.offsetTop+elt.clientTop;

  if(pageTop>=top){
    elt=views[index-1].div;
    pageTop=elt.offsetTop+elt.clientTop;
  }

  for(vari=index-2;i>=0;--i){
    elt=views[i].div;

    if(elt.offsetTop+elt.clientTop+elt.clientHeight<=pageTop){
      break;
    }

    index=i;
  }

  returnindex;
}

functiongetVisibleElements(scrollEl,views){
  varsortByVisibility=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;
  varhorizontal=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;
  vartop=scrollEl.scrollTop,
      bottom=top+scrollEl.clientHeight;
  varleft=scrollEl.scrollLeft,
      right=left+scrollEl.clientWidth;

  functionisElementBottomAfterViewTop(view){
    varelement=view.div;
    varelementBottom=element.offsetTop+element.clientTop+element.clientHeight;
    returnelementBottom>top;
  }

  functionisElementRightAfterViewLeft(view){
    varelement=view.div;
    varelementRight=element.offsetLeft+element.clientLeft+element.clientWidth;
    returnelementRight>left;
  }

  varvisible=[],
      numViews=views.length;
  varfirstVisibleElementInd=numViews===0?0:binarySearchFirstItem(views,horizontal?isElementRightAfterViewLeft:isElementBottomAfterViewTop);

  if(firstVisibleElementInd>0&&firstVisibleElementInd<numViews&&!horizontal){
    firstVisibleElementInd=backtrackBeforeAllVisibleElements(firstVisibleElementInd,views,top);
  }

  varlastEdge=horizontal?right:-1;

  for(vari=firstVisibleElementInd;i<numViews;i++){
    varview=views[i],
        element=view.div;
    varcurrentWidth=element.offsetLeft+element.clientLeft;
    varcurrentHeight=element.offsetTop+element.clientTop;
    varviewWidth=element.clientWidth,
        viewHeight=element.clientHeight;
    varviewRight=currentWidth+viewWidth;
    varviewBottom=currentHeight+viewHeight;

    if(lastEdge===-1){
      if(viewBottom>=bottom){
        lastEdge=viewBottom;
      }
    }elseif((horizontal?currentWidth:currentHeight)>lastEdge){
      break;
    }

    if(viewBottom<=top||currentHeight>=bottom||viewRight<=left||currentWidth>=right){
      continue;
    }

    varhiddenHeight=Math.max(0,top-currentHeight)+Math.max(0,viewBottom-bottom);
    varhiddenWidth=Math.max(0,left-currentWidth)+Math.max(0,viewRight-right);
    varpercent=(viewHeight-hiddenHeight)*(viewWidth-hiddenWidth)*100/viewHeight/viewWidth|0;
    visible.push({
      id:view.id,
      x:currentWidth,
      y:currentHeight,
      view:view,
      percent:percent
    });
  }

  varfirst=visible[0],
      last=visible[visible.length-1];

  if(sortByVisibility){
    visible.sort(function(a,b){
      varpc=a.percent-b.percent;

      if(Math.abs(pc)>0.001){
        return-pc;
      }

      returna.id-b.id;
    });
  }

  return{
    first:first,
    last:last,
    views:visible
  };
}

functionnoContextMenuHandler(evt){
  evt.preventDefault();
}

functionisDataSchema(url){
  vari=0,
      ii=url.length;

  while(i<ii&&url[i].trim()===''){
    i++;
  }

  returnurl.substring(i,i+5).toLowerCase()==='data:';
}

functiongetPDFFileNameFromURL(url){
  vardefaultFilename=arguments.length>1&&arguments[1]!==undefined?arguments[1]:'document.pdf';

  if(typeofurl!=='string'){
    returndefaultFilename;
  }

  if(isDataSchema(url)){
    console.warn('getPDFFileNameFromURL:'+'ignoring"data:"URLforperformancereasons.');
    returndefaultFilename;
  }

  varreURI=/^(?:(?:[^:]+:)?\/\/[^\/]+)?([^?#]*)(\?[^#]*)?(#.*)?$/;
  varreFilename=/[^\/?#=]+\.pdf\b(?!.*\.pdf\b)/i;
  varsplitURI=reURI.exec(url);
  varsuggestedFilename=reFilename.exec(splitURI[1])||reFilename.exec(splitURI[2])||reFilename.exec(splitURI[3]);

  if(suggestedFilename){
    suggestedFilename=suggestedFilename[0];

    if(suggestedFilename.includes('%')){
      try{
        suggestedFilename=reFilename.exec(decodeURIComponent(suggestedFilename))[0];
      }catch(ex){}
    }
  }

  returnsuggestedFilename||defaultFilename;
}

functionnormalizeWheelEventDelta(evt){
  vardelta=Math.sqrt(evt.deltaX*evt.deltaX+evt.deltaY*evt.deltaY);
  varangle=Math.atan2(evt.deltaY,evt.deltaX);

  if(-0.25*Math.PI<angle&&angle<0.75*Math.PI){
    delta=-delta;
  }

  varMOUSE_DOM_DELTA_PIXEL_MODE=0;
  varMOUSE_DOM_DELTA_LINE_MODE=1;
  varMOUSE_PIXELS_PER_LINE=30;
  varMOUSE_LINES_PER_PAGE=30;

  if(evt.deltaMode===MOUSE_DOM_DELTA_PIXEL_MODE){
    delta/=MOUSE_PIXELS_PER_LINE*MOUSE_LINES_PER_PAGE;
  }elseif(evt.deltaMode===MOUSE_DOM_DELTA_LINE_MODE){
    delta/=MOUSE_LINES_PER_PAGE;
  }

  returndelta;
}

functionisValidRotation(angle){
  returnNumber.isInteger(angle)&&angle%90===0;
}

functionisValidScrollMode(mode){
  returnNumber.isInteger(mode)&&Object.values(ScrollMode).includes(mode)&&mode!==ScrollMode.UNKNOWN;
}

functionisValidSpreadMode(mode){
  returnNumber.isInteger(mode)&&Object.values(SpreadMode).includes(mode)&&mode!==SpreadMode.UNKNOWN;
}

functionisPortraitOrientation(size){
  returnsize.width<=size.height;
}

varWaitOnType={
  EVENT:'event',
  TIMEOUT:'timeout'
};
exports.WaitOnType=WaitOnType;

functionwaitOnEventOrTimeout(_ref2){
  vartarget=_ref2.target,
      name=_ref2.name,
      _ref2$delay=_ref2.delay,
      delay=_ref2$delay===void0?0:_ref2$delay;
  returnnewPromise(function(resolve,reject){
    if(_typeof(target)!=='object'||!(name&&typeofname==='string')||!(Number.isInteger(delay)&&delay>=0)){
      thrownewError('waitOnEventOrTimeout-invalidparameters.');
    }

    functionhandler(type){
      if(targetinstanceofEventBus){
        target.off(name,eventHandler);
      }else{
        target.removeEventListener(name,eventHandler);
      }

      if(timeout){
        clearTimeout(timeout);
      }

      resolve(type);
    }

    vareventHandler=handler.bind(null,WaitOnType.EVENT);

    if(targetinstanceofEventBus){
      target.on(name,eventHandler);
    }else{
      target.addEventListener(name,eventHandler);
    }

    vartimeoutHandler=handler.bind(null,WaitOnType.TIMEOUT);
    vartimeout=setTimeout(timeoutHandler,delay);
  });
}

varanimationStarted=newPromise(function(resolve){
  window.requestAnimationFrame(resolve);
});
exports.animationStarted=animationStarted;

varEventBus=
/*#__PURE__*/
function(){
  functionEventBus(){
    var_ref3=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
        _ref3$dispatchToDOM=_ref3.dispatchToDOM,
        dispatchToDOM=_ref3$dispatchToDOM===void0?false:_ref3$dispatchToDOM;

    _classCallCheck(this,EventBus);

    this._listeners=Object.create(null);
    this._dispatchToDOM=dispatchToDOM===true;
  }

  _createClass(EventBus,[{
    key:"on",
    value:functionon(eventName,listener){
      vareventListeners=this._listeners[eventName];

      if(!eventListeners){
        eventListeners=[];
        this._listeners[eventName]=eventListeners;
      }

      eventListeners.push(listener);
    }
  },{
    key:"off",
    value:functionoff(eventName,listener){
      vareventListeners=this._listeners[eventName];
      vari;

      if(!eventListeners||(i=eventListeners.indexOf(listener))<0){
        return;
      }

      eventListeners.splice(i,1);
    }
  },{
    key:"dispatch",
    value:functiondispatch(eventName){
      vareventListeners=this._listeners[eventName];

      if(!eventListeners||eventListeners.length===0){
        if(this._dispatchToDOM){
          var_args5=Array.prototype.slice.call(arguments,1);

          this._dispatchDOMEvent(eventName,_args5);
        }

        return;
      }

      varargs=Array.prototype.slice.call(arguments,1);
      eventListeners.slice(0).forEach(function(listener){
        listener.apply(null,args);
      });

      if(this._dispatchToDOM){
        this._dispatchDOMEvent(eventName,args);
      }
    }
  },{
    key:"_dispatchDOMEvent",
    value:function_dispatchDOMEvent(eventName){
      varargs=arguments.length>1&&arguments[1]!==undefined?arguments[1]:null;
      vardetails=Object.create(null);

      if(args&&args.length>0){
        varobj=args[0];

        for(varkeyinobj){
          varvalue=obj[key];

          if(key==='source'){
            if(value===window||value===document){
              return;
            }

            continue;
          }

          details[key]=value;
        }
      }

      varevent=document.createEvent('CustomEvent');
      event.initCustomEvent(eventName,true,true,details);
      document.dispatchEvent(event);
    }
  }]);

  returnEventBus;
}();

exports.EventBus=EventBus;
varglobalEventBus=null;

functiongetGlobalEventBus(){
  vardispatchToDOM=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

  if(!globalEventBus){
    globalEventBus=newEventBus({
      dispatchToDOM:dispatchToDOM
    });
  }

  returnglobalEventBus;
}

functionclamp(v,min,max){
  returnMath.min(Math.max(v,min),max);
}

varProgressBar=
/*#__PURE__*/
function(){
  functionProgressBar(id){
    var_ref4=arguments.length>1&&arguments[1]!==undefined?arguments[1]:{},
        height=_ref4.height,
        width=_ref4.width,
        units=_ref4.units;

    _classCallCheck(this,ProgressBar);

    this.visible=true;
    this.div=document.querySelector(id+'.progress');
    this.bar=this.div.parentNode;
    this.height=height||100;
    this.width=width||100;
    this.units=units||'%';
    this.div.style.height=this.height+this.units;
    this.percent=0;
  }

  _createClass(ProgressBar,[{
    key:"_updateBar",
    value:function_updateBar(){
      if(this._indeterminate){
        this.div.classList.add('indeterminate');
        this.div.style.width=this.width+this.units;
        return;
      }

      this.div.classList.remove('indeterminate');
      varprogressSize=this.width*this._percent/100;
      this.div.style.width=progressSize+this.units;
    }
  },{
    key:"setWidth",
    value:functionsetWidth(viewer){
      if(!viewer){
        return;
      }

      varcontainer=viewer.parentNode;
      varscrollbarWidth=container.offsetWidth-viewer.offsetWidth;

      if(scrollbarWidth>0){
        this.bar.setAttribute('style','width:calc(100%-'+scrollbarWidth+'px);');
      }
    }
  },{
    key:"hide",
    value:functionhide(){
      if(!this.visible){
        return;
      }

      this.visible=false;
      this.bar.classList.add('hidden');
      document.body.classList.remove('loadingInProgress');
    }
  },{
    key:"show",
    value:functionshow(){
      if(this.visible){
        return;
      }

      this.visible=true;
      document.body.classList.add('loadingInProgress');
      this.bar.classList.remove('hidden');
    }
  },{
    key:"percent",
    get:functionget(){
      returnthis._percent;
    },
    set:functionset(val){
      this._indeterminate=isNaN(val);
      this._percent=clamp(val,0,100);

      this._updateBar();
    }
  }]);

  returnProgressBar;
}();

exports.ProgressBar=ProgressBar;

functionmoveToEndOfArray(arr,condition){
  varmoved=[],
      len=arr.length;
  varwrite=0;

  for(varread=0;read<len;++read){
    if(condition(arr[read])){
      moved.push(arr[read]);
    }else{
      arr[write]=arr[read];
      ++write;
    }
  }

  for(var_read=0;write<len;++_read,++write){
    arr[write]=moved[_read];
  }
}

/***/}),
/*6*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.OptionKind=exports.AppOptions=void0;

var_pdfjsLib=__webpack_require__(7);

var_viewer_compatibility=__webpack_require__(8);

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varOptionKind={
  VIEWER:0x02,
  API:0x04,
  WORKER:0x08,
  PREFERENCE:0x80
};
exports.OptionKind=OptionKind;
vardefaultOptions={
  cursorToolOnLoad:{
    value:0,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  defaultUrl:{
    value:'compressed.tracemonkey-pldi-09.pdf',
    kind:OptionKind.VIEWER
  },
  defaultZoomValue:{
    value:'',
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  disableHistory:{
    value:false,
    kind:OptionKind.VIEWER
  },
  disablePageLabels:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  enablePrintAutoRotate:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  enableWebGL:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  eventBusDispatchToDOM:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  externalLinkRel:{
    value:'noopenernoreferrernofollow',
    kind:OptionKind.VIEWER
  },
  externalLinkTarget:{
    value:0,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  historyUpdateUrl:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  imageResourcesPath:{
    value:'./images/',
    kind:OptionKind.VIEWER
  },
  maxCanvasPixels:{
    value:16777216,
    compatibility:_viewer_compatibility.viewerCompatibilityParams.maxCanvasPixels,
    kind:OptionKind.VIEWER
  },
  pdfBugEnabled:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  renderer:{
    value:'canvas',
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  renderInteractiveForms:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  sidebarViewOnLoad:{
    value:-1,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  scrollModeOnLoad:{
    value:-1,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  spreadModeOnLoad:{
    value:-1,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  textLayerMode:{
    value:1,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  useOnlyCssZoom:{
    value:false,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  viewOnLoad:{
    value:0,
    kind:OptionKind.VIEWER+OptionKind.PREFERENCE
  },
  cMapPacked:{
    value:true,
    kind:OptionKind.API
  },
  cMapUrl:{
    value:'../web/cmaps/',
    kind:OptionKind.API
  },
  disableAutoFetch:{
    value:false,
    kind:OptionKind.API+OptionKind.PREFERENCE
  },
  disableCreateObjectURL:{
    value:false,
    compatibility:_pdfjsLib.apiCompatibilityParams.disableCreateObjectURL,
    kind:OptionKind.API
  },
  disableFontFace:{
    value:false,
    kind:OptionKind.API+OptionKind.PREFERENCE
  },
  disableRange:{
    value:false,
    kind:OptionKind.API+OptionKind.PREFERENCE
  },
  disableStream:{
    value:false,
    kind:OptionKind.API+OptionKind.PREFERENCE
  },
  isEvalSupported:{
    value:true,
    kind:OptionKind.API
  },
  maxImageSize:{
    value:-1,
    kind:OptionKind.API
  },
  pdfBug:{
    value:false,
    kind:OptionKind.API
  },
  postMessageTransfers:{
    value:true,
    kind:OptionKind.API
  },
  verbosity:{
    value:1,
    kind:OptionKind.API
  },
  workerPort:{
    value:null,
    kind:OptionKind.WORKER
  },
  workerSrc:{
    value:'../build/pdf.worker.js',
    kind:OptionKind.WORKER
  }
};
{
  defaultOptions.disablePreferences={
    value:false,
    kind:OptionKind.VIEWER
  };
  defaultOptions.locale={
    value:typeofnavigator!=='undefined'?navigator.language:'en-US',
    kind:OptionKind.VIEWER
  };
  defaultOptions.printResolution={
    value:150,
    kind:OptionKind.VIEWER
  };
}
varuserOptions=Object.create(null);

varAppOptions=
/*#__PURE__*/
function(){
  functionAppOptions(){
    _classCallCheck(this,AppOptions);

    thrownewError('CannotinitializeAppOptions.');
  }

  _createClass(AppOptions,null,[{
    key:"get",
    value:functionget(name){
      varuserOption=userOptions[name];

      if(userOption!==undefined){
        returnuserOption;
      }

      vardefaultOption=defaultOptions[name];

      if(defaultOption!==undefined){
        returndefaultOption.compatibility||defaultOption.value;
      }

      returnundefined;
    }
  },{
    key:"getAll",
    value:functiongetAll(){
      varkind=arguments.length>0&&arguments[0]!==undefined?arguments[0]:null;
      varoptions=Object.create(null);

      for(varnameindefaultOptions){
        vardefaultOption=defaultOptions[name];

        if(kind){
          if((kind&defaultOption.kind)===0){
            continue;
          }

          if(kind===OptionKind.PREFERENCE){
            varvalue=defaultOption.value,
                valueType=_typeof(value);

            if(valueType==='boolean'||valueType==='string'||valueType==='number'&&Number.isInteger(value)){
              options[name]=value;
              continue;
            }

            thrownewError("Invalidtypeforpreference:".concat(name));
          }
        }

        varuserOption=userOptions[name];
        options[name]=userOption!==undefined?userOption:defaultOption.compatibility||defaultOption.value;
      }

      returnoptions;
    }
  },{
    key:"set",
    value:functionset(name,value){
      userOptions[name]=value;
    }
  },{
    key:"remove",
    value:functionremove(name){
      deleteuserOptions[name];
    }
  }]);

  returnAppOptions;
}();

exports.AppOptions=AppOptions;

/***/}),
/*7*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


varpdfjsLib;

if(typeofwindow!=='undefined'&&window['pdfjs-dist/build/pdf']){
  pdfjsLib=window['pdfjs-dist/build/pdf'];
}else{
  pdfjsLib=require('../build/pdf.js');
}

module.exports=pdfjsLib;

/***/}),
/*8*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


varcompatibilityParams=Object.create(null);
{
  varuserAgent=typeofnavigator!=='undefined'&&navigator.userAgent||'';
  varisAndroid=/Android/.test(userAgent);
  varisIOS=/\b(iPad|iPhone|iPod)(?=;)/.test(userAgent);

  (functioncheckCanvasSizeLimitation(){
    if(isIOS||isAndroid){
      compatibilityParams.maxCanvasPixels=5242880;
    }
  })();
}
exports.viewerCompatibilityParams=Object.freeze(compatibilityParams);

/***/}),
/*9*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFCursorTools=exports.CursorTool=void0;

var_grab_to_pan=__webpack_require__(10);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varCursorTool={
  SELECT:0,
  HAND:1,
  ZOOM:2
};
exports.CursorTool=CursorTool;

varPDFCursorTools=
/*#__PURE__*/
function(){
  functionPDFCursorTools(_ref){
    var_this=this;

    varcontainer=_ref.container,
        eventBus=_ref.eventBus,
        _ref$cursorToolOnLoad=_ref.cursorToolOnLoad,
        cursorToolOnLoad=_ref$cursorToolOnLoad===void0?CursorTool.SELECT:_ref$cursorToolOnLoad;

    _classCallCheck(this,PDFCursorTools);

    this.container=container;
    this.eventBus=eventBus;
    this.active=CursorTool.SELECT;
    this.activeBeforePresentationMode=null;
    this.handTool=new_grab_to_pan.GrabToPan({
      element:this.container
    });

    this._addEventListeners();

    Promise.resolve().then(function(){
      _this.switchTool(cursorToolOnLoad);
    });
  }

  _createClass(PDFCursorTools,[{
    key:"switchTool",
    value:functionswitchTool(tool){
      var_this2=this;

      if(this.activeBeforePresentationMode!==null){
        return;
      }

      if(tool===this.active){
        return;
      }

      vardisableActiveTool=functiondisableActiveTool(){
        switch(_this2.active){
          caseCursorTool.SELECT:
            break;

          caseCursorTool.HAND:
            _this2.handTool.deactivate();

            break;

          caseCursorTool.ZOOM:
        }
      };

      switch(tool){
        caseCursorTool.SELECT:
          disableActiveTool();
          break;

        caseCursorTool.HAND:
          disableActiveTool();
          this.handTool.activate();
          break;

        caseCursorTool.ZOOM:
        default:
          console.error("switchTool:\"".concat(tool,"\"isanunsupportedvalue."));
          return;
      }

      this.active=tool;

      this._dispatchEvent();
    }
  },{
    key:"_dispatchEvent",
    value:function_dispatchEvent(){
      this.eventBus.dispatch('cursortoolchanged',{
        source:this,
        tool:this.active
      });
    }
  },{
    key:"_addEventListeners",
    value:function_addEventListeners(){
      var_this3=this;

      this.eventBus.on('switchcursortool',function(evt){
        _this3.switchTool(evt.tool);
      });
      this.eventBus.on('presentationmodechanged',function(evt){
        if(evt.switchInProgress){
          return;
        }

        varpreviouslyActive;

        if(evt.active){
          previouslyActive=_this3.active;

          _this3.switchTool(CursorTool.SELECT);

          _this3.activeBeforePresentationMode=previouslyActive;
        }else{
          previouslyActive=_this3.activeBeforePresentationMode;
          _this3.activeBeforePresentationMode=null;

          _this3.switchTool(previouslyActive);
        }
      });
    }
  },{
    key:"activeTool",
    get:functionget(){
      returnthis.active;
    }
  }]);

  returnPDFCursorTools;
}();

exports.PDFCursorTools=PDFCursorTools;

/***/}),
/*10*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.GrabToPan=GrabToPan;

functionGrabToPan(options){
  this.element=options.element;
  this.document=options.element.ownerDocument;

  if(typeofoptions.ignoreTarget==='function'){
    this.ignoreTarget=options.ignoreTarget;
  }

  this.onActiveChanged=options.onActiveChanged;
  this.activate=this.activate.bind(this);
  this.deactivate=this.deactivate.bind(this);
  this.toggle=this.toggle.bind(this);
  this._onmousedown=this._onmousedown.bind(this);
  this._onmousemove=this._onmousemove.bind(this);
  this._endPan=this._endPan.bind(this);
  varoverlay=this.overlay=document.createElement('div');
  overlay.className='grab-to-pan-grabbing';
}

GrabToPan.prototype={
  CSS_CLASS_GRAB:'grab-to-pan-grab',
  activate:functionGrabToPan_activate(){
    if(!this.active){
      this.active=true;
      this.element.addEventListener('mousedown',this._onmousedown,true);
      this.element.classList.add(this.CSS_CLASS_GRAB);

      if(this.onActiveChanged){
        this.onActiveChanged(true);
      }
    }
  },
  deactivate:functionGrabToPan_deactivate(){
    if(this.active){
      this.active=false;
      this.element.removeEventListener('mousedown',this._onmousedown,true);

      this._endPan();

      this.element.classList.remove(this.CSS_CLASS_GRAB);

      if(this.onActiveChanged){
        this.onActiveChanged(false);
      }
    }
  },
  toggle:functionGrabToPan_toggle(){
    if(this.active){
      this.deactivate();
    }else{
      this.activate();
    }
  },
  ignoreTarget:functionGrabToPan_ignoreTarget(node){
    returnnode[matchesSelector]('a[href],a[href]*,input,textarea,button,button*,select,option');
  },
  _onmousedown:functionGrabToPan__onmousedown(event){
    if(event.button!==0||this.ignoreTarget(event.target)){
      return;
    }

    if(event.originalTarget){
      try{
        event.originalTarget.tagName;
      }catch(e){
        return;
      }
    }

    this.scrollLeftStart=this.element.scrollLeft;
    this.scrollTopStart=this.element.scrollTop;
    this.clientXStart=event.clientX;
    this.clientYStart=event.clientY;
    this.document.addEventListener('mousemove',this._onmousemove,true);
    this.document.addEventListener('mouseup',this._endPan,true);
    this.element.addEventListener('scroll',this._endPan,true);
    event.preventDefault();
    event.stopPropagation();
    varfocusedElement=document.activeElement;

    if(focusedElement&&!focusedElement.contains(event.target)){
      focusedElement.blur();
    }
  },
  _onmousemove:functionGrabToPan__onmousemove(event){
    this.element.removeEventListener('scroll',this._endPan,true);

    if(isLeftMouseReleased(event)){
      this._endPan();

      return;
    }

    varxDiff=event.clientX-this.clientXStart;
    varyDiff=event.clientY-this.clientYStart;
    varscrollTop=this.scrollTopStart-yDiff;
    varscrollLeft=this.scrollLeftStart-xDiff;

    if(this.element.scrollTo){
      this.element.scrollTo({
        top:scrollTop,
        left:scrollLeft,
        behavior:'instant'
      });
    }else{
      this.element.scrollTop=scrollTop;
      this.element.scrollLeft=scrollLeft;
    }

    if(!this.overlay.parentNode){
      document.body.appendChild(this.overlay);
    }
  },
  _endPan:functionGrabToPan__endPan(){
    this.element.removeEventListener('scroll',this._endPan,true);
    this.document.removeEventListener('mousemove',this._onmousemove,true);
    this.document.removeEventListener('mouseup',this._endPan,true);
    this.overlay.remove();
  }
};
varmatchesSelector;
['webkitM','mozM','msM','oM','m'].some(function(prefix){
  varname=prefix+'atches';

  if(nameindocument.documentElement){
    matchesSelector=name;
  }

  name+='Selector';

  if(nameindocument.documentElement){
    matchesSelector=name;
  }

  returnmatchesSelector;
});
varisNotIEorIsIE10plus=!document.documentMode||document.documentMode>9;
varchrome=window.chrome;
varisChrome15OrOpera15plus=chrome&&(chrome.webstore||chrome.app);
varisSafari6plus=/Apple/.test(navigator.vendor)&&/Version\/([6-9]\d*|[1-5]\d+)/.test(navigator.userAgent);

functionisLeftMouseReleased(event){
  if('buttons'inevent&&isNotIEorIsIE10plus){
    return!(event.buttons&1);
  }

  if(isChrome15OrOpera15plus||isSafari6plus){
    returnevent.which===0;
  }

  returnfalse;
}

/***/}),
/*11*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFRenderingQueue=exports.RenderingStates=void0;

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varCLEANUP_TIMEOUT=30000;
varRenderingStates={
  INITIAL:0,
  RUNNING:1,
  PAUSED:2,
  FINISHED:3
};
exports.RenderingStates=RenderingStates;

varPDFRenderingQueue=
/*#__PURE__*/
function(){
  functionPDFRenderingQueue(){
    _classCallCheck(this,PDFRenderingQueue);

    this.pdfViewer=null;
    this.pdfThumbnailViewer=null;
    this.onIdle=null;
    this.highestPriorityPage=null;
    this.idleTimeout=null;
    this.printing=false;
    this.isThumbnailViewEnabled=false;
  }

  _createClass(PDFRenderingQueue,[{
    key:"setViewer",
    value:functionsetViewer(pdfViewer){
      this.pdfViewer=pdfViewer;
    }
  },{
    key:"setThumbnailViewer",
    value:functionsetThumbnailViewer(pdfThumbnailViewer){
      this.pdfThumbnailViewer=pdfThumbnailViewer;
    }
  },{
    key:"isHighestPriority",
    value:functionisHighestPriority(view){
      returnthis.highestPriorityPage===view.renderingId;
    }
  },{
    key:"renderHighestPriority",
    value:functionrenderHighestPriority(currentlyVisiblePages){
      if(this.idleTimeout){
        clearTimeout(this.idleTimeout);
        this.idleTimeout=null;
      }

      if(this.pdfViewer.forceRendering(currentlyVisiblePages)){
        return;
      }

      if(this.pdfThumbnailViewer&&this.isThumbnailViewEnabled){
        if(this.pdfThumbnailViewer.forceRendering()){
          return;
        }
      }

      if(this.printing){
        return;
      }

      if(this.onIdle){
        this.idleTimeout=setTimeout(this.onIdle.bind(this),CLEANUP_TIMEOUT);
      }
    }
  },{
    key:"getHighestPriority",
    value:functiongetHighestPriority(visible,views,scrolledDown){
      varvisibleViews=visible.views;
      varnumVisible=visibleViews.length;

      if(numVisible===0){
        returnnull;
      }

      for(vari=0;i<numVisible;++i){
        varview=visibleViews[i].view;

        if(!this.isViewFinished(view)){
          returnview;
        }
      }

      if(scrolledDown){
        varnextPageIndex=visible.last.id;

        if(views[nextPageIndex]&&!this.isViewFinished(views[nextPageIndex])){
          returnviews[nextPageIndex];
        }
      }else{
        varpreviousPageIndex=visible.first.id-2;

        if(views[previousPageIndex]&&!this.isViewFinished(views[previousPageIndex])){
          returnviews[previousPageIndex];
        }
      }

      returnnull;
    }
  },{
    key:"isViewFinished",
    value:functionisViewFinished(view){
      returnview.renderingState===RenderingStates.FINISHED;
    }
  },{
    key:"renderView",
    value:functionrenderView(view){
      var_this=this;

      switch(view.renderingState){
        caseRenderingStates.FINISHED:
          returnfalse;

        caseRenderingStates.PAUSED:
          this.highestPriorityPage=view.renderingId;
          view.resume();
          break;

        caseRenderingStates.RUNNING:
          this.highestPriorityPage=view.renderingId;
          break;

        caseRenderingStates.INITIAL:
          this.highestPriorityPage=view.renderingId;
          view.draw()["finally"](function(){
            _this.renderHighestPriority();
          });
          break;
      }

      returntrue;
    }
  }]);

  returnPDFRenderingQueue;
}();

exports.PDFRenderingQueue=PDFRenderingQueue;

/***/}),
/*12*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFSidebar=exports.SidebarView=void0;

var_ui_utils=__webpack_require__(5);

var_pdf_rendering_queue=__webpack_require__(11);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varUI_NOTIFICATION_CLASS='pdfSidebarNotification';
varSidebarView={
  UNKNOWN:-1,
  NONE:0,
  THUMBS:1,
  OUTLINE:2,
  ATTACHMENTS:3,
  LAYERS:4
};
exports.SidebarView=SidebarView;

varPDFSidebar=
/*#__PURE__*/
function(){
  functionPDFSidebar(_ref){
    varelements=_ref.elements,
        pdfViewer=_ref.pdfViewer,
        pdfThumbnailViewer=_ref.pdfThumbnailViewer,
        eventBus=_ref.eventBus,
        _ref$l10n=_ref.l10n,
        l10n=_ref$l10n===void0?_ui_utils.NullL10n:_ref$l10n,
        _ref$disableNotificat=_ref.disableNotification,
        disableNotification=_ref$disableNotificat===void0?false:_ref$disableNotificat;

    _classCallCheck(this,PDFSidebar);

    this.isOpen=false;
    this.active=SidebarView.THUMBS;
    this.isInitialViewSet=false;
    this.onToggled=null;
    this.pdfViewer=pdfViewer;
    this.pdfThumbnailViewer=pdfThumbnailViewer;
    this.outerContainer=elements.outerContainer;
    this.viewerContainer=elements.viewerContainer;
    this.toggleButton=elements.toggleButton;
    this.thumbnailButton=elements.thumbnailButton;
    this.outlineButton=elements.outlineButton;
    this.attachmentsButton=elements.attachmentsButton;
    this.thumbnailView=elements.thumbnailView;
    this.outlineView=elements.outlineView;
    this.attachmentsView=elements.attachmentsView;
    this.eventBus=eventBus;
    this.l10n=l10n;
    this._disableNotification=disableNotification;

    this._addEventListeners();
  }

  _createClass(PDFSidebar,[{
    key:"reset",
    value:functionreset(){
      this.isInitialViewSet=false;

      this._hideUINotification(null);

      this.switchView(SidebarView.THUMBS);
      this.outlineButton.disabled=false;
      this.attachmentsButton.disabled=false;
    }
  },{
    key:"setInitialView",
    value:functionsetInitialView(){
      varview=arguments.length>0&&arguments[0]!==undefined?arguments[0]:SidebarView.NONE;

      if(this.isInitialViewSet){
        return;
      }

      this.isInitialViewSet=true;

      if(view===SidebarView.NONE||view===SidebarView.UNKNOWN){
        this._dispatchEvent();

        return;
      }

      //Flectra:Thischangeisneededhereaswecan'tchangethisparameterinaniframe.
      //passforceOpenargumenttofalsetorestrictopeningofsidebarforcefullywhen
      //pdfvieweropensinitially.
      if(!this._switchView(view,false)){
        this._dispatchEvent();
      }
    }
  },{
    key:"switchView",
    value:functionswitchView(view){
      varforceOpen=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;

      this._switchView(view,forceOpen);
    }
  },{
    key:"_switchView",
    value:function_switchView(view){
      varforceOpen=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
      varisViewChanged=view!==this.active;
      varshouldForceRendering=false;

      switch(view){
        caseSidebarView.NONE:
          if(this.isOpen){
            this.close();
            returntrue;
          }

          returnfalse;

        caseSidebarView.THUMBS:
          if(this.isOpen&&isViewChanged){
            shouldForceRendering=true;
          }

          break;

        caseSidebarView.OUTLINE:
          if(this.outlineButton.disabled){
            returnfalse;
          }

          break;

        caseSidebarView.ATTACHMENTS:
          if(this.attachmentsButton.disabled){
            returnfalse;
          }

          break;

        default:
          console.error("PDFSidebar._switchView:\"".concat(view,"\"isnotavalidview."));
          returnfalse;
      }

      this.active=view;
      this.thumbnailButton.classList.toggle('toggled',view===SidebarView.THUMBS);
      this.outlineButton.classList.toggle('toggled',view===SidebarView.OUTLINE);
      this.attachmentsButton.classList.toggle('toggled',view===SidebarView.ATTACHMENTS);
      this.thumbnailView.classList.toggle('hidden',view!==SidebarView.THUMBS);
      this.outlineView.classList.toggle('hidden',view!==SidebarView.OUTLINE);
      this.attachmentsView.classList.toggle('hidden',view!==SidebarView.ATTACHMENTS);

      if(forceOpen&&!this.isOpen){
        this.open();
        returntrue;
      }

      if(shouldForceRendering){
        this._updateThumbnailViewer();

        this._forceRendering();
      }

      if(isViewChanged){
        this._dispatchEvent();
      }

      this._hideUINotification(this.active);

      returnisViewChanged;
    }
  },{
    key:"open",
    value:functionopen(){
      if(this.isOpen){
        return;
      }

      this.isOpen=true;
      this.toggleButton.classList.add('toggled');
      this.outerContainer.classList.add('sidebarMoving','sidebarOpen');

      if(this.active===SidebarView.THUMBS){
        this._updateThumbnailViewer();
      }

      this._forceRendering();

      this._dispatchEvent();

      this._hideUINotification(this.active);
    }
  },{
    key:"close",
    value:functionclose(){
      if(!this.isOpen){
        return;
      }

      this.isOpen=false;
      this.toggleButton.classList.remove('toggled');
      this.outerContainer.classList.add('sidebarMoving');
      this.outerContainer.classList.remove('sidebarOpen');

      this._forceRendering();

      this._dispatchEvent();
    }
  },{
    key:"toggle",
    value:functiontoggle(){
      if(this.isOpen){
        this.close();
      }else{
        this.open();
      }
    }
  },{
    key:"_dispatchEvent",
    value:function_dispatchEvent(){
      this.eventBus.dispatch('sidebarviewchanged',{
        source:this,
        view:this.visibleView
      });
    }
  },{
    key:"_forceRendering",
    value:function_forceRendering(){
      if(this.onToggled){
        this.onToggled();
      }else{
        this.pdfViewer.forceRendering();
        this.pdfThumbnailViewer.forceRendering();
      }
    }
  },{
    key:"_updateThumbnailViewer",
    value:function_updateThumbnailViewer(){
      varpdfViewer=this.pdfViewer,
          pdfThumbnailViewer=this.pdfThumbnailViewer;
      varpagesCount=pdfViewer.pagesCount;

      for(varpageIndex=0;pageIndex<pagesCount;pageIndex++){
        varpageView=pdfViewer.getPageView(pageIndex);

        if(pageView&&pageView.renderingState===_pdf_rendering_queue.RenderingStates.FINISHED){
          varthumbnailView=pdfThumbnailViewer.getThumbnail(pageIndex);
          thumbnailView.setImage(pageView);
        }
      }

      pdfThumbnailViewer.scrollThumbnailIntoView(pdfViewer.currentPageNumber);
    }
  },{
    key:"_showUINotification",
    value:function_showUINotification(view){
      var_this=this;

      if(this._disableNotification){
        return;
      }

      this.l10n.get('toggle_sidebar_notification.title',null,'ToggleSidebar(documentcontainsoutline/attachments)').then(function(msg){
        _this.toggleButton.title=msg;
      });

      if(!this.isOpen){
        this.toggleButton.classList.add(UI_NOTIFICATION_CLASS);
      }elseif(view===this.active){
        return;
      }

      switch(view){
        caseSidebarView.OUTLINE:
          this.outlineButton.classList.add(UI_NOTIFICATION_CLASS);
          break;

        caseSidebarView.ATTACHMENTS:
          this.attachmentsButton.classList.add(UI_NOTIFICATION_CLASS);
          break;
      }
    }
  },{
    key:"_hideUINotification",
    value:function_hideUINotification(view){
      var_this2=this;

      if(this._disableNotification){
        return;
      }

      varremoveNotification=functionremoveNotification(view){
        switch(view){
          caseSidebarView.OUTLINE:
            _this2.outlineButton.classList.remove(UI_NOTIFICATION_CLASS);

            break;

          caseSidebarView.ATTACHMENTS:
            _this2.attachmentsButton.classList.remove(UI_NOTIFICATION_CLASS);

            break;
        }
      };

      if(!this.isOpen&&view!==null){
        return;
      }

      this.toggleButton.classList.remove(UI_NOTIFICATION_CLASS);

      if(view!==null){
        removeNotification(view);
        return;
      }

      for(viewinSidebarView){
        removeNotification(SidebarView[view]);
      }

      this.l10n.get('toggle_sidebar.title',null,'ToggleSidebar').then(function(msg){
        _this2.toggleButton.title=msg;
      });
    }
  },{
    key:"_addEventListeners",
    value:function_addEventListeners(){
      var_this3=this;

      this.viewerContainer.addEventListener('transitionend',function(evt){
        if(evt.target===_this3.viewerContainer){
          _this3.outerContainer.classList.remove('sidebarMoving');
        }
      });
      this.thumbnailButton.addEventListener('click',function(){
        _this3.switchView(SidebarView.THUMBS);
      });
      this.outlineButton.addEventListener('click',function(){
        _this3.switchView(SidebarView.OUTLINE);
      });
      this.outlineButton.addEventListener('dblclick',function(){
        _this3.eventBus.dispatch('toggleoutlinetree',{
          source:_this3
        });
      });
      this.attachmentsButton.addEventListener('click',function(){
        _this3.switchView(SidebarView.ATTACHMENTS);
      });
      this.eventBus.on('outlineloaded',function(evt){
        varoutlineCount=evt.outlineCount;
        _this3.outlineButton.disabled=!outlineCount;

        if(outlineCount){
          _this3._showUINotification(SidebarView.OUTLINE);
        }elseif(_this3.active===SidebarView.OUTLINE){
          _this3.switchView(SidebarView.THUMBS);
        }
      });
      this.eventBus.on('attachmentsloaded',function(evt){
        if(evt.attachmentsCount){
          _this3.attachmentsButton.disabled=false;

          _this3._showUINotification(SidebarView.ATTACHMENTS);

          return;
        }

        Promise.resolve().then(function(){
          if(_this3.attachmentsView.hasChildNodes()){
            return;
          }

          _this3.attachmentsButton.disabled=true;

          if(_this3.active===SidebarView.ATTACHMENTS){
            _this3.switchView(SidebarView.THUMBS);
          }
        });
      });
      this.eventBus.on('presentationmodechanged',function(evt){
        if(!evt.active&&!evt.switchInProgress&&_this3.isThumbnailViewVisible){
          _this3._updateThumbnailViewer();
        }
      });
    }
  },{
    key:"visibleView",
    get:functionget(){
      returnthis.isOpen?this.active:SidebarView.NONE;
    }
  },{
    key:"isThumbnailViewVisible",
    get:functionget(){
      returnthis.isOpen&&this.active===SidebarView.THUMBS;
    }
  },{
    key:"isOutlineViewVisible",
    get:functionget(){
      returnthis.isOpen&&this.active===SidebarView.OUTLINE;
    }
  },{
    key:"isAttachmentsViewVisible",
    get:functionget(){
      returnthis.isOpen&&this.active===SidebarView.ATTACHMENTS;
    }
  }]);

  returnPDFSidebar;
}();

exports.PDFSidebar=PDFSidebar;

/***/}),
/*13*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.OverlayManager=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varOverlayManager=
/*#__PURE__*/
function(){
  functionOverlayManager(){
    _classCallCheck(this,OverlayManager);

    this._overlays={};
    this._active=null;
    this._keyDownBound=this._keyDown.bind(this);
  }

  _createClass(OverlayManager,[{
    key:"register",
    value:function(){
      var_register=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(name,element){
        varcallerCloseMethod,
            canForceClose,
            container,
            _args=arguments;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                callerCloseMethod=_args.length>2&&_args[2]!==undefined?_args[2]:null;
                canForceClose=_args.length>3&&_args[3]!==undefined?_args[3]:false;

                if(!(!name||!element||!(container=element.parentNode))){
                  _context.next=6;
                  break;
                }

                thrownewError('Notenoughparameters.');

              case6:
                if(!this._overlays[name]){
                  _context.next=8;
                  break;
                }

                thrownewError('Theoverlayisalreadyregistered.');

              case8:
                this._overlays[name]={
                  element:element,
                  container:container,
                  callerCloseMethod:callerCloseMethod,
                  canForceClose:canForceClose
                };

              case9:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      functionregister(_x,_x2){
        return_register.apply(this,arguments);
      }

      returnregister;
    }()
  },{
    key:"unregister",
    value:function(){
      var_unregister=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(name){
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                if(this._overlays[name]){
                  _context2.next=4;
                  break;
                }

                thrownewError('Theoverlaydoesnotexist.');

              case4:
                if(!(this._active===name)){
                  _context2.next=6;
                  break;
                }

                thrownewError('Theoverlaycannotberemovedwhileitisactive.');

              case6:
                deletethis._overlays[name];

              case7:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      functionunregister(_x3){
        return_unregister.apply(this,arguments);
      }

      returnunregister;
    }()
  },{
    key:"open",
    value:function(){
      var_open=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee3(name){
        return_regenerator["default"].wrap(function_callee3$(_context3){
          while(1){
            switch(_context3.prev=_context3.next){
              case0:
                if(this._overlays[name]){
                  _context3.next=4;
                  break;
                }

                thrownewError('Theoverlaydoesnotexist.');

              case4:
                if(!this._active){
                  _context3.next=14;
                  break;
                }

                if(!this._overlays[name].canForceClose){
                  _context3.next=9;
                  break;
                }

                this._closeThroughCaller();

                _context3.next=14;
                break;

              case9:
                if(!(this._active===name)){
                  _context3.next=13;
                  break;
                }

                thrownewError('Theoverlayisalreadyactive.');

              case13:
                thrownewError('Anotheroverlayiscurrentlyactive.');

              case14:
                this._active=name;

                this._overlays[this._active].element.classList.remove('hidden');

                this._overlays[this._active].container.classList.remove('hidden');

                window.addEventListener('keydown',this._keyDownBound);

              case18:
              case"end":
                return_context3.stop();
            }
          }
        },_callee3,this);
      }));

      functionopen(_x4){
        return_open.apply(this,arguments);
      }

      returnopen;
    }()
  },{
    key:"close",
    value:function(){
      var_close=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee4(name){
        return_regenerator["default"].wrap(function_callee4$(_context4){
          while(1){
            switch(_context4.prev=_context4.next){
              case0:
                if(this._overlays[name]){
                  _context4.next=4;
                  break;
                }

                thrownewError('Theoverlaydoesnotexist.');

              case4:
                if(this._active){
                  _context4.next=8;
                  break;
                }

                thrownewError('Theoverlayiscurrentlynotactive.');

              case8:
                if(!(this._active!==name)){
                  _context4.next=10;
                  break;
                }

                thrownewError('Anotheroverlayiscurrentlyactive.');

              case10:
                this._overlays[this._active].container.classList.add('hidden');

                this._overlays[this._active].element.classList.add('hidden');

                this._active=null;
                window.removeEventListener('keydown',this._keyDownBound);

              case14:
              case"end":
                return_context4.stop();
            }
          }
        },_callee4,this);
      }));

      functionclose(_x5){
        return_close.apply(this,arguments);
      }

      returnclose;
    }()
  },{
    key:"_keyDown",
    value:function_keyDown(evt){
      if(this._active&&evt.keyCode===27){
        this._closeThroughCaller();

        evt.preventDefault();
      }
    }
  },{
    key:"_closeThroughCaller",
    value:function_closeThroughCaller(){
      if(this._overlays[this._active].callerCloseMethod){
        this._overlays[this._active].callerCloseMethod();
      }

      if(this._active){
        this.close(this._active);
      }
    }
  },{
    key:"active",
    get:functionget(){
      returnthis._active;
    }
  }]);

  returnOverlayManager;
}();

exports.OverlayManager=OverlayManager;

/***/}),
/*14*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PasswordPrompt=void0;

var_ui_utils=__webpack_require__(5);

var_pdfjsLib=__webpack_require__(7);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varPasswordPrompt=
/*#__PURE__*/
function(){
  functionPasswordPrompt(options,overlayManager){
    var_this=this;

    varl10n=arguments.length>2&&arguments[2]!==undefined?arguments[2]:_ui_utils.NullL10n;

    _classCallCheck(this,PasswordPrompt);

    this.overlayName=options.overlayName;
    this.container=options.container;
    this.label=options.label;
    this.input=options.input;
    this.submitButton=options.submitButton;
    this.cancelButton=options.cancelButton;
    this.overlayManager=overlayManager;
    this.l10n=l10n;
    this.updateCallback=null;
    this.reason=null;
    this.submitButton.addEventListener('click',this.verify.bind(this));
    this.cancelButton.addEventListener('click',this.close.bind(this));
    this.input.addEventListener('keydown',function(e){
      if(e.keyCode===13){
        _this.verify();
      }
    });
    this.overlayManager.register(this.overlayName,this.container,this.close.bind(this),true);
  }

  _createClass(PasswordPrompt,[{
    key:"open",
    value:functionopen(){
      var_this2=this;

      this.overlayManager.open(this.overlayName).then(function(){
        _this2.input.focus();

        varpromptString;

        if(_this2.reason===_pdfjsLib.PasswordResponses.INCORRECT_PASSWORD){
          promptString=_this2.l10n.get('password_invalid',null,'Invalidpassword.Pleasetryagain.');
        }else{
          promptString=_this2.l10n.get('password_label',null,'EnterthepasswordtoopenthisPDFfile.');
        }

        promptString.then(function(msg){
          _this2.label.textContent=msg;
        });
      });
    }
  },{
    key:"close",
    value:functionclose(){
      var_this3=this;

      this.overlayManager.close(this.overlayName).then(function(){
        _this3.input.value='';
      });
    }
  },{
    key:"verify",
    value:functionverify(){
      varpassword=this.input.value;

      if(password&&password.length>0){
        this.close();
        this.updateCallback(password);
      }
    }
  },{
    key:"setUpdateCallback",
    value:functionsetUpdateCallback(updateCallback,reason){
      this.updateCallback=updateCallback;
      this.reason=reason;
    }
  }]);

  returnPasswordPrompt;
}();

exports.PasswordPrompt=PasswordPrompt;

/***/}),
/*15*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFAttachmentViewer=void0;

var_pdfjsLib=__webpack_require__(7);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varPDFAttachmentViewer=
/*#__PURE__*/
function(){
  functionPDFAttachmentViewer(_ref){
    varcontainer=_ref.container,
        eventBus=_ref.eventBus,
        downloadManager=_ref.downloadManager;

    _classCallCheck(this,PDFAttachmentViewer);

    this.container=container;
    this.eventBus=eventBus;
    this.downloadManager=downloadManager;
    this.reset();
    this.eventBus.on('fileattachmentannotation',this._appendAttachment.bind(this));
  }

  _createClass(PDFAttachmentViewer,[{
    key:"reset",
    value:functionreset(){
      varkeepRenderedCapability=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      this.attachments=null;
      this.container.textContent='';

      if(!keepRenderedCapability){
        this._renderedCapability=(0,_pdfjsLib.createPromiseCapability)();
      }
    }
  },{
    key:"_dispatchEvent",
    value:function_dispatchEvent(attachmentsCount){
      this._renderedCapability.resolve();

      this.eventBus.dispatch('attachmentsloaded',{
        source:this,
        attachmentsCount:attachmentsCount
      });
    }
  },{
    key:"_bindPdfLink",
    value:function_bindPdfLink(button,content,filename){
      if(this.downloadManager.disableCreateObjectURL){
        thrownewError('bindPdfLink:Unsupported"disableCreateObjectURL"value.');
      }

      varblobUrl;

      button.onclick=function(){
        if(!blobUrl){
          blobUrl=(0,_pdfjsLib.createObjectURL)(content,'application/pdf');
        }

        varviewerUrl;
        viewerUrl='?file='+encodeURIComponent(blobUrl+'#'+filename);
        window.open(viewerUrl);
        returnfalse;
      };
    }
  },{
    key:"_bindLink",
    value:function_bindLink(button,content,filename){
      var_this=this;

      button.onclick=function(){
        _this.downloadManager.downloadData(content,filename,'');

        returnfalse;
      };
    }
  },{
    key:"render",
    value:functionrender(_ref2){
      varattachments=_ref2.attachments,
          _ref2$keepRenderedCap=_ref2.keepRenderedCapability,
          keepRenderedCapability=_ref2$keepRenderedCap===void0?false:_ref2$keepRenderedCap;
      varattachmentsCount=0;

      if(this.attachments){
        this.reset(keepRenderedCapability===true);
      }

      this.attachments=attachments||null;

      if(!attachments){
        this._dispatchEvent(attachmentsCount);

        return;
      }

      varnames=Object.keys(attachments).sort(function(a,b){
        returna.toLowerCase().localeCompare(b.toLowerCase());
      });
      attachmentsCount=names.length;

      for(vari=0;i<attachmentsCount;i++){
        varitem=attachments[names[i]];
        varfilename=(0,_pdfjsLib.removeNullCharacters)((0,_pdfjsLib.getFilenameFromUrl)(item.filename));
        vardiv=document.createElement('div');
        div.className='attachmentsItem';
        varbutton=document.createElement('button');
        button.textContent=filename;

        if(/\.pdf$/i.test(filename)&&!this.downloadManager.disableCreateObjectURL){
          this._bindPdfLink(button,item.content,filename);
        }else{
          this._bindLink(button,item.content,filename);
        }

        div.appendChild(button);
        this.container.appendChild(div);
      }

      this._dispatchEvent(attachmentsCount);
    }
  },{
    key:"_appendAttachment",
    value:function_appendAttachment(_ref3){
      var_this2=this;

      varid=_ref3.id,
          filename=_ref3.filename,
          content=_ref3.content;

      this._renderedCapability.promise.then(function(){
        varattachments=_this2.attachments;

        if(!attachments){
          attachments=Object.create(null);
        }else{
          for(varnameinattachments){
            if(id===name){
              return;
            }
          }
        }

        attachments[id]={
          filename:filename,
          content:content
        };

        _this2.render({
          attachments:attachments,
          keepRenderedCapability:true
        });
      });
    }
  }]);

  returnPDFAttachmentViewer;
}();

exports.PDFAttachmentViewer=PDFAttachmentViewer;

/***/}),
/*16*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFDocumentProperties=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

var_pdfjsLib=__webpack_require__(7);

var_ui_utils=__webpack_require__(5);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varDEFAULT_FIELD_CONTENT='-';
varNON_METRIC_LOCALES=['en-us','en-lr','my'];
varUS_PAGE_NAMES={
  '8.5x11':'Letter',
  '8.5x14':'Legal'
};
varMETRIC_PAGE_NAMES={
  '297x420':'A3',
  '210x297':'A4'
};

functiongetPageName(size,isPortrait,pageNames){
  varwidth=isPortrait?size.width:size.height;
  varheight=isPortrait?size.height:size.width;
  returnpageNames["".concat(width,"x").concat(height)];
}

varPDFDocumentProperties=
/*#__PURE__*/
function(){
  functionPDFDocumentProperties(_ref,overlayManager,eventBus){
    var_this=this;

    varoverlayName=_ref.overlayName,
        fields=_ref.fields,
        container=_ref.container,
        closeButton=_ref.closeButton;
    varl10n=arguments.length>3&&arguments[3]!==undefined?arguments[3]:_ui_utils.NullL10n;

    _classCallCheck(this,PDFDocumentProperties);

    this.overlayName=overlayName;
    this.fields=fields;
    this.container=container;
    this.overlayManager=overlayManager;
    this.l10n=l10n;

    this._reset();

    if(closeButton){
      closeButton.addEventListener('click',this.close.bind(this));
    }

    this.overlayManager.register(this.overlayName,this.container,this.close.bind(this));

    if(eventBus){
      eventBus.on('pagechanging',function(evt){
        _this._currentPageNumber=evt.pageNumber;
      });
      eventBus.on('rotationchanging',function(evt){
        _this._pagesRotation=evt.pagesRotation;
      });
    }

    this._isNonMetricLocale=true;
    l10n.getLanguage().then(function(locale){
      _this._isNonMetricLocale=NON_METRIC_LOCALES.includes(locale);
    });
  }

  _createClass(PDFDocumentProperties,[{
    key:"open",
    value:functionopen(){
      var_this2=this;

      varfreezeFieldData=functionfreezeFieldData(data){
        Object.defineProperty(_this2,'fieldData',{
          value:Object.freeze(data),
          writable:false,
          enumerable:true,
          configurable:true
        });
      };

      Promise.all([this.overlayManager.open(this.overlayName),this._dataAvailableCapability.promise]).then(function(){
        varcurrentPageNumber=_this2._currentPageNumber;
        varpagesRotation=_this2._pagesRotation;

        if(_this2.fieldData&&currentPageNumber===_this2.fieldData['_currentPageNumber']&&pagesRotation===_this2.fieldData['_pagesRotation']){
          _this2._updateUI();

          return;
        }

        _this2.pdfDocument.getMetadata().then(function(_ref2){
          varinfo=_ref2.info,
              metadata=_ref2.metadata,
              contentDispositionFilename=_ref2.contentDispositionFilename;
          returnPromise.all([info,metadata,contentDispositionFilename||(0,_ui_utils.getPDFFileNameFromURL)(_this2.url||''),_this2._parseFileSize(_this2.maybeFileSize),_this2._parseDate(info.CreationDate),_this2._parseDate(info.ModDate),_this2.pdfDocument.getPage(currentPageNumber).then(function(pdfPage){
            return_this2._parsePageSize((0,_ui_utils.getPageSizeInches)(pdfPage),pagesRotation);
          }),_this2._parseLinearization(info.IsLinearized)]);
        }).then(function(_ref3){
          var_ref4=_slicedToArray(_ref3,8),
              info=_ref4[0],
              metadata=_ref4[1],
              fileName=_ref4[2],
              fileSize=_ref4[3],
              creationDate=_ref4[4],
              modDate=_ref4[5],
              pageSize=_ref4[6],
              isLinearized=_ref4[7];

          freezeFieldData({
            'fileName':fileName,
            'fileSize':fileSize,
            'title':info.Title,
            'author':info.Author,
            'subject':info.Subject,
            'keywords':info.Keywords,
            'creationDate':creationDate,
            'modificationDate':modDate,
            'creator':info.Creator,
            'producer':info.Producer,
            'version':info.PDFFormatVersion,
            'pageCount':_this2.pdfDocument.numPages,
            'pageSize':pageSize,
            'linearized':isLinearized,
            '_currentPageNumber':currentPageNumber,
            '_pagesRotation':pagesRotation
          });

          _this2._updateUI();

          return_this2.pdfDocument.getDownloadInfo();
        }).then(function(_ref5){
          varlength=_ref5.length;
          _this2.maybeFileSize=length;
          return_this2._parseFileSize(length);
        }).then(function(fileSize){
          if(fileSize===_this2.fieldData['fileSize']){
            return;
          }

          vardata=Object.assign(Object.create(null),_this2.fieldData);
          data['fileSize']=fileSize;
          freezeFieldData(data);

          _this2._updateUI();
        });
      });
    }
  },{
    key:"close",
    value:functionclose(){
      this.overlayManager.close(this.overlayName);
    }
  },{
    key:"setDocument",
    value:functionsetDocument(pdfDocument){
      varurl=arguments.length>1&&arguments[1]!==undefined?arguments[1]:null;

      if(this.pdfDocument){
        this._reset();

        this._updateUI(true);
      }

      if(!pdfDocument){
        return;
      }

      this.pdfDocument=pdfDocument;
      this.url=url;

      this._dataAvailableCapability.resolve();
    }
  },{
    key:"setFileSize",
    value:functionsetFileSize(fileSize){
      if(Number.isInteger(fileSize)&&fileSize>0){
        this.maybeFileSize=fileSize;
      }
    }
  },{
    key:"_reset",
    value:function_reset(){
      this.pdfDocument=null;
      this.url=null;
      this.maybeFileSize=0;
      deletethis.fieldData;
      this._dataAvailableCapability=(0,_pdfjsLib.createPromiseCapability)();
      this._currentPageNumber=1;
      this._pagesRotation=0;
    }
  },{
    key:"_updateUI",
    value:function_updateUI(){
      varreset=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(reset||!this.fieldData){
        for(varidinthis.fields){
          this.fields[id].textContent=DEFAULT_FIELD_CONTENT;
        }

        return;
      }

      if(this.overlayManager.active!==this.overlayName){
        return;
      }

      for(var_idinthis.fields){
        varcontent=this.fieldData[_id];
        this.fields[_id].textContent=content||content===0?content:DEFAULT_FIELD_CONTENT;
      }
    }
  },{
    key:"_parseFileSize",
    value:function(){
      var_parseFileSize2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        varfileSize,
            kb,
            _args=arguments;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                fileSize=_args.length>0&&_args[0]!==undefined?_args[0]:0;
                kb=fileSize/1024;

                if(kb){
                  _context.next=6;
                  break;
                }

                return_context.abrupt("return",undefined);

              case6:
                if(!(kb<1024)){
                  _context.next=8;
                  break;
                }

                return_context.abrupt("return",this.l10n.get('document_properties_kb',{
                  size_kb:(+kb.toPrecision(3)).toLocaleString(),
                  size_b:fileSize.toLocaleString()
                },'{{size_kb}}KB({{size_b}}bytes)'));

              case8:
                return_context.abrupt("return",this.l10n.get('document_properties_mb',{
                  size_mb:(+(kb/1024).toPrecision(3)).toLocaleString(),
                  size_b:fileSize.toLocaleString()
                },'{{size_mb}}MB({{size_b}}bytes)'));

              case9:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      function_parseFileSize(){
        return_parseFileSize2.apply(this,arguments);
      }

      return_parseFileSize;
    }()
  },{
    key:"_parsePageSize",
    value:function(){
      var_parsePageSize2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(pageSizeInches,pagesRotation){
        var_this3=this;

        varisPortrait,sizeInches,sizeMillimeters,pageName,name,exactMillimeters,intMillimeters;
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                if(pageSizeInches){
                  _context2.next=2;
                  break;
                }

                return_context2.abrupt("return",undefined);

              case2:
                if(pagesRotation%180!==0){
                  pageSizeInches={
                    width:pageSizeInches.height,
                    height:pageSizeInches.width
                  };
                }

                isPortrait=(0,_ui_utils.isPortraitOrientation)(pageSizeInches);
                sizeInches={
                  width:Math.round(pageSizeInches.width*100)/100,
                  height:Math.round(pageSizeInches.height*100)/100
                };
                sizeMillimeters={
                  width:Math.round(pageSizeInches.width*25.4*10)/10,
                  height:Math.round(pageSizeInches.height*25.4*10)/10
                };
                pageName=null;
                name=getPageName(sizeInches,isPortrait,US_PAGE_NAMES)||getPageName(sizeMillimeters,isPortrait,METRIC_PAGE_NAMES);

                if(!name&&!(Number.isInteger(sizeMillimeters.width)&&Number.isInteger(sizeMillimeters.height))){
                  exactMillimeters={
                    width:pageSizeInches.width*25.4,
                    height:pageSizeInches.height*25.4
                  };
                  intMillimeters={
                    width:Math.round(sizeMillimeters.width),
                    height:Math.round(sizeMillimeters.height)
                  };

                  if(Math.abs(exactMillimeters.width-intMillimeters.width)<0.1&&Math.abs(exactMillimeters.height-intMillimeters.height)<0.1){
                    name=getPageName(intMillimeters,isPortrait,METRIC_PAGE_NAMES);

                    if(name){
                      sizeInches={
                        width:Math.round(intMillimeters.width/25.4*100)/100,
                        height:Math.round(intMillimeters.height/25.4*100)/100
                      };
                      sizeMillimeters=intMillimeters;
                    }
                  }
                }

                if(name){
                  pageName=this.l10n.get('document_properties_page_size_name_'+name.toLowerCase(),null,name);
                }

                return_context2.abrupt("return",Promise.all([this._isNonMetricLocale?sizeInches:sizeMillimeters,this.l10n.get('document_properties_page_size_unit_'+(this._isNonMetricLocale?'inches':'millimeters'),null,this._isNonMetricLocale?'in':'mm'),pageName,this.l10n.get('document_properties_page_size_orientation_'+(isPortrait?'portrait':'landscape'),null,isPortrait?'portrait':'landscape')]).then(function(_ref6){
                  var_ref7=_slicedToArray(_ref6,4),
                      _ref7$=_ref7[0],
                      width=_ref7$.width,
                      height=_ref7$.height,
                      unit=_ref7[1],
                      name=_ref7[2],
                      orientation=_ref7[3];

                  return_this3.l10n.get('document_properties_page_size_dimension_'+(name?'name_':'')+'string',{
                    width:width.toLocaleString(),
                    height:height.toLocaleString(),
                    unit:unit,
                    name:name,
                    orientation:orientation
                  },'{{width}}×{{height}}{{unit}}('+(name?'{{name}},':'')+'{{orientation}})');
                }));

              case11:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      function_parsePageSize(_x,_x2){
        return_parsePageSize2.apply(this,arguments);
      }

      return_parsePageSize;
    }()
  },{
    key:"_parseDate",
    value:function(){
      var_parseDate2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee3(inputDate){
        vardateObject;
        return_regenerator["default"].wrap(function_callee3$(_context3){
          while(1){
            switch(_context3.prev=_context3.next){
              case0:
                dateObject=_pdfjsLib.PDFDateString.toDateObject(inputDate);

                if(dateObject){
                  _context3.next=3;
                  break;
                }

                return_context3.abrupt("return",undefined);

              case3:
                return_context3.abrupt("return",this.l10n.get('document_properties_date_string',{
                  date:dateObject.toLocaleDateString(),
                  time:dateObject.toLocaleTimeString()
                },'{{date}},{{time}}'));

              case4:
              case"end":
                return_context3.stop();
            }
          }
        },_callee3,this);
      }));

      function_parseDate(_x3){
        return_parseDate2.apply(this,arguments);
      }

      return_parseDate;
    }()
  },{
    key:"_parseLinearization",
    value:function_parseLinearization(isLinearized){
      returnthis.l10n.get('document_properties_linearized_'+(isLinearized?'yes':'no'),null,isLinearized?'Yes':'No');
    }
  }]);

  returnPDFDocumentProperties;
}();

exports.PDFDocumentProperties=PDFDocumentProperties;

/***/}),
/*17*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFFindBar=void0;

var_ui_utils=__webpack_require__(5);

var_pdf_find_controller=__webpack_require__(18);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varMATCHES_COUNT_LIMIT=1000;

varPDFFindBar=
/*#__PURE__*/
function(){
  functionPDFFindBar(options){
    var_this=this;

    vareventBus=arguments.length>1&&arguments[1]!==undefined?arguments[1]:(0,_ui_utils.getGlobalEventBus)();
    varl10n=arguments.length>2&&arguments[2]!==undefined?arguments[2]:_ui_utils.NullL10n;

    _classCallCheck(this,PDFFindBar);

    this.opened=false;
    this.bar=options.bar||null;
    this.toggleButton=options.toggleButton||null;
    this.findField=options.findField||null;
    this.highlightAll=options.highlightAllCheckbox||null;
    this.caseSensitive=options.caseSensitiveCheckbox||null;
    this.entireWord=options.entireWordCheckbox||null;
    this.findMsg=options.findMsg||null;
    this.findResultsCount=options.findResultsCount||null;
    this.findPreviousButton=options.findPreviousButton||null;
    this.findNextButton=options.findNextButton||null;
    this.eventBus=eventBus;
    this.l10n=l10n;
    this.toggleButton.addEventListener('click',function(){
      _this.toggle();
    });
    this.findField.addEventListener('input',function(){
      _this.dispatchEvent('');
    });
    this.bar.addEventListener('keydown',function(e){
      switch(e.keyCode){
        case13:
          if(e.target===_this.findField){
            _this.dispatchEvent('again',e.shiftKey);
          }

          break;

        case27:
          _this.close();

          break;
      }
    });
    this.findPreviousButton.addEventListener('click',function(){
      _this.dispatchEvent('again',true);
    });
    this.findNextButton.addEventListener('click',function(){
      _this.dispatchEvent('again',false);
    });
    this.highlightAll.addEventListener('click',function(){
      _this.dispatchEvent('highlightallchange');
    });
    this.caseSensitive.addEventListener('click',function(){
      _this.dispatchEvent('casesensitivitychange');
    });
    this.entireWord.addEventListener('click',function(){
      _this.dispatchEvent('entirewordchange');
    });
    this.eventBus.on('resize',this._adjustWidth.bind(this));
  }

  _createClass(PDFFindBar,[{
    key:"reset",
    value:functionreset(){
      this.updateUIState();
    }
  },{
    key:"dispatchEvent",
    value:functiondispatchEvent(type,findPrev){
      this.eventBus.dispatch('find',{
        source:this,
        type:type,
        query:this.findField.value,
        phraseSearch:true,
        caseSensitive:this.caseSensitive.checked,
        entireWord:this.entireWord.checked,
        highlightAll:this.highlightAll.checked,
        findPrevious:findPrev
      });
    }
  },{
    key:"updateUIState",
    value:functionupdateUIState(state,previous,matchesCount){
      var_this2=this;

      varnotFound=false;
      varfindMsg='';
      varstatus='';

      switch(state){
        case_pdf_find_controller.FindState.FOUND:
          break;

        case_pdf_find_controller.FindState.PENDING:
          status='pending';
          break;

        case_pdf_find_controller.FindState.NOT_FOUND:
          findMsg=this.l10n.get('find_not_found',null,'Phrasenotfound');
          notFound=true;
          break;

        case_pdf_find_controller.FindState.WRAPPED:
          if(previous){
            findMsg=this.l10n.get('find_reached_top',null,'Reachedtopofdocument,continuedfrombottom');
          }else{
            findMsg=this.l10n.get('find_reached_bottom',null,'Reachedendofdocument,continuedfromtop');
          }

          break;
      }

      this.findField.classList.toggle('notFound',notFound);
      this.findField.setAttribute('data-status',status);
      Promise.resolve(findMsg).then(function(msg){
        _this2.findMsg.textContent=msg;

        _this2._adjustWidth();
      });
      this.updateResultsCount(matchesCount);
    }
  },{
    key:"updateResultsCount",
    value:functionupdateResultsCount(){
      var_this3=this;

      var_ref=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
          _ref$current=_ref.current,
          current=_ref$current===void0?0:_ref$current,
          _ref$total=_ref.total,
          total=_ref$total===void0?0:_ref$total;

      if(!this.findResultsCount){
        return;
      }

      varmatchesCountMsg='',
          limit=MATCHES_COUNT_LIMIT;

      if(total>0){
        if(total>limit){
          matchesCountMsg=this.l10n.get('find_match_count_limit',{
            limit:limit
          },'Morethan{{limit}}match'+(limit!==1?'es':''));
        }else{
          matchesCountMsg=this.l10n.get('find_match_count',{
            current:current,
            total:total
          },'{{current}}of{{total}}match'+(total!==1?'es':''));
        }
      }

      Promise.resolve(matchesCountMsg).then(function(msg){
        _this3.findResultsCount.textContent=msg;

        _this3.findResultsCount.classList.toggle('hidden',!total);

        _this3._adjustWidth();
      });
    }
  },{
    key:"open",
    value:functionopen(){
      if(!this.opened){
        this.opened=true;
        this.toggleButton.classList.add('toggled');
        this.bar.classList.remove('hidden');
      }

      this.findField.select();
      this.findField.focus();

      this._adjustWidth();
    }
  },{
    key:"close",
    value:functionclose(){
      if(!this.opened){
        return;
      }

      this.opened=false;
      this.toggleButton.classList.remove('toggled');
      this.bar.classList.add('hidden');
      this.eventBus.dispatch('findbarclose',{
        source:this
      });
    }
  },{
    key:"toggle",
    value:functiontoggle(){
      if(this.opened){
        this.close();
      }else{
        this.open();
      }
    }
  },{
    key:"_adjustWidth",
    value:function_adjustWidth(){
      if(!this.opened){
        return;
      }

      this.bar.classList.remove('wrapContainers');
      varfindbarHeight=this.bar.clientHeight;
      varinputContainerHeight=this.bar.firstElementChild.clientHeight;

      if(findbarHeight>inputContainerHeight){
        this.bar.classList.add('wrapContainers');
      }
    }
  }]);

  returnPDFFindBar;
}();

exports.PDFFindBar=PDFFindBar;

/***/}),
/*18*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFFindController=exports.FindState=void0;

var_ui_utils=__webpack_require__(5);

var_pdfjsLib=__webpack_require__(7);

var_pdf_find_utils=__webpack_require__(19);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varFindState={
  FOUND:0,
  NOT_FOUND:1,
  WRAPPED:2,
  PENDING:3
};
exports.FindState=FindState;
varFIND_TIMEOUT=250;
varMATCH_SCROLL_OFFSET_TOP=-50;
varMATCH_SCROLL_OFFSET_LEFT=-400;
varCHARACTERS_TO_NORMALIZE={
  "\u2018":'\'',
  "\u2019":'\'',
  "\u201A":'\'',
  "\u201B":'\'',
  "\u201C":'"',
  "\u201D":'"',
  "\u201E":'"',
  "\u201F":'"',
  "\xBC":'1/4',
  "\xBD":'1/2',
  "\xBE":'3/4'
};
varnormalizationRegex=null;

functionnormalize(text){
  if(!normalizationRegex){
    varreplace=Object.keys(CHARACTERS_TO_NORMALIZE).join('');
    normalizationRegex=newRegExp("[".concat(replace,"]"),'g');
  }

  returntext.replace(normalizationRegex,function(ch){
    returnCHARACTERS_TO_NORMALIZE[ch];
  });
}

varPDFFindController=
/*#__PURE__*/
function(){
  functionPDFFindController(_ref){
    varlinkService=_ref.linkService,
        _ref$eventBus=_ref.eventBus,
        eventBus=_ref$eventBus===void0?(0,_ui_utils.getGlobalEventBus)():_ref$eventBus;

    _classCallCheck(this,PDFFindController);

    this._linkService=linkService;
    this._eventBus=eventBus;

    this._reset();

    eventBus.on('findbarclose',this._onFindBarClose.bind(this));
  }

  _createClass(PDFFindController,[{
    key:"setDocument",
    value:functionsetDocument(pdfDocument){
      if(this._pdfDocument){
        this._reset();
      }

      if(!pdfDocument){
        return;
      }

      this._pdfDocument=pdfDocument;

      this._firstPageCapability.resolve();
    }
  },{
    key:"executeCommand",
    value:functionexecuteCommand(cmd,state){
      var_this=this;

      if(!state){
        return;
      }

      varpdfDocument=this._pdfDocument;

      if(this._state===null||this._shouldDirtyMatch(cmd,state)){
        this._dirtyMatch=true;
      }

      this._state=state;

      if(cmd!=='findhighlightallchange'){
        this._updateUIState(FindState.PENDING);
      }

      this._firstPageCapability.promise.then(function(){
        if(!_this._pdfDocument||pdfDocument&&_this._pdfDocument!==pdfDocument){
          return;
        }

        _this._extractText();

        varfindbarClosed=!_this._highlightMatches;
        varpendingTimeout=!!_this._findTimeout;

        if(_this._findTimeout){
          clearTimeout(_this._findTimeout);
          _this._findTimeout=null;
        }

        if(cmd==='find'){
          _this._findTimeout=setTimeout(function(){
            _this._nextMatch();

            _this._findTimeout=null;
          },FIND_TIMEOUT);
        }elseif(_this._dirtyMatch){
          _this._nextMatch();
        }elseif(cmd==='findagain'){
          _this._nextMatch();

          if(findbarClosed&&_this._state.highlightAll){
            _this._updateAllPages();
          }
        }elseif(cmd==='findhighlightallchange'){
          if(pendingTimeout){
            _this._nextMatch();
          }else{
            _this._highlightMatches=true;
          }

          _this._updateAllPages();
        }else{
          _this._nextMatch();
        }
      });
    }
  },{
    key:"scrollMatchIntoView",
    value:functionscrollMatchIntoView(_ref2){
      var_ref2$element=_ref2.element,
          element=_ref2$element===void0?null:_ref2$element,
          _ref2$pageIndex=_ref2.pageIndex,
          pageIndex=_ref2$pageIndex===void0?-1:_ref2$pageIndex,
          _ref2$matchIndex=_ref2.matchIndex,
          matchIndex=_ref2$matchIndex===void0?-1:_ref2$matchIndex;

      if(!this._scrollMatches||!element){
        return;
      }elseif(matchIndex===-1||matchIndex!==this._selected.matchIdx){
        return;
      }elseif(pageIndex===-1||pageIndex!==this._selected.pageIdx){
        return;
      }

      this._scrollMatches=false;
      varspot={
        top:MATCH_SCROLL_OFFSET_TOP,
        left:MATCH_SCROLL_OFFSET_LEFT
      };
      (0,_ui_utils.scrollIntoView)(element,spot,true);
    }
  },{
    key:"_reset",
    value:function_reset(){
      this._highlightMatches=false;
      this._scrollMatches=false;
      this._pdfDocument=null;
      this._pageMatches=[];
      this._pageMatchesLength=[];
      this._state=null;
      this._selected={
        pageIdx:-1,
        matchIdx:-1
      };
      this._offset={
        pageIdx:null,
        matchIdx:null,
        wrapped:false
      };
      this._extractTextPromises=[];
      this._pageContents=[];
      this._matchesCountTotal=0;
      this._pagesToSearch=null;
      this._pendingFindMatches=Object.create(null);
      this._resumePageIdx=null;
      this._dirtyMatch=false;
      clearTimeout(this._findTimeout);
      this._findTimeout=null;
      this._firstPageCapability=(0,_pdfjsLib.createPromiseCapability)();
    }
  },{
    key:"_shouldDirtyMatch",
    value:function_shouldDirtyMatch(cmd,state){
      if(state.query!==this._state.query){
        returntrue;
      }

      switch(cmd){
        case'findagain':
          varpageNumber=this._selected.pageIdx+1;
          varlinkService=this._linkService;

          if(pageNumber>=1&&pageNumber<=linkService.pagesCount&&pageNumber!==linkService.page&&!linkService.isPageVisible(pageNumber)){
            returntrue;
          }

          returnfalse;

        case'findhighlightallchange':
          returnfalse;
      }

      returntrue;
    }
  },{
    key:"_prepareMatches",
    value:function_prepareMatches(matchesWithLength,matches,matchesLength){
      functionisSubTerm(matchesWithLength,currentIndex){
        varcurrentElem=matchesWithLength[currentIndex];
        varnextElem=matchesWithLength[currentIndex+1];

        if(currentIndex<matchesWithLength.length-1&&currentElem.match===nextElem.match){
          currentElem.skipped=true;
          returntrue;
        }

        for(vari=currentIndex-1;i>=0;i--){
          varprevElem=matchesWithLength[i];

          if(prevElem.skipped){
            continue;
          }

          if(prevElem.match+prevElem.matchLength<currentElem.match){
            break;
          }

          if(prevElem.match+prevElem.matchLength>=currentElem.match+currentElem.matchLength){
            currentElem.skipped=true;
            returntrue;
          }
        }

        returnfalse;
      }

      matchesWithLength.sort(function(a,b){
        returna.match===b.match?a.matchLength-b.matchLength:a.match-b.match;
      });

      for(vari=0,len=matchesWithLength.length;i<len;i++){
        if(isSubTerm(matchesWithLength,i)){
          continue;
        }

        matches.push(matchesWithLength[i].match);
        matchesLength.push(matchesWithLength[i].matchLength);
      }
    }
  },{
    key:"_isEntireWord",
    value:function_isEntireWord(content,startIdx,length){
      if(startIdx>0){
        varfirst=content.charCodeAt(startIdx);
        varlimit=content.charCodeAt(startIdx-1);

        if((0,_pdf_find_utils.getCharacterType)(first)===(0,_pdf_find_utils.getCharacterType)(limit)){
          returnfalse;
        }
      }

      varendIdx=startIdx+length-1;

      if(endIdx<content.length-1){
        varlast=content.charCodeAt(endIdx);

        var_limit=content.charCodeAt(endIdx+1);

        if((0,_pdf_find_utils.getCharacterType)(last)===(0,_pdf_find_utils.getCharacterType)(_limit)){
          returnfalse;
        }
      }

      returntrue;
    }
  },{
    key:"_calculatePhraseMatch",
    value:function_calculatePhraseMatch(query,pageIndex,pageContent,entireWord){
      varmatches=[];
      varqueryLen=query.length;
      varmatchIdx=-queryLen;

      while(true){
        matchIdx=pageContent.indexOf(query,matchIdx+queryLen);

        if(matchIdx===-1){
          break;
        }

        if(entireWord&&!this._isEntireWord(pageContent,matchIdx,queryLen)){
          continue;
        }

        matches.push(matchIdx);
      }

      this._pageMatches[pageIndex]=matches;
    }
  },{
    key:"_calculateWordMatch",
    value:function_calculateWordMatch(query,pageIndex,pageContent,entireWord){
      varmatchesWithLength=[];
      varqueryArray=query.match(/\S+/g);

      for(vari=0,len=queryArray.length;i<len;i++){
        varsubquery=queryArray[i];
        varsubqueryLen=subquery.length;
        varmatchIdx=-subqueryLen;

        while(true){
          matchIdx=pageContent.indexOf(subquery,matchIdx+subqueryLen);

          if(matchIdx===-1){
            break;
          }

          if(entireWord&&!this._isEntireWord(pageContent,matchIdx,subqueryLen)){
            continue;
          }

          matchesWithLength.push({
            match:matchIdx,
            matchLength:subqueryLen,
            skipped:false
          });
        }
      }

      this._pageMatchesLength[pageIndex]=[];
      this._pageMatches[pageIndex]=[];

      this._prepareMatches(matchesWithLength,this._pageMatches[pageIndex],this._pageMatchesLength[pageIndex]);
    }
  },{
    key:"_calculateMatch",
    value:function_calculateMatch(pageIndex){
      varpageContent=this._pageContents[pageIndex];
      varquery=this._query;
      var_this$_state=this._state,
          caseSensitive=_this$_state.caseSensitive,
          entireWord=_this$_state.entireWord,
          phraseSearch=_this$_state.phraseSearch;

      if(query.length===0){
        return;
      }

      if(!caseSensitive){
        pageContent=pageContent.toLowerCase();
        query=query.toLowerCase();
      }

      if(phraseSearch){
        this._calculatePhraseMatch(query,pageIndex,pageContent,entireWord);
      }else{
        this._calculateWordMatch(query,pageIndex,pageContent,entireWord);
      }

      if(this._state.highlightAll){
        this._updatePage(pageIndex);
      }

      if(this._resumePageIdx===pageIndex){
        this._resumePageIdx=null;

        this._nextPageMatch();
      }

      varpageMatchesCount=this._pageMatches[pageIndex].length;

      if(pageMatchesCount>0){
        this._matchesCountTotal+=pageMatchesCount;

        this._updateUIResultsCount();
      }
    }
  },{
    key:"_extractText",
    value:function_extractText(){
      var_this2=this;

      if(this._extractTextPromises.length>0){
        return;
      }

      varpromise=Promise.resolve();

      var_loop=function_loop(i,ii){
        varextractTextCapability=(0,_pdfjsLib.createPromiseCapability)();
        _this2._extractTextPromises[i]=extractTextCapability.promise;
        promise=promise.then(function(){
          return_this2._pdfDocument.getPage(i+1).then(function(pdfPage){
            returnpdfPage.getTextContent({
              normalizeWhitespace:true
            });
          }).then(function(textContent){
            vartextItems=textContent.items;
            varstrBuf=[];

            for(varj=0,jj=textItems.length;j<jj;j++){
              strBuf.push(textItems[j].str);
            }

            _this2._pageContents[i]=normalize(strBuf.join(''));
            extractTextCapability.resolve(i);
          },function(reason){
            console.error("Unabletogettextcontentforpage".concat(i+1),reason);
            _this2._pageContents[i]='';
            extractTextCapability.resolve(i);
          });
        });
      };

      for(vari=0,ii=this._linkService.pagesCount;i<ii;i++){
        _loop(i,ii);
      }
    }
  },{
    key:"_updatePage",
    value:function_updatePage(index){
      if(this._scrollMatches&&this._selected.pageIdx===index){
        this._linkService.page=index+1;
      }

      this._eventBus.dispatch('updatetextlayermatches',{
        source:this,
        pageIndex:index
      });
    }
  },{
    key:"_updateAllPages",
    value:function_updateAllPages(){
      this._eventBus.dispatch('updatetextlayermatches',{
        source:this,
        pageIndex:-1
      });
    }
  },{
    key:"_nextMatch",
    value:function_nextMatch(){
      var_this3=this;

      varprevious=this._state.findPrevious;
      varcurrentPageIndex=this._linkService.page-1;
      varnumPages=this._linkService.pagesCount;
      this._highlightMatches=true;

      if(this._dirtyMatch){
        this._dirtyMatch=false;
        this._selected.pageIdx=this._selected.matchIdx=-1;
        this._offset.pageIdx=currentPageIndex;
        this._offset.matchIdx=null;
        this._offset.wrapped=false;
        this._resumePageIdx=null;
        this._pageMatches.length=0;
        this._pageMatchesLength.length=0;
        this._matchesCountTotal=0;

        this._updateAllPages();

        for(vari=0;i<numPages;i++){
          if(this._pendingFindMatches[i]===true){
            continue;
          }

          this._pendingFindMatches[i]=true;

          this._extractTextPromises[i].then(function(pageIdx){
            delete_this3._pendingFindMatches[pageIdx];

            _this3._calculateMatch(pageIdx);
          });
        }
      }

      if(this._query===''){
        this._updateUIState(FindState.FOUND);

        return;
      }

      if(this._resumePageIdx){
        return;
      }

      varoffset=this._offset;
      this._pagesToSearch=numPages;

      if(offset.matchIdx!==null){
        varnumPageMatches=this._pageMatches[offset.pageIdx].length;

        if(!previous&&offset.matchIdx+1<numPageMatches||previous&&offset.matchIdx>0){
          offset.matchIdx=previous?offset.matchIdx-1:offset.matchIdx+1;

          this._updateMatch(true);

          return;
        }

        this._advanceOffsetPage(previous);
      }

      this._nextPageMatch();
    }
  },{
    key:"_matchesReady",
    value:function_matchesReady(matches){
      varoffset=this._offset;
      varnumMatches=matches.length;
      varprevious=this._state.findPrevious;

      if(numMatches){
        offset.matchIdx=previous?numMatches-1:0;

        this._updateMatch(true);

        returntrue;
      }

      this._advanceOffsetPage(previous);

      if(offset.wrapped){
        offset.matchIdx=null;

        if(this._pagesToSearch<0){
          this._updateMatch(false);

          returntrue;
        }
      }

      returnfalse;
    }
  },{
    key:"_nextPageMatch",
    value:function_nextPageMatch(){
      if(this._resumePageIdx!==null){
        console.error('Therecanonlybeonependingpage.');
      }

      varmatches=null;

      do{
        varpageIdx=this._offset.pageIdx;
        matches=this._pageMatches[pageIdx];

        if(!matches){
          this._resumePageIdx=pageIdx;
          break;
        }
      }while(!this._matchesReady(matches));
    }
  },{
    key:"_advanceOffsetPage",
    value:function_advanceOffsetPage(previous){
      varoffset=this._offset;
      varnumPages=this._linkService.pagesCount;
      offset.pageIdx=previous?offset.pageIdx-1:offset.pageIdx+1;
      offset.matchIdx=null;
      this._pagesToSearch--;

      if(offset.pageIdx>=numPages||offset.pageIdx<0){
        offset.pageIdx=previous?numPages-1:0;
        offset.wrapped=true;
      }
    }
  },{
    key:"_updateMatch",
    value:function_updateMatch(){
      varfound=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      varstate=FindState.NOT_FOUND;
      varwrapped=this._offset.wrapped;
      this._offset.wrapped=false;

      if(found){
        varpreviousPage=this._selected.pageIdx;
        this._selected.pageIdx=this._offset.pageIdx;
        this._selected.matchIdx=this._offset.matchIdx;
        state=wrapped?FindState.WRAPPED:FindState.FOUND;

        if(previousPage!==-1&&previousPage!==this._selected.pageIdx){
          this._updatePage(previousPage);
        }
      }

      this._updateUIState(state,this._state.findPrevious);

      if(this._selected.pageIdx!==-1){
        this._scrollMatches=true;

        this._updatePage(this._selected.pageIdx);
      }
    }
  },{
    key:"_onFindBarClose",
    value:function_onFindBarClose(evt){
      var_this4=this;

      varpdfDocument=this._pdfDocument;

      this._firstPageCapability.promise.then(function(){
        if(!_this4._pdfDocument||pdfDocument&&_this4._pdfDocument!==pdfDocument){
          return;
        }

        if(_this4._findTimeout){
          clearTimeout(_this4._findTimeout);
          _this4._findTimeout=null;
        }

        if(_this4._resumePageIdx){
          _this4._resumePageIdx=null;
          _this4._dirtyMatch=true;
        }

        _this4._updateUIState(FindState.FOUND);

        _this4._highlightMatches=false;

        _this4._updateAllPages();
      });
    }
  },{
    key:"_requestMatchesCount",
    value:function_requestMatchesCount(){
      var_this$_selected=this._selected,
          pageIdx=_this$_selected.pageIdx,
          matchIdx=_this$_selected.matchIdx;
      varcurrent=0,
          total=this._matchesCountTotal;

      if(matchIdx!==-1){
        for(vari=0;i<pageIdx;i++){
          current+=this._pageMatches[i]&&this._pageMatches[i].length||0;
        }

        current+=matchIdx+1;
      }

      if(current<1||current>total){
        current=total=0;
      }

      return{
        current:current,
        total:total
      };
    }
  },{
    key:"_updateUIResultsCount",
    value:function_updateUIResultsCount(){
      this._eventBus.dispatch('updatefindmatchescount',{
        source:this,
        matchesCount:this._requestMatchesCount()
      });
    }
  },{
    key:"_updateUIState",
    value:function_updateUIState(state,previous){
      this._eventBus.dispatch('updatefindcontrolstate',{
        source:this,
        state:state,
        previous:previous,
        matchesCount:this._requestMatchesCount()
      });
    }
  },{
    key:"highlightMatches",
    get:functionget(){
      returnthis._highlightMatches;
    }
  },{
    key:"pageMatches",
    get:functionget(){
      returnthis._pageMatches;
    }
  },{
    key:"pageMatchesLength",
    get:functionget(){
      returnthis._pageMatchesLength;
    }
  },{
    key:"selected",
    get:functionget(){
      returnthis._selected;
    }
  },{
    key:"state",
    get:functionget(){
      returnthis._state;
    }
  },{
    key:"_query",
    get:functionget(){
      if(this._state.query!==this._rawQuery){
        this._rawQuery=this._state.query;
        this._normalizedQuery=normalize(this._state.query);
      }

      returnthis._normalizedQuery;
    }
  }]);

  returnPDFFindController;
}();

exports.PDFFindController=PDFFindController;

/***/}),
/*19*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.getCharacterType=getCharacterType;
exports.CharacterType=void0;
varCharacterType={
  SPACE:0,
  ALPHA_LETTER:1,
  PUNCT:2,
  HAN_LETTER:3,
  KATAKANA_LETTER:4,
  HIRAGANA_LETTER:5,
  HALFWIDTH_KATAKANA_LETTER:6,
  THAI_LETTER:7
};
exports.CharacterType=CharacterType;

functionisAlphabeticalScript(charCode){
  returncharCode<0x2E80;
}

functionisAscii(charCode){
  return(charCode&0xFF80)===0;
}

functionisAsciiAlpha(charCode){
  returncharCode>=0x61&&charCode<=0x7A||charCode>=0x41&&charCode<=0x5A;
}

functionisAsciiDigit(charCode){
  returncharCode>=0x30&&charCode<=0x39;
}

functionisAsciiSpace(charCode){
  returncharCode===0x20||charCode===0x09||charCode===0x0D||charCode===0x0A;
}

functionisHan(charCode){
  returncharCode>=0x3400&&charCode<=0x9FFF||charCode>=0xF900&&charCode<=0xFAFF;
}

functionisKatakana(charCode){
  returncharCode>=0x30A0&&charCode<=0x30FF;
}

functionisHiragana(charCode){
  returncharCode>=0x3040&&charCode<=0x309F;
}

functionisHalfwidthKatakana(charCode){
  returncharCode>=0xFF60&&charCode<=0xFF9F;
}

functionisThai(charCode){
  return(charCode&0xFF80)===0x0E00;
}

functiongetCharacterType(charCode){
  if(isAlphabeticalScript(charCode)){
    if(isAscii(charCode)){
      if(isAsciiSpace(charCode)){
        returnCharacterType.SPACE;
      }elseif(isAsciiAlpha(charCode)||isAsciiDigit(charCode)||charCode===0x5F){
        returnCharacterType.ALPHA_LETTER;
      }

      returnCharacterType.PUNCT;
    }elseif(isThai(charCode)){
      returnCharacterType.THAI_LETTER;
    }elseif(charCode===0xA0){
      returnCharacterType.SPACE;
    }

    returnCharacterType.ALPHA_LETTER;
  }

  if(isHan(charCode)){
    returnCharacterType.HAN_LETTER;
  }elseif(isKatakana(charCode)){
    returnCharacterType.KATAKANA_LETTER;
  }elseif(isHiragana(charCode)){
    returnCharacterType.HIRAGANA_LETTER;
  }elseif(isHalfwidthKatakana(charCode)){
    returnCharacterType.HALFWIDTH_KATAKANA_LETTER;
  }

  returnCharacterType.ALPHA_LETTER;
}

/***/}),
/*20*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.isDestHashesEqual=isDestHashesEqual;
exports.isDestArraysEqual=isDestArraysEqual;
exports.PDFHistory=void0;

var_ui_utils=__webpack_require__(5);

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_slicedToArray(arr,i){return_arrayWithHoles(arr)||_iterableToArrayLimit(arr,i)||_nonIterableRest();}

function_nonIterableRest(){thrownewTypeError("Invalidattempttodestructurenon-iterableinstance");}

function_iterableToArrayLimit(arr,i){var_arr=[];var_n=true;var_d=false;var_e=undefined;try{for(var_i=arr[Symbol.iterator](),_s;!(_n=(_s=_i.next()).done);_n=true){_arr.push(_s.value);if(i&&_arr.length===i)break;}}catch(err){_d=true;_e=err;}finally{try{if(!_n&&_i["return"]!=null)_i["return"]();}finally{if(_d)throw_e;}}return_arr;}

function_arrayWithHoles(arr){if(Array.isArray(arr))returnarr;}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varHASH_CHANGE_TIMEOUT=1000;
varPOSITION_UPDATED_THRESHOLD=50;
varUPDATE_VIEWAREA_TIMEOUT=1000;

functiongetCurrentHash(){
  returndocument.location.hash;
}

functionparseCurrentHash(linkService){
  varhash=unescape(getCurrentHash()).substring(1);
  varparams=(0,_ui_utils.parseQueryString)(hash);
  varpage=params.page|0;

  if(!(Number.isInteger(page)&&page>0&&page<=linkService.pagesCount)){
    page=null;
  }

  return{
    hash:hash,
    page:page,
    rotation:linkService.rotation
  };
}

varPDFHistory=
/*#__PURE__*/
function(){
  functionPDFHistory(_ref){
    var_this=this;

    varlinkService=_ref.linkService,
        eventBus=_ref.eventBus;

    _classCallCheck(this,PDFHistory);

    this.linkService=linkService;
    this.eventBus=eventBus||(0,_ui_utils.getGlobalEventBus)();
    this.initialized=false;
    this.initialBookmark=null;
    this.initialRotation=null;
    this._boundEvents=Object.create(null);
    this._isViewerInPresentationMode=false;
    this._isPagesLoaded=false;
    this.eventBus.on('presentationmodechanged',function(evt){
      _this._isViewerInPresentationMode=evt.active||evt.switchInProgress;
    });
    this.eventBus.on('pagesloaded',function(evt){
      _this._isPagesLoaded=!!evt.pagesCount;
    });
  }

  _createClass(PDFHistory,[{
    key:"initialize",
    value:functioninitialize(_ref2){
      varfingerprint=_ref2.fingerprint,
          _ref2$resetHistory=_ref2.resetHistory,
          resetHistory=_ref2$resetHistory===void0?false:_ref2$resetHistory,
          _ref2$updateUrl=_ref2.updateUrl,
          updateUrl=_ref2$updateUrl===void0?false:_ref2$updateUrl;

      if(!fingerprint||typeoffingerprint!=='string'){
        console.error('PDFHistory.initialize:The"fingerprint"mustbeanon-emptystring.');
        return;
      }

      varreInitialized=this.initialized&&this.fingerprint!==fingerprint;
      this.fingerprint=fingerprint;
      this._updateUrl=updateUrl===true;

      if(!this.initialized){
        this._bindEvents();
      }

      varstate=window.history.state;
      this.initialized=true;
      this.initialBookmark=null;
      this.initialRotation=null;
      this._popStateInProgress=false;
      this._blockHashChange=0;
      this._currentHash=getCurrentHash();
      this._numPositionUpdates=0;
      this._uid=this._maxUid=0;
      this._destination=null;
      this._position=null;

      if(!this._isValidState(state,true)||resetHistory){
        var_parseCurrentHash=parseCurrentHash(this.linkService),
            hash=_parseCurrentHash.hash,
            page=_parseCurrentHash.page,
            rotation=_parseCurrentHash.rotation;

        if(!hash||reInitialized||resetHistory){
          this._pushOrReplaceState(null,true);

          return;
        }

        this._pushOrReplaceState({
          hash:hash,
          page:page,
          rotation:rotation
        },true);

        return;
      }

      vardestination=state.destination;

      this._updateInternalState(destination,state.uid,true);

      if(this._uid>this._maxUid){
        this._maxUid=this._uid;
      }

      if(destination.rotation!==undefined){
        this.initialRotation=destination.rotation;
      }

      if(destination.dest){
        this.initialBookmark=JSON.stringify(destination.dest);
        this._destination.page=null;
      }elseif(destination.hash){
        this.initialBookmark=destination.hash;
      }elseif(destination.page){
        this.initialBookmark="page=".concat(destination.page);
      }
    }
  },{
    key:"push",
    value:functionpush(_ref3){
      var_this2=this;

      var_ref3$namedDest=_ref3.namedDest,
          namedDest=_ref3$namedDest===void0?null:_ref3$namedDest,
          explicitDest=_ref3.explicitDest,
          pageNumber=_ref3.pageNumber;

      if(!this.initialized){
        return;
      }

      if(namedDest&&typeofnamedDest!=='string'){
        console.error('PDFHistory.push:'+"\"".concat(namedDest,"\"isnotavalidnamedDestparameter."));
        return;
      }elseif(!Array.isArray(explicitDest)){
        console.error('PDFHistory.push:'+"\"".concat(explicitDest,"\"isnotavalidexplicitDestparameter."));
        return;
      }elseif(!(Number.isInteger(pageNumber)&&pageNumber>0&&pageNumber<=this.linkService.pagesCount)){
        if(pageNumber!==null||this._destination){
          console.error('PDFHistory.push:'+"\"".concat(pageNumber,"\"isnotavalidpageNumberparameter."));
          return;
        }
      }

      varhash=namedDest||JSON.stringify(explicitDest);

      if(!hash){
        return;
      }

      varforceReplace=false;

      if(this._destination&&(isDestHashesEqual(this._destination.hash,hash)||isDestArraysEqual(this._destination.dest,explicitDest))){
        if(this._destination.page){
          return;
        }

        forceReplace=true;
      }

      if(this._popStateInProgress&&!forceReplace){
        return;
      }

      this._pushOrReplaceState({
        dest:explicitDest,
        hash:hash,
        page:pageNumber,
        rotation:this.linkService.rotation
      },forceReplace);

      if(!this._popStateInProgress){
        this._popStateInProgress=true;
        Promise.resolve().then(function(){
          _this2._popStateInProgress=false;
        });
      }
    }
  },{
    key:"pushCurrentPosition",
    value:functionpushCurrentPosition(){
      if(!this.initialized||this._popStateInProgress){
        return;
      }

      this._tryPushCurrentPosition();
    }
  },{
    key:"back",
    value:functionback(){
      if(!this.initialized||this._popStateInProgress){
        return;
      }

      varstate=window.history.state;

      if(this._isValidState(state)&&state.uid>0){
        window.history.back();
      }
    }
  },{
    key:"forward",
    value:functionforward(){
      if(!this.initialized||this._popStateInProgress){
        return;
      }

      varstate=window.history.state;

      if(this._isValidState(state)&&state.uid<this._maxUid){
        window.history.forward();
      }
    }
  },{
    key:"_pushOrReplaceState",
    value:function_pushOrReplaceState(destination){
      varforceReplace=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
      varshouldReplace=forceReplace||!this._destination;
      varnewState={
        fingerprint:this.fingerprint,
        uid:shouldReplace?this._uid:this._uid+1,
        destination:destination
      };

      this._updateInternalState(destination,newState.uid);

      varnewUrl;

      if(this._updateUrl&&destination&&destination.hash){
        varbaseUrl=document.location.href.split('#')[0];

        if(!baseUrl.startsWith('file://')){
          newUrl="".concat(baseUrl,"#").concat(destination.hash);
        }
      }

      if(shouldReplace){
        if(newUrl){
          window.history.replaceState(newState,'',newUrl);
        }else{
          window.history.replaceState(newState,'');
        }
      }else{
        this._maxUid=this._uid;

        if(newUrl){
          window.history.pushState(newState,'',newUrl);
        }else{
          window.history.pushState(newState,'');
        }
      }
    }
  },{
    key:"_tryPushCurrentPosition",
    value:function_tryPushCurrentPosition(){
      vartemporary=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(!this._position){
        return;
      }

      varposition=this._position;

      if(temporary){
        position=Object.assign(Object.create(null),this._position);
        position.temporary=true;
      }

      if(!this._destination){
        this._pushOrReplaceState(position);

        return;
      }

      if(this._destination.temporary){
        this._pushOrReplaceState(position,true);

        return;
      }

      if(this._destination.hash===position.hash){
        return;
      }

      if(!this._destination.page&&(POSITION_UPDATED_THRESHOLD<=0||this._numPositionUpdates<=POSITION_UPDATED_THRESHOLD)){
        return;
      }

      varforceReplace=false;

      if(this._destination.page>=position.first&&this._destination.page<=position.page){
        if(this._destination.dest||!this._destination.first){
          return;
        }

        forceReplace=true;
      }

      this._pushOrReplaceState(position,forceReplace);
    }
  },{
    key:"_isValidState",
    value:function_isValidState(state){
      varcheckReload=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;

      if(!state){
        returnfalse;
      }

      if(state.fingerprint!==this.fingerprint){
        if(checkReload){
          if(typeofstate.fingerprint!=='string'||state.fingerprint.length!==this.fingerprint.length){
            returnfalse;
          }

          var_performance$getEntri=performance.getEntriesByType('navigation'),
              _performance$getEntri2=_slicedToArray(_performance$getEntri,1),
              perfEntry=_performance$getEntri2[0];

          if(!perfEntry||perfEntry.type!=='reload'){
            returnfalse;
          }
        }else{
          returnfalse;
        }
      }

      if(!Number.isInteger(state.uid)||state.uid<0){
        returnfalse;
      }

      if(state.destination===null||_typeof(state.destination)!=='object'){
        returnfalse;
      }

      returntrue;
    }
  },{
    key:"_updateInternalState",
    value:function_updateInternalState(destination,uid){
      varremoveTemporary=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;

      if(this._updateViewareaTimeout){
        clearTimeout(this._updateViewareaTimeout);
        this._updateViewareaTimeout=null;
      }

      if(removeTemporary&&destination&&destination.temporary){
        deletedestination.temporary;
      }

      this._destination=destination;
      this._uid=uid;
      this._numPositionUpdates=0;
    }
  },{
    key:"_updateViewarea",
    value:function_updateViewarea(_ref4){
      var_this3=this;

      varlocation=_ref4.location;

      if(this._updateViewareaTimeout){
        clearTimeout(this._updateViewareaTimeout);
        this._updateViewareaTimeout=null;
      }

      this._position={
        hash:this._isViewerInPresentationMode?"page=".concat(location.pageNumber):location.pdfOpenParams.substring(1),
        page:this.linkService.page,
        first:location.pageNumber,
        rotation:location.rotation
      };

      if(this._popStateInProgress){
        return;
      }

      if(POSITION_UPDATED_THRESHOLD>0&&this._isPagesLoaded&&this._destination&&!this._destination.page){
        this._numPositionUpdates++;
      }

      if(UPDATE_VIEWAREA_TIMEOUT>0){
        this._updateViewareaTimeout=setTimeout(function(){
          if(!_this3._popStateInProgress){
            _this3._tryPushCurrentPosition(true);
          }

          _this3._updateViewareaTimeout=null;
        },UPDATE_VIEWAREA_TIMEOUT);
      }
    }
  },{
    key:"_popState",
    value:function_popState(_ref5){
      var_this4=this;

      varstate=_ref5.state;
      varnewHash=getCurrentHash(),
          hashChanged=this._currentHash!==newHash;
      this._currentHash=newHash;

      if(!state||false){
        this._uid++;

        var_parseCurrentHash2=parseCurrentHash(this.linkService),
            hash=_parseCurrentHash2.hash,
            page=_parseCurrentHash2.page,
            rotation=_parseCurrentHash2.rotation;

        this._pushOrReplaceState({
          hash:hash,
          page:page,
          rotation:rotation
        },true);

        return;
      }

      if(!this._isValidState(state)){
        return;
      }

      this._popStateInProgress=true;

      if(hashChanged){
        this._blockHashChange++;
        (0,_ui_utils.waitOnEventOrTimeout)({
          target:window,
          name:'hashchange',
          delay:HASH_CHANGE_TIMEOUT
        }).then(function(){
          _this4._blockHashChange--;
        });
      }

      vardestination=state.destination;

      this._updateInternalState(destination,state.uid,true);

      if(this._uid>this._maxUid){
        this._maxUid=this._uid;
      }

      if((0,_ui_utils.isValidRotation)(destination.rotation)){
        this.linkService.rotation=destination.rotation;
      }

      if(destination.dest){
        this.linkService.navigateTo(destination.dest);
      }elseif(destination.hash){
        this.linkService.setHash(destination.hash);
      }elseif(destination.page){
        this.linkService.page=destination.page;
      }

      Promise.resolve().then(function(){
        _this4._popStateInProgress=false;
      });
    }
  },{
    key:"_bindEvents",
    value:function_bindEvents(){
      var_this5=this;

      var_boundEvents=this._boundEvents,
          eventBus=this.eventBus;
      _boundEvents.updateViewarea=this._updateViewarea.bind(this);
      _boundEvents.popState=this._popState.bind(this);

      _boundEvents.pageHide=function(evt){
        if(!_this5._destination||_this5._destination.temporary){
          _this5._tryPushCurrentPosition();
        }
      };

      eventBus.on('updateviewarea',_boundEvents.updateViewarea);
      window.addEventListener('popstate',_boundEvents.popState);
      window.addEventListener('pagehide',_boundEvents.pageHide);
    }
  },{
    key:"popStateInProgress",
    get:functionget(){
      returnthis.initialized&&(this._popStateInProgress||this._blockHashChange>0);
    }
  }]);

  returnPDFHistory;
}();

exports.PDFHistory=PDFHistory;

functionisDestHashesEqual(destHash,pushHash){
  if(typeofdestHash!=='string'||typeofpushHash!=='string'){
    returnfalse;
  }

  if(destHash===pushHash){
    returntrue;
  }

  var_parseQueryString=(0,_ui_utils.parseQueryString)(destHash),
      nameddest=_parseQueryString.nameddest;

  if(nameddest===pushHash){
    returntrue;
  }

  returnfalse;
}

functionisDestArraysEqual(firstDest,secondDest){
  functionisEntryEqual(first,second){
    if(_typeof(first)!==_typeof(second)){
      returnfalse;
    }

    if(Array.isArray(first)||Array.isArray(second)){
      returnfalse;
    }

    if(first!==null&&_typeof(first)==='object'&&second!==null){
      if(Object.keys(first).length!==Object.keys(second).length){
        returnfalse;
      }

      for(varkeyinfirst){
        if(!isEntryEqual(first[key],second[key])){
          returnfalse;
        }
      }

      returntrue;
    }

    returnfirst===second||Number.isNaN(first)&&Number.isNaN(second);
  }

  if(!(Array.isArray(firstDest)&&Array.isArray(secondDest))){
    returnfalse;
  }

  if(firstDest.length!==secondDest.length){
    returnfalse;
  }

  for(vari=0,ii=firstDest.length;i<ii;i++){
    if(!isEntryEqual(firstDest[i],secondDest[i])){
      returnfalse;
    }
  }

  returntrue;
}

/***/}),
/*21*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.SimpleLinkService=exports.PDFLinkService=void0;

var_ui_utils=__webpack_require__(5);

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varPDFLinkService=
/*#__PURE__*/
function(){
  functionPDFLinkService(){
    var_ref=arguments.length>0&&arguments[0]!==undefined?arguments[0]:{},
        eventBus=_ref.eventBus,
        _ref$externalLinkTarg=_ref.externalLinkTarget,
        externalLinkTarget=_ref$externalLinkTarg===void0?null:_ref$externalLinkTarg,
        _ref$externalLinkRel=_ref.externalLinkRel,
        externalLinkRel=_ref$externalLinkRel===void0?null:_ref$externalLinkRel;

    _classCallCheck(this,PDFLinkService);

    this.eventBus=eventBus||(0,_ui_utils.getGlobalEventBus)();
    this.externalLinkTarget=externalLinkTarget;
    this.externalLinkRel=externalLinkRel;
    this.baseUrl=null;
    this.pdfDocument=null;
    this.pdfViewer=null;
    this.pdfHistory=null;
    this._pagesRefCache=null;
  }

  _createClass(PDFLinkService,[{
    key:"setDocument",
    value:functionsetDocument(pdfDocument){
      varbaseUrl=arguments.length>1&&arguments[1]!==undefined?arguments[1]:null;
      this.baseUrl=baseUrl;
      this.pdfDocument=pdfDocument;
      this._pagesRefCache=Object.create(null);
    }
  },{
    key:"setViewer",
    value:functionsetViewer(pdfViewer){
      this.pdfViewer=pdfViewer;
    }
  },{
    key:"setHistory",
    value:functionsetHistory(pdfHistory){
      this.pdfHistory=pdfHistory;
    }
  },{
    key:"navigateTo",
    value:functionnavigateTo(dest){
      var_this=this;

      vargoToDestination=functiongoToDestination(_ref2){
        varnamedDest=_ref2.namedDest,
            explicitDest=_ref2.explicitDest;
        vardestRef=explicitDest[0],
            pageNumber;

        if(destRefinstanceofObject){
          pageNumber=_this._cachedPageNumber(destRef);

          if(pageNumber===null){
            _this.pdfDocument.getPageIndex(destRef).then(function(pageIndex){
              _this.cachePageRef(pageIndex+1,destRef);

              goToDestination({
                namedDest:namedDest,
                explicitDest:explicitDest
              });
            })["catch"](function(){
              console.error("PDFLinkService.navigateTo:\"".concat(destRef,"\"isnot")+"avalidpagereference,fordest=\"".concat(dest,"\"."));
            });

            return;
          }
        }elseif(Number.isInteger(destRef)){
          pageNumber=destRef+1;
        }else{
          console.error("PDFLinkService.navigateTo:\"".concat(destRef,"\"isnot")+"avaliddestinationreference,fordest=\"".concat(dest,"\"."));
          return;
        }

        if(!pageNumber||pageNumber<1||pageNumber>_this.pagesCount){
          console.error("PDFLinkService.navigateTo:\"".concat(pageNumber,"\"isnot")+"avalidpagenumber,fordest=\"".concat(dest,"\"."));
          return;
        }

        if(_this.pdfHistory){
          _this.pdfHistory.pushCurrentPosition();

          _this.pdfHistory.push({
            namedDest:namedDest,
            explicitDest:explicitDest,
            pageNumber:pageNumber
          });
        }

        _this.pdfViewer.scrollPageIntoView({
          pageNumber:pageNumber,
          destArray:explicitDest
        });
      };

      newPromise(function(resolve,reject){
        if(typeofdest==='string'){
          _this.pdfDocument.getDestination(dest).then(function(destArray){
            resolve({
              namedDest:dest,
              explicitDest:destArray
            });
          });

          return;
        }

        resolve({
          namedDest:'',
          explicitDest:dest
        });
      }).then(function(data){
        if(!Array.isArray(data.explicitDest)){
          console.error("PDFLinkService.navigateTo:\"".concat(data.explicitDest,"\"is")+"notavaliddestinationarray,fordest=\"".concat(dest,"\"."));
          return;
        }

        goToDestination(data);
      });
    }
  },{
    key:"getDestinationHash",
    value:functiongetDestinationHash(dest){
      if(typeofdest==='string'){
        returnthis.getAnchorUrl('#'+escape(dest));
      }

      if(Array.isArray(dest)){
        varstr=JSON.stringify(dest);
        returnthis.getAnchorUrl('#'+escape(str));
      }

      returnthis.getAnchorUrl('');
    }
  },{
    key:"getAnchorUrl",
    value:functiongetAnchorUrl(anchor){
      return(this.baseUrl||'')+anchor;
    }
  },{
    key:"setHash",
    value:functionsetHash(hash){
      varpageNumber,dest;

      if(hash.includes('=')){
        varparams=(0,_ui_utils.parseQueryString)(hash);

        if('search'inparams){
          this.eventBus.dispatch('findfromurlhash',{
            source:this,
            query:params['search'].replace(/"/g,''),
            phraseSearch:params['phrase']==='true'
          });
        }

        if('nameddest'inparams){
          this.navigateTo(params.nameddest);
          return;
        }

        if('page'inparams){
          pageNumber=params.page|0||1;
        }

        if('zoom'inparams){
          varzoomArgs=params.zoom.split(',');
          varzoomArg=zoomArgs[0];
          varzoomArgNumber=parseFloat(zoomArg);

          if(!zoomArg.includes('Fit')){
            dest=[null,{
              name:'XYZ'
            },zoomArgs.length>1?zoomArgs[1]|0:null,zoomArgs.length>2?zoomArgs[2]|0:null,zoomArgNumber?zoomArgNumber/100:zoomArg];
          }else{
            if(zoomArg==='Fit'||zoomArg==='FitB'){
              dest=[null,{
                name:zoomArg
              }];
            }elseif(zoomArg==='FitH'||zoomArg==='FitBH'||zoomArg==='FitV'||zoomArg==='FitBV'){
              dest=[null,{
                name:zoomArg
              },zoomArgs.length>1?zoomArgs[1]|0:null];
            }elseif(zoomArg==='FitR'){
              if(zoomArgs.length!==5){
                console.error('PDFLinkService.setHash:Notenoughparametersfor"FitR".');
              }else{
                dest=[null,{
                  name:zoomArg
                },zoomArgs[1]|0,zoomArgs[2]|0,zoomArgs[3]|0,zoomArgs[4]|0];
              }
            }else{
              console.error("PDFLinkService.setHash:\"".concat(zoomArg,"\"isnot")+'avalidzoomvalue.');
            }
          }
        }

        if(dest){
          this.pdfViewer.scrollPageIntoView({
            pageNumber:pageNumber||this.page,
            destArray:dest,
            allowNegativeOffset:true
          });
        }elseif(pageNumber){
          this.page=pageNumber;
        }

        if('pagemode'inparams){
          this.eventBus.dispatch('pagemode',{
            source:this,
            mode:params.pagemode
          });
        }
      }else{
        dest=unescape(hash);

        try{
          dest=JSON.parse(dest);

          if(!Array.isArray(dest)){
            dest=dest.toString();
          }
        }catch(ex){}

        if(typeofdest==='string'||isValidExplicitDestination(dest)){
          this.navigateTo(dest);
          return;
        }

        console.error("PDFLinkService.setHash:\"".concat(unescape(hash),"\"isnot")+'avaliddestination.');
      }
    }
  },{
    key:"executeNamedAction",
    value:functionexecuteNamedAction(action){
      switch(action){
        case'GoBack':
          if(this.pdfHistory){
            this.pdfHistory.back();
          }

          break;

        case'GoForward':
          if(this.pdfHistory){
            this.pdfHistory.forward();
          }

          break;

        case'NextPage':
          if(this.page<this.pagesCount){
            this.page++;
          }

          break;

        case'PrevPage':
          if(this.page>1){
            this.page--;
          }

          break;

        case'LastPage':
          this.page=this.pagesCount;
          break;

        case'FirstPage':
          this.page=1;
          break;

        default:
          break;
      }

      this.eventBus.dispatch('namedaction',{
        source:this,
        action:action
      });
    }
  },{
    key:"cachePageRef",
    value:functioncachePageRef(pageNum,pageRef){
      if(!pageRef){
        return;
      }

      varrefStr=pageRef.num+''+pageRef.gen+'R';
      this._pagesRefCache[refStr]=pageNum;
    }
  },{
    key:"_cachedPageNumber",
    value:function_cachedPageNumber(pageRef){
      varrefStr=pageRef.num+''+pageRef.gen+'R';
      returnthis._pagesRefCache&&this._pagesRefCache[refStr]||null;
    }
  },{
    key:"isPageVisible",
    value:functionisPageVisible(pageNumber){
      returnthis.pdfViewer.isPageVisible(pageNumber);
    }
  },{
    key:"pagesCount",
    get:functionget(){
      returnthis.pdfDocument?this.pdfDocument.numPages:0;
    }
  },{
    key:"page",
    get:functionget(){
      returnthis.pdfViewer.currentPageNumber;
    },
    set:functionset(value){
      this.pdfViewer.currentPageNumber=value;
    }
  },{
    key:"rotation",
    get:functionget(){
      returnthis.pdfViewer.pagesRotation;
    },
    set:functionset(value){
      this.pdfViewer.pagesRotation=value;
    }
  }]);

  returnPDFLinkService;
}();

exports.PDFLinkService=PDFLinkService;

functionisValidExplicitDestination(dest){
  if(!Array.isArray(dest)){
    returnfalse;
  }

  vardestLength=dest.length,
      allowNull=true;

  if(destLength<2){
    returnfalse;
  }

  varpage=dest[0];

  if(!(_typeof(page)==='object'&&Number.isInteger(page.num)&&Number.isInteger(page.gen))&&!(Number.isInteger(page)&&page>=0)){
    returnfalse;
  }

  varzoom=dest[1];

  if(!(_typeof(zoom)==='object'&&typeofzoom.name==='string')){
    returnfalse;
  }

  switch(zoom.name){
    case'XYZ':
      if(destLength!==5){
        returnfalse;
      }

      break;

    case'Fit':
    case'FitB':
      returndestLength===2;

    case'FitH':
    case'FitBH':
    case'FitV':
    case'FitBV':
      if(destLength!==3){
        returnfalse;
      }

      break;

    case'FitR':
      if(destLength!==6){
        returnfalse;
      }

      allowNull=false;
      break;

    default:
      returnfalse;
  }

  for(vari=2;i<destLength;i++){
    varparam=dest[i];

    if(!(typeofparam==='number'||allowNull&&param===null)){
      returnfalse;
    }
  }

  returntrue;
}

varSimpleLinkService=
/*#__PURE__*/
function(){
  functionSimpleLinkService(){
    _classCallCheck(this,SimpleLinkService);

    this.externalLinkTarget=null;
    this.externalLinkRel=null;
  }

  _createClass(SimpleLinkService,[{
    key:"navigateTo",
    value:functionnavigateTo(dest){}
  },{
    key:"getDestinationHash",
    value:functiongetDestinationHash(dest){
      return'#';
    }
  },{
    key:"getAnchorUrl",
    value:functiongetAnchorUrl(hash){
      return'#';
    }
  },{
    key:"setHash",
    value:functionsetHash(hash){}
  },{
    key:"executeNamedAction",
    value:functionexecuteNamedAction(action){}
  },{
    key:"cachePageRef",
    value:functioncachePageRef(pageNum,pageRef){}
  },{
    key:"isPageVisible",
    value:functionisPageVisible(pageNumber){
      returntrue;
    }
  },{
    key:"pagesCount",
    get:functionget(){
      return0;
    }
  },{
    key:"page",
    get:functionget(){
      return0;
    },
    set:functionset(value){}
  },{
    key:"rotation",
    get:functionget(){
      return0;
    },
    set:functionset(value){}
  }]);

  returnSimpleLinkService;
}();

exports.SimpleLinkService=SimpleLinkService;

/***/}),
/*22*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFOutlineViewer=void0;

var_pdfjsLib=__webpack_require__(7);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varDEFAULT_TITLE="\u2013";

varPDFOutlineViewer=
/*#__PURE__*/
function(){
  functionPDFOutlineViewer(_ref){
    varcontainer=_ref.container,
        linkService=_ref.linkService,
        eventBus=_ref.eventBus;

    _classCallCheck(this,PDFOutlineViewer);

    this.container=container;
    this.linkService=linkService;
    this.eventBus=eventBus;
    this.reset();
    eventBus.on('toggleoutlinetree',this.toggleOutlineTree.bind(this));
  }

  _createClass(PDFOutlineViewer,[{
    key:"reset",
    value:functionreset(){
      this.outline=null;
      this.lastToggleIsShow=true;
      this.container.textContent='';
      this.container.classList.remove('outlineWithDeepNesting');
    }
  },{
    key:"_dispatchEvent",
    value:function_dispatchEvent(outlineCount){
      this.eventBus.dispatch('outlineloaded',{
        source:this,
        outlineCount:outlineCount
      });
    }
  },{
    key:"_bindLink",
    value:function_bindLink(element,_ref2){
      varurl=_ref2.url,
          newWindow=_ref2.newWindow,
          dest=_ref2.dest;
      varlinkService=this.linkService;

      if(url){
        (0,_pdfjsLib.addLinkAttributes)(element,{
          url:url,
          target:newWindow?_pdfjsLib.LinkTarget.BLANK:linkService.externalLinkTarget,
          rel:linkService.externalLinkRel
        });
        return;
      }

      element.href=linkService.getDestinationHash(dest);

      element.onclick=function(){
        if(dest){
          linkService.navigateTo(dest);
        }

        returnfalse;
      };
    }
  },{
    key:"_setStyles",
    value:function_setStyles(element,_ref3){
      varbold=_ref3.bold,
          italic=_ref3.italic;
      varstyleStr='';

      if(bold){
        styleStr+='font-weight:bold;';
      }

      if(italic){
        styleStr+='font-style:italic;';
      }

      if(styleStr){
        element.setAttribute('style',styleStr);
      }
    }
  },{
    key:"_addToggleButton",
    value:function_addToggleButton(div,_ref4){
      var_this=this;

      varcount=_ref4.count,
          items=_ref4.items;
      vartoggler=document.createElement('div');
      toggler.className='outlineItemToggler';

      if(count<0&&Math.abs(count)===items.length){
        toggler.classList.add('outlineItemsHidden');
      }

      toggler.onclick=function(evt){
        evt.stopPropagation();
        toggler.classList.toggle('outlineItemsHidden');

        if(evt.shiftKey){
          varshouldShowAll=!toggler.classList.contains('outlineItemsHidden');

          _this._toggleOutlineItem(div,shouldShowAll);
        }
      };

      div.insertBefore(toggler,div.firstChild);
    }
  },{
    key:"_toggleOutlineItem",
    value:function_toggleOutlineItem(root){
      varshow=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
      this.lastToggleIsShow=show;
      var_iteratorNormalCompletion=true;
      var_didIteratorError=false;
      var_iteratorError=undefined;

      try{
        for(var_iterator=root.querySelectorAll('.outlineItemToggler')[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
          vartoggler=_step.value;
          toggler.classList.toggle('outlineItemsHidden',!show);
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
    key:"toggleOutlineTree",
    value:functiontoggleOutlineTree(){
      if(!this.outline){
        return;
      }

      this._toggleOutlineItem(this.container,!this.lastToggleIsShow);
    }
  },{
    key:"render",
    value:functionrender(_ref5){
      varoutline=_ref5.outline;
      varoutlineCount=0;

      if(this.outline){
        this.reset();
      }

      this.outline=outline||null;

      if(!outline){
        this._dispatchEvent(outlineCount);

        return;
      }

      varfragment=document.createDocumentFragment();
      varqueue=[{
        parent:fragment,
        items:this.outline
      }];
      varhasAnyNesting=false;

      while(queue.length>0){
        varlevelData=queue.shift();
        var_iteratorNormalCompletion2=true;
        var_didIteratorError2=false;
        var_iteratorError2=undefined;

        try{
          for(var_iterator2=levelData.items[Symbol.iterator](),_step2;!(_iteratorNormalCompletion2=(_step2=_iterator2.next()).done);_iteratorNormalCompletion2=true){
            varitem=_step2.value;
            vardiv=document.createElement('div');
            div.className='outlineItem';
            varelement=document.createElement('a');

            this._bindLink(element,item);

            this._setStyles(element,item);

            element.textContent=(0,_pdfjsLib.removeNullCharacters)(item.title)||DEFAULT_TITLE;
            div.appendChild(element);

            if(item.items.length>0){
              hasAnyNesting=true;

              this._addToggleButton(div,item);

              varitemsDiv=document.createElement('div');
              itemsDiv.className='outlineItems';
              div.appendChild(itemsDiv);
              queue.push({
                parent:itemsDiv,
                items:item.items
              });
            }

            levelData.parent.appendChild(div);
            outlineCount++;
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

      if(hasAnyNesting){
        this.container.classList.add('outlineWithDeepNesting');
        this.lastToggleIsShow=fragment.querySelectorAll('.outlineItemsHidden').length===0;
      }

      this.container.appendChild(fragment);

      this._dispatchEvent(outlineCount);
    }
  }]);

  returnPDFOutlineViewer;
}();

exports.PDFOutlineViewer=PDFOutlineViewer;

/***/}),
/*23*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFPresentationMode=void0;

var_ui_utils=__webpack_require__(5);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varDELAY_BEFORE_RESETTING_SWITCH_IN_PROGRESS=1500;
varDELAY_BEFORE_HIDING_CONTROLS=3000;
varACTIVE_SELECTOR='pdfPresentationMode';
varCONTROLS_SELECTOR='pdfPresentationModeControls';
varMOUSE_SCROLL_COOLDOWN_TIME=50;
varPAGE_SWITCH_THRESHOLD=0.1;
varSWIPE_MIN_DISTANCE_THRESHOLD=50;
varSWIPE_ANGLE_THRESHOLD=Math.PI/6;

varPDFPresentationMode=
/*#__PURE__*/
function(){
  functionPDFPresentationMode(_ref){
    var_this=this;

    varcontainer=_ref.container,
        _ref$viewer=_ref.viewer,
        viewer=_ref$viewer===void0?null:_ref$viewer,
        pdfViewer=_ref.pdfViewer,
        eventBus=_ref.eventBus,
        _ref$contextMenuItems=_ref.contextMenuItems,
        contextMenuItems=_ref$contextMenuItems===void0?null:_ref$contextMenuItems;

    _classCallCheck(this,PDFPresentationMode);

    this.container=container;
    this.viewer=viewer||container.firstElementChild;
    this.pdfViewer=pdfViewer;
    this.eventBus=eventBus;
    this.active=false;
    this.args=null;
    this.contextMenuOpen=false;
    this.mouseScrollTimeStamp=0;
    this.mouseScrollDelta=0;
    this.touchSwipeState=null;

    if(contextMenuItems){
      contextMenuItems.contextFirstPage.addEventListener('click',function(){
        _this.contextMenuOpen=false;

        _this.eventBus.dispatch('firstpage',{
          source:_this
        });
      });
      contextMenuItems.contextLastPage.addEventListener('click',function(){
        _this.contextMenuOpen=false;

        _this.eventBus.dispatch('lastpage',{
          source:_this
        });
      });
      contextMenuItems.contextPageRotateCw.addEventListener('click',function(){
        _this.contextMenuOpen=false;

        _this.eventBus.dispatch('rotatecw',{
          source:_this
        });
      });
      contextMenuItems.contextPageRotateCcw.addEventListener('click',function(){
        _this.contextMenuOpen=false;

        _this.eventBus.dispatch('rotateccw',{
          source:_this
        });
      });
    }
  }

  _createClass(PDFPresentationMode,[{
    key:"request",
    value:functionrequest(){
      if(this.switchInProgress||this.active||!this.viewer.hasChildNodes()){
        returnfalse;
      }

      this._addFullscreenChangeListeners();

      this._setSwitchInProgress();

      this._notifyStateChange();

      if(this.container.requestFullscreen){
        this.container.requestFullscreen();
      }elseif(this.container.mozRequestFullScreen){
        this.container.mozRequestFullScreen();
      }elseif(this.container.webkitRequestFullscreen){
        this.container.webkitRequestFullscreen(Element.ALLOW_KEYBOARD_INPUT);
      }elseif(this.container.msRequestFullscreen){
        this.container.msRequestFullscreen();
      }else{
        returnfalse;
      }

      this.args={
        page:this.pdfViewer.currentPageNumber,
        previousScale:this.pdfViewer.currentScaleValue
      };
      returntrue;
    }
  },{
    key:"_mouseWheel",
    value:function_mouseWheel(evt){
      if(!this.active){
        return;
      }

      evt.preventDefault();
      vardelta=(0,_ui_utils.normalizeWheelEventDelta)(evt);
      varcurrentTime=newDate().getTime();
      varstoredTime=this.mouseScrollTimeStamp;

      if(currentTime>storedTime&&currentTime-storedTime<MOUSE_SCROLL_COOLDOWN_TIME){
        return;
      }

      if(this.mouseScrollDelta>0&&delta<0||this.mouseScrollDelta<0&&delta>0){
        this._resetMouseScrollState();
      }

      this.mouseScrollDelta+=delta;

      if(Math.abs(this.mouseScrollDelta)>=PAGE_SWITCH_THRESHOLD){
        vartotalDelta=this.mouseScrollDelta;

        this._resetMouseScrollState();

        varsuccess=totalDelta>0?this._goToPreviousPage():this._goToNextPage();

        if(success){
          this.mouseScrollTimeStamp=currentTime;
        }
      }
    }
  },{
    key:"_goToPreviousPage",
    value:function_goToPreviousPage(){
      varpage=this.pdfViewer.currentPageNumber;

      if(page<=1){
        returnfalse;
      }

      this.pdfViewer.currentPageNumber=page-1;
      returntrue;
    }
  },{
    key:"_goToNextPage",
    value:function_goToNextPage(){
      varpage=this.pdfViewer.currentPageNumber;

      if(page>=this.pdfViewer.pagesCount){
        returnfalse;
      }

      this.pdfViewer.currentPageNumber=page+1;
      returntrue;
    }
  },{
    key:"_notifyStateChange",
    value:function_notifyStateChange(){
      this.eventBus.dispatch('presentationmodechanged',{
        source:this,
        active:this.active,
        switchInProgress:!!this.switchInProgress
      });
    }
  },{
    key:"_setSwitchInProgress",
    value:function_setSwitchInProgress(){
      var_this2=this;

      if(this.switchInProgress){
        clearTimeout(this.switchInProgress);
      }

      this.switchInProgress=setTimeout(function(){
        _this2._removeFullscreenChangeListeners();

        delete_this2.switchInProgress;

        _this2._notifyStateChange();
      },DELAY_BEFORE_RESETTING_SWITCH_IN_PROGRESS);
    }
  },{
    key:"_resetSwitchInProgress",
    value:function_resetSwitchInProgress(){
      if(this.switchInProgress){
        clearTimeout(this.switchInProgress);
        deletethis.switchInProgress;
      }
    }
  },{
    key:"_enter",
    value:function_enter(){
      var_this3=this;

      this.active=true;

      this._resetSwitchInProgress();

      this._notifyStateChange();

      this.container.classList.add(ACTIVE_SELECTOR);
      setTimeout(function(){
        _this3.pdfViewer.currentPageNumber=_this3.args.page;
        _this3.pdfViewer.currentScaleValue='page-fit';
      },0);

      this._addWindowListeners();

      this._showControls();

      this.contextMenuOpen=false;
      this.container.setAttribute('contextmenu','viewerContextMenu');
      window.getSelection().removeAllRanges();
    }
  },{
    key:"_exit",
    value:function_exit(){
      var_this4=this;

      varpage=this.pdfViewer.currentPageNumber;
      this.container.classList.remove(ACTIVE_SELECTOR);
      setTimeout(function(){
        _this4.active=false;

        _this4._removeFullscreenChangeListeners();

        _this4._notifyStateChange();

        _this4.pdfViewer.currentScaleValue=_this4.args.previousScale;
        _this4.pdfViewer.currentPageNumber=page;
        _this4.args=null;
      },0);

      this._removeWindowListeners();

      this._hideControls();

      this._resetMouseScrollState();

      this.container.removeAttribute('contextmenu');
      this.contextMenuOpen=false;
    }
  },{
    key:"_mouseDown",
    value:function_mouseDown(evt){
      if(this.contextMenuOpen){
        this.contextMenuOpen=false;
        evt.preventDefault();
        return;
      }

      if(evt.button===0){
        varisInternalLink=evt.target.href&&evt.target.classList.contains('internalLink');

        if(!isInternalLink){
          evt.preventDefault();

          if(evt.shiftKey){
            this._goToPreviousPage();
          }else{
            this._goToNextPage();
          }
        }
      }
    }
  },{
    key:"_contextMenu",
    value:function_contextMenu(){
      this.contextMenuOpen=true;
    }
  },{
    key:"_showControls",
    value:function_showControls(){
      var_this5=this;

      if(this.controlsTimeout){
        clearTimeout(this.controlsTimeout);
      }else{
        this.container.classList.add(CONTROLS_SELECTOR);
      }

      this.controlsTimeout=setTimeout(function(){
        _this5.container.classList.remove(CONTROLS_SELECTOR);

        delete_this5.controlsTimeout;
      },DELAY_BEFORE_HIDING_CONTROLS);
    }
  },{
    key:"_hideControls",
    value:function_hideControls(){
      if(!this.controlsTimeout){
        return;
      }

      clearTimeout(this.controlsTimeout);
      this.container.classList.remove(CONTROLS_SELECTOR);
      deletethis.controlsTimeout;
    }
  },{
    key:"_resetMouseScrollState",
    value:function_resetMouseScrollState(){
      this.mouseScrollTimeStamp=0;
      this.mouseScrollDelta=0;
    }
  },{
    key:"_touchSwipe",
    value:function_touchSwipe(evt){
      if(!this.active){
        return;
      }

      if(evt.touches.length>1){
        this.touchSwipeState=null;
        return;
      }

      switch(evt.type){
        case'touchstart':
          this.touchSwipeState={
            startX:evt.touches[0].pageX,
            startY:evt.touches[0].pageY,
            endX:evt.touches[0].pageX,
            endY:evt.touches[0].pageY
          };
          break;

        case'touchmove':
          if(this.touchSwipeState===null){
            return;
          }

          this.touchSwipeState.endX=evt.touches[0].pageX;
          this.touchSwipeState.endY=evt.touches[0].pageY;
          evt.preventDefault();
          break;

        case'touchend':
          if(this.touchSwipeState===null){
            return;
          }

          vardelta=0;
          vardx=this.touchSwipeState.endX-this.touchSwipeState.startX;
          vardy=this.touchSwipeState.endY-this.touchSwipeState.startY;
          varabsAngle=Math.abs(Math.atan2(dy,dx));

          if(Math.abs(dx)>SWIPE_MIN_DISTANCE_THRESHOLD&&(absAngle<=SWIPE_ANGLE_THRESHOLD||absAngle>=Math.PI-SWIPE_ANGLE_THRESHOLD)){
            delta=dx;
          }elseif(Math.abs(dy)>SWIPE_MIN_DISTANCE_THRESHOLD&&Math.abs(absAngle-Math.PI/2)<=SWIPE_ANGLE_THRESHOLD){
            delta=dy;
          }

          if(delta>0){
            this._goToPreviousPage();
          }elseif(delta<0){
            this._goToNextPage();
          }

          break;
      }
    }
  },{
    key:"_addWindowListeners",
    value:function_addWindowListeners(){
      this.showControlsBind=this._showControls.bind(this);
      this.mouseDownBind=this._mouseDown.bind(this);
      this.mouseWheelBind=this._mouseWheel.bind(this);
      this.resetMouseScrollStateBind=this._resetMouseScrollState.bind(this);
      this.contextMenuBind=this._contextMenu.bind(this);
      this.touchSwipeBind=this._touchSwipe.bind(this);
      window.addEventListener('mousemove',this.showControlsBind);
      window.addEventListener('mousedown',this.mouseDownBind);
      window.addEventListener('wheel',this.mouseWheelBind);
      window.addEventListener('keydown',this.resetMouseScrollStateBind);
      window.addEventListener('contextmenu',this.contextMenuBind);
      window.addEventListener('touchstart',this.touchSwipeBind);
      window.addEventListener('touchmove',this.touchSwipeBind);
      window.addEventListener('touchend',this.touchSwipeBind);
    }
  },{
    key:"_removeWindowListeners",
    value:function_removeWindowListeners(){
      window.removeEventListener('mousemove',this.showControlsBind);
      window.removeEventListener('mousedown',this.mouseDownBind);
      window.removeEventListener('wheel',this.mouseWheelBind);
      window.removeEventListener('keydown',this.resetMouseScrollStateBind);
      window.removeEventListener('contextmenu',this.contextMenuBind);
      window.removeEventListener('touchstart',this.touchSwipeBind);
      window.removeEventListener('touchmove',this.touchSwipeBind);
      window.removeEventListener('touchend',this.touchSwipeBind);
      deletethis.showControlsBind;
      deletethis.mouseDownBind;
      deletethis.mouseWheelBind;
      deletethis.resetMouseScrollStateBind;
      deletethis.contextMenuBind;
      deletethis.touchSwipeBind;
    }
  },{
    key:"_fullscreenChange",
    value:function_fullscreenChange(){
      if(this.isFullscreen){
        this._enter();
      }else{
        this._exit();
      }
    }
  },{
    key:"_addFullscreenChangeListeners",
    value:function_addFullscreenChangeListeners(){
      this.fullscreenChangeBind=this._fullscreenChange.bind(this);
      window.addEventListener('fullscreenchange',this.fullscreenChangeBind);
      window.addEventListener('mozfullscreenchange',this.fullscreenChangeBind);
      window.addEventListener('webkitfullscreenchange',this.fullscreenChangeBind);
      window.addEventListener('MSFullscreenChange',this.fullscreenChangeBind);
    }
  },{
    key:"_removeFullscreenChangeListeners",
    value:function_removeFullscreenChangeListeners(){
      window.removeEventListener('fullscreenchange',this.fullscreenChangeBind);
      window.removeEventListener('mozfullscreenchange',this.fullscreenChangeBind);
      window.removeEventListener('webkitfullscreenchange',this.fullscreenChangeBind);
      window.removeEventListener('MSFullscreenChange',this.fullscreenChangeBind);
      deletethis.fullscreenChangeBind;
    }
  },{
    key:"isFullscreen",
    get:functionget(){
      return!!(document.fullscreenElement||document.mozFullScreen||document.webkitIsFullScreen||document.msFullscreenElement);
    }
  }]);

  returnPDFPresentationMode;
}();

exports.PDFPresentationMode=PDFPresentationMode;

/***/}),
/*24*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFSidebarResizer=void0;

var_ui_utils=__webpack_require__(5);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varSIDEBAR_WIDTH_VAR='--sidebar-width';
varSIDEBAR_MIN_WIDTH=200;
varSIDEBAR_RESIZING_CLASS='sidebarResizing';

varPDFSidebarResizer=
/*#__PURE__*/
function(){
  functionPDFSidebarResizer(options,eventBus){
    var_this=this;

    varl10n=arguments.length>2&&arguments[2]!==undefined?arguments[2]:_ui_utils.NullL10n;

    _classCallCheck(this,PDFSidebarResizer);

    this.enabled=false;
    this.isRTL=false;
    this.sidebarOpen=false;
    this.doc=document.documentElement;
    this._width=null;
    this._outerContainerWidth=null;
    this._boundEvents=Object.create(null);
    this.outerContainer=options.outerContainer;
    this.resizer=options.resizer;
    this.eventBus=eventBus;
    this.l10n=l10n;

    if(typeofCSS==='undefined'||typeofCSS.supports!=='function'||!CSS.supports(SIDEBAR_WIDTH_VAR,"calc(-1*".concat(SIDEBAR_MIN_WIDTH,"px)"))){
      console.warn('PDFSidebarResizer:'+'Thebrowserdoesnotsupportresizingofthesidebar.');
      return;
    }

    this.enabled=true;
    this.resizer.classList.remove('hidden');
    this.l10n.getDirection().then(function(dir){
      _this.isRTL=dir==='rtl';
    });

    this._addEventListeners();
  }

  _createClass(PDFSidebarResizer,[{
    key:"_updateWidth",
    value:function_updateWidth(){
      varwidth=arguments.length>0&&arguments[0]!==undefined?arguments[0]:0;

      if(!this.enabled){
        returnfalse;
      }

      varmaxWidth=Math.floor(this.outerContainerWidth/2);

      if(width>maxWidth){
        width=maxWidth;
      }

      if(width<SIDEBAR_MIN_WIDTH){
        width=SIDEBAR_MIN_WIDTH;
      }

      if(width===this._width){
        returnfalse;
      }

      this._width=width;
      this.doc.style.setProperty(SIDEBAR_WIDTH_VAR,"".concat(width,"px"));
      returntrue;
    }
  },{
    key:"_mouseMove",
    value:function_mouseMove(evt){
      varwidth=evt.clientX;

      if(this.isRTL){
        width=this.outerContainerWidth-width;
      }

      this._updateWidth(width);
    }
  },{
    key:"_mouseUp",
    value:function_mouseUp(evt){
      this.outerContainer.classList.remove(SIDEBAR_RESIZING_CLASS);
      this.eventBus.dispatch('resize',{
        source:this
      });
      var_boundEvents=this._boundEvents;
      window.removeEventListener('mousemove',_boundEvents.mouseMove);
      window.removeEventListener('mouseup',_boundEvents.mouseUp);
    }
  },{
    key:"_addEventListeners",
    value:function_addEventListeners(){
      var_this2=this;

      if(!this.enabled){
        return;
      }

      var_boundEvents=this._boundEvents;
      _boundEvents.mouseMove=this._mouseMove.bind(this);
      _boundEvents.mouseUp=this._mouseUp.bind(this);
      this.resizer.addEventListener('mousedown',function(evt){
        if(evt.button!==0){
          return;
        }

        _this2.outerContainer.classList.add(SIDEBAR_RESIZING_CLASS);

        window.addEventListener('mousemove',_boundEvents.mouseMove);
        window.addEventListener('mouseup',_boundEvents.mouseUp);
      });
      this.eventBus.on('sidebarviewchanged',function(evt){
        _this2.sidebarOpen=!!(evt&&evt.view);
      });
      this.eventBus.on('resize',function(evt){
        if(evt&&evt.source===window){
          _this2._outerContainerWidth=null;

          if(_this2._width){
            if(_this2.sidebarOpen){
              _this2.outerContainer.classList.add(SIDEBAR_RESIZING_CLASS);

              varupdated=_this2._updateWidth(_this2._width);

              Promise.resolve().then(function(){
                _this2.outerContainer.classList.remove(SIDEBAR_RESIZING_CLASS);

                if(updated){
                  _this2.eventBus.dispatch('resize',{
                    source:_this2
                  });
                }
              });
            }else{
              _this2._updateWidth(_this2._width);
            }
          }
        }
      });
    }
  },{
    key:"outerContainerWidth",
    get:functionget(){
      if(!this._outerContainerWidth){
        this._outerContainerWidth=this.outerContainer.clientWidth;
      }

      returnthis._outerContainerWidth;
    }
  }]);

  returnPDFSidebarResizer;
}();

exports.PDFSidebarResizer=PDFSidebarResizer;

/***/}),
/*25*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFThumbnailViewer=void0;

var_ui_utils=__webpack_require__(5);

var_pdf_thumbnail_view=__webpack_require__(26);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varTHUMBNAIL_SCROLL_MARGIN=-19;
varTHUMBNAIL_SELECTED_CLASS='selected';

varPDFThumbnailViewer=
/*#__PURE__*/
function(){
  functionPDFThumbnailViewer(_ref){
    varcontainer=_ref.container,
        linkService=_ref.linkService,
        renderingQueue=_ref.renderingQueue,
        _ref$l10n=_ref.l10n,
        l10n=_ref$l10n===void0?_ui_utils.NullL10n:_ref$l10n;

    _classCallCheck(this,PDFThumbnailViewer);

    this.container=container;
    this.linkService=linkService;
    this.renderingQueue=renderingQueue;
    this.l10n=l10n;
    this.scroll=(0,_ui_utils.watchScroll)(this.container,this._scrollUpdated.bind(this));

    this._resetView();
  }

  _createClass(PDFThumbnailViewer,[{
    key:"_scrollUpdated",
    value:function_scrollUpdated(){
      this.renderingQueue.renderHighestPriority();
    }
  },{
    key:"getThumbnail",
    value:functiongetThumbnail(index){
      returnthis._thumbnails[index];
    }
  },{
    key:"_getVisibleThumbs",
    value:function_getVisibleThumbs(){
      return(0,_ui_utils.getVisibleElements)(this.container,this._thumbnails);
    }
  },{
    key:"scrollThumbnailIntoView",
    value:functionscrollThumbnailIntoView(pageNumber){
      if(!this.pdfDocument){
        return;
      }

      varthumbnailView=this._thumbnails[pageNumber-1];

      if(!thumbnailView){
        console.error('scrollThumbnailIntoView:Invalid"pageNumber"parameter.');
        return;
      }

      if(pageNumber!==this._currentPageNumber){
        varprevThumbnailView=this._thumbnails[this._currentPageNumber-1];
        prevThumbnailView.div.classList.remove(THUMBNAIL_SELECTED_CLASS);
        thumbnailView.div.classList.add(THUMBNAIL_SELECTED_CLASS);
      }

      varvisibleThumbs=this._getVisibleThumbs();

      varnumVisibleThumbs=visibleThumbs.views.length;

      if(numVisibleThumbs>0){
        varfirst=visibleThumbs.first.id;
        varlast=numVisibleThumbs>1?visibleThumbs.last.id:first;
        varshouldScroll=false;

        if(pageNumber<=first||pageNumber>=last){
          shouldScroll=true;
        }else{
          visibleThumbs.views.some(function(view){
            if(view.id!==pageNumber){
              returnfalse;
            }

            shouldScroll=view.percent<100;
            returntrue;
          });
        }

        if(shouldScroll){
          (0,_ui_utils.scrollIntoView)(thumbnailView.div,{
            top:THUMBNAIL_SCROLL_MARGIN
          });
        }
      }

      this._currentPageNumber=pageNumber;
    }
  },{
    key:"cleanup",
    value:functioncleanup(){
      _pdf_thumbnail_view.PDFThumbnailView.cleanup();
    }
  },{
    key:"_resetView",
    value:function_resetView(){
      this._thumbnails=[];
      this._currentPageNumber=1;
      this._pageLabels=null;
      this._pagesRotation=0;
      this._pagesRequests=[];
      this.container.textContent='';
    }
  },{
    key:"setDocument",
    value:functionsetDocument(pdfDocument){
      var_this=this;

      if(this.pdfDocument){
        this._cancelRendering();

        this._resetView();
      }

      this.pdfDocument=pdfDocument;

      if(!pdfDocument){
        return;
      }

      pdfDocument.getPage(1).then(function(firstPage){
        varpagesCount=pdfDocument.numPages;
        varviewport=firstPage.getViewport({
          scale:1
        });

        for(varpageNum=1;pageNum<=pagesCount;++pageNum){
          varthumbnail=new_pdf_thumbnail_view.PDFThumbnailView({
            container:_this.container,
            id:pageNum,
            defaultViewport:viewport.clone(),
            linkService:_this.linkService,
            renderingQueue:_this.renderingQueue,
            disableCanvasToImageConversion:false,
            l10n:_this.l10n
          });

          _this._thumbnails.push(thumbnail);
        }

        varthumbnailView=_this._thumbnails[_this._currentPageNumber-1];
        thumbnailView.div.classList.add(THUMBNAIL_SELECTED_CLASS);
      })["catch"](function(reason){
        console.error('Unabletoinitializethumbnailviewer',reason);
      });
    }
  },{
    key:"_cancelRendering",
    value:function_cancelRendering(){
      for(vari=0,ii=this._thumbnails.length;i<ii;i++){
        if(this._thumbnails[i]){
          this._thumbnails[i].cancelRendering();
        }
      }
    }
  },{
    key:"setPageLabels",
    value:functionsetPageLabels(labels){
      if(!this.pdfDocument){
        return;
      }

      if(!labels){
        this._pageLabels=null;
      }elseif(!(Array.isArray(labels)&&this.pdfDocument.numPages===labels.length)){
        this._pageLabels=null;
        console.error('PDFThumbnailViewer_setPageLabels:Invalidpagelabels.');
      }else{
        this._pageLabels=labels;
      }

      for(vari=0,ii=this._thumbnails.length;i<ii;i++){
        varlabel=this._pageLabels&&this._pageLabels[i];

        this._thumbnails[i].setPageLabel(label);
      }
    }
  },{
    key:"_ensurePdfPageLoaded",
    value:function_ensurePdfPageLoaded(thumbView){
      var_this2=this;

      if(thumbView.pdfPage){
        returnPromise.resolve(thumbView.pdfPage);
      }

      varpageNumber=thumbView.id;

      if(this._pagesRequests[pageNumber]){
        returnthis._pagesRequests[pageNumber];
      }

      varpromise=this.pdfDocument.getPage(pageNumber).then(function(pdfPage){
        thumbView.setPdfPage(pdfPage);
        _this2._pagesRequests[pageNumber]=null;
        returnpdfPage;
      })["catch"](function(reason){
        console.error('Unabletogetpageforthumbview',reason);
        _this2._pagesRequests[pageNumber]=null;
      });
      this._pagesRequests[pageNumber]=promise;
      returnpromise;
    }
  },{
    key:"forceRendering",
    value:functionforceRendering(){
      var_this3=this;

      varvisibleThumbs=this._getVisibleThumbs();

      varthumbView=this.renderingQueue.getHighestPriority(visibleThumbs,this._thumbnails,this.scroll.down);

      if(thumbView){
        this._ensurePdfPageLoaded(thumbView).then(function(){
          _this3.renderingQueue.renderView(thumbView);
        });

        returntrue;
      }

      returnfalse;
    }
  },{
    key:"pagesRotation",
    get:functionget(){
      returnthis._pagesRotation;
    },
    set:functionset(rotation){
      if(!(0,_ui_utils.isValidRotation)(rotation)){
        thrownewError('Invalidthumbnailsrotationangle.');
      }

      if(!this.pdfDocument){
        return;
      }

      if(this._pagesRotation===rotation){
        return;
      }

      this._pagesRotation=rotation;

      for(vari=0,ii=this._thumbnails.length;i<ii;i++){
        this._thumbnails[i].update(rotation);
      }
    }
  }]);

  returnPDFThumbnailViewer;
}();

exports.PDFThumbnailViewer=PDFThumbnailViewer;

/***/}),
/*26*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFThumbnailView=void0;

var_pdfjsLib=__webpack_require__(7);

var_ui_utils=__webpack_require__(5);

var_pdf_rendering_queue=__webpack_require__(11);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varMAX_NUM_SCALING_STEPS=3;
varTHUMBNAIL_CANVAS_BORDER_WIDTH=1;
varTHUMBNAIL_WIDTH=98;

varTempImageFactory=functionTempImageFactoryClosure(){
  vartempCanvasCache=null;
  return{
    getCanvas:functiongetCanvas(width,height){
      vartempCanvas=tempCanvasCache;

      if(!tempCanvas){
        tempCanvas=document.createElement('canvas');
        tempCanvasCache=tempCanvas;
      }

      tempCanvas.width=width;
      tempCanvas.height=height;
      tempCanvas.mozOpaque=true;
      varctx=tempCanvas.getContext('2d',{
        alpha:false
      });
      ctx.save();
      ctx.fillStyle='rgb(255,255,255)';
      ctx.fillRect(0,0,width,height);
      ctx.restore();
      returntempCanvas;
    },
    destroyCanvas:functiondestroyCanvas(){
      vartempCanvas=tempCanvasCache;

      if(tempCanvas){
        tempCanvas.width=0;
        tempCanvas.height=0;
      }

      tempCanvasCache=null;
    }
  };
}();

varPDFThumbnailView=
/*#__PURE__*/
function(){
  functionPDFThumbnailView(_ref){
    varcontainer=_ref.container,
        id=_ref.id,
        defaultViewport=_ref.defaultViewport,
        linkService=_ref.linkService,
        renderingQueue=_ref.renderingQueue,
        _ref$disableCanvasToI=_ref.disableCanvasToImageConversion,
        disableCanvasToImageConversion=_ref$disableCanvasToI===void0?false:_ref$disableCanvasToI,
        _ref$l10n=_ref.l10n,
        l10n=_ref$l10n===void0?_ui_utils.NullL10n:_ref$l10n;

    _classCallCheck(this,PDFThumbnailView);

    this.id=id;
    this.renderingId='thumbnail'+id;
    this.pageLabel=null;
    this.pdfPage=null;
    this.rotation=0;
    this.viewport=defaultViewport;
    this.pdfPageRotate=defaultViewport.rotation;
    this.linkService=linkService;
    this.renderingQueue=renderingQueue;
    this.renderTask=null;
    this.renderingState=_pdf_rendering_queue.RenderingStates.INITIAL;
    this.resume=null;
    this.disableCanvasToImageConversion=disableCanvasToImageConversion;
    this.pageWidth=this.viewport.width;
    this.pageHeight=this.viewport.height;
    this.pageRatio=this.pageWidth/this.pageHeight;
    this.canvasWidth=THUMBNAIL_WIDTH;
    this.canvasHeight=this.canvasWidth/this.pageRatio|0;
    this.scale=this.canvasWidth/this.pageWidth;
    this.l10n=l10n;
    varanchor=document.createElement('a');
    anchor.href=linkService.getAnchorUrl('#page='+id);
    this.l10n.get('thumb_page_title',{
      page:id
    },'Page{{page}}').then(function(msg){
      anchor.title=msg;
    });

    anchor.onclick=function(){
      linkService.page=id;
      returnfalse;
    };

    this.anchor=anchor;
    vardiv=document.createElement('div');
    div.className='thumbnail';
    div.setAttribute('data-page-number',this.id);
    this.div=div;
    varring=document.createElement('div');
    ring.className='thumbnailSelectionRing';
    varborderAdjustment=2*THUMBNAIL_CANVAS_BORDER_WIDTH;
    ring.style.width=this.canvasWidth+borderAdjustment+'px';
    ring.style.height=this.canvasHeight+borderAdjustment+'px';
    this.ring=ring;
    div.appendChild(ring);
    anchor.appendChild(div);
    container.appendChild(anchor);
  }

  _createClass(PDFThumbnailView,[{
    key:"setPdfPage",
    value:functionsetPdfPage(pdfPage){
      this.pdfPage=pdfPage;
      this.pdfPageRotate=pdfPage.rotate;
      vartotalRotation=(this.rotation+this.pdfPageRotate)%360;
      this.viewport=pdfPage.getViewport({
        scale:1,
        rotation:totalRotation
      });
      this.reset();
    }
  },{
    key:"reset",
    value:functionreset(){
      this.cancelRendering();
      this.renderingState=_pdf_rendering_queue.RenderingStates.INITIAL;
      this.pageWidth=this.viewport.width;
      this.pageHeight=this.viewport.height;
      this.pageRatio=this.pageWidth/this.pageHeight;
      this.canvasHeight=this.canvasWidth/this.pageRatio|0;
      this.scale=this.canvasWidth/this.pageWidth;
      this.div.removeAttribute('data-loaded');
      varring=this.ring;
      varchildNodes=ring.childNodes;

      for(vari=childNodes.length-1;i>=0;i--){
        ring.removeChild(childNodes[i]);
      }

      varborderAdjustment=2*THUMBNAIL_CANVAS_BORDER_WIDTH;
      ring.style.width=this.canvasWidth+borderAdjustment+'px';
      ring.style.height=this.canvasHeight+borderAdjustment+'px';

      if(this.canvas){
        this.canvas.width=0;
        this.canvas.height=0;
        deletethis.canvas;
      }

      if(this.image){
        this.image.removeAttribute('src');
        deletethis.image;
      }
    }
  },{
    key:"update",
    value:functionupdate(rotation){
      if(typeofrotation!=='undefined'){
        this.rotation=rotation;
      }

      vartotalRotation=(this.rotation+this.pdfPageRotate)%360;
      this.viewport=this.viewport.clone({
        scale:1,
        rotation:totalRotation
      });
      this.reset();
    }
  },{
    key:"cancelRendering",
    value:functioncancelRendering(){
      if(this.renderTask){
        this.renderTask.cancel();
        this.renderTask=null;
      }

      this.resume=null;
    }
  },{
    key:"_getPageDrawContext",
    value:function_getPageDrawContext(){
      varnoCtxScale=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      varcanvas=document.createElement('canvas');
      this.canvas=canvas;
      canvas.mozOpaque=true;
      varctx=canvas.getContext('2d',{
        alpha:false
      });
      varoutputScale=(0,_ui_utils.getOutputScale)(ctx);
      canvas.width=this.canvasWidth*outputScale.sx|0;
      canvas.height=this.canvasHeight*outputScale.sy|0;
      canvas.style.width=this.canvasWidth+'px';
      canvas.style.height=this.canvasHeight+'px';

      if(!noCtxScale&&outputScale.scaled){
        ctx.scale(outputScale.sx,outputScale.sy);
      }

      returnctx;
    }
  },{
    key:"_convertCanvasToImage",
    value:function_convertCanvasToImage(){
      var_this=this;

      if(!this.canvas){
        return;
      }

      if(this.renderingState!==_pdf_rendering_queue.RenderingStates.FINISHED){
        return;
      }

      varid=this.renderingId;
      varclassName='thumbnailImage';

      if(this.disableCanvasToImageConversion){
        this.canvas.id=id;
        this.canvas.className=className;
        this.l10n.get('thumb_page_canvas',{
          page:this.pageId
        },'ThumbnailofPage{{page}}').then(function(msg){
          _this.canvas.setAttribute('aria-label',msg);
        });
        this.div.setAttribute('data-loaded',true);
        this.ring.appendChild(this.canvas);
        return;
      }

      varimage=document.createElement('img');
      image.id=id;
      image.className=className;
      this.l10n.get('thumb_page_canvas',{
        page:this.pageId
      },'ThumbnailofPage{{page}}').then(function(msg){
        image.setAttribute('aria-label',msg);
      });
      image.style.width=this.canvasWidth+'px';
      image.style.height=this.canvasHeight+'px';
      image.src=this.canvas.toDataURL();
      this.image=image;
      this.div.setAttribute('data-loaded',true);
      this.ring.appendChild(image);
      this.canvas.width=0;
      this.canvas.height=0;
      deletethis.canvas;
    }
  },{
    key:"draw",
    value:functiondraw(){
      var_this2=this;

      if(this.renderingState!==_pdf_rendering_queue.RenderingStates.INITIAL){
        console.error('Mustbeinnewstatebeforedrawing');
        returnPromise.resolve(undefined);
      }

      this.renderingState=_pdf_rendering_queue.RenderingStates.RUNNING;
      varrenderCapability=(0,_pdfjsLib.createPromiseCapability)();

      varfinishRenderTask=functionfinishRenderTask(error){
        if(renderTask===_this2.renderTask){
          _this2.renderTask=null;
        }

        if(errorinstanceof_pdfjsLib.RenderingCancelledException){
          renderCapability.resolve(undefined);
          return;
        }

        _this2.renderingState=_pdf_rendering_queue.RenderingStates.FINISHED;

        _this2._convertCanvasToImage();

        if(!error){
          renderCapability.resolve(undefined);
        }else{
          renderCapability.reject(error);
        }
      };

      varctx=this._getPageDrawContext();

      vardrawViewport=this.viewport.clone({
        scale:this.scale
      });

      varrenderContinueCallback=functionrenderContinueCallback(cont){
        if(!_this2.renderingQueue.isHighestPriority(_this2)){
          _this2.renderingState=_pdf_rendering_queue.RenderingStates.PAUSED;

          _this2.resume=function(){
            _this2.renderingState=_pdf_rendering_queue.RenderingStates.RUNNING;
            cont();
          };

          return;
        }

        cont();
      };

      varrenderContext={
        canvasContext:ctx,
        viewport:drawViewport
      };
      varrenderTask=this.renderTask=this.pdfPage.render(renderContext);
      renderTask.onContinue=renderContinueCallback;
      renderTask.promise.then(function(){
        finishRenderTask(null);
      },function(error){
        finishRenderTask(error);
      });
      returnrenderCapability.promise;
    }
  },{
    key:"setImage",
    value:functionsetImage(pageView){
      if(this.renderingState!==_pdf_rendering_queue.RenderingStates.INITIAL){
        return;
      }

      varimg=pageView.canvas;

      if(!img){
        return;
      }

      if(!this.pdfPage){
        this.setPdfPage(pageView.pdfPage);
      }

      this.renderingState=_pdf_rendering_queue.RenderingStates.FINISHED;

      varctx=this._getPageDrawContext(true);

      varcanvas=ctx.canvas;

      if(img.width<=2*canvas.width){
        ctx.drawImage(img,0,0,img.width,img.height,0,0,canvas.width,canvas.height);

        this._convertCanvasToImage();

        return;
      }

      varreducedWidth=canvas.width<<MAX_NUM_SCALING_STEPS;
      varreducedHeight=canvas.height<<MAX_NUM_SCALING_STEPS;
      varreducedImage=TempImageFactory.getCanvas(reducedWidth,reducedHeight);
      varreducedImageCtx=reducedImage.getContext('2d');

      while(reducedWidth>img.width||reducedHeight>img.height){
        reducedWidth>>=1;
        reducedHeight>>=1;
      }

      reducedImageCtx.drawImage(img,0,0,img.width,img.height,0,0,reducedWidth,reducedHeight);

      while(reducedWidth>2*canvas.width){
        reducedImageCtx.drawImage(reducedImage,0,0,reducedWidth,reducedHeight,0,0,reducedWidth>>1,reducedHeight>>1);
        reducedWidth>>=1;
        reducedHeight>>=1;
      }

      ctx.drawImage(reducedImage,0,0,reducedWidth,reducedHeight,0,0,canvas.width,canvas.height);

      this._convertCanvasToImage();
    }
  },{
    key:"setPageLabel",
    value:functionsetPageLabel(label){
      var_this3=this;

      this.pageLabel=typeoflabel==='string'?label:null;
      this.l10n.get('thumb_page_title',{
        page:this.pageId
      },'Page{{page}}').then(function(msg){
        _this3.anchor.title=msg;
      });

      if(this.renderingState!==_pdf_rendering_queue.RenderingStates.FINISHED){
        return;
      }

      this.l10n.get('thumb_page_canvas',{
        page:this.pageId
      },'ThumbnailofPage{{page}}').then(function(ariaLabel){
        if(_this3.image){
          _this3.image.setAttribute('aria-label',ariaLabel);
        }elseif(_this3.disableCanvasToImageConversion&&_this3.canvas){
          _this3.canvas.setAttribute('aria-label',ariaLabel);
        }
      });
    }
  },{
    key:"pageId",
    get:functionget(){
      returnthis.pageLabel!==null?this.pageLabel:this.id;
    }
  }],[{
    key:"cleanup",
    value:functioncleanup(){
      TempImageFactory.destroyCanvas();
    }
  }]);

  returnPDFThumbnailView;
}();

exports.PDFThumbnailView=PDFThumbnailView;

/***/}),
/*27*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFViewer=void0;

var_base_viewer=__webpack_require__(28);

var_pdfjsLib=__webpack_require__(7);

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_get(target,property,receiver){if(typeofReflect!=="undefined"&&Reflect.get){_get=Reflect.get;}else{_get=function_get(target,property,receiver){varbase=_superPropBase(target,property);if(!base)return;vardesc=Object.getOwnPropertyDescriptor(base,property);if(desc.get){returndesc.get.call(receiver);}returndesc.value;};}return_get(target,property,receiver||target);}

function_superPropBase(object,property){while(!Object.prototype.hasOwnProperty.call(object,property)){object=_getPrototypeOf(object);if(object===null)break;}returnobject;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

varPDFViewer=
/*#__PURE__*/
function(_BaseViewer){
  _inherits(PDFViewer,_BaseViewer);

  functionPDFViewer(){
    _classCallCheck(this,PDFViewer);

    return_possibleConstructorReturn(this,_getPrototypeOf(PDFViewer).apply(this,arguments));
  }

  _createClass(PDFViewer,[{
    key:"_scrollIntoView",
    value:function_scrollIntoView(_ref){
      varpageDiv=_ref.pageDiv,
          _ref$pageSpot=_ref.pageSpot,
          pageSpot=_ref$pageSpot===void0?null:_ref$pageSpot,
          _ref$pageNumber=_ref.pageNumber,
          pageNumber=_ref$pageNumber===void0?null:_ref$pageNumber;

      if(!pageSpot&&!this.isInPresentationMode){
        varleft=pageDiv.offsetLeft+pageDiv.clientLeft;
        varright=left+pageDiv.clientWidth;
        var_this$container=this.container,
            scrollLeft=_this$container.scrollLeft,
            clientWidth=_this$container.clientWidth;

        if(this._isScrollModeHorizontal||left<scrollLeft||right>scrollLeft+clientWidth){
          pageSpot={
            left:0,
            top:0
          };
        }
      }

      _get(_getPrototypeOf(PDFViewer.prototype),"_scrollIntoView",this).call(this,{
        pageDiv:pageDiv,
        pageSpot:pageSpot,
        pageNumber:pageNumber
      });
    }
  },{
    key:"_getVisiblePages",
    value:function_getVisiblePages(){
      if(this.isInPresentationMode){
        returnthis._getCurrentVisiblePage();
      }

      return_get(_getPrototypeOf(PDFViewer.prototype),"_getVisiblePages",this).call(this);
    }
  },{
    key:"_updateHelper",
    value:function_updateHelper(visiblePages){
      if(this.isInPresentationMode){
        return;
      }

      varcurrentId=this._currentPageNumber;
      varstillFullyVisible=false;
      var_iteratorNormalCompletion=true;
      var_didIteratorError=false;
      var_iteratorError=undefined;

      try{
        for(var_iterator=visiblePages[Symbol.iterator](),_step;!(_iteratorNormalCompletion=(_step=_iterator.next()).done);_iteratorNormalCompletion=true){
          varpage=_step.value;

          if(page.percent<100){
            break;
          }

          if(page.id===currentId){
            stillFullyVisible=true;
            break;
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

      if(!stillFullyVisible){
        currentId=visiblePages[0].id;
      }

      this._setCurrentPageNumber(currentId);
    }
  },{
    key:"_setDocumentViewerElement",
    get:functionget(){
      return(0,_pdfjsLib.shadow)(this,'_setDocumentViewerElement',this.viewer);
    }
  }]);

  returnPDFViewer;
}(_base_viewer.BaseViewer);

exports.PDFViewer=PDFViewer;

/***/}),
/*28*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.BaseViewer=void0;

var_ui_utils=__webpack_require__(5);

var_pdf_rendering_queue=__webpack_require__(11);

var_annotation_layer_builder=__webpack_require__(29);

var_pdfjsLib=__webpack_require__(7);

var_pdf_page_view=__webpack_require__(30);

var_pdf_link_service=__webpack_require__(21);

var_text_layer_builder=__webpack_require__(31);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varDEFAULT_CACHE_SIZE=10;

functionPDFPageViewBuffer(size){
  vardata=[];

  this.push=function(view){
    vari=data.indexOf(view);

    if(i>=0){
      data.splice(i,1);
    }

    data.push(view);

    if(data.length>size){
      data.shift().destroy();
    }
  };

  this.resize=function(newSize,pagesToKeep){
    size=newSize;

    if(pagesToKeep){
      varpageIdsToKeep=newSet();

      for(vari=0,iMax=pagesToKeep.length;i<iMax;++i){
        pageIdsToKeep.add(pagesToKeep[i].id);
      }

      (0,_ui_utils.moveToEndOfArray)(data,function(page){
        returnpageIdsToKeep.has(page.id);
      });
    }

    while(data.length>size){
      data.shift().destroy();
    }
  };
}

functionisSameScale(oldScale,newScale){
  if(newScale===oldScale){
    returntrue;
  }

  if(Math.abs(newScale-oldScale)<1e-15){
    returntrue;
  }

  returnfalse;
}

varBaseViewer=
/*#__PURE__*/
function(){
  functionBaseViewer(options){
    var_this=this;

    _classCallCheck(this,BaseViewer);

    if(this.constructor===BaseViewer){
      thrownewError('CannotinitializeBaseViewer.');
    }

    this._name=this.constructor.name;
    this.container=options.container;
    this.viewer=options.viewer||options.container.firstElementChild;
    this.eventBus=options.eventBus||(0,_ui_utils.getGlobalEventBus)();
    this.linkService=options.linkService||new_pdf_link_service.SimpleLinkService();
    this.downloadManager=options.downloadManager||null;
    this.findController=options.findController||null;
    this.removePageBorders=options.removePageBorders||false;
    this.textLayerMode=Number.isInteger(options.textLayerMode)?options.textLayerMode:_ui_utils.TextLayerMode.ENABLE;
    this.imageResourcesPath=options.imageResourcesPath||'';
    this.renderInteractiveForms=options.renderInteractiveForms||false;
    this.enablePrintAutoRotate=options.enablePrintAutoRotate||false;
    this.renderer=options.renderer||_ui_utils.RendererType.CANVAS;
    this.enableWebGL=options.enableWebGL||false;
    this.useOnlyCssZoom=options.useOnlyCssZoom||false;
    this.maxCanvasPixels=options.maxCanvasPixels;
    this.l10n=options.l10n||_ui_utils.NullL10n;
    this.defaultRenderingQueue=!options.renderingQueue;

    if(this.defaultRenderingQueue){
      this.renderingQueue=new_pdf_rendering_queue.PDFRenderingQueue();
      this.renderingQueue.setViewer(this);
    }else{
      this.renderingQueue=options.renderingQueue;
    }

    this.scroll=(0,_ui_utils.watchScroll)(this.container,this._scrollUpdate.bind(this));
    this.presentationModeState=_ui_utils.PresentationModeState.UNKNOWN;

    this._resetView();

    if(this.removePageBorders){
      this.viewer.classList.add('removePageBorders');
    }

    Promise.resolve().then(function(){
      _this.eventBus.dispatch('baseviewerinit',{
        source:_this
      });
    });
  }

  _createClass(BaseViewer,[{
    key:"getPageView",
    value:functiongetPageView(index){
      returnthis._pages[index];
    }
  },{
    key:"_setCurrentPageNumber",
    value:function_setCurrentPageNumber(val){
      varresetCurrentPageView=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;

      if(this._currentPageNumber===val){
        if(resetCurrentPageView){
          this._resetCurrentPageView();
        }

        returntrue;
      }

      if(!(0<val&&val<=this.pagesCount)){
        returnfalse;
      }

      this._currentPageNumber=val;
      this.eventBus.dispatch('pagechanging',{
        source:this,
        pageNumber:val,
        pageLabel:this._pageLabels&&this._pageLabels[val-1]
      });

      if(resetCurrentPageView){
        this._resetCurrentPageView();
      }

      returntrue;
    }
  },{
    key:"setDocument",
    value:functionsetDocument(pdfDocument){
      var_this2=this;

      if(this.pdfDocument){
        this._cancelRendering();

        this._resetView();

        if(this.findController){
          this.findController.setDocument(null);
        }
      }

      this.pdfDocument=pdfDocument;

      if(!pdfDocument){
        return;
      }

      varpagesCount=pdfDocument.numPages;
      varpagesCapability=(0,_pdfjsLib.createPromiseCapability)();
      this.pagesPromise=pagesCapability.promise;
      pagesCapability.promise.then(function(){
        _this2._pageViewsReady=true;

        _this2.eventBus.dispatch('pagesloaded',{
          source:_this2,
          pagesCount:pagesCount
        });
      });
      varonePageRenderedCapability=(0,_pdfjsLib.createPromiseCapability)();
      this.onePageRendered=onePageRenderedCapability.promise;

      varbindOnAfterAndBeforeDraw=functionbindOnAfterAndBeforeDraw(pageView){
        pageView.onBeforeDraw=function(){
          _this2._buffer.push(pageView);
        };

        pageView.onAfterDraw=function(){
          if(!onePageRenderedCapability.settled){
            onePageRenderedCapability.resolve();
          }
        };
      };

      varfirstPagePromise=pdfDocument.getPage(1);
      this.firstPagePromise=firstPagePromise;
      firstPagePromise.then(function(pdfPage){
        varscale=_this2.currentScale;
        varviewport=pdfPage.getViewport({
          scale:scale*_ui_utils.CSS_UNITS
        });

        for(varpageNum=1;pageNum<=pagesCount;++pageNum){
          vartextLayerFactory=null;

          if(_this2.textLayerMode!==_ui_utils.TextLayerMode.DISABLE){
            textLayerFactory=_this2;
          }

          varpageView=new_pdf_page_view.PDFPageView({
            container:_this2._setDocumentViewerElement,
            eventBus:_this2.eventBus,
            id:pageNum,
            scale:scale,
            defaultViewport:viewport.clone(),
            renderingQueue:_this2.renderingQueue,
            textLayerFactory:textLayerFactory,
            textLayerMode:_this2.textLayerMode,
            annotationLayerFactory:_this2,
            imageResourcesPath:_this2.imageResourcesPath,
            renderInteractiveForms:_this2.renderInteractiveForms,
            renderer:_this2.renderer,
            enableWebGL:_this2.enableWebGL,
            useOnlyCssZoom:_this2.useOnlyCssZoom,
            maxCanvasPixels:_this2.maxCanvasPixels,
            l10n:_this2.l10n
          });
          bindOnAfterAndBeforeDraw(pageView);

          _this2._pages.push(pageView);
        }

        if(_this2._spreadMode!==_ui_utils.SpreadMode.NONE){
          _this2._updateSpreadMode();
        }

        onePageRenderedCapability.promise.then(function(){
          if(_this2.findController){
            _this2.findController.setDocument(pdfDocument);
          }

          if(pdfDocument.loadingParams['disableAutoFetch']){
            pagesCapability.resolve();
            return;
          }

          vargetPagesLeft=pagesCount;

          var_loop=function_loop(_pageNum){
            pdfDocument.getPage(_pageNum).then(function(pdfPage){
              varpageView=_this2._pages[_pageNum-1];

              if(!pageView.pdfPage){
                pageView.setPdfPage(pdfPage);
              }

              _this2.linkService.cachePageRef(_pageNum,pdfPage.ref);

              if(--getPagesLeft===0){
                pagesCapability.resolve();
              }
            },function(reason){
              console.error("Unabletogetpage".concat(_pageNum,"toinitializeviewer"),reason);

              if(--getPagesLeft===0){
                pagesCapability.resolve();
              }
            });
          };

          for(var_pageNum=1;_pageNum<=pagesCount;++_pageNum){
            _loop(_pageNum);
          }
        });

        _this2.eventBus.dispatch('pagesinit',{
          source:_this2
        });

        if(_this2.defaultRenderingQueue){
          _this2.update();
        }
      })["catch"](function(reason){
        console.error('Unabletoinitializeviewer',reason);
      });
    }
  },{
    key:"setPageLabels",
    value:functionsetPageLabels(labels){
      if(!this.pdfDocument){
        return;
      }

      if(!labels){
        this._pageLabels=null;
      }elseif(!(Array.isArray(labels)&&this.pdfDocument.numPages===labels.length)){
        this._pageLabels=null;
        console.error("".concat(this._name,".setPageLabels:Invalidpagelabels."));
      }else{
        this._pageLabels=labels;
      }

      for(vari=0,ii=this._pages.length;i<ii;i++){
        varpageView=this._pages[i];
        varlabel=this._pageLabels&&this._pageLabels[i];
        pageView.setPageLabel(label);
      }
    }
  },{
    key:"_resetView",
    value:function_resetView(){
      this._pages=[];
      this._currentPageNumber=1;
      this._currentScale=_ui_utils.UNKNOWN_SCALE;
      this._currentScaleValue=null;
      this._pageLabels=null;
      this._buffer=newPDFPageViewBuffer(DEFAULT_CACHE_SIZE);
      this._location=null;
      this._pagesRotation=0;
      this._pagesRequests=[];
      this._pageViewsReady=false;
      this._scrollMode=_ui_utils.ScrollMode.VERTICAL;
      this._spreadMode=_ui_utils.SpreadMode.NONE;
      this.viewer.textContent='';

      this._updateScrollMode();
    }
  },{
    key:"_scrollUpdate",
    value:function_scrollUpdate(){
      if(this.pagesCount===0){
        return;
      }

      this.update();
    }
  },{
    key:"_scrollIntoView",
    value:function_scrollIntoView(_ref){
      varpageDiv=_ref.pageDiv,
          _ref$pageSpot=_ref.pageSpot,
          pageSpot=_ref$pageSpot===void0?null:_ref$pageSpot,
          _ref$pageNumber=_ref.pageNumber,
          pageNumber=_ref$pageNumber===void0?null:_ref$pageNumber;
      (0,_ui_utils.scrollIntoView)(pageDiv,pageSpot);
    }
  },{
    key:"_setScaleUpdatePages",
    value:function_setScaleUpdatePages(newScale,newValue){
      varnoScroll=arguments.length>2&&arguments[2]!==undefined?arguments[2]:false;
      varpreset=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;
      this._currentScaleValue=newValue.toString();

      if(isSameScale(this._currentScale,newScale)){
        if(preset){
          this.eventBus.dispatch('scalechanging',{
            source:this,
            scale:newScale,
            presetValue:newValue
          });
        }

        return;
      }

      for(vari=0,ii=this._pages.length;i<ii;i++){
        this._pages[i].update(newScale);
      }

      this._currentScale=newScale;

      if(!noScroll){
        varpage=this._currentPageNumber,
            dest;

        if(this._location&&!(this.isInPresentationMode||this.isChangingPresentationMode)){
          page=this._location.pageNumber;
          dest=[null,{
            name:'XYZ'
          },this._location.left,this._location.top,null];
        }

        this.scrollPageIntoView({
          pageNumber:page,
          destArray:dest,
          allowNegativeOffset:true
        });
      }

      this.eventBus.dispatch('scalechanging',{
        source:this,
        scale:newScale,
        presetValue:preset?newValue:undefined
      });

      if(this.defaultRenderingQueue){
        this.update();
      }
    }
  },{
    key:"_setScale",
    value:function_setScale(value){
      varnoScroll=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
      varscale=parseFloat(value);

      if(scale>0){
        this._setScaleUpdatePages(scale,value,noScroll,false);
      }else{
        varcurrentPage=this._pages[this._currentPageNumber-1];

        if(!currentPage){
          return;
        }

        varnoPadding=this.isInPresentationMode||this.removePageBorders;
        varhPadding=noPadding?0:_ui_utils.SCROLLBAR_PADDING;
        varvPadding=noPadding?0:_ui_utils.VERTICAL_PADDING;

        if(!noPadding&&this._isScrollModeHorizontal){
          var_ref2=[vPadding,hPadding];
          hPadding=_ref2[0];
          vPadding=_ref2[1];
        }

        varpageWidthScale=(this.container.clientWidth-hPadding)/currentPage.width*currentPage.scale;
        varpageHeightScale=(this.container.clientHeight-vPadding)/currentPage.height*currentPage.scale;

        switch(value){
          case'page-actual':
            scale=1;
            break;

          case'page-width':
            scale=pageWidthScale;
            break;

          case'page-height':
            scale=pageHeightScale;
            break;

          case'page-fit':
            scale=Math.min(pageWidthScale,pageHeightScale);
            break;

          case'auto':
            varhorizontalScale=(0,_ui_utils.isPortraitOrientation)(currentPage)?pageWidthScale:Math.min(pageHeightScale,pageWidthScale);
            scale=Math.min(_ui_utils.MAX_AUTO_SCALE,horizontalScale);
            break;

          default:
            console.error("".concat(this._name,"._setScale:\"").concat(value,"\"isanunknownzoomvalue."));
            return;
        }

        this._setScaleUpdatePages(scale,value,noScroll,true);
      }
    }
  },{
    key:"_resetCurrentPageView",
    value:function_resetCurrentPageView(){
      if(this.isInPresentationMode){
        this._setScale(this._currentScaleValue,true);
      }

      varpageView=this._pages[this._currentPageNumber-1];

      this._scrollIntoView({
        pageDiv:pageView.div
      });
    }
  },{
    key:"scrollPageIntoView",
    value:functionscrollPageIntoView(_ref3){
      varpageNumber=_ref3.pageNumber,
          _ref3$destArray=_ref3.destArray,
          destArray=_ref3$destArray===void0?null:_ref3$destArray,
          _ref3$allowNegativeOf=_ref3.allowNegativeOffset,
          allowNegativeOffset=_ref3$allowNegativeOf===void0?false:_ref3$allowNegativeOf;

      if(!this.pdfDocument){
        return;
      }

      varpageView=Number.isInteger(pageNumber)&&this._pages[pageNumber-1];

      if(!pageView){
        console.error("".concat(this._name,".scrollPageIntoView:")+"\"".concat(pageNumber,"\"isnotavalidpageNumberparameter."));
        return;
      }

      if(this.isInPresentationMode||!destArray){
        this._setCurrentPageNumber(pageNumber,true);

        return;
      }

      varx=0,
          y=0;
      varwidth=0,
          height=0,
          widthScale,
          heightScale;
      varchangeOrientation=pageView.rotation%180===0?false:true;
      varpageWidth=(changeOrientation?pageView.height:pageView.width)/pageView.scale/_ui_utils.CSS_UNITS;
      varpageHeight=(changeOrientation?pageView.width:pageView.height)/pageView.scale/_ui_utils.CSS_UNITS;
      varscale=0;

      switch(destArray[1].name){
        case'XYZ':
          x=destArray[2];
          y=destArray[3];
          scale=destArray[4];
          x=x!==null?x:0;
          y=y!==null?y:pageHeight;
          break;

        case'Fit':
        case'FitB':
          scale='page-fit';
          break;

        case'FitH':
        case'FitBH':
          y=destArray[2];
          scale='page-width';

          if(y===null&&this._location){
            x=this._location.left;
            y=this._location.top;
          }

          break;

        case'FitV':
        case'FitBV':
          x=destArray[2];
          width=pageWidth;
          height=pageHeight;
          scale='page-height';
          break;

        case'FitR':
          x=destArray[2];
          y=destArray[3];
          width=destArray[4]-x;
          height=destArray[5]-y;
          varhPadding=this.removePageBorders?0:_ui_utils.SCROLLBAR_PADDING;
          varvPadding=this.removePageBorders?0:_ui_utils.VERTICAL_PADDING;
          widthScale=(this.container.clientWidth-hPadding)/width/_ui_utils.CSS_UNITS;
          heightScale=(this.container.clientHeight-vPadding)/height/_ui_utils.CSS_UNITS;
          scale=Math.min(Math.abs(widthScale),Math.abs(heightScale));
          break;

        default:
          console.error("".concat(this._name,".scrollPageIntoView:")+"\"".concat(destArray[1].name,"\"isnotavaliddestinationtype."));
          return;
      }

      if(scale&&scale!==this._currentScale){
        this.currentScaleValue=scale;
      }elseif(this._currentScale===_ui_utils.UNKNOWN_SCALE){
        this.currentScaleValue=_ui_utils.DEFAULT_SCALE_VALUE;
      }

      if(scale==='page-fit'&&!destArray[4]){
        this._scrollIntoView({
          pageDiv:pageView.div,
          pageNumber:pageNumber
        });

        return;
      }

      varboundingRect=[pageView.viewport.convertToViewportPoint(x,y),pageView.viewport.convertToViewportPoint(x+width,y+height)];
      varleft=Math.min(boundingRect[0][0],boundingRect[1][0]);
      vartop=Math.min(boundingRect[0][1],boundingRect[1][1]);

      if(!allowNegativeOffset){
        left=Math.max(left,0);
        top=Math.max(top,0);
      }

      this._scrollIntoView({
        pageDiv:pageView.div,
        pageSpot:{
          left:left,
          top:top
        },
        pageNumber:pageNumber
      });
    }
  },{
    key:"_updateLocation",
    value:function_updateLocation(firstPage){
      varcurrentScale=this._currentScale;
      varcurrentScaleValue=this._currentScaleValue;
      varnormalizedScaleValue=parseFloat(currentScaleValue)===currentScale?Math.round(currentScale*10000)/100:currentScaleValue;
      varpageNumber=firstPage.id;
      varpdfOpenParams='#page='+pageNumber;
      pdfOpenParams+='&zoom='+normalizedScaleValue;
      varcurrentPageView=this._pages[pageNumber-1];
      varcontainer=this.container;
      vartopLeft=currentPageView.getPagePoint(container.scrollLeft-firstPage.x,container.scrollTop-firstPage.y);
      varintLeft=Math.round(topLeft[0]);
      varintTop=Math.round(topLeft[1]);
      pdfOpenParams+=','+intLeft+','+intTop;
      this._location={
        pageNumber:pageNumber,
        scale:normalizedScaleValue,
        top:intTop,
        left:intLeft,
        rotation:this._pagesRotation,
        pdfOpenParams:pdfOpenParams
      };
    }
  },{
    key:"_updateHelper",
    value:function_updateHelper(visiblePages){
      thrownewError('Notimplemented:_updateHelper');
    }
  },{
    key:"update",
    value:functionupdate(){
      varvisible=this._getVisiblePages();

      varvisiblePages=visible.views,
          numVisiblePages=visiblePages.length;

      if(numVisiblePages===0){
        return;
      }

      varnewCacheSize=Math.max(DEFAULT_CACHE_SIZE,2*numVisiblePages+1);

      this._buffer.resize(newCacheSize,visiblePages);

      this.renderingQueue.renderHighestPriority(visible);

      this._updateHelper(visiblePages);

      this._updateLocation(visible.first);

      this.eventBus.dispatch('updateviewarea',{
        source:this,
        location:this._location
      });
    }
  },{
    key:"containsElement",
    value:functioncontainsElement(element){
      returnthis.container.contains(element);
    }
  },{
    key:"focus",
    value:functionfocus(){
      this.container.focus();
    }
  },{
    key:"_getCurrentVisiblePage",
    value:function_getCurrentVisiblePage(){
      if(!this.pagesCount){
        return{
          views:[]
        };
      }

      varpageView=this._pages[this._currentPageNumber-1];
      varelement=pageView.div;
      varview={
        id:pageView.id,
        x:element.offsetLeft+element.clientLeft,
        y:element.offsetTop+element.clientTop,
        view:pageView
      };
      return{
        first:view,
        last:view,
        views:[view]
      };
    }
  },{
    key:"_getVisiblePages",
    value:function_getVisiblePages(){
      return(0,_ui_utils.getVisibleElements)(this.container,this._pages,true,this._isScrollModeHorizontal);
    }
  },{
    key:"isPageVisible",
    value:functionisPageVisible(pageNumber){
      if(!this.pdfDocument){
        returnfalse;
      }

      if(this.pageNumber<1||pageNumber>this.pagesCount){
        console.error("".concat(this._name,".isPageVisible:\"").concat(pageNumber,"\"isoutofbounds."));
        returnfalse;
      }

      returnthis._getVisiblePages().views.some(function(view){
        returnview.id===pageNumber;
      });
    }
  },{
    key:"cleanup",
    value:functioncleanup(){
      for(vari=0,ii=this._pages.length;i<ii;i++){
        if(this._pages[i]&&this._pages[i].renderingState!==_pdf_rendering_queue.RenderingStates.FINISHED){
          this._pages[i].reset();
        }
      }
    }
  },{
    key:"_cancelRendering",
    value:function_cancelRendering(){
      for(vari=0,ii=this._pages.length;i<ii;i++){
        if(this._pages[i]){
          this._pages[i].cancelRendering();
        }
      }
    }
  },{
    key:"_ensurePdfPageLoaded",
    value:function_ensurePdfPageLoaded(pageView){
      var_this3=this;

      if(pageView.pdfPage){
        returnPromise.resolve(pageView.pdfPage);
      }

      varpageNumber=pageView.id;

      if(this._pagesRequests[pageNumber]){
        returnthis._pagesRequests[pageNumber];
      }

      varpromise=this.pdfDocument.getPage(pageNumber).then(function(pdfPage){
        if(!pageView.pdfPage){
          pageView.setPdfPage(pdfPage);
        }

        _this3._pagesRequests[pageNumber]=null;
        returnpdfPage;
      })["catch"](function(reason){
        console.error('Unabletogetpageforpageview',reason);
        _this3._pagesRequests[pageNumber]=null;
      });
      this._pagesRequests[pageNumber]=promise;
      returnpromise;
    }
  },{
    key:"forceRendering",
    value:functionforceRendering(currentlyVisiblePages){
      var_this4=this;

      varvisiblePages=currentlyVisiblePages||this._getVisiblePages();

      varscrollAhead=this._isScrollModeHorizontal?this.scroll.right:this.scroll.down;
      varpageView=this.renderingQueue.getHighestPriority(visiblePages,this._pages,scrollAhead);

      if(pageView){
        this._ensurePdfPageLoaded(pageView).then(function(){
          _this4.renderingQueue.renderView(pageView);
        });

        returntrue;
      }

      returnfalse;
    }
  },{
    key:"createTextLayerBuilder",
    value:functioncreateTextLayerBuilder(textLayerDiv,pageIndex,viewport){
      varenhanceTextSelection=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;
      returnnew_text_layer_builder.TextLayerBuilder({
        textLayerDiv:textLayerDiv,
        eventBus:this.eventBus,
        pageIndex:pageIndex,
        viewport:viewport,
        findController:this.isInPresentationMode?null:this.findController,
        enhanceTextSelection:this.isInPresentationMode?false:enhanceTextSelection
      });
    }
  },{
    key:"createAnnotationLayerBuilder",
    value:functioncreateAnnotationLayerBuilder(pageDiv,pdfPage){
      varimageResourcesPath=arguments.length>2&&arguments[2]!==undefined?arguments[2]:'';
      varrenderInteractiveForms=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;
      varl10n=arguments.length>4&&arguments[4]!==undefined?arguments[4]:_ui_utils.NullL10n;
      returnnew_annotation_layer_builder.AnnotationLayerBuilder({
        pageDiv:pageDiv,
        pdfPage:pdfPage,
        imageResourcesPath:imageResourcesPath,
        renderInteractiveForms:renderInteractiveForms,
        linkService:this.linkService,
        downloadManager:this.downloadManager,
        l10n:l10n
      });
    }
  },{
    key:"getPagesOverview",
    value:functiongetPagesOverview(){
      varpagesOverview=this._pages.map(function(pageView){
        varviewport=pageView.pdfPage.getViewport({
          scale:1
        });
        return{
          width:viewport.width,
          height:viewport.height,
          rotation:viewport.rotation
        };
      });

      if(!this.enablePrintAutoRotate){
        returnpagesOverview;
      }

      varisFirstPagePortrait=(0,_ui_utils.isPortraitOrientation)(pagesOverview[0]);
      returnpagesOverview.map(function(size){
        if(isFirstPagePortrait===(0,_ui_utils.isPortraitOrientation)(size)){
          returnsize;
        }

        return{
          width:size.height,
          height:size.width,
          rotation:(size.rotation+90)%360
        };
      });
    }
  },{
    key:"_updateScrollMode",
    value:function_updateScrollMode(){
      varpageNumber=arguments.length>0&&arguments[0]!==undefined?arguments[0]:null;
      varscrollMode=this._scrollMode,
          viewer=this.viewer;
      viewer.classList.toggle('scrollHorizontal',scrollMode===_ui_utils.ScrollMode.HORIZONTAL);
      viewer.classList.toggle('scrollWrapped',scrollMode===_ui_utils.ScrollMode.WRAPPED);

      if(!this.pdfDocument||!pageNumber){
        return;
      }

      if(this._currentScaleValue&&isNaN(this._currentScaleValue)){
        this._setScale(this._currentScaleValue,true);
      }

      this._setCurrentPageNumber(pageNumber,true);

      this.update();
    }
  },{
    key:"_updateSpreadMode",
    value:function_updateSpreadMode(){
      varpageNumber=arguments.length>0&&arguments[0]!==undefined?arguments[0]:null;

      if(!this.pdfDocument){
        return;
      }

      varviewer=this.viewer,
          pages=this._pages;
      viewer.textContent='';

      if(this._spreadMode===_ui_utils.SpreadMode.NONE){
        for(vari=0,iMax=pages.length;i<iMax;++i){
          viewer.appendChild(pages[i].div);
        }
      }else{
        varparity=this._spreadMode-1;
        varspread=null;

        for(var_i=0,_iMax=pages.length;_i<_iMax;++_i){
          if(spread===null){
            spread=document.createElement('div');
            spread.className='spread';
            viewer.appendChild(spread);
          }elseif(_i%2===parity){
            spread=spread.cloneNode(false);
            viewer.appendChild(spread);
          }

          spread.appendChild(pages[_i].div);
        }
      }

      if(!pageNumber){
        return;
      }

      this._setCurrentPageNumber(pageNumber,true);

      this.update();
    }
  },{
    key:"pagesCount",
    get:functionget(){
      returnthis._pages.length;
    }
  },{
    key:"pageViewsReady",
    get:functionget(){
      returnthis._pageViewsReady;
    }
  },{
    key:"currentPageNumber",
    get:functionget(){
      returnthis._currentPageNumber;
    },
    set:functionset(val){
      if(!Number.isInteger(val)){
        thrownewError('Invalidpagenumber.');
      }

      if(!this.pdfDocument){
        return;
      }

      if(!this._setCurrentPageNumber(val,true)){
        console.error("".concat(this._name,".currentPageNumber:\"").concat(val,"\"isnotavalidpage."));
      }
    }
  },{
    key:"currentPageLabel",
    get:functionget(){
      returnthis._pageLabels&&this._pageLabels[this._currentPageNumber-1];
    },
    set:functionset(val){
      if(!this.pdfDocument){
        return;
      }

      varpage=val|0;

      if(this._pageLabels){
        vari=this._pageLabels.indexOf(val);

        if(i>=0){
          page=i+1;
        }
      }

      if(!this._setCurrentPageNumber(page,true)){
        console.error("".concat(this._name,".currentPageLabel:\"").concat(val,"\"isnotavalidpage."));
      }
    }
  },{
    key:"currentScale",
    get:functionget(){
      returnthis._currentScale!==_ui_utils.UNKNOWN_SCALE?this._currentScale:_ui_utils.DEFAULT_SCALE;
    },
    set:functionset(val){
      if(isNaN(val)){
        thrownewError('Invalidnumericscale.');
      }

      if(!this.pdfDocument){
        return;
      }

      this._setScale(val,false);
    }
  },{
    key:"currentScaleValue",
    get:functionget(){
      returnthis._currentScaleValue;
    },
    set:functionset(val){
      if(!this.pdfDocument){
        return;
      }

      this._setScale(val,false);
    }
  },{
    key:"pagesRotation",
    get:functionget(){
      returnthis._pagesRotation;
    },
    set:functionset(rotation){
      if(!(0,_ui_utils.isValidRotation)(rotation)){
        thrownewError('Invalidpagesrotationangle.');
      }

      if(!this.pdfDocument){
        return;
      }

      if(this._pagesRotation===rotation){
        return;
      }

      this._pagesRotation=rotation;
      varpageNumber=this._currentPageNumber;

      for(vari=0,ii=this._pages.length;i<ii;i++){
        varpageView=this._pages[i];
        pageView.update(pageView.scale,rotation);
      }

      if(this._currentScaleValue){
        this._setScale(this._currentScaleValue,true);
      }

      this.eventBus.dispatch('rotationchanging',{
        source:this,
        pagesRotation:rotation,
        pageNumber:pageNumber
      });

      if(this.defaultRenderingQueue){
        this.update();
      }
    }
  },{
    key:"_setDocumentViewerElement",
    get:functionget(){
      thrownewError('Notimplemented:_setDocumentViewerElement');
    }
  },{
    key:"_isScrollModeHorizontal",
    get:functionget(){
      returnthis.isInPresentationMode?false:this._scrollMode===_ui_utils.ScrollMode.HORIZONTAL;
    }
  },{
    key:"isInPresentationMode",
    get:functionget(){
      returnthis.presentationModeState===_ui_utils.PresentationModeState.FULLSCREEN;
    }
  },{
    key:"isChangingPresentationMode",
    get:functionget(){
      returnthis.presentationModeState===_ui_utils.PresentationModeState.CHANGING;
    }
  },{
    key:"isHorizontalScrollbarEnabled",
    get:functionget(){
      returnthis.isInPresentationMode?false:this.container.scrollWidth>this.container.clientWidth;
    }
  },{
    key:"isVerticalScrollbarEnabled",
    get:functionget(){
      returnthis.isInPresentationMode?false:this.container.scrollHeight>this.container.clientHeight;
    }
  },{
    key:"hasEqualPageSizes",
    get:functionget(){
      varfirstPageView=this._pages[0];

      for(vari=1,ii=this._pages.length;i<ii;++i){
        varpageView=this._pages[i];

        if(pageView.width!==firstPageView.width||pageView.height!==firstPageView.height){
          returnfalse;
        }
      }

      returntrue;
    }
  },{
    key:"scrollMode",
    get:functionget(){
      returnthis._scrollMode;
    },
    set:functionset(mode){
      if(this._scrollMode===mode){
        return;
      }

      if(!(0,_ui_utils.isValidScrollMode)(mode)){
        thrownewError("Invalidscrollmode:".concat(mode));
      }

      this._scrollMode=mode;
      this.eventBus.dispatch('scrollmodechanged',{
        source:this,
        mode:mode
      });

      this._updateScrollMode(this._currentPageNumber);
    }
  },{
    key:"spreadMode",
    get:functionget(){
      returnthis._spreadMode;
    },
    set:functionset(mode){
      if(this._spreadMode===mode){
        return;
      }

      if(!(0,_ui_utils.isValidSpreadMode)(mode)){
        thrownewError("Invalidspreadmode:".concat(mode));
      }

      this._spreadMode=mode;
      this.eventBus.dispatch('spreadmodechanged',{
        source:this,
        mode:mode
      });

      this._updateSpreadMode(this._currentPageNumber);
    }
  }]);

  returnBaseViewer;
}();

exports.BaseViewer=BaseViewer;

/***/}),
/*29*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.DefaultAnnotationLayerFactory=exports.AnnotationLayerBuilder=void0;

var_pdfjsLib=__webpack_require__(7);

var_ui_utils=__webpack_require__(5);

var_pdf_link_service=__webpack_require__(21);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varAnnotationLayerBuilder=
/*#__PURE__*/
function(){
  functionAnnotationLayerBuilder(_ref){
    varpageDiv=_ref.pageDiv,
        pdfPage=_ref.pdfPage,
        linkService=_ref.linkService,
        downloadManager=_ref.downloadManager,
        _ref$imageResourcesPa=_ref.imageResourcesPath,
        imageResourcesPath=_ref$imageResourcesPa===void0?'':_ref$imageResourcesPa,
        _ref$renderInteractiv=_ref.renderInteractiveForms,
        renderInteractiveForms=_ref$renderInteractiv===void0?false:_ref$renderInteractiv,
        _ref$l10n=_ref.l10n,
        l10n=_ref$l10n===void0?_ui_utils.NullL10n:_ref$l10n;

    _classCallCheck(this,AnnotationLayerBuilder);

    this.pageDiv=pageDiv;
    this.pdfPage=pdfPage;
    this.linkService=linkService;
    this.downloadManager=downloadManager;
    this.imageResourcesPath=imageResourcesPath;
    this.renderInteractiveForms=renderInteractiveForms;
    this.l10n=l10n;
    this.div=null;
    this._cancelled=false;
  }

  _createClass(AnnotationLayerBuilder,[{
    key:"render",
    value:functionrender(viewport){
      var_this=this;

      varintent=arguments.length>1&&arguments[1]!==undefined?arguments[1]:'display';
      this.pdfPage.getAnnotations({
        intent:intent
      }).then(function(annotations){
        if(_this._cancelled){
          return;
        }

        varparameters={
          viewport:viewport.clone({
            dontFlip:true
          }),
          div:_this.div,
          annotations:annotations,
          page:_this.pdfPage,
          imageResourcesPath:_this.imageResourcesPath,
          renderInteractiveForms:_this.renderInteractiveForms,
          linkService:_this.linkService,
          downloadManager:_this.downloadManager
        };

        if(_this.div){
          _pdfjsLib.AnnotationLayer.update(parameters);
        }else{
          if(annotations.length===0){
            return;
          }

          _this.div=document.createElement('div');
          _this.div.className='annotationLayer';

          _this.pageDiv.appendChild(_this.div);

          parameters.div=_this.div;

          _pdfjsLib.AnnotationLayer.render(parameters);

          _this.l10n.translate(_this.div);
        }
      });
    }
  },{
    key:"cancel",
    value:functioncancel(){
      this._cancelled=true;
    }
  },{
    key:"hide",
    value:functionhide(){
      if(!this.div){
        return;
      }

      this.div.setAttribute('hidden','true');
    }
  }]);

  returnAnnotationLayerBuilder;
}();

exports.AnnotationLayerBuilder=AnnotationLayerBuilder;

varDefaultAnnotationLayerFactory=
/*#__PURE__*/
function(){
  functionDefaultAnnotationLayerFactory(){
    _classCallCheck(this,DefaultAnnotationLayerFactory);
  }

  _createClass(DefaultAnnotationLayerFactory,[{
    key:"createAnnotationLayerBuilder",
    value:functioncreateAnnotationLayerBuilder(pageDiv,pdfPage){
      varimageResourcesPath=arguments.length>2&&arguments[2]!==undefined?arguments[2]:'';
      varrenderInteractiveForms=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;
      varl10n=arguments.length>4&&arguments[4]!==undefined?arguments[4]:_ui_utils.NullL10n;
      returnnewAnnotationLayerBuilder({
        pageDiv:pageDiv,
        pdfPage:pdfPage,
        imageResourcesPath:imageResourcesPath,
        renderInteractiveForms:renderInteractiveForms,
        linkService:new_pdf_link_service.SimpleLinkService(),
        l10n:l10n
      });
    }
  }]);

  returnDefaultAnnotationLayerFactory;
}();

exports.DefaultAnnotationLayerFactory=DefaultAnnotationLayerFactory;

/***/}),
/*30*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFPageView=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

var_ui_utils=__webpack_require__(5);

var_pdfjsLib=__webpack_require__(7);

var_pdf_rendering_queue=__webpack_require__(11);

var_viewer_compatibility=__webpack_require__(8);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varMAX_CANVAS_PIXELS=_viewer_compatibility.viewerCompatibilityParams.maxCanvasPixels||16777216;

varPDFPageView=
/*#__PURE__*/
function(){
  functionPDFPageView(options){
    _classCallCheck(this,PDFPageView);

    varcontainer=options.container;
    vardefaultViewport=options.defaultViewport;
    this.id=options.id;
    this.renderingId='page'+this.id;
    this.pdfPage=null;
    this.pageLabel=null;
    this.rotation=0;
    this.scale=options.scale||_ui_utils.DEFAULT_SCALE;
    this.viewport=defaultViewport;
    this.pdfPageRotate=defaultViewport.rotation;
    this.hasRestrictedScaling=false;
    this.textLayerMode=Number.isInteger(options.textLayerMode)?options.textLayerMode:_ui_utils.TextLayerMode.ENABLE;
    this.imageResourcesPath=options.imageResourcesPath||'';
    this.renderInteractiveForms=options.renderInteractiveForms||false;
    this.useOnlyCssZoom=options.useOnlyCssZoom||false;
    this.maxCanvasPixels=options.maxCanvasPixels||MAX_CANVAS_PIXELS;
    this.eventBus=options.eventBus||(0,_ui_utils.getGlobalEventBus)();
    this.renderingQueue=options.renderingQueue;
    this.textLayerFactory=options.textLayerFactory;
    this.annotationLayerFactory=options.annotationLayerFactory;
    this.renderer=options.renderer||_ui_utils.RendererType.CANVAS;
    this.enableWebGL=options.enableWebGL||false;
    this.l10n=options.l10n||_ui_utils.NullL10n;
    this.paintTask=null;
    this.paintedViewportMap=newWeakMap();
    this.renderingState=_pdf_rendering_queue.RenderingStates.INITIAL;
    this.resume=null;
    this.error=null;
    this.onBeforeDraw=null;
    this.onAfterDraw=null;
    this.annotationLayer=null;
    this.textLayer=null;
    this.zoomLayer=null;
    vardiv=document.createElement('div');
    div.className='page';
    div.style.width=Math.floor(this.viewport.width)+'px';
    div.style.height=Math.floor(this.viewport.height)+'px';
    div.setAttribute('data-page-number',this.id);
    this.div=div;
    container.appendChild(div);
  }

  _createClass(PDFPageView,[{
    key:"setPdfPage",
    value:functionsetPdfPage(pdfPage){
      this.pdfPage=pdfPage;
      this.pdfPageRotate=pdfPage.rotate;
      vartotalRotation=(this.rotation+this.pdfPageRotate)%360;
      this.viewport=pdfPage.getViewport({
        scale:this.scale*_ui_utils.CSS_UNITS,
        rotation:totalRotation
      });
      this.stats=pdfPage.stats;
      this.reset();
    }
  },{
    key:"destroy",
    value:functiondestroy(){
      this.reset();

      if(this.pdfPage){
        this.pdfPage.cleanup();
      }
    }
  },{
    key:"_resetZoomLayer",
    value:function_resetZoomLayer(){
      varremoveFromDOM=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(!this.zoomLayer){
        return;
      }

      varzoomLayerCanvas=this.zoomLayer.firstChild;
      this.paintedViewportMap["delete"](zoomLayerCanvas);
      zoomLayerCanvas.width=0;
      zoomLayerCanvas.height=0;

      if(removeFromDOM){
        this.zoomLayer.remove();
      }

      this.zoomLayer=null;
    }
  },{
    key:"reset",
    value:functionreset(){
      varkeepZoomLayer=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      varkeepAnnotations=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
      this.cancelRendering(keepAnnotations);
      this.renderingState=_pdf_rendering_queue.RenderingStates.INITIAL;
      vardiv=this.div;
      div.style.width=Math.floor(this.viewport.width)+'px';
      div.style.height=Math.floor(this.viewport.height)+'px';
      varchildNodes=div.childNodes;
      varcurrentZoomLayerNode=keepZoomLayer&&this.zoomLayer||null;
      varcurrentAnnotationNode=keepAnnotations&&this.annotationLayer&&this.annotationLayer.div||null;

      for(vari=childNodes.length-1;i>=0;i--){
        varnode=childNodes[i];

        if(currentZoomLayerNode===node||currentAnnotationNode===node){
          continue;
        }

        div.removeChild(node);
      }

      div.removeAttribute('data-loaded');

      if(currentAnnotationNode){
        this.annotationLayer.hide();
      }elseif(this.annotationLayer){
        this.annotationLayer.cancel();
        this.annotationLayer=null;
      }

      if(!currentZoomLayerNode){
        if(this.canvas){
          this.paintedViewportMap["delete"](this.canvas);
          this.canvas.width=0;
          this.canvas.height=0;
          deletethis.canvas;
        }

        this._resetZoomLayer();
      }

      if(this.svg){
        this.paintedViewportMap["delete"](this.svg);
        deletethis.svg;
      }

      this.loadingIconDiv=document.createElement('div');
      this.loadingIconDiv.className='loadingIcon';
      div.appendChild(this.loadingIconDiv);
    }
  },{
    key:"update",
    value:functionupdate(scale,rotation){
      this.scale=scale||this.scale;

      if(typeofrotation!=='undefined'){
        this.rotation=rotation;
      }

      vartotalRotation=(this.rotation+this.pdfPageRotate)%360;
      this.viewport=this.viewport.clone({
        scale:this.scale*_ui_utils.CSS_UNITS,
        rotation:totalRotation
      });

      if(this.svg){
        this.cssTransform(this.svg,true);
        this.eventBus.dispatch('pagerendered',{
          source:this,
          pageNumber:this.id,
          cssTransform:true
        });
        return;
      }

      varisScalingRestricted=false;

      if(this.canvas&&this.maxCanvasPixels>0){
        varoutputScale=this.outputScale;

        if((Math.floor(this.viewport.width)*outputScale.sx|0)*(Math.floor(this.viewport.height)*outputScale.sy|0)>this.maxCanvasPixels){
          isScalingRestricted=true;
        }
      }

      if(this.canvas){
        if(this.useOnlyCssZoom||this.hasRestrictedScaling&&isScalingRestricted){
          this.cssTransform(this.canvas,true);
          this.eventBus.dispatch('pagerendered',{
            source:this,
            pageNumber:this.id,
            cssTransform:true
          });
          return;
        }

        if(!this.zoomLayer&&!this.canvas.hasAttribute('hidden')){
          this.zoomLayer=this.canvas.parentNode;
          this.zoomLayer.style.position='absolute';
        }
      }

      if(this.zoomLayer){
        this.cssTransform(this.zoomLayer.firstChild);
      }

      this.reset(true,true);
    }
  },{
    key:"cancelRendering",
    value:functioncancelRendering(){
      varkeepAnnotations=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(this.paintTask){
        this.paintTask.cancel();
        this.paintTask=null;
      }

      this.resume=null;

      if(this.textLayer){
        this.textLayer.cancel();
        this.textLayer=null;
      }

      if(!keepAnnotations&&this.annotationLayer){
        this.annotationLayer.cancel();
        this.annotationLayer=null;
      }
    }
  },{
    key:"cssTransform",
    value:functioncssTransform(target){
      varredrawAnnotations=arguments.length>1&&arguments[1]!==undefined?arguments[1]:false;
      varwidth=this.viewport.width;
      varheight=this.viewport.height;
      vardiv=this.div;
      target.style.width=target.parentNode.style.width=div.style.width=Math.floor(width)+'px';
      target.style.height=target.parentNode.style.height=div.style.height=Math.floor(height)+'px';
      varrelativeRotation=this.viewport.rotation-this.paintedViewportMap.get(target).rotation;
      varabsRotation=Math.abs(relativeRotation);
      varscaleX=1,
          scaleY=1;

      if(absRotation===90||absRotation===270){
        scaleX=height/width;
        scaleY=width/height;
      }

      varcssTransform='rotate('+relativeRotation+'deg)'+'scale('+scaleX+','+scaleY+')';
      target.style.transform=cssTransform;

      if(this.textLayer){
        vartextLayerViewport=this.textLayer.viewport;
        vartextRelativeRotation=this.viewport.rotation-textLayerViewport.rotation;
        vartextAbsRotation=Math.abs(textRelativeRotation);
        varscale=width/textLayerViewport.width;

        if(textAbsRotation===90||textAbsRotation===270){
          scale=width/textLayerViewport.height;
        }

        vartextLayerDiv=this.textLayer.textLayerDiv;
        vartransX,transY;

        switch(textAbsRotation){
          case0:
            transX=transY=0;
            break;

          case90:
            transX=0;
            transY='-'+textLayerDiv.style.height;
            break;

          case180:
            transX='-'+textLayerDiv.style.width;
            transY='-'+textLayerDiv.style.height;
            break;

          case270:
            transX='-'+textLayerDiv.style.width;
            transY=0;
            break;

          default:
            console.error('Badrotationvalue.');
            break;
        }

        textLayerDiv.style.transform='rotate('+textAbsRotation+'deg)'+'scale('+scale+','+scale+')'+'translate('+transX+','+transY+')';
        textLayerDiv.style.transformOrigin='0%0%';
      }

      if(redrawAnnotations&&this.annotationLayer){
        this.annotationLayer.render(this.viewport,'display');
      }
    }
  },{
    key:"getPagePoint",
    value:functiongetPagePoint(x,y){
      returnthis.viewport.convertToPdfPoint(x,y);
    }
  },{
    key:"draw",
    value:functiondraw(){
      var_this=this;

      if(this.renderingState!==_pdf_rendering_queue.RenderingStates.INITIAL){
        console.error('Mustbeinnewstatebeforedrawing');
        this.reset();
      }

      if(!this.pdfPage){
        this.renderingState=_pdf_rendering_queue.RenderingStates.FINISHED;
        returnPromise.reject(newError('Pageisnotloaded'));
      }

      this.renderingState=_pdf_rendering_queue.RenderingStates.RUNNING;
      varpdfPage=this.pdfPage;
      vardiv=this.div;
      varcanvasWrapper=document.createElement('div');
      canvasWrapper.style.width=div.style.width;
      canvasWrapper.style.height=div.style.height;
      canvasWrapper.classList.add('canvasWrapper');

      if(this.annotationLayer&&this.annotationLayer.div){
        div.insertBefore(canvasWrapper,this.annotationLayer.div);
      }else{
        div.appendChild(canvasWrapper);
      }

      vartextLayer=null;

      if(this.textLayerMode!==_ui_utils.TextLayerMode.DISABLE&&this.textLayerFactory){
        vartextLayerDiv=document.createElement('div');
        textLayerDiv.className='textLayer';
        textLayerDiv.style.width=canvasWrapper.style.width;
        textLayerDiv.style.height=canvasWrapper.style.height;

        if(this.annotationLayer&&this.annotationLayer.div){
          div.insertBefore(textLayerDiv,this.annotationLayer.div);
        }else{
          div.appendChild(textLayerDiv);
        }

        textLayer=this.textLayerFactory.createTextLayerBuilder(textLayerDiv,this.id-1,this.viewport,this.textLayerMode===_ui_utils.TextLayerMode.ENABLE_ENHANCE);
      }

      this.textLayer=textLayer;
      varrenderContinueCallback=null;

      if(this.renderingQueue){
        renderContinueCallback=functionrenderContinueCallback(cont){
          if(!_this.renderingQueue.isHighestPriority(_this)){
            _this.renderingState=_pdf_rendering_queue.RenderingStates.PAUSED;

            _this.resume=function(){
              _this.renderingState=_pdf_rendering_queue.RenderingStates.RUNNING;
              cont();
            };

            return;
          }

          cont();
        };
      }

      varfinishPaintTask=
      /*#__PURE__*/
      function(){
        var_ref=_asyncToGenerator(
        /*#__PURE__*/
        _regenerator["default"].mark(function_callee(error){
          return_regenerator["default"].wrap(function_callee$(_context){
            while(1){
              switch(_context.prev=_context.next){
                case0:
                  if(paintTask===_this.paintTask){
                    _this.paintTask=null;
                  }

                  if(!(errorinstanceof_pdfjsLib.RenderingCancelledException)){
                    _context.next=4;
                    break;
                  }

                  _this.error=null;
                  return_context.abrupt("return");

                case4:
                  _this.renderingState=_pdf_rendering_queue.RenderingStates.FINISHED;

                  if(_this.loadingIconDiv){
                    div.removeChild(_this.loadingIconDiv);
                    delete_this.loadingIconDiv;
                  }

                  _this._resetZoomLayer(true);

                  _this.error=error;
                  _this.stats=pdfPage.stats;

                  if(_this.onAfterDraw){
                    _this.onAfterDraw();
                  }

                  _this.eventBus.dispatch('pagerendered',{
                    source:_this,
                    pageNumber:_this.id,
                    cssTransform:false
                  });

                  if(!error){
                    _context.next=13;
                    break;
                  }

                  throwerror;

                case13:
                case"end":
                  return_context.stop();
              }
            }
          },_callee);
        }));

        returnfunctionfinishPaintTask(_x){
          return_ref.apply(this,arguments);
        };
      }();

      varpaintTask=this.renderer===_ui_utils.RendererType.SVG?this.paintOnSvg(canvasWrapper):this.paintOnCanvas(canvasWrapper);
      paintTask.onRenderContinue=renderContinueCallback;
      this.paintTask=paintTask;
      varresultPromise=paintTask.promise.then(function(){
        returnfinishPaintTask(null).then(function(){
          if(textLayer){
            varreadableStream=pdfPage.streamTextContent({
              normalizeWhitespace:true
            });
            textLayer.setTextContentStream(readableStream);
            textLayer.render();
          }
        });
      },function(reason){
        returnfinishPaintTask(reason);
      });

      if(this.annotationLayerFactory){
        if(!this.annotationLayer){
          this.annotationLayer=this.annotationLayerFactory.createAnnotationLayerBuilder(div,pdfPage,this.imageResourcesPath,this.renderInteractiveForms,this.l10n);
        }

        this.annotationLayer.render(this.viewport,'display');
      }

      div.setAttribute('data-loaded',true);

      if(this.onBeforeDraw){
        this.onBeforeDraw();
      }

      returnresultPromise;
    }
  },{
    key:"paintOnCanvas",
    value:functionpaintOnCanvas(canvasWrapper){
      varrenderCapability=(0,_pdfjsLib.createPromiseCapability)();
      varresult={
        promise:renderCapability.promise,
        onRenderContinue:functiononRenderContinue(cont){
          cont();
        },
        cancel:functioncancel(){
          renderTask.cancel();
        }
      };
      varviewport=this.viewport;
      varcanvas=document.createElement('canvas');
      canvas.id=this.renderingId;
      canvas.setAttribute('hidden','hidden');
      varisCanvasHidden=true;

      varshowCanvas=functionshowCanvas(){
        if(isCanvasHidden){
          canvas.removeAttribute('hidden');
          isCanvasHidden=false;
        }
      };

      canvasWrapper.appendChild(canvas);
      this.canvas=canvas;
      canvas.mozOpaque=true;
      varctx=canvas.getContext('2d',{
        alpha:false
      });
      varoutputScale=(0,_ui_utils.getOutputScale)(ctx);
      this.outputScale=outputScale;

      if(this.useOnlyCssZoom){
        varactualSizeViewport=viewport.clone({
          scale:_ui_utils.CSS_UNITS
        });
        outputScale.sx*=actualSizeViewport.width/viewport.width;
        outputScale.sy*=actualSizeViewport.height/viewport.height;
        outputScale.scaled=true;
      }

      if(this.maxCanvasPixels>0){
        varpixelsInViewport=viewport.width*viewport.height;
        varmaxScale=Math.sqrt(this.maxCanvasPixels/pixelsInViewport);

        if(outputScale.sx>maxScale||outputScale.sy>maxScale){
          outputScale.sx=maxScale;
          outputScale.sy=maxScale;
          outputScale.scaled=true;
          this.hasRestrictedScaling=true;
        }else{
          this.hasRestrictedScaling=false;
        }
      }

      varsfx=(0,_ui_utils.approximateFraction)(outputScale.sx);
      varsfy=(0,_ui_utils.approximateFraction)(outputScale.sy);
      canvas.width=(0,_ui_utils.roundToDivide)(viewport.width*outputScale.sx,sfx[0]);
      canvas.height=(0,_ui_utils.roundToDivide)(viewport.height*outputScale.sy,sfy[0]);
      canvas.style.width=(0,_ui_utils.roundToDivide)(viewport.width,sfx[1])+'px';
      canvas.style.height=(0,_ui_utils.roundToDivide)(viewport.height,sfy[1])+'px';
      this.paintedViewportMap.set(canvas,viewport);
      vartransform=!outputScale.scaled?null:[outputScale.sx,0,0,outputScale.sy,0,0];
      varrenderContext={
        canvasContext:ctx,
        transform:transform,
        viewport:this.viewport,
        enableWebGL:this.enableWebGL,
        renderInteractiveForms:this.renderInteractiveForms
      };
      varrenderTask=this.pdfPage.render(renderContext);

      renderTask.onContinue=function(cont){
        showCanvas();

        if(result.onRenderContinue){
          result.onRenderContinue(cont);
        }else{
          cont();
        }
      };

      renderTask.promise.then(function(){
        showCanvas();
        renderCapability.resolve(undefined);
      },function(error){
        showCanvas();
        renderCapability.reject(error);
      });
      returnresult;
    }
  },{
    key:"paintOnSvg",
    value:functionpaintOnSvg(wrapper){
      var_this2=this;

      varcancelled=false;

      varensureNotCancelled=functionensureNotCancelled(){
        if(cancelled){
          thrownew_pdfjsLib.RenderingCancelledException('Renderingcancelled,page'+_this2.id,'svg');
        }
      };

      varpdfPage=this.pdfPage;
      varactualSizeViewport=this.viewport.clone({
        scale:_ui_utils.CSS_UNITS
      });
      varpromise=pdfPage.getOperatorList().then(function(opList){
        ensureNotCancelled();
        varsvgGfx=new_pdfjsLib.SVGGraphics(pdfPage.commonObjs,pdfPage.objs);
        returnsvgGfx.getSVG(opList,actualSizeViewport).then(function(svg){
          ensureNotCancelled();
          _this2.svg=svg;

          _this2.paintedViewportMap.set(svg,actualSizeViewport);

          svg.style.width=wrapper.style.width;
          svg.style.height=wrapper.style.height;
          _this2.renderingState=_pdf_rendering_queue.RenderingStates.FINISHED;
          wrapper.appendChild(svg);
        });
      });
      return{
        promise:promise,
        onRenderContinue:functiononRenderContinue(cont){
          cont();
        },
        cancel:functioncancel(){
          cancelled=true;
        }
      };
    }
  },{
    key:"setPageLabel",
    value:functionsetPageLabel(label){
      this.pageLabel=typeoflabel==='string'?label:null;

      if(this.pageLabel!==null){
        this.div.setAttribute('data-page-label',this.pageLabel);
      }else{
        this.div.removeAttribute('data-page-label');
      }
    }
  },{
    key:"width",
    get:functionget(){
      returnthis.viewport.width;
    }
  },{
    key:"height",
    get:functionget(){
      returnthis.viewport.height;
    }
  }]);

  returnPDFPageView;
}();

exports.PDFPageView=PDFPageView;

/***/}),
/*31*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.DefaultTextLayerFactory=exports.TextLayerBuilder=void0;

var_ui_utils=__webpack_require__(5);

var_pdfjsLib=__webpack_require__(7);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varEXPAND_DIVS_TIMEOUT=300;

varTextLayerBuilder=
/*#__PURE__*/
function(){
  functionTextLayerBuilder(_ref){
    vartextLayerDiv=_ref.textLayerDiv,
        eventBus=_ref.eventBus,
        pageIndex=_ref.pageIndex,
        viewport=_ref.viewport,
        _ref$findController=_ref.findController,
        findController=_ref$findController===void0?null:_ref$findController,
        _ref$enhanceTextSelec=_ref.enhanceTextSelection,
        enhanceTextSelection=_ref$enhanceTextSelec===void0?false:_ref$enhanceTextSelec;

    _classCallCheck(this,TextLayerBuilder);

    this.textLayerDiv=textLayerDiv;
    this.eventBus=eventBus||(0,_ui_utils.getGlobalEventBus)();
    this.textContent=null;
    this.textContentItemsStr=[];
    this.textContentStream=null;
    this.renderingDone=false;
    this.pageIdx=pageIndex;
    this.pageNumber=this.pageIdx+1;
    this.matches=[];
    this.viewport=viewport;
    this.textDivs=[];
    this.findController=findController;
    this.textLayerRenderTask=null;
    this.enhanceTextSelection=enhanceTextSelection;
    this._onUpdateTextLayerMatches=null;

    this._bindMouse();
  }

  _createClass(TextLayerBuilder,[{
    key:"_finishRendering",
    value:function_finishRendering(){
      this.renderingDone=true;

      if(!this.enhanceTextSelection){
        varendOfContent=document.createElement('div');
        endOfContent.className='endOfContent';
        this.textLayerDiv.appendChild(endOfContent);
      }

      this.eventBus.dispatch('textlayerrendered',{
        source:this,
        pageNumber:this.pageNumber,
        numTextDivs:this.textDivs.length
      });
    }
  },{
    key:"render",
    value:functionrender(){
      var_this=this;

      vartimeout=arguments.length>0&&arguments[0]!==undefined?arguments[0]:0;

      if(!(this.textContent||this.textContentStream)||this.renderingDone){
        return;
      }

      this.cancel();
      this.textDivs=[];
      vartextLayerFrag=document.createDocumentFragment();
      this.textLayerRenderTask=(0,_pdfjsLib.renderTextLayer)({
        textContent:this.textContent,
        textContentStream:this.textContentStream,
        container:textLayerFrag,
        viewport:this.viewport,
        textDivs:this.textDivs,
        textContentItemsStr:this.textContentItemsStr,
        timeout:timeout,
        enhanceTextSelection:this.enhanceTextSelection
      });
      this.textLayerRenderTask.promise.then(function(){
        _this.textLayerDiv.appendChild(textLayerFrag);

        _this._finishRendering();

        _this._updateMatches();
      },function(reason){});

      if(!this._onUpdateTextLayerMatches){
        this._onUpdateTextLayerMatches=function(evt){
          if(evt.pageIndex===_this.pageIdx||evt.pageIndex===-1){
            _this._updateMatches();
          }
        };

        this.eventBus.on('updatetextlayermatches',this._onUpdateTextLayerMatches);
      }
    }
  },{
    key:"cancel",
    value:functioncancel(){
      if(this.textLayerRenderTask){
        this.textLayerRenderTask.cancel();
        this.textLayerRenderTask=null;
      }

      if(this._onUpdateTextLayerMatches){
        this.eventBus.off('updatetextlayermatches',this._onUpdateTextLayerMatches);
        this._onUpdateTextLayerMatches=null;
      }
    }
  },{
    key:"setTextContentStream",
    value:functionsetTextContentStream(readableStream){
      this.cancel();
      this.textContentStream=readableStream;
    }
  },{
    key:"setTextContent",
    value:functionsetTextContent(textContent){
      this.cancel();
      this.textContent=textContent;
    }
  },{
    key:"_convertMatches",
    value:function_convertMatches(matches,matchesLength){
      if(!matches){
        return[];
      }

      varfindController=this.findController,
          textContentItemsStr=this.textContentItemsStr;
      vari=0,
          iIndex=0;
      varend=textContentItemsStr.length-1;
      varqueryLen=findController.state.query.length;
      varresult=[];

      for(varm=0,mm=matches.length;m<mm;m++){
        varmatchIdx=matches[m];

        while(i!==end&&matchIdx>=iIndex+textContentItemsStr[i].length){
          iIndex+=textContentItemsStr[i].length;
          i++;
        }

        if(i===textContentItemsStr.length){
          console.error('Couldnotfindamatchingmapping');
        }

        varmatch={
          begin:{
            divIdx:i,
            offset:matchIdx-iIndex
          }
        };

        if(matchesLength){
          matchIdx+=matchesLength[m];
        }else{
          matchIdx+=queryLen;
        }

        while(i!==end&&matchIdx>iIndex+textContentItemsStr[i].length){
          iIndex+=textContentItemsStr[i].length;
          i++;
        }

        match.end={
          divIdx:i,
          offset:matchIdx-iIndex
        };
        result.push(match);
      }

      returnresult;
    }
  },{
    key:"_renderMatches",
    value:function_renderMatches(matches){
      if(matches.length===0){
        return;
      }

      varfindController=this.findController,
          pageIdx=this.pageIdx,
          textContentItemsStr=this.textContentItemsStr,
          textDivs=this.textDivs;
      varisSelectedPage=pageIdx===findController.selected.pageIdx;
      varselectedMatchIdx=findController.selected.matchIdx;
      varhighlightAll=findController.state.highlightAll;
      varprevEnd=null;
      varinfinity={
        divIdx:-1,
        offset:undefined
      };

      functionbeginText(begin,className){
        vardivIdx=begin.divIdx;
        textDivs[divIdx].textContent='';
        appendTextToDiv(divIdx,0,begin.offset,className);
      }

      functionappendTextToDiv(divIdx,fromOffset,toOffset,className){
        vardiv=textDivs[divIdx];
        varcontent=textContentItemsStr[divIdx].substring(fromOffset,toOffset);
        varnode=document.createTextNode(content);

        if(className){
          varspan=document.createElement('span');
          span.className=className;
          span.appendChild(node);
          div.appendChild(span);
          return;
        }

        div.appendChild(node);
      }

      vari0=selectedMatchIdx,
          i1=i0+1;

      if(highlightAll){
        i0=0;
        i1=matches.length;
      }elseif(!isSelectedPage){
        return;
      }

      for(vari=i0;i<i1;i++){
        varmatch=matches[i];
        varbegin=match.begin;
        varend=match.end;
        varisSelected=isSelectedPage&&i===selectedMatchIdx;
        varhighlightSuffix=isSelected?'selected':'';

        if(isSelected){
          findController.scrollMatchIntoView({
            element:textDivs[begin.divIdx],
            pageIndex:pageIdx,
            matchIndex:selectedMatchIdx
          });
        }

        if(!prevEnd||begin.divIdx!==prevEnd.divIdx){
          if(prevEnd!==null){
            appendTextToDiv(prevEnd.divIdx,prevEnd.offset,infinity.offset);
          }

          beginText(begin);
        }else{
          appendTextToDiv(prevEnd.divIdx,prevEnd.offset,begin.offset);
        }

        if(begin.divIdx===end.divIdx){
          appendTextToDiv(begin.divIdx,begin.offset,end.offset,'highlight'+highlightSuffix);
        }else{
          appendTextToDiv(begin.divIdx,begin.offset,infinity.offset,'highlightbegin'+highlightSuffix);

          for(varn0=begin.divIdx+1,n1=end.divIdx;n0<n1;n0++){
            textDivs[n0].className='highlightmiddle'+highlightSuffix;
          }

          beginText(end,'highlightend'+highlightSuffix);
        }

        prevEnd=end;
      }

      if(prevEnd){
        appendTextToDiv(prevEnd.divIdx,prevEnd.offset,infinity.offset);
      }
    }
  },{
    key:"_updateMatches",
    value:function_updateMatches(){
      if(!this.renderingDone){
        return;
      }

      varfindController=this.findController,
          matches=this.matches,
          pageIdx=this.pageIdx,
          textContentItemsStr=this.textContentItemsStr,
          textDivs=this.textDivs;
      varclearedUntilDivIdx=-1;

      for(vari=0,ii=matches.length;i<ii;i++){
        varmatch=matches[i];
        varbegin=Math.max(clearedUntilDivIdx,match.begin.divIdx);

        for(varn=begin,end=match.end.divIdx;n<=end;n++){
          vardiv=textDivs[n];
          div.textContent=textContentItemsStr[n];
          div.className='';
        }

        clearedUntilDivIdx=match.end.divIdx+1;
      }

      if(!findController||!findController.highlightMatches){
        return;
      }

      varpageMatches=findController.pageMatches[pageIdx]||null;
      varpageMatchesLength=findController.pageMatchesLength[pageIdx]||null;
      this.matches=this._convertMatches(pageMatches,pageMatchesLength);

      this._renderMatches(this.matches);
    }
  },{
    key:"_bindMouse",
    value:function_bindMouse(){
      var_this2=this;

      vardiv=this.textLayerDiv;
      varexpandDivsTimer=null;
      div.addEventListener('mousedown',function(evt){
        if(_this2.enhanceTextSelection&&_this2.textLayerRenderTask){
          _this2.textLayerRenderTask.expandTextDivs(true);

          if(expandDivsTimer){
            clearTimeout(expandDivsTimer);
            expandDivsTimer=null;
          }

          return;
        }

        varend=div.querySelector('.endOfContent');

        if(!end){
          return;
        }

        varadjustTop=evt.target!==div;
        adjustTop=adjustTop&&window.getComputedStyle(end).getPropertyValue('-moz-user-select')!=='none';

        if(adjustTop){
          vardivBounds=div.getBoundingClientRect();
          varr=Math.max(0,(evt.pageY-divBounds.top)/divBounds.height);
          end.style.top=(r*100).toFixed(2)+'%';
        }

        end.classList.add('active');
      });
      div.addEventListener('mouseup',function(){
        if(_this2.enhanceTextSelection&&_this2.textLayerRenderTask){
          expandDivsTimer=setTimeout(function(){
            if(_this2.textLayerRenderTask){
              _this2.textLayerRenderTask.expandTextDivs(false);
            }

            expandDivsTimer=null;
          },EXPAND_DIVS_TIMEOUT);
          return;
        }

        varend=div.querySelector('.endOfContent');

        if(!end){
          return;
        }

        end.style.top='';
        end.classList.remove('active');
      });
    }
  }]);

  returnTextLayerBuilder;
}();

exports.TextLayerBuilder=TextLayerBuilder;

varDefaultTextLayerFactory=
/*#__PURE__*/
function(){
  functionDefaultTextLayerFactory(){
    _classCallCheck(this,DefaultTextLayerFactory);
  }

  _createClass(DefaultTextLayerFactory,[{
    key:"createTextLayerBuilder",
    value:functioncreateTextLayerBuilder(textLayerDiv,pageIndex,viewport){
      varenhanceTextSelection=arguments.length>3&&arguments[3]!==undefined?arguments[3]:false;
      returnnewTextLayerBuilder({
        textLayerDiv:textLayerDiv,
        pageIndex:pageIndex,
        viewport:viewport,
        enhanceTextSelection:enhanceTextSelection
      });
    }
  }]);

  returnDefaultTextLayerFactory;
}();

exports.DefaultTextLayerFactory=DefaultTextLayerFactory;

/***/}),
/*32*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.SecondaryToolbar=void0;

var_ui_utils=__webpack_require__(5);

var_pdf_cursor_tools=__webpack_require__(9);

var_pdf_single_page_viewer=__webpack_require__(33);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varSecondaryToolbar=
/*#__PURE__*/
function(){
  functionSecondaryToolbar(options,mainContainer,eventBus){
    var_this=this;

    _classCallCheck(this,SecondaryToolbar);

    this.toolbar=options.toolbar;
    this.toggleButton=options.toggleButton;
    this.toolbarButtonContainer=options.toolbarButtonContainer;
    this.buttons=[{
      element:options.presentationModeButton,
      eventName:'presentationmode',
      close:true
    },{
      element:options.openFileButton,
      eventName:'openfile',
      close:true
    },{
      element:options.printButton,
      eventName:'print',
      close:true
    },{
      element:options.downloadButton,
      eventName:'download',
      close:true
    },{
      element:options.viewBookmarkButton,
      eventName:null,
      close:true
    },{
      element:options.firstPageButton,
      eventName:'firstpage',
      close:true
    },{
      element:options.lastPageButton,
      eventName:'lastpage',
      close:true
    },{
      element:options.pageRotateCwButton,
      eventName:'rotatecw',
      close:false
    },{
      element:options.pageRotateCcwButton,
      eventName:'rotateccw',
      close:false
    },{
      element:options.cursorSelectToolButton,
      eventName:'switchcursortool',
      eventDetails:{
        tool:_pdf_cursor_tools.CursorTool.SELECT
      },
      close:true
    },{
      element:options.cursorHandToolButton,
      eventName:'switchcursortool',
      eventDetails:{
        tool:_pdf_cursor_tools.CursorTool.HAND
      },
      close:true
    },{
      element:options.scrollVerticalButton,
      eventName:'switchscrollmode',
      eventDetails:{
        mode:_ui_utils.ScrollMode.VERTICAL
      },
      close:true
    },{
      element:options.scrollHorizontalButton,
      eventName:'switchscrollmode',
      eventDetails:{
        mode:_ui_utils.ScrollMode.HORIZONTAL
      },
      close:true
    },{
      element:options.scrollWrappedButton,
      eventName:'switchscrollmode',
      eventDetails:{
        mode:_ui_utils.ScrollMode.WRAPPED
      },
      close:true
    },{
      element:options.spreadNoneButton,
      eventName:'switchspreadmode',
      eventDetails:{
        mode:_ui_utils.SpreadMode.NONE
      },
      close:true
    },{
      element:options.spreadOddButton,
      eventName:'switchspreadmode',
      eventDetails:{
        mode:_ui_utils.SpreadMode.ODD
      },
      close:true
    },{
      element:options.spreadEvenButton,
      eventName:'switchspreadmode',
      eventDetails:{
        mode:_ui_utils.SpreadMode.EVEN
      },
      close:true
    },{
      element:options.documentPropertiesButton,
      eventName:'documentproperties',
      close:true
    }];
    this.items={
      firstPage:options.firstPageButton,
      lastPage:options.lastPageButton,
      pageRotateCw:options.pageRotateCwButton,
      pageRotateCcw:options.pageRotateCcwButton
    };
    this.mainContainer=mainContainer;
    this.eventBus=eventBus;
    this.opened=false;
    this.containerHeight=null;
    this.previousContainerHeight=null;
    this.reset();

    this._bindClickListeners();

    this._bindCursorToolsListener(options);

    this._bindScrollModeListener(options);

    this._bindSpreadModeListener(options);

    this.eventBus.on('resize',this._setMaxHeight.bind(this));
    this.eventBus.on('baseviewerinit',function(evt){
      if(evt.sourceinstanceof_pdf_single_page_viewer.PDFSinglePageViewer){
        _this.toolbarButtonContainer.classList.add('hiddenScrollModeButtons','hiddenSpreadModeButtons');
      }else{
        _this.toolbarButtonContainer.classList.remove('hiddenScrollModeButtons','hiddenSpreadModeButtons');
      }
    });
  }

  _createClass(SecondaryToolbar,[{
    key:"setPageNumber",
    value:functionsetPageNumber(pageNumber){
      this.pageNumber=pageNumber;

      this._updateUIState();
    }
  },{
    key:"setPagesCount",
    value:functionsetPagesCount(pagesCount){
      this.pagesCount=pagesCount;

      this._updateUIState();
    }
  },{
    key:"reset",
    value:functionreset(){
      this.pageNumber=0;
      this.pagesCount=0;

      this._updateUIState();

      this.eventBus.dispatch('secondarytoolbarreset',{
        source:this
      });
    }
  },{
    key:"_updateUIState",
    value:function_updateUIState(){
      this.items.firstPage.disabled=this.pageNumber<=1;
      this.items.lastPage.disabled=this.pageNumber>=this.pagesCount;
      this.items.pageRotateCw.disabled=this.pagesCount===0;
      this.items.pageRotateCcw.disabled=this.pagesCount===0;
    }
  },{
    key:"_bindClickListeners",
    value:function_bindClickListeners(){
      var_this2=this;

      this.toggleButton.addEventListener('click',this.toggle.bind(this));

      var_loop=function_loop(button){
        var_this2$buttons$button=_this2.buttons[button],
            element=_this2$buttons$button.element,
            eventName=_this2$buttons$button.eventName,
            close=_this2$buttons$button.close,
            eventDetails=_this2$buttons$button.eventDetails;
        element.addEventListener('click',function(evt){
          if(eventName!==null){
            vardetails={
              source:_this2
            };

            for(varpropertyineventDetails){
              details[property]=eventDetails[property];
            }

            _this2.eventBus.dispatch(eventName,details);
          }

          if(close){
            _this2.close();
          }
        });
      };

      for(varbuttoninthis.buttons){
        _loop(button);
      }
    }
  },{
    key:"_bindCursorToolsListener",
    value:function_bindCursorToolsListener(buttons){
      this.eventBus.on('cursortoolchanged',function(_ref){
        vartool=_ref.tool;
        buttons.cursorSelectToolButton.classList.toggle('toggled',tool===_pdf_cursor_tools.CursorTool.SELECT);
        buttons.cursorHandToolButton.classList.toggle('toggled',tool===_pdf_cursor_tools.CursorTool.HAND);
      });
    }
  },{
    key:"_bindScrollModeListener",
    value:function_bindScrollModeListener(buttons){
      var_this3=this;

      functionscrollModeChanged(_ref2){
        varmode=_ref2.mode;
        buttons.scrollVerticalButton.classList.toggle('toggled',mode===_ui_utils.ScrollMode.VERTICAL);
        buttons.scrollHorizontalButton.classList.toggle('toggled',mode===_ui_utils.ScrollMode.HORIZONTAL);
        buttons.scrollWrappedButton.classList.toggle('toggled',mode===_ui_utils.ScrollMode.WRAPPED);
        varisScrollModeHorizontal=mode===_ui_utils.ScrollMode.HORIZONTAL;
        buttons.spreadNoneButton.disabled=isScrollModeHorizontal;
        buttons.spreadOddButton.disabled=isScrollModeHorizontal;
        buttons.spreadEvenButton.disabled=isScrollModeHorizontal;
      }

      this.eventBus.on('scrollmodechanged',scrollModeChanged);
      this.eventBus.on('secondarytoolbarreset',function(evt){
        if(evt.source===_this3){
          scrollModeChanged({
            mode:_ui_utils.ScrollMode.VERTICAL
          });
        }
      });
    }
  },{
    key:"_bindSpreadModeListener",
    value:function_bindSpreadModeListener(buttons){
      var_this4=this;

      functionspreadModeChanged(_ref3){
        varmode=_ref3.mode;
        buttons.spreadNoneButton.classList.toggle('toggled',mode===_ui_utils.SpreadMode.NONE);
        buttons.spreadOddButton.classList.toggle('toggled',mode===_ui_utils.SpreadMode.ODD);
        buttons.spreadEvenButton.classList.toggle('toggled',mode===_ui_utils.SpreadMode.EVEN);
      }

      this.eventBus.on('spreadmodechanged',spreadModeChanged);
      this.eventBus.on('secondarytoolbarreset',function(evt){
        if(evt.source===_this4){
          spreadModeChanged({
            mode:_ui_utils.SpreadMode.NONE
          });
        }
      });
    }
  },{
    key:"open",
    value:functionopen(){
      if(this.opened){
        return;
      }

      this.opened=true;

      this._setMaxHeight();

      this.toggleButton.classList.add('toggled');
      this.toolbar.classList.remove('hidden');
    }
  },{
    key:"close",
    value:functionclose(){
      if(!this.opened){
        return;
      }

      this.opened=false;
      this.toolbar.classList.add('hidden');
      this.toggleButton.classList.remove('toggled');
    }
  },{
    key:"toggle",
    value:functiontoggle(){
      if(this.opened){
        this.close();
      }else{
        this.open();
      }
    }
  },{
    key:"_setMaxHeight",
    value:function_setMaxHeight(){
      if(!this.opened){
        return;
      }

      this.containerHeight=this.mainContainer.clientHeight;

      if(this.containerHeight===this.previousContainerHeight){
        return;
      }

      this.toolbarButtonContainer.setAttribute('style','max-height:'+(this.containerHeight-_ui_utils.SCROLLBAR_PADDING)+'px;');
      this.previousContainerHeight=this.containerHeight;
    }
  },{
    key:"isOpen",
    get:functionget(){
      returnthis.opened;
    }
  }]);

  returnSecondaryToolbar;
}();

exports.SecondaryToolbar=SecondaryToolbar;

/***/}),
/*33*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFSinglePageViewer=void0;

var_base_viewer=__webpack_require__(28);

var_pdfjsLib=__webpack_require__(7);

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_get(target,property,receiver){if(typeofReflect!=="undefined"&&Reflect.get){_get=Reflect.get;}else{_get=function_get(target,property,receiver){varbase=_superPropBase(target,property);if(!base)return;vardesc=Object.getOwnPropertyDescriptor(base,property);if(desc.get){returndesc.get.call(receiver);}returndesc.value;};}return_get(target,property,receiver||target);}

function_superPropBase(object,property){while(!Object.prototype.hasOwnProperty.call(object,property)){object=_getPrototypeOf(object);if(object===null)break;}returnobject;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

varPDFSinglePageViewer=
/*#__PURE__*/
function(_BaseViewer){
  _inherits(PDFSinglePageViewer,_BaseViewer);

  functionPDFSinglePageViewer(options){
    var_this;

    _classCallCheck(this,PDFSinglePageViewer);

    _this=_possibleConstructorReturn(this,_getPrototypeOf(PDFSinglePageViewer).call(this,options));

    _this.eventBus.on('pagesinit',function(evt){
      _this._ensurePageViewVisible();
    });

    return_this;
  }

  _createClass(PDFSinglePageViewer,[{
    key:"_resetView",
    value:function_resetView(){
      _get(_getPrototypeOf(PDFSinglePageViewer.prototype),"_resetView",this).call(this);

      this._previousPageNumber=1;
      this._shadowViewer=document.createDocumentFragment();
      this._updateScrollDown=null;
    }
  },{
    key:"_ensurePageViewVisible",
    value:function_ensurePageViewVisible(){
      varpageView=this._pages[this._currentPageNumber-1];
      varpreviousPageView=this._pages[this._previousPageNumber-1];
      varviewerNodes=this.viewer.childNodes;

      switch(viewerNodes.length){
        case0:
          this.viewer.appendChild(pageView.div);
          break;

        case1:
          if(viewerNodes[0]!==previousPageView.div){
            thrownewError('_ensurePageViewVisible:Unexpectedpreviouslyvisiblepage.');
          }

          if(pageView===previousPageView){
            break;
          }

          this._shadowViewer.appendChild(previousPageView.div);

          this.viewer.appendChild(pageView.div);
          this.container.scrollTop=0;
          break;

        default:
          thrownewError('_ensurePageViewVisible:Onlyonepageshouldbevisibleatatime.');
      }

      this._previousPageNumber=this._currentPageNumber;
    }
  },{
    key:"_scrollUpdate",
    value:function_scrollUpdate(){
      if(this._updateScrollDown){
        this._updateScrollDown();
      }

      _get(_getPrototypeOf(PDFSinglePageViewer.prototype),"_scrollUpdate",this).call(this);
    }
  },{
    key:"_scrollIntoView",
    value:function_scrollIntoView(_ref){
      var_this2=this;

      varpageDiv=_ref.pageDiv,
          _ref$pageSpot=_ref.pageSpot,
          pageSpot=_ref$pageSpot===void0?null:_ref$pageSpot,
          _ref$pageNumber=_ref.pageNumber,
          pageNumber=_ref$pageNumber===void0?null:_ref$pageNumber;

      if(pageNumber){
        this._setCurrentPageNumber(pageNumber);
      }

      varscrolledDown=this._currentPageNumber>=this._previousPageNumber;

      this._ensurePageViewVisible();

      this.update();

      _get(_getPrototypeOf(PDFSinglePageViewer.prototype),"_scrollIntoView",this).call(this,{
        pageDiv:pageDiv,
        pageSpot:pageSpot,
        pageNumber:pageNumber
      });

      this._updateScrollDown=function(){
        _this2.scroll.down=scrolledDown;
        _this2._updateScrollDown=null;
      };
    }
  },{
    key:"_getVisiblePages",
    value:function_getVisiblePages(){
      returnthis._getCurrentVisiblePage();
    }
  },{
    key:"_updateHelper",
    value:function_updateHelper(visiblePages){}
  },{
    key:"_updateScrollMode",
    value:function_updateScrollMode(){}
  },{
    key:"_updateSpreadMode",
    value:function_updateSpreadMode(){}
  },{
    key:"_setDocumentViewerElement",
    get:functionget(){
      return(0,_pdfjsLib.shadow)(this,'_setDocumentViewerElement',this._shadowViewer);
    }
  },{
    key:"_isScrollModeHorizontal",
    get:functionget(){
      return(0,_pdfjsLib.shadow)(this,'_isScrollModeHorizontal',false);
    }
  }]);

  returnPDFSinglePageViewer;
}(_base_viewer.BaseViewer);

exports.PDFSinglePageViewer=PDFSinglePageViewer;

/***/}),
/*34*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.Toolbar=void0;

var_ui_utils=__webpack_require__(5);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varPAGE_NUMBER_LOADING_INDICATOR='visiblePageIsLoading';
varSCALE_SELECT_CONTAINER_PADDING=8;
varSCALE_SELECT_PADDING=22;

varToolbar=
/*#__PURE__*/
function(){
  functionToolbar(options,eventBus){
    varl10n=arguments.length>2&&arguments[2]!==undefined?arguments[2]:_ui_utils.NullL10n;

    _classCallCheck(this,Toolbar);

    this.toolbar=options.container;
    this.eventBus=eventBus;
    this.l10n=l10n;
    this.items=options;
    this._wasLocalized=false;
    this.reset();

    this._bindListeners();
  }

  _createClass(Toolbar,[{
    key:"setPageNumber",
    value:functionsetPageNumber(pageNumber,pageLabel){
      this.pageNumber=pageNumber;
      this.pageLabel=pageLabel;

      this._updateUIState(false);
    }
  },{
    key:"setPagesCount",
    value:functionsetPagesCount(pagesCount,hasPageLabels){
      this.pagesCount=pagesCount;
      this.hasPageLabels=hasPageLabels;

      this._updateUIState(true);
    }
  },{
    key:"setPageScale",
    value:functionsetPageScale(pageScaleValue,pageScale){
      this.pageScaleValue=(pageScaleValue||pageScale).toString();
      this.pageScale=pageScale;

      this._updateUIState(false);
    }
  },{
    key:"reset",
    value:functionreset(){
      this.pageNumber=0;
      this.pageLabel=null;
      this.hasPageLabels=false;
      this.pagesCount=0;
      this.pageScaleValue=_ui_utils.DEFAULT_SCALE_VALUE;
      this.pageScale=_ui_utils.DEFAULT_SCALE;

      this._updateUIState(true);
    }
  },{
    key:"_bindListeners",
    value:function_bindListeners(){
      var_this=this;

      vareventBus=this.eventBus,
          items=this.items;
      varself=this;
      items.previous.addEventListener('click',function(){
        eventBus.dispatch('previouspage',{
          source:self
        });
      });
      items.next.addEventListener('click',function(){
        eventBus.dispatch('nextpage',{
          source:self
        });
      });
      items.zoomIn.addEventListener('click',function(){
        eventBus.dispatch('zoomin',{
          source:self
        });
      });
      items.zoomOut.addEventListener('click',function(){
        eventBus.dispatch('zoomout',{
          source:self
        });
      });
      items.pageNumber.addEventListener('click',function(){
        this.select();
      });
      items.pageNumber.addEventListener('change',function(){
        eventBus.dispatch('pagenumberchanged',{
          source:self,
          value:this.value
        });
      });
      items.scaleSelect.addEventListener('change',function(){
        if(this.value==='custom'){
          return;
        }

        eventBus.dispatch('scalechanged',{
          source:self,
          value:this.value
        });
      });
      items.presentationModeButton.addEventListener('click',function(){
        eventBus.dispatch('presentationmode',{
          source:self
        });
      });
      items.openFile.addEventListener('click',function(){
        eventBus.dispatch('openfile',{
          source:self
        });
      });
      items.print.addEventListener('click',function(){
        eventBus.dispatch('print',{
          source:self
        });
      });
      items.download.addEventListener('click',function(){
        eventBus.dispatch('download',{
          source:self
        });
      });
      items.scaleSelect.oncontextmenu=_ui_utils.noContextMenuHandler;
      eventBus.on('localized',function(){
        _this._localized();
      });
    }
  },{
    key:"_localized",
    value:function_localized(){
      this._wasLocalized=true;

      this._adjustScaleWidth();

      this._updateUIState(true);
    }
  },{
    key:"_updateUIState",
    value:function_updateUIState(){
      varresetNumPages=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;

      if(!this._wasLocalized){
        return;
      }

      varpageNumber=this.pageNumber,
          pagesCount=this.pagesCount,
          pageScaleValue=this.pageScaleValue,
          pageScale=this.pageScale,
          items=this.items;

      if(resetNumPages){
        if(this.hasPageLabels){
          items.pageNumber.type='text';
        }else{
          items.pageNumber.type='number';
          this.l10n.get('of_pages',{
            pagesCount:pagesCount
          },'of{{pagesCount}}').then(function(msg){
            items.numPages.textContent=msg;
          });
        }

        items.pageNumber.max=pagesCount;
      }

      if(this.hasPageLabels){
        items.pageNumber.value=this.pageLabel;
        this.l10n.get('page_of_pages',{
          pageNumber:pageNumber,
          pagesCount:pagesCount
        },'({{pageNumber}}of{{pagesCount}})').then(function(msg){
          items.numPages.textContent=msg;
        });
      }else{
        items.pageNumber.value=pageNumber;
      }

      items.previous.disabled=pageNumber<=1;
      items.next.disabled=pageNumber>=pagesCount;
      items.zoomOut.disabled=pageScale<=_ui_utils.MIN_SCALE;
      items.zoomIn.disabled=pageScale>=_ui_utils.MAX_SCALE;
      varcustomScale=Math.round(pageScale*10000)/100;
      this.l10n.get('page_scale_percent',{
        scale:customScale
      },'{{scale}}%').then(function(msg){
        varoptions=items.scaleSelect.options;
        varpredefinedValueFound=false;

        for(vari=0,ii=options.length;i<ii;i++){
          varoption=options[i];

          if(option.value!==pageScaleValue){
            option.selected=false;
            continue;
          }

          option.selected=true;
          predefinedValueFound=true;
        }

        if(!predefinedValueFound){
          items.customScaleOption.textContent=msg;
          items.customScaleOption.selected=true;
        }
      });
    }
  },{
    key:"updateLoadingIndicatorState",
    value:functionupdateLoadingIndicatorState(){
      varloading=arguments.length>0&&arguments[0]!==undefined?arguments[0]:false;
      varpageNumberInput=this.items.pageNumber;
      pageNumberInput.classList.toggle(PAGE_NUMBER_LOADING_INDICATOR,loading);
    }
  },{
    key:"_adjustScaleWidth",
    value:function_adjustScaleWidth(){
      varcontainer=this.items.scaleSelectContainer;
      varselect=this.items.scaleSelect;

      _ui_utils.animationStarted.then(function(){
        if(container.clientWidth===0){
          container.setAttribute('style','display:inherit;');
        }

        if(container.clientWidth>0){
          select.setAttribute('style','min-width:inherit;');
          varwidth=select.clientWidth+SCALE_SELECT_CONTAINER_PADDING;
          select.setAttribute('style','min-width:'+(width+SCALE_SELECT_PADDING)+'px;');
          container.setAttribute('style','min-width:'+width+'px;'+'max-width:'+width+'px;');
        }
      });
    }
  }]);

  returnToolbar;
}();

exports.Toolbar=Toolbar;

/***/}),
/*35*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.ViewHistory=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varDEFAULT_VIEW_HISTORY_CACHE_SIZE=20;

varViewHistory=
/*#__PURE__*/
function(){
  functionViewHistory(fingerprint){
    var_this=this;

    varcacheSize=arguments.length>1&&arguments[1]!==undefined?arguments[1]:DEFAULT_VIEW_HISTORY_CACHE_SIZE;

    _classCallCheck(this,ViewHistory);

    this.fingerprint=fingerprint;
    this.cacheSize=cacheSize;
    this._initializedPromise=this._readFromStorage().then(function(databaseStr){
      vardatabase=JSON.parse(databaseStr||'{}');

      if(!('files'indatabase)){
        database.files=[];
      }else{
        while(database.files.length>=_this.cacheSize){
          database.files.shift();
        }
      }

      varindex=-1;

      for(vari=0,length=database.files.length;i<length;i++){
        varbranch=database.files[i];

        if(branch.fingerprint===_this.fingerprint){
          index=i;
          break;
        }
      }

      if(index===-1){
        index=database.files.push({
          fingerprint:_this.fingerprint
        })-1;
      }

      _this.file=database.files[index];
      _this.database=database;
    });
  }

  _createClass(ViewHistory,[{
    key:"_writeToStorage",
    value:function(){
      var_writeToStorage2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        vardatabaseStr;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                databaseStr=JSON.stringify(this.database);
                localStorage.setItem('pdfjs.history',databaseStr);

              case2:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      function_writeToStorage(){
        return_writeToStorage2.apply(this,arguments);
      }

      return_writeToStorage;
    }()
  },{
    key:"_readFromStorage",
    value:function(){
      var_readFromStorage2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(){
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                return_context2.abrupt("return",localStorage.getItem('pdfjs.history'));

              case1:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2);
      }));

      function_readFromStorage(){
        return_readFromStorage2.apply(this,arguments);
      }

      return_readFromStorage;
    }()
  },{
    key:"set",
    value:function(){
      var_set=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee3(name,val){
        return_regenerator["default"].wrap(function_callee3$(_context3){
          while(1){
            switch(_context3.prev=_context3.next){
              case0:
                _context3.next=2;
                returnthis._initializedPromise;

              case2:
                this.file[name]=val;
                return_context3.abrupt("return",this._writeToStorage());

              case4:
              case"end":
                return_context3.stop();
            }
          }
        },_callee3,this);
      }));

      functionset(_x,_x2){
        return_set.apply(this,arguments);
      }

      returnset;
    }()
  },{
    key:"setMultiple",
    value:function(){
      var_setMultiple=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee4(properties){
        varname;
        return_regenerator["default"].wrap(function_callee4$(_context4){
          while(1){
            switch(_context4.prev=_context4.next){
              case0:
                _context4.next=2;
                returnthis._initializedPromise;

              case2:
                for(nameinproperties){
                  this.file[name]=properties[name];
                }

                return_context4.abrupt("return",this._writeToStorage());

              case4:
              case"end":
                return_context4.stop();
            }
          }
        },_callee4,this);
      }));

      functionsetMultiple(_x3){
        return_setMultiple.apply(this,arguments);
      }

      returnsetMultiple;
    }()
  },{
    key:"get",
    value:function(){
      var_get=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee5(name,defaultValue){
        varval;
        return_regenerator["default"].wrap(function_callee5$(_context5){
          while(1){
            switch(_context5.prev=_context5.next){
              case0:
                _context5.next=2;
                returnthis._initializedPromise;

              case2:
                val=this.file[name];
                return_context5.abrupt("return",val!==undefined?val:defaultValue);

              case4:
              case"end":
                return_context5.stop();
            }
          }
        },_callee5,this);
      }));

      functionget(_x4,_x5){
        return_get.apply(this,arguments);
      }

      returnget;
    }()
  },{
    key:"getMultiple",
    value:function(){
      var_getMultiple=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee6(properties){
        varvalues,name,val;
        return_regenerator["default"].wrap(function_callee6$(_context6){
          while(1){
            switch(_context6.prev=_context6.next){
              case0:
                _context6.next=2;
                returnthis._initializedPromise;

              case2:
                values=Object.create(null);

                for(nameinproperties){
                  val=this.file[name];
                  values[name]=val!==undefined?val:properties[name];
                }

                return_context6.abrupt("return",values);

              case5:
              case"end":
                return_context6.stop();
            }
          }
        },_callee6,this);
      }));

      functiongetMultiple(_x6){
        return_getMultiple.apply(this,arguments);
      }

      returngetMultiple;
    }()
  }]);

  returnViewHistory;
}();

exports.ViewHistory=ViewHistory;

/***/}),
/*36*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.GenericCom=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

var_app=__webpack_require__(1);

var_preferences=__webpack_require__(37);

var_download_manager=__webpack_require__(38);

var_genericl10n=__webpack_require__(39);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

function_possibleConstructorReturn(self,call){if(call&&(_typeof(call)==="object"||typeofcall==="function")){returncall;}return_assertThisInitialized(self);}

function_assertThisInitialized(self){if(self===void0){thrownewReferenceError("thishasn'tbeeninitialised-super()hasn'tbeencalled");}returnself;}

function_getPrototypeOf(o){_getPrototypeOf=Object.setPrototypeOf?Object.getPrototypeOf:function_getPrototypeOf(o){returno.__proto__||Object.getPrototypeOf(o);};return_getPrototypeOf(o);}

function_inherits(subClass,superClass){if(typeofsuperClass!=="function"&&superClass!==null){thrownewTypeError("Superexpressionmusteitherbenullorafunction");}subClass.prototype=Object.create(superClass&&superClass.prototype,{constructor:{value:subClass,writable:true,configurable:true}});if(superClass)_setPrototypeOf(subClass,superClass);}

function_setPrototypeOf(o,p){_setPrototypeOf=Object.setPrototypeOf||function_setPrototypeOf(o,p){o.__proto__=p;returno;};return_setPrototypeOf(o,p);}

;
varGenericCom={};
exports.GenericCom=GenericCom;

varGenericPreferences=
/*#__PURE__*/
function(_BasePreferences){
  _inherits(GenericPreferences,_BasePreferences);

  functionGenericPreferences(){
    _classCallCheck(this,GenericPreferences);

    return_possibleConstructorReturn(this,_getPrototypeOf(GenericPreferences).apply(this,arguments));
  }

  _createClass(GenericPreferences,[{
    key:"_writeToStorage",
    value:function(){
      var_writeToStorage2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(prefObj){
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                localStorage.setItem('pdfjs.preferences',JSON.stringify(prefObj));

              case1:
              case"end":
                return_context.stop();
            }
          }
        },_callee);
      }));

      function_writeToStorage(_x){
        return_writeToStorage2.apply(this,arguments);
      }

      return_writeToStorage;
    }()
  },{
    key:"_readFromStorage",
    value:function(){
      var_readFromStorage2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(prefObj){
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                return_context2.abrupt("return",JSON.parse(localStorage.getItem('pdfjs.preferences')));

              case1:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2);
      }));

      function_readFromStorage(_x2){
        return_readFromStorage2.apply(this,arguments);
      }

      return_readFromStorage;
    }()
  }]);

  returnGenericPreferences;
}(_preferences.BasePreferences);

varGenericExternalServices=Object.create(_app.DefaultExternalServices);

GenericExternalServices.createDownloadManager=function(options){
  returnnew_download_manager.DownloadManager(options);
};

GenericExternalServices.createPreferences=function(){
  returnnewGenericPreferences();
};

GenericExternalServices.createL10n=function(_ref){
  var_ref$locale=_ref.locale,
      locale=_ref$locale===void0?'en-US':_ref$locale;
  returnnew_genericl10n.GenericL10n(locale);
};

_app.PDFViewerApplication.externalServices=GenericExternalServices;

/***/}),
/*37*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.BasePreferences=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_typeof(obj){if(typeofSymbol==="function"&&typeofSymbol.iterator==="symbol"){_typeof=function_typeof(obj){returntypeofobj;};}else{_typeof=function_typeof(obj){returnobj&&typeofSymbol==="function"&&obj.constructor===Symbol&&obj!==Symbol.prototype?"symbol":typeofobj;};}return_typeof(obj);}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

vardefaultPreferences=null;

functiongetDefaultPreferences(){
  if(!defaultPreferences){
    defaultPreferences=Promise.resolve({
      "cursorToolOnLoad":0,
      "defaultZoomValue":"",
      "disablePageLabels":false,
      "enablePrintAutoRotate":false,
      "enableWebGL":false,
      //Flectra:Thischangeisneededhereaswecan'tchangethisparameterinaniframe.
      "eventBusDispatchToDOM":true,
      "externalLinkTarget":0,
      "historyUpdateUrl":false,
      "pdfBugEnabled":false,
      "renderer":"canvas",
      "renderInteractiveForms":false,
      "sidebarViewOnLoad":-1,
      "scrollModeOnLoad":-1,
      "spreadModeOnLoad":-1,
      "textLayerMode":1,
      "useOnlyCssZoom":false,
      "viewOnLoad":0,
      "disableAutoFetch":false,
      "disableFontFace":false,
      "disableRange":false,
      "disableStream":false
    });
  }

  returndefaultPreferences;
}

varBasePreferences=
/*#__PURE__*/
function(){
  functionBasePreferences(){
    var_this=this;

    _classCallCheck(this,BasePreferences);

    if(this.constructor===BasePreferences){
      thrownewError('CannotinitializeBasePreferences.');
    }

    this.prefs=null;
    this._initializedPromise=getDefaultPreferences().then(function(defaults){
      Object.defineProperty(_this,'defaults',{
        value:Object.freeze(defaults),
        writable:false,
        enumerable:true,
        configurable:false
      });
      _this.prefs=Object.assign(Object.create(null),defaults);
      return_this._readFromStorage(defaults);
    }).then(function(prefs){
      if(!prefs){
        return;
      }

      for(varnameinprefs){
        vardefaultValue=_this.defaults[name],
            prefValue=prefs[name];

        if(defaultValue===undefined||_typeof(prefValue)!==_typeof(defaultValue)){
          continue;
        }

        _this.prefs[name]=prefValue;
      }
    });
  }

  _createClass(BasePreferences,[{
    key:"_writeToStorage",
    value:function(){
      var_writeToStorage2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(prefObj){
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                thrownewError('Notimplemented:_writeToStorage');

              case1:
              case"end":
                return_context.stop();
            }
          }
        },_callee);
      }));

      function_writeToStorage(_x){
        return_writeToStorage2.apply(this,arguments);
      }

      return_writeToStorage;
    }()
  },{
    key:"_readFromStorage",
    value:function(){
      var_readFromStorage2=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(prefObj){
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                thrownewError('Notimplemented:_readFromStorage');

              case1:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2);
      }));

      function_readFromStorage(_x2){
        return_readFromStorage2.apply(this,arguments);
      }

      return_readFromStorage;
    }()
  },{
    key:"reset",
    value:function(){
      var_reset=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee3(){
        return_regenerator["default"].wrap(function_callee3$(_context3){
          while(1){
            switch(_context3.prev=_context3.next){
              case0:
                _context3.next=2;
                returnthis._initializedPromise;

              case2:
                this.prefs=Object.assign(Object.create(null),this.defaults);
                return_context3.abrupt("return",this._writeToStorage(this.defaults));

              case4:
              case"end":
                return_context3.stop();
            }
          }
        },_callee3,this);
      }));

      functionreset(){
        return_reset.apply(this,arguments);
      }

      returnreset;
    }()
  },{
    key:"set",
    value:function(){
      var_set=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee4(name,value){
        vardefaultValue,valueType,defaultType;
        return_regenerator["default"].wrap(function_callee4$(_context4){
          while(1){
            switch(_context4.prev=_context4.next){
              case0:
                _context4.next=2;
                returnthis._initializedPromise;

              case2:
                defaultValue=this.defaults[name];

                if(!(defaultValue===undefined)){
                  _context4.next=7;
                  break;
                }

                thrownewError("Setpreference:\"".concat(name,"\"isundefined."));

              case7:
                if(!(value===undefined)){
                  _context4.next=9;
                  break;
                }

                thrownewError('Setpreference:novalueisspecified.');

              case9:
                valueType=_typeof(value);
                defaultType=_typeof(defaultValue);

                if(!(valueType!==defaultType)){
                  _context4.next=19;
                  break;
                }

                if(!(valueType==='number'&&defaultType==='string')){
                  _context4.next=16;
                  break;
                }

                value=value.toString();
                _context4.next=17;
                break;

              case16:
                thrownewError("Setpreference:\"".concat(value,"\"isa").concat(valueType,",")+"expecteda".concat(defaultType,"."));

              case17:
                _context4.next=21;
                break;

              case19:
                if(!(valueType==='number'&&!Number.isInteger(value))){
                  _context4.next=21;
                  break;
                }

                thrownewError("Setpreference:\"".concat(value,"\"mustbeaninteger."));

              case21:
                this.prefs[name]=value;
                return_context4.abrupt("return",this._writeToStorage(this.prefs));

              case23:
              case"end":
                return_context4.stop();
            }
          }
        },_callee4,this);
      }));

      functionset(_x3,_x4){
        return_set.apply(this,arguments);
      }

      returnset;
    }()
  },{
    key:"get",
    value:function(){
      var_get=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee5(name){
        vardefaultValue,prefValue;
        return_regenerator["default"].wrap(function_callee5$(_context5){
          while(1){
            switch(_context5.prev=_context5.next){
              case0:
                _context5.next=2;
                returnthis._initializedPromise;

              case2:
                defaultValue=this.defaults[name];

                if(!(defaultValue===undefined)){
                  _context5.next=7;
                  break;
                }

                thrownewError("Getpreference:\"".concat(name,"\"isundefined."));

              case7:
                prefValue=this.prefs[name];

                if(!(prefValue!==undefined)){
                  _context5.next=10;
                  break;
                }

                return_context5.abrupt("return",prefValue);

              case10:
                return_context5.abrupt("return",defaultValue);

              case11:
              case"end":
                return_context5.stop();
            }
          }
        },_callee5,this);
      }));

      functionget(_x5){
        return_get.apply(this,arguments);
      }

      returnget;
    }()
  },{
    key:"getAll",
    value:function(){
      var_getAll=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee6(){
        return_regenerator["default"].wrap(function_callee6$(_context6){
          while(1){
            switch(_context6.prev=_context6.next){
              case0:
                _context6.next=2;
                returnthis._initializedPromise;

              case2:
                return_context6.abrupt("return",Object.assign(Object.create(null),this.defaults,this.prefs));

              case3:
              case"end":
                return_context6.stop();
            }
          }
        },_callee6,this);
      }));

      functiongetAll(){
        return_getAll.apply(this,arguments);
      }

      returngetAll;
    }()
  }]);

  returnBasePreferences;
}();

exports.BasePreferences=BasePreferences;

/***/}),
/*38*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.DownloadManager=void0;

var_pdfjsLib=__webpack_require__(7);

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

;
varDISABLE_CREATE_OBJECT_URL=_pdfjsLib.apiCompatibilityParams.disableCreateObjectURL||false;

function_download(blobUrl,filename){
  vara=document.createElement('a');

  if(!a.click){
    thrownewError('DownloadManager:"a.click()"isnotsupported.');
  }

  a.href=blobUrl;
  a.target='_parent';

  if('download'ina){
    a.download=filename;
  }

  (document.body||document.documentElement).appendChild(a);
  a.click();
  a.remove();
}

varDownloadManager=
/*#__PURE__*/
function(){
  functionDownloadManager(_ref){
    var_ref$disableCreateObj=_ref.disableCreateObjectURL,
        disableCreateObjectURL=_ref$disableCreateObj===void0?DISABLE_CREATE_OBJECT_URL:_ref$disableCreateObj;

    _classCallCheck(this,DownloadManager);

    this.disableCreateObjectURL=disableCreateObjectURL;
  }

  _createClass(DownloadManager,[{
    key:"downloadUrl",
    value:functiondownloadUrl(url,filename){
      if(!(0,_pdfjsLib.createValidAbsoluteUrl)(url,'http://example.com')){
        return;
      }

      _download(url+'#pdfjs.action=download',filename);
    }
  },{
    key:"downloadData",
    value:functiondownloadData(data,filename,contentType){
      if(navigator.msSaveBlob){
        navigator.msSaveBlob(newBlob([data],{
          type:contentType
        }),filename);
        return;
      }

      varblobUrl=(0,_pdfjsLib.createObjectURL)(data,contentType,this.disableCreateObjectURL);

      _download(blobUrl,filename);
    }
  },{
    key:"download",
    value:functiondownload(blob,url,filename){
      if(navigator.msSaveBlob){
        if(!navigator.msSaveBlob(blob,filename)){
          this.downloadUrl(url,filename);
        }

        return;
      }

      if(this.disableCreateObjectURL){
        this.downloadUrl(url,filename);
        return;
      }

      varblobUrl=_pdfjsLib.URL.createObjectURL(blob);

      _download(blobUrl,filename);
    }
  }]);

  returnDownloadManager;
}();

exports.DownloadManager=DownloadManager;

/***/}),
/*39*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.GenericL10n=void0;

var_regenerator=_interopRequireDefault(__webpack_require__(2));

__webpack_require__(40);

function_interopRequireDefault(obj){returnobj&&obj.__esModule?obj:{"default":obj};}

functionasyncGeneratorStep(gen,resolve,reject,_next,_throw,key,arg){try{varinfo=gen[key](arg);varvalue=info.value;}catch(error){reject(error);return;}if(info.done){resolve(value);}else{Promise.resolve(value).then(_next,_throw);}}

function_asyncToGenerator(fn){returnfunction(){varself=this,args=arguments;returnnewPromise(function(resolve,reject){vargen=fn.apply(self,args);function_next(value){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"next",value);}function_throw(err){asyncGeneratorStep(gen,resolve,reject,_next,_throw,"throw",err);}_next(undefined);});};}

function_classCallCheck(instance,Constructor){if(!(instanceinstanceofConstructor)){thrownewTypeError("Cannotcallaclassasafunction");}}

function_defineProperties(target,props){for(vari=0;i<props.length;i++){vardescriptor=props[i];descriptor.enumerable=descriptor.enumerable||false;descriptor.configurable=true;if("value"indescriptor)descriptor.writable=true;Object.defineProperty(target,descriptor.key,descriptor);}}

function_createClass(Constructor,protoProps,staticProps){if(protoProps)_defineProperties(Constructor.prototype,protoProps);if(staticProps)_defineProperties(Constructor,staticProps);returnConstructor;}

varwebL10n=document.webL10n;

varGenericL10n=
/*#__PURE__*/
function(){
  functionGenericL10n(lang){
    _classCallCheck(this,GenericL10n);

    this._lang=lang;
    this._ready=newPromise(function(resolve,reject){
      webL10n.setLanguage(lang,function(){
        resolve(webL10n);
      });
    });
  }

  _createClass(GenericL10n,[{
    key:"getLanguage",
    value:function(){
      var_getLanguage=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee(){
        varl10n;
        return_regenerator["default"].wrap(function_callee$(_context){
          while(1){
            switch(_context.prev=_context.next){
              case0:
                _context.next=2;
                returnthis._ready;

              case2:
                l10n=_context.sent;
                return_context.abrupt("return",l10n.getLanguage());

              case4:
              case"end":
                return_context.stop();
            }
          }
        },_callee,this);
      }));

      functiongetLanguage(){
        return_getLanguage.apply(this,arguments);
      }

      returngetLanguage;
    }()
  },{
    key:"getDirection",
    value:function(){
      var_getDirection=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee2(){
        varl10n;
        return_regenerator["default"].wrap(function_callee2$(_context2){
          while(1){
            switch(_context2.prev=_context2.next){
              case0:
                _context2.next=2;
                returnthis._ready;

              case2:
                l10n=_context2.sent;
                return_context2.abrupt("return",l10n.getDirection());

              case4:
              case"end":
                return_context2.stop();
            }
          }
        },_callee2,this);
      }));

      functiongetDirection(){
        return_getDirection.apply(this,arguments);
      }

      returngetDirection;
    }()
  },{
    key:"get",
    value:function(){
      var_get=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee3(property,args,fallback){
        varl10n;
        return_regenerator["default"].wrap(function_callee3$(_context3){
          while(1){
            switch(_context3.prev=_context3.next){
              case0:
                _context3.next=2;
                returnthis._ready;

              case2:
                l10n=_context3.sent;
                return_context3.abrupt("return",l10n.get(property,args,fallback));

              case4:
              case"end":
                return_context3.stop();
            }
          }
        },_callee3,this);
      }));

      functionget(_x,_x2,_x3){
        return_get.apply(this,arguments);
      }

      returnget;
    }()
  },{
    key:"translate",
    value:function(){
      var_translate=_asyncToGenerator(
      /*#__PURE__*/
      _regenerator["default"].mark(function_callee4(element){
        varl10n;
        return_regenerator["default"].wrap(function_callee4$(_context4){
          while(1){
            switch(_context4.prev=_context4.next){
              case0:
                _context4.next=2;
                returnthis._ready;

              case2:
                l10n=_context4.sent;
                return_context4.abrupt("return",l10n.translate(element));

              case4:
              case"end":
                return_context4.stop();
            }
          }
        },_callee4,this);
      }));

      functiontranslate(_x4){
        return_translate.apply(this,arguments);
      }

      returntranslate;
    }()
  }]);

  returnGenericL10n;
}();

exports.GenericL10n=GenericL10n;

/***/}),
/*40*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


document.webL10n=function(window,document,undefined){
  vargL10nData={};
  vargTextData='';
  vargTextProp='textContent';
  vargLanguage='';
  vargMacros={};
  vargReadyState='loading';
  vargAsyncResourceLoading=true;

  functiongetL10nResourceLinks(){
    returndocument.querySelectorAll('link[type="application/l10n"]');
  }

  functiongetL10nDictionary(){
    varscript=document.querySelector('script[type="application/l10n"]');
    returnscript?JSON.parse(script.innerHTML):null;
  }

  functiongetTranslatableChildren(element){
    returnelement?element.querySelectorAll('*[data-l10n-id]'):[];
  }

  functiongetL10nAttributes(element){
    if(!element)return{};
    varl10nId=element.getAttribute('data-l10n-id');
    varl10nArgs=element.getAttribute('data-l10n-args');
    varargs={};

    if(l10nArgs){
      try{
        args=JSON.parse(l10nArgs);
      }catch(e){
        console.warn('couldnotparseargumentsfor#'+l10nId);
      }
    }

    return{
      id:l10nId,
      args:args
    };
  }

  functionfireL10nReadyEvent(lang){
    varevtObject=document.createEvent('Event');
    evtObject.initEvent('localized',true,false);
    evtObject.language=lang;
    document.dispatchEvent(evtObject);
  }

  functionxhrLoadText(url,onSuccess,onFailure){
    onSuccess=onSuccess||function_onSuccess(data){};

    onFailure=onFailure||function_onFailure(){};

    varxhr=newXMLHttpRequest();
    xhr.open('GET',url,gAsyncResourceLoading);

    if(xhr.overrideMimeType){
      xhr.overrideMimeType('text/plain;charset=utf-8');
    }

    xhr.onreadystatechange=function(){
      if(xhr.readyState==4){
        if(xhr.status==200||xhr.status===0){
          onSuccess(xhr.responseText);
        }else{
          onFailure();
        }
      }
    };

    xhr.onerror=onFailure;
    xhr.ontimeout=onFailure;

    try{
      xhr.send(null);
    }catch(e){
      onFailure();
    }
  }

  functionparseResource(href,lang,successCallback,failureCallback){
    varbaseURL=href.replace(/[^\/]*$/,'')||'./';

    functionevalString(text){
      if(text.lastIndexOf('\\')<0)returntext;
      returntext.replace(/\\\\/g,'\\').replace(/\\n/g,'\n').replace(/\\r/g,'\r').replace(/\\t/g,'\t').replace(/\\b/g,'\b').replace(/\\f/g,'\f').replace(/\\{/g,'{').replace(/\\}/g,'}').replace(/\\"/g,'"').replace(/\\'/g,"'");
    }

    functionparseProperties(text,parsedPropertiesCallback){
      vardictionary={};
      varreBlank=/^\s*|\s*$/;
      varreComment=/^\s*#|^\s*$/;
      varreSection=/^\s*\[(.*)\]\s*$/;
      varreImport=/^\s*@import\s+url\((.*)\)\s*$/i;
      varreSplit=/^([^=\s]*)\s*=\s*(.+)$/;

      functionparseRawLines(rawText,extendedSyntax,parsedRawLinesCallback){
        varentries=rawText.replace(reBlank,'').split(/[\r\n]+/);
        varcurrentLang='*';
        vargenericLang=lang.split('-',1)[0];
        varskipLang=false;
        varmatch='';

        functionnextEntry(){
          while(true){
            if(!entries.length){
              parsedRawLinesCallback();
              return;
            }

            varline=entries.shift();
            if(reComment.test(line))continue;

            if(extendedSyntax){
              match=reSection.exec(line);

              if(match){
                currentLang=match[1].toLowerCase();
                skipLang=currentLang!=='*'&&currentLang!==lang&&currentLang!==genericLang;
                continue;
              }elseif(skipLang){
                continue;
              }

              match=reImport.exec(line);

              if(match){
                loadImport(baseURL+match[1],nextEntry);
                return;
              }
            }

            vartmp=line.match(reSplit);

            if(tmp&&tmp.length==3){
              dictionary[tmp[1]]=evalString(tmp[2]);
            }
          }
        }

        nextEntry();
      }

      functionloadImport(url,callback){
        xhrLoadText(url,function(content){
          parseRawLines(content,false,callback);
        },function(){
          console.warn(url+'notfound.');
          callback();
        });
      }

      parseRawLines(text,true,function(){
        parsedPropertiesCallback(dictionary);
      });
    }

    xhrLoadText(href,function(response){
      gTextData+=response;
      parseProperties(response,function(data){
        for(varkeyindata){
          varid,
              prop,
              index=key.lastIndexOf('.');

          if(index>0){
            id=key.substring(0,index);
            prop=key.substring(index+1);
          }else{
            id=key;
            prop=gTextProp;
          }

          if(!gL10nData[id]){
            gL10nData[id]={};
          }

          gL10nData[id][prop]=data[key];
        }

        if(successCallback){
          successCallback();
        }
      });
    },failureCallback);
  }

  functionloadLocale(lang,callback){
    if(lang){
      lang=lang.toLowerCase();
    }

    callback=callback||function_callback(){};

    clear();
    gLanguage=lang;
    varlangLinks=getL10nResourceLinks();
    varlangCount=langLinks.length;

    if(langCount===0){
      vardict=getL10nDictionary();

      if(dict&&dict.locales&&dict.default_locale){
        console.log('usingtheembeddedJSONdirectory,earlywayout');
        gL10nData=dict.locales[lang];

        if(!gL10nData){
          vardefaultLocale=dict.default_locale.toLowerCase();

          for(varanyCaseLangindict.locales){
            anyCaseLang=anyCaseLang.toLowerCase();

            if(anyCaseLang===lang){
              gL10nData=dict.locales[lang];
              break;
            }elseif(anyCaseLang===defaultLocale){
              gL10nData=dict.locales[defaultLocale];
            }
          }
        }

        callback();
      }else{
        console.log('noresourcetoload,earlywayout');
      }

      fireL10nReadyEvent(lang);
      gReadyState='complete';
      return;
    }

    varonResourceLoaded=null;
    vargResourceCount=0;

    onResourceLoaded=functiononResourceLoaded(){
      gResourceCount++;

      if(gResourceCount>=langCount){
        callback();
        fireL10nReadyEvent(lang);
        gReadyState='complete';
      }
    };

    functionL10nResourceLink(link){
      varhref=link.href;

      this.load=function(lang,callback){
        parseResource(href,lang,callback,function(){
          console.warn(href+'notfound.');
          console.warn('"'+lang+'"resourcenotfound');
          gLanguage='';
          callback();
        });
      };
    }

    for(vari=0;i<langCount;i++){
      varresource=newL10nResourceLink(langLinks[i]);
      resource.load(lang,onResourceLoaded);
    }
  }

  functionclear(){
    gL10nData={};
    gTextData='';
    gLanguage='';
  }

  functiongetPluralRules(lang){
    varlocales2rules={
      'af':3,
      'ak':4,
      'am':4,
      'ar':1,
      'asa':3,
      'az':0,
      'be':11,
      'bem':3,
      'bez':3,
      'bg':3,
      'bh':4,
      'bm':0,
      'bn':3,
      'bo':0,
      'br':20,
      'brx':3,
      'bs':11,
      'ca':3,
      'cgg':3,
      'chr':3,
      'cs':12,
      'cy':17,
      'da':3,
      'de':3,
      'dv':3,
      'dz':0,
      'ee':3,
      'el':3,
      'en':3,
      'eo':3,
      'es':3,
      'et':3,
      'eu':3,
      'fa':0,
      'ff':5,
      'fi':3,
      'fil':4,
      'fo':3,
      'fr':5,
      'fur':3,
      'fy':3,
      'ga':8,
      'gd':24,
      'gl':3,
      'gsw':3,
      'gu':3,
      'guw':4,
      'gv':23,
      'ha':3,
      'haw':3,
      'he':2,
      'hi':4,
      'hr':11,
      'hu':0,
      'id':0,
      'ig':0,
      'ii':0,
      'is':3,
      'it':3,
      'iu':7,
      'ja':0,
      'jmc':3,
      'jv':0,
      'ka':0,
      'kab':5,
      'kaj':3,
      'kcg':3,
      'kde':0,
      'kea':0,
      'kk':3,
      'kl':3,
      'km':0,
      'kn':0,
      'ko':0,
      'ksb':3,
      'ksh':21,
      'ku':3,
      'kw':7,
      'lag':18,
      'lb':3,
      'lg':3,
      'ln':4,
      'lo':0,
      'lt':10,
      'lv':6,
      'mas':3,
      'mg':4,
      'mk':16,
      'ml':3,
      'mn':3,
      'mo':9,
      'mr':3,
      'ms':0,
      'mt':15,
      'my':0,
      'nah':3,
      'naq':7,
      'nb':3,
      'nd':3,
      'ne':3,
      'nl':3,
      'nn':3,
      'no':3,
      'nr':3,
      'nso':4,
      'ny':3,
      'nyn':3,
      'om':3,
      'or':3,
      'pa':3,
      'pap':3,
      'pl':13,
      'ps':3,
      'pt':3,
      'rm':3,
      'ro':9,
      'rof':3,
      'ru':11,
      'rwk':3,
      'sah':0,
      'saq':3,
      'se':7,
      'seh':3,
      'ses':0,
      'sg':0,
      'sh':11,
      'shi':19,
      'sk':12,
      'sl':14,
      'sma':7,
      'smi':7,
      'smj':7,
      'smn':7,
      'sms':7,
      'sn':3,
      'so':3,
      'sq':3,
      'sr':11,
      'ss':3,
      'ssy':3,
      'st':3,
      'sv':3,
      'sw':3,
      'syr':3,
      'ta':3,
      'te':3,
      'teo':3,
      'th':0,
      'ti':4,
      'tig':3,
      'tk':3,
      'tl':4,
      'tn':3,
      'to':0,
      'tr':0,
      'ts':3,
      'tzm':22,
      'uk':11,
      'ur':3,
      've':3,
      'vi':0,
      'vun':3,
      'wa':4,
      'wae':3,
      'wo':0,
      'xh':3,
      'xog':3,
      'yo':0,
      'zh':0,
      'zu':3
    };

    functionisIn(n,list){
      returnlist.indexOf(n)!==-1;
    }

    functionisBetween(n,start,end){
      returnstart<=n&&n<=end;
    }

    varpluralRules={
      '0':function_(n){
        return'other';
      },
      '1':function_(n){
        if(isBetween(n%100,3,10))return'few';
        if(n===0)return'zero';
        if(isBetween(n%100,11,99))return'many';
        if(n==2)return'two';
        if(n==1)return'one';
        return'other';
      },
      '2':function_(n){
        if(n!==0&&n%10===0)return'many';
        if(n==2)return'two';
        if(n==1)return'one';
        return'other';
      },
      '3':function_(n){
        if(n==1)return'one';
        return'other';
      },
      '4':function_(n){
        if(isBetween(n,0,1))return'one';
        return'other';
      },
      '5':function_(n){
        if(isBetween(n,0,2)&&n!=2)return'one';
        return'other';
      },
      '6':function_(n){
        if(n===0)return'zero';
        if(n%10==1&&n%100!=11)return'one';
        return'other';
      },
      '7':function_(n){
        if(n==2)return'two';
        if(n==1)return'one';
        return'other';
      },
      '8':function_(n){
        if(isBetween(n,3,6))return'few';
        if(isBetween(n,7,10))return'many';
        if(n==2)return'two';
        if(n==1)return'one';
        return'other';
      },
      '9':function_(n){
        if(n===0||n!=1&&isBetween(n%100,1,19))return'few';
        if(n==1)return'one';
        return'other';
      },
      '10':function_(n){
        if(isBetween(n%10,2,9)&&!isBetween(n%100,11,19))return'few';
        if(n%10==1&&!isBetween(n%100,11,19))return'one';
        return'other';
      },
      '11':function_(n){
        if(isBetween(n%10,2,4)&&!isBetween(n%100,12,14))return'few';
        if(n%10===0||isBetween(n%10,5,9)||isBetween(n%100,11,14))return'many';
        if(n%10==1&&n%100!=11)return'one';
        return'other';
      },
      '12':function_(n){
        if(isBetween(n,2,4))return'few';
        if(n==1)return'one';
        return'other';
      },
      '13':function_(n){
        if(isBetween(n%10,2,4)&&!isBetween(n%100,12,14))return'few';
        if(n!=1&&isBetween(n%10,0,1)||isBetween(n%10,5,9)||isBetween(n%100,12,14))return'many';
        if(n==1)return'one';
        return'other';
      },
      '14':function_(n){
        if(isBetween(n%100,3,4))return'few';
        if(n%100==2)return'two';
        if(n%100==1)return'one';
        return'other';
      },
      '15':function_(n){
        if(n===0||isBetween(n%100,2,10))return'few';
        if(isBetween(n%100,11,19))return'many';
        if(n==1)return'one';
        return'other';
      },
      '16':function_(n){
        if(n%10==1&&n!=11)return'one';
        return'other';
      },
      '17':function_(n){
        if(n==3)return'few';
        if(n===0)return'zero';
        if(n==6)return'many';
        if(n==2)return'two';
        if(n==1)return'one';
        return'other';
      },
      '18':function_(n){
        if(n===0)return'zero';
        if(isBetween(n,0,2)&&n!==0&&n!=2)return'one';
        return'other';
      },
      '19':function_(n){
        if(isBetween(n,2,10))return'few';
        if(isBetween(n,0,1))return'one';
        return'other';
      },
      '20':function_(n){
        if((isBetween(n%10,3,4)||n%10==9)&&!(isBetween(n%100,10,19)||isBetween(n%100,70,79)||isBetween(n%100,90,99)))return'few';
        if(n%1000000===0&&n!==0)return'many';
        if(n%10==2&&!isIn(n%100,[12,72,92]))return'two';
        if(n%10==1&&!isIn(n%100,[11,71,91]))return'one';
        return'other';
      },
      '21':function_(n){
        if(n===0)return'zero';
        if(n==1)return'one';
        return'other';
      },
      '22':function_(n){
        if(isBetween(n,0,1)||isBetween(n,11,99))return'one';
        return'other';
      },
      '23':function_(n){
        if(isBetween(n%10,1,2)||n%20===0)return'one';
        return'other';
      },
      '24':function_(n){
        if(isBetween(n,3,10)||isBetween(n,13,19))return'few';
        if(isIn(n,[2,12]))return'two';
        if(isIn(n,[1,11]))return'one';
        return'other';
      }
    };
    varindex=locales2rules[lang.replace(/-.*$/,'')];

    if(!(indexinpluralRules)){
      console.warn('pluralformunknownfor['+lang+']');
      returnfunction(){
        return'other';
      };
    }

    returnpluralRules[index];
  }

  gMacros.plural=function(str,param,key,prop){
    varn=parseFloat(param);
    if(isNaN(n))returnstr;
    if(prop!=gTextProp)returnstr;

    if(!gMacros._pluralRules){
      gMacros._pluralRules=getPluralRules(gLanguage);
    }

    varindex='['+gMacros._pluralRules(n)+']';

    if(n===0&&key+'[zero]'ingL10nData){
      str=gL10nData[key+'[zero]'][prop];
    }elseif(n==1&&key+'[one]'ingL10nData){
      str=gL10nData[key+'[one]'][prop];
    }elseif(n==2&&key+'[two]'ingL10nData){
      str=gL10nData[key+'[two]'][prop];
    }elseif(key+indexingL10nData){
      str=gL10nData[key+index][prop];
    }elseif(key+'[other]'ingL10nData){
      str=gL10nData[key+'[other]'][prop];
    }

    returnstr;
  };

  functiongetL10nData(key,args,fallback){
    vardata=gL10nData[key];

    if(!data){
      console.warn('#'+key+'isundefined.');

      if(!fallback){
        returnnull;
      }

      data=fallback;
    }

    varrv={};

    for(varpropindata){
      varstr=data[prop];
      str=substIndexes(str,args,key,prop);
      str=substArguments(str,args,key);
      rv[prop]=str;
    }

    returnrv;
  }

  functionsubstIndexes(str,args,key,prop){
    varreIndex=/\{\[\s*([a-zA-Z]+)\(([a-zA-Z]+)\)\s*\]\}/;
    varreMatch=reIndex.exec(str);
    if(!reMatch||!reMatch.length)returnstr;
    varmacroName=reMatch[1];
    varparamName=reMatch[2];
    varparam;

    if(args&&paramNameinargs){
      param=args[paramName];
    }elseif(paramNameingL10nData){
      param=gL10nData[paramName];
    }

    if(macroNameingMacros){
      varmacro=gMacros[macroName];
      str=macro(str,param,key,prop);
    }

    returnstr;
  }

  functionsubstArguments(str,args,key){
    varreArgs=/\{\{\s*(.+?)\s*\}\}/g;
    returnstr.replace(reArgs,function(matched_text,arg){
      if(args&&arginargs){
        returnargs[arg];
      }

      if(argingL10nData){
        returngL10nData[arg];
      }

      console.log('argument{{'+arg+'}}for#'+key+'isundefined.');
      returnmatched_text;
    });
  }

  functiontranslateElement(element){
    varl10n=getL10nAttributes(element);
    if(!l10n.id)return;
    vardata=getL10nData(l10n.id,l10n.args);

    if(!data){
      console.warn('#'+l10n.id+'isundefined.');
      return;
    }

    if(data[gTextProp]){
      if(getChildElementCount(element)===0){
        element[gTextProp]=data[gTextProp];
      }else{
        varchildren=element.childNodes;
        varfound=false;

        for(vari=0,l=children.length;i<l;i++){
          if(children[i].nodeType===3&&/\S/.test(children[i].nodeValue)){
            if(found){
              children[i].nodeValue='';
            }else{
              children[i].nodeValue=data[gTextProp];
              found=true;
            }
          }
        }

        if(!found){
          vartextNode=document.createTextNode(data[gTextProp]);
          element.insertBefore(textNode,element.firstChild);
        }
      }

      deletedata[gTextProp];
    }

    for(varkindata){
      element[k]=data[k];
    }
  }

  functiongetChildElementCount(element){
    if(element.children){
      returnelement.children.length;
    }

    if(typeofelement.childElementCount!=='undefined'){
      returnelement.childElementCount;
    }

    varcount=0;

    for(vari=0;i<element.childNodes.length;i++){
      count+=element.nodeType===1?1:0;
    }

    returncount;
  }

  functiontranslateFragment(element){
    element=element||document.documentElement;
    varchildren=getTranslatableChildren(element);
    varelementCount=children.length;

    for(vari=0;i<elementCount;i++){
      translateElement(children[i]);
    }

    translateElement(element);
  }

  return{
    get:functionget(key,args,fallbackString){
      varindex=key.lastIndexOf('.');
      varprop=gTextProp;

      if(index>0){
        prop=key.substring(index+1);
        key=key.substring(0,index);
      }

      varfallback;

      if(fallbackString){
        fallback={};
        fallback[prop]=fallbackString;
      }

      vardata=getL10nData(key,args,fallback);

      if(data&&propindata){
        returndata[prop];
      }

      return'{{'+key+'}}';
    },
    getData:functiongetData(){
      returngL10nData;
    },
    getText:functiongetText(){
      returngTextData;
    },
    getLanguage:functiongetLanguage(){
      returngLanguage;
    },
    setLanguage:functionsetLanguage(lang,callback){
      loadLocale(lang,function(){
        if(callback)callback();
      });
    },
    getDirection:functiongetDirection(){
      varrtlList=['ar','he','fa','ps','ur'];
      varshortCode=gLanguage.split('-',1)[0];
      returnrtlList.indexOf(shortCode)>=0?'rtl':'ltr';
    },
    translate:translateFragment,
    getReadyState:functiongetReadyState(){
      returngReadyState;
    },
    ready:functionready(callback){
      if(!callback){
        return;
      }elseif(gReadyState=='complete'||gReadyState=='interactive'){
        window.setTimeout(function(){
          callback();
        });
      }elseif(document.addEventListener){
        document.addEventListener('localized',functiononce(){
          document.removeEventListener('localized',once);
          callback();
        });
      }
    }
  };
}(window,document);

/***/}),
/*41*/
/***/(function(module,exports,__webpack_require__){

"usestrict";


Object.defineProperty(exports,"__esModule",{
  value:true
});
exports.PDFPrintService=PDFPrintService;

var_ui_utils=__webpack_require__(5);

var_app=__webpack_require__(1);

var_app_options=__webpack_require__(6);

var_pdfjsLib=__webpack_require__(7);

varactiveService=null;
varoverlayManager=null;

functionrenderPage(activeServiceOnEntry,pdfDocument,pageNumber,size){
  varscratchCanvas=activeService.scratchCanvas;
  varPRINT_RESOLUTION=_app_options.AppOptions.get('printResolution')||150;
  varPRINT_UNITS=PRINT_RESOLUTION/72.0;
  scratchCanvas.width=Math.floor(size.width*PRINT_UNITS);
  scratchCanvas.height=Math.floor(size.height*PRINT_UNITS);
  varwidth=Math.floor(size.width*_ui_utils.CSS_UNITS)+'px';
  varheight=Math.floor(size.height*_ui_utils.CSS_UNITS)+'px';
  varctx=scratchCanvas.getContext('2d');
  ctx.save();
  ctx.fillStyle='rgb(255,255,255)';
  ctx.fillRect(0,0,scratchCanvas.width,scratchCanvas.height);
  ctx.restore();
  returnpdfDocument.getPage(pageNumber).then(function(pdfPage){
    varrenderContext={
      canvasContext:ctx,
      transform:[PRINT_UNITS,0,0,PRINT_UNITS,0,0],
      viewport:pdfPage.getViewport({
        scale:1,
        rotation:size.rotation
      }),
      intent:'print'
    };
    returnpdfPage.render(renderContext).promise;
  }).then(function(){
    return{
      width:width,
      height:height
    };
  });
}

functionPDFPrintService(pdfDocument,pagesOverview,printContainer,l10n){
  this.pdfDocument=pdfDocument;
  this.pagesOverview=pagesOverview;
  this.printContainer=printContainer;
  this.l10n=l10n||_ui_utils.NullL10n;
  this.disableCreateObjectURL=pdfDocument.loadingParams['disableCreateObjectURL'];
  this.currentPage=-1;
  this.scratchCanvas=document.createElement('canvas');
}

PDFPrintService.prototype={
  layout:functionlayout(){
    this.throwIfInactive();
    varbody=document.querySelector('body');
    body.setAttribute('data-pdfjsprinting',true);
    varhasEqualPageSizes=this.pagesOverview.every(function(size){
      returnsize.width===this.pagesOverview[0].width&&size.height===this.pagesOverview[0].height;
    },this);

    if(!hasEqualPageSizes){
      console.warn('Notallpageshavethesamesize.Theprinted'+'resultmaybeincorrect!');
    }

    this.pageStyleSheet=document.createElement('style');
    varpageSize=this.pagesOverview[0];
    this.pageStyleSheet.textContent='@supports((size:A4)and(size:1pt1pt)){'+'@page{size:'+pageSize.width+'pt'+pageSize.height+'pt;}'+'}';
    body.appendChild(this.pageStyleSheet);
  },
  destroy:functiondestroy(){
    if(activeService!==this){
      return;
    }

    this.printContainer.textContent='';

    if(this.pageStyleSheet){
      this.pageStyleSheet.remove();
      this.pageStyleSheet=null;
    }

    this.scratchCanvas.width=this.scratchCanvas.height=0;
    this.scratchCanvas=null;
    activeService=null;
    ensureOverlay().then(function(){
      if(overlayManager.active!=='printServiceOverlay'){
        return;
      }

      overlayManager.close('printServiceOverlay');
    });
  },
  renderPages:functionrenderPages(){
    var_this=this;

    varpageCount=this.pagesOverview.length;

    varrenderNextPage=functionrenderNextPage(resolve,reject){
      _this.throwIfInactive();

      if(++_this.currentPage>=pageCount){
        renderProgress(pageCount,pageCount,_this.l10n);
        resolve();
        return;
      }

      varindex=_this.currentPage;
      renderProgress(index,pageCount,_this.l10n);
      renderPage(_this,_this.pdfDocument,index+1,_this.pagesOverview[index]).then(_this.useRenderedPage.bind(_this)).then(function(){
        renderNextPage(resolve,reject);
      },reject);
    };

    returnnewPromise(renderNextPage);
  },
  useRenderedPage:functionuseRenderedPage(printItem){
    this.throwIfInactive();
    varimg=document.createElement('img');
    img.style.width=printItem.width;
    img.style.height=printItem.height;
    varscratchCanvas=this.scratchCanvas;

    if('toBlob'inscratchCanvas&&!this.disableCreateObjectURL){
      scratchCanvas.toBlob(function(blob){
        img.src=_pdfjsLib.URL.createObjectURL(blob);
      });
    }else{
      img.src=scratchCanvas.toDataURL();
    }

    varwrapper=document.createElement('div');
    wrapper.appendChild(img);
    this.printContainer.appendChild(wrapper);
    returnnewPromise(function(resolve,reject){
      img.onload=resolve;
      img.onerror=reject;
    });
  },
  performPrint:functionperformPrint(){
    var_this2=this;

    this.throwIfInactive();
    returnnewPromise(function(resolve){
      setTimeout(function(){
        if(!_this2.active){
          resolve();
          return;
        }

        print.call(window);
        setTimeout(resolve,20);
      },0);
    });
  },

  getactive(){
    returnthis===activeService;
  },

  throwIfInactive:functionthrowIfInactive(){
    if(!this.active){
      thrownewError('Thisprintrequestwascancelledorcompleted.');
    }
  }
};
varprint=window.print;

window.print=functionprint(){
  if(activeService){
    console.warn('Ignoredwindow.print()becauseofapendingprintjob.');
    return;
  }

  ensureOverlay().then(function(){
    if(activeService){
      overlayManager.open('printServiceOverlay');
    }
  });

  try{
    dispatchEvent('beforeprint');
  }finally{
    if(!activeService){
      console.error('Expectedprintservicetobeinitialized.');
      ensureOverlay().then(function(){
        if(overlayManager.active==='printServiceOverlay'){
          overlayManager.close('printServiceOverlay');
        }
      });
      return;
    }

    varactiveServiceOnEntry=activeService;
    activeService.renderPages().then(function(){
      returnactiveServiceOnEntry.performPrint();
    })["catch"](function(){}).then(function(){
      if(activeServiceOnEntry.active){
        abort();
      }
    });
  }
};

functiondispatchEvent(eventType){
  varevent=document.createEvent('CustomEvent');
  event.initCustomEvent(eventType,false,false,'custom');
  window.dispatchEvent(event);
}

functionabort(){
  if(activeService){
    activeService.destroy();
    dispatchEvent('afterprint');
  }
}

functionrenderProgress(index,total,l10n){
  varprogressContainer=document.getElementById('printServiceOverlay');
  varprogress=Math.round(100*index/total);
  varprogressBar=progressContainer.querySelector('progress');
  varprogressPerc=progressContainer.querySelector('.relative-progress');
  progressBar.value=progress;
  l10n.get('print_progress_percent',{
    progress:progress
  },progress+'%').then(function(msg){
    progressPerc.textContent=msg;
  });
}

varhasAttachEvent=!!document.attachEvent;
window.addEventListener('keydown',function(event){
  if(event.keyCode===80&&(event.ctrlKey||event.metaKey)&&!event.altKey&&(!event.shiftKey||window.chrome||window.opera)){
    window.print();

    if(hasAttachEvent){
      return;
    }

    event.preventDefault();

    if(event.stopImmediatePropagation){
      event.stopImmediatePropagation();
    }else{
      event.stopPropagation();
    }

    return;
  }
},true);

if(hasAttachEvent){
  document.attachEvent('onkeydown',function(event){
    event=event||window.event;

    if(event.keyCode===80&&event.ctrlKey){
      event.keyCode=0;
      returnfalse;
    }
  });
}

if('onbeforeprint'inwindow){
  varstopPropagationIfNeeded=functionstopPropagationIfNeeded(event){
    if(event.detail!=='custom'&&event.stopImmediatePropagation){
      event.stopImmediatePropagation();
    }
  };

  window.addEventListener('beforeprint',stopPropagationIfNeeded);
  window.addEventListener('afterprint',stopPropagationIfNeeded);
}

varoverlayPromise;

functionensureOverlay(){
  if(!overlayPromise){
    overlayManager=_app.PDFViewerApplication.overlayManager;

    if(!overlayManager){
      thrownewError('Theoverlaymanagerhasnotyetbeeninitialized.');
    }

    overlayPromise=overlayManager.register('printServiceOverlay',document.getElementById('printServiceOverlay'),abort,true);
    document.getElementById('printCancel').onclick=abort;
  }

  returnoverlayPromise;
}

_app.PDFPrintServiceFactory.instance={
  supportsPrinting:true,
  createPrintService:functioncreatePrintService(pdfDocument,pagesOverview,printContainer,l10n){
    if(activeService){
      thrownewError('Theprintserviceiscreatedandactive.');
    }

    activeService=newPDFPrintService(pdfDocument,pagesOverview,printContainer,l10n);
    returnactiveService;
  }
};

/***/})
/******/]);
//#sourceMappingURL=viewer.js.map