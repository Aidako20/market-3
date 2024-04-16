define('summernote/defaults',function(){
  /**
   *@classdefaults
   *
   *@singleton
   */
  vardefaults={
    /**@property*/
    version:'@VERSION',

    /**
     *
     *foreventoptions,referencetoEventHandler.attach
     *
     *@property{Object}options
     *@property{String/Number}[options.width=null]seteditorwidth
     *@property{String/Number}[options.height=null]seteditorheight,ex)300
     *@property{String/Number}options.minHeightsetminimumheightofeditor
     *@property{String/Number}options.maxHeight
     *@property{String/Number}options.focus
     *@property{Number}options.tabsize
     *@property{Boolean}options.styleWithSpan
     *@property{Object}options.codemirror
     *@property{Object}[options.codemirror.mode='text/html']
     *@property{Object}[options.codemirror.htmlMode=true]
     *@property{Object}[options.codemirror.lineNumbers=true]
     *@property{String}[options.lang=en-US]language'en-US','ko-KR',...
     *@property{String}[options.direction=null]textdirection,ex)'rtl'
     *@property{Array}[options.toolbar]
     *@property{Boolean}[options.airMode=false]
     *@property{Array}[options.airPopover]
     *@property{Fucntion}[options.onInit]initialize
     *@property{Fucntion}[options.onsubmit]
     */
    options:{
      width:null,                 //seteditorwidth
      height:null,                //seteditorheight,ex)300

      minHeight:null,             //setminimumheightofeditor
      maxHeight:null,             //setmaximumheightofeditor

      focus:false,                //setfocustoeditableareaafterinitializingsummernote

      tabsize:4,                  //sizeoftabex)2or4
      styleWithSpan:true,         //stylewithspan(ChromeandFFonly)

      disableLinkTarget:false,    //hidelinkTargetCheckbox
      disableDragAndDrop:false,   //disabledraganddropevent
      disableResizeEditor:false,  //disableresizingeditor
      disableResizeImage:false,   //disableresizingimage

      shortcuts:true,             //enablekeyboardshortcuts

      textareaAutoSync:true,      //enabletextareaautosync

      placeholder:false,          //enableplaceholdertext
      prettifyHtml:true,          //enableprettifyinghtmlwhiletogglingcodeview

      iconPrefix:'fafa-',        //prefixforcssiconclasses

      icons:{
        font:{
          bold:'bold',
          italic:'italic',
          underline:'underline',
          clear:'eraser',
          height:'text-height',
          strikethrough:'strikethrough',
          superscript:'superscript',
          subscript:'subscript'
        },
        image:{
          image:'picture-o',
          floatLeft:'align-left',
          floatRight:'align-right',
          floatNone:'align-justify',
          shapeRounded:'square',
          shapeCircle:'circle-o',
          shapeThumbnail:'picture-o',
          shapeNone:'times',
          remove:'trash-o'
        },
        link:{
          link:'link',
          unlink:'unlink',
          edit:'edit'
        },
        table:{
          table:'table'
        },
        hr:{
          insert:'minus'
        },
        style:{
          style:'magic'
        },
        lists:{
          unordered:'list-ul',
          ordered:'list-ol'
        },
        options:{
          help:'question',
          fullscreen:'arrows-alt',
          codeview:'code'
        },
        paragraph:{
          paragraph:'align-left',
          outdent:'outdent',
          indent:'indent',
          left:'align-left',
          center:'align-center',
          right:'align-right',
          justify:'align-justify'
        },
        color:{
          recent:'font'
        },
        history:{
          undo:'undo',
          redo:'repeat'
        },
        misc:{
          check:'check'
        }
      },

      dialogsInBody:false,         //falsewilladddialogsintoeditor

      codemirror:{                //codemirroroptions
        mode:'text/html',
        htmlMode:true,
        lineNumbers:true
      },

      //language
      lang:'en-US',               //language'en-US','ko-KR',...
      direction:null,             //textdirection,ex)'rtl'

      //toolbar
      toolbar:[
        ['style',['style']],
        ['font',['bold','italic','underline','clear']],
        //['font',['bold','italic','underline','strikethrough','superscript','subscript','clear']],
        ['fontname',['fontname']],
        ['fontsize',['fontsize']],
        ['color',['color']],
        ['para',['ul','ol','paragraph']],
        ['height',['height']],
        ['table',['table']],
        ['insert',['link','picture','hr']],
        ['view',['fullscreen','codeview']],
        ['help',['help']]
      ],

      plugin:{},

      //airmode:inlineeditor
      airMode:false,
      //airPopover:[
      //  ['style',['style']],
      //  ['font',['bold','italic','underline','clear']],
      //  ['fontname',['fontname']],
      //  ['color',['color']],
      //  ['para',['ul','ol','paragraph']],
      //  ['height',['height']],
      //  ['table',['table']],
      //  ['insert',['link','picture']],
      //  ['help',['help']]
      //],
      airPopover:[
        ['color',['color']],
        ['font',['bold','underline','clear']],
        ['para',['ul','paragraph']],
        ['table',['table']],
        ['insert',['link','picture']]
      ],

      //styletag
      styleTags:['p','blockquote','pre','h1','h2','h3','h4','h5','h6'],

      //defaultfontName
      defaultFontName:'HelveticaNeue',

      //fontName
      fontNames:[
        'Arial','ArialBlack','ComicSansMS','CourierNew',
        'HelveticaNeue','Helvetica','Impact','LucidaGrande',
        'Tahoma','TimesNewRoman','Verdana'
      ],
      fontNamesIgnoreCheck:[],

      fontSizes:['8','9','10','11','12','14','18','24','36'],

      //palletecolors(nxn)
      colors:[
        ['#000000','#424242','#636363','#9C9C94','#CEC6CE','#EFEFEF','#F7F7F7','#FFFFFF'],
        ['#FF0000','#FF9C00','#FFFF00','#00FF00','#00FFFF','#0000FF','#9C00FF','#FF00FF'],
        ['#F7C6CE','#FFE7CE','#FFEFC6','#D6EFD6','#CEDEE7','#CEE7F7','#D6D6E7','#E7D6DE'],
        ['#E79C9C','#FFC69C','#FFE79C','#B5D6A5','#A5C6CE','#9CC6EF','#B5A5D6','#D6A5BD'],
        ['#E76363','#F7AD6B','#FFD663','#94BD7B','#73A5AD','#6BADDE','#8C7BC6','#C67BA5'],
        ['#CE0000','#E79439','#EFC631','#6BA54A','#4A7B8C','#3984C6','#634AA5','#A54A7B'],
        ['#9C0000','#B56308','#BD9400','#397B21','#104A5A','#085294','#311873','#731842'],
        ['#630000','#7B3900','#846300','#295218','#083139','#003163','#21104A','#4A1031']
      ],

      //lineHeight
      lineHeights:['1.0','1.2','1.4','1.5','1.6','1.8','2.0','3.0'],

      //insertTablemaxsize
      insertTableMaxSize:{
        col:10,
        row:10
      },

      //image
      maximumImageFileSize:null,//sizeinbytes,null=nolimit

      //callbacks
      oninit:null,            //initialize
      onfocus:null,           //editablehasfocus
      onblur:null,            //editableoutoffocus
      onenter:null,           //enterkeypressed
      onkeyup:null,           //keyup
      onkeydown:null,         //keydown
      onImageUpload:null,     //imageUpload
      onImageUploadError:null,//imageUploadError
      onMediaDelete:null,     //mediadelete
      onToolbarClick:null,
      onsubmit:null,

      /**
       *manipulatelinkaddresswhenusercreatelink
       *@param{String}sLinkUrl
       *@return{String}
       */
      onCreateLink:function(sLinkUrl){
        if(sLinkUrl.indexOf('@')!==-1&&sLinkUrl.indexOf(':')===-1){
          sLinkUrl= 'mailto:'+sLinkUrl;
        }

        returnsLinkUrl;
      },

      keyMap:{
        pc:{
          'ENTER':'insertParagraph',
          'CTRL+Z':'undo',
          'CTRL+Y':'redo',
          'TAB':'tab',
          'SHIFT+TAB':'untab',
          'CTRL+B':'bold',
          'CTRL+I':'italic',
          'CTRL+U':'underline',
          'CTRL+SHIFT+S':'strikethrough',
          'CTRL+BACKSLASH':'removeFormat',
          'CTRL+SHIFT+L':'justifyLeft',
          'CTRL+SHIFT+E':'justifyCenter',
          'CTRL+SHIFT+R':'justifyRight',
          'CTRL+SHIFT+J':'justifyFull',
          'CTRL+SHIFT+NUM7':'insertUnorderedList',
          'CTRL+SHIFT+NUM8':'insertOrderedList',
          'CTRL+LEFTBRACKET':'outdent',
          'CTRL+RIGHTBRACKET':'indent',
          'CTRL+NUM0':'formatPara',
          'CTRL+NUM1':'formatH1',
          'CTRL+NUM2':'formatH2',
          'CTRL+NUM3':'formatH3',
          'CTRL+NUM4':'formatH4',
          'CTRL+NUM5':'formatH5',
          'CTRL+NUM6':'formatH6',
          'CTRL+ENTER':'insertHorizontalRule',
          'CTRL+K':'showLinkDialog'
        },

        mac:{
          'ENTER':'insertParagraph',
          'CMD+Z':'undo',
          'CMD+SHIFT+Z':'redo',
          'TAB':'tab',
          'SHIFT+TAB':'untab',
          'CMD+B':'bold',
          'CMD+I':'italic',
          'CMD+U':'underline',
          'CMD+SHIFT+S':'strikethrough',
          'CMD+BACKSLASH':'removeFormat',
          'CMD+SHIFT+L':'justifyLeft',
          'CMD+SHIFT+E':'justifyCenter',
          'CMD+SHIFT+R':'justifyRight',
          'CMD+SHIFT+J':'justifyFull',
          'CMD+SHIFT+NUM7':'insertUnorderedList',
          'CMD+SHIFT+NUM8':'insertOrderedList',
          'CMD+LEFTBRACKET':'outdent',
          'CMD+RIGHTBRACKET':'indent',
          'CMD+NUM0':'formatPara',
          'CMD+NUM1':'formatH1',
          'CMD+NUM2':'formatH2',
          'CMD+NUM3':'formatH3',
          'CMD+NUM4':'formatH4',
          'CMD+NUM5':'formatH5',
          'CMD+NUM6':'formatH6',
          'CMD+ENTER':'insertHorizontalRule',
          'CMD+K':'showLinkDialog'
        }
      }
    },

    //defaultlanguage:en-US
    lang:{
      'en-US':{
        font:{
          bold:'Bold',
          italic:'Italic',
          underline:'Underline',
          clear:'RemoveFontStyle',
          height:'LineHeight',
          name:'FontFamily',
          strikethrough:'Strikethrough',
          subscript:'Subscript',
          superscript:'Superscript',
          size:'FontSize'
        },
        image:{
          image:'Picture',
          insert:'InsertImage',
          resizeFull:'ResizeFull',
          resizeHalf:'ResizeHalf',
          resizeQuarter:'ResizeQuarter',
          floatLeft:'FloatLeft',
          floatRight:'FloatRight',
          floatNone:'FloatNone',
          shapeRounded:'Shape:Rounded',
          shapeCircle:'Shape:Circle',
          shapeThumbnail:'Shape:Thumbnail',
          shapeNone:'Shape:None',
          dragImageHere:'Dragimageortexthere',
          dropImage:'DropimageorText',
          selectFromFiles:'Selectfromfiles',
          maximumFileSize:'Maximumfilesize',
          maximumFileSizeError:'Maximumfilesizeexceeded.',
          url:'ImageURL',
          remove:'RemoveImage'
        },
        link:{
          link:'Link',
          insert:'InsertLink',
          unlink:'Unlink',
          edit:'Edit',
          textToDisplay:'Texttodisplay',
          url:'TowhatURLshouldthislinkgo?',
          openInNewWindow:'Openinnewwindow'
        },
        table:{
          table:'Table'
        },
        hr:{
          insert:'InsertHorizontalRule'
        },
        style:{
          style:'Style',
          normal:'Paragraph',
          blockquote:'Quote',
          pre:'Code',
          h1:'Header1',
          h2:'Header2',
          h3:'Header3',
          h4:'Header4',
          h5:'Header5',
          h6:'Header6'
        },
        lists:{
          unordered:'Unorderedlist',
          ordered:'Orderedlist'
        },
        options:{
          help:'Help',
          fullscreen:'FullScreen',
          codeview:'CodeView'
        },
        paragraph:{
          paragraph:'Paragraph',
          outdent:'Outdent',
          indent:'Indent',
          left:'Alignleft',
          center:'Aligncenter',
          right:'Alignright',
          justify:'Justifyfull'
        },
        color:{
          recent:'RecentColor',
          more:'MoreColor',
          background:'BackgroundColor',
          foreground:'ForegroundColor',
          transparent:'Transparent',
          setTransparent:'Settransparent',
          reset:'Reset',
          resetToDefault:'Resettodefault'
        },
        shortcut:{
          shortcuts:'Keyboardshortcuts',
          close:'Close',
          textFormatting:'Textformatting',
          action:'Action',
          paragraphFormatting:'Paragraphformatting',
          documentStyle:'DocumentStyle',
          extraKeys:'Extrakeys'
        },
        history:{
          undo:'Undo',
          redo:'Redo'
        }
      }
    }
  };

  returndefaults;
});
