#-*-coding:utf-8-*-

from__future__importprint_function
importbase64
importcopy
importio
importmath
importre
importtraceback
importcodecs
fromhashlibimportmd5

fromPILimportImage
fromxml.etreeimportElementTreeasET


try:
    importjcconv
exceptImportError:
    jcconv=None

try:
    importqrcode
exceptImportError:
    qrcode=None

from.constantsimport*
from.exceptionsimport*

defutfstr(stuff):
    """convertsstufftostringanddoeswithoutfailingifstuffisautf8string"""
    ifisinstance(stuff,str):
        returnstuff
    else:
        returnstr(stuff)

classStyleStack:
    """
    Thestylestackisusedbythexmlreceiptserializertocomputetheactivestylesalongthexml
    document.Stylesarejustxmlattributes,thereisnocssmechanism.Butthestyleappliedby
    theattributesareinheritedbydeepernodes.
    """
    def__init__(self):
        self.stack=[]
        self.defaults={  #defaultstylevalues
            'align':    'left',
            'underline':'off',
            'bold':     'off',
            'size':     'normal',
            'font' :   'a',
            'width':    48,
            'indent':   0,
            'tabwidth': 2,
            'bullet':   '-',
            'line-ratio':0.5,
            'color':   'black',

            'value-decimals':          2,
            'value-symbol':            '',
            'value-symbol-position':   'after',
            'value-autoint':           'off',
            'value-decimals-separator': '.',
            'value-thousands-separator':',',
            'value-width':              0,
            
        }

        self.types={#attributetypes,defaultisstringandcanbeommitted
            'width':   'int',
            'indent':  'int',
            'tabwidth':'int',
            'line-ratio':      'float',
            'value-decimals':  'int',
            'value-width':     'int',
        }

        self.cmds={
            #translationfromstylestoescposcommands
            #somestyledonotcorrespondtoescposcommandareusedby
            #theserializerinstead
            'align':{
                'left':    TXT_ALIGN_LT,
                'right':   TXT_ALIGN_RT,
                'center':  TXT_ALIGN_CT,
                '_order':  1,
            },
            'underline':{
                'off':     TXT_UNDERL_OFF,
                'on':      TXT_UNDERL_ON,
                'double':  TXT_UNDERL2_ON,
                #mustbeissuedafter'size'command
                #becauseESC!resetsESC-
                '_order':  10,
            },
            'bold':{
                'off':     TXT_BOLD_OFF,
                'on':      TXT_BOLD_ON,
                #mustbeissuedafter'size'command
                #becauseESC!resetsESC-
                '_order':  10,
            },
            'font':{
                'a':       TXT_FONT_A,
                'b':       TXT_FONT_B,
                #mustbeissuedafter'size'command
                #becauseESC!resetsESC-
                '_order':  10,
            },
            'size':{
                'normal':          TXT_NORMAL,
                'double-height':   TXT_2HEIGHT,
                'double-width':    TXT_2WIDTH,
                'double':          TXT_DOUBLE,
                '_order':  1,
            },
            'color':{
                'black':   TXT_COLOR_BLACK,
                'red':     TXT_COLOR_RED,
                '_order':  1,
            },
        }

        self.push(self.defaults)

    defget(self,style):
        """what'sthevalueofastyleatthecurrentstacklevel"""
        level=len(self.stack)-1
        whilelevel>=0:
            ifstyleinself.stack[level]:
                returnself.stack[level][style]
            else:
                level=level-1
        returnNone

    defenforce_type(self,attr,val):
        """convertsavaluetotheattribute'stype"""
        ifnotattrinself.types:
            returnutfstr(val)
        elifself.types[attr]=='int':
            returnint(float(val))
        elifself.types[attr]=='float':
            returnfloat(val)
        else:
            returnutfstr(val)

    defpush(self,style={}):
        """pushanewlevelonthestackwithastyledictionnarycontainingstyle:valuepairs"""
        _style={}
        forattrinstyle:
            ifattrinself.cmdsandnotstyle[attr]inself.cmds[attr]:
                print('WARNING:ESC/POSPRINTING:ignoringinvalidvalue:%sforstyle%s'%(style[attr],utfstr(attr)))
            else:
                _style[attr]=self.enforce_type(attr,style[attr])
        self.stack.append(_style)

    defset(self,style={}):
        """overridesstylevaluesatthecurrentstacklevel"""
        _style={}
        forattrinstyle:
            ifattrinself.cmdsandnotstyle[attr]inself.cmds[attr]:
                print('WARNING:ESC/POSPRINTING:ignoringinvalidvalue:%sforstyle%s'%(style[attr],attr))
            else:
                self.stack[-1][attr]=self.enforce_type(attr,style[attr])

    defpop(self):
        """popastylestacklevel"""
        iflen(self.stack)>1:
            self.stack=self.stack[:-1]

    defto_escpos(self):
        """convertsthecurrentstyletoanescposcommandstring"""
        cmd=''
        ordered_cmds=sorted(self.cmds,key=lambdax:self.cmds[x]['_order'])
        forstyleinordered_cmds:
            cmd+=self.cmds[style][self.get(style)]
        returncmd

