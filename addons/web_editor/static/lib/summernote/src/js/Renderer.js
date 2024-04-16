define([
  'summernote/core/agent',
  'summernote/core/dom',
  'summernote/core/func',
  'summernote/core/list'
],function(agent,dom,func,list){
  /**
   *@classRenderer
   *
   *renderer
   *
   *renderingtoolbarandeditable
   */
  varRenderer=function(){

    /**
     *bootstrapbuttontemplate
     *@private
     *@param{String}labelbuttonname
     *@param{Object}[options]buttonoptions
     *@param{String}[options.event]data-event
     *@param{String}[options.className]button'sclassname
     *@param{String}[options.value]data-value
     *@param{String}[options.title]button'stitleforpopup
     *@param{String}[options.dropdown]dropdownhtml
     *@param{String}[options.hide]data-hide
     */
    vartplButton=function(label,options){
      varevent=options.event;
      varvalue=options.value;
      vartitle=options.title;
      varclassName=options.className;
      vardropdown=options.dropdown;
      varhide=options.hide;

      return(dropdown?'<divclass="btn-group'+
               (className?''+className:'')+'">':'')+
               '<buttontype="button"'+
                 'class="btnbtn-secondarybtn-sm'+
                   ((!dropdown&&className)?''+className:'')+
                   (dropdown?'dropdown-toggle':'')+
                 '"'+
                 (dropdown?'data-toggle="dropdown"':'')+
                 (title?'title="'+title+'"':'')+
                 (event?'data-event="'+event+'"':'')+
                 (value?'data-value=\''+value+'\'':'')+
                 (hide?'data-hide=\''+hide+'\'':'')+
                 'tabindex="-1">'+
                 label+
                 (dropdown?'<spanclass="caret"></span>':'')+
               '</button>'+
               (dropdown||'')+
             (dropdown?'</div>':'');
    };

    /**
     *bootstrapiconbuttontemplate
     *@private
     *@param{String}iconClassName
     *@param{Object}[options]
     *@param{String}[options.event]
     *@param{String}[options.value]
     *@param{String}[options.title]
     *@param{String}[options.dropdown]
     */
    vartplIconButton=function(iconClassName,options){
      varlabel='<iclass="'+iconClassName+'"></i>';
      returntplButton(label,options);
    };

    /**
     *bootstrappopovertemplate
     *@private
     *@param{String}className
     *@param{String}content
     */
    vartplPopover=function(className,content){
      var$popover=$('<divclass="'+className+'popoverbottomin"style="display:none;">'+
               '<divclass="arrow"></div>'+
               '<divclass="popover-body">'+
               '</div>'+
             '</div>');

      $popover.find('.popover-body').append(content);
      return$popover;
    };

    /**
     *bootstrapdialogtemplate
     *
     *@param{String}className
     *@param{String}[title='']
     *@param{String}body
     *@param{String}[footer='']
     */
    vartplDialog=function(className,title,body,footer){
      return'<divclass="'+className+'modal"role="dialog"aria-hidden="false">'+
               '<divclass="modal-dialog">'+
                 '<divclass="modal-content">'+
                   (title?
                   '<headerclass="modal-header">'+
                     '<h4class="modal-title">'+title+'</h4>'+
                     '<buttontype="button"class="close"aria-hidden="true"tabindex="-1">&times;</button>'+
                   '</header>':''
                   )+
                   '<mainclass="modal-body">'+body+'</main>'+
                   (footer?
                   '<headerclass="modal-footer">'+footer+'</header>':''
                   )+
                 '</div>'+
               '</div>'+
             '</div>';
    };

    /**
     *bootstrapdropdowntemplate
     *
     *@param{String|String[]}contents
     *@param{String}[className='']
     *@param{String}[nodeName='']
     */
    vartplDropdown=function(contents,className,nodeName){
      varclasses='dropdown-menu'+(className?''+className:'');
      nodeName=nodeName||'ul';
      if(contentsinstanceofArray){
        contents=contents.join('');
      }

      return'<'+nodeName+'class="'+classes+'">'+contents+'</'+nodeName+'>';
    };

    vartplButtonInfo={
      picture:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.image.image,{
          event:'showImageDialog',
          title:lang.image.image,
          hide:true
        });
      },
      link:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.link.link,{
          event:'showLinkDialog',
          title:lang.link.link,
          hide:true
        });
      },
      table:function(lang,options){
        vardropdown=[
          '<divclass="note-dimension-picker">',
          '<divclass="note-dimension-picker-mousecatcher"data-event="insertTable"data-value="1x1"></div>',
          '<divclass="note-dimension-picker-highlighted"></div>',
          '<divclass="note-dimension-picker-unhighlighted"></div>',
          '</div>',
          '<divclass="note-dimension-display">1x1</div>'
        ];

        returntplIconButton(options.iconPrefix+options.icons.table.table,{
          title:lang.table.table,
          dropdown:tplDropdown(dropdown,'note-table')
        });
      },
      style:function(lang,options){
        varitems=options.styleTags.reduce(function(memo,v){
          varlabel=lang.style[v==='p'?'normal':v];
          returnmemo+'<li><aclass="dropdown-item"data-event="formatBlock"href="#"data-value="'+v+'">'+
                   (
                     (v==='p'||v==='pre')?label:
                     '<'+v+'>'+label+'</'+v+'>'
                   )+
                 '</a></li>';
        },'');

        returntplIconButton(options.iconPrefix+options.icons.style.style,{
          title:lang.style.style,
          dropdown:tplDropdown(items)
        });
      },
      fontname:function(lang,options){
        varrealFontList=[];
        varitems=options.fontNames.reduce(function(memo,v){
          if(!agent.isFontInstalled(v)&&!list.contains(options.fontNamesIgnoreCheck,v)){
            returnmemo;
          }
          realFontList.push(v);
          returnmemo+'<li><adata-event="fontName"href="#"data-value="'+v+'"style="font-family:\''+v+'\'">'+
                          '<iclass="'+options.iconPrefix+options.icons.misc.check+'"></i>'+v+
                        '</a></li>';
        },'');

        varhasDefaultFont=agent.isFontInstalled(options.defaultFontName);
        vardefaultFontName=(hasDefaultFont)?options.defaultFontName:realFontList[0];

        varlabel='<spanclass="note-current-fontname">'+
                        defaultFontName+
                     '</span>';
        returntplButton(label,{
          title:lang.font.name,
          className:'note-fontname',
          dropdown:tplDropdown(items,'note-check')
        });
      },
      fontsize:function(lang,options){
        varitems=options.fontSizes.reduce(function(memo,v){
          returnmemo+'<li><adata-event="fontSize"href="#"data-value="'+v+'">'+
                          '<iclass="'+options.iconPrefix+options.icons.misc.check+'"></i>'+v+
                        '</a></li>';
        },'');

        varlabel='<spanclass="note-current-fontsize">11</span>';
        returntplButton(label,{
          title:lang.font.size,
          className:'note-fontsize',
          dropdown:tplDropdown(items,'note-check')
        });
      },
      color:function(lang,options){
        varcolorButtonLabel='<iclass="'+
                                  options.iconPrefix+options.icons.color.recent+
                                '"id="colors_preview"style="color:white;background-color:#B35E9B"></i>';
        varcolorButton=tplButton(colorButtonLabel,{
          className:'note-recent-color',
          title:lang.color.recent,
          event:'color',
          value:'{"backColor":"#B35E9B"}'
        });

        varitems=[
          '<liclass="flex"><divclass="btn-groupflex-column">',
          '<divclass="note-palette-title">'+lang.color.background+'</div>',
          '<divclass="note-color-reset"data-event="backColor"',
          'data-value="inherit"title="'+lang.color.transparent+'">'+lang.color.setTransparent+'</div>',
          '<divclass="note-color-palette"data-target-event="backColor"></div>',
          '</div><divclass="btn-groupflex-column">',
          '<divclass="note-palette-title">'+lang.color.foreground+'</div>',
          '<divclass="note-color-reset"data-event="foreColor"data-value="inherit"title="'+lang.color.reset+'">',
          lang.color.resetToDefault,
          '</div>',
          '<divclass="note-color-palette"data-target-event="foreColor"></div>',
          '</div></li>'
        ];

        varmoreButton=tplButton('',{
          title:lang.color.more,
          dropdown:tplDropdown(items)
        });

        returncolorButton+moreButton;
      },
      bold:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.bold,{
          event:'bold',
          title:lang.font.bold
        });
      },
      italic:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.italic,{
          event:'italic',
          title:lang.font.italic
        });
      },
      underline:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.underline,{
          event:'underline',
          title:lang.font.underline
        });
      },
      strikethrough:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.strikethrough,{
          event:'strikethrough',
          title:lang.font.strikethrough
        });
      },
      superscript:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.superscript,{
          event:'superscript',
          title:lang.font.superscript
        });
      },
      subscript:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.subscript,{
          event:'subscript',
          title:lang.font.subscript
        });
      },
      clear:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.font.clear,{
          event:'removeFormat',
          title:lang.font.clear
        });
      },
      ul:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.lists.unordered,{
          event:'insertUnorderedList',
          title:lang.lists.unordered
        });
      },
      ol:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.lists.ordered,{
          event:'insertOrderedList',
          title:lang.lists.ordered
        });
      },
      paragraph:function(lang,options){
        varleftButton=tplIconButton(options.iconPrefix+options.icons.paragraph.left,{
          title:lang.paragraph.left,
          event:'justifyLeft'
        });
        varcenterButton=tplIconButton(options.iconPrefix+options.icons.paragraph.center,{
          title:lang.paragraph.center,
          event:'justifyCenter'
        });
        varrightButton=tplIconButton(options.iconPrefix+options.icons.paragraph.right,{
          title:lang.paragraph.right,
          event:'justifyRight'
        });
        varjustifyButton=tplIconButton(options.iconPrefix+options.icons.paragraph.justify,{
          title:lang.paragraph.justify,
          event:'justifyFull'
        });

        varoutdentButton=tplIconButton(options.iconPrefix+options.icons.paragraph.outdent,{
          title:lang.paragraph.outdent,
          event:'outdent'
        });
        varindentButton=tplIconButton(options.iconPrefix+options.icons.paragraph.indent,{
          title:lang.paragraph.indent,
          event:'indent'
        });

        vardropdown=[
          '<divclass="note-alignbtn-group">',
          leftButton+centerButton+rightButton+justifyButton,
          '</div><divclass="note-listbtn-group">',
          indentButton+outdentButton,
          '</div>'
        ];

        returntplIconButton(options.iconPrefix+options.icons.paragraph.paragraph,{
          title:lang.paragraph.paragraph,
          dropdown:tplDropdown(dropdown,'','div')
        });
      },
      height:function(lang,options){
        varitems=options.lineHeights.reduce(function(memo,v){
          returnmemo+'<li><adata-event="lineHeight"href="#"data-value="'+parseFloat(v)+'">'+
                          '<iclass="'+options.iconPrefix+options.icons.misc.check+'"></i>'+v+
                        '</a></li>';
        },'');

        returntplIconButton(options.iconPrefix+options.icons.font.height,{
          title:lang.font.height,
          dropdown:tplDropdown(items,'note-check')
        });

      },
      help:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.options.help,{
          event:'showHelpDialog',
          title:lang.options.help,
          hide:true
        });
      },
      fullscreen:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.options.fullscreen,{
          event:'fullscreen',
          title:lang.options.fullscreen
        });
      },
      codeview:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.options.codeview,{
          event:'codeview',
          title:lang.options.codeview
        });
      },
      undo:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.history.undo,{
          event:'undo',
          title:lang.history.undo
        });
      },
      redo:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.history.redo,{
          event:'redo',
          title:lang.history.redo
        });
      },
      hr:function(lang,options){
        returntplIconButton(options.iconPrefix+options.icons.hr.insert,{
          event:'insertHorizontalRule',
          title:lang.hr.insert
        });
      }
    };

    vartplPopovers=function(lang,options){
      vartplLinkPopover=function(){
        varlinkButton=tplIconButton(options.iconPrefix+options.icons.link.edit,{
          title:lang.link.edit,
          event:'showLinkDialog',
          hide:true
        });
        varunlinkButton=tplIconButton(options.iconPrefix+options.icons.link.unlink,{
          title:lang.link.unlink,
          event:'unlink'
        });
        varcontent='<ahref="http://www.google.com"target="_blank">www.google.com</a>&nbsp;&nbsp;'+
                      '<divclass="note-insertbtn-group">'+
                        linkButton+unlinkButton+
                      '</div>';
        returntplPopover('note-link-popover',content);
      };

      vartplImagePopover=function(){
        varautoButton=tplButton('<spanclass="note-fontsize-10">Auto</span>',{
          event:'resize',
          value:'auto'
        });
        varfullButton=tplButton('<spanclass="note-fontsize-10">100%</span>',{
          title:lang.image.resizeFull,
          event:'resize',
          value:'1'
        });
        varhalfButton=tplButton('<spanclass="note-fontsize-10">50%</span>',{
          title:lang.image.resizeHalf,
          event:'resize',
          value:'0.5'
        });
        varquarterButton=tplButton('<spanclass="note-fontsize-10">25%</span>',{
          title:lang.image.resizeQuarter,
          event:'resize',
          value:'0.25'
        });

        varleftButton=tplIconButton(options.iconPrefix+options.icons.image.floatLeft,{
          title:lang.image.floatLeft,
          event:'floatMe',
          value:'left'
        });
        varrightButton=tplIconButton(options.iconPrefix+options.icons.image.floatRight,{
          title:lang.image.floatRight,
          event:'floatMe',
          value:'right'
        });
        varjustifyButton=tplIconButton(options.iconPrefix+options.icons.image.floatNone,{
          title:lang.image.floatNone,
          event:'floatMe',
          value:'none'
        });

        varroundedButton=tplIconButton(options.iconPrefix+options.icons.image.shapeRounded,{
          title:lang.image.shapeRounded,
          event:'imageShape',
          value:'rounded'
        });
        varcircleButton=tplIconButton(options.iconPrefix+options.icons.image.shapeCircle,{
          title:lang.image.shapeCircle,
          event:'imageShape',
          value:'rounded-circle'
        });
        varthumbnailButton=tplIconButton(options.iconPrefix+options.icons.image.shapeThumbnail,{
          title:lang.image.shapeThumbnail,
          event:'imageShape',
          value:'img-thumbnail'
        });
        varnoneButton=tplIconButton(options.iconPrefix+options.icons.image.shapeNone,{
          title:lang.image.shapeNone,
          event:'imageShape',
          value:''
        });

        varremoveButton=tplIconButton(options.iconPrefix+options.icons.image.remove,{
          title:lang.image.remove,
          event:'removeMedia',
          value:'none'
        });

        varcontent=(options.disableResizeImage?'':'<divclass="btn-group">'+autoButton+fullButton+halfButton+quarterButton+'</div>')+
                      '<divclass="btn-group">'+leftButton+rightButton+justifyButton+'</div>'+
                      '<divclass="btn-group">'+roundedButton+circleButton+thumbnailButton+noneButton+'</div>'+
                      '<divclass="btn-group">'+removeButton+'</div>';
        returntplPopover('note-image-popover',content);
      };

      vartplAirPopover=function(){
        var$content=$('<div/>');
        for(varidx=0,len=options.airPopover.length;idx<len;idx++){
          vargroup=options.airPopover[idx];

          var$group=$('<divclass="note-'+group[0]+'btn-group">');
          for(vari=0,lenGroup=group[1].length;i<lenGroup;i++){
            var$button=$(tplButtonInfo[group[1][i]](lang,options));

            $button.attr('data-name',group[1][i]);

            $group.append($button);
          }
          $content.append($group);
        }

        returntplPopover('note-air-popover',$content.children());
      };

      var$notePopover=$('<divclass="note-popover"/>');

      $notePopover.append(tplLinkPopover());
      $notePopover.append(tplImagePopover());

      if(options.airMode){
        $notePopover.append(tplAirPopover());
      }

      return$notePopover;
    };

    this.tplButtonInfo=tplButtonInfo;//FLECTRA:allowaccessforoverride
    this.tplPopovers=tplPopovers;//FLECTRA:allowaccessforoverride

    vartplHandles=function(options){
      return'<divclass="note-handle">'+
               '<divclass="note-control-selection">'+
                 '<divclass="note-control-selection-bg"></div>'+
                 '<divclass="note-control-holdernote-control-nw"></div>'+
                 '<divclass="note-control-holdernote-control-ne"></div>'+
                 '<divclass="note-control-holdernote-control-sw"></div>'+
                 '<divclass="'+
                 (options.disableResizeImage?'note-control-holder':'note-control-sizing')+
                 'note-control-se"></div>'+
                 (options.disableResizeImage?'':'<divclass="note-control-selection-info"></div>')+
               '</div>'+
             '</div>';
    };

    /**
     *shortcuttabletemplate
     *@param{String}title
     *@param{String}body
     */
    vartplShortcut=function(title,keys){
      varkeyClass='note-shortcut-colcol-6note-shortcut-';
      varbody=[];

      for(variinkeys){
        if(keys.hasOwnProperty(i)){
          body.push(
            '<divclass="'+keyClass+'key">'+keys[i].kbd+'</div>'+
            '<divclass="'+keyClass+'name">'+keys[i].text+'</div>'
            );
        }
      }

      return'<divclass="note-shortcut-rowrow"><divclass="'+keyClass+'titleoffset-6">'+title+'</div></div>'+
             '<divclass="note-shortcut-rowrow">'+body.join('</div><divclass="note-shortcut-rowrow">')+'</div>';
    };

    vartplShortcutText=function(lang){
      varkeys=[
        {kbd:'⌘+B',text:lang.font.bold},
        {kbd:'⌘+I',text:lang.font.italic},
        {kbd:'⌘+U',text:lang.font.underline},
        {kbd:'⌘+\\',text:lang.font.clear}
      ];

      returntplShortcut(lang.shortcut.textFormatting,keys);
    };

    vartplShortcutAction=function(lang){
      varkeys=[
        {kbd:'⌘+Z',text:lang.history.undo},
        {kbd:'⌘+⇧+Z',text:lang.history.redo},
        {kbd:'⌘+]',text:lang.paragraph.indent},
        {kbd:'⌘+[',text:lang.paragraph.outdent},
        {kbd:'⌘+ENTER',text:lang.hr.insert}
      ];

      returntplShortcut(lang.shortcut.action,keys);
    };

    vartplShortcutPara=function(lang){
      varkeys=[
        {kbd:'⌘+⇧+L',text:lang.paragraph.left},
        {kbd:'⌘+⇧+E',text:lang.paragraph.center},
        {kbd:'⌘+⇧+R',text:lang.paragraph.right},
        {kbd:'⌘+⇧+J',text:lang.paragraph.justify},
        {kbd:'⌘+⇧+NUM7',text:lang.lists.ordered},
        {kbd:'⌘+⇧+NUM8',text:lang.lists.unordered}
      ];

      returntplShortcut(lang.shortcut.paragraphFormatting,keys);
    };

    vartplShortcutStyle=function(lang){
      varkeys=[
        {kbd:'⌘+NUM0',text:lang.style.normal},
        {kbd:'⌘+NUM1',text:lang.style.h1},
        {kbd:'⌘+NUM2',text:lang.style.h2},
        {kbd:'⌘+NUM3',text:lang.style.h3},
        {kbd:'⌘+NUM4',text:lang.style.h4},
        {kbd:'⌘+NUM5',text:lang.style.h5},
        {kbd:'⌘+NUM6',text:lang.style.h6}
      ];

      returntplShortcut(lang.shortcut.documentStyle,keys);
    };

    vartplExtraShortcuts=function(lang,options){
      varextraKeys=options.extraKeys;
      varkeys=[];

      for(varkeyinextraKeys){
        if(extraKeys.hasOwnProperty(key)){
          keys.push({kbd:key,text:extraKeys[key]});
        }
      }

      returntplShortcut(lang.shortcut.extraKeys,keys);
    };

    vartplShortcutTable=function(lang,options){
      varcolClass='class="note-shortcutnote-shortcut-colcol-md-6col-12"';
      vartemplate=[
        '<div'+colClass+'>'+tplShortcutAction(lang,options)+'</div>'+
        '<div'+colClass+'>'+tplShortcutText(lang,options)+'</div>',
        '<div'+colClass+'>'+tplShortcutStyle(lang,options)+'</div>'+
        '<div'+colClass+'>'+tplShortcutPara(lang,options)+'</div>'
      ];

      if(options.extraKeys){
        template.push('<div'+colClass+'>'+tplExtraShortcuts(lang,options)+'</div>');
      }

      return'<divclass="note-shortcut-rowrow">'+
               template.join('</div><divclass="note-shortcut-rowrow">')+
             '</div>';
    };

    varreplaceMacKeys=function(sHtml){
      returnsHtml.replace(/⌘/g,'Ctrl').replace(/⇧/g,'Shift');
    };

    vartplDialogInfo={
      image:function(lang,options){
        varimageLimitation='';
        if(options.maximumImageFileSize){
          varunit=Math.floor(Math.log(options.maximumImageFileSize)/Math.log(1024));
          varreadableSize=(options.maximumImageFileSize/Math.pow(1024,unit)).toFixed(2)*1+
                             ''+'KMGTP'[unit]+'B';
          imageLimitation='<small>'+lang.image.maximumFileSize+':'+readableSize+'</small>';
        }

        varbody='<divclass="form-grouprownote-group-select-from-files">'+
                     '<label>'+lang.image.selectFromFiles+'</label>'+
                     '<inputclass="note-image-inputform-control"type="file"name="files"accept="image/*"multiple="multiple"/>'+
                     imageLimitation+
                   '</div>'+
                   '<divclass="form-grouprow">'+
                     '<label>'+lang.image.url+'</label>'+
                     '<inputclass="note-image-urlform-controlcol-md-12"type="text"/>'+
                   '</div>';
        varfooter='<buttonhref="#"class="btnbtn-primarynote-image-btndisabled"disabled>'+lang.image.insert+'</button>';
        returntplDialog('note-image-dialog',lang.image.insert,body,footer);
      },

      link:function(lang,options){
        varbody='<divclass="form-grouprow">'+
                     '<label>'+lang.link.textToDisplay+'</label>'+
                     '<inputclass="note-link-textform-controlcol-md-12"type="text"/>'+
                   '</div>'+
                   '<divclass="form-grouprow">'+
                     '<label>'+lang.link.url+'</label>'+
                     '<inputclass="note-link-urlform-controlcol-md-12"type="text"value="http://"/>'+
                   '</div>'+
                   (!options.disableLinkTarget?
                     '<divclass="checkbox">'+
                       '<label>'+'<inputtype="checkbox"checked>'+
                         lang.link.openInNewWindow+
                       '</label>'+
                     '</div>':''
                   );
        varfooter='<buttonhref="#"class="btnbtn-primarynote-link-btndisabled"disabled>'+lang.link.insert+'</button>';
        returntplDialog('note-link-dialog',lang.link.insert,body,footer);
      },

      help:function(lang,options){
        varbody='<aclass="modal-closefloat-right"aria-hidden="true"tabindex="-1">'+lang.shortcut.close+'</a>'+
                   '<divclass="title">'+lang.shortcut.shortcuts+'</div>'+
                   (agent.isMac?tplShortcutTable(lang,options):replaceMacKeys(tplShortcutTable(lang,options)))+
                   '<pclass="text-center">'+
                     '<ahref="//summernote.org/"target="_blank">Summernote@VERSION</a>·'+
                     '<ahref="//github.com/summernote/summernote"target="_blank">Project</a>·'+
                     '<ahref="//github.com/summernote/summernote/issues"target="_blank">Issues</a>'+
                   '</p>';
        returntplDialog('note-help-dialog','',body,'');
      }
    };

    vartplDialogs=function(lang,options){
      vardialogs='';

      $.each(tplDialogInfo,function(idx,tplDialog){
        dialogs+=tplDialog(lang,options);
      });

      return'<divclass="note-dialog">'+dialogs+'</div>';
    };

    vartplStatusbar=function(){
      return'<divclass="note-resizebar">'+
               '<divclass="note-icon-bar"></div>'+
               '<divclass="note-icon-bar"></div>'+
               '<divclass="note-icon-bar"></div>'+
             '</div>';
    };

    varrepresentShortcut=function(str){
      if(agent.isMac){
        str=str.replace('CMD','⌘').replace('SHIFT','⇧');
      }

      returnstr.replace('BACKSLASH','\\')
                .replace('SLASH','/')
                .replace('LEFTBRACKET','[')
                .replace('RIGHTBRACKET',']');
    };

    /**
     *createTooltip
     *
     *@param{jQuery}$container
     *@param{Object}keyMap
     *@param{String}[sPlacement]
     */
    varcreateTooltip=function($container,keyMap,sPlacement){
      varinvertedKeyMap=func.invertObject(keyMap);
      var$buttons=$container.find('button');

      $buttons.each(function(i,elBtn){
        var$btn=$(elBtn);
        varsShortcut=invertedKeyMap[$btn.data('event')];
        if(sShortcut){
          $btn.attr('title',function(i,v){
            returnv+'('+representShortcut(sShortcut)+')';
          });
        }
      //bootstraptooltiponbtn-groupbug
      //https://github.com/twbs/bootstrap/issues/5687
      }).tooltip({
        container:'body',
        trigger:'hover',
        placement:sPlacement||'top'
      }).on('click',function(){
        $(this).tooltip('hide');
      });
    };

    //createPalette
    varcreatePalette=function($container,options){
      varcolorInfo=options.colors;
      $container.find('.note-color-palette').each(function(){
        var$palette=$(this),eventName=$palette.attr('data-target-event');
        varpaletteContents=[];
        for(varrow=0,lenRow=colorInfo.length;row<lenRow;row++){
          varcolors=colorInfo[row];
          varbuttons=[];
          for(varcol=0,lenCol=colors.length;col<lenCol;col++){
            varcolor=colors[col];
            buttons.push(['<buttontype="button"class="note-color-btn"style="background-color:',color,
                           ';"data-event="',eventName,
                           '"data-value="',color,
                           '"title="',color,
                           '"data-toggle="button"tabindex="-1"></button>'].join(''));
          }
          paletteContents.push('<divclass="note-color-row">'+buttons.join('')+'</div>');
        }
        $palette.html(paletteContents.join(''));
      });
    };

    this.createPalette=createPalette;//FLECTRA:allowaccessforoverride

    /**
     *createsummernotelayout(airmode)
     *
     *@param{jQuery}$holder
     *@param{Object}options
     */
    this.createLayoutByAirMode=function($holder,options){
      varlangInfo=options.langInfo;
      varkeyMap=options.keyMap[agent.isMac?'mac':'pc'];
      varid=func.uniqueId();

      $holder.addClass('note-air-editornote-editable');//FLECTRA:removingpanel-bodyclasstoremoveunwantedstyle
      $holder.attr({
        'data-note-id':id,//FLECTRA:weuse[data-note-id="{id}"]insteadof[id="{id}"]
        //'id':'note-editor-'+id,
        'contentEditable':true
      });

      varbody=document.body;
      var$container=$('#web_editor-toolbars')

      //createPopover
      var$popover=$(this.tplPopovers(langInfo,options));//FLECTRA:user(maybe)overridedmethod
      $popover.addClass('note-air-layout');
      $popover.attr('id','note-popover-'+id);
      $popover.appendTo($container);
      createTooltip($popover,keyMap);
      this.createPalette($popover,options);//FLECTRA:use(maybe)overridedmethod

      //createHandle
      var$handle=$(tplHandles(options));
      $handle.addClass('note-air-layout');
      $handle.attr('id','note-handle-'+id);
      $handle.appendTo($container);

      //createDialog
      var$dialog=$(tplDialogs(langInfo,options));
      $dialog.addClass('note-air-layout');
      $dialog.attr('id','note-dialog-'+id);
      $dialog.find('button.close,a.modal-close').click(function(){
        $(this).closest('.modal').modal('hide');
      });
      $dialog.appendTo($container);
    };

    /**
     *createsummernotelayout(normalmode)
     *
     *@param{jQuery}$holder
     *@param{Object}options
     */
    this.createLayoutByFrame=function($holder,options){
      varlangInfo=options.langInfo;

      //01.createEditor
      var$editor=$('<divclass="note-editorpanelpanel-default"/>');
      if(options.width){
        $editor.width(options.width);
      }

      //02.statusbar(resizebar)
      if(options.height>0){
        $('<divclass="note-statusbar">'+(options.disableResizeEditor?'':tplStatusbar())+'</div>').prependTo($editor);
      }

      //03editingarea
      var$editingArea=$('<divclass="note-editing-area"/>');
      //03.createeditable
      varisContentEditable=!$holder.is(':disabled');
      var$editable=$('<divclass="note-editablepanel-body"contentEditable="'+isContentEditable+'"></div>').prependTo($editingArea);

      if(options.height){
        $editable.height(options.height);
      }
      if(options.direction){
        $editable.attr('dir',options.direction);
      }
      varplaceholder=$holder.attr('placeholder')||options.placeholder;
      if(placeholder){
        $editable.attr('data-placeholder',placeholder);
      }

      $editable.html(dom.html($holder)||dom.emptyPara);

      //031.createcodable
      $('<textareaclass="note-codable"></textarea>').prependTo($editingArea);

      //04.createPopover
      var$popover=$(this.tplPopovers(langInfo,options)).prependTo($editingArea);//FLECTRA:use(maybe)overridedmethod
      this.createPalette($popover,options);//FLECTRA:use(maybe)overridedmethod
      createTooltip($popover,keyMap);

      //05.handle(controlselection,...)
      $(tplHandles(options)).prependTo($editingArea);

      $editingArea.prependTo($editor);

      //06.createToolbar
      var$toolbar=$('<divclass="note-toolbarpanel-heading"/>');
      for(varidx=0,len=options.toolbar.length;idx<len;idx++){
        vargroupName=options.toolbar[idx][0];
        vargroupButtons=options.toolbar[idx][1];

        var$group=$('<divclass="note-'+groupName+'btn-group"/>');
        for(vari=0,btnLength=groupButtons.length;i<btnLength;i++){
          varbuttonInfo=tplButtonInfo[groupButtons[i]];
          //continuecreatingtoolbarevenifabuttondoesn'texist
          if(!$.isFunction(buttonInfo)){continue;}

          var$button=$(buttonInfo(langInfo,options));
          $button.attr('data-name',groupButtons[i]); //setbutton'salias,becuasetogetbuttonelementfrom$toolbar
          $group.append($button);
        }
        $toolbar.append($group);
      }

      varkeyMap=options.keyMap[agent.isMac?'mac':'pc'];
      this.createPalette($toolbar,options);//FLECTRA:use(maybe)overridedmethod
      createTooltip($toolbar,keyMap,'bottom');
      $toolbar.prependTo($editor);

      //07.createDropzone
      $('<divclass="note-dropzone"><divclass="note-dropzone-message"></div></div>').prependTo($editor);

      //08.createDialog
      var$dialogContainer=options.dialogsInBody?$(document.body):$editor;
      var$dialog=$(tplDialogs(langInfo,options)).prependTo($dialogContainer);
      $dialog.find('button.close,a.modal-close').click(function(){
        $(this).closest('.modal').modal('hide');
      });

      //09.Editor/Holderswitch
      $editor.insertAfter($holder);
      $holder.hide();
    };

    this.hasNoteEditor=function($holder){
      returnthis.noteEditorFromHolder($holder).length>0;
    };

    this.noteEditorFromHolder=function($holder){
      if($holder.hasClass('note-air-editor')){
        return$holder;
      }elseif($holder.next().hasClass('note-editor')){
        return$holder.next();
      }else{
        return$();
      }
    };

    /**
     *createsummernotelayout
     *
     *@param{jQuery}$holder
     *@param{Object}options
     */
    this.createLayout=function($holder,options){
      if(options.airMode){
        this.createLayoutByAirMode($holder,options);
      }else{
        this.createLayoutByFrame($holder,options);
      }
    };

    /**
     *returnslayoutInfofromholder
     *
     *@param{jQuery}$holder-placeholder
     *@return{Object}
     */
    this.layoutInfoFromHolder=function($holder){
      var$editor=this.noteEditorFromHolder($holder);
      if(!$editor.length){
        return;
      }

      //connect$holderto$editor
      $editor.data('holder',$holder);

      returndom.buildLayoutInfo($editor);
    };

    /**
     *removeLayout
     *
     *@param{jQuery}$holder-placeholder
     *@param{Object}layoutInfo
     *@param{Object}options
     *
     */
    this.removeLayout=function($holder,layoutInfo,options){
      if(options.airMode){
        $holder.removeClass('note-air-editornote-editable')
               .removeAttr('contentEditable');//FLECTRA:removedid'idcontentEditable'

        layoutInfo.popover().remove();
        layoutInfo.handle().remove();
        layoutInfo.dialog().remove();
      }else{
        $holder.html(layoutInfo.editable().html());

        if(options.dialogsInBody){
          layoutInfo.dialog().remove();
        }
        layoutInfo.editor().remove();
        $holder.show();
      }
    };

    /**
     *
     *@return{Object}
     *@return{function(label,options=):string}return.button{@link#tplButtonfunctiontomaketextbutton}
     *@return{function(iconClass,options=):string}return.iconButton{@link#tplIconButtonfunctiontomakeiconbutton}
     *@return{function(className,title=,body=,footer=):string}return.dialog{@link#tplDialogfunctiontomakedialog}
     */
    this.getTemplate=function(){
      return{
        button:tplButton,
        iconButton:tplIconButton,
        dialog:tplDialog,
        dropdown:tplDropdown//FLECTRA:suggestupstream
      };
    };

    /**
     *addbuttoninformation
     *
     *@param{String}namebuttonname
     *@param{Function}buttonInfofunctiontomakebutton,referenceto{@link#tplButton},{@link#tplIconButton}
     */
    this.addButtonInfo=function(name,buttonInfo){
      tplButtonInfo[name]=buttonInfo;
    };

    /**
     *
     *@param{String}name
     *@param{Function}dialogInfofunctiontomakedialog,referenceto{@link#tplDialog}
     */
    this.addDialogInfo=function(name,dialogInfo){
      tplDialogInfo[name]=dialogInfo;
    };
  };

  returnRenderer;
});