classXmlSerializer:
    """
    Convertsthexmlinline/blocktreestructuretoastring,
    keepingtrackofnewlinesandspacings.
    Thestringisoutputtedasaptotheprovidedescposdriver.
    """
    def__init__(self,escpos):
        self.escpos=escpos
        self.stack=['block']
        self.dirty=False

    defstart_inline(self,stylestack=None):
        """startsaninlineentitywithanoptionalstyledefinition"""
        self.stack.append('inline')
        ifself.dirty:
            self.escpos._raw('')
        ifstylestack:
            self.style(stylestack)

    defstart_block(self,stylestack=None):
        """startsablockentitywithanoptionalstyledefinition"""
        ifself.dirty:
            self.escpos._raw('\n')
            self.dirty=False
        self.stack.append('block')
        ifstylestack:
            self.style(stylestack)

    defend_entity(self):
        """endstheentitydefinition.(butdoesnotcanceltheactivestyle!)"""
        ifself.stack[-1]=='block'andself.dirty:
            self.escpos._raw('\n')
            self.dirty=False
        iflen(self.stack)>1:
            self.stack=self.stack[:-1]

    defpre(self,text):
        """putsastringoftextintheentitykeepingthewhitespaceintact"""
        iftext:
            self.escpos.text(text)
            self.dirty=True

    deftext(self,text):
        """putstextintheentity.Whitespaceandnewlinesarestrippedtosinglespaces."""
        iftext:
            text=utfstr(text)
            text=text.strip()
            text=re.sub('\s+','',text)
            iftext:
                self.dirty=True
                self.escpos.text(text)

    deflinebreak(self):
        """insertsalinebreakintheentity"""
        self.dirty=False
        self.escpos._raw('\n')

    defstyle(self,stylestack):
        """applyastyletotheentity(onlyappliestocontentaddedafterthedefinition)"""
        self.raw(stylestack.to_escpos())

    defraw(self,raw):
        """putsrawtextorescposcommandintheentitywithoutaffectingthestateoftheserializer"""
        self.escpos._raw(raw)

classXmlLineSerializer:
    """
    Thisisusedtoconvertaxmltreeintoasingleline,withaleftandarightpart.
    Thecontentisnotoutputtoescposdirectly,andisintendedtobefedbacktothe
    XmlSerializerasthecontentofablockentity.
    """
    def__init__(self,indent=0,tabwidth=2,width=48,ratio=0.5):
        self.tabwidth=tabwidth
        self.indent=indent
        self.width =max(0,width-int(tabwidth*indent))
        self.lwidth=int(self.width*ratio)
        self.rwidth=max(0,self.width-self.lwidth)
        self.clwidth=0
        self.crwidth=0
        self.lbuffer =''
        self.rbuffer =''
        self.left   =True

    def_txt(self,txt):
        ifself.left:
            ifself.clwidth<self.lwidth:
                txt=txt[:max(0,self.lwidth-self.clwidth)]
                self.lbuffer+=txt
                self.clwidth+=len(txt)
        else:
            ifself.crwidth<self.rwidth:
                txt=txt[:max(0,self.rwidth-self.crwidth)]
                self.rbuffer+=txt
                self.crwidth +=len(txt)

    defstart_inline(self,stylestack=None):
        if(self.leftandself.clwidth)or(notself.leftandself.crwidth):
            self._txt('')

    defstart_block(self,stylestack=None):
        self.start_inline(stylestack)

    defend_entity(self):
        pass

    defpre(self,text):
        iftext:
            self._txt(text)
    deftext(self,text):
        iftext:
            text=utfstr(text)
            text=text.strip()
            text=re.sub('\s+','',text)
            iftext:
                self._txt(text)

    deflinebreak(self):
        pass
    defstyle(self,stylestack):
        pass
    defraw(self,raw):
        pass

    defstart_right(self):
        self.left=False

    defget_line(self):
        return''*self.indent*self.tabwidth+self.lbuffer+''*(self.width-self.clwidth-self.crwidth)+self.rbuffer
    

classEscpos:
    """ESC/POSPrinterobject"""
    device   =None
    encoding =None
    img_cache={}

    def_check_image_size(self,size):
        """Checkandfixthesizeoftheimageto32bits"""
        ifsize%32==0:
            return(0,0)
        else:
            image_border=32-(size%32)
            if(image_border%2)==0:
                return(int(image_border/2),int(image_border/2))
            else:
                return(int(image_border/2),int((image_border/2)+1))

    def_print_image(self,line,size):
        """Printformattedimage"""
        i=0
        cont=0
        buffer=""

       
        self._raw(S_RASTER_N)
        buffer=b"%02X%02X%02X%02X"%(int((size[0]/size[1])/8),0,size[1],0)
        self._raw(codecs.decode(buffer,'hex'))
        buffer=""

        whilei<len(line):
            hex_string=int(line[i:i+8],2)
            buffer+="%02X"%hex_string
            i+=8
            cont+=1
            ifcont%4==0:
                self._raw(codecs.decode(buffer,"hex"))
                buffer=""
                cont=0

    def_raw_print_image(self,line,size,output=None):
        """Printformattedimage"""
        i=0
        cont=0
        buffer=""
        raw=b""

        def__raw(string):
            ifoutput:
                output(string)
            else:
                self._raw(string)
       
        raw+=S_RASTER_N.encode('utf-8')
        buffer="%02X%02X%02X%02X"%(int((size[0]/size[1])/8),0,size[1],0)
        raw+=codecs.decode(buffer,'hex')
        buffer=""

        whilei<len(line):
            hex_string=int(line[i:i+8],2)
            buffer+="%02X"%hex_string
            i+=8
            cont+=1
            ifcont%4==0:
                raw+=codecs.decode(buffer,'hex')
                buffer=""
                cont=0

        returnraw

    def_convert_image(self,im):
        """Parseimageandprepareittoaprintableformat"""
        pixels  =[]
        pix_line=""
        im_left =""
        im_right=""
        switch  =0
        img_size=[0,0]


        ifim.size[0]>512:
            print("WARNING:Imageiswiderthan512andcouldbetruncatedatprinttime")
        ifim.size[1]>255:
            raiseImageSizeError()

        im_border=self._check_image_size(im.size[0])
        foriinrange(im_border[0]):
            im_left+="0"
        foriinrange(im_border[1]):
            im_right+="0"

        foryinrange(im.size[1]):
            img_size[1]+=1
            pix_line+=im_left
            img_size[0]+=im_border[0]
            forxinrange(im.size[0]):
                img_size[0]+=1
                RGB=im.getpixel((x,y))
                im_color=(RGB[0]+RGB[1]+RGB[2])
                im_pattern="1X0"
                pattern_len=len(im_pattern)
                switch=(switch-1)*(-1)
                forxinrange(pattern_len):
                    ifim_color<=(255*3/pattern_len*(x+1)):
                        ifim_pattern[x]=="X":
                            pix_line+="%d"%switch
                        else:
                            pix_line+=im_pattern[x]
                        break
                    elifim_color>(255*3/pattern_len*pattern_len)andim_color<=(255*3):
                        pix_line+=im_pattern[-1]
                        break
            pix_line+=im_right
            img_size[0]+=im_border[1]

        return(pix_line,img_size)

    defimage(self,path_img):
        """Openimagefile"""
        im_open=Image.open(path_img)
        im=im_open.convert("RGB")
        #ConverttheRGBimageinprintableimage
        pix_line,img_size=self._convert_image(im)
        self._print_image(pix_line,img_size)

    defprint_base64_image(self,img):

        print('print_b64_img')

        id=md5(img).digest()

        ifidnotinself.img_cache:
            print('notincache')

            img=img[img.find(b',')+1:]
            f=io.BytesIO(b'img')
            f.write(base64.decodebytes(img))
            f.seek(0)
            img_rgba=Image.open(f)
            img=Image.new('RGB',img_rgba.size,(255,255,255))
            channels=img_rgba.split()
            iflen(channels)>3:
                #usealphachannelasmask
                img.paste(img_rgba,mask=channels[3])
            else:
                img.paste(img_rgba)

            print('convertimage')
        
            pix_line,img_size=self._convert_image(img)

            print('printimage')

            buffer=self._raw_print_image(pix_line,img_size)
            self.img_cache[id]=buffer

        print('rawimage')

        self._raw(self.img_cache[id])

    defqr(self,text):
        """PrintQRCodefortheprovidedstring"""
        qr_code=qrcode.QRCode(version=4,box_size=4,border=1)
        qr_code.add_data(text)
        qr_code.make(fit=True)
        qr_img=qr_code.make_image()
        im=qr_img._img.convert("RGB")
        #ConverttheRGBimageinprintableimage
        self._convert_image(im)

    defbarcode(self,code,bc,width=255,height=2,pos='below',font='a'):
        """PrintBarcode"""
        #AlignBarCode()
        self._raw(TXT_ALIGN_CT)
        #Height
        ifheight>=2orheight<=6:
            self._raw(BARCODE_HEIGHT)
        else:
            raiseBarcodeSizeError()
        #Width
        ifwidth>=1orwidth<=255:
            self._raw(BARCODE_WIDTH)
        else:
            raiseBarcodeSizeError()
        #Font
        iffont.upper()=="B":
            self._raw(BARCODE_FONT_B)
        else:#DEFAULTFONT:A
            self._raw(BARCODE_FONT_A)
        #Position
        ifpos.upper()=="OFF":
            self._raw(BARCODE_TXT_OFF)
        elifpos.upper()=="BOTH":
            self._raw(BARCODE_TXT_BTH)
        elifpos.upper()=="ABOVE":
            self._raw(BARCODE_TXT_ABV)
        else: #DEFAULTPOSITION:BELOW
            self._raw(BARCODE_TXT_BLW)
        #Type
        ifbc.upper()=="UPC-A":
            self._raw(BARCODE_UPC_A)
        elifbc.upper()=="UPC-E":
            self._raw(BARCODE_UPC_E)
        elifbc.upper()=="EAN13":
            self._raw(BARCODE_EAN13)
        elifbc.upper()=="EAN8":
            self._raw(BARCODE_EAN8)
        elifbc.upper()=="CODE39":
            self._raw(BARCODE_CODE39)
        elifbc.upper()=="ITF":
            self._raw(BARCODE_ITF)
        elifbc.upper()=="NW7":
            self._raw(BARCODE_NW7)
        else:
            raiseBarcodeTypeError()
        #PrintCode
        ifcode:
            self._raw(code)
            #WeareusingtypeAcommands
            #Soweneedtoaddthe'NULL'character
            #https://github.com/python-escpos/python-escpos/pull/98/files#diff-a0b1df12c7c67e38915adbe469051e2dR444
            self._raw('\x00')
        else:
            raiseBarcodeCodeError()

    defreceipt(self,xml):
        """
        Printsanxmlbasedreceiptdefinition
        """

        defstrclean(string):
            ifnotstring:
                string=''
            string=string.strip()
            string=re.sub('\s+','',string)
            returnstring

        defformat_value(value,decimals=3,width=0,decimals_separator='.',thousands_separator=',',autoint=False,symbol='',position='after'):
            decimals=max(0,int(decimals))
            width   =max(0,int(width))
            value   =float(value)

            ifautointandmath.floor(value)==value:
                decimals=0
            ifwidth==0:
                width=''

            ifthousands_separator:
                formatstr="{:"+str(width)+",."+str(decimals)+"f}"
            else:
                formatstr="{:"+str(width)+"."+str(decimals)+"f}"


            ret=formatstr.format(value)
            ret=ret.replace(',','COMMA')
            ret=ret.replace('.','DOT')
            ret=ret.replace('COMMA',thousands_separator)
            ret=ret.replace('DOT',decimals_separator)

            ifsymbol:
                ifposition=='after':
                    ret=ret+symbol
                else:
                    ret=symbol+ret
            returnret

        defprint_elem(stylestack,serializer,elem,indent=0):

            elem_styles={
                'h1':{'bold':'on','size':'double'},
                'h2':{'size':'double'},
                'h3':{'bold':'on','size':'double-height'},
                'h4':{'size':'double-height'},
                'h5':{'bold':'on'},
                'em':{'font':'b'},
                'b': {'bold':'on'},
            }

            stylestack.push()
            ifelem.taginelem_styles:
                stylestack.set(elem_styles[elem.tag])
            stylestack.set(elem.attrib)

            ifelem.tagin('p','div','section','article','receipt','header','footer','li','h1','h2','h3','h4','h5'):
                serializer.start_block(stylestack)
                serializer.text(elem.text)
                forchildinelem:
                    print_elem(stylestack,serializer,child)
                    serializer.start_inline(stylestack)
                    serializer.text(child.tail)
                    serializer.end_entity()
                serializer.end_entity()

            elifelem.tagin('span','em','b','left','right'):
                serializer.start_inline(stylestack)
                serializer.text(elem.text)
                forchildinelem:
                    print_elem(stylestack,serializer,child)
                    serializer.start_inline(stylestack)
                    serializer.text(child.tail)
                    serializer.end_entity()
                serializer.end_entity()

            elifelem.tag=='value':
                serializer.start_inline(stylestack)
                serializer.pre(format_value(
                                              elem.text,
                                              decimals=stylestack.get('value-decimals'),
                                              width=stylestack.get('value-width'),
                                              decimals_separator=stylestack.get('value-decimals-separator'),
                                              thousands_separator=stylestack.get('value-thousands-separator'),
                                              autoint=(stylestack.get('value-autoint')=='on'),
                                              symbol=stylestack.get('value-symbol'),
                                              position=stylestack.get('value-symbol-position')
                                            ))
                serializer.end_entity()

            elifelem.tag=='line':
                width=stylestack.get('width')
                ifstylestack.get('size')in('double','double-width'):
                    width=width/2

                lineserializer=XmlLineSerializer(stylestack.get('indent')+indent,stylestack.get('tabwidth'),width,stylestack.get('line-ratio'))
                serializer.start_block(stylestack)
                forchildinelem:
                    ifchild.tag=='left':
                        print_elem(stylestack,lineserializer,child,indent=indent)
                    elifchild.tag=='right':
                        lineserializer.start_right()
                        print_elem(stylestack,lineserializer,child,indent=indent)
                serializer.pre(lineserializer.get_line())
                serializer.end_entity()

            elifelem.tag=='ul':
                serializer.start_block(stylestack)
                bullet=stylestack.get('bullet')
                forchildinelem:
                    ifchild.tag=='li':
                        serializer.style(stylestack)
                        serializer.raw(''*indent*stylestack.get('tabwidth')+bullet)
                    print_elem(stylestack,serializer,child,indent=indent+1)
                serializer.end_entity()

            elifelem.tag=='ol':
                cwidth=len(str(len(elem)))+2
                i=1
                serializer.start_block(stylestack)
                forchildinelem:
                    ifchild.tag=='li':
                        serializer.style(stylestack)
                        serializer.raw(''*indent*stylestack.get('tabwidth')+''+(str(i)+')').ljust(cwidth))
                        i=i+1
                    print_elem(stylestack,serializer,child,indent=indent+1)
                serializer.end_entity()

            elifelem.tag=='pre':
                serializer.start_block(stylestack)
                serializer.pre(elem.text)
                serializer.end_entity()

            elifelem.tag=='hr':
                width=stylestack.get('width')
                ifstylestack.get('size')in('double','double-width'):
                    width=width/2
                serializer.start_block(stylestack)
                serializer.text('-'*width)
                serializer.end_entity()

            elifelem.tag=='br':
                serializer.linebreak()

            elifelem.tag=='img':
                if'src'inelem.attriband'data:'inelem.attrib['src']:
                    self.print_base64_image(bytes(elem.attrib['src'],'utf-8'))

            elifelem.tag=='barcode'and'encoding'inelem.attrib:
                serializer.start_block(stylestack)
                self.barcode(strclean(elem.text),elem.attrib['encoding'])
                serializer.end_entity()

            elifelem.tag=='cut':
                self.cut()
            elifelem.tag=='partialcut':
                self.cut(mode='part')
            elifelem.tag=='cashdraw':
                self.cashdraw(2)
                self.cashdraw(5)

            stylestack.pop()

        try:
            stylestack     =StyleStack()
            serializer     =XmlSerializer(self)
            root           =ET.fromstring(xml.encode('utf-8'))

            self._raw(stylestack.to_escpos())

            print_elem(stylestack,serializer,root)

            if'open-cashdrawer'inroot.attribandroot.attrib['open-cashdrawer']=='true':
                self.cashdraw(2)
                self.cashdraw(5)
            ifnot'cut'inroot.attriborroot.attrib['cut']=='true':
                self.cut()

        exceptExceptionase:
            errmsg=str(e)+'\n'+'-'*48+'\n'+traceback.format_exc()+'-'*48+'\n'
            self.text(errmsg)
            self.cut()

            raisee

    deftext(self,txt):
        """PrintUtf8encodedalpha-numerictext"""
        ifnottxt:
            return
        try:
            txt=txt.decode('utf-8')
        except:
            try:
                txt=txt.decode('utf-16')
            except:
                pass

        self.extra_chars=0
        
        defencode_char(char): 
            """
            Encodesasingleutf-8characterintoasequenceof
            esc-poscodepagechangeinstructionsandcharacterdeclarations
            """
            char_utf8=char.encode('utf-8')
            encoded =''
            encoding=self.encoding#wereusethelastencodingtopreventcodepageswitchesateverycharacter
            encodings={
                    #TODOuseorderingtopreventuselessswitches
                    #TODOSupportotherencodingsnotnativelysupportedbypython(Thai,Khazakh,Kanjis)
                    'cp437':TXT_ENC_PC437,
                    'cp850':TXT_ENC_PC850,
                    'cp852':TXT_ENC_PC852,
                    'cp857':TXT_ENC_PC857,
                    'cp858':TXT_ENC_PC858,
                    'cp860':TXT_ENC_PC860,
                    'cp863':TXT_ENC_PC863,
                    'cp865':TXT_ENC_PC865,
                    'cp1251':TXT_ENC_WPC1251,   #win-1251coversmorecyrillicsymbolsthancp866
                    'cp866':TXT_ENC_PC866,
                    'cp862':TXT_ENC_PC862,
                    'cp720':TXT_ENC_PC720,
                    'cp936':TXT_ENC_PC936,
                    'iso8859_2':TXT_ENC_8859_2,
                    'iso8859_7':TXT_ENC_8859_7,
                    'iso8859_9':TXT_ENC_8859_9,
                    'cp1254'  :TXT_ENC_WPC1254,
                    'cp1255'  :TXT_ENC_WPC1255,
                    'cp1256'  :TXT_ENC_WPC1256,
                    'cp1257'  :TXT_ENC_WPC1257,
                    'cp1258'  :TXT_ENC_WPC1258,
                    'katakana':TXT_ENC_KATAKANA,
            }
            remaining=copy.copy(encodings)

            ifnotencoding:
                encoding='cp437'

            whileTrue:#Tryingallencodinguntilonesucceeds
                try:
                    ifencoding=='katakana':#Japanesecharacters
                        ifjcconv:
                            #trytoconvertjapanesetexttoahalf-katakanas
                            kata=jcconv.kata2half(jcconv.hira2kata(char_utf8))
                            ifkata!=char_utf8:
                                self.extra_chars+=len(kata.decode('utf-8'))-1
                                #theconversionmayresultinmultiplecharacters
                                returnencode_str(kata.decode('utf-8'))
                        else:
                             kata=char_utf8
                        
                        ifkatainTXT_ENC_KATAKANA_MAP:
                            encoded=TXT_ENC_KATAKANA_MAP[kata]
                            break
                        else:
                            raiseValueError()
                    else:
                        #First127symbolsarecoveredbycp437.
                        #Extendedrangeiscoveredbydifferentencodings.
                        encoded=char.encode(encoding)
                        iford(encoded)<=127:
                            encoding='cp437'
                        break

                except(UnicodeEncodeError,UnicodeWarning,TypeError,ValueError):
                    #theencodingfailed,selectanotheroneandretry
                    ifencodinginremaining:
                        delremaining[encoding]
                    iflen(remaining)>=1:
                        (encoding,_)=remaining.popitem()
                    else:
                        encoding='cp437'
                        encoded =b'\xb1'   #couldnotencode,outputerrorcharacter
                        break;

            ifencoding!=self.encoding:
                #iftheencodingchanged,rememberitandprefixthecharacterwith
                #theesc-posencodingchangesequence
                self.encoding=encoding
                encoded=bytes(encodings[encoding],'utf-8')+encoded

            returnencoded
        
        defencode_str(txt):
            buffer=b''
            forcintxt:
                buffer+=encode_char(c)
            returnbuffer

        txt=encode_str(txt)

        #iftheutf-8->codepageconversioninsertedextracharacters,
        #removedoublespacestotrytorestoretheoriginalstringlength
        #andpreventprintingalignmentissues
        whileself.extra_chars>0:
            dspace=txt.find(' ')
            ifdspace>0:
                txt=txt[:dspace]+txt[dspace+1:]
                self.extra_chars-=1
            else:
                break

        self._raw(txt)
        
    defset(self,align='left',font='a',type='normal',width=1,height=1):
        """Settextproperties"""
        #Align
        ifalign.upper()=="CENTER":
            self._raw(TXT_ALIGN_CT)
        elifalign.upper()=="RIGHT":
            self._raw(TXT_ALIGN_RT)
        elifalign.upper()=="LEFT":
            self._raw(TXT_ALIGN_LT)
        #Font
        iffont.upper()=="B":
            self._raw(TXT_FONT_B)
        else: #DEFAULTFONT:A
            self._raw(TXT_FONT_A)
        #Type
        iftype.upper()=="B":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL_OFF)
        eliftype.upper()=="U":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL_ON)
        eliftype.upper()=="U2":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL2_ON)
        eliftype.upper()=="BU":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL_ON)
        eliftype.upper()=="BU2":
            self._raw(TXT_BOLD_ON)
            self._raw(TXT_UNDERL2_ON)
        eliftype.upper=="NORMAL":
            self._raw(TXT_BOLD_OFF)
            self._raw(TXT_UNDERL_OFF)
        #Width
        ifwidth==2andheight!=2:
            self._raw(TXT_NORMAL)
            self._raw(TXT_2WIDTH)
        elifheight==2andwidth!=2:
            self._raw(TXT_NORMAL)
            self._raw(TXT_2HEIGHT)
        elifheight==2andwidth==2:
            self._raw(TXT_2WIDTH)
            self._raw(TXT_2HEIGHT)
        else:#DEFAULTSIZE:NORMAL
            self._raw(TXT_NORMAL)


    defcut(self,mode=''):
        """Cutpaper"""
        #Fixthesizebetweenlastlineandcut
        #TODO:handlethiswithalinefeed
        self._raw("\n\n\n\n\n\n")
        ifmode.upper()=="PART":
            self._raw(PAPER_PART_CUT)
        else:#DEFAULTMODE:FULLCUT
            self._raw(PAPER_FULL_CUT)


    defcashdraw(self,pin):
        """Sendpulsetokickthecashdrawer

        Forsomereason,withsomeprinters(ex:EpsonTM-m30),thecashdrawer
        onlyopens50%ofthetimeifyoujustsendthepulse.Butifyouread
        thestatusafterwards,itopensallthetime.
        """
        ifpin==2:
            self._raw(CD_KICK_2)
        elifpin==5:
            self._raw(CD_KICK_5)
        else:
            raiseCashDrawerError()

        self.get_printer_status()

    defhw(self,hw):
        """Hardwareoperations"""
        ifhw.upper()=="INIT":
            self._raw(HW_INIT)
        elifhw.upper()=="SELECT":
            self._raw(HW_SELECT)
        elifhw.upper()=="RESET":
            self._raw(HW_RESET)
        else:#DEFAULT:DOESNOTHING
            pass


    defcontrol(self,ctl):
        """Feedcontrolsequences"""
        ifctl.upper()=="LF":
            self._raw(CTL_LF)
        elifctl.upper()=="FF":
            self._raw(CTL_FF)
        elifctl.upper()=="CR":
            self._raw(CTL_CR)
        elifctl.upper()=="HT":
            self._raw(CTL_HT)
        elifctl.upper()=="VT":
            self._raw(CTL_VT)
